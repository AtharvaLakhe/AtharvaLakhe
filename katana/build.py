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
W, H = 1200, 640
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
            f'<text x="560" y="520" font-family="K" font-size="430" text-anchor="middle" fill="#0b0b0b">斬</text>'
            + splat + kana +
            f'<rect x="1084" y="400" width="56" height="56" rx="6" fill="#0b0b0b"/>'
            f'<text x="1112" y="442" font-family="K" font-size="38" text-anchor="middle" fill="#e7e6e1">侍</text>'
            f'<text x="60" y="600" font-family="S" font-size="15" letter-spacing="3" fill="#6d6c66">{esc("github.com/" + LOGIN)}</text>')


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

    # contributions: one cut per day, deeper for busier days
    gy, cw, ch = 392, 1040 / len(weeks), 19
    o.append(f'<text x="{x0}" y="338" font-family="N" font-size="40" fill="#fff">{total:,}</text>')
    o.append(f'<text x="{x0 + 18 + len(f"{total:,}") * 24}" y="338" font-family="S" font-size="18" fill="#9b9b9b">contributions in the last year</text>')
    bd = dt.date.fromisoformat(best["date"])
    facts = [("Longest streak", f"{longest} days"), ("Current streak", f"{current} days"), ("Best day", f"{best['contributionCount']} on {bd.day} {bd:%b}")]
    x = 1120
    for label, value in reversed(facts):
        o.append(f'<text x="{x}" y="336" font-family="S" font-size="18" text-anchor="end" fill="#e6e6e6">{esc(value)}</text>')
        x -= len(value) * 9.2 + 10
        o.append(f'<text x="{f(x)}" y="336" font-family="S" font-size="15" text-anchor="end" fill="#7a7a7a">{label}</text>')
        x -= len(label) * 7.8 + 30
    seen, lastcol = None, -9
    for c, w in enumerate(weeks):
        m = dt.date.fromisoformat(w["contributionDays"][0]["date"]).month
        if m != seen and c - lastcol > 2:
            if seen is not None or c == 0:
                o.append(f'<text x="{f(x0 + c * cw)}" y="{gy - 16}" font-family="S" font-size="13" fill="#6f6f6f">{dt.date(2000, m, 1):%b}</text>')
                lastcol = c
        seen = m
    lv = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
    cuts, dots = [], []
    for c, w in enumerate(weeks):
        for d in w["contributionDays"]:
            cx, cy = x0 + c * cw + cw / 2, gy + d["weekday"] * ch + ch / 2
            level = lv[d["contributionLevel"]]
            delay = 2.15 + c * 0.014 + d["weekday"] * 0.01
            if level == 0:
                dots.append(f'<circle class="dot" style="animation-delay:{delay:.2f}s" cx="{f(cx)}" cy="{f(cy)}" r="1.3" fill="#3b3b3b"/>')
            else:
                r = 2.2 + level * 1.55
                tone = ["", "#6d6d6d", "#a3a3a3", "#d4d4d4", "#ffffff"][level]
                cuts.append(f'<path class="cut" style="animation-delay:{delay:.2f}s" pathLength="1" d="M{f(cx - r)},{f(cy + r)}L{f(cx + r)},{f(cy - r)}" '
                            f'stroke="{tone}" stroke-width="{f(1 + level * .45)}" stroke-linecap="round"/>')
    o += dots + cuts
    ly = gy + 7 * ch + 26
    o.append(f'<text x="{x0}" y="{ly}" font-family="S" font-size="13" fill="#6f6f6f">One cut per day. Deeper cuts, busier days.</text>')
    lx = 1120 - 5 * 22 - 34
    o.append(f'<text x="{lx - 8}" y="{ly}" font-family="S" font-size="13" text-anchor="end" fill="#6f6f6f">Less</text>')
    for level in range(5):
        cx, cy = lx + 11 + level * 22, ly - 5
        if level == 0:
            o.append(f'<circle cx="{cx}" cy="{cy}" r="1.3" fill="#3b3b3b"/>')
        else:
            r = 2.2 + level * 1.55
            o.append(f'<path d="M{f(cx - r)},{f(cy + r)}L{f(cx + r)},{f(cy - r)}" stroke="{["", "#6d6d6d", "#a3a3a3", "#d4d4d4", "#fff"][level]}" stroke-width="{f(1 + level * .45)}" stroke-linecap="round"/>')
    o.append(f'<text x="1120" y="{ly}" font-family="S" font-size="13" text-anchor="end" fill="#6f6f6f">More</text>')
    ld = dt.date.fromisoformat(last)
    o.append(f'<text x="{x0}" y="612" font-family="S" font-size="13" fill="#4d4d4d">Team OBSIDIAN</text>')
    o.append(f'<text x="1120" y="612" font-family="S" font-size="13" text-anchor="end" fill="#4d4d4d">Updated {ld.day} {ld:%B %Y}</text>')
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
                    f".db{i}{{animation:d{i} {f(rnd.uniform(1.1, 1.6))}s cubic-bezier(.3,.1,.7,1) {f(1.4 + rnd.uniform(0, .25))}s both}}")
        debris.append(f'<path class="db{i}" d="M{pts(shape)}Z" fill="#ecebe6"/>')

    lo, ro = (300, 320), (900, 320)
    css = f"""
.sword{{animation:fall 1s cubic-bezier(.55,0,.95,.55) .3s both}}
@keyframes fall{{from{{transform:translate({f(p0[0])}px,{f(p0[1])}px) rotate({ANGLE:.2f}deg)}}to{{transform:translate({f(p1[0])}px,{f(p1[1])}px) rotate({ANGLE:.2f}deg)}}}}
.trail{{animation:trail 1s cubic-bezier(.55,0,.95,.55) .3s both}}
@keyframes trail{{0%{{opacity:0}}40%{{opacity:.25}}100%{{opacity:.9}}}}
.slit{{stroke-dasharray:1;animation:slit 1s cubic-bezier(.55,0,.95,.55) .3s both,hide .1s linear 1.32s both}}
@keyframes hide{{from{{opacity:1}}to{{opacity:0}}}}
@keyframes slit{{from{{stroke-dashoffset:1}}to{{stroke-dashoffset:0}}}}
.glint{{animation:glint .5s ease-out .05s both}}
@keyframes glint{{0%{{transform:scale(0) rotate(0);opacity:0}}50%{{transform:scale(1) rotate(45deg);opacity:1}}100%{{transform:scale(0) rotate(90deg);opacity:0}}}}
.lp{{transform-origin:{lo[0]}px {lo[1]}px;animation:lp 1.35s 1.3s both}}
.rp{{transform-origin:{ro[0]}px {ro[1]}px;animation:rp 1.4s 1.3s both}}
@keyframes lp{{0%{{transform:translate(0,0);animation-timing-function:cubic-bezier(.2,.8,.3,1)}}
6%{{transform:translate(-3px,0);animation-timing-function:cubic-bezier(.3,0,.3,1)}}
30%{{transform:translate(-48px,14px) rotate(-3.5deg) scale(1.02);animation-timing-function:cubic-bezier(.5,0,1,.6)}}
100%{{transform:translate(-460px,1500px) rotate(-20deg) scale(1.04)}}}}
@keyframes rp{{0%{{transform:translate(0,0);animation-timing-function:cubic-bezier(.2,.8,.3,1)}}
6%{{transform:translate(3px,0);animation-timing-function:cubic-bezier(.3,0,.3,1)}}
30%{{transform:translate(56px,8px) rotate(3deg) scale(1.02);animation-timing-function:cubic-bezier(.5,0,1,.6)}}
100%{{transform:translate(480px,1480px) rotate(16deg) scale(1.04)}}}}
.whole{{animation:hide .01s linear 1.3s both}}
.rim{{animation:hide .12s linear 1.32s reverse both}}
.shake{{animation:shake .35s steps(1) 1.3s both}}
@keyframes shake{{0%{{transform:translate(-4px,2px)}}25%{{transform:translate(3px,-3px)}}50%{{transform:translate(-2px,-1px)}}75%,100%{{transform:translate(0,0)}}}}
.cut{{stroke-dasharray:1;animation:cut .28s cubic-bezier(.6,0,.2,1) both}}
@keyframes cut{{from{{stroke-dashoffset:1}}to{{stroke-dashoffset:0}}}}
.dot{{animation:dot .4s ease-out both}}
@keyframes dot{{from{{opacity:0}}to{{opacity:1}}}}
.grain{{animation:grain .6s steps(1) infinite}}
@keyframes grain{{0%{{transform:translate(0,0)}}33%{{transform:translate(-30px,14px)}}66%{{transform:translate(20px,-24px)}}}}
{"".join(dcss)}
@media (prefers-reduced-motion:reduce){{.paper,.sword,.trail,.slit,.glint,[class^=db]{{display:none}}.cut,.dot{{animation:none}}}}"""

    gx = along(4)[0]
    defs = f"""<defs>
<linearGradient id="steel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f4f4"/><stop offset=".45" stop-color="#a2a2a2"/><stop offset=".62" stop-color="#cdcdcd"/><stop offset="1" stop-color="#fff"/></linearGradient>
<linearGradient id="streak" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#111" stop-opacity="0"/><stop offset="1" stop-color="#111" stop-opacity=".35"/></linearGradient>
<filter id="wash" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".012 .09" numOctaves="3" seed="3"/><feColorMatrix values="0 0 0 0 .55  0 0 0 0 .55  0 0 0 0 .52  0 0 0 -.9 .55"/></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="5" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .8 0"/></filter>
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
<g class="sword"><rect class="trail" x="-1100" y="-6" width="480" height="12" fill="url(#streak)"/>{katana()}</g>"""

    alt = f"Atharva Lakhe. A katana falls and cuts a sheet of paper, which tears away to show {total:,} contributions in the last year."
    fonts = font("N", "mincho-xb.ttf") + font("S", "mincho-md.ttf") + font("K", "yuji.ttf")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(alt)}">'
            f"<style>{fonts}{css}</style>{defs}{body}</svg>")


if __name__ == "__main__":
    total, weeks = calendar()
    OUT.write_text(build(total, weeks), encoding="utf-8")
    print(f"{OUT.name}: {OUT.stat().st_size // 1024} KB, {total:,} contributions")
