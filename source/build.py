"""Build the Sandgarden theme for T3 Code: sandgarden.json (+ preview SVGs in assets/svg)."""
import json, math, os, random

HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------ garden art
# All art is STATIC svg (no animation inside images). Motion is done by the CSS below,
# on gutter-sized pseudo-elements, with transform-cheap properties only.
SW, SHT, MID = 190, 1400, 700   # one margin strip: 190 wide, 1400 tall (centred on the conversation area, cropped by it)
NL, X0, PITCH = 20, 8, 9
RAKE = "112,92,52"
MOSS_RGB = "74,94,62"
MOSS_F = "64,108,48"
STONE = "rgb(104,100,92)"
SERIF = '"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif'
# stone = (cx, cy, rx, ry, rot, rings); cy is in strip space (MID = vertical centre)
STRIPS = {
    "l": [(100, 570, 28, 20, -20, 3), (150, 670, 12, 9, 30, 2), (85, 850, 36, 25, 12, 3)],
    "r": [(95, 680, 34, 24, 18, 3), (140, 515, 12, 9, -25, 2), (125, 890, 26, 18, -10, 3)],
}
GAP = 9
HDR_BG = "#ece2cb"


def f(x):
    s = f"{x:.1f}"
    return s[:-2] if s.endswith(".0") else s


def t10(v):
    s = f"{v / 10:.1f}"
    s = s[:-2] if s.endswith(".0") else s
    return s.replace("0.", ".", 1) if s.startswith("0.") else s.replace("-0.", "-.", 1) if s.startswith("-0.") else s


def data_uri(svg):
    out = svg.replace("%", "%25").replace("#", "%23").replace('"', "'").replace("<", "%3C").replace(">", "%3E")
    return 'url("data:image/svg+xml,' + out + '")'


def ring_dims(s):
    return [(s[2] + 8 + j * GAP, s[3] + 8 + j * GAP) for j in range(s[5])]


def hole(s):
    rx, ry = ring_dims(s)[-1]
    return rx + 4, ry + 4


def hole_list(kind):
    return [(s[0], s[1], *hole(s)) for s in STRIPS[kind]]


def rake(holes, w, h, nl, x0, pitch, alpha, seed, sway=1.1, bulge=.34, edge=True, dense=22, coarse=250):
    """Furrows that flow round each stone: the horizontal push is zero above/below the stone and largest at its flanks, decaying with elliptical distance. Returns bare paths (colour comes from the <use>)."""
    rnd = random.Random(seed)
    ys = {-2, h + 2}
    ys.update(range(0, h + 1, coarse))
    for cx, cy, rx, ry in holes:
        ys.update(range(int(cy - ry * 2.4), int(cy + ry * 2.4), dense))
    ys = sorted(y for y in ys if -2 <= y <= h + 2)

    def dx(x, y):
        t = 0
        for cx, cy, rx, ry in holes:
            u, v = (x - cx) / rx, (y - cy) / ry
            q = max(1.0, math.hypot(u, v))
            t += max(-1.3, min(1.3, u)) * rx * bulge * math.exp(-(q - 1) * 2.2)
        return t

    out = []
    for i in range(nl):
        x = x0 + i * pitch + rnd.uniform(-.5, .5)
        a = rnd.uniform(*alpha)
        ph = rnd.uniform(0, 6.28)
        if edge:
            a *= .45 if i in (0, nl - 1) else (.75 if i in (1, nl - 2) else 1)
        pts = [(round((x + dx(x, y) + sway * math.sin(y / 110 + ph)) * 10), y * 10) for y in ys]
        d = f"M{t10(pts[0][0])} {t10(pts[0][1])}q"
        cx_, cy_ = pts[0]
        nums = []
        for k in range(1, len(pts) - 1):
            mx, my = (pts[k][0] + pts[k + 1][0]) // 2, (pts[k][1] + pts[k + 1][1]) // 2
            nums += [pts[k][0] - cx_, pts[k][1] - cy_, mx - cx_, my - cy_]
            cx_, cy_ = mx, my
        d += " ".join(t10(v) for v in nums) + f"l{t10(pts[-1][0] - cx_)} {t10(pts[-1][1] - cy_)}"
        out.append(f"<path d='{d}' stroke-opacity='{a:.2f}'/>")
    return "".join(out)


TONES = (("#9a9588", "#5d5951"), ("#a39682", "#675a46"), ("#8a9091", "#555b5d"))


def stone_path(cx, cy, rx, ry, seed):
    rnd = random.Random(seed)
    pts = []
    for k in range(8):
        a = k * math.pi / 4
        j = rnd.uniform(.9, 1.08)
        pts.append((cx + rx * j * math.cos(a), cy + ry * j * math.sin(a)))
    mid = lambda p, q: ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    m0 = mid(pts[-1], pts[0])
    d = f"M{f(m0[0])} {f(m0[1])}"
    for k in range(8):
        m = mid(pts[k], pts[(k + 1) % 8])
        d += f"Q{f(pts[k][0])} {f(pts[k][1])} {f(m[0])} {f(m[1])}"
    return d + "Z"


def stone_svg(s, i=0):
    cx, cy, rx, ry, rot, _ = s
    hi, lo = TONES[i % 3]
    g = f"sg{i}"
    body = stone_path(cx, cy, rx, ry, cx * 7 + cy)
    return (f"<defs><radialGradient id='{g}' cx='.36' cy='.28' r='.85'><stop offset='0' stop-color='{hi}'/><stop offset='.55' stop-color='{lo}'/>"
            f"<stop offset='.9' stop-color='#6e6048'/><stop offset='1' stop-color='#8a7650'/></radialGradient>"
            f"<filter id='{g}b' x='-30%' y='-30%' width='160%' height='160%'><feGaussianBlur stdDeviation='2.2'/></filter></defs>"
            f"<g transform='rotate({rot} {cx} {cy})'><ellipse cx='{cx+4}' cy='{cy+5}' rx='{f(rx+1)}' ry='{f(ry)}' fill='rgba(60,46,24,.34)' filter='url(#{g}b)'/>"
            f"<path d='{body}' fill='url(#{g})'/>"
            f"<ellipse cx='{f(cx-rx*.25)}' cy='{f(cy-ry*.38)}' rx='{f(rx*.4)}' ry='{f(ry*.24)}' fill='rgba(255,252,240,.2)'/></g>")


