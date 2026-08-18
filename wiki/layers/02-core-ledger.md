---
title: Core ledger and product engine
type: layer
status: living
updated: 2026-08-18
sources: 10
tags: [ledger, core-banking, build-vs-buy]
---

## Summary

The ledger is the system of record for "how much money is there". Everything else in the
bank is, in a sense, a cache of it. Four invariants define a correct one; the build-vs-buy
decision is about who is on the hook for maintaining them at 3am.

## The four invariants

Any ledger — bought, built, or borrowed — must enforce these, and enforce them **at the
storage layer, not in application code** `[reported]`:

1. **Sum-to-zero.** Every transaction balances debits and credits. Money is never created
   or destroyed by a write.
2. **Postings are the truth; balances are derived.** Never store a balance as an
   independently-mutable field. Monzo's balance is computed from the ledger's double-entry
   postings `[reported]`.
3. **Append-only.** You never edit or delete a posting. Corrections are offsetting entries
   `[reported]`. This is what makes the evidence plane possible.
4. **Idempotent writes.** Explicit deduplication keys, because every upstream rail will
   deliver you the same event twice eventually.

Add two more that bite in practice:

5. **Bi-temporality.** Record both transaction time and effective date so you can
   reconstruct "what did we believe the balance was, as of then" — required for DORA-style
   logging and MiCA-style reporting `[reported]`, and for any dispute.
6. **Hierarchical account paths.** `user:1234:gbp:available` / `:pending` / `:safeguarded`.
   Flat account IDs stop scaling the moment you add pots, holds, or multi-currency.

## The options

### Build it yourself

**Who:** Monzo (Go microservices, Cassandra `[confirmed]`), Revolut (event-driven services
over a Postgres event store `[reported]`), Chime (ChimeCore, from late 2024 handling 100% of
credit-card transactions `[confirmed]`), Block (a dedicated Ledgering team maintaining the
accounting core for Square and Cash App `[confirmed]`).

**When it's right:** you have a charter, you expect the ledger to be a competitive
advantage (cost-to-serve, product velocity), and you can fund a permanent team. Chime's
public claim is a cost-to-serve roughly one third of a large bank's, attributed to owning
the processor and core `[reported]`.

**What it costs:** "Building a correct double-entry ledger from scratch can take many
months of engineering effort; budget accordingly, or don't build one" `[reported]`. In
practice, more — the ledger is the easy part; reconciliation, migration, and 24/7
operations are the hard parts.

### Buy a core banking platform

| Platform | Shape | Known users | The lock-in axis |
| --- | --- | --- | --- |
| **Thought Machine Vault Core** | Cloud-native, event-driven, Universal Product Engine | Lloyds, Standard Chartered, Intesa Sanpaolo, Atom, Zopa, Trust Bank `[reported]` | Products defined in **Smart Contracts**, a proprietary Python-flavoured language `[reported]` |
| **10x SuperCore** | Cloud-native, tier-one oriented, built-in migration tooling | Chase UK, Westpac `[reported]` | Polyglot runtime — no contract-language lock-in, vendor's own claim `[reported]` |
| **Temenos Transact** | Most widely deployed core; cloud-hosted option | Varo `[confirmed]`, ~950 banks `[reported]` | Breadth and incumbency; less "cloud-native by construction" |
| **Mambu** | SaaS core, strong in consumer/SME lending, composable | N26, ABN AMRO `[reported]` | Composability pushes complexity into your integration layer; weak migration tooling for legacy books `[reported]` |
| **Galileo Cyberbank Core** (ex-Technisys) | Cloud core + issuing + sponsor banking in one vendor | SoFi `[confirmed]` | Vendor is also a competitor to many of its customers |
| **Tuum**, **Finxact/Fiserv**, **SDK.finance**, **Skaleet** | Modular API cores | European fintechs; Finxact US-first real-time `[reported]` | Smaller ecosystems |

**When it's right:** you have a licence and want to spend your engineering on the product
and the risk models, not on postings. Zopa launched a beta current account on Vault in
September 2024 and went full-launch June 2025 `[confirmed]` — that is the speed argument in
one data point.

### Use a purpose-built ledger database or LaaS

| Option | Shape |
| --- | --- |
| **TigerBeetle** | Purpose-built financial DB; double-entry accounts/transfers are the schema, not a convention. Claims ~1,000× throughput of general-purpose DBs `[reported]`. Lowest-level option — you build everything around it |
| **Formance Ledger** | Open-source double-entry core; product logic expressed as Numscript transactions. Commonly deployed as a **sidecar ledger** alongside an existing core `[reported]` |
| **Blnk** | Open-source double-entry ledger core `[reported]` |
| **Ledger-as-a-Service** (various) | Managed API ledger; fastest, least control |

The sidecar pattern deserves attention: keep the bought core as the regulated system of
record, and run a purpose-built ledger next to it for the product features the core cannot
express fast enough. It defers the migration question without forking the truth — provided
you have a hard rule about which one is authoritative.

## The read-amplification problem — and the fix

Invariant 2 says *postings are the truth; balances are derived*. That is correct, and it has a
consequence nobody warns you about: **balance read cost grows with account age.** Monzo's April
2023 post is the only public account of hitting this wall and engineering out of it `[confirmed]`.

