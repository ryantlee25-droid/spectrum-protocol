# PLAN.md — Competitive Evaluation v2
**Agent**: Blue (scout)
**Date**: 2026-03-31
**Based on**: audit-2026-0331 (prior rubric v1.0, group reports H2/H3/H4)

---

## Context and Motivation

The audit-2026-0331 run scored Spectrum 25/40 (4th place). Three improvements since then require re-scoring:

1. **Gold moved Opus → Sonnet** — 91% cost reduction. D1 Cost score for Spectrum should increase.
2. **Nano-mode added** — 2-3 Howler runs target under 1 minute. Affects D2 Speed and D7 Setup.
3. **Contract-by-reference** — saves ~10K tokens per 5-Howler run. Affects D1 Cost and D2 Efficiency.

Additionally, the evaluation rubric changes two dimensions:
- **D5 Observability** → **D5 Security** (code review, vulnerability detection, sandboxing)
- **D6 Recovery** → **D6 Quality Checks** (review gates, testing, compliance verification)

D7 Setup and D8 Scalability remain. D1 Cost, D2 Speed (renamed Efficiency), D3 Accuracy, D4 Workflow Rigor remain with updated anchors where needed.

This is a re-evaluation, not new research. Group Howlers reuse prior evidence from `evaluation/audit-2026/` and re-score under the new rubric. The synthesis Howler builds the final table and closest-competitor analysis.

---

## Scope

**15 systems** (same as prior audit):

### Group A — Claude Code Ecosystem (7 systems)
Spectrum Protocol, Gas Town, oh-my-claudecode, Agent Teams (Anthropic), Citadel, metaswarm, Overstory

### Group B — General-Purpose Frameworks (5 systems)
LangGraph, CrewAI, OpenAI Agents SDK, AutoGen/AG2, MetaGPT (excluded from Top 15 but included in group for reference)

### Group C — Commercial and IDE-Native (5 systems)
Devin, Cursor agents, Augment Code/Intent, GitHub Copilot Workspace, Factory

*(Note: Amazon Q Developer and Windsurf were excluded from the prior Top 15. Factory was included. Maintain same Top 15 composition as audit-2026: Citadel, Gas Town, LangGraph, Overstory, metaswarm, CrewAI, Factory, OpenAI Agents SDK, Augment Code/Intent, Devin, Cursor agents, Agent Teams, oh-my-claudecode, AutoGen/AG2, GitHub Copilot Workspace.)*

---

## New Rubric — 8 Dimensions with 1-5 Anchors

### D1 — Cost per Run

**What it measures**: Token/compute cost for a representative parallel coding task (3-5 agent run, ~10 files, ~2,000-5,000 tokens output per agent).

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | Negligible cost | Free tier covers meaningful parallel workloads OR documented cost under $0.10/run at representative scale. |
| **4** | Low cost | Documented cost $0.10-$0.50/run OR free open-source with typical cloud model costs. Community reports costs as non-issue. |
| **3** | Moderate cost | Documented or community-reported cost $0.50-$2.00/run. Cost noted in comparisons but not blocking. |
| **2** | High cost | Documented cost $2-$10/run OR subscription pricing that restricts parallel usage. Cost regularly cited as a drawback. |
| **1** | Prohibitive | >$10/run at representative scale OR pricing model that makes parallel runs economically impractical for individual developers. |

**Spectrum v2 scoring note**: Gold moved to Sonnet (91% cost reduction). The prior $9.43 estimate for 5-Howler full mode was calculated under Opus-Gold. Updated cost should be recalculated. Contract-by-reference saves ~10K tokens per 5-Howler run. Nano-mode (2-3 Howlers, under 1 min) likely under $1/run. Re-score Spectrum honestly against updated estimates from `evaluation/TOKEN-OPTIMIZATION.md`.

---

### D2 — Efficiency (Token Usage, Overhead Ratio)