def ring_svg(s, color, width=1.2, light=True):
    out = ""
    for rx, ry in ring_dims(s):
        out += f"<ellipse cx='{s[0]}' cy='{s[1]}' rx='{f(rx)}' ry='{f(ry)}' fill='none' stroke='{color}' stroke-width='{width}'/>"
        if light:
            out += f"<ellipse cx='{s[0] + 1.4}' cy='{s[1] + 1.2}' rx='{f(rx)}' ry='{f(ry)}' fill='none' stroke='rgba(255,251,238,.7)' stroke-width='{width * .8:.1f}'/>"
    return out


def fade_defs(h, top=.075, bot=.075):
    return (f"<linearGradient id='fg' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='black'/><stop offset='{top}' stop-color='white'/>"
            f"<stop offset='{1-bot}' stop-color='white'/><stop offset='1' stop-color='black'/></linearGradient>")


def hole_mask_svg(holes, w, h):
    hs = "".join(f"<ellipse cx='{cx}' cy='{cy}' rx='{f(rx)}' ry='{f(ry)}' fill='black'/>" for cx, cy, rx, ry in holes)
    return (f"<mask id='m' maskUnits='userSpaceOnUse' x='0' y='0' width='{w}' height='{h}'><rect width='{w}' height='{h}' fill='url(#fg)'/>{hs}</mask>")


def seed_of(kind):
    return 11 if kind == "l" else 23


def strip_svg(kind):
    """Sand garden: each furrow is a raked groove (dark line + lit edge), bent round the stones, with rings and stones on top."""
    stones = STRIPS[kind]
    body = (f"<defs>{fade_defs(SHT)}{hole_mask_svg(hole_list(kind), SW, SHT)}"
            f"<g id='F' fill='none' stroke-width='1.2' stroke-linecap='round'>{rake(hole_list(kind), SW, SHT, NL, X0, PITCH, (.3, .44), seed_of(kind))}</g></defs>"
            f"<g mask='url(#m)'><use href='#F' stroke='rgb({RAKE})'/><use href='#F' x='1.5' y='.4' stroke='rgb(255,251,238)' opacity='.85'/></g>"
            f"<g mask='url(#fm)'>" + "".join(ring_svg(s, f"rgba({RAKE},.4)") for s in stones) + "</g>"
            + "".join(stone_svg(s, i) for i, s in enumerate(stones)))
    body = body.replace("<defs>", f"<defs><mask id='fm' maskUnits='userSpaceOnUse' x='0' y='0' width='{SW}' height='{SHT}'><rect width='{SW}' height='{SHT}' fill='url(#fg)'/></mask>", 1)
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {SW} {SHT}'>{body}</svg>"


def moss_svg(kind):
    """The same furrows in moss (same bends and holes). Revealed by a mask wipe while a turn runs."""
    body = (f"<defs>{fade_defs(SHT)}{hole_mask_svg(hole_list(kind), SW, SHT)}"
            f"<g id='F' fill='none' stroke-linecap='round'>{rake(hole_list(kind), SW, SHT, NL, X0, PITCH, (1, 1), seed_of(kind))}</g></defs>"
            f"<g mask='url(#m)'><use href='#F' stroke='rgb(241,233,214)' stroke-width='3.6' opacity='.92'/><use href='#F' stroke='rgb({MOSS_F})' stroke-width='1.4' opacity='.52'/></g>")
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {SW} {SHT}'>{body}</svg>"


def ring_layer(s):
    """One stone's moss rings as their own image, so each set can spread from its own stone centre."""
    rx, ry = ring_dims(s)[-1]
    W, H = int(2 * rx + 6), int(2 * ry + 6)
    ell = "".join(f"<ellipse cx='{W/2}' cy='{H/2}' rx='{f(a)}' ry='{f(b)}' fill='none' stroke='rgba({MOSS_RGB},.6)' stroke-width='1'/>" for a, b in ring_dims(s))
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}'>{ell}</svg>", W, H


MWD, MTH = 72, 240          # narrow-gutter strips: a 72x240 stone tile (furrows bent round one stone, two rings) between two plain furrow pieces
MST = (36, 120, 10, 7, 16, 2)
MHOLE = [(36, 120, *hole(MST))]
MSEED = 7


def mini_tile(moss=False):
    """Stone tile: 7 furrows round one small stone with two rings, straight at the tile's top and bottom edges so it joins the plain pieces. Moss version erases the sand grooves under it."""
    p = rake(MHOLE, MWD, MTH, 7, 6, 10, (1, 1) if moss else (.3, .44), MSEED, sway=0, dense=14, coarse=160)
    mk = f"<mask id='m' maskUnits='userSpaceOnUse' x='0' y='0' width='{MWD}' height='{MTH}'><rect width='{MWD}' height='{MTH}' fill='white'/><ellipse cx='36' cy='120' rx='{f(MHOLE[0][2])}' ry='{f(MHOLE[0][3])}' fill='black'/></mask>"
    if moss:
        body = (f"<defs>{mk}<g id='F' fill='none' stroke-linecap='round'>{p}</g></defs><g mask='url(#m)'><use href='#F' stroke='rgb(241,233,214)' stroke-width='3.6' opacity='.92'/>"
                f"<use href='#F' stroke='rgb({MOSS_F})' stroke-width='1.4' opacity='.52'/></g>{ring_svg(MST, f'rgba({MOSS_RGB},.6)', 1, False)}")
    else:
        body = (f"<defs>{mk}<g id='F' fill='none' stroke-width='1.2' stroke-linecap='round'>{p}</g></defs><g mask='url(#m)'><use href='#F' stroke='rgb({RAKE})'/>"
                f"<use href='#F' x='1.5' y='.4' stroke='rgb(255,251,238)' opacity='.85'/></g>{ring_svg(MST, f'rgba({RAKE},.4)')}" + stone_svg(MST, 1))
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {MWD} {MTH}'>{body}</svg>"


