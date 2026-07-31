# Advisory Board

**A multi-agent financial advisory simulator where four agents argue over one household budget — and you can audit exactly how the disagreement was settled.**

Single HTML file. No build step, no dependencies, no framework. Open it and it runs.

> Built for the Cognition problem statement *"Multi-Agent Financial Advisory Simulator"*.

---

## The problem

Personal financial planning means balancing goals that genuinely compete — debt payoff, savings, investing. Ask one model to do all of it in one prompt and it quietly picks a favourite, or splits the difference and calls it balance. Neither is a plan you can defend.

The fix isn't a smarter single prompt. It's separating the concerns into specialists that each argue their own corner, and forcing a coordinator to reconcile them **against visible rules** instead of averaging them into mush.

## What it actually does

Four agents. Four separate calls to `claude-sonnet-4-6`, each with its own system prompt and a strict JSON contract.

| # | Agent | Mandate | Cannot |
|---|-------|---------|--------|
| 1 | **Budgeting** | Confirms true discretionary income, proposes a three-way split (buffer / debt / investing) | Pick a payoff method or asset mix |
| 2 | **Debt strategy** | Payoff method + share of discretionary income for *extra* payment | Set the investing share |
| 3 | **Investment planning** | Share to start investing now + category-level mix | Name any product; choose a payoff method |
| 4 | **Coordinator** | Sees all three. Names the conflict, cites a numbered rule, publishes one allocation | **Average the proposals** |

Agents 2 and 3 are deliberately written to disagree — one argues certainty of interest saved, the other argues time in the market. **That is the point.** The conflict is structural, not staged, because both agents are asking for the same rupees out of a pool that cannot cover both.

### The coordinator's rule set

| Rule | Trigger | Effect |
|------|---------|--------|
| **R1** Starter buffer | Emergency fund below ~1 month of essentials | Fund that gap first |
| **R2** Toxic debt | Any debt ≥ 15% APR | Paid aggressively before discretionary investing |
| **R3** Cheap debt | Debt below ~10% APR | Minimum only; freed share goes to investing on a long horizon |
| **R4** Hard cap | Asks exceed discretionary income | Scale every component proportionally until it fits |

If none of the four cleanly covers the real conflict, the coordinator is instructed to **say so** in a `rule_gap` field rather than stretch a citation. Case 03 exercises this: the dispute there is a wedding 18 months out versus a 30-year horizon, and no rule in the set arbitrates by time.

---

## Guardrails: prompt vs. code

This distinction is the honest part of the submission, so it's surfaced in the UI rather than buried.

**Enforced in the prompt** — the model is *asked*, and could fail:
- No named stocks, funds, schemes, insurers, brokers or tickers — category level only
- No guaranteed or projected returns
- No legal, tax-filing, or debt-settlement advice (routed to an out-of-scope field)
- No figure that isn't in the client file

**Enforced in code** — the model *cannot* fail these. They run in JavaScript after the response lands and render as a pass/fail panel the model has no ability to influence:

| ID | Check |
|----|-------|
| `G1` | Allocation re-summed in JS must not exceed discretionary income |
| `G2` | Final percentages total 100 (±1pp rounding) |
| `G3` | No negative component; contractual minimums stay reserved |
| `G4` | Output regex-scanned for ticker-shaped tokens, named institutions, guarantee language |
| `G5` | Payoff timeline is a **local amortisation simulation**, not the model's claim |
| `G6` | JSON parsed defensively — fences stripped, then first `{` to last `}` |

`G4` earns its keep: during development it caught the *local engine's own* narrative using the phrase "a guaranteed 41% saved". The check failed the build's flagship persona and the copy was rewritten.

`G5` matters too — on Case 01 the debt agent asserts a 21-month payoff while the browser's own simulation of the coordinator's actual allocation returns 32 months. Both numbers are shown, side by side.

---

## Running it

**It is self-contained and needs no host.** One file, no build, no dependencies, no server, no account. Double-click it.

```bash
git clone https://github.com/Atharva-Lakhe/AtharvaLakhe.git
cd AtharvaLakhe
open index.html                 # works immediately, on the local engine
```

### The two engines

The page probes for model access on load and tells you, in the top bar, which one it is running.

**Local rule engine — the default, zero setup.** Every agent is played by deterministic code in this file. All four personas produce real, persona-specific figures computed from the live client file. Nothing is stubbed and no network is touched. This is what you get by opening the file directly, and it is enough to exercise the whole negotiation, every rule, and every guardrail.

