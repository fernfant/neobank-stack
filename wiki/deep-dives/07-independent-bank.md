---
title: Deep dive — Building an independent bank, layer by layer
type: deep-dive
status: living
updated: 2026-08-19
sources: 22
tags: [greenfield, licence, principal-member, vendors, uk, decisions]
---

## Summary

The hardest configuration, and the one with the fewest shortcuts: **your own banking licence, your
own Bank of England settlement account, your own Visa/Mastercard principal membership.** No sponsor
anywhere. Ten layers, each with a decision, a build option and real vendor alternatives.

The through-line: *owning* a layer and *building* a layer are different things. You can hold
principal membership and still buy the processor. You can be a direct participant and still buy the
gateway technology. Independence is about **who the regulated entity is**, not about writing all
the code.

---

## Layer 01 — Licence and authorisation

**The decision:** full bank licence (PRA + FCA) versus EMI.

Since the premise is *no sponsor and you hold deposits*, this is a bank licence. The UK route is
**two-stage mobilisation** `[reported]`: authorisation with restrictions and **~£1m capital**,
during which you complete build and testing, then full authorisation at **£5m initial capital**
with restrictions lifted.

| Option | Notes |
| --- | --- |
| **Bank licence via mobilisation** | The only route if you hold deposits with FSCS protection |
| **EMI first, bank later** | Ship on safeguarded e-money, convert later. Cheaper start, but a migration you will pay for twice |
| **Acquire a licensed entity** | Fastest, rarely available, and you inherit their systems and their supervisory history |

**What it forces:** capital planning, Basel 3.1 under the PRA's 2026 programme, ICAAP/ILAAP,
SM&CR, board composition, and a treasury function you did not have. Treat mobilisation as an
**engineering phase with exit criteria** — it is the one period where you can rehearse migration
and reconciliation with a bounded blast radius.

---

## Layer 02 — Scheme and rail membership

**The decision:** you have said no sponsor, which means **Directly Connected Settling Participant**
on the payment schemes and **principal membership** on the card schemes. Two separate applications
to two separate kinds of institution.

**Payment rails.** A Bank of England **settlement account**, RTGS access, and direct participation
in Faster Payments, Bacs and CHAPS via Pay.UK. Settlement is **prefunded** into a segregated,
interest-bearing account at the Bank `[reported]`. The **July 2026 flexible Net Sender Cap model**
materially reduced that prefunding burden — if your business case predates it, redo the numbers.

**Card schemes.** Principal membership requires your licence *plus* collateral, scheme
certification, operational infrastructure and **ongoing dues into the millions of euros annually**
`[reported]`. This is the line item founders most often miss.

**Connectivity — and an important nuance.** Being a direct participant does not mean writing the
gateway. You can settle in your own name and still buy the technology:

| Option | Notes |
| --- | --- |
| **Build it** | Monzo's Go monolith: active-active over two data centres, DRBD, four HSMs, store-and-forward stand-in. See [Deep dive — Monzo payments, end to end](../deep-dives/06-monzo-payments.md) |
| **Form3** | Cloud-native managed payments-as-a-service across UK, EU and US rails `[reported]` |
| **Icon Solutions (IPF)** | Highly customisable payments framework; connected to TCH and SEPA Inst `[reported]` |
| **Volante** | Cloud-native payment hub for mid-to-large institutions — RTP, FedNow, wires, SEPA Inst, cross-border `[reported]` |
| **ACI Worldwide, Finastra** | Incumbent payment hubs |

**Using Form3 or Icon while you settle yourself is not sponsorship.** You remain the participant
and the regulated entity; they supply the pipe. That distinction is worth making explicitly in
board papers, because "we use Form3" is often misheard as "we are indirect".

---

## Layer 03 — Core banking and ledger

**The decision:** build, buy, or buy-with-a-sidecar.

