# 📖 Bible Notes

A simple, phone-friendly app for taking notes on sermons at church and during personal Bible study.
It's plain HTML/CSS/JavaScript with no build step or server. It works offline, and your notes stay on your device.

## Features

- **Sermon notes**: title, speaker, date, scripture passages, church/event, series and tags.
- **Bible study notes**: blank or a **SOAP** template (Scripture · Observation · Application · Prayer).
- **Built-in Bible text (works offline).** Type a reference like `John 3:16`, `rom 8:28` or `1 Cor 13:4-7`
  and press **Enter**. The verse text is added to your note automatically:
  - A line that is *only* a reference is replaced by the verse: `📖 John 3:16 “For God so loved…” (BSB)`
  - A reference inside a sentence (`Paul says in Rom 8:28 all things…`) gets the verse added on the line below,
    and you keep typing where you were.
  - Tap **Undo** on the pop-up to remove it, or put the cursor on a line and tap **📖 Verse** to add it by hand.
  - Choose **BSB** (Berean Standard Bible, modern English) or **KJV** in Settings, or turn auto-insert off.
    Both are public domain, which is why they can be bundled. ESV and NIV are copyrighted and can't be included.
- **Quick-mark buttons** for headings, bullet points, ⭐ key points, 📖 verses, ❓ questions, ➡️ applications and 🙏 prayers.
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

| Type this            | You get                         |
|----------------------|---------------------------------|
| `# Main point`       | Heading                         |
| `- text`             | Bullet point                    |
| `> text`             | Quote                           |
| `⭐ text`            | Highlighted key point           |
| `📖 John 10:11 …`    | Verse callout (with link)       |
| `❓ text`            | Question to study later         |
| `➡️ text`            | Application                     |
| `🙏 text`            | Prayer                          |
| `**bold**` / `*italic*` | **bold** / *italic*          |
| `John 3:16` + Enter  | Verse text inserted automatically |

## Project layout

```
index.html             The whole app (markup, styles and script)
manifest.webmanifest   App name, colors and icons for "Add to Home Screen"
sw.js                  Service worker that caches the app for offline use
icons/                 App icons
bible/bsb.js, kjv.js   Bible text (loaded only when needed, cached for offline use)
tools/build_bible.py   Script that generated bible/*.js from public-domain source data
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
