"""Render one page per language from content/<lang>.json + docs/audio/<lang>/timings.json.

Uzbek is the default page (docs/index.html, the QR target); other languages go to docs/<lang>/index.html.
"""
import html, json, re, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = "uz"
ORDER = ["uz", "ru", "en"]
LANGS = [l for l in ORDER if (ROOT / "content" / f"{l}.json").exists()]
VER = str(int(time.time()))

# One line icon per section, in the order the h2 headings appear (sun, atom, compass)
ICONS = [
    '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    '<circle cx="12" cy="12" r="1.5"/><ellipse cx="12" cy="12" rx="10" ry="4"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(-60 12 12)"/>',
    '<circle cx="12" cy="12" r="10"/><path d="m16.2 7.8-2.1 6.3-6.3 2.1 2.1-6.3z"/>',
]


def typeset(t, lang):
    if lang != "uz":
        return t
    # Uzbek Latin: o‘ g‘ take the turned comma; every other apostrophe is the tutuq belgisi ʼ
    t = re.sub(r"([OoGg])['‘’`]", r"\1‘", t)
    return re.sub(r"['’`]", "ʼ", t)


def esc(s):
    return html.escape(s, quote=True)


def build(lang):
    c = json.loads((ROOT / "content" / f"{lang}.json").read_text())
    timing = json.loads((ROOT / "docs/audio" / lang / "timings.json").read_text())
    assert len(timing["segments"]) == len(c["segments"]), f"re-run build_audio.py {lang} after editing content/{lang}.json"
    prefix = "" if lang == DEFAULT else "../"

    h1, intro, cards = None, [], []
    for i, s in enumerate(c["segments"]):
        t = html.escape(typeset(s["text"], lang), quote=False)
        if s["type"] == "h1":
            h1 = f'<h1 class="seg" data-i="{i}">{t}</h1>'
        elif s["type"] == "h2":
            icon = ICONS[len(cards) % len(ICONS)]
            cards.append([f'<div class="icon" aria-hidden="true"><svg viewBox="0 0 24 24">{icon}</svg></div>',
                          f'<h2 class="seg" data-i="{i}">{t}</h2>'])
        else:
            cls = "seg quote" if s.get("emphasis") else "seg"
            (cards[-1] if cards else intro).append(f'<p class="{cls}" data-i="{i}">{t}</p>')

    body = ['<section class="intro">', '  <p class="eyebrow">VOSIQ</p>', *("  " + x for x in intro), "</section>"]
    for card in cards:
        body += ['<section class="card">', *("  " + x for x in card), "</section>"]

    switch = []
    for l in LANGS:
        lc = json.loads((ROOT / "content" / f"{l}.json").read_text())
        href = prefix + ("" if l == DEFAULT else f"{l}/")
        cur = ' aria-current="page"' if l == lang else ""
        switch.append(f'<a href="{href or "./"}" hreflang="{l}" lang="{l}" data-lang="{l}"{cur}>{lc["label"]}</a>')

    d = timing["duration"]
    minutes = str(max(1, round(d / 60)))
    ui = {k: esc(typeset(v, lang)) for k, v in c["ui"].items()}
    first_p = next(s["text"] for s in c["segments"] if s["type"] == "p")
    repl = {
        "LANG": lang, "P": prefix, "TITLE": esc(c["title"]), "SCHOOL": esc(c["school"]),
        "DESC": esc(typeset(first_p, lang)[:155]), "H1": h1,
        "BODY": "\n".join("    " + x for x in body), "SWITCH": "\n      ".join(switch),
        "DURATION": f"{d:.1f}", "DURSTR": f"{int(d)//60}:{int(d)%60:02d}",
        "VER": VER, "DEFAULT": DEFAULT,
        **{"UI_" + k.upper(): v.replace("{min}", minutes) for k, v in ui.items()},
    }
    page = (ROOT / "tools/template.html").read_text()
    for k, v in repl.items():
        page = page.replace("{{" + k + "}}", v)
    assert "{{" not in page, re.findall(r"\{\{\w+\}\}", page)
    out = ROOT / "docs" / (f"{lang}/index.html" if prefix else "index.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    print(out.relative_to(ROOT), len(page) // 1024, "KB")


for lang in LANGS:
    build(lang)
