"""Draw katana/banner.svg: a katana falls through a six-panel ink page, the page tears away,
and my details and the last year of contributions are underneath.

    python katana/build.py            # needs GITHUB_TOKEN, or a logged-in gh CLI
"""
import base64
import datetime as dt
import json
import math
import os
import random
import re
import subprocess
import urllib.request
from pathlib import Path

LOGIN = "AtharvaLakhe"
HERE = Path(__file__).resolve().parent
OUT = HERE / "banner.svg"
W, H = 1200, 900
rnd = random.Random(11)

# ---------------------------------------------------------------- data

def token():
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"]
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def calendar():
    q = ('{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions '
         'weeks{contributionDays{date weekday contributionCount contributionLevel}}}}}}' % LOGIN)
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": q}).encode(),
                                 {"Authorization": f"bearer {token()}", "Content-Type": "application/json"})
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], cal["weeks"]


def stats(weeks):
    days = [d for w in weeks for d in w["contributionDays"]]
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    current, tail = 0, days[::-1]
    if tail and tail[0]["contributionCount"] == 0:  # today isn't over yet
        tail = tail[1:]
    for d in tail:
        if not d["contributionCount"]:
            break
        current += 1
    best = max(days, key=lambda d: d["contributionCount"])
    return longest, current, best, days[-1]["date"]


# ---------------------------------------------------------------- helpers

def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def pts(p):
    return "L".join(f"{f(x)},{f(y)}" for x, y in p)


def font(family, file):
    data = base64.b64encode((HERE / "fonts" / file).read_bytes()).decode()
    return f"@font-face{{font-family:{family};src:url(data:font/ttf;base64,{data}) format('truetype')}}"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


# ---------------------------------------------------------------- the cut
C0, C1 = (830.0, -20.0), (370.0, 920.0)
_L = math.hypot(C1[0] - C0[0], C1[1] - C0[1])
U = ((C1[0] - C0[0]) / _L, (C1[1] - C0[1]) / _L)   # down the cut
N = (-U[1], U[0]) if -U[1] > 0 else (U[1], -U[0])    # across it, pointing right
ANGLE = math.degrees(math.atan2(U[1], U[0]))


def along(s, n=0.0):
    return C0[0] + U[0] * s + N[0] * n, C0[1] + U[1] * s + N[1] * n


def tear_line():
    """The torn edge: a knife cut that ripped, so mostly straight with a ragged bite."""
    out, s = [], -80.0
    ph = [rnd.uniform(0, 6.3) for _ in range(3)]
    while s < _L + 80:
        n = 2.6 * math.sin(s / 37 + ph[0]) + 1.6 * math.sin(s / 13 + ph[1]) + 0.9 * math.sin(s / 5.1 + ph[2]) + rnd.uniform(-1.1, 1.1)
        out.append((s, n))
        s += rnd.uniform(3, 6)
    return out


def piece(edge, side):
    """One half of the sheet. side=-1 is left of the cut, +1 right."""
    line = [along(s, n) for s, n in edge]
    far = -400 if side < 0 else W + 400
    poly = line + [(far, line[-1][1] + 300), (far, line[0][1] - 300)]
    # the torn rim: a pale band of exposed fibre, a hairline shadow inside it, and loose hairs
    inner = [along(s, n - side * (2.2 + 2.6 * abs(math.sin(s / 9.0)) + rnd.uniform(0, 1.6))) for s, n in edge]
    rim = f'<path d="M{pts(line + inner[::-1])}Z" fill="#fbfbf8"/>'
    rim += f'<path d="M{pts(inner)}" fill="none" stroke="#b9b8b1" stroke-width=".7"/>'
    hairs = []
    for s, n in edge[::2]:
        if rnd.random() < 0.55:
            ln = rnd.uniform(1.5, 7)
            x0, y0 = along(s, n)
            x1, y1 = along(s + rnd.uniform(-3, 3), n + side * ln)
            hairs.append(f"M{f(x0)},{f(y0)}Q{f((x0 + x1) / 2 + rnd.uniform(-2, 2))},{f((y0 + y1) / 2 + rnd.uniform(-2, 2))} {f(x1)},{f(y1)}")
    rim += f'<path d="{"".join(hairs)}" fill="none" stroke="#f2f1ec" stroke-width=".7" stroke-linecap="round"/>'
    return poly, rim




# ---------------------------------------------------------------- ink and impact

def focus(cx, cy, rx, ry, n, fill, wmin=.004, wmax=.014, reach=1600):
    """Focus lines: rays from far outside toward a clear centre."""
    d = []
    for i in range(n):
        a = i / n * 2 * math.pi + rnd.uniform(-.02, .02)
        k = rnd.uniform(1.0, 1.6)
        ix, iy = cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k
        w = rnd.uniform(wmin, wmax)
        d.append(f"M{f(ix)},{f(iy)}L{f(cx + math.cos(a + w) * reach)},{f(cy + math.sin(a + w) * reach)}"
                 f"L{f(cx + math.cos(a - w) * reach)},{f(cy + math.sin(a - w) * reach)}Z")
    return f'<path d="{"".join(d)}" fill="{fill}"/>'


def starburst(cx, cy, r0, r1, n, fill, stroke="none"):
    """The flash at the point of a cut: long thin spikes of uneven length."""
    p = []
    for i in range(n * 2):
        a = i / (n * 2) * 2 * math.pi
        r = r0 if i % 2 else r1 * rnd.uniform(.45, 1)
        p.append((cx + math.cos(a) * r, cy + math.sin(a) * r * .8))
    return f'<path d="M{pts(p)}Z" fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="miter"/>'


def slash(width, fill, rough=2.0):
    """A tapered stroke along the cut, thick in the middle."""
    top, bot = [], []
    for i in range(121):
        t = i / 120
        s = -40 + (_L + 80) * t
        w = width * (math.sin(math.pi * t) ** .6) + rnd.uniform(-rough, rough) * (0 < t < 1)
        top.append(along(s, w))
        bot.append(along(s, -w * .45))
    return f'<path d="M{pts(top + bot[::-1])}Z" fill="{fill}"/>'


def path_lines(n, fill):
    """Speed lines running parallel to the fall, either side of the blade's path."""
    d = []
    for _ in range(n):
        off = rnd.choice([-1, 1]) * rnd.uniform(26, 190)
        s = rnd.uniform(-60, _L)
        ln, w = rnd.uniform(60, 260), rnd.uniform(.5, 1.6)
        a, b = along(s, off), along(s + ln, off)
        d.append(f"M{f(a[0])},{f(a[1])}L{f(b[0] + N[0] * w)},{f(b[1] + N[1] * w)}L{f(b[0] - N[0] * w)},{f(b[1] - N[1] * w)}Z")
    return f'<path d="{"".join(d)}" fill="{fill}"/>'


