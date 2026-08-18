---
title: Deep dive — Rail adapters (buy access, build normalisation)
type: deep-dive
status: living
updated: 2026-08-18
sources: 9
tags: [payments, rails, iso8583, iso20022, build, open-source]
---

## Summary

Nobody sensible builds scheme connectivity from scratch — you buy access from Form3, ClearBank,
Modulr, Column or a sponsor bank. But the layer **between** that access and your ledger is
always yours, because it encodes the one thing no vendor can know: what a payment *means* in
your product. Uber's version of this layer normalises 50+ PSP formats into a single `PSPEvent`
type `[confirmed]`. That is the pattern, at the largest public scale.

The good news, and the thing most teams miss: the wire-format work — ISO 8583, ISO 20022, Nacha
ACH, Fedwire — is **solved open source**. You should not be writing a bitmap parser in 2026.

## The packages that already exist

### Card rails — ISO 8583

| Package | Notes |
| --- | --- |
| **jPOS** (Java) | The de-facto open-source ISO 8583 implementation. In production in **120+ countries**, from startups to Fortune 100, "processing thousands of transactions every second, 24x7x365" `[reported]`. Powers switches, gateways, acquiring systems and **issuer systems** |
| **moov-io/iso8583** (Go) | Marshal/unmarshal ISO 8583, Apache-licensed, modern Go ergonomics |

**Licensing matters here.** jPOS is **AGPL** — free for open-source use, but running it inside a
proprietary product requires a commercial licence from Transactility `[reported]`. That is a
budget line, not a blocker, and it is far cheaper than writing your own. Transactility also
sells jCARD, a card-management engine on top.

### US rails — Nacha, Fedwire, Check21, credit reporting

The **moov-io** family is the strongest open-source payments toolkit in existence, all Go,
single-responsibility, Apache 2.0 `[reported]`:

| Package | Format |
| --- | --- |
| `moov-io/ach` | ACH file generation and parsing, **all Standard Entry Class codes** |
| `moov-io/wire` | Fedwire Funds Service files |
| `moov-io/imagecashletter` | Check21 / X9 image cash letter |
| `moov-io/metro2` | Metro 2 — consumer credit reporting to the US bureaus |
| `moov-io/fed` | FedACH and Fedwire participant directories (routing number lookup) |
| `moov-io/iso8583` | Cards |

If you are building a US neobank, that list covers a genuinely large fraction of the
file-format work, and `metro2` in particular is a package people usually discover only after
writing their own badly.

### ISO 20022 — the UK/EU direction of travel

| Package | Notes |
| --- | --- |
| **prowide-iso20022** (Java, Apache 2.0) | Complete typed model and parser for **all** MX messages — pain.001/002/008/013, pacs.002/004/008/009/010, camt, every version. `AbstractMX.parse()` auto-detects type from the XML namespace `[confirmed]` |
| **prowide-core** | The MT (legacy SWIFT) side |
| **Prowide Integrator Translations** | Commercial MT↔MX conversion for migration |

Since the UK's NPA work has narrowed to replacing Faster Payments on an ISO 20022 basis and the
RPIB consultation opened in June 2026, modelling your internal messages on ISO 20022 now is the
cheap option — see [Payment rails and money movement](../layers/03-payment-rails.md).

### The state machine

A cross-border transfer or an ACH debit is not a request/response — it is a workflow that lives
for days and can fail at any stage. **Temporal** is the current default for this: durable
execution, exactly-once semantics, complete audit trails. Stripe standardised on it for payment
workflows where exactly-once is non-negotiable; **Coinbase migrated its transaction workflows
onto it specifically to delete a homegrown SAGA implementation** `[reported]`. That second
datapoint is the useful one — homegrown saga orchestration is the thing teams build, regret,
and replace.

## What you build on top

The normalisation layer, and it has five parts:

**1. One canonical money-movement event.** Uber's `PSPEvent` — amount, currency, transaction
date — with everything rail-specific pushed into the adapter `[confirmed]`. Resist the urge to
make this a union of every rail's fields; it should be the intersection plus a typed extension.

**2. An adapter per rail, and a corridor as configuration.** The test of a good design: adding
a new payout corridor or PSP is a config entry plus an adapter, never a branch in core logic.
Remitly's architecture is the reference for corridor-shaped complexity `[reported]` — see
[Remitly (USA / cross-border)](../banks/remitly.md).

**3. An explicit payment state machine.**

```
initiated → risk-checked → authorised → submitted → accepted → settled
                │              │            │           │
                └─ blocked     └─ rejected  └─ returned  └─ reversed
                                              (days later)
```

