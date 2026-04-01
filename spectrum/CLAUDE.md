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

**Operator's manual** (for prompts): `~/.claude/SPECTRUM-OPS.md` (~550 lines — use this in Gold/Howler drop prompts)
**Full specification** (deep reference): `~/.claude/SPECTRUM.md` (~2,300 lines — read only when the OPS manual doesn't answer)

**What follows is the operational reference** — the rules Claude Code enforces during parallel execution.

### Activation Criteria

Spectrum activates when ALL of the following are true:
- Work spans 3+ independent features or domains
- A PLAN.md exists (run Blue first if not)
- The human explicitly confirms the spectrum manifest

For everything else, use standard single-agent routing.

### Phase 1 — Muster (Gold)

Gold plans the spectrum. Before dropping any Howlers:

1. **Generate rain ID** (short slug: `auth-refactor-0328`)
2. **Create spectrum directory**: `~/.claude/spectrum/<rain-id>/`
3. **Read LESSONS.md + ENTITIES.md** if present — incorporate past learnings and entity knowledge
4. **Validate PLAN.md** — sample 3-5 files to verify gap claims are current; flag stale assumptions
5. **Update ARCHITECTURE.md** — persistent codebase structure at `~/.claude/projects/<slug>/ARCHITECTURE.md`. If it exists, read it and patch only changed sections (new files, removed modules, shifted dependencies). If it doesn't exist, create it (~50-100 lines). Copy to spectrum directory for Howler reference. **Never regenerate from scratch** — incremental updates preserve cross-spectrum knowledge and save ~2 minutes.
6. **Optional Phase 0.5**: For API/schema spectrum runs, spawn Violet → DESIGN.md (behavioral spec)
7. **Decomposition hazard scan** — before writing MANIFEST.md, answer: (a) does any Howler synthesize outputs from others? Apply barrel file or fragment+stitch; (b) are any tasks inherently serial? Label them; (c) is any task significantly larger than peers? Flag as critical-path risk
8. **Write MANIFEST.md** to the spectrum directory with:
   - Task list with scope statements and per-Howler `effort: S/M/L`, `serial_risk: yes/no`
   - File ownership matrix (every CREATES/MODIFIES file appears exactly once)
   - Howler names and branch names
   - Dependency graph in DAG format (each node declares its own edges; no flat batch lists)
9. **Write CONTRACT.md** to the spectrum directory with:
   - Shared types, interfaces, constants that multiple Howlers depend on
   - Naming conventions and patterns Howlers must follow
   - Per-Howler codebase context: Gold reads each MODIFIES file and summarizes key patterns,
     function signatures, and gotchas (5–15 lines per file; skip for newly CREATED files)
   - Integration points (what connects to what)
   - Preconditions, postconditions, and invariants per Howler (full DbC for interface-heavy Howlers; conventions-only for pure-create Howlers)
   - Test impact map per Howler (run `tools/test_impact_map.py`; include in CONTRACT.md)
10. **White Pre-Check** — after writing CONTRACT.md, before freezing: drop White to verify all
    referenced files exist and documented signatures match the actual codebase. Gold patches
    CONTRACT.md based on findings. Skip for reaping mode and nano mode.
11. **Write `convoy-contracts.d.ts`** (at project root, or `src/types/convoy-contracts.d.ts` if `src/` exists) with shared TypeScript types; commit to the spectrum base branch before Howlers fork (TypeScript spectrum only; skip for doc-only spectrum runs)
12. **Adversarial plan review (Phase 1.5 — The Passage)** — spawn a Politico (Sonnet) to challenge CONTRACT.md and MANIFEST.md before freezing. The Politico reads both artifacts and tries to find: (a) file ownership gaps (files that will be needed but aren't in the matrix), (b) contract ambiguities (underspecified interfaces that will cause seam mismatches), (c) decomposition flaws (tasks that should be sequential but are parallel, or vice versa). Gold addresses Politico's objections or documents why they're acceptable. Only freeze CONTRACT.md after Politico has no remaining blockers. Skip for reaping mode.
13. **Present manifest + contract to human for approval** — explicitly flag high-risk seams and any Politico concerns that were accepted-with-rationale
14. **Do not drop Howlers until confirmed.**
15. **Write initial CHECKPOINT.json** (phase: approved, all howlers pending) with defined schema: `rain_id`, `phase` (enum: planning/approved/dispatching/running/integrating/merging/complete), `mode` (full/reaping), `howlers` (array of `{name, status, branch, worktree_path}`), `errors` (array), `resumed_at` (optional)
16. **Pre-create all worktrees** (post-approval, before drop):
    ```bash
    git worktree add -b spectrum/<id>/<howler-name> \
      ~/.claude/spectrum/<id>/worktrees/<howler-name> <base_commit>
    ```
    Verify with `git worktree list`. Howlers write files into pre-initialized directories — no branch creation needed. If git still fails, Howler sets `git_status: needs_operator_commit` in HOOK.md; Gold commits on their behalf.

**File ownership rule**: If two Howlers need to MODIFY the same file, restructure the tasks or make them sequential. No exceptions.

**CONTRACT.md is frozen at drop.** If a Howler discovers the contract is wrong, set `Status: blocked` and describe the needed change. Gold re-runs muster with the updated contract. Howlers never modify CONTRACT.md directly.

### Reaping Mode (3-4 Howlers, Pure-Create, No Interface Deps)

For small spectrum runs where full muster ceremony (~8 min) exceeds the actual work time, use reaping mode to cut overhead to ~3 min.

**Activation criteria (all must be true):**
- 3-4 Howlers maximum
- All Howlers only CREATE new files (no MODIFIES, no integration Howler)
- No shared TypeScript interfaces between Howlers at drop time
- Human explicitly requests "reaping" OR Gold judges overhead excessive

**In reaping mode, Gold writes:**
- **LIGHT-MANIFEST.md** — task list + file ownership only (no DAG YAML, no base_commit tracking)
- **Simplified CONTRACT.md** — naming conventions and shared patterns only (no per-Howler Design-by-Contract sections)
- **CHECKPOINT.json** — always required, includes `"mode": "reaping"`

**Skips:** ARCHITECTURE.md, full DAG, per-Howler Design-by-Contract, Obsidian, ENTITIES.md update

**Keeps (never downgrade):** White + Gray + /diff-review per Howler, HOOK.md per Howler, debrief per Howler, worktree pre-creation, LESSONS.md after merge

**Escalation:** If any Howler sets `Status: blocked` during reaping mode, Gold may upgrade to full spectrum mode (write full MANIFEST.md + CONTRACT.md) if the blocker suggests the tasks were not as independent as assumed.

### Nano Mode (2-3 Howlers, Pure-Create, Obvious Boundaries)

For runs where even reaping mode overhead is excessive. Targets muster + drop in under 1 minute.

**Activation criteria (all must be true):**
- 2-3 Howlers maximum
- All Howlers only CREATE new files (no MODIFIES)
- No shared interfaces between Howlers
- Task boundaries are obvious — human or Gold judges without analysis

**In nano mode, Gold writes:**
- **NANO-MANIFEST.md** — task list + file ownership only (no CONTRACT.md, no DAG)
- **CHECKPOINT.json** — always required, includes `"mode": "nano"`
- **Auto-approves** — presents manifest and drops Howlers immediately, no human confirmation gate

**Skips:** CONTRACT.md, Politico, ARCHITECTURE.md, Obsidian, ENTITIES.md, human approval gate, White + Gray + /diff-review, worktree pre-creation

**Keeps (never downgrade):** File ownership tracking, HOOK.md per Howler, debrief per Howler, LESSONS.md after merge

**Escalation:** If any Howler blocks, Gold upgrades to reaping mode immediately.

### Status Roster (Mandatory — All Phases)

Gold MUST print a status roster inline after every dispatch, completion, and phase transition. This is the user's primary visibility into the spectrum. Format: one line per agent with glyph, name, role, status symbol (`●` running, `✓` done, `✗` failed, `■` blocked, `○` pending), and task context. Include ALL agents (Blues, Whites, Grays, Coppers, Obsidians, Browns) — not just Howlers. See SPECTRUM-OPS.md for full format.

### Phase 2 — The Drop

**Structural enforcement**: During muster and drop, Gold MUST NOT use Write/Edit on project source files. Gold plans; it does not code. Only spectrum artifacts (MANIFEST.md, CONTRACT.md, etc.) are written by Gold.

Drop Howlers per DAG — drop each Howler when all its deps are satisfied. Checkpoint deps (`howler-name#types`) unblock on `STABLE` signal, not full completion. There is no concept of "batch complete" — Howlers advance as soon as their edges are satisfied. Branch naming: `spectrum/<rain-id>/<howler-name>`.

**Discovery relay**: When dropping Howlers whose dependencies have completed, Gold compresses completed Howlers' key findings into a ~500-token brief and includes it in the drop prompt. This propagates learnings without requiring the new Howler to read full debriefs.

**Post-drop worktree verification** is mandatory: after each Howler drop, verify branch name, base_branch, and base_commit match MANIFEST.md. Each DAG node specifies `base_branch` and `base_commit` to eliminate ambiguity.

**Howler execution rules** (in addition to CONTRACT.md):
- **Scope alignment check**: Every 20 tool calls, Howler re-reads original task + CONTRACT.md and writes `Alignment: on-track` or `Alignment: drifted — [reason]` in HOOK.md. If drifted, STOP and correct.
- **Completion verification**: Before declaring done, mechanically verify: all CREATES files exist (`ls`), all MODIFIES changed (`git diff --name-only`), type checks pass (`tsc --noEmit`), tests pass. Write results in HOOK.md `## Completion Verification`.
- **Issue re-read**: After completion verification, Howler re-reads the original task and writes a
  3–5 line correctness assessment in HOOK.md. If a gap is found, fix before quality gates.

### Phase 3 — The Proving (Per Howler)

Before opening a PR, every Howler runs ALL THREE in parallel:

1. **White** — zero blockers required
2. **Gray** — zero failures required (coverage gaps noted in PR, not blocking)
3. **/diff-review** — zero security criticals required (high/medium = warning in PR description)

**Worktree cleanup**: Before running quality gates on the merged branch, remove all Howler worktrees (`git worktree remove <path> --force; git worktree prune`) to prevent test framework false duplicates.

This is the same gate as single-agent PRs. Spectrum doesn't weaken quality standards.

### Phase 4 — The Forge

When a Howler fails, Gold reads its HOOK.md and:

1. **Classify the failure type**: `transient`, `logical`, `structural`, `environmental`, or `conflict`
2. **Transient failures**: Gold may auto-Resume without human confirmation
3. **All other types**: present the human with options

| Option | When to use |
|--------|-------------|
| **Resume** | `transient` or `logical` (after Orange diagnosis). Drop new Howler with: "Read HOOK.md and continue. Don't repeat checked-off work. Check Errors Encountered to avoid known dead ends." |
| **Retry** | `logical` (fresh approach needed). Drop fresh Howler with original task. |
| **Skip** | Any type (task is no longer needed or can be done later as follow-up). |
| **Restructure** | `structural` or `conflict` (contract/boundaries wrong). Re-plan with different decomposition. |

**Circuit breaker**: 2 failures on the same locus auto-escalate the failure type to `structural` — even if the individual failure was classified `transient` or `logical`. Gold pauses and escalates to human instead of dropping a third Howler.

### Phase 5 — Pax (Gold)

After all Howlers complete (or fail):

1. **Read all debrief entries** from `~/.claude/spectrum/<rain-id>/`
2. **Independent validation** — do NOT trust Howler self-reports. For each Howler, Gold reads 2-3 key files the Howler created/modified and verifies against CONTRACT.md postconditions. Check: (a) exported types match the contract, (b) integration points exist where claimed, (c) no files outside the ownership matrix were touched. Flag discrepancies as integration risks.
3. **Cross-reference seams**: every seam Howler A declares about Howler B should have a matching confirmation in Howler B's debrief
4. **Review cross-domain observations**: read each Howler's HOOK.md cross-domain section for issues that need attention before merge
5. **Validate assumptions**: every assumption maps to completed work
6. **Check for conflicts**: overlapping file creates, divergent implementations of the same interface
7. **Write PAX-PLAN.md** to the spectrum directory with: merge order, seam check results, independent validation results, warnings, integration risks
8. **Present to human for review**

**No auto-merging.** Human reviews and merges PRs in the recommended order. **Gray runs after each merge** (incremental integration testing for 3+ PRs). **Per-PR self-reflect**: after each merge, Gold writes a 3-5 line reflection in CHECKPOINT.json — what worked, what surprised, what the next merge should watch for.

**Budget tracking**: If `cost_tracking.budget_limit` is set in CHECKPOINT.json, Gold checks cumulative cost before each Howler drop. If projected to exceed budget, present options to human.

### Phase 6 — Triumph

After all PRs merge:
1. Run **Gray** on the fully merged main branch (final integration check)
2. If integration failures exist, fix as sequential follow-up (not a new spectrum)
3. Run **Obsidian** — verifies PLAN.md (+ DESIGN.md) acceptance criteria → SENTINEL-REPORT.md
4. Run **Brown** — drafts LESSONS.md + ENTITIES.md updates → Gold reviews and commits
5. Gold curates **ENTITIES.md**, records scaling observations in LESSONS.md
6. Set CHECKPOINT.json to "complete", delete `~/.claude/spectrum/<rain-id>/`

### Rules

- **No overlapping file ownership** — verified in muster and by Politico, no exceptions
- **Max 8 parallel Howlers** — more than this and coordination overhead dominates
- **Max 2 Orange retries per Howler** — then mark blocked, escalate to human
- **Dependent tasks run sequentially** — wait for the dependency's PR to merge first
- **Howlers are ephemeral, state is not** — HOOK.md and debrief survive Howler death
- **CONTRACT.md is frozen at drop** — Howlers block and escalate, never modify
- **Contract deviations must be filed as AMENDMENT.md** (`non-breaking` or `breaking`) — silent divergence is a blocker
- **Gold does not write source code** — only spectrum artifacts (structural enforcement)
- **Branch naming**: `spectrum/<rain-id>/<howler-name>`
- **Spectrum directories are ephemeral** — cleaned up after successful merge
- **`convoy-contracts.d.ts` committed to base branch before drop** (TypeScript spectrum only)
- **Transient failures may be auto-recovered; all other types require human confirmation**
- **Scope alignment check every 20 tool calls** — Howlers verify they're still on-task
- **Completion verification is mechanical** — `ls`, `git diff`, `tsc --noEmit`, test runner before declaring done
- **Discovery relay for dependent Howlers** — compressed findings from completed Howlers injected into drop
- **Per-PR self-reflect** — Gold captures learnings after each merge, not just post-spectrum
- **LESSONS.md written after every successful spectrum** to `~/.claude/projects/<project-slug>/memory/LESSONS.md`

---

## Pre-PR Quality Gates

Before Copper opens a PR/MR, run all three in parallel:

1. **White** — zero blockers
2. **Gray** — zero failures (coverage gaps noted in PR, not blocking)
3. **/diff-review** — zero security criticals (high/medium = warning in PR description)

**Always parallel** — spawn all three in the same message. Never sequential.

Coverage gaps and security high/medium findings are warnings, not blockers. Note them in the PR description and proceed.

---

## Model Assignments

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
- **Triple quality gate**: White + Gray + /diff-review in parallel per Howler (security criticals block)
- **CHECKPOINT.json at every phase transition**: enables resume-from-any-point on session death
- **ENTITIES.md curated after every spectrum**: entity-level project memory
- **Dynamic scaling**: 3+ tasks = spectrum, 2 = consider sequential, 1 = single-agent
- **Release notes in README**: before committing, Copper must update the `README.md` with a release notes section reflecting the changes being committed. Append a dated entry under a `## Release Notes` heading (create it if absent). Stage `README.md` alongside the other changed files before creating the commit.