def enso(cx, cy, R):
    """A dry-brush ensō: an ink-rich start that thins into broken bristle marks."""
    a0, sweep = math.radians(118), math.radians(318)

    def width(t):
        return 46 * (min(1, t * 9) ** .5) * (1 - .62 * t)
    core_o, core_i = [], []
    for i in range(140):
        t = i / 139 * .72
        a = a0 - sweep * t
        r = R + rnd.uniform(-1.2, 1.2)
        core_o.append((cx + math.cos(a) * (r + width(t) / 2), cy + math.sin(a) * (r + width(t) / 2)))
        core_i.append((cx + math.cos(a) * (r - width(t) / 2), cy + math.sin(a) * (r - width(t) / 2)))
    o = [f'<path d="M{pts(core_o + core_i[::-1])}Z" fill="#0c0c0c"/>']
    bristles = []
    for b in range(46):
        off = (b / 45 - .5)
        end = rnd.uniform(.82, 1.0) if abs(off) < .3 else rnd.uniform(.6, .95)
        seg, t = [], rnd.uniform(.0, .05)
        while t < end:
            a = a0 - sweep * t
            r = R + off * width(t) * rnd.uniform(.95, 1.05)
            if t > .55 and rnd.random() < .07 + (t - .55) * .5:  # the brush runs dry
                if len(seg) > 1:
                    bristles.append(seg)
                seg = []
            else:
                seg.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
            t += .006
        if len(seg) > 1:
            bristles.append(seg)
    o.append(f'<path d="{"".join("M" + pts(s) for s in bristles)}" fill="none" stroke="#0c0c0c" stroke-width="1.7" stroke-linecap="round"/>')
    return "".join(o)


def katana(scale=1.0, line=False):
    """A bare katana, tip at the origin, hilt toward negative x.

    Inked the way manga draw steel: white blade, a hard black reflection band on the flat,
    a crisp hamon, star glints, and a cord-wrapped hilt in hard black and white."""
    k = scale
    blade = f"M{-440*k},{-9*k}Q{-200*k},{-11*k} {-30*k},{-8*k}L0,{-3*k}Q{-14*k},{4*k} {-32*k},{6*k}Q{-200*k},{11*k} {-440*k},{9*k}Z"
    if line:  # the thin divider on the page underneath
        o = [f'<path d="{blade}" fill="none" stroke="#e8e8e8" stroke-width="1.1"/>',
             f'<path d="M{-440*k},{2*k}Q{-200*k},{2*k} {-30*k},{-1*k}" fill="none" stroke="#777" stroke-width=".8"/>',
             f'<rect x="{-454*k}" y="{-11*k}" width="{14*k}" height="{22*k}" rx="2" fill="none" stroke="#e8e8e8" stroke-width=".9"/>',
             f'<ellipse cx="{-461*k}" cy="0" rx="{7*k}" ry="{30*k}" fill="#000" stroke="#e8e8e8" stroke-width="1.2"/>',
             f'<path d="M{-468*k},{-13*k}L{-610*k},{-11*k}Q{-616*k},0 {-610*k},{11*k}L{-468*k},{13*k}Z" fill="#000" stroke="#e8e8e8" stroke-width="1.1"/>']
        for i in range(7):
            cx = (-484 - i * 18.5) * k
            o.append(f'<path d="M{f(cx-7.5*k)},0L{f(cx)},{f(-9*k)}L{f(cx+7.5*k)},0L{f(cx)},{f(9*k)}Z" fill="none" stroke="#bdbdbd" stroke-width=".8"/>')
        return "".join(o)

    o = [f'<path d="{blade}" fill="#fff"/>']
    # the flat between ridge and back: one hard black reflection band, broken where the light hits
    band = lambda x0, x1: (f"M{x0},-9.6Q{(x0 + x1) / 2},{-10.4} {x1},{-8.2}"
                           f"L{x1},{-4.4}Q{(x0 + x1) / 2},{-5.6} {x0},{-4.6}Z")
    o.append(f'<path d="{band(-436, -250)}{band(-214, -150)}{band(-128, -44)}" fill="#0a0a0a"/>')
    o.append(f'<path d="M-420,-7.2Q-330,-8 -262,-7.4M-200,-7.6L-160,-7.4" stroke="#fff" stroke-width=".9" fill="none"/>')
    # ridge line, yokote and the hamon with its frosted edge
    o.append('<path d="M-440,-3.6Q-200,-5 -36,-5.2M-36,-8.6L-31,5.6" fill="none" stroke="#000" stroke-width="1.1"/>')
    ham = [(x, 3.6 - 1.7 * math.sin(x / 9.5) - .9 * math.sin(x / 3.7)) for x in range(-436, -38, 3)]
    o.append(f'<path d="M{pts(ham)}" fill="none" stroke="#000" stroke-width=".9"/>')
    o.append('<path d="M-30,-1Q-16,-2 -6,-2.6" fill="none" stroke="#000" stroke-width=".8"/>')
    o.append('<path d="M-430,8.2Q-200,10 -36,5.4" fill="none" stroke="#fff" stroke-width="1.2" opacity=".9"/>')
    o.append(f'<path d="{blade}" fill="none" stroke="#000" stroke-width="1.8" stroke-linejoin="round"/>')
    # star glints on the steel
    for gx, gy, r in ((-318, -1, 13), (-96, -4, 9)):
        o.append(f'<path d="M{gx},{gy - r}Q{gx + 1},{gy - 1} {gx + r * 1.6},{gy}Q{gx + 1},{gy + 1} {gx},{gy + r}Q{gx - 1},{gy + 1} {gx - r * 1.6},{gy}Q{gx - 1},{gy - 1} {gx},{gy - r}Z" fill="#fff" stroke="#000" stroke-width=".7"/>')
    # habaki, hatched; seppa washers; a pierced guard seen nearly edge-on
    o.append('<rect x="-456" y="-11.5" width="16" height="23" fill="#fff" stroke="#000" stroke-width="1.5"/>')
    o.append('<path d="M-453,-11.5l6,23M-447,-11.5l6,23M-456,-4h16" stroke="#000" stroke-width=".9"/>')
    o.append('<rect x="-460" y="-14" width="4" height="28" fill="#fff" stroke="#000" stroke-width="1.1"/><rect x="-475" y="-14" width="4" height="28" fill="#fff" stroke="#000" stroke-width="1.1"/>')
    o.append('<ellipse cx="-465.5" cy="0" rx="7" ry="36" fill="#0a0a0a" stroke="#000" stroke-width="1.5"/>')
    o.append('<path d="M-462.5,-33Q-460,0 -462.5,33" fill="none" stroke="#fff" stroke-width="1.4"/>')
    o.append('<path d="M-468,-24q3,5 0,10q-3,-5 0,-10ZM-468,14q3,5 0,10q-3,-5 0,-10Z" fill="#fff"/>')
    # fuchi, then the hilt: white same-skin diamonds under a black braided wrap
    o.append('<rect x="-486" y="-13.5" width="11" height="27" fill="#0a0a0a" stroke="#000" stroke-width="1.2"/><path d="M-483,-12v24" stroke="#fff" stroke-width="1"/>')
    o.append('<path d="M-486,-13Q-550,-14.5 -612,-12L-612,12Q-550,14.5 -486,13Z" fill="#0a0a0a" stroke="#000" stroke-width="1.6"/>')
    for i in range(7):
        cx = -497 - i * 16.6
        o.append(f'<path d="M{f(cx - 6.6)},0L{f(cx)},-9.6L{f(cx + 6.6)},0L{f(cx)},9.6Z" fill="#f6f6f6" stroke="#000" stroke-width=".8"/>')
        o.append(f'<path d="M{f(cx - 9.4)},0L{f(cx)},-13L{f(cx + 9.4)},0L{f(cx)},13Z" fill="none" stroke="#fff" stroke-width=".8" opacity=".5"/>')
        o.append(f'<path d="M{f(cx + 8.3)},-12.6L{f(cx + 1.6)},-2.4M{f(cx - 8.3)},12.6L{f(cx - 1.6)},2.4" stroke="#fff" stroke-width="1.1" opacity=".7"/>')
    o.append('<path d="M-560,-5q6,-6 12,0q6,6 12,0" fill="none" stroke="#fff" stroke-width="2.2"/><path d="M-560,-5q6,-6 12,0q6,6 12,0" fill="none" stroke="#000" stroke-width=".8"/>')
    o.append('<path d="M-612,-12.5Q-624,-12 -625,0Q-624,12 -612,12.5Z" fill="#0a0a0a" stroke="#000" stroke-width="1.4"/>')
    o.append('<path d="M-616,-8Q-621,0 -616,8" fill="none" stroke="#fff" stroke-width="1.3"/><circle cx="-619" cy="0" r="1.8" fill="#fff"/>')
    return "".join(o)



