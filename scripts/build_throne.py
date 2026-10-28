"""Builds assets/throne.svg: animated throne hero for the GitHub profile README.

Everything (photo, fonts) is inlined as base64 because GitHub renders README
SVGs as <img>, which can't load external resources.

    python scripts/build_throne.py
"""
import base64
import random
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AVATAR = ROOT / "assets" / "avatar.jpg"
OUT = ROOT / "assets" / "throne.svg"

W, H = 1000, 680
CX = 500          # throne centre line
AV_Y = 275        # avatar centre (after throne offset)
AV_R = 66
CARD_W = 262

TITLE = "WASIM VORVOI"
SUBTITLE = "AI  ·  SECURITY  ·  HARDWARE"
FOOTER = "SOUTH BRUNSWICK, NJ  ·  9 WINS / 16 HACKATHONS  ·  BUILT IN 24 HOURS"

# (title, subtitle, icon)
LEFT = [
    ("9× Hackathon Winner", "prizes at 9 of 16 events", "trophy"),
    ("Public Choice", "HackJPS 2026 · DocLAB", "star"),
    ("Most Innovative", "HackTCNJ 2026 · WearWise", "bulb"),
    ("First Place", "LaunchSB · Dexarm, 44 teams", "medal"),
    ("AI Engineer", "VividSense · $15K raised", "eye"),
]
RIGHT = [
    ("Co-CEO", "Atmosphere · AI for Roblox", "planet"),
    ("Cyber Intern", "NJCCIC · 2026", "shield"),
    ("Top 2%", "Garden State Cyber CTF", "flag"),
    ("86% Accuracy", "Vauxguard deepfake research", "wave"),
    ("Anthropic Certified", "Claude Code in Action", "burst"),
]

# 24x24 stroke icons
ICONS = {
    "trophy": '<path d="M8 4h8v4a4 4 0 0 1-8 0z M8 5H5v1a3 3 0 0 0 3 3 M16 5h3v1a3 3 0 0 1-3 3 M12 12v4 M8 20h8 M10 16h4v4"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    "bulb": '<path d="M9 18h6 M10 21h4 M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
    "medal": '<path d="M8 3l3 7 M16 3l-3 7 M8 3h8"/><circle cx="12" cy="15" r="5"/><path d="M11 13.5l1.2-.8V17.5"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "planet": '<circle cx="12" cy="12" r="5"/><path d="M7.5 14.5C3.8 16.8 2.4 18.6 3.2 19.4c1.3 1.3 7.2-1.6 13.1-6.5s9.4-10 8.1-11.2c-.6-.6-2.2-.1-4.4 1.2"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z M9 12l2 2 4-4"/>',
    "flag": '<path d="M5 21V4 M5 4h12l-2.5 4.5L17 13H5"/>',
    "wave": '<path d="M3 12v0 M7 8v8 M11 4v16 M15 8v8 M19 10v4 M21 12v0"/>',
    "burst": '<path d="M12 2v20 M2 12h20 M4.9 4.9l14.2 14.2 M19.1 4.9L4.9 19.1"/>',
}

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")


def font_face(family, weight, text, alias):
    """Fetch a Google Font subset to exactly `text` and return an @font-face rule."""
    q = urllib.parse.urlencode({"family": f"{family}:wght@{weight}", "text": text})
    req = urllib.request.Request(f"https://fonts.googleapis.com/css2?{q}", headers={"User-Agent": UA})
    css = urllib.request.urlopen(req).read().decode()
    url = re.search(r"url\((https://[^)]+)\)", css).group(1)
    data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA})).read()
    b64 = base64.b64encode(data).decode()
    return f"@font-face{{font-family:'{alias}';src:url(data:font/woff2;base64,{b64}) format('woff2');font-weight:{weight};}}"