def mini_line(moss=False):
    """Stone-free furrow piece (same seed, so the same x positions as the stone tile); stretched vertically to fill the gutter height (preserveAspectRatio none keeps vertical lines identical)."""
    p = rake([], MWD, 20, 7, 6, 10, (1, 1) if moss else (.3, .44), MSEED, sway=0, coarse=160)
    if moss:
        body = (f"<defs><g id='F' fill='none' stroke-linecap='round'>{p}</g></defs><use href='#F' stroke='rgb(241,233,214)' stroke-width='3.6' opacity='.92'/>"
                f"<use href='#F' stroke='rgb({MOSS_F})' stroke-width='1.4' opacity='.52'/>")
    else:
        body = (f"<defs><g id='F' fill='none' stroke-width='1.2' stroke-linecap='round'>{p}</g></defs><use href='#F' stroke='rgb({RAKE})'/>"
                f"<use href='#F' x='1.5' y='.4' stroke='rgb(255,251,238)' opacity='.85'/>")
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {MWD} 20' preserveAspectRatio='none'>{body}</svg>"


DW, DH = 100, 36


def dock_svg(moss=False):
    """Small garden for the header rail: 10 furrows bent round one stone with two rings. The moss version erases the sand grooves under its strokes (no backdrop)."""
    st = (70, 18, 7, 5, -14, 0)
    rings = ((12, 9), (17, 13))
    holes = [(70, 18, 21, 16)]
    col = f"rgb({MOSS_F})" if moss else f"rgb({RAKE})"
    paths = rake(holes, DW, DH, 8, 4, 6.2, (1, 1) if moss else (.4, .55), 5, sway=.5, dense=6, coarse=18)
    if moss:
        rg = "".join(f"<ellipse cx='70' cy='18' rx='{a}' ry='{b}' fill='none' stroke='{HDR_BG}' stroke-width='2.4'/><ellipse cx='70' cy='18' rx='{a}' ry='{b}' fill='none' stroke='rgba({MOSS_RGB},.8)' stroke-width='1.2'/>" for a, b in rings)
        return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {DW} {DH}' preserveAspectRatio='xMinYMid slice' opacity='.7'><defs><linearGradient id='fg' x1='0' y1='0' x2='1' y2='0'>"
                f"<stop offset='0' stop-color='black'/><stop offset='.2' stop-color='white'/><stop offset='.8' stop-color='white'/><stop offset='1' stop-color='black'/></linearGradient>"
                f"<mask id='m' maskUnits='userSpaceOnUse' x='0' y='0' width='{DW}' height='{DH}'><rect width='{DW}' height='{DH}' fill='url(#fg)'/><ellipse cx='70' cy='18' rx='21' ry='16' fill='black'/></mask>"
                f"<g id='F' fill='none' stroke-linecap='round'>{paths}</g></defs><g mask='url(#m)'><use href='#F' stroke='{HDR_BG}' stroke-width='3' opacity='.95'/><use href='#F' stroke='{col}' stroke-width='1.2' opacity='.7'/></g>{rg}</svg>")
    rg = "".join(f"<ellipse cx='70' cy='18' rx='{a}' ry='{b}' fill='none' stroke='rgba({RAKE},.5)' stroke-width='1.2'/>" for a, b in rings)
    hl = "<use href='#F' x='1.2' stroke='rgb(255,251,238)' opacity='.8'/>"
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {DW} {DH}' opacity='.7'><defs><linearGradient id='fg' x1='0' y1='0' x2='1' y2='0'>"
            f"<stop offset='0' stop-color='black'/><stop offset='.2' stop-color='white'/><stop offset='.8' stop-color='white'/><stop offset='1' stop-color='black'/></linearGradient>"
            f"<mask id='m' maskUnits='userSpaceOnUse' x='0' y='0' width='{DW}' height='{DH}'><rect width='{DW}' height='{DH}' fill='url(#fg)'/>"
            f"<ellipse cx='70' cy='18' rx='21' ry='16' fill='black'/></mask>"
            f"<g id='F' fill='none' stroke-width='1.2'>{paths}</g></defs>"
            f"<g mask='url(#m)'><use href='#F' stroke='{col}'/>{hl}</g>{rg}<g opacity='.65'>" + stone_svg(st, 0) + "</g></svg>")


def wave3():
    return ("<svg xmlns='http://www.w3.org/2000/svg' width='40' height='8' viewBox='0 0 40 8'>"
            "<path d='M0 1.5Q10 -.3 20 1.5T40 1.5M0 4Q10 2.2 20 4T40 4M0 6.5Q10 4.7 20 6.5T40 6.5' fill='none' stroke='rgba(78,98,60,.78)' stroke-width='1'/></svg>")


def grain():
    return ("<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'>"
            "<feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/>"
            "<feColorMatrix values='0 0 0 0 .42  0 0 0 0 .34  0 0 0 0 .18  0 0 0 .55 -.06'/></filter>"
            "<rect width='180' height='180' filter='url(#n)'/></svg>")


