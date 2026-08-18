---
title: Deep dive — KYC orchestration (build)
type: deep-dive
status: living
updated: 2026-08-18
sources: 9
tags: [kyc, orchestration, build, decision-engine, entity-resolution]
---

## Summary

You buy the signals — documents, liveness, identity data, sanctions lists. You build the thing
that **decides which signals to gather, in what order, for whom, and what to do when one of them
is down**. That router is the orchestration layer, and the trigger to build it is stated in the
build-vs-buy table as "more than one country or product" — but in practice the trigger arrives
as an incident: *a single vendor's outage stopped all onboarding*.

## The argument, stated properly

An onboarding funnel is a decision tree over unreliable third parties. Three properties make it
different from ordinary integration work:

1. **Vendors have different coverage by geography and document type.** No single provider is
   best everywhere, so a multi-market neobank routes.
2. **Vendors fail.** Not rarely. Without a fallback chain, their availability is your conversion
   rate.
3. **Every decision must be defensible years later.** You will be asked why you approved a
   specific customer in 2026 — which means inputs, provider responses, model versions and the
   decision itself must be logged immutably at the time.

Alloy exists as a company because of point 1 and 2: it markets **270+ data sources** behind one
vendor-neutral orchestration layer `[reported]`. That is the shape of the thing. The question is
whether you rent it or own it.

Wise Platform is the instructive real-world design: it offers a **hybrid** model where partners
own the onboarding experience through APIs but fall back to Wise-hosted flows for requirements
that cannot be collected via API — explicitly so that changing regulatory requirements do not
break the flow and new regions can be added faster `[reported]`. Even a company with Wise's
resources designs for "the requirements will change under us".

## The architecture

```
application
   ↓
[ orchestrator ]  ── routing rules: geography · product · risk band
   ├── device & behavioural signals        (Sardine, in-house)
   ├── document + liveness                 (Onfido · Jumio · Persona · Veriff)   ← swappable step
   ├── identity data verification          (Socure · Experian · LexisNexis)      ← swappable step
   ├── sanctions / PEP / adverse media     (OpenSanctions+yente · ComplyAdvantage)
   └── entity resolution (KYB, UBOs)       (Senzing · Splink · Quantexa)
   ↓
[ decision engine ] ── model score + policy rules, separately versioned
   ↓
approve · refer · decline  →  [ immutable decision log ]  →  case management
```

Two design rules carry most of the value:

**Every provider call is a step with a timeout, a fallback and a cost.** The orchestrator owns
retry, circuit-breaking and provider selection. A step is defined by its *contract* (what
question it answers), not by the vendor implementing it, so swapping Onfido for Veriff in one
market is configuration.

**Separate the model from the policy.** The model emits a probability; policy emits a decision.
Hard cuts, regulatory constraints and geography rules live in a separately versioned,
human-readable policy layer, because policy changes weekly and models change quarterly. The same
rule applies in [Credit and decisioning](../layers/07-credit-scoring.md).

## Software to build on

### Decision and rules engines

| Package | Shape | Licence |
| --- | --- | --- |
| **GoRules / ZEN Engine** | Visual decision tables over a JSON Decision Model; embeddable engine with bindings; DMN support; fast, no heavy infrastructure `[reported]` | Open source core |
| **Drools** | The most battle-tested open-source rule engine in production; DMN + BPMN, Workbench for authoring and testing, decision tables `[reported]` | Apache 2.0 |
| **Camunda** | BPMN for orchestration + DMN for decisions; strong for long-running processes with embedded decision tables `[reported]` | Source-available/commercial |
| **Kogito** | Cloud-native Drools-lineage decisions + process, built for Kubernetes `[reported]` | Apache 2.0 |
| **Open Policy Agent / Rego** | Policy as code, decoupled from application code. Runs as a daemon, a **Go library embedded in your service**, or a sidecar. Returns structured decisions — not just allow/deny but warnings, violations, metadata, **risk scores** `[reported]` | Apache 2.0 |
| **DecisionRules, Nected** | Commercial, business-user-operable without BPMN overhead `[reported]` | Commercial |

OPA is the underrated option for a neobank. Because it evaluates against pre-loaded in-memory
data and can be embedded as a library, it fits the latency budget, and "policy separate from
application code, returning structured decisions with risk scores" is precisely the
model-versus-policy separation above. It is also the closest widely-adopted analogue to what
Monzo built with Starlark for fraud — see [Deep dive — Fraud and AML detection (build)](../deep-dives/04-fraud-aml.md).

### Screening — the self-hosting option

