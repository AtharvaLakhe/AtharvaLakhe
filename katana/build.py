"""Draw katana/banner.svg: a falling katana cuts an ink-brushed page, the page tears away,
and my details and the last year of contributions are underneath.

    python katana/build.py            # needs GITHUB_TOKEN, or a logged-in gh CLI
"""
import base64
import datetime as dt
import json
import math
import os
import random
import subprocess
import urllib.request
from pathlib import Path

LOGIN = "AtharvaLakhe"
HERE = Path(__file__).resolve().parent
OUT = HERE / "banner.svg"
W, H = 1200, 700
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
C0, C1 = (780.0, -20.0), (420.0, 660.0)
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




# ---------------------------------------------------------------- timing (seconds)

FALL, FALL_DUR = 0.3, 2.3      # the katana drops, slows to a near stop mid-cut, then whips out
IMP = FALL + FALL_DUR          # impact frame
SLIDE = IMP + 0.6              # after a beat of silence, the cut half slides along the line
TS = SLIDE + 0.45              # then the page tears and falls


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


def paper():
    """The sheet: washi, an ensō, and calligraphy, in the manner of an ink-wash manga."""
    fib = []
    for _ in range(140):
        x, y = rnd.uniform(-50, W + 50), rnd.uniform(-50, H + 50)
        a, ln = rnd.uniform(0, math.pi), rnd.uniform(20, 90)
        dx, dy = math.cos(a) * ln, math.sin(a) * ln
        fib.append(f'<path d="M{f(x)},{f(y)}q{f(dx / 2 + rnd.uniform(-12, 12))},{f(dy / 2 + rnd.uniform(-12, 12))} {f(dx)},{f(dy)}" '
                   f'stroke="{rnd.choice(["#d2d1ca", "#dcdbd5", "#c8c7c0"])}" stroke-width="{f(rnd.uniform(.4, 1.1))}" opacity="{f(rnd.uniform(.4, .9))}" fill="none"/>')
    splat = "".join(f'<circle cx="{f(rnd.gauss(470, 120))}" cy="{f(rnd.gauss(560, 50))}" r="{f(rnd.expovariate(.7) + .4)}" fill="#0c0c0c" opacity="{f(rnd.uniform(.6, 1))}"/>' for _ in range(28))
    kana = "".join(f'<text x="1150" y="{120 + i * 30}" font-family="K" font-size="25" text-anchor="middle" fill="#1a1a1a">{c}</text>'
                   for i, c in enumerate("アタルヴァ・ラケ"))
    return (f'<rect x="-400" y="-400" width="{W + 800}" height="{H + 800}" fill="#e9e8e3"/>'
            f'<rect x="-400" y="-400" width="{W + 800}" height="{H + 800}" filter="url(#wash)" opacity=".5"/>'
            + "".join(fib) + enso(540, 350, 225) + splat +
            f'<text x="1030" y="250" font-family="K" font-size="170" text-anchor="middle" fill="#0c0c0c">一</text>'
            f'<text x="1030" y="440" font-family="K" font-size="170" text-anchor="middle" fill="#0c0c0c">閃</text>'
            + kana +
            f'<rect x="1124" y="378" width="52" height="52" rx="4" fill="#0c0c0c"/>'
            f'<text x="1150" y="417" font-family="K" font-size="36" text-anchor="middle" fill="#e9e8e3">侍</text>'
            f'<text x="60" y="660" font-family="S" font-size="15" letter-spacing="3" fill="#6d6c66">{esc("github.com/" + LOGIN)}</text>')


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

# ---------------------------------------------------------------- what's underneath

