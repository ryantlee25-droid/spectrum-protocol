# Protocol Evaluation: Claude Code Ecosystem

> Group 1 of 3 | Evaluator: howler-claude-code | Rain: protocol-eval-0401
> Date: 2026-04-01

Scoring rubric: 1 (not addressed) to 5 (comprehensive with feedback loop).
Anti-inflation rule: claims without architectural evidence capped at 3.

---

## 1. Spectrum Protocol v5.1

**Source**: ~/.claude/CLAUDE.md, SPECTRUM.md, SPECTRUM-OPS.md (~3,700 lines total)
**Type**: CLAUDE.md coordination protocol for Claude Code sub-agents

### Scores

| # | Dimension | Score | Evidence |
|---|-----------|-------|----------|
| 1 | Task Decomposition | 5 | Gold decomposes via MANIFEST.md with per-Howler scope statements, effort sizing (S/M/L), serial_risk flags. Decomposition hazard scan answers three explicit questions before writing manifest. Politico adversarially reviews decomposition for flaws. |
| 2 | Conflict Prevention | 5 | File ownership matrix enforced at muster: every CREATES/MODIFIES file appears exactly once. Politico verifies no gaps. "If two Howlers need the same file, restructure the tasks." No exceptions. CONTRACT.md frozen at drop. |
| 3 | Communication Efficiency | 4 | Structured HOOK.md per Howler (cross-domain observations, errors encountered). Discovery relay compresses completed Howler findings into ~500-token briefs for dependent Howlers. No real-time inter-Howler messaging -- communication is async via artifacts. |
| 4 | Failure Recovery | 5 | Five failure types (transient/logical/structural/environmental/conflict) with typed recovery paths (Resume/Retry/Skip/Restructure). Circuit breaker: 2 failures on same locus auto-escalate to structural. Transient failures auto-recovered; all others require human confirmation. CHECKPOINT.json enables resume-from-any-point. |
| 5 | Knowledge Sharing | 4 | LESSONS.md written after every spectrum with Known Failure Patterns section. ENTITIES.md curated post-spectrum. Browns aggregate findings. Discovery relay propagates learnings to dependent Howlers. Cross-spectrum knowledge persists via ARCHITECTURE.md incremental updates. |
| 6 | State Management | 5 | CHECKPOINT.json at every phase transition with defined schema (rain_id, phase enum, mode, howlers array with status). HOOK.md per Howler survives Howler death. Debrief entries persist in spectrum directory. Full resume-from-any-point on session death. |
| 7 | Quality Assurance | 5 | Triple quality gate per Howler: White (zero blockers), Gray (zero failures), /diff-review (zero security criticals). Contract-to-test generation for structural postconditions. Scope alignment check every 20 tool calls. Mechanical completion verification (ls, git diff, tsc --noEmit). Obsidian post-merge spec compliance. |
| 8 | Scalability | 4 | Max 8 parallel Howlers enforced. Three mode tiers: nano (~1 min, 2-3 Howlers), reaping (~3 min, 3-4), full (~8 min, up to 8). DAG-based dependency resolution -- Howlers advance as edges are satisfied. Multi-candidate mode for accuracy-critical tasks. Constraint: single orchestrator (Gold) is a bottleneck at scale. |
| 9 | Mode Adaptability | 5 | Three explicit modes (nano/reaping/full) with clear activation criteria and escalation paths. Nano auto-escalates to reaping on block; reaping escalates to full on structural issues. SWE-bench mode for benchmark tasks. Multi-candidate mode for accuracy-critical work. |
| 10 | Setup Complexity | 4 | "No dependencies. No build step. No database. Copy four files." One-line curl install. But: ~3,700 lines of protocol spec across CLAUDE.md, SPECTRUM.md, SPECTRUM-OPS.md. Learning curve is significant even if setup is trivial. |
| 11 | Observability | 4 | Status roster mandatory after every dispatch/completion/phase transition with glyphs and status symbols. CHECKPOINT.json tracks all state. HOOK.md provides per-Howler visibility. Gap: no dashboard, no metrics collection, no cost tracking UI (budget_limit exists but no visualization). |
| 12 | Cost Awareness | 4 | Model assignments optimize cost (Haiku for mechanical tasks, Sonnet for reasoning). Budget tracking in CHECKPOINT.json. Reaping/nano modes explicitly reduce overhead. Gold-eval showed 91% cost reduction with Sonnet vs Opus. Gap: no per-run cost reporting or historical cost tracking. |

