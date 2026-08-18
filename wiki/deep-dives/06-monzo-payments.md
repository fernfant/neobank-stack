---
title: Deep dive — Monzo payments, end to end
type: deep-dive
status: living
updated: 2026-08-18
sources: 14
tags: [monzo, payments, fps, bacs, cards, uk, insourcing]
---

## Summary

Monzo is the most completely documented payments stack in retail banking, and its defining
characteristic is that **it insourced every rail, one at a time, over six years** — each move
triggered by a specific operational limit rather than by cost. Cards in 2017–18, Faster Payments
in 2019–20, Bacs in 2022. Today it settles against its own Bank of England account and has no UK
sponsor at all.

## The insourcing arc

| Rail | Before | In-house from | The trigger |
| --- | --- | --- | --- |
| **Cards** | GPS (now Thredd), prepaid only | Current-account launch, 2017–18 | Vendor outages; wanting to own the whole experience |
| **Faster Payments** | An unnamed third-party gateway | Gateway live Nov 2019; migration **2 Nov 2020** | A payments incident on 30 May 2019; active-standby failover took **~15 minutes** |
| **Bacs** | A sponsor bank, from 2017 | Direct participant, **12 Sept 2022** | Manual transfers to the sponsor, and **regulatory caps on funds held there at payroll peaks** |

Note the pattern: **none of these was a cost decision.** Each was a constraint — a vendor's
reliability, a failover time, a balance cap — that had become the binding limit on the business.
That is a better build-vs-buy rule than any volume threshold.

## How a Monzo payment actually works

From Monzo's own explainer, and still the clearest public description of FPS mechanics
`[confirmed]`:

1. You give an account number and sort code. The bank validates them (**Luhn algorithm**).
2. Your bank **places a hold** on your account for the amount.
3. An **ISO 8583** message goes to **Vocalink**.
4. Vocalink routes it to the recipient's bank by sort code.
5. The receiving bank confirms the account is open and able to receive.
6. The recipient's account is credited.
7. The receiving bank acknowledges back through Vocalink.
8. **Only then** does your bank debit your account and release the hold.

The customer-visible payment is complete. **No money has moved between the banks.** FPS uses
**deferred net settlement**: individual payments accumulate into net positions and settle at the
Bank of England — three times a day on weekdays. Millions of payments become a handful of central
bank ledger entries. This is exactly the authorisation/clearing/settlement split in
[Deep dive — Payment rails](../deep-dives/05-payment-rails.md), and it is why a bank's internal ledger and its settlement
position are different things.

Two scheme facts worth holding: the FPS limit is **£250,000** per payment, and Monzo's own default
customer daily limit is **£10,000** `[reported]`. **Paym** is a lookup table mapping mobile numbers
to account details, resolved before a perfectly ordinary Faster Payment `[confirmed]`.

## The FPS gateway — a deliberate monolith

The most interesting thing Monzo has published about payments, because it runs against everything
else the company is known for `[confirmed]`.

| Property | Choice |
| --- | --- |
| Shape | **A monolithic replicated application in Go — explicitly not microservices** |
| Topology | **Active-active** across two data centres (previously active-standby, ~15 min failover) |
| Connectivity | Per-payment-type TCP connections to the FPS hub; **two physical links per data centre**, tolerating 3 of 4 failing |
| Deployment | **Docker and Docker Compose on virtual machines** — not Kubernetes |
| Storage | **DRBD** — three servers per DC, dual SSDs, six replicas per write; survives a whole server plus one disk per remaining machine |
| Security | **Four HSMs**, two per DC; the gateway still runs on one |
| Resilience | **Store-and-forward stand-in** — on a per-message timeout it answers the scheme hub itself, then forwards when the processor recovers |
| Observability | 10-second metrics, 60-second alert threshold, logs to **BigQuery** with sensitive data stripped, dedicated payments on-call |

The migration completed in **one hour against a three-hour window**. TransferWise, Pay.UK and
Vocalink are credited as advisers, not vendors.

**Why the monolith.** A scheme gateway is a different problem from a product estate: a small,
fixed protocol surface, an extreme availability requirement, and a hard dependency on physical
connectivity and HSMs. Distributing it would add failure modes without adding capability. Monzo
runs >3,000 microservices *and* this — the lesson is that architectural style should follow the
problem, not the house style.

**The store-and-forward detail is the one to steal.** If your internal processor is slow, the
gateway answers the hub on a timeout rather than letting the payment be rejected. Without it, an
internal wobble becomes a customer-visible failure and a scheme-level performance problem.

## Bacs — direct participation

Sponsor bank from 2017. Two problems forced the change `[confirmed]`: manual money transfers to
the sponsor carried operational risk and needed manual controls, and **regulatory limits capped
how much Monzo could hold at the sponsor during mid-month and end-of-month payroll peaks**. The
second is the interesting one — the sponsor model did not just cost money, it *bounded the
business* at exactly the moment volume was highest.

