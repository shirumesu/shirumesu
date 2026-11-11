#!/usr/bin/env python3
"""
Build the profile SVGs: design/src/*.svg -> resource/*.svg

GitHub renders README images through <img>, so SVGs there cannot load web
fonts. This script turns every <text> in the sources into outlined <path>s
using LXGW WenKai, and inlines `@img/<file>` references as data URIs.

Setup (fonts are not committed, ~25MB each):
    pip install fonttools
    gh release download -R lxgw/LxgwWenKai -p 'LXGWWenKai-Regular.ttf' -p 'LXGWWenKai-Medium.ttf' -D design/fonts
    # cute round handwriting used sparingly in the quote cloud (SetoFont derivative, OFL)
    gh release download -R lxgw/kose-font -p 'Xiaolai-Regular.ttf' -D design/fonts

Usage:
    python design/build.py            # all sources
    python design/build.py banner     # only src/banner.svg

<text> attributes understood by the builder:
    x, y            baseline origin (for data-v: x is the column centre, y the top)
    font-size       px
    data-w          "m" Medium · "x" Xiaolai (round handwriting); default Regular
    text-anchor     start | middle | end
    letter-spacing  px
    data-v          vertical text (uses the font's `vert` alternates)
    data-maxw       shrink font-size until the line fits this width
Everything else (fill, class, style, opacity, transform, ...) is copied onto the
generated <path>. <tspan> children may override fill / font-size / data-w and add dx.
"""
import base64
import html
import mimetypes
import pathlib
import re
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src"
IMG = ROOT / "img"
OUT = ROOT.parent / "resource"
FONT_DIR = ROOT / "fonts"


def ntos(v):
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    if s == "-0":
        s = "0"
    return s


class Face:
    def __init__(self, path):
        self.font = TTFont(path, lazy=True)
        self.cmap = self.font.getBestCmap()
        self.gs = self.font.getGlyphSet()
        self.hmtx = self.font["hmtx"]
        self.upm = self.font["head"].unitsPerEm
        self.vert = {}
        # fonts without a GSUB feature list simply have no vertical alternates
        gsub = self.font["GSUB"].table if "GSUB" in self.font else None
        records = gsub.FeatureList.FeatureRecord if gsub is not None and gsub.FeatureList else []
        idx = set()
        for fr in records:
            if fr.FeatureTag == "vert":
                idx.update(fr.Feature.LookupListIndex)
        for i in idx:
            lk = gsub.LookupList.Lookup[i]
            for st in lk.SubTable:
                if lk.LookupType == 7:
                    st = st.ExtSubTable
                if hasattr(st, "mapping"):
                    self.vert.update(st.mapping)
        self._cache = {}

    def glyph(self, ch, vertical=False):
        name = self.cmap.get(ord(ch))
        if name is None:
            return None
        if vertical:
            name = self.vert.get(name, name)
        return name

    def advance(self, name):
        return self.hmtx[name][0]

    def outline(self, name, x, y, size):
        s = size / self.upm
        pen = SVGPathPen(self.gs, ntos=ntos)
        tpen = TransformPen(pen, (s, 0, 0, -s, x, y))
        self.gs[name].draw(tpen)
        return pen.getCommands()


FACES = {}


def face(w):
    if w not in FACES:
        fn = {"r": "LXGWWenKai-Regular.ttf", "m": "LXGWWenKai-Medium.ttf",
              "x": "Xiaolai-Regular.ttf"}[w]
        p = FONT_DIR / fn
        if not p.exists():
            sys.exit(f"missing font {p} - see the docstring for setup")
        FACES[w] = Face(p)
    return FACES[w]


ATTR_RE = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')
TEXT_RE = re.compile(r"<text\b([^>]*)>(.*?)</text>", re.S)
TSPAN_RE = re.compile(r"<tspan\b([^>]*)>(.*?)</tspan>", re.S)
LAYOUT_KEYS = {"x", "y", "font-size", "data-w", "text-anchor", "letter-spacing", "data-v", "data-maxw", "dx"}
missing = set()


def parse_attrs(s):
    return dict(ATTR_RE.findall(s))


def runs_of(body, base):
    runs, pos = [], 0
    for m in TSPAN_RE.finditer(body):
        if m.start() > pos:
            runs.append((dict(base), body[pos:m.start()]))
        a = dict(base)
        a.update(parse_attrs(m.group(1)))
        runs.append((a, m.group(2)))
        pos = m.end()
    if pos < len(body):
        runs.append((dict(base), body[pos:]))
    out = []
    for a, t in runs:
        t = html.unescape(re.sub(r"\s+", " ", t))
        if t.strip():  # whitespace-only runs between <tspan>s are source formatting
            out.append((a, t))
    if out:  # trim outer whitespace like SVG does
        a, t = out[0]
        out[0] = (a, t.lstrip())
        a, t = out[-1]
        out[-1] = (a, t.rstrip())
    return out


def measure(runs, ls):
    total = 0.0
    for a, t in runs:
        f = face(a.get("data-w", "r"))
        size = float(a["font-size"])
        total += float(a.get("dx", 0))
        for ch in t:
            g = f.glyph(ch)
            adv = f.advance(g) if g else f.upm * 0.5
            total += adv * size / f.upm + ls
    return total - ls if total else 0


