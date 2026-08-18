---
title: Deep dive — Payment rails
type: deep-dive
status: living
updated: 2026-08-18
sources: 16
tags: [payments, rails, uk, usa, settlement, iso20022, bacs, ach]
---

## Summary

Rails are where a clean internal model meets other people's weak guarantees. Almost every
expensive mistake in this layer traces to one conceptual error: **treating authorisation,
clearing and settlement as the same event.** They are three different things, happening at
three different times, with three different failure modes — and a ledger that models only one
of them will be wrong in a way that surfaces months later as an unexplainable break.

## The three things people call "a payment"

| | What it is | Has money moved? |
| --- | --- | --- |
| **Authorisation** | A real-time promise. An obligation is created and a hold placed | **No** |
| **Clearing** | Exchange of transaction information between institutions; gross flows compressed into net positions | **No** |
| **Settlement** | Actual transfer of funds — for domestic rails, central bank money | **Yes** |

"When the merchant sees *approved*, no funds have moved; an obligation has been created and a
hold placed" `[reported]`. Clearing "is not itself the movement of money — it is the
reconciliation of the obligation to move money" `[reported]`.

**Why this matters to your ledger.** Each stage is a different posting. An authorisation is a
*hold* against available balance. Clearing is when the amount becomes certain — and it can
differ from the authorised amount (tips, fuel, hotels). Settlement is when your position at the
central bank or your sponsor actually changes. If you post once and call it done, you cannot
answer "why does available balance differ from cleared balance", and you cannot reconcile
against the scheme's daily files. See [Deep dive — Reconciliation (build)](../deep-dives/01-reconciliation.md).

---

## UK rails

### Faster Payments — real-time to the customer, not to the banks

The customer sees the money instantly. The banks settle **hours later**, on a net basis.

The bridge between those two facts is **prefunding**: every participating PSP holds a cash
deposit sufficient to cover its net position in a **segregated, interest-bearing account at the
Bank of England** `[reported]`. This eliminates settlement risk — a failing participant cannot
take others down — at the cost of tying up liquidity. The settlement lag can be several hours
during the week `[reported]`.

**The 2026 change worth knowing.** In **July 2026 Pay.UK went live with a flexible liquidity
model for Faster Payments Net Sender Caps**, explicitly to reduce prefunding requirements and
lower the cost of direct access for non-bank PSPs `[reported]`. Prefunding has been the single
biggest economic barrier to direct participation; if you evaluated direct access before mid-2026
and rejected it on liquidity cost, that calculation has changed.

**Three access models**, and they are genuinely different architectures `[reported]`:

| Model | Settlement account | Who clears | What you build |
| --- | --- | --- | --- |
| **Direct participant** | Your own, at the Bank of England | You | Scheme gateway, HSMs, liquidity management, 24/7 payments on-call |
| **Directly connected sponsored participant** | Sponsor's | You (real-time direct technical access) | Scheme gateway; sponsor carries settlement |
| **Indirect participant** | Sponsor's, prefunded for your net activity | Sponsor | An API integration — and a dependency |

Monzo's route through these is the best-documented worked example: a third-party gateway from
2017, then an in-house gateway live November 2019, migrated 2 November 2020 — see
[Monzo (UK)](../banks/monzo.md).

### Bacs — a three-day cycle and a whole message taxonomy

Bacs runs a **three-day cycle** (input, processing, entry) and comes with a set of return message
services that are, in effect, a subsystem you must build `[reported]`:

| Service | What it tells you |
| --- | --- |
| **AUDDIS** | Problems setting up a Direct Debit Instruction, or the payer cancelling the setup. Responses arrive **Day 2** |
| **ADDACS** | Amendments and cancellations of DDIs initiated by the customer |
| **ARUDD** | Returned / unpaid Direct Debits |
| **DDICA** | **Indemnity claims** — the payer's bank clawing money back under the Direct Debit Guarantee |

Two operational traps:

- **Reason code 1 means the payer explicitly cancelled.** Re-presenting after that will produce
  an indemnity claim `[reported]`. Your retry logic must branch on reason code, not on
  "did it fail".
- **Indemnity claims have effectively no time bound.** DDICA reason codes cover amount or date
  differing from the advance notice, no advance notice given, DDI cancelled by the paying bank,
  the payer cancelling directly with the service user, no instruction held, fraudulent signature,
  a claim raised at the service user's request, and the service user's name being disputed
  `[reported]`. Every one of those is a reversal your ledger must accept, possibly months later.

If you support Direct Debit, budget for mandate lifecycle management, advance-notice generation,
reason-code-aware retry, and indemnity handling. It is not an integration; it is a product.

### CHAPS — the one that already migrated to ISO 20022

Real-time gross settlement, same-day, high value — property, treasury, interbank.

The timeline matters because it is the template for what the rest of UK payments is heading
toward `[confirmed]`:

