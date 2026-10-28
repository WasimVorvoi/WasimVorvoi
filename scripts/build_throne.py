"""Builds assets/throne.svg: the animated throne hero for the GitHub profile README.

Drawn for GitHub's dark theme (#0d1117) so it blends into the page. The
achievements orbit the throne on a tilted ring: each one exists twice, a copy
behind the throne and a copy in front, and they hand off at the ring's sides
so the orbit reads as passing behind it.

Everything (photo, fonts) is inlined as base64 because GitHub renders README
SVGs as <img>, which can't load external resources.

    python scripts/build_throne.py
"""
import base64
import io
import math
import re
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
AVATAR = ROOT / "assets" / "avatar.jpg"
OUT = ROOT / "assets" / "throne.svg"

W, H = 1000, 600
BG = "#0d1117"          # GitHub dark canvas
INK = "#c9d1d9"         # line art
TEXT = "#e6edf3"
MUTED = "#8d96a0"

CX = 500
AV_Y, AV_R = 262, 60

NAME = "Wasim Vorvoi"
TAGLINE = "Builds where AI, security and hardware meet"

# orbit
O_CX, O_CY = 500, 360
O_RX, O_RY = 395, 150
O_TILT = math.radians(-7)
PERIOD = 80          # seconds per revolution
SAMPLES = 72

ACHIEVEMENTS = [
    ("9× hackathon winner", "prizes at 9 of 16 events"),
    ("AI Engineer at VividSense", "$15K raised for assistive tech"),
    ("Top 2%, Garden State CTF", "cyber competition run by NJCCIC"),
    ("Public Choice, HackJPS", "DocLAB, 2026"),
    ("Co-CEO of Atmosphere", "AI for Roblox Studio"),
    ("NJCCIC cyber intern", "summer 2026"),
    ("1st of 44 teams", "Dexarm prosthetic at LaunchSB"),
    ("86% deepfake detection", "Vauxguard voice research"),
]

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


def mono_avatar():
    im = ImageOps.grayscale(Image.open(AVATAR)).crop((55, 25, 305, 275))   # face, not the room
    im = ImageOps.autocontrast(im, cutoff=1).point(lambda v: 255 * (v / 255) ** 0.72)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86, optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def orbit_point(theta):
    """Point on the tilted ring; sin(theta) > 0 is the near (front) half."""
    x, y = O_RX * math.cos(theta), O_RY * math.sin(theta)
    return (O_CX + x * math.cos(O_TILT) - y * math.sin(O_TILT),
            O_CY + x * math.sin(O_TILT) + y * math.cos(O_TILT))


def ring_half(front):
    pts = []
    for k in range(121):
        t = math.pi * k / 120 + (0 if front else math.pi)
        pts.append("%.1f %.1f" % orbit_point(t))
    return "M" + " L".join(pts)


def orbiters(front):
    """One copy of every achievement; `front` copies are visible on the near half only."""
    thetas = [2 * math.pi * k / SAMPLES for k in range(SAMPLES + 1)]
    pos = ";".join("%.1f %.1f" % orbit_point(t) for t in thetas)
    scale = ";".join("%.3f" % (0.84 + 0.16 * math.sin(t)) for t in thetas)
    op = []
    for t in thetas:
        s = math.sin(t)
        visible = (s >= 0) if front else (s < 0)
        op.append("%.2f" % ((0.62 + 0.38 * s) if front else (0.62 + 0.25 * s)) if visible else "0")
    op = ";".join(op)

    out = []
    n = len(ACHIEVEMENTS)
    for i, (title, sub) in enumerate(ACHIEVEMENTS):
        begin = -PERIOD * i / n
        a = f'dur="{PERIOD}s" begin="{begin:.2f}s" repeatCount="indefinite"'
        out.append(f'''<g opacity="0">
  <animateTransform attributeName="transform" type="translate" values="{pos}" {a}/>
  <animate attributeName="opacity" values="{op}" {a}/>
  <g><animateTransform attributeName="transform" type="scale" values="{scale}" {a}/>
    <circle r="3" class="node"/>
    <text y="-26" class="ot">{title}</text>
    <text y="-10" class="os">{sub}</text>
  </g>
</g>''')
    return "\n".join(out)


