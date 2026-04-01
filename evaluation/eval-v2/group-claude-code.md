# Claude Code Ecosystem Scoring Report — v2
**Spectrum**: eval-v2-0331
**Howler**: H1-claude-code
**Date**: 2026-03-31
**Rubric version**: evaluation/eval-v2/PLAN.md v2.0
**Prior report**: evaluation/audit-2026/group-claude-code.md

---

## Scoring Table

| System | D1 Cost | D2 Efficiency | D3 Accuracy | D4 Workflow Rigor | D5 Security | D6 Quality Checks | D7 Setup | D8 Scalability | Total |
|--------|---------|---------------|-------------|-------------------|-------------|-------------------|----------|----------------|-------|
| Spectrum Protocol | 2 | 4 | 2 | 5 | 2 | 5 | 3 | 3 | 26 |
| Gas Town | 3 | 5 | 2 | 3 | 2 | 2 | 2 | 5 | 24 |
| oh-my-claudecode | 3 | 4 | 2 | 2 | 1 | 1 | 5 | 3 | 21 |
| Agent Teams (Anthropic) | 3 | 4 | 3 | 2 | 2 | 2 | 4 | 3 | 23 |
| Citadel | 3 | 4 | 2 | 4 | 2 | 3 | 4 | 3 | 25 |
| metaswarm | 3 | 3 | 2 | 4 | 2 | 4 | 3 | 3 | 24 |
| Overstory | 3 | 4 | 2 | 3 | 2 | 2 | 3 | 4 | 23 |

---

## Score Changes from v1

| System | v1 Total | v2 Total | Delta | Driver |
|--------|----------|----------|-------|--------|
| Spectrum Protocol | 25 | 26 | +1 | D2 +1 (Nano mode), D5 new (2), D6 new (5) replacing D5 Obs (3) + D6 Recovery (4) |
| Gas Town | 26 | 24 | -2 | D5 new (2), D6 new (2) replace prior D5 Obs (3) + D6 Recovery (3) |
| oh-my-claudecode | 23 | 21 | -2 | D5 new (1), D6 new (1) replace prior D5 Obs (2) + D6 Recovery (2) |
| Agent Teams | 23 | 23 | 0 | D5 new (2), D6 new (2) replace prior D5 Obs (2) + D6 Recovery (2) |
| Citadel | 27 | 25 | -2 | D5 new (2), D6 new (3) replace prior D5 Obs (3) + D6 Recovery (4) |
| metaswarm | 24 | 24 | 0 | D5 new (2), D6 new (4) replace prior D5 Obs (2) + D6 Recovery (4) |
| Overstory | 26 | 23 | -3 | D5 new (2), D6 new (2) replace prior D5 Obs (4) + D6 Recovery (3) |

*Note: D2 was renamed from "Speed" to "Efficiency" but scores are compared directly. Spectrum D1 remains 2 despite Gold→Sonnet migration (full-mode cost still $5-6 at representative scale). D2 increased from 3 to 4 due to Nano mode.*

---

## Per-System Evidence Notes

---

### Spectrum Protocol

*Scored as a peer. Self-reported claims from README and SPECTRUM-OPS.md are treated as inputs subject to the same evidence standard as any other system, per PLAN.md evidence hierarchy.*

**D1 Cost — 2**: Gold moved from Opus to Sonnet (README release notes, 2026-03-31: "91% reduction in Gold phase costs (~$3.50/spectrum saved)"). Updated cost calculation using TOKEN-OPTIMIZATION.md phase breakdown:

Prior Opus-Gold phases (5-Howler): Gold Muster ($1.99) + Gold Pax ($1.57) + Gold self-reflect x5 ($0.28) + Gold reviews Brown ($0.38) = **$4.22 Opus-Gold total**. At Sonnet pricing (÷5 on output, ÷5 on input): Muster ($0.40) + Pax ($0.31) + self-reflect ($0.06) + Brown review ($0.08) = **$0.85 Sonnet-Gold total**. Savings: ~$3.37.

Updated cost estimates: 5-Howler full ≈ $9.43 - $3.37 = **~$6.06**. 3-Howler reaping: ~$3.10 (proportional reduction). Nano mode (2-3 Howlers, no quality gates, minimal Gold): **~$1.50-2.00**.

Nano mode puts individual runs into D1=3 territory ($0.50-$2.00). However, the representative 5-Howler full-mode case at ~$6.06 remains in the D1=2 range ($2-$10). The rubric anchors at "representative 3-5 agent scale." At 5-agent full mode, Spectrum lands at the midpoint of D1=2. The cost improvement is real but not sufficient to move the 5-Howler case to D1=3. Score remains 2. [MEDIUM CONFIDENCE — recalculated from TOKEN-OPTIMIZATION.md phase breakdown; README cost table not yet updated to reflect Sonnet-Gold]

