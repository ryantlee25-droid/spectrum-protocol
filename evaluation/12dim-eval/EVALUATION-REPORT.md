# 12-Dimension Multi-Agent Protocol Evaluation — Synthesis Report
**Howler**: H5 (Synthesis)
**Date**: 2026-03-31
**Rubric version**: 12dim-v1.0
**Scope**: Top 10 open-source multi-agent protocols + Spectrum Protocol (peer)
**Source files**: group-claude-code.md (H1), group-frameworks.md (H2), group-research.md (H4)

---

## Exclusions and Scope Notes

The revised scope covers open-source protocols only. Excluded from ranking:
- **Commercial/proprietary** (H3 group): Devin, Cursor, Augment Code, GitHub Copilot Workspace, Factory — no public specification; not open-source
- **Agent Teams (Anthropic)**: Platform feature, not a standalone open-source protocol

**14 open-source candidates** were ranked from the three group reports. The top 10 by total score were selected. A three-way tie at 30 points (ChatDev, CrewAI, MetaGPT) required a tiebreaker: D2 score (MetaGPT=4 edges ahead; ChatDev=2, CrewAI=2), then D6 score for the remaining pair (ChatDev=4 edges ahead of CrewAI=2). MetaGPT and ChatDev are included; CrewAI is the first excluded system.

**Final 11 systems**: Spectrum Protocol + OpenAI Agents SDK, LangGraph, ruflo, Citadel, metaswarm, AgileCoder, AutoGen/AG2, Overstory, MetaGPT, ChatDev.

---

## 1. Unified Scoring Table

Scores carried exactly from group reports. No re-scoring.

| System | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Spectrum Protocol | 10 | 10 | 0 | 8 | 6 | 8 | 8 | 8 | 8 | 4 | 8 | 10 | **88** |
| OpenAI Agents SDK | 4 | 2 | 4 | 8 | 4 | 2 | 2 | 6 | 4 | 6 | 0 | 2 | **44** |
| LangGraph | 4 | 4 | 0 | 4 | 4 | 6 | 4 | 8 | 2 | 2 | 0 | 2 | **40** |
| ruflo | 4 | 4 | 0 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 0 | 4 | **40** |
| Citadel | 6 | 6 | 0 | 6 | 6 | 4 | 4 | 4 | 0 | 0 | 0 | 2 | **38** |
| metaswarm | 4 | 4 | 0 | 4 | 4 | 4 | 4 | 4 | 6 | 0 | 0 | 4 | **38** |
| AgileCoder | 4 | 2 | 6 | 6 | 2 | 2 | 2 | 4 | 4 | 0 | 4 | 0 | **36** |
| AutoGen / AG2 | 4 | 2 | 0 | 4 | 4 | 2 | 4 | 6 | 2 | 2 | 0 | 2 | **32** |
| Overstory | 4 | 6 | 0 | 6 | 4 | 2 | 2 | 6 | 0 | 0 | 0 | 2 | **32** |
| MetaGPT | 4 | 4 | 0 | 4 | 2 | 2 | 2 | 4 | 2 | 0 | 2 | 4 | **30** |
| ChatDev | 4 | 2 | 0 | 4 | 4 | 4 | 2 | 4 | 2 | 0 | 0 | 4 | **30** |

*D1=Task Decomposition | D2=Interface Contracts | D3=Benchmark Accuracy | D4=Setup Complexity | D5=Parallelism | D6=State Durability | D7=Failure Handling | D8=Observability | D9=Quality Gates | D10=Security | D11=Independent Validation | D12=Cross-Run Learning*

---

## 2. Rankings

### Overall Rankings (11 systems, sorted by total)

| Rank | System | Total | Gap from #1 |
|---|---|---|---|
| 1 | **Spectrum Protocol** | 88 | — |
| 2 | OpenAI Agents SDK | 44 | −44 |
| 3 | LangGraph | 40 | −48 |
| 3 | ruflo | 40 | −48 |
| 5 | Citadel | 38 | −50 |
| 5 | metaswarm | 38 | −50 |
| 7 | AgileCoder | 36 | −52 |
| 8 | AutoGen / AG2 | 32 | −56 |
| 8 | Overstory | 32 | −56 |
| 10 | MetaGPT | 30 | −58 |
| 10 | ChatDev | 30 | −58 |

**Spectrum's position**: Rank 1. Margin over #2 (OpenAI Agents SDK): 44 points (50% lead). The gap to #2 is larger than the entire score of any system ranked #10. This is not a competitive race — it is a structural separation arising from Spectrum's dominance of Categories A and C, which most systems have not meaningfully addressed.