**Composite Score**: 4.50 / 5.00

### Strengths
- Most comprehensive coordination protocol in the Claude Code ecosystem
- Typed failure recovery with circuit breakers is unique among evaluated systems
- Three-tier mode system (nano/reaping/full) provides genuine adaptability
- File ownership enforcement eliminates a major class of merge conflicts

### Weaknesses
- Single orchestrator (Gold) is a scalability bottleneck
- No real-time inter-agent communication -- all async via artifacts
- Protocol complexity (~3,700 lines) creates a learning barrier
- No built-in cost tracking dashboard or metrics visualization

---

## 2. Gas Town (steveyegge/gastown)

**Source**: GitHub repository, public documentation
**Type**: CLAUDE.md coordination protocol for Claude Code sub-agents

### Scores

| # | Dimension | Score | Evidence |
|---|-----------|-------|----------|
| 1 | Task Decomposition | 4 | Mayor decomposes into Rider tasks with scope statements. Convoy manifest defines task boundaries. Less formal than Spectrum's decomposition hazard scan but effective. |
| 2 | Conflict Prevention | 4 | File ownership tracking in convoy manifest. Riders declare files they touch. No formal adversarial review (no Politico equivalent), but Mayor validates boundaries. |
| 3 | Communication Efficiency | 4 | Convoy mailboxes enable structured inter-agent communication. Health checks provide periodic status. More real-time communication model than Spectrum's async approach. |
| 4 | Failure Recovery | 3 | Riders can signal failure to Mayor. Mayor can retry or skip. No typed failure classification (transient vs structural). No circuit breaker mechanism. Basic but functional. |
| 5 | Knowledge Sharing | 3 | Rider debriefs after completion. No persistent cross-convoy knowledge (no LESSONS.md equivalent). No entity tracking. Knowledge is convoy-scoped. |
| 6 | State Management | 4 | Persistent state via HOOK.md (inspired Spectrum's adoption). Convoy state tracking. Riders maintain durable state that survives crashes. No formal checkpoint schema with resume-from-any-point. |
| 7 | Quality Assurance | 3 | Inspector role for code review. No triple quality gate. No contract-to-test generation. No scope alignment checks. Quality depends on Inspector thoroughness. |
| 8 | Scalability | 3 | Supports parallel Riders but no explicit scaling limits or DAG-based dependency resolution. No mode tiers for different task sizes. Convoy size is ad-hoc. |
| 9 | Mode Adaptability | 2 | Single convoy mode. No nano/reaping/full tier system. No SWE-bench or multi-candidate modes. Adapts through convoy size but not through protocol complexity reduction. |
| 10 | Setup Complexity | 4 | CLAUDE.md-based, similar simplicity to Spectrum. Fewer files to install. Less protocol complexity means lower learning curve. |
| 11 | Observability | 3 | Health checks provide periodic visibility. Convoy mailboxes serve as communication log. No formal status roster or checkpoint tracking. |
| 12 | Cost Awareness | 2 | No explicit model assignment optimization. No budget tracking. No mode tiers for cost reduction. Cost management is implicit. |

**Composite Score**: 3.25 / 5.00

### Strengths
- Pioneered persistent state (HOOK.md) and convoy mailboxes in Claude Code ecosystem
- Real-time communication via mailboxes is more flexible than pure async
- Lower complexity barrier than Spectrum
- Strong influence on the ecosystem (Spectrum adopted several Gas Town patterns)

### Weaknesses
- No typed failure recovery or circuit breakers
- No cross-convoy knowledge persistence
- No mode adaptability for different task scales
- No formal quality gate pipeline

---

## 3. oh-my-claudecode (Yeachan-Heo)

**Source**: GitHub repository
**Type**: Plugin/extension system for Claude Code

### Scores

| # | Dimension | Score | Evidence |
|---|-----------|-------|----------|
| 1 | Task Decomposition | 2 | Focuses on enhancing Claude Code's existing capabilities rather than multi-agent decomposition. Plugin architecture allows custom task handling but no structured decomposition protocol. |
| 2 | Conflict Prevention | 1 | Not addressed. Plugin system operates at single-agent level. No file ownership matrix or conflict prevention mechanism. |
| 3 | Communication Efficiency | 2 | Plugin hooks provide extension points. No inter-agent communication protocol. Communication is between human and single agent. |
| 4 | Failure Recovery | 2 | Relies on Claude Code's built-in error handling. Plugins can add custom error handling but no structured failure taxonomy. |
| 5 | Knowledge Sharing | 2 | Plugin system could enable knowledge persistence but no built-in mechanism. Individual plugins may implement their own. |
| 6 | State Management | 2 | Plugins can manage their own state. No protocol-level state management or checkpoint system. |
| 7 | Quality Assurance | 2 | Plugin hooks could add quality checks. No built-in quality gate pipeline. Depends on individual plugin implementation. |
| 8 | Scalability | 2 | Plugin architecture is extensible but not designed for multi-agent scaling. Single-agent focus. |
| 9 | Mode Adaptability | 2 | Plugin system is flexible by nature. Can adapt behavior through plugin selection. Not a multi-agent mode system. |
| 10 | Setup Complexity | 4 | Easy to install and configure. Plugin-based approach lets users add capabilities incrementally. Lower barrier than full coordination protocols. |
| 11 | Observability | 2 | Depends on plugin implementation. No built-in observability framework for multi-agent work. |
| 12 | Cost Awareness | 1 | Not addressed. No cost tracking or model assignment optimization. |

**Composite Score**: 2.00 / 5.00

### Strengths
- Low barrier to entry with plugin architecture
- Extensible -- users add only what they need
- Enhances single-agent Claude Code experience effectively
- Active community development

### Weaknesses
- Not designed as a multi-agent coordination protocol
- No file ownership, conflict prevention, or failure recovery
- No quality gate pipeline
- Scoring is inherently limited by single-agent focus

---

## 4. Citadel (SethGammon)

**Source**: GitHub repository
**Type**: CLAUDE.md coordination protocol for Claude Code sub-agents

### Scores

| # | Dimension | Score | Evidence |
|---|-----------|-------|----------|
| 1 | Task Decomposition | 3 | Structured task breakdown with role assignments. Less formal than Spectrum's manifest/DAG system but more structured than ad-hoc approaches. |
| 2 | Conflict Prevention | 3 | File scope tracking in task definitions. No formal ownership matrix enforcement or adversarial review. Relies on orchestrator discipline. |
| 3 | Communication Efficiency | 3 | Agent communication through structured artifacts. No mailbox system or discovery relay. Post-completion debriefs. |
| 4 | Failure Recovery | 2 | Basic retry capability. No typed failure classification or circuit breaker. Manual escalation for persistent failures. |
| 5 | Knowledge Sharing | 2 | Per-run artifacts but no cross-run knowledge persistence. No LESSONS.md or entity tracking equivalent. |
| 6 | State Management | 3 | Run state tracked in artifacts. Some checkpoint capability. Less formal than Spectrum's CHECKPOINT.json schema with phase enumeration. |
| 7 | Quality Assurance | 3 | Code review step before merge. No triple quality gate or contract-to-test generation. Quality checks are present but not as layered. |
| 8 | Scalability | 3 | Supports multiple parallel agents. No explicit scaling limits or DAG-based scheduling. |
| 9 | Mode Adaptability | 2 | Single operational mode. No scaling tiers for different task sizes. |
| 10 | Setup Complexity | 4 | CLAUDE.md-based setup similar to other Claude Code protocols. Reasonable documentation. |
| 11 | Observability | 2 | Basic status reporting. No formal status roster or structured checkpoint tracking. |
| 12 | Cost Awareness | 2 | Some model assignment guidance. No budget tracking or cost optimization tiers. |

**Composite Score**: 2.67 / 5.00

### Strengths
- Structured approach to Claude Code multi-agent coordination
- Clear role definitions
- Practical for small-to-medium parallel tasks
- Lower protocol overhead than Spectrum

### Weaknesses
- Limited failure recovery (no typed classification)
- No cross-run knowledge persistence
- No mode adaptability
- Quality assurance is single-layer

---

## 5. Overstory (jayminwest)

**Source**: GitHub repository
**Type**: CLAUDE.md configuration for Claude Code workflows

### Scores

| # | Dimension | Score | Evidence |
|---|-----------|-------|----------|
| 1 | Task Decomposition | 2 | Workflow-oriented rather than decomposition-oriented. Defines how Claude Code should handle common tasks. Not a multi-agent decomposition system. |
| 2 | Conflict Prevention | 1 | Not addressed. Single-agent workflow focus. No file ownership or conflict prevention mechanism. |
| 3 | Communication Efficiency | 1 | Single-agent workflow. No inter-agent communication needed or provided. |
| 4 | Failure Recovery | 2 | Workflow-level error handling guidance. No multi-agent failure taxonomy. |
| 5 | Knowledge Sharing | 2 | Workflow templates encode knowledge. No dynamic knowledge sharing between agents or across runs. |
| 6 | State Management | 1 | Relies on Claude Code's built-in state. No additional state management layer. |
| 7 | Quality Assurance | 2 | Workflow definitions can include quality steps. No formal quality gate pipeline. |
| 8 | Scalability | 1 | Single-agent workflows. Not designed for multi-agent scaling. |
| 9 | Mode Adaptability | 2 | Different workflows for different task types. Not multi-agent mode adaptation. |
| 10 | Setup Complexity | 5 | Minimal setup -- copy CLAUDE.md. Focused scope means less to learn. Easiest entry point in the ecosystem. |
| 11 | Observability | 1 | No multi-agent observability. Standard Claude Code output. |
| 12 | Cost Awareness | 1 | Not addressed. |

**Composite Score**: 1.75 / 5.00

### Strengths
- Simplest setup in the ecosystem
- Effective for single-agent workflow optimization
- Good entry point for Claude Code users
- Clean, focused scope

### Weaknesses
- Not a multi-agent coordination protocol (scoring is inherently limited)
- No conflict prevention, failure recovery, or quality gates
- No state management beyond Claude Code defaults
- No knowledge sharing or observability

---

## Group Summary

| System | Composite | Rank |
|--------|-----------|------|
| Spectrum Protocol v5.1 | 4.50 | 1 |
| Gas Town | 3.25 | 2 |
| Citadel | 2.67 | 3 |
| oh-my-claudecode | 2.00 | 4 |
| Overstory | 1.75 | 5 |

**Key observations:**
- Spectrum is the only system with typed failure recovery, mode adaptability, and triple quality gates
- Gas Town pioneered key patterns (HOOK.md, mailboxes) that Spectrum formalized and extended
- oh-my-claudecode and Overstory are not multi-agent coordination protocols; their low scores reflect scope mismatch, not quality
- The Claude Code ecosystem shows a clear maturity gradient from workflow configs to full coordination protocols