Source: evaluation/TOKEN-OPTIMIZATION.md §1.2 phase breakdown; spectrum-protocol/README.md release notes (2026-03-31); spectrum/SPECTRUM-OPS.md Model Assignments table (Gold: sonnet).

**D2 Efficiency — 4**: Three modes now exist: Nano (<1 min, 2-3 Howlers), Reaping (~3 min overhead, 3-4 Howlers), Full (~8 min overhead, 3-8 Howlers). SPECTRUM-OPS.md (Nano Mode section) confirms Nano "targets muster + drop in under 1 minute" and "auto-approves — presents manifest and drops Howlers immediately, no human confirmation gate." Genuine parallel execution via pre-created git worktrees. Overhead ratio: Nano mode has near-zero orchestration overhead (NANO-MANIFEST.md only). Full mode overhead is significant (~8 min pre-execution + human approval gate).

Scoring reflects mode mix: Nano and Reaping modes represent the majority of practical Spectrum use cases (small parallel work, pure-create Howlers). The prior D2=3 was based solely on full-mode with 3-8 min muster. Nano and Reaping mode meaningfully lower the overhead for the most common use case. Wall clock for a 3-Howler Nano run: <5 min total (under 1 min overhead + parallel execution). This matches the D2=4 anchor (5-15 min, parallelism evident, overhead ≤25%). Full-mode 8-Howler remains D2=3 territory (>30 min with muster + human review), but full mode is documented as the high-ceremony path for complex, risky decompositions. Score 4 reflects the weighted capability.

Source: spectrum/SPECTRUM-OPS.md §Nano Mode; spectrum/SPECTRUM-OPS.md §Reaping Mode ("~3 min instead of ~8 min"); CLAUDE.md §Activation Criteria.

**D3 Accuracy — 2**: No published SWE-Bench score or independent accuracy benchmark for Spectrum Protocol. The README documents a gold-comparison evaluation (gold-eval-0331) with 18 benchmark scenarios and 12 head-to-head runs, but this measures Gold's orchestration quality, not end-to-end code accuracy. No third-party benchmark or community reports with accuracy data found in public sources. Per the missing-evidence rule: no benchmark data → score 2. [LOW CONFIDENCE — no public benchmark evidence; self-reported orchestration-quality evaluation only]

Source: spectrum-protocol/README.md §Evaluation and release notes (2026-03-31); evaluation/gold-comparison/results/ (internal evaluation, not publicly benchmarked).

**D4 Workflow Rigor — 5**: All four D4=5 components remain fully documented and enforced: (a) **Pre-execution contracts**: CONTRACT.md with per-Howler preconditions/postconditions/invariants (full DbC for interface-heavy Howlers), MANIFEST.md file ownership matrix where every file appears exactly once, verified during muster and by Politico; (b) **Failure taxonomy**: 5 distinct types (transient, logical, structural, environmental, conflict) with different handling paths (Resume/Retry/Skip/Restructure) per type; (c) **Circuit breaker**: 2 failures on same locus auto-escalate to structural, Gold pauses and escalates to human; (d) **Independent adversarial review**: Politico (independent Sonnet) challenges CONTRACT.md and MANIFEST.md before freeze, all blockers must be resolved. AMENDMENT.md protocol enforces silent divergence prevention. Caveat from prior audit stands: enforcement is via LLM instruction adherence, not machine verification, which is a meaningful distinction from hard-coded framework enforcement.

Source: spectrum/SPECTRUM-OPS.md §Phase 1 Muster, §Phase 4 Forge, §Rules; spectrum-protocol/README.md §Feature Highlights.

**D5 Security — 2** *(new dimension — no prior score to port)*: Spectrum's security posture has one genuine component and two notable absences.

Present: **/diff-review security gate** — the triple quality gate mandates `/diff-review` per Howler before any PR opens. SPECTRUM-OPS.md: "zero security criticals required (high/medium = warning in PR description)." This is a documented security-focused review step with blocking enforcement on criticals.

Absent: (a) **No automated SAST/SCA** — no static analysis tool integration documented. Security review is LLM-driven (/diff-review), not tooling-driven. (b) **No sandboxing** — Spectrum runs in local git worktrees on the host machine. SPECTRUM-OPS.md confirms worktrees are created under `~/.claude/spectrum/<rain-id>/worktrees/`, which is local filesystem. Generated code executes without isolation from host. (c) **No documented prompt injection protection** — Spectrum's contract system enforces scope boundaries between agents, which provides some resistance to lateral scope expansion, but explicit prompt injection threat modeling is not documented.

The /diff-review gate is a genuine security contribution but it is LLM-based code review, not automated scanning. It covers 1 of 4 D5=5 components (security-focused review step). Missing: SAST/SCA, sandboxed execution, documented injection protection. Score 2 (code runs on host machine without sandboxing; security review step present but no automated scanning).

