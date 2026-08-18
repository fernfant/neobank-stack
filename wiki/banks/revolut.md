---
title: Revolut (UK/EU)
type: bank
status: living
updated: 2026-08-18
sources: 5
tags: [uk, kotlin, event-sourcing, gcp, multi-currency]
---

## Summary

The JVM-and-GCP counterexample to Monzo. Event-driven microservices in Java/Kotlin over a
Postgres event store, multi-currency ledger with ACID guarantees, and a published foundation
model for banking event streams (PRAGMA) that is the most interesting ML artefact any
neobank has put out.

## Stack

| Layer | Choice | Confidence |
| --- | --- | --- |
| Language | Java, Kotlin, Spring Boot; Ktor and coroutines referenced | `[reported]` |
| Frontend | React, TypeScript | `[reported]` |
| Runtime | Kubernetes, microservices | `[reported]` |
| Datastore | PostgreSQL with streaming replication; single event store on Postgres | `[reported]` |
| Cloud | GCP | `[reported]` |
| Architecture | Event-driven — services communicate by publishing/consuming persisted events | `[reported]` |

Named engineering problems from its own hiring material `[reported]`: real-time currency
conversion across liquidity providers, sub-second card payment processing, fraud detection
pipelines, **multi-currency ledger with ACID guarantees**, and jurisdiction-aware
notifications.

## What's distinctive

### The event store, in detail

Revolut's own writing fills this in `[reported]`:

- The messaging and event-streaming platform is **Kotlin on JetBrains Ktor with coroutines** —
  not Spring, and not Kafka.
- Most services store data in **PostgreSQL**; events are stored there too.
- Events use PostgreSQL's **`LISTEN`/`NOTIFY`** mechanism, so consumers can run *advanced SQL
  queries* against the event stream rather than replaying a log.
- Two instance roles: a **master for writing events**, **replicas for streaming and fetching**.
- The EventStore application is scaled **horizontally** behind a load balancer, instance count
  driven by load.

Revolut also publishes open source under `github.com/revolut-engineering`, including
**PgExposed**, a Kotlin PostgreSQL library.

**Why this matters.** Using Postgres `LISTEN`/`NOTIFY` as the event backbone instead of Kafka is
the single most distinctive architectural choice in this whole research set. It buys transactional
consistency between a state change and its event — the dual-write problem solved by construction —
and it makes the event stream *queryable*, which a log is not. The cost is a scaling ceiling you
must engineer around with read replicas and horizontal EventStore instances, exactly as described.

**A single Postgres event store as the spine.** Rather than Kafka-as-the-log, events are
persisted in one event store built on Postgres `[reported]`. That buys transactional
consistency between state change and event emission — the classic dual-write problem solved
by construction — at the cost of a scaling ceiling you have to engineer around.

**Multi-currency as a first-class ledger concern.** Most neobanks bolt FX on. Revolut's
product is FX, so the ledger models currency and liquidity-provider routing natively. Any
multi-currency design should start from the assumption that an account is
`(user, currency)`, not `user` with a currency attribute.

**PRAGMA.** Revolut published a foundation model for banking event streams: BERT-style
masked modelling over multi-source customer events (transactions, app events,
communications) tokenised as `(key, value, time)` triples, then reused via embedding probe
or LoRA for credit scoring, fraud detection and LTV prediction. This is the clearest
statement of the "foundation model for the bank's own event stream" thesis, and it converges
with Monzo's self-supervised embedding direction. A teaching-scale recreation of the recipe
exists as `pragma_mini.py` in the separate Mini PRAGMA repo (`~/Pragma LLM model`).

## Open questions

- Is Revolut's core ledger in-house end to end, or does any bought component sit under it?
- How does it shard the Postgres event store, and what is the current ceiling?
- Has PRAGMA been deployed in production decisioning, and with what measured lift?

## Sources

- Revolut Tech, Recording more events… but where will we store them? — https://medium.com/revolut/recording-more-events-but-where-will-we-store-them-4b1dad457cf5
- Revolut Tech, Under the Hood: Engineering at Revolut — https://medium.com/revolut/under-the-hood-engineering-at-revolut-2dc183c04228
- revolut-engineering/PgExposed — https://github.com/revolut-engineering/PgExposed
- Google Cloud, Revolut case study — https://cloud.google.com/customers/revolut-data
- StackShare, Revolut — https://stackshare.io/companies/revolut
- Netguru, Kotlin in fintech banking stacks — https://www.netguru.com/blog/tech-stack-for-a-fintech-app-or-replacement-for-java-in-banking-kotlin-is-here-to-rock
- Revolut engineering talent programmes — https://www.revolut.com/en-US/talent-programmes-engineering/
- LinkedIn discussion of Revolut neobank platform architecture — https://www.linkedin.com/posts/anton-hapieiev_revoluts-architecture-for-its-neobank-platform-activity-7092472594158764032-gRxd
- PRAGMA paper — https://arxiv.org/abs/2604.08649
