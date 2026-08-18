---
title: Zopa Bank (UK)
type: bank
status: living
updated: 2026-08-18
sources: 4
tags: [uk, thought-machine, vault, bought-core]
---

## Summary

The clearest recent UK example of Archetype B: own banking licence, **bought core**. Zopa
selected Thought Machine's Vault Core to power its move from lending into everyday banking
with its current account, "Biscuit".

## The datapoint that matters

Using Vault Core, Zopa launched a **beta current account in September 2024** and the **full
product in June 2025** `[confirmed]`. Thought Machine's framing is significant time-to-market
reduction `[confirmed]` — vendor-sourced, so treat the causal claim as `[reported]`, but the
dates are checkable.

For a build-vs-buy argument, this is the single most useful public comparison point against
Monzo's multi-year in-house core build.

## Stack

| Layer | Choice | Confidence |
| --- | --- | --- |
| Licence | UK bank | `[confirmed]` |
| Core ledger / product engine | Thought Machine Vault Core | `[confirmed]` |
| Product definition | Vault **Smart Contracts** (proprietary Python-flavoured DSL) | `[reported]` |
| Everything above the core | In-house | `[inferred]` — from the fact that only the core was announced |

Vault Core is cloud-native and event-driven, with a Universal Product Engine and real-time
event streaming `[reported]`. Other Vault users include Lloyds, Standard Chartered, Intesa
Sanpaolo, Atom bank, C6 and Trust Bank `[reported]`.

## The lock-in axis to watch

Vault expresses financial products as Smart Contracts in a proprietary language `[reported]`.
That is genuine leverage — a product change is a contract change, not a release — and genuine
lock-in. 10x's competing pitch is a polyglot runtime with no contract-language lock-in and
built-in migration tooling `[reported]`; that is a vendor's framing of its rival's weakness,
so verify it rather than repeat it.

## Open questions

- What did Zopa keep in-house — payments orchestration, fincrime, decisioning?
- Is the legacy lending book on Vault, or running alongside on the old stack?
- What does the Vault integration look like on the data side: does Zopa stream postings out
  to its own warehouse?

## Sources

- Thought Machine × Zopa press release — https://www.thoughtmachine.net/press-releases/zopa-bank
- The Fintech Times, Zopa selects Thought Machine — https://thefintechtimes.com/zopa-selects-thought-machine-to-power-step-into-everyday-banking/
- The Paypers, Thought Machine supports Zopa to launch Biscuit — https://thepaypers.com/fintech/news/thought-machine-supports-zopa-bank-to-launch-biscuit
- 10x Banking, core banking platforms compared — https://www.10xbanking.com/core-banking-platforms-compared