# ------------------------------------------------------------ colours
colors = {
    "canvas": "#f1e9d6", "chrome": "#e8dec6", "toolbar": "#ece2cb", "toolbarForeground": "#2e2a22",
    "toolbarBorder": "#cdbf9f", "toolbarControl": "#e0d4b8", "toolbarControlForeground": "#2e2a22",
    "toolbarControlHover": "#d6c8a8", "surface": "#f7f1e2", "surfaceRaised": "#faf6ea",
    "surfaceOverlay": "#fbf8ef", "text": "#2b2822", "textMuted": "#5b5546", "border": "#cfc1a0",
    "input": "#b9aa86", "focus": "#4a5e3e", "accent": "#4a5e3e", "accentForeground": "#f7f2e3",
    "secondary": "#ddd0b0", "secondaryForeground": "#37322a", "muted": "#e6dbc1",
    "mutedForeground": "#5b5546", "placeholder": "#756d5a", "secondaryLabel": "#66604e",
    "iconMuted": "#766e5a", "error": "#a23a2c", "errorForeground": "#8c2e22", "errorSurface": "#f4ddd3",
    "warning": "#8a6212", "warningForeground": "#6b4c0b", "warningSurface": "#f2e4bc",
    "update": "#3a6470", "updateForeground": "#2c4f5a", "updateSurface": "#dce8e4",
    "accentSurface": "#dfe5cd", "accentSurfaceForeground": "#34452a", "messageSurface": "#e3d8bc",
    "messageForeground": "#2b2822", "messageAction": "#4a5e3e", "messageActionForeground": "#f7f2e3",
    "messageActionHover": "#3a4c30", "codeBackground": "#e9e0c8", "codeForeground": "#2b2822",
    "searchMatchBackground": "#ebd58c", "searchMatchForeground": "#2b2822",
    "searchMatchActiveBackground": "#4a5e3e", "searchMatchActiveForeground": "#f7f2e3",
    "sidebar": "#e7ddc4", "sidebarForeground": "#2e2a22", "sidebarMutedForeground": "#5d5748",
    "sidebarControlSurface": "#f0e7d1", "sidebarRowHover": "#ddd1b3", "sidebarRowActive": "#d7caa9",
    "sidebarRowSelected": "#d3c6a3", "sidebarBorder": "#cbbe9e", "terminalBackground": "#f3ecd8",
    "terminalForeground": "#2b2822", "terminalCursor": "#4a5e3e", "terminalSelection": "#d4d3a8",
    "terminalScrollbar": "#cdbf9f", "terminalScrollbarHover": "#b5a680",
}

CW = "var(--chat-content-max-width,46rem)"
G = f"(100% - {CW})/2"
BUSY = ('body:has([data-timeline-row-kind="working"])',
        'body:has([data-thread-item] [aria-busy="true"][aria-current]:not([aria-current="false"]))')


def busy(sel):
    return ",".join(f"{b} {sel}" for b in BUSY)


NOREDUCE = "@media (prefers-reduced-motion:no-preference)"
MOSS = "#4a5e3e"
CONV = '[data-workspace-area="conversation"]'
# strip width: 190px when the gutter can hold it with 28px to spare, else 0 (art hidden, dock takes over)
SWX = f"clamp(0px,({G} - 218px)*1000,{SW}px)"
SB = "#e7ddc4"
SBF = "repeating-linear-gradient(90deg,rgba(112,92,52,.055) 0 1px,transparent 1px 9px)"
GRAIN = "var(--sg-g) 0 0/180px 180px"

RINGS = {k: [ring_layer(st) for st in STRIPS[k]] for k in STRIPS}
vars_ = ":root{" + f"--sg-l:{data_uri(strip_svg('l'))};--sg-r:{data_uri(strip_svg('r'))};"
for k in "lr":
    vars_ += f"--sg-m{k}:{data_uri(moss_svg(k))};" + "".join(f"--sg-m{k}{i}:{data_uri(r[0])};" for i, r in enumerate(RINGS[k]))
vars_ += f"--sg-ms:{data_uri(mini_tile())};--sg-mm:{data_uri(mini_tile(True))};--sg-ls:{data_uri(mini_line())};--sg-lm:{data_uri(mini_line(True))};--sg-dock:{data_uri(dock_svg())};--sg-dockm:{data_uri(dock_svg(True))};--sg-wave:{data_uri(wave3())};--sg-g:{data_uri(grain())}}}"
PROP = "@property --sg-p{syntax:'<number>';inherits:false;initial-value:0}"


DRAW = 20      # seconds for the rake to cover both groups of margins: four passes of five furrows
B = [0, 48, 93, 138, SW]               # column edges (px) of the four rake passes (five furrows each)
GA = B[:-1]
GW = [B[k + 1] - B[k] for k in range(4)]


def pass_of(x):
    return max(k for k in range(4) if GA[k] <= x)


def mask_layers(kind):
    """Four column passes of furrows + one radial layer per stone, so each ring set appears whole once the rake reaches its column (never a half ring)."""
    img = [f"linear-gradient(#000 calc(clamp(0,var(--sg-p) - {k},1)*100%),transparent 0)" for k in range(4)]
    size = [f"{GW[k]}px 100%" for k in range(4)]
    pos = [f"{GA[k]}px 0" for k in range(4)]
    for st in STRIPS[kind]:
        hx, hy = hole(st)
        img.append(f"radial-gradient(ellipse closest-side,rgb(0 0 0/clamp(0,(var(--sg-p) - {pass_of(max(0, st[0] - hx))})*8,1)) 98%,transparent 100%)")
        size.append(f"min({f(2 * hx)}px,{PWX}) {f(2 * hy)}px")
        pos.append(f"{f(st[0] - hx)}px calc(50% + {f(st[1] - MID)}px)")
    # narrow tier: one ring mask centred on the mini stone, open once the pass that reaches it has started (zero width in the wide tier)
    mrx, mry = ring_dims(MST)[-1]
    mo = MOFF[0 if kind == "l" else 1]
    img.append(f"radial-gradient(ellipse {f(mrx + 1)}px {f(mry + 1)}px at {MST[0]}px calc(50% + {mo}px),rgb(0 0 0/clamp(0,(var(--sg-p) - {pass_of(max(0, MST[0] - mrx))})*8,1)) 98%,transparent 100%)")
    size.append(f"{PMX} 100%")
    pos.append("0 0")
    img, size, pos = ",".join(img), ",".join(size), ",".join(pos)
    return (f"mask-image:{img};-webkit-mask-image:{img};mask-size:{size};-webkit-mask-size:{size};mask-position:{pos};-webkit-mask-position:{pos};"
            "mask-repeat:no-repeat;-webkit-mask-repeat:no-repeat;")


