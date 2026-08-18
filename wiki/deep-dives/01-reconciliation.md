---
title: Deep dive — Reconciliation (build)
type: deep-dive
status: living
updated: 2026-08-18
sources: 9
tags: [reconciliation, build, ledger, uber, formance]
---

## Summary

Reconciliation is the only layer in the stack where the default is **build, with no trigger to
reconsider**. Not because vendors are bad — Duco, AutoRek, SmartStream and Gresham are mature
products — but because what they sell is a *matching engine*, and the hard part is not matching.
The hard part is the **break taxonomy**: the classification of *why* two records disagree, which
is specific to your rails, your partners and your product, and which is the thing an examiner
actually asks about.

You buy the engine. You build the taxonomy, the enrichment, and the break lifecycle.

## Real implementation: Uber's settlement accounting

The most detailed public architecture in this space `[confirmed]`. Three services:

| Service | Job |
| --- | --- |
| **File Ingestion Service** | Pulls settlement files from **50+ PSPs** over SFTP, API and blob store; normalises wildly different formats into a single `PSPEvent` object (amount, currency, transaction date) |
| **Feed Processor Service** | Processes normalised events in parallel splits, calls reconciliation for matching, routes failures to a **dead-letter queue** for retry, forwards enriched events to the accounting engine |
| **Reconciliation & Accounting Service** | Matches `PSPEvent` against internal payment-platform records on a deterministic `transactionReference`, enriches matches from **15 upstream sources**, applies accounting rules, emits transaction models |

Scale: **1.2 billion settlements a month**, roughly **$130bn of cash a year**, reconciliation
landing about **T+7** after the transaction. Kafka carries events in and validated transactions
out `[confirmed]`.

Three things to steal:

1. **Normalisation is a separate service from matching.** Uber's ingestion layer exists purely
   to turn 50 vendor formats into one internal type. That boundary is what stops PSP-specific
   quirks leaking into accounting logic — the same argument as [Deep dive — Rail adapters (buy access, build normalisation)](../deep-dives/02-rail-adapters.md).
2. **A balancing identity as the control.** `Settlements − Deductions = Payout`. One equation
   that must hold; anything that violates it is an investigation. Define yours explicitly.
3. **Failed reconciliation is a queue, not an exception.** The DLQ-and-retry shape acknowledges
   that most breaks are timing, and timing resolves itself if you let it.

Airbnb operates the comparable problem at **191 countries, 70+ currencies, 20+ processors**
`[reported]` — the same shape, different constants.

## The seven matching patterns

Formance's published reference is the clearest public taxonomy `[confirmed]` — vendor-authored,
but technical enough to check. Execute them as a **rule chain in this order**, cheapest first:

| # | Pattern | Where it applies |
| --- | --- | --- |
| 1 | **1:1** — exact match on ID, amount, posting date | Wires, single invoice payments with stable references |
| 2 | **N:1** — group internal records by batch key; sum equals one external credit | Card network net settlement |
| 3 | **1:N** — sum of external records equals one internal amount within tolerance | Partial payments, instalments |
| 4 | **N:M** — bounded subset-sum search | B2B netting, cross-currency. Expensive — invoke only after 1–3 exhaust |
| 5 | **Time-window** — timestamp tolerance **defined per rail** | Auth/capture/settle lifecycles, timezone cut-offs |
| 6 | **Balance-level** — internal balance sum equals external reported balance at a point in time | Omnibus accounts, **safeguarding** |
| 7 | **Exception** — residual unmatched after the chain | Everything left |

Pattern 6 is the one UK EMIs are now legally required to run daily under FCA PS25/12, and
pattern 4 is the one that will take your compute budget if you let it run unbounded.

## Break taxonomy — the thing you cannot buy

Formance's three top-level classes are the right starting skeleton `[reported]`:

- **Data quality** — malformed, truncated, encoding, missing fields
- **Identifier** — reference missing, mismatched, reused, or the counterparty rewrote it
- **Timing** — real difference now, expected to resolve; the largest category by count

Underneath those, the useful taxonomy is yours and is rail-specific. A worked example of the
level of granularity that actually helps an ops team:

```
timing/
  timing.settlement-lag            expected, auto-close after N days
  timing.cutoff-crossed            posted after rail cut-off
  timing.auth-capture-gap          card lifecycle, not a break
identifier/
  identifier.reference-rewritten   counterparty replaced our reference
  identifier.duplicate-key         same idempotency key, two postings  ← urgent
amount/
  amount.fx-rounding               within tolerance, auto-close
  amount.fee-undisclosed           PSP deducted a fee we did not model  ← revenue leak
  amount.partial-settlement        expect a sibling record
missing/
  missing.internal                 external has it, we do not  ← money we cannot explain
  missing.external                 we have it, rail does not   ← money in flight or lost
```

`missing.internal` and `identifier.duplicate-key` are the two that end companies. Everything
else is operations.

## What "build" actually means — the component list