# ---------------------------------------------------------------- timing (seconds)

RED = "#D7263D"
PANELS = [0.0, 0.3, 0.6, 0.9, 1.2, 1.5]   # the cover's panels arrive in reading order
FALL, FALL_DUR = 2.1, 2.3                 # the katana drops, slows to a near stop mid-cut, then whips out
IMP = FALL + FALL_DUR                     # impact frame
SLIDE = IMP + 0.6                         # after a beat of silence, the cut half slides along the line
TS = SLIDE + 0.45                         # then the page tears and falls


def poly(p):
    return f"M{pts(p)}Z"


# ---------------------------------------------------------------- the cover: six panels

P = [[(394, 22), (1178, 22), (1178, 284), (394, 300)],     # 1 red moon over a torii
     [(22, 22), (380, 22), (380, 580), (22, 580)],          # 2 thumb on the guard
     [(394, 314), (1178, 298), (1178, 440), (394, 440)],    # 3 the eyes
     [(394, 454), (770, 454), (756, 580), (394, 580)],      # 4 a leaf, cut in the air
     [(784, 454), (1178, 454), (1178, 580), (770, 580)],    # 5 the edge, the moon in it
     [(22, 594), (1178, 594), (1178, 878), (22, 878)]]      # 6 ensō and calligraphy


def centre(p):
    return sum(x for x, _ in p) / len(p), sum(y for _, y in p) / len(p)


def panel1():
    hill = [(380, 320), (380, 262)] + [(x, 262 - 34 * math.exp(-((x - 640) / 120) ** 2) + rnd.uniform(-1.5, 1.5)) for x in range(380, 1200, 12)] + [(1200, 320)]
    torii = ("M596,268L601,152H611L615,268Z M687,268L691,152H701L705,268Z"
             "M566,142Q646,134 726,142L736,130Q646,120 556,130Z M574,146H718V154H574Z"
             "M586,182H712V192H586Z M642,154H652V182H642Z")
    birds = "".join(f'<path d="M{x},{y}q6,-6 12,0q6,-6 12,0" fill="none" stroke="#000" stroke-width="1.6"/>' for x, y in ((880, 70), (912, 92), (850, 104)))
    grass = "".join(f'<path d="M{x},{f(262 - 34 * math.exp(-((x - 640) / 120) ** 2) + 2)}l{rnd.uniform(-4, 4):.1f},-{rnd.uniform(6, 14):.1f}" stroke="#000" stroke-width="1.4"/>' for x in range(400, 1190, 9))
    return (f'<rect x="380" y="0" width="820" height="320" fill="#fff"/>'
            f'<rect x="380" y="0" width="820" height="320" fill="url(#tone2)" mask="url(#fadedown)"/>'
            f'<g class="moon"><circle cx="1010" cy="150" r="80" fill="{RED}"/>'
            f'<circle cx="1010" cy="150" r="80" fill="url(#tone)" opacity=".18"/></g>'
            f'<path d="M820,128Q1000,118 1180,124L1180,128Q1000,124 830,131Z M900,176Q1040,170 1180,178L1180,181Q1040,175 910,179Z" fill="#000"/>'
            + birds + f'<path d="M{pts(hill)}Z" fill="#000"/>' + f'<path d="{torii}" fill="#000"/>' + grass)


