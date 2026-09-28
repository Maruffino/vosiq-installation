"""Render docs/index.html from content.json + docs/audio/timings.json."""
import html, json, re, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
content = json.loads((ROOT / "content.json").read_text())
timing = json.loads((ROOT / "docs/audio/timings.json").read_text())
assert len(timing["segments"]) == len(content["segments"]), "re-run build_audio.py after editing content.json"


def typeset(t):
    # Uzbek Latin: o‘ g‘ take the turned comma; every other apostrophe is the tutuq belgisi ʼ
    t = re.sub(r"([OoGg])['‘’`]", r"\1‘", t)
    return re.sub(r"['’`]", "ʼ", t)


# One line icon per section, in the order the h2 headings appear (sun, atom, compass)
ICONS = [
    '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    '<circle cx="12" cy="12" r="1.5"/><ellipse cx="12" cy="12" rx="10" ry="4"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(-60 12 12)"/>',
    '<circle cx="12" cy="12" r="10"/><path d="m16.2 7.8-2.1 6.3-6.3 2.1 2.1-6.3z"/>',
]

h1, intro, cards = None, [], []
for i, s in enumerate(content["segments"]):
    t = html.escape(typeset(s["text"]), quote=False)
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
for c in cards:
    body += ['<section class="card">', *("  " + x for x in c), "</section>"]

d = timing["duration"]
first_p = next(s["text"] for s in content["segments"] if s["type"] == "p")
repl = {
    "TITLE": html.escape(content["title"]), "SCHOOL": html.escape(content["school"]),
    "DESC": html.escape(typeset(first_p)[:155]), "H1": h1,
    "BODY": "\n".join("    " + x for x in body),
    "DURATION": f"{d:.1f}", "DURSTR": f"{int(d)//60}:{int(d)%60:02d}", "MINUTES": str(max(1, round(d / 60))),
    "VER": str(int(time.time())),
}
page = (ROOT / "tools/template.html").read_text()
for k, v in repl.items():
    page = page.replace("{{" + k + "}}", v)
assert "{{" not in page
(ROOT / "docs/index.html").write_text(page)
print("docs/index.html", len(page) // 1024, "KB")
