# Resilience Audit: Spectrum Protocol
**Date**: 2026-03-31
**Auditor**: Reliability Engineering (Blue)
**Scope**: SPECTRUM-OPS.md, SPECTRUM.md Phase 3, CLAUDE.md operational rules
**Method**: Static analysis of specification documents; no live runs observed

---

## Executive Summary

Spectrum Protocol has a well-reasoned failure taxonomy and circuit breaker, but carries five structural gaps that can cause silent data loss or runaway token spend: (1) no atomic writes for CHECKPOINT.json, (2) Gold session death has no recovery owner, (3) the circuit breaker threshold of 2 is too aggressive for fast-transient errors, (4) downstream Howlers block indefinitely when an upstream types checkpoint is never posted, and (5) nano mode skips every safety rail simultaneously.

The taxonomy covers ~80% of observed failure modes. Token exhaustion, Gold death, and API rate limits are unclassified and lack documented recovery paths.

---

## Part 1: Failure Taxonomy Completeness

### 1.1 The Five Canonical Types

| Type | Coverage assessment |
|------|-------------------|
| `transient` | Reasonably defined. Signal guide (context limit, timeout, recent completions) is actionable. Main gap: confounds token exhaustion with rate limiting — different recoveries. |
| `logical` | Well defined. "Same task checked and unchecked multiple times" is a reliable signal. |
| `structural` | Well defined. Howler self-reporting via `Status: blocked` + CONTRACT.md reference is a clear signal. |
| `environmental` | Defined but detection is reactive. The 3-Howler correlation rule is the only proactive signal. |
| `conflict` | Defined but detection depends on Howler honesty. Gold's Pax independent validation can catch post-hoc conflicts, but in-flight conflict detection is passive. |

### 1.2 Failure Modes Without a Classification

**FM-01: Token Exhaustion Mid-Howler**
Severity: HIGH
Currently lumped under `transient`. The recovery action (Resume) is the same, but the cause is different: a context-exhausted Howler may have written corrupted partial files that a resumed Howler will silently inherit. The spec says "Read HOOK.md and continue" but does not say to verify file integrity before resuming. A resumed Howler inheriting a partially written TypeScript file will fail type checks, which will be classified `logical`, triggering Orange — wasting 2 additional agent calls before the real problem (corrupt file) is identified.

Recommended addition: Before resuming from token exhaustion, Gold should verify file integrity of all CREATES/MODIFIES listed in HOOK.md (not just check that files exist via `ls`).

**FM-02: Gold Session Death Mid-Spectrum**
Severity: CRITICAL
No recovery path is documented. Gold holds the orchestration state in its own context: active DAG, locus history, per-Howler failure counts, circuit breaker state. CHECKPOINT.json records phase and Howler statuses, but it does not record:
- Which loci have already fired circuit breakers
- Active Orange assignments (Gold holds this in-context)
- The cascade plan for in-flight structural failures

If Gold dies after writing `phase: running` to CHECKPOINT.json, the next operator must manually reconstruct the DAG state by reading all HOOK.md files and debrief entries. The spec says "HOOK.md and debrief survive Howler death" but does not say who recovers Gold, or how CHECKPOINT.json is sufficient for full resume.

**FM-03: API Rate Limiting (Provider-Level)**
Severity: MEDIUM
The spec mentions rate limits as a `transient` signal, but provider-level rate limiting (429s) is systemic: every new Howler spawned in recovery will also hit the rate limit immediately. Auto-resuming a `transient` failure caused by a 429 will just burn more quota. This is structurally environmental, not transient. A 6-Howler run hitting a sustained rate limit will trigger 6 auto-resumes in rapid succession, burning 6x the retry budget before Gold notices the correlation.

**FM-04: Corrupt or Stale CHECKPOINT.json**
Severity: HIGH
No corruption recovery is documented. If CHECKPOINT.json is written mid-phase-transition and the write is interrupted (machine sleep, filesystem full), the file may be syntactically invalid JSON. Gold's recovery instructions ("read CHECKPOINT.json to resume") fail silently if the file is unparseable. The spec has no fallback for this case.

