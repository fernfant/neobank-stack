---
title: Starling Bank and Engine by Starling (UK)
type: bank
status: living
updated: 2026-08-18
sources: 5
tags: [uk, java, engine, saas-core]
---

## Summary

A UK licensed bank that turned its own core into a product. Java microservices on AWS, built
famously fast (a working bank in about a year), now sold to other banks as **Engine by
Starling** — which makes Starling simultaneously an Archetype A bank and a core-banking
vendor competing with Thought Machine and 10x.

## Stack

| Layer | Choice | Confidence |
| --- | --- | --- |
| Licence | UK bank | `[confirmed]` |
| Language | Java (a "Java house"), deployed with embedded web server in Docker | `[reported]` |
| Runtime | Kubernetes | `[reported]` |
| Datastore | Postgres, Elasticsearch | `[reported]` `[dated: 2018]` |
| Cloud | AWS primary, some GCP | `[reported]` |
| Analytics | BigQuery | `[reported]` |
| Mobile | Java/Android, Swift/iOS | `[reported]` |

Early architecture was roughly 20 Java microservices (March 2018) `[reported]` `[dated: 2018]`
— an instructive contrast with Monzo's four-figure count at similar scale. Two licensed UK
banks, opposite granularity philosophies, both working.

## Engine

Engine is the complete, cloud-native SaaS banking platform derived from Starling's own
systems: onboarding and origination, core, payment processing, and customer service
`[confirmed]`. Architecture is AWS (some GCP), microservices, RESTful APIs, Java backend
`[reported]`. Starling is pushing Engine into the US market `[reported]`.

Strategic point worth noting for any build-vs-buy analysis: Engine's pitch is that it is
*proven by operating a real bank*, which is a different claim from Vault's or 10x's
(engineered as a platform from the start). Whether "battle-tested on one bank" beats
"designed multi-tenant" is a genuine open question.

## Open questions

- Current Engine client list and go-live count.
- Does Engine share a codebase with Starling Bank, or has it forked?
- What is Starling's current microservice count and datastore layout?

## Sources

- Engine by Starling, platform overview — https://enginebystarling.com/platform/
- Engine by Starling, AWS re:Invent — https://enginebystarling.com/events/aws-reinvent/
- Container Solutions, Starling: How to Build a Bank in a Year — https://blog.container-solutions.com/starling-how-to-build-a-bank-in-a-year
- Diginomica, Starling and open source Kubernetes — https://diginomica.com/starling-bank-cashes-in-on-open-source-flexibility-and-agility
- AntStack notes, PwC/AWS/Engine re:Invent session — https://www.antstack.com/talks/reinvent24/pwc-aws-and-engine-by-starling-a-digital-transformation-in-banking-cop216/
