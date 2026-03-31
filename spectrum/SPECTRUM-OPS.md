# Spectrum Ops Manual

> Condensed operational reference. Full spec: `~/.claude/SPECTRUM.md`

---

## Roles

| Role | `subagent_type` | Model | Glyph | Color | Purpose |
|------|----------------|-------|-------|-------|---------|
| Golds | `golds` | sonnet | ♛ | `yellow` | Muster, contracts, seam analysis, merge planning |
| Blues | `blues` | sonnet | ◎ | `blue` | Plan work → PLAN.md (before Spectrum) |
| Howlers | `howlers` | sonnet+ | » | `orange` | Implement tasks in isolated worktrees |
| Whites | `whites` | sonnet | ✦ | `purple` | Pre-PR diff review, contract compliance |
| Grays | `grays` | sonnet | ⛨ | `gray` | Run tests, diagnose failures, write coverage |
| Oranges | `oranges` | sonnet | ✧ | `red` | Root cause analysis on blocked Howlers |
| Coppers | `coppers` | haiku | ▶ | `cyan` | Commits, branches, PRs |
| Obsidians | `obsidians` | sonnet | ⊘ | `teal` | Post-merge spec compliance against PLAN.md |
| Browns | `browns` | haiku | ⌂ | `overlay` | Draft LESSONS.md from Spectrum artifacts |
| Politicos | `politicos` | sonnet | ⚡ | `red` | Adversarial review of CONTRACT.md + MANIFEST.md before freeze |

---

## Activation

Spectrum activates when ALL are true:
- 3+ independent features/domains
- PLAN.md exists (run Blue first)
- Human confirms the manifest

---

## Phase 1: Muster (Gold)

**Structural enforcement**: During muster, the Gold MUST NOT use Write or Edit tools on project source files. The Gold plans; it does not code. The only files the Gold writes are Spectrum artifacts (MANIFEST.md, CONTRACT.md, ARCHITECTURE.md, CHECKPOINT.json, convoy-contracts.d.ts). If the Gold needs to modify source code, that work belongs to a Howler.

1. Generate rain ID (short slug: `auth-refactor-0329`)
2. Create `~/.claude/spectrum/<rain-id>/`
3. Read `LESSONS.md` + `ENTITIES.md` if present
4. **Validate PLAN.md** — sample 3-5 files to verify gap claims are current; flag stale assumptions. If PLAN.md is stale, have Blue refresh it before proceeding.
5. Evaluate scale: 3+ tasks = Spectrum, 2 = consider sequential, 1 = single-agent
6. **Update ARCHITECTURE.md** — persistent file at `~/.claude/projects/<slug>/ARCHITECTURE.md`. If exists: read it, patch only changed sections (new files, removed modules, dependency shifts). If not: create (~50-100 lines). Copy to Spectrum directory. **Never regenerate from scratch.**
7. For API/schema Spectrums: run Phase 1.5 → **DESIGN.md** (behavioral spec)
8. **Decomposition hazard scan** — before writing MANIFEST.md, answer:
   - Does any Howler synthesize outputs from others? → Apply barrel file or fragment+stitch
   - Are any tasks inherently serial (audits, stitchers)? → Label as critical-path risk
   - Is any task significantly larger than peers? → Flag with `effort: L`
   - Document reasoning: "I chose N Howlers because X. Alternative: M Howlers, rejected because Y."
9. Write **MANIFEST.md** (tasks with `effort: S/M/L` + `serial_risk: yes/no`, DAG with base_branch/base_commit, file ownership matrix)
10. Write **CONTRACT.md** (shared types, Design-by-Contract per Howler — full DbC for interface-heavy Howlers, conventions-only for pure-create Howlers)
11. For TypeScript: commit `convoy-contracts.d.ts` to base branch
12. **Adversarial plan review (Phase 1.5: The Passage)** — drop Politico (Sonnet) with:
    ```
    "Read MANIFEST.md and CONTRACT.md for Spectrum {id}. You are the adversary.
    Find: (a) file ownership gaps — files needed but missing from the matrix,
    (b) contract ambiguities — underspecified interfaces that will cause seam
    mismatches, (c) decomposition flaws — tasks that should be sequential but
    are parallel, or vice versa. Report blockers (must fix), warnings (should
    fix), and observations (FYI). Be specific — name files and interfaces."
    ```
    Gold addresses Politico's blockers before freezing CONTRACT.md. Warnings are documented in MANIFEST.md. **Skip for reaping mode.**
