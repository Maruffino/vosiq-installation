"""Write qr/qr.svg (for print) and qr/qr.png (for preview) for the given URL."""
import sys
from pathlib import Path

import qrcode
import qrcode.image.svg

url = sys.argv[1]
out = Path(__file__).resolve().parent.parent / "qr"
out.mkdir(exist_ok=True)
# M = 15% error correction, enough for a laminated label; the URL stays short so the modules stay large
kw = dict(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
qrcode.make(url, image_factory=qrcode.image.svg.SvgPathFillImage, **kw).save(out / "qr.svg")
qrcode.make(url, box_size=20, **kw).save(out / "qr.png")
print(url, "->", out)
