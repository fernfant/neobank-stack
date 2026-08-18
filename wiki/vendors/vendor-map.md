---
title: Vendor map — who uses what
type: vendor
status: living
updated: 2026-08-18
sources: 14
tags: [vendors, attribution, market-map, uk, usa]
---

## Summary

The vendor landscape is well documented. **Which neobank uses which vendor is not** — and that
asymmetry is the whole point of this page. Vendors publish logos; banks rarely confirm. Below is
every attribution that traces to a company statement, a vendor's own named customer list, a
filing or credible trade press, with the confidence tag attached. Where nothing is public, the
page says so rather than guessing.

**Read the gaps as information.** A vendor with a large customer count and no named neobank is
usually selling to banks that do not advertise it, not failing to sell.

## Core banking / ledger

| Vendor | Named users | Confidence |
| --- | --- | --- |
| **Thought Machine Vault Core** | **Zopa** (Biscuit current account — beta Sept 2024, full launch June 2025), **Atom bank**, Lloyds, Standard Chartered, Intesa Sanpaolo, C6, Trust Bank | `[confirmed]` for Zopa; `[reported]` for the rest |
| **10x SuperCore** | **Chase UK** (JPMorgan), Westpac | `[reported]` |
| **Temenos Transact** | **Varo** (cloud-hosted, at charter go-live), ~950 banks total | `[confirmed]` for Varo `[dated: 2020]` |
| **Mambu** | **N26**, ABN AMRO (New10, and its neobank BUUT), Western Union, Commonwealth Bank of Australia, BancoEstado, Wio Bank, Raiffeisen, Bank Islam, Orange Bank, Nyla. **260+ customers in 65 countries** | `[reported]` — vendor's own customer pages |
| **Galileo Cyberbank Core** (ex-Technisys) | **SoFi** — for commercial payment services and its sponsor-banking programme | `[confirmed]` |
| **Finxact** (Fiserv) | Mercantile Bank, Live Oak | `[reported]` |
| **Engine by Starling** | Starling Bank itself; external client list not public | `[reported]` |
| *In-house* | **Monzo**, **Starling**, **Revolut**, **Block** (Square + Cash App shared Ledgering core), **Chime** (ChimeCore) | `[confirmed]` |

## Issuer-processor

| Vendor | Named users | Confidence |
| --- | --- | --- |
| **Galileo** (SoFi) | **Chime**, **SoFi**, **Robinhood**, **Varo**, KOHO — plus the **US-based business of Monzo, Revolut, Wise (TransferWise)** and Paysafe | `[reported]` — note the "US business of" qualifier; it does not mean Monzo's or Revolut's home market |
| **Marqeta** | **Block / Cash App** — its largest customer at **41% of revenue in Q2 2026**, down from 46% a year earlier; also Klarna, Affirm, Branch | `[reported]`. Block is **winding down**: Marqeta will issue "little to no" new Cash App cards by end of year |
| **Thredd** (formerly GPS) | **Curve** (since founding in 2016, now 4m+ customers), **Zilch**, **Revolut**, **Starling Bank**. 100+ customers across 44–50 countries | `[reported]` |
| **GPS → in-house (Monzo)** | **Monzo** used GPS for its *prepaid* card from 2016; built its **own processor** for the current account with no third-party issuing bank, and wound the prepaid product down in 2017–18 | `[confirmed]` |
| **Lithic** | No neobank publicly named. >$1bn/month processed | `[reported]` |
| **Highnote**, **i2c**, **Stripe Issuing**, **Wallester**, **Monavate** | No neobank publicly named | — |

The Galileo row is the single most useful fact on this page: **Galileo simultaneously powers
Chime, Robinhood, Varo and SoFi's own bank** — and SoFi owns it. Chime's move to ChimeCore is
exactly what that conflict predicts.

## Payment rails access

| Vendor | Named users | Confidence |
| --- | --- | --- |
| *Direct participation (no vendor)* | **Monzo** — in-house Faster Payments gateway live 2 Nov 2020; **Bacs direct participant** since 12 Sept 2022, settling against its own Bank of England account. **Starling**, **Revolut** and other licensed UK banks are also direct participants | `[confirmed]` for Monzo |
| **ClearBank** (UK) | **Tide**, Chip, Coinbase, OakNorth. **200+ customers**, 13m accounts, ~$4bn assets. First new UK clearing bank in 250+ years | `[reported]` |
| **Form3** | Banks and regulated PSPs; no neobank publicly named | — |
| **Modulr** | UK/EU-licensed EMI, embedded payments; no neobank publicly named | — |
| **LHV**, **Banking Circle** | Agency access; no neobank publicly named | — |
| **Icon Solutions IPF**, **Volante** | Bank-scale message infrastructure | — |
| **Column**, **Increase**, **Moov**, **Dwolla** (US) | No neobank publicly named | — |

