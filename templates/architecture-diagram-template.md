---
title: Neobank architecture diagram — template
type: template
status: living
updated: 2026-08-18
---

# Neobank architecture diagram template

A fill-in-the-blanks Mermaid skeleton plus the conventions that make these diagrams
comparable across companies. Copy this file, replace every `‹PLACEHOLDER›`, delete what does
not apply, and file the result in `diagrams/`.

## Rules that make a diagram useful

1. **Bands, not clouds.** Lay the diagram out in horizontal bands matching the ten layers in
   `wiki/layers/00-layer-map.md`. Every box belongs to exactly one band. If you cannot place a
   box, you do not understand it yet.
2. **Label every box with `name / vendor-or-inhouse / confidence`.** `Ledger / in-house /
   [confirmed]`. A diagram without provenance is a wish list.
3. **Mark the regulated boundary.** Draw an explicit line showing which side holds the money.
   This is the single most informative element and almost every published diagram omits it.
4. **Show the two planes.** Reconciliation flows and evidence/decision-log flows get their own
   line style. They are usually invisible in architecture diagrams and are where the failures
   are.
5. **Annotate the hot path with its latency budget.** The card authorisation path is the only
   part with a hard deadline. Write the number on it.
6. **One diagram per question.** A single "everything" diagram is a poster, not a tool. Produce:
   a context diagram, a layered component diagram, and one sequence diagram per critical flow.

## Legend (use consistently)

| Element | Meaning |
| --- | --- |
| Solid box | In-house component |
| Dashed box | Third-party vendor |
| Double border | Regulated entity / system of record |
| Solid arrow `-->` | Synchronous request in the critical path |
| Dotted arrow `-.->` | Asynchronous event / stream |
| Thick arrow `==>` | Money movement |
| `~~~` or a distinct colour | Reconciliation or evidence flow |

---

## Diagram 1 — Context (who is who)

```mermaid
flowchart LR
    Customer([Customer])
    subgraph OURS["‹COMPANY› — the part we build"]
      App["Mobile & web apps"]
      Platform["Product + risk platform"]
    end
    subgraph REGULATED["Regulated money layer"]
      Bank[["‹OWN LICENCE or SPONSOR BANK›"]]
    end
    subgraph EXTERNAL["Schemes & networks"]
      Schemes["‹Visa/Mastercard›"]
      Rails["‹FPS/Bacs/CHAPS or ACH/RTP/FedNow›"]
    end
    Customer --> App --> Platform
    Platform ==> Bank
    Bank ==> Schemes
    Bank ==> Rails
```

Replace `‹OWN LICENCE or SPONSOR BANK›` honestly. If it is a sponsor bank, add a second box
for the **partner ledger** and a reconciliation arrow between it and yours — that relationship
is the thing regulators examine.

---

## Diagram 2 — Layered component view (the main one)

```mermaid
flowchart TB
    %% ============ 1. CHANNELS ============
    subgraph L1["① Channels"]
      direction LR
      IOS["iOS / ‹Swift›"]
      AND["Android / ‹Kotlin›"]
      WEB["Web / ‹React+TS›"]
      OPS["Ops & agent console"]
    end

    %% ============ 2. EDGE ============
    subgraph L2["② Edge / experience"]
      direction LR
      GW["API gateway / BFF"]
      AUTHN["AuthN / AuthZ / device binding"]
    end

    %% ============ 3. PRODUCT ============
    subgraph L3["③ Product services"]
      direction LR
      ACCT["Accounts & pots"]
      PAY["Payments orchestration"]
      CARD["Card management"]
      LEND["Lending & limits"]
      SUB["Subscriptions / pricing"]
    end

    %% ============ 4. DECISIONING ============
    subgraph L4["④ Decisioning — hot path ‹Xms budget›"]
      direction LR
      FEAT["Feature service<br/>JIT · near-RT · batch"]
      ENG["Control / rules engine<br/>‹Starlark-style pure functions›"]
      MODEL["Model serving"]
      POLICY["Policy layer<br/>hard cuts, affordability"]
    end

    %% ============ 5. CORE ============
    subgraph L5["⑤ Core — system of record"]
      LEDGER[["Ledger / ‹in-house | Vault | 10x | Temenos›<br/>double-entry · append-only · idempotent · bi-temporal"]]
      PRODENG["Product engine / interest & fees"]
    end

    %% ============ 6. MONEY MOVEMENT ============
    subgraph L6["⑥ Money movement — rail adapters"]
      direction LR
      FPS["‹FPS / ACH›"]
      BACS["‹Bacs / Same Day ACH›"]
      CHAPS["‹CHAPS / Wire›"]
      RTPX["‹RTP / FedNow›"]
      SCHEME["Card scheme iface / ‹issuer-processor›"]
      FX["FX & cross-border"]
    end

    %% ============ 7. EXTERNAL ============
    subgraph L7["⑦ External providers"]
      direction LR
      KYC[/"KYC — ‹Onfido | Persona | Socure›"/]
      SCREEN[/"Sanctions/PEP — ‹ComplyAdvantage›"/]
      TM[/"TM/fraud — ‹Unit21 | Feedzai | in-house›"/]
      BUREAU[/"Bureaus — ‹Experian | Equifax | TransUnion›"/]
      OB[/"Open banking / ‹Plaid›"/]
      PROC[/"Issuer-processor — ‹Marqeta | Galileo | Lithic›"/]
    end

    %% ============ 8. DATA ============
    subgraph L8["⑧ Data & ML platform"]
      direction LR
      BUS["Event bus / ‹Kafka›"]
      STREAM["Stream processing / ‹Flink›"]
      ONLINE["Online feature store / ‹Redis | DynamoDB›"]
      DWH["Warehouse / ‹BigQuery | Snowflake›"]
      MLP["ML platform: registry · monitoring · LLM orchestration"]
    end

    %% ============ 9. PLATFORM ============
    subgraph L9["⑨ Runtime"]
      direction LR
      K8S["‹Kubernetes› on ‹AWS | GCP›"]
      DB["‹Postgres | Cassandra | Aurora›"]
      OBS["Observability / SLOs"]
    end

    %% ============ 10. CONTROL ============
    subgraph L10["⑩ Reconciliation, evidence & resilience"]
      direction LR
      RECON["Reconciliation workers<br/>‹daily | near-real-time›"]
      BREAKS["Break management & aging"]
      EVID["Evidence store<br/>immutable decision logs · bi-temporal"]
      REG["Regulatory reporting"]
    end

    L1 --> L2 --> L3
    L3 --> L4
    L4 --> L5
    L3 --> L5
    L5 ==> L6
    L6 ==> L7
    L4 --> L7
    L3 -.-> BUS
    L4 -.-> BUS
    L5 -.-> BUS
    BUS --> STREAM --> ONLINE --> FEAT
    BUS -.-> DWH
    DWH --> MLP --> MODEL
    L5 ~~~ RECON
    L6 ~~~ RECON
    RECON --> BREAKS
    L4 ~~~ EVID
    L5 ~~~ EVID
    EVID --> REG
    EVID -.-> DWH
```