# Inside the pseudo-elements a background-size percentage is of the pseudo's own width (190px wide tier, 72px narrow tier), so the tier is read from that:
PWX = f"clamp(0px,(100% - {MWD}px)*1000,{SW}px)"
PMX = f"clamp(0px,({MWD + 1}px - 100%)*1000,{MWD}px)"


def mbg(kind, sc):
    """Background sizes/positions of the moss layers: one ring image per stone (centred on its stone, scaled about that centre), the furrows, then the narrow-tier pieces. Wide sizes are capped by PWX (0 in the narrow tier), the narrow ones by PMX (0 in the wide tier)."""
    sizes, pos = [], []
    for st, (_, w, h) in zip(STRIPS[kind], RINGS[kind]):
        W, H = w * sc, h * sc
        sizes.append(f"min({f(W)}px,{PWX}) {f(H)}px")
        pos.append(f"{f(st[0] - W / 2)}px calc(50% + {f(st[1] - MID)}px)")
    sizes.append(f"{PWX} {SHT}px"); pos.append("0 50%")
    for _, p, z in mini_layers("", "", 0 if kind == "l" else 1, "left 0", PMX):
        sizes.append(z); pos.append(p)
    return f"background-size:{','.join(sizes)};background-position:{','.join(pos)};"


def mimgs(kind):
    return ",".join([f"var(--sg-m{kind}{i})" for i in range(len(STRIPS[kind]))] + [f"var(--sg-m{kind})", "var(--sg-mm)", "var(--sg-lm)", "var(--sg-lm)"])


DOCKPOS = "calc(100% - 176px) 50%"


def hdr(s4, x4, m):
    size = f"100% 1px,100% 1px,100% 1px,{s4} 2px,{DW}px {DH}px,{m}"
    pos = f"0 100%,0 calc(100% - 3px),0 calc(100% - 6px),{x4} calc(100% - 3px),{DOCKPOS},{DOCKPOS}"
    return f"background-size:{size};background-position:{pos};"


def furrow_rule(sel, h="6px"):
    return (f"{sel}{{border:0!important;height:{h}!important;background:linear-gradient(rgba(112,92,52,.4),rgba(112,92,52,.4)) 0 0/100% 1px no-repeat,"
            "linear-gradient(rgba(112,92,52,.26),rgba(112,92,52,.26)) 0 2px/100% 1px no-repeat,"
            "linear-gradient(rgba(112,92,52,.14),rgba(112,92,52,.14)) 0 4px/100% 1px no-repeat!important}")


TINES = ("linear-gradient(rgba(112,92,52,.4),rgba(112,92,52,.4)) 0 100%/3em 1px no-repeat,"
         "linear-gradient(rgba(112,92,52,.28),rgba(112,92,52,.28)) 0 calc(100% - 4px)/2.2em 1px no-repeat,"
         "linear-gradient(rgba(112,92,52,.16),rgba(112,92,52,.16)) 0 calc(100% - 8px)/1.4em 1px no-repeat")

C = []
add = C.append
add(vars_)
add(PROP)
# ---------------------------------------------------------------- conversation: static sand garden + grain
# Both the base garden and the moss pseudo-elements anchor their 190x1400 images at `50%` vertically (so the stones line up at every window height), and the gutter is cropped by the conversation box.
# Narrow tier (gutter 108..218px): a 72px strip with one stone per side, sand at rest, moss grows over it while busy (background-size transition). Hidden when the full strips fit or the gutter is under 108px.
MWX = f"min(clamp(0px,({G} - 108px)*1000,{MWD}px),clamp(0px,(218px - ({G}))*1000,{MWD}px))"
MOFF = (0, 120)     # the right strip's stone sits 120px lower than the left one's


def mini_layers(stone, plain, side, hx, mw=MWX):
    """Narrow tier (gutter 108..218px): the stone tile centred at 50% + offset (a position percentage is of the free space, so 50% keeps it centred) plus a plain furrow piece above and below, so the strip runs the full gutter height with no fades. hx is the horizontal position."""
    o = MOFF[side]
    hi = f"calc(50% - {MTH // 2}px + {o}px)"
    lo = f"calc(50% - {MTH // 2}px - {o}px)"
    return [(stone, f"{hx} top calc(50% + {o}px)", f"{mw} {MTH}px"), (plain, f"{hx} top 0", f"{mw} {hi}"), (plain, f"{hx} bottom 0", f"{mw} {lo}")]


def conv_bg():
    lay = [f"var(--sg-l) left 8px top 50%/{SWX} {SHT}px", f"var(--sg-r) right 8px top 50%/{SWX} {SHT}px"]
    for side, hx in ((0, "left 8px"), (1, "right 8px")):
        lay += [f"{i} {p}/{z}" for i, p, z in mini_layers("var(--sg-ms)", "var(--sg-ls)", side, hx)]
    return ",".join(x + " no-repeat" for x in lay)