1. **Ingestion adapters**, one per source, producing a canonical settlement event. Shared with
   [Deep dive — Rail adapters (buy access, build normalisation)](../deep-dives/02-rail-adapters.md).
2. **A matching rule chain**, ordered cheapest-first, configurable per rail, with per-rail
   tolerances (amount and time) as data, not code.
3. **Stateless, replayable workers.** Rerunning a past day must reproduce that day's answer.
   This is the property that makes the output evidence rather than an opinion.
4. **Bi-temporal storage.** Record both occurrence time and recording time. Formance's example:
   a webhook arriving 2 April with an effective date of 31 March is *recorded* on 2 April and
   *counted* in the 31 March balance `[confirmed]` — without this, in-flight settlement looks
   identical to missing money. Query shape: `GET /accounts/{path}?pit=2026-03-31T23:59:59Z`.
5. **Hierarchical account paths** — `@psp:stripe:fees:markup`, `@merchant:acme:receivable` —
   so you can aggregate by any prefix without rewriting matching rules per provider `[confirmed]`.
6. **A break register**: owner, age, amount, class, and an **aging report**. Unaged breaks are
   how shortfalls hide.
7. **Enrichment**, joining the matched pair to whatever context the investigator needs. Uber
   pulls from 15 sources for this `[confirmed]`.

## Software to build on

| Package | What it gives you | Licence |
| --- | --- | --- |
| **TigerBeetle** | Purpose-built double-entry financial DB; accounts and transfers are the schema | Apache 2.0 |
| **Formance Ledger** | Double-entry core, Numscript atomic multi-party transactions, plus separate Connectivity / Reconciliation / Flows modules; commonly deployed as a **sidecar** next to an existing core | Open source core |
| **Blnk** | Open-source double-entry ledger core | Open source |
| **Temporal** | Durable execution for the long-running, retry-heavy parts. Stripe standardised on it for payment workflows; Coinbase used it to delete a homegrown SAGA implementation | MIT |
| **Modern Treasury Ledgers** | Immutable double-entry ledger as an API, with reconciliation; sub-account reconciliation is their stated core problem | Commercial |
| **Fragment** | Ledger API aimed at engineers | Commercial |

The **idempotency trap** is worth stating explicitly, because it is the most common way a
correct-looking system produces a phantom: *a retried payout that reuses the same idempotency
key books the same transfer twice* `[confirmed]`. The defence is atomic multi-party posting —
either the whole transaction lands or none of it does — not application-level checks.

## Vendors you might still buy (and who they are actually for)

| Vendor | Built for |
| --- | --- |
| **Duco** | Cloud-native, self-service config so ops can build reconciliations without IT. Capital markets, prime brokerage, asset management `[reported]` |
| **AutoRek** | Strong UK financial-services presence; regulated reporting `[reported]` |
| **SmartStream TLM** | Large institutions; cash, securities, settlements, treasury confirmations, transaction lifecycle control `[reported]` |
| **Gresham Clareti** | Complex reconciliation at bank scale `[reported]` |
| **BlackLine, Broadridge, Osfin, Kosh** | Enterprise finance close, more accounting than payments `[reported]` |

Read the pattern: these are **capital-markets and enterprise-finance** tools. They are excellent
at securities and cash reconciliation and were not designed for a neobank reconciling a card
processor, three rails, a sponsor bank and a safeguarding account against one product ledger,
daily, with regulator-facing output. That mismatch — not price — is the real reason neobanks
build.

## Open questions

- Does any neobank publish its break taxonomy or aging metrics? Nobody found so far.
- What is a realistic auto-match rate by rail (cards vs ACH vs FPS) at a mature neobank?
- Has anyone run Formance or TigerBeetle as a reconciliation sidecar next to Vault or SuperCore
  in production, and what did the integration cost?
- What does the FDIC's final rule text define as "near real-time"? (Still the P1 question.)

## Sources

- Uber, Streamlining Financial Precision: Uber's Advanced Settlement Accounting System — https://www.uber.com/us/en/blog/ubers-advanced-settlement-accounting-system/
- Formance, Account Reconciliation Patterns for High-Volume Fintech — https://www.formance.com/blog/financial-operations/account-reconciliation-patterns-for-high-volume-fintech
- Formance, core banking system architecture — https://www.formance.com/blog/financial-operations/core-banking-system-architecture
- Airbnb Tech Blog, Tracking the money — scaling financial reporting at Airbnb — https://medium.com/airbnb-engineering/tracking-the-money-scaling-financial-reporting-at-airbnb-6d742b80f040
- Gresham, best reconciliation software for financial institutions 2026 — https://www.greshamtech.com/blog/best-reconciliation-software-for-financial-institutions-in-2026
- Osfin, enterprise reconciliation software — https://www.osfin.ai/blog/enterprise-reconciliation-software
- Modern Treasury, Announcing Ledgers — https://www.moderntreasury.com/journal/announcing-ledgers
- Modern Treasury, Spring 2026 product release — https://www.moderntreasury.com/journal/spring-product-release-recap
- Temporal, durable execution — https://temporal.io/
