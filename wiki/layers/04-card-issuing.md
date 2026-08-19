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
| **Thredd** (formerly GPS) | International issuer-processor, "AI-first", debit + credit + value-added in one composable architecture | **>2bn transactions/yr, 130+ clients, 50+ countries** `[reported]`. Named users: **Curve** (since 2016, 4m+ customers), **Zilch**, **Revolut**, **Starling**. **Arranges BIN sponsorship through partner banks** — e.g. Sutton Bank for US programmes — rather than holding it itself. Sells local scheme-rule and regulatory expertise per market |
| **i2c**, **Wallester**, **Monavate**, **Stripe Issuing** | Alternatives by segment | Stripe Issuing is the fastest route to virtual cards if you are already on Stripe |

## Two completely different things are called a "gateway"

This is the single most common source of confusion in payments, and it costs people whole
conversations `[reported]`:

| | **Scheme gateway** (issuer / bank side) | **Payment gateway** (merchant / acquirer side) |
| --- | --- | --- |
| Connects | Your bank to FPS, Bacs or the card scheme's network | A merchant's checkout to an acquirer |
| Speaks | ISO 8583 / ISO 20022 to a scheme hub | HTTPS APIs, hosted fields, SDKs |
| Built by | Monzo (its Faster Payments gateway) | Adyen, Checkout.com, Stripe, Braintree |
| Concerned with | HSMs, physical links, settlement, availability | Conversion, auth rates, tokenisation, 3DS |

When Monzo says it "moved its Faster Payments gateway in-house", that is the first column. When a
merchant says it "uses Adyen as its gateway", that is the second. **Same word, opposite ends of
the transaction.**

## Issuing vs acquiring — the two sides that meet at the scheme

A card transaction has two halves, and almost every company in payments sits firmly on one side:

```
        ISSUING SIDE                                    ACQUIRING SIDE
   (the cardholder's money)                          (the merchant's money)

  Monzo · Chime · Revolut                    Adyen · Checkout.com · Stripe · Worldpay
         │                                                    │
  issuer-processor                              gateway + acquirer + processor
  (in-house · Thredd · Galileo · Marqeta)
         │                                                    │
         └──────────────  VISA / MASTERCARD  ─────────────────┘
                           (the scheme)
```

**Monzo and Adyen never compete.** They are on opposite ends of the same transaction. When a Monzo
customer buys something from an Adyen merchant: the merchant's checkout hits Adyen's gateway,
Adyen acquires and routes into Mastercard, Mastercard routes to Monzo's issuer processor, Monzo
checks the balance and its fraud controls, and the approval travels all the way back. Two
sophisticated payment companies, one transaction, zero overlap.

### What Adyen and Checkout.com actually are

| | **Adyen** | **Checkout.com** |
| --- | --- | --- |
| Model | **Full-stack**: gateway, acquiring, processing and risk in one system, built in-house on a single platform across markets | Direct acquiring in **55+ countries**, digital-first |
| Licences | Its own **banking and acquiring licences** — EU, UK and US | Acquiring licences; not a bank in the same sense |
| Channels | **Omnichannel** — online plus physical point of sale ("Unified Commerce", its fastest-scaling pillar) | **Digital only — no physical POS** |
| Pitch | Seeing the *whole* payment journey rather than a fragment lets its models approve more good transactions — i.e. **authorisation rate** | Auth-rate performance too: approval analytics, decline recovery, real-time transaction intelligence |

The strategic point: **Adyen's banking licence is what let it expand beyond acquiring** into
issuing, business accounts and embedded lending `[reported]`. That matters here because it means
Adyen is now creeping toward the issuing side — **Adyen Issuing competes with Marqeta**, and in
principle a neobank could use Adyen as its card issuing platform. The two halves of the diagram
above are converging at the edges, and Adyen is the clearest example.

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

## Building from scratch — who covers which of the four roles

The founder's question is not "which processor has the nicest API". It is **how many separate
partners must I find, diligence, negotiate and integrate** — because that, not the API, sets the
launch date.

| Option | BIN sponsor | Processing | Program mgmt | Scheme/rail access |
| --- | --- | --- | --- | --- |
| **Build it all** (Monzo) | You | You | You | You |
| **Marqeta + TransactPay** | **Covered** — EMI licensed UK/EEA, principal member of Mastercard *and* Visa, live in 25 countries, 16 currencies | **Covered** | **Covered** — UK + EU under one contract | Separate |
| **Thredd + partner bank** | Via partner (e.g. Sutton Bank) | **Covered** | **Covered** — local market experts | Separate |
| **Adyen** | **Covered** — its own banking licence, EU/UK/US | **Covered** | **Covered** | Partly — accounts, not UK schemes |
| **Galileo · Lithic · Highnote** | Via partner banks | **Covered** | Varies | Separate |
| **US sponsor bank** + its processor | **Covered** | **Covered** | **Covered** | **Covered** — on their balance sheet |

**Marqeta's TransactPay acquisition** (announced Feb 2025, completed Aug 2025) is exactly a move
to collapse cells: TransactPay is an EMI licensed in the UK and EEA and a principal member of both
schemes, so Marqeta customers can now run UK and EU card programmes **through a single partner**
rather than assembling several `[reported]`. **Adyen** collapses them a different way — by holding
its own banking licence — and its embedded-finance suite lets a platform white-label payments,
accounts, issuing and capital on Adyen's own licensed infrastructure `[reported]`.

**Marqeta is not itself a bank**; outside the TransactPay footprint it provides technology on top
of bank partners, and its standout capability is **Just-in-Time funding** — authorising and
funding a transaction in real time from your own logic `[reported]`.

### Choosing, honestly