add(f"{CONV}{{position:relative;background:{conv_bg()},{GRAIN},#f1e9d6!important}}")
# ---------------------------------------------------------------- margin strips (pseudo-elements, gutter sized): the moss garden
# Layers: one ring image per stone + the moss furrows, revealed by four mask passes driven by --sg-p (a registered number on the pseudo, transitioned in steps while busy).
# Turn complete is a transition, not an animation swap: opacity fades over 1.6s, each ring set spreads from its own stone, and --sg-p keeps its value for 1.6s (transition delay) before snapping back, so a turn that ends mid-draw fades the part that was drawn and never flashes the rest.
PS = f"{CONV}::before,{CONV}::after"
add(f"{PS}{{content:\"\";position:absolute;top:0;bottom:0;width:calc({SWX} + {MWX});pointer-events:none;background-repeat:no-repeat;opacity:0;--sg-p:0}}")
for pseudo, side, k in (("::before", "left", "l"), ("::after", "right", "r")):
    add(f"{CONV}{pseudo}{{{side}:8px;background-image:{mimgs(k)};{mbg(k, 1.08)}{mask_layers(k)}}}")
    add(busy(f"{CONV}{pseudo}") + "{opacity:1;--sg-p:4;" + mbg(k, 1) + "}")
add(NOREDUCE + "{")
add(f"{PS}{{transition:opacity 1.6s ease-out,background-size 1.6s ease-out,background-position 1.6s ease-out,--sg-p 0s linear 1.6s}}")
for pseudo, delay, k in (("::before", "0s", "l"), ("::after", "1s", "r")):
    add(busy(f"{CONV}{pseudo}") + "{" + f"transition:opacity .8s ease-out,background-size 0s,background-position 0s,--sg-p {DRAW}s steps(160,end) {delay};"
        + f"animation:sg-breath-{k} 12s steps(12) {'21s' if k == 'l' else '22s'} infinite alternate" + "}")
    a, b = mbg(k, 1).split(";")[:2], mbg(k, 1.07).split(";")[:2]
    add(f"@keyframes sg-breath-{k}{{from{{{a[0]};{a[1]}}}to{{{b[0]};{b[1]}}}}}")
add("}")
# ---------------------------------------------------------------- header: three furrows, a moss tine walks them while busy; a small garden sits at its right end (sand layer + a moss layer that grows over it while busy: it is part of the header's own background stack, so it always sits behind header content). It is the state signal when the margins are too narrow.
add("@property --sg-hw{syntax:'<number>';inherits:false;initial-value:0}@property --sg-t{syntax:'<number>';inherits:false;initial-value:0}")
# Header: --sg-hw (0..1) widens the moss header garden (left edge pinned, so it wipes in and out) and the 40px tine; --sg-t (0..1) walks the tine along the rail once (24s) and holds. Both are registered numbers on the header itself (the wave image is --sg-wave: the two must never share a name, see the guard at the end), so no background-* property is transitioned and nothing snaps when the turn ends: the garden retracts over .8s and the tine shrinks where it stands, then --sg-t resets after a .8s delay.
DX = f"calc(100% - 176px)"
HSIZE = "100% 1px,100% 1px,100% 1px,{tine} 2px," + f"{DW}px {DH}px,calc(var(--sg-hw)*{DW}px) {DH}px"
add("[data-chat-header]{--sg-hw:0;--sg-t:0;background-color:rgba(236,226,203,.96)!important;border-bottom:none!important;"
    "background-image:linear-gradient(rgba(112,92,52,.34),rgba(112,92,52,.34)),linear-gradient(rgba(112,92,52,.22),rgba(112,92,52,.22)),linear-gradient(rgba(112,92,52,.12),rgba(112,92,52,.12)),linear-gradient(rgba(74,94,62,.7),rgba(74,94,62,.7)),var(--sg-dock),var(--sg-dockm)!important;"
    "background-repeat:no-repeat;"
    f"background-size:{HSIZE.format(tine='calc(var(--sg-hw)*40px)')};"
    # the tine walks to the left edge of the header garden (276px from the rail's right edge) and stops there
    f"background-position:0 100%,0 calc(100% - 3px),0 calc(100% - 6px),calc(var(--sg-t)*(100% - 276px)) calc(100% - 3px),{DX} 50%,calc(100% - 276px + var(--sg-hw)*{DW}px) 50%}}")
add(busy("[data-chat-header]") + "{--sg-hw:1;--sg-t:1}")
add(NOREDUCE + "{[data-chat-header]{transition:--sg-hw .8s ease-out,--sg-t 0s linear .8s}" + busy("[data-chat-header]") + "{transition:--sg-hw .8s ease-out,--sg-t 24s steps(240,end)}}")
add(f"[data-chat-header]{{font-family:{SERIF};letter-spacing:.01em}}")
# ---------------------------------------------------------------- live rows: three wavy furrows. The look is static (so reduced motion keeps the state), only the flow is animated.
add('[data-timeline-row-kind="working"],[data-thread-item] [aria-busy="true"]{background-image:var(--sg-wave)!important;background-size:40px 8px;background-repeat:repeat-x;background-position:0 100%}')
add(NOREDUCE + '{[data-timeline-row-kind="working"]{animation:sg-flow 2s linear infinite}[data-thread-item] [aria-busy="true"]{animation:sg-flow 4s linear infinite}@keyframes sg-flow{to{background-position:40px 100%}}}')
add('[data-timeline-row-kind="working"]{padding-bottom:8px!important}')
add('[data-timeline-row-kind="work"]{font-variant-numeric:tabular-nums}')
# ---------------------------------------------------------------- sidebar
add(f"[data-slot=\"sidebar-inner\"]{{background:{SBF},{GRAIN},{SB}!important}}")
add("[data-thread-item]{position:relative}")
add("[data-thread-item]::after{content:\"\";position:absolute;left:12px;right:12px;bottom:0;height:8px;pointer-events:none;background-image:linear-gradient(#4a5e3e,#4a5e3e),linear-gradient(#4a5e3e,#4a5e3e),linear-gradient(#4a5e3e,#4a5e3e);background-repeat:no-repeat;"
    "background-position:0 7px,0 4px,0 1px;background-size:0 1px,0 1px,0 1px}")