**Live agents — optional.** Click the mode pill in the top bar, paste an Anthropic API key, and the same four roles become four real streamed calls to `claude-sonnet-4-6`, token-by-token into each agent card.

```bash
npx serve .                     # then open the printed http:// address
```

Use a served address rather than `file://` for live mode — browsers send `Origin: null` from the filesystem and the API rejects it. The key is held in a JS variable for that tab only: never written to disk, never sent anywhere but `api.anthropic.com`. There is no `localStorage` or `sessionStorage` anywhere in the file; close the tab and the session is gone.

**The two are never confused.** When the local engine is running, a banner says so in plain words and names what is producing the text. Simulated output is never presented as model output — a demo that silently fakes its agents isn't a demo of anything.

---

## The interface

**Two stages.** You pick a client first, then get the full file — rather than landing in a dense form with nothing loaded.

**Four cases ship with it**, each chosen to exercise a different path through the rules:

- **Case 01 · Rhea Kulkarni** — a 41% credit card beside a 9.2% education loan. R2 and R3 fire against each other; the debt agent asks for 80% of the pool. Sharpest conflict.
- **Case 02 · Devansh Rao** — irregular freelance income, buffer under one month of essentials. R1 outranks everything.
- **Case 03 · Aisha & Neil Fernandes** — no toxic debt at all. The conflict is time-horizon, not interest-rate, and the coordinator declares the rule gap.
- **Blank** — enter your own household.

**The debt chart** is the interactive centrepiece. Balance is the magnitude, so it gets bar length. APR is a second measure on a different scale — which is never a second axis — so it sets the fill from a single-hue sequential ramp and is stated as a direct label. The rule that applies to each account rides alongside as **text** (`R2 · paid first`, `R3 · minimum only`, `judgement call`), never colour alone. Re-sort by APR, balance, payoff order or minimum and the bars redraw; hover for cost of carry; click for the full account detail; toggle to a table view for the same data as figures.

The rules are legible in the layout before a single agent has spoken.

**The rejected average.** The ruling shows what a naive average of the three asks *would* have produced — struck through and labelled rejected — directly above the actual allocation, with per-bucket `pp` deltas. It demonstrates the thesis instead of asserting it.

**Also:** live-recalculating discretionary income, an expandable negotiation ledger filterable by conflicts or rule applications, a per-agent concession table, plain-text export via clipboard or download, a print stylesheet, `aria-live` status announcements, visible focus states, full keyboard operation, both colour themes, and `prefers-reduced-motion` respected throughout.

### Design

Neo-brutalist, adapted for a tool rather than a landing page: offset zero-blur shadows, buttons that depress into their own shadow, a soft straw intake screen giving way to a bone workspace. The coordinator's ruling is the only charcoal block on the page, because it is the only verdict.

The palette is **computed, not eyeballed**. The three allocation series are a validated categorical set — light `#00907a / #c4553a / #5a6ec4`, dark `#25ab8e / #cf6a4f / #7b8ad8` — passing all six checks in both modes: lightness band, chroma floor, CVD separation (worst adjacent pair ΔE 8.5, above the floor), normal-vision separation, and contrast against each surface. Dark mode is *selected* rather than flipped: its own steps from the same hues, validated against the dark surface.

An earlier revision ran every surface at maximum contrast — saturated fills, pure-black 2px borders in light, near-white borders in dark — and it was tiring to look at. Accents now sit well below full saturation, borders are a mid tone rather than an extreme, and large filled blocks became washes with a coloured edge. The brutalist language survives; the glare doesn't.

Typography is a system stack by design: the page ships as one file with zero network dependencies, and a webfont that fails to load silently is worse than a system face chosen deliberately.

---

## Verification

The engine was exercised headless across all four personas and every render path — proposals, ruling, ledger, the chart at each sort in both chart and table view, plus thinking / error / mixed-agent states.

Results: allocations sum exactly to discretionary income in all four cases, percentages total 100, traces land in the 5–7 range, narratives run 103–129 words, bar widths stay within 0–100% with the largest always at full scale, every row carries an `aria-label` and a text rule chip, the empty-account case is handled, and no `undefined` or `NaN` reaches the DOM.

---

## Repository

```
index.html    the entire application — markup, styles, agents, engine
README.md     this file
LICENSE       MIT
```

---

## Disclaimer

An educational simulation, not advice from a licensed financial advisor. No return is guaranteed and all investing carries risk of loss. Tax, legal, and creditor-negotiation questions need a qualified professional.
