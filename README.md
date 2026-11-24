# MapleTracker V4 (prototype)

Web tracker for MapleStory Classic World. Capture a game window using Chrome/Edge screen sharing; experimental browser OCR, EXP/h and mesos/h diagnostics, and manual ETC profit ledger.

## Run
Open index.html through a static web server or GitHub Pages (HTTPS required for display capture). Click **Chọn cửa sổ MapleStory**, select the game window, and inspect the OCR diagnostic. No Python required.

## Important limitations
- OCR is **experimental**, not yet calibrated to the actual game HUD. It may fail to find EXP or mesos. Mesos may not be visible unless Inventory is open.
- ETC icon recognition, team accounts, shared history, level-up handling and verified profit are **not implemented**.
- Tesseract.js loads from CDN; internet is needed for OCR assets.
- Screen capture stays in browser; the app does not upload screenshots.
- No memory reading, packet interception or game automation.

## GitHub Pages
Settings → Pages → Build and deployment → Deploy from a branch → main / (root). Then wait for the published URL. This repository does not automatically enable Pages.
