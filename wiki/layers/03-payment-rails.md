---
title: Payment rails and money movement
type: layer
status: living
updated: 2026-08-18
sources: 10
tags: [payments, uk, usa, rails]
---

## Summary

> **Deeper treatment:** settlement mechanics, prefunding, access models, Bacs message
> taxonomy and ACH return-code risk are in [Deep dive — Payment rails](../deep-dives/05-payment-rails.md).

Rails are the layer where your clean internal model meets other people's weak delivery
guarantees. The engineering job is to normalise every rail behind an adapter into one
internal money-movement model, and to make the ledger the only place financial state lives
`[reported]`.

## UK rails

| Rail | Speed | Use | Notes |
| --- | --- | --- | --- |
| **Faster Payments (FPS)** | Seconds, 24/7 | P2P, most outbound | >5.1bn payments/yr `[reported]`. Direct participation requires a settlement account at the Bank of England; otherwise you go via a sponsor/agency bank or an aggregator (ClearBank, LHV, Banking Circle) |
| **Bacs** | 3-day cycle | Salaries, Direct Debits, supplier payments | ~£6bn/day early 2025 `[reported]`. Direct Debit means mandate management, ADDACS/AUDDIS reason codes, and indemnity claims — a whole subsystem |
| **CHAPS** | Same-day, high value | Property, treasury | ~£378bn/day over ~200k payments `[reported]` |
| **Open Banking / A2A** | Real-time | Pay-by-bank, VRPs | The UK Payments Initiative (announced 2 June 2026) aims to scale commercial VRPs for recurring business/government payments `[reported]` |
| **Cards (Visa/Mastercard)** | Real-time auth, T+n settle | Everyday spend | See [Card issuing and processing](../layers/04-card-issuing.md) |

**The NPA question.** The New Payments Architecture was conceived to consolidate FPS, Bacs,
CHAPS and cheques onto one ISO 20022 framework, but scope was narrowed after regulatory
review to **replacing Faster Payments**, with Bacs optional later `[reported]`. On 25 June
2026 the Retail Payments Infrastructure Board opened a consultation on the design of the
next-generation retail payments infrastructure `[confirmed]`. Practical read: assume
ISO 20022 message models internally now, but do not build to a specific NPA API yet.

**Confirmation of Payee** is mandatory name-checking on outbound payments; the PSR is
consulting on richer transaction-level data sharing, including signals like account age and
usage frequency `[reported]`. This is an integration on your outbound path with real
latency and real UX consequence.

## USA rails

| Rail | Speed | Use | Notes |
| --- | --- | --- | --- |
| **ACH / Same Day ACH** | 1–3 days / same day | Payroll, bills, funding | Still the cheapest for recurring low-value, non-time-critical flows `[reported]`. Nacha rules; return codes (R01, R10…) drive a whole risk model |
| **RTP (The Clearing House)** | Instant, 24/7 | A2A, disbursements | 550+ FIs; >1.5m payments/day in 2026; approaching $500bn/quarter `[reported]` |
| **FedNow** | Instant, 24/7 | Same | 650+ FIs in 2026 `[reported]` |
| **Wire (Fedwire/CHIPS)** | Same-day | High value | |
| **Cards** | Real-time auth | Everyday spend | Durbin interchange economics are the core US neobank revenue model |
| **Push-to-card (Visa Direct / Mastercard Send)** | Near-instant | Disbursements, cash-out | Common neobank instant-transfer feature |

Instant payments in the US are still a small fraction of non-cash volume but growing fastest
in payroll, insurance disbursement and A2A `[reported]`. Nearly 70% of businesses expect to
adopt RTP or FedNow within two years `[reported]`. For a consumer neobank the practical
posture in 2026 is: ACH as the workhorse, RTP/FedNow for the premium "instant" tier, and a
routing layer that picks per transaction on cost/speed/reachability.

## Cross-border

Remitly's model — direct integrations with banks, MTOs and payout agents across corridors,
with funding, FX and payout as separate stages `[reported]` — is the reference. The hard
parts are corridor-specific: payout partner reliability, cut-off times, FX rate sourcing and
hedging, and a state machine for a transfer that can be pending for days.