**FM-05: Howler Writes Outside Ownership Matrix (Silent)**
Severity: MEDIUM
The spec addresses this in Pax independent validation: Gold checks `git diff --name-only` against the ownership matrix. But this is a post-hoc check. If Howler A writes to a file also listed in Howler B's CREATES before Howler B runs, Howler B's worktree is unaffected (separate branches), but when both PRs are opened, the merge will conflict. The spec handles this at merge time but not at drop time. Gold cannot currently detect that Howler A is about to violate ownership while Howler A is still running.

**FM-06: HOOK.md File Lock / Write Conflict**
Severity: LOW
Multiple Howlers run in parallel. Each Howler writes to its own HOOK.md in its own worktree. There is no shared write conflict risk here. However, Gold reads HOOK.md after Howler completion — if the Howler crashes mid-write, HOOK.md may be truncated. This is an edge case but relevant for long Howlers on slow filesystems.

**FM-07: Contract Test Stub Failure (Mismatched Contract)**
Severity: MEDIUM
Gold auto-generates contract test stubs from CONTRACT.md postconditions. If Gold's extraction of postconditions is incorrect (it documents a signature that doesn't match what the Howler will actually produce), the contract test will fail on first run. The Howler is supposed to fix this in the revision pass (max 2 tries). But if the contract itself is wrong (not just the implementation), the Howler cannot fix it without filing a structural block. The revision pass loop will exhaust its 2 attempts before the Howler realizes the contract test is wrong, not the code.

---

## Part 2: Recovery Path Robustness

### 2.1 Transient Recovery

**Assessed: Adequate for true transients, fragile for token exhaustion**

The Resume path ("Read HOOK.md and continue, avoid Errors Encountered") works when HOOK.md accurately reflects progress. Risk: a Howler that hits context limits while in the middle of writing a file will have an incomplete HOOK.md — the last checkpoint entry is the one before the in-progress file write. The resumed Howler reads "step N complete" and skips re-doing it, but the actual file from step N may be partial.

Gap: No file integrity check before Resume. The spec should require resumed Howlers to run `git status` in their worktree and verify all claimed-complete files are non-empty and syntactically valid before continuing.

### 2.2 Logical Recovery (Orange Path)

**Assessed: Solid but expensive**

Orange diagnosis then Resume/Retry is well-designed. The 2-Orange-retry limit prevents runaway. The gap is timing: Orange must read full HOOK.md + the codebase context to diagnose — this is a 1-2 minute agent call for each retry. In a 6-Howler run where 3 Howlers fail `logical`, the total Orange overhead is 6 agent calls before any human sees results. This is acceptable cost but should be surfaced to the operator via CHECKPOINT.json so they can abort early if budget is constrained.

### 2.3 Structural Recovery (Re-Muster)

**Assessed: Correct but blast-radius is underspecified**

The one-for-all strategy is correct: freeze downstream dependents, fix contract, re-drop. The gap is that "freeze" is not defined operationally. In the current sub-agent model, Gold cannot cancel a running Howler mid-execution. "Freeze" effectively means: let the running Howlers complete (or fail), then do not dispatch new Howlers that depend on the failed contract. But running Howlers consuming the wrong contract will produce work that must be discarded. The spec does not say this explicitly, creating operator confusion about whether in-flight Howler work is salvageable.

Additionally, re-muster after a structural failure inherits stale ARCHITECTURE.md. The spec says "patch only changed sections" but a structural failure often means the original decomposition was wrong — the changed sections may be precisely the ones that caused the failure. Gold should be instructed to re-validate the failed Howler's codebase context specifically when re-mustering after structural.

### 2.4 Environmental Recovery

**Assessed: Weakest documented path**

"Pause all Howlers. Fix environment. Resume all." is three words for a complex operation. In the current architecture, Gold cannot pause running Howlers. Environmental failures will cause Howlers to fail, Gold will read each HOOK.md, classify each one, and potentially auto-resume some as `transient` before recognizing the pattern. The 3-Howler correlation rule is the only guardrail, and it requires 3 failures to fire. In a 4-Howler run, 3 environmental failures will trigger the correlation correctly, but the 4th Howler may be auto-resumed as `transient` before the pattern is recognized.

