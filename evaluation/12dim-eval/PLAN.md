# PLAN.md — 12-Dimension Multi-Agent Protocol Evaluation
**Blue**: 12dim-eval
**Date**: 2026-03-31
**Prior evaluations**: evaluation/audit-2026/COMPETITIVE-AUDIT.md, evaluation/eval-v2/COMPETITIVE-EVAL-V2.md
**Rubric version**: 12dim-v1.0

---

## Purpose

This evaluation applies a 12-dimension rubric across 21 multi-agent systems to produce a unified competitive analysis. The 12 dimensions extend prior 8-dimension evaluations (audit-2026, eval-v2) by splitting each existing cluster and adding four new dimensions in the post-execution category that prior audits left underdeveloped.

**New vs. prior coverage:**
- D1-D4 (Category A) replace and refine prior D1/D7/D4/D3
- D5-D8 (Category B) replace and refine prior D2/D5/D6/D8
- D9-D12 (Category C) are net-new: prior evaluations had no dedicated post-execution category

---

## Systems Under Evaluation (21 total)

### Group H1 — Claude Code Ecosystem (8 systems)
1. Spectrum Protocol
2. Gas Town
3. oh-my-claudecode
4. Agent Teams (Anthropic)
5. Citadel
6. metaswarm
7. Overstory
8. ruflo

### Group H2 — General-Purpose Frameworks (6 systems)
9. CrewAI
10. LangGraph
11. MetaGPT
12. AutoGen / AG2
13. OpenAI Agents SDK
14. ChatDev

### Group H3 — Commercial / IDE (5 systems)
15. Devin
16. Cursor agents
17. Augment Code / Intent
18. GitHub Copilot Workspace
19. Factory

### Group H4 — Research Systems (2 systems)
20. AgentCoder
21. AgileCoder

---

## Execution Structure (Reaping Mode)

Five Howlers, all pure-create (no MODIFIES), no shared interfaces at drop time. H5 runs sequentially after H1-H4.

| Howler | Group | Systems | Output File | Mode | Suggested Model |
|--------|-------|---------|-------------|------|-----------------|
| H1 | Claude Code Ecosystem | 8 (Spectrum scored as peer) | group-claude-code.md | parallel | Opus (depth required — Spectrum scored as peer here) |
| H2 | General-Purpose Frameworks | 6 | group-frameworks.md | parallel | Sonnet |
| H3 | Commercial / IDE | 5 | group-commercial.md | parallel | Sonnet |
| H4 | Research Systems | 2 | group-research.md | parallel | Sonnet (small, fast) |
| H5 | Synthesis & Report | all 21 | EVALUATION-REPORT.md | **sequential after H1-H4** | Sonnet |

**File ownership matrix:**

| File | Howler |
|------|--------|
| `evaluation/12dim-eval/group-claude-code.md` | H1 |
| `evaluation/12dim-eval/group-frameworks.md` | H2 |
| `evaluation/12dim-eval/group-commercial.md` | H3 |
| `evaluation/12dim-eval/group-research.md` | H4 |
| `evaluation/12dim-eval/EVALUATION-REPORT.md` | H5 |
| `evaluation/12dim-eval/PLAN.md` | Blue (this file, read-only for Howlers) |

No file appears in more than one Howler's scope. H5 reads all four group files as inputs; it does not modify them.

---

## DAG

```
H1 ──┐
H2 ──┤
     ├──► H5 (synthesis)
H3 ──┤
H4 ──┘
```

H1, H2, H3, H4 are fully parallel. H5 depends on all four completing.

---

## Impartiality Rules (Mandatory for all Howlers)

These rules apply without exception to every system including Spectrum Protocol:

1. **Score from specification only.** Evidence must be drawn from public documentation, protocol files, published benchmarks, or verifiable community sources. Marketing claims without specification backing score no higher than the "claimed but unverified" tier.

2. **Spectrum is a peer.** Spectrum Protocol is scored identically to every other system using the same rubric. No preferential treatment for hosting project context. Howler H1 scores Spectrum alongside Gas Town, Citadel, etc. using the same evidence standard.