**Stablecoins** are now a legitimate settlement rail for this problem. GENIUS Act signed
18 July 2025, effective 18 January 2027, with OCC/FDIC/Treasury NPRMs in 2026 `[reported]`.
Stripe acquired Bridge for $1.1bn (Feb 2025) and launched Stablecoin Financial Accounts in
101 countries; Mastercard acquired BVNK (Mar 2026, up to $1.8bn) `[reported]`. Relevant
where dollar bank rails are slow or absent; largely irrelevant to a domestic UK/US current
account.

## Engineering pattern: the money-movement layer

Sit one layer between rails and ledger `[reported]`:

- **Adapters** per rail, normalising inbound/outbound events into one internal model.
- **Deduplication and ordering** — every rail will redeliver, reorder, or arrive late.
- **A payment state machine** that is explicit about `initiated → authorised → submitted →
  settled → reversed/returned`, with returns arriving days later (ACH R-codes, Direct Debit
  indemnity claims).
- **Reconciliation workers** reading rail statements against postings, emitting breaks.
- **Idempotency keys** end to end.

The failure mode this prevents: adapter-specific bugs propagating into the ledger, and
balance state being replicated at the webhook layer where it drifts `[reported]`.

## Worked example — Monzo's insourcing sequence

The clearest public account of a UK bank taking each rail in-house, and a useful template for
sequencing `[confirmed]`:

| Rail | Before | In-house from | What forced it |
| --- | --- | --- | --- |
| Cards | GPS (now Thredd), prepaid only | Current-account launch, 2017–18 | Vendor outages; wanting to own the whole experience |
| Faster Payments | Unnamed third-party gateway | Gateway live Nov 2019, migration 2 Nov 2020 | A payments incident on 30 May 2019; active-standby failover took ~15 minutes |
| Bacs | A sponsor bank, from 2017 | Direct participant, 12 Sept 2022 | Manual transfers to the sponsor, and **regulatory caps on funds held at the sponsor during payroll peaks** |

Two details worth carrying into your own design. First, Monzo's FPS gateway is a **deliberate Go
monolith, active-active across two data centres on VMs with Docker Compose** — at a company
otherwise famous for four-figure microservice counts. The rail gateway is a different problem
from the product estate, and they built it differently on purpose. Second, they implemented
**stand-in store-and-forward at the gateway**: on a per-message timeout it answers the scheme
hub itself and forwards later, so a slow internal processor never becomes a rejected customer
payment. Full detail in [Monzo (UK)](../banks/monzo.md).

## Cross-border, done properly — Monzo's pipeline

Monzo's international payments system is the clearest public instance of the money-movement layer
pattern `[confirmed]`. Four stages:

**adapter → deciders → effects → application**

- **Adapters** marshal each partner's wire format into one common representation.
- **Deciders** run in parallel returning Accept / Reject / **Hold**, with explicit precedence:
  Hold blocks, Reject overrides Accept. Encoding precedence rather than ordering rules is what
  keeps compliance and limits logic from becoming an if-ladder.
- **Effects** are generated from the decision — ledger entries, notifications, internal movements —
  and then **applied and logged separately**. Splitting "decide what should happen" from "make it
  happen" is what makes the whole thing testable and auditable.

FX for **40+ currencies without holding accounts in each**: a correspondent partner bank receives
the payment, does the exchange, and forwards over **SWIFT** with the rate attached. Plus IBAN
checksum validation, BIC codes, and idempotency for exactly-once. Each partner gets an adapter and
a separate microservice for its quirks, so onboarding a partner never touches the core processor.

## Stand-in at the rail level

Monzo's Stand-in platform accepts **Mastercard, Faster Payments and Bacs** traffic when the primary
is down, routed either through the primary's **edge services** (partial outage — they are earliest
in the payment path and most resilient) or **direct from the data centres** (severe failure)
`[confirmed]`. Detail in [Resilience, regulatory reporting and operations](../layers/10-resilience-regulatory.md) and [Monzo (UK)](../banks/monzo.md).