def panel2():
    o = ['<rect x="0" y="0" width="400" height="600" fill="#fff"/>',
         '<rect x="0" y="0" width="400" height="600" fill="url(#tone)" mask="url(#fadeup)"/>',
         focus(200, 320, 66, 54, 120, "#000")]
    hilt = ['<path d="M172,-20H228V292H172Z" fill="#0b0b0b"/>']
    for i in range(9):
        cy = 4 + i * 34
        hilt.append(f'<path d="M180,{cy}L200,{cy - 14}L220,{cy}L200,{cy + 14}Z" fill="#f4f4f4" stroke="#000" stroke-width="1"/>')
        hilt.append(f'<path d="M178,{cy - 16}L222,{cy + 16}M222,{cy - 16}L178,{cy + 16}" stroke="#fff" stroke-width="1" opacity=".45"/>')
    hilt += ['<path d="M184,120q8,-10 16,0q8,10 16,0" fill="none" stroke="#fff" stroke-width="3"/>',
             '<rect x="169" y="290" width="62" height="13" fill="#d5d5d5" stroke="#000" stroke-width="2"/>',
             '<ellipse cx="200" cy="313" rx="94" ry="17" fill="#0b0b0b" stroke="#000" stroke-width="2"/>',
             '<path d="M121,309Q200,296 279,309" stroke="#fff" stroke-width="2" fill="none" opacity=".7"/>',
             '<path d="M150,312q8,-5 16,0q-8,5 -16,0ZM234,312q8,-5 16,0q-8,5 -16,0Z" fill="#fff"/>',
             '<rect x="179" y="324" width="42" height="26" fill="#e3e3e3" stroke="#000" stroke-width="2"/>',
             '<path d="M187,324l8,26M199,324l8,26" stroke="#8a8a8a" stroke-width="1.5"/>']
    o.append(f'<g class="hilt">{"".join(hilt)}</g>')
    o += ['<path d="M176,334H224V620H176Z" fill="#050505" stroke="#000" stroke-width="2"/>',
          '<path d="M187,352V600" stroke="#fff" stroke-width="2.5" opacity=".5"/>',
          '<rect x="173" y="332" width="54" height="14" fill="#cfcfcf" stroke="#000" stroke-width="2"/>',
          '<path d="M224,420q40,10 52,44q6,22 -10,40" fill="none" stroke="#e9e9e9" stroke-width="5" stroke-dasharray="6 3"/>',
          '<path d="M224,420q40,10 52,44q6,22 -10,40" fill="none" stroke="#000" stroke-width="1" stroke-dasharray="6 3"/>',
          '<g class="kspark" style="transform-origin:224px 330px"><path d="M224,306Q226,328 248,330Q226,332 224,354Q222,332 200,330Q222,328 224,306Z" fill="#fff" stroke="#000" stroke-width="1.2"/></g>']
    return "".join(o)


def eye(cx, cy, d):
    """A manga eye, narrowed: heavy upper lid, thin lower lid, crimson iris, hard highlights."""
    t = f'transform="translate({cx} {cy}) scale({d} 1)"'
    white = "M-62,6C-40,-14 20,-24 66,-4C30,18 -10,20 -50,12Z"
    return (f'<g {t}><path d="{white}" fill="#fff"/>'
            f'<clipPath id="ec{cx}"><path d="{white}"/></clipPath>'
            f'<g clip-path="url(#ec{cx})"><circle cx="6" cy="2" r="20" fill="{RED}" stroke="#000" stroke-width="2.2"/>'
            f'<circle cx="6" cy="2" r="20" fill="url(#tone)" opacity=".35"/>'
            f'<ellipse cx="6" cy="3" rx="5.5" ry="10" fill="#000"/>'
            f'<rect x="-70" y="-30" width="140" height="22" fill="#000" opacity=".55"/>'
            f'<circle cx="-3" cy="-6" r="4.6" fill="#fff"/><circle cx="14" cy="9" r="2" fill="#fff"/></g>'
            f'<path d="M-64,6C-42,-16 20,-28 70,-8L76,-14C24,-34 -44,-26 -66,0Z" fill="#000"/>'
            f'<path d="M-50,12C-10,21 30,19 60,6" fill="none" stroke="#000" stroke-width="1.8"/>'
            f'<path d="M60,-10l14,-4M64,-6l13,0M66,-1l10,4" stroke="#000" stroke-width="1.6"/>'
            f'<path d="M-66,-34L72,-56L72,-50L-62,-24Z" fill="#000"/>'
            f'<path d="M-30,30l10,-6M-16,32l10,-6M-2,33l10,-6M12,32l10,-6" stroke="#000" stroke-width="1.1"/></g>')


def panel3():
    return ('<rect x="380" y="290" width="820" height="160" fill="#fff"/>'
            '<rect x="380" y="290" width="820" height="62" fill="url(#tone)" opacity=".8"/>'
            + speed_h(394, 1178, 300, 440, 30, "#d9d9d9") +
            f'<g class="eyes" style="transform-origin:786px 372px">{eye(640, 376, -1)}{eye(930, 376, 1)}</g>'
            '<path d="M786,396q-6,18 2,26" fill="none" stroke="#000" stroke-width="1.4"/>')


def speed_h(x0, x1, y0, y1, n, fill):
    d = []
    for _ in range(n):
        y, x = rnd.uniform(y0, y1), rnd.uniform(x0 - 100, x1)
        ln, w = rnd.uniform(80, 300), rnd.uniform(.5, 1.4)
        d.append(f"M{f(x)},{f(y)}L{f(x + ln)},{f(y - w)}L{f(x + ln)},{f(y + w)}Z")
    return f'<path d="{"".join(d)}" fill="{fill}"/>'


def panel4():
    leaf = "M-60,0C-30,-22 30,-22 62,0C30,22 -30,22 -60,0Z"
    veins = "M-58,0L60,0" + "".join(f"M{x},0L{x + 14},{s * 12}" for x in range(-40, 50, 16) for s in (-1, 1))
    half = lambda cid, cls: (f'<g class="{cls}"><g clip-path="url(#{cid})" transform="rotate(-24)">'
                             f'<path d="{leaf}" fill="#fff" stroke="#000" stroke-width="2"/>'
                             f'<path d="{leaf}" fill="url(#tone)" opacity=".35"/>'
                             f'<path d="{veins}" stroke="#000" stroke-width="1"/></g></g>')
    return ('<rect x="380" y="440" width="400" height="160" fill="#fff"/>'
            '<rect x="380" y="440" width="400" height="160" fill="url(#tone)" mask="url(#fadeup4)"/>'
            '<path d="M470,452L470,500M520,450L520,488M650,456L650,494M700,452L700,482" stroke="#000" stroke-width="1"/>'
            '<clipPath id="lh"><path d="M-80,-60L30,-60L-30,60L-80,60Z"/></clipPath><clipPath id="rh"><path d="M30,-60L90,-60L90,60L-30,60Z"/></clipPath>'
            f'<g transform="translate(578 520)">{half("lh", "leafa")}{half("rh", "leafb")}</g>'
            '<path d="M520,590L640,446" stroke="#fff" stroke-width="3"/><path d="M520,590L640,446" stroke="#000" stroke-width=".8"/>')


