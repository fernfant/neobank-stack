---
title: Overview — how a neobank is built in 2026
type: overview
status: living
updated: 2026-08-18
sources: 24
tags: [architecture, uk, usa, thesis]
---

## Summary

A neobank is not one system. It is a **thin, fast product layer over a slow, regulated
money layer**, and almost every interesting engineering decision is about where you draw
the line between them. The layer map in [The ten-layer map](layers/00-layer-map.md) has ten strata; a founding
team really only makes four big decisions — *licence*, *ledger*, *card processor*,
*fincrime posture* — and the rest follows from those.

## The four decisions everything else hangs off

**1. What are you licensed as?** This is an architecture decision disguised as a legal one.
A UK bank licence (PRA-authorised deposit taker) means you hold the deposits, you settle
into your own Bank of England account, and you own the ledger of record. An EMI means you
safeguard funds in a trust account at a partner and your "balance" is a claim, not a
deposit. In the USA a national bank charter versus a sponsor-bank arrangement is the same
fork. See [Licence and charter — whose balance sheet?](layers/01-licence-and-charter.md).

**2. Do you own the ledger?** The single most consequential build-vs-buy call. Monzo and
Chime built theirs; Varo bought Temenos; Chase UK bought 10x; Zopa bought Thought Machine
Vault. Owning it means owning correctness, reconciliation and 24/7 on-call for money. Not
owning it means your product roadmap is throttled by someone else's release train. See
[Core ledger and product engine](layers/02-core-ledger.md).

**3. Who authorises your card transactions?** The issuer-processor sits in the hot path of
every tap, with a hard latency budget and a 100% availability expectation. Chime's whole
public efficiency story is that it moved this in-house (ChimeCore) `[confirmed]`. See
[Card issuing and processing](layers/04-card-issuing.md).

**4. Is financial crime a vendor or a platform?** Buying ComplyAdvantage or Unit21 gets you
live in weeks. Building — Monzo's Starlark-based control engine, Revolut's real-time
pipelines — gets you a rate of iteration vendors cannot match, at the cost of a permanent
platform team. See [Financial crime — AML, transaction monitoring, fraud](layers/06-fincrime.md).

## The observed pattern: three archetypes

### Archetype A — "Full-stack bank" (Monzo, Starling, Revolut, Chime)

Own licence (or, for Chime, own processor without a charter). Own ledger. Own fincrime
platform. Buy only the commodity edges: identity documents, sanctions lists, bureau data.

The stack looks like: Go or Java/Kotlin microservices on Kubernetes, an in-house
double-entry ledger over a horizontally-scalable store (Cassandra at Monzo `[confirmed]`,
Postgres event store at Revolut `[reported]`), direct scheme membership on the payment
rails, and a streaming data platform feeding real-time risk models.

The cost is enormous: Monzo runs ~1,600–2,800 microservices `[reported]` and had to build
its own RPC framework, its own deployment tooling, and a bespoke Cassandra operations
practice to get there.

### Archetype B — "Platform tenant" (Zopa, Chase UK, Varo, Atom)

Own licence, **bought core**. Thought Machine Vault, 10x SuperCore, or Temenos Transact
runs the ledger and product engine; the bank builds the experience layer, the risk models,
and the integration fabric. Zopa launched a beta current account on Vault in ~10 months
`[confirmed]`.

This is now the mainstream choice for licensed challengers. The product-definition language
becomes a lock-in axis: Vault's Python-flavoured Smart Contracts versus 10x's polyglot
runtime is a genuine architectural fork, not a feature checkbox `[reported]`.

### Archetype C — "Fintech over a sponsor bank" (Current, Dave, most US neobanks)

No charter. A sponsor bank holds the deposits; a BaaS/processor (Galileo, Marqeta, Lithic,
Unit) supplies the ledger and card rails. Fastest to market, thinnest moat, and — since
Synapse — the riskiest posture with regulators. The FDIC's proposed recordkeeping rule
(informally "the Synapse rule") pushes **near-real-time reconciliation of every fintech
partner account** into the requirements `[confirmed]`, which turns a business-model choice
into an engineering mandate. See [Licence and charter — whose balance sheet?](layers/01-licence-and-charter.md).

## What changed in 2025–2026

