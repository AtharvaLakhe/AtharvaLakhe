"""A pixel wall anyone can paint by opening an issue.

    python wall/paint.py paint "paint red at 20,10" <github-user>   # prints the bot's reply
    python wall/paint.py render                                    # redraw wall.svg and README.md
"""
import base64
import datetime as dt
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

REPO = "AtharvaLakhe/AtharvaLakhe"
COLS, ROWS = 40, 20
HERE = Path(__file__).resolve().parent
STATE = HERE / "wall.json"
README = HERE.parent / "README.md"

COLOURS = {
    "black": "#0E0F12", "white": "#F2EFE8", "red": "#E5484D", "orange": "#F2802E", "yellow": "#F5C842",
    "green": "#46A758", "teal": "#12A594", "blue": "#3E7BFA", "purple": "#8E4EC6", "pink": "#F076B5",
}
CANVAS, FRAME, DOT, RULER, TEXT = "#1E2127", "#2C3038", "#3A3F49", "#7C8494", "#E9E6DF"

# "AL", signed in the corner by the owner so the wall never starts blank
SIGNATURE = [".#..#..", "#.#.#..", "###.#..", "#.#.#..", "#.#.###"]
EXAMPLE = "paint red at 20,10"


def load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    stamp = "2026-10-11T00:00:00Z"
    hist = [dict(x=COLS - 8 + i, y=ROWS - 6 + j, colour="white", user="AtharvaLakhe", at=stamp)
            for j, row in enumerate(SIGNATURE) for i, ch in enumerate(row) if ch == "#"]
    return {"history": hist}


def save(state):
    STATE.write_text(json.dumps(state, indent=1) + "\n")


def grid(state):
    cells = {}
    for p in state["history"]:
        cells[(p["x"], p["y"])] = p["colour"]
    return cells


