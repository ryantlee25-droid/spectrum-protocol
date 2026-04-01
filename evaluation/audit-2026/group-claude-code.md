# Claude Code Ecosystem Scoring Report
**Spectrum**: audit-2026-0331
**Howler**: H2-claude
**Date**: 2026-03-31
**Rubric version**: evaluation/audit-2026/RUBRIC.md v1.0

---

## Scoring Table

| System | D1 Cost | D2 Speed | D3 Accuracy | D4 Workflow Rigor | D5 Observability | D6 Recovery | D7 Setup | D8 Scalability | Total |
|--------|---------|----------|-------------|-------------------|------------------|-------------|----------|----------------|-------|
| Gas Town | 3 | 5 | 2 | 3 | 3 | 3 | 2 | 5 | 26 |
| oh-my-claudecode | 3 | 4 | 2 | 2 | 2 | 2 | 5 | 3 | 23 |
| Agent Teams (Anthropic) | 3 | 4 | 3 | 2 | 2 | 2 | 4 | 3 | 23 |
| Spectrum Protocol | 2 | 3 | 2 | 5 | 3 | 4 | 3 | 3 | 25 |
| Citadel | 3 | 4 | 2 | 4 | 3 | 4 | 4 | 3 | 27 |
| metaswarm | 3 | 3 | 2 | 4 | 2 | 4 | 3 | 3 | 24 |
| Overstory | 3 | 4 | 2 | 3 | 4 | 3 | 3 | 4 | 26 |

---

## Per-System Evidence Notes

---

### Gas Town (steveyegge/gastown)

**D1 Cost — 3**: Gas Town runs on standard Claude Code API pricing with no additional platform fees. No documented per-run cost estimate. The architecture targets large enterprise workloads (20-30+ agents), which implies high token consumption per run at scale. Community reports describe Gas Town as viable on individual developer budgets at small scale, comparable to standard Claude Code usage. [MEDIUM CONFIDENCE — model costs only; no per-run benchmark at representative 3-5 agent scale]
Source: steveyegge/gastown README (github.com/steveyegge/gastown); Steve Yegge Medium post "Welcome to Gas Town," January 2026.

**D2 Speed — 5**: Gas Town is purpose-built for maximum parallel throughput. The GUPP (Go Until a Problem Presents) principle means agents execute immediately without waiting for orchestrator permission. Pull-based work queues enable genuine concurrent execution across 20-30+ agents. Architecture documentation confirms simultaneous multi-agent execution with no artificial serialization. The landscape survey scores Gas Town 10/10 on parallel execution, highest in class.
Source: AGENTIC-LANDSCAPE.md §2.5; steveyegge/gastown README; DeepWiki gastown core concepts (deepwiki.com/steveyegge/gastown/2-core-concepts).

**D3 Accuracy — 2**: No published SWE-Bench result or independent benchmark for Gas Town. The AGENTIC-LANDSCAPE.md survey notes Gas Town scores 3/10 on Spec Compliance — below most systems. GUPP's aggressive autonomy trades accuracy checkpoints for throughput. No pre-flight contract mechanism means agent interpretation of shared interfaces is unverified. [MEDIUM CONFIDENCE — no benchmark data; community reports only]
Source: AGENTIC-LANDSCAPE.md §6 cross-cutting table; steveyegge/gastown README limitations section.

**D4 Workflow Rigor — 3**: Gas Town provides actor attribution (Git-backed provenance records), a 3-tier watchdog (Deacon health monitor with escalating interventions), and pull-based task queues. These constitute role separation and retry-with-logging, satisfying the D4=3 anchor. However: (a) no pre-execution interface contracts between agents, (b) no formal failure taxonomy (the watchdog detects stalls but does not classify failure types), (c) no independent adversarial review step. File conflicts are discovered at runtime via attribution, not prevented pre-flight. The system provides structure but misses two of the four D4=5 components.
Source: AGENTIC-LANDSCAPE.md §2.5; gastown/docs/glossary.md (github.com/steveyegge/gastown/blob/main/docs/glossary.md).

**D5 Observability — 3**: Git-backed provenance records on every action provide structured, attributable logs. Post-hoc inspection of agent activity is solid. No documented real-time dashboard or terminal UI showing per-agent status during execution. No replay capability equivalent to LangGraph. Status during execution is limited to `gt status` CLI output and Deacon health reports. Satisfies D4=3 (structured logs with agent labels) but not D4=4 (real-time dashboard).
Source: steveyegge/gastown README; AGENTIC-LANDSCAPE.md §2.5 State Management; DeepWiki gastown configuration (deepwiki.com/steveyegge/gastown/7-configuration-and-tooling).

