---
title: Deep dive — Fraud and AML detection (build)
type: deep-dive
status: living
updated: 2026-08-18
sources: 12
tags: [fincrime, fraud, aml, build, feature-store, open-source]
---

## Summary

Two public architectures define the state of the art, and they agree on the shape: **Monzo's
control platform** and **Stripe Radar**. Both put a model and a rules layer inside the hot path
under a hard latency budget, both separate scoring from decisioning, and both treat the decision
log as a first-class product. The buy-to-launch advice holds — but in the UK, APP reimbursement
liability makes "later" arrive on day one.

The 2026 development that changes the build calculus: the feature platform underneath this is
now **open source and battle-tested**, and so are two credible transaction-monitoring cores.

## Real implementation 1 — Monzo

Documented across Monzo's engineering blog and InfoQ `[confirmed]`. Four steps per transaction:

1. **Control selection** from transaction context, user behaviour and risk scores
2. **Feature loading** by a dedicated microservice
3. **Control execution** — controls run as **pure functions written in Starlark** inside an
   Engine microservice, making them safely testable and **back-testable against history without
   touching live traffic**
4. **Action application** — an Action Applier enforces decisions and applies safeguards such as
   rate limits

Controls are typed into three kinds — **detectors** (flag), **action controls** (recommend an
intervention), **action-selection controls** (combine recommendations into one decision). That
separation is what lets a new control ship without blast radius.

Features come from a separate service over a **DAG pipeline** in three latency tiers:
just-in-time, near-real-time (precomputed and cached), batch. Per-execution metadata — input
features, decision, control version — lands in **BigQuery** so effectiveness and false-positive
rates are measurable `[confirmed]`.

Scale context: roughly **1 in 10,000 transactions is fraudulent**, against £1.17bn of UK fraud
losses in 2024 `[reported]`.

## Real implementation 2 — Stripe Radar

Three layers `[reported]`:

| Layer | Job |
| --- | --- |
| **Feature extraction** | Signals from the incoming transaction and from recent history |
| **Model serving** | Trained model produces a risk score |
| **Decision** | Score plus merchant-specific rules → allow / block / challenge |

Runs on every transaction **inside the authorisation path with a sub-100ms budget**. Notable
engineering detail: Stripe moved **off XGBoost** because it was incompatible with techniques
they wanted — transfer learning and embeddings — and adopted an architecture inspired by
**ResNeXt** `[reported]`. Labels arrive automatically when cardholders dispute charges, which is
the structural advantage: a free, continuous, correctly-timed label stream. Reported outcome:
fraud volume down >50% with false positives also down `[reported]` — vendor's own figure.

The pattern to copy is the **rules-on-top-of-score** design. The model produces a number; the
customer-specific or product-specific policy decides what to do with it. Same
model/policy separation as [Deep dive — KYC orchestration (build)](../deep-dives/03-kyc-orchestration.md) and [Credit and decisioning](../layers/07-credit-scoring.md).

## The feature platform — now open source

This is the most consequential 2026 finding for anyone deciding build-vs-buy here.

**Chronon** is Airbnb's declarative feature-engineering framework, which centralises feature
computation for **both offline training and online low-latency serving** — the single-definition
property that eliminates training/serving skew. It began life as *Zipline*, and it was **first
deployed at Airbnb specifically to combat payments fraud** `[reported]`. It is now Apache 2.0.

The datapoint that matters: **Stripe integrated Chronon, and it powers 100% of Stripe's
charge-path fraud prediction models** `[reported]`. A neobank building a fraud feature platform
in 2026 can start from the same substrate two of the most sophisticated payments fraud teams in
the world use.

Alternatives:

| Package | Position |
| --- | --- |
| **Chronon** | Apache 2.0; declarative; one definition for batch and streaming; fraud-origin `[reported]` |
| **Feast** | Open source; benchmarked at **sub-millisecond** retrieval with a Java gRPC server and Redis `[reported]`. Cost control and no lock-in |
| **Tecton** | Managed; **sub-10ms p99** serving out of the box; positioned squarely at real-time fraud `[reported]` |
| **Hopsworks** | Self-hosted or managed; "often the leading, and sometimes only, choice" in finance, healthcare and government — i.e. where data cannot leave `[reported]` |

Monzo's three-tier taxonomy maps onto any of them; the tiering is the design, the product is the
implementation.

## The control-execution engine — what Monzo's Starlark choice really is

Monzo's insight generalises: **risk controls should be sandboxed pure functions in a small
embeddable language**, so they can be authored by risk analysts, evaluated deterministically,
back-tested against history, and deployed without a service release.

Options if you build this:

| Language / engine | Why |
| --- | --- |
| **Starlark** (`starlark-go`) | Google's Python-like config language. Deterministic, sandboxed, no I/O, hermetic — exactly the properties back-testing needs. Monzo's choice `[confirmed]` |
| **Open Policy Agent / Rego** | Embeddable as a Go library; returns structured decisions including **risk scores**, not just allow/deny; policy fully decoupled from application code `[reported]` |
| **CEL** (Common Expression Language) | Google; designed for fast, safe, sub-millisecond expression evaluation in hot paths |
| **GoRules ZEN / Drools / Camunda DMN** | Decision tables when the authors are analysts rather than engineers `[reported]` |

The choice matters less than the four properties: deterministic, sandboxed, versioned,
back-testable.

## Open-source transaction-monitoring cores

Genuinely new options, worth knowing before signing a vendor contract:

