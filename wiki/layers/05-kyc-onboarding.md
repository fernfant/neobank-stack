---
title: Identity and onboarding (KYC / KYB)
type: layer
status: living
updated: 2026-08-18
sources: 6
tags: [kyc, identity, onboarding, fincrime]
---

## Summary

Onboarding is where conversion and risk trade off most directly, and where a neobank's cost
per account is set. The architectural decision is not *which vendor* but *whether you own
the orchestration* — because you will change vendors, and you will want to route different
applicants down different paths.

## The pipeline

```
application → device & behavioural signals → document + selfie (liveness)
   → data-source verification (bureau, electoral roll, SSN/DOB match)
   → sanctions / PEP / adverse media screening
   → risk scoring & decision → manual review queue → ongoing (perpetual) KYC
```

Every stage should be an independently swappable step behind your own decision engine.

## Vendors

| Vendor | Strength | Reads as |
| --- | --- | --- |
| **Persona** | Highly configurable onboarding flows; strong for custom journeys `[reported]` | Buy when your flow is the product |
| **Socure** | Identity fraud, synthetic identity, first-party fraud, risk decisioning `[reported]` | Buy when fraud, not compliance, is the blocker. US-centric |
| **Alloy** | KYC **orchestration** across many data partners `[reported]` | Buy when you want the router, not the signal |
| **Onfido** (Entrust IDV) | Document verification depth; deep integrations into regulated banking compliance stacks `[reported]` | The UK/EU incumbent choice |
| **Jumio** | Broad document coverage, mature liveness `[reported]` | Global footprint; higher price point `[reported]` |
| **Sumsub, Veriff, Trulioo, IDnow, GBG, Shufti** | Regional depth / price | Sumsub and Zyphe called out for data-residency and ongoing-monitoring architecture `[reported]` |

Pricing: Jumio and Onfido typically run higher than Persona or Socure at comparable
application volumes `[reported]`. Note that most published vendor comparisons in this space
are content marketing — treat all of the above as `[reported]` and verify with a bake-off.

## The orchestration question

Two patterns:

1. **Single-vendor waterfall.** One provider does documents, data, and screening. Simple,
   fast, and you are exposed to their coverage gaps and their price rises.
2. **Own the orchestrator.** Your service calls providers as pluggable steps, with routing
   rules (by geography, product, risk band) and a fallback chain. Alloy sells this as a
   product; large neobanks build it.

Build the orchestrator if you operate in more than one country or run more than one product.
The tell that you needed it: an incident where one vendor's outage stopped all onboarding.

**Log every decision immutably.** Store which providers were called, what they returned, the
model version, and the decision — the evidence plane in [The ten-layer map](../layers/00-layer-map.md). You will be
asked to justify a 2026 decision in 2029.

## KYB (business onboarding)

Materially harder than KYC and often underestimated: entity resolution, ownership
structures, UBO identification at 25% thresholds, director verification, sanctions
screening on every related party, and business-type risk classification. Mercury, Tide and
Revolut Business are the reference implementations to study.

## Accessibility is a conversion problem — a worked example

Monzo's February 2025 post is the only public neobank writing on IDV UX, and it is notable for
what it does *not* say: **no vendor is named anywhere** `[confirmed]`, consistent with identity
being the thinnest attribution layer in [Vendor map — who uses what](../vendors/vendor-map.md).

The flow is the industry standard — photograph an ID document, then record a selfie video
repeating a phrase. The work was entirely on the capture experience: in-the-moment face-framing
feedback, a dimmed background with a frame for contrast, a blur fade-in to give people time to
prepare, gating recording until a face is clearly visible, **colour *and* haptic feedback**, screen
reader compatibility, and explicit **sign language support**.

Result: a **73% reduction in IDV selfie video errors**.

Two lessons generalise. First, in an onboarding funnel the **capture step, not the matching
algorithm, is usually where conversion is lost** — and it is the part you control regardless of
which vendor sits behind it. Second, accessibility work here is not compliance overhead; it moved
the single biggest error rate in the funnel by three quarters. Note their remaining problem:
the phrase format makes one-handed BSL signing awkward, which they are considering changing to
numbers.

## Perpetual KYC

The industry has moved from periodic refresh cycles to **event-driven re-verification** —
triggered by behaviour change, sanctions-list updates, or document expiry. One vendor-cited
figure puts compliance-operations cost reduction at 60–80% at mid-size institutions
`[reported]` — treat the number sceptically, but the architecture is right: subscribe to
change events rather than run a quarterly batch.

Note the hard requirement underneath it: **OFAC screening must happen at onboarding, on an
ongoing basis, and within 24 hours of list updates** `[reported]`. That is a streaming
requirement, not a batch one.

## Open questions

- What is the actual all-in cost per verified account for a UK neobank in 2026 (document +
  data + screening + manual review)?
- How are firms handling AI-generated document and deepfake selfie attacks — is liveness
  still holding, and which vendors have published injection-attack detection results?
- Does the FCA have a published view on fully-automated onboarding decisions with no human
  in the loop?

## Sources

- Zyphe, identity verification software comparison 2026 — https://www.zyphe.com/resources/blog/identity-verification-software-comparison-2026
- ClearStaq, best KYC verification software for lenders 2026 — https://clearstaq.com/blog/best-kyc-verification-software-for-online-lenders
- Signzy, top KYC companies for US fintech onboarding — https://www.signzy.com/blogs/top-10-kyc-companies-for-us-fintech-onboarding
- deepidv, top identity verification platforms 2026 — https://www.deepidv.com/media/articles/top-10-identity-verification-platforms-2026-comparison
- Monzo, Making identity verification more accessible — https://monzo.com/blog/making-identity-verification-more-accessible
- Shufti Pro, KYC for fintech and neobank onboarding — https://shuftipro.com/blog/kyc-for-fintech-neobank-onboarding/
- Canarie, AML compliance for neobanks — https://www.canarie.ai/blog/aml-compliance-neobanks-guide
