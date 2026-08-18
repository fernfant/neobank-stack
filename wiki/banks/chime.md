---
title: Chime (USA)
type: bank
status: living
updated: 2026-08-18
sources: 6
tags: [usa, chimecore, sponsor-bank, vertical-integration]
---

## Summary

The most important US datapoint in this research. Chime is **not a bank** — it says so
explicitly in its S-1 — yet it built its own payments processor (**ChimeCore**) and made
vertical integration the centrepiece of its public equity story. It is the proof that you can
own the technology without owning the charter.

## Stack

| Layer | Choice | Confidence |
| --- | --- | --- |
| Licence | None. Partners with **The Bancorp Bank, N.A.** and **Stride Bank, N.A.** | `[confirmed]` |
| Processor (historic) | Galileo | `[reported]` |
| Processor (current) | **ChimeCore** — proprietary; processes a portion of transactions and handles certain bookkeeping; **100% of credit-card transactions since late 2024** | `[confirmed]` |
| Data storage | MySQL and Snowflake | `[reported]` |
| Data pipeline | Migrated large-file processing (Galileo RDF files) from MySQL to Snowflake | `[reported]` |
| Core datastore | **CoreDB** — a MySQL cluster on AWS RDS. 5 instances (2× db.r5.8xlarge, 3× db.r5.24xlarge), **40TB**, 10k+ connections on the writer, 30k across the cluster. "Powers core financial services for millions of members" | `[confirmed]` |
| Runtime | **AWS EKS**; ~**1,000 deployments a day**; GitOps via Argo CD + Helm; Terraform | `[confirmed]` |
| Cloud | **AWS** — egress well over **2PB**/month | `[confirmed]` |
| Internal tooling | **Atlas** (connection routing library), **Mani-Diffy** (Argo manifest renderer, open-sourced), **ha-nat** (HA NAT instances, open-sourced), **Monocle** (PR risk advisor) | `[confirmed]` |
| Mobile | React Native | `[confirmed]` |

## The ChimeCore argument

From the S-1: ChimeCore reduced software maintenance costs and made Chime less dependent on
third-party technology providers, and Chime planned further investment in it post-IPO
`[confirmed]`. Reporting attributes a **cost-to-serve roughly one third of a large bank's** to
the proprietary processor `[reported]`.

IPO context: filed 2025, listed on NASDAQ as CHYM on 13 June 2025 at $27, ~$770m net proceeds,
seeking ~$11.2bn valuation `[reported]`; FY revenue ~$1.67bn `[reported]`.

The strategic read: in a sponsor-bank model your gross margin is eaten by processor and BaaS
fees. Chime's answer was to insource the fee-bearing layer while leaving the regulated layer
with the banks. That is a genuinely distinct third path from "get a charter" and "stay a thin
fintech", and it is the one most likely to be copied.

## CoreDB — the closest thing to an answer on ChimeCore's substrate

Chime's April 2025 post on upgrading its core database is the most revealing thing it has
published `[confirmed]`. **CoreDB is a MySQL cluster on AWS RDS** holding **40TB** and serving
30k connections, described as powering "core financial services for millions of members".

The MySQL 5 → 8 upgrade is a masterclass in how to move a live financial datastore:

- **Three clusters, not two.** Blue (MySQL 5 production), Green (MySQL 8 replica), and
  **BluePrime** — a second MySQL 5 cluster kept as the fallback. Replication chained
  Blue → Green → BluePrime, so a rollback target survived the cutover.
- **Binary logging turned on** specifically for this (it had been off for performance).
- **10 days of production read traffic on Green** before any write cutover, with reads routed
  there only when replication lag was low — lag ran to hours under peak load.
- `pt-heartbeat` for real-time lag detection, surfaced through Chime's **Atlas** connection
  library.
- **Six months of preparation and five full upgrade/rollback rehearsals** in non-production.
- Cutover at 11pm PDT: reads to Green at 9pm → Blue read-only → wait for sync → Green writable →
  DNS endpoints updated → Blue connections killed to force reconnection. **Five minutes of
  member-facing downtime.**

