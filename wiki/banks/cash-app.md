---
title: Cash App / Block (USA)
type: bank
status: living
updated: 2026-08-18
sources: 3
tags: [usa, block, ledger, agentic-ai]
---

## Summary

Block runs a dedicated **Ledgering** team maintaining the accounting core that holds
authoritative balances for both Square and Cash App, plus the transaction and settlement
machinery that moves the money `[confirmed]`. That single fact — a shared ledger platform
serving two very different products — is the most useful thing in the public record.

## Stack

| Layer | Choice | Confidence |
| --- | --- | --- |
| Ledger | In-house accounting core, shared across Square and Cash App, owned by a dedicated Ledgering team | `[confirmed]` |
| Licence | Block holds various licences; Cash App banking services via partner banks | `[reported]` |
| Consumer AI | **Money Bot** — GA early 2026, ~1m active users in a week; surfaces patterns such as forgotten recurring charges | `[reported]` |
| AI strategy | Agentic AI embedded in both internal engineering and products | `[reported]` |

## The shared-ledger question

A ledger that serves a merchant-acquiring business (Square) and a consumer wallet (Cash App)
must model both merchant settlement and peer-to-peer balances in one account hierarchy. That
is a strong argument for hierarchical account paths and a generic posting model over
product-specific ledgers — the design principle in [Core ledger and product engine](../layers/02-core-ledger.md).

## Caution on sources

Public material about Cash App's internals is thin and polluted by scam/SEO content. A claim
circulating in 2026 that Cash App runs "a hybrid digital ledger combining instant settlement
with blockchain-backed verification" appears only in low-quality sources and should be treated
as **unverified** — do not propagate it without a Block engineering-blog or filing citation.

## Open questions

- What technology is the Ledgering core built on?
- How does Cash App's balance relate to partner-bank FBO accounts, and at what reconciliation
  cadence?
- Is Money Bot read-only, or can it initiate money movement? (Determines whether it needs the
  evidence plane in [Resilience, regulatory reporting and operations](../layers/10-resilience-regulatory.md).)

## Sources

- Block careers, Senior Software Engineer, Ledgering — https://block.xyz/careers/jobs/5281196008
- Block, Cash App — https://block.xyz/news/cashapp
- Perspective AI, Block's AI strategy 2026 — https://getperspective.ai/blog/block-square-ai-customer-research-seller-ecosystem-2026
