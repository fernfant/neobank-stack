---
title: The ten-layer map
type: layer
status: living
updated: 2026-08-18
sources: 6
tags: [architecture, reference-model]
---

## Summary

Ten strata. Read top-to-bottom as request flow, bottom-to-top as dependency. Each has its
own page; each page answers *what the options are*, *what the trade-off is*, and *what the
choice forces downstream*.

| # | Layer | The question it answers | Page |
| --- | --- | --- | --- |
| 1 | Licence / charter | Whose balance sheet holds the money? | [Licence and charter — whose balance sheet?](../layers/01-licence-and-charter.md) |
| 2 | Core ledger & product engine | What is the system of record for a balance? | [Core ledger and product engine](../layers/02-core-ledger.md) |
| 3 | Payment rails & money movement | How does value actually leave the building? | [Payment rails and money movement](../layers/03-payment-rails.md) |
| 4 | Card issuing & processing | Who says yes to a tap in 200ms? | [Card issuing and processing](../layers/04-card-issuing.md) |
| 5 | Identity & onboarding (KYC/KYB) | How do you know who this is? | [Identity and onboarding (KYC / KYB)](../layers/05-kyc-onboarding.md) |
| 6 | Financial crime (AML/TM/fraud) | How do you stop bad money and bad actors? | [Financial crime — AML, transaction monitoring, fraud](../layers/06-fincrime.md) |
| 7 | Credit & decisioning | Who gets lent money, how much, at what price? | [Credit and decisioning](../layers/07-credit-scoring.md) |
| 8 | Data & ML platform | How do signals get from events to decisions? | [Data and ML platform](../layers/08-data-ml-platform.md) |
| 9 | Runtime & infrastructure | What does it all run on? | [Runtime and infrastructure](../layers/09-infrastructure-runtime.md) |
| 10 | Resilience, regulatory & ops | How do you prove it works, to a regulator? | [Resilience, regulatory reporting and operations](../layers/10-resilience-regulatory.md) |

## Two orthogonal planes

The ten layers are the *vertical* stack. Two things cut horizontally across all of them and
are the usual source of architectural pain:

**The reconciliation plane.** Every layer holds a version of "how much money is there" — the
scheme, the sponsor bank, the processor, your ledger, your data warehouse. Reconciliation is
the machinery that keeps those agreeing. Synapse failed here `[reported]`; FCA PS25/12 now
mandates daily reconciliation for UK EMIs `[confirmed]`; the FDIC's proposed rule pushes
near-real-time reconciliation onto US sponsor banks `[confirmed]`. Treat reconciliation as a
first-class subsystem with its own team, not as a nightly batch job someone owns part-time.

**The evidence plane.** Regulators do not ask "does it work", they ask "show me it worked on
14 March at 09:12". That means bi-temporal records (transaction time *and* effective date),
append-only postings, immutable decision logs for every risk control, and the ability to
reconstruct a historical balance or a historical model decision without rewriting anything
`[reported]`. Monzo stores per-control-execution metadata — input features, decision, control
version — in BigQuery precisely for this `[confirmed]`.

Design both planes on day one. Retrofitting either is a rewrite.

## Sources

- Formance, core banking reference model — https://www.formance.com/blog/financial-operations/core-banking-system-architecture
- Trio, neobank architecture guide — https://trio.dev/neobank-architecture-guide/
- Crassula, digital banking architecture 2026 — https://crassula.io/guides/banking-architecture/
- InfoQ on Monzo real-time fraud detection — https://www.infoq.com/news/2025/11/monzo-real-time-fraud-detection/
- ClearBank on FCA PS25/12 — https://clear.bank/learn/insights/the-fcas-safeguarding-overhaul-the-new-rules-their-impact-and-how-to-prepare
- National Law Review, BaaS liability allocation — https://natlawreview.com/article/who-owns-compliance-failure-bank-fintech-liability-allocation-banking-service-baas
