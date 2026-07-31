# Sample export — Case 01

Produced by clicking **Download plan** on the ruling stage for *Rhea Kulkarni*, the
debt-heavy persona. This is the file the app writes, unedited apart from the run date.

It is worth reading for three things: the payoff projection is computed by a local
amortisation loop rather than asserted, the guardrail block is re-verified in
JavaScript after the plan is built, and the ledger records the order the negotiation
actually happened in.

```text
FINANCIAL PLAN — produced by a four-agent advisory simulation
==================================================================
Client        Rhea Kulkarni, 29 — Product designer · Pune
Prepared      <run date>
Source        local rule engine

MONTHLY POSITION
  Net income                  ₹1,05,000
  Fixed essentials          − ₹52,000
  Contractual minimums      − ₹19,450
  Discretionary income      = ₹33,550

DEBT SCHEDULE
  Credit card                 ₹1,85,000     41%  min ₹9,250
  Consumer durable EMI          ₹38,000     18%  min ₹3,400
  Education loan              ₹4,60,000    9.2%  min ₹6,800

GOALS
  Retirement                    360 months
  House down payment             60 months   target ₹15,00,000
  Debt-free                      36 months
  Risk tolerance             6/10

THE CONFLICT
  Debt wants 80% for a 41% balance; investing wants 37% for a 30-year horizon. Only 100% exists.

RULES APPLIED
  R1 Starter buffer
     Buffer is ₹40,000 against ₹52,000 of monthly essentials — a gap of ₹12,000.
  R2 Toxic debt priority
     Credit card at 41% APR is a certain cost that outranks any uncertain return.
  R3 Cheap debt vs. investing
     Education loan at 9.2% stays at its ₹6,800 minimum; that share moves to investing.
  R4 Hard cap
     Asks summed to 157% of ₹33,550; every component scaled until the total fits exactly.

FINAL MONTHLY ALLOCATION
  Emergency fund                   ₹12,078   36%
  Extra debt payment               ₹14,762   44%
  Investing                         ₹6,710   20%
  Total allocated                  ₹33,550   of ₹33,550 discretionary
  (contractual minimums continue in full alongside this)

PAYOFF PROJECTION (computed locally, not asserted by a model)
  Every balance clears in about 2 yrs 8 mo, with roughly ₹1,07,663 of interest.

NEGOTIATION LEDGER
  01  [PROPOSAL] Budgeting: 40/35/25 across buffer, debt, investing
      ₹40,000 on hand against ₹52,000 of monthly essentials leaves the household one bad month from new borrowing, so the buffer takes the largest slice.
  02  [PROPOSAL] Debt: avalanche, 80% to extra payment
      The Credit card at 41% is a certain cost while any return is a forecast; clearing ₹6,83,000 of balances is the highest-confidence use of this pool.
  03  [PROPOSAL] Investing: 37% now, 66% equity
      Retirement sits 30 years out at risk 6/10; contributions started now do the compounding work that later contributions cannot.
  04  [CONFLICT] Three asks total 157% of a 100% pool
      Debt wants 80% and investing wants 37% of the same ₹33,550. Both cannot be funded; the overshoot is 57 points.
  05  [RULE_APPLIED] R1 Starter buffer applied
      Buffer is ₹40,000 against ₹52,000 of monthly essentials — a gap of ₹12,000.
      -> R1: If the emergency fund is below roughly one month of fixed essentials, fund that gap first. A household with no buffer converts its next surprise into new high-interest debt, which undoes any payoff or investing progress made in the same period.
  06  [RULE_APPLIED] R2 Toxic debt priority applied
      Credit card at 41% APR is a certain cost that outranks any uncertain return.
      -> R2: Any debt carrying 15% APR or above is paid down aggressively before discretionary investing begins. A guaranteed 15%+ cost of carry outranks an uncertain expected return, so retiring that balance is the higher-certainty use of the same money.
  07  [RULE_APPLIED] R3 Cheap debt vs. investing applied
      Education loan at 9.2% stays at its ₹6,800 minimum; that share moves to investing.
      -> R3: Debt below roughly 10% APR is serviced at its contractual minimum only. The share that would have gone to extra payoff is redirected to investing where the goal horizon is long, because the expected return on a long horizon plausibly exceeds a sub-10% cost of carry.

GUARDRAIL CHECKS (re-verified in code after the response)
  [PASS] G1  Allocation re-summed in JS does not exceed discretionary income — ₹33,550 of ₹33,550 · ₹0 free
  [PASS] G2  Final percentages total 100 — 100%
  [PASS] G3  No negative component; contractual minimums untouched — ₹19,450/mo reserved first
  [PASS] G4  Scanned for named products, tickers and guarantee language — clean · negation in disclaimer
  [PASS] G5  Payoff timeline computed by local amortisation, not asserted — simulated in browser

THE PLAN
  Your buffer is ₹40,000 against ₹52,000 of monthly essentials, and that
  is the first thing we fix. ₹12,078 a month goes there until you are
  covered for a full month — everything else here is unstable until that
  is true.

  ₹14,762 of it goes at the Credit card, which is costing you 41% a year
  whatever else happens. Your investment agent argued for more now, and on
  a 30-year view it is not wrong — but 41% of certain cost removed
  outranks an uncertain return, so investing starts at ₹6,710 and steps up
  the month that balance clears.

  Revisit this the month the credit card clears — projected around 2 yrs 8
  mo at this rate — and move the freed payment straight into investing
  rather than into spending.

==================================================================
This is an educational simulation, not advice from a licensed financial advisor. No return is guaranteed and all investing carries risk of loss. Tax, legal and creditor-negotiation questions need a qualified professional.
```