| Situation | Pragmatic answer |
| --- | --- |
| UK/EU, no licence, ship this year | **Marqeta + TransactPay** — fewest separate partners in Europe |
| Multi-country, cards *are* the product | **Thredd** — breadth and local scheme expertise |
| You also acquire from merchants | **Adyen** — issuing and acquiring on one licensed platform |
| US, developer-led, virtual cards | **Lithic** or **Highnote** (one API and one ledger for both sides) |
| US, no charter, bundle everything | **Sponsor bank + its processor** — fastest, and their balance sheet |
| Millions of cards already | **Consider building** — only when fees are the top cost line or their release train gates product |

**The mistake to avoid:** choosing a processor on API quality, then discovering **BIN sponsorship
is a separate six-month conversation with a bank that has its own risk appetite**, and that
disputes, chargebacks and scheme compliance are yours unless someone contracted to take them. Ask
every vendor: *"Which of the four roles are you, contractually, and who fills the others?"*

**And scheme access is a separate track.** Nothing in that table gets you onto Faster Payments or
Bacs — see [Deep dive — Payment rails](../deep-dives/05-payment-rails.md). Cards and domestic rails are independent procurements,
and rarely the same vendor.

## Own licence + BIN sponsor — a coherent configuration

**A regulatory licence and scheme membership are two different permissions** `[reported]`:

- Your FCA/PRA licence (bank or EMI) = permission to **hold customer money**
- Visa/Mastercard **principal membership** = permission to **issue cards under your own BIN**

The licence is a *prerequisite* for membership, not a substitute. Principal membership additionally
requires collateral, scheme certification, operational infrastructure and **ongoing dues running
into millions of euros annually** `[reported]`. So a licensed institution can rationally keep its
licence and rent scheme access.

| | Licence + principal | **Licence + BIN sponsor** | No licence + sponsor bank |
| --- | --- | --- | --- |
| Regulatory licence | You | **You** | Sponsor's |
| Scheme principal member | You | **The sponsor** | Sponsor |
| Holds customer funds | You | **You** — your balance sheet, your ledger | Sponsor's omnibus/FBO |
| Issuer of record | You | **The sponsor** | Sponsor |
| Liable to the scheme | You | **Sponsor → recovers from you by contract** | Sponsor |

The middle column keeps the things that matter strategically — the licence, the funds, the ledger,
the customer relationship — while skipping the scheme joining cost. What it does **not** do is move
the economics: the sponsor is liable to the scheme and then **recovers from you under contract,
with losses allocated by root cause** `[reported]`.

**A 2026 change to this trade-off.** Mastercard has **tightened its BIN sponsor rules** (reported
February 2026) `[reported]`. The passive-sponsor model is explicitly obsolete: sponsors now carry
ongoing operational oversight of the programmes they sponsor, face increased audit frequency and
depth, and are accountable for partners' compliance and operational integrity, with every network
mandate assigned, tracked and audit-ready. **"Rent the BIN and be left alone" is no longer the
deal** — expect a materially more intrusive sponsor relationship than two years ago.

## Chargebacks — three questions, not one

**Who is liable**, **who does the work**, and **what tooling it runs on** are separate.

**Liability** flows: the BIN sponsor is issuer of record and liable to the scheme; it then recovers
from the programme manager under contract, with allocation by root cause `[reported]`. You cannot
contract away the economics — only the operations.

**The lifecycle** you are staffing for `[reported]`:
`presentment → pre-dispute → chargeback → representment → pre-arbitration → arbitration → appeal`.
Network rules set **hard deadlines** at each stage; a missed deadline loses the case outright and
repeated misses attract penalties. Deadline pressure, not case volume, is what breaks manual
handling first.

**The tooling, in three layers:**

| Layer | Options |
| --- | --- |
| **Pre-dispute collaboration** — resolve before a chargeback exists | **Ethoca** (Mastercard-owned) flags disputes pre-chargeback · **Verifi** (Visa-owned), issuer-connected, ~24h resolution · **Visa RDR** · **Mastercard Collaboration** |
| **Network platforms of record** — non-optional | **VROL** (Visa Resolve Online) · **MasterCom** |
| **Issuer dispute platform** — intake, routing, evidence, deadlines, reporting | **Quavo (QFD)** — built for issuers and processors, full lifecycle, compliance-automation focus · **Pega Smart Dispute** — Amex/MC/Visa rules, integrates VROL/MasterCom and Ethoca/Verifi, twice-yearly updates, consumer-protection SLAs; mid-to-large institutions · **Rivero (Amiko)** · **Q2/CentrixDQS** for community and regional banks |

**Your processor already covers some of it.** Marqeta, Thredd and Galileo all expose dispute and
chargeback workflow via API as part of card-lifecycle management `[reported]`. For a first
programme that is often enough; the question is whether it survives your volume, regulatory SLAs
and evidence requirements, or only the happy path.

**Build regardless of vendor:** workflows and documentation, team and training, analytics and KPIs,
upstream fraud layering, **transaction descriptors** (a large share of "I don't recognise this"
disputes are just an unrecognisable descriptor), and case history and audit trail `[reported]`.

### By configuration

| Setup | Dispute operations |
| --- | --- |
| Licence + **Marqeta/TransactPay** | Start on Marqeta's dispute APIs; add **Quavo** or **Rivero** when volume or SLAs outgrow it. Ethoca and Verifi from day one |
| Licence + **Adyen** | Adyen is principal member on its own licence, so disputes sit inside its platform. Least assembly, least control |
| Licence + **Thredd** + separate sponsor | Thredd runs the workflow; **negotiate explicitly** with the sponsor over who runs cases and who absorbs losses |
| Licence + **own principal membership** | All yours — you need a real platform and a staffed team from launch |

**The clause to read before the API docs:** *who absorbs a loss when root cause is contested, and
what is the process for deciding?*

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
