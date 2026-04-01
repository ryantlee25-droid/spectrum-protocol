# COMPETITIVE-AUDIT.md — 2026 Multi-Agent Coding Systems Audit
**Spectrum**: audit-2026-0331
**Howler**: H5-synthesis
**Date**: 2026-03-31
**Rubric version**: evaluation/audit-2026/RUBRIC.md v1.0

---

## Executive Summary

*(See Step 6 below for the full 300–400 word summary.)*

---

## Step 1 — Top 15 Selection

See `TOP15-RANKING.md` for complete inclusion/exclusion rationale. The 15 selected systems are: Citadel, Gas Town, LangGraph, Overstory, metaswarm, CrewAI, Factory, OpenAI Agents SDK, Augment Code/Intent, Devin, Cursor agents, Agent Teams (Anthropic), oh-my-claudecode, AutoGen/AG2, and GitHub Copilot Workspace.

Excluded: MetaGPT, ChatDev, CAMEL-AI, Amazon Q Developer, Windsurf (rationale in TOP15-RANKING.md).

---

## Step 2 — Unified Scoring Table

Scores carried forward exactly from group reports (H2, H3, H4). No re-scoring by H5. Conflict flag: no system appears in more than one group report — no score conflicts detected.

| System | D1 Cost | D2 Speed | D3 Accuracy | D4 Workflow Rigor | D5 Observability | D6 Recovery | D7 Setup | D8 Scalability | Total |
|--------|---------|----------|-------------|-------------------|------------------|-------------|----------|----------------|-------|
| **Spectrum Protocol** | **2** | **3** | **2** | **5** | **3** | **4** | **3** | **3** | **25** |
| Citadel | 3 | 4 | 2 | 4 | 3 | 4 | 4 | 3 | 27 |
| Gas Town | 3 | 5 | 2 | 3 | 3 | 3 | 2 | 5 | 26 |
| LangGraph | 4 | 3 | 2 | 3 | 5 | 3 | 3 | 3 | 26 |
| Overstory | 3 | 4 | 2 | 3 | 4 | 3 | 3 | 4 | 26 |
| metaswarm | 3 | 3 | 2 | 4 | 2 | 4 | 3 | 3 | 24 |
| CrewAI | 4 | 4 | 2 | 2 | 3 | 2 | 4 | 3 | 24 |
| Factory | 3 | 3 | 3 | 3 | 3 | 2 | 4 | 3 | 24 |
| OpenAI Agents SDK | 4 | 3 | 2 | 2 | 4 | 2 | 5 | 3 | 25 |
| Augment Code/Intent | 2 | 3 | 4 | 3 | 2 | 2 | 4 | 3 | 23 |
| Devin | 2 | 4 | 2 | 2 | 3 | 2 | 5 | 3 | 23 |
| Cursor agents | 2 | 4 | 3 | 2 | 2 | 2 | 5 | 3 | 23 |
| Agent Teams (Anthropic) | 3 | 4 | 3 | 2 | 2 | 2 | 4 | 3 | 23 |
| oh-my-claudecode | 3 | 4 | 2 | 2 | 2 | 2 | 5 | 3 | 23 |
| AutoGen / AG2 | 4 | 3 | 2 | 2 | 3 | 2 | 3 | 3 | 22 |
| GitHub Copilot Workspace | 3 | 2 | 4 | 2 | 3 | 2 | 5 | 1 | 22 |

**Dimension key**: D1=Cost (5=cheapest), D2=Speed, D3=Accuracy, D4=Workflow Rigor, D5=Observability, D6=Recovery, D7=Setup (5=easiest), D8=Scalability

**Source reports**: group-claude-code.md (H2), group-frameworks.md (H3), group-commercial.md (H4)

---

## Step 3 — Closest Competitors Analysis

### Euclidean Distance from Spectrum

Normalized to 0–1 per CONTRACT.md §6: `(score − 1) / 4`. Distance = √Σ(Δ_dim²).

