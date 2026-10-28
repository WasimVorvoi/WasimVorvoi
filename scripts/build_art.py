"""Builds the animated README drawings into assets/:

    timeline.svg   every hackathon in order, the line draws itself on load
    gimdrone.svg   the caged drone, gimbal rings turning, props spinning
    dexarm.svg     the prosthetic hand closing and opening
    stack.svg      what I build with, as chips on a board with signals moving

Same palette and line weights as the skyline. Facts come from Devpost, the
VividSense site and the hackathon sheet, so check them before changing copy.

    python scripts/build_art.py
"""
import html
import math
from pathlib import Path

from svgkit import BG, DIM, INK, MUTED, PANEL, TEXT, font_face, text_of

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"


def fonts_for(body, mono=False):
    chars = text_of(body)
    out = (font_face("Schibsted Grotesk", 600, chars, "SchibstedB")
           + font_face("Schibsted Grotesk", 400, chars, "Schibsted"))
    if mono:
        out += font_face("Geist Mono", 500, chars, "GeistMono")
    return out


BASE_CSS = f"""
.h{{font-family:'SchibstedB',sans-serif;font-weight:600;fill:{TEXT}}}
.p{{font-family:'Schibsted',sans-serif;fill:{MUTED}}}
.line{{fill:none;stroke:{INK};stroke-width:1.5;stroke-linejoin:round;stroke-linecap:round}}
.fine{{fill:none;stroke:{INK};stroke-width:.8;opacity:.55}}
.solid{{fill:{BG};stroke:{INK};stroke-width:1.5;stroke-linejoin:round}}
"""


