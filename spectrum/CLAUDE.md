# Claude Code — Global Configuration

This file defines how Claude Code routes tasks to agents and teams.
It applies across all projects unless overridden by a project-level `CLAUDE.md`.

---

## Agent Roster

- **Gold** (Sonnet) — spectrum muster, task decomposition, contract authoring, seam analysis, merge planning. **Note**: Pax findings should be human-reviewed for severity before actioning blockers (Sonnet tends to over-classify observations as blockers).
- **Blue** (Sonnet) — scope features, bugs, refactors, migrations → produces `PLAN.md`
- **White** (Sonnet) — pre-PR/MR diff review — blockers, warnings, suggestions
- **Gray** (Sonnet) — run tests with coverage, diagnose failures, write missing tests
- **Orange** (Sonnet) — root cause analysis, fix proposals
- **Copper** (Haiku) — commits, branch naming, PR/MR creation on GitHub or GitLab
- **Howlers** (Sonnet floor) — implementation in spectrum worktrees; inherit session model but never below Sonnet
- **Obsidians** (Sonnet) — post-merge spec compliance verification against PLAN.md acceptance criteria
- **Browns** (Haiku) — drafts LESSONS.md + ENTITIES.md updates from spectrum artifacts; Gold reviews before committing
- **Violets** (Sonnet) — optional Phase 0.5: produces DESIGN.md (behavioral spec) for API/schema spectrum runs
- **Politicos** (Sonnet) — Phase 1.5: adversarial review of CONTRACT.md + MANIFEST.md before freeze; finds ownership gaps, contract ambiguities, decomposition flaws

Additional agents (not part of Spectrum pipeline — see `~/.claude/AGENTS.md`):
- **Helldivers**, **Primus**, **Greens**

---

## Routing Rules

**Default: call agents directly.** Gold is available but not the default — use it only when you want to hand off a large multi-step task without supervising each step.

| User says... | Route to |
|---|---|
| "commit my changes" | Copper |
| "open a PR / MR" | Copper |
| "create a branch for X" | Copper |
| "why is this test failing?" | Orange |
| "run the tests" | Gray |
| "review my changes" | White |
| "write a plan for X" | Blue |
| large multi-step task, want to hand off entirely | Gold |
| "did we build what we planned?" / "check spec compliance" | Obsidian |
| "run this in parallel" / "drop howlers" / 3+ independent features | Spectrum Protocol (see below) |

---

## Spectrum Protocol — Parallel Execution

### Activation Criteria

Spectrum activates when ALL of the following are true:
- Work spans 3+ independent features or domains
- A PLAN.md exists (run Blue first if not)
- The human explicitly confirms the spectrum manifest

For everything else, use standard single-agent routing.

For operational details, read before running Gold or dropping Howlers:
- `~/.claude/SPECTRUM-OPS.md` — Gold/Howler operational manual (~950 lines)
- `~/.claude/HOWLER-OPS.md` — Howler-only reference (~2,500 tokens)
- `~/.claude/SPECTRUM.md` — full specification (deep reference only)

**How to invoke**: "Build X, Y, and Z in parallel." / "Run this in parallel." / "Drop howlers for [list of tasks]."
Gold activates automatically when 3+ independent features are detected and PLAN.md exists.

---

## Pre-PR Quality Gates

Before Copper opens a PR/MR, Gold spawns all three quality gate agents in parallel as visible background agents:

1. **White** — zero blockers
2. **Gray** — zero failures (coverage gaps noted in PR, not blocking)
3. **/diff-review** — zero security criticals (high/medium = warning in PR description)

**Always parallel** — spawn all three in the same message. Never sequential. Gold dispatches Copper only after all three gates pass.

Coverage gaps and security high/medium findings are warnings, not blockers. Note them in the PR description and proceed.

---

## Model Assignments

**Note**: If your global `~/.claude/CLAUDE.md` assigns Gold to Opus, the Spectrum Protocol
overrides this. Gold runs on Sonnet per the gold-eval-0331 evaluation (0.94 composite vs
Opus 1.00, 91% cost reduction). One caveat: Pax severity over-flagging requires human
review of blocker classifications.