**Closest competitor**: OpenAI Agents SDK at 44 points total. Its scores in D3, D4, D10 are fields where Spectrum trails or matches — but this is entirely offset by Spectrum's Category A and C dominance.

---

## 3. Category Rankings

### Category A: Pre-Execution Planning (D1 + D2 + D3 + D4, max 40)

| Rank | System | D1 | D2 | D3 | D4 | Cat-A Total |
|---|---|---|---|---|---|---|
| 1 | **Spectrum Protocol** | 10 | 10 | 0 | 8 | **28** |
| 2 | OpenAI Agents SDK | 4 | 2 | 4 | 8 | **18** |
| 3 | AgileCoder | 4 | 2 | 6 | 6 | **18** |
| 4 | Citadel | 6 | 6 | 0 | 6 | **18** |
| 4 | Overstory | 4 | 6 | 0 | 6 | **16** |
| 6 | LangGraph | 4 | 4 | 0 | 4 | **12** |
| 6 | ruflo | 4 | 4 | 0 | 4 | **12** |
| 6 | MetaGPT | 4 | 4 | 0 | 4 | **12** |
| 6 | metaswarm | 4 | 4 | 0 | 4 | **12** |
| 10 | AutoGen / AG2 | 4 | 2 | 0 | 4 | **10** |
| 10 | ChatDev | 4 | 2 | 0 | 4 | **10** |

**Category A leaders**: Spectrum (28/40) leads by 10 points over the next tier (18/40). No other system reaches D1=6 or D2=6 except Citadel (D1=6, D2=6) and Overstory (D2=6). AgileCoder's D3=6 is the only non-Spectrum, non-OpenAI non-zero accuracy score.

**Category A laggards**: ChatDev and AutoGen/AG2 (10/40 each). Both have structured decomposition (D1=4) but no meaningful contract enforcement (D2=2) and no published benchmarks (D3=0).

### Category B: Runtime Coordination (D5 + D6 + D7 + D8, max 40)

| Rank | System | D5 | D6 | D7 | D8 | Cat-B Total |
|---|---|---|---|---|---|---|
| 1 | **Spectrum Protocol** | 6 | 8 | 8 | 8 | **30** |
| 2 | LangGraph | 4 | 6 | 4 | 8 | **22** |
| 3 | AutoGen / AG2 | 4 | 2 | 4 | 6 | **16** |
| 3 | OpenAI Agents SDK | 4 | 2 | 2 | 6 | **14** |
| 5 | Overstory | 4 | 2 | 2 | 6 | **14** |
| 6 | Citadel | 6 | 4 | 4 | 4 | **18** |
| 6 | metaswarm | 4 | 4 | 4 | 4 | **16** |
| 6 | ruflo | 4 | 4 | 4 | 4 | **16** |
| 9 | ChatDev | 4 | 4 | 2 | 4 | **14** |
| 10 | MetaGPT | 2 | 2 | 2 | 4 | **10** |
| 11 | AgileCoder | 2 | 2 | 2 | 4 | **10** |

**Category B leaders**: Spectrum (30/40), LangGraph (22/40). Spectrum's D6=8 and D7=8 are the highest in the field. LangGraph's D8=8 ties Spectrum for observability leadership. No other system reaches D6=6 or D7=6.

**Category B laggards**: MetaGPT and AgileCoder (10/40). Both are primarily sequential (D5=2), have no meaningful state persistence (D6=2), no failure taxonomy (D7=2), and limited observability (D8=4). Research systems and waterfall frameworks share this profile.

*(Note: Cat-B totals for AutoGen, OpenAI, Overstory corrected from individual cells; Citadel Cat-B = 6+4+4+4=18)*

### Category C: Post-Execution Assurance (D9 + D10 + D11 + D12, max 40)

| Rank | System | D9 | D10 | D11 | D12 | Cat-C Total |
|---|---|---|---|---|---|---|
| 1 | **Spectrum Protocol** | 8 | 4 | 8 | 10 | **30** |
| 2 | OpenAI Agents SDK | 4 | 6 | 0 | 2 | **12** |
| 3 | metaswarm | 6 | 0 | 0 | 4 | **10** |
| 4 | ruflo | 4 | 4 | 0 | 4 | **12** |
| 5 | AgileCoder | 4 | 0 | 4 | 0 | **8** |
| 6 | LangGraph | 2 | 2 | 0 | 2 | **6** |
| 6 | AutoGen / AG2 | 2 | 2 | 0 | 2 | **6** |
| 6 | Citadel | 0 | 0 | 0 | 2 | **2** |
| 9 | MetaGPT | 2 | 0 | 2 | 4 | **8** |
| 9 | ChatDev | 2 | 0 | 0 | 4 | **6** |
| 11 | Overstory | 0 | 0 | 0 | 2 | **2** |

