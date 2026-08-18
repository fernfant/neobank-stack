---
title: Monzo (UK)
type: bank
status: living
updated: 2026-08-18
sources: 9
tags: [uk, build-your-own, go, cassandra]
---

## Summary

The most transparent neobank engineering organisation in the world, and therefore the
de-facto reference architecture for Archetype A ("full-stack bank"). UK banking licence,
in-house ledger, in-house financial-crime platform, ~1,600–2,800 Go microservices on
Kubernetes over Cassandra, on AWS.

## Stack

| Layer | Choice | Confidence |
| --- | --- | --- |
| Licence | UK bank (PRA/FCA) | `[confirmed]` |
| Core ledger | In-house double-entry `service.ledger`; balances derived from postings | `[confirmed]` |
| Language | Go; in-house RPC framework | `[confirmed]` / `[reported]` |
| Runtime | Kubernetes on **EKS** (migrated from self-managed); Docker; monorepo | `[confirmed]` |
| Service count | **>3,000 microservices** migrated to the new EKS cluster | `[confirmed]` |
| Service mesh / RPC | **Linkerd** (Finagle-based) — Power of Two Choices + Peak EWMA, retry budgets | `[confirmed]` `[dated: 2016]` |
| Messaging | **Kafka**, at-least-once | `[confirmed]` `[dated: 2016]` |
| Datastore | Cassandra (Amazon Keyspaces referenced in AWS material) | `[confirmed]` / `[reported]` |
| Cloud | AWS primary; GCP for analytics/training | `[confirmed]` / `[reported]` |
| Warehouse | BigQuery | `[confirmed]` |
| Fincrime | In-house control platform, Starlark controls | `[confirmed]` |
| Card processing | **In-house.** GPS (now Thredd) processed the *prepaid* card 2016–2018; the current account runs on Monzo's own processor, no third-party issuing bank | `[confirmed]` |
| Faster Payments | **In-house gateway**, direct participant. Third-party gateway 2017–2019 | `[confirmed]` |
| Bacs / Direct Debit | **Direct participant** since 12 Sept 2022. Sponsor bank 2017–2022 | `[confirmed]` |
| Galileo | Powers Monzo's **US** business only — not the UK | `[reported]` |
| Customer ops | In-house LLM Ops Agent, 150+ intents | `[confirmed]` |

## What's distinctive

**Microservice count as a design philosophy.** On the order of 1,600–2,800 services
`[reported]`. This is only viable because service creation and operation are made cheap by
bespoke Go tooling, a uniform RPC layer, and heavy investment in deployment automation. The
security argument they give is granularity: `service.ledger`, the service that moves money,
gets the most stringent controls precisely because it is small and isolated `[reported]`.

**Fraud controls as sandboxed pure functions.** Controls run in **Starlark** as pure
functions inside an Engine microservice, which makes them safe to test and back-test against
history without touching live traffic `[confirmed]`. Controls are typed as detectors, action
controls, and action-selection controls. Feature loading is a separate service with a DAG
pipeline over three latency tiers (just-in-time / near-real-time / batch). Per-execution
metadata goes to BigQuery for effectiveness and false-positive measurement `[confirmed]`.

**ML direction (2025).** Multi-task deep learning replacing fleets of specialised models;
self-supervised embeddings of customer and transaction behaviour; five priorities — fincrime,
customer/ops, credit decisioning, personalisation, and the ML platform itself `[confirmed]`.

**The Ops Agent.** An LLM agent that executes end-to-end operational processes across 150+
customer intents, combined with deterministic workflows, with rigorous evaluation and
human-in-the-loop `[confirmed]`. The most advanced public example of agentic AI in banking
operations.

## UK payments processing — all of it in-house

Monzo has systematically insourced every payment path. Three separate migrations:

**Cards.** Monzo selected **GPS (Global Processing Services, now Thredd)** as processor after
getting its banking licence in August 2016, sitting between Monzo and Mastercard for the
*prepaid* card `[confirmed]`. GPS outages hit Monzo more than once `[reported]`. For the
**current account**, Monzo's engineering team "built a new payment processor from the ground
up", with **no third-party issuing bank** — explicitly to control the whole experience and
improve reliability `[confirmed]`. The prepaid product was wound down through 2017–18.

