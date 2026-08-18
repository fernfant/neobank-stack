---
title: Licence and charter — whose balance sheet?
type: layer
status: living
updated: 2026-08-18
sources: 8
tags: [regulation, uk, usa, licensing]
---

## Summary

The licence determines what your ledger *means*. A deposit at a licensed bank is a
liability on your balance sheet, insured by FSCS/FDIC, settled from your own central-bank
account. An e-money balance is a claim against safeguarded funds. A sponsor-bank fintech
balance is a sub-ledger position inside someone else's FBO account. Same UI, three utterly
different correctness requirements.

## UK

| Path | Regulator | Capital floor | Funds protection | Ledger implication |
| --- | --- | --- | --- | --- |
| Bank licence | PRA + FCA | £5m initial `[reported]`; £1m in mobilisation `[reported]` | FSCS to £85k | You own the system of record; you can hold a BoE settlement account and join FPS directly |
| EMI (Electronic Money Institution) | FCA | £350k or 2% of avg outstanding e-money `[reported]` | Safeguarding (segregated trust or insurance), **not** FSCS | Your ledger tracks claims; a safeguarding reconciliation ledger runs alongside it |
| Payment Institution (PI) | FCA | Lower still | Safeguarding | Payments only, no stored value |
| Agency / sponsored access | via a sponsor bank | n/a | Sponsor's | You are a sub-ledger tenant |

**Mobilisation** is the UK's distinctive feature: a two-stage bank authorisation where you
get a restricted licence (typically capped deposits) while you finish building and testing,
then lift restrictions on demonstrating operational readiness `[reported]`. Architecturally
this is a gift — it gives you a real regulatory environment to run migration and
reconciliation rehearsals in, with a bounded blast radius. Plan the mobilisation period as
an engineering phase with explicit exit criteria, not as paperwork.

**Safeguarding is now an engineering requirement.** FCA PS25/12 takes effect **7 May 2026**
and imposes on EMIs and PIs `[confirmed]`:

- mandatory **daily** reconciliation of safeguarded funds,
- **monthly** regulatory returns,
- **annual** safeguarding audits,
- a board-designated individual accountable for safeguarding,
- CASS 10 resolution packs retrievable within **48 hours**.

Read that as: a daily-close reconciliation pipeline with break detection and an
auditable resolution-pack export must be in your v1 architecture if you take the EMI path.

## USA

| Path | Regulator | Reality |
| --- | --- | --- |
| National bank charter | OCC | Rare for consumer fintech. Varo was the first consumer fintech to get one `[confirmed]` |
| State bank / ILC | State + FDIC | Slow, politically contested |
| Sponsor bank partnership | Sponsor's regulator (FDIC/OCC/Fed) | The default. The fintech is not the regulated entity — but its controls are examined through the bank |
| MSB / money transmitter | FinCEN + 50 states | Required for remittance and wallet models; own BSA/AML programme and SAR obligations `[reported]` |

**The Synapse lesson.** Synapse sat as middleware holding the ledger that mapped pooled FBO
deposits to end users. It filed Chapter 11 in April 2024 leaving a $60–90m shortfall
`[reported]`. Between 2022 and 2025 the FDIC, OCC and Fed issued consent orders against
seven sponsor banks running BaaS programmes; Evolve Bank & Trust took a Fed cease-and-desist
in May 2025 for failure to oversee fintech partners `[reported]`. The consistent finding:
**the chartered bank bears the regulatory consequence, and the middleware ledger was the
single point of failure** `[reported]`.

The FDIC's proposed recordkeeping rule (informally "the Synapse rule") requires **near
real-time reconciliation of all fintech partner accounts** `[confirmed]`. For an architect
this collapses a whole design space: if you are a US fintech on a sponsor bank, you must be
able to prove, continuously, that your sub-ledger sums to the bank's FBO balance, per end
user, with an audit trail. Design for the bank to be able to query your ledger, not just
receive a file.

### What this forces downstream

- **Charter → own ledger, own settlement, own scheme membership.** Highest cost, highest
  control, and you inherit 24/7 money on-call.
- **EMI/sponsor → dual ledger.** Your product ledger *plus* a reconciliation ledger against
  the partner. Never let these be the same table with a flag.
- **MSB → licensing sprawl.** 50-state money transmitter licensing is an operational, not
  technical, drag but it gates market launch sequencing. Remitly's architecture is shaped by
  this — see [Remitly (USA / cross-border)](../banks/remitly.md).

## Open questions

- Does the FDIC's proposed rule get finalised in its current form, and what latency does
  "near real-time" actually resolve to in the final text?
- Is the UK mobilisation route still ~12–18 months end-to-end in 2026, or has FCA
  throughput changed?
- How many of the current UK "neobanks" are EMIs rather than banks? (One estimate: fewer
  than 20% of firms marketed as neobanks hold a full banking licence `[reported]` — worth
  verifying against the FCA register directly.)

## Sources

- Bratby Law, FCA authorisation for PIs and EMIs — https://bratby.law/practice-areas/payments-regulation/authorisation-and-licensing/
- ClearBank, FCA safeguarding overhaul PS25/12 — https://clear.bank/learn/insights/the-fcas-safeguarding-overhaul-the-new-rules-their-impact-and-how-to-prepare
- The Payments Association, CASS 15 compliance — https://thepaymentsassociation.org/whitepaper/safeguarding-how-payment-and-e-money-firms-can-stay-compliant-with-cass-15/
- EQWIRE, FCA-authorised EMI vs bank — https://eqwire.com/news/fca-authorised-emi-vs-bank-uk
- Yale Journal of International Affairs, the Synapse collapse — https://www.yalejournal.org/publications/the-synapse-collapse
- National Law Review, bank-fintech liability allocation — https://natlawreview.com/article/who-owns-compliance-failure-bank-fintech-liability-allocation-banking-service-baas
- Legis1, Synapse collapse and accountability gap — https://legis1.com/news/synapse-collapse-fintech-regulation-exposes
- Temenos, Varo national bank charter — https://www.temenos.com/press_release/varo-first-consumer-fintech-granted-national-bank-charter-in-the-us-goes-live-with-temenos-cloud-technology/