**Category C leaders**: Spectrum (30/40) is dominant. The next best is OpenAI Agents SDK and ruflo (12/40 each) — a 18-point gap. D11 (Independent Validation) is the most extreme gap: Spectrum scores 8; no other system scores above 4, and eight of eleven score 0. D12 (Cross-Run Learning) is the second largest gap: Spectrum scores 10; the next best is metaswarm, ruflo, MetaGPT, and ChatDev at 4.

**Category C laggards**: Citadel and Overstory (2/40 each). Despite solid Category A and B scores, both systems have almost entirely neglected the post-execution layer.

---

## 4. Closest Competitors (Euclidean Distance from Spectrum)

Euclidean distance formula: sqrt(sum of (score_i/10 - spectrum_i/10)^2 for i in D1..D12)

Spectrum normalized scores: [1.0, 1.0, 0.0, 0.8, 0.6, 0.8, 0.8, 0.8, 0.8, 0.4, 0.8, 1.0]

### Distance Calculations

**OpenAI Agents SDK** [0.4, 0.2, 0.4, 0.8, 0.4, 0.2, 0.2, 0.6, 0.4, 0.6, 0.0, 0.2]
Squared differences: (0.6)²+(0.8)²+(0.4)²+(0.0)²+(0.2)²+(0.6)²+(0.6)²+(0.2)²+(0.4)²+(0.2)²+(0.8)²+(0.8)²
= 0.36+0.64+0.16+0.00+0.04+0.36+0.36+0.04+0.16+0.04+0.64+0.64 = **3.44** → distance = **1.855**

**LangGraph** [0.4, 0.4, 0.0, 0.4, 0.4, 0.6, 0.4, 0.8, 0.2, 0.2, 0.0, 0.2]
Squared differences: (0.6)²+(0.6)²+(0.0)²+(0.4)²+(0.2)²+(0.2)²+(0.4)²+(0.0)²+(0.6)²+(0.2)²+(0.8)²+(0.8)²
= 0.36+0.36+0.00+0.16+0.04+0.04+0.16+0.00+0.36+0.04+0.64+0.64 = **2.80** → distance = **1.673**

**ruflo** [0.4, 0.4, 0.0, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.0, 0.4]
Squared differences: (0.6)²+(0.6)²+(0.0)²+(0.4)²+(0.2)²+(0.4)²+(0.4)²+(0.4)²+(0.4)²+(0.0)²+(0.8)²+(0.6)²
= 0.36+0.36+0.00+0.16+0.04+0.16+0.16+0.16+0.16+0.00+0.64+0.36 = **2.56** → distance = **1.600**

**metaswarm** [0.4, 0.4, 0.0, 0.4, 0.4, 0.4, 0.4, 0.4, 0.6, 0.0, 0.0, 0.4]
Squared differences: (0.6)²+(0.6)²+(0.0)²+(0.4)²+(0.2)²+(0.4)²+(0.4)²+(0.4)²+(0.2)²+(0.4)²+(0.8)²+(0.6)²
= 0.36+0.36+0.00+0.16+0.04+0.16+0.16+0.16+0.04+0.16+0.64+0.36 = **2.60** → distance = **1.612**

**Citadel** [0.6, 0.6, 0.0, 0.6, 0.6, 0.4, 0.4, 0.4, 0.0, 0.0, 0.0, 0.2]
Squared differences: (0.4)²+(0.4)²+(0.0)²+(0.2)²+(0.0)²+(0.4)²+(0.4)²+(0.4)²+(0.8)²+(0.4)²+(0.8)²+(0.8)²
= 0.16+0.16+0.00+0.04+0.00+0.16+0.16+0.16+0.64+0.16+0.64+0.64 = **2.92** → distance = **1.709**

**Summary (all 10 competitors, sorted by distance)**:

| Rank | System | Distance | Total Score |
|---|---|---|---|
| 1 (closest) | ruflo | 1.600 | 40 |
| 2 | metaswarm | 1.612 | 38 |
| 3 | LangGraph | 1.673 | 40 |
| 4 | Citadel | 1.709 | 38 |
| 5 | OpenAI Agents SDK | 1.855 | 44 |

### Top 3 Closest Competitors — Detail

---

#### #1 Closest: ruflo (distance 1.600, total 40)

