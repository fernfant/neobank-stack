---
title: Credit and decisioning
type: layer
status: living
updated: 2026-08-18
sources: 8
tags: [credit, underwriting, uk, usa, ml]
---

## Summary

A neobank has an asymmetric advantage in credit: it can see the applicant's actual cash
flow. In 2025–2026 that stopped being a proprietary trick and became productised — FICO,
Experian and Nova Credit all shipped cash-flow-augmented scores. The architectural question
is where the decision boundary sits between bureau score, cash-flow model, and your own
behavioural model, and how you evidence each.

## UK

- **Bureaus:** Experian, Equifax, TransUnion (formerly Callcredit). Plus CRA-shared data via
  CAIS/Insight/SHARE.
- **Open Banking** gives permissioned access to current-account transaction data — the UK
  had this before the US, and it is the reason UK challengers' affordability models are
  ahead.
- **Regulatory frame:** FCA Consumer Duty and affordability rules mean you must evidence not
  just *credit risk* but *affordability* and *foreseeable harm*. Model explainability is not
  optional.

## USA

- **Bureaus:** Experian, Equifax, TransUnion. Scores: FICO (multiple versions), VantageScore
  4.0.
- **CFPB §1033** personal financial data rights were finalised October 2024, requiring large
  institutions to expose consumer-permissioned data through standardised APIs by **April
  2026** `[reported]`. This is the US catching up to Open Banking — and it changes the
  build-vs-buy calculus for data aggregation.
- **Regulatory frame:** ECOA/Reg B adverse action notices mean every decline needs a
  specific, accurate reason. That constrains model choice more than most teams expect —
  reason-code generation must be a first-class model output, not a post-hoc rationalisation.

## Cash-flow underwriting — the 2025–2026 shift

- **FICO × Plaid** (Nov 2025): next-generation cash-flow UltraFICO using Plaid for real-time
  cash-flow connectivity, deliberately packaged to slot into existing lender workflows
  `[confirmed]`.
- **Experian Credit + Cashflow Score** (Nov 2025): claimed >40% predictive-accuracy gain
  versus conventional models across personal loans, bankcards, LOCs and mortgages
  `[reported]` — vendor's own figure, treat as a ceiling not a baseline.
- **Nova Credit NovaScore Cash Flow**, plus PayPal adopting Nova Credit's Cash Atlas
  (Sept 2025) `[reported]` — evidence that large payment companies are underwriting from
  transaction data directly.
- Other cash-flow data providers: Ocrolus, MeridianLink, eNoah `[reported]`. Plaid also
  ships income verification via payroll connections and a credit risk signal, LendScore
  `[reported]`.

For a neobank the punchline is: **you already have the data these products sell.** Your own
account holders' inflows and outflows are a better cash-flow signal than a permissioned
third-party pull. The decision is whether to build the score or buy one for regulatory
cover and cross-portfolio comparability.

## Architecture

```
application
  → bureau pull (hard/soft)            ← cache, cost per pull matters
  → open banking / internal txn history ← the differentiator
  → feature engineering (shared with fincrime feature store)
  → scorecard / ML model ensemble
  → policy rules layer (hard cuts, regulatory, affordability)
  → limit & pricing engine
  → adverse-action reason generation
  → decision log (immutable, model-versioned)
```

Two design rules that matter more than the model:

1. **Separate the model from the policy.** Models produce a probability; policy produces a
   decision. Keep hard cuts, regulatory constraints and affordability rules in a separately
   versioned, human-readable policy layer. Regulators, and your own risk team, will change
   policy far more often than models.
2. **Share the feature store with fincrime.** Transaction velocity, income stability, and
   balance volatility are the same features in both domains. Monzo explicitly runs feature
   management and versioning as shared ML platform capability `[confirmed]`. Two feature
   pipelines computing "average monthly inflow" differently is a real and common bug.

## What Monzo does

Credit decisioning is one of Monzo's five stated ML priorities: credit-risk prediction,
utilisation forecasting, and product propensity, with recent effort going into "stronger
feature representations" and modern algorithms `[confirmed]`. Notably, Monzo's fincrime work
uses **self-supervised embeddings of customer and transaction behaviour** and multi-task
deep learning `[confirmed]` — the same representation-learning approach transfers directly
to credit, which is precisely the foundation-model-for-banking-events thesis.

Upstart is the pure-play datapoint for whether ML underwriting scales commercially: Q1 2026
originations +61% YoY on revenue of ~$308m `[reported]`.

## Open questions

- Does anyone publish a like-for-like lift comparison of internal-transaction-data models
  versus bureau-only, at a neobank, with a proper out-of-time sample?
- How are firms generating ECOA-compliant reason codes from deep models — SHAP-based,
  surrogate scorecards, or constrained architectures?
- What did §1033's April 2026 deadline actually change in practice for aggregator pricing?

## Sources

- FICO, cash-flow UltraFICO with Plaid — https://www.fico.com/en/newsroom/fico-partners-plaid-launch-next-generation-cash-flow-ultrafico-score
- American Banker, FICO upgrades cash-flow score — https://www.americanbanker.com/news/fico-upgrades-its-cashflow-powered-score-with-real-time-data
- Nova Credit, NovaScore Cash Flow — https://www.novacredit.com/corporate-blog/introducing-the-novascore-cash-flow-the-future-of-consumer-credit-risk
- Plaid, alternative credit data — https://plaid.com/resources/lending/alternative-credit-data/
- Celent, cash flow data and credit scoring — https://www.celent.com/en/insights/insight-49
- Oscilar, credit scoring for fintechs — https://oscilar.com/blog/credit-scoring-guide
- Monzo, Machine Learning at Monzo in 2025 — https://monzo.com/blog/machine-learning-at-monzo-in-2025
- Cobalt Intelligence, top alternative credit data providers — https://blog.cobaltintelligence.com/post/top-10-alternative-credit-data-providers-in-the-united-states
