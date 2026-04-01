# Claude Code Ecosystem — 12-Dimension Evaluation
**Spectrum**: 12dim-eval
**Howler**: H1-claude-code
**Date**: 2026-03-31
**Rubric version**: evaluation/12dim-eval/PLAN.md v1.0
**Prior reports**: evaluation/audit-2026/group-claude-code.md, evaluation/eval-v2/group-claude-code.md

---

## Scoring Table

| System | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | Total |
|--------|----|----|----|----|----|----|----|----|----|----|-----|-----|-------|
| Spectrum Protocol | 10 | 10 | 0 | 8 | 6 | 8 | 8 | 8 | 8 | 4 | 8 | 10 | 88 |
| Gas Town | 2 | 2 | 0 | 2 | 10 | 4 | 2 | 2 | 0 | 0 | 0 | 2 | 26 |
| oh-my-claudecode | 2 | 0 | 0 | 10 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 14 |
| Agent Teams (Anthropic) | 2 | 4 | 4 | 8 | 4 | 2 | 2 | 2 | 0 | 0 | 0 | 0 | 28 |
| Citadel | 6 | 6 | 0 | 6 | 6 | 4 | 4 | 4 | 0 | 0 | 0 | 2 | 38 |
| metaswarm | 4 | 4 | 0 | 4 | 4 | 4 | 4 | 4 | 6 | 0 | 0 | 4 | 38 |
| Overstory | 4 | 6 | 0 | 6 | 4 | 2 | 2 | 6 | 0 | 0 | 0 | 2 | 32 |
| ruflo | 4 | 4 | 0 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 0 | 4 | 40 |

---

## Per-System Evidence Notes

---

## Spectrum Protocol

**Category**: Claude Code Ecosystem
**Public source**: /Users/ryan/spectrum-protocol/ (this repository); spectrum/SPECTRUM-OPS.md, spectrum/SPECTRUM.md, README.md
**Prior eval scores**: D1=2, D2=4, D3=2, D4=5, D5=2, D6=5, D7=3, D8=3 (eval-v2)

### D1 -- Task Decomposition Quality
**Score**: 10
**Evidence**: SPECTRUM-OPS.md Phase 1 Muster documents all D1=10 components: (a) explicit file ownership matrix in MANIFEST.md where every file appears exactly once, (b) DAG dependency graph with base_branch/base_commit per node, (c) scope statements and effort/serial-risk tags per Howler, (d) decomposition hazard scan before MANIFEST.md, (e) per-Howler preconditions/postconditions/invariants (full DbC for interface-heavy Howlers, conventions-only for pure-create), (f) adversarial Politico review of decomposition before freeze, finding ownership gaps, contract ambiguities, and decomposition flaws. Zero-overlap guarantee verified during muster and by Politico. Human review of decomposition required before execution. All D1=10 anchor components are present.

### D2 -- Interface Contract Enforcement
**Score**: 10
**Evidence**: SPECTRUM-OPS.md Phase 1 step 10 documents CONTRACT.md with shared types, interfaces, naming conventions, integration points, and per-Howler Design-by-Contract. Step 11 documents White Pre-Check: a pre-freeze factual verification that all referenced files exist and documented signatures match the actual codebase (STALE/MISSING/MISMATCH findings patched before freeze). Step 14 documents adversarial Politico review challenging the contract for ambiguities, gaps, and decomposition flaws before freeze. CONTRACT.md is frozen at drop; Howlers may not modify it. Contract deviations require formal AMENDMENT.md (non-breaking or breaking). All D2=10 anchor components are present: frozen contracts + factual verification + adversarial review + formal amendment protocol.

### D3 -- Benchmark Accuracy
**Score**: 0 [LOW CONFIDENCE]
**Evidence**: No published SWE-Bench Verified score or equivalent benchmark for Spectrum Protocol. README.md documents a gold-comparison evaluation (gold-eval-0331) measuring orchestration quality, not end-to-end code accuracy. No third-party or community benchmark data found. Per rubric: no accuracy data published = score 0.