**What it measures**: Wall-clock time for parallel task completion AND token efficiency — ratio of useful output tokens to total tokens consumed. Replaces the prior "Speed" dimension with broader coverage of overhead.

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | Industry-leading parallel speed + lean overhead | ≤5 min wall clock for 3-agent coding task AND overhead ratio (orchestration tokens / task tokens) ≤ 10%. Genuine sub-task parallelism with no artificial serialization. |
| **4** | Fast; parallelism evident; reasonable overhead | 5-15 min wall clock for 3-agent task, OR 3+ simultaneous agents documented. Overhead ratio ≤ 25%. No significant serialization bottlenecks. |
| **3** | Moderate speed; some parallelism; noticeable overhead | Parallel execution with constraints (limited concurrent agents, rate limiting, or 25-50% overhead ratio). Community reports acceptable but not fast. |
| **2** | Slow; limited parallelism; high overhead | Primarily sequential with parallelism as bolt-on. >50% overhead ratio or documented wall times >30 min for tasks that should parallelize. |
| **1** | No meaningful parallelism | Single-agent execution only, OR all subtasks serialized in practice. Overhead dominates useful work. |

**Spectrum v2 scoring note**: Nano-mode targets under 1 minute for 2-3 Howler runs. Prior score was 3 (muster adds 3-8 min overhead). Nano-mode may push Spectrum toward 4 for small runs; full-mode ceiling remains. Score reflects the mode mix available to users.

---

### D3 — Accuracy (Code Quality, Benchmark Results)

**What it measures**: Plan quality, code quality, and test pass rates. Primary benchmark is SWE-Bench Verified (% of real GitHub issues resolved).

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | State-of-the-art accuracy | SWE-Bench ≥50%, OR top-3 published ranking on a recognized coding benchmark. Minimal hallucination and spec-drift reports. |
| **4** | Strong accuracy | SWE-Bench 30-50%, OR second-tier benchmark ranking. Community reports high quality with occasional failures. |
| **3** | Acceptable accuracy | SWE-Bench 15-30%, OR community consensus that output requires moderate review/correction. |
| **2** | Below-average accuracy | SWE-Bench <15% or no benchmark. Community reports frequent correction cycles. |
| **1** | Poor accuracy | No published benchmark AND SWE-Bench <5%. Consistent failure, hallucination, or code that does not compile. |

**Missing evidence rule**: No evidence → score 2 with [LOW CONFIDENCE]. Same as prior rubric.

---

### D4 — Workflow Rigor (Pre-execution Contracts, Failure Taxonomy, Circuit Breaker, Adversarial Review)

**What it measures**: Degree to which the system enforces disciplined multi-agent coordination — contracts, file ownership, failure taxonomy, adversarial review, and prevention of silent divergence. **Unchanged from prior rubric.**

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | Comprehensive rigor with enforcement | ALL of: (a) pre-execution interface contracts or ownership declarations, (b) explicit failure taxonomy with distinct handling paths, (c) automated circuit breakers or escalation, (d) independent review step (adversarial or reviewer-author separation). Enforced by the framework, not merely recommended. |
| **4** | Strong rigor; most components present | At least 3 of the 4 components above. Missing component documented as a known gap. |
| **3** | Moderate rigor; some structure | Task decomposition with role separation OR retry-on-failure with logging. No file ownership contracts. No formal failure taxonomy. |
| **2** | Minimal rigor | Multiple agents but coordination informal. No documented failure modes. Recovery is "try again." |
| **1** | No workflow rigor | Agents sharing state without coordination mechanisms. Failure handling is uncaught exceptions or silent context loss. |

---

### D5 — Security (Code Review, Vulnerability Detection, Sandboxing)