Gap: The correlation check should fire before auto-resuming any `transient` if 2 or more failures have already occurred within a short time window, not just when a 3rd failure occurs.

### 2.5 Conflict Recovery

**Assessed: Correct but detection is late**

Freeze-and-escalate is the right call. The problem is detection timing: conflicts are caught either by (a) a Howler discovering them while implementing and filing a block, or (b) Gold during Pax independent validation. Option (b) means conflict is detected after all Howlers complete — potentially hours into the run. The seam_check.py script in Pax catches file overlap in debrief frontmatter, but it runs post-completion.

No mechanism exists for Gold to detect an emerging conflict while Howlers are still running (other than passive reading of HOOK.md updates if Agent Teams messaging is active). In a 6-Howler run, a conflict between Howler A and Howler C may not surface until Pax, by which time Howlers D, E, F have all completed work that may depend on the conflicting interface.

### 2.6 HOOK.md Corruption

**Assessed: Unaddressed**

The spec is silent on corrupt or empty HOOK.md. If HOOK.md is corrupt, Gold reads it, cannot parse reliable signals, and must classify the failure without evidence. In practice, Gold will likely default to `transient` (the safest auto-recoverable option). But if the failure was structural, auto-resuming will re-hit the same wall.

Recommendation: If HOOK.md is empty or unparseable, Gold should default to `logical` (requires human confirmation), not `transient`.

---

## Part 3: State Durability

### 3.1 Atomicity of CHECKPOINT.json Writes

**Finding: Non-atomic, no verification**

CHECKPOINT.json is written by Gold using standard Write tool calls. No atomic write protocol (write-to-temp, rename) is specified. If Gold's session dies mid-write, the file will be partially written. The spec relies on CHECKPOINT.json for resume-from-any-point, but does not specify how to detect or recover from a corrupt checkpoint.

At minimum, Gold should write `CHECKPOINT.json.tmp` and rename, or write a `checksum` field that can be verified on read. The current spec has no such mechanism.

### 3.2 Race Conditions Between Howlers and CHECKPOINT.json

**Finding: No race condition for CHECKPOINT.json (Gold owns it exclusively)**

CHECKPOINT.json is written only by Gold. Howlers do not write to it. Howlers write to their own HOOK.md in their own worktrees. There is no structural race condition here. This is a well-designed separation.

However: if Agent Teams messaging (Phase A integration) is used and Howlers send status updates, and Gold processes multiple messages concurrently, Gold could theoretically write CHECKPOINT.json twice in rapid succession with inconsistent state. This is speculative for current architecture.

### 3.3 HOOK.md Durability

**Finding: Durable by design, no atomic write required**

Each Howler writes its own HOOK.md. No other agent writes the same file. HOOK.md is append-heavy (progress updates). The risk is mid-write truncation (same as CHECKPOINT.json), but HOOK.md is less critical: a partially written HOOK.md is recoverable because it retains earlier progress entries. The loss is the most recent status line, not the full history.

### 3.4 Machine Reboot / Filesystem Durability

**Finding: No redundancy, home directory storage only**

All spectrum state lives in `~/.claude/spectrum/<rain-id>/`. This is local filesystem with no replication. A machine reboot mid-spectrum loses:
- All in-memory Gold state (DAG, locus history, circuit breaker counters)
- Any HOOK.md updates not yet flushed to disk

What survives: CHECKPOINT.json, all written HOOK.md files, debrief entries, worktrees (git branches persisted to disk).

The recovery procedure (Gold reads CHECKPOINT.json and all HOOK.md files) is documented implicitly but not as an explicit "resume after reboot" runbook. An operator facing a post-reboot spectrum would need to manually reconstruct context that Gold held in-memory.

