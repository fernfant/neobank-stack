---
title: Runtime and infrastructure
type: layer
status: living
updated: 2026-08-18
sources: 8
tags: [infrastructure, cloud, kubernetes, languages]
---

## Summary

There is more convergence here than anywhere else in the stack: containers on Kubernetes, a
statically-typed backend language, a horizontally-scalable datastore, and one primary cloud.
The differences that matter are language choice (which shapes hiring and service granularity)
and datastore choice (which shapes the ledger's consistency model).

## What the public record shows

| Bank | Language(s) | Runtime | Datastore | Cloud |
| --- | --- | --- | --- | --- |
| **Monzo** | Go `[confirmed]` | **EKS**, Docker, monorepo; **>3,000 services**; Linkerd RPC; Kafka `[confirmed]` | Cassandra `[confirmed]`; BigQuery warehouse | AWS `[confirmed]`, GCP for analytics `[reported]` |
| **Starling / Engine** | Java `[reported]` | Docker with embedded web server; Kubernetes; ~20 services in 2018 `[reported]` `[dated: 2018]` | Postgres, Elasticsearch `[reported]` | AWS primary, some GCP `[reported]` |
| **Revolut** | Java, Kotlin, Spring Boot; **Ktor + coroutines** for the event platform `[reported]` | Kubernetes `[reported]` | **PostgreSQL event store using `LISTEN`/`NOTIFY`**; master writes, replicas stream `[reported]` | GCP `[reported]` |
| **N26** | Kotlin, Java, Spring Boot `[confirmed]` | Nomad/Consul/Vault → **Kubernetes**; Traefik ingress, Envoy sidecars, Consul DNS, AWS NLB; 60+ services, 100+ deploys/week in 2018 `[confirmed]` | Not publicly named | AWS `[confirmed]` |
| **Chime** | Not public; React Native mobile `[confirmed]` | **EKS**, ~**1,000 deploys/day**, Argo CD + Helm + Terraform, App-of-Apps `[confirmed]` | **CoreDB — MySQL on RDS, 40TB, 30k connections** `[confirmed]`; Snowflake warehouse `[reported]` | AWS, **>2PB** egress `[confirmed]` |
| **SoFi** | Kotlin + Spring Boot; **GraphQL BFF**; **Flutter** mobile (~2.5m lines) `[reported]` | — | Snowflake data mesh `[reported]` | — |
| **Remitly** | Java, Kotlin, Go `[reported]` | Microservices `[reported]` | PostgreSQL, Amazon Aurora `[reported]` | AWS `[reported]` |

Frontend is near-universal: React/TypeScript web, native Swift iOS and Kotlin Android;
Remitly uses Kotlin Multiplatform `[reported]`.

## The Go-vs-JVM fork

**Updated service count.** Monzo's May 2026 platform post states it migrated **>3,000
microservices** onto a new **EKS** cluster using a purpose-built Migrator service `[confirmed]`.
The widely-repeated "1,600" figure is stale; the estate roughly doubled and has not consolidated.

What makes that survivable is not the services but the **platform abstraction layer**: rather than
giving engineers raw infrastructure access, Monzo wraps each capability in an owned service with
an opinionated interface — for example `service.karpenter`, which exposes the Kubernetes
autoscaler through RPC gated by **multi-party approval** `[confirmed]`. Everything lives in a
monorepo with common build, deploy and operate patterns.

The 2016 foundations are still visible `[confirmed]` `[dated: 2016]`: Kubernetes on CoreOS on AWS
(after ~a year on Mesos/Marathon, which cut infrastructure spend to ~25% of previous), **Linkerd**
for RPC — Power of Two Choices + Peak EWMA load balancing, automatic retry budgets for idempotent
requests, deployed as Kubernetes daemon sets — and **Kafka** as a replayable at-least-once commit
log. Polyglot by design (Go primary; Java, Python, Scala supported) with RPC as the boundary.

Monzo's stated reason for Go: "quite simple, statically typed, and it makes it easy for us to
get people on board" `[reported]`. That choice interacts with service granularity — Monzo
runs on the order of **1,600–2,800 microservices** `[reported]`, a number only tractable
because service creation is cheap and the shared RPC and deployment tooling is bespoke and
excellent. Monzo built its own RPC libraries in Go `[reported]`.

The JVM houses (Starling, Revolut, Remitly) run far fewer, larger services. Neither is wrong.
The question to ask is: *what is your cost of creating and operating one more service?* If it
is high, do not adopt a Monzo-shaped topology; you will get the distributed-systems tax with
none of the tooling that pays for it.

## Datastore and the consistency question

- **Cassandra (Monzo)** — chosen for horizontal scalability `[reported]`. Public numbers:
  **300,000 reads/second at peak**, **500+ services** each with its own keyspace (the ledger's is
  `service.ledger`), and **2,300+ clients** `[confirmed]`. Access is secured with **HashiCorp
  Vault**-issued dynamic credentials expiring weekly and renewed at ~80% of their life; Monzo
  forked Vault's database plugin to key credentials off Kubernetes ServiceAccount annotations, and
  cut bcrypt rounds from 10 to 4 (64× faster auth) using 95-bit-entropy random passwords to make
  short-lived credentials affordable. The cost is that
  strong multi-key transactions are not available, so ledger correctness must be constructed
  from idempotency, careful partitioning, and application-level invariants. Monzo's public
  material on running Cassandra on Kubernetes is the deepest available account of this
  trade-off.
- **Postgres event store (Revolut)** — an event-sourced architecture over Postgres, with
  services communicating via persisted events `[reported]`. Strong per-transaction guarantees
  and a natural audit log; scaling is a sharding problem rather than a consistency one.
- **Aurora (Remitly)** — managed Postgres/MySQL-compatible, chosen on operational grounds
  `[reported]`.

**Two datapoints worth sitting with.** Chime's core financial store is **MySQL on RDS at 40TB** —
utterly conventional, and it serves millions of members. Revolut's event backbone is **PostgreSQL
`LISTEN`/`NOTIFY`**, not Kafka, which solves the dual-write problem by construction and makes the
event stream queryable. Neither is exotic. The exotic choice in this set is Monzo's Cassandra, and
it is the one that demanded the most bespoke operational investment.

For a new build in 2026 the defensible defaults are: Postgres (or Aurora/Spanner/CockroachDB
if you need horizontal scale with transactions) for the ledger, and something
horizontally-scalable for the high-volume append-only event data. Reach for Cassandra only
if you are prepared to own the operational practice.

## Cloud

### Monzo's cross-cloud link, and what it enables

Monzo runs AWS for production and GCP for analytics — and connects them **privately** rather than
over the internet `[confirmed]`. **AWS Direct Connect** on one side, **GCP Interconnect** on the
other, bridged by a **Megaport** virtual router in a colocation facility, all managed in Terraform.
They modified their open-source **`egress-operator`** to route 26 specific Google API endpoints
over the private link, intercepting at the Kubernetes layer rather than by DNS hijacking, with
automatic failover to internet routing if the private path degrades. Saving: ~**60% of GCP egress
NAT gateway cost**.

Worth noting the through-line: this cross-cloud plumbing, built in 2022 to cut egress cost, is the
same foundation that makes a **GCP-hosted Stand-in platform** viable — see
[Resilience, regulatory reporting and operations](../layers/10-resilience-regulatory.md). (Chime solved the identical NAT-gateway cost problem the
other way, self-managing NAT instances and open-sourcing `ha-nat` — see [Chime (USA)](../banks/chime.md).)

### Load spikes are a scheduling problem, not an autoscaling one

Monzo's "Get Paid Early" feature lets customers pull Bacs credits at 4pm the day before they are
due, producing **up to a 500% traffic increase in seconds** across up to 250,000 eligible payments
— and then a cascade as those customers immediately pay bills, move money into pots and withdraw
cash `[confirmed]`. Reactive autoscaling "simply can't react quickly enough".

The answer was **predictive pre-scaling**: forecast the day's demand from the incoming **Bacs
records themselves**, size it against historical CPU in Prometheus, and use **Jaeger** distributed
traces to identify *every* downstream service that needs headroom — then scale up before the event
and back down after. If your load spikes are scheduled by an external rail, you already know the
future; use it.

AWS dominates the UK neobank set; Revolut is the notable GCP house `[reported]`. Engine by
Starling is AWS-first with some GCP and markets itself explicitly on AWS `[reported]`.

The regulatory overlay matters as much as the technical one: DORA and the FCA/PRA's
operational resilience regime require concentration-risk assessment and documented exit
strategies for critical ICT providers (DORA Articles 28, 29, 30) `[reported]`. The ECB found
more than 30% of significant banks' outsourcing budgets concentrated on ten providers
`[reported]`. You will be asked how you exit your cloud provider. "We can't" is not an
answer that survives an examination, but neither is a fictional multi-cloud plan — see
[Resilience, regulatory reporting and operations](../layers/10-resilience-regulatory.md).

## Open questions

- ~~Has Monzo's microservice count stabilised?~~ **Answered: >3,000 and growing** `[confirmed]`.
- Is Linkerd still the RPC layer in 2026, or has it been replaced?
- ~~What is Chime's runtime stack?~~ **Answered: AWS EKS, Argo CD/Helm/Terraform, ~1,000
  deploys/day, CoreDB on MySQL/RDS** `[confirmed]`. Backend *language* still unknown.
- Is Monzo's Linkerd RPC layer still in place in 2026, or replaced?
- How many Cassandra nodes and how much data? Read throughput is public; cluster size is not.
- What datastore sits under N26's services? Never named publicly.
- Is anyone running the ledger on a distributed SQL store (Spanner, CockroachDB, TiDB) in
  production at a licensed bank?

## Sources

- Monzo, We secured thousands of Cassandra clients — https://monzo.com/blog/we-secured-thousands-of-cassandra-clients-to-keep-monzos-data-safe
- Monzo, Reducing NAT Gateway cost with private networking between AWS and GCP — https://monzo.com/blog/2022/11/25/reducing-nat-gateway-cost-with-private-networking-between-aws-and-gcp
- Monzo, Preparing for spikes in traffic as millions get paid early — https://monzo.com/blog/2023/01/26/preparing-for-spikes-in-traffic-as-millions-get-paid-early
- Monzo, The Engineering Behind the Platform — https://monzo.com/blog/the-engineering-behind-the-platform
- Monzo, Building a Modern Bank Backend — https://monzo.com/blog/2016/09/19/building-a-modern-bank-backend
- The Register, How Monzo keeps 1,600 microservices spinning — https://www.theregister.com/2020/03/09/monzo_microservices/
- InfoQ, Cassandra, Kubernetes and microservices at Monzo — https://www.infoq.com/articles/cassandra-kubernetes-microservices/
- InfoQ, Modern Banking in 1500 Microservices — https://www.infoq.com/presentations/monzo-microservices/
- AWS, Monzo cloud-native core banking on EKS and Keyspaces — https://www.youtube.com/watch?v=O3s3MWD-UUA
- Container Solutions, Starling: How to Build a Bank in a Year — https://blog.container-solutions.com/starling-how-to-build-a-bank-in-a-year
- Chime, How We Upgraded Our Core Database with Just 5 Minutes of Downtime — https://careers.chime.com/life-at-chime/how-we-upgraded-our-core-database-with-just-5-minutes-of-downtime/
- Chime, How We Preview Kubernetes Changes at Chime — https://careers.chime.com/life-at-chime/how-we-preview-kubernetes-changes-at-chime/
- N26, Kubernetes and Site Reliability at N26 — https://n26.com/en-eu/blog/kubernetes-and-site-reliability-at-n26-an-engineering-success-story
- N26, Tech at N26 — The Bank in the cloud — https://n26.com/en-eu/blog/tech-at-n26-the-bank-in-the-cloud
- Revolut Tech, Recording more events… but where will we store them? — https://medium.com/revolut/recording-more-events-but-where-will-we-store-them-4b1dad457cf5
- Engine by Starling platform overview — https://enginebystarling.com/platform/
- TEKsystems, Remitly Amazon Aurora migration — https://www.teksystems.com/en/insights/success-stories/remitly-amazon-aurora
- Regulation-DORA, cloud exit strategies and concentration risk — https://www.regulation-dora.eu/blog/cloud-exit-strategy-concentration-risk-dora
