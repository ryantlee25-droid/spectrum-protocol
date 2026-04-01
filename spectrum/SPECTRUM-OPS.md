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
3. Read `LESSONS.md` + `ENTITIES.md` if present. If LESSONS.md contains a `## Known Failure Patterns` section, scan for patterns matching the current spectrum's task types and include relevant ones in each Howler's drop prompt under `KNOWN RISKS (from prior spectrums)`.
4. **Validate PLAN.md** — sample 3-5 files to verify gap claims are current; flag stale assumptions. If PLAN.md is stale, have Blue refresh it before proceeding.
5. Evaluate scale: 3+ tasks = Spectrum, 2 = consider sequential, 1 = single-agent
6. **Update ARCHITECTURE.md** — persistent file at `~/.claude/projects/<slug>/ARCHITECTURE.md`. If exists: read it, patch only changed sections (new files, removed modules, dependency shifts). If not: create (~50-100 lines). Copy to Spectrum directory. **Never regenerate from scratch.**

**Parallel muster reads**: Steps 3 (LESSONS.md + ENTITIES.md), ARCHITECTURE.md update,
and codebase_index.py runs are independent read operations. Gold SHOULD initiate them
in parallel (e.g., as background agents) rather than sequentially. Estimated savings:
1-2 min per muster.
7. For API/schema Spectrums: run Phase 1.5 → **DESIGN.md** (behavioral spec)
8. **Decomposition hazard scan** — before writing MANIFEST.md, answer:
   - Does any Howler synthesize outputs from others? → Apply barrel file or fragment+stitch
   - Are any tasks inherently serial (audits, stitchers)? → Label as critical-path risk
   - Is any task significantly larger than peers? → Flag with `effort: L`
   - Document reasoning: "I chose N Howlers because X. Alternative: M Howlers, rejected because Y."
9. Write **MANIFEST.md** (tasks with `effort: S/M/L` + `serial_risk: yes/no`, DAG with base_branch/base_commit, file ownership matrix)
10. Write **CONTRACT.md** with:
    - Shared types, interfaces, constants that multiple Howlers depend on
    - Naming conventions and patterns Howlers must follow
    - Per-Howler `## Codebase Context` section: Gold reads each file in the Howler's MODIFIES list and summarizes existing function signatures relevant to the task, patterns in use (e.g., "uses factory pattern", "all exports are named, not default"), and any gotchas observed (e.g., "this file has a circular import with X — avoid touching the import block"). Keep summaries to 5–15 lines per file. For Howlers with no MODIFIES files (all CREATES): write `## Codebase Context: N/A (all new files)`.
      Gold MUST run `tools/codebase_index.py` when it exists. The tool extracts import
      graphs, function signatures, and patterns for each file in the Howler's MODIFIES
      list. Output is ready to paste into CONTRACT.md's per-Howler Codebase Context
      section. If the tool is unavailable, Gold writes prose summaries as fallback
      (5–15 lines per file).
      Usage: `python3 tools/codebase_index.py --files {MODIFIES list} --root {project_root}`
    - Integration points (what connects to what)
    - Design-by-Contract per Howler — full DbC for interface-heavy Howlers, conventions-only for pure-create Howlers
    - Test impact map per Howler: output of `python3 tools/test_impact_map.py --files {MODIFIES+CREATES} --root {project_root}` — which test files cover the Howler's owned files
10.5. **Issue Confirmation Gate** — After writing CONTRACT.md, before running White Pre-Check or
    Politico, Gold displays to the human:

    > "Here is what I understood this issue to require:
    > - **Problem**: [one sentence]
    > - **Desired behavior**: [one sentence]
    > - **Out of scope**: [what was excluded and why]
    > Confirm or correct before I freeze the contract."

    Gold also writes a `## Issue Interpretation` block at the **top** of CONTRACT.md with these
    three bullets. Human confirms or redirects. If redirected, Gold revises CONTRACT.md and
    repeats the gate. **Do not proceed to White Pre-Check or Politico until confirmed.**
    **Skip for reaping mode and nano mode** (those modes do not produce a full CONTRACT.md).

