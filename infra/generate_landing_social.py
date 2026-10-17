"""Regenerate the packaged landing-page social preview from saved evidence."""

import json
from itertools import pairwise
from pathlib import Path

from matplotlib import get_data_path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
fonts = Path(get_data_path()) / "fonts/ttf"
f = lambda size, bold=False: ImageFont.truetype(
    str(fonts / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")), size
)
im = Image.new("RGB", (1200, 630), "#f7f9fc")
d = ImageDraw.Draw(im)
d.rounded_rectangle((45, 45, 90, 90), 12, fill="#315dee")
d.text((108, 42), "Querylane.", font=f(35, True), fill="#18283b")
d.text((55, 158), "From business questions", font=f(43, True), fill="#18283b")
d.text((55, 215), "to evidence-backed", font=f(43, True), fill="#315dee")
d.text((55, 272), "decisions.", font=f(43, True), fill="#18283b")
d.text(
    (58, 365), "Advanced reports. Validated predictions.", font=f(21), fill="#596a82"
)
d.text((58, 400), "Conversational voice BI.", font=f(21), fill="#596a82")
d.rounded_rectangle((55, 488, 325, 548), 10, fill="#315dee")
d.text((78, 502), "Open Querylane →", font=f(23, True), fill="white")
d.text(
    (58, 578), "No sign-up · Public synthetic retail demo", font=f(16), fill="#596a82"
)
d.rounded_rectangle((730, 110, 1150, 527), 16, fill="white", outline="#dbe2ed", width=2)
d.text((755, 138), "SAVED FORECAST EXAMPLE", font=f(13, True), fill="#176f69")
d.text((755, 181), "Monthly revenue · USD", font=f(20, True), fill="#18283b")
points = json.loads((root / "Frontend/src/lib/landing-preview-data.json").read_text())[
    "points"
]
coords = [
    (
        760 + i * 31,
        425
        - (p["observed"] if p["observed"] is not None else p["forecast"]) / 16e6 * 170,
    )
    for i, p in enumerate(points)
]
for v in [4, 8, 12, 16]:
    y = 425 - v / 16 * 170
    d.line((753, y, 1120, y), fill="#e5eaf3", width=1)
d.line(coords[:9], fill="#315dee", width=4)
for a, b in pairwise(coords[8:]):
    for t in range(0, 10, 2):
        segment = [
            (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
            for u in (t / 10, (t + 1) / 10)
        ]
        d.line(segment, fill="#176f69", width=4)
d.text((755, 448), "Observed —   Forecast - -", font=f(15), fill="#596a82")
d.text((755, 483), "Cutoff: Sep 30, 2026 · No intervals", font=f(12), fill="#596a82")
im.save(root / "Frontend/public/querylane-social.png", optimize=True)