- **19 June 2023** — CHAPS payments migrated to ISO 20022 messaging.
- **28 April 2025** — the Bank of England's new RTGS core ledger and settlement engine went live.
- **1 May 2025** — enhanced data became **mandatory**: Purpose Codes and LEIs on domestic
  interbank CHAPS payments (pacs.009 CORE and certain pacs.008), and Purpose Codes on property
  transactions.
- **2026** — the Bank is consulting on extending RTGS and CHAPS settlement hours toward
  **near-24x7 settlement**, which would allow more frequent net settlement cycles and lower
  prefunding costs across the other rails too `[confirmed]`.

The direction of travel is unambiguous: **structured, mandatory, machine-readable data attached
to payments.** Build your internal message model on ISO 20022 semantics now, even where the rail
you touch today does not require it.

### Open banking and A2A

PSD2-derived, mature. The UK Payments Initiative (announced 2 June 2026) is pushing commercial
Variable Recurring Payments for recurring business and government collections — the first
credible challenge to Direct Debit's monopoly on "pull" payments `[reported]`.

---

## USA rails

### ACH — cheap, slow, and governed by a return-rate threshold

ODFI (originating institution) → ACH operator → RDFI (receiving institution). The return codes
are the entire risk model:

| Code | Meaning | What to do |
| --- | --- | --- |
| **R01** | Insufficient funds | Retry — but **wait 3–5 business days** before the first attempt `[reported]` |
| **R09** | Uncollected funds | As R01 |
| **R10** | Customer advises not authorised | **Never retry** |
| **R29** | *Corporate* customer advises not authorised | **Never retry.** Must be returned within **2 banking days** `[reported]` |
| **R05, R07, R11, R51** | Other unauthorised variants | **Never retry** |

**The number that can end your ACH access:** Nacha's **Unauthorized Return Rate Threshold is
0.5%**, measured across R05, R07, R10, R29 and R51 `[reported]`. That is not a target — it is a
threshold with enforcement behind it. It means unauthorised-return rate is a metric your product
and risk teams must monitor continuously, and it makes consent capture and clear billing
descriptors an engineering concern, not a marketing one.

**Same Day ACH** per-entry limit rises from $1m to **$10m, effective 17 September 2027**
`[reported]`.

### RTP and FedNow — two instant rails, not one

| | **RTP** (The Clearing House) | **FedNow** (Federal Reserve) |
| --- | --- | --- |
| Live since | 2017 | 2023 |
| Transaction limit | **$10m** (raised from $1m, Feb 2025) | **$100k** default, raisable to **$500k** `[reported]` |
| Messaging | ISO 20022 | ISO 20022 |
| Direction | **Credit-push only** | **Credit-push only** |
| Participants | 550+ FIs | 650+ FIs |

Both carry request-for-payment messages alongside credit transfers, and FedNow also defines
interbank liquidity transfer and system/account reporting messages `[reported]`.

**Credit-push only** is the design fact that matters. Neither rail can *pull* funds. Any product
that needs to debit a customer — subscriptions, loan repayments, top-ups — still needs ACH or
cards underneath, with request-for-payment as at best a nudge. This is the opposite of the UK,
where Direct Debit makes pull the default and instant is push-only too.

Because the two networks have different reach, limits and pricing, a US neobank needs a **routing
layer** that picks per transaction on cost, speed and reachability — not a hardcoded rail.

---

## Cards — three events, three files, T+1 or T+2

Cards are the odd one out because the three stages are maximally separated `[reported]`:

1. **Authorisation** — real-time, sub-second, a hold. No money moves.
2. **Clearing** — authorisations are batched and presented, usually overnight. The scheme
   calculates what every issuer owes every acquirer, compressing gross flows into a small number
   of net positions.
3. **Settlement** — net positions move. Interchange is applied here. The acquirer funds the
   merchant typically **T+1 or T+2**.

For an issuer this means your ledger sees a *hold* at authorisation and a *clearing* posting
later — for a different amount, sometimes days later, sometimes never (expired auths). Modelling
these as one event is the classic issuer bug. See [Card issuing and processing](../layers/04-card-issuing.md).

---

## Cross-border

Correspondent banking, with the practical shape Monzo published `[confirmed]`: support **40+
currencies without holding an account in each one** by having a partner bank receive the payment,
perform the exchange, and forward it over **SWIFT** with the rate attached. Plus IBAN checksum
validation, BIC routing, and idempotency for exactly-once.

Stablecoin settlement (Bridge/Stripe, BVNK/Mastercard, Circle) is a real alternative where
dollar bank rails are slow, expensive or absent — see [Payment rails and money movement](../layers/03-payment-rails.md).

---

## What this forces you to build

**1. A payment state machine with a long tail.**

```
initiated → risk-checked → authorised → submitted → accepted → settled
     │            │             │            │           │
     └─ blocked   └─ rejected   └─ failed    └─ returned  └─ reversed
```