**What it measures**: The degree to which the system reviews generated code for vulnerabilities, detects security issues before merge, enforces execution sandboxing, and prevents injection/privilege-escalation attacks.

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | Comprehensive security enforcement | ALL of: (a) automated vulnerability scanning of generated code (SAST/SCA), (b) documented sandboxed execution environment (no host file system access by default), (c) security-focused review step before any code merges, (d) documented protection against prompt injection or privilege escalation. |
| **4** | Strong security; most components present | At least 3 of the 4 components above. E.g., sandboxed execution + security review gate but no automated SAST. |
| **3** | Moderate security | Sandboxed execution OR security-focused code review step, but not both. Basic isolation documented. No automated vulnerability scanning. |
| **2** | Minimal security | Code runs on host machine without documented sandboxing. No security-specific review step. Human is the only security gate. |
| **1** | No security controls | Generated code executes without sandboxing or review. No documented threat model. Known injection vulnerabilities unremediated. |

**Scoring notes**:
- Commercial IDE systems (Cursor, Devin, GitHub Copilot Workspace) run on cloud VMs — this is sandboxing, score up from 1 baseline.
- CLAUDE.md-based protocols (Spectrum, Gas Town, Citadel) run in local git worktrees on the host machine — no sandboxing by default.
- The `/diff-review` security gate in Spectrum is a security-focused review step; document its actual scope per SPECTRUM-OPS.md.

---

### D6 — Quality Checks (Review Gates, Testing, Compliance Verification)

**What it measures**: Whether the system enforces automated quality checks — test runs, code review gates, spec compliance verification — before code is merged or considered complete.

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | Comprehensive quality enforcement | ALL of: (a) automated test execution with pass/fail gate, (b) peer or adversarial code review step, (c) spec/acceptance-criteria compliance check, (d) coverage reporting. Gates are blocking — code cannot merge on failure. |
| **4** | Strong quality gates; most components | At least 3 of the 4 components above. One gate may be advisory rather than blocking. |
| **3** | Moderate quality checks | Automated test execution OR code review step, but not both. Some spec checking. Tests run but coverage not enforced. |
| **2** | Minimal quality checks | Tests run only if the user configures them. No built-in review step. Code review is optional and human-initiated. |
| **1** | No quality checks | No test execution, no code review step, no spec verification. Code is produced and delivered with no automated quality gate. |

**Spectrum v2 scoring notes**:
- Spectrum's triple gate (White + Gray + /diff-review) is blocking for White (zero blockers) and Gray (zero failures). This is 3 of 4 components (missing: coverage enforcement is advisory not blocking). Prior D6 Recovery score was 4; this new dimension captures different behavior.
- Gray runs after each merge (Phase 5), providing incremental integration testing. Obsidian checks spec compliance in Phase 6. These are genuine quality components.
- Systems that run tests only if the user sets them up score 2. Systems with no test integration score 1.

---

### D7 — Setup Complexity (Time to First Run, Dependencies, Learning Curve)

**What it measures**: Dependencies, configuration burden, and learning curve to run a first parallel multi-agent task. **Unchanged from prior rubric.**

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | Near-zero setup | Single command installation. No API key config beyond primary LLM. First parallel run within 15 minutes. Zero infrastructure dependencies. |
| **4** | Low setup | 2-3 steps. API keys for 1-2 services. First parallel run within 1 hour. Optional infrastructure. |
| **3** | Moderate setup | 4-6 steps or tutorial required. Environment variables or config files. First parallel run within a half-day. Framework abstraction learning curve. |
| **2** | High setup | Multiple dependencies beyond core LLM (vector store, message broker, DB). Framework-specific knowledge required. Full day to first parallel run. |
| **1** | Very high setup | Infrastructure provisioning required (Docker, cloud services, self-hosted). >1 day to first run. Community reports of failed installations. |

---

### D8 — Scalability (Agent Count, Coordination Overhead)