The branch teams under-build is the late one. ACH returns arrive with R-codes days after the
fact (R01 insufficient funds, R10 unauthorised); Direct Debit indemnity claims can arrive
*months* later and are effectively unbounded. Both must reverse cleanly against the ledger.

**4. Idempotency and dedup end to end.** Every rail will redeliver, reorder, or arrive late.
The key is chosen by you, not by the rail, because the rail's identifier is exactly the thing
that gets rewritten — see `identifier.reference-rewritten` in
[Deep dive — Reconciliation (build)](../deep-dives/01-reconciliation.md).

**5. Emit into the reconciliation plane.** Every adapter also produces the statement side of
the reconciliation input. Building these two together is much cheaper than retrofitting.

## Access — what you actually buy

| Market | Providers |
| --- | --- |
| **UK/EU** | ClearBank, LHV, Banking Circle (agency access to FPS, Bacs, CHAPS, SEPA); Form3 and Modulr (payments-as-a-service, scheme connectivity) |
| **US** | Column, Increase, Moov, Dwolla (ACH, RTP, FedNow access); sponsor bank direct |
| **Cards** | Marqeta, Galileo, Lithic, Highnote, Thredd — see [Card issuing and processing](../layers/04-card-issuing.md) |
| **Bank-scale message infrastructure** | Icon Solutions IPF, Volante — used where an institution runs its own scheme connectivity |
| **Stablecoin settlement** | Bridge (Stripe), BVNK (Mastercard), Circle |

The question to ask any of them is not "do you support FPS" but **"what happens when you have
an incident, and what is my failover?"** A single access provider is a single point of failure
for all outbound money, and it is the concentration risk DORA Article 29 asks about.

## Independent confirmation — Monzo's international payments pipeline

Monzo built exactly the layer argued for above, and published it `[confirmed]`:
**adapter → deciders → effects → effect application**, with partner-specific logic in a separate
microservice behind each adapter so the core processor stays lightweight, and a new partner is an
adapter rather than a branch. Deciders return Accept / Reject / **Hold** with encoded precedence.
Effects (ledger entries, notifications, internal movements) are **generated separately from being
applied**, and every application is logged for audit.

Two design points worth lifting verbatim: **precedence as data** rather than ordering, and the
**generate/apply split**, which is what makes the pipeline testable as a closed box. Their testing
runs at three levels — unit, acceptance treating the system as a closed box, and scheduled staging
runs against current platform services.

## Failure modes

- **Adapter logic leaking into the ledger.** The reason Uber separates ingestion from
  accounting. Once a PSP quirk is encoded in a posting rule, it is permanent.
- **Balance state at the webhook layer.** Replicating balance into the webhook handler is how
  it drifts `[reported]`. Webhooks translate to postings; the ledger stays authoritative.
- **Treating cross-border as slow domestic.** It is a multi-stage state machine with
  corridor-specific cut-offs and FX exposure between quote and settlement.
- **No stand-in policy.** What authorises when the ledger cannot answer? See
  [Card issuing and processing](../layers/04-card-issuing.md).

## Open questions

- Who is actually running moov-io libraries in a licensed UK/US institution at scale, and what
  did they have to fork?
- What does a jPOS commercial licence cost at neobank volume?
- Does the RPIB outcome change the direct-vs-agency calculus? (Open in [Payment rails and money movement](../layers/03-payment-rails.md).)
- Is anyone using Temporal for the *card authorisation* path, or only for the async rails?
  (Suspect only async — the latency budget forbids it — worth confirming.)

## Sources

- Uber, Advanced Settlement Accounting System — https://www.uber.com/us/en/blog/ubers-advanced-settlement-accounting-system/
- jPOS project — https://jpos.org/
- Transactility, jPOS licensing — https://transactility.com/products/jpos-licensing/
- moov-io repositories — https://github.com/orgs/moov-io/repositories
- moov-io/iso8583 — https://github.com/moov-io/iso8583
- Prowide ISO 20022 open-source Java library — https://www.prowidesoftware.com/products/open-source/iso20022
- prowide/prowide-iso20022 — https://github.com/prowide/prowide-iso20022
- Temporal — https://temporal.io/
- Monzo, Building a processing system for International Payments — https://monzo.com/blog/building-a-processing-system-for-international-payments
- Bank of England, RPIB consultation — https://www.bankofengland.co.uk/news/2026/june/rpib-launches-consultation-on-next-generation-uk-payments-infrastructure
