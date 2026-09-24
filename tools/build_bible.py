#!/usr/bin/env python3
"""Build the bundled Bible files in bible/ from public-domain sources.

    python3 tools/build_bible.py --bsb BSB_usfm.zip --kjv eng-kjv.osis.xml

Sources:
  BSB  Official USFM release, https://github.com/BSB-publishing/bsb2usfm/releases (BSB_usfm.zip)
  KJV  eBible.org OSIS, via https://github.com/seven1m/open-bibles (eng-kjv.osis.xml)

Each output file (bible/<code>.js) is a script (so it also loads from file://) that sets
    BIBLE_DATA[CODE] = { v: 2, books: [ book: [ chapter: [ block, ... ] ] ] }
in the Protestant 66-book order. A block is [type, ...items]:
  type   "s1" "s2" section heading, "ms"/"mr" major section, "r" parallel passages,
         "d" psalm title, "qa" acrostic letter  -> items: [text]
         "p" "m" "pi" "pc" "pmo" "q1" "q2" "qr" "li1" "li2"  -> paragraph or poetry line
         "b" blank line
  items  a number starts that verse; a string is text;
         ["j", text] words of Jesus, ["a", text] words supplied by translators, ["ja", text] both;
         ["f", note] a footnote (text; _underscores_ mark quoted alternatives).
The app derives plain verse text from these blocks for verse insertion and copying.
"""
import argparse
import io
import json
import os
import re
import xml.etree.ElementTree as ET
import zipfile

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'bible')

USFM_BOOKS = [
    'GEN', 'EXO', 'LEV', 'NUM', 'DEU', 'JOS', 'JDG', 'RUT', '1SA', '2SA', '1KI', '2KI', '1CH', '2CH', 'EZR', 'NEH', 'EST',
    'JOB', 'PSA', 'PRO', 'ECC', 'SNG', 'ISA', 'JER', 'LAM', 'EZK', 'DAN', 'HOS', 'JOL', 'AMO', 'OBA', 'JON', 'MIC', 'NAM',
    'HAB', 'ZEP', 'HAG', 'ZEC', 'MAL', 'MAT', 'MRK', 'LUK', 'JHN', 'ACT', 'ROM', '1CO', '2CO', 'GAL', 'EPH', 'PHP', 'COL',
    '1TH', '2TH', '1TI', '2TI', 'TIT', 'PHM', 'HEB', 'JAS', '1PE', '2PE', '1JN', '2JN', '3JN', 'JUD', 'REV',
]
OSIS_BOOKS = [
    'Gen', 'Exod', 'Lev', 'Num', 'Deut', 'Josh', 'Judg', 'Ruth', '1Sam', '2Sam', '1Kgs', '2Kgs', '1Chr', '2Chr', 'Ezra',
    'Neh', 'Esth', 'Job', 'Ps', 'Prov', 'Eccl', 'Song', 'Isa', 'Jer', 'Lam', 'Ezek', 'Dan', 'Hos', 'Joel', 'Amos', 'Obad',
    'Jonah', 'Mic', 'Nah', 'Hab', 'Zeph', 'Hag', 'Zech', 'Mal', 'Matt', 'Mark', 'Luke', 'John', 'Acts', 'Rom', '1Cor',
    '2Cor', 'Gal', 'Eph', 'Phil', 'Col', '1Thess', '2Thess', '1Tim', '2Tim', 'Titus', 'Phlm', 'Heb', 'Jas', '1Pet',
    '2Pet', '1John', '2John', '3John', 'Jude', 'Rev',
]

TITLE_BLOCKS = {'s1', 's2', 's3', 'ms', 'ms1', 'mr', 'r', 'd', 'qa'}
PARA_BLOCKS = {'p', 'm', 'pi', 'pi1', 'pi2', 'pc', 'pmo', 'q', 'q1', 'q2', 'q3', 'qr', 'qc', 'li', 'li1', 'li2', 'lf', 'nb', 'mi'}
PARA_ALIASES = {'pi1': 'pi', 'pi2': 'pi', 'q': 'q1', 'q3': 'q2', 'qc': 'pc', 'li': 'li1', 'lf': 'p', 'nb': 'm', 'mi': 'm', 'ms1': 'ms', 's3': 's2'}
SKIP_MARKERS = {'id', 'h', 'toc1', 'toc2', 'toc3', 'mt', 'mt1', 'mt2', 'ide', 'rem', 'usfm', 'cl', 'cp'}