**What it measures**: Performance at 8+ parallel agents — documented ceilings, coordination overhead growth, architecture-imposed limits. **Unchanged from prior rubric.**

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | Scales to 10+ agents with documented evidence | Published evidence or architecture docs confirming effective parallel execution at 8+ agents with sub-linear coordination overhead. No documented ceiling below 10 agents. |
| **4** | Scales to 6-8 agents effectively | Architecture supports 6-8 with documented guidance. Coordination overhead acknowledged but managed. Performance at 8 is acceptable relative to 2. |
| **3** | Scales to 3-5 agents; degrades beyond | Documented or community-reported sweet spot of 3-5 agents. Performance degrades noticeably beyond 5-6. |
| **2** | Scales to 2-3 agents only | Practical ceiling 2-3 agents before failures or quality degradation. Community or docs acknowledge limited ceiling. |
| **1** | No scalability beyond single agent | Single-agent execution or parallelism that degrades to sequential at 2+ agents. |

---

## Evidence Hierarchy (Binding)

1. **Public benchmarks** — SWE-Bench, HumanEval, published third-party evaluations. Cite paper/publication.
2. **Official documentation** — README, docs site, pricing pages, changelog. Cite URL or document name.
3. **Community reports** — GitHub issues, Reddit, HN, developer blogs. Cite source specifically.
4. **First-principles reasoning** — Acceptable when higher-quality evidence is unavailable. Label `[First-principles reasoning]`.

**Missing evidence rule**: No evidence → score 2 with [LOW CONFIDENCE]. Partial evidence → conservative score + [MEDIUM CONFIDENCE]. Do not assign score 3 as a default for unknown systems. Spectrum is scored identically to all other systems — no favorable anchor interpretation.

---

## Howler Structure: Reaping Mode

Three parallel group Howlers + one synthesis Howler. Reaping mode applies (3-4 Howlers, all creating new files, no shared TypeScript interfaces).

### H1 — group-claude-code (Claude Code Ecosystem)

**Task**: Re-score the 7 Claude Code ecosystem systems under the new 8-dimension rubric. Read `evaluation/audit-2026/group-claude-code.md` for prior evidence. Re-score all 7 systems. Produce `evaluation/eval-v2/group-claude-code.md`.

**Systems**: Spectrum Protocol, Gas Town, oh-my-claudecode, Agent Teams (Anthropic), Citadel, metaswarm, Overstory

**Key re-scoring guidance**:
- Spectrum D1 Cost: Gold is now Sonnet. Prior $9.43 estimate was Opus-Gold. Use `evaluation/TOKEN-OPTIMIZATION.md` to calculate updated cost for 5-Howler full-mode with Sonnet-Gold. Nano-mode (<$1) is also available. Score accordingly — D1=2 may no longer be accurate.
- Spectrum D2 Efficiency: Nano-mode targets <1 minute for 2-3 Howlers. Prior D2=3 was based on 3-8 minute muster. Nano-mode changes this substantially for small runs.
- Spectrum D5 Security: /diff-review is a security-focused gate (zero security criticals required). Local git worktrees = no sandboxing. Score honestly.
- Spectrum D6 Quality Checks: Triple gate (White + Gray + /diff-review) blocks on zero failures. Gray per-merge, Obsidian post-merge. Prior D6 Recovery = 4 was for failure recovery — different dimension. Re-score fresh.
- For all systems: D5 Security and D6 Quality Checks are entirely new — prior report has no scores for these. Research each system's security and quality check posture from available evidence.
- Gas Town D5 Security: Git-backed provenance does not equal sandboxing. Score honestly.
- Citadel: If circuit breaker claim is now substantiated with newer evidence, update D4.

**Output format**: Follow same structure as `evaluation/audit-2026/group-claude-code.md`. Table first, then per-system evidence notes for all 8 dimensions.

---

### H2 — group-frameworks (General-Purpose Frameworks)

**Task**: Re-score the 5 general-purpose frameworks under the new 8-dimension rubric. Read `evaluation/audit-2026/group-frameworks.md` for prior evidence. Produce `evaluation/eval-v2/group-frameworks.md`.

**Systems**: LangGraph, CrewAI, OpenAI Agents SDK, AutoGen/AG2, MetaGPT *(MetaGPT remains in the group report for reference but is excluded from the Top 15 synthesis table — note this distinction)*

