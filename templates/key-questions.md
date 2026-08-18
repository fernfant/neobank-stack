---
title: Key questions — neobank architecture
type: template
status: living
updated: 2026-08-18
---

# Key questions

Use this three ways: as a **design review** checklist for your own build, as a **due-diligence**
script for a vendor or an acquisition target, and as the **research agenda** the daily scout
works through for other companies.

Questions marked **★** are the ones that most often expose a real problem. If you only have an
hour, ask those.

---

## 0. Framing

1. Are we designing a bank, an EMI/wallet, or a product on someone else's bank? ★
2. What is our target cost-to-serve per active account, and which layer dominates it? ★
3. Which layer, if it fails for four hours, ends the company?
4. What is the single number the board tracks that this architecture must move?

## 1. Licence and charter

5. Who holds the money, legally? Whose balance sheet? ★
6. If a sponsor bank: what happens if they are ordered to exit the programme, and what is our
   migration path and timeline? ★
7. UK: are we going for mobilisation, and what are the exit criteria as engineering
   deliverables?
8. UK EMI: are we ready for daily safeguarding reconciliation, monthly returns, annual audits
   and 48-hour CASS 10 resolution packs from 7 May 2026? ★
9. US: which state money-transmitter licences gate which markets, and does that sequence our
   launch plan?
10. Which entity files the SARs/SAR, and who owns the AML programme of record?

## 2. Core ledger

11. Is the ledger double-entry with balances **derived** from postings, or is there a mutable
    balance field anywhere? ★
12. Are the invariants enforced at the storage layer or in application code? ★
13. Is it append-only? How are corrections made?
14. Is every write idempotent, and what is the deduplication key? ★
15. Is it bi-temporal — can we reconstruct what we believed the balance was on a past date?
16. What is the account-path scheme, and does it already accommodate pots, holds, multi-currency
    and safeguarded funds without a schema change?
17. Where does product logic live — encoded as ledger transactions, or in application code that
    posts to the ledger? ★
18. What is the consistency model, and which consumers must be idempotent as a result?
19. If bought: what language/DSL defines products, and what is the migration cost away from it? ★
20. If bought: can we stream raw postings out continuously into our own warehouse?
21. If built: who is on the 3am rota, and what is the runbook for a duplicate posting?
22. What is the throughput ceiling and how was it measured (not marketed)?

## 3. Payment rails and money movement

23. Which rails do we touch, and is access direct, agency, or via a PaaS? ★
24. What is the failover if the access provider has an incident? Has it been tested?
25. Is there one normalised internal money-movement model, or per-rail special cases? ★
26. Draw the payment state machine. Where can it hang, and for how long? ★
27. How are late returns handled — ACH R-codes days later, Direct Debit indemnity claims months
    later?
28. What is the deduplication and ordering strategy per rail?
29. Cross-border: is a corridor configuration + adapter, or a code branch? ★
30. Cross-border: how is FX exposure between quote and settlement managed, and how is FX
    gain/loss posted?
31. Is ISO 20022 the internal message model? (UK: NPA/RPIB direction. )
32. UK: is Confirmation of Payee on the outbound path, and what is its latency and failure mode?
33. US: what routes a payment between ACH, RTP and FedNow, and on what cost/speed/reachability
    logic?

## 4. Card issuing

34. Which of the four roles (BIN sponsor, issuer-processor, program manager, fulfilment) is each
    vendor actually performing? ★
35. What is the measured p99 and p99.9 authorisation latency, and how much of the budget is left
    for our risk checks? ★
36. What is the stand-in policy when our ledger is unavailable, what are the limits, and who
    carries the exposure? ★
37. What is the approval-rate baseline, and who owns improving it? (In the US this is revenue.)
38. How are disputes and chargebacks handled — whose workflow, whose timelines?
39. Are network tokens, 3DS and wallet provisioning included, or our problem?
40. At what card volume does insourcing the processor beat the fee? Have we modelled it? ★

## 5. Identity and onboarding

41. Do we own the orchestration, or is one vendor the whole funnel? ★
42. What happens to onboarding when the primary IDV vendor is down? Is there a fallback chain? ★
43. Are all inputs, provider responses, model versions and the final decision logged immutably? ★
44. What is the all-in cost per verified account, including manual review?
45. What is the manual-review rate, and what is the queue's SLA?
46. Is OFAC/sanctions rescreening event-driven and within 24 hours of list updates? ★
47. KYB: how are UBOs resolved, and at what ownership threshold?
48. What is the perpetual-KYC trigger set — behaviour change, list change, document expiry?
49. How do we detect injected/deepfake documents and selfies, and when was that last tested?