### Fill-in checklist

- [ ] Every `‹…›` replaced or the box deleted
- [ ] Confidence tag on every third-party box
- [ ] Regulated boundary drawn and labelled
- [ ] Latency budget written on the decisioning band
- [ ] Reconciliation frequency stated (daily? near-real-time? what does the regulator require?)
- [ ] Stand-in authorisation path shown (what happens when the ledger is unavailable?)
- [ ] Failure/degraded mode noted for each critical vendor

---

## Diagram 3 — Sequence: card authorisation (the hot path)

```mermaid
sequenceDiagram
    autonumber
    participant M as Merchant/Acquirer
    participant S as Scheme
    participant P as Issuer-processor ‹vendor|in-house›
    participant D as Decisioning
    participant F as Feature store
    participant L as Ledger
    M->>S: Authorisation request
    S->>P: ISO 8583 / API auth
    P->>D: Risk check (budget ‹X ms›)
    D->>F: Fetch features (JIT + cached)
    F-->>D: Features
    D-->>P: approve / decline / step-up
    P->>L: Reserve funds (idempotent hold)
    L-->>P: OK / insufficient
    P-->>S: Response
    S-->>M: Approved
    Note over P,L: Stand-in policy applies if L unavailable —<br/>state limits and who owns the exposure
    P->>L: Clearing & settlement (T+n, separate flow)
```

## Diagram 4 — Sequence: outbound instant payment with scam controls (UK-shaped)

```mermaid
sequenceDiagram
    autonumber
    participant C as Customer
    participant A as App
    participant O as Payment orchestration
    participant CoP as Confirmation of Payee
    participant D as Fraud controls
    participant L as Ledger
    participant R as ‹FPS / RTP›
    C->>A: Initiate payment
    A->>O: Create payment intent
    O->>CoP: Name check
    CoP-->>O: match / close match / no match
    O->>D: Scam controls (in-flight)
    D-->>O: allow / warn / friction / block
    alt Warned or friction
      O-->>A: Interstitial warning / step-up
      A-->>C: Confirm or abandon
    end
    O->>L: Post debit (idempotent)
    L-->>O: Posted
    O->>R: Submit
    R-->>O: Accepted / rejected
    O->>L: Reverse on rejection
    Note over D: UK: APP reimbursement liability to £85k,<br/>50/50 sending/receiving PSP. This branch is a P&L line.
```

## Diagram 5 — Sequence: onboarding

```mermaid
sequenceDiagram
    autonumber
    participant C as Applicant
    participant A as App
    participant ORCH as KYC orchestrator
    participant IDV as Document + liveness ‹vendor›
    participant DATA as Data verification ‹vendor›
    participant SCR as Sanctions/PEP ‹vendor›
    participant DEC as Decision engine
    participant E as Evidence store
    C->>A: Apply
    A->>ORCH: Start case
    ORCH->>IDV: Document + selfie
    ORCH->>DATA: Identity data match
    ORCH->>SCR: Screening
    IDV-->>ORCH: Result
    DATA-->>ORCH: Result
    SCR-->>ORCH: Hits / clear
    ORCH->>DEC: Score & decide
    DEC->>E: Log inputs, versions, decision
    DEC-->>A: approve / refer / decline
    Note over ORCH: Each vendor is a swappable step<br/>with a fallback chain.
```

## Diagram 6 — Reconciliation (the one everyone omits)

```mermaid
flowchart LR
    LED[["Our ledger — postings"]]
    RAIL["Rail statements / scheme files"]
    PART["Partner or sponsor bank balances"]
    PROC["Processor clearing files"]
    W["Reconciliation workers<br/>stateless · replayable · per-rail"]
    B["Break register<br/>owner · age · amount"]
    RPT["Regulatory returns<br/>‹daily safeguarding | partner recon›"]
    LED --> W
    RAIL --> W
    PART --> W
    PROC --> W
    W --> B
    W --> RPT
    B --> RPT
```

---

## How to use this with the wiki

1. Pick the company or the design you are documenting.
2. Answer `templates/key-questions.md` for it first. The answers *are* the diagram labels.
3. Fill the skeleton, keep the confidence tags.
4. Save to `diagrams/‹name›.mmd` and link it from the relevant wiki page and `index.md`.
5. Anything you could not answer goes into `open-questions.md` — that is the daily scout's
   work queue.
