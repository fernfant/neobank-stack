---
title: Vendor evaluation scorecard
type: template
status: living
updated: 2026-08-18
---

# Vendor evaluation scorecard

One page per vendor per layer. Score 1–5; weight per your context. The weights below are a
starting point for a licensed challenger; a pre-launch fintech should raise *Speed to live*
and lower *Exit cost*.

| Criterion | Weight | Score | Evidence |
| --- | --- | --- | --- |
| **Fit to requirement** — does it do the actual job, not the demo | 3 | | |
| **Hot-path performance** — measured p99/p99.9, not marketed | 3 | | |
| **Data egress** — can we stream raw records out continuously, in our format | 3 | | |
| **Exit cost** — DORA Art. 30 exit plan; has anyone executed it | 3 | | |
| **Regulatory standing** — who is the regulated entity; consent-order history | 3 | | |
| **Incident history** — public postmortems, status page, SLA with teeth | 2 | | |
| **Speed to live** — realistic, with references, not the sales number | 2 | | |
| **Cost at 10× volume** — where the fee curve goes, not today's price | 2 | | |
| **Roadmap control** — can we ship a product change without their release | 2 | | |
| **Competitive conflict** — is the vendor or its parent a competitor | 2 | | |
| **Support model** — named engineers or a ticket queue | 1 | | |
| **Ecosystem** — integrations we would otherwise build | 1 | | |

## Mandatory reference checks

- Two customers **at our scale or larger**, in our market.
- One customer who **left** them. (Ask the vendor for it. The reaction is the datapoint.)
- Their status page history for the last 12 months, read personally.

## Automatic disqualifiers

- Cannot or will not give us continuous raw data egress.
- No contractual exit and transition provisions for a critical function.
- Unable to state who the regulated entity is in the arrangement.
- Refuses to share measured latency distributions under NDA.