class Chapter:
    """Collects blocks for one chapter, merging adjacent text runs with the same style."""

    def __init__(self):
        self.blocks = []

    def block(self, kind, *items):
        self.blocks.append([PARA_ALIASES.get(kind, kind), *items])

    def add(self, item, title=False):
        if not self.blocks or (not title and self.blocks[-1][0] in TITLE_BLOCKS | {'b'}):
            self.block('p')  # text with no paragraph marker yet
        blk = self.blocks[-1]
        if isinstance(item, str):
            if not item:
                return
            if len(blk) > 1 and isinstance(blk[-1], str):
                blk[-1] += item
                return
        elif isinstance(item, list) and item[0] in ('j', 'a', 'ja'):
            if not item[1]:
                return
            if len(blk) > 1 and isinstance(blk[-1], list) and blk[-1][0] == item[0]:
                blk[-1][1] += item[1]
                return
        blk.append(item)

    def text(self, text, wj, add, title=False):
        style = ('j' if wj else '') + ('a' if add else '')
        self.add([style, text] if style else text, title)

    def finish(self):
        out = []
        for blk in self.blocks:
            items = []
            for it in blk[1:]:
                if isinstance(it, str):
                    it = re.sub(r'\s+', ' ', it)
                elif isinstance(it, list) and it[0] != 'f':
                    it = [it[0], re.sub(r'\s+', ' ', it[1])]
                items.append(it)
            # Trim spaces at the start and end of each block.
            if items and isinstance(items[0], str):
                items[0] = items[0].lstrip()
            if items and isinstance(items[-1], str):
                items[-1] = items[-1].rstrip()
            items = [it for it in items if it != '' and not (isinstance(it, list) and it[0] != 'f' and not it[1])]
            if blk[0] in TITLE_BLOCKS:
                text = ''.join(i if isinstance(i, str) else i[1] for i in items if not (isinstance(i, list) and i[0] == 'f'))
                if text.strip():
                    out.append([blk[0], text.strip()])
            elif blk[0] == 'b':
                if out and out[-1] != ['b']:
                    out.append(['b'])
            elif any(not (isinstance(i, list) and i[0] == 'f') for i in items):
                out.append([blk[0], *items])
        while out and out[-1] == ['b']:
            out.pop()
        return out


# ---------------------------------------------------------------- USFM (BSB)
TOKEN_RE = re.compile(r'\\(\+?[a-z0-9]+\*)|\\(\+?[a-z0-9]+)[ ]?|([^\\]+)')


def footnote_text(raw):
    """'\\fr 10:8 \\ft BYZ \\fqa All who came' -> 'BYZ _All who came_'."""
    parts, style = [], 'ft'
    for m in TOKEN_RE.finditer(raw):
        marker, text = m.group(1) or m.group(2), m.group(3)
        if marker:
            marker = marker.lstrip('+')
            if marker.endswith('*'):
                style = 'ft'
            else:
                style = marker
            continue
        if style in ('fr', 'fv'):
            continue  # the verse reference ("10:8") is shown by the note's position
        parts.append(f'_{text.strip()}_ ' if style in ('fqa', 'fq') else text)
    return re.sub(r'\s+', ' ', ''.join(parts)).replace(' _ ', ' ').strip()


def parse_usfm_book(src):
    chapters = {}
    chap = None
    wj = add = False
    # Footnotes can't nest, so pull them out first as placeholders.
    notes = []

    def stash(m):
        notes.append(footnote_text(m.group(1)))
        return f'\\zfn{len(notes) - 1}\\zfn* '
    src = re.sub(r'\\\+?ref ([^|\\]*)\|[^\\]*\\\+?ref\*', r'\1', src)     # keep the display text of \ref
    src = re.sub(r'\\f \+ (.*?)\\f\*', stash, src, flags=re.S)
    src = re.sub(r'\\x .*?\\x\*', '', src, flags=re.S)                    # cross-reference notes

    for line in src.splitlines():
        line = line.rstrip()
        m = re.match(r'\\([a-z0-9]+)\s?(.*)$', line)
        if not m:
            if chap and line.strip():
                inline(chap, line + ' ', notes, [wj, add])
            continue
        marker, rest = m.group(1), m.group(2)
        if marker == 'c':
            n = int(rest.split()[0])
            chap = chapters.setdefault(n, Chapter())
            wj = add = False
            continue
        if marker in SKIP_MARKERS or chap is None:
            continue
        if marker in TITLE_BLOCKS:
            chap.block(marker)
            state = [False, False]
            inline(chap, rest, notes, state, title=True)
            continue
        if marker == 'b':
            chap.block('b')
            continue
        if marker in PARA_BLOCKS:
            chap.block(marker)
            state = [wj, add]
            inline(chap, rest + ' ', notes, state)
            wj, add = state
            continue
        # Any other marker at the start of a line (e.g. \v in a continuing paragraph).
        state = [wj, add]
        inline(chap, line + ' ', notes, state)
        wj, add = state
    return [chapters[n].finish() for n in sorted(chapters)]


def inline(chap, text, notes, state, title=False):
    wj, add = state
    for m in TOKEN_RE.finditer(text):
        marker, run = m.group(1) or m.group(2), m.group(3)
        if run is not None:
            chap.text(run, wj and not title, add and not title, title)
            continue
        base = marker.lstrip('+')
        if base == 'v':
            vm = re.match(r'(\d+)', text[m.end():])
            chap.add(int(vm.group(1)))
            # Skip the verse number itself.
            rest = text[m.end() + vm.end():]
            inline(chap, rest, notes, state, title)
            return
        if base.startswith('zfn') and not base.endswith('*'):
            chap.add(['f', notes[int(base[3:])]])
        elif base == 'wj':
            wj = True
        elif base == 'wj*':
            wj = False
        elif base == 'add':
            add = True
        elif base == 'add*':
            add = False
        # Other character markers (\nd, \qs, …) keep their text and are otherwise ignored.
        state[0], state[1] = wj, add
    state[0], state[1] = wj, add


