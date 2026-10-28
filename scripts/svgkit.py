"""Shared palette and font loading for the README SVGs.

GitHub renders README SVGs as <img>, which can't load anything external, so
fonts are fetched as subsets of exactly the glyphs used and inlined as base64.
"""
import base64
import re
import urllib.parse
import urllib.request

BG = "#0d1117"       # GitHub dark canvas
INK = "#c9d1d9"      # line art
TEXT = "#e6edf3"
MUTED = "#8d96a0"
DIM = "#6e7681"
PANEL = "#161b22"

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


def text_of(svg_body):
    """Every character inside <text> elements, for font subsetting."""
    return "".join(re.findall(r"<text[^>]*>([^<]*)</text>", svg_body))
