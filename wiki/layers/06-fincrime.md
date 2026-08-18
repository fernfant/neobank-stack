---
title: Financial crime — AML, transaction monitoring, fraud
type: layer
status: living
updated: 2026-08-18
sources: 12
tags: [fincrime, aml, fraud, transaction-monitoring, uk, usa]
---

## Summary

Three overlapping problems that vendors sell as one: **AML** (is this money dirty?),
**fraud** (is this person being robbed, or robbing us?), and **sanctions** (is this party
prohibited?). They have different latency budgets, different regulators, and different
failure costs. Monzo's redesigned platform is the best-documented public architecture and is
worth copying at the level of shape.

## Monzo's control platform — the reference implementation

Documented in Monzo's engineering blog and InfoQ `[confirmed]`. Four steps per transaction:

1. **Control selection** — pick applicable controls from transaction context, user
   behaviour, and risk scores.
2. **Feature loading** — a dedicated microservice supplies contextual data: transaction
   patterns, account history, fraud indicators.
3. **Control execution** — an Engine microservice runs controls as **pure functions written
   in Starlark**, which makes them safely testable and back-testable against history without
   touching live traffic.
4. **Action application** — an Action Applier enforces decisions and applies safeguards such
   as rate limits.

Controls come in three types: **detectors** (flag), **action controls** (recommend an
intervention), and **action-selection controls** (combine recommendations into one
decision). That separation is what lets a new control ship without blast radius.

Features are computed by a separate service over a **DAG pipeline** with three classes:
just-in-time (computed on demand), near-real-time (precomputed and cached), and batch
(periodic). Observability metadata for every control execution — input features, decision,
control metadata — lands in **BigQuery**, so effectiveness and false-positive rates are
measurable and controls can be iterated `[confirmed]`.

Scale context: roughly **1 in 10,000 transactions is fraudulent**, and UK Finance reported
£1.17bn of UK fraud losses in 2024 `[reported]`. Extreme class imbalance is the defining
modelling constraint.

Three things to steal from this design:

- **Controls as pure functions in a sandboxed language.** Deployable by risk analysts,
  back-testable, no production access needed.
- **Feature tiering by latency.** Not everything needs to be real-time; deciding which does
  is the whole performance budget.
- **Decision logs as a first-class product.** Every execution is an evidence record.

### What the models actually are (2026 primary sources)

Two Monzo posts move this past "they use ML" `[confirmed]`:

**Multi-task representation learning.** Input features pass through **3 shared feed-forward
layers**, then split into **3 heads** predicting fraud, payment method and fraud type. The fraud
head's output plus the original features feed a **LightGBM** model. ~**30% improvement over the
LightGBM baseline**, concentrated in rare subtypes; with entire subtypes withheld from training it
retained substantially higher recall. The mechanism is shared statistical strength — rare fraud
types borrow structure from common ones. This is the practical answer to the class-imbalance
problem that defines the domain.

**LLMs as feature extractors, never as deciders.** A five-stage pipeline: supervised models score
every transaction → high-risk cases trigger a customer questionnaire → a multimodal reasoning
model converts the responses into **structured semantic features** → a separate supervised model
scores those features independently → a **meta-stacking ensemble** combines the transaction-time
and questionnaire probabilities. Monzo's stated reasoning: LLMs are weak at calibrated
quantitative assessment and strong at structuring unstructured interaction. Measured live:
**+20% fraud cases caught and money prevented**, while *reducing* legitimate payments diverted to
human review.

That design is the current best answer to "can you put an LLM in the fincrime path?" — you can,
positioned so that the auditable decision is still made by a calibrated supervised model.

### Two implementation details from the primary source

- **Detectors are "typically machine learning models"** that output fraud type and confidence and
  deliberately do **not** prescribe an action `[confirmed]`. Separating prediction from
  intervention is what lets you retune one without the other.
- **The feature DAG degrades rather than fails**: it returns every feature it could load *plus the
  errors for those it could not*, with per-feature timeouts so one slow source cannot blow the
  latency budget `[confirmed]`. The Action Applier rate-limits per action type and alerts
  engineers when a threshold trips — a bug in a new control cannot cascade.

## Vendors

| Vendor | Category | Notes |
| --- | --- | --- |
| **Feedzai** | Enterprise fraud + AML at scale | Billions of transactions; reported 33% alert-rate reduction `[reported]`. Enterprise cost/implementation puts it out of reach for most fintechs `[reported]` |
| **ComplyAdvantage** | AI-native financial crime platform ("Mesh") | 3,000+ institutions, 75 countries; screening + TM + payment screening + fraud + case management on one risk-intelligence layer `[reported]`. Developer-friendly, fast to deploy — the common challenger choice |
| **Unit21** | No-code TM and case management | Reported 50–70% false-positive reduction, 44% faster alert review `[reported]`. Lets compliance change rules without engineering tickets |
| **Hawk AI** | Behavioural monitoring over existing real-time and batch flows `[reported]` | Good fit when you already have the pipelines |
| **Sardine** | Device fingerprinting, behavioural biometrics, consortium velocity data `[reported]` | Strongest at the *signal* layer rather than the case layer |
| **Featurespace** | Adaptive behavioural analytics | Long-standing UK/enterprise presence; less 2026 public material found |
| **NICE Actimize** | AML-first enterprise | Bank incumbent |
| **Sigma360, Flagright, Sanction Scanner, Salv** | Screening / mid-market TM | Low-code, weeks to deploy `[reported]` |