| Option | Notes |
| --- | --- |
| **Thought Machine Vault Core** | Products as Smart Contracts (Python-flavoured DSL). Zopa, Atom, Lloyds, Standard Chartered |
| **10x SuperCore** | Polyglot runtime, built-in migration tooling. Chase UK, Westpac |
| **Temenos Transact** | Most widely deployed; Varo at charter go-live |
| **Mambu** | SaaS, lending-strong, composable. N26, ABN AMRO. 260+ customers |
| **Tuum · Finxact (Fiserv) · Engine by Starling** | Modular API cores; Engine is bank-proven rather than multi-tenant by design |
| **Build on OSS** | **TigerBeetle** (double-entry as the schema), **Formance** (Numscript, sidecar pattern), **Blnk** |
| **Build entirely** | Monzo, Starling, Revolut. Months of engineering for the ledger, years for reconciliation and operations |

**What it forces:** the six invariants (sum-to-zero, postings-as-truth, append-only, idempotent,
bi-temporal, hierarchical account paths) and — the one nobody plans for — **balance checkpointing**.
See [Core ledger and product engine](../layers/02-core-ledger.md).

---

## Layer 04 — Card issuing, with your own BIN

You hold principal membership, so **no BIN sponsor is needed**. What remains is processing and a
physical supply chain.

**Issuer processing:**

| Option | Notes |
| --- | --- |
| **Thredd** | 2bn+ transactions/yr, 50+ countries. Curve, Zilch, Revolut, Starling |
| **Marqeta** | Largest independent; Just-in-Time funding; TransactPay gives UK/EU programme management you may not need if you are your own principal |
| **Galileo** | SoFi-owned — note it also serves your competitors |
| **Enfuce · i2c · Wallester** | European and mid-market alternatives |
| **Build** | Monzo and Chime both did, after volume made the fee the top cost line |

**Payment HSMs** — mandatory, and a real procurement:

| Vendor | Notes |
| --- | --- |
| **Thales payShield** | ~30.5% category mindshare, FIPS 140-2 Level 3, ~1,000 TPS, PCI SSC and EMVCo compliant `[reported]` |
| **Futurex** | ~17.1% and rising fast; FIPS L3 and PCI HSM validated; payment plus general-purpose `[reported]` |
| **Utimaco** | European, Atalla AT1000; strong data-sovereignty positioning `[reported]` |

**Card manufacture and personalisation:**

| Vendor | Notes |
| --- | --- |
| **IDEMIA** | 30+ service centres, **800m+ cards a year**, 180+ countries `[reported]` |
| **Thales** | Market leader alongside IDEMIA |
| **Giesecke+Devrient** | Mainstream positioning |
| **CompoSecure** | Metal cards |

Plus tokenisation and wallet provisioning (scheme network tokens, Apple Pay, Google Pay) and 3DS —
bought if you buy the processor, certified yourself if you build.

---

## Layer 05 — Payment processing and orchestration

**The decision:** none, really — **you always build the normalisation layer**. What you choose is
what you build it on.

| Need | Options |
| --- | --- |
| ISO 8583 | **jPOS** (Java, AGPL + commercial, 120+ countries in production) · **moov-io/iso8583** (Go, Apache) |
| US file formats | **moov-io**: `ach` (all SEC codes), `wire`, `imagecashletter`, `metro2`, `fed` |
| ISO 20022 | **prowide-iso20022** (all MX messages, Apache 2.0) · **prowide-core** (MT) |
| Long-running workflow | **Temporal** (Stripe standardised on it; Coinbase replaced a homegrown SAGA) · Cadence · AWS Step Functions · Camunda |

Build on top: one canonical money-movement event, an adapter per rail, an explicit state machine
with the returns branch, your own idempotency keys, and statement emission into reconciliation. See
[Deep dive — Rail adapters (buy access, build normalisation)](../deep-dives/02-rail-adapters.md).

---

## Layer 06 — Identity, onboarding, KYC and KYB

**The decision:** who orchestrates. Buy the signals; own the router once you have more than one
country or product.

| Function | Options |
| --- | --- |
| **Document + liveness** | Onfido/Entrust (Monzo, Revolut) · Jumio · Persona · Veriff · Sumsub |
| **Identity data** | Experian · LexisNexis · GBG · TransUnion · Socure (US-centric) |
| **Orchestration** | **Alloy** (270+ data sources) · Sumsub workflows · **or build it** |
| **Screening** | ComplyAdvantage · LexisNexis Bridger · Dow Jones · Napier · **OpenSanctions + yente**, self-hosted as two Docker containers so no customer data leaves |
| **KYB entity resolution** | Senzing · Quantexa · **Splink** (UK MoJ, open source) · Zingg |