**Key re-scoring guidance**:
- All systems: D5 Security and D6 Quality Checks are new dimensions — no prior scores. Research each system.
- LangGraph D5 Security: StateGraph runs user-defined Python code; no sandboxing by default. LangSmith does not add security review. Score honestly.
- LangGraph D6 Quality Checks: LangGraph has human-in-the-loop pause points (partial review gate). No built-in test execution. Score carefully.
- CrewAI D6 Quality Checks: Task retry ≠ quality gate. Does CrewAI have a code review agent role? Document.
- OpenAI Agents SDK D5 Security: Guardrails (input/output validation) are security-relevant. Codex runs in sandboxed VMs. Score the security posture of guardrails + execution environment together.
- OpenAI Agents SDK D6 Quality Checks: Does the SDK have test execution integration? Document.
- D5 Observability scores from prior audit: Do NOT port to D5 Security. D5 is a new dimension. Prior D5 scores (LangGraph=5, OpenAI=4, etc.) are irrelevant to the new Security dimension.
- D6 Recovery scores from prior audit: Do NOT port to D6 Quality Checks. Prior D6 Recovery scores should not bias the new D6 Quality Checks dimension.

**Output format**: Same structure as `evaluation/audit-2026/group-frameworks.md`.

---

### H3 — group-commercial (Commercial and IDE-Native)

**Task**: Re-score the 5 commercial systems under the new 8-dimension rubric. Read `evaluation/audit-2026/group-commercial.md` for prior evidence. Produce `evaluation/eval-v2/group-commercial.md`.

**Systems**: Devin, Cursor agents, Augment Code/Intent, GitHub Copilot Workspace, Factory

**Key re-scoring guidance**:
- All systems: D5 Security and D6 Quality Checks are new dimensions. Research each system.
- Devin D5 Security: Managed Devins run in isolated cloud VMs (sandboxing). Document the security model. Does Devin run any SAST on generated code?
- Cursor D5 Security: Background agents run on cloud VMs. Security posture of generated code review?
- GitHub Copilot Workspace D5 Security: GitHub Advanced Security (CodeQL) integration is relevant. Does Copilot Workspace trigger CodeQL on generated PRs? Document.
- Augment Code/Intent D5 Security: Verifier role — does it include security review? Document.
- Factory D5 Security: Factory Droids run in cloud VMs. Document security controls.
- D6 Quality Checks: Commercial systems vary widely — Devin tests code before submitting PRs. Cursor agents create PRs but testing is CI-dependent. GitHub Copilot Workspace has human review step built in. Document each carefully.
- Amazon Q Developer and Windsurf: These were excluded from the Top 15 but if Factory is covered, note their omission rationale consistently with TOP15-RANKING.md.

**Output format**: Same structure as `evaluation/audit-2026/group-commercial.md`.

---

### H4 — synthesis (COMPETITIVE-EVAL-V2.md)

**Task**: Synthesize all three group reports into a unified competitive evaluation. Produce `evaluation/eval-v2/COMPETITIVE-EVAL-V2.md`.

**Input files**: 
- `evaluation/eval-v2/group-claude-code.md` (H1 output)
- `evaluation/eval-v2/group-frameworks.md` (H2 output)
- `evaluation/eval-v2/group-commercial.md` (H3 output)
- `evaluation/audit-2026/COMPETITIVE-AUDIT.md` (prior audit for comparison)

**Required sections**:

1. **Unified Scoring Table** — All 15 Top 15 systems, all 8 dimensions. Carry scores forward exactly from group reports — no re-scoring by H4. Include prior audit scores (D1-D8 v1) alongside new scores (D1-D8 v2) for dimensions that changed (D5, D6). Flag any system whose total changed by 3+ points as "notable change."

2. **Score Delta Analysis** — For each of the 15 systems, compute the delta between v1 and v2 total scores. Show the 5 largest movers (up or down) and explain the driver. If Spectrum's position in the ranking changed, state it explicitly.

