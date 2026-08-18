---
title: Build vs buy, layer by layer
type: comparison
status: living
updated: 2026-08-18
sources: 8
tags: [strategy, build-vs-buy]
---

## Summary

A default recommendation per layer, with the trigger that should make you change your mind.
The general principle: **buy anything whose correctness is defined by someone else (lists,
documents, schemes); build anything whose iteration speed is your loss rate or your margin.**

| Layer | Default | Build when | Never build |
| --- | --- | --- | --- |
| Licence | Depends on ambition | You need deposit funding or independence from a sponsor | — |
| **Core ledger** | **Buy** (Vault / 10x / Temenos) at MVP | Ledger economics or product velocity is the moat *and* you can fund a permanent team | If you cannot staff 24/7 money on-call |
| Reconciliation | **Build** — always | Always. Nobody sells your break taxonomy | — · [Deep dive — Reconciliation (build)](../deep-dives/01-reconciliation.md) |
| Payment rails adapters | Buy access (agency/PaaS), build the adapter layer | Always build the normalisation layer | Scheme connectivity itself, initially · [Deep dive — Rail adapters (buy access, build normalisation)](../deep-dives/02-rail-adapters.md) |
| **Card issuing** | **Buy** | Volume makes processor fees the top cost line, or the release train gates product (Chime's case) | Scheme certification, if you can avoid it |
| KYC document/data | **Buy** | Never — this is commodity data | Document forensics |
| KYC **orchestration** | **Build** (or Alloy) once you have >1 country or >1 product | The first vendor outage that stops onboarding | — · [Deep dive — KYC orchestration (build)](../deep-dives/03-kyc-orchestration.md) |
| Sanctions/PEP screening | **Buy** | Never | The list itself |
| Case management, SAR filing | **Buy** | Never — it is workflow software | — |
| **Fraud/AML detection** | Buy to launch, build to win | Fraud is material to P&L; UK APP liability applies | — · [Deep dive — Fraud and AML detection (build)](../deep-dives/04-fraud-aml.md) |
| Credit scoring | Buy a bureau score, build the overlay | You have transaction data the bureau doesn't (i.e. you are a neobank) | Bureau data itself |
| Feature store | Buy or OSS (Tecton/Feast) | Latency in the auth path forces custom | — |
| Data warehouse | **Buy** (BigQuery/Snowflake) | Never | — |
| Customer ops automation | Build on bought models | It touches money movement and needs your evidence plane | Foundation models |

## The three triggers to re-open a "buy" decision

1. **The vendor fee becomes your largest cost-to-serve line.** Chime's threshold. Below a few
   million cards, buying wins; above it, the arithmetic flips.
2. **The vendor's release train becomes your roadmap.** If a product change takes two quarters
   because it needs a vendor change, you have already lost the velocity argument.
3. **The vendor becomes a competitor or a regulatory risk.** Galileo is owned by SoFi. Synapse
   went bankrupt with customer funds unreconciled. Concentration risk is now a documented
   regulatory requirement (DORA Art. 28/29), not a philosophical concern.

## The one thing to build first, regardless

**Reconciliation.** It is the only subsystem that both UK and US regulators independently
converged on mandating (daily safeguarding reconciliation under FCA PS25/12; near-real-time
partner-account reconciliation in the FDIC's proposed rule), it is what failed at Synapse, and
no vendor can build it for you because it encodes your specific relationships between your
ledger, your rails and your partners.

## Deep dives

Each of the four **build** rows above has a dedicated page with real implementations, named
open-source packages and the vendors you still buy: [Deep dive — Reconciliation (build)](../deep-dives/01-reconciliation.md),
[Deep dive — Rail adapters (buy access, build normalisation)](../deep-dives/02-rail-adapters.md), [Deep dive — KYC orchestration (build)](../deep-dives/03-kyc-orchestration.md), [Deep dive — Fraud and AML detection (build)](../deep-dives/04-fraud-aml.md).

## Sources

- Formance, core banking reference model and build sequence — https://www.formance.com/blog/financial-operations/core-banking-system-architecture
- Finantrix, how to build a neobank technology stack — https://www.finantrix.com/articles/how-to-build-a-neobank-technology-stack-core-ledger-cards-compliance
- Trio, neobank architecture guide — https://trio.dev/neobank-architecture-guide/
- SiliconANGLE, Chime and ChimeCore — https://siliconangle.com/2025/06/02/financial-technology-company-chime-seeking-11-2b-valuation-upcoming-ipo/
- Thought Machine × Zopa — https://www.thoughtmachine.net/press-releases/zopa-bank
- ClearBank, FCA PS25/12 — https://clear.bank/learn/insights/the-fcas-safeguarding-overhaul-the-new-rules-their-impact-and-how-to-prepare
- Yale Journal of International Affairs, Synapse — https://www.yalejournal.org/publications/the-synapse-collapse
- Regulation-DORA, concentration risk and exit — https://www.regulation-dora.eu/blog/cloud-exit-strategy-concentration-risk-dora
