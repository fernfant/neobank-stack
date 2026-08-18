---
title: UK vs USA — where the stacks diverge
type: comparison
status: living
updated: 2026-08-18
sources: 10
tags: [uk, usa, comparison]
---

## Summary

The application layer looks the same on both sides of the Atlantic. Everything underneath is
different, and four differences dominate: **licence structure**, **payment rails**, **credit
data**, and **fraud liability**. A stack designed for one market does not port; the ledger and
the product layer might, but the money-movement, fincrime and decisioning layers will not.

## The table

| Dimension | UK | USA |
| --- | --- | --- |
| **Route to market** | Real bank licences are attainable — Monzo, Starling, Revolut, Zopa, Atom, Kroo all hold one. EMI is the fast alternative | Charters are rare (Varo the notable consumer-fintech exception). Sponsor bank is the default |
| **Regulator** | FCA + PRA; PSR for payment systems | Fragmented: OCC/FDIC/Fed via the sponsor, CFPB for consumer, FinCEN for BSA/AML, 50 states for money transmission |
| **Instant rail** | Faster Payments — universal, mature, >5.1bn payments/yr | RTP + FedNow — two competing networks, ~550 and ~650 FIs, still a small share of volume |
| **Batch rail** | Bacs (3-day), Direct Debit with mandates and indemnity claims | ACH / Same Day ACH, Nacha return codes |
| **Rail access** | Direct BoE settlement account, or agency via ClearBank/LHV/Banking Circle | Via sponsor bank, or Dwolla/Moov/Increase style access |
| **Open banking** | Mature since PSD2; A2A and VRPs advancing (UKPI, June 2026) | CFPB §1033 standardised APIs from April 2026 — catching up |
| **Credit data** | Experian/Equifax/TransUnion + rich open-banking transaction data | Same three bureaus + FICO/VantageScore; cash-flow data newly productised (FICO×Plaid, Experian, Nova Credit) |
| **Decline explainability** | Consumer Duty, affordability evidence | ECOA/Reg B adverse action reason codes — legally specific |
| **Scam liability** | **Mandatory APP fraud reimbursement** to £85k, 50/50 sending/receiving PSP, since Oct 2024 | **No equivalent.** Liability largely rests with the consumer for authorised payments |
| **Safeguarding/deposit** | FSCS £85k for banks; CASS-style safeguarding with **daily reconciliation** from May 2026 for EMIs | FDIC insurance passed through the sponsor; near-real-time reconciliation proposed post-Synapse |
| **Interchange economics** | Capped low (EU-derived caps) — interchange is not a business model | Durbin-exempt debit interchange is *the* neobank revenue model |
| **Cloud** | AWS-dominant; Revolut on GCP | Mixed |
| **Resilience regime** | FCA/PRA SS2/21, PS6/21, critical third parties regime; DORA-aligned | Interagency guidance; no single DORA equivalent |

## The four divergences that force different architecture

### 1. Interchange changes what you optimise

US neobank revenue is dominated by debit interchange under the Durbin exemption. That makes
**card authorisation volume and approval rate** the primary P&L lever, which is why Chime
insourced the processor and why US neobanks obsess over decline rates. UK interchange caps mean
UK challengers monetise through lending, subscriptions and business banking instead — which is
why Monzo's and Revolut's ML priorities lead with credit and fincrime rather than
authorisation optimisation.

### 2. APP reimbursement makes outbound fraud a UK-only P&L line

Since 7 Oct 2024 UK PSPs reimburse most APP fraud to £85k, split 50/50 between sending and
receiving PSP, with the PSP carrying the burden of proving gross negligence. Result: UK
neobanks build **in-flight intervention** on outbound payments (Monzo's reactive platform) and
**mule detection** on inbound. US neobanks have no such mandate and invest correspondingly less
in outbound scam prevention.

If you are porting a US stack to the UK, this is the single biggest gap you will discover late.

### 3. Rail maturity changes the product

Faster Payments being universal and instant means UK customers expect instant, free A2A
transfers as a baseline. In the US, instant is a *premium feature* — which is why "instant
transfer for a fee" is a US neobank revenue line and would be unsellable in the UK.

### 4. Licensing shapes the reconciliation burden differently

UK: if you are an EMI you owe daily safeguarding reconciliation and a 48-hour resolution pack
from 7 May 2026. USA: if you are a fintech on a sponsor bank you owe your sponsor
near-real-time reconciliation evidence under the FDIC's proposed rule. **Both markets converged
on the same conclusion — reconciliation must be continuous and provable — from opposite
directions.** That is the strongest signal in this whole research: build the reconciliation
subsystem first, whichever market you are in.

## Open questions

- Will any US regulator import APP-style reimbursement for Zelle/RTP scams?
- Does §1033 close the open-banking data gap in practice by end-2026, or does aggregator
  pricing keep it open?
- Does the RPIB/NPA outcome change the direct-vs-agency access calculus for UK challengers?

## Sources

- PSR, APP fraud reimbursement requirements — https://www.psr.org.uk/news-and-updates/latest-news/news/psr-confirms-new-requirements-for-app-fraud-reimbursement/
- Crowdfund Insider, PSR evaluation of APP policy (July 2026) — https://www.crowdfundinsider.com/2026/07/290056-uk-payment-systems-regulator-psr-confirms-app-fraud-reimbursement-policy-delivers-strong-positive-results/
- Transfi, UK payment rails — https://www.transfi.com/blog/united-kingdoms-payment-rails-how-they-work---faster-payments-bacs-chaps-open-banking
- Bank of England, RPIB consultation — https://www.bankofengland.co.uk/news/2026/june/rpib-launches-consultation-on-next-generation-uk-payments-infrastructure
- eco.com, FedNow vs RTP 2026 — https://eco.com/support/en/articles/15650251-fednow-vs-rtp-2026-real-time-payment-rails-compared
- ClearBank, FCA safeguarding PS25/12 — https://clear.bank/learn/insights/the-fcas-safeguarding-overhaul-the-new-rules-their-impact-and-how-to-prepare
- National Law Review, BaaS liability allocation — https://natlawreview.com/article/who-owns-compliance-failure-bank-fintech-liability-allocation-banking-service-baas
- EQWIRE, EMI vs bank UK — https://eqwire.com/news/fca-authorised-emi-vs-bank-uk
- FICO × Plaid — https://www.fico.com/en/newsroom/fico-partners-plaid-launch-next-generation-cash-flow-ultrafico-score
- App Economy Insights, how Chime makes money — https://www.appeconomyinsights.com/p/chime-how-they-make-money
