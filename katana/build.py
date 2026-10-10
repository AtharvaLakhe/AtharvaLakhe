"""Draw katana/banner.svg: a falling katana cuts a sheet of paper, the paper tears away,
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
TS = 2.75  # when the paper starts to tear
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


def paper():
    """The sheet the katana falls through: washi with an ink character on it."""
    fib = []
    for _ in range(140):
        x, y = rnd.uniform(-50, W + 50), rnd.uniform(-50, H + 50)
        a, ln = rnd.uniform(0, math.pi), rnd.uniform(20, 90)
        dx, dy = math.cos(a) * ln, math.sin(a) * ln
        fib.append(f'<path d="M{f(x)},{f(y)}q{f(dx / 2 + rnd.uniform(-12, 12))},{f(dy / 2 + rnd.uniform(-12, 12))} {f(dx)},{f(dy)}" '
                   f'stroke="{rnd.choice(["#d2d1ca", "#dcdbd5", "#c8c7c0"])}" stroke-width="{f(rnd.uniform(.4, 1.1))}" opacity="{f(rnd.uniform(.4, .9))}" fill="none"/>')
    splat = "".join(f'<circle cx="{f(rnd.gauss(560, 170))}" cy="{f(rnd.gauss(330, 120))}" r="{f(rnd.expovariate(.8) + .4)}" fill="#0d0d0d" opacity="{f(rnd.uniform(.5, 1))}"/>' for _ in range(36))
    kana = "".join(f'<text x="1112" y="{88 + i * 36}" font-family="K" font-size="30" text-anchor="middle" fill="#151515">{c}</text>'
                   for i, c in enumerate("アタルヴァ・ラケ"))
    return (f'<rect x="-400" y="-400" width="{W + 800}" height="{H + 800}" fill="#e7e6e1"/>'
            f'<rect x="-400" y="-400" width="{W + 800}" height="{H + 800}" filter="url(#wash)" opacity=".55"/>'
            + "".join(fib) +
            f'<text x="560" y="555" font-family="K" font-size="450" text-anchor="middle" fill="#0b0b0b">斬</text>'
            + splat + kana +
            f'<rect x="1084" y="400" width="56" height="56" rx="6" fill="#0b0b0b"/>'
            f'<text x="1112" y="442" font-family="K" font-size="38" text-anchor="middle" fill="#e7e6e1">侍</text>'
            f'<text x="60" y="660" font-family="S" font-size="15" letter-spacing="3" fill="#6d6c66">{esc("github.com/" + LOGIN)}</text>')


def katana(scale=1.0, line=False):
    """A bare katana, tip at the origin, hilt toward negative x."""
    k = scale
    blade = f"M{-440*k},{-9*k}Q{-200*k},{-11*k} {-30*k},{-8*k}L0,{-3*k}Q{-14*k},{4*k} {-32*k},{6*k}Q{-200*k},{11*k} {-440*k},{9*k}Z"
    if line:
        stroke = 'fill="none" stroke="#e8e8e8" stroke-width="1.1"'
        o = [f'<path d="{blade}" {stroke}/>',
             f'<path d="M{-440*k},{2*k}Q{-200*k},{2*k} {-30*k},{-1*k}" fill="none" stroke="#777" stroke-width=".8"/>']
    else:
        o = [f'<path d="{blade}" fill="url(#steel)" stroke="#0d0d0d" stroke-width="1"/>']
        ham = [(x, 9 * k * (1 - (x / (-440 * k)) ** 0 * 0) - 4.5 * k - 1.8 * k * math.sin(x / (11 * k)) - 1 * k * math.sin(x / (4 * k)))
               for x in [-438 * k + i * 4 for i in range(int(400 * k / 4))]]
        o.append(f'<path d="M{pts(ham)}" fill="none" stroke="#fff" stroke-width="1.6" opacity=".9"/>')
        o.append(f'<path d="M{-440*k},{-2*k}Q{-200*k},{-3*k} {-30*k},{-3*k}" fill="none" stroke="#6f6f6f" stroke-width=".8"/>')
    o.append(f'<rect x="{-454*k}" y="{-11*k}" width="{14*k}" height="{22*k}" rx="2" fill="{"none" if line else "#dcdcdc"}" stroke="{"#e8e8e8" if line else "#0d0d0d"}" stroke-width=".9"/>')
    o.append(f'<ellipse cx="{-461*k}" cy="0" rx="{7*k}" ry="{30*k}" fill="{"#000" if line else "#0b0b0b"}" stroke="#e8e8e8" stroke-width="{1.2 if line else 1.6}"/>')
    o.append(f'<path d="M{-468*k},{-13*k}L{-610*k},{-11*k}Q{-616*k},0 {-610*k},{11*k}L{-468*k},{13*k}Z" fill="{"#000" if line else "#0b0b0b"}" stroke="#e8e8e8" stroke-width="{1.1 if line else 1.4}"/>')
    for i in range(7):
        cx = (-484 - i * 18.5) * k
        o.append(f'<path d="M{f(cx-7.5*k)},0L{f(cx)},{f(-9*k)}L{f(cx+7.5*k)},0L{f(cx)},{f(9*k)}Z" fill="{"none" if line else "#efefef"}" stroke="{"#bdbdbd" if line else "none"}" stroke-width=".8"/>')
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
    p0, p1 = along(s0), along(s1)

    debris, dcss = [], []
    for i in range(16):
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

    lo, ro = (300, 340), (900, 340)
    q = [0, .45, .52, 1]  # how far down the cut the tip is at each stop: enter, slow motion, out
    at = ["0%", "28%", "82%", "100%"]
    ease = ["cubic-bezier(.25,.6,.35,1)", "linear", "cubic-bezier(.6,0,1,.55)", ""]

    def stop(i, body):
        return f"{at[i]}{{{body}" + (f";animation-timing-function:{ease[i]}" if ease[i] else "") + "}"
    pos = [along(s0 + (s1 - s0) * v) for v in q]
    fall = "".join(stop(i, f"transform:translate({f(x)}px,{f(y)}px) rotate({ANGLE:.2f}deg)") for i, (x, y) in enumerate(pos))
    slit = "".join(stop(i, f"stroke-dashoffset:{1 - v:.3f}") for i, v in enumerate(q))
    css = f"""