def build_bsb(zip_path):
    z = zipfile.ZipFile(zip_path)
    names = {os.path.basename(n).split('.')[0].upper(): n for n in z.namelist() if n.lower().endswith('.usfm')}
    books = []
    for code in USFM_BOOKS:
        name = names.get(code) or next(n for k, n in names.items() if code in k)
        books.append(parse_usfm_book(z.read(name).decode('utf-8-sig')))
    return books


# ---------------------------------------------------------------- OSIS (KJV)
def build_kjv(osis_path):
    ns = '{http://www.bibletechnologies.net/2003/OSIS/namespace}'
    root = ET.parse(osis_path).getroot()
    books = {b: {} for b in OSIS_BOOKS}
    state = {'book': None, 'chap': None, 'wj': False, 'q': {}}

    def cur():
        return state['chap']

    def emit(text, add=False):
        if text and cur() is not None:
            cur().text(text, state['wj'], add)

    def walk(el, add=False):
        tag = el.tag.replace(ns, '')
        a = el.attrib
        if tag == 'chapter' and 'sID' in a:
            book, ch = a['osisRef'].split('.')
            state['book'] = book if book in books else None
            state['chap'] = books[book].setdefault(int(ch), Chapter()) if state['book'] else None
        elif tag == 'chapter' and 'eID' in a:
            state['chap'] = None
        elif tag == 'verse' and 'sID' in a and cur() is not None:
            cur().add(int(a['n']))
        elif tag == 'q' and 'sID' in a:
            state['q'][a['sID']] = a.get('who') == 'Jesus'
            if a.get('who') == 'Jesus':
                state['wj'] = True
        elif tag == 'q' and 'eID' in a:
            if state['q'].pop(a['eID'], False):
                state['wj'] = False
        elif tag == 'title' and cur() is not None:
            kind = {'psalm': 'd', 'acrostic': 'qa'}.get(a.get('type'))
            if kind:
                cur().block(kind)
                cur().add(''.join(el.itertext()).strip(), title=True)
            emit(el.tail)
            return
        elif tag == 'p' and cur() is not None:
            cur().block('p')
        elif tag == 'l' and cur() is not None:
            cur().block('q2' if a.get('level') == '2' else 'q1')
        elif tag == 'lg' and cur() is not None:
            pass
        elif tag == 'note':
            emit(el.tail, add)
            return
        if tag not in ('title',):
            emit(el.text, add or (tag == 'transChange' and a.get('type') == 'added'))
        for child in el:
            walk(child, add or (tag == 'transChange' and a.get('type') == 'added'))
        emit(el.tail, add)

    walk(root)
    out = []
    for b in OSIS_BOOKS:
        chapters = books[b]
        assert chapters, f'KJV: missing {b}'
        out.append([chapters[n].finish() for n in sorted(chapters)])
    return out


# ---------------------------------------------------------------- output
def plain_verses(chapter):
    """Verse number -> plain text, the way the app derives it."""
    verses, v = {}, 0
    for blk in chapter:
        if blk[0] in TITLE_BLOCKS or blk[0] == 'b':
            continue
        for it in blk[1:]:
            if isinstance(it, int):
                v = it
                verses.setdefault(v, '')
            elif v and isinstance(it, str):
                verses[v] += it if not verses[v] or verses[v].endswith(' ') or it.startswith(' ') else ' ' + it
            elif v and it[0] != 'f':
                verses[v] += it[1] if not verses[v] or verses[v].endswith(' ') or it[1].startswith(' ') else ' ' + it[1]
    return {k: re.sub(r'\s+', ' ', t).strip() for k, t in verses.items()}


def write(code, title, books):
    os.makedirs(OUT_DIR, exist_ok=True)
    dest = os.path.join(OUT_DIR, code.lower() + '.js')
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(f'// {title} (public domain)\n')
        f.write('window.BIBLE_DATA = window.BIBLE_DATA || {};\n')
        f.write(f'BIBLE_DATA.{code} = ')
        json.dump({'v': 2, 'books': books}, f, ensure_ascii=False, separators=(',', ':'))
        f.write(';\n')
    print(dest, os.path.getsize(dest), 'bytes')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--bsb', help='BSB_usfm.zip from the official release')
    ap.add_argument('--kjv', help='eng-kjv.osis.xml')
    args = ap.parse_args()
    if args.bsb:
        write('BSB', 'BSB: Berean Standard Bible', build_bsb(args.bsb))
    if args.kjv:
        write('KJV', 'KJV: King James Version (1769)', build_kjv(args.kjv))