**OpenSanctions + yente** is the significant one for anyone with data-residency constraints
`[confirmed]`:

- `yente` is the open-source screening API that powers the hosted OpenSanctions API. It searches,
  retrieves and **bulk-matches** FollowTheMoney entities — people, companies, vessels — against
  sanctions lists, PEP lists and watchlists.
- It ships as **two Docker containers** (app + Elasticsearch), runs well on Kubernetes, and can
  be run **on-premises as a KYC appliance so no customer data leaves your deployment**.
- It can screen against your own custom watchlists and company registries, not just OpenSanctions
  data, and supports the Reconciliation API spec.

That combination — open data, open matching engine, fully self-hosted — removes the usual
argument that screening must be a SaaS vendor. It does not remove the need for a commercial
provider's curated adverse-media and enhanced-diligence content, which is where ComplyAdvantage,
Dow Jones and LexisNexis still earn their fee.

### Entity resolution — the KYB problem

Business onboarding is where orchestration gets genuinely hard: resolving entities, ownership
structures, UBOs at 25% thresholds, and screening every related party.

| Package | Notes |
| --- | --- |
| **Splink** | Open-source probabilistic record linkage from the **UK Ministry of Justice**. Fellegi-Sunter model with EM estimation, building on FastLink. **3m+ downloads**; links a million records **on a laptop in about a minute**; scales to 100m+ on Spark or AWS Athena `[reported]` |
| **Zingg** | Open-source ML-based entity resolution `[reported]` |
| **Senzing** | Commercial, embedded-engineering model; explicitly targets KYC, AML, fraud rings, sanctions screening `[reported]` |
| **Quantexa** | Commercial; entity resolution plus **network graph analytics** over billions of data points to surface hidden relationships `[reported]` |
| **AWS Entity Resolution, Tamr, Reltio, Informatica** | Cloud/MDM-shaped alternatives `[reported]` |

Splink deserves attention specifically because it is government-built, permissively licensed,
statistically principled, and fast enough that the "we cannot afford entity resolution" argument
does not survive contact with it.

### Long-running cases

A referral can sit with a human for days. **Temporal** handles this the same way it handles
payments — durable state, audit trail, survives restarts. If your orchestrator is a chain of
webhook handlers and a database status column, you will rebuild it as a workflow engine
eventually.

## Vendors you still buy

Documents and liveness (Onfido/Entrust, Jumio, Persona, Veriff, Sumsub), identity data (Socure,
Experian, LexisNexis, GBG, Trulioo), curated screening content, and case management. If you
decide not to build the orchestrator at all: Alloy, Sumsub workflows, ComplyCube and Persona all
sell no-code orchestration `[reported]`.

## Failure modes

- **One vendor is the whole funnel.** The tell is the outage. Design the fallback chain before
  you need it, and test it by disabling the primary in staging on purpose.
- **Decisions logged as outcomes, not inputs.** "Approved" is not evidence. Store what each
  provider returned, the policy version, the model version.
- **Screening as a batch job.** OFAC obligations require screening at onboarding, on an ongoing
  basis, and **within 24 hours of list updates** `[reported]` — that is a streaming requirement.
- **KYB modelled as KYC with extra fields.** It is a graph problem. Treat it as one.

## Open questions

- All-in cost per verified account for a UK neobank in 2026, including manual review.
- Which neobanks run `yente` self-hosted rather than a screening SaaS?
- How are firms handling injected/deepfake documents, and which vendors publish detection results?
- Does the FCA have a published view on fully automated onboarding with no human in the loop?

## Sources

- Alloy, onboarding and orchestration — https://www.alloy.com/onboarding
- Wise Platform, onboarding and KYC documentation — https://docs.wise.com/guides/product/kyc
- OpenSanctions, yente documentation — https://www.opensanctions.org/docs/yente/
- OpenSanctions, self-hosting the API — https://www.opensanctions.org/docs/self-hosted/
- opensanctions/yente on GitHub — https://github.com/opensanctions/yente
- Splink documentation (UK Ministry of Justice) — https://moj-analytical-services.github.io/splink/index.html
- ADR UK, Splink: free software for probabilistic record linkage at scale — https://www.adruk.org/news-publications/news-blogs/splink-free-software-for-probabilistic-record-linkage-at-scale/
- Open Policy Agent, policy language — https://www.openpolicyagent.org/docs/policy-language
- Tilores, top entity resolution tools 2026 — https://tilores.io/content/top-10-entity-resolution-tools-for-enterprises-in-2026-ranked-by-use-case/