- **Vertical integration is back.** Chime built ChimeCore and moved 100% of credit-card
  transaction processing onto it from late 2024, citing lower maintenance cost and less
  third-party dependence `[confirmed]`. SoFi owns Galileo *and* Technisys/Cyberbank Core,
  and sells the stack to competitors `[confirmed]`.
- **The BaaS middle got squeezed.** Seven US sponsor banks took consent orders between 2022
  and 2025 `[reported]`; the middleware ledger was the single point of failure at Synapse
  `[reported]`. "BaaS" as a word is out of favour; the surviving pattern is direct
  fintech↔bank with the bank holding a real-time reconciled ledger.
- **Agentic AI moved into ops, not just chat.** Monzo's Ops Agent executes end-to-end
  operational workflows across 150+ customer intents, from Pot management to fraud
  investigation `[confirmed]`. This is the first ML use case in a neobank to touch money
  movement operationally rather than advisorily.
- **Cash-flow underwriting went mainstream.** FICO + Plaid shipped a cash-flow UltraFICO in
  Nov 2025; Experian's Credit + Cashflow Score claims >40% predictive lift `[reported]`.
  CFPB §1033 standardised APIs land April 2026 `[reported]`. For a neobank this means the
  transaction data you already hold is now a *scoring* asset, not just a feature source.
- **UK safeguarding got hard.** FCA PS25/12 takes effect 7 May 2026: mandatory **daily**
  reconciliations, monthly returns, annual audits, 48-hour resolution packs `[confirmed]`.
  That is a data-engineering requirement, not a policy document.
- **Stablecoins became a rail, not a product.** GENIUS Act signed July 2025, effective Jan
  2027; Stripe bought Bridge for $1.1bn; Mastercard bought BVNK `[reported]`. Relevant to
  cross-border neobanks (Remitly-shaped problems) far more than to domestic current accounts.

## The uncomfortable truths

- **Public information decays fast and vendors market hard.** Much of what is written about
  neobank stacks is 2019–2022 conference material or SEO listicles. Everything here carries
  a confidence tag for that reason; see the tagging rules in `CLAUDE.md`.
- **Nobody publishes their ledger schema.** The ledger is the most important component and
  the least documented. What is public is the *shape* (double-entry, append-only, balances
  derived from postings, idempotent writes) and almost never the implementation.
- **Cost-to-serve is the real scoreboard.** Chime's claim is a cost-to-serve roughly a third
  of a large bank's, attributed to owning the processor `[reported]`. Architecture arguments
  in this space should be settled in cost-per-active-account, not in elegance.

## Sources

- Monzo engineering blog — https://monzo.com/blog/topic/technology
- InfoQ, "Monzo's Real-Time Fraud Detection Architecture with BigQuery and Microservices" (Nov 2025) — https://www.infoq.com/news/2025/11/monzo-real-time-fraud-detection/
- InfoQ, "Modern Banking in 1500 Microservices" — https://www.infoq.com/presentations/monzo-microservices/
- Chime S-1 coverage, Banking Dive — https://www.bankingdive.com/news/chime-files-for-ipo-sec-nasdaq-chym/748152/
- Galileo/SoFi, Cyberbank Core — https://www.galileo-ft.com/news/sofi-to-adopt-galileos-cyberbank-core-for-commercial-payment-services-and-sponsor-banking/
- Thought Machine × Zopa — https://www.thoughtmachine.net/press-releases/zopa-bank
- 10x Banking, core platforms compared — https://www.10xbanking.com/core-banking-platforms-compared
- Formance, core banking reference model — https://www.formance.com/blog/financial-operations/core-banking-system-architecture
- Yale Journal of International Affairs on Synapse — https://www.yalejournal.org/publications/the-synapse-collapse
- ClearBank on FCA safeguarding overhaul (PS25/12) — https://clear.bank/learn/insights/the-fcas-safeguarding-overhaul-the-new-rules-their-impact-and-how-to-prepare
- FICO × Plaid cash-flow UltraFICO — https://www.fico.com/en/newsroom/fico-partners-plaid-launch-next-generation-cash-flow-ultrafico-score
- Forbes, stablecoin cross-border payments 2026 — https://www.forbes.com/sites/danielwebber/2026/03/30/stablecoin-cross-border-payments-in-2026-from-theory-to-practice/