| Rank | System | Distance | Notes |
|------|--------|----------|-------|
| 1 | **metaswarm** | **0.433** | Closest competitor |
| 2 | **Citadel** | **0.500** | Second closest |
| 3 | **Overstory** | **0.750** | Third closest |
| 4 | Factory | 0.829 | — |
| 5 | LangGraph | 0.901 | — |
| 6 | Augment Code/Intent | 0.935 | — |
| 7 | Gas Town | 0.968 | — |
| 7 | MetaGPT* | 0.968 | *excluded from Top 15 |
| 9 | AutoGen/AG2 | 1.031 | — |
| 10 | Agent Teams | 1.061 | — |

---

### Closest Competitor #1: metaswarm (distance 0.433)

**Dimension comparison:**

| Dimension | Spectrum | metaswarm | Delta |
|-----------|----------|-----------|-------|
| D1 Cost | 2 | 3 | metaswarm +1 |
| D2 Speed | 3 | 3 | same |
| D3 Accuracy | 2 | 2 | same |
| D4 Workflow Rigor | **5** | 4 | Spectrum +1 |
| D5 Observability | 3 | **2** | Spectrum +1 |
| D6 Recovery | 4 | 4 | same |
| D7 Setup | 3 | 3 | same |
| D8 Scalability | 3 | 3 | same |

**Why they're close**: metaswarm and Spectrum occupy nearly identical positions on speed, accuracy, setup, and scalability. Both are mid-tier coordination-heavy frameworks that trade raw throughput for workflow discipline. Both score 4 on recovery (automated retry with escalation, persisted failure state), an unusual characteristic absent from most competitors.

**Key divergence**: Spectrum scores 5 on D4 (Workflow Rigor) vs. metaswarm's 4. The gap is the absence of a formal failure taxonomy in metaswarm — its retry path is a single "fix, re-validate, fresh reviewer, retry 3 times" loop, regardless of failure type. Spectrum distinguishes 5 failure types (transient/logical/structural/environmental/conflict) with distinct handling for each. metaswarm's D5 (Observability) is lower (2 vs. 3) because it has no documented mid-execution dashboard or per-agent log export, while Spectrum's mandatory status roster and HOOK.md files provide structured per-agent attribution.

**Developer trade-off**: A developer choosing metaswarm over Spectrum gets slightly lower cost (D1=3 vs. 2, meaningful on a project budget), equivalent speed and scalability, and nearly equivalent recovery rigor — while giving up Spectrum's formal failure taxonomy and the Politico adversarial review phase. metaswarm's TDD enforcement and mandatory 100% coverage gate are stronger coded constraints than Spectrum's quality gates, which are LLM-instruction-enforced rather than machine-verified. A developer who wants enforced test coverage and a simpler cognitive model should prefer metaswarm. A developer managing a large parallel run where failure classification matters (production incident, costly re-run) should prefer Spectrum.

---

### Closest Competitor #2: Citadel (distance 0.500)

**Dimension comparison:**

| Dimension | Spectrum | Citadel | Delta |
|-----------|----------|---------|-------|
| D1 Cost | 2 | **3** | Citadel +1 |
| D2 Speed | 3 | **4** | Citadel +1 |
| D3 Accuracy | 2 | 2 | same |
| D4 Workflow Rigor | **5** | 4 | Spectrum +1 |
| D5 Observability | 3 | 3 | same |
| D6 Recovery | 4 | 4 | same |
| D7 Setup | 3 | **4** | Citadel +1 |
| D8 Scalability | 3 | 3 | same |

**Why they're close**: Citadel and Spectrum are the two most rigor-conscious systems in the Claude Code ecosystem. Both have: circuit breakers, campaign/HOOK.md state persistence, and multi-tier recovery. Both scored 4 on recovery — the only two systems in the top 15 to do so alongside metaswarm. Spectrum's README explicitly acknowledges Citadel in its acknowledgments ("machine-verifiable phase conditions"), marking a direct intellectual lineage.

