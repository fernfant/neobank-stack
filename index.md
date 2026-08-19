# Index

The content catalogue. Read this first when answering a question, then drill into pages.
Updated on every ingest.

## Overview

| Page | One line |
| --- | --- |
| [wiki/overview.md](wiki/overview.md) | The thesis: four decisions, three archetypes, what changed in 2025–26 |
| [wiki/layers/00-layer-map.md](wiki/layers/00-layer-map.md) | Ten layers plus the two orthogonal planes (reconciliation, evidence) |

## Layers

| # | Page | One line |
| --- | --- | --- |
| 1 | [01-licence-and-charter](wiki/layers/01-licence-and-charter.md) | Bank vs EMI vs sponsor bank; FCA PS25/12; the Synapse rule |
| 2 | [02-core-ledger](wiki/layers/02-core-ledger.md) | Six invariants; build vs Vault/10x/Temenos vs TigerBeetle/Formance |
| 3 | [03-payment-rails](wiki/layers/03-payment-rails.md) | FPS/Bacs/CHAPS vs ACH/RTP/FedNow; the money-movement layer pattern |
| 4 | [04-card-issuing](wiki/layers/04-card-issuing.md) | The four vendor roles; Marqeta/Galileo/Lithic/Highnote/Thredd; ChimeCore |
| 5 | [05-kyc-onboarding](wiki/layers/05-kyc-onboarding.md) | Pipeline, orchestration, perpetual KYC, KYB |
| 6 | [06-fincrime](wiki/layers/06-fincrime.md) | Monzo's control platform as reference; vendors; UK APP liability |
| 7 | [07-credit-scoring](wiki/layers/07-credit-scoring.md) | Cash-flow underwriting; model/policy separation; reason codes |
| 8 | [08-data-ml-platform](wiki/layers/08-data-ml-platform.md) | Kafka/Flink/feature store/warehouse; training-serving parity; agentic ops |
| 9 | [09-infrastructure-runtime](wiki/layers/09-infrastructure-runtime.md) | Go vs JVM; Cassandra vs Postgres event store; cloud concentration |
| 10 | [10-resilience-regulatory](wiki/layers/10-resilience-regulatory.md) | Reconciliation, evidence store, DORA exit planning, ops |

## Banks

### UK

| Page | Archetype | Signature |
| --- | --- | --- |
| [monzo](wiki/banks/monzo.md) | A — full-stack | Go, Cassandra, ~1,600–2,800 services, Starlark fraud controls, Ops Agent |
| [starling](wiki/banks/starling.md) | A + vendor | Java on AWS; sells its core as Engine |
| [revolut](wiki/banks/revolut.md) | A — full-stack | Kotlin/Ktor, **Postgres `LISTEN`/`NOTIFY` event store**, multi-currency, PRAGMA |
| [n26](wiki/banks/n26.md) | B — bought core | Mambu core, Kotlin on AWS, HashiCorp → Kubernetes, the NLB latency war story |
| [zopa](wiki/banks/zopa.md) | B — bought core | Thought Machine Vault; beta in 9 months |
| [chase-uk](wiki/banks/chase-uk.md) | B — bought core | 10x SuperCore; incumbent-backed challenger |

### USA

| Page | Archetype | Signature |
| --- | --- | --- |
| [chime](wiki/banks/chime.md) | C → vertical | No charter, own processor (ChimeCore); **CoreDB = MySQL/RDS, 40TB**; EKS, ~1k deploys/day |
| [sofi](wiki/banks/sofi.md) | A + vendor | Charter + owns Galileo + Cyberbank Core; Kotlin/GraphQL, ~2.5m-line Flutter app |
| [varo](wiki/banks/varo.md) | B — bought core | First consumer-fintech national charter; Temenos Transact |
| [remitly](wiki/banks/remitly.md) | Cross-border | Java/Kotlin/Go, Aurora, Kafka+Snowflake, corridor payout network |
| [cash-app](wiki/banks/cash-app.md) | Block | Shared Ledgering core across Square and Cash App; Money Bot |

## Deep dives — the four "build" layers

