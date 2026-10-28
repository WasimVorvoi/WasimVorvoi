"""Builds assets/hero.svg: the README header, a halftone portrait beside my name.

The subject is cut out of the selfie with GrabCut and redrawn as a dot screen,
so there's no room behind him and nothing to compress badly. Static on purpose.
Fonts are inlined as base64 because GitHub renders README SVGs as <img>.

    python scripts/build_hero.py
"""
import base64
import re
import urllib.parse
import urllib.request
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
PHOTO = Path.home() / "Downloads" / "WasimPic.png"
OUT = ROOT / "assets" / "hero.svg"

W, H = 1000, 470
BG = "#0d1117"
DOT = "#b1bac4"

NAME = "wasim vorvoi"
LINES = ["ai, security and hardware", "south brunswick, new jersey"]

# dot grid over the crop of the photo that holds the subject
N, STEP, X0, Y0 = 114, 4.0, 70, 12
BOX = (60, 230, 1340, 1510)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")


def font_face(family, weight, text, alias):
    """Fetch a Google Font subset to exactly `text` and return an @font-face rule."""
    q = urllib.parse.urlencode({"family": f"{family}:wght@{weight}", "text": "".join(sorted(set(text)))})
    req = urllib.request.Request(f"https://fonts.googleapis.com/css2?{q}", headers={"User-Agent": UA})
    css = urllib.request.urlopen(req).read().decode()
    url = re.search(r"url\((https://[^)]+)\)", css).group(1)
    data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA})).read()
    b64 = base64.b64encode(data).decode()
    return f"@font-face{{font-family:'{alias}';src:url(data:font/woff2;base64,{b64}) format('woff2');font-weight:{weight};}}"


def person_mask():
    """GrabCut the subject out of the selfie (walls marked as background)."""
    img = cv2.imread(str(PHOTO))
    sc = 0.5
    small = cv2.resize(img, None, fx=sc, fy=sc)
    mask = np.full(small.shape[:2], cv2.GC_BGD, np.uint8)

    def mark(x0, y0, x1, y1, v):
        mask[int(y0 * sc):int(y1 * sc), int(x0 * sc):int(x1 * sc)] = v
    mark(40, 250, 1300, 1960, cv2.GC_PR_FGD)
    mark(0, 250, 430, 1080, cv2.GC_BGD)
    mark(1050, 250, 1440, 1060, cv2.GC_BGD)
    mark(560, 420, 900, 1000, cv2.GC_FGD)
    mark(300, 1300, 1100, 1800, cv2.GC_FGD)
    cv2.grabCut(small, mask, None, np.zeros((1, 65)), np.zeros((1, 65)), 8, cv2.GC_INIT_WITH_MASK)
    m = np.where((mask == 1) | (mask == 3), 255, 0).astype("uint8")
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    m = cv2.GaussianBlur(cv2.resize(m, (img.shape[1], img.shape[0])), (21, 21), 0)
    return Image.fromarray(m)


def dots():
    mask = person_mask().crop(BOX)
    lum = ImageOps.autocontrast(ImageOps.grayscale(Image.open(PHOTO)).crop(BOX), cutoff=2, mask=mask).resize((N, N), Image.LANCZOS)
    keep = mask.resize((N, N), Image.LANCZOS)
    out = []
    for j in range(N):
        for i in range(N):
            k = keep.getpixel((i, j)) / 255
            b = lum.getpixel((i, j)) / 255
            r = k * (0.16 + 0.84 * b ** 0.55) * STEP * 0.56
            if r > 0.3:
                out.append(f'<circle cx="{X0 + i * STEP:.1f}" cy="{Y0 + j * STEP:.1f}" r="{r:.2f}"/>')
    return "".join(out)


def build():
    fonts = (font_face("Geist", 500, NAME, "Geist")
             + font_face("Geist Mono", 400, "".join(LINES), "GeistMono"))
    lines = "\n".join(f'<text x="563" y="{270 + 24 * i}" class="m"{" opacity=\".6\"" if i else ""}>{t}</text>'
                      for i, t in enumerate(LINES))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Wasim Vorvoi, halftone portrait">
<title>Wasim Vorvoi</title>
<style>{fonts}
.n{{font-family:'Geist',sans-serif;font-weight:500;font-size:58px;letter-spacing:-2px;fill:#f0f6fc}}
.m{{font-family:'GeistMono',monospace;font-size:14px;fill:#8d96a0}}
</style>
<rect width="{W}" height="{H}" fill="{BG}"/>
<g fill="{DOT}">{dots()}</g>
<text x="560" y="232" class="n">{NAME}</text>
{lines}
</svg>
'''
    OUT.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    build()