def apron_arches(x0, x1, y, h, n):
    w = (x1 - x0) / n
    d = []
    for i in range(n):
        a = x0 + i * w + 3
        b = a + w - 6
        m = (a + b) / 2
        d.append(f"M{a:.1f} {y + h}V{y + h * .45:.1f}Q{a:.1f} {y + 4} {m:.1f} {y + 3}Q{b:.1f} {y + 4} {b:.1f} {y + h * .45:.1f}V{y + h}")
    return "".join(d)


def build():
    avatar = mono_avatar()
    fonts = (font_face("UnifrakturMaguntia", 400, NAME, "Frak")
             + font_face("Schibsted Grotesk", 600, "".join(t for t, _ in ACHIEVEMENTS), "SchibstedB")
             + font_face("Schibsted Grotesk", 400, TAGLINE + "".join(s for _, s in ACHIEVEMENTS), "Schibsted"))

    back_arch = "M372 478V214C372 142 444 104 500 58C556 104 628 142 628 214V478Z"
    inner_arch = "M390 468V220C390 158 452 122 500 84C548 122 610 158 610 220V468Z"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Wasim Vorvoi on a throne, with achievements orbiting around him">
<title>Wasim Vorvoi</title>
<style>
{fonts}
.name{{font-family:'Frak',serif;font-size:64px;fill:url(#chrome)}}
.tag{{font-family:'Schibsted',sans-serif;font-size:15px;fill:{MUTED}}}
.ot{{font-family:'SchibstedB',sans-serif;font-weight:600;font-size:16px;fill:{TEXT};text-anchor:middle;paint-order:stroke;stroke:{BG};stroke-width:8px;stroke-linejoin:round}}
.os{{font-family:'Schibsted',sans-serif;font-size:12.5px;fill:{MUTED};text-anchor:middle;paint-order:stroke;stroke:{BG};stroke-width:6px;stroke-linejoin:round}}
.node{{fill:{TEXT}}}
.line{{fill:none;stroke:{INK};stroke-width:1.5;stroke-linejoin:round}}
.fine{{fill:none;stroke:{INK};stroke-width:.8;opacity:.55}}
.solid{{fill:{BG};stroke:{INK};stroke-width:1.5;stroke-linejoin:round}}
.halo{{animation:hover 5s ease-in-out infinite}}
@keyframes hover{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-5px)}}}}
@media (prefers-reduced-motion:reduce){{.halo{{animation:none}}}}
</style>
<defs>
  <linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset=".42" stop-color="#c9d1d9"/>
    <stop offset=".5" stop-color="#57606a"/><stop offset=".56" stop-color="#e6edf3"/>
    <stop offset="1" stop-color="#8b949e"/>
  </linearGradient>
  <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="#6e7681"/><stop offset="1" stop-color="#e6edf3"/>
  </linearGradient>
  <radialGradient id="aura" cx="{CX}" cy="{AV_Y}" r="300" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#e6edf3" stop-opacity=".10"/><stop offset=".55" stop-color="#e6edf3" stop-opacity=".03"/><stop offset="1" stop-color="#e6edf3" stop-opacity="0"/>
  </radialGradient>
  <pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(90)">
    <path d="M0 0V7" stroke="{INK}" stroke-width=".7" opacity=".28"/>
  </pattern>
  <clipPath id="av"><circle cx="{CX}" cy="{AV_Y}" r="{AV_R}"/></clipPath>
  <filter id="bloom" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="4"/></filter>
</defs>

<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#aura)"/>