## US sponsor banks

| Bank | Named fintech partners | Confidence |
| --- | --- | --- |
| **The Bancorp Bank, N.A.** | **Chime** | `[confirmed]` — Chime states it |
| **Stride Bank, N.A.** | **Chime** | `[confirmed]` |
| **Sutton Bank** | **Monzo (US)** — holds deposits and provides FDIC insurance for Monzo's US accounts; publishes the Monzo cardholder agreement on its own site | `[confirmed]` |
| **Cross River Bank** | X Money, Best Egg (since 2013); strategic processing partnership with **Thredd** to route international fintechs into the US | `[reported]` |
| **Evolve Bank & Trust** | Federal Reserve cease-and-desist, May 2025, for failure to oversee fintech partners | `[reported]` |
| **Column**, **Lead Bank** | No neobank publicly named in this sweep | — |

Chime running **two** sponsor banks is itself an architectural fact — it implies a reconciliation
obligation across both, which is precisely what the FDIC's proposed rule targets. See
[Deep dive — Reconciliation (build)](../deep-dives/01-reconciliation.md).

## Identity and onboarding

| Vendor | Named users | Confidence |
| --- | --- | --- |
| **Onfido** (now Entrust IDV) | **Monzo** and **Revolut**. Revolut case study: check volume **+293%**, checks completed **38 seconds faster** than the previous provider. Financial services ≈50% of Onfido revenue, led by tier-1 banks and neobanks | `[reported]` — vendor case study |
| **Alloy** | Orchestration across **270+ data sources**; no neobank publicly named | `[reported]` |
| **Jumio**, **Persona**, **Socure**, **Sumsub**, **Veriff**, **Trulioo** | No neobank publicly named | — |

This is the thinnest attribution layer in the whole map, and predictably so: naming your IDV
vendor tells fraudsters which liveness check to defeat.

## Financial crime — fraud, AML, screening

| Vendor | Named users | Confidence |
| --- | --- | --- |
| **Featurespace** (ARIC Risk Hub) | **NatWest** (enterprise-wide; **scam detection +135%**, false positives down within 24 hours of deployment), **HSBC**, **Danske Bank**, **Permanent TSB**, **ClearBank**, **Marqeta**, TSYS, Worldpay, Contis, Akbank, Edenred. **70+ direct customers**, 200,000 institutions reached | `[reported]` — vendor newsroom, but named and specific |
| **Unit21** | **Chime**, **Brex**, PrimeTrust, Yotta, Airbase (founding members of its Fintech Fraud DAO); plus Gusto, Intuit, Flywire, Piermont Bank, Crypto.com, Wealthsimple. Holds data from 100+ fintechs | `[reported]` |
| **Sardine** | SardineX consortium founding members: Novo, Blockchain.com, Airbase, Chesapeake Bank, Visa, Alloy Labs Alliance, iLex | `[reported]` |
| **ComplyAdvantage** | 1,000–3,000+ institutions claimed; **no neobank publicly named**. Monzo has appeared in a ComplyAdvantage-hosted panel discussion — that is **not** evidence of a customer relationship and should not be recorded as one | `[inferred]` — deliberately not asserted |
| **Feedzai**, **NICE Actimize**, **Hawk AI**, **Flagright**, **Salv** | No neobank publicly named | — |
| *In-house* | **Monzo** (Starlark control platform), **Stripe** (Radar), **Revolut** | `[confirmed]` |

**A necessary caveat on "in-house".** The FCA fined **Monzo £21m in 2025** for failing to design,
implement and maintain adequate customer onboarding, customer risk assessment and transaction
monitoring systems `[confirmed]`. Building your own fincrime platform is not the same as building
an adequate one, and the most sophisticated public architecture in this research belongs to a
bank that was penalised for control failings. Both facts are true; a vendor map that showed only
the first would be misleading.

## Credit and data

| Vendor | Named users / relationships | Confidence |
| --- | --- | --- |
| **Experian, Equifax, TransUnion** | Universal in both markets. Experian launched Credit + Cashflow Score Nov 2025 | `[reported]` |
| **FICO** | Cash-flow UltraFICO built **with Plaid**, Nov 2025 | `[confirmed]` |
| **Plaid** | FICO partnership; largest US consumer-permissioned bank data network | `[confirmed]` / `[reported]` |
| **Nova Credit** | **PayPal** selected its Cash Atlas platform, Sept 2025 | `[reported]` |
| **Ocrolus, MeridianLink, eNoah** | Cash-flow and document data | `[reported]` |