add("[data-thread-item]:hover::after{background-size:100% 1px,82% 1px,64% 1px}")
add("[data-thread-item]:has([aria-busy=\"true\"])::after{background-size:0 1px,0 1px,0 1px!important}")
add("[data-thread-item] [aria-current]:not([aria-current=\"false\"]){box-shadow:inset 3px 0 0 #4a5e3e}")
add("[data-slot=\"project-monogram\"]{border-radius:42% 58% 50% 50%/55% 45% 55% 45%!important;border:1px solid rgba(112,92,52,.35)!important;font-family:" + SERIF + "}")
add(f"[data-thread-item]{{border-radius:10px;font-family:{SERIF}}}")
# ---------------------------------------------------------------- messages, composer, code
add("[data-user-message-bubble]{background:rgba(227,216,188,.98)!important;border:1px solid rgba(160,140,96,.42)!important;border-radius:24px 26px 24px 8px/22px 24px 22px 10px!important}")
add("[data-slot=\"composer-host\"]{background-color:rgba(247,241,226,.97)!important;border:1px solid rgba(160,140,96,.5)!important;border-radius:18px!important}")
add("[data-slot=\"composer-host\"]{background-image:linear-gradient(rgba(112,92,52,.28),rgba(112,92,52,.28)),linear-gradient(rgba(112,92,52,.18),rgba(112,92,52,.18)),linear-gradient(rgba(112,92,52,.1),rgba(112,92,52,.1));"
    "background-repeat:no-repeat;background-size:calc(100% - 44px) 1px,calc(100% - 64px) 1px,calc(100% - 84px) 1px;background-position:22px 6px,32px 9px,42px 12px}")
add(busy("[data-slot=\"composer-host\"]") + "{background-image:linear-gradient(rgba(74,94,62,.55),rgba(74,94,62,.55)),linear-gradient(rgba(74,94,62,.38),rgba(74,94,62,.38)),linear-gradient(rgba(74,94,62,.22),rgba(74,94,62,.22))}")
add("[data-slot=\"composer-host\"]:focus-within{border-color:rgba(74,94,62,.85)!important;box-shadow:0 0 0 3px rgba(74,94,62,.14),0 0 0 8px rgba(74,94,62,.07)}")
add("[data-slot=\"composer-host\"] :focus-visible,.composer-tiptap,.composer-tiptap:focus,.composer-tiptap:focus-visible{outline:none!important;box-shadow:none}")
add(".composer-tiptap{caret-color:#4a5e3e}")
add(".chat-markdown-codeblock{background:#e9e0c8!important;border:1px solid rgba(160,140,96,.4)!important;border-left:3px solid #4a5e3e!important;border-radius:8px!important;letter-spacing:.01em}")
add(".chat-markdown :not(pre)>code{color:#3a4c30;background:rgba(74,94,62,.11);padding:.05em .32em;border-radius:6px}")
add(f".chat-markdown :is(h1,h2,h3){{font-family:{SERIF};font-weight:600;letter-spacing:.005em}}")
add(f".chat-markdown :is(h1,h2){{padding-bottom:.5em;background:{TINES}}}")
add(".chat-markdown a{color:#3a6470!important;text-decoration-style:wavy;text-decoration-thickness:1px;text-underline-offset:4px}")
add(".chat-markdown blockquote{border-left:3px solid rgba(112,92,52,.4)!important;color:#5b5546;font-style:italic}")
add(".chat-markdown table{border-collapse:collapse}.chat-markdown :is(th,td){border:1px solid rgba(160,140,96,.4)!important;padding:.35em .7em}"
    f".chat-markdown th{{background:rgba(112,92,52,.09)!important;font-family:{SERIF};font-weight:600}}.chat-markdown tr:nth-child(even) td{{background:rgba(112,92,52,.035)}}")
add(furrow_rule(".chat-markdown hr"))
add(".chat-markdown>ul>li::marker{content:'\\25CF  ';font-size:.7em;color:#8a8478}.chat-markdown ol>li::marker{color:#4a5e3e}")
add("::selection{background:rgba(74,94,62,.26)}")
# ---------------------------------------------------------------- floating surfaces and controls
add("[data-slot=\"dialog-popup\"],[data-slot=\"popover-popup\"],[data-slot=\"menu-popup\"]{background:#fbf8ef!important;border-radius:14px!important;border:1px solid #cfc1a0!important;"
    "box-shadow:0 14px 36px rgba(70,56,30,.2),inset 0 0 0 1px rgba(255,252,240,.6)!important}")