<!-- far half of the ring, then the achievements behind the throne -->
<path d="{ring_half(False)}" class="fine" stroke-dasharray="2 6"/>
{orbiters(front=False)}

<!-- throne: spires -->
<g class="solid">
  <path d="M348 484V176L360 120L372 176V484Z"/>
  <path d="M628 484V176L640 120L652 176V484Z"/>
</g>
<path d="M360 104l3 9 9 3-9 3-3 9-3-9-9-3 9-3zM640 104l3 9 9 3-9 3-3 9-3-9-9-3 9-3z" fill="{TEXT}"/>
<path d="M354 200H366M354 300H366M354 400H366M634 200H646M634 300H646M634 400H646" class="fine"/>

<!-- throne: back -->
<path d="{back_arch}" class="solid"/>
<path d="{inner_arch}" fill="url(#hatch)"/>
<path d="{inner_arch}" class="fine"/>
<path d="M500 30l4 14 14 4-14 4-4 14-4-14-14-4 14-4z" fill="{TEXT}"/>
<path d="M500 58V30" class="fine"/>
<circle cx="{CX}" cy="{AV_Y}" r="{AV_R + 16}" fill="{BG}"/>
<circle cx="{CX}" cy="{AV_Y}" r="{AV_R + 16}" class="fine"/>
<circle cx="{CX}" cy="{AV_Y}" r="{AV_R + 11}" class="fine" stroke-dasharray="1 4"/>

<!-- avatar -->
<image x="{CX - AV_R}" y="{AV_Y - AV_R}" width="{AV_R * 2}" height="{AV_R * 2}" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{avatar}" xlink:href="data:image/jpeg;base64,{avatar}"/>
<circle cx="{CX}" cy="{AV_Y}" r="{AV_R}" fill="none" stroke="url(#ring)" stroke-width="3"/>

<!-- halo -->
<g class="halo">
  <ellipse cx="{CX}" cy="{AV_Y - AV_R - 26}" rx="46" ry="9" fill="none" stroke="#ffffff" stroke-width="3" opacity=".5" filter="url(#bloom)"/>
  <ellipse cx="{CX}" cy="{AV_Y - AV_R - 26}" rx="46" ry="9" fill="none" stroke="#f0f6fc" stroke-width="1.6"/>
</g>

<!-- throne: arms, seat, apron, legs -->
<g class="solid">
  <path d="M322 366H392V382H322Z"/><circle cx="322" cy="374" r="12"/>
  <path d="M608 366H678V382H608Z"/><circle cx="678" cy="374" r="12"/>
  <path d="M332 382H350V478H332Z"/><path d="M650 382H668V478H650Z"/>
  <path d="M362 404H638V434H362Z"/>
  <path d="M366 434H634V474H366Z"/>
  <path d="M372 474H394L390 496H376Z"/><path d="M606 474H628L624 496H610Z"/>
</g>
<circle cx="322" cy="374" r="5" class="fine"/><circle cx="678" cy="374" r="5" class="fine"/>
<path d="M370 412H630" class="fine"/>
<path d="{apron_arches(372, 628, 438, 32, 10)}" class="fine"/>

<!-- dais -->
<g class="solid">
  <path d="M312 496H688V514H312Z"/>
  <path d="M290 514H710V532H290Z"/>
  <path d="M268 532H732V552H268Z"/>
</g>
<path d="M320 505H680M298 523H702M276 542H724" class="fine" stroke-dasharray="1 5"/>

<!-- near half of the ring, then the achievements in front -->
<path d="{ring_half(True)}" class="fine" stroke-dasharray="2 6"/>
{orbiters(front=True)}

<!-- name -->
<text x="{CX}" y="584" text-anchor="middle" class="tag">{TAGLINE}</text>
<text x="40" y="78" class="name">{NAME.split()[0]}</text>
<text x="{W - 40}" y="78" text-anchor="end" class="name">{NAME.split()[1]}</text>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    build()