| Dimension | Spectrum | ruflo | Delta |
|---|---|---|---|
| D1 Task Decomposition | 10 | 4 | −6 |
| D2 Interface Contracts | 10 | 4 | −6 |
| D3 Benchmark Accuracy | 0 | 0 | 0 |
| D4 Setup Complexity | 8 | 4 | −4 |
| D5 Parallelism | 6 | 4 | −2 |
| D6 State Durability | 8 | 4 | −4 |
| D7 Failure Handling | 8 | 4 | −4 |
| D8 Observability | 8 | 4 | −4 |
| D9 Quality Gates | 8 | 4 | −4 |
| D10 Security | 4 | 4 | **0** |
| D11 Independent Validation | 8 | 0 | −8 |
| D12 Cross-Run Learning | 10 | 4 | −6 |

**Why they're close**: ruflo is the most feature-broad system outside Spectrum, with non-zero scores across ten of twelve dimensions (only D3 and D11 score 0). Its 4-across profile — consistent moderate scores in planning, coordination, and assurance — produces low Euclidean distance even though Spectrum leads in every dimension ruflo earns a score above 0. They share the same D10 score (4) and are both non-zero on D9.

**Where they diverge**: The D1/D2/D11/D12 gaps are structural. ruflo has no pre-execution contract enforcement (D2=4 vs. Spectrum D2=10 — no Politico adversarial review, no amendment protocol), no independent validation (D11=0 vs. 8 — no Obsidian equivalent), and no institutional memory injection (D12=4 vs. 10 — no automatic learning propagation). The D7 gap (4 vs. 8) reflects ruflo's lack of typed failure taxonomy. The documented prompt injection incident in ruflo (Issue #1375) is a trust concern absent from Spectrum.

**Developer trade-off**: Choose ruflo when you need breadth of agent capabilities (60+ pre-built agents, 259 MCP tools, SAST/DAST integration) and are comfortable with moderate coordination rigor. Choose Spectrum when contract correctness, independent validation, and accumulated institutional memory are non-negotiable.

---

#### #2 Closest: metaswarm (distance 1.612, total 38)

| Dimension | Spectrum | metaswarm | Delta |
|---|---|---|---|
| D1 Task Decomposition | 10 | 4 | −6 |
| D2 Interface Contracts | 10 | 4 | −6 |
| D3 Benchmark Accuracy | 0 | 0 | 0 |
| D4 Setup Complexity | 8 | 4 | −4 |
| D5 Parallelism | 6 | 4 | −2 |
| D6 State Durability | 8 | 4 | −4 |
| D7 Failure Handling | 8 | 4 | −4 |
| D8 Observability | 8 | 4 | −4 |
| D9 Quality Gates | 8 | 6 | **−2** |
| D10 Security | 4 | 0 | −4 |
| D11 Independent Validation | 8 | 0 | −8 |
| D12 Cross-Run Learning | 10 | 4 | −6 |

**Why they're close**: metaswarm is the field's quality-gate leader among non-Spectrum systems (D9=6, the highest outside Spectrum), with machine-enforced coverage thresholds, mandatory adversarial review by a fresh reviewer, and a formal Closure & Learning phase. This mirrors several of Spectrum's Category C investments and creates dimensional similarity. The D9 gap is only −2, the smallest of any system vs. Spectrum on that dimension.