13. Present to human → explicitly flag high-risk seams + Politico concerns accepted-with-rationale → **do not drop until confirmed**
14. Write initial **CHECKPOINT.json** with schema:
    ```json
    {
      "rain_id": "...",
      "phase": "approved",
      "mode": "full|reaping",
      "howlers": [{"name": "...", "status": "pending", "branch": "...", "worktree_path": "...", "commit": null}],
      "errors": [],
      "cost_tracking": {
        "budget_limit": null,
        "total_tokens": 0,
        "per_howler": {}
      },
      "merge_reflections": [],
      "created_at": "ISO timestamp",
      "resumed_at": null
    }
    ```
    Valid phases: `planning`, `approved`, `dispatching`, `running`, `integrating`, `merging`, `complete`
    Valid howler statuses: `pending`, `dispatching`, `running`, `blocked`, `complete`, `failed`, `auto-skipped`

    **Budget tracking**: If `budget_limit` is set (in tokens or USD), the Gold checks cumulative cost before dropping each new Howler. If the Spectrum is projected to exceed budget, the Gold presents options to the human: continue, skip remaining Howlers, or abort. Token counts are logged per Howler from the Agent tool's usage output.

**Muster checklist:**
- [ ] PLAN.md validated (sampled files confirm gap claims are current)
- [ ] DAG is acyclic
- [ ] Zero overlapping CREATES/MODIFIES in file matrix
- [ ] Decomposition hazard scan completed (no unaddressed integration bottlenecks)
- [ ] Every Howler has effort/risk tags in MANIFEST.md
- [ ] Every Howler has Preconditions/Postconditions/Invariants (full DbC for interface-heavy; conventions-only for pure-create)
- [ ] Every checkpoint dep name exists in the contract
- [ ] LESSONS.md + ENTITIES.md incorporated
- [ ] Adversarial Politico review completed (blockers addressed, warnings documented) — skip for reaping mode
- [ ] High-risk seams and accepted Politico concerns flagged for human review
- [ ] ARCHITECTURE.md updated (persistent, incremental — never regenerated)
- [ ] CHECKPOINT.json written with defined schema

### Post-Approval: Worktree Pre-Creation

**After human confirms the manifest**, pre-create all worktrees before dropping any Howlers. This eliminates the ~50% git permission failure rate observed in production Spectrums (remnant-narrative-0329, remnant-ux-0329).

For each Howler in the DAG:

```bash
git worktree add -b spectrum/<rain-id>/<howler-name> \
  ~/.claude/spectrum/<rain-id>/worktrees/<howler-name> \
  <base_commit>
```

Verify all worktrees exist:

```bash
git worktree list
```

**Howlers are dropped into pre-initialized directories.** They write files only — no branch creation, no initial commit required. If a Howler's git operations still fail, it should write all files and set `git_status: needs_operator_commit` in HOOK.md. The Gold commits on the Howler's behalf.

### DAG Node Format
```yaml
- id: howler-auth
  deps: []
  branch: spectrum/<rain-id>/howler-auth
  base_branch: staging
  base_commit: abc1234

- id: howler-api
  deps: [howler-auth#types]
  branch: spectrum/<rain-id>/howler-api
  base_branch: staging
  base_commit: abc1234
```

Deps: `howler-name` = full completion, `howler-name#types` = STABLE checkpoint.

---

## Reaping Mode

For 3-4 Howler Spectrums where all tasks are pure-create with no shared interfaces:

**Activation** (all must be true):
- 3-4 Howlers maximum
- All Howlers only CREATE new files (no MODIFIES)
- No shared TypeScript interfaces between Howlers
- Human requests "reaping" or Gold judges overhead excessive

**Simplified muster (~3 min instead of ~8 min):**

1. Generate rain ID
2. Create Spectrum directory
3. Read LESSONS.md if present
4. Write **LIGHT-MANIFEST.md**:
   ```markdown
   # Light Manifest: <rain-id>
   Mode: reaping

   | Howler | Scope | Creates |
   |--------|-------|---------|
   | howler-a | ... | file1.md, file2.md |
   | howler-b | ... | file3.md, file4.md |

   CONFLICTS: none (all pure-create, verified)
   ```