.sword{{animation:fall 2.3s .3s both}}
@keyframes fall{{{fall}}}
.trail{{animation:trail 2.3s .3s both}}
@keyframes trail{{0%{{opacity:0}}18%{{opacity:.5}}30%{{opacity:.1}}36%,82%{{opacity:0}}100%{{opacity:.9}}}}
.slit{{stroke-dasharray:1;animation:slit 2.3s .3s both,hide .1s linear {TS + .02}s both}}
@keyframes slit{{{slit}}}
@keyframes hide{{from{{opacity:1}}to{{opacity:0}}}}
.bglint{{animation:bglint 1.1s cubic-bezier(.4,0,.6,1) 1s both}}
@keyframes bglint{{from{{transform:translateX(0)}}to{{transform:translateX(560px)}}}}
.glint{{animation:glint .5s ease-out .05s both}}
@keyframes glint{{0%{{transform:scale(0) rotate(0);opacity:0}}50%{{transform:scale(1) rotate(45deg);opacity:1}}100%{{transform:scale(0) rotate(90deg);opacity:0}}}}
.lp{{transform-origin:{lo[0]}px {lo[1]}px;animation:lp 1.35s {TS}s both}}
.rp{{transform-origin:{ro[0]}px {ro[1]}px;animation:rp 1.4s {TS}s both}}
@keyframes lp{{0%{{transform:translate(0,0);animation-timing-function:cubic-bezier(.2,.8,.3,1)}}
6%{{transform:translate(-3px,0);animation-timing-function:cubic-bezier(.3,0,.3,1)}}
30%{{transform:translate(-48px,14px) rotate(-3.5deg) scale(1.02);animation-timing-function:cubic-bezier(.5,0,1,.6)}}
100%{{transform:translate(-460px,1500px) rotate(-20deg) scale(1.04)}}}}
@keyframes rp{{0%{{transform:translate(0,0);animation-timing-function:cubic-bezier(.2,.8,.3,1)}}
6%{{transform:translate(3px,0);animation-timing-function:cubic-bezier(.3,0,.3,1)}}
30%{{transform:translate(56px,8px) rotate(3deg) scale(1.02);animation-timing-function:cubic-bezier(.5,0,1,.6)}}
100%{{transform:translate(480px,1480px) rotate(16deg) scale(1.04)}}}}
.whole{{animation:hide .01s linear {TS}s both}}
.rim{{animation:hide .12s linear {TS + .02}s reverse both}}
.shake{{animation:shake .35s steps(1) {TS}s both}}
@keyframes shake{{0%{{transform:translate(-4px,2px)}}25%{{transform:translate(3px,-3px)}}50%{{transform:translate(-2px,-1px)}}75%,100%{{transform:translate(0,0)}}}}
.bar{{animation:grow .55s cubic-bezier(.2,.8,.2,1) both}}
@keyframes grow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
.peak{{animation:hide .5s ease-out {TS + 1.8}s reverse both}}
.grain{{animation:grain .6s steps(1) infinite}}
@keyframes grain{{0%{{transform:translate(0,0)}}33%{{transform:translate(-30px,14px)}}66%{{transform:translate(20px,-24px)}}}}
{"".join(dcss)}
@media (prefers-reduced-motion:reduce){{.paper,.sword,.trail,.slit,.glint,[class^=db]{{display:none}}.bar,.peak{{animation:none}}}}"""

    gx = along(4)[0]
    defs = f"""<defs>
