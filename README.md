# Spectrum Protocol v4.0

**A coordination protocol for parallel AI agents in Claude Code.**

Spectrum turns Claude Code's sub-agent system from a stateless dispatcher into a stateful, recoverable workspace. Workers maintain durable state, declare file ownership, communicate through structured debriefs, and follow a defined failure/recovery protocol.

No dependencies. No build step. No database. Copy three files and you're running.

---

## Agent Roster

Spectrum defines 14 agents across two tiers: the **core pipeline** (10 agents that run during a spectrum) and **auxiliary agents** (3 agents for adjacent work).

### Core Pipeline

| Color | Glyph | Role | Model | What They Do |
|-------|-------|------|-------|-------------|
| **Golds** | &#9819; | Orchestrator | Opus | Muster, contracts, seam analysis, merge planning |
| **Blues** | &#9678; | Planner | Sonnet | Scopes work, produces PLAN.md before spectrum activates |
| **Howlers** | &#187; | Worker | Sonnet+ | Implements tasks in isolated worktrees (parallel) |
| **Whites** | &#10022; | Reviewer | Sonnet | Pre-PR diff review, contract compliance |
| **Grays** | &#9960; | Tester | Sonnet | Runs tests, diagnoses failures, writes missing coverage |
| **Oranges** | &#10023; | Debugger | Sonnet | Root cause analysis when Howlers hit blockers |
| **Coppers** | &#9654; | Delivery | Haiku | Commits, branch naming, PR creation |
| **Obsidians** | &#8856; | Validator | Sonnet | Post-merge spec compliance against PLAN.md |
| **Browns** | &#8962; | Archivist | Haiku | Drafts LESSONS.md from spectrum artifacts |
| **Violets** | -- | Designer | Sonnet | Optional: produces DESIGN.md (behavioral spec) for API/schema work |
| **Politicos** | &#9889; | Critic | Sonnet | Adversarial review of contracts + manifest before freeze |

### Auxiliary Agents

| Color | Glyph | Role | Model | What They Do |
|-------|-------|------|-------|-------------|
| **Helldivers** | &#9672; | Researcher | Sonnet | Problem research, validation, opportunity sizing |
| **Primus** | &#8853; | Strategist | Sonnet | PRDs, prioritization, roadmaps |
| **Greens** | &#8801; | Decomposer | Sonnet | Breaks specs into scoped tickets |

---

## Protocol Phases

A Spectrum run follows seven phases:

| Phase | Name | What Happens |
|-------|------|-------------|
| 0 | **Blue Plans** | Blue scopes work into PLAN.md (prerequisite, not part of spectrum) |
| 1 | **Muster** | Gold decomposes tasks, writes MANIFEST.md + CONTRACT.md, defines file ownership |
| 1.5 | **The Passage** | Politico adversarially reviews the manifest and contract before freeze |
| 2 | **The Drop** | Gold spawns Howlers per DAG as dependencies are satisfied |
| 3 | **The Proving** | Each Howler runs triple quality gate: White + Gray + security review |
| 4 | **The Forge** | Failed Howlers are diagnosed, classified, and recovered or escalated |
| 5 | **Pax** | Gold independently validates all Howler work, cross-references seams, writes merge plan |
| 6 | **Triumph** | Human merges PRs, Gray runs integration tests, Obsidian verifies spec compliance |

Every phase writes to `CHECKPOINT.json`, enabling resume-from-any-point if a session dies.

---

## Quick Start

### One-line install

```bash
curl -fsSL https://raw.githubusercontent.com/ryantlee25-droid/spectrum-protocol/main/install.sh | bash
```

### Or manually

```bash
# 1. Copy the protocol files
cp spectrum/CLAUDE.md ~/.claude/CLAUDE.md
cp spectrum/SPECTRUM-OPS.md ~/.claude/SPECTRUM-OPS.md
cp spectrum/SPECTRUM.md ~/.claude/SPECTRUM.md

# 2. Copy agent definitions
mkdir -p ~/.claude/agents && cp agents/*.md ~/.claude/agents/

# 3. Copy tooling
mkdir -p ~/.claude/hooks && cp tools/seam_check.py ~/.claude/hooks/

# Done. No dependencies. No build step.
```

Then tell Claude Code: "Plan and build the auth system, dashboard, and API layer in parallel."

Gold will activate, run muster, and present a manifest for your approval before any Howlers are dropped.

**New to Spectrum?** Read the [Tutorial](TUTORIAL.md) for a full walkthrough. Keep the [Cheat Sheet](CHEATSHEET.md) handy.

---

## Feature Highlights