5. Write **simplified CONTRACT.md** (conventions only, no Design-by-Contract sections)
6. Present to human → confirm
7. Write CHECKPOINT.json with `"mode": "reaping"`
8. Pre-create worktrees (always required)

**What stays the same:** White + Gray + /diff-review, HOOK.md, debriefs, worktree pre-creation, LESSONS.md

**What's skipped:** ARCHITECTURE.md, full DAG YAML, per-Howler DbC, Obsidian, ENTITIES.md

**Escalation:** If a Howler blocks, Gold may upgrade to full mode mid-Spectrum.

Gold notes `"mode": "reaping"` in CHECKPOINT.json. Lessons are still recorded.

---

## Status Roster (Mandatory — All Phases)

Gold MUST print a status roster inline in the conversation at every phase transition and after each agent dispatch or completion. This is the user's primary visibility into which agents are running.

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

**Status symbols:**
- `●` — currently running
- `✓` — completed successfully
- `✗` — failed
- `■` — blocked
- `○` — pending / queued / not yet dispatched

**When to print:**
1. After muster approval (shows full roster with all agents pending)
2. After each Howler dispatch (update dispatched agent to `●`)
3. After each agent completion or failure (update to `✓` or `✗`)
4. At phase transitions (Muster → Drop → Proving → Forge → Pax → Triumph)
5. When the user asks for status

**Rules:**
- Include ALL agents that will participate, not just Howlers — Blues, Whites, Grays, Coppers, Obsidians, Browns all appear
- Show the agent's task in parentheses for Howlers
- Show dependency waits for pending Howlers
- For the triple quality gate (White + Gray + /diff-review per Howler), show each gate agent
- Keep the roster compact — one line per agent, no verbose descriptions

---

## Phase 2: The Drop

### Discovery Relay

When dropping Howlers whose dependencies have completed, the Gold compresses completed Howlers' key findings into a ~500-token brief and includes it in the drop prompt under `DISCOVERY RELAY`. This propagates learnings from early Howlers to later Howlers without requiring the later Howler to read full debriefs.

**What to include in the relay:**
- Key decisions made by completed Howlers (from their HOOK.md Decisions section)
- File paths created that the new Howler might need to import from
- Warnings or surprises encountered
- Cross-domain observations relevant to the new Howler

**What NOT to include:** Full debrief content, error logs, or anything the CONTRACT.md already covers.

### Post-Drop Worktree Verification

**Immediately after each Howler drop**, verify:
1. Worktree exists at expected path
2. Branch is `spectrum/<id>/<howler-name>` (not auto-generated `worktree-agent-*`)
3. Base commit matches `base_commit` from MANIFEST.md DAG node
4. `git log -1` confirms the right starting point

If wrong: halt Howler, fix, re-drop. Adds ~5s per Howler, prevents 10+ min debugging.

### Howler Drop Template
```
Agent(isolation="worktree", run_in_background=True, model="sonnet", prompt="
  Spectrum: {rain-id}
  Howler: {howler-name}
  Branch: spectrum/{rain-id}/{howler-name}
  Worktree: ~/.claude/spectrum/{rain-id}/worktrees/{howler-name}
  Task: {scope from MANIFEST}

  WORKTREE NOTE: Your worktree is pre-initialized on branch
  spectrum/{rain-id}/{howler-name} from commit {base_commit}. Write your files
  to this directory. If git operations fail, write all files and set
  git_status: needs_operator_commit in HOOK.md — the Gold will commit on
  your behalf.

  File Ownership:
    CREATES: {files}
    MODIFIES: {files}
    READS: {files}

  Dependencies: {deps from DAG}

  CONTRACT (frozen -- block if wrong):
  {CONTRACT.md contents}

  INSTRUCTIONS:
  1. Write HOOK.md immediately (before any code).
  2. Update HOOK.md continuously -- decisions, seams, blockers, errors.
  3. Follow CONTRACT exactly. If wrong: Status: blocked, describe why.
  4. Only touch files in your CREATES/MODIFIES.
  5. REFLEXION: After every 5th file write, re-read CONTRACT.md scope and your
     File Ownership list. If touching files outside ownership, STOP and log drift.
  6. SCOPE ALIGNMENT CHECK: After every 20 tool calls, re-read your original
     Task above and CONTRACT.md. Write a 1-line 'Alignment: on-track' or
     'Alignment: drifted — [reason]' entry in HOOK.md under Progress.
     If drifted, STOP and correct before continuing.
  7. When types are finalized: mark Checkpoints.types: STABLE in HOOK.md.
  8. COMPLETION VERIFICATION: Before declaring done, verify mechanically:
     - Every file in CREATES exists: ls -la {each file}
     - Every file in MODIFIES has been changed: git diff --name-only
     - For TypeScript (if node_modules exists): tsc --noEmit passes
       (Skip if node_modules not installed — type checking defers to The Proving)
     - For tests (if test framework installed): test runner passes on your files
       (Skip if dependencies not installed — testing defers to The Proving)
     Write verification results in HOOK.md under '## Completion Verification'.
  9. When verified: run White + Gray + /diff-review in parallel (triple gate).
     Security criticals from /diff-review block the PR. High/medium = warning.
  10. Fix blockers. If blockers fixed, re-run White before proceeding.
     (Max 2 Orange retries, then Status: blocked).
  11. Write debrief to ~/.claude/spectrum/{rain-id}/{howler-name}.md
  12. Open PR via Copper targeting main.

  DISCOVERY RELAY (if provided):
  {compressed_findings from previously-completed Howlers — ~500 tokens max.
   Use these as context but do NOT depend on them for correctness.
   Your CONTRACT.md is the source of truth, not relay content.}
")
```