Incidental findings that show the maturity of the estate: 14 tables had zero-date defaults that
AWS pre-upgrade checks caught, `temptable_max_mmap` needed raising to 50% of local storage, and
query cache was removed ahead of time to reduce risk.

**What this does and does not tell us.** It establishes that Chime's core financial data sits in
MySQL on RDS at 40TB — a conventional, well-understood substrate, not something exotic. It does
*not* establish whether CoreDB *is* ChimeCore's ledger or a separate operational store. That
distinction remains the P1 open question.

## Infrastructure and open source

- **EKS with ~1,000 deployments a day**, GitOps: Argo CD reconciles Helm charts from a central
  repo, using the App-of-Apps pattern; Terraform for infrastructure `[confirmed]`.
- **Mani-Diffy** — internally built, now open-sourced. Walks the Argo CD Application hierarchy,
  renders the Kubernetes manifests, and commits the rendered output back onto the pull request so
  reviewers see the *actual* manifests before merge. A genuinely good idea for anyone running
  App-of-Apps.
- **ha-nat** — open-sourced. Chime replaced managed NAT Gateways with self-managed NAT instances
  in Auto Scaling Groups across AZs, with Lambda health checks and route switching and a standby
  Gateway for failover. NAT Gateway's dual charge (per-GB processing *plus* egress) was its
  largest AWS line; at 2PB the modelled saving was ~**62.8%** — $147k/month down to ~$55k/month.
  Chime moves "considerably more than 2PB" `[confirmed]`.
- **Monocle** — a risk advisor that flags risky pull requests, part of a proactive security
  culture `[confirmed]`.

## The interesting unknown

**Does ChimeCore hold the deposit sub-ledger, or only card authorisation and bookkeeping?**
The public language ("a portion of user transactions", "certain bookkeeping tasks") is
deliberately imprecise. This matters enormously post-Synapse: if Chime maintains the
authoritative sub-ledger against Bancorp's and Stride's FBO accounts, then the FDIC's proposed
near-real-time reconciliation rule lands directly on ChimeCore. This is the highest-value open
question in the whole US section.

## Open questions

- ChimeCore's scope: ledger or processor? Is **CoreDB** ChimeCore's store or a separate one?
- ~~Runtime stack — orchestration, cloud~~ — **answered: AWS, EKS, Argo CD/Helm/Terraform,
  ~1,000 deploys/day** `[confirmed]`. Backend *language* still not public.
- How are the two sponsor banks split (product? geography? redundancy?), and how is
  reconciliation run across both?
- What proportion of debit (not credit) volume is on ChimeCore in 2026?

## Sources

- Banking Dive, Chime files for IPO — https://www.bankingdive.com/news/chime-files-for-ipo-sec-nasdaq-chym/748152/
- SiliconANGLE, Chime IPO and ChimeCore — https://siliconangle.com/2025/06/02/financial-technology-company-chime-seeking-11-2b-valuation-upcoming-ipo/
- Mostly Metrics, Chime IPO S-1 breakdown — https://www.mostlymetrics.com/p/chime-ipo-s1-breakdown
- Chime Careers, Redesigning Large File Processing — https://careers.chime.com/en/life-at-chime/engineering-at-chime/redesigning-large-file-processing-at-chime/
- App Economy Insights, how Chime makes money — https://www.appeconomyinsights.com/p/chime-how-they-make-money
- Chime, How We Upgraded Our Core Database with Just 5 Minutes of Downtime — https://careers.chime.com/life-at-chime/how-we-upgraded-our-core-database-with-just-5-minutes-of-downtime/
- Chime, How We Reduced Our AWS Bill by Seven Figures — https://careers.chime.com/life-at-chime/how-we-reduced-our-aws-bill-by-seven-figures/
- Chime, How We Preview Kubernetes Changes at Chime — https://careers.chime.com/life-at-chime/how-we-preview-kubernetes-changes-at-chime/
- Chime, Monocle: proactive security and engineering culture — https://careers.chime.com/life-at-chime/proactive-security-culture-at-chime-monocle-part-1/
- Chime newsroom, CTO appointment — https://www.chime.com/newsroom/news/jeff-currier-joins-chime-as-chief-technology-officer/