### File Ownership Matrix
Every file that will be created or modified is assigned to exactly one Howler. No overlaps, verified during muster and by the Politico. If two Howlers need the same file, Gold restructures the tasks.

### Frozen Contracts
CONTRACT.md is frozen at drop time. If a Howler discovers the contract is wrong, it stops and escalates -- it never silently diverges. Breaking changes require an AMENDMENT.md and Gold intervention.

### Design-by-Contract Per Worker
Each Howler gets formal preconditions, postconditions, and invariants in CONTRACT.md. Interface-heavy Howlers get full DbC; pure-create Howlers get conventions-only. No other multi-agent system surveyed implements this.

### Adversarial Plan Review (The Passage)
Before freezing the contract, Gold spawns a Politico -- an independent Sonnet agent that tries to break the plan. It looks for file ownership gaps, contract ambiguities, and decomposition flaws. Blockers must be fixed before Howlers drop.

### Independent Validation (Pax)
Gold does not trust Howler self-reports. During integration, Gold reads key files each Howler created and verifies them against CONTRACT.md postconditions. Discrepancies are flagged as integration risks.

### Typed Failure Taxonomy
Failures are classified into 5 types: `transient`, `logical`, `structural`, `environmental`, `conflict`. Each has a defined recovery path. A circuit breaker auto-escalates after 2 failures on the same locus.

### Durable State (HOOK.md)
Every Howler writes a HOOK.md immediately on start and updates it continuously. If a session dies, a new Howler can resume from the last checkpoint without repeating completed work.

### Triple Quality Gate
Before any PR opens: White (code review) + Gray (tests) + security diff review, all in parallel. Security criticals block. Coverage gaps warn but don't block.

### Reaping Mode
For small spectrum runs (3-4 Howlers, all creating new files, no shared interfaces), reaping mode cuts muster from ~8 minutes to ~3 minutes while keeping all quality gates intact.

### Budget Tracking
Optional token/cost budgets in CHECKPOINT.json. Gold checks cumulative cost before each Howler drop and presents options if the spectrum is projected to exceed budget.

---

## Best For

- **3-8 parallel agents** working on a mid-sized codebase
- Teams who want **safety guarantees** (file ownership, frozen contracts, adversarial review) over raw speed
- Projects where **failed parallel work is expensive** (the protocol prevents wasted effort through upfront planning)
- Claude Code users who want to **coordinate sub-agents** without installing a binary or running a daemon
- Teams building features that span **multiple domains** (auth + API + UI + tests)

## Not For