The tail lengths per rail are the design constraint:

| Rail | Reversal window |
| --- | --- |
| Faster Payments | Minutes to hours (recall, not guaranteed) |
| Cards | Chargeback windows — up to 120+ days by scheme rules |
| ACH | Days — R01 within 2 banking days for most, longer for consumer unauthorised |
| **Bacs Direct Debit** | **Effectively unbounded** — indemnity claims under the Guarantee |

**2. A liquidity management system, if you go direct.** Prefunding is not a one-off deposit; it
is a continuously managed position with caps, monitoring and top-up automation. This is the part
teams underestimate when they model direct participation as purely a technical project.

**3. Rail-aware retry.** Branch on reason code, never on "it failed". Retrying an R10 or a Bacs
reason code 1 is not a bug that costs you a payment — it is a compliance event.

**4. Cut-offs and value dating as first-class concepts.** Every rail has a cut-off; a payment
submitted after it takes a different value date. Customers experience this as "the money
vanished for a day".

**5. Reconciliation inputs per rail.** Each adapter must emit the statement side of the
reconciliation — see [Deep dive — Reconciliation (build)](../deep-dives/01-reconciliation.md) and the normalisation-layer argument in
[Deep dive — Rail adapters (buy access, build normalisation)](../deep-dives/02-rail-adapters.md).

## The questions to ask

1. For each rail: are we direct, sponsored, or indirect — and what breaks if the sponsor exits?
2. Does our ledger model authorisation, clearing and settlement as **three** events?
3. What is our unauthorised ACH return rate, and who watches it against the 0.5% threshold?
4. Does retry logic branch on reason code?
5. Can we accept a Bacs indemnity claim arriving a year later and reverse it cleanly?
6. Who manages the prefunded position, and what happens when it is exhausted mid-day?
7. Is our internal message model ISO 20022-shaped?
8. What routes a US payment between ACH, RTP and FedNow — and is it a decision or a hardcode?

## Open questions

- What is the actual all-in cost of FPS direct participation post the July 2026 Net Sender Cap
  change? The barrier is said to have dropped; no public number found.
- Typical unauthorised-return rates for consumer neobanks against the 0.5% threshold.
- Has any neobank published its Direct Debit indemnity claim rate?
- Does the RTGS near-24x7 consultation outcome change prefunding economics materially?

## Sources

- Bank of England, RTGS Renewal Programme — https://www.bankofengland.co.uk/payments/rtgs-renewal-programme
- Bank of England, mandating ISO 20022 enhanced data in CHAPS — https://www.bankofengland.co.uk/payment-and-settlement/rtgs-renewal-programme/additional-guidance-on-mandating-iso20022
- Bank of England, extending RTGS and CHAPS settlement hours — https://www.bankofengland.co.uk/paper/2026/cp/extending-rtgs-and-chaps-settlement-hours-next-steps
- Bank of England, a brief introduction to RTGS and CHAPS — https://www.bankofengland.co.uk/payments/a-brief-introduction-to-the-real-time-gross-settlement-system-and-chaps
- Finextra, Pay.UK launches liquidity model for Faster Payments — https://www.finextra.com/pressarticle/110304/payuk-launches-liquidity-model-for-faster-payments
- Faster Payments, challengers boosted by new settlement model — http://www.fasterpayments.org.uk/press-release/challengers-boosted-new-settlement-model-faster-payments
- Form3, UK Faster Payments Scheme connectivity guide — https://get.form3.tech/how-to-access-faster-payments-scheme/
- ClearBank, indirect access to the UK payments system — https://clear.bank/indirect-access-to-uk-payments-system
- AccessPay, ADDACS reason codes explained — https://www.accesspaysuite.com/blog/addacs-reason-codes/
- AccessPay, AUDDIS reason codes — https://www.accesspaysuite.com/blog/auddis-reason-codes/
- GoCardless, Direct Debit reports and messages from the banks — https://gocardless.com/direct-debit/receiving-messages
- Plaid, ACH return codes — https://plaid.com/resources/ach/ach-return/
- Nacha, ACH network risk and enforcement topics — https://www.nacha.org/rules/ach-network-risk-and-enforcement-topics
- Nacha, new rules — https://www.nacha.org/newrules
- Volante, FedNow vs RTP — https://www.volantetech.com/fednow-vs-rtp-unveiling-the-future/
- Federal Reserve, the FedNow Service and ISO 20022 — https://www.frbservices.org/financial-services/fednow/what-is-iso-20022-why-does-it-matter
- Checkout.com, clearing vs settlement — https://www.checkout.com/blog/clearing-vs-settlement
- Marqeta, card program clearing and settlement — https://www.marqeta.com/blog/card-program-clearing-and-settlement-how-issuer-processors-manage-fund-flow
