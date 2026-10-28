"""Builds assets/skyline.svg: the last year of contributions as an isometric city.

Every day is a tower whose height follows that day's contribution count. The
towers rise in a sweep from the oldest week to the newest each time the page
loads, then hold. Same palette and line weights as the throne hero.

Needs a GitHub token (GITHUB_TOKEN or GH_TOKEN, or a logged-in `gh`). The
daily workflow in .github/workflows/skyline.yml reruns this and commits it.

    python scripts/build_skyline.py
"""
import datetime as dt
import json
import math
import os
import re
import subprocess
import urllib.request
from pathlib import Path

from svgkit import font_face

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "skyline.svg"
LOGIN = "WasimVorvoi"

W, H = 1000, 560
BG = "#0d1117"
INK = "#c9d1d9"
TEXT = "#e6edf3"
MUTED = "#8d96a0"

# isometric axes: one week steps right-down, one weekday steps left-down
U = (14.6, 5.0)
V = (-10.0, 6.0)
ORIGIN = (148, 196)
MAX_H = 140
SWEEP = 3.2          # seconds for the build to cross the whole year
RISE = 0.9           # seconds for one tower to rise

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")

QUERY = """{user(login:"%s"){contributionsCollection{contributionCalendar{
  totalContributions weeks{contributionDays{date weekday contributionCount}}}}}}""" % LOGIN


def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def calendar():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY}).encode(),
        headers={"Authorization": f"bearer {token()}", "User-Agent": UA},
    )
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], cal["weeks"]


def pt(w, d, lift=0.0):
    return ORIGIN[0] + w * U[0] + d * V[0], ORIGIN[1] + w * U[1] + d * V[1] - lift


def poly(points):
    return " ".join("%.1f,%.1f" % p for p in points)


def tower(w, d, h, shade, begin):
    """Top face plus the two faces that look at the viewer, rising from flat to h."""
    a, b, c, e = (w, d), (w + 1, d), (w + 1, d + 1), (w, d + 1)
    gap = 0.12   # keep neighbouring towers from fusing into one block
    a, b, c, e = [(x + (gap if x == w else -gap), y + (gap if y == d else -gap)) for x, y in (a, b, c, e)]

    def faces(lift):
        top = [pt(*p, lift) for p in (a, b, c, e)]
        right = [pt(*b), pt(*c), pt(*c, lift), pt(*b, lift)]
        front = [pt(*e), pt(*c), pt(*c, lift), pt(*e, lift)]
        return right, front, top

    out = []
    timing = f'dur="{RISE}s" begin="{begin:.2f}s" fill="freeze" calcMode="spline" keySplines=".2 .7 .2 1"'
    for cls, flat, full in zip(("r", "f", "t"), faces(0), faces(h)):
        fill = {"r": "#161b22", "f": "#21262d", "t": shade}[cls]
        out.append(f'<polygon class="{cls}" fill="{fill}" points="{poly(flat)}">'
                   f'<animate attributeName="points" from="{poly(flat)}" to="{poly(full)}" {timing}/></polygon>')
    return "".join(out)