**Faster Payments.** A third-party gateway provider from 2017 until **2 November 2019**
(Monzo does not name them) `[confirmed]`. A payments incident on 30 May 2019 was the trigger:
the conclusion drawn was that "operating our own infrastructure and systems is the key to
reliability". The in-house gateway went operational November 2019 and the **live migration
completed 2 November 2020**, finishing in one hour against a three-hour window `[confirmed]`.

The gateway's design is the most interesting thing Monzo has published about payments, because
it is **a deliberate monolith**:

| Property | Choice |
| --- | --- |
| Shape | **Monolithic replicated application in Go — not microservices** |
| Topology | **Active-active** across two data centres (the previous setup was active-standby with ~15 minute failover) |
| Connectivity | Per-payment-type TCP connections to the FPS hub; **two physical connections per data centre**, tolerating 3 of 4 failing |
| Deployment | Docker and Docker Compose **on virtual machines** |
| Storage | **DRBD** — three servers per DC with dual SSDs; six SSD replicas per write; survives a whole server plus one disk per remaining machine |
| Security | **Four HSMs**, two per data centre; the gateway still runs on one |
| Resilience | **Stand-in / store-and-forward** — responds to the hub on per-message timeout if the payment processor is unresponsive, then retries forward when restored, so payments are not rejected |
| Observability | 10-second metric granularity, 60-second alert threshold, logs to **BigQuery** with sensitive data stripped, dedicated payments on-call |

TransferWise, Pay.UK and Vocalink are credited as advisers, not vendors `[confirmed]`.

**Bacs.** Monzo used a **sponsor bank** from 2017 (unnamed) `[confirmed]`. Two problems forced
the change: manual money transfers to the sponsor carried operational risk, and regulatory
limits capped how much Monzo could hold at the sponsor during **mid-month and end-of-month
payroll peaks**. Direct participation took ~18 months across engineering, operations, risk,
legal and infrastructure. Migration day was **12 September 2022** — deliberately chosen for
lower volumes — and the first Direct Debit file landed at **00:19 on 13 September 2022**
`[confirmed]`. Built for it: a **SWIFT Banking Network** connection to Bacs, HSMs holding the
certificates that sign and verify files, Bacs microservices that generate and hash files, and
**direct settlement against Monzo's Bank of England account**.

### The pattern

Sponsor or vendor first, in-house once volume makes the dependency the binding constraint —
cards by 2018, Faster Payments by 2020, Bacs by 2022. Each move was triggered by a specific
operational limit rather than by cost: a vendor outage, a failover time, a balance cap at a
sponsor. That is a more useful build-vs-buy rule than any threshold — see
[Build vs buy, layer by layer](../comparisons/build-vs-buy.md).

**Do not confuse markets.** Galileo's customer list includes "the US-based business of Monzo"
`[reported]`. That is Monzo's US operation, not the UK bank, which runs on the stack above.

## Monzo Stand-in — a second bank, on a second cloud, for 1% of the cost

The most important thing Monzo has published, and the best answer in this entire research to
"what happens when your cloud goes down" `[confirmed]`.

**Stand-in is a completely separate backup banking infrastructure.** The primary platform runs on
**AWS**; Stand-in runs on **GCP**, with its own Kubernetes clusters, services, databases, queues
and locking. Explicitly framed as "a backup of last resort, not our primary mechanism of providing
a reliable service".

| | Primary | Stand-in |
| --- | --- | --- |
| Cloud | AWS | **GCP** |
| Services | ~3,000 microservices | **18 minimal services** |
| Cost | — | ~**1% of the primary platform** |
| Role | System of record, always | Never authoritative for customer data |

**What customers can still do:** card spending and cash withdrawals, sending and receiving bank
transfers, checking balance and transactions, freezing and unfreezing a card. The app detects the
mode and shows a simplified UI.

**How state flows.** A **Stand-in Data Syncer** consumes events from the primary platform's event
system and maintains minimal immutable state — deliberately *non-blocking and eventually
consistent*, not strongly consistent, with lag monitored and alerted against an explicit appetite.
Going the other way, Stand-in publishes **"Monzo Advices"** — durable records of transaction
approvals — to **GCP PubSub**, which the primary platform applies **verbatim** once it recovers.
Correlation IDs deduplicate transactions that appear on both sides, and the primary is tolerant of
receiving advices **in any order**.

