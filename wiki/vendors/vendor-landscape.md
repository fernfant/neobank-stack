---
title: Vendor landscape
type: vendor
status: living
updated: 2026-08-18
sources: 15
tags: [vendors, procurement, uk, usa]
---

## Summary

One table per layer. **Caveat before you read any of it:** most published vendor comparisons
in this sector are SEO content marketing produced by vendors or their agencies. Everything
below is `[reported]` unless a company or regulator said it. Use this as a *shortlist
generator*, never as a decision.

## Core banking / ledger

| Vendor | Type | Geo | Known users |
| --- | --- | --- | --- |
| Thought Machine Vault Core | Cloud-native core, Smart Contracts DSL | UK/global | Lloyds, Standard Chartered, Intesa Sanpaolo, Zopa, Atom, C6, Trust Bank |
| 10x SuperCore | Cloud-native core, polyglot runtime, migration tooling | UK/global | Chase UK, Westpac |
| Temenos Transact | Established core, cloud-hosted | Global | Varo, ~950 banks |
| Mambu | SaaS core, lending-strong, composable | EU/global | N26, ABN AMRO |
| Galileo Cyberbank Core | Core + issuing + sponsor banking | US/LatAm | SoFi |
| Engine by Starling | Bank-proven SaaS platform | UK, expanding US | Starling itself + clients |
| Tuum | Modular API core | EU | European banks/fintechs |
| Finxact (Fiserv) | US-first real-time core | US | Mercantile, Live Oak |
| TigerBeetle | Purpose-built ledger DB (OSS) | — | Self-hosted |
| Formance Ledger | OSS double-entry ledger, Numscript; sidecar pattern | — | Self-hosted / managed |
| Blnk | OSS double-entry ledger | — | Self-hosted |

## Card issuing / processing

| Vendor | Position |
| --- | --- |
| Marqeta | Largest independent issuer-processor; ~$383bn processed 2025; TransactPay acquisition added UK/EU BIN sponsorship |
| Galileo | Visa-certified processor; long neobank roster; SoFi-owned |
| Lithic | Developer-first US issuing; >$1bn/month |
| Highnote | Issuing + acquiring on one API and one ledger |
| Thredd | International; >2bn txns/yr, 130+ clients, 50+ countries |
| i2c, Wallester, Monavate, Stripe Issuing | Segment alternatives; Stripe Issuing fastest for virtual cards |

## Identity / KYC / KYB

| Vendor | Best for |
| --- | --- |
| Persona | Highly configurable onboarding flows |
| Socure | Identity fraud, synthetic identity, risk decisioning (US-centric) |
| Alloy | Orchestration across multiple data partners |
| Onfido (Entrust IDV) | Document depth; regulated-bank integrations; UK/EU incumbent |
| Jumio | Broad document coverage, mature liveness; higher price |
| Sumsub, Veriff, Trulioo, IDnow, GBG, Shufti, Signzy | Regional depth / price |

## Financial crime — TM, screening, case management

| Vendor | Category |
| --- | --- |
| Feedzai | Enterprise fraud + AML at massive scale |
| ComplyAdvantage (Mesh) | AI-native platform: screening + TM + payment screening + fraud + case mgmt |
| Unit21 | No-code TM + case management |
| Hawk AI | Behavioural monitoring over existing real-time and batch flows |
| Sardine | Device fingerprinting, behavioural biometrics, consortium velocity data |
| Featurespace | Adaptive behavioural analytics |
| NICE Actimize | AML-first enterprise incumbent |
| Sigma360, Flagright, Sanction Scanner, Salv, Alessa | Screening / mid-market TM |

## Credit data and decisioning

| Vendor | Role |
| --- | --- |
| Experian, Equifax, TransUnion | Bureaus (both markets) |
| FICO | Scores incl. cash-flow UltraFICO (with Plaid, Nov 2025) |
| VantageScore | Alternative US score |
| Plaid | Consumer-permissioned bank data, income verification, LendScore |
| Nova Credit | Cash Atlas / NovaScore Cash Flow; cross-border credit |
| Ocrolus, MeridianLink, eNoah | Cash-flow / document data |
| Oscilar, Taktile, Provenir | Decision engines |

## Payments infrastructure and access

| Vendor | Role |
| --- | --- |
| ClearBank, LHV, Banking Circle | UK/EU agency access to FPS/Bacs/CHAPS/SEPA |
| Modulr, Form3 | Payments-as-a-service, scheme connectivity |
| Dwolla, Moov, Increase | US ACH/RTP/FedNow access |
| Visa Direct, Mastercard Send | Push-to-card disbursement |
| Bridge (Stripe), BVNK (Mastercard), Circle | Stablecoin settlement rails |

## Data / ML infrastructure

| Vendor | Role |
| --- | --- |
| Confluent / Apache Kafka | Event backbone |
| Apache Flink | Stateful stream processing for real-time features |
| BigQuery, Snowflake, Databricks | Warehouse / lakehouse |
| dbt | Transformation |
| Redis, DynamoDB | Online feature serving |
| Tecton, Feast | Feature stores |

## Procurement questions that actually separate vendors

1. Who is the **regulated entity** in this arrangement, and what happens to my customers if
   you exit the business? (Post-Synapse, this is question one.)
2. Can I get my **raw postings and decision logs** out, continuously, in a format I control?
3. What is your **incident history** and will you contract to an SLA with teeth?
4. What is the **exit plan**, contractually (DORA Art. 30), and has anyone actually executed it?
5. Where does **product logic** live — in your DSL, or in my code? What is the migration cost
   if I leave?
6. What is the **latency distribution** (p99, p99.9) of the hot-path call, measured, not
   marketed?
7. Are your other customers my competitors, and what is your policy on that?

## Sources

- 10x Banking, core banking platforms compared — https://www.10xbanking.com/core-banking-platforms-compared
- SDK.finance, core banking software list — https://sdk.finance/blog/top-core-banking-software-list/
- OpenBankingTracker, banktech providers — https://www.openbankingtracker.com/banktech-providers
- OpenBankingTracker, card issuing — https://www.openbankingtracker.com/embedded-finance/category/card-issuing
- Highnote, issuing platform comparison — https://highnote.com/blog/stripe-issuing-vs-marqeta-vs-highnote-enterprise-comparison-guide
- Zyphe, identity verification comparison 2026 — https://www.zyphe.com/resources/blog/identity-verification-software-comparison-2026
- cside, transaction monitoring software 2026 — https://cside.com/blog/best-transaction-monitoring-software
- Sphinx, best AML software 2026 — https://sphinxhq.com/blog-posts/best-aml-software
- Sigma360, sanctions screening tools — https://www.sigma360.com/sanctions-screening-tools/
- Plaid, alternative credit data — https://plaid.com/resources/lending/alternative-credit-data/
- FICO × Plaid — https://www.fico.com/en/newsroom/fico-partners-plaid-launch-next-generation-cash-flow-ultrafico-score
- Nova Credit — https://www.novacredit.com/corporate-blog/introducing-the-novascore-cash-flow-the-future-of-consumer-credit-risk
- Kai Waehner, data streaming landscape 2026 — https://www.kai-waehner.de/blog/2025/12/05/the-data-streaming-landscape-2026/
- Formance — https://www.formance.com/blog/financial-operations/core-banking-system-architecture
- Trio, payment ledger architecture — https://trio.dev/payment-ledger-architecture-fintech/