def card(x, y, title, sub, icon, delay, side):
    w, h = CARD_W, 58
    # tether from the card's inner edge to the avatar
    tx = x + w if side == "L" else x
    ty = y + h / 2
    mx = (tx + CX) / 2
    tether = (f'<path class="tether" d="M{tx} {ty} Q{mx} {ty - 40} {CX} {AV_Y}" '
              f'style="animation-delay:{delay}s"/>')
    g = f'''<g transform="translate({x} {y})"><g class="bob" style="animation-delay:{delay}s">
  <rect class="card" width="{w}" height="{h}" rx="14"/>
  <rect class="card-shine" x="1" y="1" width="{w - 2}" height="{h / 2}" rx="13"/>
  <circle cx="30" cy="{h / 2}" r="19" fill="url(#gold)"/>
  <circle cx="30" cy="{h / 2}" r="19" class="icon-glow" style="animation-delay:{delay}s"/>
  <g transform="translate(19 {h / 2 - 11}) scale(0.92)" class="icon">{ICONS[icon]}</g>
  <text x="60" y="25" class="ct">{title}</text>
  <text x="60" y="43" class="cs">{sub}</text>
</g></g>'''
    return tether, g


def embers(rng, n=46):
    out = []
    for _ in range(n):
        x = rng.uniform(60, W - 60)
        r = rng.uniform(0.8, 2.4)
        dur = rng.uniform(6, 13)
        begin = -rng.uniform(0, dur)
        drift = rng.uniform(-40, 40)
        y0, y1 = rng.uniform(560, 660), rng.uniform(120, 300)
        col = rng.choice(["#ffd76a", "#ffb347", "#c9a2ff", "#ffe9a8"])
        out.append(
            f'<circle cx="{x:.0f}" cy="{y0:.0f}" r="{r:.1f}" fill="{col}" filter="url(#soft)">'
            f'<animate attributeName="cy" values="{y0:.0f};{y1:.0f}" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cx" values="{x:.0f};{x + drift:.0f};{x:.0f}" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;0.8;0" keyTimes="0;0.15;0.7;1" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
            f'</circle>')
    return "\n".join(out)


def twinkles(rng, n=22):
    out = []
    for _ in range(n):
        x, y = rng.uniform(30, W - 30), rng.uniform(20, 560)
        if 300 < x < 700 and y > 90:   # keep the throne area clean
            continue
        sc = rng.uniform(0.5, 1.1)
        dur = rng.uniform(2.5, 5)
        out.append(
            f'<path d="M0 -6Q0 0 6 0Q0 0 0 6Q0 0 -6 0Q0 0 0 -6z" fill="#fff4c7" '
            f'transform="translate({x:.0f} {y:.0f}) scale({sc:.2f})" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;0" dur="{dur:.1f}s" begin="{-rng.uniform(0, dur):.1f}s" repeatCount="indefinite"/></path>')
    return "\n".join(out)


def rays(n=28):
    out = []
    for i in range(n):
        a = 360 / n * i
        half = 2.2 if i % 2 else 4.2
        out.append(f'<path d="M0 0 L{-half * 7} -460 L{half * 7} -460 Z" transform="rotate({a})"/>')
    return "".join(out)


def runes(r, n, size):
    out = []
    glyphs = ["M0 -4v8 M-3 -1l3 -3 3 3", "M-3 -4l6 8 M3 -4l-6 8", "M0 -4v8 M0 0l3 -3", "M-3 4l3 -8 3 8",
              "M-3 -4h6 M0 -4v8", "M-3 0h6 M0 -4l3 4 -3 4"]
    for i in range(n):
        a = 360 / n * i
        out.append(f'<path d="{glyphs[i % len(glyphs)]}" transform="rotate({a}) translate(0 {-r}) scale({size})"/>')
    return "".join(out)


def build():
    rng = random.Random(7)
    avatar_b64 = base64.b64encode(AVATAR.read_bytes()).decode()

    all_cards = LEFT + RIGHT
    cinzel_text = TITLE + SUBTITLE + "".join(t for t, _, _ in all_cards)
    raj_text = FOOTER + "".join(s for _, s, _ in all_cards)
    fonts = (font_face("Cinzel", 700, "".join(sorted(set(cinzel_text))), "Cinzel")
             + font_face("Rajdhani", 600, "".join(sorted(set(raj_text))), "Rajdhani"))

    xs = [40, 18, 4, 18, 40]
    ys = [130, 210, 290, 370, 450]
    tethers, cards = [], []
    for i, (t, s, ic) in enumerate(LEFT):
        a, b = card(xs[i], ys[i], t, s, ic, -i * 1.1, "L")
        tethers.append(a); cards.append(b)
    for i, (t, s, ic) in enumerate(RIGHT):
        a, b = card(W - CARD_W - xs[i], ys[i], t, s, ic, -i * 1.1 - 0.55, "R")
        tethers.append(a); cards.append(b)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Wasim Vorvoi on a golden throne surrounded by achievements">