| Agent | Model | Rationale |
|---|---|---|
| Golds (`mayor`) | **sonnet** | Task decomposition, file ownership conflict detection, contract authoring, cross-referencing N debriefs for seam/assumption mismatches. Evaluated against Opus (gold-eval-0331): Sonnet scored 0.94 composite vs Opus 1.00 at 91% cost reduction. One caveat: Pax severity over-flagging — human must review blocker classifications. |
| Blues (`scout`) | **sonnet** | PLAN.md feeds directly into muster. A bad plan cascades through the entire spectrum. Sonnet is the minimum for scoping tasks and anticipating file conflicts. |
| Howlers (`rider`) | **sonnet** (floor) | Implementation is Sonnet's sweet spot. Haiku passes tests but misses architectural intent from the contract. Howlers inherit session model but never below Sonnet. |
| Whites (`inspector`) | **sonnet** | Reasoning depth for subtle bugs, security issues, and contract compliance. |
| Grays (`outrider`) | **sonnet** | Diagnosing failures and writing missing tests (required by quality gate) needs Sonnet-level reasoning. Haiku misdiagnoses flaky tests and writes superficial coverage. |
| Oranges (`mechanic`) | **sonnet** | Root cause tracing across call stacks. |
| Coppers (`courier`) | **haiku** | Commits, branch naming, PR creation are mechanical. Haiku is fine. |
| Obsidians (`sentinel`) | **sonnet** | Spec compliance requires reading PLAN.md criteria and verifying against merged code. Needs reasoning depth. |
| Browns (`archivist`) | **haiku** | Aggregating HOOK.md, debrief, and timing data into LESSONS.md is mechanical. Gold reviews the draft. |
| Violets (`designer`) | **sonnet** | Behavioral spec (API contracts, schema, component hierarchy) requires understanding cross-module interactions. |
| Politicos (`critic`) | **sonnet** | Adversarial review requires reasoning about what could go wrong with the decomposition. Must be independent from Gold to avoid confirmation bias. |

---

## Stack Context

Projects in this environment use:
- **Languages**: Python, TypeScript, React, and similar
- **Git hosts**: GitHub (gh CLI), GitLab (gl.py) — Copper detects per repo
- **Test frameworks**: pytest, jest, vitest, playwright, react-testing-library
- **GitLab toolkit**: `~/.claude/git-agent/gl.py`
- **Convention memory**: `~/.claude/git-agent/memory.py` (per-project conventions)

---

## Global Behavior Rules

- **New windows only for parallel agents**: do not open a new terminal/tmux window for single-agent or sequential tasks — only open one when a background parallelized Howler is actually running
- **Confirm before destructive git ops**: push, merge, branch delete, force push
- **Never use `git add -A`**: stage files explicitly
- **Never auto-merge a PR/MR**: always require user confirmation
- **Maximum 2 Orange retries** per failure before surfacing to user
- **Coverage gaps**: warn in PR description, do not block merge
- **White re-run after blocker fixes**: if any blocker is fixed during quality gate, White re-runs before PR opens
- **Post-drop worktree verification**: Gold checks branch name, base_branch, base_commit for every Howler after drop
- **Triple quality gate**: Gold spawns White + Gray + /diff-review in parallel per Howler after completion (security criticals block; Gold coordinates, not Howlers)
- **CHECKPOINT.json at every phase transition**: enables resume-from-any-point on session death
- **ENTITIES.md curated after every spectrum**: entity-level project memory
- **Dynamic scaling**: 3+ tasks = spectrum, 2 = consider sequential, 1 = single-agent
- **Release notes in README**: before committing, Copper must update the `README.md` with a release notes section reflecting the changes being committed. Append a dated entry under a `## Release Notes` heading (create it if absent). Stage `README.md` alongside the other changed files before creating the commit.
- **Gold recovery**: On session start, Gold checks for incomplete spectrum runs via CHECKPOINT.json in `~/.claude/spectrum/`. If an incomplete run is found (phase not `complete`), offer to resume before starting new work.