def write(name, w, h, label, css, body, mono=False, reduced=""):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{html.escape(label)}">
<title>{html.escape(label)}</title>
<style>
{fonts_for(body, mono)}
{BASE_CSS}
{css}
@media (prefers-reduced-motion:reduce){{{reduced}}}
</style>
<rect width="{w}" height="{h}" fill="{BG}"/>
{body}
</svg>
'''
    p = ASSETS / name
    p.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {p.name} ({p.stat().st_size / 1024:.0f} KB)")


def loop(values, dur, attr, begin=0.0, kind=None):
    """A repeating SMIL animation over `values` (a list of strings)."""
    v = ";".join(values)
    if kind:
        return (f'<animateTransform attributeName="transform" type="{kind}" values="{v}" '
                f'dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite"/>')
    return f'<animate attributeName="{attr}" values="{v}" dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'


# 1. Hackathon timeline ------------------------------------------------------

# In order. Months aren't known for every event, so the axis is the sequence,
# not the calendar. (event, year, project, award); award None = no prize.
EVENTS = [
    ("BRHS Hackathon", 2024, "Diabetes Logger", "Winner"),
    ("Secaucus Hacks", 2024, None, None),
    ("HackTCNJ", 2025, None, None),
    ("HackSB", 2025, "VerifAI", "Winner"),
    ("MontyHacks VIII", 2025, "Security SandBox", "Prize winner"),
    ("HackMHS X", 2025, None, None),
    ("hackPHS", 2025, "SproutShare", "2nd Place, Best .Tech"),
    ("HackTCNJ", 2026, "WearWise", "Most Innovative"),
    ("HackSB", 2026, "Clutch", "Winner"),
    ("HackJPS", 2026, "DocLAB", "Public Choice"),
    ("MontyHacks IX", 2026, "SproutGO", "Prize winner"),
    ("Hack for Humanity", 2026, None, None),
    ("HackNJX", 2026, None, None),
    ("Build Beyond", 2026, None, None),
    ("PeddieHacks", 2026, "AdaptFit", "HS Track 1 Prize"),
    ("hackPHS", 2026, "GimDrone", None),
]


def timeline():
    W, H = 1000, 360
    x0, x1, ly = 70, 930, 252
    draw_t, start = 3.0, 0.3
    n = len(EVENTS)
    wins = sum(1 for e in EVENTS if e[3])
    levels = [30, 66, 102, 138]

    parts = [
        f'<text x="40" y="52" class="h" font-size="28">{wins} wins at {n} hackathons</text>',
        f'<text x="40" y="76" class="p" font-size="13">From my first one in {EVENTS[0][1]} to the latest, in order</text>',
        f'<path d="M{x0} {ly}H{x1}" class="fine"/>',
        f'<path d="M{x0} {ly}H{x1}" class="line draw" stroke-dasharray="{x1 - x0}" stroke-dashoffset="{x1 - x0}" '
        f'style="animation-duration:{draw_t}s;animation-delay:{start}s"/>',
    ]
    k = 0
    prev_year = None
    for i, (event, year, project, award) in enumerate(EVENTS):
        x = x0 + (x1 - x0) * i / (n - 1)
        t = start + draw_t * i / (n - 1)
        if year != prev_year:
            # year marker: a taller tick and the year, under the line
            parts.append(f'<g class="pop" style="animation-delay:{t:.2f}s">'
                         f'<path d="M{x - 26:.1f} {ly + 50}V{ly + 84}" class="fine"/>'
                         f'<text x="{x - 20:.1f}" y="{ly + 82}" class="p" font-size="12">{year}</text></g>')
            prev_year = year
        name = f'<text x="0" y="0" class="p ev" font-size="10.5" transform="translate({x + 4:.1f} {ly + 14}) rotate(38)">{event}</text>'
        if award:
            h = levels[k % len(levels)]
            k += 1
            parts.append(
                f'<path d="M{x:.1f} {ly - 7}V{ly - h}" class="line draw" stroke-width="1" stroke-dasharray="{h}" stroke-dashoffset="{h}" '
                f'style="animation-duration:.45s;animation-delay:{t + .1:.2f}s"/>'
                f'<g class="pop" style="animation-delay:{t + .35:.2f}s">'
                f'<text x="{x:.1f}" y="{ly - h - 22}" class="h" font-size="13.5" text-anchor="middle">{project}</text>'
                f'<text x="{x:.1f}" y="{ly - h - 7}" class="p" font-size="11" text-anchor="middle">{award}</text></g>'
                f'<g class="pop" style="animation-delay:{t:.2f}s"><circle cx="{x:.1f}" cy="{ly}" r="5.5" fill="{TEXT}"/>{name}</g>')
        else:
            parts.append(f'<g class="pop" style="animation-delay:{t:.2f}s">'
                         f'<circle cx="{x:.1f}" cy="{ly}" r="3.6" fill="{BG}" stroke="{MUTED}" stroke-width="1.2"/>{name}</g>')

    # legend
    parts.append(f'<g class="pop" style="animation-delay:{start + draw_t:.2f}s">'
                 f'<circle cx="{W - 190}" cy="47" r="5" fill="{TEXT}"/><text x="{W - 178}" y="51" class="p" font-size="12">won a prize</text>'
                 f'<circle cx="{W - 96}" cy="47" r="3.6" fill="{BG}" stroke="{MUTED}" stroke-width="1.2"/><text x="{W - 84}" y="51" class="p" font-size="12">didn\'t</text></g>')

    css = """
.draw{animation-name:draw;animation-timing-function:ease-out;animation-fill-mode:forwards}
.pop{opacity:0;animation:pop .45s ease-out forwards}
.ev{fill:#6e7681}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes pop{to{opacity:1}}
"""
    write("timeline.svg", W, H, f"Timeline of {n} hackathons with {wins} prize wins", css, "\n".join(parts),
          reduced=".draw{animation:none;stroke-dashoffset:0}.pop{animation:none;opacity:1}")


# 2. GimDrone ------------------------------------------------------------------

def gimdrone():
    W, H = 1000, 440
    cx, cy, R = 290, 222, 168
    steps = 48

    def ring_vals(r, phase):
        """Apparent rx (or ry) of a circle of radius r turning about a screen axis, over one turn."""
        return ["%.1f" % (r * abs(math.cos(2 * math.pi * k / steps + phase))) for k in range(steps + 1)]

    p = []
    # outer cage: a sphere of meridians turning slowly about the vertical axis, plus fixed latitudes
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" class="line" stroke-width="1.2"/>')
    for lat in (-50, -22, 22, 50):
        y = cy - R * math.sin(math.radians(lat))
        rx = R * math.cos(math.radians(lat))
        p.append(f'<ellipse cx="{cx}" cy="{y:.1f}" rx="{rx:.1f}" ry="{rx * .16:.1f}" class="fine"/>')
    for m in range(6):
        p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{R}" ry="{R}" class="fine">'
                 f'{loop(ring_vals(R, math.pi * m / 6), 24, "rx")}</ellipse>')

    # gimbal: two rings, one rolling about the horizontal axis, one yawing about the vertical
    r1, r2 = R * .84, R * .74
    p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{r1:.1f}" ry="{r1:.1f}" fill="none" stroke="{TEXT}" stroke-width="2.2">'
             f'{loop(ring_vals(r1, 0), 9, "ry")}</ellipse>')
    p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{r2:.1f}" ry="{r2:.1f}" fill="none" stroke="{INK}" stroke-width="1.8">'
             f'{loop(ring_vals(r2, .9), 6.5, "rx")}</ellipse>')
    # pivots where the rings meet the cage and the drone
    for dx, dy in ((-r1, 0), (r1, 0)):
        p.append(f'<circle cx="{cx + dx:.1f}" cy="{cy + dy:.1f}" r="3.5" fill="{TEXT}"/>')

    # the drone, seen from slightly above, held level by the gimbal
    arms = [(-86, -18), (86, -18), (-86, 20), (86, 20)]
    d = [f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -3;0 0" dur="3.2s" repeatCount="indefinite"/>']
    for ax, ay in arms:
        d.append(f'<path d="M{cx} {cy}L{cx + ax} {cy + ay}" class="line" stroke-width="3" stroke="{INK}"/>')
    for i, (ax, ay) in enumerate(arms):
        mx, my = cx + ax, cy + ay
        d.append(f'<ellipse cx="{mx}" cy="{my - 6}" rx="40" ry="9" fill="{TEXT}" fill-opacity=".06" stroke="{INK}" stroke-width=".6" stroke-opacity=".5"/>')
        d.append(f'<rect x="{mx - 5}" y="{my - 6}" width="10" height="9" rx="2" class="solid" stroke-width="1.2"/>')
        sgn = 1 if i in (0, 3) else -1
        blade = []
        for k in range(13):
            a = sgn * 2 * math.pi * k / 12
            ux, uy = 39 * math.cos(a), 8.5 * math.sin(a)
            blade.append("M%.1f %.1fL%.1f %.1f" % (mx - ux, my - 6 - uy, mx + ux, my - 6 + uy))
        d.append(f'<path d="{blade[0]}" stroke="{TEXT}" stroke-width="2" stroke-linecap="round">'
                 f'<animate attributeName="d" values="{";".join(blade)}" dur=".3s" repeatCount="indefinite"/></path>')
    d.append(f'<rect x="{cx - 30}" y="{cy - 11}" width="60" height="22" rx="6" class="solid"/>')
    d.append(f'<rect x="{cx - 9}" y="{cy + 7}" width="18" height="10" rx="2" class="solid" stroke-width="1.2"/>')
    d.append(f'<circle cx="{cx}" cy="{cy + 12}" r="2.4" fill="{TEXT}"/>')
    d.append(f'<path d="M{cx + 14} {cy - 9}l10 -22" class="line" stroke-width="1"/>')
    d.append('</g>')
    p += d

    # callouts
    tx = 560
    p.append(f'<text x="{tx}" y="74" class="h" font-size="30">GimDrone</text>')
    p.append(f'<text x="{tx}" y="98" class="p" font-size="13.5">hackPHS 2026. A search-and-rescue FPV drone built to take</text>')
    p.append(f'<text x="{tx}" y="117" class="p" font-size="13.5">the crash instead of trying to avoid it. Our first hardware hack.</text>')
    notes = [
        ("250 mm cage", "3D printed PETG, reinforced with carbon fiber", (cx + R * .94, cy - R * .34)),
        ("GLRC F411 all-in-one", "Betaflight, ExpressLRS and the video transmitter on one board", (cx + 30, cy)),
        ("Two-ring gimbal", "the cage rolls off a wall while the drone stays level", (cx + r1 * .72, cy + r1 * .52)),
        ("Ground station", "a Raspberry Pi tracks AprilTags and steers through an ESP32-S3", None),
    ]
    for i, (title, sub, anchor) in enumerate(notes):
        y = 176 + i * 62
        p.append(f'<text x="{tx}" y="{y}" class="h" font-size="15">{title}</text>')
        p.append(f'<text x="{tx}" y="{y + 19}" class="p" font-size="12.5">{sub}</text>')
        if anchor:
            ax, ay = anchor
            p.append(f'<path d="M{ax:.1f} {ay:.1f}L{tx - 40} {y - 5}H{tx - 12}" class="fine" stroke-dasharray="2 4"/>'
                     f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="2.5" fill="{TEXT}"/>')
    write("gimdrone.svg", W, H, "GimDrone: a quadcopter inside a gimballed cage, props spinning", "", "\n".join(p))


# 3. Dexarm --------------------------------------------------------------------

def dexarm():
    W, H = 1000, 400
    dur = 6.0
    kt = "0;.14;.38;.62;.86;1"     # open, close, hold, open, rest

    def curl(angle):
        v = ";".join(f"{a} 0 0" for a in (0, 0, angle, angle, 0, 0))
        return (f'<animateTransform attributeName="transform" type="rotate" values="{v}" keyTimes="{kt}" dur="{dur}s" '
                f'calcMode="spline" keySplines="0 0 1 1;.5 0 .3 1;0 0 1 1;.5 0 .3 1;0 0 1 1" repeatCount="indefinite"/>')

    def seg(length, wdt, last=False):
        r = wdt / 2
        tip = f'<circle cx="{length - 4}" cy="0" r="1.6" fill="{TEXT}"/>' if last else ""
        return (f'<rect x="-{r * .4:.1f}" y="-{r:.1f}" width="{length + r * .4:.1f}" height="{wdt}" rx="{r * .9:.1f}" class="solid"/>'
                f'<circle cx="0" cy="0" r="{r * .42:.1f}" class="fine" style="opacity:.9"/>{tip}')

    def finger(x, y, lens, angles, wdt, depth):
        a1, a2, a3 = angles
        l1, l2, l3 = lens
        op = 1 - depth * .17
        return (f'<g transform="translate({x} {y})" opacity="{op:.2f}"><g>{curl(a1)}{seg(l1, wdt)}'
                f'<g transform="translate({l1} 0)"><g>{curl(a2)}{seg(l2, wdt * .94)}'
                f'<g transform="translate({l2} 0)"><g>{curl(a3)}{seg(l3, wdt * .88, True)}'
                f'</g></g></g></g></g></g>')

    p = []
    # forearm socket with servos and the cables that pull the fingers
    p.append('<path d="M40 150C120 140 220 148 300 160L306 262C220 274 120 282 40 276Z" class="solid"/>')
    p.append('<path d="M56 160C130 152 220 158 290 168M56 266C130 272 220 266 292 254" class="fine"/>')
    for x in (70, 136, 202):
        p.append(f'<rect x="{x}" y="190" width="52" height="30" rx="3" class="solid" stroke-width="1.2"/>'
                 f'<circle cx="{x + 14}" cy="205" r="7" class="fine" style="opacity:.9"/>'
                 f'<path d="M{x + 30} 198h14M{x + 30} 205h14M{x + 30} 212h9" class="fine"/>')
    p.append('<path d="M70 240h200" class="fine" stroke-dasharray="1 4"/>')
    p.append('<text x="70" y="258" class="p" font-size="10.5">servos</text>')

    # palm and wrist
    p.append('<path d="M300 160L340 152C400 146 452 154 474 170L478 252C472 270 444 280 414 282L304 264Z" class="solid"/>')
    p.append('<path d="M340 154L344 274" class="fine"/>')
    p.append('<rect x="370" y="198" width="44" height="24" rx="3" class="solid" stroke-width="1.1"/><path d="M377 210h30" class="fine"/>')

    # fingers, far to near so the near ones overlap the far ones
    fingers = [  # (base x, base y, lengths, curl angles, width)
        (452, 166, (48, 30, 24), (54, 78, 50), 18),     # pinky
        (462, 187, (60, 38, 28), (52, 80, 52), 21),     # ring
        (470, 209, (64, 40, 30), (50, 82, 54), 22),     # middle
        (468, 232, (60, 38, 28), (48, 78, 50), 22),     # index
    ]
    for depth, (x, y, lens, angles, wdt) in zip((3, 2, 1, 0), fingers):
        p.append(f'<path d="M296 {190 + depth * 8}C360 {184 + depth * 6} 400 {y} {x - 8} {y}" class="fine" stroke-dasharray="3 3"/>')
        p.append(finger(x, y, lens, angles, wdt, depth))

    # thumb, opposing from under the palm
    p.append(finger(424, 276, (42, 32, 22), (-42, -36, -20), 22, 0))

    # grip sensor reading, rising as the hand closes
    gx, gy = 680, 286
    vals = ["0", "0", "1", "1", "0", "0"]
    p.append(f'<text x="{gx}" y="{gy - 12}" class="p" font-size="12">grip sensor</text>')
    p.append(f'<rect x="{gx}" y="{gy}" width="250" height="6" rx="3" fill="{PANEL}" stroke="{INK}" stroke-width=".6" stroke-opacity=".5"/>')
    p.append(f'<rect x="{gx}" y="{gy}" width="0" height="6" rx="3" fill="{TEXT}">'
             f'<animate attributeName="width" values="{";".join(str(int(v) * 250) for v in vals)}" '
             f'keyTimes="{kt}" dur="{dur}s" calcMode="spline" keySplines="0 0 1 1;.5 0 .3 1;0 0 1 1;.5 0 .3 1;0 0 1 1" '
             f'repeatCount="indefinite"/></rect>')

    tx = 680
    p.append(f'<text x="{tx}" y="96" class="h" font-size="30">Dexarm</text>')
    p.append(f'<text x="{tx}" y="121" class="p" font-size="13.5">An affordable prosthetic arm from VividSense.</text>')
    p.append(f'<text x="{tx}" y="140" class="p" font-size="13.5">1st of 44 teams at LaunchSB, April 2026.</text>')
    p.append(f'<text x="{tx}" y="186" class="h" font-size="15">Version 3</text>')
    p.append(f'<text x="{tx}" y="205" class="p" font-size="12.5">stronger grip, lighter materials,</text>')
    p.append(f'<text x="{tx}" y="223" class="p" font-size="12.5">better sensor feedback</text>')
    write("dexarm.svg", W, H, "Dexarm, a prosthetic hand, closing and opening", "", "\n".join(p))


# 4. Stack -------------------------------------------------------------------

def stack():
    W, H = 1000, 340
    ch = 40
    top = ["Python", "TypeScript", "Rust", "C++", "Swift", "Dart"]
    bottom = ["PyTorch", "React", "Next.js", "Tauri", "ESP32", "Firebase", "Flutter"]
    chips = {n: (50 + i * 155, 70, 128) for i, n in enumerate(top)}
    chips.update({n: (45 + i * 130, 232, 114) for i, n in enumerate(bottom)})
    # (lower chip, upper chip, x offset where the trace enters the upper chip)
    links = [("PyTorch", "Python", 0), ("React", "TypeScript", -22), ("Next.js", "TypeScript", 22),
             ("Tauri", "Rust", 0), ("ESP32", "C++", 0), ("Firebase", "Swift", 0), ("Flutter", "Dart", 0)]

    p = [f'<defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r=".8" fill="{INK}" opacity=".18"/></pattern>'
         f'<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5"/></filter></defs>',
         f'<rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="10" fill="url(#grid)" stroke="{INK}" stroke-opacity=".25"/>']
    traces = []
    for k, (a, b, off) in enumerate(links):
        ax, ay, aw = chips[a]
        bx, by, bw = chips[b]
        x1, x2 = ax + aw / 2, bx + bw / 2 + off
        lane = 160 + (6 if k % 2 else -6)
        d = f"M{x1:.0f} {ay}V{lane}H{x2:.0f}V{by + ch}"
        traces.append((d, (ay - lane) + abs(x1 - x2) + (lane - by - ch), k, (x1, lane), (x2, lane)))
    for d, length, k, c1, c2 in traces:
        p.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.4" opacity=".45"/>')
        for cx, cy in (c1, c2):
            p.append(f'<circle cx="{cx:.0f}" cy="{cy}" r="2.6" fill="{BG}" stroke="{INK}" stroke-width="1" opacity=".7"/>')
    for d, length, k, c1, c2 in traces:
        dur = 1.4 + length / 160
        style = f"--l:{length + 30:.0f}px;animation-duration:{dur:.2f}s;animation-delay:{k * .45:.2f}s"
        dash = f'stroke-dasharray="22 {length + 60:.0f}" stroke-dashoffset="{length + 30:.0f}"'
        p.append(f'<path d="{d}" fill="none" stroke="{TEXT}" stroke-width="5" opacity=".5" filter="url(#glow)" {dash} class="sig" style="{style}"/>')
        p.append(f'<path d="{d}" fill="none" stroke="#ffffff" stroke-width="2.4" stroke-linecap="round" {dash} class="sig" style="{style}"/>')
    for name, (x, y, w) in chips.items():
        pins = "".join(f"M{x + 12 + i * 12} {y}v-6M{x + 12 + i * 12} {y + ch}v6" for i in range(int((w - 16) // 12)))
        p.append(f'<path d="{pins}" stroke="{INK}" stroke-width="1.2" opacity=".6"/>')
        p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{ch}" rx="4" fill="{PANEL}" stroke="{INK}" stroke-width="1.3"/>')
        p.append(f'<circle cx="{x + 9}" cy="{y + 9}" r="2" fill="{INK}" opacity=".5"/>')
        p.append(f'<text x="{x + w / 2}" y="{y + 25}" class="chip" text-anchor="middle">{name}</text>')
    css = f"""
.chip{{font-family:'GeistMono',monospace;font-weight:500;font-size:14px;fill:{TEXT}}}
.sig{{animation:run linear infinite}}
@keyframes run{{from{{stroke-dashoffset:var(--l)}}to{{stroke-dashoffset:-22px}}}}
"""
    names = ", ".join(top + bottom)
    write("stack.svg", W, H, f"Languages and tools as chips on a circuit board: {names}", css, "\n".join(p),
          mono=True, reduced=".sig{animation:none;opacity:0}")


if __name__ == "__main__":
    timeline()
    gimdrone()
    dexarm()
    stack()
