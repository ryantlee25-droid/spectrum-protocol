# Spectrum Protocol v4.0

**A coordination protocol for parallel AI agents in Claude Code.**

Spectrum turns Claude Code's sub-agent system from a stateless dispatcher into a stateful, recoverable workspace. Howlers maintain durable state, declare file ownership, communicate through structured debriefs, and follow a defined failure/recovery protocol.

Inspired by [steveyegge/gastown](https://github.com/steveyegge/gastown). Adapted for Claude Code's native agent and worktree primitives.

---

## Roles

| Name | `subagent_type` | Role | Model | Color |
|------|----------------|------|-------|-------|
| **Golds** ♛ | `golds` | Orchestrator -- muster, contracts, seam analysis, merge planning | Sonnet | `yellow` |
| **Blues** ◎ | `blues` | Planner -- scopes work, produces PLAN.md before spectrum activates | Sonnet | `blue` |
| **Howlers** » | `howlers` | Workers -- implement tasks in isolated worktrees | Sonnet (floor) | `orange` |
| **Whites** ✦ | `whites` | Code reviewer -- pre-PR diff review, contract compliance | Sonnet | `purple` |
| **Grays** ⛨ | `grays` | Test runner -- runs tests, diagnoses failures, writes missing coverage | Sonnet | `gray` |
| **Oranges** ✧ | `oranges` | Debugger -- root cause analysis when Howlers hit blockers | Sonnet | `red` |
| **Coppers** ▶ | `coppers` | Delivery -- commits, branch naming, PR creation | Haiku | `cyan` |
| **Obsidians** ⊘ | `obsidians` | Spec compliance -- post-merge verification against PLAN.md acceptance criteria | Sonnet | `teal` |
| **Browns** ⌂ | `browns` | Retrospective -- drafts LESSONS.md from HOOK.md, debriefs, White reports, timing | Haiku | `overlay` |
| **Politicos** ⚡ | `politicos` | Adversarial -- challenges CONTRACT.md + MANIFEST.md before freeze (Phase 1.5) | Sonnet | `red` |

Auxiliary agents (not part of spectrum -- see `~/.claude/AGENTS.md`):

| Name | `subagent_type` | Role | Model | Color |
|------|----------------|------|-------|-------|
| **Helldivers** ◈ | `helldivers` | Problem research, validation, opportunity sizing | Sonnet | `yellow` |
| **Primus** ⊕ | `primus` | PRDs, prioritization, roadmaps, strategy | Sonnet | `green` |
| **Greens** ≡ | `greens` | Decompose specs into scoped Jira tickets | Sonnet | `green` |

Agent definitions live in `~/.claude/agents/{role-name}.md`. Claude Code's built-in agent names (`code-reviewer`, `test-runner`, etc.) are preserved as aliases in the role detection system for backward compatibility.



---

## The Problem

Claude Code can spawn parallel sub-agents in isolated git worktrees. Out of the box, those agents are:

- **Ephemeral** -- if a session dies, all context is lost. No recovery.
- **Silent** -- Howlers can't communicate with each other during execution. Gold only sees results after completion.
- **Uncoordinated** -- there's no handoff protocol. Howler A can't tell Howler B "I created this type, import it from here."
- **Uncontracted** -- Howlers interpret tasks independently. Two Howlers touching adjacent code can produce inconsistent patterns.

This works for 1-2 small parallel tasks. It breaks at scale.

---

## When Spectrum Activates

Spectrum is NOT the default mode. Use standard single-agent execution unless:

- Work spans 3+ independent features or domains
- The human explicitly asks to run in parallel or drop Howlers
- A PLAN.md exists with parallelizable tasks and non-overlapping file scope

For single tasks, sequential work, or simple requests: route directly to the appropriate agent with zero overhead.

### Reaping Mode

For small spectrum runs (3-4 Howlers, all pure-create, no shared interfaces), use Reaping Mode to reduce muster from ~8 minutes to ~3 minutes. Reaping mode skips ARCHITECTURE.md, full DAG YAML, per-Howler Design-by-Contract, Obsidian, and ENTITIES.md — but never downgrades quality gates (White + Gray + /diff-review), HOOK.md, debriefs, or worktree pre-creation. See SPECTRUM-OPS.md for the full reaping mode procedure.

Gold sets `"mode": "reaping"` in CHECKPOINT.json. If a Howler blocks during reaping mode, Gold may escalate to full spectrum mode.

### Nano Mode

For 2-3 Howler runs with obvious task boundaries, use Nano Mode to reduce muster to under 1 minute. Nano mode skips CONTRACT.md, Politico, ARCHITECTURE.md, Obsidian, ENTITIES.md, the human approval gate, and all quality gates (Howlers self-verify only). Howlers create their own branches — no pre-created worktrees. The one non-negotiable: file ownership tracking (without it, nano mode is indistinguishable from uncoordinated parallel execution).

Gold sets `"mode": "nano"` in CHECKPOINT.json and auto-approves after presenting NANO-MANIFEST.md. If any Howler blocks, Gold escalates to reaping mode immediately. See SPECTRUM-OPS.md for the full nano mode procedure.

**Mode continuum**: nano (~1 min) → reaping (~3 min) → full (~8 min). Choose based on task count, shared file modifications, and how obvious the task boundaries are.

---

## The Architecture

```
Human: "build the auth system, the dashboard, and the API layer"
  |
  v
Blue -> PLAN.md (if one doesn't exist)
  |
  v
Gold
  |
  |  Muster:
  |  1. Decomposes tasks with explicit file ownership
  |  2. Writes MANIFEST.md (who does what, touching which files)
  |     DAG edges replace flat batches — Howlers dispatch as deps are satisfied
  |  3. Writes CONTRACT.md (shared types, conventions, integration points)
  |     convoy-contracts.d.ts committed to base branch for TypeScript spectrum runs
  |  4. Reads LESSONS.md if present (project memory from prior spectrum runs)
  |  5. Presents to human for approval
  |
  |  [human confirms]
  |
  |  Dispatch:
  |  6. Spawns Howlers as DAG edges are satisfied (not in flat batches)
  |     Each Howler receives: task + file ownership + CONTRACT.md
  |
  +--------+---------+---------+
  |        |         |         |
  v        v         v         v
Howler  Howler    Howler    Howler
  |        |         |         |
  | Each Howler:
  | a. Writes HOOK.md immediately (persistent state)
  | b. Implements the task
  | c. Updates HOOK.md continuously (decisions, seams, blockers)
  | d. Marks type checkpoints STABLE when interfaces are finalized
  | e. Runs White + Gray in parallel (quality gate)
  | f. Writes debrief entry with YAML frontmatter (handoff manifest)
  | g. Opens a PR via Copper
  |
  +--------+---------+---------+
  |
  v
Gold reads all debriefs
  |
  | Pax:
  | - Automated seam-check against YAML frontmatter (writes SEAM-CHECK.md)
  | - Validates assumptions and file overlap
  | - Reads AMENDMENT.md files from Howler worktrees
  | - Writes PAX-PLAN.md with merge order, warnings, integration risks
  |
  v
Human merges PRs in recommended order (Gray runs after each merge)
  |
  v
Gray on fully merged branch (final integration check)
  |
  v
Phase 6.25: Obsidian verifies spec compliance -> SENTINEL-REPORT.md
  |
  v
Phase 6.5: Brown drafts LESSONS.md -> Gold reviews -> spectrum directory cleaned up
```

---

## Phase 1: Muster

Before spawning any Howlers, Gold completes ALL of the following.

### 1.1 Task Decomposition

Break the work into discrete tasks. Each task must have:
- A clear scope statement (1-2 sentences)
- An explicit list of files it will **CREATE** or **MODIFY**
- A list of files it will **READ** (but not change)
- Named dependencies on other tasks (if any), expressed as DAG edges

### 1.2 File Ownership Matrix and DAG

Every file that any Howler will create or modify must appear exactly once. This is written to `MANIFEST.md` in the spectrum directory.

In v4.0, dependencies are expressed as a **DAG** rather than flat batch lists. Each node declares its own edges; Gold does not pre-group Howlers into batches.

**DAG node format** (per contract C2):

```yaml
- id: howler-auth
  deps: []
  howler: howler-auth
  branch: spectrum/auth-refactor-0328/howler-auth
  base_branch: staging
  base_commit: abc1234

- id: howler-api
  deps: [howler-auth#types]
  howler: howler-api
  branch: spectrum/auth-refactor-0328/howler-api
  base_branch: staging
  base_commit: abc1234

- id: howler-ui
  deps: [howler-auth#types]
  howler: howler-ui
  branch: spectrum/auth-refactor-0328/howler-ui
  base_branch: staging
  base_commit: abc1234
```

- `base_branch` is the branch the Howler's worktree forks from (e.g., `main`, `staging`, `develop`). All Howlers in an spectrum run normally share the same base branch.
- `base_commit` is the short SHA of the base branch tip at dispatch time. Gold records this during muster and the post-dispatch worktree verification (§2.1a) checks against it.

- `deps` is an array of strings. An empty array means no dependencies.
- Each dep is either `howler-name` (full completion — Howler's debrief entry exists) or `howler-name#checkpoint-name` (checkpoint dependency — Howler's HOOK.md shows that checkpoint as `STABLE`).
- The only checkpoint defined in v4.0 is `types`. Future checkpoints require a contract amendment.

**Dispatch behavior**: When any Howler completes or reaches a checkpoint, Gold immediately checks the DAG for Howlers whose **all** deps are now satisfied and dispatches them without delay. There is no concept of "batch complete" — Howlers advance as soon as their edges are satisfied.

**Example dispatch sequence** for `auth-refactor-0328`:

1. Muster complete → `howler-auth` has no deps → dispatched immediately
2. `howler-auth` marks `types: STABLE` in HOOK.md → `howler-api` dep `howler-auth#types` satisfied → dispatched immediately; `howler-ui` dep `howler-auth#types` satisfied → dispatched immediately
3. `howler-api` and `howler-ui` run in parallel
4. Both complete → no remaining Howlers → spectrum proceeds to Phase 4

This removes artificial batch wait: if a five-Howler spectrum run has three Howlers with no deps and two that depend only on checkpoint `types`, all three start immediately, and the remaining two start as soon as the `types` checkpoint fires — even if other Howlers from the first group are still running.

**Full MANIFEST.md template:**

```markdown
# Manifest: auth-refactor-0328

## Howlers

| Howler | Scope |
|-------|-------|
| howler-auth | Clerk middleware, auth routes, session types |
| howler-api | User and org API routes |
| howler-ui | Dashboard shell, header, sidebar |

## Dependency DAG

```yaml
- id: howler-auth
  deps: []
  howler: howler-auth
  branch: spectrum/auth-refactor-0328/howler-auth
  base_branch: staging
  base_commit: abc1234

- id: howler-api
  deps: [howler-auth#types]
  howler: howler-api
  branch: spectrum/auth-refactor-0328/howler-api
  base_branch: staging
  base_commit: abc1234

- id: howler-ui
  deps: [howler-auth#types]
  howler: howler-ui
  branch: spectrum/auth-refactor-0328/howler-ui
  base_branch: staging
  base_commit: abc1234
```

## File Ownership Matrix

```
howler-auth:
  CREATES:  src/middleware/auth.ts
            src/types/auth.ts
            src/routes/sign-in.tsx
  MODIFIES: src/app/layout.tsx
  READS:    src/config/env.ts

howler-api:
  CREATES:  src/api/users.ts
            src/api/orgs.ts
  MODIFIES: src/app/api/route.ts
  READS:    src/types/auth.ts (from contract; howler-auth creates this file)

howler-ui:
  CREATES:  src/components/Dashboard.tsx
            src/components/Header.tsx
  MODIFIES: src/app/page.tsx
  READS:    src/types/auth.ts (from contract; howler-auth creates this file)

CONFLICTS: none
```
```

**Rules:**
- If two Howlers need to MODIFY the same file: restructure the tasks or make them sequential. No exceptions.
- If a Howler READS a file another Howler CREATES: the reader codes against the contract, not the actual file (which may not exist yet).
- No Howler modifies another Howler's CREATES list. If a seam requires it, split the work or make them sequential.

### 1.3 Shared Contract

`CONTRACT.md` defines shared interfaces, types, constants, and conventions that multiple Howlers depend on. Every Howler receives this in their task prompt.

In v4.0, CONTRACT.md includes **Design-by-Contract sections** for each Howler: preconditions, postconditions, and invariants. These make seam-checking attributable during Phase 4: Gold can ask "Did Howler A satisfy the postconditions that Howler B declared as preconditions?"

**CONTRACT.md template:**

```markdown
# Contract: auth-refactor-0328

**Frozen at dispatch. If this contract is wrong, set Status: blocked in HOOK.md
and describe the needed change. Do NOT modify this file directly.**

## Shared Types

Source of truth: `convoy-contracts.d.ts` at project root (or `src/types/convoy-contracts.d.ts`
if `src/` exists). All Howlers import shared types from this file; they never redeclare them.

- `UserSession { userId: string; orgId: string; role: 'admin' | 'member' }`
- `AuthContext { session: UserSession | null; isLoaded: boolean }`
- `AuthResponse { ok: boolean; session: UserSession | null; error?: string }`

## Shared Constants

- Auth routes: /sign-in, /sign-up, /sign-out
- Protected route prefix: /dashboard/*

## Conventions

- All API routes use auth() from @clerk/nextjs for session access
- Error responses follow `{ error: string; code: number }` shape
- All new components use named exports (not default)
- All new files use the existing project's import alias (@/)

## Design-by-Contract: howler-auth

### Preconditions
- Clerk environment variables are present in the project's .env
- No existing middleware.ts at project root (or Gold has confirmed it can be overwritten)

### Postconditions
- `src/types/auth.ts` exists and exports `UserSession`, `AuthContext`, `AuthResponse`
- `src/middleware/auth.ts` exports a default middleware that gates /dashboard/* routes
- HOOK.md checkpoint `types: STABLE` is set before the postconditions on file content are complete, once interfaces are finalized and unlikely to change

### Invariants
- `UserSession.role` is always `'admin' | 'member'` — never widened to `string`
- Auth middleware never imports from API route files (no circular deps)

## Design-by-Contract: howler-api

### Preconditions
- `howler-auth#types` checkpoint is STABLE (interfaces are finalized)
- `UserSession`, `AuthResponse` are importable from `convoy-contracts.d.ts`

### Postconditions
- All user and org routes return responses matching `AuthResponse`
- No route handler redeclares `UserSession` — all imports come from the contracts file

### Invariants
- No circular imports between `src/api/` and `src/middleware/`

## Design-by-Contract: howler-ui

### Preconditions
- `howler-auth#types` checkpoint is STABLE
- `AuthContext` is importable from `convoy-contracts.d.ts`

### Postconditions
- Dashboard and Header components accept `AuthContext` as a prop (not inline-typed)
- No component file redeclares `UserSession` or `AuthContext`

### Invariants
- No UI component imports directly from `src/api/` (goes through hooks or server components only)
```

This eliminates the "howler-2 assumed something howler-1 didn't build" failure mode. Howlers code against the contract, not against each other's output.

**CONTRACT.md is frozen at dispatch.** If a Howler discovers the contract is wrong, set `Status: blocked` in HOOK.md and describe the needed change. Gold re-runs muster with the updated contract. Howlers never modify CONTRACT.md directly.

### 1.3a Compiler-Enforced Contracts (TypeScript Spectrum Runs)

For TypeScript spectrum runs, Gold generates a shared declarations file during muster and commits it to the spectrum base branch **before** Howlers fork their worktrees.

**File location** (per contract C6):

```
convoy-contracts.d.ts               (project root, if no src/ directory)
src/types/convoy-contracts.d.ts     (if src/ directory exists)
```

**What goes in this file:**

All shared interfaces, types, and constants declared in CONTRACT.md under "Shared Types" are written as TypeScript ambient declarations. Howlers never redeclare these types — they import from this file.

```typescript
// convoy-contracts.d.ts
// Auto-generated by Gold during muster for spectrum auth-refactor-0328.
// Do not edit manually. Source of truth: CONTRACT.md.

export interface UserSession {
  userId: string;
  orgId: string;
  role: 'admin' | 'member';
}

export interface AuthContext {
  session: UserSession | null;
  isLoaded: boolean;
}

export interface AuthResponse {
  ok: boolean;
  session: UserSession | null;
  error?: string;
}
```

**Quality gate**: `tsc --noEmit` is a mandatory check in every Howler's quality gate for TypeScript spectrum runs. A type error anywhere in the project is a blocker — it means a Howler redeclared a shared type or drifted from the contract.

**Documentation spectrum runs**: If the spectrum run produces no TypeScript (e.g., doc-only, markdown-only), skip this step entirely.

**Steps for Gold during muster:**

1. Check whether `src/` exists in the project root
2. Write `convoy-contracts.d.ts` (or `src/types/convoy-contracts.d.ts`) with all shared types
3. Commit this file to the spectrum base branch
4. Howlers fork from this commit, so the contracts file is present from the start
5. Add a reference in CONTRACT.md under "Shared Types": `Source of truth: convoy-contracts.d.ts`

### 1.4 Adversarial Plan Review (Phase 1.5)

Before freezing CONTRACT.md, Gold spawns a **Politicos** agent (Sonnet) to adversarially review the plan. Politico is a separate agent — not Gold reviewing its own work — to avoid confirmation bias.

**Politico prompt template:**

```
Read MANIFEST.md and CONTRACT.md for spectrum {id}. You are the adversary.
Find:
(a) File ownership gaps — files that will be needed but aren't in the matrix
(b) Contract ambiguities — underspecified interfaces that will cause seam mismatches
(c) Decomposition flaws — tasks that should be sequential but are parallel, or vice versa
(d) Integration bottlenecks — Howlers that will become serial bottlenecks or stub generators
Report: blockers (must fix before dispatch), warnings (should fix), observations (FYI).
Be specific — name files and interfaces. Reference CONTRACT.md sections.
```

**Gold response protocol:**
- **Blockers**: Must be addressed. Update MANIFEST.md or CONTRACT.md before proceeding.
- **Warnings**: Document in MANIFEST.md under a "Politico Warnings (Accepted)" section with rationale for each.
- **Observations**: Noted in CHECKPOINT.json under `politico_observations`.

**Skip for reaping mode runs** — the reduced artifact surface makes adversarial review low-value.

### 1.5 Approval Gate

Present to the human:

1. MANIFEST.md (tasks, dependency DAG, file ownership matrix, Politico warnings with rationale)
2. CONTRACT.md (shared interfaces, Design-by-Contract sections per Howler)
3. For TypeScript spectrum runs: confirm `convoy-contracts.d.ts` has been committed to the base branch
4. Howler count and estimated scope
5. Any high-risk seams flagged by Gold or Politico

**Muster checklist (Gold must complete before presenting):**

- [ ] PLAN.md validated (sampled files confirm gap claims are current)
- [ ] DAG is acyclic — no circular dependencies
- [ ] File ownership matrix has zero overlapping CREATES or MODIFIES
- [ ] Decomposition hazard scan completed
- [ ] Every Howler has effort/risk tags in MANIFEST.md
- [ ] Politico review completed — blockers addressed, warnings documented (skip for reaping mode)
- [ ] Every shared type in CONTRACT.md is present in `convoy-contracts.d.ts` (TypeScript spectrum runs only)
- [ ] `convoy-contracts.d.ts` committed to base branch (TypeScript spectrum runs only)
- [ ] Every Howler has Preconditions, Postconditions, and Invariants in CONTRACT.md (full DbC for interface-heavy; conventions-only for pure-create)
- [ ] Every checkpoint dep in the DAG corresponds to a checkpoint name defined in the contract
- [ ] `LESSONS.md` read if present at `~/.claude/projects/<project-slug>/memory/LESSONS.md` — past mistakes incorporated into this decomposition
- [ ] ARCHITECTURE.md updated (persistent, incremental — not regenerated)

**Do not spawn Howlers until the human confirms.**

### 1.5 Worktree Pre-Creation (Post-Approval)

After human approval and before dispatching any Howlers, Gold pre-creates all worktrees. This eliminates the ~50% git permission failure rate observed across two production spectrum runs (remnant-narrative-0329, remnant-ux-0329).

**For each Howler in the DAG:**

```bash
git worktree add -b spectrum/<rain-id>/<howler-name> \
  ~/.claude/spectrum/<rain-id>/worktrees/<howler-name> \
  <base_commit>
```

**Verification:**

```bash
git worktree list  # All spectrum worktrees should appear
```

**Rationale:** Howlers write files into pre-initialized directories. They never need to create branches or run initial commits. Gold retains git authority; Howlers exercise write authority only. If a Howler's git operations still fail (edge case), it sets `git_status: needs_operator_commit` in HOOK.md and Gold commits on its behalf after file writes are complete.

---

## Status Roster (Mandatory — All Phases)

Gold MUST print a status roster inline in the conversation at every phase transition and after each agent dispatch or completion. This is the user's primary visibility into the spectrum.

**Format:**

```
━━━ Spectrum: {rain-id} — {phase name} ━━━

  ♛ Golds       Orchestrator   ● active
  ◎ Blues        Planner        ✓ done
  » howler-auth Worker         ● running    (auth middleware)
  » howler-api  Worker         ● running    (API routes)
  » howler-ui   Worker         ○ pending    (waiting: howler-auth#types)
  ✦ Whites      Reviewer       ○ queued
  ⛨ Grays       Tester         ○ queued
  ▶ Coppers     Delivery       ○ queued

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Status symbols:** `●` running, `✓` complete, `✗` failed, `■` blocked, `○` pending/queued.

**When to print:**
1. After muster approval (full roster, all pending)
2. After each Howler dispatch (update to `●`)
3. After each agent completion or failure (update to `✓` or `✗`)
4. At every phase transition
5. On user request

**Rules:**
- Include ALL agents — Blues, Whites, Grays, Coppers, Obsidians, Browns — not just Howlers
- Show task in parentheses for Howlers, dependency waits for pending ones
- Show each quality gate agent (White + Gray + /diff-review) per Howler during The Proving
- One line per agent, compact

---

## Phase 2: The Drop

### 2.0 Structural Enforcement

During muster and dispatch, Gold MUST NOT use Write or Edit tools on project source files. Gold plans; it does not code. The only files Gold writes are spectrum artifacts (MANIFEST.md, CONTRACT.md, ARCHITECTURE.md, CHECKPOINT.json, convoy-contracts.d.ts). If Gold needs to modify source code, that work belongs to a Howler.

### 2.0a Discovery Relay

When dispatching Howlers whose dependencies have completed, Gold compresses completed Howlers' key findings into a ~500-token brief and includes it in the dispatch prompt under `DISCOVERY RELAY`. This propagates decisions, file paths, and warnings from early Howlers to later Howlers without requiring full debrief reads.

**Include**: Key decisions (from HOOK.md), file paths created, warnings, cross-domain observations relevant to the new Howler.
**Exclude**: Full debrief content, error logs, or anything CONTRACT.md already covers.

### 2.1 Howler Dispatch

Each Howler is spawned as a background Agent with `isolation: "worktree"`. Gold uses the following template for every Howler prompt:

```
Agent(isolation="worktree", run_in_background=True, model="sonnet", prompt="
  Spectrum: {rain-id}
  Howler: {howler-name}
  Branch: spectrum/{rain-id}/{howler-name}
  Worktree: ~/.claude/spectrum/{rain-id}/worktrees/{howler-name}
  Task: {scope statement from MANIFEST.md}

  WORKTREE NOTE: Your worktree is pre-initialized on branch
  spectrum/{rain-id}/{howler-name} from commit {base_commit}. Write your files
  to this directory. If git operations fail, write all files and set
  git_status: needs_operator_commit in HOOK.md — Gold will commit on
  your behalf.

  File Ownership:
    CREATES: {files from MANIFEST.md}
    MODIFIES: {files from MANIFEST.md}
    READS: {files from MANIFEST.md}

  Dependencies:
    {deps list from MANIFEST.md DAG node — howler-name or howler-name#types}

  CONTRACT (frozen -- do not modify, block if wrong):
  Read ~/.claude/spectrum/{rain-id}/CONTRACT.md before starting.
  Do NOT modify this file. If the contract is wrong, set Status: blocked.
  # Token note: CONTRACT.md is referenced by path, not inlined. For a 5-Howler run
  # with a 2000-token contract this saves ~10,000 input tokens (~$0.03 at Sonnet rates).

  INSTRUCTIONS:
  0. Read CONTRACT.md at the path above FIRST. This is your source of truth.
  1. Write HOOK.md in worktree root IMMEDIATELY (before any implementation).
  2. Update HOOK.md as you progress -- decisions, seams, blockers, errors.
  3. Follow CONTRACT.md exactly. If the contract is wrong, set Status: blocked
     in HOOK.md and describe the needed change. Do NOT modify CONTRACT.md.
  4. Only touch files listed in your CREATES/MODIFIES ownership. READS are read-only.
  5. REFLEXION CHECK: After every 5th file write, re-read your scope in CONTRACT.md
     and your File Ownership list above. If you are touching files outside your
     ownership matrix, STOP immediately and log the drift in HOOK.md under Blockers.
  6. SCOPE ALIGNMENT CHECK: After every 20 tool calls, re-read your original
     Task above and CONTRACT.md. Write 'Alignment: on-track' or
     'Alignment: drifted — [reason]' in HOOK.md under Progress.
     If drifted, STOP and correct before continuing.
  7. When type/interface exports are finalized (but before full implementation is done),
     mark Checkpoints.types as STABLE in HOOK.md. This unblocks checkpoint-dependent Howlers.
     STABLE is a contract -- do not change exported types after marking STABLE.
  8. COMPLETION VERIFICATION: Before declaring done, verify mechanically:
     - Every file in CREATES exists: ls -la {each file}
     - Every file in MODIFIES has been changed: git diff --name-only
     - For TypeScript: tsc --noEmit passes
     - For tests: test runner passes on your files
     Write results in HOOK.md under '## Completion Verification'.
  9. When verified: run White + Gray + /diff-review in parallel (triple gate).
     Security criticals block. High/medium = warnings in PR description.
  10. Fix any blockers from review. If blockers were fixed, re-run White before
     proceeding (max 2 Orange retries total, then set Status: blocked).
  11. Write debrief entry to ~/.claude/spectrum/{rain-id}/{howler-name}.md
  12. Open a PR via Copper targeting main. Never push directly to main.

  DISCOVERY RELAY (if provided):
  {compressed_findings from previously-completed Howlers — ~500 tokens max}
")
```

Gold fills in every `{placeholder}` from MANIFEST.md. CONTRACT.md is referenced by path — Howlers read it as their first action. No improvisation -- the template ensures every Howler receives identical structure.

### 2.1a Post-Dispatch Worktree Verification

**Immediately after each Howler is spawned**, Gold verifies the worktree is correct. This addresses recurring failures (remnant-infra-0329: wrong base branch; remnant-narrative-0329: ~50% git permission failures).

**Verification checklist (per Howler):**

1. Worktree exists at the expected path
2. Branch name matches `spectrum/<rain-id>/<howler-name>` (not auto-generated `worktree-agent-*`)
3. Base commit matches the tip of `base_branch` from MANIFEST.md DAG node
4. `git log -1 --oneline` confirms the right starting point

```bash
# Gold runs after each Howler dispatch:
cd <worktree-path>
git rev-parse --abbrev-ref HEAD   # should be spectrum/<id>/<howler-name>
git log -1 --oneline              # should match base_branch tip
git merge-base --is-ancestor <expected-base-commit> HEAD && echo "OK"
```

**If verification fails:**
- If branch name is wrong: the Howler likely auto-created a branch. Halt the Howler, create the correct branch manually, re-dispatch.
- If base commit is wrong: the worktree forked from the wrong branch (e.g., `main` instead of `staging`). Halt, delete worktree, re-dispatch with explicit `--branch` and base.
- If worktree doesn't exist: dispatch failed silently. Re-dispatch.

**This check is mandatory for every Howler.** It adds ~5 seconds per Howler but prevents 10+ minute debugging sessions when a Howler builds on stale code.

**DAG-based dispatch**: Gold does not batch-dispatch all Howlers at once. When a Howler completes (debrief entry exists), Gold checks the DAG for newly unblocked Howlers and dispatches them. For checkpoint deps (`howler-name#types`), Gold checks HOOK.md for `types: STABLE` and dispatches as soon as the checkpoint fires — the upstream Howler may still be in progress.

### 2.2 HOOK.md -- Persistent Work State

Every Howler writes a `HOOK.md` at its worktree root **immediately upon starting**, before any implementation work. This is the durable state file.

**HOOK.md serves two purposes:**
1. **Recovery** -- if the session dies, a replacement Howler reads HOOK.md and resumes
2. **Post-mortem** -- if the Howler fails, Gold reads HOOK.md to understand what went wrong

```markdown
# Hook: Add authentication middleware
Spectrum: auth-refactor-0328
Howler: howler-auth
Branch: spectrum/auth-refactor-0328/howler-auth
Started: 2026-03-28T14:30:00Z
Updated: 2026-03-28T14:45:00Z
Status: in_progress
Confidence: medium
Confidence-Note: Clerk middleware integration untested against Next 16 proxy -- worked in isolation

## Task
Implement Clerk middleware in proxy.ts, protect /dashboard/* routes,
create sign-in/sign-up pages, define UserSession type per CONTRACT.md.

## File Ownership
CREATES: src/middleware/auth.ts, src/types/auth.ts, src/routes/sign-in.tsx
MODIFIES: src/app/layout.tsx

## Checkpoints
- types: STABLE

## Progress
- [x] Install Clerk via Marketplace
- [x] Create proxy.ts with clerkMiddleware()
- [x] Define UserSession type in types/auth.ts (STABLE -- do not change)
- [ ] Add sign-in/sign-up routes
- [ ] Test protected route redirects

## Decisions
- Used proxy.ts (Next.js 16) instead of middleware.ts -- project is on Next 16
- Set NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in explicitly (not auto-detected)

## Seams
- howler-ui needs to import SignInButton from @clerk/nextjs in the header
- Created types/auth.ts with UserSession type per CONTRACT -- howler-api should import
  [LOW CONFIDENCE: confirm UserSession shape matches howler-api expectations before wiring]

## Cross-Domain Observations
- (anything noticed outside your ownership boundary — bugs, inconsistencies,
  opportunities in other Howlers' domains. Flag it even if you can't fix it.)

## Completion Verification
- [ ] All CREATES files exist: {ls results}
- [ ] All MODIFIES files changed: {git diff --name-only results}
- [ ] Type check passes: {tsc --noEmit or N/A}
- [ ] Tests pass on owned files: {test results or N/A}

## Blockers
- (none)

## Errors Encountered
- (none)
```

**Howler heartbeat**: Every 30 tool calls or ~1 hour (whichever comes first), Howlers must update HOOK.md with current status. If Gold detects no heartbeat for 4+ hours, the Howler is treated as stuck and escalated without waiting for manual intervention.

**Update rules:**
- Update `Updated` timestamp on every progress change
- If blocked, set `Status: blocked` immediately and describe the blocker
- If you hit errors, log them in Errors Encountered even if resolved (prevents recovery Howlers from repeating dead ends)
- If you deviate from CONTRACT.md, document why in Decisions AND Seams
- Set `Confidence` honestly. White prioritizes review of low-confidence areas. Mention low-confidence seams explicitly in your debrief entry so Gold flags them during integration.

### 2.3 Confidence Signaling

The `Confidence` field in HOOK.md communicates the Howler's certainty about its implementation. It is required and must be set before writing the debrief entry.

| Value | Meaning |
|-------|---------|
| `high` | Implementation is well-tested and matches CONTRACT.md. No known risks. |
| `medium` | Works in the happy path; edge cases or integration points have not been fully verified. |
| `low` | Significant uncertainty. The approach may need revision once integrated. |

**`Confidence-Note:`** is optional but strongly recommended for `medium` and required for `low`. Describe exactly what is uncertain and where.

**White behavior**: When reviewing a Howler's diff, White reads HOOK.md and gives additional scrutiny to any seams or files tagged as low-confidence. A low-confidence rating does not block a PR on its own -- but it raises the bar for White approval in that area.

**Debrief propagation**: The `confidence` field in the YAML frontmatter of the debrief entry must match the final `Confidence` value in HOOK.md. Gold uses this during integration to weight seam-verification priority.

### 2.4 Progressive Disclosure -- Type Checkpoints

By default, a downstream Howler waits for its dependency's full completion (debrief entry exists) before starting. Type checkpoints allow earlier unblocking: a Howler can declare its type/interface exports STABLE before finishing implementation, and checkpoint-dependent Howlers can start immediately.

**When to use**: A Howler has finished defining all shared types and interfaces, committed the types file, and is confident the shape will not change. Full implementation (tests, integration, routes) may still be in progress.

**Checkpoint states**: Exactly `STABLE` or `PENDING` (all-caps). `PENDING` is the initial state. Do not invent other states.

**How to mark STABLE:**

1. Commit the types file (e.g., `src/types/auth.ts`)
2. In HOOK.md, update the `## Checkpoints` section:

```markdown
## Checkpoints
- types: STABLE (committed at abc1234)
```

3. Gold polls HOOK.md of in-progress Howlers and dispatches any Howler whose checkpoint dep is now satisfied.

**DAG checkpoint dep syntax** (from MANIFEST.md):

```yaml
- id: howler-api
  deps: [howler-auth#types]
  howler: howler-api
  branch: spectrum/auth-refactor-0328/howler-api
```

A dep of `howler-auth#types` means: dispatch howler-api when howler-auth's HOOK.md shows `types: STABLE`. A dep of `howler-auth` (no `#types`) means: dispatch howler-api only when howler-auth's debrief entry exists (full completion).

**STABLE is a contract.** If a Howler marks `types: STABLE` and subsequently changes an exported type, this is treated as a contract violation with the same severity as modifying CONTRACT.md directly. Dependent Howlers may have already built against the stable types. Required actions:

1. Set `Status: blocked` in HOOK.md
2. File an AMENDMENT.md describing the type change (see Contract Amendments section)
3. Gold decides whether to re-dispatch affected Howlers before proceeding

**What checkpoint-dependent Howlers should do:**

- Confirm the upstream types file is committed at the noted SHA before importing
- Note the dependency in HOOK.md under Decisions (e.g., "Importing UserSession from howler-auth#types at abc1234")
- If the types file is missing or incomplete, set `Status: blocked` immediately -- do not attempt to re-derive types

### 2.5 Quality Gate

Before opening a PR, every Howler spawns ALL THREE in parallel:

1. **White** -- zero blockers required; White reads HOOK.md `Confidence` field and gives additional scrutiny to low-confidence seams
2. **Gray** -- zero test failures required (coverage gaps noted in PR, not blocking)
3. **/diff-review** -- zero security criticals required (high/medium = warning noted in PR description)

**Content-heavy spectrum runs** (narrative, documentation, generated text): Gray must also grep for Unicode curly quotes that break string literals:

```bash
grep -rP '[\x{2018}\x{2019}\x{201C}\x{201D}]' src/ --include='*.ts' --include='*.tsx'
```

Any matches are blockers — replace with escaped ASCII equivalents. (From remnant-narrative-0329 lesson: a smart apostrophe `'` terminated a TypeScript string literal.)

This is the same quality gate as single-agent PRs. Spectrum doesn't weaken standards. If blockers are found, the Howler fixes them (max 2 Orange retries). If still blocked, set `Status: blocked` in HOOK.md.

### 2.6 Completion -- Debrief Entry

When the PR is open, write a handoff to `~/.claude/spectrum/<rain-id>/<howler-name>.md`. In v4.0 this file uses YAML frontmatter for automated cross-referencing, followed by a human-readable narrative body.

```markdown
---
howler: howler-auth
rain: auth-refactor-0328
status: complete
pr: https://github.com/org/repo/pull/47
completed: 2026-03-28T15:20:00Z
confidence: medium
seams:
  - id: s1
    target_howler: howler-ui
    type: import
    what: "SignInButton from @clerk/nextjs"
    where: "Header.tsx"
  - id: s2
    target_howler: howler-api
    type: import
    what: "UserSession from @/types/auth"
    where: "route handlers"
assumptions:
  - id: a1
    about_howler: howler-ui
    what: "will add SignInButton to the header component"
files_created:
  - src/middleware/auth.ts
  - src/types/auth.ts
  - src/routes/sign-in.tsx
files_modified:
  - src/app/layout.tsx
contract_compliance: full
open_exits:
  - "No org-creation flow"
warnings:
  - "Clerk requires manual Vercel Dashboard setup"
---

## What I Built
- Clerk auth middleware (proxy.ts)
- Sign-in and sign-up routes
- Protected /dashboard/* behind authentication
- UserSession type in types/auth.ts per CONTRACT.md

## Contract Compliance
All items assigned to this Howler in CONTRACT.md are implemented as specified.

## Confidence Note
Confidence: medium. Clerk middleware integration was tested in isolation but not against
the full Next 16 proxy stack. White should closely review the proxy.ts seam and the
UserSession import path in howler-api's integration.

## Seams
- howler-ui: import SignInButton from @clerk/nextjs in Header.tsx
- howler-api: import { UserSession } from '@/types/auth' in route handlers
- howler-api: auth() is available in all route handlers via proxy.ts middleware

## Assumptions
- howler-ui will add SignInButton to the header component
- howler-api will use auth() from @clerk/nextjs, not implement its own auth

## Open Exits
- No org-creation flow -- user with no org sees empty dashboard state

## Warnings
- Clerk integration requires manual Vercel Dashboard setup step (not automatable)
```

The `confidence` field in the frontmatter must match the final `Confidence` value in HOOK.md. Gold uses this field during integration to weight seam-verification priority.

---

## Phase 3: The Forge

### When Recovery Is Needed

A Howler may fail because: session hit context limits, the task was harder than expected, a dependency was missing, or the approach was wrong.

Gold detects failure when a Howler returns without a completed PR. Gold then reads the Howler's HOOK.md to assess the situation.

**Note on monitoring**: Claude Code's sub-agent model means Gold waits for Howlers to return. Gold cannot poll HOOK.md mid-execution. Detection happens when:
- A Howler returns early (error, timeout, context limit)
- All Howlers complete and Gold checks for missing debrief entries
- The human asks for a status update — Gold reads all available HOOK.md files

---

### 3.0 Failure Classification

Before choosing a recovery action, Gold **classifies the failure**. Classification determines the supervision strategy and whether human confirmation is required.

Gold reads the Howler's HOOK.md — specifically `Errors Encountered`, `Blockers`, and `Failure Classification` — and assigns one of five types:

| Type | Definition | Supervision Strategy | Requires Human? |
|------|-----------|---------------------|-----------------|
| `transient` | Context window exceeded, rate limit, timeout, network error. Howler made progress (HOOK.md shows recent completions). | Auto-resume: spawn new Howler with "Read HOOK.md and continue" | **No** — Gold auto-dispatches |
| `logical` | Wrong approach, tests fail, Howler goes in circles. HOOK.md shows same task attempted multiple times. | Orange diagnoses, then Resume or Retry | Yes |
| `structural` | CONTRACT.md is wrong, file ownership conflict, task boundaries are wrong. Howler sets `Status: blocked` citing contract. | Gold re-runs muster. One-for-all restart of downstream dependents. | Yes |
| `environmental` | Test infra down, deps won't install, Docker broken. Multiple Howlers may fail with similar errors. | Pause all Howlers. Fix environment. Resume all. | Yes |
| `conflict` | Contract mismatch discovered mid-execution. Howler's work contradicts another Howler's completed work. | Freeze-and-escalate. Gold evaluates blast radius. | Yes |

**`transient` is the only type where Gold may auto-recover without human confirmation.**

#### Classification Signal Guide

When reading HOOK.md, Gold looks for these signals:

| Signal in HOOK.md | Likely Type |
|-------------------|-------------|
| `Status: in-progress`, recent completions, no blockers, timeout/context error | `transient` |
| Same task checked and unchecked multiple times, test failures looping | `logical` |
| `Status: blocked`, references CONTRACT.md, mentions file conflict | `structural` |
| Error messages about missing deps, infra, toolchain; other Howlers report similar errors | `environmental` |
| Describes mismatch with another Howler's completed work, interface divergence | `conflict` |

#### Environmental Correlation

If 3 or more Howlers fail with structurally similar error messages in a short window, escalate classification to `environmental` regardless of individual HOOK.md classification. Pause all remaining Howlers and fix the environment before resuming.

#### Failure Classification Field in HOOK.md

Howlers (or Orange during diagnosis) fill in a `Failure Classification:` field on failure:

```markdown
## Status
blocked

## Failure Classification
structural

## Blockers
CONTRACT.md defines `UserSession` as having `userId: string`, but `src/types/auth.ts`
already exports `UserSession` with `userId: number`. File ownership conflict — auth.ts
is listed under howler-auth in the manifest but this Howler also needs to write to it.
```

Valid values: `transient` | `logical` | `structural` | `environmental` | `conflict`

---

### 3.1 Supervision Strategies

Failure classification determines which supervision strategy applies. These are modeled on Erlang/OTP supervisor behaviors:

#### one-for-one (default)

Only the failed Howler is affected. Used for `transient` and `logical` failures.

- The failed Howler is stopped
- A new Howler is dispatched for the same task (Resume or fresh Retry)
- All other Howlers continue unaffected

**Example**: `howler-api` hits a context limit mid-task. HOOK.md shows 4 of 7 checklist items complete. Gold auto-resumes with a new `howler-api` instance. `howler-auth` and `howler-ui` are unaffected.

#### one-for-all (structural failures)

The failed Howler AND all downstream dependents are stopped. Used for `structural` failures.

- Gold freezes all in-flight Howlers that depend (directly or transitively) on the failed Howler
- Gold re-runs muster with an updated contract and task decomposition
- All affected Howlers are re-dispatched after human approval

**Example**: `howler-auth` files a `structural` block — the `UserSession` type in CONTRACT.md is wrong. `howler-api` and `howler-ui` both depend on `howler-auth#types`. Gold freezes both, fixes the contract, and re-dispatches all three.

#### rest-for-one (dependency chain failures)

All Howlers dispatched after the failed Howler in the dependency chain are restarted. Used when a failure reveals that a dependency's outputs are incorrect, invalidating everything built on top.

- The failed Howler and all Howlers started after it (in dispatch order) are stopped
- Howlers that completed before the failure and have no dependency on the failed Howler are unaffected
- Re-dispatch proceeds in original dependency order after the root failure is resolved

**Example**: `howler-auth` completes, but its types are later discovered to be wrong by `howler-api`. `howler-ui` (dispatched after `howler-api`) is also stopped. `howler-auth` is retried, then `howler-api`, then `howler-ui`.

---

### 3.2 Circuit Breaker

The circuit breaker prevents futile retries where a Howler keeps hitting the same wall.

#### Locus Tracking

Failure tracking is per-**locus** — the specific file or test that is failing — not just a count of Howler failures. A Howler that fails on five different files is less alarming than a Howler that fails on the same file twice.

`Errors Encountered` entries in HOOK.md gain a `locus:` tag:

```markdown
## Errors Encountered
- Attempted to write `src/middleware/auth.ts` — TypeScript compile error on line 42, `userId` type mismatch.
  locus: src/middleware/auth.ts
- Retried after adjusting type — same compile error persists.
  locus: src/middleware/auth.ts
```

Gold reads locus tags when evaluating recovery options.

#### Circuit Breaker States

| State | Condition | Gold Behavior |
|-------|-----------|----------------|
| **Closed** | Fewer than 2 failures on the same locus | Normal recovery flow |
| **Half-Open** | 2 failures on the same locus | Auto-escalate to `structural`; dispatch Orange to diagnose |
| **Open** | Orange confirms no simple fix | Require `Restructure` — re-run muster for this task |

#### Escalation Rule

After **2 failures on the same locus** (same file path or same test identifier), Gold automatically escalates the failure classification:

- `transient` → `structural`
- `logical` → `structural`

This prevents Gold from auto-resuming a `transient` failure that is actually a contract or ownership problem. The circuit breaker trips *before* a third dispatch.

**Example**: `howler-auth` fails twice on `src/middleware/auth.ts`. First failure was classified `transient` (context limit). Gold checks locus history before auto-resuming and finds the same locus in a previous HOOK.md. Classification auto-escalates to `structural`. Gold pauses and escalates to human instead of spawning a third Howler.

#### Locus History Check (Gold Protocol)

Before auto-resuming a `transient` failure, Gold runs this check:

1. Read `Errors Encountered` from current HOOK.md — collect all `locus:` values
2. Read `Errors Encountered` from any previous HOOK.md backups for this Howler (if the spectrum directory contains `<howler-name>-prev.md` entries)
3. If any locus appears 2+ times across all attempts: escalate to `structural`, do not auto-resume

---

### 3.3 Recovery Options

After classification determines the supervision strategy, Gold selects a recovery action. These options apply once human confirmation is obtained (except `transient` + circuit breaker clear):

| Option | When to use | What happens |
|--------|-------------|--------------|
| **Resume** | Howler made meaningful progress; `transient` failure or `logical` after Orange diagnosis | New Howler spawned with: "Read HOOK.md and CONTRACT.md. Continue from where the previous Howler left off. Don't repeat checked-off work. Avoid approaches listed in Errors Encountered." |
| **Retry** | Howler went down a bad path; `logical` failure, no useful progress to preserve | Fresh Howler spawned with original task. Previous HOOK.md ignored. |
| **Skip** | Task is deferrable; `logical` or `environmental` where fix is disproportionate | Mark as follow-up work. Adjust merge plan for remaining Howlers. |
| **Restructure** | Task boundaries were wrong; circuit breaker open; `structural` or `conflict` failure | Re-run muster with different decomposition. CONTRACT.md updated. |

**Maximum 2 Orange retries per `logical` failure.** If Orange cannot resolve it in 2 attempts, escalate to human with a `Restructure` recommendation.

---

### 3.4 Partial Spectrum Completion

If some Howlers succeed and others fail:
- Completed Howlers' PRs can still be merged
- Gold adjusts merge order to account for missing dependencies
- Failed tasks become sequential follow-up after successful PRs merge
- Gold notes failed tasks and their classification in PAX-PLAN.md under a `Failed Tasks` section

---

## Phase 4: Pax

After all Howlers complete (or fail), Gold reads ALL debrief entries and performs automated cross-reference analysis using the structured YAML frontmatter.

### 4.0 Structured Handoff Schema

Every Howler debrief file (`<howler-name>.md`) begins with a YAML frontmatter block. This enables automated seam-checking and file-overlap detection by Gold.

**Required frontmatter schema:**

```yaml
---
howler: howler-auth
rain: auth-refactor-0328
status: complete
pr: https://github.com/org/repo/pull/47
completed: 2026-03-28T15:20:00Z
confidence: high
seams:
  - id: s1
    target_howler: howler-ui
    type: import
    what: "SignInButton from @clerk/nextjs"
    where: "Header.tsx"
  - id: s2
    target_howler: howler-api
    type: import
    what: "UserSession from @/types/auth"
    where: "route handlers"
assumptions:
  - id: a1
    about_howler: howler-ui
    what: "will add SignInButton to the header component"
files_created:
  - src/middleware/auth.ts
  - src/types/auth.ts
files_modified:
  - src/app/layout.tsx
contract_compliance: full
open_exits:
  - "No org-creation flow — user with no org sees empty dashboard"
warnings:
  - "Clerk integration requires manual Vercel Dashboard setup"
---
```

**Field specifications:**

| Field | Type | Values |
|-------|------|--------|
| `howler` | string | Matches Howler name from MANIFEST |
| `rain` | string | Spectrum ID |
| `status` | enum | `complete` \| `blocked` \| `failed` |
| `pr` | string or null | PR URL, or `null` for doc spectrum runs |
| `completed` | string | ISO 8601 timestamp |
| `confidence` | enum | `high` \| `medium` \| `low` |
| `seams` | array | Seam objects (see sub-fields below) |
| `assumptions` | array | Assumption objects (see sub-fields below) |
| `files_created` | array | Path strings |
| `files_modified` | array | Path strings |
| `contract_compliance` | enum | `full` \| `partial` \| `none` |
| `open_exits` | array | Strings describing known gaps |
| `warnings` | array | Strings describing risks or manual steps |

**Seam sub-fields:** `id`, `target_howler`, `type`, `what`, `where`

**Assumption sub-fields:** `id`, `about_howler`, `what`

Below the closing `---`, the freeform narrative section (What I Built, Decisions Made, etc.) continues for human context. The frontmatter enables automated cross-referencing; the narrative is for Gold and for PR reviewers.

**Example complete debrief entry:**

```markdown
---
howler: howler-auth
rain: auth-refactor-0328
status: complete
pr: https://github.com/org/repo/pull/47
completed: 2026-03-28T15:20:00Z
confidence: high
seams:
  - id: s1
    target_howler: howler-ui
    type: import
    what: "SignInButton from @clerk/nextjs"
    where: "Header.tsx"
  - id: s2
    target_howler: howler-api
    type: import
    what: "UserSession from @/types/auth"
    where: "route handlers"
assumptions:
  - id: a1
    about_howler: howler-ui
    what: "will add SignInButton to the header component"
files_created:
  - src/middleware/auth.ts
  - src/types/auth.ts
files_modified:
  - src/app/layout.tsx
contract_compliance: full
open_exits:
  - "No org-creation flow — user with no org sees empty dashboard"
warnings:
  - "Clerk integration requires manual Vercel Dashboard setup"
---

## What I Built

Added Clerk authentication middleware and session types. ClerkProvider wraps the root layout. The `UserSession` type in `src/types/auth.ts` is the shared contract for howler-api's route handlers.

## Decisions Made

Used Clerk's `auth()` helper rather than `getServerSideProps` pattern — this is the recommended approach for App Router and avoids the older session cookie pattern.

## Assumptions I Made

howler-ui will add the SignInButton to the Header component. I've exported it cleanly from `@clerk/nextjs` — no custom wrapper needed.
```

### 4.1 Independent Validation (Don't Trust Howler Self-Reports)

Before seam-checking, Gold independently validates each Howler's claimed output. Howlers report what they built in their debrief, but Gold must verify — a Howler can claim `contract_compliance: full` while having missed a postcondition, or can report files_created that don't actually satisfy the contract interface.

**For each completed Howler:**

1. Read 2-3 key files the Howler created or modified (focus on contract-critical files — shared types, integration points, exports)
2. Check against CONTRACT.md postconditions for that Howler:
   - Do exported types match the contract shapes?
   - Do integration points exist at the paths claimed?
   - Are naming conventions followed?
3. Check no files outside the Howler's ownership matrix were touched (`git diff --name-only` on the Howler's branch)
4. Record validation results in PAX-PLAN.md under "Independent Validation"

**Discrepancy handling:**
- **Type mismatch** (exported type doesn't match contract): Integration risk — flag in PAX-PLAN.md, may require Howler fix before merge
- **Missing postcondition** (file exists but doesn't satisfy contract): Warning — human decides
- **Ownership violation** (touched files outside matrix): Blocker — Howler must revert or Gold restructures

This step catches "green but wrong" — a Howler that passes its own quality gate but doesn't actually satisfy the contract. No other multi-agent system does this verification.

### 4.2 Automated Seam Check

Gold runs automated seam-checking against the YAML frontmatter of all debrief files. This is not a manual scan — it is a structured cross-reference of declared seams against confirmed work.

**Algorithm:**

1. **Collect frontmatters.** Parse the YAML block from every `<howler-name>.md` in the spectrum directory.

2. **Seam cross-reference.** For each seam declared by Howler A targeting Howler B:
   - Search Howler B's `files_created` and `files_modified` for the path referenced in `where`
   - Check Howler B's `contract_compliance` (a value of `none` downgrades all seams to WARNING)
   - If the target file appears in Howler B's ownership: mark **CONFIRMED**
   - If not found in file lists but `contract_compliance` is `full` or `partial`: mark **UNCONFIRMED — verify in diff**
   - If Howler B's `status` is `failed` or `blocked`: mark **BLOCKED**

3. **Assumption cross-reference.** For each assumption by Howler A about Howler B:
   - Search Howler B's `files_created`, `files_modified`, and narrative body for matching work
   - If matching: mark **VALIDATED**
   - If not found: mark **UNVALIDATED — verify manually**

4. **File overlap check.** Merge all `files_created` and `files_modified` arrays across all debriefs. Flag any path appearing more than once as **CONFLICT** — this indicates the muster file ownership matrix was violated.

5. **Output: `SEAM-CHECK.md`** written to the spectrum directory.

**Example SEAM-CHECK.md:**

```markdown
# Seam Check: auth-refactor-0328
Generated: 2026-03-28T16:00:00Z

## Seam Results

| Seam ID | Declared By | Target Howler | Status | Notes |
|---------|-------------|--------------|--------|-------|
| s1 | howler-auth | howler-ui | CONFIRMED | Header.tsx in howler-ui files_modified |
| s2 | howler-auth | howler-api | UNCONFIRMED | route handlers not in howler-api files lists — verify in diff |

## Assumption Results

| Assumption ID | Declared By | About Howler | Status | Notes |
|---------------|-------------|-------------|--------|-------|
| a1 | howler-auth | howler-ui | VALIDATED | howler-ui narrative confirms SignInButton added to Header |

## File Overlap Check

No conflicts. All files appear in exactly one Howler's ownership.

## Summary

- 1/2 seams confirmed, 1 unconfirmed (requires manual diff check)
- 1/1 assumptions validated
- 0 file ownership conflicts
- 1 howler with warnings: howler-auth (Clerk manual setup)
```

### 4.2 Merge Plan

After automated seam-checking, Gold writes `PAX-PLAN.md` to the spectrum directory and presents it to the human. The SEAM-CHECK.md results are incorporated directly.

```markdown
# Merge Plan: auth-refactor-0328

## Merge Order
1. howler-auth (PR #47) — no dependencies, merge first
2. howler-api (PR #48) — depends on types/auth.ts from #47
3. howler-ui (PR #49) — depends on types/auth.ts from #47

## Seam Check Results
- 1/2 seams confirmed, 1 unconfirmed: howler-api did not list route handlers in files_modified — check diff before merging PR #48
- 1/1 assumptions validated

## File Ownership
- No conflicts detected

## Warnings (from debriefs)
- Clerk requires manual Vercel Dashboard config (howler-auth)
- No org-creation flow (howler-auth open_exits)

## Integration Risks
- No integration tests for auth + API interaction — recommend adding post-merge
- howler-api `confidence: medium` — White should pay extra attention to route handler changes

## Open Exits (carry forward)
- howler-auth: No org-creation flow — user with no org sees empty dashboard
```

**No auto-merging.** Human reviews PAX-PLAN.md and SEAM-CHECK.md, then merges PRs in the recommended order.

### 4.3 Post-Merge

After all PRs merge:
1. Run **Gray** on the merged main branch (delegates to Gray agent)
2. If integration failures exist, fix as sequential follow-up (not a new spectrum run)
3. Proceed to Phase 6.5 (Learning) before cleaning up the spectrum directory

---

## Phase 5: Merge (Incremental Integration Testing)

Human merges PRs in the order specified in PAX-PLAN.md. **After each merge, Gray runs integration tests before proceeding to the next merge.** This catches composition bugs before they compound.

**Merge ordering rules:**

- Dependencies merge before dependents. A Howler that another Howler's PR depends on must merge first.
- If two Howlers have no dependency relationship, they can merge in any order.
- **After each merge, Gray runs on the updated branch.** If tests fail, halt the merge sequence and fix before proceeding. This prevents a late "everything merged but nothing works" failure.

**Incremental merge protocol:**

```
for each PR in PAX-PLAN.md order:
  1. Human merges PR
  2. Gray runs tests on the updated branch
  3. If PASS → continue to next PR
  4. If FAIL → halt, diagnose, fix as sequential follow-up before merging more
```

**Per-PR self-reflect**: After each merge, Gold writes a 3-5 line note in CHECKPOINT.json under `merge_reflections`: what worked, what surprised, what the next merge should watch for. These compound — reflection N informs merge N+1. Captures learnings atomic with the code, not just post-spectrum.

**Budget tracking**: If `cost_tracking.budget_limit` is set in CHECKPOINT.json, Gold checks cumulative token cost before dispatching each new Howler. If projected to exceed budget, present options to human: continue, skip remaining Howlers, or abort. Token counts logged per Howler from the Agent tool's usage output.

For spectrum runs with 2 or fewer PRs, a single post-merge Gray run (Phase 6) is sufficient — incremental testing adds value at 3+ merges where composition failures are likely. Self-reflect still runs after each merge regardless.

**No auto-merging.** Gold presents PAX-PLAN.md and SEAM-CHECK.md. The human reviews and merges. Gold does not merge PRs.

---

## Phase 6: Triumph

After all PRs merge:
1. Run **Gray** on the merged main branch (delegates to Gray agent)
2. If integration failures exist, fix as sequential follow-up (not a new spectrum run)
3. Proceed to Phase 6.25 (Obsidian verification)

**Do not clean up the spectrum directory until Phase 6.5 is complete.** LESSONS.md depends on data in the spectrum directory.

---

## Phase 6.25: Obsidian Verification

**Trigger:** After Phase 6 Gray passes (no integration test failures).

Obsidian closes the loop between planning and delivery. It verifies that what was built satisfies what was planned — a check that neither White (diff quality) nor Gray (test correctness) performs.

### 6.25.1 Obsidian Protocol

Gold spawns the Obsidian agent with:

```
Agent(model="sonnet", subagent_type="obsidians", prompt="
  Spectrum: {rain-id}
  Role: Obsidian — spec compliance verification

  PLAN.md location: {path to PLAN.md}
  MANIFEST.md location: ~/.claude/spectrum/{rain-id}/MANIFEST.md
  Merged branch: {branch name}

  INSTRUCTIONS:
  1. Read PLAN.md — extract every acceptance criterion, user story, and stated goal.
  2. Read MANIFEST.md — map each criterion to the Howler(s) responsible.
  3. For each criterion, verify against the merged codebase:
     - Read the relevant files (grep, glob, read as needed)
     - Determine: PASS (criterion fully met), PARTIAL (partially met, state what's missing),
       or FAIL (not met at all)
  4. Read all debrief open_exits — these are known gaps, not failures. Classify separately.
  5. Write SENTINEL-REPORT.md to the spectrum directory with:
     - Per-criterion verdicts (PASS/PARTIAL/FAIL)
     - Evidence for each verdict (file paths, line numbers, grep results)
     - Open exits (known gaps carried forward, not counted as failures)
     - Overall verdict: COMPLIANT / PARTIAL / NON-COMPLIANT
  6. If any criterion is FAIL: flag for human review before proceeding to learning.
")
```

### 6.25.2 SENTINEL-REPORT.md Format

```markdown
# Obsidian Report: {rain-id}
Generated: {ISO timestamp}
Overall: COMPLIANT | PARTIAL | NON-COMPLIANT

## Criteria Verdicts

| # | Criterion (from PLAN.md) | Howler | Verdict | Evidence |
|---|--------------------------|-------|---------|----------|
| 1 | User can sign in via Clerk | howler-auth | PASS | src/routes/sign-in.tsx exists, proxy.ts gates /dashboard/* |
| 2 | API routes return AuthResponse shape | howler-api | PASS | All handlers return { ok, session, error? } |
| 3 | Dashboard shows user name | howler-ui | PARTIAL | Header shows email but not display name |

## Open Exits (known gaps, not failures)
- No org-creation flow (howler-auth, acknowledged in debrief)

## Summary
- 2/3 criteria PASS, 1/3 PARTIAL, 0 FAIL
- 1 open exit carried forward
```

### 6.25.3 Gold Response to Obsidian Report

| Overall Verdict | Gold Action |
|----------------|--------------|
| COMPLIANT | Proceed to Phase 6.5 (Learning) |
| PARTIAL | Present report to human. Human decides: fix now or accept and proceed |
| NON-COMPLIANT | Present report to human. Do not proceed until criteria are addressed |

**Obsidian never blocks autonomously** — it reports. The human decides whether PARTIAL results are acceptable.

---

## Phase 6.5: Learning

**Trigger:** After Obsidian verification passes or human accepts PARTIAL results.

This phase captures what worked and what didn't, so future spectrum runs on the same project benefit from accumulated experience. Gold is responsible for writing the lessons entry.

### 6.5.0 LESSONS.md

**Brown** drafts the LESSONS.md entry; Gold reviews and commits it.

**Brown dispatch:**

```
Agent(model="haiku", subagent_type="browns", prompt="
  Spectrum: {rain-id}
  Role: Brown — retrospective drafting

  Read ALL of the following from ~/.claude/spectrum/{rain-id}/:
  - MANIFEST.md (task decomposition, DAG, file ownership)
  - All <howler-name>.md debrief entries (YAML frontmatter + narrative)
  - SEAM-CHECK.md (seam and assumption results)
  - PAX-PLAN.md (merge order, warnings, integration risks)
  - SENTINEL-REPORT.md (spec compliance verdicts)

  Also read HOOK.md from each Howler worktree (if worktrees still exist).

  Write a LESSONS.md draft entry following the schema below. Include:
  - Decomposition Patterns (what worked, what caused friction)
  - Contract Friction (amendments filed, types that were wrong)
  - Failure Modes (failures by type, loci, recovery actions taken)
  - Timing (per-Howler duration, critical path, total wall time)
  - Obsidian Results (spec compliance summary)
  - Recommendations (actionable items for next spectrum run on this project)

  Write the draft to ~/.claude/spectrum/{rain-id}/LESSONS-DRAFT.md
")
```

Gold reviews LESSONS-DRAFT.md, edits if needed, then appends to the project's LESSONS.md.

Gold appends one entry to the project's LESSONS.md file after every successful spectrum run:

```
~/.claude/projects/<project-slug>/memory/LESSONS.md
```

- Written by Gold after post-merge Gray passes
- One file per project — **append** each new entry, do not overwrite
- Read by Blue before decomposing work on this project
- Read by Gold before writing CONTRACT.md for a new spectrum run on this project

**Entry schema:**

```markdown
## Spectrum: auth-refactor-0328
Date: 2026-03-28T17:30:00Z
Scope: Add Clerk authentication, protect API routes, update UI with sign-in flow

### Decomposition Patterns

What worked:
- Splitting auth middleware (howler-auth), API protection (howler-api), and UI sign-in (howler-ui) gave clean ownership boundaries — no file conflicts
- Checkpoint deps (`howler-auth#types`) allowed howler-api to start as soon as shared types were stable, saving ~30 min over waiting for full howler-auth completion

What caused friction:
- howler-ui needed both the Clerk component AND the updated layout from howler-auth — the layout change should have been a separate, earlier task or a checkpoint, not bundled into howler-auth's final PR

### Contract Friction

- CONTRACT.md was missing the `orgRole` field on `UserSession` — howler-auth filed a non-breaking amendment mid-flight; affected howlers absorbed it without re-dispatch (working as intended)
- `convoy-contracts.d.ts` type for `AuthContext` was too broad (`Record<string, unknown>`) — howler-api spent time refining it; should have been more specific at contract time

### Failure Modes

- howler-ui: `transient` failure (context limit) — resumed successfully from HOOK.md checkpoint
- No structural or conflict failures in this spectrum run

### Timing

- howler-auth: 45 min (critical path — types checkpoint blocked howler-api until 20 min in)
- howler-api: 35 min (started at howler-auth#types STABLE, completed ~10 min after howler-auth)
- howler-ui: 50 min (waited for howler-auth full completion; one transient failure added ~10 min)
- Total wall time: ~50 min (parallel efficiency high)

### Recommendations

- For auth spectrum runs: always declare a `types` checkpoint in the auth Howler — downstream API/UI Howlers benefit significantly from early type stability
- Consider splitting layout-level changes (ClerkProvider wrapping) into a tiny muster task rather than bundling into the auth Howler PR
- Add integration test for auth + API handoff to post-merge Gray checklist — this was an open gap in this spectrum run
```

### 6.5.1 Muster Integration

LESSONS.md feeds back into the next spectrum run's muster. Both Blue and Gold must check for it:

**Gold muster checklist addition:**

> Before writing CONTRACT.md, read `~/.claude/projects/<project-slug>/memory/LESSONS.md` if present. Check `Contract Friction` entries for types that were wrong in prior spectrum runs and ensure those are more precisely specified this time. Check `Decomposition Patterns` for task boundaries that caused friction — adjust the ownership matrix accordingly.

**Blue planning checklist addition:**

> Before writing PLAN.md, read `~/.claude/projects/<project-slug>/memory/LESSONS.md` if present. Check `Failure Modes` for recurring loci and `Decomposition Patterns` for splits that worked well. Propose task boundaries that avoid known friction points.

### 6.5.2 Learning Loop Summary

```
Spectrum completes
      |
      v
Phase 6: Gray on merged main
      |
  (passes)
      |
      v
Phase 6.25: Obsidian verifies spec compliance
  Writes SENTINEL-REPORT.md
      |
  (COMPLIANT or human accepts PARTIAL)
      |
      v
Phase 6.5: Brown drafts LESSONS.md, Gold reviews
  ~/.claude/projects/<project-slug>/memory/LESSONS.md
      |
      v
Next spectrum run on same project:
  Blue reads LESSONS.md → better PLAN.md
  Gold reads LESSONS.md → better CONTRACT.md
```

The spectrum directory is cleaned up after Phase 6.5 completes. LESSONS.md persists — it is project memory, not spectrum memory.

---

## Contract Amendments

CONTRACT.md is frozen at dispatch. Howlers never modify it directly. When a Howler discovers the contract is wrong or incomplete, they follow this protocol.

### Amendment Classification

Not all contract changes are equal. The taxonomy determines whether the spectrum run must pause:

**Non-breaking changes** — can be proposed without re-dispatching affected Howlers:

- Adding optional fields to existing interfaces or shared types
- Adding new exported types or functions that no existing Howler currently depends on
- Extending a union type with a new variant (when consumers only use, not narrow the union)
- Adding new optional parameters to existing functions

**Breaking changes** — require freeze-and-escalate (same response as a contract violation):

- Renaming or removing any existing type, field, or export
- Changing a required parameter's type
- Narrowing a union type (removing variants)
- Changing a function's return type
- Changing a required field to optional (callers may have assumed its presence)

When in doubt, treat as breaking.

### AMENDMENT.md Format

A Howler that needs a contract change writes `AMENDMENT.md` in their worktree root. The `Type` field must be exactly `non-breaking` or `breaking` (lowercase, hyphenated):

```markdown
# Amendment: howler-auth — 2026-03-28T15:00:00Z
Type: non-breaking
Change: Add optional `orgRole` field to UserSession
Rationale: Clerk returns this in session; downstream Howlers can ignore it safely
Affected Howlers: howler-api (can optionally consume), howler-ui (no impact)
contracts.d.ts update: Add `orgRole?: string` to UserSession interface
```

For a breaking change:

```markdown
# Amendment: howler-api — 2026-03-28T15:45:00Z
Type: breaking
Change: Rename `UserSession.userId` to `UserSession.sub` to match JWT convention
Rationale: All Clerk JWT helpers use `sub` — using `userId` requires a mapping step in every handler
Affected Howlers: howler-auth (defines the type), howler-ui (reads userId for display)
contracts.d.ts update: Rename `userId: string` to `sub: string` in UserSession interface
```

### Howler Behavior

**For non-breaking changes:**
1. Write `AMENDMENT.md` in your worktree root
2. Continue working — do not set `Status: blocked`
3. Note the amendment in your debrief YAML under `warnings`
4. Gold incorporates it during Phase 4 Pax

**For breaking changes:**
1. Set `Status: blocked` in HOOK.md
2. Write `AMENDMENT.md` in your worktree root describing the needed change
3. Stop work — do not proceed with a contract deviation
4. Gold re-runs muster with the updated contract before you resume

### Gold Behavior During Pax

**Non-breaking amendments** discovered during Phase 4:
1. Read the `AMENDMENT.md` from the affected Howler's worktree
2. Verify the change is genuinely non-breaking by the classification above
3. Note in PAX-PLAN.md: "Amendment applied: `orgRole` field added to UserSession (non-breaking)"
4. Notify any Howler whose work might benefit from the new field (informational only — no re-dispatch)
5. Incorporate into the post-spectrum LESSONS.md `Contract Friction` entry

**Breaking amendments** (Howler already blocked):
1. Read the `AMENDMENT.md`
2. Assess scope: which Howlers are affected, which have already completed work based on the old contract
3. Re-run muster with the updated contract
4. Determine whether completed Howler PRs need revision or can merge unchanged
5. Re-dispatch blocked Howler with updated CONTRACT.md

### Amendment Record

The amendment is not lost after the spectrum run. Gold includes it in the LESSONS.md `Contract Friction` section so future spectrum runs on this project know where the contract was imprecise.

```markdown
### Contract Friction

- howler-auth filed non-breaking amendment: added `orgRole?: string` to UserSession.
  Impact: none — downstream Howlers ignored it. Root cause: Clerk session shape was
  not fully inspected during muster. Future: check Clerk session schema before
  writing UserSession type.
```

### Rules Summary

| Scenario | Howler Action | Gold Action |
|----------|-------------|--------------|
| Non-breaking gap discovered | Write AMENDMENT.md, continue, note in debrief warnings | Incorporate during Pax, record in LESSONS.md |
| Breaking conflict discovered | Write AMENDMENT.md, set Status: blocked | Re-run muster, re-dispatch |
| Howler deviates silently | — | Treat as contract violation — blocker in SEAM-CHECK.md |

**Silent divergence is never acceptable.** If a Howler implements something that contradicts CONTRACT.md without filing an amendment, it is treated as a blocker during seam-checking regardless of whether the change was technically non-breaking.

---

## Spectrum Directory Structure

```
~/.claude/spectrum/
  <rain-id>/
    MANIFEST.md          # Tasks, dependency DAG, file ownership matrix (Gold, muster)
    CONTRACT.md          # Shared types, interfaces, conventions (Gold, muster)
    howler-auth.md       # Debrief entry with YAML frontmatter (Howler, on completion)
    howler-api.md        # Debrief entry with YAML frontmatter (Howler, on completion)
    howler-ui.md         # Debrief entry with YAML frontmatter (Howler, on completion)
    SEAM-CHECK.md        # Automated cross-reference results (Gold, Pax)
    PAX-PLAN.md          # Cross-reference analysis + merge order (Gold, Pax)
    SENTINEL-REPORT.md   # Spec compliance verdicts (Obsidian, post-merge)
    LESSONS-DRAFT.md     # Retrospective draft (Brown, post-Obsidian)
    CHECKPOINT.json      # Spectrum state snapshot (Gold, updated at every phase transition)
    ARCHITECTURE.md      # Codebase structure snapshot (Gold, muster)
```

Each Howler's worktree contains:
```
<worktree-root>/
  HOOK.md              # Persistent state (Howler, written immediately, updated continuously)
  AMENDMENT.md         # Contract amendment (Howler, filed when contract is wrong — optional)
  [normal project files]
```

Project memory (persists beyond spectrum lifecycle):
```
~/.claude/projects/<project-slug>/memory/
  LESSONS.md           # Cross-spectrum learning log (Gold, written after Phase 6.5)
  ENTITIES.md          # Entity memory — persistent knowledge about specific code entities
```

TypeScript spectrum runs also commit:
```
convoy-contracts.d.ts               (project root, or src/types/convoy-contracts.d.ts)
```

**Cleanup**: After Phase 6.5 completes and LESSONS.md is written, delete the spectrum directory. `convoy-contracts.d.ts` may be deleted post-merge or kept as documentation — Gold's discretion.

---

## Checkpoint Persistence

Inspired by LangGraph's time-travel debugging. Gold writes `CHECKPOINT.json` after every significant state change, enabling resume-from-any-point if a session dies.

### CHECKPOINT.json Schema

**Valid phases**: `planning`, `muster`, `approved`, `dispatch`, `integrating`, `merging`, `complete`
**Valid howler statuses**: `pending`, `dispatching`, `in_progress`, `blocked`, `complete`, `failed`, `auto-skipped`
**Valid modes**: `full`, `light`

```json
{
  "rain_id": "auth-refactor-0329",
  "phase": "dispatch",
  "mode": "full",
  "phase_number": 2,
  "timestamp": "2026-03-29T15:20:00Z",
  "base_branch": "staging",
  "base_commit": "abc1234",
  "resumed_at": null,
  "howlers": {
    "howler-auth": {
      "status": "complete",
      "debrief": true,
      "pr": "#47",
      "checkpoint_types": "STABLE",
      "worktree": "/tmp/worktree-howler-auth"
    },
    "howler-api": {
      "status": "in_progress",
      "debrief": false,
      "pr": null,
      "checkpoint_types": "PENDING",
      "hook_updated": "2026-03-29T15:18:00Z"
    },
    "howler-ui": {
      "status": "pending",
      "debrief": false,
      "pr": null,
      "deps_satisfied": false,
      "blocked_by": ["howler-auth#types"]
    }
  },
  "dag_state": {
    "howler-auth#types": "STABLE",
    "howler-auth": "complete"
  },
  "amendments": [],
  "failures": [],
  "quality_gates": {
    "howler-auth": { "white": "pass", "gray": "pass", "diff_review": "pass" }
  }
}
```

### When to Write Checkpoints

Gold writes (or updates) CHECKPOINT.json at these moments:

| Event | `phase` Value | What Changed |
|-------|--------------|--------------|
| Muster complete, awaiting human approval | `muster` | Initial state with all howlers `pending` |
| Human confirms manifest | `approved` | No howler changes, just phase advance |
| Each Howler dispatched | `dispatch` | Howler status → `in_progress` |
| Howler checkpoint fires (types: STABLE) | `dispatch` | `dag_state` updated, deps recalculated |
| Howler completes (debrief written) | `dispatch` | Howler status → `complete`, PR URL recorded |
| Howler fails | `dispatch` | Howler status → `failed`, failure added to `failures[]` |
| All Howlers done, Pax begins | `integration` | Phase advance |
| SEAM-CHECK.md written | `integration` | Seam results recorded |
| PAX-PLAN.md written | `merge_ready` | Phase advance |
| Each PR merged | `merging` | Howler `merged: true` |
| All PRs merged, Gray running | `post_merge` | Phase advance |
| Obsidians complete | `obsidians` | Obsidians verdict recorded |
| LESSONS.md written | `complete` | Terminal state |

### Session Recovery Protocol

On session start, Gold checks for incomplete spectrum runs:

```
1. Scan ~/.claude/spectrum/*/CHECKPOINT.json
2. For each with phase != "complete":
   a. Read CHECKPOINT.json — determine last completed phase
   b. Present to human: "Spectrum {id} was interrupted at Phase {phase}.
      {N}/{total} Howlers complete. Resume from {phase}?"
   c. If resuming:
      - Skip completed phases
      - For in_progress Howlers: read HOOK.md, classify state, resume or re-dispatch
      - For pending Howlers: dispatch normally when deps are satisfied
   d. If starting fresh: archive spectrum directory to ~/.claude/spectrum/{id}-abandoned/
```

**CHECKPOINT.json is the source of truth for spectrum state.** HOOK.md files are per-Howler state; CHECKPOINT.json is spectrum-wide state. Both are needed for full recovery.

---

## Architecture Snapshot (Persistent)

ARCHITECTURE.md is a **persistent, incrementally-updated** file at `~/.claude/projects/<project-slug>/ARCHITECTURE.md`. It is NOT regenerated from scratch each spectrum run — Gold reads the existing file and patches only changed sections (new files, removed modules, shifted dependencies). A copy is placed in the spectrum directory for Howler reference.

**If no ARCHITECTURE.md exists** (first spectrum run for this project), Gold creates it with a full structural scan (~50-100 lines). On subsequent spectrum runs, incremental updates save ~2 minutes of muster time.

This gives all Howlers shared codebase context without redundant exploration, and preserves cross-spectrum architectural knowledge.

### What ARCHITECTURE.md Contains

```markdown
# Architecture: {project name}
Generated: {ISO timestamp}
Root: {project root path}

## Project Type
{framework} ({language}) — detected from package.json / pyproject.toml / etc.

## Key Directories
- src/app/         — Next.js App Router pages and layouts
- src/components/  — React components (43 files)
- src/lib/         — Utilities and shared logic
- src/api/         — API route handlers
- src/types/       — TypeScript type definitions

## Entry Points
- src/app/layout.tsx    — Root layout (ClerkProvider, fonts, metadata)
- src/app/page.tsx      — Home page
- src/middleware.ts      — Auth middleware (Clerk)

## Key Dependencies
- next: 16.x, react: 19.x, @clerk/nextjs: 6.x
- @neondatabase/serverless (database)
- @upstash/redis (cache)

## Module Boundaries
- src/app/ imports from src/components/, src/lib/, src/types/
- src/components/ imports from src/lib/, src/types/ (never from src/app/)
- src/api/ imports from src/lib/, src/types/ (never from src/components/)

## Recent Activity (last 5 commits)
- abc1234 Add dashboard skeleton
- def5678 Configure Clerk auth
- ...
```

### Gold Protocol

1. Read `package.json` / `pyproject.toml` / `Cargo.toml` for project type and dependencies
2. Glob `src/**` (or project root) for directory structure
3. Read key entry points (layout, main, index) to map module boundaries
4. Run `git log -5 --oneline` for recent activity
5. Write ARCHITECTURE.md to spectrum directory (~50-100 lines)
6. Include ARCHITECTURE.md reference in every Howler dispatch prompt

**This adds ~30 seconds to muster and saves each Howler 2-5 minutes of codebase exploration.**

---

## Entity Memory

Persistent knowledge about specific code entities (functions, types, modules) that accumulates across spectrum runs. Fills the gap between session-level memory (HOOK.md) and project-level memory (LESSONS.md).

### ENTITIES.md Location

```
~/.claude/projects/<project-slug>/memory/ENTITIES.md
```

### Format

```markdown
# Entity Memory: {project name}
Last updated: {ISO timestamp}

## src/middleware/auth.ts
- Clerk middleware wrapping proxy.ts (added spectrum auth-refactor-0329)
- Must call clerkMiddleware() for auth() to work in Server Components
- Gotcha: proxy.ts must be at same level as app/ directory

## UserSession (src/types/auth.ts)
- Fields: userId, orgId, role ('admin' | 'member'), orgRole? (optional)
- Source of truth for all auth-related types
- Spectrum auth-refactor-0329: amendment added orgRole field

## src/db/repository.ts
- All database queries go through this file
- Uses @neondatabase/serverless with connection pooling
- Gotcha: pool exhaustion under concurrent requests — use waitUntil for cleanup

## /api/users (src/api/users.ts)
- CRUD operations for user management
- Requires auth() middleware — returns 401 without it
- Returns AuthResponse shape: { ok, session, error? }
```

### Read/Write Rules

| Agent | Read | Write |
|-------|------|-------|
| Blue | During planning — check for known gotchas before decomposing | Never |
| Gold | During muster — incorporate entity knowledge into CONTRACT.md | During Phase 6.5 — curate Brown additions |
| Howlers | At start — check for known gotchas on files they own | Append when discovering important facts about entities |
| Brown | During LESSONS.md drafting — extract entity-level knowledge | Draft new entity entries from spectrum artifacts |

**Keep ENTITIES.md under 200 lines.** Gold curates during Phase 6.5 — remove stale entries, merge duplicates, promote important discoveries from Howlers.

---

## Agent Teams Integration

When Anthropic's Agent Teams feature is enabled (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`), Howlers can use direct inter-agent messaging alongside the standard debrief protocol.

### What Changes with Agent Teams

| Feature | Without Agent Teams | With Agent Teams |
|---------|-------------------|-----------------|
| Howler-to-Howler communication | Debrief at completion only | Direct messaging during execution |
| Checkpoint notification | Gold polls HOOK.md | Howler sends message: "types STABLE" |
| Blocking questions | Howler sets Status: blocked, waits | Howler asks teammate directly |
| Seam declarations | Written at completion in debrief | Can be declared in real-time |

### What Does NOT Change

- **MANIFEST.md, CONTRACT.md, HOOK.md** — still mandatory. Same formats.
- **Debrief entries** — still mandatory at completion. Teammate messages are supplementary.
- **File ownership** — still strict. Teammate messaging doesn't grant cross-ownership.
- **Quality gates** — still White + Gray + /diff-review in parallel.
- **Human checkpoints** — still required at manifest approval, failure escalation, merge review.

### Dispatch Template (Agent Teams Variant)

When Agent Teams is available, the dispatch template adds one instruction:

```
  11. TEAMMATE MESSAGING (if Agent Teams enabled):
      - Send checkpoint notifications to dependent Howlers directly
        (e.g., "types STABLE — import UserSession from src/types/auth.ts")
      - Ask blocking questions to specific teammates (not broadcast)
      - Declare seams in real-time to the target Howler
      - All teammate messages are ephemeral — the debrief entry remains the
        authoritative handoff record
```

### When to Use Agent Teams vs. Standard Dispatch

| Scenario | Recommendation |
|----------|---------------|
| All Howlers are independent (no checkpoint deps) | Standard dispatch — no benefit from messaging |
| Howlers have checkpoint deps (#types) | Agent Teams — faster unblocking via direct notification |
| Howlers need to coordinate on shared behavior | Agent Teams — blocking questions prevent drift |
| < 3 Howlers | Standard dispatch — messaging overhead not worth it |

**Agent Teams is still experimental (as of March 2026).** Use standard dispatch as the default. Opt into Agent Teams per-spectrum when checkpoint deps would benefit from real-time notification.

### Phased Adoption Path

Spectrum's relationship with Agent Teams is **integration, not competition**. Spectrum provides the coordination protocol (contracts, failure taxonomy, Obsidian) that Agent Teams lacks. Agent Teams provides the execution primitives (worktree management, inter-agent messaging) that Spectrum implements manually today.

**Phase A — Available Now: Checkpoint Messaging** (documented above)

Supplementary real-time notifications via `TeammateTool send_message`. HOOK.md and debriefs remain authoritative. Zero risk — additive only.

**Phase B — When Agent Teams Exits Preview: Native Worktree Management**

Target: When Anthropic removes the `EXPERIMENTAL` flag.

Replace DIY worktree creation (§1.5 Worktree Pre-Creation) with Agent Teams' native `TeammateTool.create()` and `TeammateTool.assign()`. This eliminates the entire class of worktree git permission failures (~50% of Howlers in production spectrum runs) at the infrastructure level rather than via workaround.

Adoption gate: Agent Teams must demonstrate production-grade worktree reliability across 3+ spectrum runs before replacing DIY worktrees as the default. Run both approaches in parallel during validation.

**Phase C — When Stable for 3+ Months: Full Native Integration**

Evaluate whether CONTRACT.md and MANIFEST.md can be expressed as Lead context + structured `TeammateTool.assign()` parameters, reducing muster document ceremony while retaining Spectrum's non-negotiable guarantees:
- File ownership (no overlaps)
- Frozen contracts (with amendment protocol)
- Failure taxonomy (5 types + circuit breaker)
- Human gates (manifest, merge, non-transient failures)

Phase C is speculative — pursue only if Phase B proves Agent Teams primitives are sufficient. Document the evaluation criteria before starting.

---

## Security Quality Gate (/diff-review)

Trail of Bits' `differential-review` plugin is integrated as a third parallel quality gate alongside White and Gray.

### Per-Howler Quality Gate (Updated)

Before opening a PR, every Howler spawns **three gates in parallel**:

1. **White** — code quality review (zero blockers required)
2. **Gray** — test execution (zero failures required; coverage gaps = warning)
3. **/diff-review** — security-focused differential review (zero critical findings required)

```
                   ┌── White (code quality)
Howler completes ──┼── Gray (tests)
                   └── /diff-review (security)
                          │
                     All three pass
                          │
                     Copper opens PR
```

### /diff-review Classification

| Severity | Action |
|----------|--------|
| **CRITICAL** | Blocker — must fix before PR opens. Security vulnerabilities, injection risks, auth bypasses. |
| **HIGH** | Warning — noted in PR description. Should fix but doesn't block merge. |
| **MEDIUM/LOW** | Noted — included in PR description for human review. |

### When to Skip /diff-review

- **Doc-only spectrum runs** — no code to review
- **Test-only changes** — low security impact
- **Config/tooling changes** — unless touching auth, secrets, or deployment config

The Howler decides whether to run /diff-review based on the nature of their changes. If in doubt, run it — it adds ~30 seconds.

---

## Optional: Design Document Phase (Phase 0.5)

For spectrum runs involving API design, database schema changes, or complex UI architecture, an optional design phase produces a shared behavioral specification.

### When to Use Phase 0.5

- Spectrum touches 3+ API endpoints
- Spectrum includes database schema migrations
- Spectrum involves complex UI state management across multiple components
- CONTRACT.md alone can't capture the behavioral intent (only structural types)

### Phase 0.5 Protocol

After Blue writes PLAN.md and before Gold writes MANIFEST.md:

1. Gold spawns a **Violet** agent (Sonnet):

```
Agent(model="sonnet", prompt="
  Role: Violet — produce a shared design document for this spectrum run.
  Read: PLAN.md at {path}

  Produce DESIGN.md covering:
  1. API contracts — endpoint signatures, request/response shapes, error codes
  2. Data model changes — schema migrations, new tables/columns, constraints
  3. Component hierarchy — parent/child relationships, prop flow, shared state
  4. Sequence diagrams (text-based) — cross-module request flows
  5. Edge cases — what happens when auth fails, data is missing, concurrent writes

  DESIGN.md is a behavioral spec. CONTRACT.md (written next) is the structural spec.
  Together they define what Howlers build and how.

  Write DESIGN.md to the spectrum directory.
")
```

2. Gold reviews DESIGN.md, then writes MANIFEST.md and CONTRACT.md informed by both PLAN.md and DESIGN.md
3. DESIGN.md is committed to the spectrum directory and referenced in Howler prompts
4. Obsidian reads DESIGN.md (in addition to PLAN.md) during spec compliance verification

### DESIGN.md is Living (Unlike CONTRACT.md)

DESIGN.md captures behavioral intent — it may evolve as implementation reveals edge cases. Howlers can annotate DESIGN.md with implementation notes. CONTRACT.md remains frozen.

---

## Dynamic Scaling Rules

Gold adjusts spectrum approach based on complexity signals observed during and after execution.

### Muster Scaling

During muster, Gold evaluates whether an spectrum run is warranted:

| Signal | Action |
|--------|--------|
| PLAN.md has 3+ independent tasks with non-overlapping files | Spectrum (standard) |
| PLAN.md has 2 tasks | Consider sequential execution with quality gates (no spectrum overhead) |
| PLAN.md has 1 task | Single-agent execution — route to appropriate agent directly |
| PLAN.md has 9+ tasks | Split into 2 spectrum runs or restructure to reduce to 8 max |

### Post-Completion Scaling Feedback

After Phase 6.5, Gold evaluates spectrum efficiency and records scaling guidance in LESSONS.md:

```markdown
### Scaling Observations

- howler-auth completed in 73s with high confidence → task was well-scoped
- howler-config completed in 28s with high confidence → task was over-decomposed;
  merge with a related task next time (e.g., combine config + env setup)
- howler-api hit 2 Orange retries on different loci → task was under-decomposed;
  split API routes by domain (users vs. orgs) next time
```

### Real-Time Scaling

During execution, Gold does NOT dynamically add or remove Howlers. The DAG is fixed at dispatch. However:

- If a Howler completes and reports the task was trivial → Gold notes for next spectrum run
- If a Howler blocks and needs restructuring → that task becomes sequential follow-up, not a mid-spectrum split

**Spectrum size is planned, not reactive.** Dynamic scaling happens between spectrum runs via LESSONS.md, not within a running spectrum run.

---

## Model Assignments

| Role | Model | Rationale |
|------|-------|-----------|
| **Gold** | Sonnet | Task decomposition, contract authoring, cross-referencing N debriefs for seam/assumption mismatches. Evaluated against Opus (gold-eval-0331): 0.94 composite at 91% cost savings. Pax severity over-flagging is the one caveat -- human reviews blocker classifications before actioning. |
| **Blue** | Sonnet | PLAN.md feeds muster. A bad plan cascades through the entire spectrum run. |
| **Howlers** | Sonnet (floor) | Implementation is Sonnet's sweet spot. Haiku passes tests but misses architectural intent from the contract. Inherit session model, never below Sonnet. |
| **White** | Sonnet | Reasoning depth for subtle bugs, security, and contract compliance. |
| **Gray** | Sonnet | Diagnosing failures and writing missing tests needs Sonnet-level reasoning. Haiku misdiagnoses flaky tests. |
| **Orange** | Sonnet | Root cause tracing across call stacks. |
| **Copper** | Haiku | Commits, branch naming, PR creation are mechanical. |
| **Obsidian** | Sonnet | Spec compliance requires reading PLAN.md acceptance criteria and verifying against merged code. Needs reasoning depth to assess whether criteria are truly met vs. superficially satisfied. |
| **Brown** | Haiku | Summarizing HOOK.md files, debrief entries, and timing data into LESSONS.md is mechanical aggregation. Gold reviews the draft before committing. |

---

## Safety Rails

- **No overlapping file CREATES/MODIFIES** -- verified in muster, no exceptions
- **No auto-merging** -- human reviews and merges every PR
- **No auto-recovery (except transient)** -- `transient` failures may be auto-recovered by Gold without human confirmation; all other failure types require human decision
- **Circuit breaker: 2 failures on same locus auto-escalate to structural** -- even `transient` failures become `structural` when the same locus fails twice; Gold cannot auto-resume past the breaker
- **Type checkpoints: dependent Howlers may start on `#types` STABLE signals** -- Gold polls HOOK.md for checkpoint state; dispatches as soon as checkpoint fires, not waiting for full Howler completion
- **`convoy-contracts.d.ts` committed to base branch before dispatch** -- TypeScript spectrum runs only; Howlers fork from this commit so shared types are present from the start
- **Transient failures may be auto-recovered without human confirmation** -- but locus history check is mandatory before auto-resuming; see Phase 3.2
- **LESSONS.md written after every successful spectrum run** -- project memory at `~/.claude/projects/<project-slug>/memory/LESSONS.md`; Gold writes it during Phase 6.5 before cleanup
- **Max 8 parallel Howlers** -- coordination overhead grows nonlinearly; 8 is the practical ceiling before seam management dominates
- **Max 2 Orange retries per Howler** -- then mark blocked, escalate to human
- **Quality gates are mandatory** -- White + Gray in parallel, same as single-agent PRs
- **White re-run after blocker fixes is mandatory** -- if any blocker is fixed during quality gate, White must re-run before Copper opens the PR
- **Reflexion check every 5 file writes** -- Howlers re-read their scope in CONTRACT.md; if touching files outside ownership matrix, stop and log drift
- **Post-dispatch worktree verification is mandatory** -- Gold checks branch name, base_branch, base_commit for every Howler immediately after dispatch
- **Incremental integration testing during merge** -- Gray runs after each PR merge (3+ PRs), not just after all merges
- **Obsidian verification before learning** -- Obsidian checks spec compliance after Gray passes; PARTIAL/NON-COMPLIANT requires human decision
- **Smart quote grep for content-heavy spectrum runs** -- Gray greps for Unicode curly quotes in .ts/.tsx after merge
- **CONTRACT.md is frozen at dispatch** -- Howlers never modify it; if the contract is wrong, block and escalate to Gold who re-runs muster
- **Contract deviations must be documented** -- if a Howler can't follow CONTRACT.md, they write AMENDMENT.md and explain why, not silently diverge
- **Branch naming**: `spectrum/<rain-id>/<howler-name>` -- easy identification and cleanup
- **Confirm before destructive git ops** -- push, force push, branch delete
- **Spectrum directories are ephemeral** -- cleaned up after Phase 6.5 completes

---

## CMUX Integration

[CMUX](https://github.com/anthropics/cmux) is a terminal multiplexer for Claude Code sessions. When running spectrum inside CMUX, you get color-coded sidebar pills showing agent status and token usage, structured log entries, and desktop notifications.

All hooks are optional -- Spectrum works identically without CMUX. Agent results render inline in the terminal by Claude Code natively -- no custom display is needed.

### Architecture

```
convoy_roles.py          Shared module (role detection, spectrum state, dispatch registry,
  |                                     pill management with file locking)
  |
  +-- cmux-agent-track.sh   PostToolUse(Agent) — sets sidebar pill, logs dispatch,
  |                                               writes dispatch registry, updates spectrum state
  +-- cmux-agent-window.sh  SubagentStop       — reads dispatch registry for role identity,
  |                                               updates pill with token count + duration,
  |                                               logs completion, updates spectrum state
  +-- cmux-notify.sh        Stop / Task        — desktop notifications with spectrum context
```

**State files** (all in `/tmp/`, ephemeral):

| File | Written by | Read by | Purpose |
|------|-----------|---------|---------|
| `cmux-spectrum-state.json` | track + window hooks | CLI, notify | Spectrum lifecycle (howlers, progress, phase) |
| `cmux-dispatch-registry.json` | track hook | window hook | Maps status_key → role identity across dispatch→completion |
| `cmux-active-pills.json` | track + window hooks | track + window hooks | Pill cap enforcement (max 3, with timestamps for duration) |

**CLI**: `cmux-spectrum-status` reads state files directly and prints a formatted summary. Supports `--json` and `--watch` flags.

### What You See

**Sidebar pills** (max 3, auto-cycling):
```
  Blue                       (blue compass — dispatched, running)
  White ✓ 28.4k 0m 33s      (gray checkmark — completed with token count + duration)
  Howler                     (amber hare — dispatched, running)
```

- Max 3 pills visible at any time. When a 4th agent dispatches, the oldest pill is evicted.
- On completion, pills update to show: `{role} ✓ {tokens} {duration}` (gray) or `{role} ✗ {tokens} {duration}` (red).
- All pills auto-clear after 15 seconds.
- Pill operations use `fcntl.LOCK_EX` to prevent corruption under concurrent dispatch/completion.

**Structured log** (sidebar):
```
[Blue]      Spawned: plan auth system [bg]
[Howler]    howler-auth dispatched [bg]
[Howler]      owns: src/middleware/auth.ts, src/types/auth.ts
[Howler]    howler-api dispatched [bg]
[White]     ✓ review hook correctness 28.4k 0m 33s
[Gray]      ✓ test hooks end-to-end 22.8k 1m 15s
[Gold]      All 3 howlers complete — ready for Pax
```

**Token usage** is parsed from the agent's transcript JSONL file (`agent_transcript_path` in SubagentStop event). The hook sums `input_tokens + output_tokens` across all API calls.

### Dispatch Registry

The dispatch registry (`/tmp/cmux-dispatch-registry.json`) solves a key problem: Claude Code's `SubagentStop` event has different fields than `PostToolUse(Agent)` -- notably `agent_type` instead of `subagent_type`, and no `tool_input.description`.

The track hook writes `{status_key: {role_key, role, description}}` on dispatch. The window hook uses a multi-strategy lookup on completion:
1. Try registry by description-based status_key
2. Try registry by description match
3. Detect role from `agent_type`, then find the oldest matching registry entry by role

This ensures the completion hook updates the correct pill (not a duplicate) and shows the right role name/color in logs.

### Role Detection

Roles are detected by `convoy_roles.py` with priority ordering:

1. **`subagent_type` / `agent_type` mapping** (highest confidence):

   | Spectrum Role | `subagent_type` | Built-in Alias |
   |---|---|---|
   | Gold | `mayor` | `orchestrator` |
   | Blue | `scout`, `Plan`, `Explore` | `work-planner` |
   | Whites | `inspector` | `code-reviewer` |
   | Grays | `outrider` | `test-runner` |
   | Oranges | `mechanic` | `debugger` |
   | Coppers | `courier` | `git-agent` |
   | Howlers | `rider` | `general-purpose` |
   | Helldivers | `helldivers` | `product-research` |
   | Primus | `primus` | `product-strategy-partner` |
   | Greens | `greens` | `jira-ticket-writer` |
   | Obsidians | `sentinel` | — |
   | Browns | `archivist` | — |

2. **Word-boundary keyword match** -- `\brider\b` (not substring, avoids false positives like "provider")

3. **Structured spectrum fallback** -- only if prompt contains `Spectrum: <id>` (not just the words "spectrum")

| Role | Color | Hex | Icon | Glyph |
|------|-------|-----|------|-------|
| Gold | Gold | #f9e2af | crown | ♛ |
| Blue | Blue | #89b4fa | compass | ◎ |
| Howler | Peach | #fab387 | hare | » |
| White | Mauve | #cba6f7 | magnifying glass | ✦ |
| Gray | Sky | #89dceb | shield | ⛨ |
| Orange | Flamingo | #eba0ac | wrench | ✧ |
| Copper | Overlay | #9399b2 | paper plane | ▶ |
| Helldiver | Gold | #f9e2af | binoculars | ◈ |
| Primus | Pink | #f5c2e7 | map | ⊕ |
| Green | Lavender | #b4befe | clipboard | ≡ |
| Obsidian | Teal | #94e2d5 | shield-check | ⊘ |
| Brown | Overlay | #9399b2 | archive | ⌂ |

Palette is Catppuccin Mocha-aligned: all accent colors achieve 7:1+ contrast on dark (#1e1e2e) backgrounds.

### Spectrum State Lifecycle

```
dispatch (track hook)    -> state.json created, howlers registered as "running"
completion (window hook) -> howler marked "complete"/"failed"
all howlers done         -> phase set to "pax"
session end (notify)     -> notification includes spectrum summary
```

### Setup

Hooks in `~/.claude/settings.json` (already configured):

```json
{
  "hooks": {
    "Stop": [{ "hooks": [{ "type": "command", "command": "~/.claude/hooks/cmux-notify.sh" }] }],
    "PostToolUse": [
      { "matcher": "Task", "hooks": [{ "type": "command", "command": "~/.claude/hooks/cmux-notify.sh" }] },
      { "matcher": "Agent", "hooks": [{ "type": "command", "command": "~/.claude/hooks/cmux-agent-track.sh", "async": true }] }
    ],
    "SubagentStop": [{ "hooks": [{ "type": "command", "command": "~/.claude/hooks/cmux-agent-window.sh", "async": true }] }]
  },
  "sandbox": { "allowUnixSockets": ["~/Library/Application Support/cmux/cmux.sock"] }
}
```

- Tracking and window hooks run `async: true` so they don't block agent execution
- `sandbox.allowUnixSockets` is required for CMUX socket access
- All hooks gracefully exit if CMUX isn't running
- No `jq` dependency -- hooks use `python3` (macOS default)

### Writing Custom Hooks

Import from the shared module:

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/hooks"))
from convoy_roles import (
    detect_role, cmux, get_spectrum_state,
    add_pill, remove_pill, get_pill_timestamp,
)
```

Available CMUX commands:
- `cmux set-status <key> <label> --icon <name> --color <hex>` -- sidebar pill
- `cmux clear-status <key>` -- remove pill
- `cmux log --level <info|progress|success|warning|error> --source <name> -- <msg>` -- structured log
- `cmux notify --title <title> --body <body>` -- desktop notification

---

## Quick Reference: Gold Checklist

```
MUSTER
[ ] Read LESSONS.md if present at ~/.claude/projects/<project-slug>/memory/LESSONS.md
[ ] Read ENTITIES.md if present at ~/.claude/projects/<project-slug>/memory/ENTITIES.md
[ ] Verify PLAN.md exists (run Blue if not)
[ ] Evaluate spectrum size: 3+ tasks = spectrum, 2 = consider sequential, 1 = single-agent
[ ] If API/schema spectrum: run Phase 0.5 (Violet → DESIGN.md) before MANIFEST
[ ] Write ARCHITECTURE.md (codebase structure snapshot)
[ ] Decompose work into tasks with explicit file ownership lists
[ ] Build file ownership matrix -- no overlaps in CREATES/MODIFIES
[ ] Express dependencies as a DAG (not flat batches) — verify DAG is acyclic
[ ] Verify all checkpoint dep names in the DAG are defined in the contract
[ ] Verify Design-by-Contract: every Howler has Preconditions, Postconditions, Invariants
[ ] Write MANIFEST.md to spectrum directory
[ ] Write CONTRACT.md with shared types, Design-by-Contract sections, conventions
[ ] For TypeScript spectrum runs: write and commit convoy-contracts.d.ts to base branch
[ ] Present manifest + contract to human
[ ] Human confirmed -> proceed
[ ] Write initial CHECKPOINT.json (phase: approved, all howlers pending)

DISPATCH
[ ] Spawn Howlers using the dispatch template -- fill every placeholder, no improvisation
[ ] Dispatch Howlers as DAG edges are satisfied (not all at once)
[ ] Branch naming: spectrum/<rain-id>/<howler-name>
[ ] Post-dispatch worktree verification per Howler (§2.1a): branch name, base_branch, base_commit
[ ] CONTRACT.md is now frozen -- no Howler may modify it
[ ] Monitor for checkpoint signals (types: STABLE in HOOK.md) -- dispatch deps immediately
[ ] Update CHECKPOINT.json after each dispatch, completion, checkpoint, or failure

RECOVERY (when a Howler fails)
[ ] Classify failure type before choosing recovery action (transient/logical/structural/environmental/conflict)
[ ] Check locus history before auto-resuming transient failures
[ ] transient: auto-resume (no human confirmation needed) — unless circuit breaker trips
[ ] logical/structural/environmental/conflict: present options to human
[ ] Circuit breaker: if same locus failed 2+ times, escalate to structural regardless of type

PAX (after Howlers return)
[ ] Check for missing debrief entries (indicates failed Howlers)
[ ] For failed Howlers: read HOOK.md, classify failure, present recovery options to human
[ ] Read all debrief entries (YAML frontmatter)
[ ] Run automated seam-check against YAML frontmatter — write SEAM-CHECK.md
[ ] Read all AMENDMENT.md files from Howler worktrees
[ ] Validate assumptions: every assumption maps to completed work
[ ] Check file overlap: no path in two Howlers' files_created/files_modified
[ ] Write PAX-PLAN.md with merge order, seam check results, warnings, integration risks
[ ] Present SEAM-CHECK.md + PAX-PLAN.md to human

MERGE (incremental integration testing)
[ ] For each PR in PAX-PLAN.md order: merge → Gray → pass → next
[ ] If Gray fails after a merge: halt, diagnose, fix before continuing

TRIUMPH
[ ] Run Gray on fully merged main branch (final integration check)
[ ] Flag integration failures as sequential follow-up
[ ] Spawn Obsidian for spec compliance verification (§6.25)
[ ] Review SENTINEL-REPORT.md — COMPLIANT proceeds, PARTIAL/NON-COMPLIANT needs human decision
[ ] Spawn Brown to draft LESSONS.md entry (§6.5.0)
[ ] Review and commit LESSONS-DRAFT.md to ~/.claude/projects/<project-slug>/memory/LESSONS.md
[ ] Update ENTITIES.md with entity-level discoveries from this spectrum run
[ ] Record scaling observations in LESSONS.md (over/under-decomposed tasks)
[ ] Set CHECKPOINT.json phase to "complete"
[ ] Clean up spectrum directory (after LESSONS.md is written)
```

---

## Acknowledgments

Core ideas adapted from [Gas Town](https://github.com/steveyegge/gastown) by Steve Yegge -- a workspace manager for coordinating 20-30+ AI coding agents at enterprise scale. Spectrum takes Gas Town's most impactful patterns (persistent hooks, async messaging, shared contracts) and implements them using Claude Code's native primitives: sub-agents, worktree isolation, and the filesystem.

The key insight: **the difference between "parallel execution" and "coordinated parallel work" is persistent state and shared contracts.** Howlers are ephemeral. State is not.