**D6 Recovery — 3**: Three-tier watchdog provides retry-on-failure with configurable intervention levels. Stall detection is autonomous — the Deacon issues escalating responses without waiting for human input. Hooks (persistent work queues) survive agent restarts, so work does not restart from scratch. However, the landscape survey notes no formal failure taxonomy; stall detection is the primary mechanism, not failure classification. No documented circuit breaker in the failure-taxonomy sense (though the watchdog's escalating tiers approximate one). Satisfies D6=3 (retry with max-attempts, state persists) but not D6=4 (3+ distinct failure types with different handling paths).
Source: AGENTIC-LANDSCAPE.md §2.5 Error Recovery; gastown README Deacon section.

**D7 Setup — 2**: Requires Go 1.25+, Git, Dolt (secondary issue tracker), and tmux for full-stack mode. Installation: `go install` for `gt` binary plus `bd` (Beads) binary, then `gt install ~/gt --shell` to initialize workspace, then `gt daemon start` for the background supervisor. Multiple dependencies beyond the core LLM (Go runtime, Dolt issue tracker, optional launchd/systemd daemon). AGENTIC-LANDSCAPE.md characterizes Gas Town as having "heavy infrastructure requirements." Installation documentation exists but the setup path is multi-step and requires Go knowledge. Consistent with D7=2 (multiple dependencies beyond core LLM, framework-specific knowledge required).
Source: gastown/docs/INSTALLING.md (github.com/steveyegge/gastown/blob/main/docs/INSTALLING.md); DeepWiki installation guide (deepwiki.com/steveyegge/gastown/2.1-installation); AGENTIC-LANDSCAPE.md §2.5 Limitations.

**D8 Scalability — 5**: Gas Town is the only open-source system explicitly designed for 20-30+ concurrent agents. Pull-based work queues scale dynamically with queue depth. The landscape survey assigns 10/10 on scalability and 10/10 on parallel execution, noting it as the only system in the 20-30+ agent class. Architecture documentation confirms no documented ceiling below 10 agents — the design ceiling is substantially higher. Sub-linear coordination overhead growth is the stated goal of the pull-based architecture.
Source: AGENTIC-LANDSCAPE.md §2.5 and §7 (Scalability leader); steveyegge/gastown README architecture section.

**Uncertainty flags**: D1 (no per-run cost benchmark), D3 (no published accuracy benchmark).

---

### oh-my-claudecode

**D1 Cost — 3**: No separate platform fee; runs on Claude API pricing. Smart routing (Haiku for simple tasks, Opus for complex) is documented to produce 30-50% token savings versus undifferentiated Opus usage. Community reports confirm cost is not a blocking concern but is noticeable for large parallel runs. The savings claim would push toward D1=4, but it is community-reported and not independently verified. Conservative score of 3 applied per partial-evidence rule.
Source: byteiota.com/oh-my-claudecode-multi-agent-orchestration-for-claude-code/; AGENTIC-LANDSCAPE.md §4.3.

**D2 Speed — 4**: Ultrapilot mode runs up to 5 concurrent Claude Code instances in isolated git worktrees. Community reports of 3-5x speedup are consistent with the architecture. Documentation confirms simultaneous agent execution. No precise wall-clock benchmarks published, but 5 parallel workers with git worktree isolation is consistent with D2=4 (parallelism evident, 3+ simultaneous agents). Ceiling of 5 instances is the documented Ultrapilot limit.
Source: AGENTIC-LANDSCAPE.md §4.3; byteiota.com oh-my-claudecode overview; ohmyclaudecode.com.

**D3 Accuracy — 2**: No published SWE-Bench or independent benchmark. Autopilot mode explicitly removes human checkpoints, which MASFT research identifies as a primary driver of specification failure (42% of all MAS failures come from specification errors requiring human judgment). 30-50% token savings from smart routing suggest some tasks are handled by smaller models, which may affect output quality. The landscape survey notes 2/10 on Spec Compliance and 2/10 on Shared Contracts for oh-my-claudecode. [MEDIUM CONFIDENCE — no benchmark data; community reports only]
Source: AGENTIC-LANDSCAPE.md §6 cross-cutting table; MASFT paper (arxiv.org/abs/2503.13657).

**D4 Workflow Rigor — 2**: No file ownership contracts. No frozen interface mechanism. No failure taxonomy. Coordination is via shared task list (pull-based), which is informal delegation — task boundaries rely entirely on task list granularity. The 32 specialist agents provide role separation, satisfying partial credit, but role separation alone without contracts, ownership, or failure classification does not reach D4=3. No independent adversarial review step. Consistent with D4=2 (multiple agents, coordination informal, recovery is "try again").
Source: AGENTIC-LANDSCAPE.md §4.3; oh-my-claudecode README (github.com/yeachan-heo/oh-my-claudecode).

**D5 Observability — 2**: No documented dashboard or structured logging system. Supervisor monitors progress, but the observation mechanism is not described in technical detail in available documentation. No trace IDs or replay capability documented. User observability appears to be through standard Claude Code output per instance. Consistent with D5=2 (no agent-level log attribution documented).
Source: AGENTIC-LANDSCAPE.md §4.3; ohmyclaudecode.com feature documentation.

**D6 Recovery — 2**: No structured failure recovery documented. The shared task list allows agents to move on to unclaimed tasks if one is blocked, which is a form of basic resilience, but no failure classification, state persistence for recovery, or circuit breaker is documented. Consistent with D6=2 (basic recovery: move to next task, no failure classification).
Source: AGENTIC-LANDSCAPE.md §4.3 Limitations; oh-my-claudecode README.

**D7 Setup — 5**: Zero-configuration is the explicit design goal. Works without MANIFEST.md, CONTRACT.md, or pre-flight planning. Installable as a CLAUDE.md preset with no infrastructure dependencies. 858 stars in 24 hours at launch suggests near-zero barrier to first use — developers can try it immediately without documentation study. No binary, no daemon, no additional services required.
Source: AGENTIC-LANDSCAPE.md §4.3; byteiota.com oh-my-claudecode overview; AGENTIC-LANDSCAPE.md §7 Coordination Overhead.

**D8 Scalability — 3**: Documented ceiling of 5 instances in Ultrapilot mode. This is below the D8=4 threshold of 6-8 agents. AGENTIC-LANDSCAPE.md notes "5-instance practical ceiling in Ultrapilot is lower than Convoy's 8-Rider ceiling." No documentation of effective performance degradation at the ceiling. Consistent with D8=3 (3-5 agent sweet spot, degrades beyond).
Source: AGENTIC-LANDSCAPE.md §4.3 Limitations.

**Uncertainty flags**: D1 (token savings community-reported only), D3 (no benchmark), D5 (observability mechanism underdocumented).

---

### Agent Teams (Anthropic Official)

**D1 Cost — 3**: No separate platform fee; runs on Claude Code API pricing. The Lead agent requires Opus 4.6 (highest-tier model), adding cost overhead for the orchestration layer that other systems do not impose. At representative 3-5 agent scale with an Opus Lead, per-run costs are moderately higher than systems using Sonnet uniformly. No published per-run cost estimate. [MEDIUM CONFIDENCE — model costs only; Opus Lead adds overhead]
Source: AGENTIC-LANDSCAPE.md §4.1; TechCrunch "Anthropic releases Opus 4.6 with new 'agent teams'" (techcrunch.com/2026/02/05).

**D2 Speed — 4**: Native TeammateTool supports up to 8 parallel teammates in isolated git worktrees with individual context windows. Direct inter-agent messaging during execution (not just at completion) avoids synchronization wait points. Git worktree isolation prevents filesystem conflicts during parallel execution. Architecture documentation (13 TeammateTool operations, full coordination lifecycle) confirms genuine parallel execution. No published wall-clock benchmarks. [MEDIUM CONFIDENCE — architecture supports parallelism, no timing benchmarks]
Source: AGENTIC-LANDSCAPE.md §4.1; blog.imseankim.com Claude Code team mode (March 2026); heeki.medium.com Agent Teams (March 2026).

**D3 Accuracy — 3**: No Agent Teams-specific SWE-Bench result. The underlying model (Opus 4.6) is documented at ~49% SWE-Bench Verified for single-agent Claude Code (consistent with D3=4 anchor for the model alone). Agent Teams introduces coordination overhead and potential specification drift absent from single-agent runs. Research preview status means reliability gaps may exist. Net score of 3 is conservative: model capability supports higher, but coordination overhead and research preview maturity pull down. [MEDIUM CONFIDENCE — no Agent Teams-specific benchmark; Opus 4.6 base performance cited]
Source: AGENTIC-LANDSCAPE.md §4.1 and §8.7; TechCrunch Opus 4.6 launch article; SWE-Bench Verified leaderboard data as of March 2026.

**D4 Workflow Rigor — 2**: TeammateTool provides team lifecycle management, task assignment, mid-execution inter-agent messaging, and status checking. Role separation (Lead vs. teammates) is enforced. However: (a) no pre-execution interface contracts or file ownership matrix — coordination is via TeammateTool calls and the Lead's implicit reasoning, (b) no documented failure taxonomy — error recovery "likely follows single-agent retry behavior" per AGENTIC-LANDSCAPE.md, (c) no independent adversarial review step. Code merges only when tests pass (a partial quality gate), but this is a single condition, not a multi-component gate. Consistent with D4=2 (multiple agents, coordination informal, no formal contracts or taxonomy).
Source: AGENTIC-LANDSCAPE.md §4.1; paddo.dev "Claude Code hidden swarm"; GitHub issue #28087 anthropics/claude-code (ANTHROPIC_API_KEY bug report indicating early-stage maturity).

**D5 Observability — 2**: No documented dashboard or structured per-teammate logs. `check_status` TeammateTool operation provides polling capability, but no real-time observability UI or trace IDs per agent are documented. Internal observability details are not public for the research preview. [MEDIUM CONFIDENCE — internal observability undocumented; research preview]
Source: AGENTIC-LANDSCAPE.md §4.1; releasebot.io Claude Code release notes (March 2026).

**D6 Recovery — 2**: Research preview documentation does not formalize recovery behavior. AGENTIC-LANDSCAPE.md states error recovery "likely follows single-agent retry behavior per teammate." Teammates merge only when tests pass (partial failure gate), but failure classification and circuit breakers are not documented. Single retry or manual Lead re-assignment is the evident recovery path. Consistent with D6=2 (basic: single retry or manual intervention, no failure classification).
Source: AGENTIC-LANDSCAPE.md §4.1 Limitations; releasebot.io Claude Code release notes (March 2026).

**D7 Setup — 4**: Native to Claude Code — no external tooling, no worktree setup scripts, no binary installation. Activation requires setting `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and having Opus 4.6 access (requires Claude Teams/Enterprise plan or API access). Available to all Claude Code users with API access in principle, but Opus 4.6 requirement adds a plan-tier prerequisite. First parallel run achievable well within 1 hour. Consistent with D4=4 (2-3 setup steps, 1-2 service prerequisites).
Source: AGENTIC-LANDSCAPE.md §4.1; TechCrunch Opus 4.6 launch article; Claude Code release notes (anthropics/claude-code releases).

**D8 Scalability — 3**: TeammateTool supports up to 8 teammates per the 13-operation API documentation. AGENTIC-LANDSCAPE.md scores Agent Teams 7/10 on parallel execution and 7/10 on scalability. However, research preview status means large-scale reliability at 8 agents is unproven. The architecture could support 6-8 effectively (D8=4), but the research preview maturity warrants conservative scoring. [MEDIUM CONFIDENCE — architecture supports 8 agents; empirical evidence at scale absent for research preview]
Source: AGENTIC-LANDSCAPE.md §4.1 and §6 cross-cutting table.

**Uncertainty flags**: D3 (no Agent Teams benchmark; model-level data used), D5 (internal observability undocumented), D6 (recovery behavior undocumented for research preview), D8 (scale reliability unproven at preview stage).

---

### Spectrum Protocol

*Scored as a peer. Self-reported claims from README and SPECTRUM-OPS.md are treated as inputs subject to the same verification standard as any other system's documentation, per CONTRACT.md §2.*

**D1 Cost — 2**: Spectrum's own README documents per-run cost estimates: ~$4.80 for 3-Howler reaping, ~$9.43 for 5-Howler full, ~$15.20 for 8-Howler full. At representative 3-5 agent scale, the documented cost range is $4.80–$9.43. The D1=2 anchor is $2–$10/run or subscription pricing that restricts parallel usage, with cost regularly cited as a drawback. The 5-Howler run at ~$9.43 falls at the top of the D1=2 range. The README itself lists cost management (budget tracking in CHECKPOINT.json) as a feature, implying cost is a known concern for users. Note: the README's $9.43 figure is self-reported and may not reflect actual token usage in practice — it is based on internal estimates, not published benchmarks. Applying conservative interpretation: the documented cost lands in D1=2 territory for the representative 5-agent case.
Source: Spectrum Protocol README.md (spectrum-protocol/README.md) §Token Costs table.

**D2 Speed — 3**: Spectrum supports parallel execution via git worktrees, with Howlers dispatched per DAG as dependencies are satisfied. Genuine parallelism is documented. However, the muster phase (8 minutes for full mode, 3 minutes for reaping mode) adds significant wall-clock overhead before any Howler starts. For a 3-agent reaping run, the 3-minute pre-execution overhead is material relative to the task. SPECTRUM-OPS.md explicitly notes muster ceremony as overhead and introduces reaping mode to reduce it. No published wall-clock benchmarks for end-to-end run time. Pre-execution overhead and the human approval gate before Howler drop add structural serialization that is absent from systems like Gas Town or oh-my-claudecode. Consistent with D2=3 (parallelism present but with constraints and overhead).
Source: Spectrum Protocol README.md; SPECTRUM-OPS.md §Reaping Mode ("~3 min instead of ~8 min"); AGENTIC-LANDSCAPE.md §1.4 (DAG-based dispatch).

**D3 Accuracy — 2**: No published SWE-Bench score or independent benchmark for Spectrum Protocol. The README claims three capabilities unique to Spectrum and leads in coordination rigor, but these are self-reported claims, not benchmark results. SPECTRUM-OPS.md was written to describe the protocol's own workflow, not to evidence output accuracy. Community reports are not available in public sources. The coordination rigor may improve accuracy on multi-file tasks, but this has not been independently measured. Per the missing-evidence rule: no benchmark data → score 2 with uncertainty flag. [LOW CONFIDENCE — no public benchmark evidence; self-reported claims only]
Source: Spectrum Protocol README.md §Evaluation (self-reported); no independent SWE-Bench citation found in public sources.

**D4 Workflow Rigor — 5**: Spectrum documents all four D4=5 components: (a) pre-execution CONTRACT.md with per-Howler preconditions/postconditions/invariants and file ownership matrix (MANIFEST.md) — every file assigned exactly once, verified during muster and by Politico; (b) formal failure taxonomy with 5 distinct types (transient, logical, structural, environmental, conflict) with different handling paths per type (Resume/Retry/Skip/Restructure); (c) circuit breaker — 2 failures on same locus auto-escalate to structural, Gold pauses and escalates to human; (d) independent adversarial review step — Politico agent challenges CONTRACT.md and MANIFEST.md before freeze, must resolve all blockers before Howlers drop. All four components are documented as enforced by the protocol, not merely recommended. Caveat: "enforced by the framework" for a CLAUDE.md-based protocol means enforcement is via LLM instruction adherence, not machine verification — a meaningful distinction from hard-coded framework enforcement.
Source: SPECTRUM-OPS.md §Phase 1 Muster; SPECTRUM-OPS.md §Phase 4 Forge; Spectrum Protocol README.md §Feature Highlights.

**D5 Observability — 3**: Spectrum requires a mandatory status roster printed at every phase transition showing per-agent status with glyphs, roles, and task context. HOOK.md per Howler provides structured per-agent state that persists across session failures. CHECKPOINT.json captures phase and all howler states. These constitute structured logs with agent-level attribution (D5=3). No real-time dashboard — status is provided via inline console output (the roster) and file inspection, not a dedicated UI. No trace IDs or replay capability. Consistent with D5=3 (structured logs with agent labels and timestamps; no real-time dashboard).
Source: SPECTRUM-OPS.md §Status Roster; SPECTRUM-OPS.md §CHECKPOINT.json; Spectrum Protocol README.md §Durable State.

**D6 Recovery — 4**: Spectrum documents a formal failure taxonomy (5 types), automated recovery for transient failures (auto-Resume without human confirmation), a circuit breaker (2-failure auto-escalation on same locus), and persistent failure state (HOOK.md survives Howler death, enabling resume rather than restart). These satisfy three of the four D6=5 components: formal taxonomy, automated recovery class, and persistent failure state. The circuit breaker is present and documented. All four components of D6=5 are technically present in the documentation, but "automated recovery" applies only to transient failures — all other types require human confirmation. This partial automation is consistent with D6=4 (3 of 4 components, documentation explicitly describes failure types and handling, one tier may be considered partial).
Source: SPECTRUM-OPS.md §Phase 4 Forge; Spectrum Protocol README.md §Typed Failure Taxonomy.

**D7 Setup — 3**: The README states "No dependencies. No build step. Copy three files and you're running." Installation is: (1) copy CLAUDE.md to ~/.claude/, (2) copy SPECTRUM-OPS.md to ~/.claude/, (3) copy SPECTRUM.md to ~/.claude/. Three distinct steps with no infrastructure. However, "running" requires understanding the protocol's 7 phases, multiple agent types, muster flow, and CLAUDE.md configuration before the first productive parallel run. SPECTRUM-OPS.md alone is ~550 lines. Reaping mode reduces ceremony, but full-mode first runs require half-day documentation study for unfamiliar users. Consistent with D7=3 (4-6 steps or a tutorial; requires familiarity with framework abstractions before first run).
Source: Spectrum Protocol README.md §Quick Start and §Not For ("Zero-config quick start — use oh-my-claudecode").

**D8 Scalability — 3**: Spectrum documents a documented maximum of 8 parallel Howlers ("Max 8 parallel Howlers — more than this and coordination overhead dominates" per SPECTRUM-OPS.md). The architecture is DAG-based with pre-planned file ownership, which is theoretically more conflict-resistant than pull-queue architectures at scale, but the 8-Howler ceiling is explicitly stated as the design limit. AGENTIC-LANDSCAPE.md §8.6 notes that Gas Town patterns were designed for 20+ agents, positioning them differently from Spectrum's 3-8 sweet spot. The README explicitly states "Not For: 20+ agents at scale — use Gas Town." Consistent with D8=3 (3-5 agent sweet spot, degrades beyond 5-6 for large coordination overhead; Spectrum's own documentation sets the ceiling at 8 but explicitly describes 3-8 as the sweet spot).
Source: SPECTRUM-OPS.md §Rules; Spectrum Protocol README.md §Best For and §Not For.

**Uncertainty flags**: D1 (self-reported cost estimate, not externally benchmarked), D3 (no public benchmark — lowest-confidence score in this report).

---

### Citadel (SethGammon/Citadel)

**D1 Cost — 3**: No platform fee; runs on Claude Code API. Citadel includes native cost accounting: it reads Claude Code session files for exact token counts and computes real cost from API pricing per session, campaign, and agent. This transparency does not reduce cost but enables cost awareness. No published per-run benchmark. At representative 3-5 agent scale with standard API pricing, cost is comparable to other Claude Code orchestrators. [MEDIUM CONFIDENCE — model costs only; orchestration overhead unknown]
Source: github.com/SethGammon/Citadel README (retrieved via web search March 2026).

**D2 Speed — 4**: Parallel agents in isolated git worktrees are documented as a core feature. Discovery relay between waves propagates findings between agent generations without requiring full debrief re-reads. Campaign persistence means sessions resume immediately from prior state. No published wall-clock benchmarks. Four-tier routing (`/do`) dispatches work efficiently. Architecture is consistent with genuine concurrent execution at 3+ agents. [MEDIUM CONFIDENCE — architecture supports parallelism; no timing benchmarks available]
Source: github.com/SethGammon/Citadel README and description.

**D3 Accuracy — 2**: No published SWE-Bench or independent benchmark. Citadel is a protocol/orchestration layer, not a model. Code quality depends on the underlying model (Claude Code). No community benchmark data found in public sources. [LOW CONFIDENCE — no public evidence]
Source: No benchmark citation found in search results.

**D4 Workflow Rigor — 4**: Citadel documents: campaign persistence across sessions (structured state), parallel agents in isolated worktrees, discovery relay between waves, lifecycle hooks, and a documented circuit breaker ("stops failure spirals before they burn tokens"). The circuit breaker is a documented enforcement mechanism. Four-tier routing (`/do`) implies structured task decomposition with routing decisions. Machine-verifiable phase conditions are cited in Spectrum's README acknowledgments as Citadel's key contribution ("Citadel — machine-verifiable phase conditions"). A failure taxonomy or adversarial review step is not documented in available sources. Three of four D4=5 components are present (contracts/routing, circuit breaker, structured state), with adversarial review absent. Consistent with D4=4.
Source: github.com/SethGammon/Citadel README; Spectrum Protocol README.md §Acknowledgments.

**D5 Observability — 3**: Native cost accounting reads Claude Code session files and provides per-session, per-campaign, and per-agent cost breakdowns. This constitutes structured per-agent logging with attribution. No real-time dashboard documented. Cost observability is well-specified; execution-state observability (what agents are doing mid-run, not just what they cost) is not described in detail in available sources. [MEDIUM CONFIDENCE — cost observability documented; execution observability limited evidence]
Source: github.com/SethGammon/Citadel README cost accounting description.

**D6 Recovery — 4**: Circuit breaker is explicitly documented ("stops failure spirals before they burn tokens"). Campaign persistence means failure state survives session death — recovery resumes from the last campaign state. Lifecycle hooks provide intervention points for failure handling. Discovery relay means downstream agents receive findings from prior waves, enabling informed retry. Three of the four D6=5 components are documented: circuit breaker present, failure state persisted, automated recovery mechanisms via lifecycle hooks. A formal multi-tier failure taxonomy (≥3 distinct types with different paths) is not documented in available sources — this prevents reaching D6=5. Consistent with D6=4.
Source: github.com/SethGammon/Citadel README circuit breaker and campaign persistence descriptions.

**D7 Setup — 4**: Described as a plugin installable on any codebase. Plugin-based installation implies 2-3 setup steps. No daemon, no Go binary, no infrastructure beyond Claude Code. If installation is truly plugin-based (copy files or install command), first run is achievable within 1 hour. No community reports of installation failures found. [MEDIUM CONFIDENCE — installation described but process not fully documented in available sources]
Source: github.com/SethGammon/Citadel README ("install it as a plugin and it works on any codebase").

**D8 Scalability — 3**: No documented agent count ceiling or scalability guidance found. Campaign persistence and worktree isolation support multiple parallel agents. Without documented guidance on optimal batch size or observed behavior beyond small-scale runs, architectural inference applies: campaign-based orchestration with worktree isolation is consistent with moderate scalability (3-5 agents). No evidence of production use at 6+ agents. [MEDIUM CONFIDENCE — architectural inference; no empirical evidence at scale]
Source: github.com/SethGammon/Citadel README; first-principles reasoning from architecture description.

**Uncertainty flags**: D3 (no benchmark), D5 (execution observability limited), D7 (installation process not fully documented), D8 (no scale evidence).

---

### metaswarm (dsifry/metaswarm)

**D1 Cost — 3**: No platform fee. Supports delegating review tasks to Gemini 2.5 Pro (free tier: 1,000 req/day) for cost reduction. This cross-model routing provides a genuine cost reduction path absent from most systems. However, the base implementation uses Claude (Sonnet/Opus) for implementation agents, and the 18-agent roster with mandatory quality gates implies substantial token usage per run. The Gemini delegation for review is a cost optimization, not a zero-cost architecture. Net assessment: comparable to other Claude Code orchestrators at representative scale, with cost optimization options available. [MEDIUM CONFIDENCE — cross-model routing documented but total per-run cost not benchmarked]
Source: dsifry.github.io/metaswarm/ and github.com/dsifry/metaswarm README; web search result on Gemini free tier integration.

**D2 Speed — 3**: 9-phase workflow (Research → Plan → Design Review Gate → Work Unit Decomposition → Orchestrated Execution → Final Review → PR Creation → PR Shepherd → Closure & Learning) is sequential at the phase level. Within Orchestrated Execution, parallel work units are supported. However, mandatory blocking phase transitions (Design Review Gate, Final Review Gate) introduce structural serialization. The 4-Phase execution loop per work unit (IMPLEMENT → VALIDATE → ADVERSARIAL REVIEW → COMMIT) adds per-unit overhead. This is parallelism with significant orchestration overhead, consistent with D2=3.
Source: dsifry.github.io/metaswarm/ workflow description; github.com/dsifry/metaswarm USAGE.md.

**D3 Accuracy — 2**: No published SWE-Bench or independent benchmark. Creator Dave Sifry describes the system as "production-tested" across "hundreds of PRs" with 100% test coverage enforcement. This is strong community-level evidence but not an independent benchmark. The mandatory TDD enforcement and multi-stage review gates suggest output quality is above average, but cannot be independently verified. Per partial-evidence rule: community reports without benchmark → score 2, flag medium confidence. [MEDIUM CONFIDENCE — no benchmark data; creator claims production validation across hundreds of PRs]
Source: github.com/dsifry/metaswarm README self-description; web search results on metaswarm production claims.

**D4 Workflow Rigor — 4**: Metaswarm documents: (a) structured 9-phase workflow with blocking state transitions — "there is no instruction path from FAIL to COMMIT" per documentation; (b) mandatory adversarial review — "IMPLEMENT → VALIDATE → ADVERSARIAL REVIEW → COMMIT" with a fresh reviewer (never the same as the implementer) on each retry; (c) .coverage-thresholds.json as a machine-enforced blocking gate; (d) retry logic: fix → re-validate → spawn fresh reviewer → retry up to 3 times → escalate with full failure history. This covers role separation, quality gates, and an adversarial review step. A formal failure taxonomy with ≥3 distinct failure types and different handling paths is not documented; the retry mechanism is a single path regardless of failure type. Three of four D4=5 components are present. Consistent with D4=4.
Source: dsifry.github.io/metaswarm/ adversarial review and quality gate documentation; web search result on metaswarm failure handling.

**D5 Observability — 2**: No documented dashboard, trace IDs, or structured logging system with per-agent attribution. The framework produces structured outputs (per-phase artifacts, coverage reports), which constitute post-hoc observability of results. Execution-level observability (what is happening mid-run) is not documented in available sources. 18-agent roster complexity suggests monitoring need, but no monitoring mechanism is described. [MEDIUM CONFIDENCE — internal observability undocumented]
Source: github.com/dsifry/metaswarm README; no observability documentation found in web search results.

**D6 Recovery — 4**: Retry with fresh reviewer (never the same agent) up to 3 times before escalation. On escalation: full failure history is passed to the human. State persists through the retry cycle (the failure context accumulates and is preserved). Blocking state transitions prevent silent propagation of failures. The retry mechanism with mandatory context handoff to human on escalation satisfies most D6=4 components. Formal failure taxonomy (≥3 types with distinct paths) is not present; the same 3-retry-then-escalate path applies regardless of failure type. Consistent with D6=4 (3 of 4 D6=5 components: automated recovery, failure state persisted, escalation mechanism; missing: formal multi-tier taxonomy).
Source: web search result on metaswarm failure handling ("On failure: fix, re-validate, spawn a fresh reviewer... retry up to three times before escalating with full failure history").

**D7 Setup — 3**: Installation documented via INSTALL.md. Supports Claude Code, Gemini CLI, and Codex CLI — multi-tool support implies some configuration complexity. 18 specialized agents plus 13 skills and 15 commands represent substantial framework knowledge required before first productive run. GETTING_STARTED.md exists, suggesting the developer recognized a learning curve. External tools setup template (external-tools-setup.md) implies additional configuration steps. Consistent with D7=3 (tutorial required; framework-specific knowledge needed; first run achievable within a half-day).
Source: github.com/dsifry/metaswarm INSTALL.md and GETTING_STARTED.md; web search result on metaswarm skills and commands count.

**D8 Scalability — 3**: 18 specialized agents are defined, but these are role definitions, not concurrent instances. Documentation describes orchestrated work unit decomposition without specifying a maximum concurrent agent count. The sequential phase structure and per-unit adversarial review impose coordination overhead. Without published evidence of runs at 6+ concurrent agents, architectural inference applies: the framework's overhead-heavy design (9 phases, per-unit adversarial review, 3-retry cycles) is optimized for quality over throughput, suggesting a practical ceiling lower than systems designed for raw parallelism. [MEDIUM CONFIDENCE — architectural inference; no empirical evidence at scale]
Source: github.com/dsifry/metaswarm README; first-principles reasoning from 9-phase workflow structure.

**Uncertainty flags**: D3 (no benchmark; creator claims production use), D5 (observability undocumented), D8 (no scale evidence).

---

### Overstory (jayminwest/overstory)

**D1 Cost — 3**: No platform fee; runs on any supported runtime (Claude Code, Pi, Gemini CLI, Aider, Goose, Amp). Cross-runtime routing allows selecting cheaper models for some agents. Token/cost analysis commands (`--live`, `--by-capability`, `--last`) provide per-run cost visibility. No published per-run benchmark. At representative scale the cost is comparable to other Claude Code orchestrators. [MEDIUM CONFIDENCE — model costs only; cross-runtime routing adds cost optimization potential]
Source: github.com/jayminwest/overstory README; deepwiki.com/jayminwest/overstory/8.5-agent-inspection.

**D2 Speed — 4**: Each agent runs in an isolated git worktree via tmux, with genuine concurrent execution. A tiered watchdog (Tier 0 mechanical daemon, Tier 1 AI-assisted triage, Tier 2 monitor agent) confirms continuous operation monitoring. SQLite mail system (WAL mode, ~1-5ms per query) enables fast inter-agent messaging without blocking. FIFO merge queue handles branch merges back to canonical. Architecture supports genuine parallelism without artificial serialization at the task level. No published wall-clock benchmarks. [MEDIUM CONFIDENCE — architecture supports parallelism; no timing benchmarks]
Source: web search result on Overstory architecture; github.com/jayminwest/overstory README.

**D3 Accuracy — 2**: No published SWE-Bench or independent benchmark. Overstory's STEELMAN.md (per available repository files) likely documents design rationale. No community benchmark data found. [LOW CONFIDENCE — no public evidence]
Source: No benchmark citation found in search results.

**D4 Workflow Rigor — 3**: Overstory provides: (a) instruction overlays and tool-call guards that enforce agent boundaries (a form of role/scope enforcement); (b) tiered watchdog system for health monitoring; (c) FIFO merge queue with 4-tier conflict resolution for integration; (d) typed protocol messages for inter-agent communication. These constitute role separation and structured coordination. However, no pre-execution interface contracts (equivalent to CONTRACT.md), no formal failure taxonomy, and no adversarial review step are documented. The 4-tier merge conflict resolution is the strongest coordination element. Satisfies D4=3 (role separation or retry-with-logging) but not D4=4 (3 of 4 components).
Source: web search results on Overstory architecture; github.com/jayminwest/overstory README description.

**D5 Observability — 4**: Overstory documents: `trace` command for agent/bead timeline viewing (replay-class observability); triage result type providing structured `{ verdict, fallback, reason }` output; per-agent token/cost analysis with multiple breakdown modes; tiered watchdog providing real-time fleet health monitoring (Tier 0 mechanical, Tier 1 AI triage, Tier 2 monitor). This combination — timeline trace, structured triage output, per-agent cost attribution, and live health monitoring — satisfies three of the four D5=5 components (structured logs, real-time status via watchdog, agent-level attribution). Replay/step-through capability is approximated by the trace command. Missing: mid-execution inspection without interrupting the run (the trace command appears post-hoc). Consistent with D5=4.
Source: web search result on Overstory trace command and triage observability; deepwiki.com/jayminwest/overstory/8.5-agent-inspection.

**D6 Recovery — 3**: Tiered watchdog (Tier 0 mechanical daemon, Tier 1 AI-assisted triage, Tier 2 monitor) provides automated health monitoring with structured triage output. The triage result type (`{ verdict, fallback, reason }`) implies multiple recovery options per failure. However, a formal failure taxonomy (≥3 named failure types with distinct handling paths) is not documented in available sources. The watchdog's escalation tiers approximate circuit breaker behavior. Failure state persists via Git-backed architecture. Consistent with D6=3 (retry with configurable max attempts, failure output fed back, no formal taxonomy).
Source: web search results on Overstory tiered watchdog; github.com/jayminwest/overstory README recovery section.

**D7 Setup — 3**: Overstory is a TypeScript/Node project (package.json visible in repository). Installation likely requires `npm install` or equivalent. Pluggable AgentRuntime interface for 11 runtimes adds configuration complexity. Tmux dependency for agent execution is an additional infrastructure requirement. INSTALLING.md documentation exists. Initial setup for a developer unfamiliar with the system requires understanding the runtime adapter model and SQLite mail system. Consistent with D7=3 (4-6 steps including tutorial; tmux and Node dependencies required; half-day to first productive run).
Source: github.com/jayminwest/overstory package.json; deepwiki.com/jayminwest/overstory/2.1-installation; README tmux and runtime adapter documentation.

**D8 Scalability — 4**: Pull-based tmux architecture with isolated worktrees per agent, SQLite WAL mail system for low-latency inter-agent messaging (~1-5ms), and a FIFO merge queue. The pluggable runtime interface supporting 11 runtimes suggests the architecture was designed for heterogeneous multi-agent deployment. Tiered watchdog is a fleet health mechanism consistent with larger agent counts. Overstory's README explicitly warns about "compounding error rates, cost amplification" at scale — suggesting the developer has experience with larger deployments. No documented ceiling below 10 agents. Architecture supports 6-8 effectively. [MEDIUM CONFIDENCE — architectural evidence supports 6-8+ agents; no empirical evidence at that scale published]
Source: web search result on Overstory SQLite mail architecture and tmux worktrees; github.com/jayminwest/overstory README scale warnings.

**Uncertainty flags**: D3 (no benchmark), D6 (failure taxonomy not documented), D8 (architectural inference only).

---

## Cross-System Observations

**Where competitors score higher than Spectrum on specific dimensions:**

- **D1 Cost**: Gas Town, oh-my-claudecode, Agent Teams, Citadel, metaswarm, and Overstory all score 3 vs. Spectrum's 2. Spectrum's documented per-run cost ($9.43 for 5-Howler full, $15.20 for 8-Howler full) is higher than comparable parallel runs in systems that do not impose an Opus-model muster phase or extensive pre-flight ceremony. This is a direct cost disadvantage Spectrum should acknowledge.

- **D2 Speed**: Gas Town (5) scores higher than Spectrum (3). Gas Town's GUPP principle eliminates the muster/approval gate that is structural to Spectrum. oh-my-claudecode (4), Agent Teams (4), Citadel (4), and Overstory (4) also score higher than Spectrum on speed. The muster overhead is Spectrum's most significant speed disadvantage.

- **D7 Setup**: oh-my-claudecode (5) scores materially higher than Spectrum (3). The zero-config design of oh-my-claudecode directly addresses the use case Spectrum's own README identifies as "Not For." Agent Teams (4) and Citadel (4) also have lower setup burden than Spectrum.

- **D8 Scalability**: Gas Town (5) scores higher than Spectrum (3), consistent with its explicit design for 20-30+ agents vs. Spectrum's documented 8-agent ceiling.

**Where Spectrum scores higher:**

- **D4 Workflow Rigor**: Spectrum (5) leads this group and the broader field. No other system in this group documents all four rigor components (pre-execution contracts, failure taxonomy, circuit breaker, independent adversarial review) as enforced protocol elements. Citadel (4) and metaswarm (4) are the closest competitors.

- **D6 Recovery**: Spectrum (4) ties with Citadel (4) and metaswarm (4), leading oh-my-claudecode (2), Agent Teams (2), and Gas Town (3).
