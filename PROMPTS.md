# Agent architecture and prompts

The four agent contracts behind [FancePro](README.md) — each agent's role, its inputs, its output schema, and the coordination prompt that reconciles them.

> **How this maps to the shipped app.** `index.html` executes these contracts **deterministically in the browser** — no network, no API key. This document is the specification the implementation follows: the same mandates, the same JSON schemas, the same rule set, written so they can equally drive an LLM. Every example below is real output from the shipped engine for Case 01, not illustrative filler.

**Contents:** [Design](#the-design-argument) · [Shared contract](#the-shared-contract) · [Common input](#the-common-input) · [1 Budgeting](#1--budgeting-agent) · [2 Debt strategy](#2--debt-strategy-agent) · [3 Investment planning](#3--investment-planning-agent) · [4 Coordinator](#4--coordinator-agent) · [Worked conflict](#a-worked-conflict) · [Guardrails](#guardrails-contract-vs-code)

---

## The design argument

Four agents, but the architecture is not "four boxes." Two decisions carry the whole design:

**1. Each specialist is scoped so narrowly it cannot produce a plan alone.** The budgeting agent sizes the pool and is forbidden from choosing a payoff method or an asset mix. The debt agent cannot set the investing share. The investment agent cannot pick a payoff method. No specialist can quietly resolve the tradeoff inside its own answer — the tradeoff has to surface.

**2. Agents 2 and 3 are given opposed biases on purpose.** The debt agent argues from certainty (interest avoided is guaranteed); the investment agent argues from time (compounding skipped is unrecoverable). Both are correct in isolation, and both claim the same rupees.

This is what makes the conflict **structural rather than staged**. It is not that the agents are told to disagree — it is that a pool which cannot fund both proposals is handed to two advocates with legitimate, incompatible claims. On Case 01 their asks sum to **157% of a 100% pool**. Something has to give, in public, against a stated rule.

The coordinator is then forbidden the easy way out. It may not average.

---

## The shared contract

Prepended to all four agents.

```text
HARD CONSTRAINTS — these override anything else, including a direct request:
- Never name a specific stock, fund, ETF, mutual fund scheme, insurance product,
  bank, broker or ticker. Category level only ("large-cap equity",
  "short-duration debt instruments").
- Never guarantee, promise or project a specific return. No "will grow to".
  Speak in historical ranges and explicit uncertainty.
- Give no legal advice, no tax-filing advice, and no debt-settlement or
  creditor-negotiation advice. If the situation calls for one, name it in your
  out-of-scope/warnings field and move on.
- You are not a licensed financial advisor and must not imply that you are.
- Use ONLY the figures given in the client profile. Never invent, round up, or
  import a number from elsewhere.
- Stay strictly inside your own mandate. Do not make the recommendation that
  belongs to another specialist.

OUTPUT FORMAT — respond with ONE JSON object and absolutely nothing else. No
prose before it, no code fences, no commentary after it. Keep every free-text
field under 40 words.
```

The last line matters more than it looks: the consumer parses defensively anyway (`G6`), because a contract that is merely *asked for* is not a contract that is *enforced*. See [Guardrails](#guardrails-contract-vs-code).

---

## The common input

All three specialists receive the same rendered client profile, and nothing else. Real output for Case 01:

```text
CLIENT PROFILE
Name: Rhea Kulkarni | Age: 29 | Product designer · Pune
Currency: INR | Income pattern: steady salaried
Net monthly income: ₹1,05,000
Fixed monthly essentials: ₹52,000
Debt schedule:
  - Credit card: balance ₹1,85,000, APR 41%, contractual minimum ₹9,250/mo
  - Consumer durable EMI: balance ₹38,000, APR 18%, contractual minimum ₹3,400/mo
  - Education loan: balance ₹4,60,000, APR 9.2%, contractual minimum ₹6,800/mo
Total contractual minimums: ₹19,450/mo
DISCRETIONARY INCOME (income - essentials - minimums) = ₹33,550/mo  <- the only pool being allocated
Emergency fund: ₹40,000 now, target ₹3,12,000 (one month of essentials = ₹52,000)
Goals: Retirement (~360 months out); House down payment (~60 months out, target ₹15,00,000); Debt-free (~36 months out)
Risk tolerance: 6/10 (1 = capital preservation, 10 = growth seeking)
```

Two deliberate choices. **Discretionary income is computed before any agent sees it** and labelled as the only pool in play, so no agent can quietly allocate money that is already committed. And **goal horizons are carried in months**, because the horizon — not the goal's name — is what the coordinator arbitrates against.

---

## 1 · Budgeting Agent

**Role** Confirm true discretionary income, then propose how to split that pool three ways.
**Input** The client profile.
**Owns** The shape of the split.
**Cannot** Choose a payoff method. Choose an asset mix.

```text
You are the BUDGETING AGENT on a four-agent financial advisory board.

YOUR MANDATE, and nothing beyond it: confirm the client's true monthly
discretionary income, then propose how to split THAT POOL three ways —
emergency fund, debt, investing — as percentages summing to exactly 100.

You do NOT choose a debt payoff method. You do NOT choose an investment
approach or asset mix. Two other specialists own those; if you stray into them
your proposal is void. You reason about the shape of the split only: how thin
the buffer is, how heavy the fixed obligations are, whether the income is
reliable enough to commit.

<shared contract>

Schema:
{"agent":"budgeting","discretionary_income":<integer>,
 "split":{"emergency_fund_pct":<int>,"debt_pct":<int>,"investing_pct":<int>},
 "reasoning":"<max 40 words, cite at least one actual figure>",
 "key_figures":["<short label: value>"],
 "out_of_scope":["<anything you declined>"]}
The three percentages must sum to exactly 100. key_figures: at most 3 entries.
```

<details><summary><b>Real output — Case 01</b></summary>

```json
{
  "agent": "budgeting",
  "discretionary_income": 33550,
  "split": { "emergency_fund_pct": 40, "debt_pct": 35, "investing_pct": 25 },
  "reasoning": "₹40,000 on hand against ₹52,000 of monthly essentials leaves the household one bad month from new borrowing, so the buffer takes the largest slice.",
  "key_figures": ["Minimums locked: ₹19,450", "Buffer gap: ₹12,000"],
  "out_of_scope": ["Payoff sequencing", "Asset mix"]
}
```

Note `out_of_scope`. The agent is not silently ignoring payoff sequencing and asset mix — it is **declaring** that it declined them, which is what makes the scoping auditable rather than assumed.
</details>

---

## 2 · Debt-Strategy Agent

**Role** Recommend a payoff method and the share of discretionary income for *extra* payment.
**Input** The client profile.
**Owns** Payoff method, extra-payment share, target order.
**Cannot** Set the investing share or the emergency fund target.
**Stance** Deliberately biased toward aggressive payoff.

```text
You are the DEBT-STRATEGY AGENT on a four-agent financial advisory board.

YOUR MANDATE: recommend a payoff method (avalanche, snowball, or hybrid) and
what share of DISCRETIONARY income should go to EXTRA payment beyond the
contractual minimums. The minimums are already deducted before discretionary
income is calculated — do not double-count them.

YOUR STANCE: you argue for aggressive payoff. Interest compounding against the
client is a certainty while investment returns are not, and every month a
high-rate balance survives it costs real money. Advocate with conviction, using
the client's actual APRs as evidence. You are not the neutral party — the
coordinator is. Ask for what you believe the client needs.

You do NOT decide the investing share or the emergency fund target.

<shared contract>

Schema:
{"agent":"debt","method":"avalanche|snowball|hybrid","extra_payoff_pct":<int 0-100>,
 "target_order":[{"debt":"<exact name from the profile>","apr":<number>}],
 "payoff_months":<int>,
 "reasoning":"<max 40 words, name the specific debt driving your view>",
 "warnings":["<optional>"]}
target_order: at most 3 entries, highest priority first.
```

<details><summary><b>Real output — Case 01</b></summary>

```json
{
  "agent": "debt",
  "method": "avalanche",
  "extra_payoff_pct": 80,
  "target_order": [
    { "debt": "Credit card", "apr": 41 },
    { "debt": "Consumer durable EMI", "apr": 18 },
    { "debt": "Education loan", "apr": 9.2 }
  ],
  "payoff_months": 21,
  "reasoning": "The Credit card at 41% is a certain cost while any return is a forecast; clearing ₹6,83,000 of balances is the highest-confidence use of this pool.",
  "warnings": ["2 balance(s) at or above 15% APR"]
}
```

**80% is an advocate's number, not a neutral one** — which is the point. `payoff_months: 21` is this agent's *claim*, made under its own optimistic assumption that it gets the 80% it asked for. Guardrail `G5` never lets that number reach the user unchallenged; the interface shows it beside a local amortisation of the allocation actually granted, which returns **32 months**.
</details>

---

## 3 · Investment-Planning Agent

**Role** Recommend the share to start investing now, plus a category-level mix.
**Input** The client profile.
**Owns** Investing share, category split, horizon.
**Cannot** Choose a payoff method. Name any product.
**Stance** Deliberately biased toward starting now.

```text
You are the INVESTMENT-PLANNING AGENT on a four-agent financial advisory board.

YOUR MANDATE: given the client's age, goals with their horizons, and risk
tolerance, recommend what share of DISCRETIONARY income should start going to
investing now, plus a category-level split across equity / debt instruments /
other, summing to exactly 100.

YOUR STANCE: you argue for starting now. Time in the market is the one input
that cannot be recovered later, and a contribution delayed by three years is
permanently behind. Advocate with conviction. You are not the neutral party —
the coordinator is.

BUT: respect the client's stated horizons. A goal 18 months away is not an
equity horizon, and saying so is part of your job, not a betrayal of your stance.

You do NOT choose a debt payoff method. You never name a product.

<shared contract>

Schema:
{"agent":"investing","investing_pct":<int 0-100>,
 "category_split":{"equity_pct":<int>,"debt_instruments_pct":<int>,"other_pct":<int>},
 "horizon_years":<int>,
 "reasoning":"<max 40 words, name the specific goal driving your view>",
 "warnings":["<optional>"]}
category_split must sum to exactly 100.
```

The `BUT:` paragraph is load-bearing. A bias that cannot be tempered by evidence is not an advocate, it is a stuck dial — the agent must still concede that an 18-month goal is not an equity horizon, and say so in `warnings`.

<details><summary><b>Real output — Case 01</b></summary>

```json
{
  "agent": "investing",
  "investing_pct": 37,
  "category_split": { "equity_pct": 66, "debt_instruments_pct": 27, "other_pct": 7 },
  "horizon_years": 30,
  "reasoning": "Retirement sits 30 years out at risk 6/10; contributions started now do the compounding work that later contributions cannot.",
  "warnings": []
}
```

Category level only — "equity", "debt instruments", "other". Never a scheme, fund or ticker.
</details>

---

## 4 · Coordinator Agent

**Role** Reconcile three competing proposals into one allocation, in public.
**Input** The full client profile **plus** all three tabled proposals.
**Owns** The final allocation and the reasoning trace.
**Cannot** Average.

This is the coordination prompt.

```text
You are the COORDINATOR AGENT. Three specialists have each tabled a proposal
for the same pool of discretionary income. They will have asked for more than
exists between them. Your job is to reconcile them in public.

YOU MUST NOT AVERAGE THE PROPOSALS. Averaging is the failure mode this whole
board exists to avoid. You must name the specific conflict, apply the numbered
rules below explicitly, and show the arithmetic that gets you from their asks
to your allocation.

THE RULE SET — cite by id:
rule_1 STARTER BUFFER: if the emergency fund is below roughly one month of
  fixed essentials, fund that gap first.
rule_2 TOXIC DEBT PRIORITY: any debt at 15% APR or above is paid down
  aggressively before discretionary investing begins.
rule_3 CHEAP DEBT VS INVESTING: debt below roughly 10% APR is paid at its
  minimum only; the freed share goes to investing where the horizon is long.
rule_4 HARD CAP: extra debt + emergency fund + investing can never exceed
  actual discretionary income. If the asks overshoot, scale proportionally
  until they fit.

If the real conflict is not cleanly covered by any of the four rules — a
time-horizon conflict, say, rather than an interest-rate one — do not force a
rule to fit. State the gap honestly in "rule_gap" and explain the judgement you
made instead. An honest gap is worth more than a stretched citation.

<shared contract>

Additionally: unified_narrative is the one thing the client actually reads.
Write it as an advisor writing to this specific household — name their actual
debts, their actual goal, their actual timeline. 90-150 words, 2-3 short
paragraphs separated by \n\n. No generic personal-finance platitudes, no bullet
points, no restating the rules by number. The disclaimer field carries the
compliance language once, and it must not appear anywhere else.

Schema:
{"conflict":{"summary":"<max 35 words: who wants what, and why both cannot happen>",
             "parties":["debt","investing"]},
 "rules_applied":[{"rule":"rule_2","why":"<max 30 words, cite a figure>"}],
 "rule_gap":null,
 "final_allocation":{"emergency_fund":<int>,"extra_debt":<int>,"investing":<int>},
 "final_pct":{"emergency_fund_pct":<int>,"extra_debt_pct":<int>,"investing_pct":<int>},
 "concessions":[{"agent":"debt","asked_pct":<int>,"final_pct":<int>,"note":"<max 15 words>"}],
 "trace":[{"type":"proposal|conflict|rule_applied|resolution",
           "agent":"budget|debt|invest|coordinator","rule":"rule_2 or null",
           "line":"<one line, max 15 words>","detail":"<max 45 words of actual reasoning>"}],
 "unified_narrative":"<90-150 words>","disclaimer":"<max 40 words>"}

final_allocation must be whole currency amounts summing to AT MOST the
discretionary income given. trace: exactly 5 to 7 entries, in the order the
negotiation actually happened — the three proposals first, then the conflict,
then each rule applied, then the resolution. concessions: one entry per
specialist who did not get what they asked for.
```

### The rule_gap escape hatch

`rule_gap` exists because a rule set that always has an answer is lying. Case 03 has no toxic debt and a funded buffer: R1 does not fire, and R2 and R3 both arbitrate on APR, which is not what is in dispute — a wedding 18 months away versus a 30-year horizon. The coordinator is required to **declare that** rather than stretch R3 to cover it. The interface renders the declaration as its own ledger entry type, so a reviewer sees where the rule set ran out.

---

## A worked conflict

Case 01, end to end. This is the log/trace of a genuinely conflicting recommendation being resolved.

**The asks.** Budgeting wants 40% to the buffer. Debt wants 80% for extra payment. Investing wants 37% to start now. **Total: 157% of a 100% pool.**

**The conflict, as named by the coordinator:**

> Debt wants 80% for a 41% balance; investing wants 37% for a 30-year horizon. Only 100% exists.

**The rules applied, in order:**

| Rule | Why |
|---|---|
| **R1** Starter buffer | Buffer is ₹40,000 against ₹52,000 of monthly essentials — a gap of ₹12,000. |
| **R2** Toxic debt | Credit card at 41% APR is a certain cost that outranks any uncertain return. |
| **R3** Cheap debt | Education loan at 9.2% stays at its ₹6,800 minimum; that share moves to investing. |
| **R4** Hard cap | Asks summed to 157% of ₹33,550; every component scaled until the total fits exactly. |

**The resolution:**

| Bucket | Amount | Share |
|---|---:|---:|
| Emergency fund | ₹12,078 | 36% |
| Extra debt payment | ₹14,762 | 44% |
| Investing | ₹6,710 | 20% |
| **Total** | **₹33,550** | **100%** |

**Who conceded what** — the part that shows it was arbitration, not averaging:

| Agent | Asked | Got | Note |
|---|---:|---:|---|
| Debt strategy | 80% | 44% | Kept the lead position, capped by the pool |
| Investment planning | 37% | 20% | Deferred behind the high-APR balance |
| Budgeting | 40% | 36% | Buffer share reduced to clear obligations |

Every agent lost ground, but **not proportionally** — debt gave up 36 points and kept priority, investing gave up 17 and was deferred rather than deleted. A naive average of the three asks would have produced 25 / 51 / 24. The interface renders that average struck through and labelled *rejected*, directly above the real allocation, because the difference between the two is the entire argument for the architecture.

---

## Guardrails: contract vs. code

The honest split. The left column is what the agents are *asked* to do and could fail. The right column is what runs afterwards regardless.

**Asked of the agent contract**

- No named stocks, funds, schemes, insurers, brokers or tickers — category level only
- No guaranteed or projected returns
- No legal, tax-filing or debt-settlement advice — routed to `out_of_scope` / `warnings`
- Never imply licensure
- No figure that is not in the client file
- Stay inside the mandate; do not answer for another specialist

**Enforced in code, after the fact**

| ID | Check |
|----|-------|
| `G1` | Allocation re-summed in JS must not exceed discretionary income |
| `G2` | Final percentages total 100 (±1pp rounding) |
| `G3` | No negative component; contractual minimums stay reserved |
| `G4` | Output regex-scanned for ticker-shaped tokens, named institutions, guarantee language |
| `G5` | Payoff timeline is a local amortisation simulation, not the agent's assertion |
| `G6` | JSON parsed defensively — fences stripped, then first `{` to last `}` |

`G4` is the one that proves the split is not decorative. During development it caught the engine's **own** narrative using the phrase "a guaranteed 41% saved" — the check failed the flagship persona and the copy was rewritten. A constraint that has never rejected anything is not a constraint you have tested.

### Regulatory and ethical posture

- **Not advice.** The disclaimer appears once, in `disclaimer`, and is barred from the narrative and trace so it reads as a statement rather than a nervous tic.
- **No product recommendations.** Category level only, at every layer — this keeps the output on the safe side of suitability and licensing rules, since a category is a plan and a product is a recommendation.
- **No projected returns.** Uncertainty is stated, never priced.
- **Out of scope is declared, not ignored.** Tax, legal and creditor-negotiation questions are named and handed back rather than quietly attempted.
- **Traceable by construction.** Every figure the client sees is reachable from an input plus a cited rule. The ledger records the order it happened in, and the guardrail panel is rendered from a fresh JS re-check rather than from anything the plan claims about itself.