## 6. Financial crime

50. Can a risk analyst ship a new control without an engineer and without production access? ★
51. Can a proposed control be back-tested against history before it goes live? ★
52. Is every control execution logged with its input features, version and decision? ★
53. What is the false-positive rate, and what is the alerts-per-analyst-per-day figure?
54. Are detection, recommendation and final-action logic separated, or fused in one rule?
55. What is the latency budget for in-line controls, and which controls are async?
56. UK: what is our APP fraud reimbursement exposure, and which in-flight interventions reduce
    it? ★
57. UK: what is our inbound mule-detection capability, given 50/50 receiving-side liability? ★
58. Are AML, fraud and sanctions one platform or three, and is that deliberate?
59. Who files SARs, on what system, and what is the median time from alert to filing?
60. Is any model in the decisioning path unexplainable, and how is that defended to a regulator?

## 7. Credit and decisioning

61. Are model and policy separately versioned and separately deployable? ★
62. How are adverse-action reason codes generated, and are they actually the reasons? (US: ECOA) ★
63. UK: how is affordability evidenced under Consumer Duty?
64. Are credit and fincrime sharing one feature store, or computing "average monthly inflow"
    twice? ★
65. Are training sets built point-in-time-correct from decision logs, or from current-state
    tables? ★
66. What lift does internal transaction data give over bureau-only, measured out-of-time?
67. What is the cost per bureau pull, and is the caching strategy compliant?
68. How often are models retrained, and what triggers an out-of-cycle retrain?
69. What is the champion/challenger setup, and how is a challenger promoted?

## 8. Data and ML platform

70. Is the decision path independent of the analytics path? Can the warehouse be down without
    declining payments? ★
71. Are feature definitions single-sourced across batch and streaming? ★
72. What is the p99 online feature-retrieval latency in the auth path?
73. Is the event log replayable, and has a replay actually been performed?
74. Is there a model registry with lineage from data to deployed artefact?
75. What monitoring exists for drift, and who is paged?
76. If LLMs are in operational workflows: what is the evaluation regime, where is the human in
    the loop, and can the agent move money? ★
77. What is the data retention policy per class, and does it satisfy the longest regulatory
    obligation?

## 9. Runtime and infrastructure

78. What is the cost of creating and operating one more service? Does our topology match it? ★
79. Which datastore holds the ledger, and does its consistency model support the invariants?
80. What is the DR posture — RTO and RPO — for the ledger specifically? ★
81. Multi-region or single? What is the actual tested failover time?
82. What is the deployment frequency, and can a change to a risk control ship in under a day?
83. How is secrets management and key handling done for card data / PCI scope?
84. What is in PCI scope, and has the scope been deliberately minimised?

## 10. Resilience, reconciliation, evidence

85. **Is reconciliation a first-class subsystem with an owner, or a batch job?** ★
86. What is the reconciliation frequency per rail and per partner, and does it meet the
    regulatory requirement (UK daily safeguarding; US near-real-time partner accounts)? ★
87. Is there a break register with owner, age and amount? What is the oldest open break? ★
88. Can the sponsor bank or regulator independently verify our sub-ledger, continuously? ★
89. Can we reconstruct any historical balance and any historical decision without rewriting
    anything? ★
90. Which vendors are on the critical path for an important business service?
91. For each: what is the documented exit strategy (DORA Art. 30), and has it been rehearsed? ★
92. What is our concentration risk on cloud, and what is the honest degraded-mode plan?
93. What are the impact tolerances for each important business service, and were they tested?
94. What is the 24/7 on-call model for money incidents, and what is the escalation to the board?

## 11. Commercial and organisational

95. What is the revenue model — interchange, lending, subscription, FX — and which layer earns
    it? ★
96. Which vendor fee grows fastest with scale?
97. Is any vendor also a competitor? ★
98. How many engineers does this architecture require to *operate*, separate from building it? ★
99. What is the single biggest architectural regret we would have in three years?
100. What would we do differently if we were starting today, and why aren't we?

---

## Scoring (optional)

For a design review, score each starred question 0–3:

| Score | Meaning |
| --- | --- |
| 0 | No answer, or the answer reveals the thing does not exist |
| 1 | Answer exists but is aspirational / undocumented / untested |
| 2 | Documented and implemented, not recently tested |
| 3 | Implemented, tested, and someone is accountable for it by name |

Anything at 0 or 1 in section 10 (reconciliation and evidence) is the highest-priority
remediation regardless of what else scores badly. Both UK and US regulators converged on that
layer independently — see `wiki/comparisons/uk-vs-usa.md`.