**Payments in Stand-in** `[confirmed]`: Mastercard cards, Faster Payments transfers, and Bacs
direct debits and credits. Two routing paths — via the primary platform's **edge services** during
a partial outage (chosen because they are the earliest service in the payment path and the most
resilient), or **directly from the data centres** during a severe failure.

Rather than sharing logic with the primary, Stand-in reimplements payment processing using a
**validators pattern**: independent checks running in parallel (is the card frozen, is the account
open), with different validator sets per payment type. Divergence is caught by **shadow testing a
proportion of production traffic** and comparing Stand-in's decisions against the primary's,
requiring differences to stay within an explainable range.

**How it is trusted.** Tested "rigorously and continuously, in production" — small customer
populations run on Stand-in permanently in testing mode. Activation is manual: a Stand-in
Configuration service runs in both platforms, and engineers enable components for specific user
segments via CLI. In an August 2024 incident the outage ran about an hour before Stand-in was
activated.

### Why this matters beyond Monzo

Every regulator now asks the cloud concentration question — DORA Articles 28–30, the FCA/PRA
critical-third-parties regime. Most firms answer with a document. Monzo answered by **building a
minimal second bank on a different cloud and running real customers through it continuously**.
That is a genuine, testable exit-and-continuity capability, and the 1%-of-cost figure is the
number that makes the argument affordable. See [Resilience, regulatory reporting and operations](../layers/10-resilience-regulatory.md).

## Running migrations across thousands of services

Monzo's August 2024 post puts the service count at **2,800** and describes a repeatable
seven-phase migration pattern `[confirmed]`:

1. Plan and align via a written proposal and architecture review
2. **Wrap the old library** so behaviour can switch on configuration
3. Update call-sites with automated refactoring — `gopls`, `gorename` (`go-patch` and `rf` for
   harder cases)
4. **Wrap the new library behind a feature flag**, initially off
5. Mass-deploy services with internal tooling and automated rollback checks (Argo Rollouts)
6. **Roll out via config**, gradually, cheapest-to-riskiest using a **service tiering** system
7. Clean up, with `semgrep` in CI blocking any new dependency on the deprecated library

The detail that makes it work: **config refreshes every 60 seconds**, against a couple of minutes
per deployment. Rollback is a config change, not a redeploy — which is why the flag wrapper in
steps 2 and 4 is worth the effort.

### Service count over time

| Date | Services |
| --- | --- |
| 2016 (beta / launch) | ~100 → ~150 |
| May 2022 | ~2,000 |
| Nov 2022 | 2,100+ |
| Aug 2024 | **2,800** |
| Feb 2025 | ~3,000 |
| May 2026 | **>3,000** (migrated to EKS) |

## International payments — adapters, deciders, effects

Monzo's July 2024 post describes a modular pipeline built for correctness, testability and
reuse `[confirmed]`:

1. **Payment creation (adapter layer)** — raw partner messages, each in a different format,
   marshalled into one common representation. Adapters decouple wire formats from downstream logic.
2. **Decisioning** — multiple **Deciders** evaluate account existence, compliance and limits,
   returning Accept, Reject or Hold, with explicit precedence: **Hold blocks, Reject overrides
   Accept.**
3. **Effect generation** — the decision produces *effects*: ledger entries, bank notifications,
   internal account movements.
4. **Effect application** — effects executed and logged for audit and debugging.

