---
title: Data and ML platform
type: layer
status: living
updated: 2026-08-18
sources: 8
tags: [data, ml, streaming, feature-store]
---

## Summary

The data platform is where a neobank's two hardest latency requirements meet: a sub-second
decision in the payment path, and a full-history analytical view for models, regulators and
finance. The standard 2026 answer is a streaming spine (Kafka, often Flink), a tiered
feature store, and a warehouse — with a hard architectural rule that the *decision* path
never depends on the *analytics* path.

## The canonical shape

```
services ──events──▶ Kafka ──▶ Flink / stream processors ──▶ online feature store (Redis/DynamoDB)
                       │                                              │
                       └──▶ warehouse (BigQuery / Snowflake) ◀── dbt ─┘
                                     │
                             batch features, training sets,
                             regulatory reporting, decision-log analytics
```

- **Kafka** as the ingestion and decoupling layer: durability during downstream outages, and
  replay for debugging and model validation `[reported]`.

  **But a log is not a queue.** Monzo moved NSQ → Kafka for durability and then had to rebuild
  queue semantics on top `[confirmed]`. Two problems bite everyone: a single unprocessable
  message (**poison pill**) blocks its partition indefinitely, and strict per-partition ordering
  prevents concurrent processing, capping throughput. Their client library adds **deadlettering**
  (after `maxAttempts`, messages move to a deadletter topic, with a CLI to replay them onto a
  retry topic once a fix ships) and **unordered concurrent processing** — multiple goroutines per
  partition behind an `UnorderedOffsetManager` that tracks in-flight events so the committed
  offset only advances past fully-processed messages. Scale: **400+ services subscribing to
  2,500+ topics**. If you adopt Kafka for financial events, budget for this library; you will
  build it eventually.
- **Flink** for true streaming (per-event, stateful, exactly-once) where windowed aggregates
  are needed in the decision path `[reported]`.
- **Feature store, tiered by latency.** Monzo's three tiers are the model to copy:
  just-in-time (computed on demand), near-real-time (precomputed, cached), batch (periodic)
  `[confirmed]`. Online serving from a low-latency KV store; offline from the warehouse
  `[reported]`.
- **Warehouse.** Monzo uses **BigQuery** `[confirmed]`; Chime uses **MySQL + Snowflake**,
  having moved large-file processing (Galileo RDF files) from MySQL to Snowflake
  `[reported]`; Remitly runs **Kafka + Snowflake** `[reported]`.

## Training/serving split, in practice

Monzo's ML stack has historically spanned two clouds: analytics and training on **GCP**
(BigQuery), serving inside **AWS** microservices `[reported]`. That is unusual and expensive,
and worth understanding as a consequence of history (bank on AWS, analytics team on GCP)
rather than as a recommendation. The generalisable lesson is the *interface*: models are
trained where the data is and served where the traffic is, so the feature definitions must be
shared artefacts across the boundary, not code duplicated on both sides.

## Feature parity — the recurring bug

Training/serving skew is the most common and most expensive ML defect in banking. Mitigations
that actually work:

- One feature definition, compiled to both a batch and a streaming implementation.
- Point-in-time-correct training sets built from the **decision log**, not from current-state
  tables. If you log the features you actually used at decision time (Monzo logs input
  features per control execution to BigQuery `[confirmed]`), your training set is free and
  correct by construction.
- Back-testing new logic against history without touching live traffic — Monzo's Starlark
  pure-function controls exist for exactly this `[confirmed]`.

## The stack underneath — Monzo, 2021 → 2026

The 2021 post gives the components; the 2026 mesh post gives the governance layered on top
`[confirmed]`. Reading them together is the most complete public picture of a neobank data
platform.

| Function | Choice |
| --- | --- |
| Ingestion | A custom **Analytics Event Processor and Shipper** consuming the **Kafka** and **NSQ** firehose from backend services; **Fivetran** for external SaaS; manual loads to GCS/BigQuery |
| Warehouse | **BigQuery**. 4,700+ dbt models in 2021 → **12,000+ by 2026**. Some analytics tables ~**60TB rebuilt daily** |
| Transformation | **dbt**, ~**600k lines of SQL**. Forked in 2019 and containerised; custom extensions `dbt upstream prod` (speed) and **`indirect_ref`** (access control via interface tables) |
| Orchestration | **Airflow**, DAGs auto-generated from dbt models; nightly refreshes, some tables every 15 minutes |
| BI | **Looker** — **80% of staff** active users |
| ML serving | A **feature store that ships features from BigQuery into Cassandra**, i.e. from the analytics plane into the production plane |
| Model serving | **Sanic**-based Python microservice templates |
| Repo/CI | Monorepo on GitHub; CI cut from ~30 minutes to ~5 |

Two things stand out. **`indirect_ref` in 2021 is the direct ancestor of the "governed interfaces"
in the 2026 mesh** — the same idea (explicit contracts for cross-team consumption) first appearing
as a dbt hack and later becoming the organising principle. And **the feature store's job is a
cross-plane copy, BigQuery → Cassandra**, which is the concrete answer to how a
train-in-analytics / serve-in-production split is actually bridged.

## A worked warehouse design — Monzo's data mesh

Published April 2026 `[confirmed]`, and the most complete public account of a neobank warehouse:
**100+ teams, 12,000+ dbt models**, four layers modelled as *business objects* rather than the
usual staging/intermediate convention.

