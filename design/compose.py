#!/usr/bin/env python3
"""
Writes design/src/*.svg (layout layer). Then build.py outlines the text.

    python design/compose.py && python design/build.py

Design system — "summer note"
  Colour, four tokens, each with one job:
    INK    #1F3A4A  all text. Secondary text = INK at 60%.
    PAPER  #FAFCFB  every surface.
    SEA    #177F98  things you can follow: labels, links, the accent half of the quote cloud.
    SUN    #F4D35E  emphasis only: highlighter marks, sticky notes, the main project, the call to action.
  Type, four sizes (quote cloud excepted): 12 meta · 15 body · 20 heading · 32 display.
  Surfaces are flat: 1px ink hairline, 8px corners, a 1px white top highlight.
  Glass appears once per section at most, and only over an image or a glow.
  Motion: quotes are "written in" one by one; marker strokes sweep; glows drift slowly.
"""
import html
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build  # noqa: E402

SRC = pathlib.Path(__file__).resolve().parent / "src"

INK, PAPER, SEA, SUN = "#1F3A4A", "#FAFCFB", "#177F98", "#F4D35E"
ON_SUN = "#1F3A4B"  # text sitting on SUN: stays dark in both themes
DARK = False

# Dark variants are a token swap of the finished light SVG (written as <name>-dark.svg).
# Ink and paper trade places, sea lifts to a lighter cyan, white highlights become a dim
# glass tone, and SUN keeps its hue but drops its highlighter strength.
DARK_MAP = [
    ("#1F3A4A", "#DCE8EC"),   # ink   -> light ink
    ("#FAFCFB", "#0F1A20"),   # paper -> deep sea-night
    ("#177F98", "#6CC6DC"),   # sea   -> lighter sea
    ("#FFFFFF", "#3A4C55"),   # rims / glass / tape highlights
    ("melonbang-home-light.webp", "melonbang-home-dark.webp"),  # the app screenshot has its own dark theme
    ('stop-color="#F4D35E" stop-opacity=".75"', 'stop-color="#F4D35E" stop-opacity=".34"'),
    ('stop-color="#F4D35E" stop-opacity=".6"', 'stop-color="#F4D35E" stop-opacity=".26"'),
    ('stop-color="#F4D35E" stop-opacity=".2"', 'stop-color="#F4D35E" stop-opacity=".1"'),
    ('values="0 0 0 0 .12  0 0 0 0 .23  0 0 0 0 .29  .12 0 0 0 -.035"', 'values="0 0 0 0 .86  0 0 0 0 .92  0 0 0 0 .95  .09 0 0 0 -.025"'),
]
META, BODY, HEAD, DISP = 12, 15, 20, 32
SOFT = ".62"  # secondary text opacity
LAST_UPDATED = "2026.11.11 Wed."

STYLE = """<style>
    .drift { animation: drift 22s ease-in-out infinite; }
    .drift2 { animation: drift2 28s ease-in-out infinite; }
    @keyframes drift { 0%, 100% { transform: translate(0, 0); } 50% { transform: translate(36px, 14px); } }
    @keyframes drift2 { 0%, 100% { transform: translate(0, 0); } 50% { transform: translate(-40px, -10px); } }
    .sweep { animation: sweep .9s cubic-bezier(.3, .7, .2, 1) both; transform-box: fill-box; transform-origin: left center; }
    @keyframes sweep { from { transform: scaleX(0); } to { transform: scaleX(1); } }
    .draw { stroke-dasharray: 1200; stroke-dashoffset: 1200; animation: draw 1.4s ease-out forwards; }
    @keyframes draw { to { stroke-dashoffset: 0; } }
    .flow { stroke-dasharray: 4 6; animation: flow 1.4s linear infinite; }
    @keyframes flow { to { stroke-dashoffset: -20; } }
    .fade { animation: fade .8s ease-out both; }
    @keyframes fade { from { opacity: 0; } to { opacity: 1; } }
    .blink { animation: blink 3.2s ease-in-out infinite; }
    .twinkle { animation: twinkle 3.6s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
    @keyframes twinkle { 0%, 100% { transform: scale(1); } 50% { transform: scale(.5); } }
    @keyframes blink { 0%, 100% { opacity: .35; } 50% { opacity: 1; } }
    @media (prefers-reduced-motion: reduce) { * { animation: none !important; } .draw, .ink { stroke-dashoffset: 0 !important; } }
  </style>"""

DEFS = """<defs>
    <linearGradient id="wash" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#177F98" stop-opacity=".045"/><stop offset=".6" stop-color="#177F98" stop-opacity="0"/><stop offset="1" stop-color="#F4D35E" stop-opacity=".07"/>
    </linearGradient>
    <radialGradient id="gSea"><stop offset="0" stop-color="#177F98" stop-opacity=".11"/><stop offset="1" stop-color="#177F98" stop-opacity="0"/></radialGradient>
    <radialGradient id="gSun"><stop offset="0" stop-color="#F4D35E" stop-opacity=".2"/><stop offset="1" stop-color="#F4D35E" stop-opacity="0"/></radialGradient>
    <linearGradient id="rim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF"/><stop offset=".18" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="marker" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#F4D35E" stop-opacity=".75"/><stop offset=".9" stop-color="#F4D35E" stop-opacity=".6"/><stop offset="1" stop-color="#F4D35E" stop-opacity="0"/>
    </linearGradient>
    <pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="8" cy="8" r=".9" fill="#1F3A4A" fill-opacity=".14"/></pattern>
    <filter id="grain" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="4" stitchTiles="stitch"/>
      <feColorMatrix type="matrix" values="0 0 0 0 .12  0 0 0 0 .23  0 0 0 0 .29  .12 0 0 0 -.035"/>
    </filter>
    {extra}
  </defs>"""


def svg(name, w, h, label, body, extra_defs=""):
    out = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(label)}">\n'
        f"  {STYLE}\n  {DEFS.replace('{extra}', extra_defs)}\n  {body}\n</svg>\n"
    )
    if DARK:
        for a, b in DARK_MAP:
            out = out.replace(a, b)
        name += "-dark"
    (SRC / f"{name}.svg").write_text(out)


