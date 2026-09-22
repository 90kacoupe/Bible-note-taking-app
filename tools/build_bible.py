#!/usr/bin/env python3
"""Convert public-domain Bible JSON into the compact files in bible/.

Source: https://github.com/scrollmapper/bible_databases (formats/json/<CODE>.json)

    python3 tools/build_bible.py BSB.json KJV.json

Each output file (bible/<code>.js) assigns
    BIBLE_DATA[CODE] = [ book: [ chapter: [ "verse 1 text", "verse 2 text", ... ] ] ]
using the Protestant 66-book order. It is a script (not .json) so it loads
even when index.html is opened straight from the file system.
"""
import json
import os
import re
import sys

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'bible')


def convert(path):
    code = os.path.basename(path).split('.')[0].upper()
    data = json.load(open(path, encoding='utf-8'))
    books = data['books']
    assert len(books) == 66, f'{path}: expected 66 books, got {len(books)}'
    out = []
    for book in books:
        chapters = []
        for i, ch in enumerate(book['chapters'], 1):
            assert ch['chapter'] == i, f"{book['name']} chapter numbering"
            verses = []
            for v in ch['verses']:
                text = v['text'].replace('[', '').replace(']', '')  # KJV marks supplied words with [ ]
                text = re.sub(r'\s+', ' ', text).strip()
                # Fill any gap in numbering so index == verse - 1.
                while len(verses) < v['verse'] - 1:
                    verses.append('')
                verses.append(text)
            chapters.append(verses)
        out.append(chapters)
    os.makedirs(OUT_DIR, exist_ok=True)
    dest = os.path.join(OUT_DIR, code.lower() + '.js')
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(f'// {data["translation"]} (public domain)\n')
        f.write('window.BIBLE_DATA = window.BIBLE_DATA || {};\n')
        f.write(f'BIBLE_DATA.{code} = ')
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
        f.write(';\n')
    print(dest, os.path.getsize(dest), 'bytes')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        convert(p)
