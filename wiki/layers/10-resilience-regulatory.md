---
title: Resilience, regulatory reporting and operations
type: layer
status: living
updated: 2026-08-18
sources: 8
tags: [resilience, dora, reconciliation, reporting, operations]
---

## Summary

This is the layer that turns a working system into a *defensible* one. Three subsystems do
most of the work: reconciliation, the evidence store, and exit/continuity planning. All
three are cheap to design in and brutally expensive to retrofit.

## Reconciliation

Every layer holds an opinion about how much money exists. Reconciliation is the machinery
that forces agreement and surfaces disagreement fast.

Build it as **stateless, replayable workers** that read postings and external statements and
emit **breaks** `[reported]`. Properties that matter:

- **Per-rail and per-partner**, not one giant job.
- **Replayable** — rerunning yesterday must produce yesterday's answer.
- **Break lifecycle** — every break is a ticket with an owner, an age, and an aging report.
  Unaged breaks are how shortfalls hide.
- **Frequency driven by regulation, not convenience.** UK EMIs: **daily** safeguarding
  reconciliation from 7 May 2026 under FCA PS25/12 `[confirmed]`. US sponsor-bank programmes:
  the FDIC's proposed rule pushes **near real-time** reconciliation of fintech partner
  accounts `[confirmed]`.

The Synapse failure is the canonical case: middleware held the mapping from pooled FBO
deposits to end users, and when it failed there was a $60–90m gap nobody could resolve
`[reported]`. If you are a fintech on a sponsor bank, assume the regulator's question is
"can the bank independently verify your sub-ledger, continuously?" and build for a yes.

## The evidence store

Regulators ask what you decided, when, on what basis. Requirements:

- **Bi-temporal records** — transaction time and effective date — so historical balances can
  be reconstructed without rewriting postings `[reported]`.
- **Immutable decision logs** for every risk control: input features, model/control version,
  output, action taken. Monzo puts exactly this in BigQuery `[confirmed]`.
- **Retention** aligned to the longest applicable obligation, with lineage.
- **Reports derived from the ledger**, not from a parallel reporting database `[reported]`.
  Two sources of truth for a regulatory number is a finding waiting to happen.

The dividend: this same store is your point-in-time-correct ML training set (see
[Data and ML platform](../layers/08-data-ml-platform.md)).

## Operational resilience and exit planning

**UK/EU frame:** DORA in the EU; FCA/PRA SS2/21 and PS6/21 in the UK, which the FCA and PRA
have aligned with DORA principles `[reported]`. The UK critical-third-parties regime extends
supervision to major providers directly.

What is actually required `[reported]`:

- Due diligence before onboarding an ICT provider.
- **Concentration risk assessment** before entering any new critical-function arrangement,
  and continuous monitoring (DORA Art. 28/29).
- **Documented exit strategy** and transition provisions in the contract (Art. 30), for
  critical functions.
- Enhanced monitoring and contingency plans for critical providers.
- Important business services mapped, with impact tolerances set and tested.

Engineering translation: know which of your vendors are on the critical path for an important
business service, know what happens when each is down, and have a tested answer — even if the
answer is "degraded mode for 48 hours with these specific customer impacts". A fictional
multi-cloud plan is worse than an honest degraded-mode plan.

### The best public answer: Monzo Stand-in

Most firms answer the cloud-concentration question with a document. Monzo built a **second bank**
`[confirmed]`.

**Stand-in is a completely separate backup banking infrastructure on a different cloud.** Primary
runs on AWS; Stand-in runs on **GCP** with its own Kubernetes clusters, databases, queues and
locking. It is **18 minimal services against the primary's ~3,000**, and it costs roughly **1% of
the primary platform**.

| Design choice | Why it matters |
| --- | --- |
| **Minimal scope** — card spend, ATM, send/receive transfers, balance, freeze card | Continuity does not mean full function. Pick the handful of things customers cannot live without and build only those |
| **Different cloud** | Makes it a genuine answer to concentration risk rather than a same-provider failover |
| **Eventually consistent sync** via a Data Syncer over the primary's event stream | Non-blocking by design — the backup must never be able to slow the primary |
| **"Monzo Advices"** to GCP PubSub, applied **verbatim** by the primary on recovery, deduplicated by correlation ID and **tolerant of any order** | This is the reconciliation contract. Without it, Stand-in would create exactly the break class that ends companies |
| **Reimplemented logic, not shared code** — a *validators* pattern | Shared code means a shared bug takes both platforms down |
| **Shadow testing** production traffic to compare Stand-in vs primary decisions | Proves the reimplementation has not drifted |
| **Real customers run on it continuously** in testing mode | A failover you have never used is a hypothesis, not a control |
| **Primary remains system of record throughout** | The backup never becomes authoritative — no ambiguity about truth |

