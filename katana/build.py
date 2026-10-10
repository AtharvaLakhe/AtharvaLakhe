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
LAYOUTS = {"banner.svg": (1200, 960), "banner-mobile.svg": (720, 1400)}
W, H = 1200, 960
MOBILE = False
KS = 1.0  # katana scale
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

def configure(name):
    """Set the canvas and the line of the cut for one layout."""
    global W, H, MOBILE, KS, C0, C1, _L, U, N, ANGLE
    W, H = LAYOUTS[name]
    MOBILE = name.endswith("mobile.svg")
    KS = 1.25 if MOBILE else 1.0
    C0, C1 = ((520.0, -20.0), (190.0, H + 20.0)) if MOBILE else ((820.0, -20.0), (380.0, H + 20.0))
    _L = math.hypot(C1[0] - C0[0], C1[1] - C0[1])
    U = ((C1[0] - C0[0]) / _L, (C1[1] - C0[1]) / _L)   # down the cut
    N = (-U[1], U[0]) if -U[1] > 0 else (U[1], -U[0])    # across it, pointing right
    ANGLE = math.degrees(math.atan2(U[1], U[0]))
    rnd.seed(11)


configure("banner.svg")


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
        return 46 * R / 225 * (min(1, t * 9) ** .5) * (1 - .62 * t)
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
    for _ in range(170):
        x, y = rnd.uniform(-50, W + 50), rnd.uniform(-50, H + 50)
        a, ln = rnd.uniform(0, math.pi), rnd.uniform(20, 90)
        dx, dy = math.cos(a) * ln, math.sin(a) * ln
        fib.append(f'<path d="M{f(x)},{f(y)}q{f(dx / 2 + rnd.uniform(-12, 12))},{f(dy / 2 + rnd.uniform(-12, 12))} {f(dx)},{f(dy)}" '
                   f'stroke="{rnd.choice(["#d2d1ca", "#dcdbd5", "#c8c7c0"])}" stroke-width="{f(rnd.uniform(.4, 1.1))}" opacity="{f(rnd.uniform(.4, .9))}" fill="none"/>')
    if MOBILE:
        ex, ey, er = 360, 470, 250
        cal = [(250, 1090, "一"), (480, 1090, "閃")]
        csize, kx, ky, kstep, ksize = 210, 676, 110, 40, 32
        seal, url = (582, 1150, 64), (40, 1366, 24)
    else:
        ex, ey, er = 520, 470, 300
        cal = [(1010, 340, "一"), (1010, 590, "閃")]
        csize, kx, ky, kstep, ksize = 220, 1146, 150, 38, 30
        seal, url = (1116, 640, 60), (60, 920, 17)
    splat = "".join(f'<circle cx="{f(rnd.gauss(ex - er * .25, er * .45))}" cy="{f(rnd.gauss(ey + er * .92, er * .2))}" r="{f(rnd.expovariate(.6) + .5)}" fill="#0c0c0c" opacity="{f(rnd.uniform(.6, 1))}"/>' for _ in range(34))
    kana = "".join(f'<text x="{kx}" y="{ky + i * kstep}" font-family="K" font-size="{ksize}" text-anchor="middle" fill="#1a1a1a">{c}</text>'
                   for i, c in enumerate("アタルヴァ・ラケ"))
    sx, sy, sz = seal
    return (f'<rect x="-400" y="-400" width="{W + 800}" height="{H + 800}" fill="#e9e8e3"/>'
            f'<rect x="-400" y="-400" width="{W + 800}" height="{H + 800}" filter="url(#wash)" opacity=".5"/>'
            + "".join(fib) + enso(ex, ey, er) + splat
            + "".join(f'<text x="{x}" y="{y}" font-family="K" font-size="{csize}" text-anchor="middle" fill="#0c0c0c">{c}</text>' for x, y, c in cal)
            + kana +
            f'<rect x="{sx}" y="{sy}" width="{sz}" height="{sz}" rx="5" fill="#0c0c0c"/>'
            f'<text x="{sx + sz / 2}" y="{sy + sz * .76}" font-family="K" font-size="{f(sz * .7)}" text-anchor="middle" fill="#e9e8e3">侍</text>'
            f'<text x="{url[0]}" y="{url[1]}" font-family="S" font-size="{url[2]}" letter-spacing="3" fill="#6d6c66">{esc("github.com/" + LOGIN)}</text>')


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
    o.append('<path d="M-440,-3.6Q-200,-5 -36,-5.2L-33,1.5Q-200,3 -440,3Z" fill="url(#ktone)" opacity=".55"/>')
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
    days = [d for w in weeks for d in w["contributionDays"]]
    months = {}
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["contributionCount"]
    top_month = max(months, key=months.get)
    bd, tm = dt.date.fromisoformat(best["date"]), dt.date.fromisoformat(top_month + "-01")
    ld = dt.date.fromisoformat(last)
    works = ["Security4Her", "PSR-Net", "SPARC", "CarbonLedger", "FancePro", "LancePro"]
    roles = ["Android and Wear OS", "Satellite imagery", "AI agents"]
    facts = [(str(longest), "longest streak, days"), (str(current), "current streak, days"),
             (str(best["contributionCount"]), f"best day, {bd.day} {bd:%b}"), (str(months[top_month]), f"busiest month, {tm:%b}")]
    o = [f'<rect width="{W}" height="{H}" fill="#050505"/>']
    T = lambda x, y, txt, fam, size, fill, anchor="start", extra="": o.append(
        f'<text x="{f(x)}" y="{f(y)}" font-family="{fam}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{extra}>{esc(txt)}</text>')

    if MOBILE:
        x0, x1 = 64, 680
        T(40, 122, "ATHARVA LAKHE", "N", 58, "#fff", extra=' letter-spacing="4"')
        T(40, 170, "Builds software that shows its work.", "S", 25, "#a3a3a3")
        for i, r in enumerate(roles):
            T(40, 228 + i * 38, r, "S", 25, "#d6d6d6")
        div = (680, 370, (680 - 40) / 616)
        T(40, 430, "Works", "S", 19, "#777")
        T(40, 468, " ".join(works[:3]), "S", 25, "#ececec", extra=' word-spacing="14"')
        T(40, 504, " ".join(works[3:]), "S", 25, "#ececec", extra=' word-spacing="14"')
        T(40, 552, "atharvalakhe09@gmail.com", "S", 24, "#a3a3a3")
        T(40, 660, f"{total:,}", "N", 76, "#fff")
        T(40, 700, "contributions in the last year", "S", 24, "#8a8a8a")
        for i, (value, label) in enumerate(facts):
            x, y = 40 + (i % 2) * 330, 790 + (i // 2) * 100
            o.append(f'<path d="M{x - 2},{y - 46}V{y + 34}" stroke="#2a2a2a"/>')
            T(x + 16, y, value, "N", 46, "#fff")
            T(x + 16, y + 30, label, "S", 21, "#8a8a8a")
        by, gh, fs, sy, sh, ml, foot = 1150, 170, 19, 1254, 56, 1288, 1372
    else:
        x0, x1 = 80, 1120
        T(x0, 138, "ATHARVA LAKHE", "N", 68, "#fff", extra=' letter-spacing="7"')
        T(x0, 192, "Builds software that shows its work.", "S", 25, "#a3a3a3")
        for i, r in enumerate(roles):
            T(x1, 92 + i * 30, r, "S", 21, "#d6d6d6", "end")
        div = (x1, 250, (x1 - x0) / 616)
        T(x0, 316, "Works", "S", 18, "#777")
        T(x0 + 76, 316, " ".join(works), "S", 21, "#ececec", extra=' word-spacing="22"')
        T(x1, 192, "atharvalakhe09@gmail.com", "S", 20, "#a3a3a3", "end")
        T(x0, 430, f"{total:,}", "N", 68, "#fff")
        T(x0, 462, "contributions in the last year", "S", 20, "#8a8a8a")
        for i, (value, label) in enumerate(facts):
            x = 470 + i * 170
            o.append(f'<path d="M{x - 18},386V462" stroke="#2a2a2a"/>')
            T(x, 426, value, "N", 38, "#fff")
            T(x, 454, label, "S", 15, "#8a8a8a")
        by, gh, fs, sy, sh, ml, foot = 778, 230, 14, 862, 46, 888, 936

    art = katana(line=True).replace("/>", ' vector-effect="non-scaling-stroke"/>')
    o.append(f'<g transform="translate({div[0]} {div[1]}) scale({div[2]:.4f} {.62 if not MOBILE else .7})">{art}</g>')

    # the year as an ink ridgeline, one point per week
    sums = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    mx = max(sums) or 1
    step = next(v for v in (5, 10, 20, 25, 50, 100, 200, 250, 500, 1000) if mx / v <= 4)
    top = step * math.ceil(mx / step)
    cw = (x1 - x0) / (len(weeks) - 1)
    for v in range(step, top + 1, step):
        y = by - v / top * gh
        o.append(f'<path d="M{x0},{f(y)}H{x1}" stroke="#1c1c1c" stroke-dasharray="2 5"/>')
        T(x0 - 10, y + fs * .35, str(v), "S", fs, "#666", "end")

    def ridge(vals):
        pts_ = [(x0 + i * cw, by - v / top * gh) for i, v in enumerate(vals)]
        d = f"M{f(pts_[0][0])},{f(pts_[0][1])}"
        for i in range(len(pts_) - 1):
            p0, p1, p2, p3 = pts_[max(i - 1, 0)], pts_[i], pts_[i + 1], pts_[min(i + 2, len(pts_) - 1)]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            d += f"C{f(c1[0])},{f(min(c1[1], by))} {f(c2[0])},{f(min(c2[1], by))} {f(p2[0])},{f(p2[1])}"
        return d
    far = [sum(sums[max(0, i - 3):i + 4]) / len(sums[max(0, i - 3):i + 4]) * 1.25 for i in range(len(sums))]
    o.append(f'<path class="back" d="{ridge(far)}L{x1},{by}L{x0},{by}Z" fill="#161616"/>')
    line = ridge(sums)
    o.append(f'<path class="wash" d="{line}L{x1},{by}L{x0},{by}Z" fill="url(#ink)"/>')
    o.append(f'<path class="ridge" pathLength="1" d="{line}" fill="none" stroke="#fff" stroke-width="{2.6 if MOBILE else 2.2}" stroke-linejoin="round"/>')
    o.append(f'<path d="M{x0},{by}H{x1}" stroke="#444"/>')
    T(x0, by - gh - 12, "Per week", "S", fs, "#666")
    peak = sums.index(mx)
    px, ph = x0 + peak * cw, by - mx / top * gh
    pd = dt.date.fromisoformat(weeks[peak]["contributionDays"][0]["date"])
    anchor, lx = ("end", px - 12) if px > x0 + (x1 - x0) * .7 else ("start", px + 12)
    o.append(f'<g class="peak"><circle cx="{f(px)}" cy="{f(ph)}" r="{6 if MOBILE else 4.5}" fill="#050505" stroke="#fff" stroke-width="2"/>'
             f'<path d="M{f(px)},{f(ph - 8)}V{f(ph - 34)}" stroke="#fff" stroke-width="1"/>'
             f'<text x="{f(lx)}" y="{f(ph - fs * 2.2)}" font-family="N" font-size="{fs + 8}" text-anchor="{anchor}" fill="#fff">{mx}</text>'
             f'<text x="{f(lx)}" y="{f(ph - fs * .9)}" font-family="S" font-size="{fs}" text-anchor="{anchor}" fill="#8a8a8a">week of {pd.day} {pd:%b}</text></g>')

    # every day of the year, one stroke each
    dmax = max(d["contributionCount"] for d in days) or 1
    dw = (x1 - x0) / len(days)
    for i, d in enumerate(days):
        x = x0 + i * dw + dw / 2
        c = d["contributionCount"]
        if c == 0:
            o.append(f'<circle cx="{f(x)}" cy="{sy - 1}" r=".9" fill="#3a3a3a"/>')
            continue
        h = max(2, (c / dmax) ** .6 * sh)
        o.append(f'<path class="tick" style="transform-origin:{f(x)}px {sy}px;animation-delay:{TS + 1.2 + i * .0035:.2f}s" d="M{f(x)},{sy}V{f(sy - h)}" '
                 f'stroke="{"#fff" if d is best else "#9a9a9a"}" stroke-width="{f(min(dw * .75, 2.2))}"/>')
    T(x0 - 10, sy - 2, "day", "S", fs - 2, "#666", "end")
    seen, lastcol = None, -9
    gap = 4 if MOBILE else 2
    for c, w in enumerate(weeks):
        m = dt.date.fromisoformat(w["contributionDays"][0]["date"]).month
        if m != seen and c - lastcol > gap and c < len(weeks) - 2:
            T(x0 + c * cw, ml, f"{dt.date(2000, m, 1):%b}", "S", fs, "#8a8a8a")
            lastcol = c
        seen = m
    T(x0 if not MOBILE else 40, foot, "Team OBSIDIAN", "S", fs, "#4d4d4d")
    T(x1, foot, f"Updated {ld.day} {ld:%B %Y}", "S", fs, "#4d4d4d", "end")
    return "".join(o)


# ---------------------------------------------------------------- assemble

def build(total, weeks):
    edge = tear_line()
    lpoly, lrim = piece(edge, -1)
    rpoly, rrim = piece(edge, +1)
    s0, s1 = -40, _L + 616 * KS + 80
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
    sa = 616 * KS + (_L - 616 * KS) * .3       # slow motion while the whole sword is on the page
    sb = 616 * KS + (_L - 616 * KS) * .62
    q = [0, (sa - s0) / (s1 - s0), (sb - s0) / (s1 - s0), 1]
    at = ["0%", "28%", "82%", "100%"]
    ease = ["cubic-bezier(.25,.6,.35,1)", "linear", "cubic-bezier(.6,0,1,.55)", ""]

    def stop(i, body):
        return f"{at[i]}{{{body}" + (f";animation-timing-function:{ease[i]}" if ease[i] else "") + "}"
    pos = [along(s0 + (s1 - s0) * v) for v in q]
    fall = "".join(stop(i, f"transform:translate({f(x)}px,{f(y)}px) rotate({ANGLE:.2f}deg) scale({KS})") for i, (x, y) in enumerate(pos))
    slit = "".join(stop(i, f"stroke-dashoffset:{1 - v:.3f}") for i, v in enumerate(q))
    p0, p1 = along(s0), along(s1)

    # the delayed cut: the right half slides down the line, holds, then tears away
    rd = TS + 1.4 - SLIDE
    pc = lambda t: f"{(t - SLIDE) / rd * 100:.1f}%"
    sx, sy = U[0] * 16, U[1] * 16
    lo, ro = (W * .25, H * .5), (W * .75, H * .5)
    drops = {-1: [], 1: []}
    for _ in range(90):
        side = rnd.choice([-1, 1])
        s_ = rnd.gauss(_L * .5, _L * .2)
        dist = rnd.expovariate(1 / 26) + 4
        sx_, sy_ = along(s_, side * dist + rnd.uniform(-2, 2))
        r = max(.6, rnd.expovariate(1 / 2.2) * (1.4 if dist < 20 else .9))
        stretch = 1 + min(dist / 18, 3) * rnd.uniform(.4, 1)
        ang = math.degrees(math.atan2(N[1] * side, N[0] * side)) + rnd.uniform(-25, 25)
        drops[side].append(f'<g class="drop" style="--dx:{f(-N[0] * side * dist)}px;--dy:{f(-N[1] * side * dist)}px;transform-origin:{f(sx_)}px {f(sy_)}px">'
                           f'<ellipse cx="{f(sx_)}" cy="{f(sy_)}" rx="{f(r * stretch)}" ry="{f(r)}" transform="rotate({ang:.0f} {f(sx_)} {f(sy_)})" fill="#0c0c0c"/></g>')
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
100%{{transform:translate(-{W * .4:.0f}px,{H * 1.9:.0f}px) rotate(-18deg) scale(1.04)}}}}
.rp{{transform-origin:{ro[0]}px {ro[1]}px;animation:rp {rd:.2f}s {SLIDE}s both}}
@keyframes rp{{0%{{transform:translate(0,0);animation-timing-function:cubic-bezier(.2,.7,.2,1)}}
{pc(SLIDE + .2)}{{transform:translate({f(sx)}px,{f(sy)}px)}}
{pc(TS)}{{transform:translate({f(sx)}px,{f(sy)}px);animation-timing-function:cubic-bezier(.2,.8,.3,1)}}
{pc(TS + .084)}{{transform:translate({f(sx + 3)}px,{f(sy)}px);animation-timing-function:cubic-bezier(.3,0,.3,1)}}
{pc(TS + .42)}{{transform:translate({f(sx + 56)}px,{f(sy + 8)}px) rotate(3deg) scale(1.02);animation-timing-function:cubic-bezier(.5,0,1,.6)}}
100%{{transform:translate({W * .42:.0f}px,{H * 1.9:.0f}px) rotate(14deg) scale(1.04)}}}}
.whole{{animation:hide .01s linear {SLIDE}s both}}
.rim{{animation:hide .1s linear {SLIDE}s reverse both}}
.ridge{{stroke-dasharray:1;animation:draw 1.6s cubic-bezier(.45,0,.25,1) {TS + .5}s both}}
@keyframes draw{{from{{stroke-dashoffset:1}}to{{stroke-dashoffset:0}}}}
.wash{{animation:hide 1.2s ease-out {TS + .9}s reverse both}}
.back{{animation:hide 1s ease-out {TS + .4}s reverse both}}
.tick{{animation:grow .35s cubic-bezier(.2,.8,.2,1) both}}
.drop{{animation:spray .22s cubic-bezier(.1,.8,.3,1) {IMP + .3}s both}}
@keyframes spray{{from{{transform:translate(var(--dx),var(--dy)) scale(.2);opacity:0}}}}
@keyframes grow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
.peak{{animation:hide .5s ease-out {TS + 1.8}s reverse both}}
{"".join(dcss)}
@media (prefers-reduced-motion:reduce){{.paper,.sword,.slit,.glint,.impact,.kira,.pl,[class^=db]{{display:none}}.ridge,.wash,.back,.tick,.drop,.peak{{animation:none}}}}"""

    gx = along(4)[0]
    defs = f"""<defs>