Built for it: a **SWIFT Banking Network** connection to Bacs; **HSMs** holding the certificates
that sign and verify files; Bacs microservices that generate files and hash them, with the HSM
signing the hash before transmission; and **direct settlement against Monzo's own Bank of England
account**, removing the sponsor from the money path entirely.

Eighteen months, across engineering, operations, support, risk, legal and infrastructure.
Migration day **12 September 2022**, deliberately chosen for lower volumes; the first Direct Debit
file landed at **00:19 on 13 September**.

## Monzo → Monzo: the payment that isn't a payment

For a current-account-to-current-account transfer between two Monzo customers, there is **no
external money movement at all** `[confirmed]`. The `p2p-payments` service
(`POST /p2p-payments/create_transfer`) checks account types via the account service, then simply
**debits one ledger account and credits another**. No rail, no scheme, no settlement.

This is the structural advantage of a closed-loop balance and the reason in-network transfers are
instant and free. It also means your ledger, not the rail, is the constraint — see the balance-read
section below.

During the prepaid-to-current-account transition the same flow crossed a boundary: prepaid
balances lived at a third-party processor and issuing bank, so those transfers required weekly
batch reconciliation spreadsheets sent to the issuing bank, and metadata caching to avoid four
RPC calls per lookup `[confirmed]`. A neat illustration of how much complexity the closed loop
removes.

## International — adapters, deciders, effects

A modular pipeline built for correctness, testability and reuse `[confirmed]`:

**adapter → deciders → effects → effect application**

- **Adapters** marshal each partner's wire format into one common representation.
- **Deciders** evaluate account existence, compliance and limits in parallel, returning Accept,
  Reject or **Hold**, with encoded precedence: **Hold blocks, Reject overrides Accept.**
- **Effects** — ledger entries, bank notifications, internal movements — are *generated* from the
  decision.
- **Effect application** executes and logs them for audit and debugging.