FX: **40+ currencies** without holding accounts in each. A correspondent partner bank receives the
payment, performs the exchange and forwards via **SWIFT** with the rate attached. IBAN validation
with checksums, BIC codes (Monzo's is `MONZGB2L`), and idempotency controls for exactly-once.
Each partner gets an adapter plus a separate microservice for partner-specific logic, so onboarding
a new partner does not touch the core processor.

This is precisely the normalisation-layer pattern argued for in
[Deep dive — Rail adapters (buy access, build normalisation)](../deep-dives/02-rail-adapters.md) — independently arrived at, which is the best kind of
confirmation.

## Platform engineering — the tooling that makes 3,000 services survivable

Monzo's platform teams treat internal engineers as their users and the platform as their product
`[confirmed]`. Two named internal systems from its May 2026 post:

- **`service.karpenter`** — a backend service wrapping the Kubernetes autoscaler Karpenter,
  letting engineers toggle disruption per nodepool via RPC, gated behind **multi-party approval**.
- **Migrator service** — purpose-built automation that moved **>3,000 microservices** onto the new
  EKS cluster.

The pattern worth noting: rather than giving engineers raw access to infrastructure, Monzo wraps
each capability in an owned service with an opinionated interface and access controls. That is
how a four-figure service estate stays governable, and it is the missing half of the "1,600
microservices" story people usually repeat.

The 2016 foundations still show through `[confirmed]` `[dated: 2016]`: Kubernetes on CoreOS on
AWS (after ~a year on Mesos/Marathon, which cut infrastructure cost to ~25% of previous),
**Linkerd** for RPC with Power of Two Choices + Peak EWMA load balancing and automatic retry
budgets for idempotent requests, and **Kafka** as a replayable at-least-once commit log. Service
count then: ~100 at beta, ~150 at publication. Today: >3,000.

## The data platform — a mesh with 12,000 dbt models

Published April 2026 `[confirmed]`. **100+ independent teams** contribute to a warehouse of
**12,000+ dbt models**. Four layers, modelled as *business objects* rather than the usual
staging/intermediate convention:

| Layer | Contents |
| --- | --- |
| **Landing** | Flattens raw event payloads into clean per-object timelines. **Fully automated, no hand-written SQL** |
| **Normalised** | Single-entity attributes with SCD Type-2 history. Auto-generated |
| **Logical** | Combines normalised objects into richer structures. Where humans actually work |
| **Presentation** | Lightweight consumer models for dashboards and ML features |

Only the normalised and logical layers expose **governed interfaces** for cross-team consumption
— hundreds of them, explicitly declared, which removes implicit dependencies and stops schema
changes rippling.

Two pieces of in-house tooling carry it:

- **Modelgen** — a CLI that generates the landing and normalised layers from YAML. Practitioners
  describe an object once (key identifiers, source events, fields). This only works because
  Monzo's microservices emit **uniformly structured event payloads** — the payoff for a decade of
  platform discipline.
- **Data standards framework** — CI enforcement on every pull request: unique key per model,
  freshness tests, incremental processing unless exempted, named owner team, documentation,
  naming conventions. A GitHub bot comments failures before merge.

Stated principles: *be opinionated* (fewer choices scale better), *formalise sharing through
declared interfaces*, and **automate compliance rather than gatekeep**. At ~30% migrated:
~**40% cost reduction** in some domains, ~**25% faster data landing**, and warehouse cost growth
reversed.

## Fraud modelling — what is actually in the model

Two 2026 posts move this well past "they use ML" `[confirmed]`.

**Representation learning (March 2026).** A multi-task neural network: input features flow
through **3 shared feed-forward layers**, then split into **3 task heads** predicting *fraud*,
*payment method* and *fraud type*. The fraud head's output plus the original input features are
then fed into a **LightGBM** model. Result: ~**30% improvement over the LightGBM baseline**,
concentrated in **rarer fraud subtypes** — and when entire subtypes were withheld from training,
the multi-task model retained substantially higher recall. The mechanism is shared statistical
strength: rare subtypes borrow structure from common ones.

**Generative AI + predictive modelling (July 2026).** A five-stage pipeline where **the LLM never
decides**:

1. Supervised models score every transaction, producing calibrated fraud probabilities
2. High-risk cases trigger a customer questionnaire
3. A multimodal reasoning model turns the responses into **structured semantic features**
4. A separate supervised fraud model consumes those enriched features for an independent probability
5. A **meta-stacking ensemble** combines transaction-time and questionnaire probabilities

Monzo's stated reasoning is precise: LLMs are weak at well-calibrated quantitative assessment and
strong at turning unstructured interaction into structure, so they are used as **feature
extractors**, not decision-makers. Measured in live deployment: **+20% fraud cases caught and
money prevented**, while *reducing* legitimate payments diverted to human review.

## Agent Chip — agentic AI in engineering

Published August 2026 `[confirmed]`. An in-house coding agent authoring ~**10% of all merged PRs**
and running **1,800+ tasks a day**, with nearly all engineers using a coding agent regularly.

Architecture: an **MCP Gateway** supplying institutional context; remote agentic infrastructure
spawning **sandboxed containers** with per-task tool access; a `remote-code-agent-trigger` service
mapping Slack/Linear/webhook events to standard workflows; deployment in an **isolated namespace**
with a **single HTTP proxy** controlling all egress; secrets held outside agent execution.
Deliberately **model-agnostic** — "if a model provider suffers an outage we can quickly swap in
another". Used for alert investigation and incident response, PR implementation from Slack,
automated review, and library upgrades.

## What to copy, what not to

**Copy:** the control-plane design (pure functions, back-testing, decision logs), the
latency-tiered feature store, the discipline of deriving balances from postings.

**Don't copy:** the microservice count. It is a consequence of a decade of tooling
investment, not a starting point.

## Open questions

- ~~Current microservice count~~ — **answered: >3,000** `[confirmed]`, and still growing rather
  than consolidating.
- Is the GCP-training / AWS-serving split still in place in 2026? BigQuery is still the warehouse
  and decision-log store; the serving side is not restated in recent posts.
- Has any part of the ledger moved off Cassandra? Still unanswered — recent posts cover EKS,
  platform and data, never the ledger's datastore.
- What models power Agent Chip? Deliberately not disclosed.
- Which LLM does the fincrime questionnaire pipeline use, and how is it evidenced to the FCA?

## Sources

- Monzo blog, technology — https://monzo.com/blog/topic/technology
- Monzo, Building a Modern Bank Backend — https://monzo.com/blog/2016/09/19/building-a-modern-bank-backend
- Monzo, Building a reactive Fraud Prevention Platform — https://monzo.com/blog/build-a-reactive-fraud-prevention-platform
- Monzo, Machine Learning at Monzo in 2025 — https://monzo.com/blog/machine-learning-at-monzo-in-2025
- Monzo, The Monzo Ops Agent — https://monzo.com/blog/engineering-the-future-of-customer-operations-the-monzo-ops-agent
- Monzo, A "meshy" approach to Data — https://monzo.com/blog/a-meshy-approach-to-data
- Monzo, Representation Learning for Enhanced Fraud Detection — https://monzo.com/blog/representation-learning-for-enhanced-fraud-detection
- Monzo, Combining generative AI and predictive modelling to fight financial crime — https://monzo.com/blog/combining-generative-ai-and-predictive-modelling-to-fight-financial-crime
- Monzo, The Engineering Behind the Platform — https://monzo.com/blog/the-engineering-behind-the-platform
- Monzo, Building Agent Chip — https://monzo.com/blog/building-agent-chip
- Monzo, Tolerating full cloud outages with Monzo Stand-in — https://monzo.com/blog/tolerating-full-cloud-outages-with-monzo-stand-in
- Monzo, Processing payments in Monzo Stand-in — https://monzo.com/blog/processing-payments-in-monzo-stand-in
- Monzo, How we run migrations across 2,800 microservices — https://monzo.com/blog/how-we-run-migrations-across-2800-microservices
- Monzo, Building a processing system for International Payments — https://monzo.com/blog/building-a-processing-system-for-international-payments
- Monzo, Argo Rollouts at scale — https://monzo.com/blog/2022/11/02/argo-rollouts-at-scale
- Monzo, How we moved our Faster Payments connection in-house — https://monzo.com/blog/how-we-moved-our-faster-payments-connection-in-house
- Monzo, Becoming direct participants of Bacs — https://monzo.com/blog/2023/02/22/becoming-direct-participants-of-bacs
- Monzo, A technical look at how Monzo-to-Monzo payments work — https://monzo.com/blog/2018/04/05/how-monzo-to-monzo-payments-work
- InfoQ, Monzo real-time fraud detection — https://www.infoq.com/news/2025/11/monzo-real-time-fraud-detection/
- InfoQ, Modern Banking in 1500 Microservices — https://www.infoq.com/presentations/monzo-microservices/
- The Register, 1,600 microservices — https://www.theregister.com/2020/03/09/monzo_microservices/
- AWS, Monzo on EKS and Keyspaces — https://www.youtube.com/watch?v=O3s3MWD-UUA