**The model.** Monzo's ledger addresses are a **5-tuple**: legal entity, namespace, name, currency,
account ID. Entries are grouped by address. Computing a balance means reading *every entry in the
address group* and summing them.

**The wall.** By 2022 that was P99 **400–500ms** and climbing with the customer base. Monzo
segmented users into four categories by ledger entry count, because the distribution — not the
average — is what breaks you.

**Why it was urgent, and this is the part to internalise.** During card authorisation, if the
balance read is too slow, **the card scheme triggers its own stand-in processing without waiting
for Monzo's answer**. The scheme then approves on the issuer's behalf, which can authorise
payments beyond available balance and means the issuer's fraud checks never ran at all. A slow
ledger read does not degrade gracefully into a decline — it silently hands your authorisation
decision to Mastercard. See [Card issuing and processing](../layers/04-card-issuing.md).

**The fix, in two parts:**

1. **Pre-computed balance blocks.** Group consecutive ledger entries into blocks, store the
   aggregated sums in a separate table keyed by balance name, and only maintain this for
   frequently-read names such as `customer-facing-balance`. A running balance maintained forward,
   rather than a sum computed backward.
2. **Time-series reindexing.** Reindex entries in Cassandra partitioned by committed timestamp
   combined with the address columns, so reads can filter by time and read partially rather than
   scanning the whole group.

Monzo explicitly rejected the obvious alternative — throwing read throughput at it — as
"fundamentally unscalable". Concurrent multi-threaded bucket reads tested best across all four
user categories. Result: **P99 down to ~200ms** by March 2023.

**Design rule to take away:** derive balances from postings, but **checkpoint them**. Append-only
plus derived balances is correct and unbounded; append-only plus periodic immutable snapshots is
correct *and* bounded. Decide the checkpoint strategy before you have five years of entries,
because retrofitting it is an online migration of your most sensitive table.

## The decision, compressed

- **No licence, need speed** → sponsor bank + processor ledger (Galileo/Lithic/Unit), plus
  your own shadow ledger for reconciliation. Never operate without the shadow ledger; that
  is the Synapse failure mode `[reported]`.
- **Licence, want velocity** → Vault or 10x. Pick on the product-definition model and
  migration tooling, not the feature matrix.
- **Licence, ledger is the moat** → build, and staff reconciliation as a first-class team.
- **Existing core, new product it can't express** → Formance/TigerBeetle sidecar.

## Architectural consequences

- **Consistency model.** A monolithic ledger gives you strong ACID in one transaction but
  cascading failure. Event-driven microservices give you isolated failure domains and
  eventual consistency via sagas — which means **every consumer must be idempotent**
  `[reported]`. Monzo's answer was to accept the distributed model and invest heavily in the
  RPC and deployment tooling to make ~1,600+ services tractable `[reported]`.
- **Product logic placement.** Encode fee splits and interest accrual **as ledger
  transactions**, not as application code that later posts to the ledger `[reported]`.
  Otherwise correctness lives in two places.
- **Reconciliation as stateless workers.** Build it as an independent, replayable subsystem
  that reads postings and rail statements and emits breaks. See [Resilience, regulatory reporting and operations](../layers/10-resilience-regulatory.md).

## Open questions

- What store is Chime's ChimeCore built on, and does it own the deposit sub-ledger or only
  card authorisation and bookkeeping?
- Has Monzo moved any of its ledger off Cassandra / onto Amazon Keyspaces at scale?
- Which UK challengers have actually completed a core migration (as opposed to launching a
  new product on a new core alongside the old one)?

## Sources

- Formance, core banking system architecture reference model — https://www.formance.com/blog/financial-operations/core-banking-system-architecture
- Monzo, Speeding up our balance read time: the planning phase — https://monzo.com/blog/2023/04/28/speeding-up-our-balance-read-time-the-planning-phase
- Monzo, We secured thousands of Cassandra clients — https://monzo.com/blog/we-secured-thousands-of-cassandra-clients-to-keep-monzos-data-safe
- Monzo, Building a Modern Bank Backend — https://monzo.com/blog/2016/09/19/building-a-modern-bank-backend
- InfoQ, Modern Banking in 1500 Microservices — https://www.infoq.com/presentations/monzo-microservices/
- InfoQ, Banking on Thousands of Microservices — https://www.infoq.com/articles/cassandra-kubernetes-microservices/
- 10x Banking, core banking platforms compared — https://www.10xbanking.com/core-banking-platforms-compared
- Thought Machine × Zopa press release — https://www.thoughtmachine.net/press-releases/zopa-bank
- Temenos × Varo — https://www.temenos.com/press_release/varo-first-consumer-fintech-granted-national-bank-charter-in-the-us-goes-live-with-temenos-cloud-technology/
- Trio, payment ledger architecture — https://trio.dev/payment-ledger-architecture-fintech/
- SDK.finance, best ledger software — https://sdk.finance/blog/best-ledger-software-for-banks-and-fintechs/
- Block careers, Senior Software Engineer Ledgering — https://block.xyz/careers/jobs/5281196008