**Key divergence**: Citadel is faster (D2=4 vs. 3) and easier to set up (D7=4 vs. 3). Citadel's plugin-based architecture removes the manual muster ceremony that adds overhead to every Spectrum run. On D4, Spectrum scores higher because it documents all four rigor components (pre-execution contracts, failure taxonomy, circuit breaker, independent adversarial review); Citadel's adversarial review analog is not documented in available sources, and its failure taxonomy is implicit rather than formal. Both lack published accuracy benchmarks (D3=2).

**Developer trade-off**: A developer choosing Citadel over Spectrum gets faster startup, lower cost, and plugin-based installation (no manual file configuration). They give up Spectrum's Politico adversarial review phase and its formal 5-tier failure taxonomy. Citadel's "machine-verifiable phase conditions" claim suggests stronger mechanistic enforcement than Spectrum's LLM-instruction-enforced rules — if that claim is substantiated, it would reverse the D4 comparison. The evidence does not yet support this reversal.

---

### Closest Competitor #3: Overstory (distance 0.750)

**Dimension comparison:**

| Dimension | Spectrum | Overstory | Delta |
|-----------|----------|-----------|-------|
| D1 Cost | 2 | **3** | Overstory +1 |
| D2 Speed | 3 | **4** | Overstory +1 |
| D3 Accuracy | 2 | 2 | same |
| D4 Workflow Rigor | **5** | 3 | Spectrum +2 |
| D5 Observability | 3 | **4** | Overstory +1 |
| D6 Recovery | **4** | 3 | Spectrum +1 |
| D7 Setup | 3 | 3 | same |
| D8 Scalability | 3 | **4** | Overstory +1 |

**Why they're close**: Overstory and Spectrum share the same philosophy of durable, observable, coordination-heavy agent execution — both require understanding a significant framework before the first productive run. Both score 2 on accuracy (no benchmark) and 3 on setup. The tiered watchdog in Overstory (Tier 0 mechanical, Tier 1 AI-triage, Tier 2 monitor) echoes Spectrum's Gold oversight role in spirit.

