---
title: SoFi (USA) — and Galileo / Technisys
type: bank
status: living
updated: 2026-08-18
sources: 5
tags: [usa, galileo, technisys, cyberbank, vertical-integration, vendor]
---

## Summary

The full vertical stack, assembled by acquisition. SoFi holds a US national bank charter, owns
its issuer-processor (**Galileo**, 2020) and its core banking platform (**Technisys /
Cyberbank Core**, 2022), and sells both to other fintechs and banks — including competitors.
It is simultaneously Archetype A, a core-banking vendor, and a sponsor bank.

## Stack

| Layer | Choice | Confidence |
| --- | --- | --- |
| Licence | US national bank charter (SoFi Bank, N.A.) | `[confirmed]` |
| Issuer-processor | **Galileo** (SoFi subsidiary), Visa-certified | `[confirmed]` |
| Core banking | **Galileo Cyberbank Core** (ex-Technisys) — cloud-based, real-time | `[confirmed]` |
| Digital experience | Cyberbank Digital | `[reported]` |
| Scope of Cyberbank adoption | Adopted for commercial payment services and its sponsor-banking programme: debit, prepaid, ACH, wire | `[confirmed]` |

Technisys is a cloud-native multi-product core letting institutions design, configure and
manage products across deposits, lending and digital banking `[reported]`. Together the
acquisitions gave SoFi ownership of the payments layer, the core ledger and the digital
experience engine — the same stack now serving dozens of fintechs and financial institutions
`[reported]`.

## Above the core — the parts SoFi actually writes about

SoFi's own engineering blog is mostly people and leadership Q&As; the architecture detail lives in
partner material `[reported]`:

| Layer | Choice |
| --- | --- |
| Backend | **Kotlin + Spring Boot** microservices |
| API | **GraphQL** BFF (backends-for-frontends) layer |
| Mobile | **Flutter** — one codebase replacing native iOS and Android |
| Data | **Snowflake data mesh** across lines of business; Hightouch and Braze for activation; Snowflake data sharing with partners |

**The Flutter bet is the notable one.** SoFi runs one of the largest production Flutter codebases
anywhere: roughly **1m lines in the first two years** after the rewrite, **another 1m the
following year**, and **500k in a recent quarter** — acceleration attributed to AI-assisted
scaffolding and test generation. Architecture emphasis is on modularisation, moving from global
service locators to dependency injection (Riverpod), and an enforced design system, with a senior
platform team whose stated goal is making it "easy to do things the right way and hard to do
things the wrong way". Weekly release cadence.

The motivation given is directly relevant to any multi-product neobank: the Director of Mobile
Engineering came from Uber, where maintaining separate iOS and Android codebases required
"enormous coordination" just to hold feature parity. For a super-app with lending, banking,
invest and crypto in one shell, that coordination cost compounds per product.

Data side: a **Snowflake data mesh** supporting the product suite across **8.1m members**, with
governance and partner data sharing as stated goals — the same mesh pattern Monzo describes, at a
company with far more product lines and correspondingly more domains.

## Why this shape

Galileo is the processor behind a long roster of neobanks — Chime historically, plus Robinhood,
Varo and others `[reported]`. Owning it means SoFi earns from competitors' volume while
insourcing its own. The Cyberbank acquisition then closed the remaining gap: SoFi no longer
rents a core.

The structural tension worth tracking: **Galileo's customers are SoFi's competitors.** Chime's
move to ChimeCore is exactly what that tension predicts. Any neobank evaluating Galileo should
price in the strategic risk, not just the technical fit.

## Open questions

- Has SoFi migrated its *own* retail deposits onto Cyberbank Core, or is that still the older
  stack with Cyberbank serving the commercial/sponsor programme?
- What is Galileo's customer retention since Chime's insourcing?
- What are Cyberbank Core's actual scale characteristics? No credible independent numbers found.

## Sources

- Galileo, SoFi to adopt Cyberbank Core — https://www.galileo-ft.com/news/sofi-to-adopt-galileos-cyberbank-core-for-commercial-payment-services-and-sponsor-banking/
- SoFi press release — https://www.sofi.com/press/sofi-technologies-adopt-galileos-cyberbank-core-new-commercial-payment-services-sponsor-banking-program/
- WhiteSight, SoFi's technology platform: the Galileo–Technisys stack unpacked — https://whitesight.net/sofis-technology-platform-the-galileo-technisys-stack-unpacked/
- PYMNTS, SoFi adopts Galileo's Cyberbank Core — https://www.pymnts.com/news/digital-banking/2024/sofi-adopts-galileos-cyberbank-core-for-improved-commercial-payments/
- Very Good Ventures, How SoFi scales mobile engineering with Flutter and AI — https://verygood.ventures/blog/how-sofi-scales-mobile-engineering-with-flutter-and-ai/
- Very Good Ventures, Enterprise-scale Flutter architecture at SoFi — https://www.verygood.ventures/podcasts/phil-rabin-sofi--enterprise-scale-flutter-modernizing-architecture-for-a-2-million-line-flutter-codebase
- Snowflake, a technical deep dive of SoFi's data mesh strategy — https://www.snowflake.com/webinars/customer-webinars/show-me-your-architecture-a-technical-deep-dive-of-sofis-snowflake-data-mesh-strategy-to-support-its-wide-suite-of-products-2024-05-28/
- SoFiety blog — https://sofietyblog.sofi.com
- DashDevs, Galileo platform guide — https://dashdevs.com/blog/galileo-financial-technologies-migration-guide/