def underneath(total, weeks):
    longest, current, best, last = stats(weeks)
    o = [f'<rect width="{W}" height="{H}" fill="#050505"/>']
    x0 = 80
    o.append(f'<text x="{x0}" y="118" font-family="N" font-size="64" letter-spacing="8" fill="#fff">ATHARVA LAKHE</text>')
    o.append(f'<text x="{x0}" y="160" font-family="S" font-size="21" fill="#9b9b9b">Builds software that shows its work.</text>')
    for i, s in enumerate(["Android and Wear OS", "Satellite imagery", "AI agents"]):
        o.append(f'<text x="1120" y="{92 + i * 30}" font-family="S" font-size="18" text-anchor="end" fill="#d6d6d6">{s}</text>')
    art = katana(line=True).replace("/>", ' vector-effect="non-scaling-stroke"/>')
    o.append(f'<g transform="translate(1120 206) scale({1040 / 616:.4f} .62)">{art}</g>')

    works = ["Security4Her", "PSR-Net", "SPARC", "CarbonLedger", "FancePro", "LancePro"]
    o.append(f'<text x="{x0}" y="262" font-family="S" font-size="15" fill="#6f6f6f">Works</text>')
    o.append(f'<text x="{x0 + 70}" y="262" font-family="S" font-size="17" fill="#e6e6e6" word-spacing="18">{" ".join(works)}</text>')
    o.append(f'<text x="1120" y="262" font-family="S" font-size="16" text-anchor="end" fill="#9b9b9b">atharvalakhe09@gmail.com</text>')

    # contributions: the big number, three facts, then one blade per week
    o.append(f'<text x="{x0}" y="346" font-family="N" font-size="50" fill="#fff">{total:,}</text>')
    o.append(f'<text x="{x0 + 16 + len(f"{total:,}") * 29}" y="345" font-family="S" font-size="20" fill="#9b9b9b">contributions in the last year</text>')
    bd = dt.date.fromisoformat(best["date"])
    facts = [(str(longest), "Longest streak, days"), (str(current), "Current streak, days"),
             (str(best["contributionCount"]), f"Best day, {bd.day} {bd:%b}")]
    for i, (value, label) in enumerate(reversed(facts)):
        x = 1120 - i * 175
        o.append(f'<text x="{x}" y="336" font-family="N" font-size="32" text-anchor="end" fill="#fff">{value}</text>')
        o.append(f'<text x="{x}" y="360" font-family="S" font-size="15" text-anchor="end" fill="#8a8a8a">{esc(label)}</text>')

    sums = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    mx = max(sums) or 1
    step = next(s for s in (5, 10, 20, 25, 50, 100, 200, 250, 500, 1000) if mx / s <= 4)
    top = step * math.ceil(mx / step)
    by, gh, cw = 626, 206, 1040 / len(weeks)
    for v in range(step, top + 1, step):
        y = by - v / top * gh
        o.append(f'<path d="M{x0},{f(y)}H1120" stroke="#1d1d1d" stroke-width="1"/>')
        o.append(f'<text x="{x0 - 10}" y="{f(y + 4)}" font-family="S" font-size="14" text-anchor="end" fill="#7a7a7a">{v}</text>')
    o.append(f'<path d="M{x0},{by}H1120" stroke="#3a3a3a" stroke-width="1"/>')
    peak = sums.index(mx)
    for c, v in enumerate(sums):
        bw = cw * 0.58
        x = x0 + c * cw + (cw - bw) / 2
        delay = TS + 0.75 + c * 0.018
        if v == 0:
            o.append(f'<circle class="bar" style="transform-origin:{f(x + bw / 2)}px {by}px;animation-delay:{delay:.2f}s" cx="{f(x + bw / 2)}" cy="{by - 3}" r="1.6" fill="#555"/>')
            continue
        h = max(v / top * gh, 3)
        tip = min(bw * 1.1, h)
        o.append(f'<path class="bar" style="transform-origin:{f(x)}px {by}px;animation-delay:{delay:.2f}s" '
                 f'd="M{f(x)},{by}V{f(by - h + tip)}L{f(x + bw)},{f(by - h)}V{by}Z" fill="{"#fff" if c == peak else "url(#barfill)"}"/>')
    px = x0 + peak * cw + cw / 2
    pd = dt.date.fromisoformat(weeks[peak]["contributionDays"][0]["date"])
    anchor = "end" if px > 900 else "start" if px < 300 else "middle"
    ph = by - mx / top * gh
    o.append(f'<g class="peak"><text x="{f(px)}" y="{f(ph - 26)}" font-family="N" font-size="20" text-anchor="{anchor}" fill="#fff">{mx}</text>'
             f'<text x="{f(px)}" y="{f(ph - 10)}" font-family="S" font-size="13" text-anchor="{anchor}" fill="#8a8a8a">week of {pd.day} {pd:%b}</text></g>')
    seen, lastcol = None, -9
    for c, w in enumerate(weeks):
        m = dt.date.fromisoformat(w["contributionDays"][0]["date"]).month
        if m != seen and c - lastcol > 2 and c < len(weeks) - 1:
            o.append(f'<text x="{f(x0 + c * cw)}" y="652" font-family="S" font-size="14" fill="#8a8a8a">{dt.date(2000, m, 1):%b}</text>')
            lastcol = c
        seen = m
    ld = dt.date.fromisoformat(last)
    o.append(f'<text x="{x0}" y="686" font-family="S" font-size="13" fill="#4d4d4d">Team OBSIDIAN</text>')
    o.append(f'<text x="1120" y="686" font-family="S" font-size="13" text-anchor="end" fill="#4d4d4d">Updated {ld.day} {ld:%B %Y}</text>')
    return "".join(o)