def render_text(attrs, body):
    base = {k: v for k, v in attrs.items() if k in ("font-size", "data-w", "fill")}
    base.setdefault("font-size", "16")
    runs = runs_of(body, base)
    ls = float(attrs.get("letter-spacing", 0))
    x, y = float(attrs.get("x", 0)), float(attrs.get("y", 0))
    vertical = "data-v" in attrs
    passthrough = " ".join(f'{k}="{v}"' for k, v in attrs.items() if k not in LAYOUT_KEYS and k not in ("fill",))

    if "data-maxw" in attrs and not vertical:
        maxw = float(attrs["data-maxw"])
        w = measure(runs, ls)
        if w > maxw:
            k = maxw / w
            runs = [(dict(a, **{"font-size": str(float(a["font-size"]) * k)}), t) for a, t in runs]
            ls *= k

    parts = []  # (fill, d)
    if vertical:
        cy = y
        for a, t in runs:
            f = face(a.get("data-w", "r"))
            size = float(a["font-size"])
            for ch in t:
                g = f.glyph(ch, vertical=True)
                if g is None:
                    missing.add(ch)
                    cy += size + ls
                    continue
                adv = f.advance(g) * size / f.upm
                d = f.outline(g, x - adv / 2, cy + size * 0.88, size)
                parts.append((a.get("fill"), d))
                cy += size + ls
    else:
        w = measure(runs, ls)
        anchor = attrs.get("text-anchor", "start")
        cx = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
        for a, t in runs:
            f = face(a.get("data-w", "r"))
            size = float(a["font-size"])
            cx += float(a.get("dx", 0))
            for ch in t:
                g = f.glyph(ch)
                if g is None:
                    missing.add(ch)
                    cx += size * 0.5 + ls
                    continue
                d = f.outline(g, cx, y, size)
                if d:
                    parts.append((a.get("fill"), d))
                cx += f.advance(g) * size / f.upm + ls

    fills = {p[0] for p in parts}
    top_fill = attrs.get("fill")
    if len(fills) <= 1:
        fill = next(iter(fills)) if fills else top_fill
        fa = f' fill="{fill}"' if fill else ""
        return f'<path{fa} {passthrough} d="{"".join(d for _, d in parts)}"/>'.replace("  ", " ")
    # several colours: group by fill
    groups = {}
    for fl, d in parts:
        groups.setdefault(fl, []).append(d)
    inner = "".join(f'<path fill="{fl}" d="{"".join(ds)}"/>' for fl, ds in groups.items())
    return f"<g {passthrough}>{inner}</g>"


def inline_images(svg):
    def rep(m):
        p = IMG / m.group(1)
        mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        return f'href="data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"'

    return re.sub(r'href="@img/([^"]+)"', rep, svg)


def build_svg(src_text):
    out = TEXT_RE.sub(lambda m: render_text(parse_attrs(m.group(1)), m.group(2)), src_text)
    out = inline_images(out)
    out = re.sub(r"<!--.*?-->", "", out, flags=re.S)
    out = re.sub(r"\n\s*\n", "\n", out)
    return out


def text_path(s, size, w="r", x=0, y=0, anchor="start", ls=0):
    """Helper for other build steps (e.g. the visitor worker glyphs)."""
    attrs = {"x": str(x), "y": str(y), "font-size": str(size), "data-w": w, "text-anchor": anchor, "letter-spacing": str(ls)}
    m = re.search(r' d="([^"]*)"', render_text(attrs, html.escape(s)))
    return m.group(1), measure([({"font-size": str(size), "data-w": w}, s)], ls)


def build_worker():
    """Outline the visitor counter's fixed text + digits into cloudflare/worker.js."""
    import json

    worker = ROOT.parent / "cloudflare" / "worker.js"
    src = worker.read_text()
    ld, lw = text_path("✿ あなたは", 15, "r", ls=0.5)
    rd, rw = text_path("人目の訪問者です。 ✿", 15, "r", ls=0.5)
    ls = 1.5
    digits = {"ls": ls}
    for ch in "0123456789":
        d, w = text_path(ch, 20, "m")
        digits[ch] = {"d": d, "w": round(w + ls, 2)}
    data = {"left": {"d": ld, "w": round(lw, 2)}, "right": {"d": rd, "w": round(rw, 2)}, "digits": digits}
    block = f"// <glyphs>\nconst GLYPHS = {json.dumps(data, ensure_ascii=False)};\n// </glyphs>"
    new = re.sub(r"// <glyphs>.*?// </glyphs>", lambda _: block, src, flags=re.S)
    worker.write_text(new)
    print(f"{'cloudflare/worker.js':28s} {len(new) / 1024:8.1f} KB")


def main():
    only = set(sys.argv[1:])
    if not only or "worker" in only:
        build_worker()
    OUT.mkdir(exist_ok=True)
    for src in sorted(SRC.glob("*.svg")):
        if only and src.stem not in only:
            continue
        out = build_svg(src.read_text())
        (OUT / src.name).write_text(out)
        print(f"{src.name:28s} {len(out) / 1024:8.1f} KB")
    if missing:
        print("missing glyphs:", "".join(sorted(missing)))


if __name__ == "__main__":
    main()
