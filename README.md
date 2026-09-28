# VOSIQ atrium installation — QR info page

A visitor scans the QR code next to the installation, and a phone page opens with the text and an Uzbek narration.

- `content.json` holds the text. Edit only this file.
- `tools/build_audio.py [voice]` generates `docs/audio/narration.mp3` and `timings.json` with Microsoft Edge neural TTS
  (`uz-UZ-SardorNeural` male, the default; `uz-UZ-MadinaNeural` female). It needs internet access.
- `tools/build_page.py` renders `docs/index.html` from `tools/template.html`. It normalises apostrophes to o‘ g‘ ʼ on display.
- `tools/make_qr.py URL` writes `qr/qr.svg` and `qr/qr.png`.

After editing the text, rebuild the audio and then the page:

    python3 -m venv .venv && .venv/bin/pip install edge-tts qrcode
    .venv/bin/python tools/build_audio.py && .venv/bin/python tools/build_page.py

Hosting: GitHub Pages serves `docs/`. When moving to a custom domain, add it under Settings → Pages.
GitHub then redirects the old `*.github.io` address, so QR codes that are already printed keep working
as long as this repository stays on GitHub.