def paint(state, title, user):
    m = re.match(r"^\s*paint\s+([a-z]+)\s+(?:at\s+)?(\d{1,3})\s*[,\s]\s*(\d{1,3})\s*$", title, re.I)
    if not m:
        return False, (f"I couldn't find a colour and a square in “{title.strip()}”.\n\n"
                       f"Write the title like `{EXAMPLE}`: a colour, then the column (1–{COLS}) and the row (1–{ROWS}).")
    colour, x, y = m.group(1).lower(), int(m.group(2)), int(m.group(3))
    if colour not in COLOURS:
        return False, f"I don't have **{colour}**. Pick one of: {', '.join(COLOURS)}. Then open a new issue."
    if not (1 <= x <= COLS and 1 <= y <= ROWS):
        return False, f"{x},{y} is off the wall. Columns go from 1 to {COLS} and rows from 1 to {ROWS}."
    before = grid(state).get((x - 1, y - 1))
    state["history"].append(dict(x=x - 1, y=y - 1, colour=colour, user=user,
                                 at=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")))
    over = f" over {before}" if before and before != colour else ""
    return True, (f"Painted {x},{y} {colour}{over}. It's on the wall now: https://github.com/{REPO.split('/')[0]}\n\n"
                  f"It can take a minute or two to show up. Thanks for stopping by.")


def font():
    return base64.b64encode((HERE / "Silkscreen-Regular.ttf").read_bytes()).decode()


def wall_svg(state):
    cell, x0, y0 = 27, 72, 92
    W, H = x0 + COLS * cell + 48, y0 + ROWS * cell + 44
    cells = grid(state)
    hist = state["history"]
    painters = {p["user"] for p in hist} - {"AtharvaLakhe"}
    visits = sum(1 for p in hist if p["user"] != "AtharvaLakhe")
    o = [f'<rect width="{W}" height="{H}" rx="18" fill="{CANVAS}"/>',
         f'<text x="{x0}" y="50" class="t" font-size="22" fill="{TEXT}">atharva\'s wall</text>']
    status = ("nobody has painted yet" if not painters else
              f"{visits} pixel{'s' * (visits != 1)} by {len(painters)} {'person' if len(painters) == 1 else 'people'}")
    o.append(f'<text x="{x0 + COLS * cell}" y="50" class="t" font-size="16" fill="{RULER}" text-anchor="end">{status}</text>')
    o.append(f'<rect x="{x0 - 6}" y="{y0 - 6}" width="{COLS * cell + 12}" height="{ROWS * cell + 12}" rx="6" fill="none" stroke="{FRAME}" stroke-width="2"/>')
    for c in range(COLS):
        if c == 0 or (c + 1) % 5 == 0:
            o.append(f'<text x="{x0 + c * cell + cell / 2}" y="{y0 - 14}" class="t" font-size="14" fill="{RULER}" text-anchor="middle">{c + 1}</text>')
    for r in range(ROWS):
        if r == 0 or (r + 1) % 5 == 0:
            o.append(f'<text x="{x0 - 14}" y="{y0 + r * cell + cell / 2 + 4}" class="t" font-size="14" fill="{RULER}" text-anchor="end">{r + 1}</text>')
    o.append(f'<pattern id="d" width="{cell}" height="{cell}" patternUnits="userSpaceOnUse" x="{x0}" y="{y0}">'
             f'<circle cx="{cell / 2}" cy="{cell / 2}" r="1.6" fill="{DOT}"/></pattern>')
    o.append(f'<rect x="{x0}" y="{y0}" width="{COLS * cell}" height="{ROWS * cell}" fill="url(#d)"/>')
    for (x, y), colour in sorted(cells.items()):
        o.append(f'<rect x="{x0 + x * cell + 1}" y="{y0 + y * cell + 1}" width="{cell - 2}" height="{cell - 2}" rx="3" fill="{COLOURS[colour]}"/>')
    if not painters:  # empty state: show where the example title would paint
        ex, ey = x0 + 19 * cell, y0 + 9 * cell
        o.append(f'<rect class="p" x="{ex + 1}" y="{ey + 1}" width="{cell - 2}" height="{cell - 2}" rx="3" fill="none" stroke="{TEXT}" stroke-width="1.5" stroke-dasharray="4 3"/>')
        o.append(f'<text x="{ex + cell + 8}" y="{ey + cell / 2 + 5}" class="t" font-size="14" fill="{RULER}">20,10</text>')
    last = hist[-1]
    if last["user"] != "AtharvaLakhe":
        lx, ly = x0 + last["x"] * cell, y0 + last["y"] * cell
        o.append(f'<rect class="p" x="{lx - 3}" y="{ly - 3}" width="{cell + 6}" height="{cell + 6}" rx="6" fill="none" stroke="{TEXT}" stroke-width="2"/>')
        o.append(f'<text x="{x0 + COLS * cell}" y="{y0 + ROWS * cell + 32}" class="t" font-size="13" fill="{RULER}" text-anchor="end">'
                 f'latest: {last["x"] + 1},{last["y"] + 1} by @{last["user"].lower()}</text>')
    style = (f"@font-face{{font-family:S;src:url(data:font/ttf;base64,{font()}) format('truetype')}}"
             ".t{font-family:S,monospace}.p{animation:p 1.4s ease-in-out 5}"
             "@keyframes p{50%{opacity:.15}}@media (prefers-reduced-motion:reduce){.p{animation:none}}")
    label = f"Atharva's pixel wall: {status}."
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="{label}"><style>{style}</style>{"".join(o)}</svg>')


def swatch(hex_):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">'
            f'<rect x="2" y="2" width="44" height="44" rx="10" fill="{hex_}" stroke="#2C3038" stroke-width="3"/></svg>')


def issue_url(colour):
    body = (f"Change **20,10** in the title to the square you want, column first (1–{COLS}) then row (1–{ROWS}). "
            f"You can also change the colour. Then press **Create**. A bot paints it and replies here.")
    return f"https://github.com/{REPO}/issues/new?title={quote(f'paint {colour} at 20,10')}&body={quote(body)}"


def readme(state):
    hist = state["history"]
    recent = []
    for p in reversed(hist):
        if p["user"] != "AtharvaLakhe" and p["user"] not in recent:
            recent.append(p["user"])
    swatches = " ".join(f'<a href="{issue_url(c)}"><img src="wall/swatches/{c}.svg" width="40" alt="Paint {c}" title="{c}"></a>'
                         for c in COLOURS)
    if recent:
        faces = " ".join(f'<a href="https://github.com/{u}"><img src="https://github.com/{u}.png?size=64" width="32" height="32" alt="@{u}" title="@{u}"></a>'
                         for u in recent[:12])
        painters = f"<p>Recently painted by<br><br>{faces}</p>"
    else:
        painters = "<p><sub>Nobody has painted yet. The first square is yours.</sub></p>"
    return f"""<div align="center">

<img src="wall/wall.svg?v={len(hist)}" width="100%" alt="Atharva's pixel wall. Anyone can paint one square at a time.">

<h3>Paint a square on my wall</h3>

<p>Pick a colour. GitHub opens an issue with the title <code>{EXAMPLE}</code>.<br>
Change <code>20,10</code> to your square (column, then row) and press Create. A bot paints it within a minute.</p>

<p>{swatches}</p>

{painters}

</div>

<br>

<sub>I build software that shows its work: <a href="https://security4her.vercel.app">Security4Her</a>, <a href="https://github.com/AtharvaLakhe/PSR-Net">PSR-Net</a>, <a href="https://github.com/AtharvaLakhe/SPARC">SPARC</a>, <a href="https://github.com/AtharvaLakhe/CarbonLedger">CarbonLedger</a>, <a href="https://github.com/AtharvaLakhe/FancePro">FancePro</a>, <a href="https://github.com/AtharvaLakhe/LancePro">LancePro</a>. Write to me at <a href="mailto:atharvalakhe09@gmail.com">atharvalakhe09@gmail.com</a>.</sub>
"""


def render(state):
    (HERE / "wall.svg").write_text(wall_svg(state), encoding="utf-8")
    (HERE / "swatches").mkdir(exist_ok=True)
    for name, hex_ in COLOURS.items():
        (HERE / "swatches" / f"{name}.svg").write_text(swatch(hex_))
    README.write_text(readme(state), encoding="utf-8")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    state = load()
    if len(sys.argv) >= 4 and sys.argv[1] == "paint":
        ok, reply = paint(state, sys.argv[2], sys.argv[3])
        print(reply)
        if ok:
            save(state)
            render(state)
        sys.exit(0 if ok else 1)
    elif sys.argv[1:] == ["render"]:
        save(state)
        render(state)
    else:
        sys.exit(__doc__)