### HOOK.md Template
```markdown
# Hook: {task title}
Spectrum: {id}
Howler: {name}
Branch: spectrum/{id}/{name}
Worktree: ~/.claude/spectrum/{id}/worktrees/{name}
Started: {ISO timestamp}
Updated: {ISO timestamp}
Status: in_progress
git_status: ok
Confidence: medium
Confidence-Note: {what's uncertain}

## Task
{scope statement}

## File Ownership
CREATES: {files}
MODIFIES: {files}

## Checkpoints
- types: PENDING

## Progress
- [x] Step 1
- [ ] Step 2

## Decisions
- {key decisions and rationale}

## Seams
- {what other Howlers need from this work}

## Cross-Domain Observations
- {anything noticed outside your ownership boundary — bugs, inconsistencies, opportunities in other Howlers' domains. Flag it here even if you can't fix it.}

## Completion Verification
- [ ] All CREATES files exist: {ls results}
- [ ] All MODIFIES files changed: {git diff --name-only results}
- [ ] Type check passes: {tsc --noEmit or N/A}
- [ ] Tests pass on owned files: {test results or N/A}

## Blockers
- (none)

## Errors Encountered
- (none)
  locus: {file path}
```

**`git_status` values**: `ok` (default — git operations work), `needs_operator_commit` (git failed — Gold commits on Howler's behalf after Howler completes file writes).

**Howler heartbeat**: Every 30 tool calls or ~1 hour (whichever comes first), update HOOK.md with current status. If the Gold detects no heartbeat for 4+ hours, the Howler is treated as stuck and escalated without waiting for manual intervention.

### Type Checkpoints

Mark `types: STABLE` in HOOK.md when interfaces are finalized. This unblocks `#types` deps. **STABLE is a contract** — do not change exports after marking.

### Worktree Cleanup Before Quality Gates

Before dropping White or Gray on the merged branch, verify all Howler worktrees are removed:

```bash
git worktree list
# If any spectrum worktrees remain:
git worktree remove <path> --force
git worktree prune
```

Test discovery frameworks (Vitest, pytest, jest) find test files in mounted worktrees and report false duplicates (lesson: remnant-ux-0329).

### Quality Gate (per Howler)

Drop **all three in parallel** before opening PR:
1. White — zero blockers (code quality)
2. Gray — zero failures (tests; coverage gaps = warning)
3. /diff-review — zero criticals (security; high/medium = warning)

If blockers are found and fixed: **re-run White** before Copper opens PR.

**Content-heavy Spectrums**: Gray also greps for Unicode curly quotes (`[''""]`) in .ts/.tsx — these are blockers.

Skip /diff-review for: doc-only Spectrums, test-only changes, non-security config.

### Debrief YAML Frontmatter
```yaml
---
howler: howler-auth
spectrum: auth-refactor-0329
status: complete
pr: https://github.com/org/repo/pull/47
completed: 2026-03-29T15:20:00Z
confidence: medium
seams:
  - id: s1
    target_howler: howler-ui
    type: import
    what: "SignInButton from @clerk/nextjs"
    where: "Header.tsx"
assumptions:
  - id: a1
    about_howler: howler-ui
    what: "will add SignInButton to the header"
files_created:
  - src/middleware/auth.ts
files_modified:
  - src/app/layout.tsx
contract_compliance: full
open_exits:
  - "No org-creation flow"
warnings:
  - "Clerk requires manual dashboard setup"
---

## What I Built
{narrative}

## Decisions Made
{narrative}
```

---

## Phase 3: The Forge

### Failure Classification

| Type | Auto-recover? | Action |
|------|--------------|--------|
| transient | Yes (if circuit breaker clear) | Resume from HOOK.md |
| logical | No — human confirms | Orange diagnoses, then Resume or Retry |
| structural | No — human confirms | Re-run muster |
| environmental | No — human confirms | Pause all, fix env, resume |
| conflict | No — human confirms | Freeze and escalate |

### Circuit Breaker
2 failures on same `locus:` → auto-escalate to structural. Gold checks locus history before auto-resuming.

### Contract Amendments

**Non-breaking** (additive): Write AMENDMENT.md, continue working.
**Breaking** (rename/remove): Write AMENDMENT.md, set Status: blocked, stop.

---

## Phase 4: Pax (Gold)

1. **Independent validation** — do NOT trust Howler self-reports. For each Howler:
   - Read 2-3 key files the Howler created/modified
   - Verify against CONTRACT.md postconditions (exported types match? integration points exist?)
   - Check no files outside the ownership matrix were touched
   - Flag discrepancies as integration risks in PAX-PLAN.md
2. Run `python3 ~/.claude/hooks/seam_check.py ~/.claude/spectrum/<rain-id>/`
3. Read SEAM-CHECK.md results
4. Review Cross-Domain Observations from each Howler's HOOK.md — surface issues that need attention
5. Read AMENDMENT.md files from Howler worktrees
6. Write PAX-PLAN.md with merge order, independent validation results, seam check results, warnings, risks
7. Present to human — **no auto-merging**

---

## Phase 5: Merge (Incremental Integration Testing)

Human merges PRs in PAX-PLAN.md order. Dependencies merge first.

**After each merge:**
1. **Gray runs tests.** If tests fail, halt and fix before merging more.
2. **Per-PR self-reflect** — Gold writes a 3-5 line note in CHECKPOINT.json under `merge_reflections`: what worked, what surprised, what the next merge should watch for. These compound — reflection N informs merge N+1. (From metaswarm: capture learnings atomic with the code, not just post-Spectrum.)

(For 2 or fewer PRs, a single post-merge Gray run is sufficient. Self-reflect still runs.)

---

## Phase 6: Triumph

1. Run Gray on fully merged main (final integration check)
2. Fix integration failures as sequential follow-up
3. Drop **Obsidian** — verifies PLAN.md (+ DESIGN.md if present) against merged code → SENTINEL-REPORT.md
   - COMPLIANT → proceed. PARTIAL/NON-COMPLIANT → human decides.
4. Drop **Brown** — drafts LESSONS.md + ENTITIES.md updates from Spectrum artifacts → LESSONS-DRAFT.md
5. Gold reviews and commits LESSONS.md to `~/.claude/projects/<project-slug>/memory/LESSONS.md`
6. Gold curates ENTITIES.md — merge Brown additions, remove stale entries
7. Record scaling observations (over/under-decomposed tasks) in LESSONS.md
8. Set CHECKPOINT.json phase to "complete"
9. Delete Spectrum directory

---

## Agent Teams Integration

Spectrum can run on top of Claude Code's Agent Teams primitives as they mature. Adoption is phased to avoid betting on research-preview features.

### Phase A — Available Now: Checkpoint Messaging

When `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is set:

Howlers can use `TeammateTool send_message` to notify the Lead when checkpoint deps are STABLE, instead of waiting for the Gold to poll HOOK.md. This is **supplementary** — HOOK.md updates and debrief entries remain mandatory and authoritative.

**Example Howler instruction (append to drop template when Agent Teams is enabled):**

```
When your types checkpoint is STABLE, send a TeammateTool message to the Lead:
"howler-auth#types STABLE. Types at src/types/auth.ts. Key exports: UserSession,
AuthContext." Then continue your work without waiting for acknowledgment.
```

This reduces checkpoint latency from "Gold polls HOOK.md" to "real-time message."

### Phase B — When Agent Teams Exits Preview: Worktree Management

**Target**: When Anthropic removes the `EXPERIMENTAL` flag (estimated Q3-Q4 2026).

Replace the DIY worktree creation (§Post-Approval: Worktree Pre-Creation) with Agent Teams' native worktree management. Gold uses `TeammateTool.create()` and `TeammateTool.assign()` instead of manual `git worktree add`. This eliminates the entire class of worktree git permission failures at the infrastructure level.

**Adoption gate**: Agent Teams must demonstrate production-grade worktree reliability across 3+ Spectrums before replacing DIY worktrees as the default.

### Phase C — When Stable for 3+ Months: Full Native Integration

Evaluate whether CONTRACT.md and MANIFEST.md can be expressed as Lead context + structured `TeammateTool.assign()` parameters, reducing muster document ceremony while retaining coordination guarantees (file ownership, frozen contracts, failure taxonomy).

**This phase is speculative** — only pursue if Phase B proves Agent Teams primitives are sufficient for Spectrum's coordination needs.

---

## Safety Rails

**Ownership & Contracts:**
- No overlapping file CREATES/MODIFIES — verified during muster and by Politico
- CONTRACT.md frozen at drop — Howlers block and escalate, never modify
- STABLE checkpoints are contracts — no changes after marking
- Silent contract divergence is always a blocker (file AMENDMENT.md)

**Gold Constraints:**
- Gold does not write source code — only Spectrum artifacts (structural enforcement)
- No auto-merging — human merges every PR
- PLAN.md validated before manifest authoring

**Howler Constraints:**
- Reflexion check every 5 file writes (re-read scope, stop if drifted)
- Scope alignment check every 20 tool calls (re-read task + CONTRACT.md, log alignment)
- Completion verification is mechanical (ls, git diff, tsc, tests) before declaring done
- Heartbeat every 30 tool calls or 1 hour — 4+ hours without update = stuck escalation

**Quality & Recovery:**
- Triple quality gate: White + Gray + /diff-review in parallel — criticals block
- White re-run mandatory after blocker fixes
- Max 2 Orange retries per Howler — then blocked, escalate to human
- Smart quote grep for content-heavy Spectrums (.ts/.tsx)

**Coordination:**
- Max 8 parallel Howlers
- Branch naming: `spectrum/<rain-id>/<howler-name>`
- Post-drop worktree verification mandatory
- Discovery relay: compressed findings from completed Howlers injected into dependent Howler drop
- Per-PR self-reflect: Gold captures learnings after each merge

**Persistence:**
- CHECKPOINT.json updated at every phase transition (with budget tracking)
- ARCHITECTURE.md persistent and incremental (never regenerated)
- LESSONS.md written after every successful Spectrum
- ENTITIES.md curated after every Spectrum
- Spectrum directories are ephemeral — cleaned up after merge

**Scaling:**
- Dynamic: 3+ = Spectrum, 2 = consider sequential, 1 = single-agent
- Reaping mode: 3-4 pure-create Howlers, ~3 min muster
- Incremental integration testing during merge (3+ PRs)
- Obsidian verification before LESSONS.md (skip in reaping mode)

---

## Directory Structure

```
~/.claude/spectrum/<rain-id>/
  MANIFEST.md          # DAG + file ownership (Gold, muster)
  CONTRACT.md          # Shared contracts (Gold, muster)
  <howler-name>.md     # Debrief with YAML frontmatter (Howler)
  SEAM-CHECK.md        # seam_check.py output (Gold, integration)
  PAX-PLAN.md          # Merge order + risks (Gold, integration)
  SENTINEL-REPORT.md   # Spec compliance verdicts (Obsidian, post-merge)
  LESSONS-DRAFT.md     # Retrospective draft (Brown, post-Obsidian)
  CHECKPOINT.json      # Spectrum state snapshot (Gold, every phase transition)
  ARCHITECTURE.md      # Codebase structure snapshot (Gold, muster)
  DESIGN.md            # Behavioral spec (Violet, optional Phase 1.5)

Each Howler worktree:
  HOOK.md              # Persistent state (Howler)
  AMENDMENT.md         # Contract change (Howler, optional)
```