3. **Even scores only.** Valid scores: 0, 2, 4, 6, 8, 10. No odd numbers. No half-points.

4. **Document evidence for every score.** Every dimension score must have a 1-3 sentence evidence citation naming the source (file path, URL, or document name). Scores without evidence are invalid.

5. **Low confidence flag.** If evidence is absent or ambiguous, score conservatively and append `[LOW CONFIDENCE]` to the score line. Do not inflate scores where evidence is missing.

6. **No interpolation from adjacent dimensions.** A system's strength in D1 does not imply strength in D2. Score each dimension independently.

7. **Rubric anchor precedence.** The rubric anchor descriptions in this PLAN.md are authoritative. If a system's behavior is ambiguous relative to an anchor, choose the lower score.

8. **Prior eval scores are reference, not binding.** The audit-2026 and eval-v2 scores may be cited as starting points but must be re-evaluated against this 12-dimension rubric. Dimension definitions differ.

---

## Evidence Requirements Per Howler

For each system, Howlers must:

1. **Name the source** for each score. Acceptable sources:
   - Public GitHub repository (link or file path)
   - Official documentation URL
   - Published benchmark result with citation
   - Protocol specification file (for Spectrum: `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md`, `SPECTRUM.md`, `CLAUDE.md`)
   - Prior audit findings (audit-2026, eval-v2) — usable as reference, must be re-verified against rubric

2. **Quote or paraphrase the specification evidence.** A 1-2 sentence excerpt or paraphrase from the source document is required for scores of 6, 8, or 10. Lower scores may use absence-of-evidence as justification.

3. **Flag unknowns explicitly.** If a dimension cannot be assessed for a system (e.g., a commercial system with no published architecture), write `UNKNOWN — no public specification` and score 0 or 2 depending on what can be inferred.

---

## 12-Dimension Rubric (Full Specification)

This rubric is the authoritative scoring reference. All Howlers use this version. Do not derive dimensions from prior evaluations.

---

### Category A: Pre-Execution Planning (D1–D4)

**Definition**: What the system does *before* any worker agent begins execution — planning, contract enforcement, decomposition, and accuracy baselines.

---

#### D1 — Task Decomposition Quality

*Does the system provide structured mechanisms for breaking work into parallel or sequential subtasks with explicit scope, dependencies, and ownership?*

| Score | Anchor |
|-------|--------|
| 0 | No decomposition support. Work is dispatched as a single monolithic prompt. |
| 2 | Basic splitting. Work can be divided into subtasks, but no formal ownership, dependency graph, or scope specification. |
| 4 | Structured decomposition. Tasks have defined scope statements and a dependency ordering. File or resource ownership is implied but not formally enforced. |
| 6 | Formal decomposition. Explicit file/resource ownership matrix. Dependency graph (DAG or equivalent). Scope statements per worker. Human review of decomposition before execution. |
| 8 | Formal decomposition + hazard scan. Above, plus an explicit pre-decomposition hazard analysis (integration bottlenecks, serial risks, effort estimation). Decomposition artifacts are versioned. |
| 10 | Full Design-by-Contract decomposition. Above, plus per-worker preconditions/postconditions/invariants (DbC). Adversarial review of decomposition by a dedicated independent agent before freeze. Zero-overlap guarantee mechanically verified. |

---

#### D2 — Interface Contract Enforcement

*Does the system define and enforce contracts for how workers interact — types, interfaces, naming conventions, integration points — before execution begins?*

| Score | Anchor |
|-------|--------|
| 0 | No contracts. Workers share no formal interface agreements. |
| 2 | Informal conventions. Shared patterns exist in documentation or prompts, but are not formally specified or enforced. |
| 4 | Shared type definitions. A shared types file or interface document exists. Workers are expected to follow it, but compliance is not verified. |
| 6 | Frozen contracts. A formal CONTRACT.md or equivalent is written before workers start. Workers may not modify it. Violations require escalation. |
| 8 | Frozen contracts + factual verification. Above, plus a pre-freeze accuracy check verifying all referenced files exist and documented signatures match the actual codebase. |
| 10 | Frozen contracts + factual verification + adversarial review. Above, plus an independent adversarial agent challenges the contract for ambiguities, gaps, and decomposition flaws before freeze. Contract deviations require formal AMENDMENT.md. |