- **20+ agents at scale** -- use [Gas Town](https://github.com/steveyegge/gastown) (compiled Go, daemon architecture, built for high agent counts)
- **Zero-config quick start** -- use [oh-my-claudecode](https://github.com/nicekid1/oh-my-claudecode) (17k+ stars, community CLAUDE.md presets, no ceremony)
- **Single-agent tasks** -- Spectrum activates only for 3+ parallel features. For everything else, use Claude Code's standard agent routing.
- **Non-Claude-Code environments** -- Spectrum is built specifically for Claude Code's sub-agent and worktree primitives

---

## Evaluation

Spectrum was evaluated against **28 multi-agent systems** across four categories: Claude Code orchestrators, general-purpose frameworks (CrewAI, LangGraph, MetaGPT), commercial autonomous agents (Devin, Factory), and AI IDEs (Cursor, Kiro, Windsurf).

Key findings from the evaluation:

- **Three capabilities are unique to Spectrum** across all 28 systems: Design-by-Contract per worker, adversarial plan review (Politico), and independent Gold validation of worker self-reports
- Spectrum leads in coordination rigor (failure taxonomy, contract management, merge planning, quality gates)
- The field is converging on patterns Spectrum already implements: spec-before-code, git worktree isolation, quality gates before merge, model routing by task complexity

Full evaluation documents are in the [`evaluation/`](evaluation/) directory:
- [Final Audit Synthesis](evaluation/FINAL-AUDIT.md) -- cross-referenced findings from five independent analysis tracks
- [Agentic Landscape](evaluation/AGENTIC-LANDSCAPE.md) -- survey of 28 multi-agent systems
- [Token Optimization Guide](evaluation/TOKEN-OPTIMIZATION.md) -- cost analysis and optimization strategies
- [Cost Analysis](evaluation/COST-ANALYSIS.md) -- phase-by-phase token budget breakdown

---

## Repository Structure

```
spectrum-protocol/
├── README.md                  # You are here
├── LICENSE                    # MIT
├── INSTALL.md                 # Quick installation guide
├── TUTORIAL.md                # Step-by-step first run walkthrough
├── CHEATSHEET.md              # One-page quick reference
├── install.sh                 # One-line installer script
├── ACKNOWLEDGMENTS.md         # Credits and inspiration
├── spectrum/
│   ├── CLAUDE.md              # Main routing config (copy to ~/.claude/)
│   ├── SPECTRUM-OPS.md        # Operator's manual (~550 lines)
│   └── SPECTRUM.md            # Full specification (~2,300 lines)
├── agents/
│   ├── golds.md               # Orchestrator
│   ├── blues.md               # Planner
│   ├── howlers.md             # Worker
│   ├── whites.md              # Reviewer
│   ├── grays.md               # Tester
│   ├── oranges.md             # Debugger
│   ├── coppers.md             # Delivery
│   ├── obsidians.md           # Validator
│   ├── browns.md              # Archivist
│   ├── violets.md             # Designer
│   ├── politicos.md           # Critic
│   ├── helldivers.md          # Researcher
│   ├── primus.md              # Strategist
│   └── greens.md              # Decomposer
├── tools/
│   └── seam_check.py          # Seam validation tool
├── examples/
│   ├── MANIFEST.md            # Sample manifest
│   ├── CONTRACT.md            # Sample contract
│   ├── HOOK.md                # Sample Howler state
│   └── debrief.md             # Sample debrief
└── evaluation/
    ├── FINAL-AUDIT.md         # Audit synthesis
    ├── TOKEN-OPTIMIZATION.md  # Token cost guide
    ├── AGENTIC-LANDSCAPE.md   # 28-system landscape survey
    └── COST-ANALYSIS.md       # Phase-by-phase cost breakdown
```

---

## Token Costs

Spectrum runs on standard Claude Code API pricing. No additional costs.

| Spectrum Size | Estimated Total Tokens | Estimated Cost |
|---------------|----------------------|----------------|
| 3-Howler (Reaping) | ~540,000 | ~$4.80 |
| 5-Howler (Full) | ~955,000 | ~$9.43 |
| 8-Howler (Full) | ~1,460,000 | ~$15.20 |

Howlers consume 76% of tokens but only 32% of cost (Sonnet pricing). Gold consumes 15% of tokens but 45% of cost (Opus pricing). See [Token Optimization Guide](evaluation/TOKEN-OPTIMIZATION.md) for detailed breakdown.

---

## License

[MIT](LICENSE)

---

## Naming: The Red Rising Theme

Spectrum's agent names are drawn from the **Color caste system** in Pierce Brown's [Red Rising saga](https://www.piercebrown.com/) — a science fiction series where society is stratified into Colors, each with a defined role. Golds command. Howlers execute the impossible. Whites judge. Obsidians guard the line.

---

## Lineage & Inspiration

Spectrum exists because of [**steveyegge/gastown**](https://github.com/steveyegge/gastown) (13k+ stars), the first serious multi-agent orchestration system for Claude Code. Gas Town proved that parallel agents need persistent state (HOOK.md), structured communication (mailboxes), and health checks to work reliably.

**How Spectrum differs from Gas Town:**

| | Gas Town | Spectrum |
|---|---|---|
| Format | Compiled Go binary + daemon | Protocol-as-CLAUDE.md (plain text) |
| Installation | `go install` + config | Copy 3 files |
| Agent model | Generic workers | Typed Colors with defined responsibilities |
| Coordination | Health checks + message passing | Frozen contracts + file ownership matrix + DAG dispatch |
| Failure handling | Health check timeouts | Typed failure taxonomy (5 classes) + circuit breakers |
| Plan review | None | Adversarial Politico review before freeze |
| Integration | Post-merge validation | Independent Gold validation of worker self-reports |

Gas Town is the better choice for large-scale deployments (20+ agents) and teams who want a production daemon. Spectrum is the better choice for teams who want protocol-level safety guarantees without installing anything.

### Additional Acknowledgments

- [**Pierce Brown**](https://www.piercebrown.com/) — Red Rising created the Color system that makes Spectrum's agent roles instantly recognizable
- [**Anthropic**](https://docs.anthropic.com/en/docs/claude-code) — Claude Code's sub-agent and worktree primitives are the foundation Spectrum builds on
- **The ecosystem** — [Overstory](https://github.com/jayminwest/overstory) (structural tool enforcement), [Citadel](https://github.com/SethGammon/Citadel) (machine-verifiable phase conditions), [metaswarm](https://github.com/dsifry/metaswarm) (adversarial review gates), and [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) (context preservation) each contributed innovations that influenced v4.0

See [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md) for full credits.