<linearGradient id="streak" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".4"/></linearGradient>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="ink" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d8d8d8" stop-opacity=".95"/><stop offset=".35" stop-color="#6a6a6a" stop-opacity=".9"/><stop offset="1" stop-color="#0d0d0d" stop-opacity=".9"/></linearGradient>
<pattern id="ktone" width="3.2" height="3.2" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><circle cx="1.6" cy="1.6" r=".55" fill="#000"/></pattern>
<linearGradient id="barfill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9e9e9"/><stop offset="1" stop-color="#5a5a5a"/></linearGradient>
<filter id="wash" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".012 .09" numOctaves="3" seed="3"/><feColorMatrix values="0 0 0 0 .55  0 0 0 0 .55  0 0 0 0 .52  0 0 0 -.9 .55"/></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="5" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .8 0"/></filter>
<clipPath id="bclip"><path d="M-440,-9Q-200,-11 -30,-8L0,-3Q-14,4 -32,6Q-200,11 -440,9Z"/></clipPath>
<clipPath id="lc"><path d="M{pts(lpoly)}Z"/></clipPath><clipPath id="rc"><path d="M{pts(rpoly)}Z"/></clipPath>
<g id="sheet">{paper()}</g>
</defs>"""

    specks = "".join(f'<circle cx="{f(mid[0] + math.cos(a) * r)}" cy="{f(mid[1] + math.sin(a) * r * .8)}" r="{f(rnd.uniform(1.2, 3.4))}" fill="#fff"/>'
                     for a, r in ((rnd.uniform(0, 6.3), rnd.uniform(120, max(W, H) * .4)) for _ in range(44)))
    body = f"""{underneath(total, weeks)}