---

#### D3 — Benchmark Accuracy

*What is the system's documented accuracy on standardized coding benchmarks (SWE-Bench Verified or equivalent)?*

| Score | Anchor |
|-------|--------|
| 0 | No accuracy data published. No benchmark results in any public source. |
| 2 | No benchmark results, but architectural reasoning suggests accuracy investment (e.g., multi-pass verification, spec compliance checking). `[LOW CONFIDENCE]` required. |
| 4 | Community-reported benchmark results available (not official), OR official results below 40% SWE-Bench Verified. |
| 6 | Official benchmark results 40-59% SWE-Bench Verified, or equivalent published evaluation. |
| 8 | Official benchmark results 60-74% SWE-Bench Verified, or equivalent. |
| 10 | Official benchmark results 75%+ SWE-Bench Verified, or equivalent class-leading published evaluation. |

---

#### D4 — Setup Complexity

*How much friction does a new developer face to configure and make their first productive use of the system?*

| Score | Anchor |
|-------|--------|
| 0 | No public documentation. Setup process unknown or inaccessible. |
| 2 | Requires significant configuration (compile from source, daemon setup, manual config files, framework-specific boilerplate). |
| 4 | Standard package install (npm, pip, go install). Requires reading documentation to configure. Non-trivial learning curve. |
| 6 | Package install + minimal config. Works out of the box with a short getting-started guide. Reasonable learning curve. |
| 8 | Copy files or simple CLI command. Core concepts understandable in under 30 minutes. |
| 10 | Zero-config. Works immediately after install with no required configuration. Discoverable conventions. |

---

### Category B: Runtime Coordination (D5–D8)

**Definition**: What the system does *during* agent execution — parallelism, state durability, failure handling, and observability.

---

#### D5 — Parallelism and Execution Efficiency

*Does the system support genuine parallel execution, and how efficiently does it manage coordination overhead relative to throughput?*

| Score | Anchor |
|-------|--------|
| 0 | No parallelism. All work is strictly sequential. |
| 2 | Limited parallelism. Some concurrent execution but no structured parallelism model. High coordination overhead relative to throughput. |
| 4 | Structured parallelism. Workers run in parallel with dependency-aware scheduling. Coordination overhead is moderate. |
| 6 | Parallel execution with DAG dispatch. Workers dispatched as their dependencies complete (not batch-complete). Coordination overhead is managed. Startup time under 5 minutes. |
| 8 | Parallel execution + optimized dispatch. Above, plus lightweight modes (reaping/nano) for small runs. Sub-3-minute startup achievable. |
| 10 | Continuous parallel execution. Workers start immediately, no muster ceremony, no mandatory human gate. Coordination overhead near-zero (daemon or persistent orchestrator). |

---

#### D6 — State Durability and Resumability

*If an agent session dies mid-execution, can the run be resumed from a checkpoint without repeating completed work?*

| Score | Anchor |
|-------|--------|
| 0 | No persistent state. Session death requires complete restart. |
| 2 | Partial persistence. Some state survives session death, but resumption requires manual reconstruction. |
| 4 | Checkpoint-based persistence. Structured checkpoints written at phase transitions. Resumption is possible but requires reading checkpoint artifacts manually. |
| 6 | Automatic checkpoint with resume protocol. A defined resume procedure exists. Workers read their own checkpoint on restart and skip completed work. |
| 8 | Full durable state with worker-level granularity. Above, plus per-worker state files (HOOK.md equivalent) updated continuously during execution. Worker death resumes at last per-worker checkpoint, not last phase checkpoint. |
| 10 | Fully durable with automated resume. Above, plus the orchestrator automatically detects session death and resumes without human intervention. All state transitions are idempotent. |

---

#### D7 — Failure Handling and Recovery

*When a worker fails, how does the system classify, route, and recover from the failure?*