**What it forces:** immutable decision logs (inputs, provider responses, model and policy versions),
a fallback chain per step, and event-driven rescreening — OFAC within **24 hours** of list updates.

---

## Layer 07 — Financial crime and disputes

**The decision:** buy to launch, build detection once fraud is material. In the UK, **APP
reimbursement makes it material on day one**.

| Function | Options |
| --- | --- |
| **Transaction monitoring** | ComplyAdvantage Mesh · Unit21 · Feedzai · Hawk AI · Featurespace ARIC (NatWest, HSBC, Danske) · NICE Actimize · Flagright · **OSS: Marble, Jube, Tazama** |
| **Device + behavioural signal** | Sardine · BioCatch · Featurespace · ThreatMetrix |
| **Build the control plane** | Monzo's pattern: sandboxed pure functions (Starlark), three control types, latency-tiered feature service, every execution logged. See [Financial crime — AML, transaction monitoring, fraud](../layers/06-fincrime.md) |
| **Disputes — pre-dispute** | **Ethoca** (Mastercard) · **Verifi** (Visa, ~24h) · Visa RDR · Mastercard Collaboration |
| **Disputes — networks of record** | **VROL** · **MasterCom** — non-optional |
| **Disputes — issuer platform** | **Quavo (QFD)** · **Pega Smart Dispute** · **Rivero (Amiko)** · Q2/CentrixDQS |

As your own principal member, **you are the issuer of record** — dispute liability is yours
directly, with no sponsor to absorb or contest it. That is the cost of independence at this layer.

---

## Layer 08 — Credit and decisioning

| Function | Options |
| --- | --- |
| **Bureaus** | Experian · Equifax · TransUnion |
| **Open banking data** | **TrueLayer** (UK/EU data and payments, VRP) · **Tink** (Visa-owned, 3,400+ institutions, 18 markets, refresh up to 4×/day) · **Yapily** (white-label, 19 countries) · **GoCardless Bank Account Data** (ex-Nordigen, generous free tier) · Plaid (US default) `[reported]` |
| **Decision engines** | Taktile · Provenir · Oscilar · **GoRules/ZEN** · Drools · **OPA/Rego** |
| **Scores** | FICO (cash-flow UltraFICO with Plaid) · VantageScore · Nova Credit |

**What it forces:** model and policy separately versioned, reason codes as a first-class model
output, affordability evidence under Consumer Duty, and a feature store shared with fincrime so
"average monthly inflow" is computed once.

---

## Layer 09 — Data and ML platform