Source: spectrum/SPECTRUM-OPS.md §Phase 3 (Triple Quality Gate); spectrum/CLAUDE.md §Pre-PR Quality Gates; spectrum-protocol/README.md §Feature Highlights (Triple Quality Gate).

**D6 Quality Checks — 5** *(new dimension — replaces prior D6 Recovery)*: Spectrum implements comprehensive quality enforcement across four distinct components:

(a) **Automated test execution with pass/fail gate**: Gray runs tests with zero-failures required before any PR opens. Gray also runs after each merge (incremental integration testing) and a final Gray run after all PRs merge. Tests are not optional — the triple gate blocks PR opening until Gray passes. Source: SPECTRUM-OPS.md §Phase 3 (Gray — zero failures required).

(b) **Peer/adversarial code review gate**: White code review requires zero blockers before PR opens. White re-runs after any blocker fixes. Source: SPECTRUM-OPS.md §Phase 3 (White — zero blockers required); CLAUDE.md §Pre-PR Quality Gates.

(c) **Spec/acceptance-criteria compliance check**: Obsidian runs post-merge in Phase 6, verifying PLAN.md acceptance criteria against merged code and producing SENTINEL-REPORT.md. Additionally, Politico independently reviews the plan before execution. Contract compliance is verified by both White (per-PR) and Gold Pax (independent validation against CONTRACT.md postconditions). Source: SPECTRUM-OPS.md §Phase 6 Triumph; README §Feature Highlights (Obsidian, Independent Validation).

(d) **Coverage reporting**: Gray reports coverage gaps in PR descriptions. Coverage gaps are advisory not blocking, but they are surfaced on every PR. Source: SPECTRUM-OPS.md §Phase 3 (coverage gaps noted in PR, not blocking).

All three primary gates (White, Gray, /diff-review) are blocking — code cannot merge on failures. Obsidian is post-merge but required by protocol for every full spectrum. The only gap from a strict D6=5 reading is that coverage enforcement is advisory rather than blocking. However, three of four components are fully blocking gates, and the fourth (spec compliance) is independently implemented twice (Obsidian + Gold Pax). This is the strongest quality check posture in this group. Score 5.

Source: spectrum/SPECTRUM-OPS.md §Phase 3, §Phase 5, §Phase 6; spectrum/CLAUDE.md §Pre-PR Quality Gates; spectrum-protocol/README.md §Triple Quality Gate.