| Score | Anchor |
|-------|--------|
| 0 | No failure handling. System halts or undefined behavior on worker failure. |
| 2 | Basic retry. Failed workers are retried N times with no failure classification. |
| 4 | Classified retry. Failures are classified into at least 2 types (transient vs. non-transient) with distinct retry behavior. |
| 6 | Typed failure taxonomy. 3+ failure types with distinct handling paths (e.g., Resume, Retry, Skip, Restructure). Circuit breaker after repeated failures. Escalation to human for non-transient failures. |
| 8 | Full typed taxonomy + auto-recovery. Above, plus automated recovery for transient failures without human confirmation. Post-failure state is preserved for resume. |
| 10 | Full typed taxonomy + auto-recovery + Orange/diagnosis agent. Above, plus a dedicated root-cause agent performs diagnosis on blocked workers before recovery is attempted. Recovery decision informed by diagnosis. |

---

#### D8 — Observability and Debuggability

*During execution, can an operator see what agents are doing, audit past decisions, and diagnose problems?*

| Score | Anchor |
|-------|--------|
| 0 | No observability. No logs, traces, or status reporting during execution. |
| 2 | Basic logging. Text output to console. No structured per-agent attribution. |
| 4 | Structured per-agent logging. Each agent's output is attributed and logged separately. Status can be inferred from logs. |
| 6 | Real-time status roster. A human-readable status roster showing all agents (pending/running/done/failed) is available at any point. Per-agent log export. |
| 8 | Real-time roster + timeline. Above, plus a timeline view or trace that shows execution history, phase transitions, and timing. Per-agent cost breakdown. |
| 10 | Full observability platform. Streaming dashboard, time-travel debugging, OpenTelemetry or equivalent trace export. Integration with external monitoring tools. |

---

### Category C: Post-Execution Assurance (D9–D12)

**Definition**: What the system does *after* workers complete — quality gates, security, independent validation, and integration testing.

---

#### D9 — Pre-Merge Quality Gates

*Before any worker's output is merged or accepted, what automated quality checks are required?*

| Score | Anchor |
|-------|--------|
| 0 | No quality gates. Worker output accepted without verification. |
| 2 | Manual review only. Human reviews output before merge but no automated checks. |
| 4 | Automated test execution. Tests are run before merge; failures block merge. |
| 6 | Multi-gate pipeline. Tests + code review (automated or agent) both required before merge. Either gate can block. |
| 8 | Triple gate (tests + review + security). All three required before merge. Security criticals block; medium findings warn. |
| 10 | Triple gate + machine-enforced coverage thresholds. Above, plus coverage must meet a configurable minimum (enforced by tooling, not LLM instruction). |

---

#### D10 — Security Posture

*Does the system protect against prompt injection, sandbox execution environments, SAST scanning, or other security measures during agent execution?*

| Score | Anchor |
|-------|--------|
| 0 | No security features documented. |
| 2 | Basic awareness. Security mentioned in documentation but no specific mechanisms implemented. |
| 4 | Security review gate. A dedicated security review step exists (agent or tool) that checks for common vulnerabilities before merge. |
| 6 | Security review + input validation. Above, plus prompt injection protection or sandboxed execution for untrusted code paths. |
| 8 | SAST integration + sandboxed execution. Above, plus static analysis tools (Semgrep, CodeQL, or equivalent) integrated into the pipeline. Sandboxed execution for agent-generated code. |
| 10 | Full security stack. SAST + sandboxing + formal security certification (SOC 2, ISO 42001, or equivalent) + supply chain controls. |

---

#### D11 — Independent Validation and Spec Compliance

*After workers report completion, does the system independently verify that the spec or contract requirements were actually met?*

| Score | Anchor |
|-------|--------|
| 0 | No independent validation. Worker self-reports are accepted. |
| 2 | Human spot-check. Human reviews worker output informally against requirements. |
| 4 | Automated contract test execution. Contract tests (stubs asserting postconditions) are run before merge is accepted. |
| 6 | Orchestrator validation. The orchestrator (or a dedicated agent) independently reads key files the worker created/modified and verifies them against documented postconditions. |
| 8 | Orchestrator validation + spec compliance report. Above, plus a post-merge spec compliance pass generates a formal report (SENTINEL-REPORT.md or equivalent) verifying all acceptance criteria were met. |
| 10 | Full traceability. Above, plus automated traceability from spec requirements to test coverage to deployed artifact. Every requirement maps to a test. |

