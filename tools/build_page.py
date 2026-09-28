"""Render docs/index.html from content.json + docs/audio/timings.json."""
import html, json, math, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
content = json.loads((ROOT / "content.json").read_text())
timing = json.loads((ROOT / "docs/audio/timings.json").read_text())
assert len(timing["segments"]) == len(content["segments"]), "re-run build_audio.py after editing content.json"

import re
def typeset(t):
    # Uzbek Latin: o‘ g‘ take the turned comma; every other apostrophe is the tutuq belgisi ʼ
    t = re.sub(r"([OoGg])['‘’`]", r"\1‘", t)
    return re.sub(r"['’`]", "ʼ", t)

body = []
for i, s in enumerate(content["segments"]):
    t = html.escape(typeset(s["text"]), quote=False)
    tag = s["type"]
    cls = "seg quote" if s.get("emphasis") else "seg"
    body.append(f'    <{tag} class="{cls}" data-i="{i}">{t}</{tag}>')

def ellipse_path(rot):
    # 140x46 ellipse rotated by `rot` degrees, as a path CSS offset-path can follow
    pts = []
    for k in range(73):
        a = 2 * math.pi * k / 72
        x, y = 140 * math.cos(a), 46 * math.sin(a)
        r = math.radians(rot)
        pts.append(f"{x*math.cos(r)-y*math.sin(r):.1f},{x*math.sin(r)+y*math.cos(r):.1f}")
    return "M" + " L".join(pts) + "Z"

# faceted sun: a hexagon split into six triangles, alternating tones for a cut-crystal read
R, facets = 38, []
tones = ["#f3dfa2", "#e2b04a", "#c8922f", "#f0cf78", "#b9832a", "#e8bf5c"]
for k in range(6):
    a1, a2 = math.radians(60 * k - 90), math.radians(60 * (k + 1) - 90)
    facets.append(f'<path d="M0,0 L{R*math.cos(a1):.1f},{R*math.sin(a1):.1f} L{R*math.cos(a2):.1f},{R*math.sin(a2):.1f}Z" fill="{tones[k]}"/>')
inner = 17
for k in range(6):
    a1, a2 = math.radians(60 * k - 60), math.radians(60 * (k + 1) - 60)
    facets.append(f'<path d="M0,0 L{inner*math.cos(a1):.1f},{inner*math.sin(a1):.1f} L{inner*math.cos(a2):.1f},{inner*math.sin(a2):.1f}Z" fill="{tones[(k+3)%6]}" opacity=".85"/>')
facets_svg = '<g stroke="#0e1640" stroke-width=".6" stroke-linejoin="round">' + "".join(facets) + "</g>"

rays = []
for k in range(36):
    a = math.radians(k * 10)
    r1, r2 = 50, (118 if k % 3 == 0 else 84)
    rays.append(f'<line x1="{r1*math.cos(a):.1f}" y1="{r1*math.sin(a):.1f}" x2="{r2*math.cos(a):.1f}" y2="{r2*math.sin(a):.1f}"/>')

d = timing["duration"]
first_p = next(s["text"] for s in content["segments"] if s["type"] == "p")
repl = {
    "TITLE": html.escape(content["title"]), "SCHOOL": html.escape(content["school"]),
    "DESC": html.escape(first_p[:155]), "BODY": "\n".join(body),
    "RAYS": "".join(rays), "FACETS": facets_svg,
    "O1": ellipse_path(0), "O2": ellipse_path(60), "O3": ellipse_path(-60),
    "DURATION": f"{d:.1f}", "DURSTR": f"{int(d)//60}:{int(d)%60:02d}", "MINUTES": str(max(1, round(d / 60))),
    "VER": str(int(time.time())),
}
page = (ROOT / "tools/template.html").read_text()
for k, v in repl.items():
    page = page.replace("{{" + k + "}}", v)
assert "{{" not in page
(ROOT / "docs/index.html").write_text(page)
print("docs/index.html", len(page) // 1024, "KB")
