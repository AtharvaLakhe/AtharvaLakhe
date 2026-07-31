# Sample Exported Plan

This is a representative export from **Case 01: Rhea Kulkarni**. The exact wording can vary as the local rules respond to edited client inputs, but the structure is what the app produces.

```text
FINANCIAL PLAN - produced by a four-agent advisory simulation
==================================================================
Client        Rhea Kulkarni, 29 - Product designer, Pune
Source        local rule engine

MONTHLY POSITION
  Net income                  INR 105,000
  Fixed essentials          - INR 52,000
  Contractual minimums      - INR 19,450
  Discretionary income      = INR 33,550

DEBT SCHEDULE
  Credit card                  INR 185,000   41%   min INR 9,250
  Consumer durable EMI          INR 38,000   18%   min INR 3,400
  Education loan               INR 460,000  9.2%   min INR 6,800

THE CONFLICT
  The debt strategy wants nearly all discretionary cash directed to toxic debt,
  while the investment plan wants to preserve a small start toward long-horizon goals.

RULES APPLIED
  R1 Starter buffer
     Emergency cash is below roughly one month of fixed essentials, so the first
     allocation must close that immediate fragility.

  R2 Toxic debt priority
     The 41% credit card and 18% consumer EMI are above the 15% APR threshold and
     outrank discretionary investing until they are under control.

FINAL MONTHLY ALLOCATION
  Emergency fund               INR 13,420   40%
  Extra debt payment           INR 16,775   50%
  Investing                     INR 3,355   10%
  Total allocated              INR 33,550   of INR 33,550 discretionary
  Contractual minimums continue in full alongside this.

PAYOFF PROJECTION
  Computed locally from the debt balances, APRs, minimums, and final extra-debt
  allocation. The projection is a simplified estimate, not a promise.

NEGOTIATION LEDGER
  01  [PROPOSAL] Budgeting tables a starter-buffer split.
  02  [PROPOSAL] Debt asks for aggressive extra payoff using avalanche order.
  03  [PROPOSAL] Investing asks to keep a small monthly habit alive.
  04  [CONFLICT] Debt and investing ask for the same rupees.
  05  [RULE] R1 reserves emergency cash first.
  06  [RULE] R2 prioritises toxic debt before discretionary investing.

GUARDRAIL CHECKS
  [PASS] G1 Allocation does not exceed discretionary income.
  [PASS] G2 Percentages total 100.
  [PASS] G3 No negative component.
  [PASS] G4 No named products, tickers, or guaranteed-return language.
  [PASS] G5 Payoff timeline computed locally.
  [PASS] G6 JSON parsed defensively.

DISCLAIMER
  Educational simulation only. Not financial, legal, tax, or debt-settlement advice.
==================================================================
```