| Function | Options |
| --- | --- |
| **Streaming** | Apache Kafka / Confluent · Redpanda · Apache Flink |
| **Warehouse** | BigQuery (Monzo) · Snowflake (Chime, Remitly) · Databricks |
| **Transformation** | dbt — Monzo runs 12,000+ models across 100+ teams |
| **Feature platform** | **Chronon** (Apache 2.0; powers 100% of Stripe's charge-path fraud models) · **Feast** · Tecton (sub-10ms p99) · Hopsworks (self-host, regulated sectors) |
| **Serving** | Python microservice templates · Seldon · BentoML |

**The rule:** the decision path must not depend on the analytics path. The warehouse can be down
without declining payments.

---

## Layer 10 — Runtime, resilience and regulatory reporting

| Function | Options |
| --- | --- |
| **Cloud** | AWS · GCP · Azure — and a documented, tested exit under DORA Art. 28–30 |
| **Continuity** | **A second-cloud stand-in.** Monzo's is 18 services on GCP against ~3,000 on AWS, at **~1% of primary cost** — the only public answer that is testable rather than aspirational |
| **Observability** | Datadog · Grafana + Prometheus · Jaeger for tracing |
| **Reconciliation** | **Build the taxonomy** (nobody sells it) on Duco · AutoRek (UK-strong) · SmartStream TLM · Gresham Clareti |
| **Regulatory reporting** | **Regnology** (has consolidated hard — acquired Wolters Kluwer's FRR division and Vermeg's AGILE) · **Suade Labs** (open FIRE data standard) · Wolters Kluwer OneSumX. The **FCA publishes a list of independent software vendors** — start there `[reported]` |

2026 context: the PRA's **Basel 3.1** programme is the live reporting workstream.

---

## The same ten layers, three real banks

| Layer | **Monzo** — UK bank, builds | **Revolut** — UK bank, mixed | **Chime** — no licence, builds tech |
| --- | --- | --- | --- |
| 01 Licence | UK bank (PRA/FCA) | UK bank + EU | **None** — Bancorp + Stride hold deposits |
| 02 Scheme access | **Own FPS gateway**, Bacs direct, own BoE account | Own licence; scheme access not public | Via the sponsor banks |
| 03 Core ledger | **Built** — `service.ledger` on Cassandra | **Built** — Postgres event store, `LISTEN`/`NOTIFY` | **Built** — ChimeCore; CoreDB is MySQL/RDS, 40TB |
| 04 Cards | **Built own processor** (GPS only for old prepaid) | **Thredd** (+ Galileo for US) | Galileo → **ChimeCore**, 100% of credit since late 2024 |
| 05 Payment orchestration | **Built** — adapter → deciders → effects | **Built** — event-driven microservices | Not public |
| 06 Identity | **Onfido** | **Onfido** | Not public |
| 07 Fincrime | **Built** — Starlark controls, multi-task NN | **Built** | **Unit21** |
| 08 Credit | **Built** | **Built** — PRAGMA foundation model | Not public |
| 09 Data & ML | BigQuery, dbt (12k models), Kafka | GCP, PostgreSQL | MySQL + Snowflake |
| 10 Resilience | **Stand-in on GCP** — 18 services, ~1% of cost | Not public | EKS, ~1k deploys/day, `ha-nat` |

**No neobank in this research publicly documents its dispute platform.** Fraud stacks are written
about extensively; the layer carrying hard regulatory deadlines and real balance-sheet exposure is
never named. That silence is itself informative — disputes are treated as back-office operations
rather than engineering, which is why the deflection funnel in [Card issuing and processing](../layers/04-card-issuing.md) is where
the advantage still sits.

**What it teaches:** licence and technology are **orthogonal** — Chime has no charter yet built its
processor, while Revolut holds a licence and rents card processing. **Everyone builds the ledger**
(the only universal build). **Everyone buys identity** — both UK banks use Onfido. **Fincrime
splits on liability**: the two UK banks build detection because APP reimbursement makes fraud a
direct P&L line; Chime, with no such regime, buys. And **only one built continuity** — Monzo's
second-cloud Stand-in has no public counterpart anywhere in this research.

## Chargebacks are a plane, not a layer

Ask where disputes live and most teams point at layer 07. That is only where the *case* lives.

| Layer | What a chargeback demands of it |
| --- | --- |
| **02 Scheme access** | **Sets the liability.** As your own principal member you are the issuer of record and the loss is yours, with no sponsor to absorb or contest it |
| **03 Core ledger** | **Two postings, not one** — a provisional credit at intake (regulatory timelines force it, so the customer has the money while the case is open), then reversal or confirmation at resolution. Model it as a **contingent position** |
| **04 Card processing** | **Delivers the message.** Thredd, Marqeta and Galileo expose the workflow by API — enough for a first programme, rarely enough at volume |
| **07 Disputes** | **Where the case lives** — evidence, representment, pre-arbitration, hard scheme deadlines. Quavo · Pega · Rivero; Ethoca and Verifi to stop cases becoming chargebacks at all |
| **10 Reconciliation** | **Closes the loop.** A won chargeback is money arriving that must match a scheme settlement file — its own break class, and easily left unreconciled for months |

**The design consequence:** crossing five layers and four teams means **nobody owns it end to end
by default**, and the failure surfaces not as a lost case but as an unexplained break months later
in a reconciliation nobody connected to disputes. Name an owner for the **whole plane**.

## The decisions, ranked by regret cost

1. **The ledger's invariants and checkpointing.** Retrofitting is an online migration of your most sensitive table.
2. **Reconciliation as a first-class subsystem.** Both regulators independently mandate it; no vendor encodes your break taxonomy.
3. **Card scheme principal membership timing.** Millions a year in dues, and a long lead time.
4. **Prefunding and treasury.** A managed position, not a deposit — and cheaper since July 2026.
5. **Whether fincrime detection is yours.** In the UK, APP liability decides this for you.
6. **Cloud continuity.** Cheap if scoped ruthlessly, impossible to retrofit credibly.

## What independence actually buys

No sponsor can exit your programme, cap your balances at payroll peaks, or be ordered out of the
business. You settle in your own name and you are the issuer of record. In exchange you carry
capital requirements, scheme dues, treasury operations, 24/7 money on-call, dispute liability with
nobody to share it, and a regulatory reporting obligation that is itself a product.

**Independence is a cost structure, not an architecture.** The architecture question underneath is
unchanged: which dependency can you least afford?

## Open questions

- Realistic all-in cost and timeline for Visa/Mastercard principal membership at a UK challenger.
- What FPS direct participation costs post the July 2026 Net Sender Cap change.
- Does anyone publish a full greenfield-bank build cost with a layer breakdown?

## Sources

- Bratby Law, FCA authorisation for PIs and EMIs — https://bratby.law/practice-areas/payments-regulation/authorisation-and-licensing/
- Vialet, Visa and Mastercard principal membership — https://vialet.eu/article/what-is-visa-and-mastercard-principal-membership-and-why-does-it-matter/
- Enfuce, BIN sponsorship — https://enfuce.com/blog/bin-sponsorship/
- Finextra, Pay.UK liquidity model for Faster Payments — https://www.finextra.com/pressarticle/110304/payuk-launches-liquidity-model-for-faster-payments
- Form3 — https://www.form3.tech/payment-platform/uk/uk-instant
- Icon Solutions IPF — https://iconsolutions.com/
- CCG Catalyst, payment hubs sector spotlight — https://www.ccgcatalyst.com/thought-leadership/research-snapshot/sector-spotlight-payment-hubs/
- 10x Banking, core platforms compared — https://www.10xbanking.com/core-banking-platforms-compared
- ABI Research, payment HSM competitive ranking — https://www.abiresearch.com/press/thales-futurex-and-utimaco-take-top-spots-in-abi-researchs-payment-hsm-vendor-competitive-ranking
- Thales, top payment HSM provider — https://cpl.thalesgroup.com/blog/encryption/thales-top-payment-hsm-provider-abi-research
- IDEMIA, card personalization services — https://www.idemia.com/card-personalization-services
- ABI Research, metal payment card ranking — https://www.abiresearch.com/press/composecure-idemia-and-thales-named-market-leaders-in-abi-researchs-metal-payment-card-competitive-ranking
- OpenBankingTracker, UK open banking APIs — https://www.openbankingtracker.com/open-banking-apis-uk
- Fintegration, Plaid vs Tink vs TrueLayer 2026 — https://www.fintegrationfs.com/post/plaid-vs-tink-vs-truelayer-2026-best-open-banking-api
- FCA, list of independent software vendors — https://www.fca.org.uk/firms/regdata/technical-information-updates/list-independent-software-vendors
- Suade Labs, 2026 UK regulatory reporting calendar — https://suade.org/2026-uk-regulatory-reporting-calendar/
- Wolters Kluwer OneSumX regulatory reporting — https://www.wolterskluwer.com/en/solutions/onesumx-for-finance-risk-and-regulatory-reporting/onesumx-for-regulatory-reporting
- Rivero, dispute management guide for card issuers — https://rivero.tech/guide-dispute-management
- Quavo Fraud & Disputes — https://www.quavo.com/processors/
- Pega Smart Dispute — https://www.pega.com/industries/financial-services/smart-dispute
- Monzo, Tolerating full cloud outages with Stand-in — https://monzo.com/blog/tolerating-full-cloud-outages-with-monzo-stand-in
- jPOS — https://jpos.org/