def build():
    total, weeks = calendar()
    days = [day for wk in weeks for day in wk["contributionDays"]]
    peak = max(days, key=lambda x: x["contributionCount"])
    active = sum(1 for x in days if x["contributionCount"])
    top = max(1, peak["contributionCount"])

    # longest streak, ending anywhere in the year
    streak = best = 0
    for x in days:
        streak = streak + 1 if x["contributionCount"] else 0
        best = max(best, streak)

    cells = []
    for w, wk in enumerate(weeks):
        for day in wk["contributionDays"]:
            cells.append((w, day["weekday"], day["contributionCount"], day["date"]))
    cells.sort(key=lambda c: (c[0] + c[1], c[0]))   # painter's order: far to near

    n = len(weeks)
    floor, towers, heights = [], [], {}
    for w, d, count, date in cells:
        tile = [pt(w + .12, d + .12), pt(w + .88, d + .12), pt(w + .88, d + .88), pt(w + .12, d + .88)]
        floor.append(f'<polygon class="tile" points="{poly(tile)}"/>')
        if count:
            k = math.sqrt(count / top)
            h = 4 + k * (MAX_H - 4)
            g = int(0x6e + (0xf0 - 0x6e) * k)
            heights[(w, d)] = h
            towers.append(tower(w, d, h, f"#{g:02x}{g:02x}{min(255, g + 6):02x}", 0.3 + SWEEP * w / n))

    # month labels along the front (Sunday-side) edge, skipping the first partial month
    months = []
    seen = set()
    for w, wk in enumerate(weeks):
        first = wk["contributionDays"][0]["date"]
        m = first[:7]
        if m not in seen and w > 0 and int(first[8:]) <= 7:
            x, y = pt(w + .5, 7.6)
            label = dt.date.fromisoformat(first).strftime("%b")
            months.append(f'<text x="{x:.1f}" y="{y:.1f}" class="mo" transform="rotate(18.9 {x:.1f} {y:.1f})">{label}</text>')
        seen.add(m)

    # the newest day gets a slow pulse so the page reads as live
    last = days[-1]
    lw, ld = len(weeks) - 1, last["weekday"]
    nx, ny = pt(lw + .5, ld + .5, heights.get((lw, ld), 0))

    peak_date = dt.date.fromisoformat(peak["date"]).strftime("%b %-d" if os.name != "nt" else "%b %#d")
    stat_text = [
        (f"{total:,}", "contributions in the last year"),
        (f"{active}", "days with something shipped"),
        (f"{best}", "days in the longest streak"),
        (f"{peak['contributionCount']}", f"on {peak_date}, the busiest day"),
    ]
    updated = dt.date.fromisoformat(last["date"]).strftime("%B %-d, %Y" if os.name != "nt" else "%B %#d, %Y")

    numerals = "".join(a for a, _ in stat_text)
    small = "".join(b for _, b in stat_text) + "".join(re.findall(r">([A-Za-z]+)</text>", "".join(months))) \
        + f"One tower per day. Rebuilt every night from GitHub, last on {updated}"
    fonts = (font_face("Schibsted Grotesk", 600, numerals, "SchibstedB")
             + font_face("Schibsted Grotesk", 400, small, "Schibsted"))

    stats = []
    for i, (big, label) in enumerate(stat_text):
        x = 40 + i * 235
        stats.append(f'<g class="stat" style="animation-delay:{.15 * i:.2f}s">'
                     f'<text x="{x}" y="64" class="big">{big}</text>'
                     f'<text x="{x}" y="88" class="lab">{label}</text></g>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{total:,} GitHub contributions in the last year, drawn as an isometric skyline with one tower per day">
<title>{total:,} contributions in the last year</title>
<style>
{fonts}
.big{{font-family:'SchibstedB',sans-serif;font-weight:600;font-size:30px;fill:{TEXT};paint-order:stroke;stroke:{BG};stroke-width:8px;stroke-linejoin:round}}
.lab{{font-family:'Schibsted',sans-serif;font-size:13px;fill:{MUTED};paint-order:stroke;stroke:{BG};stroke-width:6px;stroke-linejoin:round}}
.mo{{font-family:'Schibsted',sans-serif;font-size:11px;fill:{MUTED}}}
.foot{{font-family:'Schibsted',sans-serif;font-size:11px;fill:#6e7681}}
.tile{{fill:none;stroke:{INK};stroke-width:.6;opacity:.22}}
.t,.r,.f{{stroke:{INK};stroke-width:.7;stroke-linejoin:round}}
.r,.f{{stroke-opacity:.55}}
.stat{{opacity:0;animation:in .8s ease-out forwards}}
.now{{animation:pulse 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
@keyframes pulse{{0%,100%{{opacity:.9;transform:scale(1)}}50%{{opacity:.15;transform:scale(2.4)}}}}
@media (prefers-reduced-motion:reduce){{.stat{{animation:none;opacity:1}}.now{{animation:none}}}}
</style>
<rect width="{W}" height="{H}" fill="{BG}"/>
<g>{"".join(floor)}</g>
<g>{"".join(towers)}</g>
<ellipse cx="{nx:.1f}" cy="{ny:.1f}" rx="5" ry="3" fill="none" stroke="{TEXT}" stroke-width="1.2" class="now"/>
<g>{"".join(months)}</g>
{"".join(stats)}
<text x="{W - 40}" y="{H - 22}" text-anchor="end" class="foot">One tower per day. Rebuilt every night from GitHub, last on {updated}</text>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB), {total:,} contributions, peak {top}")


if __name__ == "__main__":
    build()
