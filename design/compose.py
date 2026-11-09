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
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build  # noqa: E402

SRC = pathlib.Path(__file__).resolve().parent / "src"

INK, PAPER, SEA, SUN = "#1F3A4A", "#FAFCFB", "#177F98", "#F4D35E"
META, BODY, HEAD, DISP = 12, 15, 20, 32
SOFT = ".62"  # secondary text opacity
LAST_UPDATED = "2026.11.09 Mon."

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
    @media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
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
    (SRC / f"{name}.svg").write_text(out)


def T(x, y, s, txt, fill=INK, w="r", anchor=None, ls=None, maxw=None, op=None, v=False, cls=None, style=None):
    a = [f'x="{x}" y="{y}" font-size="{s}" fill="{fill}"']
    if w == "m":
        a.append('data-w="m"')
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
_clip_n = 0


def written(x, y, s, txt, fill=INK, w="r", op=None, ls=0, v=False, delay=0.0, rot=None, anchor=None):
    """Phrase that is 'written in' left→right (or top→bottom). Falls back to fully visible without SMIL."""
    global _clip_n
    _clip_n += 1
    cid = f"wr{_clip_n}"
    if v:
        n = len(txt)
        W, H = s * 1.3, n * (s + ls) + 4
        cx, cy = x - W / 2, y - 2
        attr = "height"
        full = H
    else:
        tw = width(txt, s, w, ls)
        W, H = tw + 10, s * 1.45
        cx = (x - tw / 2 if anchor == "middle" else x) - 4
        cy = y - s * 1.08
        attr = "width"
        full = W
    dur = delay + 0.25 + min(1.2, len(txt) * 0.05)
    k = delay / dur
    clip = (f'<clipPath id="{cid}"><rect x="{cx:.1f}" y="{cy:.1f}" width="{W:.1f}" height="{H:.1f}">'
            f'<animate attributeName="{attr}" values="0;0;{full:.1f}" keyTimes="0;{k:.3f};1" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
    t = T(x, y, s, txt, fill, w, anchor, ls or None, op=op, v=v)
    g = f'{clip}<g clip-path="url(#{cid})">{t}</g>'
    return f'<g transform="rotate({rot})">{g}</g>' if rot else g


def note(x, y, w, h, rot, fill=SUN, op=".5", tape=True):
    """Flat sticky note / index tab."""
    t = (f'<rect x="{x + w / 2 - 22}" y="{y - 7}" width="44" height="14" fill="{PAPER}" fill-opacity=".85" '
         f'stroke="{INK}" stroke-opacity=".08"/>') if tape else ""
    return (f'<g transform="rotate({rot} {x + w / 2} {y + h / 2})"><rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="{fill}" fill-opacity="{op}"/>{t}</g>')


def banner():
    W, H = 880, 404
    p = [tile("pg", 8, 1, 864, 400, 10, glows=[("gSea", 120, 40, 320, "drift"), ("gSun", 790, 380, 300, "drift2")], dots=True, grain=True, hair=".12")]
    # header line: journal date
    p.append(f'<line x1="610" y1="44" x2="852" y2="44" stroke="{INK}" stroke-opacity=".18"/>')
    p.append(T(612, 38, META, "Last updated", INK, op=SOFT, ls=1))
    p.append(T(852, 38, BODY, LAST_UPDATED, INK, anchor="end"))
    p.append(f'<g transform="rotate(-90 36 372)">{T(36, 372, META, "SHIRUMESU’S NOTE", INK, op=".4", ls=4)}</g>')
    p.append(f'<rect x="300" y="-6" width="116" height="22" fill="{SEA}" fill-opacity=".14" transform="rotate(-3 358 5)"/>')

    d = iter([i * 0.09 for i in range(40)])
    # row 1
    p.append(f'<path class="draw" style="animation-delay:.9s" d="M106 70 C 200 64 330 72 450 66 S 540 64 562 68" fill="none" stroke="{SEA}" stroke-width="2.2" stroke-linecap="round"/>')
    p.append(written(106, 58, 29, "ただの人間には興味ありません!", INK, "m", ls=.5, delay=next(d)))
    p.append(written(142, 92, 12.5, "你能回到过去拯救那个没被 QB 欺骗的我吗", INK, op=SOFT, delay=next(d)))
    p.append(written(582, 30, 17, "一即是全，全即是一", SEA, ls=1, v=True, delay=next(d)))
    p.append(written(620, 92, 16, "晚安，Sion", INK, op=SOFT, delay=next(d)))
    p.append(written(104, 128, 18, "区区小司…", SEA, delay=next(d)))
    p.append(written(236, 118, 14, "我师傅的真实身份是…好人", INK, delay=next(d)))
    p.append(written(456, 110, 17, "(=ω=.)", SEA, delay=next(d)))
    p.append(f'<path class="draw" style="animation-delay:1.4s" d="M448 104 C 446 90 470 86 492 88 C 512 90 518 100 512 108 C 504 118 470 118 456 114 C 446 110 444 100 452 94" fill="none" stroke="{INK}" stroke-opacity=".35" stroke-width="1.2" stroke-linecap="round"/>')
    p.append(written(428, 144, 18, "アッシエント!", INK, rot="-2 480 138", delay=next(d)))
    # P5R: flat ink label
    p.append(f'<g transform="rotate(-6 721 124)"><g class="fade" style="animation-delay:.5s"><rect x="606" y="96" width="230" height="56" fill="{INK}"/>'
             + T(721, 137, 35, "P5R天下第一", PAPER, "m", "middle", 1) + '</g></g>')
    p.append(written(222, 160, 21, "娶妻当如古河渚", INK, delay=next(d)))
    # 計画通り with marker
    p.append(marker(108, 210, 296, 18, .9, -1))
    p.append(written(112, 230, 48, "計画通り…", INK, "m", ls=1, delay=next(d)))
    p.append(written(408, 196, 15, "原来你真是美发师啊", SEA, delay=next(d)))
    # EL PSY on sea tape
    p.append(f'<g transform="rotate(-3 735 206)"><rect x="626" y="188" width="218" height="34" fill="{SEA}" fill-opacity=".12"/>'
             + written(735, 212, 18, "EL PSY CONGROO", INK, anchor="middle", ls=2, delay=next(d)) + "</g>")
    p.append(written(420, 250, 23, "你这家伙在看我吧", INK, rot="-2 510 242", delay=next(d)))
    p.append(written(642, 262, 16, "秀吉的性别是秀吉啊!", SEA, delay=next(d)))
    p.append(written(113, 250, 14, "吾且问，汝为人乎", INK, op=SOFT, ls=1, v=True, delay=next(d)))
    p.append(written(140, 276, 14, "立于浮华之世，奏响天籁之音。", INK, op=SOFT, delay=next(d)))
    p.append(written(140, 310, 19, "为了我，成为炎拳吧", INK, delay=next(d)))
    p.append(written(138, 340, 15, "家庭教师是你真的太好了", SEA, delay=next(d)))
    p.append(written(150, 376, 14, "有木有WIFI?", INK, delay=next(d)))
    p.append(written(380, 292, 15, "请别忘记，这最棒的一年。", SEA, delay=next(d)))
    p.append(f'<path class="draw" style="animation-delay:2s" d="M380 299 C 440 296 500 300 562 296" fill="none" stroke="{SEA}" stroke-opacity=".5" stroke-width="1.4" stroke-linecap="round"/>')
    p.append(written(600, 290, 13, "淑女只让她心仪的人摸她的头发哦", INK, op=SOFT, delay=next(d)))
    p.append(written(390, 334, 21, "友情・努力・勝利", INK, "m", ls=1, delay=next(d)))
    # 放課後 on a sticky note
    p.append(note(618, 304, 188, 38, 2))
    p.append(f'<g transform="rotate(2 712 323)">{written(712, 330, 19, "放課後ティータイム", INK, anchor="middle", delay=next(d))}</g>')
    p.append(written(322, 370, 29, "貧乳はステータスだ、希少価値だ!", SEA, ls=.5, delay=next(d)))
    p.append(f'<path class="draw" style="animation-delay:2.6s" d="M318 382 Q 360 377 400 382 T 480 382 T 560 382 T 640 382 T 720 382 T 790 380" fill="none" stroke="{INK}" stroke-opacity=".28" stroke-width="1.6" stroke-linecap="round"/>')
    # two tiny sun dots as the only ornament
    p.append(f'<circle class="blink" cx="548" cy="100" r="3" fill="{SUN}"/><circle class="blink" style="animation-delay:-1.6s" cx="842" cy="356" r="3" fill="{SUN}"/>')
    svg("banner", W, H, f"shirumesu's notebook · last updated {LAST_UPDATED}", "\n  ".join(p))


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
    p.append(f'<g transform="rotate(3 489 211)">{T(430, 205, META, "The truth shall make", INK, "m")}{T(430, 221, META, "you free.", INK, "m")}'
             f'{T(548, 236, META, "John 8:32", INK, op=SOFT, anchor="end")}</g>')
    # gif, full bleed
    p.append(f'<g clip-path="url(#ph)"><image href="@img/konata.gif" x="595" y="1" width="277" height="402" preserveAspectRatio="xMidYMid slice"/><rect x="595" y="1" width="277" height="402" fill="url(#phFade)"/></g>')
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
    glass = (f'<g class="drift2"><circle cx="470" cy="70" r="150" fill="url(#gSea)"/></g>'
             f'<rect x="330" y="-30" width="210" height="190" rx="14" fill="#FFFFFF" fill-opacity=".38" stroke="#FFFFFF" stroke-opacity=".9" transform="rotate(14 435 65)"/>'
             f'<rect x="402" y="26" width="160" height="150" rx="12" fill="#FFFFFF" fill-opacity=".3" stroke="{SEA}" stroke-opacity=".12" transform="rotate(-8 482 101)"/>')
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
    gei = T(24, 33, HEAD, "芸", SEA, "m", "middle")
    mids = [
        ("uibot", "羽衣 bot", f'<g transform="translate(28 24)">{feather}</g>', "基于 Nonebot 的 QQ 机器人", "搜图、订阅、彩云续写……", "Python", 0),
        ("neopot", "Neo-pot", '<image href="@img/neopot-icon.png" x="28" y="26" width="44" height="44"/>', "pot-desktop 的现代化重构", "划词翻译 + OCR，跨平台", "TypeScript", 1),
        ("gei", "芸", f'<g transform="translate(28 26)"><rect width="44" height="44" rx="8" fill="{SEA}" fill-opacity=".08" stroke="{SEA}" stroke-opacity=".3"/><g transform="translate(-2 4)">{gei}</g></g>', "一套 Skill，开箱即用", "涵盖所有使用场景", "AI · Skills", 2),
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
    smalls = [("gptize", "GPTize", "好玩", "让文本变成 GPT 一样味大。"), ("respond", "Respond-like-human", "好玩", "让你的 GPT 说人话"),
              ("antianime", "反二次元许可证", "好玩", "二次元完蛋了喵！")]
    h3 = 128
    for i, (key, name, cat, desc) in enumerate(smalls):
        x0 = 8
        p = [tile("tsm", x0, TH, 293 - 16, h3 - 2 * TH)]
        p.append(T(x0 + 23, 36, META, cat, INK, op=SOFT, ls=2))
        p.append(T(x0 + 254, 36, META, "↗", SEA, anchor="end"))
        p.append(T(x0 + 23, 76, HEAD, name, INK, "m", maxw=236))
        p.append(T(x0 + 23, 104, BODY, desc, INK, op=".86", maxw=236))
        svg(f"row-{key}", 293, h3, f"{name} — {desc}", "\n  ".join(p))
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


# ------------------------------------------------------------------ my website / one more thing
def site():
    w, h = 880, 300
    ex = ('<clipPath id="pc"><rect x="8" y="1" width="864" height="298" rx="8"/></clipPath>'
          '<clipPath id="gl"><rect x="572" y="20" width="280" height="260" rx="10"/></clipPath>'
          '<filter id="frost" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="14"/></filter>'
          '<clipPath id="av"><circle cx="616" cy="76" r="22"/></clipPath>'
          f'<linearGradient id="side" x1="0" y1="0" x2="1" y2="0"><stop offset=".45" stop-color="{PAPER}" stop-opacity="0"/><stop offset="1" stop-color="{PAPER}" stop-opacity=".5"/></linearGradient>')
    img = '<image href="@img/site-photo.jpg" x="8" y="-60" width="864" height="486" preserveAspectRatio="xMidYMid slice"/>'
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
    p.append(T(638, 65, BODY, "Buy me a coffee", INK, "m"))
    p.append(T(826, 65, BODY, "↗", INK, anchor="end"))
    svg("support", 880, 120, "感谢你能喜欢我的作品？ Buy me a coffee", "\n  ".join(p))


def footer():
    p = [tile("tf", 8, 1, 864, 150, glows=[("gSea", 800, 80, 180, "drift")], dots=True)]
    p.append(T(34, 66, DISP, "© 2006 ~ 2026", INK, "m", ls=1))
    p.append(T(34, 98, BODY, "埼玉・糟日部・陵樱学园高等部 / SOS团", INK, op=".86", ls=.5))
    p.append(T(82, 120, META, "konakona", INK, op=SOFT, anchor="middle", ls=2))
    p.append(T(34, 138, BODY, "@shirumesu", SEA, "m"))
    p.append(f'<path class="draw" d="M32 145 C 56 142 96 146 132 143" fill="none" stroke="{SEA}" stroke-width="1.4" stroke-linecap="round"/>')
    p.append(f'<line x1="700" y1="22" x2="700" y2="130" stroke="{INK}" stroke-opacity=".12" stroke-dasharray="3 4"/>')
    p.append('<image href="@img/sos-logo.png" x="742" y="16" width="96" height="119"/>')
    svg("footer", 880, 152, "© 2006 ~ 2026 埼玉 · 糟日部 · 陵樱学园高等部 / SOS团 @shirumesu", "\n  ".join(p))


if __name__ == "__main__":
    for f in SRC.glob("*.svg"):
        f.unlink()
    banner(); titles(); about(); projects(); site(); support(); footer()
    print("\n".join(sorted(f.name for f in SRC.glob("*.svg"))))