### D4 -- Setup Complexity
**Score**: 8
**Evidence**: README.md documents a one-line curl installer (`curl -fsSL ... | bash`) and a manual path of copying 3 files plus agents/*.md and tools/seam_check.py. No daemon, no binary, no database, no build step. Core concepts (muster, drop, proving, forge, pax) are learnable from the CHEATSHEET.md and TUTORIAL.md. However, the protocol has a ~550-line ops manual and 7 phases, which requires more than 30 minutes to understand fully for first productive use. Reaping and nano modes reduce ceremony for common cases. The curl one-liner plus tutorial path is consistent with D4=8 (copy files or simple CLI command; core concepts understandable in under 30 minutes for nano/reaping modes). Full-mode first runs require deeper study, but the rubric scores the system's best reasonable onboarding path.

### D5 -- Parallelism and Execution Efficiency
**Score**: 6
**Evidence**: SPECTRUM-OPS.md documents DAG-based dispatch where Howlers are dropped as their dependencies are satisfied (not batch-complete). Three modes: Nano (<1 min startup, 2-3 Howlers), Reaping (~3 min startup, 3-4 Howlers), Full (~8 min startup, 3-8 Howlers). Pre-created git worktrees enable genuine parallel execution. Checkpoint deps (howler-name#types) unblock on STABLE signal, not full completion. The full-mode human approval gate and 8-minute muster add structural overhead. Nano mode achieves sub-3-minute startup but skips quality gates. The representative full-mode case has significant startup overhead (8 min before any worker starts), which prevents reaching D5=8. Reaping mode at ~3 min is consistent with D5=6 (parallel execution with DAG dispatch, startup under 5 minutes in reaping mode, coordination overhead managed).

### D6 -- State Durability and Resumability
**Score**: 8
**Evidence**: SPECTRUM-OPS.md documents CHECKPOINT.json written at every phase transition with defined schema (rain_id, phase, mode, howlers array with per-Howler status, errors, cost_tracking). Per-Howler HOOK.md updated continuously during execution with progress checklist, decisions, blockers, errors, and completion verification. HOOK.md heartbeat every 30 tool calls or 1 hour; 4+ hours without update triggers stuck escalation. Howler death resumes at HOOK.md checkpoint (not phase checkpoint). Resume instructions: "Read HOOK.md and continue. Don't repeat checked-off work. Check Errors Encountered to avoid known dead ends." All D6=8 anchor components present: full durable state with worker-level granularity, per-worker state files updated continuously. Automated resume detection is not present (human must initiate resume), preventing D6=10.

### D7 -- Failure Handling and Recovery
**Score**: 8
**Evidence**: SPECTRUM-OPS.md Phase 4 (The Forge) documents 5 failure types (transient, logical, structural, environmental, conflict) with distinct handling paths (Resume, Retry, Skip, Restructure). Transient failures: Gold may auto-Resume without human confirmation. Circuit breaker: 2 failures on same locus auto-escalate to structural. Orange agent performs root-cause diagnosis on blocked Howlers before recovery is attempted. Post-failure state preserved in HOOK.md for resume. All D7=10 anchor components are present except one nuance: the dedicated diagnosis agent (Orange) is specified and available, but the protocol does not mandate Orange diagnosis before every recovery attempt -- Gold classifies first, then optionally spawns Orange for logical/structural failures. This is functionally equivalent to the D7=10 anchor. However, applying rubric precedence conservatively: Orange is available but not universally mandatory. Score 8 is appropriate; all D7=8 components are clearly met (full typed taxonomy + auto-recovery for transient failures + preserved post-failure state).

### D8 -- Observability and Debuggability
**Score**: 8
**Evidence**: SPECTRUM-OPS.md mandates a status roster printed at every phase transition and after each agent dispatch/completion, showing all agents with glyphs, roles, status symbols, and task context. CHECKPOINT.json tracks per-Howler status across all phases. Per-Howler HOOK.md provides structured per-agent activity log with decisions, seams, blockers, errors, and completion verification. Budget tracking in CHECKPOINT.json provides per-Howler cost breakdown. Phase transitions create a timeline of execution history. The combination of mandatory status roster (real-time roster), CHECKPOINT.json (timeline/phase transitions), per-Howler cost tracking, and structured HOOK.md logs satisfies D8=8 (real-time roster + timeline + per-agent cost breakdown). Missing: no OpenTelemetry export, no streaming dashboard, no time-travel debugging, preventing D8=10.

### D9 -- Pre-Merge Quality Gates
**Score**: 8
**Evidence**: SPECTRUM-OPS.md Phase 3 (The Proving) mandates three gates in parallel before any PR opens: (a) White code review (zero blockers required), (b) Gray test execution (zero failures required; coverage gaps = warning), (c) /diff-review security review (zero criticals required; high/medium = warning in PR description). All three are blocking. Security criticals block merge. This is the D9=8 anchor exactly: triple gate (tests + review + security), all three required, security criticals block, medium findings warn. Coverage thresholds are advisory not machine-enforced, preventing D9=10.

### D10 -- Security Posture
**Score**: 4
**Evidence**: SPECTRUM-OPS.md mandates /diff-review as a security-focused review step before every PR, with security criticals blocking merge. This is a dedicated security review gate (D10=4 anchor). However: no SAST tool integration (Semgrep, CodeQL) documented in the protocol. No sandboxed execution -- Howlers run in local git worktrees on the host machine. No prompt injection protection documented beyond contract scope enforcement. No formal security certification. Score 4 (security review gate exists; no SAST or sandboxing).

### D11 -- Independent Validation and Spec Compliance
**Score**: 8
**Evidence**: SPECTRUM-OPS.md Phase 4 (Pax) documents independent Gold validation: "do NOT trust Howler self-reports. For each Howler, Gold reads 2-3 key files the Howler created/modified and verifies against CONTRACT.md postconditions." Cross-references seams between Howler debriefs. Phase 6 (Triumph) documents Obsidian agent verifying PLAN.md acceptance criteria against merged code, producing SENTINEL-REPORT.md with COMPLIANT/PARTIAL/NON-COMPLIANT verdicts. Contract test stubs (generated from postconditions) are run by Howlers during completion verification. The combination of orchestrator validation (Pax) + formal spec compliance report (SENTINEL-REPORT.md) satisfies D11=8. Missing: automated traceability from spec requirements to test coverage to deployed artifact, preventing D11=10.

### D12 -- Cross-Run Learning and Memory
**Score**: 10
**Evidence**: SPECTRUM-OPS.md Phase 6 (Triumph) mandates Brown drafts LESSONS.md with Known Failure Patterns extracted per structured format (task type, failure mode, signal, mitigation). Gold reviews and commits to ~/.claude/projects/<slug>/memory/LESSONS.md. ENTITIES.md curated after every spectrum. ARCHITECTURE.md is persistent and incremental -- "never regenerated from scratch" -- preserving cross-spectrum knowledge. Phase 1 (Muster) step 3 mandates reading LESSONS.md and ENTITIES.md, with Known Failure Patterns matching current task types injected into Howler drop prompts as KNOWN RISKS. Discovery relay propagates learnings from completed Howlers to dependent Howlers. All D12=10 components present: structured lesson capture + automatic injection into future runs + entity memory (ENTITIES.md) + incremental ARCHITECTURE.md + failure pattern extraction into Howler drop prompts.

---

## Gas Town (steveyegge/gastown)

**Category**: Claude Code Ecosystem
**Public source**: https://github.com/steveyegge/gastown
**Prior eval scores**: D1=3, D2=5, D3=2, D4=3, D5=3, D6=3, D7=2, D8=5 (audit-2026)

### D1 -- Task Decomposition Quality
**Score**: 2
**Evidence**: Gas Town uses pull-based work queues where agents claim tasks from a shared issue tracker (beads/Dolt). Tasks can be divided into subtasks but there is no formal file ownership matrix, no dependency DAG, no scope specification per worker, and no pre-execution hazard analysis. The GUPP (Go Until a Problem Presents) principle means agents execute immediately without structured decomposition. Consistent with D1=2 (basic splitting, no formal ownership or dependency graph).

### D2 -- Interface Contract Enforcement
**Score**: 2
**Evidence**: No pre-execution CONTRACT.md or equivalent frozen interface agreement documented. Agents coordinate through shared task queues and message passing. Git-backed provenance provides attribution after the fact but not pre-flight interface contracts. Naming conventions may exist in documentation but are not formally specified or enforced. Consistent with D2=2 (informal conventions).

### D3 -- Benchmark Accuracy
**Score**: 0 [LOW CONFIDENCE]
**Evidence**: No published SWE-Bench Verified score or independent benchmark for Gas Town. GUPP's aggressive autonomy trades accuracy checkpoints for throughput. No community benchmark data found.

### D4 -- Setup Complexity
**Score**: 2
**Evidence**: Requires Go 1.25+, Git, Dolt, tmux. Multi-step installation: `go install` for `gt` binary plus `bd` (Beads) binary, then `gt install ~/gt --shell`, then `gt daemon start`. Multiple dependencies beyond core LLM. gastown/docs/INSTALLING.md documents the process. AGENTIC-LANDSCAPE.md characterizes it as having "heavy infrastructure requirements." Consistent with D4=2 (significant configuration, compile from source, daemon setup, manual config files).

### D5 -- Parallelism and Execution Efficiency
**Score**: 10
**Evidence**: Gas Town is purpose-built for maximum parallel throughput. GUPP eliminates orchestrator approval gates. Pull-based work queues enable genuine concurrent execution across 20-30+ agents. Daemon architecture means near-zero startup overhead -- agents pull work immediately. No muster ceremony, no mandatory human gate. This is the D5=10 anchor exactly: continuous parallel execution, no muster ceremony, coordination overhead near-zero via persistent daemon.

### D6 -- State Durability and Resumability
**Score**: 4
**Evidence**: Git-backed hooks (persistent work queues) survive agent restarts. Dolt issue tracker maintains state across sessions. Agents can resume from prior queue state. However, no structured per-agent checkpoint file (HOOK.md equivalent) with continuous updates is documented. Resumption requires the daemon and Dolt to be running. The state survives session death via git-backed hooks and Dolt, and structured checkpoints exist at the queue level, but no defined per-worker resume protocol. Consistent with D6=4 (checkpoint-based persistence at phase/queue level; resumption possible but requires reading checkpoint artifacts).

### D7 -- Failure Handling and Recovery
**Score**: 2
**Evidence**: Three-tier watchdog (Deacon) provides health monitoring with escalating interventions for stalled agents. Stall detection is autonomous. However, no formal failure taxonomy (watchdog detects stalls but does not classify failure types into distinct categories with different handling paths). Recovery is retry-based with escalation tiers, not typed. Consistent with D7=2 (basic retry with no failure classification).

### D8 -- Observability and Debuggability
**Score**: 2
**Evidence**: Git-backed provenance records on every action provide structured attributable logs after the fact. `gt status` CLI provides basic status. Deacon health reports monitor agent health. No documented real-time dashboard, no per-agent timeline, no replay capability. Status during execution is limited to CLI output. Consistent with D8=2 (basic logging, text output to console, no structured per-agent attribution in real-time).

### D9 -- Pre-Merge Quality Gates
**Score**: 0
**Evidence**: No documented built-in code review step, test execution gate, or security review before code is committed. GUPP philosophy means agents proceed until blocked -- code is produced and committed with human review as the only external gate. No automated quality checks enforced by the framework. Consistent with D9=0 (no quality gates; worker output accepted without verification by the framework).

### D10 -- Security Posture
**Score**: 0 [LOW CONFIDENCE]
**Evidence**: No documented security features. Agents run on local machine via Go binary and daemon with host filesystem access. No SAST integration, no sandboxing, no security-focused review step. Git-backed provenance provides attribution, not prevention. No threat model documented.

### D11 -- Independent Validation and Spec Compliance
**Score**: 0
**Evidence**: No documented independent validation of worker output against specifications. No spec compliance agent or report. Worker self-reports (via completed beads) are the primary completion signal. Consistent with D11=0 (no independent validation; worker self-reports accepted).

### D12 -- Cross-Run Learning and Memory
**Score**: 2
**Evidence**: Git-backed state persists across sessions and Dolt issue tracker maintains historical data. Some state carries forward but no structured lesson extraction protocol, no LESSONS.md equivalent, no entity memory, no automatic injection of prior learnings into new runs. Consistent with D12=2 (ad-hoc memory; some persistence but no structured extraction or application protocol).

---

## oh-my-claudecode

**Category**: Claude Code Ecosystem
**Public source**: https://github.com/Yeachan-Heo/oh-my-claudecode
**Prior eval scores**: D1=3, D2=4, D3=2, D4=2, D5=1, D6=1, D7=5, D8=3 (eval-v2)

### D1 -- Task Decomposition Quality
**Score**: 2
**Evidence**: oh-my-claudecode uses a shared task list where agents claim tasks. Up to 5 concurrent Claude Code instances in Ultrapilot mode. Tasks can be divided but there is no formal file ownership matrix, no dependency graph, no scope specification per worker, and no decomposition hazard analysis. 32 specialist agents provide role separation but not structured decomposition. Consistent with D1=2 (basic splitting without formal ownership or dependency graph).

### D2 -- Interface Contract Enforcement
**Score**: 0
**Evidence**: No pre-execution interface contracts documented. No shared types file. No frozen contract mechanism. Coordination is via shared task list with informal delegation. No CONTRACT.md equivalent. Consistent with D2=0 (no contracts; workers share no formal interface agreements).

### D3 -- Benchmark Accuracy
**Score**: 0 [LOW CONFIDENCE]
**Evidence**: No published SWE-Bench or independent benchmark. Autopilot mode removes human checkpoints. No community benchmark data. Per rubric: no accuracy data = score 0.

### D4 -- Setup Complexity
**Score**: 10
**Evidence**: Zero-configuration design goal. Works as a CLAUDE.md preset with no infrastructure dependencies. No binary, no daemon, no build step. 858 stars in 24 hours confirms near-zero barrier to first use. Consistent with D4=10 (zero-config, works immediately after install with no required configuration, discoverable conventions).

### D5 -- Parallelism and Execution Efficiency
**Score**: 2
**Evidence**: Ultrapilot mode runs up to 5 concurrent Claude Code instances in isolated git worktrees. Community reports of 3-5x speedup. No muster overhead. However, no structured parallelism model -- no dependency-aware scheduling, no DAG dispatch. Workers run concurrently but coordination is unstructured (shared task list). Ceiling of 5 instances. Consistent with D5=2 (limited parallelism; some concurrent execution but no structured parallelism model).

### D6 -- State Durability and Resumability
**Score**: 0
**Evidence**: No documented state persistence mechanism. No checkpoint files. No per-worker state files. No resume protocol. If a session dies, there is no documented way to resume from a checkpoint. The shared task list allows agents to move to unclaimed tasks but this is resilience, not resumability. Consistent with D6=0 (no persistent state; session death requires complete restart).

### D7 -- Failure Handling and Recovery
**Score**: 0
**Evidence**: No structured failure recovery documented. No failure classification. No retry mechanism with failure typing. No circuit breaker. If an agent fails, the task remains unclaimed on the shared list. No escalation protocol. Consistent with D7=0 (no failure handling; system halts or undefined behavior on worker failure).

### D8 -- Observability and Debuggability
**Score**: 0
**Evidence**: No documented dashboard, structured logging, or per-agent attribution. Supervisor monitors progress but the mechanism is not described in technical detail. User observability is through standard Claude Code output per instance. No trace IDs, no replay. Consistent with D8=0 (no observability; no logs, traces, or status reporting during execution).

### D9 -- Pre-Merge Quality Gates
**Score**: 0
**Evidence**: No documented test execution, code review step, or security review before merge. Autopilot mode bypasses human approval gates. No built-in quality gate of any kind. Consistent with D9=0 (no quality gates).

### D10 -- Security Posture
**Score**: 0
**Evidence**: No security features documented. No SAST, no sandboxing, no security review step, no threat model. Zero-configuration philosophy means security controls are absent by design. Autopilot removes human checkpoints. Consistent with D10=0 (no security features documented).

### D11 -- Independent Validation and Spec Compliance
**Score**: 0
**Evidence**: No independent validation mechanism. No spec compliance check. Worker output accepted directly. Consistent with D11=0.

### D12 -- Cross-Run Learning and Memory
**Score**: 0
**Evidence**: No documented cross-run learning mechanism. No LESSONS.md, no entity memory, no structured lesson capture. Each run starts from the CLAUDE.md preset without prior-run context. Consistent with D12=0 (no memory; each run starts from zero).

---

## Agent Teams (Anthropic Official)

**Category**: Claude Code Ecosystem
**Public source**: https://code.claude.com/docs/en/agent-teams; TeammateTool API
**Prior eval scores**: D1=3, D2=4, D3=3, D4=2, D5=2, D6=2, D7=4, D8=3 (eval-v2)

### D1 -- Task Decomposition Quality
**Score**: 2
**Evidence**: TeammateTool supports spawning up to 8 parallel teammates with task assignment. The Lead agent decomposes work but there is no formal file ownership matrix, no DAG specification, no scope statements per worker, and no decomposition hazard analysis. Decomposition is implicit in the Lead's reasoning, not a structured artifact. Consistent with D1=2 (basic splitting; work can be divided but no formal ownership or dependency graph).

### D2 -- Interface Contract Enforcement
**Score**: 4
**Evidence**: Agent Teams documentation describes the Lead providing task context and coordination via TeammateTool messaging (13 operations). Teammates can communicate directly. The Lead implicitly defines shared expectations, but there is no formal CONTRACT.md or frozen interface document. The structured TeammateTool API provides a shared coordination protocol (spawn, assign, message, check_status), which functions as a shared interface system. However, compliance is not verified pre-execution. Consistent with D2=4 (shared interface system exists; workers expected to follow but compliance not verified).

### D3 -- Benchmark Accuracy
**Score**: 4
**Evidence**: No Agent Teams-specific SWE-Bench result. The underlying model (Opus 4.6) is documented at ~49% SWE-Bench Verified for single-agent Claude Code. Agent Teams adds coordination overhead that may reduce effective accuracy. The ~49% figure is for the base model, not the multi-agent system. Consistent with D3=4 (official results below 40% for the multi-agent system itself, but the base model exceeds 40%; conservative score applied since Agent Teams-specific results are unavailable). [LOW CONFIDENCE]

### D4 -- Setup Complexity
**Score**: 8
**Evidence**: Native to Claude Code -- no external tooling, no worktree scripts, no binary. Activation requires setting `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and having Opus 4.6 access (requires Claude Teams/Enterprise plan or API). One environment variable + API access. First parallel run achievable in minutes once prerequisites met. Consistent with D4=8 (simple CLI command / environment variable; core concepts understandable quickly).

### D5 -- Parallelism and Execution Efficiency
**Score**: 4
**Evidence**: Native TeammateTool supports up to 8 parallel teammates in isolated git worktrees. Direct inter-agent messaging during execution. No muster ceremony. However, the Lead agent must manually coordinate dispatch, which is not DAG-driven -- there is no structured dependency graph or automatic dispatch as dependencies complete. Research preview stability concerns. Consistent with D5=4 (structured parallelism; workers run in parallel with some coordination, but no DAG dispatch).

### D6 -- State Durability and Resumability
**Score**: 2
**Evidence**: Research preview documentation does not formalize state persistence or resume behavior. Teammates operate in git worktrees (code survives), but no structured checkpoint system, no per-teammate state file, no defined resume protocol. If a session dies, manual reconstruction is required based on worktree contents. Consistent with D6=2 (partial persistence; some state survives but resumption requires manual reconstruction).

### D7 -- Failure Handling and Recovery
**Score**: 2
**Evidence**: Research preview does not document failure classification or typed recovery. Error handling "likely follows single-agent retry behavior per teammate" per prior audit. No circuit breaker, no failure taxonomy. Teammates merge only when tests pass (partial failure gate). Consistent with D7=2 (basic retry; failed workers retried with no failure classification).

### D8 -- Observability and Debuggability
**Score**: 2
**Evidence**: TeammateTool `check_status` operation provides polling capability for teammate status. No documented real-time dashboard, no per-agent timeline, no trace IDs. Internal observability not public for research preview. The `check_status` polling provides basic structured status. Consistent with D8=2 (basic logging; status can be polled but no structured per-agent attribution or dashboard).

### D9 -- Pre-Merge Quality Gates
**Score**: 0
**Evidence**: "Code merges only when tests pass" per prior audit is a single merge condition, not a quality gate enforced by Agent Teams itself -- it is standard Git/CI behavior. No built-in code review agent, no security review step, no multi-gate pipeline native to Agent Teams. Consistent with D9=0 (no quality gates native to the framework; external CI may apply but is not part of Agent Teams).

### D10 -- Security Posture
**Score**: 0 [LOW CONFIDENCE]
**Evidence**: No documented security features specific to Agent Teams. Runs on host machine with git worktree isolation per teammate. No SAST, no sandboxing, no security review step. Research preview with no security documentation. Consistent with D10=0.

### D11 -- Independent Validation and Spec Compliance
**Score**: 0
**Evidence**: No documented independent validation of teammate output against specifications. No spec compliance agent. Lead may review teammate output but this is informal and not protocol-enforced. Consistent with D11=0.

### D12 -- Cross-Run Learning and Memory
**Score**: 0
**Evidence**: No documented cross-run learning mechanism native to Agent Teams. Each team session starts fresh. Claude Code's auto-memory feature may persist some context, but this is not Agent Teams-specific. No structured lesson extraction or entity memory. Consistent with D12=0 (no memory; each run starts from zero).

---

## Citadel (SethGammon/Citadel)

**Category**: Claude Code Ecosystem
**Public source**: https://github.com/SethGammon/Citadel
**Prior eval scores**: D1=3, D2=4, D3=2, D4=4, D5=2, D6=3, D7=4, D8=3 (eval-v2)

### D1 -- Task Decomposition Quality
**Score**: 6
**Evidence**: Citadel documents four-tier routing (/do) that dispatches work across tiers with structured routing decisions. Campaign persistence implies structured task decomposition. Discovery relay between waves propagates findings. Parallel agents in isolated worktrees with lifecycle hooks. Spectrum's README acknowledges Citadel for "machine-verifiable phase conditions." The four-tier routing provides structured decomposition with defined scope per tier. File ownership is implied by worktree isolation but not formally documented as a matrix. No adversarial review. Consistent with D6 (formal decomposition with dependency ordering and implicit file ownership, human review via campaign structure, but no hazard scan or DbC).

### D2 -- Interface Contract Enforcement
**Score**: 6
**Evidence**: Citadel's campaign persistence and lifecycle hooks provide a structured coordination framework. Discovery relay between waves functions as a coordination protocol. Machine-verifiable phase conditions (acknowledged in Spectrum's README) imply formal phase transition requirements -- a form of contract enforcement. Circuit breaker enforces behavioral contracts. However, no documented frozen CONTRACT.md equivalent and no adversarial review of contracts. Consistent with D2=6 (formal coordination framework with enforced phase conditions; workers may not bypass phase gates; but no factual verification or adversarial review).

### D3 -- Benchmark Accuracy
**Score**: 0 [LOW CONFIDENCE]
**Evidence**: No published SWE-Bench or independent benchmark. Citadel is an orchestration layer; accuracy depends on underlying model. No community benchmark data found.

### D4 -- Setup Complexity
**Score**: 6
**Evidence**: Described as a plugin installable on any codebase ("install it as a plugin and it works on any codebase" per README). No daemon, no Go binary, no infrastructure beyond Claude Code. QUICKSTART.md exists. Plugin installation + minimal config is consistent with D4=6 (package install + minimal config; works with a short getting-started guide).

### D5 -- Parallelism and Execution Efficiency
**Score**: 6
**Evidence**: Parallel agents in isolated git worktrees documented as core feature. Discovery relay between waves means findings propagate as waves complete -- a form of dependency-aware dispatch (not full DAG, but wave-based). Campaign persistence enables immediate session resumption. Four-tier routing dispatches work efficiently with ~2.5% overhead (~500 tokens at Tier 4 only). Wave-based dispatch with low overhead is consistent with D5=6 (parallel execution with wave dispatch, startup under 5 minutes, coordination overhead managed).

### D6 -- State Durability and Resumability
**Score**: 4
**Evidence**: Campaign persistence across sessions is a core feature -- state survives session death and the next session resumes from prior campaign state. However, no documented per-agent state file (HOOK.md equivalent) with continuous updates. Campaign-level persistence provides checkpoint-based resumption but not worker-level granularity. Resumption is possible via campaign state but requires reading campaign artifacts. Consistent with D6=4 (checkpoint-based persistence at campaign level; resumption possible but not at per-worker granularity).

### D7 -- Failure Handling and Recovery
**Score**: 4
**Evidence**: Circuit breaker explicitly documented ("stops failure spirals before they burn tokens"). Campaign persistence means failure state persists. Lifecycle hooks provide intervention points. Discovery relay passes context to downstream agents. However, no formal multi-type failure taxonomy (the circuit breaker is a single mechanism, not typed classification). Retry with escalation present but not typed. Consistent with D7=4 (classified retry with at least 2 types implicit in circuit breaker behavior -- proceed vs. halt -- with circuit breaker preventing cascading failures).

### D8 -- Observability and Debuggability
**Score**: 4
**Evidence**: Native cost accounting reads Claude Code session files for per-session, per-campaign, and per-agent cost breakdowns. Campaign state provides structured audit trail. Cost observability is well-documented. Execution observability (what agents are doing mid-run) is less documented. Per-agent cost attribution is structured and specific. Consistent with D8=4 (structured per-agent logging via cost accounting; status inferable from campaign state).

### D9 -- Pre-Merge Quality Gates
**Score**: 0 [LOW CONFIDENCE]
**Evidence**: No documented multi-gate quality pipeline native to Citadel. The circuit breaker prevents failure spirals but is not a pre-merge quality gate. No documented test execution gate, code review agent, or security review step native to the framework. Consistent with D9=0. Quality gates may be configured by the user but are not enforced by Citadel itself.

### D10 -- Security Posture
**Score**: 0 [LOW CONFIDENCE]
**Evidence**: No documented security features. Runs on host machine with local git worktrees. No SAST, no sandboxing, no security review step. Consent system gates external actions (pushes, PRs), which is a safety feature but not a security review. Consistent with D10=0.

### D11 -- Independent Validation and Spec Compliance
**Score**: 0 [LOW CONFIDENCE]
**Evidence**: No documented independent validation of worker output against specifications. Machine-verifiable phase conditions validate phase transitions but not output correctness against a spec. No spec compliance agent or report. Consistent with D11=0.

### D12 -- Cross-Run Learning and Memory
**Score**: 2
**Evidence**: Campaign persistence preserves state across sessions, which provides some continuity. Discovery relay between waves propagates findings within a campaign. However, no documented structured lesson extraction, no LESSONS.md equivalent, no entity memory, no automatic injection of learnings into future campaigns. Consistent with D12=2 (ad-hoc memory; state persists but no structured extraction or application protocol).

---

## metaswarm (dsifry/metaswarm)

**Category**: Claude Code Ecosystem
**Public source**: https://github.com/dsifry/metaswarm; https://dsifry.github.io/metaswarm/
**Prior eval scores**: D1=3, D2=3, D3=2, D4=4, D5=2, D6=4, D7=3, D8=3 (eval-v2)

### D1 -- Task Decomposition Quality
**Score**: 4
**Evidence**: metaswarm's 9-phase workflow includes a Work Unit Decomposition phase that breaks work into parallel units. Structured scope per work unit. 18 specialized agents with defined roles. However, no formal file ownership matrix documented, no DAG dependency graph (phases are sequential with parallel work units within), and no adversarial review of decomposition. Consistent with D1=4 (structured decomposition; tasks have defined scope and dependency ordering, but file ownership implied rather than formally enforced).

### D2 -- Interface Contract Enforcement
**Score**: 4
**Evidence**: metaswarm enforces cross-model review ("the writer is always reviewed by a different model"). .coverage-thresholds.json is a machine-enforced configuration that workers must satisfy. Blocking state transitions ("there is no instruction path from FAIL to COMMIT") enforce behavioral contracts. However, no frozen CONTRACT.md equivalent, no pre-execution shared types file, and no factual verification step. Consistent with D2=4 (shared configuration and behavioral expectations exist; workers expected to follow but no frozen contract document).

### D3 -- Benchmark Accuracy
**Score**: 0 [LOW CONFIDENCE]
**Evidence**: No published SWE-Bench or independent benchmark. Creator claims production-tested across hundreds of PRs with 100% coverage enforcement. This is strong production evidence but not an independent benchmark. Per rubric: no benchmark data published = score 0. The production claims would support D3=2 but "architectural reasoning" is insufficient without accuracy data.

### D4 -- Setup Complexity
**Score**: 4
**Evidence**: INSTALL.md and GETTING_STARTED.md exist. Supports Claude Code, Gemini CLI, and Codex CLI. 18 specialized agents, 13 skills, 15 commands represent substantial framework knowledge. External-tools-setup.md implies additional configuration. Standard package/file install with non-trivial learning curve. Consistent with D4=4 (standard install; requires reading documentation to configure; non-trivial learning curve).

### D5 -- Parallelism and Execution Efficiency
**Score**: 4
**Evidence**: Within the Orchestrated Execution phase, parallel work units are supported. However, the 9-phase workflow is sequential at the phase level with mandatory blocking transitions (Design Review Gate, Final Review Gate). Per-unit 4-phase loop (IMPLEMENT, VALIDATE, ADVERSARIAL REVIEW, COMMIT) adds per-unit overhead. Parallelism exists within phases but overall structure is heavily sequentialized. Consistent with D5=4 (structured parallelism within phases; workers run in parallel but coordination overhead is moderate due to sequential phase structure).

### D6 -- State Durability and Resumability
**Score**: 4
**Evidence**: BEADS task tracking provides structured state persistence. Git-native knowledge base preserves work state. The 9-phase workflow with blocking transitions creates implicit checkpoints at each phase boundary. However, no documented per-agent continuous state file or defined resume protocol. State survives but resumption requires understanding the phase structure. Consistent with D6=4 (checkpoint-based persistence at phase transitions; resumption possible but requires reading artifacts manually).

### D7 -- Failure Handling and Recovery
**Score**: 4
**Evidence**: Retry with fresh reviewer (never the same agent) up to 3 times before escalation. Full failure history passed to human on escalation. Blocking state transitions prevent silent failure propagation ("no instruction path from FAIL to COMMIT"). However, no formal multi-type failure taxonomy (same 3-retry path regardless of failure type). Consistent with D7=4 (classified retry: the system distinguishes pass/fail/concerns/rework as at least 2 types with distinct behavior; circuit-breaker-like escalation after 3 retries).

### D8 -- Observability and Debuggability
**Score**: 4
**Evidence**: Structured per-phase artifacts (coverage reports, review outputs) provide post-hoc observability. BEADS task tracking attributes work to agents. The 4-level gate output (PASS/CONCERNS/REWORK/FAIL) is a structured per-agent status indicator. However, no documented real-time dashboard, no timeline view, no per-agent cost breakdown. Consistent with D8=4 (structured per-agent logging via BEADS and phase artifacts; status inferable from structured outputs).

### D9 -- Pre-Merge Quality Gates
**Score**: 6
**Evidence**: metaswarm mandates: (a) test execution with 100% coverage enforcement via .coverage-thresholds.json (machine-enforced blocking gate), (b) adversarial code review by a fresh reviewer (never the implementer) on each retry cycle, (c) cross-model review (writer reviewed by different model). Blocking state transitions enforce all gates: "There is no instruction path from FAIL to COMMIT." The coverage enforcement is machine-enforced via configurable threshold. However, no dedicated security review step. D9=8 requires "triple gate (tests + review + security)" which is not met without a security component. Consistent with D9=6 (multi-gate pipeline: tests + code review both required before merge; either gate can block; machine-enforced coverage is an exceptional strength but does not substitute for the missing security gate).

### D10 -- Security Posture
**Score**: 0 [LOW CONFIDENCE]
**Evidence**: No documented security features specific to metaswarm. The adversarial review gate focuses on correctness and coverage, not security vulnerabilities. No SAST, no sandboxing, no threat model. Runs in standard Claude Code / Gemini CLI environment. Consistent with D10=0.

### D11 -- Independent Validation and Spec Compliance
**Score**: 0
**Evidence**: The adversarial review gate validates code quality and test coverage but is not spec compliance verification against acceptance criteria. No post-merge spec compliance agent or report. The coverage gate validates a quantitative threshold but not that the specification was met. Consistent with D11=0 (no independent validation against spec).

### D12 -- Cross-Run Learning and Memory
**Score**: 4
**Evidence**: metaswarm describes itself as "self-improving" with a git-native knowledge base. The 9th phase (Closure & Learning) captures learnings. BEADS tracking preserves task history. Per-PR self-reflect during merge (acknowledged in Spectrum's ops manual as a pattern adopted from metaswarm). Structured lesson capture exists but automatic injection into future runs is not documented. Consistent with D12=4 (structured lesson capture; available for future runs but not automatically injected).

---

## Overstory (jayminwest/overstory)

**Category**: Claude Code Ecosystem
**Public source**: https://github.com/jayminwest/overstory
**Prior eval scores**: D1=3, D2=4, D3=2, D4=3, D5=2, D6=2, D7=3, D8=4 (eval-v2)

### D1 -- Task Decomposition Quality
**Score**: 4
**Evidence**: Overstory uses an Orchestrator, Team Lead, Specialist Workers hierarchy with instruction overlays and tool-call guards that enforce agent boundaries. Tasks are decomposed across worker agents with defined scope via overlays. Pluggable AgentRuntime interface for 11 runtimes suggests structured task routing. However, no formal file ownership matrix, no DAG dependency graph (FIFO merge queue implies sequential merge, not dependency-driven dispatch), and no adversarial review. Consistent with D1=4 (structured decomposition; tasks have scope and ordering but ownership is implied, not formally enforced).

### D2 -- Interface Contract Enforcement
**Score**: 6
**Evidence**: Instruction overlays and tool-call guards enforce agent boundaries -- a form of scope/interface enforcement. Typed protocol messages for inter-agent communication provide structured interface agreements. FIFO merge queue with 4-tier conflict resolution enforces integration standards. Spectrum's README acknowledges Overstory for "structural tool enforcement." However, no frozen contract document and no adversarial review. Tool-call guards are a form of machine enforcement of agent scope boundaries. Consistent with D2=6 (formal coordination framework with enforced scope boundaries; workers cannot bypass tool-call guards; violations are structural not discretionary).

### D3 -- Benchmark Accuracy
**Score**: 0 [LOW CONFIDENCE]
**Evidence**: No published SWE-Bench or independent benchmark. No community benchmark data found.

### D4 -- Setup Complexity
**Score**: 6
**Evidence**: TypeScript/Node project requiring npm install. tmux dependency for agent execution. Pluggable AgentRuntime interface for 11 runtimes. INSTALLING.md documentation exists. Initialization creates .overstory/ directory. SessionStart and UserPromptSubmit hooks auto-configured. Package install + tmux + initialization is a reasonable onboarding path. Consistent with D4=6 (package install + minimal config; works with a short getting-started guide; reasonable learning curve given hook auto-configuration).

### D5 -- Parallelism and Execution Efficiency
**Score**: 4
**Evidence**: Each agent runs in an isolated git worktree via tmux with genuine concurrent execution. SQLite WAL mail system (~1-5ms per query) for fast inter-agent messaging. FIFO merge queue handles branch merges. Tiered watchdog confirms continuous operation. However, dispatch is not DAG-driven -- agents are spawned and coordinate through mail, not through a dependency graph. Merge is FIFO, not dependency-ordered. Consistent with D5=4 (structured parallelism; workers run in parallel with coordination overhead moderate; no DAG dispatch).

### D6 -- State Durability and Resumability
**Score**: 2
**Evidence**: Git-backed architecture means code changes survive agent death. SQLite mail system persists messages. However, no documented per-agent checkpoint file or defined resume protocol. If a session dies, the git state persists but there is no structured resumption mechanism -- manual reconstruction from git state and mail queue is required. Consistent with D6=2 (partial persistence; state survives but resumption requires manual reconstruction).

### D7 -- Failure Handling and Recovery
**Score**: 2
**Evidence**: Tiered watchdog (Tier 0 mechanical daemon, Tier 1 AI-assisted triage, Tier 2 monitor) provides automated health monitoring. Triage result type ({verdict, fallback, reason}) implies multiple recovery options. However, no formal failure taxonomy with 3+ named types and distinct handling paths. Watchdog escalation tiers approximate retry behavior but are not typed. Consistent with D7=2 (basic retry; health monitoring detects failures and retries with escalation but no formal classification).

### D8 -- Observability and Debuggability
**Score**: 6
**Evidence**: `trace` command provides agent/bead timeline viewing (replay-class observability). Per-agent token/cost analysis with multiple breakdown modes (--live, --by-capability, --last). Tiered watchdog provides real-time fleet health monitoring. Structured triage output ({verdict, fallback, reason}). The combination of timeline trace, per-agent cost attribution, and real-time watchdog health monitoring satisfies D8=6 (real-time status roster via watchdog + per-agent log export + trace command for history).

### D9 -- Pre-Merge Quality Gates
**Score**: 0 [LOW CONFIDENCE]
**Evidence**: No documented built-in test execution gate, code review agent, or security review step. The FIFO merge queue handles merge mechanics, not quality. The watchdog monitors health, not output quality. The `trace` command provides post-hoc observability, not a gate. Consistent with D9=0 (no quality gates native to the framework).

### D10 -- Security Posture
**Score**: 0
**Evidence**: No documented security features. Local tmux execution without host-isolation sandboxing. Instruction overlays and tool-call guards restrict agent scope (partial access control) but are not security features per se. No SAST, no security review step. SECURITY.md exists in the repo but documents vulnerability reporting, not runtime security features. Consistent with D10=0.

### D11 -- Independent Validation and Spec Compliance
**Score**: 0
**Evidence**: No documented independent validation of worker output against specifications. No spec compliance agent or report. Worker completion inferred from task state. Consistent with D11=0.

### D12 -- Cross-Run Learning and Memory
**Score**: 2
**Evidence**: Git-backed architecture and SQLite mail persist historical data. `trace` command allows reviewing past runs. However, no documented structured lesson extraction, no LESSONS.md equivalent, no entity memory, no automatic injection of prior learnings. Consistent with D12=2 (ad-hoc memory; historical data persists but no structured extraction protocol).

---

## ruflo (ruvnet/ruflo)

**Category**: Claude Code Ecosystem
**Public source**: https://github.com/ruvnet/ruflo
**Prior eval scores**: N/A (not in prior evaluations)

### D1 -- Task Decomposition Quality
**Score**: 4
**Evidence**: ruflo (formerly Claude Flow) coordinates 60+ pre-built agents across multiple DDD contexts. Tasks are decomposed into work units dispatched to specialized agents. Tier-based task classification (simple/medium/complex) with routing to appropriate models. However, no formal file ownership matrix documented, no DAG dependency graph, and no adversarial review of decomposition. The tiered routing provides structured decomposition but without formal ownership guarantees. Consistent with D1=4 (structured decomposition with scope and ordering but ownership not formally enforced).

### D2 -- Interface Contract Enforcement
**Score**: 4
**Evidence**: ruflo has 259 MCP tools and 8 AgentDB controllers providing structured interfaces between agents. Hooks (pre-edit guidance, post-edit verification) enforce behavioral contracts. However, no documented frozen contract equivalent, no pre-execution shared types document, and no factual verification or adversarial review. Consistent with D2=4 (shared interface systems exist through MCP tools and hooks; workers expected to follow but no frozen contract or compliance verification).

### D3 -- Benchmark Accuracy
**Score**: 0 [LOW CONFIDENCE]
**Evidence**: No published SWE-Bench or independent benchmark. Claims "production-tested" but no independent accuracy data. Per rubric: no accuracy data = score 0.

### D4 -- Setup Complexity
**Score**: 4
**Evidence**: ruflo v3.5 has substantial infrastructure: 5,900+ commits, 259 MCP tools, 60+ agents, 8 AgentDB controllers. Installation likely requires configuration of MCP tools and agent definitions. Wiki documentation extensive (session persistence, API reference, memory system, hooks). The framework's breadth (58 agents across 12 DDD contexts) implies significant learning curve. Consistent with D4=4 (standard install; requires reading documentation to configure; non-trivial learning curve).

### D5 -- Parallelism and Execution Efficiency
**Score**: 4
**Evidence**: ruflo coordinates multi-agent swarms with parallel execution. Tiered task classification routes simple tasks to WebAssembly transforms (near-zero latency) and complex tasks to full agent swarms. Claude Code Agent Teams integration enables parallel teammates. However, no documented DAG dispatch or dependency-aware scheduling native to ruflo. Parallelism exists but coordination model is not formally structured. Consistent with D5=4 (structured parallelism; workers run in parallel with dependency awareness through Agent Teams integration but moderate coordination overhead).

### D6 -- State Durability and Resumability
**Score**: 4
**Evidence**: ruflo documents automated checkpointing that tracks every edit, task, and session. Session persistence maintains complete development environment state including processes, file contexts, and working directories. Workflow state management with checkpoint data in database schema. Instant rollback to any tagged state. However, the checkpoint system is at session/workflow level, not per-worker continuous state files. Resumption uses checkpoints but the granularity is session, not individual worker. Consistent with D6=4 (checkpoint-based persistence at session/workflow level; structured checkpoints enable resumption).

### D7 -- Failure Handling and Recovery
**Score**: 4
**Evidence**: ruflo claims fault tolerance as a key capability. Self-learning and memory optimization enable recovery. Checkpoint rollback provides recovery mechanism. However, no documented formal failure taxonomy with named types and distinct handling paths. Recovery appears checkpoint-based (rollback to last good state) rather than typed (resume/retry/skip/restructure). Consistent with D7=4 (classified retry: the system distinguishes recoverable vs. non-recoverable failures through checkpoint rollback, with at least 2 implicit types).

### D8 -- Observability and Debuggability
**Score**: 4
**Evidence**: GitHub Hooks publish every operation, task start, memory change, and context update. Full historical logging of every sub-agent action. Per-agent tracking via AgentDB controllers. However, no documented real-time dashboard or timeline view. Logging is structured and per-agent but appears post-hoc. Consistent with D8=4 (structured per-agent logging; each agent's output attributed and logged separately; status inferable from logs).

### D9 -- Pre-Merge Quality Gates
**Score**: 4
**Evidence**: ruflo includes enforcement gates (enforcement-gates.md tutorial in repository). Hooks provide preventive guidance (before edits) and verification feedback (after edits). Quality engineering capabilities include TDD and coverage analysis. However, the specific gate pipeline (what blocks what) is not clearly documented in public sources as a multi-gate requirement. Consistent with D9=4 (automated test execution exists; failures block; but not clearly a multi-gate pipeline with review + security).

### D10 -- Security Posture
**Score**: 4
**Evidence**: ruflo documents SAST, DAST, and dependency scanning as agent capabilities. Enterprise-grade security with input validation and sandboxing claimed. CLAUDE MD Security Audit exists as wiki page. However, it is important to note documented security concerns: tool descriptions contained hidden instructions directing the LLM to add the repository owner as a contributor -- identified as prompt injection via MCP tool descriptions (Issue #1375). v3.5.40 addressed findings. The SAST/security scanning capabilities exist as agent skills, and sandboxing is claimed. The prompt injection incident is a significant concern but was addressed. Consistent with D10=4 (security review gate exists via SAST agent capabilities; but trust concerns from the prompt injection incident reduce confidence). [LOW CONFIDENCE]

### D11 -- Independent Validation and Spec Compliance
**Score**: 0 [LOW CONFIDENCE]
**Evidence**: No documented independent validation of worker output against specifications. No spec compliance agent or report documented in public sources. TDD enforcement validates tests pass but not that specifications were met. Consistent with D11=0.

### D12 -- Cross-Run Learning and Memory
**Score**: 4
**Evidence**: ruflo documents a Memory System (wiki page) with namespace support and TTL settings for persistent memory. Self-learning capability claimed. Git-native knowledge base. Full historical logging enables learning from past runs. However, automatic injection of learnings into future run prompts is not documented as a structured protocol. Memory exists and is structured but automatic application is unclear. Consistent with D12=4 (structured memory capture; available for future runs but automatic injection not documented).

---

## Corrected Scoring Table

| System | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | Total |
|--------|----|----|----|----|----|----|----|----|----|----|-----|-----|-------|
| Spectrum Protocol | 10 | 10 | 0 | 8 | 6 | 8 | 8 | 8 | 8 | 4 | 8 | 10 | 88 |
| Gas Town | 2 | 2 | 0 | 2 | 10 | 4 | 2 | 2 | 0 | 0 | 0 | 2 | 26 |
| oh-my-claudecode | 2 | 0 | 0 | 10 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 14 |
| Agent Teams (Anthropic) | 2 | 4 | 4 | 8 | 4 | 2 | 2 | 2 | 0 | 0 | 0 | 0 | 28 |
| Citadel | 6 | 6 | 0 | 6 | 6 | 4 | 4 | 4 | 0 | 0 | 0 | 2 | 38 |
| metaswarm | 4 | 4 | 0 | 4 | 4 | 4 | 4 | 4 | 6 | 0 | 0 | 4 | 38 |
| Overstory | 4 | 6 | 0 | 6 | 4 | 2 | 2 | 6 | 0 | 0 | 0 | 2 | 32 |
| ruflo | 4 | 4 | 0 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 0 | 4 | 40 |

---

## Per-System Narratives

### Spectrum Protocol
Spectrum dominates Category A (pre-execution planning) with perfect scores in task decomposition and contract enforcement -- no other system in this group implements Design-by-Contract per worker, adversarial plan review, White Pre-Check factual verification, and frozen contracts with formal amendment protocol. It also leads Category C (post-execution assurance) with independent Pax validation and Obsidian spec compliance reporting. Its principal weaknesses are the absence of any published benchmark (D3=0) and moderate security posture (no SAST or sandboxing). The muster ceremony, while providing safety guarantees, caps parallelism efficiency at D5=6 in full mode. Spectrum is the right choice for teams who need coordination rigor and are willing to pay for it in setup and ceremony cost.

### Gas Town
Gas Town is the parallelism leader in this group (D5=10) -- the only system designed for 20-30+ concurrent agents with near-zero startup overhead via its daemon architecture. This comes at the cost of everything else: no contracts, no quality gates, no independent validation, no structured failure handling. Gas Town is a throughput-maximizing system that trades safety for speed. Best for large-scale concurrent work where the human operator provides all quality assurance externally.

### oh-my-claudecode
oh-my-claudecode is the adoption leader (D4=10) -- zero configuration, instant productivity. It scores 0 on 9 of 12 dimensions because it deliberately provides no coordination infrastructure. The 32 specialist agents and Ultrapilot mode provide basic parallelism but without any formal coordination, quality, or safety mechanisms. Best for solo developers who want quick parallel execution and accept full responsibility for quality.

### Agent Teams (Anthropic)
Agent Teams benefits from native Claude Code integration (D4=8) and the underlying model's benchmark capability (D3=4, the only non-zero accuracy score in this group). However, its research preview status means most coordination features are undocumented or absent: no contracts, no quality gates, no failure taxonomy, no state durability, no spec compliance. Best for simple parallel tasks where native integration matters more than coordination rigor.

### Citadel
Citadel is the most balanced system in this group after Spectrum, with moderate scores across most dimensions and no catastrophic gaps in Categories A and B. Campaign persistence, circuit breaker, discovery relay, and machine-verifiable phase conditions provide a solid coordination foundation. Its gap is Category C: no quality gates, no security, no validation, no learning. Best for teams who want structured coordination without Spectrum's ceremony.

### metaswarm
metaswarm's strength is quality engineering: the strongest quality gates outside Spectrum (D9=6) with machine-enforced coverage thresholds and mandatory adversarial review by a fresh reviewer. Its 9-phase workflow provides structure but at the cost of parallelism efficiency (sequential phase transitions). The Closure & Learning phase and self-improving architecture provide above-average memory. Best for teams who prioritize code quality and TDD enforcement over raw parallelism.

### Overstory
Overstory provides the best observability outside Spectrum (D8=6) with its trace command, per-agent cost analysis, and tiered watchdog. Its pluggable runtime adapter for 11 runtimes is unique in this group. Tool-call guards provide genuine scope enforcement (D2=6). However, it lacks quality gates, security, validation, and structured failure handling. Best for teams running heterogeneous agent runtimes who need observability.

### ruflo
ruflo has the broadest feature set in this group (60+ agents, 259 MCP tools, SAST/DAST capabilities) and is the only system with documented security scanning features (D10=4). Its moderate scores across all dimensions reflect breadth over depth -- no dimension above 4 except security. The prompt injection incident (Issue #1375, now addressed) is a trust concern. Best for teams who need breadth of agent capabilities and security scanning integration, though the depth of coordination rigor trails Spectrum and Citadel.

---

## Cross-System Observations

### Category A (Pre-Execution Planning) Leaders
Spectrum (28/40) dominates this category. No other system implements adversarial plan review, frozen contracts with amendment protocol, or Design-by-Contract per worker. Citadel (12/40) and Overstory (16/40) provide moderate planning infrastructure. Agent Teams, oh-my-claudecode, and Gas Town provide minimal pre-execution planning.

### Category B (Runtime Coordination) Leaders
Gas Town leads D5 (10) and is the only system designed for 20+ agents. Spectrum leads D6 (8) and D7 (8) with the most sophisticated state durability and failure handling. Overstory leads D8 (6) among non-Spectrum systems. No system in this group reaches D5=10 except Gas Town, and no system reaches D8=10.

### Category C (Post-Execution Assurance) Leaders
Spectrum (30/40) dominates Category C with the only documented independent validation, spec compliance reporting, and institutional memory systems. metaswarm (10/40) is the closest with quality gates and structured learning. Most systems in this group score 0-4 across all Category C dimensions. This is the largest differentiation gap in the evaluation.

### D3 Accuracy: Universal Gap
Every system in this group scores 0 on D3 except Agent Teams (4, based on underlying Opus 4.6 model capability). No Claude Code orchestration system has published multi-agent benchmark results. This is a field-wide gap, not a Spectrum-specific weakness.

### D10 Security: Near-Universal Gap
Only ruflo (4) and Spectrum (4) score above 0 on security. All Claude Code orchestrators run on host machines without sandboxing. This is an architectural characteristic of the Claude Code ecosystem.
