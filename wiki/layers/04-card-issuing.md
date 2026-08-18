---
title: Card issuing and processing
type: layer
status: living
updated: 2026-08-18
sources: 7
tags: [cards, issuing, processor]
---

## Summary

The issuer-processor answers scheme authorisation requests in the hot path — a hard latency
budget, no acceptable downtime, and the place where your balance, your fraud controls and
your product rules must all agree within a few hundred milliseconds. It is the layer most
neobanks buy first and, if they get big enough, the layer they most want back.

## The stack, decomposed

Four roles, often sold bundled and frequently confused:

1. **BIN sponsor / issuing bank** — the licensed principal member of Visa/Mastercard whose
   BIN your cards sit under.
2. **Issuer-processor** — receives ISO 8583 / scheme authorisation messages, applies rules,
   returns approve/decline, produces clearing and settlement files.
3. **Program manager** — commercial wrapper: onboarding, disputes, scheme compliance.
4. **Card manufacture and fulfilment** — physical plastic, personalisation, mailing.

Know which of the four each vendor is actually providing before you sign.

## Vendors

| Vendor | Position | Notes |
| --- | --- | --- |
| **Marqeta** | Largest independent issuer-processor; debit, credit, prepaid; US-strongest | ~$383bn processed 2025; first GAAP-profitable quarter early 2026; 2025 acquisition of EMI TransactPay added UK/EU BIN sponsorship and program management `[reported]` |
| **Galileo** (SoFi) | Visa-certified processor behind many neobanks; expanding into sponsor banking | Powers Chime among others `[reported]`; also sells Cyberbank Core |
| **Lithic** | Developer-first US issuing, from the Privacy.com team | >$1bn/month processed `[reported]` |
| **Highnote** | Issuing *and* acquiring behind one API and one ledger | $90m Series B in 2025 `[reported]`. The single-ledger claim is architecturally interesting if you do both sides |
| **Thredd** | International issuer-processor | >2bn transactions/yr, 130+ clients, 50+ countries `[reported]`. Common for UK/EU programmes |
| **i2c**, **Wallester**, **Monavate**, **Stripe Issuing** | Alternatives by segment | Stripe Issuing is the fastest route to virtual cards if you are already on Stripe |

## Build vs buy

Chime is the current best argument for building. It rolled out **ChimeCore**, a proprietary
platform processing a portion of transactions and handling bookkeeping, and since late 2024
it processes **100% of its users' credit-card transactions** `[confirmed]`. Its S-1 gives
the rationale as reduced software maintenance cost and reduced dependence on third-party
providers `[confirmed]`, with reporting attributing a cost-to-serve roughly one third of a
large bank's to owning the processor `[reported]`.

SoFi took the other route to the same place: it *bought* the processor (Galileo, 2020) and
the core (Technisys, 2022), and now sells both to competitors `[confirmed]`.

The threshold question is volume. Below a few million cards, the processor fee is cheaper
than the team; above it, the fee becomes the largest line item in cost-to-serve and the
release train becomes the binding constraint on product.

## What the choice forces downstream

- **A slow ledger read does not fail safe.** If the issuer cannot answer in time, **the scheme
  invokes its own stand-in and approves on your behalf** — potentially beyond available balance,
  with none of your fraud checks having run `[confirmed]`. Monzo hit this at P99 400–500ms on
  balance reads and engineered down to ~200ms. Budget the ledger read as part of the auth path,
  not as a separate concern. See [Core ledger and product engine](../layers/02-core-ledger.md).
- **Authorisation latency budget.** Whatever fraud scoring you want in-line must fit inside
  the scheme's timeout minus network. This is the single hardest constraint on
  [Financial crime — AML, transaction monitoring, fraud](../layers/06-fincrime.md) and drives the feature-store design in [Data and ML platform](../layers/08-data-ml-platform.md).
- **Stand-in processing.** What happens to authorisations when your ledger is unavailable?
  Every processor has a stand-in policy; you must decide the limits and own the resulting
  exposure. If you build, you must build stand-in yourself.
- **Dispute and chargeback workflow.** Scheme-mandated timelines, evidence packs,
  representment. Usually underestimated by an order of magnitude.
- **Tokenisation and wallets.** Apple Pay/Google Pay provisioning, network tokens, 3DS.
  Buying gets these; building means scheme certification for each.

## Open questions

- What is ChimeCore actually built on, and does it hold the deposit sub-ledger or only
  authorisation plus bookkeeping?
- Post-TransactPay, is Marqeta a credible single-vendor answer for a UK launch or still
  US-first in practice?
- What do issuer-processors charge per authorisation at 1m / 5m cards in 2026? (No reliable
  public number found — a gap worth filling.)

## Sources

- Highnote, Stripe Issuing vs Marqeta vs Highnote — https://highnote.com/blog/stripe-issuing-vs-marqeta-vs-highnote-enterprise-comparison-guide
- OpenBankingTracker, card issuing platforms — https://www.openbankingtracker.com/embedded-finance/category/card-issuing
- SDK.finance, top card issuing platforms — https://sdk.finance/blog/top-10-card-issuing-platforms-a-comprehensive-comparison-for-fintech-businesses/
- wiki.private.law, BIN sponsorship and issuer-processors — https://wiki.private.law/en/issuer-processors
- Banking Dive, Chime IPO filing — https://www.bankingdive.com/news/chime-files-for-ipo-sec-nasdaq-chym/748152/
- SiliconANGLE, Chime IPO and ChimeCore — https://siliconangle.com/2025/06/02/financial-technology-company-chime-seeking-11-2b-valuation-upcoming-ipo/
- WhiteSight, SoFi's Galileo-Technisys stack — https://whitesight.net/sofis-technology-platform-the-galileo-technisys-stack-unpacked/