## Money coming *in* is a different vendor entirely — the gap most layer models skip

Rails cover interbank movement. They do **not** cover how customers put money into your bank. If a
customer funds their account with a debit card, **you are accepting a card payment — that is
acquiring, not issuing**, and your scheme connection does nothing for it.

| Money movement | What it actually is | Who supplies it |
| --- | --- | --- |
| **In — bank transfer** | Inbound FPS to your own sort code | Your scheme connection: Form3 · Icon · Volante, or build |
| **In — card top-up** | **Acquiring.** You are the merchant; the customer's other bank is the issuer | **Checkout.com · Adyen · Stripe · Worldpay · Nuvei** |
| **In — Direct Debit** | A Bacs collection you originate | Your Bacs connection (Adyen also supports top-ups over SEPA, Bacs and ACH) |
| **Out — interbank** | FPS, Bacs, CHAPS | Your scheme connection |
| **Out — push-to-card** | Visa Direct · Mastercard Send | **Checkout.com** (Card Payouts) · Adyen · the schemes directly |
| **Out — card spending** | Issuing authorisation | Your issuer processor — [Card issuing and processing](../layers/04-card-issuing.md) |

**Checkout.com and Form3 are not substitutes** `[reported]`. Form3 connects *your bank* to domestic
schemes where you are the participant; Checkout is an **acquirer** taking card payments *in* where
you are the merchant. A neobank needs both.

Checkout's actual surface: checkout, gateway, tokenisation, processing, **local acquiring in 55+
countries**, fraud controls, **payouts** — Bank Payouts over real-time networks and Card Payouts
via Visa Direct and Mastercard Send — and **issuing capabilities now rolling out in the UAE and
US**, plus open banking and stablecoin investment `[reported]`.

**The convergence to watch:** Adyen already holds its own banking licence and does issuing;
Checkout is moving the same way. "Which side of the transaction is this vendor on?" is becoming a
less clean question — see [Card issuing and processing](../layers/04-card-issuing.md).

## Open questions

- What are the actual per-transaction economics of RTP vs FedNow vs Same Day ACH for a
  consumer neobank at 1m accounts, in 2026?
- Which UK aggregator do most EMIs use for FPS access, and what is the failover story when
  that aggregator has an incident?
- Does the RPIB consultation outcome change the direct-participation calculus for
  challengers?

## Sources

- Transfi, UK payment rails — https://www.transfi.com/blog/united-kingdoms-payment-rails-how-they-work---faster-payments-bacs-chaps-open-banking
- Bank of England, RPIB consultation (June 2026) — https://www.bankofengland.co.uk/news/2026/june/rpib-launches-consultation-on-next-generation-uk-payments-infrastructure
- ACI Worldwide, New Payments Architecture — https://www.aciworldwide.com/new-payments-architecture
- Regulation Tomorrow, UK Payments Initiative launch — https://www.regulationtomorrow.com/2026/06/uk-payments-initiative-uk-banks-and-fintechs-launch-new-payment-scheme/
- PSR, APP fraud and CoP data sharing — https://www.psr.org.uk/news-and-updates/latest-news/news/psr-confirms-new-requirements-for-app-fraud-reimbursement/
- eco.com, FedNow vs RTP 2026 — https://eco.com/support/en/articles/15650251-fednow-vs-rtp-2026-real-time-payment-rails-compared
- Dwolla, FedNow and RTP — https://www.dwolla.com/updates/fednow-and-rtp-everything-you-need-to-know
- Deloitte, instant payments vs ACH — https://www.deloitte.com/us/en/services/consulting/articles/instant-payments-vs-ach.html
- Forbes, stablecoin cross-border payments 2026 — https://www.forbes.com/sites/danielwebber/2026/03/30/stablecoin-cross-border-payments-in-2026-from-theory-to-practice/
- Formance, core banking reference model (money movement layer) — https://www.formance.com/blog/financial-operations/core-banking-system-architecture
