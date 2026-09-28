# VOSIQ atrium installation — QR info page

A visitor scans the QR code next to the installation, and a phone page opens with the text and an Uzbek narration.

- `content/uz.json`, `ru.json`, `en.json` hold the text, the button labels, the voice, and `say`: spoken-only respellings,
  e.g. "(atom)" to "(aatom)" in Uzbek only. Edit only these files.
- `tools/build_audio.py [uz ru en]` writes `docs/audio/<lang>/narration.mp3` and `timings.json` with Microsoft Edge neural TTS
  (Uzbek Sardor, Russian Dmitry, English Ryan en-GB). It needs internet access and retries when the free endpoint drops a request.
- `tools/build_page.py` renders `docs/index.html` (Uzbek, the QR target) plus `docs/ru/` and `docs/en/`.
  It normalises Uzbek apostrophes to o‘ g‘ ʼ on display. The page remembers the visitor's last language.
- `tools/pronunciation_tests.py` writes clips of hard words in several spellings to `pronunciation_tests/`, to choose by ear.
- `tools/make_qr.py URL` writes `qr/qr.svg` and `qr/qr.png`.

After editing a language file, rebuild that language's audio and then the pages:

    python3 -m venv .venv && .venv/bin/pip install edge-tts qrcode
    .venv/bin/python tools/build_audio.py ru && .venv/bin/python tools/build_page.py

Hosting: GitHub Pages serves `docs/`. When moving to a custom domain, add it under Settings → Pages.
GitHub then redirects the old `*.github.io` address, so QR codes that are already printed keep working
as long as this repository stays on GitHub.
