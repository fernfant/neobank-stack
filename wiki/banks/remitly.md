---
title: Remitly (USA / cross-border)
type: bank
status: living
updated: 2026-08-18
sources: 4
tags: [usa, cross-border, remittance, aurora, kafka]
---

## Summary

Not a neobank, but the best public example of the **money-movement layer** done at scale
across dozens of corridors. Polyglot JVM+Go microservices on AWS, Aurora for financial data,
Kafka+Snowflake for the data platform, and a payout network assembled from direct integrations
with banks, MTOs and cash-payout agents.

## Stack

| Layer | Choice | Confidence |
| --- | --- | --- |
| Language | Java, Kotlin, Go | `[reported]` |
| Frontend | React web; Swift iOS; **Kotlin Multiplatform** | `[reported]` |
| Cloud | AWS | `[reported]` |
| Datastore | PostgreSQL and **Amazon Aurora** — migrated from RDS MySQL | `[reported]` |
| Data platform | Apache Kafka + Snowflake | `[reported]` |
| Payout | Direct API integrations with banks, MTOs, payout agents per corridor | `[reported]` |
| Risk | ML models monitoring transaction patterns in real time for fraud and AML | `[reported]` |

## What's architecturally interesting

**A transfer is a long-lived state machine, not a transaction.** Funding, compliance screening,
FX, payout submission, and payout confirmation are separate stages that can each fail, retry,
or hang for days. This is the opposite of a card authorisation and demands a completely
different design: durable workflow state, per-corridor cut-off awareness, and a reversal path
at every stage.

**Corridor asymmetry is the dominant complexity.** Each destination has its own partners,
payout methods (bank deposit, cash pickup, mobile wallet, home delivery), cut-off times and
failure modes. The architecture that survives is one where a corridor is configuration plus an
adapter, not a code branch.

**FX is a position, not a price lookup.** Quoting a rate to a customer creates exposure between
quote and settlement. Rate sourcing, spread, hedging and the ledger treatment of FX gain/loss
are core, not peripheral.

**Kotlin Multiplatform** for shared mobile logic is unusual at this scale and worth noting —
it suggests business logic (fee calculation, quote display) that must be identical across
platforms and is expensive to duplicate.

## Relevance to a neobank

Any neobank offering international transfers inherits all of the above. Most underestimate it
and try to model a cross-border payout as a slow domestic payment. It is not — see the state
machine section of [Payment rails and money movement](../layers/03-payment-rails.md).

Stablecoin rails (Bridge, BVNK, Stripe's Stablecoin Financial Accounts) are being adopted
precisely for corridors where dollar bank rails are slow, expensive or absent `[reported]`.

## Open questions

- How is the payout partner network abstracted — a routing engine with cost/speed/reliability
  scoring, or corridor-specific code?
- Does Remitly hold a ledger of record separate from the payout partners' records, and at what
  reconciliation frequency?
- Has Remitly adopted stablecoin settlement for any corridor?

## Sources

- TEKsystems, Remitly Amazon Aurora migration — https://www.teksystems.com/en/insights/success-stories/remitly-amazon-aurora
- Remitly careers, Senior Full Stack SDE — https://careers.remitly.com/job/23353363/senior-full-stack-software-development-engineer-seattle-wa/
- StackShare, Remitly — https://stackshare.io/companies/remitly/blog
- AWS Architecture Blog, modernization of real-time payment orchestration — https://aws.amazon.com/blogs/architecture/modernization-of-real-time-payment-orchestration-on-aws/