**[Published page](https://claude.ai/code/artifact/1efb55a6-2b1c-487f-abe0-d6cc6f6ba246)** — all four, with diagrams.

| Page | The argument |
| --- | --- |
| [01-reconciliation](wiki/deep-dives/01-reconciliation.md) | Uber's 3-service settlement system, the seven matching patterns, a worked break taxonomy, TigerBeetle/Formance/Temporal |
| [02-rail-adapters](wiki/deep-dives/02-rail-adapters.md) | jPOS, the moov-io family, Prowide ISO 20022, the payment state machine, who to buy access from |
| [03-kyc-orchestration](wiki/deep-dives/03-kyc-orchestration.md) | The router pattern, OPA/GoRules/Drools, self-hosted OpenSanctions+yente, Splink for KYB |
| **[07-independent-bank](wiki/deep-dives/07-independent-bank.md)** | No sponsor anywhere — 10 layers, every decision, 60+ vendor options from HSMs and card bureaux to regulatory reporting — **[published](https://fernfant.github.io/neobank-stack/summary/independent-bank.html)** |
| **[06-monzo-payments](wiki/deep-dives/06-monzo-payments.md)** | Monzo end to end — the insourcing arc, FPS mechanics, the monolithic gateway, Bacs direct participation, international, Stand-in — **[published](https://fernfant.github.io/neobank-stack/summary/monzo-payments.html)** |
| **[05-payment-rails](wiki/deep-dives/05-payment-rails.md)** | Auth vs clearing vs settlement; FPS prefunding and the July 2026 Net Sender Cap change; Bacs AUDDIS/ADDACS/ARUDD/DDICA; ACH return codes and the 0.5% threshold; RTP vs FedNow — **[published](https://claude.ai/code/artifact/6a4be261-f66f-4f2d-bc89-e075b9a96379)** |
| [04-fraud-aml](wiki/deep-dives/04-fraud-aml.md) | Monzo's Starlark controls vs Stripe Radar, Chronon (open source, powers 100% of Stripe's charge-path models), Marble/Jube/Tazama |

## Vendors and comparisons

| Page | One line |
| --- | --- |
| **[Vendor map — who uses what](https://claude.ai/code/artifact/fc08f1f1-eef4-4e57-8617-7ca7f431a6b9)** | Published: 40 vendors by layer, with the banks named as using each |
| [vendor-map](wiki/vendors/vendor-map.md) | The attribution matrix, with confidence tags and the gaps marked |
| [vendor-landscape](wiki/vendors/vendor-landscape.md) | Every layer's vendor table + the seven procurement questions that separate them |
| [uk-vs-usa](wiki/comparisons/uk-vs-usa.md) | The four divergences: interchange, APP liability, rail maturity, licensing |
| [build-vs-buy](wiki/comparisons/build-vs-buy.md) | Default per layer, and the three triggers to re-open a buy decision |

## Templates and diagrams

| Artefact | Use |
| --- | --- |
| [architecture-diagram-template](templates/architecture-diagram-template.md) | Six fill-in Mermaid diagrams + the rules that make them comparable |
| [key-questions](templates/key-questions.md) | 100 questions across 11 sections; ★ = the ones that expose real problems |
| [vendor-evaluation-scorecard](templates/vendor-evaluation-scorecard.md) | Weighted scorecard, reference checks, automatic disqualifiers |
| **[Published: full reference](https://claude.ai/code/artifact/2b1b1ea1-7f4f-4f40-9e8e-2af6049b3d6a)** | Reference architecture, archetypes, hot path, reconciliation |
| **[Published: brief, with diagrams](https://claude.ai/code/artifact/10168ec5-9832-4b67-b785-9de2c91ff0a2)** | ~9-minute executive summary + two diagrams |
| **[Published: brief, text only](https://claude.ai/code/artifact/d6b7c2d4-2fc4-4735-ab7c-2054c2659b50)** | The same summary without diagrams |
| [summary/](summary/) | Source of the two briefs |
| [reference-architecture.html](diagrams/reference-architecture.html) | Source of the published page; redeploy via `neobank-architect` |
| [reference-architecture.mmd](diagrams/reference-architecture.mmd) | The generic ten-band architecture |
| [uk-neobank.mmd](diagrams/uk-neobank.mmd) | Monzo-shaped UK licensed bank |
| [usa-neobank.mmd](diagrams/usa-neobank.mmd) | Chime-shaped US fintech on sponsor banks |
| [card-auth-sequence.mmd](diagrams/card-auth-sequence.mmd) | The hot path |
| [recon-flow.mmd](diagrams/recon-flow.mmd) | The subsystem everyone omits |

## Bookkeeping

- [CLAUDE.md](CLAUDE.md) — the schema