---

#### D12 — Cross-Run Learning and Memory

*Does the system capture learnings from completed runs and apply them to future runs?*

| Score | Anchor |
|-------|--------|
| 0 | No memory. Each run starts from zero. |
| 2 | Ad-hoc memory. Learnings may be captured informally but no structured protocol for extraction or application. |
| 4 | Structured lesson capture. A defined artifact (LESSONS.md or equivalent) is written after runs. Content is available for future runs but not automatically injected. |
| 6 | Structured lesson capture + automatic injection. Lessons from prior runs are automatically injected into new run prompts where relevant (pattern matching, task type matching). |
| 8 | Lessons + entity memory. Above, plus a persistent entity registry (ENTITIES.md or equivalent) capturing project-specific knowledge (file ownership history, known failure patterns, seam records). |
| 10 | Full institutional memory. Above, plus incremental ARCHITECTURE.md that is never regenerated from scratch, cross-spectrum knowledge preservation, and automated failure pattern extraction into future Howler drop prompts. |

---

## Scoring Procedure (Per Howler)

For each system in your group:

### 1. System Header
```
## [System Name]
**Category**: [Claude Code Ecosystem | General-Purpose Framework | Commercial/IDE | Research]
**Public source**: [URL or file path]
**Prior eval scores**: [D1-D8 from audit-2026 if available, else N/A]
```

### 2. Per-Dimension Scoring Block
For each dimension D1-D12:
```
### D[N] — [Dimension Name]
**Score**: [0|2|4|6|8|10] [LOW CONFIDENCE if applicable]
**Evidence**: [1-3 sentences citing source and quoting/paraphrasing the relevant specification text]
```

### 3. Summary Table
```
| System | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | Total |
|--------|----|----|----|----|----|----|----|----|----|-----|-----|-----|-------|
| [Name] | .. | .. | .. | .. | .. | .. | .. | .. | .. | ..  | ..  | ..  | ..    |
```

### 4. Per-System Narrative (3-5 sentences)
Summarize: where does this system lead? Where does it trail? What is its strongest use case?

---

## Deliverables

| File | Howler | Contents |
|------|--------|----------|
| `evaluation/12dim-eval/group-claude-code.md` | H1 | 8 systems × 12 dimensions, summary table, per-system narratives |
| `evaluation/12dim-eval/group-frameworks.md` | H2 | 6 systems × 12 dimensions, summary table, per-system narratives |
| `evaluation/12dim-eval/group-commercial.md` | H3 | 5 systems × 12 dimensions, summary table, per-system narratives |
| `evaluation/12dim-eval/group-research.md` | H4 | 2 systems × 12 dimensions, summary table, per-system narratives |
| `evaluation/12dim-eval/EVALUATION-REPORT.md` | H5 | Unified table (21 systems), radar analysis, tradeoff patterns, honest Spectrum assessment, recommendations |

---

## H5 Synthesis Instructions (Sequential, runs after H1-H4)

H5 reads all four group files and produces EVALUATION-REPORT.md. This is a synthesis task, not a re-scoring task. H5 carries forward scores exactly as recorded by H1-H4.

### Required sections in EVALUATION-REPORT.md:

**1. Unified Scoring Table** — all 21 systems, all 12 dimensions, totals. Sorted by total score descending.

**2. Category Rankings** — separate rankings for Category A (D1-D4), B (D5-D8), C (D9-D12). Identifies category leaders and category laggards.

**3. Radar Analysis** — for the top 8 systems by total score, describe the "shape" of their profile: are they Category A–dominant? Category C–weak? Balanced? Each profile described in 2-3 sentences.

**4. Tradeoff Patterns** — identify 3-5 structural tradeoffs observed across the field. Examples from prior evals: rigor vs. speed, cost vs. safety, setup friction vs. feature depth. Each tradeoff described with representative systems on each side.