3. **Closest Competitors to Spectrum** — Euclidean distance analysis (same methodology as prior audit: normalize 0-1 per dimension, compute √Σ(Δ_dim²)). Identify top 3 closest competitors in the new scoring space and provide detailed comparison tables.

4. **Spectrum: Honest Assessment** — Where does Spectrum stand now, after optimizations? Do the Gold→Sonnet migration, nano-mode, and contract-by-reference change Spectrum's ranking? Which weaknesses from the prior audit remain unaddressed? Which of the 5 prior recommendations have been partially or fully acted on?

5. **New Dimension Analysis** — How do the 15 systems compare on D5 Security and D6 Quality Checks specifically? Who leads on each new dimension? What does the field look like on these dimensions?

6. **Recommendations** — 3-5 highest-priority improvements for Spectrum based on the new scoring. Frame against specific competitor scores. Carry forward un-acted-on recommendations from the prior audit if still relevant; retire ones that have been addressed.

7. **Executive Summary** — 300-400 words. Open with the ranking change (if any). Identify the top 3 competitors by overall score and by Euclidean proximity to Spectrum. Conclude with Spectrum's clearest differentiators and most important remaining gaps.

---

## Deliverables

| File | Howler | Description |
|------|--------|-------------|
| `evaluation/eval-v2/group-claude-code.md` | H1 | Claude Code ecosystem group, all 8 dimensions re-scored |
| `evaluation/eval-v2/group-frameworks.md` | H2 | General-purpose frameworks group, all 8 dimensions re-scored |
| `evaluation/eval-v2/group-commercial.md` | H3 | Commercial/IDE-native group, all 8 dimensions re-scored |
| `evaluation/eval-v2/COMPETITIVE-EVAL-V2.md` | H4 | Synthesis: unified table, delta analysis, closest competitors, honest assessment, recommendations |

---

## Execution Notes

### Mode: Reaping

All 4 Howlers create new files only. No MODIFIES. No shared interfaces. Reaping mode is appropriate.

**Howler drop order**: H1, H2, H3 in parallel. H4 after all three complete (H4 reads the group files).

### Key Constraints

1. **Do not port D5/D6 scores from the prior audit** — Observability and Recovery are different constructs from Security and Quality Checks. Every system gets a fresh D5 and D6 score.
2. **Do not inflate Spectrum's scores** — Apply the same evidence standard to Spectrum as every other system. If Spectrum's nano-mode is the only evidence for D2 improvement and full-mode remains slow, score reflects the full-mode experience for typical users.
3. **Use updated cost figures** — The prior $9.43 estimate for Spectrum 5-Howler full-mode used Opus-Gold. `TOKEN-OPTIMIZATION.md` shows Gold/Muster was 21% of run cost at Opus pricing. Recalculate for Sonnet-Gold before finalizing D1.
4. **Carry forward Top 15** — Same 15 systems as prior audit. No additions or removals. MetaGPT stays in group-frameworks.md but is excluded from the synthesis Top 15 table (consistent with prior audit).
5. **Evidence citations required** — Every score requires at least one specific citation per the evidence hierarchy. "General knowledge" is not a citation. For new dimensions without prior evidence in the group reports, use first-principles reasoning with explicit labeling.

### Prior Audit Reference Files

All at `evaluation/audit-2026/`:
- `COMPETITIVE-AUDIT.md` — synthesis with full closest-competitors analysis
- `RUBRIC.md` — prior rubric (for reference; new rubric embedded above)
- `group-claude-code.md` — H2 evidence for Claude Code ecosystem
- `group-frameworks.md` — H3 evidence for frameworks
- `group-commercial.md` — H4 evidence for commercial systems
- `AGENTIC-LANDSCAPE.md` — landscape survey (source for many prior citations)
- `TOKEN-OPTIMIZATION.md` — Spectrum token cost analysis (key input for D1 re-score)