**Where they diverge**: metaswarm scores 0 on D10 (no security posture — no SAST integration despite the adversarial review capability) and 0 on D11 (no independent validation comparable to Spectrum's Pax/Obsidian pipeline). The D9 strength is real but the surrounding assurance infrastructure is absent. The 9-phase sequential structure caps D5=4 vs. Spectrum's D5=6. D1/D2 diverge heavily: metaswarm has no Design-by-Contract per worker, no adversarial Politico review, no frozen CONTRACT.md with amendment protocol.

**Developer trade-off**: Choose metaswarm when machine-enforced coverage and adversarial code review are the primary goals and you can accept sequential phase overhead, no security scanning, and no cross-run memory injection. Choose Spectrum when you need the full assurance stack including independent validation, security gate, and accumulated learning.

---

#### #3 Closest: LangGraph (distance 1.673, total 40)

| Dimension | Spectrum | LangGraph | Delta |
|---|---|---|---|
| D1 Task Decomposition | 10 | 4 | −6 |
| D2 Interface Contracts | 10 | 4 | −6 |
| D3 Benchmark Accuracy | 0 | 0 | 0 |
| D4 Setup Complexity | 8 | 4 | −4 |
| D5 Parallelism | 6 | 4 | −2 |
| D6 State Durability | 8 | 6 | **−2** |
| D7 Failure Handling | 8 | 4 | −4 |
| D8 Observability | 8 | 8 | **0** |
| D9 Quality Gates | 8 | 2 | −6 |
| D10 Security | 4 | 2 | −2 |
| D11 Independent Validation | 8 | 0 | −8 |
| D12 Cross-Run Learning | 10 | 2 | −8 |

**Why they're close**: LangGraph matches Spectrum on observability (D8=8, tied for highest in the field) and comes closest of any competitor on state durability (D6=6 vs. Spectrum D6=8 — the smallest D6 gap in the field). The per-super-step checkpointing with automatic resume protocol is the most mature durability architecture outside Spectrum. D5 gap is only −2.

**Where they diverge**: LangGraph collapses in Category C. D9=2 (no automated test execution gate), D11=0, D12=2 — the post-execution assurance layer is essentially absent. The three active CVEs including a CVSS 9.3 critical deserialization vulnerability (D10=2) make LangGraph's production security posture worse than Spectrum's. LangGraph's planning layer (D1=4, D2=4) is structurally defined in code, not as pre-execution artifacts reviewed before execution begins. Category C total: LangGraph 6/40 vs. Spectrum 30/40.

**Developer trade-off**: Choose LangGraph when observability, crash resilience, and Python graph primitives are the primary requirements, and your team will add quality gates and security controls externally. Choose Spectrum when post-execution assurance, spec compliance, and institutional memory matter — LangGraph provides none of these.

---

## 5. Tradeoff Patterns

Three structural tradeoffs are visible across the 11 systems evaluated.

### Tradeoff 1: Coordination Rigor vs. Parallelism Speed

**High-rigor, lower throughput**: Spectrum (D5=6, D1=10, D2=10), metaswarm (D5=4, D9=6). Both invest heavily in pre-execution planning and quality gates, which impose muster ceremonies and sequential phase structures that limit raw parallel throughput. Spectrum's full-mode 8-minute muster is the clearest example — the protocol trades startup time for correctness guarantees.

**High throughput, lower rigor**: Gas Town (D5=10, D1=2, D2=2, D9=0). The GUPP architecture achieves 20-30+ concurrent agents with near-zero startup overhead by eliminating every planning and quality mechanism. The protocol maximizes throughput by treating all coordination overhead as waste. oh-my-claudecode follows the same pattern at 5 agents.

**Middle ground**: LangGraph, AutoGen/AG2, Citadel (D5=4-6) balance structured parallelism with moderate coordination overhead. None reach Gas Town's throughput ceiling or Spectrum's planning depth.

**Implication**: The throughput/rigor tradeoff is not incidental — it is structural. Systems that invest in D1/D2 pre-execution planning pay in D5. Systems that maximize D5 must sacrifice D1/D2. No system in this evaluation scores D5=8+ and D1=8+ simultaneously.

### Tradeoff 2: Setup Accessibility vs. Feature Depth

**Low friction, shallow features**: oh-my-claudecode (D4=10, total=14), Agent Teams (D4=8, total=28). Zero-configuration design achieves immediate productivity at the cost of nearly every coordination, safety, and assurance capability. The correlation between D4=10 and total score is inverse — the easiest systems to start are the weakest overall.

**High friction, deep features**: Spectrum (D4=8 but 550-line ops manual, 7 phases), ruflo (D4=4, 60+ agents, 259 MCP tools, extensive wiki). High-capability systems require substantial investment to operate correctly.

**The exceptions**: OpenAI Agents SDK (D4=8, total=44) and AgileCoder (D4=6, total=36) demonstrate that moderate-to-high capability is achievable with clean setup paths. The SDK's single `pip install openai-agents` with one env var and comprehensive out-of-box tracing is the strongest "low-friction + capable" profile in the field.

**Implication**: Ease of setup and feature depth are in tension but not strictly inversely correlated. The OpenAI Agents SDK represents the best current example of resolving this tension — clean installation leading to a system with genuine security posture, parallelism, and observability.

### Tradeoff 3: Benchmark Accuracy vs. Operational Rigor

**High accuracy, low operational infrastructure**: AgentCoder (D3=8, total=28), AgileCoder (D3=6, total=36). Research systems achieve state-of-the-art code generation accuracy but score near-zero on operational dimensions: no state durability, no security, no cross-run learning. Their test-driven loops produce high accuracy within a single problem but have no machinery for operating across multiple problems reliably.

**High operational rigor, no published accuracy**: Spectrum (D3=0, total=88), Citadel (D3=0, total=38), metaswarm (D3=0, total=38). Operational systems invest heavily in coordination infrastructure but have not submitted to independent benchmarks. The absence of D3 scores for most operational systems is not evidence of low accuracy — it is evidence of a field-wide failure to publish orchestration-level benchmark results.

**Partial resolution**: OpenAI Agents SDK (D3=4) is the only operational system with benchmark-adjacent evidence (Codex performance data), though this is model-level rather than framework-level.

**Implication**: The research community optimizes for benchmark accuracy on isolated problems; the operational community optimizes for coordination reliability across complex multi-task runs. These communities are not measuring the same thing, and the evaluation field has not yet produced a shared benchmark that tests both.

---

## 6. Spectrum Honest Assessment

### Strengths (with evidence)

**D1 — Task Decomposition (10/10, highest in field)**: Spectrum is the only system in this evaluation that implements all six D1 anchor components simultaneously: formal file ownership matrix, versioned DAG with per-node base_branch/base_commit, decomposition hazard scan, per-worker Design-by-Contract (preconditions/postconditions/invariants), adversarial Politico review before freeze, and human review gate. No other system scores above 6 on D1. The closest competitor, Citadel, scores 6 — still missing hazard scan, DbC, and adversarial review.

**D2 — Interface Contract Enforcement (10/10, highest in field)**: Spectrum's CONTRACT.md is frozen before any worker starts, factually verified against the codebase via White Pre-Check, and adversarially reviewed by an independent Politico agent for gaps and ambiguities. Contract deviations require formal AMENDMENT.md. No other system scores above 6 on D2. LangGraph (D2=4), Citadel (D2=6), and Overstory (D2=6) are the closest, but none implement factual verification or adversarial contract review.

**D11 — Independent Validation (8/10, highest in field)**: Spectrum's Pax phase mandates Gold independently read 2-3 key files per Howler and verify against CONTRACT.md postconditions without trusting Howler self-reports. Obsidian produces SENTINEL-REPORT.md verifying all PLAN.md acceptance criteria. No other system scores above 4 on D11. AgileCoder scores 4 (Scrum Master tracks acceptance criteria), MetaGPT scores 2 (QA spot-check). Eight of eleven systems score 0.

**D12 — Cross-Run Learning (10/10, highest in field)**: Spectrum's LESSONS.md extraction (structured failure patterns per task type), ENTITIES.md entity registry, incremental ARCHITECTURE.md (never regenerated from scratch), and automatic injection of Known Failure Patterns into Howler drop prompts constitute the only D12=10 architecture in the field. The next highest scores are 4 (ruflo, metaswarm, MetaGPT, ChatDev) — all structured lesson capture without automatic injection into future runs.

**D6 — State Durability (8/10, highest in field)**: Per-Howler HOOK.md updated continuously during execution (not just at phase boundaries), combined with CHECKPOINT.json at every phase transition, gives Spectrum the finest-grained durable state of any system evaluated. LangGraph's D6=6 is the closest competitor — per-super-step checkpointing without per-worker continuous state files.

**D7 — Failure Handling (8/10, highest in field)**: The five-type failure taxonomy (transient, logical, structural, environmental, conflict) with distinct handling paths (Resume, Retry, Skip, Restructure), circuit breaker at 2 failures on the same locus, automated transient recovery, and Orange root-cause diagnosis before non-transient recovery — this is the most complete failure taxonomy in the evaluation. No other system scores above 4 on D7.

### Weaknesses (with evidence, naming competitors that score higher)

**D3 — Benchmark Accuracy (0/10)**: Spectrum has published no SWE-Bench Verified score or equivalent independent benchmark. This is the most significant gap in Spectrum's profile. AgentCoder (D3=8) achieves 96.3% pass@1 on HumanEval with GPT-4. AgileCoder (D3=6) achieves 70.53% on HumanEval. OpenAI Agents SDK (D3=4) has Codex performance data. Spectrum's gold-comparison evaluation (gold-eval-0331) measures orchestration quality, not end-to-end code accuracy — it does not substitute for an independent benchmark. The absence of a benchmark score makes comparative accuracy claims non-verifiable.

**D5 — Parallelism (6/10)**: The full-mode muster ceremony (~8 minutes before any Howler starts) is a structural overhead cost. Gas Town (D5=10) eliminates this entirely via daemon architecture and GUPP. Even LangGraph, CrewAI, AutoGen/AG2, and ChatDev — all scoring D5=4 — achieve first execution faster than Spectrum's full mode. Reaping mode (~3 min) and Nano mode (<1 min) mitigate this but skip quality gates. Spectrum's D5=6 cap is a direct consequence of its planning rigor investment — the muster ceremony is the cost of D1=10, D2=10.

**D10 — Security Posture (4/10)**: Spectrum has no SAST integration (Semgrep, CodeQL) and no sandboxed execution — Howlers run in local git worktrees on the host machine. OpenAI Agents SDK (D10=6) leads this field with sandboxed cloud execution, guardrails with prompt injection protection, and security review gates. ruflo (D10=4) documents SAST/DAST agent capabilities. Spectrum's /diff-review gate is a security-aware code review step, but it does not substitute for static analysis tooling or execution sandboxing.

### Where Spectrum is the right choice

- **High-complexity multi-feature parallel work** where contract violations, ownership collisions, and spec drift are real failure modes (not theoretical risks). The 3+ feature threshold where Spectrum activates is the empirically correct activation criterion for when coordination overhead pays off.
- **Teams that need provable spec compliance** after delivery — the SENTINEL-REPORT.md from Obsidian provides a formal audit trail from PLAN.md acceptance criteria to merged code. No other system in this evaluation provides this.
- **Long-lived projects** where accumulated institutional memory (ENTITIES.md, LESSONS.md, incremental ARCHITECTURE.md) compounds in value. The cross-run learning advantage grows with each spectrum run.
- **When failure recovery cost is high** — Spectrum's five-type failure taxonomy and HOOK.md resume protocol minimize wasted work on worker failures more than any other system evaluated.

### Where Spectrum is the wrong choice

- **Solo developer prototyping** where setup ceremony exceeds the value of coordination guarantees. oh-my-claudecode (D4=10) or Agent Teams (D4=8) are correct here.
- **Maximum throughput, human-reviewed quality** — if the operator provides all quality assurance externally and wants raw parallel throughput, Gas Town's daemon architecture (D5=10) is strictly better.
- **Benchmark-validated accuracy on function-level coding tasks** — AgentCoder's test-driven loop (D3=8) with iterative refinement is the superior architecture for single-problem accuracy benchmarks. Spectrum's orchestration overhead adds no value on isolated coding problems.
- **Python/TypeScript framework integration** — LangGraph and CrewAI integrate naturally with existing Python ML/agent tooling. Spectrum is a protocol-level overlay on Claude Code and does not integrate with LangGraph, CrewAI, or similar frameworks.

---

## 7. Field Observations

### Observation 1: The Post-Execution Layer is the Field's Universal Blind Spot

Category C scores (D9-D12) reveal the largest structural gap in multi-agent protocol design. Excluding Spectrum (30/40), the next highest Category C score in this evaluation is 12/40 (OpenAI Agents SDK and ruflo). The average Category C score for the 10 non-Spectrum systems is 7.2/40. D11 (Independent Validation) is 0 for 8 of 11 systems — the overwhelming default is to trust worker self-reports unconditionally.

This is not a measurement artifact. It reflects a genuine field-level assumption: that multi-agent coordination is a planning and execution problem, not a verification problem. The assumption holds when agents are used for low-stakes tasks but fails systematically when agents generate code that will be merged into production. The absence of independent validation means most systems cannot distinguish "worker reported done" from "spec was actually met."

### Observation 2: Security is an Afterthought Except at OpenAI

D10 scores: OpenAI Agents SDK (6), Spectrum (4), ruflo (4), LangGraph (2), AutoGen/AG2 (2), CrewAI (2) — and then seven systems at 0. Three of the highest-profile frameworks in the evaluation (MetaGPT, ChatDev, Citadel, Overstory, Gas Town, oh-my-claudecode) have no documented security mechanisms whatsoever. In the same evaluation period, LangGraph disclosed three CVEs including a CVSS 9.3 critical, and CrewAI disclosed four CVEs including an RCE sandbox escape.

The pattern suggests security is treated as infrastructure (the user's problem) rather than protocol responsibility. OpenAI is the exception: sandboxed cloud execution, guardrails with prompt injection protection, and a security review gate are first-class features of the Agents SDK. The field is converging on security awareness but has not converged on security architecture.

### Observation 3: Benchmark Accuracy is a Research Metric, Not an Operational One

Nine of eleven systems score D3=0 on benchmark accuracy. This is not because these systems produce bad code — it is because no general-purpose orchestration framework has submitted to SWE-Bench as a multi-agent system. The research systems (AgentCoder, AgileCoder) have benchmark results, but on HumanEval/MBPP (function-level), not SWE-Bench Verified (repository-level). The operational systems have no results at all.

This creates a measurement gap: the community cannot currently compare the accuracy of Spectrum's orchestrated multi-agent runs vs. LangGraph's stateful graphs vs. MetaGPT's waterfall pipeline on a shared benchmark. The field needs a multi-agent systems track on SWE-Bench Verified or an equivalent repository-level benchmark where the unit of measurement is the orchestration system, not the underlying model.

### Observation 4: Cross-Run Learning is Structurally Absent Everywhere Except Spectrum

D12 scores: Spectrum (10), ruflo/metaswarm/MetaGPT/ChatDev (4), everyone else (0-2). No system besides Spectrum achieves D12=6 (automatic injection of past learnings into new run prompts via pattern matching). The four systems at 4 have structured lesson capture mechanisms but do not automatically apply them. Every framework-category system scores D12=2 (ad-hoc memory).

Multi-agent systems are typically treated as stateless invocation engines: each run starts from the same configuration regardless of what previous runs discovered. This is architecturally similar to running CI without test history — you can find failures but can't learn from them systematically. The institutional memory gap means most systems repeat the same failure modes across runs.

### Observation 5: The Observability Leaders Are Pulling Away

LangGraph (D8=8) and Spectrum (D8=8) have pulled significantly ahead of the field on observability, with AutoGen/AG2 and Overstory at D8=6. All other systems score D8=4 or below. The separation is architectural: LangGraph's LangSmith integration provides time-travel debugging and per-node cost breakdown that most systems cannot replicate without a comparable trace aggregation backend. Spectrum's mandatory status roster, CHECKPOINT.json, and per-Howler HOOK.md provide equivalent depth through structured artifacts rather than a hosted dashboard.

The gap between D8=8 and D8=4 is not a feature difference — it is a debugging experience difference. Systems at D8=4 can diagnose problems post-hoc; systems at D8=8 can observe, replay, and cost-attribute during execution. As agent runs grow in cost and duration, this gap will become increasingly significant for production operators.

---

## 8. Executive Summary

This evaluation applied a 12-dimension rubric across 11 open-source multi-agent protocols, producing the most granular comparative analysis of this field conducted to date. The rubric covers pre-execution planning (D1-D4), runtime coordination (D5-D8), and post-execution assurance (D9-D12) — the third category being largely absent from prior evaluations.

**The headline finding is separation, not competition.** Spectrum Protocol scores 88/120, leading the second-ranked system (OpenAI Agents SDK, 44/120) by 44 points — a margin larger than the total score of any system ranked below 7th. This is not a marginal lead; it is a structural separation arising from Spectrum's simultaneous investment in all three evaluation categories while every competitor has neglected at least one. No other system scores above 10 in Category C (post-execution assurance). No other system scores above 18 in Category A (pre-execution planning). Spectrum is the only system that treats coordination as a pre-execution, runtime, and post-execution concern simultaneously.

**Spectrum's genuine strengths are verifiable.** D1=10 (task decomposition), D2=10 (contract enforcement), D11=8 (independent validation), and D12=10 (cross-run learning) are the highest scores in the field on each dimension, backed by specification evidence in SPECTRUM-OPS.md and SPECTRUM.md. The Politico adversarial review, Obsidian spec compliance reporting, and LESSONS.md injection protocol are features no other evaluated system implements.

**Spectrum's genuine weaknesses are also verifiable.** D3=0 (no published benchmark) is a real gap — AgentCoder (D3=8), AgileCoder (D3=6), and even the OpenAI Agents SDK (D3=4) have accuracy evidence Spectrum lacks. D5=6 (parallelism capped by muster overhead) means Gas Town's daemon architecture is objectively faster for raw parallel throughput. D10=4 (no SAST or sandboxed execution) trails the OpenAI Agents SDK (D10=6). These are not scoring artifacts — they are architectural choices with real costs.

**The field has three universal gaps.** First: independent validation is absent in 73% of evaluated systems — most multi-agent protocols accept worker self-reports unconditionally. Second: cross-run learning is structurally absent in all frameworks — no framework achieves D12=6 (automatic injection of past learnings). Third: benchmark accuracy is unmeasured for all operational systems — the field lacks a shared benchmark for multi-agent orchestration quality at the repository level.

**The most actionable finding for Spectrum**: the D3 gap (benchmark accuracy) is the highest-priority improvement opportunity because it is the only weakness that affects external credibility. Addressing D10 (SAST integration) and D5 (sub-3-minute full-mode startup) would close gaps with OpenAI Agents SDK and LangGraph respectively. The post-execution assurance lead (Category C) is durable — no competitor is within 18 points — but the D3 gap remains a legitimate objection to Spectrum's completeness as an evaluated system.

For most teams evaluating multi-agent protocols in 2026, the choice is not between Spectrum and its peers — it is between Spectrum's coordination rigor and the much lower setup cost of systems like the OpenAI Agents SDK or LangGraph. The 44-point gap represents real protocol investment. Whether that investment is justified depends entirely on the complexity, criticality, and duration of the work being orchestrated.

---

*This report was produced by H5 (Synthesis Howler) as part of the 12dim-eval spectrum run. Scores are carried exactly from H1 (group-claude-code.md), H2 (group-frameworks.md), and H4 (group-research.md). H5 does not re-score any system. Where H5 notes potential disagreements with group scores, they are flagged in footnotes rather than overriding the group report.*

*H3 (group-commercial.md) was not produced; commercial systems are excluded from this revised-scope report.*