**5. Honest Spectrum Assessment** — following the same format as audit-2026 Step 4: genuine strengths (where Spectrum leads with evidence), genuine weaknesses (where Spectrum trails with evidence), use cases where Spectrum is the wrong choice, use cases where it is the right choice. Spectrum is assessed as a competitor, not a host.

**6. Closest Competitor Analysis** — top 3 closest competitors to Spectrum by Euclidean distance (normalized per-dimension, same formula as prior audits: `(score - 0) / 10` for 0-10 scale). Per-competitor: dimension-by-dimension table, "why they're close" narrative, "where they diverge" narrative, developer trade-off recommendation.

**7. Field Observations** — 3-5 observations about trends in the multi-agent field that are visible from this evaluation. What are most systems getting right? What gap does almost no system address? Where is the field converging?

**8. Recommendations for Spectrum** — top 5 actionable improvement recommendations, each linked to a specific dimension gap, with a reference competitor showing what a higher score looks like.

---

## Reference Files for Howlers

### For Spectrum Protocol (H1 must read):
- `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md` — current operational protocol
- `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM.md` — full specification (use if OPS manual is insufficient)
- `/Users/ryan/spectrum-protocol/README.md` — public-facing feature summary and token costs
- `/Users/ryan/spectrum-protocol/evaluation/eval-v2/COMPETITIVE-EVAL-V2.md` — prior 8-dim scores for reference
- `/Users/ryan/spectrum-protocol/evaluation/audit-2026/COMPETITIVE-AUDIT.md` — prior 8-dim audit for reference

### For other Claude Code ecosystem systems (H1):
- Gas Town: https://github.com/steveyegge/gastown
- oh-my-claudecode: https://github.com/nicekid1/oh-my-claudecode (or community repo)
- Agent Teams: Anthropic Claude Code documentation on sub-agents
- Citadel: https://github.com/SethGammon/Citadel
- metaswarm: https://github.com/dsifry/metaswarm
- Overstory: https://github.com/jayminwest/overstory
- ruflo: search for public specification

### For frameworks (H2), commercial (H3), research (H4):
Use public repositories, official documentation, and published benchmark results. Cite sources explicitly for each score.

---

## Known Risks and Mitigations

**Risk 1: Uneven documentation depth across systems.** Some systems (Spectrum, LangGraph, CrewAI) have extensive public specifications. Others (ruflo, AgentCoder) may have minimal public documentation. Mitigation: apply `[LOW CONFIDENCE]` and score conservatively for underdocumented systems. Do not inflate.

**Risk 2: Commercial systems with closed architectures.** Devin, Cursor, Augment Code may have limited architectural disclosure. Mitigation: score from published blog posts, documentation, benchmark announcements, and community analysis. Flag what is inferred vs. documented.

**Risk 3: Research systems with dated results.** AgentCoder and AgileCoder are research papers; their benchmark results may reflect specific dataset conditions. Mitigation: score D3 from the published paper's reported numbers. Note the benchmark name (HumanEval, MBPP, SWE-Bench) explicitly — these are not always directly comparable.

**Risk 4: Spectrum conflict of interest.** This evaluation lives in the Spectrum repository. H1 must apply the same evidence standard to Spectrum as to Gas Town or Citadel. The impartiality rules above are binding.

**Risk 5: H5 scope creep.** H5 synthesizes — it does not re-score or editorialize beyond the synthesis sections defined above. If H5 disagrees with a group score, it notes the disagreement in a footnote but does not override the group report.

---

## Acceptance Criteria

The evaluation is complete when:

1. All five files exist in `evaluation/12dim-eval/`
2. Every system has scores for all 12 dimensions in the appropriate group file
3. Every score is an even number (0, 2, 4, 6, 8, 10)
4. Every score has a 1-3 sentence evidence citation
5. Spectrum Protocol's scores in group-claude-code.md are sourced from its specification files, not from its position as the host project
6. EVALUATION-REPORT.md contains all 8 required sections listed under H5 instructions
7. The unified table in EVALUATION-REPORT.md contains exactly 21 rows (one per system)
8. Scores in EVALUATION-REPORT.md match the group files exactly (H5 does not re-score)