Two things to take from it even if you never build one. First, **the cost of a credible
continuity capability can be ~1% of production** if you are ruthless about scope — which removes
the usual objection. Second, **the hard part is not failover, it is the reconciliation contract on
the way back**: ordered-tolerant, idempotent, deduplicated advices applied verbatim. That is the
same machinery as [Deep dive — Reconciliation (build)](../deep-dives/01-reconciliation.md), and it is why the reconciliation subsystem is
the first thing to build.

## Privileged access as a designed control

Regulators ask who can do what to customer money. Monzo's answer is worth copying because it is
declarative and lives with the code `[confirmed]`.

Scale of the problem: **~6,000 RPCs across 2,000+ microservices** (May 2022). Rather than a
separate access-control system that drifts, engineers declare access in a custom proto field —
**`humans_who_can_rpc`** — on the RPC definition itself, so permissions cannot get out of sync
with the thing they protect. The authorisation service reads them via **proto reflection**.

Five modes, and the published distribution is the interesting part:

| Mode | Share |
| --- | --- |
| `ENGINEERS_WITHOUT_APPROVAL` — any staff, immediately | ~25% |
| `ENGINEERS_WITH_APPROVAL` / `CONTRIBUTORS_WITH_APPROVAL` — peer sign-off required | **50%** |
| `CONTRIBUTORS_WITHOUT_APPROVAL` — service owners only | (within the above) |
| `BREAK_GLASS_ONLY` — security on-call, during incidents | ~25% |

**Half of all internal RPCs require a second human.** A software-ownership system keeps contributor
lists current asynchronously (under an hour's delay). Multi-party approval reappears in the
platform layer too — `service.karpenter` gates node-disruption changes the same way (see
[Monzo (UK)](../banks/monzo.md)).

The transferable idea: **make the permission a property of the API definition, not of a separate
registry**, and publish the distribution so "who can touch money" is a measurable number rather
than an assertion.

## Operations

- **24/7 money on-call.** A ledger incident is not a page you defer to morning. Runbooks for
  stuck payments, duplicate postings, and stand-in authorisation limits.
- **Customer operations at scale** is the hidden cost centre. Monzo's response was to
  automate it: the Ops Agent runs end-to-end processes across 150+ intents, combined with
  deterministic workflows, with rigorous evaluation and human-in-the-loop `[confirmed]`.
- **Change management for risk controls.** Controls change weekly. Monzo's answer — controls
  as sandboxed pure functions with back-testing `[confirmed]` — is a change-management design
  as much as a technical one.

## Open questions

- What does the FDIC's final rule text define as "near real-time"?
- How are UK firms actually evidencing the 48-hour CASS 10 resolution pack requirement — a
  live export, or a documented manual procedure?
- Has any regulator accepted a "degraded mode" exit plan for a hyperscaler dependency, or do
  they still expect portability? Monzo's Stand-in is the strongest public example of what
  "credible" looks like — has any regulator commented on it directly?
- Does anyone else run a minimal second-cloud bank? Nothing comparable found for Starling,
  Revolut, Chime or N26.

## Sources

- ClearBank, FCA safeguarding overhaul PS25/12 — https://clear.bank/learn/insights/the-fcas-safeguarding-overhaul-the-new-rules-their-impact-and-how-to-prepare
- The Payments Association, CASS 15 compliance — https://thepaymentsassociation.org/whitepaper/safeguarding-how-payment-and-e-money-firms-can-stay-compliant-with-cass-15/
- Kiteworks, DORA Article 28 exit strategies — https://www.kiteworks.com/third-party-risk/dora-article-28-exit-strategies/
- Regulation-DORA, cloud exit strategy and concentration risk — https://www.regulation-dora.eu/blog/cloud-exit-strategy-concentration-risk-dora
- Schneider Downs, DORA exit strategy and termination — https://schneiderdowns.com/our-thoughts-on/doras-approach-to-exit-strategy-and-termination/
- Yale Journal of International Affairs, the Synapse collapse — https://www.yalejournal.org/publications/the-synapse-collapse
- Formance, core banking reference model — https://www.formance.com/blog/financial-operations/core-banking-system-architecture
- Monzo, Humans who can RPC: securing staff access to microservices — https://monzo.com/blog/2022/05/26/humans-who-can-rpc-securing-staff-access-to-microservices
- Monzo, Tolerating full cloud outages with Monzo Stand-in — https://monzo.com/blog/tolerating-full-cloud-outages-with-monzo-stand-in
- Monzo, Processing payments in Monzo Stand-in — https://monzo.com/blog/processing-payments-in-monzo-stand-in
- Monzo, Engineering the Future of Customer Operations — https://monzo.com/blog/engineering-the-future-of-customer-operations-the-monzo-ops-agent