**Key divergence**: The largest gap is D4 (Workflow Rigor: 5 vs. 3). Overstory has instruction overlays, a FIFO merge queue, and typed protocol messages, but lacks pre-execution interface contracts (analogous to Spectrum's CONTRACT.md) and a formal failure taxonomy with distinct handling paths. On D5, Overstory scores higher (4 vs. 3) because its `trace` command provides timeline replay capability that Spectrum's status roster does not. On D8, Overstory scores higher (4 vs. 3) because its pull-based tmux architecture with SQLite WAL messaging is architecturally similar to Gas Town's design, positioning it for 6-8+ agents; Spectrum's documented 8-agent ceiling is explicitly stated in SPECTRUM-OPS.md.

**Developer trade-off**: Overstory is cheaper, faster, more observable, and more scalable than Spectrum. It gives up Spectrum's formal contract enforcement and failure taxonomy. A developer who values seeing what agents are doing (D5=4 trace command, per-agent cost breakdown) over having formally classified failure recovery should choose Overstory.

---

## Step 4 — Spectrum: Honest Strengths and Weaknesses

*This section treats Spectrum as a competitor under evaluation, not as the reference system. Scores and competitor comparisons are drawn from the unified scoring table above.*

---

### Genuine Strengths

**D4 Workflow Rigor — Score 5, sole leader in the field**

Spectrum is the only system in this audit that documents all four D4 components as enforced protocol elements: (a) pre-execution CONTRACT.md with file ownership matrix — every file assigned exactly once, enforced at muster and verified by a dedicated adversarial agent (Politico); (b) formal failure taxonomy with 5 distinct types (transient, logical, structural, environmental, conflict) each with a distinct handling path (Resume/Retry/Skip/Restructure); (c) circuit breaker — 2 failures on the same locus auto-escalates to structural, Gold pauses and escalates to human; (d) independent adversarial review — Politico challenges CONTRACT.md and MANIFEST.md before any Howler is dropped, with no blockers permitted at freeze. The next-closest systems are Citadel (D4=4) and metaswarm (D4=4). The gap between Spectrum and the field on this dimension is not marginal — no other system documents the adversarial pre-execution review phase at all.

Caveat from H2: "enforced by the framework for a CLAUDE.md-based protocol means enforcement is via LLM instruction adherence, not machine verification." This is a genuine qualifier on the D4=5 score — the rigor is documented, not mechanistically guaranteed.

**D6 Recovery — Score 4, tied for highest in the field with metaswarm and Citadel**

Spectrum's 5-tier failure taxonomy with automated recovery for transient failures, HOOK.md-persisted failure state, and a documented circuit breaker places it in the top tier of recovery sophistication. No system in the commercial group reaches D6=4 — all commercial systems score D6=2. For runs where failure recovery quality matters (large parallel execution, expensive re-runs), Spectrum's recovery architecture is a genuine differentiator relative to competitors like Gas Town (D6=3), LangGraph (D6=3), and all commercial systems.

**D4 + D6 as a combined strength**

The combination of the highest workflow rigor and top-tier recovery is unique to Spectrum in this field. Citadel and metaswarm each achieve D4=4 and D6=4 but not D4=5. This pairing is the core of Spectrum's value proposition: for high-stakes parallel coding runs where failure is expensive and conflicts are costly, Spectrum's formal discipline is not matched by any competitor.

---

### Genuine Weaknesses

**D1 Cost — Score 2, the lowest score in the field for open-source systems**

Spectrum scores 2 on cost — tied with Devin, Cursor agents, and Augment Code/Intent, which are commercial products with per-seat or per-ACU billing. For an open-source protocol, this is a significant disadvantage. The documented cause (Spectrum README §Token Costs): a 5-Howler full run costs approximately $9.43; an 8-Howler full run costs approximately $15.20. Every system in the Claude Code ecosystem group (Gas Town, oh-my-claudecode, Agent Teams, Citadel, metaswarm, Overstory) scores D1=3, meaning Spectrum is the only open-source Claude Code ecosystem system at D1=2. The muster ceremony — which includes a Gold (Opus) phase, Politico adversarial review, and mandatory human approval gate before any Howlers drop — is the structural cause of this cost premium. There is no workaround within full-mode Spectrum: the muster overhead is the feature.

Reaping mode reduces cost (documented at ~$4.80 for 3-Howler reaping), but reaping mode omits ARCHITECTURE.md, full DAG, per-Howler Design-by-Contract, Obsidian, and ENTITIES.md updates — i.e., the components that distinguish Spectrum from less rigorous systems.

**D2 Speed — Score 3, behind Gas Town (5), oh-my-claudecode (4), Citadel (4), Overstory (4), and Agent Teams (4)**

Spectrum's 3-minute reaping muster and 8-minute full muster add wall-clock overhead before any Howler executes. The mandatory human approval gate before Howler drop is additional structural serialization absent from every competitor except GitHub Copilot Workspace. Gas Town's GUPP (Go Until a Problem Presents) principle eliminates the muster gate entirely — agents start immediately. Citadel's plugin architecture eliminates the manual muster ceremony. For tasks where wall-clock time matters, Spectrum is categorically slower to start than four of its closest competitors. This is not a configuration issue — the muster phase is load-bearing for the rigor that makes D4=5 possible.

**D7 Setup — Score 3, behind oh-my-claudecode (5), OpenAI Agents SDK (5), Devin (5), Cursor agents (5), GitHub Copilot Workspace (5)**

SPECTRUM-OPS.md is ~550 lines. SPECTRUM.md is ~2,300 lines. The README acknowledges this directly: "Not For: Zero-config quick start — use oh-my-claudecode." Five systems in the Top 15 score D7=5. Spectrum's documentation burden is inherent to the protocol's complexity — a developer cannot use Spectrum effectively without understanding the muster/Howler/Gold/Politico hierarchy. No shortcut exists.

**D3 Accuracy — Score 2, tied for last with Gas Town, oh-my-claudecode, LangGraph, metaswarm, Overstory, Devin, Windsurf, and CAMEL-AI (excluded)**

No published SWE-Bench result exists for Spectrum Protocol. The D3=2 score applies the rubric's missing-evidence rule: no benchmark data → score 2 with LOW CONFIDENCE flag. Spectrum's coordination rigor may improve accuracy on multi-file parallel coding tasks relative to uncoordinated systems, but this hypothesis has not been tested or published. Augment Code/Intent (D3=4, 70.6% SWE-bench), GitHub Copilot Workspace (D3=4, 55-56% SWE-bench), Amazon Q Developer (D3=4, 66% SWE-bench, April 2025), and Cursor agents (D3=3) all score higher on accuracy with published or community evidence. Spectrum cannot claim competitive accuracy without a published evaluation.

**D8 Scalability — Score 3, behind Gas Town (5) and Overstory (4)**

Spectrum's SPECTRUM-OPS.md explicitly states: "Max 8 parallel Howlers — more than this and coordination overhead dominates." The README states "Not For: 20+ agents at scale — use Gas Town." This is an honest acknowledgment in the documentation, but it means Spectrum cannot compete with Gas Town for large-scale parallel execution. At 20+ agents, Spectrum is not the right tool by its own admission.

---

### Use Cases Where Spectrum Is the Wrong Choice

1. **Time-critical work where startup latency matters**: The 3-8 minute muster plus mandatory human approval gate makes Spectrum unsuitable for quick-turn tasks. Use oh-my-claudecode or Agent Teams.

2. **Developers who want zero-configuration**: Spectrum requires understanding 7 protocol phases, multiple agent roles, HOOK.md format, CHECKPOINT.json schema, and CONTRACT.md conventions before the first productive run. Use oh-my-claudecode or OpenAI Agents SDK.

3. **Teams on tight token budgets**: $9.43 for a 5-Howler run exceeds what most open-source alternatives cost. Use Gas Town, Citadel, or any D1=3+ system for equivalent or higher throughput at lower cost.

4. **Large-scale (20+ agent) parallel execution**: Spectrum explicitly cedes this to Gas Town. The 8-agent ceiling is design-enforced.

5. **Teams that need published accuracy guarantees**: No SWE-Bench result. Teams evaluating systems on benchmark evidence cannot place Spectrum in the top tier for accuracy.

---

### Use Cases Where Spectrum Is the Right Choice

1. **High-stakes parallel coding where conflicts are expensive**: The CONTRACT.md + file ownership matrix + Politico adversarial review prevents the most common class of multi-agent failures (conflicting file modifications, interface mismatches) before they happen. No other system in this audit provides a Politico-equivalent pre-execution adversarial review.

2. **Runs where failure recovery cost is high**: The formal 5-tier failure taxonomy and HOOK.md-persisted state enable resuming a failed run from exactly where it broke, with failure context preserved. This is superior to any commercial system (all at D6=2) and matches only Citadel and metaswarm among open-source alternatives.

3. **Developers who need auditable coordination**: CHECKPOINT.json, HOOK.md, MANIFEST.md, CONTRACT.md, and the status roster create a full paper trail. For team environments or audit requirements, Spectrum produces more structured coordination artifacts than any competing system.

4. **3-8 agent coding tasks of medium complexity**: The DAG-based dispatch and per-Howler scope management is well-suited to features spanning 3-8 logical components with clear interface boundaries. This is the sweet spot explicitly documented in the README.

---

## Step 5 — Recommendations

### Recommendation 1: Implement a lightweight pre-flight mode to address D2 Speed and D7 Setup

**Dimension addressed**: D2 Speed (Spectrum=3; Citadel=4, Gas Town=5, oh-my-claudecode=4)
**Competitor reference**: Citadel's plugin architecture demonstrates that muster ceremony overhead can be reduced to near-zero for well-understood task types. oh-my-claudecode demonstrates that zero-config parallel execution is achievable.

**Action**: Define a `nano` mode below reaping mode — for 2-3 Howler runs with obvious task boundaries, allow Gold to generate only a LIGHT-MANIFEST.md (task list + file ownership, no ARCHITECTURE.md, no CONTRACT.md, no Politico) with automatic approval. This trades rigor for speed on small runs. Reaping mode already moves in this direction; nano mode would complete the continuum. The key constraint: nano mode must include file ownership to prevent the primary failure mode (overlapping file edits). Without ownership tracking, it is indistinguishable from oh-my-claudecode with extra steps.

---

### Recommendation 2: Publish a SWE-Bench evaluation to address D3 Accuracy

**Dimension addressed**: D3 Accuracy (Spectrum=2; Augment Code/Intent=4, GitHub Copilot Workspace=4, Amazon Q Developer=4, Cursor agents=3)
**Competitor reference**: Augment Code's 70.6% SWE-bench Verified is the highest in this audit. GitHub Copilot Workspace publishes 55-56%. Amazon Q Developer published 66% (April 2025). All three commercial systems used SWE-bench as their primary accuracy signal.

**Action**: Run Spectrum against SWE-bench Verified on a representative sample of tasks (even a 50-task subset is publishable). Spectrum's coordination rigor hypothesis — that pre-execution contracts reduce specification drift and therefore improve accuracy on multi-file tasks — should be testable. If the result is below competitors, that is useful signal for where accuracy investment is needed. If above, it closes the largest open question about Spectrum's value proposition. A D3=2 (no benchmark data) next to Augment Code's D3=4 (70.6% SWE-bench) is the most damaging gap for Spectrum's credibility in competitive comparison.

---

### Recommendation 3: Reduce cost for the Gold/Politico muster phase to address D1 Cost

**Dimension addressed**: D1 Cost (Spectrum=2; every open-source competitor in this audit scores D1=3 or higher)
**Competitor reference**: Gas Town, Citadel, metaswarm, Overstory, CrewAI, LangGraph all score D1=3+ without platform fees. Spectrum's D1=2 is driven by the muster phase cost (Gold=Opus for full mode, Politico=Sonnet adversarial review), not Howler execution.

**Action**: The CLAUDE.md model assignments already moved Gold from Opus to Sonnet (gold-eval-0331 found 0.94 composite at 91% cost reduction). Apply the same evaluation to Politico: can a Haiku-class model perform effective adversarial review of CONTRACT.md and MANIFEST.md, given that the review criteria are well-specified? If Politico can be downgraded to Haiku, and if muster overhead can be further reduced for full-mode runs, Spectrum could reach D1=3 on a representative 5-Howler run. The README should also update its cost table to reflect the current Sonnet-Gold configuration, as the $9.43 estimate may be stale if it was calculated under Opus-Gold.

---

### Recommendation 4: Add a structured log export / observability integration to address D5 Observability

**Dimension addressed**: D5 Observability (Spectrum=3; LangGraph=5, OpenAI Agents SDK=4, Overstory=4)
**Competitor reference**: LangGraph's LangSmith integration provides real-time dashboard, time-travel debugging, and structured trace export — the D5=5 reference implementation. Overstory's `trace` command provides timeline replay. OpenAI Agents SDK provides full tracing to the OpenAI backend out of the box.

**Action**: Spectrum currently provides structured per-agent state via HOOK.md and CHECKPOINT.json, and console-printed status rosters. These are file-based structured logs, not streaming observability. Adding OpenTelemetry trace emission from the CHECKPOINT.json write step (one span per Howler state transition) would enable integration with any OTEL-compatible backend (Jaeger, Honeycomb, LangSmith) without adding infrastructure dependencies. This moves Spectrum from D5=3 to D5=4 if real-time OTEL dashboard integration is achieved, and closes the gap with LangGraph's observability advantage.

---

### Recommendation 5: Define and document a maximum per-run cost budget enforcement mechanism to address D1 Cost perception

**Dimension addressed**: D1 Cost (Spectrum=2; community perception)
**Competitor reference**: Citadel documents native cost accounting per session, campaign, and agent. Spectrum's README mentions `cost_tracking.budget_limit` in CHECKPOINT.json as a feature, but the enforcement mechanism is described as manual: "Gold checks cumulative cost before each Howler drop."

**Action**: Automate budget limit enforcement: if `cost_tracking.budget_limit` is set and the projected total exceeds it, Gold halts automatically without requiring a human prompt — and presents a structured options menu (Reduce Howler count / Switch to reaping mode / Proceed). This directly addresses the D1 cost concern not by reducing cost but by giving users control over unexpected cost escalation — a frequent pain point in community reports about multi-agent tools (referenced in Cursor agents and Devin evidence notes). A budget-controlled run is more predictable than a run with manual cost checking.

---

## Step 6 — Executive Summary

Multi-agent coding systems have fragmented into three distinct architectural philosophies. Commercial IDE tools (Cursor, Devin, GitHub Copilot Workspace, Augment Code) optimize for developer experience and accuracy benchmarks, with Augment Code/Intent leading on SWE-bench Verified at 70.6%. General-purpose frameworks (LangGraph, CrewAI, OpenAI Agents SDK) offer flexibility and ecosystem reach, with LangGraph's LangSmith integration providing the strongest observability in the field. Specialist coordination protocols (Spectrum, Citadel, metaswarm, Gas Town) compete on workflow discipline and parallel execution safety.

Spectrum's three closest competitors by Euclidean distance on the 8-dimension scoring vector are **metaswarm** (distance 0.433), **Citadel** (0.500), and **Overstory** (0.750). All three are Claude Code ecosystem systems that share Spectrum's combination of structured coordination and parallel worktree execution. The proximity reflects genuine architectural similarity, not superficial resemblance: metaswarm matches Spectrum on 5 of 8 dimensions exactly (speed, accuracy, setup, recovery, scalability); Citadel matches on 4 (accuracy, observability, recovery, scalability).

Spectrum's genuine differentiators are its D4 Workflow Rigor score of 5 — the sole top score in this dimension across all 16 systems — and its D6 Recovery score of 4, tied only with Citadel and metaswarm. The adversarial Politico review phase, formal 5-tier failure taxonomy, and HOOK.md-persisted failure state have no equivalent in any other system in this audit. For high-stakes parallel coding runs where conflicts are expensive and failure recovery cost is high, Spectrum is the most rigorously documented coordination protocol available.

Spectrum's genuine limitations are equally clear. Its D1 Cost score of 2 makes it the most expensive open-source system in this audit — a 5-Howler full run costs approximately $9.43 in documented estimates, compared to D1=3 for every other open-source Claude Code ecosystem system. Its D2 Speed score of 3 reflects the muster phase's 3-8 minute startup overhead plus the mandatory human approval gate, placing it behind Gas Town (D2=5), Citadel (D2=4), Overstory (D2=4), and oh-my-claudecode (D2=4) on time-to-first-Howler. It has no published SWE-Bench score (D3=2), leaving its accuracy claim unverifiable relative to Augment Code, GitHub Copilot Workspace, and Amazon Q Developer, all of which publish benchmark results. And its 8-agent ceiling is explicitly documented — it is not the right tool for 20+ agent runs.

Spectrum is the correct choice when: multi-file conflicts are expensive, failure classification matters, a full audit trail is required, and the task complexity justifies a 3-8 minute coordination investment before execution begins. It is the wrong choice when: startup time is constrained, token budget is tight, a published accuracy guarantee is required, or more than 8 parallel agents are needed.

The five highest-priority improvements identified from this audit are: (1) a nano-mode below reaping to reduce startup overhead for small runs; (2) a SWE-Bench evaluation to close the D3 gap; (3) cost reduction in the muster phase (Politico model evaluation for downgrade); (4) OpenTelemetry integration to match LangGraph's observability advantage; and (5) automated budget enforcement to reduce cost unpredictability.

---

*All scores carried forward from group-claude-code.md (H2), group-frameworks.md (H3), group-commercial.md (H4) without modification. No conflicts detected (no system appeared in multiple group reports). Euclidean distances computed using normalized 0–1 values per CONTRACT.md §6.*