## Infrastructure and data platform

| Technology | Named users | Confidence |
| --- | --- | --- |
| **AWS** | **Monzo** (primary), **Starling** (primary), **Remitly** | `[confirmed]` / `[reported]` |
| **GCP** | **Revolut** (primary), **Monzo** (analytics and training) | `[reported]` |
| **BigQuery** | **Monzo** — fraud control-execution metadata and decision logs; **Starling** | `[confirmed]` / `[reported]` |
| **Snowflake** | **Chime** (migrated large-file processing of Galileo RDF files from MySQL), **Remitly** | `[reported]` |
| **Cassandra** | **Monzo** — ledger and 150+ services | `[confirmed]` |
| **PostgreSQL** | **Revolut** (single event store), **Starling**, **Remitly** | `[reported]` |
| **Amazon Aurora** | **Remitly** (migrated from RDS MySQL) | `[reported]` |
| **Apache Kafka** | **Remitly**, **Uber** (settlement pipeline) | `[reported]` / `[confirmed]` |

## What this map cannot tell you

Four honest limits:

1. **Absence of a name is not absence of a customer.** Most banks contractually avoid being
   named, especially in fincrime and identity.
2. **Vendor customer lists go stale and rarely announce departures.** Chime still appears on
   Galileo material; it has been moving to ChimeCore since 2024. Marqeta's Block relationship is
   winding down. Assume every logo is at least a year behind.
3. **"Uses vendor X" hides the scope.** Galileo powering "the US business of Monzo" is a very
   different claim from Galileo powering Monzo. Scope qualifiers matter more than logos.
4. **Nobody publishes what they pay.** Every cost question in the research backlog (`open-questions.md`) remains open.

## Open questions

- Which fincrime vendor, if any, does Monzo run alongside its in-house platform post-fine?
- Who processes Chime's **debit** volume in 2026 — Galileo, ChimeCore, or split?
- Does Revolut use Thredd in its home market or only for specific programmes?
- Which IDV vendors do Chime, Starling and Zopa use? Nothing public found.
- What replaced Cash App's Marqeta programme?

## Sources

- Galileo clients in the news — https://www.galileo-ft.com/news/galileo-clients-in-the-news/
- Forbes, the company powering Robinhood and Chime — https://www.forbes.com/sites/donnafuscaldo/2019/10/17/galileo-financial-raises-77-million-as-it-fuels-some-of-the-worlds-biggest-fintechs/
- Payments Dive, Marqeta flags Cash App hit — https://www.paymentsdive.com/news/marqeta-flags-cash-app-hit/813350/
- eMarketer, Marqeta will issue little to no new Cash App cards — https://www.emarketer.com/content/marqeta-will-issue--little-no--new-cash-app-cards-by-year-end
- Businesswire, GPS rebrands as Thredd — https://www.businesswire.com/news/home/20230427005429/en/GPS-Rebrands-as-Thredd-to-Reflect-Its-Unique-Position-as-the-Go-to-Payments-Partner-of-Innovators-Worldwide
- Cross River and Thredd partnership — https://www.crossriver.com/newsroom/thredd-and-cross-river-to-accelerate-expansion-into-the-us-market-for-global-fintechs
- CB Insights, ClearBank and competitors — https://www.cbinsights.com/research/clearbank-competitors-banking-circle-mmob-weavr-modulr-form3/
- Onfido, onboarding for digital banks — https://onfido.com/industries/financial-services/digital-banking/
- Featurespace, NatWest deploys ARIC — https://www.featurespace.com/newsroom/natwest-deploys-aric-for-transaction-monitoring-and-payments-fraud-detection
- Featurespace, NatWest improves scam detection by 135% — https://www.featurespace.com/newsroom/natwest-improves-scam-detection-rate-by-135-using-featurespaces-technology
- Featurespace, Danske Bank — https://www.featurespace.com/newsroom/danske-bank-boosts-fraud-prevention-with-featurespace-aric-risk-hub
- Businesswire, Unit21 Fintech Fraud DAO with Brex, Chime, PrimeTrust — https://www.businesswire.com/news/home/20221014005500/en/Unit21-Launches-Fintech-Fraud-DAO-to-Combat-Financial-Crime-With-Brex-Chime-and-PrimeTrust-as-Early-Customers
- Mambu customers — https://mambu.com/en/customers
- FCA, final notice to Monzo Bank Limited — https://www.fca.org.uk/publication/final-notices/monzo-bank-limited.pdf
