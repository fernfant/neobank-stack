# Neobank Tech Stack Wiki — schema and working rules

This directory is an **LLM-maintained knowledge base** on the technology stacks of UK and
USA neobanks. A human curates sources and asks questions. The agent writes and maintains
every page here.

## Layers

1. **`raw/`** — immutable source material. Clipped articles, PDFs, engineering-blog dumps,
   job-ad snapshots, S-1 extracts. **Never edit a file in `raw/`.** Read from it only.
2. **`wiki/`** — the agent-owned synthesis. Layer pages, bank profiles, vendor pages,
   comparisons. This is where knowledge accumulates.
3. **`templates/`, `diagrams/`** — reusable artefacts derived from the wiki.
4. **`index.md`, `log.md`, `open-questions.md`** — navigation and bookkeeping.

## Directory map

```
neobank-stack/
├── CLAUDE.md              this file — the schema
├── index.md               content catalogue; read this FIRST on any query
├── log.md                 append-only chronological record
├── open-questions.md      the research backlog; the daily scout works from this
├── raw/                   immutable sources (one file per source)
├── wiki/
│   ├── overview.md        the thesis: how a neobank stack is put together in 2026
│   ├── layers/            one page per architectural layer (00-10)
│   ├── banks/             one page per neobank
│   ├── vendors/           vendor landscape + per-vendor pages as they earn one
│   └── comparisons/       cross-cutting analyses (UK vs USA, build vs buy, …)
├── templates/             architecture-diagram template, key questions, scorecards
├── diagrams/              .mmd Mermaid sources, rendered outputs
├── jobs/                  runbooks for the scheduled jobs
└── scripts/               shell entrypoints for those jobs
```

## Page conventions

Every wiki page starts with YAML frontmatter:

```yaml
---
title: Core ledger
type: layer            # layer | bank | vendor | comparison | overview
status: living         # living | stable | stale
updated: 2026-08-18
sources: 7             # count of distinct sources feeding this page
tags: [ledger, core-banking, uk, usa]
---
```

Then: a one-paragraph **Summary**, the body, and a **Sources** list at the bottom with
full URLs.

### Linking

Use `[[wiki-link]]` style with the page's path stem, e.g. `[[layers/02-core-ledger]]`,
`[[banks/monzo]]`. Link liberally. A link to a page that does not exist yet is a to-do,
not an error — add it to `open-questions.md` as a "page wanted" item.

### Confidence tags

Financial-infrastructure reporting is full of vendor marketing and stale blog posts. Tag
every non-obvious claim:

- **`[confirmed]`** — stated by the company itself (engineering blog, S-1, press release,
  conference talk) or by a regulator.
- **`[reported]`** — credible third party (InfoQ, American Banker, The Register, Finextra),
  not denied by the company.
- **`[inferred]`** — deduced from job ads, vendor customer lists, StackShare, or reasoning.
  Say what the inference rests on.
- **`[dated: YYYY]`** — attach to any claim whose source is older than ~18 months. Stacks
  move. A 2020 claim about a 2026 stack is a hypothesis.

Never launder an `[inferred]` claim into a `[confirmed]` one when rewriting a page.

## Workflows

### Ingest a source

Invoke the **`neobank-ingest`** skill. In short: read the source → drop a copy in `raw/`
→ extract claims with confidence tags → update every layer/bank/vendor page it touches
(a good source touches 5-15 pages) → update `index.md` → append to `log.md` → add any new
questions it raises to `open-questions.md`.

### Answer a question

Read `index.md` first, then the relevant pages, then answer with citations. If the answer
is durable and non-obvious, **file it back into the wiki** as a new page or a new section —
that is the whole point. Log it.

### Daily scout

Invoke the **`neobank-scout`** skill (also wired to a scheduled job — see `jobs/`). It
searches for new public information, ingests what is material, generates new questions,
and refreshes the architecture diagram if the landscape moved.

### Maintain

Invoke the **`neobank-lint`** skill weekly. It hunts contradictions, stale claims, orphan
pages, missing cross-references, and gaps worth a web search.

### Redraw the architecture

Invoke the **`neobank-architect`** skill. It regenerates `diagrams/*.mmd` from the current
state of the wiki and re-publishes the artifact.

## House rules

- **Cite or don't claim.** Every factual statement traces to a source in the page's
  Sources list.
- **Vendor names are not architecture.** A page that lists twelve vendors and no
  trade-offs has failed. Always say *what decision the choice forces* downstream.
- **Prefer primary sources**: engineering blogs, S-1/annual reports, regulator
  publications, conference talks, job ads. Vendor "top 10" listicles are weak evidence and
  should be tagged `[reported]` at best — many are SEO content marketing.
- **Distinguish the two questions**: "what does company X run?" and "what should we run?"
  Bank profiles answer the first. Layer pages answer the second.
- **UK ≠ USA.** Rails, licensing, credit data, and fraud liability differ sharply. Any
  layer page must handle both or say explicitly that it only covers one.
- Keep diffs small and focused. Do not restructure the wiki without being asked.