The market splits three ways `[reported]`: AML-first platforms for regulated FIs (Actimize,
ComplyAdvantage), fraud+AML hybrids built for fintechs (Feedzai, Sardine, Hawk AI, Unit21),
and simpler rules engines for lower volumes.

## Buy, build, or both

The honest answer for most: **buy case management and screening, build detection.**

- **Screening** (sanctions/PEP/adverse media) is a data problem with a regulatory SLA —
  OFAC within 24 hours of list updates `[reported]`. Buy the list and the matching engine.
- **Case management, SAR/SARs filing, audit trail** — buy. It is workflow software and
  building it wins you nothing. (US: FinCEN SAR; UK: NCA SARs.)
- **Detection** — build if fraud is material to your P&L, because your iteration speed on
  controls *is* your loss rate. Monzo, Revolut and Chime all build here.

## The UK's APP fraud regime changes the maths

Since **7 October 2024** UK PSPs must reimburse most APP fraud, capped at **£85,000**, with
cost split **50/50 between sending and receiving PSP** `[confirmed]`. The burden of proof is
on the PSP to show *gross negligence* — a higher bar than ordinary negligence `[reported]` —
and reimbursement must happen within five working days `[reported]`.

Independent evaluation published by the PSR on 1 July 2026 found APP fraud losses over
Faster Payments down ~21% (~£73m/yr), with 97% of in-scope claims reimbursed `[reported]`.

Two architectural consequences:

1. **You are liable for money your customer sends away voluntarily.** Outbound scam
   detection — not just inbound fraud — becomes a P&L line. This is why Monzo built a
   *reactive* prevention platform with in-flight interventions rather than post-hoc alerting.
2. **Receiving-side liability means mule detection matters as much as victim protection.**
   Your inbound-account risk model is now directly monetised.

The USA has no equivalent mandatory reimbursement regime, which is the single biggest
UK/USA divergence in fraud architecture. See [UK vs USA — where the stacks diverge](../comparisons/uk-vs-usa.md).

## Open questions

- Has any US regulator moved toward APP-style reimbursement liability for Zelle/RTP scams?
- What are realistic false-positive rates for a mature neobank TM stack in 2026, and what
  alert-per-analyst-per-day economics follow?
- ~~Is anyone running LLMs in the decisioning path?~~ **Answered by Monzo, July 2026**: LLMs
  generate structured features from customer questionnaires; a calibrated supervised model and a
  meta-stacking ensemble make the decision. Still open: how that is evidenced to the FCA, and
  which model is used.

## Sources

- Monzo, Building a reactive Fraud Prevention Platform — https://monzo.com/blog/build-a-reactive-fraud-prevention-platform
- Monzo, Representation Learning for Enhanced Fraud Detection — https://monzo.com/blog/representation-learning-for-enhanced-fraud-detection
- Monzo, Combining generative AI and predictive modelling to fight financial crime — https://monzo.com/blog/combining-generative-ai-and-predictive-modelling-to-fight-financial-crime
- InfoQ, Monzo's real-time fraud detection architecture — https://www.infoq.com/news/2025/11/monzo-real-time-fraud-detection/
- Monzo, Machine Learning at Monzo in 2025 — https://monzo.com/blog/machine-learning-at-monzo-in-2025
- cside, best transaction monitoring software 2026 — https://cside.com/blog/best-transaction-monitoring-software
- deepidv, top AML transaction monitoring platforms 2026 — https://www.deepidv.com/media/articles/top-10-aml-transaction-monitoring-platforms-2026
- Sphinx, best AML software 2026 — https://sphinxhq.com/blog-posts/best-aml-software
- PSR, APP fraud reimbursement requirements — https://www.psr.org.uk/news-and-updates/latest-news/news/psr-confirms-new-requirements-for-app-fraud-reimbursement/
- PSR / Frontier Economics evaluation coverage — https://www.crowdfundinsider.com/2026/07/290056-uk-payment-systems-regulator-psr-confirms-app-fraud-reimbursement-policy-delivers-strong-positive-results/
- A&O Shearman, the UK's APP fraud reimbursement scheme — https://www.aoshearman.com/en/insights/ao-shearman-on-fintech-and-digital-assets/the-uks-authorised-push-payment-app-fraud-reimbursement-scheme
- Freshfields, APP fraud mandatory reimbursement — https://www.freshfields.com/en/our-thinking/briefings/2024/09/authorised-push-payment-fraud-a-new-mandatory-reimbursement-regime-for-uk-psps
- Canarie, AML compliance for neobanks — https://www.canarie.ai/blog/aml-compliance-neobanks-guide
- Sigma360, sanctions screening tools 2026 — https://www.sigma360.com/sanctions-screening-tools/
