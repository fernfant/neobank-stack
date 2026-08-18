# Neobank Tech Stack Research

**Live:** https://fernfant.github.io/neobank-stack/ · **Repo:** https://github.com/fernfant/neobank-stack

A living knowledge base on how UK and USA neobanks are actually built — the ledger, the
payment rails, the card stack, the financial-crime stack, credit decisioning, data/ML, and
the infrastructure underneath — plus a reusable **architecture diagram template** and a
**key-questions bank** for designing or due-diligencing one.

## Start here

| If you want… | Read |
| --- | --- |
| The thesis in one page | [wiki/overview.md](wiki/overview.md) |
| The layer-by-layer map | [wiki/layers/00-layer-map.md](wiki/layers/00-layer-map.md) |
| A specific neobank | [wiki/banks/](wiki/banks/) |
| Who the vendors are | [wiki/vendors/vendor-landscape.md](wiki/vendors/vendor-landscape.md) |
| UK vs USA differences | [wiki/comparisons/uk-vs-usa.md](wiki/comparisons/uk-vs-usa.md) |
| To draw your own architecture | [templates/architecture-diagram-template.md](templates/architecture-diagram-template.md) |
| Questions to ask in a design review | [templates/key-questions.md](templates/key-questions.md) |
| The reference diagram | [diagrams/reference-architecture.mmd](diagrams/reference-architecture.mmd) |
| A 9-minute brief instead of all this | [summary/summary-with-diagram.html](https://claude.ai/code/artifact/10168ec5-9832-4b67-b785-9de2c91ff0a2) |

## How it stays current

Four skills and two scheduled jobs:

- **`neobank-scout`** — daily. Searches for new public information across a fixed watchlist
  of companies, vendors, and regulators; ingests what is material; proposes new questions.
- **`neobank-ingest`** — on demand. Files one source into the wiki properly.
- **`neobank-architect`** — regenerates the architecture diagrams from the wiki.
- **`neobank-lint`** — weekly. Contradictions, stale claims, orphans, gaps.

Run one manually:

```bash
claude -p "/neobank-scout"
```

The schema the agent follows lives in [CLAUDE.md](CLAUDE.md).

## Scope

**UK:** Monzo, Starling (and Engine), Revolut, Zopa, Chase UK, Kroo, Atom, Tide.
**USA:** Chime, SoFi (and Galileo), Varo, Current, Dave, Cash App/Block, Mercury, Remitly.

Remitly sits slightly outside "neobank" — it is a cross-border remittance company — but its
payout-network and FX architecture is the best public example of the money-movement layer,
so it is in scope.