Recommendation: Add a `locus_history` field to CHECKPOINT.json so Gold can restore circuit breaker state without re-reading all HOOK.md files.

### 3.5 Debrief Files

**Finding: Durable but cleanup destroys history**

Debrief files (`<howler-name>.md`) survive Howler death and are read during Pax. However, Phase 6 Triumph deletes the entire spectrum directory. If Triumph fails mid-execution (after deleting debriefs but before writing LESSONS.md), the retrospective is lost. Brown is called before deletion, but the delete-then-done sequence means a partial Triumph destroys the audit trail.

Recommendation: Copy debrief files to `~/.claude/projects/<slug>/history/<rain-id>/` before deleting the spectrum directory.

---

## Part 4: Edge Cases

### 4.1 Howler Writes Outside Ownership Matrix

**What happens**: Pax catches this via `git diff --name-only` on the Howler's branch. If the violation is detected, it is flagged as a blocker in PAX-PLAN.md. The Howler must revert or Gold restructures.

**Gap**: The violation is detected post-completion. No runtime enforcement exists. A Howler that writes to an unauthorized file and passes its own quality gate (White + Gray + /diff-review) will not be caught until Pax, which occurs after all PRs are open. Reverting a file from an already-opened PR requires either forcing a commit or closing and reopening the PR. The spec says "Howler must revert or Gold restructures" but does not give Copper a procedure for reverting an already-opened PR.

### 4.2 Howler Worktree Has Merge Conflicts with Main

**What happens**: Not documented. Pre-created worktrees are based on `base_commit` from the DAG, which is a specific commit on `base_branch` (typically `staging` or `main`). If `main` advances significantly while Howlers are running (hours in a 6-Howler run), the base commit becomes stale. When Copper opens a PR, GitHub will flag conflicts.

**Gap**: No staleness check is performed between worktree creation and PR opening. For long-running spectrums, a `git fetch && git merge-base` check before Copper opens each PR would catch this. Currently, the operator discovers the conflict at PR review time.

### 4.3 No Test Framework in Project

**What happens**: Gray is told to run tests; if no test framework exists, Gray should report "no tests found" (not fail). The spec says "skip if dependencies not installed — testing defers to The Proving" — but The Proving IS Gray. If Gray is running at The Proving and there's no test framework, Gray exits with a coverage gap warning (not blocking). This is handled correctly.

**Edge case**: Gray writes missing tests as part of its mandate. If no test framework exists, Gray cannot write meaningful tests without first setting up the framework. The spec does not address whether Gray should set up test infrastructure or just skip. An operator who expects Gray to add tests to a project with no test framework will get a confusing "no tests found" result with no guidance.

### 4.4 White Flags a Blocker After PR is Already Open

**What happens**: The spec is sequential: White runs first (triple gate), then Copper opens PR. If White finds zero blockers at gate time, Copper opens the PR. White cannot flag blockers "after the PR is already open" in the normal flow — that would require White to re-run independently.

**Edge case**: White re-run is mandatory only if blockers are fixed during the quality gate. If a human reviews the PR (post-Copper) and asks White to review the diff separately, and White now finds a blocker, there is no documented procedure. The spec covers the pre-PR gate but not post-PR White review requests.

### 4.5 Nano Mode Failure

**Finding: Nano has no structural recovery path**

Nano mode skips: CONTRACT.md, Politico, ARCHITECTURE.md, Obsidian, ENTITIES.md, human approval gate, White + Gray + /diff-review, and worktree pre-creation. The only recovery path is "if any Howler blocks, upgrade to reaping mode immediately."

But escalation to reaping requires writing CONTRACT.md, ARCHITECTURE.md, and running Politico — work that takes ~3 minutes and requires reading the codebase that Gold did not analyze during nano muster. If a nano Howler blocks mid-implementation (not at the start), the codebase may have partially written files from the failed Howler in its worktree, which reaping mode's pre-created worktrees will not account for.

Nano mode's "self-verify only" without White/Gray means bugs and security issues can reach PR without any external review. For a "pure-create, obvious boundaries" task, this is acceptable. But the criteria for nano activation ("task boundaries are obvious — Gold judges without analysis") is subjective and creates pressure to misuse nano for tasks that should be reaping.