<title>Wasim Vorvoi</title>
<style>
{fonts}
.card{{fill:#120a22;fill-opacity:.88;stroke:url(#goldStroke);stroke-width:1.3}}
.card-shine{{fill:#fff;opacity:.04}}
.icon{{fill:none;stroke:#2a1600;stroke-width:2.1;stroke-linecap:round;stroke-linejoin:round}}
.icon-glow{{fill:none;stroke:#ffd76a;stroke-width:2;opacity:0;animation:ping 4.4s ease-out infinite}}
.ct{{font-family:'Cinzel',serif;font-weight:700;font-size:15px;fill:url(#goldText);letter-spacing:.4px}}
.cs{{font-family:'Rajdhani',sans-serif;font-weight:600;font-size:12.5px;fill:#b9a6d9;letter-spacing:.3px}}
.title{{font-family:'Cinzel',serif;font-weight:700;font-size:46px;letter-spacing:9px;fill:url(#shimmer)}}
.sub{{font-family:'Cinzel',serif;font-weight:700;font-size:13px;letter-spacing:5px;fill:#a78bdb}}
.foot{{font-family:'Rajdhani',sans-serif;font-weight:600;font-size:13px;letter-spacing:3px;fill:#7d6aa3}}
.tether{{fill:none;stroke:#ffcf5a;stroke-width:1.2;stroke-dasharray:3 9;opacity:.45;animation:flow 3s linear infinite}}
.bob{{animation:bob 6s ease-in-out infinite}}
.crown{{animation:bob 4s ease-in-out infinite}}
.pulse{{animation:pulse 3.2s ease-in-out infinite}}
@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-9px)}}}}
@keyframes flow{{to{{stroke-dashoffset:-120}}}}
@keyframes pulse{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
@keyframes ping{{0%{{opacity:.9;r:19px}}60%,100%{{opacity:0;r:30px}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<defs>
  <radialGradient id="bg" cx="50%" cy="42%" r="75%">
    <stop offset="0" stop-color="#2b1250"/><stop offset=".45" stop-color="#150a2b"/><stop offset="1" stop-color="#06030d"/>
  </radialGradient>
  <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff4c7"/><stop offset=".35" stop-color="#f6c94f"/><stop offset=".7" stop-color="#c58b14"/><stop offset="1" stop-color="#7a4f06"/>
  </linearGradient>
  <linearGradient id="goldH" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#8a5a08"/><stop offset=".5" stop-color="#ffe08a"/><stop offset="1" stop-color="#8a5a08"/>
  </linearGradient>
  <linearGradient id="goldStroke" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffe08a"/><stop offset=".5" stop-color="#7a4f06" stop-opacity=".6"/><stop offset="1" stop-color="#ffd76a"/>
  </linearGradient>
  <linearGradient id="goldText" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff1c2"/><stop offset="1" stop-color="#f0b93a"/>
  </linearGradient>
  <linearGradient id="shimmer" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">
    <stop offset="0" stop-color="#d79a1e"/><stop offset=".42" stop-color="#f6c94f"/><stop offset=".5" stop-color="#fffbe6"/><stop offset=".58" stop-color="#f6c94f"/><stop offset="1" stop-color="#d79a1e"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-{W} 0;{W} 0" dur="5s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="velvet" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#5b1f8f"/><stop offset=".6" stop-color="#3a0f63"/><stop offset="1" stop-color="#1e0636"/>
  </linearGradient>
  <linearGradient id="stone" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2a1f3d"/><stop offset="1" stop-color="#120c1e"/>
  </linearGradient>
  <radialGradient id="rayFade" cx="0" cy="0" r="460" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#ffd76a" stop-opacity=".55"/><stop offset=".5" stop-color="#b57bff" stop-opacity=".16"/><stop offset="1" stop-color="#b57bff" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="aura">
    <stop offset="0" stop-color="#ffe7a0" stop-opacity=".9"/><stop offset=".35" stop-color="#f6b93b" stop-opacity=".45"/><stop offset="1" stop-color="#8a3dff" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="floorGlow">
    <stop offset="0" stop-color="#b57bff" stop-opacity=".5"/><stop offset="1" stop-color="#b57bff" stop-opacity="0"/>
  </radialGradient>
  <pattern id="tuft" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="11" cy="11" r="1.6" fill="#f6c94f" opacity=".55"/>
    <path d="M0 0L11 11L22 0M0 22L11 11L22 22" stroke="#000" stroke-opacity=".25" fill="none"/>
  </pattern>
  <filter id="soft" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="1.2"/></filter>
  <filter id="blur18" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="18"/></filter>
  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <clipPath id="av"><circle cx="{CX}" cy="{AV_Y}" r="{AV_R}"/></clipPath>
</defs>

<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>

<!-- god rays -->
<g transform="translate({CX} {AV_Y})" fill="url(#rayFade)">
  <g>{rays()}<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="90s" repeatCount="indefinite"/></g>
</g>
<circle cx="{CX}" cy="{AV_Y}" r="190" fill="url(#aura)" class="pulse" filter="url(#blur18)"/>

<!-- floor magic circle -->
<ellipse cx="{CX}" cy="588" rx="380" ry="60" fill="url(#floorGlow)"/>
<g transform="translate({CX} 588) scale(1 .165)" fill="none" stroke="#c9a2ff" stroke-linecap="round">
  <g stroke-width="5" opacity=".55">
    <circle r="330" stroke-dasharray="2 18"/><circle r="300"/>
    <g stroke-width="7">{runes(315, 36, 2.2)}</g>
    <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="60s" repeatCount="indefinite"/>
  </g>
  <g stroke-width="5" opacity=".4" stroke="#ffd76a">
    <circle r="250" stroke-dasharray="40 14 4 14"/>
    <path d="M0 -250L216 125L-216 125Z M0 250L-216 -125L216 -125Z"/>
    <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="45s" repeatCount="indefinite"/>
  </g>
</g>

<!-- energy tethers -->
{"".join(tethers)}

<!-- throne -->
<g transform="translate(0 20)">
  <!-- dais -->
  <rect x="300" y="495" width="400" height="22" rx="3" fill="url(#stone)"/>
  <rect x="270" y="517" width="460" height="22" rx="3" fill="url(#stone)"/>
  <rect x="240" y="539" width="520" height="24" rx="3" fill="url(#stone)"/>
  <path d="M300 495h400M270 517h460M240 539h520" stroke="url(#goldH)" stroke-width="2"/>
  <path d="M458 495h84l10 68h-104z" fill="#6d1238"/>
  <path d="M458 495h84l10 68h-104z" fill="none" stroke="#f6c94f" stroke-width="1.5" opacity=".8"/>

  <!-- side spires -->
  <g fill="url(#gold)" filter="url(#glow)">
    <rect x="358" y="150" width="24" height="320" rx="4"/>
    <rect x="618" y="150" width="24" height="320" rx="4"/>
    <path d="M370 102l14 48h-28z M630 102l14 48h-28z"/>
    <circle cx="370" cy="98" r="7"/><circle cx="630" cy="98" r="7"/>
  </g>
  <!-- back -->
  <path d="M380 440V190q0-40 40-50l35-20q45-50 90 0l35 20q40 10 40 50v250z" fill="url(#gold)" filter="url(#glow)"/>
  <path d="M398 432V198q0-33 32-40l32-16q38-40 76 0l32 16q32 7 32 40v234z" fill="url(#velvet)"/>
  <path d="M398 432V198q0-33 32-40l32-16q38-40 76 0l32 16q32 7 32 40v234z" fill="url(#tuft)"/>
  <!-- crest gem -->
  <g filter="url(#glow)">
    <path d="M500 66l18 22-18 24-18-24z" fill="#b57bff" stroke="#fff4c7" stroke-width="2"/>
    <path d="M500 66l6 22-6 24-6-24z" fill="#fff" opacity=".35"/>
  </g>
</g>

<!-- halo + avatar (drawn without the throne offset, AV_Y already accounts for it) -->
<g transform="translate({CX} {AV_Y})" fill="none" stroke="#ffd76a">
  <g opacity=".85">
    <circle r="86" stroke-width="1.5" stroke-dasharray="1 7"/>
    <circle r="80" stroke-width="1" opacity=".5"/>
    <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="24s" repeatCount="indefinite"/>
  </g>
</g>
<circle cx="{CX}" cy="{AV_Y}" r="{AV_R + 10}" fill="#ffd76a" opacity=".35" filter="url(#blur18)" class="pulse"/>
<image x="{CX - AV_R}" y="{AV_Y - AV_R}" width="{AV_R * 2}" height="{AV_R * 2}" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{avatar_b64}" xlink:href="data:image/jpeg;base64,{avatar_b64}"/>
<circle cx="{CX}" cy="{AV_Y}" r="{AV_R}" fill="none" stroke="url(#gold)" stroke-width="6"/>
<circle cx="{CX}" cy="{AV_Y}" r="{AV_R + 5}" fill="none" stroke="#fff4c7" stroke-width="1" opacity=".6"/>

<!-- floating crown -->
<g class="crown">
  <g transform="translate({CX} {AV_Y - AV_R - 18})" filter="url(#glow)">
    <path d="M-30 12L-34 -14L-16 -2L0 -22L16 -2L34 -14L30 12Z" fill="url(#gold)" stroke="#fff4c7" stroke-width="1"/>
    <rect x="-31" y="10" width="62" height="7" rx="2" fill="url(#gold)"/>
    <circle cx="0" cy="0" r="3.5" fill="#d6304f"/><circle cx="-18" cy="4" r="2.5" fill="#6fb6ff"/><circle cx="18" cy="4" r="2.5" fill="#6fb6ff"/>
    <circle cx="-34" cy="-15" r="2.5" fill="#fff4c7"/><circle cx="34" cy="-15" r="2.5" fill="#fff4c7"/><circle cx="0" cy="-23" r="3" fill="#fff4c7"/>
  </g>
</g>

<!-- seat + arms (in front of avatar's lower edge) -->
<g transform="translate(0 20)">
  <rect x="368" y="398" width="264" height="34" rx="12" fill="url(#velvet)" stroke="#f6c94f" stroke-width="1.5"/>
  <path d="M362 430h276v36q0 8-8 8H370q-8 0-8-8z" fill="url(#gold)"/>
  <path d="M380 452h240" stroke="#7a4f06" stroke-width="2" stroke-dasharray="10 6"/>
  <circle cx="500" cy="452" r="8" fill="#b57bff" stroke="#fff4c7" stroke-width="1.5"/>
  <g fill="url(#gold)" filter="url(#glow)">
    <rect x="318" y="350" width="80" height="17" rx="8"/>
    <rect x="602" y="350" width="80" height="17" rx="8"/>
    <circle cx="322" cy="358" r="13"/><circle cx="678" cy="358" r="13"/>
    <rect x="330" y="366" width="18" height="108" rx="4"/>
    <rect x="652" y="366" width="18" height="108" rx="4"/>
    <path d="M362 474h26l-4 22h-18z M612 474h26l-4 22h-18z"/>
  </g>
  <circle cx="322" cy="358" r="5" fill="#b57bff"/><circle cx="678" cy="358" r="5" fill="#b57bff"/>
</g>

<!-- achievements -->
{"".join(cards)}

<!-- twinkles + embers -->
{twinkles(rng)}
{embers(rng)}

<!-- title -->
<text x="{CX}" y="56" text-anchor="middle" class="title">{TITLE}</text>
<text x="{CX}" y="84" text-anchor="middle" class="sub">{SUBTITLE}</text>
<text x="{CX}" y="664" text-anchor="middle" class="foot">{FOOTER}</text>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="21" fill="none" stroke="url(#goldStroke)" stroke-width="1.5" opacity=".7"/>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    build()