<linearGradient id="steel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f4f4"/><stop offset=".45" stop-color="#a2a2a2"/><stop offset=".62" stop-color="#cdcdcd"/><stop offset="1" stop-color="#fff"/></linearGradient>
<linearGradient id="streak" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#111" stop-opacity="0"/><stop offset="1" stop-color="#111" stop-opacity=".35"/></linearGradient>
<filter id="wash" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".012 .09" numOctaves="3" seed="3"/><feColorMatrix values="0 0 0 0 .55  0 0 0 0 .55  0 0 0 0 .52  0 0 0 -.9 .55"/></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="5" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .8 0"/></filter>
<clipPath id="bclip"><path d="M-440,-9Q-200,-11 -30,-8L0,-3Q-14,4 -32,6Q-200,11 -440,9Z"/></clipPath>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="barfill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9e9e9"/><stop offset="1" stop-color="#5a5a5a"/></linearGradient>
<clipPath id="lc"><path d="M{pts(lpoly)}Z"/></clipPath><clipPath id="rc"><path d="M{pts(rpoly)}Z"/></clipPath>
<g id="sheet">{paper()}</g>
</defs>"""

    body = f"""{underneath(total, weeks)}
<rect class="grain" x="-40" y="-40" width="{W + 80}" height="{H + 80}" filter="url(#grain)" opacity=".05"/>
<g class="paper shake">
<use class="whole" href="#sheet"/>
<g class="lp"><g clip-path="url(#lc)"><use href="#sheet"/></g><g class="rim">{lrim}</g></g>
<g class="rp"><g clip-path="url(#rc)"><use href="#sheet"/></g><g class="rim">{rrim}</g></g>
<path class="slit" pathLength="1" d="M{f(p0[0])},{f(p0[1])}L{f(p1[0])},{f(p1[1])}" stroke="#0a0a0a" stroke-width="2.2"/>
</g>
{"".join(debris)}
<g class="glint" style="transform-origin:{f(gx)}px 8px"><path d="M{f(gx)},-18Q{f(gx+3)},5 {f(gx+26)},8Q{f(gx+3)},11 {f(gx)},34Q{f(gx-3)},11 {f(gx-26)},8Q{f(gx-3)},5 {f(gx)},-18Z" fill="#111"/></g>
<g class="sword"><rect class="trail" x="-1100" y="-6" width="480" height="12" fill="url(#streak)"/>{katana()}<g clip-path="url(#bclip)"><rect class="bglint" x="-560" y="-14" width="90" height="28" fill="url(#bg)"/></g></g>"""

    alt = f"Atharva Lakhe. A katana falls and cuts a sheet of paper, which tears away to show {total:,} contributions in the last year."
    fonts = font("N", "mincho-xb.ttf") + font("S", "mincho-md.ttf") + font("K", "yuji.ttf")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(alt)}">'
            f"<style>{fonts}{css}</style>{defs}{body}</svg>")


if __name__ == "__main__":
    total, weeks = calendar()
    OUT.write_text(build(total, weeks), encoding="utf-8")
    print(f"{OUT.name}: {OUT.stat().st_size // 1024} KB, {total:,} contributions")