11. **Pre-freeze review (parallel)** — Gold spawns White Pre-Check AND Politico
    simultaneously. They run in parallel:
    - White Pre-Check: verifies factual accuracy of CONTRACT.md against the codebase
    - Politico: adversarially reviews decomposition logic and interface design
    Gold waits for both to complete. Fixes White Pre-Check findings first (factual),
    then addresses Politico blockers (logical). Both must clear before freezing.
    **Estimated savings: ~3-4 min per full muster (previously sequential).**

    White Pre-Check prompt:
    ```
    "Read CONTRACT.md for Spectrum {id}. You are doing a pre-freeze accuracy check against the
    actual codebase. Check: (a) do all files listed in MODIFIES actually exist? (b) do the
    function signatures and types documented in each Howler's Codebase Context section match what
    is actually in those files? (c) are there any interface names or constants referenced in the
    contract that don't exist in the codebase? Report mismatches only — not style observations.
    Flag each as: STALE (contract references something that changed), MISSING (file/type doesn't
    exist), or MISMATCH (documented signature differs from actual). Skip for files in CREATES
    (they don't exist yet by design)."
    ```
    Gold patches CONTRACT.md to fix all STALE, MISSING, and MISMATCH findings before proceeding.
    For each finding that cannot be fixed (e.g., a file genuinely needs to be created as a
    precondition), document it as an `[ASSUMPTION: unverifiable, reason]` in CONTRACT.md.
    **Skip White Pre-Check for reaping mode and nano mode.**