FX for **40+ currencies without holding an account in each**: a correspondent partner bank
receives the payment, performs the exchange and forwards over **SWIFT** with the rate attached.
IBAN validation with checksums, BIC codes (Monzo's is **`MONZGB2L`**), idempotency for
exactly-once. Each partner gets an adapter plus a separate microservice for its quirks.

## Cards

GPS (now **Thredd**) processed the *prepaid* card from 2016, sitting between Monzo and Mastercard.
GPS outages hit Monzo more than once `[reported]`. For the **current account**, Monzo built its
own processor from the ground up with **no third-party issuing bank** `[confirmed]`, and wound
prepaid down through 2017–18.

**The US is the opposite arrangement.** The Monzo Mastercard there is **issued by Sutton Bank
under licence from Mastercard**, with Monzo Inc. providing services on Sutton's behalf
`[confirmed]`, and Galileo processing `[reported]`. Same brand, inverted architecture — see
[Monzo (UK)](../banks/monzo.md).

## Payments in Stand-in

When the primary platform is unavailable, the Stand-in platform on GCP processes **Mastercard,
Faster Payments and Bacs** `[confirmed]`. Two routing paths: via the primary's **edge services**
during a partial outage — chosen because they are earliest in the payment path and most resilient
— or **direct from the data centres** during a severe failure.

Stand-in **reimplements** payment logic using a **validators** pattern (independent parallel
checks: is the card frozen, is the account open) rather than sharing code, so one bug cannot take
both platforms down. Divergence is caught by **shadow-testing a proportion of production traffic**
against the primary's decisions. Full detail in [Resilience, regulatory reporting and operations](../layers/10-resilience-regulatory.md).

## The constraint underneath everything: balance reads

Monzo's ledger addresses are a 5-tuple, and a balance means summing every entry in the group. By
2022 that was **P99 400–500ms** `[confirmed]`.

The consequence is specific to payments: during card authorisation, if the balance read is too
slow, **the scheme invokes its own stand-in and approves on Monzo's behalf** — potentially beyond
available balance, with Monzo's fraud checks never running. Fixed with pre-computed balance blocks
and time-series reindexing; **P99 fell to ~200ms**. See [Core ledger and product engine](../layers/02-core-ledger.md).

## The product layer

**A unified payment flow**, eight months of work, merging bank transfers and Monzo-to-Monzo into
one interface `[confirmed]`. The engineering split is instructive: **eligibility checks and payment
processing run server-side**; input validation and screen transitions run client-side for
responsiveness. Backend endpoints distinguish **blocking from non-blocking** calls so a failure in
a non-critical feature cannot break the whole flow, and **server-side eligibility means feature
rollouts do not need an app release**.

**Confirmation of Payee** got a new backend endpoint returning richer data, so clients can show
field-level feedback and generate smart suggestions for correcting recipient details `[confirmed]`.

**Bulk payments** for business: CSV upload, typical batches of **21–24 items**, CoP scaled across
multiple payments at the same success-rate standard as single payments, and **role-based approval**
— collaborators set up, admins approve, and approval can happen on mobile while setup happened on
web `[confirmed]`. Roughly **70% retention** post-launch.

## Load: two very different spikes

**Crowdfunding (2019).** Prepared for **100,000 investments in five minutes** and **1,000/second**
peak, 15–30× normal load `[confirmed]`. Architecture: an API service, a `crowdfunding-total`
in-memory singleton, `crowdfunding-pre-investment`, **NSQ**, and a `crowdfunding-investment`
singleton consuming at ~60/second into the **same ledger service the bank uses** — two entries,
out of the customer's account and into a Monzo investment account. The trick was a **`balance-cache`
in-memory LRU** doing approximate balance checks to keep **Cassandra out of the pre-investment
path** entirely. Actual: **£4m in under two minutes**, ~£7m in five.

**Payday.** "Get Paid Early" lets customers pull Bacs credits at 4pm the day before, producing
**up to a 500% traffic increase in seconds** across up to 250,000 eligible payments — then a
cascade as those customers immediately pay bills and move money `[confirmed]`. Reactive autoscaling
cannot react fast enough, so Monzo **forecasts demand from the incoming Bacs records themselves**,
sizes it against historical CPU in Prometheus, and uses **Jaeger** traces to find every downstream
service needing headroom.

The pairing is the lesson: one spike is unpredictable and absorbed by removing the database from
the hot path; the other is *scheduled by an external rail*, so it is absorbed by reading the future
off the rail and pre-scaling.

## Scam controls and APP liability

UK APP reimbursement makes outbound scam detection a P&L line — see [Financial crime — AML, transaction monitoring, fraud](../layers/06-fincrime.md). Monzo
warns on risky payments and will **block** some outright where it has strong reason to think it is
a scam `[reported]`. It has also shipped **customer-managed** controls — Known Locations, Trusted
Contacts and Secret QR codes — which are opt-in and shift some control to the customer `[reported]`.
That is a distinctive answer: rather than only tuning the model, give the victim-side user tools
that make certain coerced payments structurally harder.

## What to steal

1. **Insource on constraints, not on cost.** Every Monzo move was triggered by a specific
   operational limit.
2. **Let the rail gateway be a monolith.** Different problem, different architecture.
3. **Store-and-forward at the gateway** so internal slowness never becomes a scheme-level failure.
4. **Precedence as data** in the decisioning layer (Hold blocks, Reject overrides Accept).
5. **Generate effects separately from applying them** — the thing that makes payments testable.
6. **Keep the database out of the spike path**, and **pre-scale from the rail** when the rail tells
   you what is coming.
7. **Server-side eligibility** so payment rollouts do not need app releases.

## Open questions

- Is Monzo a **CHAPS** direct participant? FPS and Bacs are confirmed; CHAPS is not established.
- Is Monzo a Mastercard **principal member** in the UK, and what does its in-house processor
  actually cover — authorisation only, or clearing and settlement too?
- Who was the Bacs sponsor 2017–2022, and the pre-2019 FPS gateway provider? Never named.
- What are Monzo's current FPS/Bacs volumes and its net settlement position size?
- Does Stand-in support international payments, or domestic rails only?

## Sources

- Monzo, How do bank payments work? — https://monzo.com/blog/2016/01/20/how-do-bank-payments-work
- Monzo, How we moved our Faster Payments connection in-house — https://monzo.com/blog/how-we-moved-our-faster-payments-connection-in-house
- Monzo, Becoming direct participants of Bacs — https://monzo.com/blog/2023/02/22/becoming-direct-participants-of-bacs
- Monzo, A technical look at how Monzo-to-Monzo payments work — https://monzo.com/blog/2018/04/05/how-monzo-to-monzo-payments-work
- Monzo, Building a processing system for International Payments — https://monzo.com/blog/building-a-processing-system-for-international-payments
- Monzo, Processing payments in Monzo Stand-in — https://monzo.com/blog/processing-payments-in-monzo-stand-in
- Monzo, Tolerating full cloud outages with Monzo Stand-in — https://monzo.com/blog/tolerating-full-cloud-outages-with-monzo-stand-in
- Monzo, Delightful Payments — https://monzo.com/blog/delightful-payments/
- Monzo, Designing bulk payments for how businesses really work — https://monzo.com/blog/designing-bulk-payments-for-how-businesses-really-work
- Monzo, How we built a backend for our £20 million crowdfunding round — https://monzo.com/blog/2019/01/14/crowdfunding-technology-backend-architecture
- Monzo, Preparing for spikes in traffic as millions get paid early — https://monzo.com/blog/2023/01/26/preparing-for-spikes-in-traffic-as-millions-get-paid-early
- Monzo, Speeding up our balance read time — https://monzo.com/blog/2023/04/28/speeding-up-our-balance-read-time-the-planning-phase
- Monzo Help, warnings when making a payment — https://monzo.com/help/monzo-fraud-category/fraud-warnings
- Sutton Bank, Monzo cardholder agreement — https://www.suttonbank.com/_/kcms-doc/85/89855/Monzo-Agreement-12.16.24.pdf