def panel5():
    edge = [(x, 548 - 2.5 * math.sin(x / 11) - 1.4 * math.sin(x / 4.3)) for x in range(760, 1201, 4)]
    return ('<rect x="760" y="440" width="440" height="160" fill="#060606"/>'
            + speed_h(770, 1178, 456, 578, 26, "#2b2b2b") +
            '<path d="M760,488Q980,478 1200,470L1200,566Q980,572 760,578Z" fill="#fff" stroke="#000" stroke-width="2"/>'
            '<path d="M760,494Q980,484 1200,476L1200,500Q980,508 760,516Z" fill="#0a0a0a"/>'
            '<path d="M760,520Q980,512 1200,506" fill="none" stroke="#000" stroke-width="1.6"/>'
            f'<path d="M{pts(edge)}" fill="none" stroke="#000" stroke-width="1.2"/>'
            f'<ellipse cx="1040" cy="534" rx="34" ry="11" fill="{RED}"/><ellipse cx="1040" cy="534" rx="34" ry="11" fill="url(#tone)" opacity=".25"/>'
            '<path d="M900,526Q902,536 924,538Q902,540 900,550Q898,540 876,538Q898,536 900,526Z" fill="#fff" stroke="#000" stroke-width=".8"/>'
            '<g clip-path="url(#c5)"><rect class="sweep" x="700" y="440" width="70" height="160" fill="url(#bg)" transform="skewX(-20)"/></g>')


def enso_path(cx, cy, R):
    a0, sweep = math.radians(118), math.radians(318)
    return "M" + "L".join(f"{f(cx + math.cos(a0 - sweep * i / 80) * R)},{f(cy + math.sin(a0 - sweep * i / 80) * R)}" for i in range(81))


def panel6():
    splat = "".join(f'<circle cx="{f(rnd.gauss(440, 90))}" cy="{f(rnd.gauss(830, 26))}" r="{f(rnd.expovariate(.8) + .4)}" fill="#0c0c0c"/>' for _ in range(22))
    kana = "".join(f'<text x="1124" y="{640 + i * 28}" font-family="K" font-size="23" text-anchor="middle" fill="#1a1a1a">{c}</text>' for i, c in enumerate("アタルヴァ・ラケ"))
    return ('<rect x="0" y="580" width="1200" height="320" fill="#f3f2ee"/>'
            
            f'<mask id="ensomask" maskUnits="userSpaceOnUse" x="0" y="580" width="1200" height="320"><path class="paint" pathLength="1" d="{enso_path(520, 736, 112)}" stroke="#fff" stroke-width="70" fill="none"/></mask>'
            f'<g mask="url(#ensomask)">{enso(520, 736, 112)}</g>' + splat +
            '<text x="880" y="704" font-family="K" font-size="112" text-anchor="middle" fill="#0c0c0c">一</text>'
            '<text x="880" y="830" font-family="K" font-size="112" text-anchor="middle" fill="#0c0c0c">閃</text>'
            + kana +
            f'<rect x="996" y="796" width="50" height="50" rx="4" fill="{RED}"/>'
            '<text x="1021" y="833" font-family="K" font-size="34" text-anchor="middle" fill="#f3f2ee">侍</text>'
            f'<text x="56" y="856" font-family="S" font-size="15" letter-spacing="3" fill="#6d6c66">{esc("github.com/" + LOGIN)}</text>')


def page():
    """The whole cover. Every animation runs from a starting state to this resting one."""
    makers = [panel1, panel2, panel3, panel4, panel5, panel6]
    o = [f'<rect x="-400" y="-400" width="{W + 800}" height="{H + 800}" fill="#fbfaf7"/>',
         "".join(f'<clipPath id="c{i + 1}"><path d="{poly(p)}"/></clipPath>' for i, p in enumerate(P))]
    for i, (p, make) in enumerate(zip(P, makers)):
        cx, cy = centre(p)
        o.append(f'<g class="pin" style="transform-origin:{f(cx)}px {f(cy)}px;animation-delay:{PANELS[i]}s">'
                 f'<g clip-path="url(#c{i + 1})">{make()}</g>'
                 f'<path d="{poly(p)}" fill="none" stroke="#000" stroke-width="3.5"/></g>')
    return "".join(o)


# ---------------------------------------------------------------- underneath: the details, in panels

I = [[(22, 22), (790, 22), (770, 300), (22, 300)],
     [(804, 22), (1178, 22), (1178, 300), (784, 300)],
     [(22, 314), (1178, 314), (1178, 600), (22, 600)],
     [(22, 614), (690, 614), (670, 878), (22, 878)],
     [(704, 614), (1178, 614), (1178, 878), (684, 878)]]
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
SHADE = ["#171717", "#404040", "#7d7d7d", "#d2d2d2", RED]