12. **Contract-to-test generation** (TypeScript/Python spectrum runs only) — for each Howler
    with postconditions in CONTRACT.md, Gold generates a stub test file at
    `tests/spectrum/<howler-name>.contract.test.{ts|py}` that asserts **structural
    postconditions only**. Generate test stubs ONLY for:
    - **File existence**: "src/types/auth.ts exists"
    - **Export presence**: "module exports UserSession"
    - **Type shape**: "UserSession.role is 'admin' | 'member'"

    Do NOT generate tests for behavioral postconditions ("the auth middleware returns 401 for
    expired tokens", "function returns X under condition Y", business logic). Behavioral
    postconditions belong in CONTRACT.md as documentation targets for Gray — Gray verifies
    runtime behavior during the quality gate after implementation, where it has the actual code
    to test against. Attempting to generate behavioral tests at muster time produces either
    trivially passing tests (false confidence) or tests with Gold-introduced bugs.

    Stage structural contract test stubs alongside convoy-contracts.d.ts and commit together
    in step 13. Howlers run these contract tests as part of completion verification.
    **Skip for doc-only spectrums, nano mode, and reaping mode** (reaping mode uses simplified
    contracts with no per-Howler DbC sections, so there are no structural postconditions to test).

    Example contract test stub (TypeScript — structural assertions only):
    ```typescript
    // tests/spectrum/howler-auth.contract.test.ts
    // Auto-generated from CONTRACT.md structural postconditions — do not edit manually
    // Behavioral postconditions are verified by Gray during the quality gate.
    import { describe, it, expect } from 'vitest';

    describe('howler-auth structural postconditions', () => {
      it('src/types/auth.ts exports UserSession', async () => {
        const mod = await import('@/types/auth');
        expect(mod.UserSession).toBeDefined();
      });
      it('src/middleware/auth.ts exports authMiddleware', async () => {
        const mod = await import('@/middleware/auth');
        expect(mod.authMiddleware).toBeDefined();
      });
    });
    ```

    Use the project's existing test framework (jest/vitest for TypeScript, pytest for Python).
    If no test infrastructure exists, skip this step and document as `[ASSUMPTION: no test
    infrastructure — contract tests skipped]` in CONTRACT.md.
13. For TypeScript: commit `convoy-contracts.d.ts` to base branch
14. *(Politico runs in parallel with White Pre-Check in step 11 — see step 11 above.)*
    Politico prompt:
    ```
    "Read MANIFEST.md and CONTRACT.md for Spectrum {id}. You are the adversary.
    Find: (a) file ownership gaps — files needed but missing from the matrix,
    (b) contract ambiguities — underspecified interfaces that will cause seam
    mismatches, (c) decomposition flaws — tasks that should be sequential but
    are parallel, or vice versa. Report blockers (must fix), warnings (should
    fix), and observations (FYI). Be specific — name files and interfaces.
    Note: the White Pre-Check has already validated factual accuracy of CONTRACT.md
    against the codebase. Your role is adversarial review of the *decomposition logic and
    interface design*, not re-checking file existence."
    ```
    Gold addresses Politico's blockers before freezing CONTRACT.md. Warnings are documented in MANIFEST.md. **Skip for reaping mode.**
15. Present to human → explicitly flag high-risk seams + Politico concerns accepted-with-rationale → **do not drop until confirmed**
16. Write initial **CHECKPOINT.json** with schema:
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
      "locus_history": {},
      "circuit_breaker_state": {},
      "active_diagnostics": [],
      "gold_context_snapshot": {
        "last_phase": "dispatching",
        "pending_dag_edges": [],
        "manifest_path": "~/.claude/spectrum/{rain-id}/MANIFEST.md",
        "contract_path": "~/.claude/spectrum/{rain-id}/CONTRACT.md"
      },
      "created_at": "ISO timestamp",
      "resumed_at": null
    }
    ```
    Valid phases: `planning`, `approved`, `dispatching`, `running`, `integrating`, `merging`, `complete`
    Valid howler statuses: `pending`, `dispatching`, `running`, `blocked`, `complete`, `failed`, `auto-skipped`

    **Gold MUST update `locus_history` and `circuit_breaker_state` after every failure classification** (not just at phase transitions) so a new Gold session can reconstruct circuit breaker state on recovery.

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
- [ ] Test impact map generated for each Howler's MODIFIES/CREATES files (run tools/test_impact_map.py; include output in CONTRACT.md per Howler)
- [ ] Codebase context sections written in CONTRACT.md for each Howler's MODIFIES files (existing function signatures, patterns, gotchas — 5-15 lines per file; skip for Howlers with CREATES-only file lists)
- [ ] Issue Confirmation Gate passed — human confirmed 3-bullet interpretation (problem, desired behavior, out of scope) before White Pre-Check (skip for reaping mode and nano mode)
- [ ] White Pre-Check completed — all STALE/MISSING/MISMATCH findings patched or documented as ASSUMPTION in CONTRACT.md (skip for reaping mode and nano mode)
- [ ] Contract test stubs generated and committed for each Howler with postconditions (skip for doc-only, nano mode, and reaping mode)
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

## Nano Mode

For 2-3 Howler runs with obvious task boundaries where even reaping mode overhead (~3 min) is excessive. Targets muster + drop in under 1 minute.

**Activation** (all must be true):
- 2-3 Howlers maximum
- All Howlers only CREATE new files (no MODIFIES)
- No shared interfaces between Howlers
- Task boundaries are obvious — human or Gold judges without analysis

**Muster (~1 min):**

1. Generate rain ID
2. Create Spectrum directory
3. Write **NANO-MANIFEST.md** — task list + file ownership only:
   ```markdown
   # Nano Manifest: <rain-id>
   Mode: nano

   | Howler | Creates |
   |--------|---------|
   | howler-a | file1.md, file2.md |
   | howler-b | file3.md, file4.md |

   CONFLICTS: none (pure-create, verified)
   ```
4. Write **CHECKPOINT.json** with `"mode": "nano"`
5. **Auto-approve** — Gold presents the manifest and drops Howlers immediately. No human confirmation gate.
6. Howlers create their own branches (no pre-created worktrees)

**What stays the same:** File ownership tracking, HOOK.md per Howler, debrief per Howler, LESSONS.md after merge

**What's skipped:** CONTRACT.md, Politico, ARCHITECTURE.md, Obsidian, ENTITIES.md, human approval gate, White + Gray + /diff-review (Howlers self-verify only), worktree pre-creation

**Escalation:** If any Howler blocks, Gold upgrades to reaping mode immediately. Nano mode has no structural recovery path.

**Self-verify (nano Howlers only):** Before declaring done, run `ls` to confirm all created files exist and write a one-line completion note in HOOK.md. No type checks or test runner required unless the created files include test infrastructure.

---

## SWE-bench Mode

For single-issue benchmark tasks, Gold uses `examples/mini-CONTRACT.md` as the
contract template instead of the full CONTRACT.md. This template includes the
issue text, failing tests, regression guard, affected files, codebase context,
and test impact map — optimized for single-Howler accuracy runs.

Gold produces this ~50-100 line document in ~2 minutes (Variant A) or writes
a 200-token task brief instead (Variant B — the recommended starting point).
See `evaluation/swe-bench-prep/pipeline-design.md` for the full variant specs.

---

## Multi-Candidate Mode (SWE-bench and Accuracy-Critical Runs)

For accuracy-critical tasks (benchmarks, production hotfixes), Gold may run a
Howler N times (default N=3) on the same task and select the candidate whose
patch passes the most tests.

**Activation**: Gold sets `candidates: N` in the Howler's MANIFEST.md entry.
Only for single-Howler tasks — multi-Howler spectrums use standard dispatch.

**Selection**: After all N candidates complete, Gold runs Gray on each patch
independently. The patch with the highest test pass rate is selected. Ties
broken by: fewer files modified > fewer lines changed > first to complete.

**Cost**: N× the single-Howler cost. At N=3 with Variant B ($0.38/task),
total is ~$1.14/task — still below competitor per-task costs.

**When to use**: SWE-bench evaluation runs, production incident fixes,
any task where correctness outweighs cost.

**When NOT to use**: Standard spectrum runs (3+ Howlers), doc-only work,
tasks where the first-pass revision loop (step 8c) is sufficient.

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
4. At phase transitions (Muster → Drop → Forge → Pax → Merge → Triumph)
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

### Quality Gate Triggering

**Per-Howler gate triggering**: Quality gates (White + Gray + /diff-review) trigger
immediately when each individual Howler declares completion — Gold spawns them as
visible background agents (see Gold Post-Howler Protocol below). Do NOT wait for all
Howlers to finish before starting gates. On a 4-Howler run with staggered completion,
this reclaims 8-15 minutes that would otherwise be spent waiting.

PAX begins only after the last Howler completes (or fails). PRs may be opened while other Howlers are still running, provided PAX has not started.

### Gold Post-Howler Protocol

When a Howler returns with `Status: complete`, Gold runs the quality gate pipeline
as separate, visible agents. This replaces the previous model where Howlers
self-reviewed inside their own session.

**For each completed Howler, Gold spawns in parallel:**

1. **White** (code review):
   ```
   Agent(description="✦ Whites — reviewing {howler-name}", model="sonnet",
         run_in_background=True, prompt="
     Review the diff for {howler-name} in branch spectrum/{rain-id}/{howler-name}.
     Read HOOK.md for confidence areas. Zero blockers required.
     Output: structured Blocker/Warning/Suggestion report.
   ")
   ```

2. **Gray** (test runner):
   ```
   Agent(description="⛨ Grays — testing {howler-name}", model="sonnet",
         run_in_background=True, prompt="
     Run tests for {howler-name}'s changes in branch spectrum/{rain-id}/{howler-name}.
     Use the Test Impact Map from CONTRACT.md. Zero failures required.
     Output: test results with pass/fail counts.
   ")
   ```

3. **/diff-review** (security):
   ```
   Agent(description="✧ Oranges — security review {howler-name}", model="sonnet",
         run_in_background=True, prompt="
     Security-focused diff review for {howler-name}. Zero criticals required.
     High/medium = warnings in PR description.
   ")
   ```

**After all 3 return:**
- All pass → spawn Copper: `Agent(description="▶ Coppers — PR for {howler-name}", model="haiku", ...)`
- Any blocker → spawn Orange for diagnosis: `Agent(description="✧ Oranges — diagnosing {howler-name}", model="sonnet", ...)`
- After Orange diagnosis → Gold decides: Resume Howler, Retry, or Restructure

**Status roster update**: Gold prints an updated roster after each gate agent completes:
```
  » howler-auth  Worker     ✓ done
    ✦ White      Reviewer   ● running
    ⛨ Gray       Tester     ✓ pass
    ✧ /diff-rev  Security   ✓ pass
  » howler-api   Worker     ● running
```

**Nano mode exception**: In nano mode, Howlers self-verify (ls + HOOK.md note) and Gold
skips the quality gate pipeline entirely. No White, Gray, or /diff-review agents spawn.

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
  Read ~/.claude/spectrum/{rain-id}/CONTRACT.md before starting.
  Do NOT modify this file. If the contract is wrong, set Status: blocked.
  # Token note: CONTRACT.md is referenced by path, not inlined. For a 5-Howler run
  # with a 2000-token contract this saves ~10,000 input tokens (~$0.03 at Sonnet rates).

  INSTRUCTIONS:
  0. Read CONTRACT.md at the path above FIRST. Pay special attention to:
     - Your per-Howler `## Codebase Context` section (existing patterns you must follow)
     - Your preconditions/postconditions
     - Shared types and interfaces
     This is your source of truth. Do not re-derive patterns from the codebase if
     CONTRACT.md has already captured them — use what Gold documented.
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
       (Skip if node_modules not installed — type checking defers to the quality gate)
     - For tests (if test framework installed): run the specific test files listed in your
       ## Test Impact Map (from CONTRACT.md). If no map was provided, run tests on your owned
       files. Tests must pass; coverage gaps are warnings, not blockers.
       For files marked [none-found] in the impact map, run the full test suite rather than
       relying on the impact map — no targeted tests were found for those files.
       (Skip if dependencies not installed — testing defers to the quality gate)
     - Contract tests: run `tests/spectrum/{howler-name}.contract.test.{ts|py}` — these verify
       your CONTRACT.md postconditions are satisfied. All must pass before quality gates.
     - Postcondition verification (if CONTRACT.md has DbC for this Howler):
       run `python3 tools/verify_postconditions.py --contract {path} --howler {name} --root {project}`
       All postconditions must pass. Failures are blockers.
     Write verification results in HOOK.md under '## Completion Verification'.
  9. ISSUE RE-READ: After mechanical verification, re-read your CONTRACT.md
      postconditions section. For each postcondition, write a one-line assessment
      in HOOK.md under '## Issue Re-Read':
        - State the postcondition
        - State whether your implementation satisfies it (YES/NO/PARTIAL)
        - If NO or PARTIAL: what's missing and can you fix it now?
      If all postconditions are satisfied: write "All postconditions verified."
      If any are PARTIAL or NO: fix before proceeding to step 10 (revision pass).
      For Howlers without postconditions (pure-create, nano mode): fall back to
      the original prose-based re-read ("Does my implementation resolve the task?
      What edge cases does the task imply? Is there anything I deprioritized?").
      If no gaps: write "Issue re-read: no gaps identified." and proceed.
  10. REVISION PASS: If completion verification or contract tests revealed failures:
      - Read the test output and error messages carefully
      - Identify the root cause (not just the symptom)
      - Fix the issue
      - Re-run the failing tests
      - Update HOOK.md with what you fixed and why
      Maximum 2 revision passes. If tests still fail after 2 passes, document the
      failures in HOOK.md and proceed to debrief — Gold will run the quality gate
      and surface these failures to White and Gray with full context.
      If all tests passed on first try: skip this step.
  11. Write debrief to ~/.claude/spectrum/{rain-id}/{howler-name}.md
      (Use the Debrief YAML Frontmatter template. Include open_exits and warnings.)
  12. Signal completion: set Status: complete in HOOK.md. Your job ends here.
      Gold will spawn White, Gray, and /diff-review — do not run these yourself.
      Do not open a PR. Gold coordinates Copper after the gates pass.

  DISCOVERY RELAY (if provided):
  {compressed_findings from previously-completed Howlers — ~500 tokens max.
   Use these as context but do NOT depend on them for correctness.
   Your CONTRACT.md is the source of truth, not relay content.}

  KNOWN RISKS (from prior spectrums — if any match this task type):
  {Gold injects 0-3 relevant failure patterns from LESSONS.md ## Known Failure Patterns. If none match, omit this section.}
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
- [ ] Postcondition verification passes: {verify_postconditions.py results or N/A if no DbC}

## Issue Re-Read
- [ ] Re-read CONTRACT.md postconditions (or original task if no postconditions)
- {postcondition}: {YES/NO/PARTIAL} — {one-line evidence or what's missing}
- {postcondition}: {YES/NO/PARTIAL} — {one-line evidence or what's missing}
- Summary: {"All postconditions verified." | "Issue re-read: no gaps identified." | gaps and fix plan}

## Revision Pass
- Pass 1: {what failed, what was fixed, or "all tests passed — no revision needed"}
- Pass 2: {if needed — what failed, what was fixed}

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
3. Spawn **Obsidian** as a visible background agent:
   ```
   Agent(run_in_background=True, model="sonnet",
     description="⊘ Obsidians — spec compliance",
     prompt="
       Verify PLAN.md acceptance criteria against merged code.
       Write SENTINEL-REPORT.md with per-criterion PASS/PARTIAL/FAIL verdicts.
     ")
   ```
   - COMPLIANT → proceed. PARTIAL/NON-COMPLIANT → present to human before continuing.
4. Spawn **Brown** as a visible background agent after Obsidian completes:
   ```
   Agent(run_in_background=True, model="haiku",
     description="⌂ Browns — lessons learned",
     prompt="
       Read all spectrum artifacts. Draft LESSONS.md entry with decomposition
       patterns, contract friction, failure modes, timing, and Known Failure
       Patterns. Write to ~/.claude/spectrum/{rain-id}/LESSONS-DRAFT.md
     ")
   ```
   Gold reviews the draft before committing LESSONS.md to `~/.claude/projects/<project-slug>/memory/LESSONS.md`.
5. Gold curates ENTITIES.md — merge Brown additions, remove stale entries
6. Record scaling observations (over/under-decomposed tasks) in LESSONS.md
7. Set CHECKPOINT.json phase to "complete"
8. Delete Spectrum directory

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
- Issue re-read mandatory after completion verification — correctness assessment before quality gates
- Revision pass: max 2 attempts to fix test failures before escalating to quality gates
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
- CHECKPOINT.json persists `locus_history` and `circuit_breaker_state` (not just phase/howler status)
- Gold recovery from session death: read CHECKPOINT.json + MANIFEST.md + all HOOK.md files to reconstruct state
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

## Gold Recovery (Session Death)

If Gold's session dies mid-spectrum (context limit, crash, network), a new Gold session recovers by:

1. Read CHECKPOINT.json — determine current phase and Howler statuses
2. Read MANIFEST.md — reconstruct the DAG and file ownership
3. Read CONTRACT.md — reconstruct shared interfaces
4. Read each Howler's HOOK.md — determine per-agent progress
5. Read `locus_history` from CHECKPOINT.json — reconstruct circuit breaker state
6. Resume from the current phase:
   - If `phase=dispatching`: check which Howlers haven't been dropped yet, drop them
   - If `phase=running`: wait for in-flight Howlers (they persist via HOOK.md)
   - If `phase=integrating`: read debriefs, proceed to Pax
   - If `phase=merging`: check which PRs are merged, continue merge sequence

Gold MUST update CHECKPOINT.json with `locus_history` and `circuit_breaker_state` after every failure classification, not just at phase transitions.

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