---

## Part 5: Cascading Failures

### 5.1 Howler A Fails; Howler B Waits on A's #types Checkpoint

**Scenario**: Howler A is dispatched but fails (any type) before writing `types: STABLE` to HOOK.md. Howler B has `deps: [howler-a#types]` in the DAG and is waiting for the STABLE signal.

**What happens**: Howler B is never dropped (it is pending). Gold detects Howler A's failure, classifies it, and must decide: (a) attempt recovery of A, or (b) restructure. Meanwhile Howler B sits in `status: pending` indefinitely.

**Gap**: The spec does not define a timeout for checkpoint dependency waiting. If Howler A is classified `structural` and re-muster takes 15 minutes, Howler B waits 15 minutes in pending state with no status update. For an 8-Howler run where Howler A is the critical-path types provider, all downstream Howlers (potentially 5-6) are blocked indefinitely. CHECKPOINT.json will show them as `pending`, which looks identical to "not yet dispatched" — an operator checking status cannot distinguish "waiting for recovery" from "not yet reached in the DAG."

Recommendation: Add `blocking_reason: "waiting on howler-a#types (howler-a is failed/recovering)"` to the pending Howler's CHECKPOINT.json entry.

### 5.2 Circuit Breaker Fires During a 6-Howler Run

**Scenario**: Howler A fails twice on the same locus. Circuit breaker escalates to `structural`. Gold must freeze downstream dependents and pause.