| Layer | Contents | Hand-written? |
| --- | --- | --- |
| Landing | Raw event payloads flattened into per-object timelines | **No — fully automated** |
| Normalised | Single-entity attributes, SCD Type-2 history | **No — generated** |
| Logical | Normalised objects combined into richer structures | Yes — the human layer |
| Presentation | Lightweight models for dashboards and ML features | Yes |

Three transferable ideas:

1. **Governed interfaces, not implicit dependencies.** Only the normalised and logical layers
   expose cross-team contracts — hundreds of explicitly declared ones. Schema changes stop
   rippling.
2. **Generate the boring layers.** In-house tool **Modelgen** produces landing and normalised
   models from a YAML description of each object. This is only possible because Monzo's
   microservices emit **uniformly structured event payloads** — the platform discipline pays off
   in the warehouse years later.
3. **Automate compliance instead of gatekeeping.** A data standards framework runs in CI on every
   PR: unique key, freshness tests, incremental processing unless exempted, named owner,
   documentation, naming conventions. A bot comments failures before merge.

At ~30% migrated: ~**40% cost reduction** in some domains, ~**25% faster data landing**, warehouse
cost growth reversed.

## ML platform capabilities to plan for

From Monzo's own list of platform investments `[confirmed]`:

- feature management and **versioning**
- model monitoring and evaluation
- **LLM orchestration and retrieval**
- compliance-focused architecture (lineage, explainability, retention)

**How the LLM line actually resolves.** Monzo's July 2026 fincrime post is the clearest public
answer to where LLMs belong in a regulated decision path: they turn unstructured customer
interaction into **structured features**, and a calibrated supervised model plus a meta-stacking
ensemble makes the decision. +20% fraud caught, with fewer legitimate payments sent to human
review `[confirmed]`. Internally, Monzo's **Agent Chip** authors ~10% of merged PRs and runs
1,800+ tasks a day behind an MCP gateway, sandboxed containers and a single egress proxy — and is
deliberately model-agnostic so a provider outage is a swap, not an incident `[confirmed]`.

The LLM line is not decoration. Monzo's **Ops Agent** executes end-to-end operational
processes across **150+ customer intents**, from Pot management to fraud investigation, and
was built with rigorous evaluation systems and human-in-the-loop workflows alongside
deterministic workflows `[confirmed]`. Block shipped **Money Bot** in Cash App to GA in early
2026, reaching a million active users in a week `[reported]`. Agentic AI in this sector is
now an ops-automation story, not a chatbot story — which means it needs the same evidence
plane as any other decisioning system.

## Modelling notes specific to banking events

- **Extreme class imbalance** — ~1 in 10,000 transactions fraudulent `[reported]`. Sampling
  strategy and metric choice (PR-AUC, alert-rate-at-recall) matter more than architecture.
- **Multi-task deep learning** replacing fleets of single-purpose models, plus
  **self-supervised embeddings** of customer and transaction behaviour `[confirmed]` — the
  foundation-model pattern applied to event streams.
- **Sequence models over (key, value, time) event triples** are the natural fit for this
  data shape; see Revolut's PRAGMA work and the local `pragma_mini.py` in this repo's parent
  project for the reduced version of that recipe.

## Open questions

- Is Monzo still split GCP-for-training / AWS-for-serving in 2026, or has that consolidated?
- Who is using a commercial feature store (Tecton, Feast, Databricks) versus building, and
  does anyone publish latency numbers for online feature retrieval in the auth path?
- What evaluation frameworks are being accepted by regulators for LLM-in-the-loop ops
  decisions?

## Sources

- Monzo, Machine Learning at Monzo in 2025 — https://monzo.com/blog/machine-learning-at-monzo-in-2025
- Monzo, Monzo's machine learning stack (2022) — https://monzo.com/blog/2022/04/26/monzos-machine-learning-stack
- Monzo, An introduction to Monzo's data stack — https://monzo.com/blog/2021/10/14/an-introduction-to-monzos-data-stack
- Monzo, How we built a queue on top of Kafka — https://monzo.com/blog/how-we-built-a-queue-on-top-of-kafka
- Monzo, A "meshy" approach to Data — https://monzo.com/blog/a-meshy-approach-to-data
- Monzo, Building Agent Chip — https://monzo.com/blog/building-agent-chip
- Monzo, Engineering the Future of Customer Operations: The Monzo Ops Agent — https://monzo.com/blog/engineering-the-future-of-customer-operations-the-monzo-ops-agent
- InfoQ, Monzo real-time fraud detection — https://www.infoq.com/news/2025/11/monzo-real-time-fraud-detection/
- ZenML MLOps database, Monzo's ML stack — https://www.zenml.io/mlops-database/monzo-monzos-ml-stack-end-to-end-ml-infrastructure-combining-gcp-analytics-training-and-aws-microservice-serving-for-fra
- Kai Waehner, online feature store with Kafka and Flink — https://www.kai-waehner.de/blog/2025/09/15/online-feature-store-for-ai-and-machine-learning-with-apache-kafka-and-flink/
- Chime Careers, Redesigning Large File Processing at Chime — https://careers.chime.com/en/life-at-chime/engineering-at-chime/redesigning-large-file-processing-at-chime/
- Perspective AI, Block's AI strategy 2026 — https://getperspective.ai/blog/block-square-ai-customer-research-seller-ecosystem-2026
