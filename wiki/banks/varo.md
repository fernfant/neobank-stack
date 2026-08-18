---
title: Varo Bank (USA)
type: bank
status: living
updated: 2026-08-18
sources: 3
tags: [usa, charter, temenos, bought-core]
---

## Summary

The first US consumer fintech granted a national bank charter, and the clearest US example of
Archetype B: own charter, bought core. Varo went live on **Temenos Transact** hosted in the
cloud.

## Stack

| Layer | Choice | Confidence |
| --- | --- | --- |
| Licence | OCC national bank charter — first consumer fintech to get one | `[confirmed]` |
| Core banking | **Temenos Transact**, cloud-hosted | `[confirmed]` |
| Processor | Galileo appears on Galileo's client roster | `[reported]` |

Temenos' pitch for the deployment is continuous feature deployment on a cloud-native platform
`[reported]` — vendor framing.

## Why it's the useful counterexample

Varo took the hardest regulatory path (a charter) and the easiest technology path (a bought,
established core). Chime took the opposite pair: no charter, custom technology. Both are
coherent; they optimise different things. Varo bought regulatory independence and rents
technology; Chime bought technological independence and rents regulation.

If you are choosing, the question is which dependency you can least afford: a sponsor bank
that can be ordered to exit BaaS, or a core vendor whose release train gates your roadmap.

## Open questions

- Is Varo still on Temenos in 2026, or has it moved? The public record thins out after the
  2020 go-live and 2026 mentions are not specific `[dated: 2020]`.
- Did the charter deliver the expected funding-cost advantage in practice?
- What does Varo run above the core — in-house or vendor fincrime and decisioning?

## Sources

- Temenos, Varo goes live with Temenos cloud technology — https://www.temenos.com/press_release/varo-first-consumer-fintech-granted-national-bank-charter-in-the-us-goes-live-with-temenos-cloud-technology/
- Finextra, Varo goes live on Temenos core platform — https://www.finextra.com/pressarticle/83870/varo-goes-live-on-temenos-core-platform
- IBS Intelligence, Varo integrates Temenos cloud — https://ibsintelligence.com/ibsi-news/varo-mobile-centric-national-bank-charter-in-the-u-s-integrates-temenos-cloud-technology/
