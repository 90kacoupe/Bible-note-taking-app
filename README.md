# 📖 Bible Notes

A simple, phone-friendly app for taking notes on sermons at church and during personal Bible study.
It's plain HTML/CSS/JavaScript with no build step or server. It works offline, and your notes stay on your device.

## Features

- **Two styles, switchable in Settings → Style:**
  - **Leather:** a classic Bible look, with an oxblood-and-gold header, parchment pages, Garamond type,
    and references in red small caps.
  - **Journal:** a warm notebook look, with dotted and ruled paper, handwritten dates and questions,
    highlighted key points, checkable applications, and prayers on a sticky note.

  Each style has a light and a dark mode (Settings → Light or dark). The fonts are bundled, so everything
  works offline.
- **Bible reader (the Bible tab):**
  - Read any chapter in BSB or KJV (offline), or ESV, NLT or your YouVersion translations (online; falls back to BSB when offline).
  - Tap the chapter name to pick a book and chapter, tap the search icon to jump to a reference (e.g. `rom 8:28`),
    and swipe or use the arrows to change chapters. The app remembers where you left off.
  - **Printed-Bible layout:** section headings, parallel passages, paragraphs, poetry lines and footnotes (tap the
    small letter to read one). BSB has all of these; KJV has its paragraphs, Psalm titles and poetry, and shows the
    words the translators supplied in italics, as printed KJVs do. YouVersion translations show the headings,
    paragraphs and footnotes YouVersion provides. ESV and NLT show verse text only for now. Settings → *Words of Jesus
    in red* turns on red letters.
  - **Highlight:** tap verses to select them, then choose one of five colors. Highlights are saved per verse, so they
    show in every translation, and they're included in your backup.
  - **Copy, share, or start a note** from selected verses. The new note has the passage and verse text filled in.
  - **Your notes, linked:** a banner shows notes that cover the chapter, and a marker appears on verses your notes
    quote or mention. Tap it to see those notes. Verse references in your notes open the reader.
- **Reading view:** notes open ready to read. Tap **Edit** to change them. In the reading view you can
  tick off applications as you do them.