**D7 Setup — 3**: No change from prior audit. The README now includes a one-line curl installer and copies agent .md files as an additional step. However, the setup remains: (1) copy CLAUDE.md, (2) copy SPECTRUM-OPS.md, (3) copy SPECTRUM.md, (4) copy agents/*.md, (5) copy seam_check.py. That is now 5 discrete steps plus the learning curve for a ~550-line ops manual and 7-phase protocol before the first productive run. The README explicitly states "Not For: Zero-config quick start — use oh-my-claudecode." Nano mode reduces ceremony for experienced users but does not lower the first-run learning curve. Consistent with D7=3.

Source: spectrum-protocol/README.md §Quick Start (curl + manual steps); spectrum-protocol/README.md §Not For.

**D8 Scalability — 3**: No change. Documented maximum of 8 parallel Howlers, with the README explicitly stating this is where coordination overhead dominates. Nano mode (2-3 Howlers), Reaping mode (3-4 Howlers), and Full mode (3-8 Howlers) all operate within this ceiling. The README explicitly says "Not For: 20+ agents at scale — use Gas Town." Consistent with D8=3 (documented sweet spot 3-5 agents; ceiling at 8 explicit in protocol rules).

Source: spectrum-protocol/README.md §Best For and §Not For; SPECTRUM-OPS.md §Rules ("Max 8 parallel Howlers — more than this and coordination overhead dominates").

**Uncertainty flags**: D1 (recalculated from TOKEN-OPTIMIZATION.md; README cost table not yet updated), D3 (no public benchmark — lowest-confidence score in this report).

---

### Gas Town (steveyegge/gastown)

**D1 Cost — 3**: No change from prior audit. No platform fee; standard Claude Code API pricing. No per-run benchmark published. Community reports describe Gas Town as viable on individual developer budgets at small scale. [MEDIUM CONFIDENCE — model costs only; no per-run benchmark at representative 3-5 agent scale]

Source: steveyegge/gastown README (github.com/steveyegge/gastown); Steve Yegge Medium post "Welcome to Gas Town," January 2026.

**D2 Efficiency — 5**: No change. Gas Town is purpose-built for maximum parallel throughput. GUPP (Go Until a Problem Presents) eliminates orchestrator approval gates. Pull-based work queues enable genuine concurrent execution across 20-30+ agents. Overhead ratio is minimal — agents pull work and execute without muster ceremony. Architecture documentation confirms simultaneous multi-agent execution with no artificial serialization.

Source: AGENTIC-LANDSCAPE.md §2.5; steveyegge/gastown README; DeepWiki gastown core concepts (deepwiki.com/steveyegge/gastown/2-core-concepts).

**D3 Accuracy — 2**: No change. No published SWE-Bench or independent benchmark. GUPP's aggressive autonomy trades accuracy checkpoints for throughput. No pre-flight contract mechanism. [MEDIUM CONFIDENCE]

Source: AGENTIC-LANDSCAPE.md §6 cross-cutting table; steveyegge/gastown README limitations section.

**D4 Workflow Rigor — 3**: No change. Git-backed provenance, 3-tier watchdog, pull-based task queues provide role separation and retry-with-logging. Missing: pre-execution interface contracts, formal failure taxonomy (watchdog detects stalls but does not classify), independent adversarial review. Satisfies D4=3 but not D4=4.

Source: AGENTIC-LANDSCAPE.md §2.5; gastown/docs/glossary.md.

**D5 Security — 2** *(new dimension)*: Gas Town runs on local machine in Go binary + daemon mode, with agents accessing host filesystem directly. No documented sandboxing of agent execution. No automated SAST or security-focused review step documented. Git-backed provenance records actions after the fact but provides attribution, not prevention. The 3-tier watchdog monitors agent health (stall detection), not security. No documented threat model or prompt injection protection. 0 of 4 D5=5 components present. Score 2 (code runs on host machine without sandboxing; no security review step; human is the only gate).

Source: steveyegge/gastown README (Go binary architecture); AGENTIC-LANDSCAPE.md §2.5 architecture description; [First-principles reasoning from documented architecture].

**D6 Quality Checks — 2** *(new dimension)*: Gas Town has no documented built-in code review step, test execution gate, or spec compliance verification before code is committed. The 3-tier watchdog handles agent health and stall detection — it is not a quality gate. Git-backed provenance records what happened; it does not enforce quality standards before commit. GUPP's philosophy (agents proceed until blocked) means code is produced and committed with human review as the only external gate. Score 2 (tests run only if user configures them; no built-in review step; code review is manual and human-initiated).

Source: steveyegge/gastown README; AGENTIC-LANDSCAPE.md §2.5 Error Recovery; [First-principles reasoning — no quality gate documentation found].

**D7 Setup — 2**: No change. Requires Go 1.25+, Git, Dolt, tmux. Multi-step installation (go install, gt install, gt daemon start). Multiple dependencies beyond core LLM. AGENTIC-LANDSCAPE.md characterizes as "heavy infrastructure requirements."

Source: gastown/docs/INSTALLING.md; AGENTIC-LANDSCAPE.md §2.5 Limitations.

**D8 Scalability — 5**: No change. Explicitly designed for 20-30+ concurrent agents. Pull-based work queues scale dynamically. No documented ceiling below 10 agents.

Source: AGENTIC-LANDSCAPE.md §2.5 and §7; steveyegge/gastown README architecture section.

**Uncertainty flags**: D1 (no per-run benchmark), D3 (no benchmark), D5 (security details of daemon architecture not fully documented in public sources), D6 (no quality gate documentation found).

---

### oh-my-claudecode

**D1 Cost — 3**: No change from prior audit. Smart routing (Haiku/Sonnet/Opus by task complexity) documented at 30-50% token savings. No separate platform fee. [MEDIUM CONFIDENCE]

Source: byteiota.com/oh-my-claudecode-multi-agent-orchestration-for-claude-code/; AGENTIC-LANDSCAPE.md §4.3.

**D2 Efficiency — 4**: No change. Ultrapilot mode runs up to 5 concurrent Claude Code instances in isolated git worktrees. Community reports of 3-5x speedup. No published wall-clock benchmarks. 5 parallel workers with zero muster overhead is consistent with D2=4 (parallelism evident, no significant serialization).

Source: AGENTIC-LANDSCAPE.md §4.3; byteiota.com oh-my-claudecode overview.

**D3 Accuracy — 2**: No change. No published SWE-Bench benchmark. Autopilot mode removes human checkpoints. [MEDIUM CONFIDENCE]

Source: AGENTIC-LANDSCAPE.md §6 cross-cutting table; MASFT paper (arxiv.org/abs/2503.13657).

**D4 Workflow Rigor — 2**: No change. No file ownership contracts, no frozen interface mechanism, no failure taxonomy. Coordination via shared task list (informal delegation). Role separation via 32 specialist agents partially satisfies D4=3 but without contracts, ownership, or failure classification.

Source: AGENTIC-LANDSCAPE.md §4.3; oh-my-claudecode README.

**D5 Security — 1** *(new dimension)*: oh-my-claudecode is a CLAUDE.md preset with no documented security controls. No SAST integration, no sandboxing (runs in standard Claude Code environment on host machine), no security-focused review step, no documented threat model. The zero-configuration design philosophy means security controls are absent by design — friction is removed, including security friction. The 32 specialist agents execute autonomously (Autopilot mode removes human checkpoints). 0 of 4 D5=5 components. Score 1 (generated code executes without sandboxing or review; no documented security controls).

Source: oh-my-claudecode README (github.com/nicekid1/oh-my-claudecode); AGENTIC-LANDSCAPE.md §4.3 (Autopilot removes human checkpoints); [First-principles reasoning from zero-config design philosophy].

**D6 Quality Checks — 1** *(new dimension)*: No documented test execution, code review step, or spec compliance verification. The shared task list allows agents to move to unclaimed tasks on block, which is resilience, not quality checking. Autopilot mode bypasses human approval gates. No built-in test runner, no review agent, no spec validator. Score 1 (no quality checks — code is produced and delivered with no automated quality gate).

Source: AGENTIC-LANDSCAPE.md §4.3 Limitations; oh-my-claudecode README; [First-principles reasoning — zero-config design, no quality gate documentation found].

**D7 Setup — 5**: No change. Zero-configuration design goal. CLAUDE.md preset, no infrastructure, no binary, no daemon. 858 stars in 24 hours confirms near-zero barrier to first use.

Source: AGENTIC-LANDSCAPE.md §4.3; byteiota.com oh-my-claudecode overview.

**D8 Scalability — 3**: No change. Documented ceiling of 5 instances in Ultrapilot mode. Below D8=4 threshold.

Source: AGENTIC-LANDSCAPE.md §4.3 Limitations.

**Uncertainty flags**: D1 (savings community-reported only), D3 (no benchmark), D5 (security posture reasoned from absence of documentation).

---

### Agent Teams (Anthropic Official)

**D1 Cost — 3**: No change. Standard Claude Code API pricing. Lead agent requires Opus 4.6, adding orchestration-layer cost. No published per-run estimate. [MEDIUM CONFIDENCE]

Source: AGENTIC-LANDSCAPE.md §4.1; TechCrunch "Anthropic releases Opus 4.6" (techcrunch.com/2026/02/05).

**D2 Efficiency — 4**: No change. Native TeammateTool supports up to 8 parallel teammates in isolated git worktrees. Direct inter-agent messaging avoids synchronization wait points. Architecture supports genuine parallel execution. No published wall-clock benchmarks. [MEDIUM CONFIDENCE]

Source: AGENTIC-LANDSCAPE.md §4.1; blog.imseankim.com Claude Code team mode (March 2026).

**D3 Accuracy — 3**: No change. No Agent Teams-specific SWE-Bench result. Underlying model (Opus 4.6) documented at ~49% SWE-Bench Verified for single-agent Claude Code. Coordination overhead and research preview status pull down from model ceiling. [MEDIUM CONFIDENCE]

Source: AGENTIC-LANDSCAPE.md §4.1 and §8.7; SWE-Bench Verified leaderboard data (March 2026).

**D4 Workflow Rigor — 2**: No change. TeammateTool provides team lifecycle management and role separation (Lead vs. teammates). No pre-execution interface contracts, no documented failure taxonomy, no adversarial review step. Code merges only when tests pass (partial quality gate). Consistent with D4=2.

Source: AGENTIC-LANDSCAPE.md §4.1; paddo.dev "Claude Code hidden swarm."

**D5 Security — 2** *(new dimension)*: Agent Teams runs as native Claude Code feature on host machine with standard git worktree isolation per teammate. No documented sandboxing beyond git worktrees. No SAST integration. The Lead agent can issue instructions to teammates without explicit contract freeze — no documented protection against prompt injection via crafted task content. No security-specific review step documented in the research preview. Score 2 (code runs on host machine without documented sandboxing; no security review step; human is primary gate).

Source: AGENTIC-LANDSCAPE.md §4.1; TeammateTool API documentation (13 operations); [First-principles reasoning — research preview, no security documentation found].

**D6 Quality Checks — 2** *(new dimension)*: "Code merges only when tests pass" per AGENTIC-LANDSCAPE.md is a partial quality gate (one condition). No built-in code review agent, no spec compliance verification. Test execution is present but as a single merge condition, not a multi-component gate. Recovery behavior "likely follows single-agent retry behavior" — not a structured quality pipeline. Score 2 (automated test pass/fail present as single gate; no code review step; no spec compliance verification built in to the research preview).

Source: AGENTIC-LANDSCAPE.md §4.1; releasebot.io Claude Code release notes (March 2026).

**D7 Setup — 4**: No change. Native to Claude Code, no external tooling. Activation requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and Opus 4.6 access. First parallel run within 1 hour. Consistent with D7=4.

Source: AGENTIC-LANDSCAPE.md §4.1; TechCrunch Opus 4.6 launch article.

**D8 Scalability — 3**: No change. TeammateTool supports up to 8 teammates. Research preview status means large-scale reliability at 8 agents is unproven. Conservative score. [MEDIUM CONFIDENCE]

Source: AGENTIC-LANDSCAPE.md §4.1 and §6.

**Uncertainty flags**: D3 (no Agent Teams-specific benchmark), D5 (security undocumented for research preview), D6 (quality gate details limited for research preview), D8 (scale reliability unproven at preview stage).

---

### Citadel (SethGammon/Citadel)

**D1 Cost — 3**: No change. No platform fee. Native cost accounting for cost awareness, not cost reduction. Comparable to other Claude Code orchestrators at representative scale. [MEDIUM CONFIDENCE]

Source: github.com/SethGammon/Citadel README.

**D2 Efficiency — 4**: No change. Parallel agents in isolated git worktrees documented as core feature. Discovery relay between waves propagates findings efficiently. Campaign persistence enables immediate session resumption. Four-tier routing (`/do`) dispatches work efficiently. Architecture consistent with genuine concurrent execution. [MEDIUM CONFIDENCE — no timing benchmarks]

Source: github.com/SethGammon/Citadel README.

**D3 Accuracy — 2**: No change. No published SWE-Bench or independent benchmark. Citadel is an orchestration layer; code quality depends on underlying model. [LOW CONFIDENCE]

Source: No benchmark citation found.

**D4 Workflow Rigor — 4**: No change. Campaign persistence (structured state), parallel agents in isolated worktrees, discovery relay between waves, lifecycle hooks, and documented circuit breaker ("stops failure spirals before they burn tokens"). Three of four D4=5 components present. Adversarial review step is absent. Consistent with D4=4.

Source: github.com/SethGammon/Citadel README; Spectrum Protocol README.md §Acknowledgments.

**D5 Security — 2** *(new dimension)*: Citadel is a CLAUDE.md-based protocol running on host machine with local git worktrees. No documented sandboxing. No SAST integration. No security-focused review step documented in available sources (the circuit breaker is a failure prevention mechanism, not a security review). Cost accounting reads Claude Code session files — no security relevance. Score 2 (code runs on host machine without sandboxing; no documented security review step; circuit breaker is quality/cost focused, not security focused). [MEDIUM CONFIDENCE — security posture not addressed in available documentation]

Source: github.com/SethGammon/Citadel README; [First-principles reasoning from Claude Code plugin architecture].

**D6 Quality Checks — 3** *(new dimension)*: Citadel's circuit breaker prevents failure spirals (blocking on repeated failure), and campaign persistence with lifecycle hooks provides structured intervention points. Discovery relay between waves implies some form of output review before passing findings downstream. However, no dedicated test execution gate, no explicit code review agent, and no spec compliance check are documented. The circuit breaker is a failure-prevention mechanism, not a quality gate per se. Score 3 (automated test execution OR code review step, but not both clearly documented; circuit breaker provides partial enforcement; coverage and spec compliance not documented). [MEDIUM CONFIDENCE — quality gate mechanisms not fully documented in available sources]

Source: github.com/SethGammon/Citadel README circuit breaker and lifecycle hooks descriptions.

**D7 Setup — 4**: No change. Plugin-based installation on any codebase. No daemon, no infrastructure beyond Claude Code. First run achievable within 1 hour. [MEDIUM CONFIDENCE]

Source: github.com/SethGammon/Citadel README ("install it as a plugin and it works on any codebase").

**D8 Scalability — 3**: No change. No documented agent count ceiling or scalability guidance. Architectural inference: campaign-based orchestration with worktree isolation consistent with moderate scalability (3-5 agents). No evidence of production use at 6+ agents. [MEDIUM CONFIDENCE — architectural inference]

Source: github.com/SethGammon/Citadel README; [First-principles reasoning].

**Uncertainty flags**: D3 (no benchmark), D5 (security details not documented), D6 (quality gate extent unclear from available documentation), D7 (installation process not fully documented), D8 (no scale evidence).

---

### metaswarm (dsifry/metaswarm)

**D1 Cost — 3**: No change. Gemini 2.5 Pro free tier delegation (1,000 req/day) for review tasks provides genuine cost reduction path. Base implementation uses Claude for implementation agents. Comparable to other Claude Code orchestrators with cost optimization options. [MEDIUM CONFIDENCE]

Source: dsifry.github.io/metaswarm/; github.com/dsifry/metaswarm README.

**D2 Efficiency — 3**: No change. 9-phase workflow with mandatory blocking phase transitions introduces structural serialization. Parallel work units within Orchestrated Execution phase. Per-unit 4-phase loop (IMPLEMENT → VALIDATE → ADVERSARIAL REVIEW → COMMIT) adds overhead. Parallelism with significant orchestration overhead. Consistent with D2=3.

Source: dsifry.github.io/metaswarm/ workflow description; github.com/dsifry/metaswarm USAGE.md.

**D3 Accuracy — 2**: No change. No published SWE-Bench benchmark. Creator claims production-tested across "hundreds of PRs" with 100% coverage enforcement. [MEDIUM CONFIDENCE — no independent benchmark]

Source: github.com/dsifry/metaswarm README.

**D4 Workflow Rigor — 4**: No change. Structured 9-phase workflow with blocking transitions, mandatory adversarial review (fresh reviewer per retry), .coverage-thresholds.json as machine-enforced blocking gate, retry logic with escalation and failure history. Three of four D4=5 components. Missing: formal failure taxonomy with ≥3 distinct types. Consistent with D4=4.

Source: dsifry.github.io/metaswarm/ adversarial review and quality gate documentation.

**D5 Security — 2** *(new dimension)*: metaswarm runs in standard Claude Code / Gemini CLI / Codex CLI environments without documented sandboxing of agent execution. No SAST integration. The adversarial review gate (IMPLEMENT → VALIDATE → ADVERSARIAL REVIEW) is a code quality review by design, but its documented scope is correctness and test coverage, not security vulnerability detection specifically. No documented threat model or prompt injection protection. Score 2 (no sandboxing; code review present but security-specific scope not documented; human is primary security gate). [MEDIUM CONFIDENCE — security scope of adversarial review not explicitly described]

Source: github.com/dsifry/metaswarm README adversarial review documentation; dsifry.github.io/metaswarm/; [First-principles reasoning].

**D6 Quality Checks — 4** *(new dimension)*: metaswarm's quality gate posture is strong for this group. (a) **Test execution gate**: 100% coverage enforcement via .coverage-thresholds.json — machine-enforced blocking gate. (b) **Adversarial code review**: Fresh reviewer (never same as implementer) on each retry cycle — blocking before COMMIT. (c) **Blocking state transitions**: "There is no instruction path from FAIL to COMMIT" — spec compliance is enforced via workflow gates. (d) **Coverage reporting**: .coverage-thresholds.json provides coverage enforcement, not just reporting.

Three of four D6=5 components are strongly documented. The missing component is a dedicated spec/acceptance-criteria compliance check equivalent to Obsidian — the 9-phase workflow enforces coverage and review but does not explicitly verify PLAN.md acceptance criteria. Score 4 (3 of 4 components: automated tests blocking, adversarial review blocking, coverage enforcement; missing: formal spec compliance check post-merge).

Source: dsifry.github.io/metaswarm/ adversarial review and .coverage-thresholds.json documentation; github.com/dsifry/metaswarm README.

**D7 Setup — 3**: No change. INSTALL.md + GETTING_STARTED.md. Multi-tool support (Claude Code, Gemini CLI, Codex CLI) plus external-tools-setup.md implies configuration complexity. 18 specialized agents, 13 skills, 15 commands represent a learning curve. Tutorial required. Consistent with D7=3.

Source: github.com/dsifry/metaswarm INSTALL.md and GETTING_STARTED.md.

**D8 Scalability — 3**: No change. 18 role definitions, not 18 concurrent instances. Sequential phase structure and per-unit adversarial review impose coordination overhead. Architecture optimized for quality over throughput. Practical ceiling likely 3-5 agents before overhead dominates. [MEDIUM CONFIDENCE — architectural inference]

Source: github.com/dsifry/metaswarm README; [First-principles reasoning from 9-phase workflow structure].

**Uncertainty flags**: D3 (no independent benchmark), D5 (security scope of adversarial review not explicitly described), D8 (no scale evidence).

---

### Overstory (jayminwest/overstory)

**D1 Cost — 3**: No change. No platform fee. Cross-runtime routing (11 supported runtimes) allows selecting cheaper models. Per-agent cost analysis commands provide cost visibility. [MEDIUM CONFIDENCE]

Source: github.com/jayminwest/overstory README; deepwiki.com/jayminwest/overstory/8.5-agent-inspection.

**D2 Efficiency — 4**: No change. Each agent in isolated git worktree via tmux with genuine concurrent execution. SQLite WAL mail system (~1-5ms per query) for fast inter-agent messaging. FIFO merge queue. Tiered watchdog confirms continuous operation monitoring. No published wall-clock benchmarks. Architecture consistent with D2=4. [MEDIUM CONFIDENCE]

Source: github.com/jayminwest/overstory README; web search results on Overstory architecture.

**D3 Accuracy — 2**: No change. No published SWE-Bench or independent benchmark. [LOW CONFIDENCE]

Source: No benchmark citation found.

**D4 Workflow Rigor — 3**: No change. Instruction overlays and tool-call guards enforce agent boundaries. Tiered watchdog. FIFO merge queue with 4-tier conflict resolution. Typed protocol messages. No pre-execution interface contracts, no formal failure taxonomy, no adversarial review step. Satisfies D4=3 but not D4=4.

Source: github.com/jayminwest/overstory README; web search results on Overstory architecture.

**D5 Security — 2** *(new dimension)*: Overstory runs each agent in a local tmux session with git worktree isolation — isolation at the filesystem level but not process-level sandboxing. Instruction overlays and tool-call guards restrict agent scope (a form of access control), which is security-relevant. However, no SAST/SCA integration, no security-focused review step, and no documented threat model or injection protection. The tiered watchdog monitors agent health and stall detection, not security. Tool-call guards are the strongest security element: documented in the README as scope enforcement. Score 2 (local machine execution without host-isolation sandboxing; tool-call guards provide partial access control; no SAST or security review step). [MEDIUM CONFIDENCE]

Source: github.com/jayminwest/overstory README (instruction overlays, tool-call guards); deepwiki.com/jayminwest/overstory architecture; [First-principles reasoning].

**D6 Quality Checks — 2** *(new dimension)*: Overstory's architecture focuses on execution orchestration (tmux isolation, merge queue, watchdog) rather than quality gate enforcement. The FIFO merge queue with 4-tier conflict resolution handles merge mechanics, not code quality. The tiered watchdog provides health monitoring, not test execution. No documented built-in test runner, code review agent, or spec compliance verification found in available sources. The `trace` command provides post-hoc observability of agent activity, but this is observability, not a quality gate. Score 2 (tests run only if user configures them; no built-in review step; code review is optional and human-initiated). [MEDIUM CONFIDENCE — quality gate documentation not found in available sources]

Source: github.com/jayminwest/overstory README; deepwiki.com/jayminwest/overstory/8.5-agent-inspection; [First-principles reasoning from architecture documentation].

**D7 Setup — 3**: No change. TypeScript/Node project, npm install, tmux dependency, pluggable AgentRuntime for 11 runtimes adds configuration complexity. INSTALLING.md exists. Tutorial required for runtime adapter model. Consistent with D7=3.

Source: github.com/jayminwest/overstory package.json; deepwiki.com/jayminwest/overstory/2.1-installation.

**D8 Scalability — 4**: No change. Pull-based tmux architecture with isolated worktrees per agent. SQLite WAL mail system for low-latency messaging. FIFO merge queue. Pluggable runtime interface for 11 runtimes suggests design for heterogeneous multi-agent deployment. Tiered watchdog is a fleet health mechanism consistent with larger agent counts. README warns about "compounding error rates, cost amplification" at scale — suggesting developer experience with larger deployments. No documented ceiling below 10 agents. [MEDIUM CONFIDENCE — architectural evidence; no empirical evidence at scale published]

Source: github.com/jayminwest/overstory README; web search results on Overstory SQLite mail architecture.

**Uncertainty flags**: D3 (no benchmark), D5 (security scope of tool-call guards not fully specified), D6 (no quality gate documentation found), D8 (architectural inference only).

---

## Cross-System Observations

**D5 Security — general findings**: All seven systems in this group run on local host machines without process-level sandboxing. This is an architectural characteristic of Claude Code orchestrators (they use git worktrees, not VMs). No system in this group reaches D5=3, let alone D5=4 or D5=5. The security leader in this group is Spectrum, which has a documented /diff-review security gate — the only system with a formal security-focused review step enforced before merge. Systems with zero documented security controls (oh-my-claudecode) correctly score D5=1.

**D6 Quality Checks — general findings**: Spectrum (5) and metaswarm (4) lead this dimension by large margins. Both systems mandate test execution and code review before merge as protocol-enforced blocking gates. Systems without built-in quality gates (Gas Town, oh-my-claudecode, Overstory) score D6=1-2. Agent Teams and Citadel have partial quality gate postures (single condition or partial documentation). The new D6 dimension rewards explicit quality engineering — a dimension where Spectrum's protocol rigor translates directly to score advantage.

**D4 Workflow Rigor — Spectrum maintains sole 5**: No other system in this group documents all four rigor components as enforced protocol elements. Citadel and metaswarm remain at D4=4.

**Ranking summary (v2)**: Spectrum (26) leads this group, followed by Citadel (25), then Gas Town and metaswarm (24 each), Overstory and Agent Teams (23), and oh-my-claudecode (21). The prior leader was Citadel (27); the new dimension weighting shifts the ranking toward systems with formal quality engineering.