def underneath(total, weeks):
    longest, current, best, last = stats(weeks)
    days = [d for w in weeks for d in w["contributionDays"]]
    active = sum(1 for d in days if d["contributionCount"])
    months = {}
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["contributionCount"]
    top_month = max(months, key=months.get)
    o = [f'<rect width="{W}" height="{H}" fill="#000"/>'] + [f'<path d="{poly(p)}" fill="#0b0b0b"/>' for p in I]

    # 1: name
    x0 = 56
    o.append(f'<clipPath id="i1"><path d="{poly(I[0])}"/></clipPath><g clip-path="url(#i1)">{speed_h(380, 800, 30, 290, 50, "#161616")}</g>')
    o.append(f'<text x="{x0}" y="100" font-family="N" font-size="56" letter-spacing="6" fill="#fff">ATHARVA LAKHE</text>')
    o.append(f'<text x="{x0}" y="142" font-family="S" font-size="20" fill="#a3a3a3">Builds software that shows its work.</text>')
    art = katana(line=True).replace("/>", ' vector-effect="non-scaling-stroke"/>')
    o.append(f'<g transform="translate(746 192) scale({(746 - x0) / 616:.4f} .55)">{art}</g>')
    o.append(f'<text x="{x0}" y="252" font-family="S" font-size="15" fill="#7a7a7a">Works</text>')
    o.append(f'<text x="{x0 + 62}" y="252" font-family="S" font-size="17" fill="#ececec" word-spacing="14">Security4Her PSR-Net SPARC CarbonLedger FancePro LancePro</text>')

    # 2: what I do
    for i, s in enumerate(["Android and Wear OS", "Satellite imagery", "AI agents"]):
        y = 46 + i * 46
        o.append(f'<rect x="846" y="{y}" width="306" height="34" fill="#fff"/><rect x="846" y="{y}" width="5" height="34" fill="{RED}"/>')
        o.append(f'<text x="1002" y="{y + 23}" font-family="S" font-size="17" text-anchor="middle" fill="#000">{s}</text>')
    o.append(f'<text x="1152" y="220" font-family="S" font-size="17" text-anchor="end" fill="#fff">atharvalakhe09@gmail.com</text>')
    o.append(f'<text x="1152" y="256" font-family="S" font-size="13" text-anchor="end" fill="#6a6a6a">Team OBSIDIAN</text>')
    ld = dt.date.fromisoformat(last)
    o.append(f'<text x="1152" y="278" font-family="S" font-size="13" text-anchor="end" fill="#6a6a6a">Updated {ld.day} {ld:%B %Y}</text>')
    o.append(f'<rect x="830" y="240" width="40" height="40" rx="3" fill="{RED}"/><text x="850" y="270" font-family="K" font-size="27" text-anchor="middle" fill="#0b0b0b">侍</text>')

    # 3: every day of the year
    o.append(f'<text x="{x0}" y="372" font-family="N" font-size="46" fill="#fff">{total:,}</text>')
    o.append(f'<text x="{x0 + 14 + len(f"{total:,}") * 27}" y="371" font-family="S" font-size="19" fill="#a3a3a3">contributions in the last year</text>')
    lx = 1152 - 5 * 18 - 34
    o.append(f'<text x="{lx - 8}" y="370" font-family="S" font-size="13" text-anchor="end" fill="#7a7a7a">Less</text>')
    for i in range(5):
        o.append(f'<rect x="{lx + i * 18}" y="358" width="14" height="14" rx="2" fill="{SHADE[i]}"/>')
    o.append(f'<text x="1152" y="370" font-family="S" font-size="13" text-anchor="end" fill="#7a7a7a">More</text>')
    gx, gy, cs = 100, 412, 20
    for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        o.append(f'<text x="{gx - 10}" y="{gy + r * cs + 13}" font-family="S" font-size="13" text-anchor="end" fill="#6a6a6a">{name}</text>')
    seen, lastcol = None, -9
    for c, w in enumerate(weeks):
        m = dt.date.fromisoformat(w["contributionDays"][0]["date"]).month
        if m != seen and c - lastcol > 2 and c < len(weeks) - 1:
            o.append(f'<text x="{gx + c * cs}" y="{gy - 10}" font-family="S" font-size="13" fill="#8a8a8a">{dt.date(2000, m, 1):%b}</text>')
            lastcol = c
        seen = m
        for d in w["contributionDays"]:
            x, y = gx + c * cs, gy + d["weekday"] * cs
            delay = TS + .55 + c * .011 + (6 - d["weekday"]) * .025
            o.append(f'<rect class="cell" style="transform-origin:{x + 8.5}px {y + 8.5}px;animation-delay:{delay:.2f}s" x="{x}" y="{y}" width="17" height="17" rx="2" fill="{SHADE[LEVEL[d["contributionLevel"]]]}"/>')
    o.append(f'<text x="{x0}" y="582" font-family="S" font-size="13" fill="#7a7a7a">Each square is a day. Crimson squares are my busiest days.</text>')

    # 4: month by month
    o.append(f'<text x="50" y="648" font-family="S" font-size="15" fill="#8a8a8a">By month</text>')
    keys = list(months)
    mx = max(months.values()) or 1
    bx0, bx1, by, bh = 56, 648, 842, 160
    slot = (bx1 - bx0) / len(keys)
    for i, k in enumerate(keys):
        v = months[k]
        h = max(v / mx * bh, 2)
        x, bw = bx0 + i * slot + slot * .18, slot * .64
        o.append(f'<rect class="bar" style="transform-origin:{f(x)}px {by}px;animation-delay:{TS + .9 + i * .04:.2f}s" x="{f(x)}" y="{f(by - h)}" width="{f(bw)}" height="{f(h)}" fill="{RED if k == top_month else "url(#barfill)"}"/>')
        o.append(f'<text class="num" style="animation-delay:{TS + 1.3 + i * .04:.2f}s" x="{f(x + bw / 2)}" y="{f(by - h - 7)}" font-family="S" font-size="13" text-anchor="middle" fill="{"#fff" if k == top_month else "#bdbdbd"}">{v}</text>')
        o.append(f'<text x="{f(x + bw / 2)}" y="{by + 20}" font-family="S" font-size="12" text-anchor="middle" fill="#7a7a7a">{dt.date(2000, int(k[5:]), 1):%b}</text>')
    o.append(f'<path d="M{bx0},{by}H{bx1}" stroke="#4a4a4a"/>')

    # 5: the numbers
    bd = dt.date.fromisoformat(best["date"])
    tm = dt.date.fromisoformat(top_month + "-01")
    facts = [(str(active), f"active days of {len(days)}"), (f"{total / len(days):.1f}", "contributions a day"),
             (str(longest), "longest streak, days"), (str(current), "current streak, days"),
             (str(best["contributionCount"]), f"best day, {bd.day} {bd:%b}"), (str(months[top_month]), f"busiest month, {tm:%b %Y}")]
    for i, (value, label) in enumerate(facts):
        x, y = 726 + (i % 2) * 222, 636 + (i // 2) * 78
        o.append(f'<g class="fact" style="animation-delay:{TS + 1 + i * .08:.2f}s"><rect x="{x}" y="{y}" width="210" height="66" fill="#fff"/>'
                 f'<rect x="{x}" y="{y}" width="5" height="66" fill="{RED}"/>'
                 f'<text x="{x + 18}" y="{y + 36}" font-family="N" font-size="28" fill="#000">{value}</text>'
                 f'<text x="{x + 18}" y="{y + 56}" font-family="S" font-size="13" fill="#444">{esc(label)}</text></g>')

    o += [f'<path d="{poly(p)}" fill="none" stroke="#fff" stroke-width="2.5"/>' for p in I]
    return "".join(o)


# ---------------------------------------------------------------- assemble

def build(total, weeks):
    edge = tear_line()
    lpoly, lrim = piece(edge, -1)
    rpoly, rrim = piece(edge, +1)
    s0, s1 = -40, _L + 700
    mid = along(_L * .45)

    debris, dcss = [], []
    for i in range(20):
        s = rnd.uniform(40, _L - 60)
        x, y = along(s)
        side = rnd.choice([-1, 1])
        dx, dy = N[0] * side * rnd.uniform(40, 160), H + 40 - y + rnd.uniform(0, 200)
        sz = rnd.uniform(3, 8)
        shape = [(rnd.uniform(-sz, sz), rnd.uniform(-sz, sz)) for _ in range(4)]
        dcss.append(f"@keyframes d{i}{{0%{{transform:translate({f(x)}px,{f(y)}px) rotate(0) scale(.3);opacity:0}}"
                    f"12%{{opacity:1;transform:translate({f(x + dx * .25)}px,{f(y - rnd.uniform(10, 40))}px) rotate({rnd.randint(-90, 90)}deg) scale(1)}}"
                    f"100%{{transform:translate({f(x + dx)}px,{f(y + dy)}px) rotate({rnd.randint(-540, 540)}deg) scale(1);opacity:1}}}}"
                    f".db{i}{{animation:d{i} {f(rnd.uniform(1.1, 1.6))}s cubic-bezier(.3,.1,.7,1) {f(TS + .1 + rnd.uniform(0, .25))}s both}}")
        debris.append(f'<path class="db{i}" d="M{pts(shape)}Z" fill="#f3f2ee" stroke="#000" stroke-width=".5"/>')

    q = [0, .40, .48, 1]
    at = ["0%", "28%", "82%", "100%"]
    ease = ["cubic-bezier(.25,.6,.35,1)", "linear", "cubic-bezier(.6,0,1,.55)", ""]

    def stop(i, body):
        return f"{at[i]}{{{body}" + (f";animation-timing-function:{ease[i]}" if ease[i] else "") + "}"
    pos = [along(s0 + (s1 - s0) * v) for v in q]
    fall = "".join(stop(i, f"transform:translate({f(x)}px,{f(y)}px) rotate({ANGLE:.2f}deg)") for i, (x, y) in enumerate(pos))
    slit = "".join(stop(i, f"stroke-dashoffset:{1 - v:.3f}") for i, v in enumerate(q))
    p0, p1 = along(s0), along(s1)

    rd = TS + 1.4 - SLIDE
    pc = lambda t: f"{(t - SLIDE) / rd * 100:.1f}%"
    sx, sy = U[0] * 16, U[1] * 16
    lo, ro = (300, 450), (900, 450)
    p = PANELS
    css = f"""
@keyframes hide{{from{{opacity:1}}to{{opacity:0}}}}
.pin{{animation:pin .45s cubic-bezier(.2,.8,.2,1) both}}
@keyframes pin{{from{{opacity:0;transform:scale(1.05)}}}}
.moon{{animation:moon 1.2s cubic-bezier(.2,.8,.2,1) {p[0] + .1}s both}}
@keyframes moon{{from{{transform:translateY(70px);opacity:.2}}}}
.hilt{{animation:koi .2s cubic-bezier(.2,.9,.3,1.3) {p[1] + .45}s both}}
@keyframes koi{{from{{transform:translateY(18px)}}}}
.kspark{{animation:spark .5s ease-out {p[1] + .55}s both}}
@keyframes spark{{0%{{transform:scale(0) rotate(0);opacity:0}}40%{{transform:scale(1.3) rotate(30deg);opacity:1}}}}
.eyes{{animation:eyes .25s cubic-bezier(.2,.9,.3,1.2) {p[2] + .45}s both}}
@keyframes eyes{{from{{transform:scaleY(.06)}}}}
.leafa{{animation:leafa .7s cubic-bezier(.2,.7,.3,1) {p[3] + .3}s both}}
.leafb{{animation:leafb .7s cubic-bezier(.2,.7,.3,1) {p[3] + .3}s both}}
@keyframes leafa{{from{{transform:translate(4px,-40px)}}to{{transform:translate(-9px,-7px) rotate(-7deg)}}}}
@keyframes leafb{{from{{transform:translate(4px,-40px)}}to{{transform:translate(10px,9px) rotate(6deg)}}}}
.sweep{{animation:sweep 1s ease-in-out {p[4] + .4}s both}}
@keyframes sweep{{from{{transform:skewX(-20deg) translateX(0)}}to{{transform:skewX(-20deg) translateX(700px)}}}}
.paint{{stroke-dasharray:1;animation:paint .9s cubic-bezier(.5,0,.3,1) {p[5] + .2}s both}}
@keyframes paint{{from{{stroke-dashoffset:1}}to{{stroke-dashoffset:0}}}}
.sword{{animation:fall {FALL_DUR}s {FALL}s both}}
@keyframes fall{{{fall}}}
.trail{{animation:trail {FALL_DUR}s {FALL}s both}}
@keyframes trail{{0%{{opacity:0}}18%{{opacity:.5}}30%{{opacity:.1}}36%,82%{{opacity:0}}92%{{opacity:.9}}100%{{opacity:0}}}}
.pl{{animation:pl {FALL_DUR}s {FALL}s both}}
@keyframes pl{{0%{{opacity:0}}10%{{opacity:.75}}28%{{opacity:.15}}34%,82%{{opacity:0}}92%{{opacity:.9}}100%{{opacity:0}}}}
.slit{{stroke-dasharray:1;animation:slit {FALL_DUR}s {FALL}s both,hide .05s linear {SLIDE}s forwards}}
@keyframes slit{{{slit}}}
.bglint{{animation:bglint 1.1s cubic-bezier(.4,0,.6,1) {FALL + .75}s both}}
@keyframes bglint{{from{{transform:translateX(0)}}to{{transform:translateX(560px)}}}}
.impact{{opacity:0;animation:imp .3s steps(1) {IMP}s forwards}}
@keyframes imp{{0%{{opacity:1}}27%{{opacity:0}}47%{{opacity:1}}73%,100%{{opacity:0}}}}
.kira{{opacity:0;animation:kira .3s steps(1) {IMP}s forwards}}
@keyframes kira{{0%{{opacity:0}}27%{{opacity:1}}47%,100%{{opacity:0}}}}
.shake{{animation:shake .45s steps(1) {IMP}s both}}
@keyframes shake{{0%{{transform:translate(-8px,5px)}}18%{{transform:translate(7px,-6px)}}36%{{transform:translate(-5px,-2px)}}54%{{transform:translate(3px,3px)}}72%{{transform:translate(-1px,1px)}}90%,100%{{transform:translate(0,0)}}}}
.lp{{transform-origin:{lo[0]}px {lo[1]}px;animation:lp 1.35s {TS}s both}}
@keyframes lp{{0%{{transform:translate(0,0);animation-timing-function:cubic-bezier(.2,.8,.3,1)}}
6%{{transform:translate(-3px,0);animation-timing-function:cubic-bezier(.3,0,.3,1)}}
30%{{transform:translate(-48px,14px) rotate(-3.5deg) scale(1.02);animation-timing-function:cubic-bezier(.5,0,1,.6)}}
100%{{transform:translate(-520px,1700px) rotate(-18deg) scale(1.04)}}}}
.rp{{transform-origin:{ro[0]}px {ro[1]}px;animation:rp {rd:.2f}s {SLIDE}s both}}
@keyframes rp{{0%{{transform:translate(0,0);animation-timing-function:cubic-bezier(.2,.7,.2,1)}}
{pc(SLIDE + .2)}{{transform:translate({f(sx)}px,{f(sy)}px)}}
{pc(TS)}{{transform:translate({f(sx)}px,{f(sy)}px);animation-timing-function:cubic-bezier(.2,.8,.3,1)}}
{pc(TS + .084)}{{transform:translate({f(sx + 3)}px,{f(sy)}px);animation-timing-function:cubic-bezier(.3,0,.3,1)}}
{pc(TS + .42)}{{transform:translate({f(sx + 56)}px,{f(sy + 8)}px) rotate(3deg) scale(1.02);animation-timing-function:cubic-bezier(.5,0,1,.6)}}
100%{{transform:translate(540px,1680px) rotate(14deg) scale(1.04)}}}}
.whole{{animation:hide .01s linear {SLIDE}s both}}
.halves{{animation:hide .01s linear {SLIDE}s reverse both}}
.cell{{animation:cell .35s cubic-bezier(.2,.9,.3,1.4) both}}
@keyframes cell{{from{{transform:scale(0)}}}}
.bar{{animation:grow .55s cubic-bezier(.2,.8,.2,1) both}}
@keyframes grow{{from{{transform:scaleY(0)}}}}
.num,.fact{{animation:hide .4s ease-out reverse both}}
{"".join(dcss)}
@media (prefers-reduced-motion:reduce){{.paper,.sword,.slit,.impact,.kira,.pl,[class^=db]{{display:none}}.cell,.bar,.num,.fact{{animation:none}}}}"""

    live = page()
    still = re.sub(r' class="[^"]*"', "", live).replace(' mask="url(#ensomask)"', "").replace('id="', 'id="s')
    still = still.replace('url(#c', 'url(#sc').replace('url(#ec', 'url(#sec').replace('url(#lh)', 'url(#slh)').replace('url(#rh)', 'url(#srh)')
    defs = f"""<defs>
<linearGradient id="streak" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".4"/></linearGradient>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="barfill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ececec"/><stop offset="1" stop-color="#6a6a6a"/></linearGradient>
<pattern id="tone" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><circle cx="3" cy="3" r="1.35" fill="#000"/></pattern>
<pattern id="tone2" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><circle cx="2.5" cy="2.5" r="1.45" fill="#000"/></pattern>
<linearGradient id="gup" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#fff"/><stop offset=".75" stop-color="#000"/></linearGradient>
<linearGradient id="gdown" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset=".8" stop-color="#000"/></linearGradient>
<mask id="fadeup" maskContentUnits="userSpaceOnUse"><rect x="0" y="0" width="400" height="600" fill="url(#gup)"/></mask>
<mask id="fadeup4" maskContentUnits="userSpaceOnUse"><rect x="380" y="440" width="400" height="160" fill="url(#gup)"/></mask>
<mask id="fadedown" maskContentUnits="userSpaceOnUse"><rect x="380" y="0" width="820" height="320" fill="url(#gdown)"/></mask>
<filter id="wash" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".012 .09" numOctaves="3" seed="3"/><feColorMatrix values="0 0 0 0 .55  0 0 0 0 .55  0 0 0 0 .52  0 0 0 -.9 .55"/></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="5" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .8 0"/></filter>
<clipPath id="bclip"><path d="M-440,-9Q-200,-11 -30,-8L0,-3Q-14,4 -32,6Q-200,11 -440,9Z"/></clipPath>
<clipPath id="lc"><path d="M{pts(lpoly)}Z"/></clipPath><clipPath id="rc"><path d="M{pts(rpoly)}Z"/></clipPath>
<g id="still">{still}</g>
</defs>"""

    specks = "".join(f'<circle cx="{f(mid[0] + math.cos(a) * r)}" cy="{f(mid[1] + math.sin(a) * r * .8)}" r="{f(rnd.uniform(1.2, 3.4))}" fill="#fff"/>'
                     for a, r in ((rnd.uniform(0, 6.3), rnd.uniform(120, 460)) for _ in range(44)))
    body = f"""{underneath(total, weeks)}
<rect x="-40" y="-40" width="{W + 80}" height="{H + 80}" filter="url(#grain)" opacity=".05"/>
<g class="paper shake">
<g class="whole">{live}</g>
<g class="halves"><g class="lp"><g clip-path="url(#lc)"><use href="#still"/></g>{lrim}</g>
<g class="rp"><g clip-path="url(#rc)"><use href="#still"/></g>{rrim}</g></g>
<path class="slit" pathLength="1" d="M{f(p0[0])},{f(p0[1])}L{f(p1[0])},{f(p1[1])}" stroke="#000" stroke-width="2.4"/>
<g class="pl">{path_lines(50, "#111")}</g>
</g>
{"".join(debris)}
<g class="sword"><rect class="trail" x="-1100" y="-6" width="480" height="12" fill="url(#streak)"/>{katana()}<g clip-path="url(#bclip)"><rect class="bglint" x="-560" y="-14" width="90" height="28" fill="url(#bg)"/></g></g>
<g class="impact"><rect x="-20" y="-20" width="{W + 40}" height="{H + 40}" fill="#000"/>{focus(mid[0], mid[1], 300, 200, 200, "#fff")}{slash(24, "#fff", 3)}{starburst(mid[0], mid[1], 18, 190, 28, "#fff")}<circle cx="{f(mid[0])}" cy="{f(mid[1])}" r="9" fill="{RED}"/>{specks}</g>
<g class="kira"><rect x="-20" y="-20" width="{W + 40}" height="{H + 40}" fill="#fff"/>{slash(9, "#000", 1)}{starburst(mid[0], mid[1], 10, 130, 22, "none", "#000")}<path d="{slash_red()}" fill="{RED}"/></g>"""

    alt = f"Atharva Lakhe. A katana falls through a six-panel ink page, cuts it, and the page tears away to show my details and {total:,} contributions in the last year."
    fonts = font("N", "mincho-xb.ttf") + font("S", "mincho-md.ttf") + font("K", "yuji.ttf")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(alt)}">'
            f"<style>{fonts}{css}</style>{defs}{body}</svg>")


def slash_red():
    """A thin crimson core inside the white flash, like light catching the edge."""
    a, b = along(-40, 1), along(_L + 40, 1)
    c, d = along(_L + 40, -1), along(-40, -1)
    return f"M{pts([a, b, c, d])}Z"


if __name__ == "__main__":
    total, weeks = calendar()
    OUT.write_text(build(total, weeks), encoding="utf-8")
    print(f"{OUT.name}: {OUT.stat().st_size // 1024} KB, {total:,} contributions")