def T(x, y, s, txt, fill=INK, w="r", anchor=None, ls=None, maxw=None, op=None, v=False, cls=None, style=None):
    a = [f'x="{x}" y="{y}" font-size="{s}" fill="{fill}"']
    if w != "r":
        a.append(f'data-w="{w}"')
    if anchor:
        a.append(f'text-anchor="{anchor}"')
    if ls:
        a.append(f'letter-spacing="{ls}"')
    if maxw:
        a.append(f'data-maxw="{maxw}"')
    if op:
        a.append(f'fill-opacity="{op}"')
    if v:
        a.append('data-v="1"')
    if cls:
        a.append(f'class="{cls}"')
    if style:
        a.append(f'style="{style}"')
    return f'<text {" ".join(a)}>{html.escape(txt, quote=False)}</text>'


def width(txt, s, w="r", ls=0):
    return build.text_path(txt, s, w, ls=ls)[1]


def tile(cid, x, y, w, h, r=8, glows=(), dots=False, grain=False, inner="", hair=".1"):
    gl = "".join(f'<g class="{c}"><circle cx="{gx}" cy="{gy}" r="{gr}" fill="url(#{g})"/></g>' for (g, gx, gy, gr, c) in glows)
    dt = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#dots)"/>' if dots else ""
    gn = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" filter="url(#grain)"/>' if grain else ""
    return f"""<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/></clipPath>
  <g clip-path="url(#{cid})">
    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}"/><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#wash)"/>
    {dt}{gl}{inner}{gn}
  </g>
  <rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="{r - .5}" fill="none" stroke="{INK}" stroke-opacity="{hair}"/>
  <rect x="{x + 1.5}" y="{y + 1.5}" width="{w - 3}" height="{h - 3}" rx="{r - 1.5}" fill="none" stroke="url(#rim)" stroke-width="1.2"/>"""


def marker(x, y, w, h=10, delay=0, rot=0):
    """Highlighter stroke (SUN = emphasis)."""
    return (f'<g transform="rotate({rot} {x} {y})"><rect class="sweep" style="animation-delay:{delay}s" '
            f'x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="url(#marker)"/></g>')


def label(x, y, txt, fill=SEA, anchor=None):
    return T(x, y, META, txt, fill, "m", anchor, ls=2)


# ------------------------------------------------------------------ quote cloud
# Choreography: the posters go up first, then the four big lines land, the rest are written
# in roughly in reading order, then the props arrive (stamp, badges, notes, pin, doodles), and
# last the 吾且问 question gets its answer handwritten in. After that only a handful of slow
# loops stay alive: the pinned note swings, the sticky note sways, (=ω=.) wobbles, two
# sparkles twinkle. Everything else stays still so the page reads cleanly.
# The round handwriting ("x") is an accent for four lines only, not a second body face.


def written(x, y, s, txt, fill=INK, w="r", op=None, ls=0, v=False, delay=0.0, rot=None, wobble=False, cls="pop"):
    """Phrase that pops in (fade + rise)."""
    t = T(x, y, s, txt, fill, w, None, ls or None, op=op, v=v)
    if wobble:
        t = f'<g class="wobble">{t}</g>'
    g = f'<g class="{cls}" style="animation-delay:{delay:.2f}s">{t}</g>'
    return f'<g transform="rotate({rot})">{g}</g>' if rot else g


def scribbled(mid, x, y, s, txt, fill=INK, w="r", op=None, ls=0, begin=0.0, dur=1.0):
    """Phrase revealed left-to-right as if being written. SMIL, so it also runs inside <img>.
    The mask's resting width is the full line, so a renderer without SMIL still shows it.
    The mask uses the keyword `white` on purpose: the dark token swap rewrites #FFFFFF."""
    full = width(txt, s, w, ls) + 8
    k = begin / (begin + dur)
    m = (f'<mask id="{mid}" maskUnits="userSpaceOnUse"><rect x="{x - 4:.1f}" y="{y - s * 1.1:.1f}" width="{full:.1f}" height="{s * 1.5:.1f}" fill="white">'
         f'<animate attributeName="width" values="0;0;{full:.1f}" keyTimes="0;{k:.3f};1" begin="0s" dur="{begin + dur}s" fill="freeze" '
         f'calcMode="spline" keySplines="0 0 1 1;.45 .05 .55 .95"/></rect></mask>')
    return m + f'<g mask="url(#{mid})">{T(x, y, s, txt, fill, w, None, ls or None, op=op)}</g>'


def tape_strip(cx, cy, rot, w=58, h=16):
    """Strip of washi tape, centred on (cx, cy). On the dark wall it is a pale translucent strip."""
    fill, op = (INK, ".22") if DARK else (PAPER, ".8")
    return (f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" fill="{fill}" fill-opacity="{op}" '
            f'stroke="{INK}" stroke-opacity=".08" transform="rotate({rot} {cx} {cy})"/>')


def note(x, y, w, h, rot, fill=SUN, op=".5", tape=True):
    """Flat sticky note / index tab."""
    if DARK:
        op = ".88"
    t = tape_strip(x + w / 2, y, 0, 44, 14) if tape else ""
    return (f'<g transform="rotate({rot} {x + w / 2} {y + h / 2})"><rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="{fill}" fill-opacity="{op}"/>{t}</g>')


def pin(cx, cy):
    """Push pin seen from above: soft shadow, sea head, white glint."""
    return (f'<ellipse cx="{cx + 2}" cy="{cy + 3}" rx="5" ry="3.4" fill="{INK}" fill-opacity=".16"/>'
            f'<circle cx="{cx}" cy="{cy}" r="5.2" fill="{SEA}"/><circle cx="{cx - 1.6}" cy="{cy - 1.8}" r="1.6" fill="white" fill-opacity=".7"/>')


def doodle(d, delay, color=INK, op=".38", sw=1.3, length=300):
    """Pen stroke drawn on (stroke-dashoffset)."""
    return (f'<path class="ink" style="animation-delay:{delay}s;stroke-dasharray:{length};stroke-dashoffset:{length}" d="{d}" '
            f'fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')


POP_CSS = """<style>
    .pop { animation: pop .7s cubic-bezier(.2, .8, .3, 1.25) both; }
    @keyframes pop { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
    .land { animation: land .8s cubic-bezier(.2, .9, .25, 1.15) both; transform-box: fill-box; transform-origin: 30% 80%; }
    @keyframes land { from { opacity: 0; transform: translateY(-14px) scale(1.06); } to { opacity: 1; transform: none; } }
    .stamp { animation: stamp .5s cubic-bezier(.3, 1.5, .5, 1) both; transform-box: fill-box; transform-origin: center; }
    @keyframes stamp { from { opacity: 0; transform: scale(1.5) rotate(4deg); } to { opacity: 1; transform: none; } }
    .ink { animation: ink 1s ease-out forwards; }
    @keyframes ink { to { stroke-dashoffset: 0; } }
    .wobble { animation: wobble 3.2s ease-in-out infinite alternate; transform-box: fill-box; transform-origin: 50% 90%; }
    @keyframes wobble { from { transform: rotate(-8deg); } to { transform: rotate(-2deg); } }
    .drop { animation: drop .9s cubic-bezier(.25, 1.4, .45, 1) both; transform-box: fill-box; transform-origin: 50% 0; }
    @keyframes drop { from { opacity: 0; transform: translateY(-22px) rotate(-7deg); } to { opacity: 1; transform: none; } }
    .swing { animation: swing 5.5s ease-in-out 3.4s infinite alternate; transform-box: fill-box; transform-origin: 50% 0; }
    @keyframes swing { from { transform: rotate(-1.6deg); } to { transform: rotate(1.6deg); } }
    .sway { animation: sway 7s ease-in-out 3s infinite alternate; transform-box: fill-box; transform-origin: 50% 0; }
    @keyframes sway { from { transform: rotate(-.8deg) translateY(0); } to { transform: rotate(.8deg) translateY(1px); } }
  </style>"""


def poster(img, x, y, w, h, rot, delay):
    """Printed key visual taped to the wall: paper border, hairline, a strip of tape on top."""
    b = 4
    cx, cy = x + w / 2, y + h / 2
    body = (f'<rect x="{x + 2}" y="{y + 3}" width="{w}" height="{h}" fill="{INK}" fill-opacity=".08"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}" stroke="{INK}" stroke-opacity=".12"/>'
            f'<image href="@img/{img}" x="{x + b}" y="{y + b}" width="{w - 2 * b}" height="{h - 2 * b}" preserveAspectRatio="xMidYMid slice"/>'
            + tape_strip(cx, y + 2, -rot * 2))
    return f'<g transform="rotate({rot} {cx} {cy})"><g class="drop" style="animation-delay:{delay}s">{body}</g></g>'


def badge(img, cx, cy, r, delay, cid):
    """Can badge (缶バッジ): round print, rim, a soft gloss and a shadow."""
    return (f'<clipPath id="{cid}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
            f'<g class="stamp" style="animation-delay:{delay}s">'
            f'<circle cx="{cx + 1.5}" cy="{cy + 2.5}" r="{r + 1}" fill="{INK}" fill-opacity=".16"/>'
            f'<image href="@img/{img}" x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" clip-path="url(#{cid})"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r - 1.2}" fill="none" stroke="#FFFFFF" stroke-width="2.4"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{INK}" stroke-opacity=".18"/>'
            f'<path d="M{cx - r * .84} {cy - r * .2} A {r * .86} {r * .86} 0 0 1 {cx - r * .2} {cy - r * .84}" fill="none" stroke="white" stroke-opacity=".5" stroke-width="{r * .09:.1f}" stroke-linecap="round"/>'
            f'</g>')


def jump_motto(x, y, delay):
    """友情・努力・勝利 — Weekly Shōnen Jump's three principles, set as the wall's motto rather
    than a quote: the three words stamp in one beat apart, then a skewed sun slash sweeps behind
    them."""
    s, ls = 22, 1
    words = ["友情・", "努力・", "勝利"]
    total = width("".join(words), s, "m", ls)
    out = [f'<g class="sweep" style="animation-delay:{delay + .5:.2f}s"><path d="M{x - 8} {y + 6} L{x - 2} {y - 22} L{x + total + 10} {y - 24} L{x + total + 4} {y + 4} Z" '
           f'fill="{SUN}" fill-opacity=".55"/></g>']
    cx = x
    for i, wd in enumerate(words):
        out.append(f'<g class="stamp" style="animation-delay:{delay + .14 * i:.2f}s">{T(cx, y, s, wd, INK, "m", ls=ls)}</g>')
        cx += width(wd, s, "m", ls) + ls
    return "".join(out)


def banner():
    """The collection wall: three posters and four badges break the grid; the quotes cluster
    densely around 計画通り in the middle and thin out toward the edges."""
    W, H = 880, 540
    p = [tile("pg", 8, 1, 864, H - 2, 10, glows=[("gSea", 330, 200, 300, "drift"), ("gSun", 760, 500, 300, "drift2")], dots=True, grain=True, hair=".12")]
    p.append(f'<line x1="612" y1="44" x2="852" y2="44" stroke="{INK}" stroke-opacity=".18"/>')
    p.append(T(614, 38, META, "Last updated", INK, op=SOFT, ls=1))
    p.append(T(852, 38, BODY, LAST_UPDATED, INK, anchor="end"))

    # posters first: they are the wall
    p.append(poster("poster-haruhi.webp", 26, 26, 108, 152, -4, .05))
    p.append(poster("poster-steins.webp", 744, 156, 100, 150, 4, .2))
    p.append(poster("poster-keion.webp", 742, 352, 104, 147, -3, .35))

    # wave 1 — anchors
    p.append(written(152, 74, 28, "ただの人間には興味ありません!", INK, "m", ls=.5, delay=.2, cls="land"))
    p.append(marker(150, 182, 296, 20, .9, -1))
    p.append(written(154, 206, 58, "計画通り…", INK, "m", ls=1, delay=.4, cls="land"))
    p.append(written(40, 516, 30, "貧乳はステータスだ、希少価値だ!", SEA, ls=.5, delay=.6, cls="land"))
    p.append(written(476, 428, 34, "山田尚子是神！", INK, "x", delay=.75, cls="land"))

    seq = iter(round(1.0 + .07 * i, 3) for i in range(40))
    # the dense core, around 計画通り
    p.append(written(176, 100, 12, "你能回到过去拯救那个没被 QB 欺骗的我吗", INK, op=SOFT, delay=next(seq)))
    p.append(written(158, 134, 18, "区区小司…", SEA, delay=next(seq)))
    p.append(written(258, 130, 14, "我师傅的真实身份是…好人", INK, delay=next(seq)))
    p.append(written(436, 148, 20, "アッシエント!", INK, rot="-5 494 140", delay=next(seq)))
    p.append(written(520, 112, 17, "(=ω=.)", SEA, delay=next(seq), wobble=True))
    p.append(written(96, 424, 14, "原来你真是美发师啊", SEA, delay=next(seq)))
    p.append(written(336, 248, 24, "娶妻当如古河渚", INK, delay=next(seq)))
    p.append(written(206, 300, 27, "你这家伙在看我吧", INK, rot="-3 318 290", delay=next(seq)))
    p.append(written(446, 296, 17, "秀吉的性别是秀吉啊!", SEA, delay=next(seq)))
    p.append(written(604, 56, 17, "一即是全，全即是一", SEA, ls=1, v=True, delay=next(seq)))
    p.append(written(634, 214, 15, "晚安，Sion", INK, op=SOFT, delay=next(seq)))
    # the left margin, looser
    p.append(written(36, 226, 15, "吾且问，汝为人乎", INK, op=SOFT, ls=1, delay=next(seq)))
    p.append(written(54, 322, 13, "立于浮华之世，奏响天籁之音", INK, op=SOFT, delay=next(seq)))
    p.append(written(36, 350, 20, "为了我，成为炎拳吧", INK, delay=next(seq)))
    p.append(written(70, 380, 15, "家庭教师是你真的太好了", SEA, delay=next(seq)))
    p.append(written(124, 468, 14, "有木有WIFI?", INK, rot="-3 150 464", delay=next(seq)))
    # the lower middle, around the K-ON corner
    p.append(written(248, 340, 16, "请别忘记，这最棒的一年", SEA, delay=next(seq)))
    p.append(written(428, 320, 12.5, "淑女只让她心仪的人摸她的头发哦", INK, op=SOFT, delay=next(seq)))
    p.append(jump_motto(250, 390, delay=next(seq)))
    p.append(written(478, 372, 22, "欢迎回来，京阿尼", INK, "x", delay=next(seq)))
    p.append(written(286, 430, 16, "明天，美食广场见", INK, op=".86", delay=next(seq)))
    p.append(written(222, 458, 15, "友谊是时间的窃贼", INK, op=SOFT, delay=next(seq)))

    # props
    p.append(f'<g transform="rotate(-6 730 92)"><g class="stamp" style="animation-delay:2.4s"><rect x="626" y="64" width="216" height="54" fill="{INK}"/>'
             + T(734, 104, 33, "P5R天下第一", PAPER, "m", "middle", 1) + '</g></g>')
    p.append(f'<g transform="rotate(-4 722 150)"><g class="pop" style="animation-delay:2.5s"><rect x="624" y="134" width="196" height="32" fill="{PAPER}" fill-opacity=".92"/>'
             f'<rect x="624" y="134" width="196" height="32" fill="{SEA}" fill-opacity=".16"/>'
             + T(722, 156, 17, "EL PSY CONGROO", INK, anchor="middle", ls=2) + "</g></g>")
    p.append(f'<g class="drop" style="animation-delay:2.6s"><g class="sway">{note(664, 330, 178, 36, 3, op=".9")}'
             f'<g transform="rotate(3 753 348)">{T(753, 354, 18, "放課後ティータイム", ON_SUN, anchor="middle")}</g></g></g>')
    card = (f'<rect x="516" y="460" width="212" height="40" rx="3" fill="{PAPER}" stroke="{INK}" stroke-opacity=".14"/>'
            + T(622, 486, 15, "本喵明明什么坏事都没干喵！", INK, "x", anchor="middle") + pin(622, 465))
    p.append(f'<g transform="rotate(-3 622 465)"><g class="drop" style="animation-delay:2.75s"><g class="swing">{card}</g></g></g>')
    # badges next to the line they belong to
    p.append(badge("badge-light.webp", 484, 196, 30, 2.2, "bl"))
    p.append(badge("badge-nagisa.webp", 534, 238, 24, 2.3, "bn"))
    p.append(badge("badge-hideyoshi.webp", 640, 268, 22, 2.4, "bh"))

    # pen doodles
    p.append(doodle("M152 86 C 250 80 400 89 480 82 S 540 80 548 84", 1.0, SEA, "1", 2.2, 460))
    p.append(doodle("M514 104 C 512 90 536 86 558 88 C 578 90 584 100 578 108 C 570 118 536 118 522 114 C 512 110 510 100 518 94", 2.0, INK, ".35", 1.2, 200))
    p.append(doodle("M248 348 C 310 345 370 349 412 345", 2.3, SEA, ".5", 1.4, 200))
    p.append(doodle("M34 232 C 28 242 34 252 52 254 M46 248 52 254 45 259", 2.9, INK, ".35", 1.2, 80))
    p.append(doodle("M474 382 C 540 378 600 383 648 379", 2.4, SUN, "1", 3.2, 220))
    p.append(doodle("M700 384 l -2 -12 M712 388 l 8 -10 M721 396 l 12 -4", 2.2, SUN, "1", 2.4, 40))  # burst at 神
    # red pen, circled twice, like marking the answer in a notebook
    p.append(doodle("M712 412 C 714 394 650 397 590 398 C 520 399 466 402 464 420 C 462 440 530 446 596 445 C 660 444 716 438 714 416 C 713 404 700 398 684 396", 2.5, "#E5484D", ".9", 1.8, 760))
    p.append(doodle("M470 406 C 490 394 560 395 610 395 C 670 395 722 401 720 420 C 718 442 650 448 588 448 C 520 448 458 440 462 418", 2.9, "#E5484D", ".75", 1.4, 760))
    p.append(doodle("M36 526 Q 76 521 116 526 T 196 526 T 276 526 T 356 526 T 436 526 T 494 524", 2.7, INK, ".28", 1.6, 520))

    # two quiet pockets above the bottom line get small notebook clutter so the eye doesn't funnel
    p.append(f'<g class="pop" style="animation-delay:2.6s">'
             f'<rect x="36" y="402" width="9" height="9" rx="1.5" fill="none" stroke="{INK}" stroke-opacity=".45"/>'
             + T(51, 411, META, "追番", INK, op=SOFT)
             + f'<rect x="36" y="420" width="9" height="9" rx="1.5" fill="none" stroke="{INK}" stroke-opacity=".45"/>'
             + T(51, 429, META, "早睡", INK, op=SOFT) + "</g>")
    p.append(doodle("M37 406 l 3 3 l 6 -8", 2.8, SEA, "1", 1.6, 20))
    p.append(written(34, 458, 12, "(｀・ω・´)ゞ", INK, op=SOFT, delay=2.65))
    p.append(f'<g transform="translate(274 424)"><path class="twinkle" style="animation-delay:-.9s" d="M0-5 1.1-1.1 5 0 1.1 1.1 0 5-1.1 1.1-5 0-1.1-1.1Z" fill="{SEA}" fill-opacity=".6"/></g>')

    # the answer to 吾且问 is handwritten in last
    p.append(scribbled("ans", 58, 258, 20, "否，吾乃天——壶中之天", SEA, "x", begin=3.0, dur=1.3))

    star = "M0-6 1.3-1.3 6 0 1.3 1.3 0 6-1.3 1.3-6 0-1.3-1.3Z"
    p.append(f'<g transform="translate(150 186)"><path class="twinkle" d="{star}" fill="{SUN}"/></g>')
    p.append(f'<g transform="translate(724 528)"><path class="twinkle" style="animation-delay:-1.8s" d="{star}" fill="{SEA}" fill-opacity=".7"/></g>')
    svg("banner", W, H, f"shirumesu's notebook · last updated {LAST_UPDATED}", "\n  ".join(p), POP_CSS)


# ------------------------------------------------------------------ titles
def titles():
    """Centred heading; decoration mirrors outward: sun dot · sea star · ring · hand wave · dashed rule."""
    star = "M0-6 1.3-1.3 6 0 1.3 1.3 0 6-1.3 1.3-6 0-1.3-1.3Z"
    for key, en, jp in [("about", "about me", "じこしょうかい"), ("projects", "projects", "つくったもの"),
                        ("stats", "github stats", "きろく"), ("site", "my website", "ぶろぐ"), ("more", "one more thing", "おまけ")]:
        we = width(en, HEAD, "m")
        cx, cy = 440, 26
        half = we / 2 + 26
        p = [marker(cx - we / 2 - 3, 21, we + 6, 9, .2),
             T(cx, 28, HEAD, en, INK, "m", "middle"),
             T(cx, 48, META, jp, SEA, anchor="middle", ls=3)]
        for sgn in (-1, 1):
            x = lambda d: cx + sgn * (half + d)
            p.append(f'<circle class="blink" cx="{x(0):.1f}" cy="{cy}" r="3" fill="{SUN}"/>')
            p.append(f'<g transform="translate({x(16):.1f} {cy})"><path class="twinkle" d="{star}" fill="{SEA}" fill-opacity=".7"/></g>')
            p.append(f'<circle cx="{x(30):.1f}" cy="{cy}" r="2.4" fill="none" stroke="{SEA}" stroke-opacity=".6" stroke-width="1.2"/>')
            w0, w1 = x(42), x(112)
            a, b = (w0, w1) if sgn > 0 else (w1, w0)
            seg = (b - a) / 4
            wave = f"M{a:.1f} {cy} " + " ".join(f"Q {a + seg * (i + .5):.1f} {cy + (-3 if i % 2 == 0 else 3)} {a + seg * (i + 1):.1f} {cy}" for i in range(4))
            p.append(f'<path class="draw" style="animation-delay:.3s" d="{wave}" fill="none" stroke="{SEA}" stroke-opacity=".55" stroke-width="1.3" stroke-linecap="round"/>')
            r0, r1 = x(122), (16 if sgn < 0 else 864)
            a, b = sorted((r0, r1))
            p.append(f'<line x1="{a:.1f}" y1="{cy}" x2="{b:.1f}" y2="{cy}" stroke="{INK}" stroke-opacity=".16" stroke-dasharray="2 5" stroke-linecap="round"/>')
            p.append(f'<circle cx="{r1 + (-6 if sgn < 0 else 6) * 0:.1f}" cy="{cy}" r="2" fill="{INK}" fill-opacity=".2"/>')
        svg(f"title-{key}", 880, 56, en, "\n  ".join(p))


# ------------------------------------------------------------------ about (one image, bento)
def about():
    W, H = 880, 404
    ex = (f'<clipPath id="ph"><rect x="595" y="1" width="277" height="402" rx="8"/></clipPath>'
          f'<linearGradient id="phFade" x1="0" y1="0" x2="0" y2="1"><stop offset=".7" stop-color="{PAPER}" stop-opacity="0"/><stop offset="1" stop-color="{PAPER}" stop-opacity=".35"/></linearGradient>')
    p = [tile("ta", 8, 1, 571, 262, glows=[("gSea", 520, 20, 220, "drift")], dots=True)]
    p.append(label(34, 36, "INTRO"))
    p.append(f'<text x="34" y="74" font-size="{HEAD}" data-w="m"><tspan fill="{INK}">吾辈是</tspan><tspan fill="{SEA}">希露梅斯</tspan><tspan fill="{INK}">，</tspan></text>')
    for y, line in [(108, "别看我这样子，其实我之前是个二次元.jpg"), (134, "虽然从来没有认可过自己的技术……但姑且就认为是技术宅吧！"),
                    (160, "毕竟去异世界这种事说不定也会发生哦"), (198, "总而言之，我在做一些有趣的事，让我觉得开心的事"), (224, "如果让你也觉得有趣就再好不过了。")]:
        p.append(T(34, y, BODY, line, INK, maxw=520, op=".86"))
    # the quote: a small sticky note tucked in the corner
    p.append(note(418, 180, 142, 62, 3, op=".55"))
    p.append(f'<g transform="rotate(3 489 211)">{T(430, 205, META, "The truth shall make", ON_SUN, "m")}{T(430, 221, META, "you free.", ON_SUN, "m")}'
             f'{T(548, 236, META, "John 8:32", ON_SUN, op=SOFT, anchor="end")}</g>')
    # animated photo (konata.webp, pre-cropped to this slice), full bleed
    p.append(f'<g clip-path="url(#ph)"><image href="@img/konata.webp" x="595" y="1" width="277" height="402" preserveAspectRatio="xMidYMid slice"/><rect x="595" y="1" width="277" height="402" fill="url(#phFade)"/></g>')
    p.append(f'<rect x="595.5" y="1.5" width="276" height="401" rx="7.5" fill="none" stroke="{INK}" stroke-opacity=".1"/>')
    p.append('<rect x="596.5" y="2.5" width="274" height="399" rx="6.5" fill="none" stroke="url(#rim)" stroke-width="1.2"/>')
    # stack, one line
    p.append(tile("ts", 8, 279, 571, 124, glows=[("gSun", 560, 420, 220, "drift2")]))
    p.append(label(34, 322, "STACK"))
    x = 34
    for name in ["Dart", "Python", "TypeScript", "C++", "C#"]:
        p.append(f'<circle cx="{x + 4}" cy="{362 - 5}" r="3.5" fill="{SEA}"/>')
        p.append(T(x + 16, 362, HEAD, name, INK))
        x += 16 + width(name, HEAD) + 30
    svg("about", W, H, "吾辈是希露梅斯，别看我这样子，其实我之前是个二次元.jpg", "\n  ".join(p), ex)


# ------------------------------------------------------------------ projects (sliced bento)
TH = 4  # baked top/bottom half-gap; GitHub adds ~7px of line gap between rows


def projects():
    # row 1: hero 2/3 + package 1/3
    w1, h1 = 587, 300
    # the app itself, as a window tilted into the card
    wx, wy, ww = 338, 40, 212
    wh = ww * 404 / 640 + 16
    win = (f'<rect x="{wx + 4}" y="{wy + 6}" width="{ww}" height="{wh:.0f}" rx="10" fill="{INK}" fill-opacity=".1"/>'
           f'<clipPath id="win"><rect x="{wx}" y="{wy}" width="{ww}" height="{wh:.0f}" rx="10"/></clipPath>'
           f'<g clip-path="url(#win)"><rect x="{wx}" y="{wy}" width="{ww}" height="16" fill="{PAPER}"/>'
           f'<image href="@img/melonbang-home-light.webp" x="{wx}" y="{wy + 16}" width="{ww}" height="{ww * 404 / 640:.1f}"/></g>'
           f'<circle cx="{wx + 11}" cy="{wy + 8}" r="2.6" fill="#EA6A5A"/><circle cx="{wx + 20}" cy="{wy + 8}" r="2.6" fill="{SUN}"/><circle cx="{wx + 29}" cy="{wy + 8}" r="2.6" fill="{SEA}" fill-opacity=".7"/>'
           f'<rect x="{wx + .5}" y="{wy + .5}" width="{ww - 1}" height="{wh - 1:.0f}" rx="9.5" fill="none" stroke="{INK}" stroke-opacity=".16"/>')
    glass = (f'<g class="drift2"><circle cx="470" cy="70" r="170" fill="url(#gSea)"/></g>'
             f'<g transform="rotate(-4 {wx + ww / 2} {wy + wh / 2:.0f})"><g class="pop" style="animation-delay:.3s">{win}</g></g>')
    p = [tile("th", 8, TH, w1 - 16, h1 - 2 * TH, inner=glass)]
    p.append(marker(32, 31, 112, 10, .3))
    p.append(label(34, 38, "MAIN PROJECT", INK))
    p.append('<image href="@img/melonbang-icon.svg" x="34" y="70" width="52" height="52"/>')
    p.append(T(100, 108, DISP, "MelonBanG", INK, "m"))
    p.append(T(34, 162, BODY, "得意之作！基于 Bangumi 的追番播放器", INK, op=".86"))
    x = 34
    for c in ["多源聚合", "混合弹幕", "内置下载", "跨平台"]:
        cw = width(c, META) + 20
        p.append(f'<rect x="{x}" y="184" width="{cw:.0f}" height="26" rx="13" fill="none" stroke="{INK}" stroke-opacity=".2"/>')
        p.append(T(x + cw / 2, 201.5, META, c, INK, anchor="middle"))
        x += cw + 8
    p.append(f'<line x1="34" y1="242" x2="{w1 - 34}" y2="242" stroke="{INK}" stroke-opacity=".1"/>')
    p.append(T(34, 270, META, "Dart · Flutter", INK, op=SOFT, ls=.5))
    p.append(T(w1 - 34, 270, META, "shirumesu/MelonBanG ↗", SEA, anchor="end"))
    # dependency arrow crossing the seam (continues in the package slice)
    p.append(f'<line class="flow" x1="{w1 - 22}" y1="150" x2="{w1}" y2="150" stroke="{SEA}" stroke-width="1.6"/>')
    p.append(f'<circle cx="{w1 - 22}" cy="150" r="3" fill="{SEA}"/>')
    svg("proj-melonbang", w1, h1, "MelonBanG — 主项目", "\n  ".join(p))

    w2 = 293
    p = [tile("tp", 8, TH, w2 - 16, h1 - 2 * TH)]
    p.append(f'<line class="flow" x1="-10" y1="150" x2="24" y2="150" stroke="{SEA}" stroke-width="1.6"/>')
    p.append(f'<path d="M18 145 24 150 18 155" fill="none" stroke="{SEA}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>')
    p.append(label(32, 38, "PACKAGE"))
    p.append(T(32, 62, META, "← used by MelonBanG", INK, op=SOFT))
    p.append(T(32, 112, HEAD, "melon_libtorrent", INK, "m", maxw=236))
    p.append(T(32, 162, BODY, "MelonBanG 的下载引擎", INK, op=".86"))
    p.append(T(32, 188, BODY, "libtorrent 2.1 的 Flutter 绑定", INK, op=".86", maxw=236))
    p.append(T(32, 214, BODY, "内置 HTTP 服务，边下边播", INK, op=".86", maxw=236))
    p.append(f'<line x1="32" y1="242" x2="{w2 - 32}" y2="242" stroke="{INK}" stroke-opacity=".1"/>')
    p.append(T(32, 270, META, "C++ · macOS / Win / Linux", INK, op=SOFT, maxw=200))
    p.append(T(w2 - 32, 270, META, "↗", SEA, anchor="end"))
    svg("proj-libtorrent", w2, h1, "melon_libtorrent — MelonBanG 的下载引擎", "\n  ".join(p))

    # row 2: three mid projects
    feather = (f'<path d="M14 40C16 26 24 12 40 6C39 20 32 32 17 38Z" fill="none" stroke="{SEA}" stroke-width="1.6" stroke-linejoin="round"/>'
               f'<path d="M10 44 34 14M22 28 29 29M26 22 33 22M18 34 24 35" stroke="{SEA}" stroke-width="1.4" stroke-linecap="round"/>')
    mids = [
        ("uibot", "羽衣 bot", f'<g transform="translate(28 24)">{feather}</g>', "基于 Nonebot 的 QQ 机器人", "搜图、订阅、彩云续写……", "Python", 0),
        ("neopot", "Neo-pot", '<image href="@img/neopot-icon.webp" x="28" y="26" width="44" height="44"/>', "pot-desktop 的现代化重构", "划词翻译 + OCR，跨平台", "TypeScript", 1),
        ("arubox", "arubox", '<image href="@img/arubox-icon.svg" x="28" y="26" width="44" height="44"/>', "托盘常驻的个人工具箱", "桌面整理・启动器・截图・翻译", "Go · TypeScript · macOS / Win", 2),
    ]
    h2 = 212
    for key, name, icon, d1, d2, meta, i in mids:
        x0 = 8
        p = [tile("tm", x0, TH, 293 - 16, h2 - 2 * TH)]
        p.append(icon.replace('x="28"', f'x="{x0 + 27}"').replace("translate(28 ", f"translate({x0 + 27} "))
        p.append(T(x0 + 27, 100, HEAD, name, INK, "m"))
        p.append(T(x0 + 27, 134, BODY, d1, INK, op=".86", maxw=234))
        p.append(T(x0 + 27, 158, BODY, d2, INK, op=".86", maxw=234))
        p.append(T(x0 + 27, 190, META, meta, INK, op=SOFT, ls=.5))
        p.append(T(x0 + 250, 190, META, "↗", SEA, anchor="end"))
        svg(f"proj-{key}", 293, h2, name, "\n  ".join(p))

    # row 3: three small · row 4: two compact
    smalls = [("gptize", "GPTize", "好玩", "让文本变成 GPT 一样味大。"), ("antianime", "反二次元许可证", "好玩", "二次元完蛋了喵！")]
    h3 = 128
    for i, (key, name, cat, desc) in enumerate(smalls):
        x0 = 8
        p = [tile("tsm", x0, TH, 293 - 16, h3 - 2 * TH)]
        p.append(T(x0 + 23, 36, META, cat, INK, op=SOFT, ls=2))
        p.append(T(x0 + 254, 36, META, "↗", SEA, anchor="end"))
        p.append(T(x0 + 23, 76, HEAD, name, INK, "m", maxw=236))
        p.append(T(x0 + 23, 104, BODY, desc, INK, op=".86", maxw=236))
        svg(f"row-{key}", 293, h3, f"{name} — {desc}", "\n  ".join(p))
    ad_slot(h3)
    mods = [("sharespire", "ShareTheSpire2", "杀戮尖塔 2 物品共享模组"), ("shopsts2", "Shop-Enhancement-STS2", "杀戮尖塔 2 商店体验增强模组")]
    h4 = 84
    for i, (key, name, desc) in enumerate(mods):
        x0 = 8
        p = [tile("tmo", x0, TH, 440 - 16, h4 - 2 * TH)]
        p.append(T(x0 + 23, 37, META, "MOD · 非原创", INK, op=SOFT, ls=2))
        p.append(T(x0 + 23, 64, BODY, name, INK, "m", maxw=200))
        p.append(T(x0 + 400, 64, META, desc, INK, op=SOFT, anchor="end", maxw=180))
        p.append(T(x0 + 400, 37, META, "↗", SEA, anchor="end"))
        svg(f"row-{key}", 440, h4, f"{name} — {desc}", "\n  ".join(p))


def ad_slot(h):
    """Joke sponsor tile: a vacant ad slot 'trusted by' big names. The guest logos keep their
    own brand colours (that is the joke) and are drawn small and flat; a note says it is fake."""
    x0 = 8
    p = [tile("tad", x0, TH, 293 - 16, h - 2 * TH, glows=[("gSun", 250, 130, 120, "drift")])]
    p.append(T(x0 + 23, 36, META, "SPONSORED", INK, op=SOFT, ls=2))
    p.append(T(x0 + 254, 36, META, "虚位以待", SEA, anchor="end"))
    p.append(marker(x0 + 21, 64, width("广告位招租", HEAD, "m") + 6, 10, .3))
    p.append(T(x0 + 23, 76, HEAD, "广告位招租", INK, "m"))
    # trusted by: G · four squares · your logo here
    y = 99
    p.append(T(x0 + 23, y + 4, META, "trusted by", INK, op=SOFT, ls=.5))
    gx, r = x0 + 100, 6.6
    c = 2 * math.pi * r
    for col, a0, a1 in [("#4285F4", 0, 48), ("#34A853", 48, 140), ("#FBBC05", 140, 214), ("#EA4335", 214, 318)]:
        seg = c * (a1 - a0) / 360
        p.append(f'<circle cx="{gx}" cy="{y}" r="{r}" fill="none" stroke="{col}" stroke-width="3" '
                 f'stroke-dasharray="{seg:.2f} {c:.2f}" stroke-dashoffset="{-c * a0 / 360:.2f}"/>')
    p.append(f'<rect x="{gx}" y="{y - 1.5}" width="{r + 1.5}" height="3" fill="#4285F4"/>')
    mx = gx + 16
    for i, col in enumerate(["#F25022", "#7FBA00", "#00A4EF", "#FFB900"]):
        p.append(f'<rect x="{mx + (i % 2) * 7.4:.1f}" y="{y - 7 + (i // 2) * 7.4:.1f}" width="6.6" height="6.6" fill="{col}"/>')
    bx = mx + 24
    p.append(f'<rect x="{bx}" y="{y - 7.5}" width="15" height="15" rx="3" fill="none" stroke="{INK}" stroke-opacity=".35" stroke-dasharray="2 2"/>')
    p.append(T(bx + 7.5, y + 4, META, "?", INK, op=SOFT, anchor="middle"))
    p.append(T(x0 + 254, y + 4, META, "*纯属虚构", INK, op=SOFT, anchor="end"))
    svg("row-ad", 293, h, "广告位招租 — 虚位以待（赞助商标志纯属娱乐）", "\n  ".join(p))


# ------------------------------------------------------------------ my website / one more thing
def site():
    w, h = 880, 300
    ex = ('<clipPath id="pc"><rect x="8" y="1" width="864" height="298" rx="8"/></clipPath>'
          '<clipPath id="gl"><rect x="572" y="20" width="280" height="260" rx="10"/></clipPath>'
          '<filter id="frost" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="14"/></filter>'
          '<clipPath id="av"><circle cx="616" cy="76" r="22"/></clipPath>'
          f'<linearGradient id="side" x1="0" y1="0" x2="1" y2="0"><stop offset=".45" stop-color="{PAPER}" stop-opacity="0"/><stop offset="1" stop-color="{PAPER}" stop-opacity=".5"/></linearGradient>'
          '<image id="photo" href="@img/site-photo.jpg" x="8" y="-60" width="864" height="486" preserveAspectRatio="xMidYMid slice"/>')
    img = '<use href="#photo"/>'  # drawn twice (sharp + frosted); inlined once
    p = [f'<g clip-path="url(#pc)">{img}<rect x="8" y="1" width="864" height="298" fill="url(#side)"/>'
         f'<g clip-path="url(#gl)"><g filter="url(#frost)">{img}</g>'
         f'<rect x="572" y="20" width="280" height="260" fill="#FFFFFF" fill-opacity=".64"/></g></g>']
    p.append(f'<rect x="572.5" y="20.5" width="279" height="259" rx="9.5" fill="none" stroke="{INK}" stroke-opacity=".12"/>')
    p.append('<rect x="573.5" y="21.5" width="277" height="257" rx="8.5" fill="none" stroke="url(#rim)" stroke-width="1.4"/>')
    p.append(f'<rect x="8.5" y="1.5" width="863" height="297" rx="7.5" fill="none" stroke="{INK}" stroke-opacity=".1"/>')
    p.append(label(594, 46, "BLOG"))
    p.append('<g clip-path="url(#av)"><image href="@img/site-avatar.jpg" x="594" y="54" width="44" height="44"/></g>')
    p.append(f'<circle cx="616" cy="76" r="22" fill="none" stroke="#FFFFFF" stroke-width="2"/>')
    p.append(T(652, 88, DISP, "杜撰录", INK, "m", ls=2))
    p.append(T(594, 142, BODY, "总该写点什么，我说。", INK))
    p.append(T(594, 168, META, "随笔・技术・AI・偶尔的碎碎念", INK, op=SOFT))
    p.append(f'<line x1="594" y1="230" x2="830" y2="230" stroke="{INK}" stroke-opacity=".12"/>')
    p.append(T(594, 260, BODY, "konataizumi.com", SEA, "m"))
    p.append(T(830, 260, BODY, "↗", SEA, anchor="end"))
    svg("site", w, h, "杜撰录 · konataizumi.com", "\n  ".join(p), ex)


def support():
    p = [tile("tc", 8, 1, 864, 118, glows=[("gSun", 780, 120, 260, "drift"), ("gSea", 80, 0, 200, "drift2")])]
    p.append(label(34, 36, "SUPPORT"))
    p.append(T(34, 70, HEAD, "感谢你能喜欢我的作品？", INK, "m"))
    p.append(T(34, 98, BODY, "一瓶波子汽水、一杯咖啡，都会变成下一个项目的燃料。", INK, op=".86"))
    p.append(f'<rect x="616" y="36" width="230" height="48" rx="8" fill="{SUN}"/>')
    p.append(f'<rect x="617" y="37" width="228" height="46" rx="7" fill="none" stroke="url(#rim)" stroke-width="1.2"/>')
    p.append(T(638, 65, BODY, "Buy me a coffee", ON_SUN, "m"))
    p.append(T(826, 65, BODY, "↗", ON_SUN, anchor="end"))
    svg("support", 880, 120, "感谢你能喜欢我的作品？ Buy me a coffee", "\n  ".join(p))


def footer():
    p = [tile("tf", 8, 1, 864, 150, glows=[("gSea", 800, 80, 180, "drift")], dots=True)]
    p.append(T(34, 66, DISP, "© 2006 ~ 2026", INK, "m", ls=1))
    p.append(T(34, 98, BODY, "埼玉・糟日部・陵樱学园高等部 / SOS团", INK, op=".86", ls=.5))
    p.append(T(82, 120, META, "konakona", INK, op=SOFT, anchor="middle", ls=2))
    p.append(T(34, 138, BODY, "@shirumesu", SEA, "m"))
    p.append(f'<path class="draw" d="M32 145 C 56 142 96 146 132 143" fill="none" stroke="{SEA}" stroke-width="1.4" stroke-linecap="round"/>')
    p.append(f'<line x1="700" y1="22" x2="700" y2="130" stroke="{INK}" stroke-opacity=".12" stroke-dasharray="3 4"/>')
    p.append('<image href="@img/sos-logo.webp" x="742" y="16" width="96" height="119"/>')
    svg("footer", 880, 152, "© 2006 ~ 2026 埼玉 · 糟日部 · 陵樱学园高等部 / SOS团 @shirumesu", "\n  ".join(p))


if __name__ == "__main__":
    for f in SRC.glob("*.svg"):
        f.unlink()
    for DARK in (False, True):
        banner(); titles(); about(); projects(); site(); support(); footer()
    print("\n".join(sorted(f.name for f in SRC.glob("*.svg"))))