| Project | Notes |
| --- | --- |
| **Marble** (`checkmarble/marble`) | "Real-time decision engine for fraud and AML" — transaction monitoring, screening and case investigation, with an **open-source core**, deployable on-premise or as SaaS. Positions itself directly as an alternative to ComplyAdvantage, Actimize and Fiserv `[reported]` |
| **Jube** | Open source (**AGPLv3**) real-time transaction monitoring with ML, aimed at AML compliance and fraud; fully containerised (Docker, Kubernetes), multi-tenant `[reported]` |
| **Tazama** | A charity-run open-source transaction monitoring system built around **ISO 20022** messages `[reported]` — relevant given the UK's ISO 20022 direction |

None of these removes the need for a compliance function, curated list data, or a filed SAR
workflow. What they remove is the argument that the *engine* must be bought.

## Network and entity analysis — the mule problem

The UK's 50/50 receiving-side APP liability makes **inbound mule detection** directly monetised,
and mule networks are a graph problem, not a per-transaction one.

- **Splink** — UK Ministry of Justice, open source, Fellegi-Sunter probabilistic linkage; a
  million records in about a minute on a laptop, 100m+ on Spark/Athena `[reported]`
- **Senzing** — commercial, embedded; explicitly targets fraud rings `[reported]`
- **Quantexa** — commercial; entity resolution plus network graph analytics over billions of
  data points `[reported]`
- **Zingg**, **Neo4j**, **AWS Entity Resolution** — other points on the curve

## Screening

**OpenSanctions + yente**, self-hosted as two Docker containers, covering sanctions, PEPs and
custom watchlists with no customer data leaving your infrastructure `[confirmed]`. Detail in
[Deep dive — KYC orchestration (build)](../deep-dives/03-kyc-orchestration.md). Note the hard obligation it must satisfy: OFAC screening at
onboarding, ongoing, and **within 24 hours of list updates** `[reported]`.

## Vendors — and what you are actually buying

| Vendor | Category |
| --- | --- |
| **Feedzai** | Enterprise fraud + AML at massive scale; reported 33% alert-rate reduction. Cost and implementation put it out of reach for most fintechs `[reported]` |
| **ComplyAdvantage (Mesh)** | Screening + TM + payment screening + fraud + case management on one risk-intelligence layer; 3,000+ institutions, 75 countries. The common challenger choice `[reported]` |
| **Unit21** | No-code TM and case management; reported 50–70% false-positive reduction, 44% faster alert review `[reported]` |
| **Hawk AI** | Behavioural monitoring over existing real-time and batch flows `[reported]` |
| **Sardine** | Device fingerprinting, behavioural biometrics, consortium velocity data — strongest at the **signal** layer `[reported]` |
| **Featurespace** | Adaptive behavioural analytics; long-standing UK/enterprise presence |
| **NICE Actimize** | AML-first bank incumbent |
| **Flagright, Salv, Alessa, Sigma360, Sanction Scanner** | Mid-market TM and screening; low-code, weeks to deploy `[reported]` |

The durable split: **buy case management, SAR/SARs filing and list data; build detection.**
Case management is workflow software and building it wins nothing. Detection is where your
iteration speed *is* your loss rate.

## The UK forcing function

Since 7 October 2024, UK PSPs must reimburse most APP fraud up to **£85,000**, split **50/50**
between sending and receiving PSP, with the burden on the PSP to prove gross negligence and
reimbursement within five working days `[confirmed]`. The PSR's July 2026 evaluation found APP
losses over Faster Payments down ~21% (~£73m/yr) with 97% of in-scope claims reimbursed
`[reported]`.

Consequences for the architecture, not just the policy:

1. **In-flight intervention, not post-hoc alerting.** The control must be able to warn, add
   friction, or block *before* the payment leaves — Monzo's "reactive" platform design.
2. **Inbound mule detection is revenue.** Receiving-side liability means your inbound risk model
   has a direct P&L line.
3. **Evidence, because you carry the burden of proof.** Proving gross negligence requires the
   warning you showed, when, and what the customer did next — logged immutably.

## Open questions

- Is anyone running an LLM **in the decisioning path** (not alert-narrative generation), and how
  is it evidenced to a regulator?
- Realistic false-positive rates and alerts-per-analyst-per-day for a mature neobank stack.
- Has any US regulator moved toward APP-style reimbursement for Zelle/RTP scams?
- Which neobanks, if any, run Chronon or Feast rather than a bespoke feature service?
- What is Marble or Jube's largest known production deployment? Neither publishes references.

## Sources

- Monzo, Building a reactive Fraud Prevention Platform — https://monzo.com/blog/build-a-reactive-fraud-prevention-platform
- InfoQ, Monzo's real-time fraud detection architecture — https://www.infoq.com/news/2025/11/monzo-real-time-fraud-detection/
- Monzo, Machine Learning at Monzo in 2025 — https://monzo.com/blog/machine-learning-at-monzo-in-2025
- ByteByteGo, how Stripe detects fraudulent transactions within 100ms — https://blog.bytebytego.com/p/how-stripe-detects-fraudulent-transactions
- Stripe, a primer on machine learning for fraud detection — https://stripe.com/guides/primer-on-machine-learning-for-fraud-protection
- Airbnb Tech Blog, Chronon is now open source — https://medium.com/airbnb-engineering/chronon-airbnbs-ml-feature-platform-is-now-open-source-d9c4dba859e8
- Chronon project — https://chronon.ai/
- ZenML, Zipline/Chronon feature platform infrastructure — https://www.zenml.io/llmops-database/building-agents-for-high-stakes-production-systems-with-feature-platform-infrastructure
- checkmarble/marble — https://github.com/checkmarble/marble
- Jube, open-source AML and fraud transaction monitoring — https://jube.io/learn-more/
- OpenSanctions, open building blocks for financial crime — https://www.opensanctions.org/docs/opensource/fincrime/
- PSR, APP fraud reimbursement requirements — https://www.psr.org.uk/news-and-updates/latest-news/news/psr-confirms-new-requirements-for-app-fraud-reimbursement/