**Gap**: Gold must identify all downstream dependents transitively — not just direct deps. For a DAG like A → B → C → D, a structural failure on A freezes B, C, D. The spec says "Gold freezes all in-flight Howlers that depend (directly or transitively) on the failed Howler." But if B and C are already running (dispatched before A's second failure), they cannot be stopped. Gold must wait for them to complete (or fail), then discard their work because A's contract is wrong.

The spec does not say what to do with completed work from B and C when A is restructured. Their PRs may be open. After re-muster, B and C will be re-dropped with a new contract — potentially creating duplicate PRs for the same task. Copper is not given instructions for closing the old PRs before opening new ones.

### 5.3 Worst-Case Token Burn

**Scenario**: 8-Howler run, Howler A fails twice on the same locus (structural), Gold fires circuit breaker. Gold re-musters. Re-mustered Howler A fails again (contract still wrong). Gold fires circuit breaker again (2nd structural failure). Escalated to human. Human restructures into 6-Howler run. Meanwhile, 7 other Howlers have been running or waiting, accumulating token spend.

**Worst-case estimate (qualitative)**:
- Muster 1: ~8 min, high token cost
- 8 Howlers running: 8 × Howler cost
- Howler A fails ×2, Orange diagnoses ×2: +2 Orange calls
- Re-muster: additional Gold cost
- Howler A fails ×2 again: +2 more Orange calls
- Human restructure: new muster
- B, C, D, E, F, G, H may have completed — their work may be discarded or retained depending on restructure

**Gap**: No cost checkpoint fires between Muster 1 and the second structural failure. `budget_limit` in CHECKPOINT.json is checked "before each Howler drop" but not before Orange dispatches or re-muster. A budget-capped spectrum can exceed its limit between Howler drops. Orange calls are not counted in `per_howler` cost tracking.

---

## Part 6: Failure Mode Catalog with Severity Ratings

| ID | Failure Mode | Severity | Recovery Documented? |
|----|-------------|----------|---------------------|
| FM-01 | Token exhaustion inheriting corrupt partial files on Resume | HIGH | Partial — Resume path exists but no file integrity check |
| FM-02 | Gold session death mid-spectrum | CRITICAL | No — CHECKPOINT.json insufficient for full resume |
| FM-03 | API rate limiting treated as transient, auto-resume loop | MEDIUM | No — classified transient, no rate-limit detection |
| FM-04 | Corrupt CHECKPOINT.json on reboot/crash | HIGH | No — no fallback documented |
| FM-05 | Ownership violation undetected until Pax (post-PR) | MEDIUM | Partial — caught in Pax but no PR rollback procedure |
| FM-06 | HOOK.md truncated mid-write | LOW | No — Gold defaults to transient (should be logical) |
| FM-07 | Contract test stubs wrong (contract error, not impl error) | MEDIUM | Partial — revision pass exhausted before structural block filed |
| FM-08 | types#checkpoint never posted (Howler A dies before STABLE) | HIGH | No — B waits indefinitely, no timeout or blocking_reason |
| FM-09 | B, C complete while A is being re-mustered; duplicate PRs | MEDIUM | No — Copper has no close-old-PR instruction |
| FM-10 | Nano mode misused for non-pure-create tasks | HIGH | Partial — escalation to reaping exists but no validation at activation |
| FM-11 | Reboot destroys in-memory Gold state (DAG, locus history) | HIGH | No — no locus_history in CHECKPOINT.json |
| FM-12 | Rate limit on 3+ simultaneous Howler spawns | MEDIUM | No — no stagger/backoff on drop |
| FM-13 | Triumph partial execution deletes debriefs before LESSONS.md written | MEDIUM | No — no backup of debriefs before delete |
| FM-14 | Worktree staleness (base_commit stale when PR opened) | LOW | No — no staleness check before PR creation |
| FM-15 | Environmental failure auto-resumed before 3-Howler correlation fires | MEDIUM | Partial — 3-Howler rule helps but fires too late |

---

## Part 7: Circuit Breaker Analysis

### Is 2 the right threshold?

**Context**: Circuit breaker fires after 2 failures on the same locus. This converts auto-recoverable `transient` into `structural`, requiring human confirmation.

**Too aggressive for**: Fast-transient errors (temporary network partition, model overload spike). Two rapid 429 errors on the same file will fire the circuit breaker even though a 60-second backoff would resolve the issue. A Howler that hits two context limit errors (a long file, not a structural problem) on the same locus also fires the breaker.

**Too lenient for**: Slow logical failures where a Howler tries a different approach on the third attempt but is still fundamentally wrong. The circuit breaker only fires if the same locus appears twice — a Howler that cycles across multiple different files will never trip it.

**Recommendation**: Threshold of 2 is broadly correct for structural detection, but needs a `transient_window` concept: if both failures occurred within 5 minutes and are identical error types (e.g., both 429s, both context limits), treat as a single failure event rather than incrementing the locus counter. This prevents false circuit-breaker trips on fast-transient bursts while preserving the protection against repeated structural failure.

### Locus Tracking Completeness

The locus concept is well-designed. Tracking by file path is appropriate. Weakness: test identifiers as loci are mentioned ("same file path or same test identifier") but the spec does not show how Gold extracts test identifiers from HOOK.md `Errors Encountered` free text. This is manual and prone to Gold misreading test output.

---

## Top 10 Resilience Recommendations

**R-01 (CRITICAL): Document Gold recovery as an explicit runbook**
Gold session death is the highest-severity gap. Add to SPECTRUM-OPS.md: "If Gold dies mid-spectrum, the human operator reads CHECKPOINT.json to determine current phase, reads all HOOK.md files to reconstruct Howler states, and re-drops Gold with a prompt including the full CHECKPOINT.json and a summary of active HOOK.md files." Persist locus history in CHECKPOINT.json so circuit breaker state survives Gold death.

**R-02 (HIGH): Add locus_history to CHECKPOINT.json schema**
Current schema has no field for locus failure counts. Gold reconstructing from CHECKPOINT.json after a crash cannot restore circuit breaker state. Add:
```json
"locus_history": {
  "src/middleware/auth.ts": 1,
  "src/types/auth.ts": 2
}
```
Updated by Gold after each failure classification.

**R-03 (HIGH): File integrity check before Resume from token exhaustion**
When resuming a Howler after context limit (token exhaustion), Gold should run `git status` in the Howler's worktree and check for zero-byte or syntactically invalid files in the ownership list. If corrupt files are found, classify as `structural` rather than resuming.

**R-04 (HIGH): Add blocking_reason to pending Howler entries in CHECKPOINT.json**
When a pending Howler cannot be dispatched because a dependency is failing or recovering, set `"blocking_reason": "waiting on howler-a#types (howler-a: structural recovery in progress)"`. This allows operators to distinguish "not yet dispatched" from "blocked by failure cascade."

**R-05 (HIGH): Define atomic write protocol for CHECKPOINT.json**
Specify: Gold writes to `CHECKPOINT.json.tmp`, verifies the JSON is valid, then renames to `CHECKPOINT.json`. On read, if `CHECKPOINT.json` is unparseable, attempt to read `CHECKPOINT.json.tmp` as fallback. This prevents a crashed mid-write from destroying checkpoint state.

**R-06 (MEDIUM): Rate limit detection before auto-resume**
Before auto-resuming a `transient` failure, check if the error message contains rate-limit indicators (429, "rate limit exceeded", "quota exceeded"). If so, classify as `environmental` (requires human confirmation) rather than auto-resuming. Prevents cascade of auto-resumes that burn quota without making progress.

**R-07 (MEDIUM): Environmental correlation window tightened**
Change the 3-Howler correlation rule to: "if 2 or more failures occur within 10 minutes AND error messages share structural similarity, escalate to `environmental` before auto-resuming any individual failure." This prevents the current gap where the first 2 environmental failures are auto-resumed as `transient` before the 3rd fires the correlation check.

**R-08 (MEDIUM): Backup debriefs before Triumph deletion**
In Phase 6 Triumph, before deleting the spectrum directory, copy all `<howler-name>.md` debrief files to `~/.claude/projects/<slug>/history/<rain-id>/`. This ensures that if Triumph's LESSONS.md write fails, the audit trail is not lost. Cost: negligible (small markdown files).

**R-09 (MEDIUM): Add staleness check before Copper opens PR**
Before Copper opens each PR, Gold (or Copper) runs `git merge-base --is-ancestor <base_commit> origin/<base_branch>` to verify the worktree's base is still reachable from the current base branch. If the base is stale (main has advanced significantly), flag to operator before opening the PR.

**R-10 (MEDIUM): Harden nano mode activation criteria**
Nano mode currently requires "task boundaries are obvious — human or Gold judges without analysis." Add a mechanical check: Gold must verify (a) all planned files have extensions consistent with pure-create (not modifying existing files), and (b) no planned file path matches any existing file in the repository. If either check fails, escalate to reaping mode automatically rather than relying on judgment.

---

## Appendix: Classification Signal Reliability Assessment

| Signal | Reliability | Notes |
|--------|-------------|-------|
| `Status: in_progress` + recent completions + timeout → transient | HIGH | Reliable. Howlers update status frequently. |
| Same task checked/unchecked multiple times → logical | HIGH | Reliable but requires HOOK.md to be intact. |
| `Status: blocked` + CONTRACT.md reference → structural | HIGH | Reliable. Howlers are instructed to file this explicitly. |
| 3+ Howlers with similar errors → environmental | MEDIUM | Requires Gold to compare error messages across HOOK.md files. Similarity is subjective. |
| Interface divergence described in HOOK.md → conflict | LOW | Requires Howler to proactively recognize and report the conflict. Easy to miss if the Howler doesn't yet know what the other Howler built. |
| Empty/corrupt HOOK.md → unknown | NOT ADDRESSED | Gold has no documented default for this case. |

The taxonomy's main weakness is that it relies on Howlers accurately self-reporting their situation in HOOK.md. A Howler that does not understand why it is failing (e.g., a subtle contract error that manifests as a type error) will write `Errors Encountered` entries that point to a symptom rather than the cause. Gold will classify based on the symptom (type error → logical) rather than the cause (contract error → structural), selecting the wrong recovery path.

This is partially mitigated by the circuit breaker (2 logical failures on the same locus → structural), but the mitigation requires burning 2 attempts first.