add(f"[data-slot=\"dialog-popup\"] :is(h1,h2,h3){{font-family:{SERIF};padding-bottom:.55em;background:{TINES}}}")
add("[data-slot=\"menu-popup\"] [role=\"menuitem\"]:hover,[data-slot=\"menu-popup\"] [role=\"menuitem\"]:focus-visible,[data-slot=\"popover-popup\"] [role=\"option\"]:hover{background:#e3d8bc!important;border-radius:8px}")
add("[data-slot=\"tooltip-popup\"]{background:#2e2a22!important;color:#f7f2e3!important;border-radius:8px!important;border:0!important}")
add("[data-slot=\"button\"],[data-slot=\"input\"],[data-slot=\"select-trigger\"]{border-radius:10px!important}")
add("[data-slot=\"button\"]:hover{box-shadow:inset 0 0 0 999px rgba(74,94,62,.07)}[data-slot=\"button\"]:active{transform:translateY(1px);box-shadow:none}")
add("[data-slot=\"input\"]{background:#faf6ea!important;border-color:#b9aa86!important}[data-slot=\"input\"]:hover,[data-slot=\"select-trigger\"]:hover{border-color:#8f8460!important}")
add("[data-slot=\"select-trigger\"]{background:#f7f1e2!important}")
add("[data-slot=\"button\"]:focus-visible,[data-slot=\"select-trigger\"]:focus-visible{outline:2px solid #4a5e3e!important;outline-offset:2px}")
add("[data-slot=\"input\"]:focus-visible{outline:none!important;border-color:#4a5e3e!important;box-shadow:0 0 0 3px rgba(74,94,62,.2)}")
add("[data-slot=\"switch\"]{border-radius:999px!important}[data-slot=\"switch\"][aria-checked=\"false\"]{background-color:#cdbf9f!important}[data-slot=\"switch\"][aria-checked=\"true\"]{background-color:#4a5e3e!important}"
    "[data-slot=\"switch\"]:focus-visible{outline:2px solid #4a5e3e!important;outline-offset:2px}")
add("svg.lucide{stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}")
add("::-webkit-scrollbar{width:10px;height:10px}::-webkit-scrollbar-track{background:transparent}"
    "::-webkit-scrollbar-thumb,[data-slot=\"scroll-area-thumb\"]{background:rgba(112,92,52,.3)!important;border-radius:8px!important;border:2px solid transparent;background-clip:padding-box}"
    "::-webkit-scrollbar-thumb:hover,[data-slot=\"scroll-area-thumb\"]:hover{background:rgba(74,94,62,.55)!important;background-clip:padding-box}"
    "[data-slot=\"scroll-area-scrollbar\"]{background:transparent!important}")
# ---------------------------------------------------------------- panels
add("[data-thread-details-card]{background:#f7f1e2!important;border:1px solid #cfc1a0!important;border-radius:14px!important;box-shadow:0 6px 18px rgba(70,56,30,.1)}")
add(furrow_rule("[data-thread-details-card] :is(hr,[role=\"separator\"])"))
add(f"[data-thread-details-card] :is(h1,h2,h3,h4){{font-family:{SERIF}}}")
add("[data-thread-terminal-drawer]{background:#f3ecd8!important;border-top:1px solid #cfc1a0!important;box-shadow:inset 0 4px 0 -3px rgba(112,92,52,.3),inset 0 8px 0 -7px rgba(112,92,52,.18)}")
add(f"[data-settings-page-scroll]{{background:{SBF},{GRAIN},#f1e9d6!important}}[data-settings-page-scroll] :is(h1,h2,h3){{font-family:{SERIF}}}")
# ---------------------------------------------------------------- narrow: SWX hides the margin strips when the gutter is under 218px (window width or panels alike); the 72px mini strips (108..218px gutters) then carry the working and done state.
add(NOREDUCE + "{[data-thread-item]::after{transition:background-size .5s cubic-bezier(.2,.7,.2,1)}[data-slot=\"composer-host\"]{transition:border-color .25s,box-shadow .45s cubic-bezier(.2,.7,.2,1)}"
    "[data-slot=\"button\"],[data-slot=\"input\"],[data-slot=\"select-trigger\"]{transition:background-color .2s,border-color .2s,box-shadow .3s,transform .15s}}")
# reduced motion: no transitions or animations exist outside the query; the busy header is a deliberate still (garden grown, tine hidden)
add("@media (prefers-reduced-motion:reduce)" + "{" + busy("[data-chat-header]") + "{--sg-t:0;background-size:" + HSIZE.format(tine="0px") + "}}")

# ---------------------------------------------------------------- build-time guard (round 8): a registered <number> must never share its name with a :root url variable
import re
_root = re.search(r"^:root\{(.*?)\}", css_all := "".join(x for x in C if x), re.S).group(1)
_root_names = set(re.findall(r"(--sg-[\w-]+):", _root))
_props = set(re.findall(r"@property (--[\w-]+)", css_all))
assert not (_props & _root_names), f"@property name clashes with a :root variable: {_props & _root_names}"
_declared = _root_names | _props | set(re.findall(r"(--sg-[\w-]+):[^;{}]*[;}]", css_all.replace(_root, "")))
_used = set(re.findall(r"var\((--sg-[\w-]+)", css_all))
assert _used <= _declared, f"var() of an undeclared custom property: {_used - _declared}"
for _n in _props:   # a registered number must only ever be given numbers
    for _m in re.findall(re.escape(_n) + r":([^;{}]*)[;}]", css_all.replace(_root, "")):
        assert re.fullmatch(r"[\d.]+", _m.strip()) or "transition" in _m or _m.strip().startswith("var"), f"{_n} set to a non-number: {_m[:40]}"

css = "".join(x for x in C if x)

theme = {"id": "sandgarden", "version": 1, "name": "Sandgarden", "appearance": "light", "accent": "#4a5e3e",
         "canvas": "#f1e9d6", "colors": colors, "css": css}

with open(os.path.join(HERE, "..", "sandgarden.json"), "w") as fh:
    json.dump(theme, fh, ensure_ascii=False)
print("css chars:", len(css))
d = os.path.join(HERE, "..", "assets", "svg")
os.makedirs(d, exist_ok=True)
for fn in os.listdir(d):
    os.remove(os.path.join(d, fn))
for name, svg in (("mini-stone", mini_tile()), ("mini-stone-moss", mini_tile(True)), ("mini-line", mini_line()), ("mini-line-moss", mini_line(True)), ("moss-dock", dock_svg(True)), ("garden-left", strip_svg("l")), ("garden-right", strip_svg("r")), ("moss-left", moss_svg("l")), ("dock", dock_svg())):
    with open(os.path.join(d, name + ".svg"), "w") as fh:
        fh.write(svg)