- **Sermon notes**: title, speaker, date, scripture passages, church/event, series and tags.
- **Bible study notes**: blank or a **SOAP** template (Scripture · Observation · Application · Prayer).
- **Built-in Bible text (works offline).** Type a reference like `John 3:16`, `rom 8:28` or `1 Cor 13:4-7`
  and press **Enter**. The verse text is added to your note automatically:
  - A line that is *only* a reference is replaced by the verse: `📖 John 3:16 “For God so loved…” (BSB)`
  - A reference inside a sentence (`Paul says in Rom 8:28 all things…`) gets the verse added on the line below,
    and you keep typing where you were.
  - Tap **Undo** on the pop-up to remove it, or put the cursor on a line and tap **📖 Verse** to add it by hand.
  - Choose the translation in **Settings → Verse text**, or turn auto-insert off:

    | Translation | Where the text comes from | Needs |
    |-------------|---------------------------|-------|
    | **BSB** Berean Standard Bible | Bundled in the app | Nothing, works offline |
    | **KJV** King James Version | Bundled in the app | Nothing, works offline |
    | **ESV** English Standard Version | Crossway's ESV API | Internet + free key from [api.esv.org](https://api.esv.org/) |
    | **NLT** New Living Translation | Tyndale's NLT API | Internet (built-in test key, or your own free key from [api.nlt.to](https://api.nlt.to/)) |
    | **YouVersion** (NIV and many more) | [YouVersion Platform](https://developers.youversion.com/) | Internet + your YouVersion app key |

    Once your YouVersion Bibles are loaded, the separate ESV and NLT options are hidden if YouVersion offers the
    same translation (and a selected ESV/NLT switches to the YouVersion copy).

    BSB and KJV are public domain, so they can be bundled. ESV and NLT are copyrighted and come from the
    publishers' own services. If an online translation can't be reached, or the key is missing or rejected,
    the verse is added from the BSB and the pop-up says why.

    **YouVersion setup:** in Settings, paste your app key under **YouVersion app key** and tap
    **Load my YouVersion Bibles**. The English Bibles your key can use then appear under **Verse text**.

    Keys are typed into Settings on each device and saved only there. Never put a key in the code,
    since this repository can be published through GitHub Pages.

    To add another service, add an entry to `TRANSLATIONS` in `index.html` with a
    `fetch(reference, key, ref)` function.
- **Quick-mark buttons** for headings, points, key points, verses, questions, applications and prayers.
  Bullet lists continue automatically when you press Enter.
- **Preview mode** shows color-coded notes. Verse references such as `John 3:16` or `1 Cor 13:4-7` become links
  to Bible Gateway in your chosen translation (ESV, NIV, KJV, NKJV, NLT, CSB, NASB, AMP, MSG).
- **Autosave** while you type, and again if you lock your phone or switch apps.
- **Search** across titles, passages, speakers, tags and note text, with filters for sermons, studies and tags.
- **Share** a note through your phone's share sheet (text, email, etc.).
- **Backup and restore**: export all notes as a JSON backup or a readable `.txt` file, and import a backup on another device.
- Light and dark themes, adjustable text size, and "Add to Home Screen" support so it opens like a real app.

## Getting it onto your phone

### Option 1: GitHub Pages (recommended)
1. On GitHub, open the repo's **Settings → Pages**.
2. Under "Build and deployment", choose **Deploy from a branch**. Pick your branch and the `/ (root)` folder, then save.
3. After a minute or so, open the URL GitHub shows (e.g. `https://<username>.github.io/Bible-note-taking-app/`) on your phone.
4. Add it to your home screen:
   - **iPhone (Safari):** Share button → **Add to Home Screen**
   - **Android (Chrome):** ⋮ menu → **Add to Home screen** / **Install app**

The app then opens full-screen from its icon and works without internet. (GitHub Pages for a *private* repo needs a paid GitHub plan.
Otherwise make the repo public. Only the app code is public; your notes never leave your phone.)

### Option 2: Run it locally on your computer and open it on your phone
```sh
python3 -m http.server 8000
```
Then on your phone (on the same Wi-Fi) go to `http://<your-computer's-IP>:8000`.
Note that notes saved this way are tied to that address.

### Option 3: Just open the file
You can also open `index.html` directly in a browser. Everything works except offline install
and the home-screen icon. Some phone browsers limit saving data for local files, so use Option 1 for day-to-day use.

## ⚠️ About your data
Notes are stored in the browser's local storage **on that device only**. Clearing browser data,
or uninstalling the home-screen app on some phones, will erase them.
Use **Settings → Export backup** regularly, and keep the file somewhere safe (Google Drive, iCloud, email to yourself).

## Formatting cheat-sheet

| Type this              | You get                                  |
|------------------------|------------------------------------------|
| `John 3:16` + Enter    | Verse text inserted automatically        |
| `# Main point`         | Heading                                  |
| `- text`               | Bullet point                             |
| `★ text`               | Key point                                |
| `> text`               | Scripture or quote typed by hand         |
| `? text`               | Question to study later                  |
| `→ text`               | Application (a checkbox; ticked = `✓`)   |
| `✝ text`               | Prayer                                   |
| `**bold**` / `*italic*`| **bold** / *italic*                      |

The toolbar buttons type these for you. Notes written with the older emoji markers (⭐ 📖 ❓ ➡️ 🙏) still display correctly.

## Project layout

```
index.html             The app (markup and script)
styles.css             Both styles (Leather and Journal), light and dark
fonts/                 Bundled fonts (SIL Open Font License, licenses included)
manifest.webmanifest   App name, colors and icons for "Add to Home Screen"
sw.js                  Service worker that caches the app for offline use
icons/                 App icons
bible/bsb.js, kjv.js   Bible text with headings, paragraphs and footnotes (loaded when needed, cached for offline use)
tools/build_bible.py   Builds bible/*.js from the official BSB USFM release and the eBible.org KJV (public domain)
```

When you change `index.html`, bump `VERSION` in `sw.js` so installed copies pick up the update.

## Future: Android / iPhone apps

The app is plain web code, so it can be wrapped as a native app with [Capacitor](https://capacitorjs.com/)
without a rewrite:

```sh
npm init -y
npm install @capacitor/core @capacitor/cli @capacitor/android @capacitor/ios
npx cap init "Bible Notes" com.example.biblenotes --web-dir www
# copy index.html, manifest.webmanifest, sw.js and icons/ into www/
npx cap add android   # opens in Android Studio
npx cap add ios       # needs a Mac with Xcode
```

Possible next steps at that point include cloud sync between devices, licensed translations
such as ESV/NIV through their official APIs, and reminders for reading plans.