# ---------------------------------------------------------------- assemble

def build(total, weeks):
    edge = tear_line()
    lpoly, lrim = piece(edge, -1)
    rpoly, rrim = piece(edge, +1)
    s0, s1 = -40, _L + 680
    mid = along(_L * .48)

    debris, dcss = [], []
    for i in range(18):
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
        debris.append(f'<path class="db{i}" d="M{pts(shape)}Z" fill="#ecebe6"/>')

    # the fall: enter, slow motion across the page, then gone
    q = [0, .45, .52, 1]
    at = ["0%", "28%", "82%", "100%"]
    ease = ["cubic-bezier(.25,.6,.35,1)", "linear", "cubic-bezier(.6,0,1,.55)", ""]

    def stop(i, body):
        return f"{at[i]}{{{body}" + (f";animation-timing-function:{ease[i]}" if ease[i] else "") + "}"
    pos = [along(s0 + (s1 - s0) * v) for v in q]
    fall = "".join(stop(i, f"transform:translate({f(x)}px,{f(y)}px) rotate({ANGLE:.2f}deg)") for i, (x, y) in enumerate(pos))
    slit = "".join(stop(i, f"stroke-dashoffset:{1 - v:.3f}") for i, v in enumerate(q))
    p0, p1 = along(s0), along(s1)

    # the delayed cut: the right half slides down the line, holds, then tears away
    rd = TS + 1.4 - SLIDE
    pc = lambda t: f"{(t - SLIDE) / rd * 100:.1f}%"
    sx, sy = U[0] * 16, U[1] * 16
    lo, ro = (300, 340), (900, 340)
    css = f"""
@keyframes hide{{from{{opacity:1}}to{{opacity:0}}}}
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
.glint{{animation:glint .5s ease-out .05s both}}
@keyframes glint{{0%{{transform:scale(0) rotate(0);opacity:0}}50%{{transform:scale(1) rotate(45deg);opacity:1}}100%{{transform:scale(0) rotate(90deg);opacity:0}}}}
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
100%{{transform:translate(-460px,1500px) rotate(-20deg) scale(1.04)}}}}
.rp{{transform-origin:{ro[0]}px {ro[1]}px;animation:rp {rd:.2f}s {SLIDE}s both}}
@keyframes rp{{0%{{transform:translate(0,0);animation-timing-function:cubic-bezier(.2,.7,.2,1)}}
{pc(SLIDE + .2)}{{transform:translate({f(sx)}px,{f(sy)}px)}}
{pc(TS)}{{transform:translate({f(sx)}px,{f(sy)}px);animation-timing-function:cubic-bezier(.2,.8,.3,1)}}
{pc(TS + .084)}{{transform:translate({f(sx + 3)}px,{f(sy)}px);animation-timing-function:cubic-bezier(.3,0,.3,1)}}
{pc(TS + .42)}{{transform:translate({f(sx + 56)}px,{f(sy + 8)}px) rotate(3deg) scale(1.02);animation-timing-function:cubic-bezier(.5,0,1,.6)}}
100%{{transform:translate(480px,1480px) rotate(16deg) scale(1.04)}}}}
.whole{{animation:hide .01s linear {SLIDE}s both}}
.rim{{animation:hide .1s linear {SLIDE}s reverse both}}
.bar{{animation:grow .55s cubic-bezier(.2,.8,.2,1) both}}
@keyframes grow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
.peak{{animation:hide .5s ease-out {TS + 1.8}s reverse both}}
.grain{{animation:grain .6s steps(1) infinite}}
@keyframes grain{{0%{{transform:translate(0,0)}}33%{{transform:translate(-30px,14px)}}66%{{transform:translate(20px,-24px)}}}}
{"".join(dcss)}
@media (prefers-reduced-motion:reduce){{.paper,.sword,.slit,.glint,.impact,.kira,.pl,[class^=db]{{display:none}}.bar,.peak{{animation:none}}}}"""

    gx = along(4)[0]
    defs = f"""<defs>
<linearGradient id="streak" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".4"/></linearGradient>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="barfill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9e9e9"/><stop offset="1" stop-color="#5a5a5a"/></linearGradient>
<filter id="wash" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".012 .09" numOctaves="3" seed="3"/><feColorMatrix values="0 0 0 0 .55  0 0 0 0 .55  0 0 0 0 .52  0 0 0 -.9 .55"/></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="5" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .8 0"/></filter>
<clipPath id="bclip"><path d="M-440,-9Q-200,-11 -30,-8L0,-3Q-14,4 -32,6Q-200,11 -440,9Z"/></clipPath>
<clipPath id="lc"><path d="M{pts(lpoly)}Z"/></clipPath><clipPath id="rc"><path d="M{pts(rpoly)}Z"/></clipPath>
<g id="sheet">{paper()}</g>
</defs>"""

    specks = "".join(f'<circle cx="{f(mid[0] + math.cos(a) * r)}" cy="{f(mid[1] + math.sin(a) * r * .8)}" r="{f(rnd.uniform(1.2, 3.4))}" fill="#fff"/>'
                     for a, r in ((rnd.uniform(0, 6.3), rnd.uniform(120, 420)) for _ in range(40)))
    body = f"""{underneath(total, weeks)}
<rect class="grain" x="-40" y="-40" width="{W + 80}" height="{H + 80}" filter="url(#grain)" opacity=".05"/>
<g class="paper shake">
<use class="whole" href="#sheet"/>
<g class="lp"><g clip-path="url(#lc)"><use href="#sheet"/></g><g class="rim">{lrim}</g></g>
<g class="rp"><g clip-path="url(#rc)"><use href="#sheet"/></g><g class="rim">{rrim}</g></g>
<path class="slit" pathLength="1" d="M{f(p0[0])},{f(p0[1])}L{f(p1[0])},{f(p1[1])}" stroke="#000" stroke-width="2.4"/>
<g class="pl">{path_lines(46, "#111")}</g>
</g>
{"".join(debris)}
<g class="glint" style="transform-origin:{f(gx)}px 8px"><path d="M{f(gx)},-18Q{f(gx+3)},5 {f(gx+26)},8Q{f(gx+3)},11 {f(gx)},34Q{f(gx-3)},11 {f(gx-26)},8Q{f(gx-3)},5 {f(gx)},-18Z" fill="#111"/></g>
<g class="sword"><rect class="trail" x="-1100" y="-6" width="480" height="12" fill="url(#streak)"/>{katana()}<g clip-path="url(#bclip)"><rect class="bglint" x="-560" y="-14" width="90" height="28" fill="url(#bg)"/></g></g>
<g class="impact"><rect x="-20" y="-20" width="{W + 40}" height="{H + 40}" fill="#000"/>{focus(mid[0], mid[1], 300, 190, 190, "#fff")}{slash(22, "#fff", 3)}{starburst(mid[0], mid[1], 16, 170, 26, "#fff")}{specks}</g>
<g class="kira"><rect x="-20" y="-20" width="{W + 40}" height="{H + 40}" fill="#fff"/>{slash(9, "#000", 1)}{starburst(mid[0], mid[1], 10, 120, 22, "none", "#000")}</g>"""

    alt = f"Atharva Lakhe. A katana falls through an ink-brushed page, cuts it, and the page tears away to show my details and {total:,} contributions in the last year."
    fonts = font("N", "mincho-xb.ttf") + font("S", "mincho-md.ttf") + font("K", "yuji.ttf")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(alt)}">'
            f"<style>{fonts}{css}</style>{defs}{body}</svg>")


if __name__ == "__main__":
    total, weeks = calendar()
    OUT.write_text(build(total, weeks), encoding="utf-8")
    print(f"{OUT.name}: {OUT.stat().st_size // 1024} KB, {total:,} contributions")