<rect x="-40" y="-40" width="{W + 80}" height="{H + 80}" filter="url(#grain)" opacity=".05"/>
<g class="paper shake">
<use class="whole" href="#sheet"/>
<g class="lp"><g clip-path="url(#lc)"><use href="#sheet"/>{"".join(drops[-1])}</g><g class="rim">{lrim}</g></g>
<g class="rp"><g clip-path="url(#rc)"><use href="#sheet"/>{"".join(drops[1])}</g><g class="rim">{rrim}</g></g>
<path class="slit" pathLength="1" d="M{f(p0[0])},{f(p0[1])}L{f(p1[0])},{f(p1[1])}" stroke="#000" stroke-width="2.4"/>
<g class="pl">{path_lines(46, "#111")}</g>
</g>
{"".join(debris)}
<g class="glint" style="transform-origin:{f(gx)}px 8px"><path d="M{f(gx)},-18Q{f(gx+3)},5 {f(gx+26)},8Q{f(gx+3)},11 {f(gx)},34Q{f(gx-3)},11 {f(gx-26)},8Q{f(gx-3)},5 {f(gx)},-18Z" fill="#111"/></g>
<g class="sword"><rect class="trail" x="-1100" y="-6" width="480" height="12" fill="url(#streak)"/>{katana()}<g clip-path="url(#bclip)"><rect class="bglint" x="-560" y="-14" width="90" height="28" fill="url(#bg)"/></g></g>
<g class="impact"><rect x="-20" y="-20" width="{W + 40}" height="{H + 40}" fill="#000"/>{focus(mid[0], mid[1], W * .25, H * .2, 200, "#fff")}{slash(22, "#fff", 3)}{starburst(mid[0], mid[1], 16, 170, 26, "#fff")}{specks}</g>
<g class="kira"><rect x="-20" y="-20" width="{W + 40}" height="{H + 40}" fill="#fff"/>{slash(9, "#000", 1)}{starburst(mid[0], mid[1], 10, 120, 22, "none", "#000")}</g>"""

    alt = f"Atharva Lakhe. A katana falls through an ink-brushed page, cuts it, and the page tears away to show my details and {total:,} contributions in the last year."
    fonts = font("N", "mincho-xb.ttf") + font("S", "mincho-md.ttf") + font("K", "yuji.ttf")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(alt)}">'
            f"<style>{fonts}{css}</style>{defs}{body}</svg>")


if __name__ == "__main__":
    total, weeks = calendar()
    for name in LAYOUTS:
        configure(name)
        out = HERE / name
        out.write_text(build(total, weeks), encoding="utf-8")
        print(f"{name}: {W}x{H}, {out.stat().st_size // 1024} KB, {total:,} contributions")
