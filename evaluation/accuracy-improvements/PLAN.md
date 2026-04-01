# Accuracy Improvements — Implementation Plan

**Date**: 2026-03-31
**Author**: Blue (Sonnet planner)
**Source research**: `/Users/ryan/spectrum-protocol/evaluation/accuracy-research/ACCURACY-REPORT.md`
**Scope**: 4 pre-SWE-bench accuracy improvements, all implementable now

---

## Overview

These 4 improvements address known accuracy gaps identified in the research report. They are all
additive prompt/protocol changes — no architectural surgery required. All 4 are **independent** and
can be implemented in parallel by 4 Howlers.

| Improvement | Source | Type | Effort | D3 Impact |
|---|---|---|---|---|
| I1: Issue Re-Read (Reflexion) | P3 | Prompt change | 1–2 hrs | +0.3–0.5 |
| I2: Test Dependency Maps | P2 | New tool + template | 4–6 hrs | +0.5–1.0 |
| I3: Codebase Context Injection | P4 | Muster protocol change | 3–5 hrs | +0.5–1.0 |
| I4: White Pre-Check | P5 | New muster step + prompt | 3–4 hrs | +0.3–0.5 |

**Total effort**: ~11–17 hours across 4 parallel Howlers, or ~4–6 hours wall-clock in parallel.

**Dependency**: None between I1–I4. All are safe to implement simultaneously. I2 has a sub-
dependency (write the Python tool first, then add the template reference — both in the same Howler).

---

## I1: Issue Re-Read (Reflexion)

**What**: Add a mandatory re-read step after mechanical completion verification. The Howler
re-reads the original task statement and writes a 3–5 line self-assessment: "Does my implementation
actually resolve the stated problem?" If it finds a gap, it fixes before proceeding to quality gates.

**Research basis**: Reflexion achieves 91% on HumanEval vs 80% baseline. The key: self-reflection
on correctness, not just compliance. Spectrum's existing alignment checks are compliance-focused
("am I touching the right files?"). This adds a correctness-focused check.

### Files to Change

**File 1**: `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md`
- Section: `### Howler Drop Template` (lines 289–350)
- Change type: Prompt text addition
- Where: After instruction `8. COMPLETION VERIFICATION` block (after the line ending `Write
  verification results in HOOK.md under '## Completion Verification'.`), before instruction `9.`
- Add this block (renumber subsequent instructions +1):

```
  8b. ISSUE RE-READ: After mechanical verification, re-read the original Task
      above (not just the file list — the full task description). Write a 3–5
      line assessment in HOOK.md under '## Issue Re-Read':
        - "Does my implementation resolve the stated problem end-to-end?"
        - "What edge cases does the task imply that I may not have handled?"
        - "Is there anything in the task description I deprioritized?"
      If you identify a gap, fix it before moving to step 9 (quality gates).
      If no gaps: write "Issue re-read: no gaps identified." and proceed.
```

**File 2**: `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md`
- Section: `### HOOK.md Template` (lines 352–401)
- Change type: Add new section to template
- Where: After `## Completion Verification` section, before `## Blockers`
- Add:

```markdown
## Issue Re-Read
- [ ] Re-read original task
- Assessment: {3-5 line correctness assessment or "no gaps identified"}
```

**File 3**: `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md`
- Section: `## Safety Rails` → `**Howler Constraints:**`
- Change type: Add one bullet
- Add after "Completion verification is mechanical..." bullet:

```
- Issue re-read mandatory after completion verification — correctness assessment before quality gates
```

**File 4**: `/Users/ryan/spectrum-protocol/spectrum/CLAUDE.md`
- Section: `### Phase 2 — The Drop` → `**Howler execution rules**`
- Change type: Add one rule
- Add after "Completion verification" bullet:

```
- **Issue re-read**: After completion verification, Howler re-reads the original task and writes a
  3–5 line correctness assessment in HOOK.md. If a gap is found, fix before quality gates.
```

**Effort**: 1–2 hours. Four text additions across 2 files. No logic changes.

---

## I2: Test Dependency Maps

**What**: Before dropping a Howler, Gold generates a test impact map — which test files cover
which source files. Include this in the Howler drop template as a `## Test Impact Map` section.
Howlers run these specific tests during completion verification instead of "run all tests."

**Research basis**: TDAD (arxiv 2603.17973) showed 70% regression reduction by providing
*contextual* test information (which tests to run) vs. procedural mandates (write tests first).
The key: the agent needs to *know* which tests are relevant, not be told to write tests.

### Files to Change

**File 1 (new tool)**: `/Users/ryan/spectrum-protocol/tools/test_impact_map.py`
- Change type: New file (tool)
- Purpose: Given a list of source files, return the test files that exercise them via import
  tracing and naming convention matching.
- Interface:
  ```
  python3 test_impact_map.py --files src/auth/login.ts src/auth/session.ts --root .
  ```
  Output (stdout):
  ```
  ## Test Impact Map
  src/auth/login.ts → tests/auth/login.test.ts, tests/integration/auth.test.ts
  src/auth/session.ts → tests/auth/session.test.ts
  Total: 3 test files to verify
  ```
- Logic:
  1. For each source file, look for a corresponding test file by naming convention:
     `foo.ts` → `foo.test.ts`, `foo.spec.ts`, `__tests__/foo.ts` (same basename, both directions)
  2. For Python: `foo.py` → `test_foo.py`, `tests/test_foo.py`
  3. For files with no direct match: scan test files for `import` statements referencing the
     source file path or module name (AST-free: grep for the basename)
  4. Deduplicate and sort results
  5. Print the `## Test Impact Map` block to stdout (ready to paste into CONTRACT.md)
  6. Exit 0 even if no test files found (no-test projects should not fail the map)

**File 2**: `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md`
- Section: `## Phase 1: Muster (Gold)` — the muster checklist at the end
- Change type: Add one checklist item
- Where: After `- [ ] LESSONS.md + ENTITIES.md incorporated` and before the Politico item
- Add:

```
- [ ] Test impact map generated for each Howler's MODIFIES/CREATES files (run tools/test_impact_map.py; include output in CONTRACT.md per Howler)
```

**File 3**: `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md`
- Section: `### Howler Drop Template` — instruction 8 COMPLETION VERIFICATION block
- Change type: Edit existing verification step
- Where: The line `- For tests (if test framework installed): test runner passes on your files`
- Replace with:

```
     - For tests (if test framework installed): run the specific test files listed in your
       ## Test Impact Map (from CONTRACT.md). If no map was provided, run tests on your owned
       files. Tests must pass; coverage gaps are warnings, not blockers.
```

**File 4**: `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md`
- Section: `## Phase 1: Muster (Gold)` — step 10 (Write CONTRACT.md)
- Change type: Add one sentence to the CONTRACT.md content description
- Where: After "Preconditions, postconditions, and invariants per Howler" bullet
- Add:

```
   - Test impact map per Howler: output of `python3 tools/test_impact_map.py --files {MODIFIES+CREATES} --root {project_root}` — which test files cover the Howler's owned files
```

**File 5**: `/Users/ryan/spectrum-protocol/spectrum/CLAUDE.md`
- Section: `### Phase 1 — Muster (Gold)` → step 9 (Write CONTRACT.md)
- Change type: Add one bullet to CONTRACT.md content list
- Add after invariants bullet:

```
   - Test impact map per Howler (run `tools/test_impact_map.py`; include in CONTRACT.md)
```

**Effort**: 4–6 hours. The Python tool is the main work (~100–150 lines). Template changes are small.

**Notes**:
- The tool lives at `/Users/ryan/spectrum-protocol/tools/test_impact_map.py` matching the
  existing `seam_check.py` location.
- Gold runs the tool during muster, not Howlers. Howlers only *consume* the map.
- For projects with no test framework: tool outputs an empty map; Howlers skip the map-based step.
- Reaping mode and nano mode: skip the test impact map (overhead not justified for pure-create runs).

---

## I3: Codebase Context Injection

**What**: During muster, Gold reads the actual content of each file in a Howler's MODIFIES list
and writes a structured `## Codebase Context` section in CONTRACT.md for that Howler. This gives
Howlers pre-digested context about existing code patterns, function signatures, and naming
conventions — not just file paths.

**Research basis**: Augment Code's 70.6% SWE-bench score is primarily attributable to its Context
Engine (semantic codebase indexing). Spectrum's ARCHITECTURE.md provides structural context but is
Gold-authored and high-level. Howlers currently read file paths and then have to discover patterns
themselves. Pre-digesting key patterns into CONTRACT.md closes part of the context gap.

**Scope boundary**: This is NOT full semantic indexing. It's Gold reading 3–10 files and
summarizing. Each summary is 5–15 lines. Total CONTRACT.md overhead: ~100–200 tokens per Howler.

### Files to Change

**File 1**: `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md`
- Section: `## Phase 1: Muster (Gold)` — step 10 (Write CONTRACT.md content)
- Change type: Add one bullet to CONTRACT.md content description
- Where: After "Naming conventions and patterns Howlers must follow" bullet
- Add:

```
   - Per-Howler `## Codebase Context` section: Gold reads each file in the Howler's MODIFIES list and summarizes: existing function signatures relevant to the task, patterns in use (e.g., "uses factory pattern", "all exports are named, not default"), and any gotchas observed (e.g., "this file has a circular import with X — avoid touching the import block"). Keep summaries to 5–15 lines per file. Skip for files being newly CREATED.
```

**File 2**: `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md`
- Section: `## Phase 1: Muster (Gold)` — muster checklist
- Change type: Add one checklist item
- Where: After the test impact map checklist item (added in I2)
- Add:

```
- [ ] Codebase context sections written in CONTRACT.md for each Howler's MODIFIES files (existing function signatures, patterns, gotchas — 5-15 lines per file)
```

**File 3**: `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md`
- Section: `### Howler Drop Template` — the CONTRACT reference instruction (instruction 0)
- Change type: Edit existing instruction
- Where: Instruction `0. Read CONTRACT.md at the path above FIRST. This is your source of truth.`
- Replace with:

```
  0. Read CONTRACT.md at the path above FIRST. Pay special attention to:
     - Your per-Howler `## Codebase Context` section (existing patterns you must follow)
     - Your preconditions/postconditions
     - Shared types and interfaces
     This is your source of truth. Do not re-derive patterns from the codebase if CONTRACT.md
     has already captured them — use what Gold documented.
```

**File 4**: `/Users/ryan/spectrum-protocol/spectrum/CLAUDE.md`
- Section: `### Phase 1 — Muster (Gold)` → step 9 (Write CONTRACT.md)
- Change type: Add one bullet
- Add after naming conventions bullet:

```
   - Per-Howler codebase context: Gold reads each MODIFIES file and summarizes key patterns,
     function signatures, and gotchas (5–15 lines per file; skip for newly CREATED files)
```

**Effort**: 3–5 hours. Entirely prompt/documentation changes — no code. The effort is in writing
clear instructions that prevent Gold from over-generating (common failure mode: Gold reads 20 files
and writes 2000-token summaries instead of focused 5–15 line summaries).

**Notes**:
- For reaping mode and nano mode: skip codebase context (pure-create Howlers have no MODIFIES files).
- If a Howler's MODIFIES list is empty (all CREATES): Gold writes `## Codebase Context: N/A (all new files)`.
- Gold does NOT read files it doesn't own during muster — but reading files to *document* them for
  Howlers is explicitly within Gold's muster responsibilities (Gold does not *write* source, but
  reading and summarizing is planning work, not implementation).

---

## I4: White Pre-Check

**What**: After Gold writes CONTRACT.md but before freezing it, run a lightweight White review
against the actual codebase. White checks: do referenced files exist? do the function signatures
Gold documented in CONTRACT.md match the real code? are there any obvious stale assumptions? Gold
patches CONTRACT.md based on White's findings before freezing.

**Research basis**: MAST taxonomy shows specification errors are a top-3 failure category in
multi-agent systems. Politico (Phase 1.5) reviews CONTRACT.md adversarially but *in isolation* —
it doesn't compare the contract against the codebase. White Pre-Check fills this gap: it validates
the contract's *factual claims* about the codebase, not just internal consistency.

**Distinction from existing Politico**:
- Politico: adversarial review of decomposition logic and interface consistency (contract vs. contract)
- White Pre-Check: factual accuracy review (contract vs. codebase)

### Files to Change

**File 1**: `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md`
- Section: `## Phase 1: Muster (Gold)` — between step 10 (CONTRACT.md) and step 11 (convoy-contracts.d.ts)
- Change type: Insert new step (renumber steps 11–14 → 12–15; current step 12 The Passage becomes 13)
- Insert as new step 11:

```
11. **Pre-freeze contract check (White Pre-Check)** — after writing CONTRACT.md, before freezing
    it, drop a White with this prompt:
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
    **Skip for reaping mode and nano mode.**
```

**File 2**: `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md`
- Section: `## Phase 1: Muster (Gold)` — muster checklist
- Change type: Add one checklist item
- Where: After "Zero overlapping CREATES/MODIFIES" and before "Every Howler has effort/risk tags"
- Add:

```
- [ ] White Pre-Check completed — all STALE/MISSING/MISMATCH findings patched or documented as ASSUMPTION in CONTRACT.md
```

**File 3**: `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md`
- Section: `## Phase 1: Muster (Gold)` — Phase 1.5 / The Passage step description
- Change type: Clarify distinction with White Pre-Check in the existing Politico prompt
- Where: The existing Politico prompt block (step now numbered 13 after renumbering)
- Add one sentence before the closing `"` of the Politico prompt:

```
    Note: the White Pre-Check (step 11) has already validated factual accuracy of CONTRACT.md
    against the codebase. Your role is adversarial review of the *decomposition logic and
    interface design*, not re-checking file existence.
```

**File 4**: `/Users/ryan/spectrum-protocol/spectrum/CLAUDE.md`
- Section: `### Phase 1 — Muster (Gold)` — the ordered list
- Change type: Insert new step between step 9 (CONTRACT.md) and step 10 (convoy-contracts.d.ts)
- Insert as new step 10 (renumber existing 10–15 → 11–16):

```
10. **White Pre-Check** — after writing CONTRACT.md, before freezing: drop White to verify all
    referenced files exist and documented signatures match the actual codebase. Gold patches
    CONTRACT.md based on findings. Skip for reaping mode and nano mode.
```

**Effort**: 3–4 hours. No new tools. White already exists. The work is: writing the White Pre-Check
prompt text precisely enough that White doesn't hallucinate issues (common failure: White reviews
CREATES files and flags them as MISSING — must explicitly exclude them).

**Notes**:
- White Pre-Check runs *before* Politico (step 11 vs. step 13). This is intentional: Politico
  should review a contract that is already factually accurate.
- For reaping/nano modes: skip. The overhead is not justified for pure-create runs where there
  are no MODIFIES files to verify.
- This step adds ~2–4 minutes to muster. That's acceptable for full-mode Spectrums where muster
  is already ~8 minutes.
- Cost: one White invocation per Spectrum run. At Sonnet rates, negligible.

---

## Dependency Graph

```
I1 (Issue Re-Read)       ──── independent ────► can drop immediately
I2 (Test Dependency Map) ──── independent ────► can drop immediately
I3 (Context Injection)   ──── independent ────► can drop immediately
I4 (White Pre-Check)     ──── independent ────► can drop immediately
```

All 4 improvements touch different parts of the protocol. No shared files modified by more than
one improvement (verified below).

### File Ownership Matrix

| File | I1 | I2 | I3 | I4 |
|------|----|----|----|-----|
| `spectrum/SPECTRUM-OPS.md` — Howler Drop Template | MODIFIES | MODIFIES | MODIFIES | — |
| `spectrum/SPECTRUM-OPS.md` — HOOK.md Template | MODIFIES | — | — | — |
| `spectrum/SPECTRUM-OPS.md` — Safety Rails | MODIFIES | — | — | — |
| `spectrum/SPECTRUM-OPS.md` — Muster step 10 (CONTRACT.md) | — | MODIFIES | MODIFIES | — |
| `spectrum/SPECTRUM-OPS.md` — Muster checklist | — | MODIFIES | MODIFIES | MODIFIES |
| `spectrum/SPECTRUM-OPS.md` — New muster step 11 (Pre-Check) | — | — | — | MODIFIES |
| `spectrum/SPECTRUM-OPS.md` — Politico prompt | — | — | — | MODIFIES |
| `spectrum/CLAUDE.md` — Howler execution rules | MODIFIES | MODIFIES | — | — |
| `spectrum/CLAUDE.md` — Muster step 9 (CONTRACT.md) | — | MODIFIES | MODIFIES | — |
| `spectrum/CLAUDE.md` — New muster step 10 (Pre-Check) | — | — | — | MODIFIES |
| `tools/test_impact_map.py` | — | CREATES | — | — |

**Conflict check**: SPECTRUM-OPS.md is the most-touched file. Each improvement modifies a
*different section* — but because all 4 Howlers will be in the same file, there is a coordination
risk. Two options:

**Option A (recommended)**: Assign all SPECTRUM-OPS.md edits to one Howler per improvement,
but make the edits non-overlapping by section. Gold pre-checks by explicitly listing the line
ranges each Howler will touch and verifying no overlap before drop.

**Option B**: Serialize improvements 1–4 against SPECTRUM-OPS.md (each Howler waits for the
prior to PR-merge before starting). This adds latency but eliminates merge conflict risk.

**Recommended approach**: Use Option A with explicit line-range ownership tracked in MANIFEST.md.
SPECTRUM-OPS.md has well-separated sections. The Howler Drop Template (I1, I2, I3), HOOK.md
Template (I1 only), Safety Rails (I1 only), Muster steps (I2, I3, I4), and Muster checklist
(I2, I3, I4) are all in distinct non-overlapping regions.

---

## Acceptance Criteria

### I1 — Issue Re-Read

- [ ] `## Issue Re-Read` section exists in HOOK.md template in SPECTRUM-OPS.md
- [ ] Instruction `8b` (or equivalent) exists in Howler Drop Template after completion verification
- [ ] The instruction explicitly requires a correctness assessment, not just "am I on track?"
- [ ] Safety Rails section lists issue re-read as a mandatory Howler constraint
- [ ] CLAUDE.md Howler execution rules include the issue re-read step

### I2 — Test Dependency Maps

- [ ] `tools/test_impact_map.py` exists and handles: direct naming conventions (test_foo.py,
  foo.test.ts), import-based discovery (grep for basename in test files), empty results (no-test
  projects), and Python + TypeScript/JavaScript projects
- [ ] Tool outputs a `## Test Impact Map` block directly pasteable into CONTRACT.md
- [ ] Muster checklist in SPECTRUM-OPS.md includes test impact map generation step
- [ ] CONTRACT.md content description in SPECTRUM-OPS.md includes test impact map per Howler
- [ ] Howler Drop Template instruction 8 (completion verification) references the test impact map
  from CONTRACT.md for which tests to run

### I3 — Codebase Context Injection

- [ ] CONTRACT.md content description in SPECTRUM-OPS.md includes per-Howler `## Codebase Context`
  section with scope limit (5–15 lines per file)
- [ ] Muster checklist includes codebase context generation
- [ ] Howler Drop Template instruction 0 directs Howlers to pay special attention to the Codebase
  Context section
- [ ] CLAUDE.md muster step 9 mentions the codebase context requirement
- [ ] Pure-create (CREATES only) Howlers are explicitly exempted: `N/A (all new files)` is valid

### I4 — White Pre-Check

- [ ] New step exists in SPECTRUM-OPS.md Phase 1 muster sequence between CONTRACT.md and
  convoy-contracts.d.ts
- [ ] White Pre-Check prompt explicitly excludes CREATES files from the "MISSING" check
- [ ] White Pre-Check runs before Politico (factual accuracy → adversarial logic review)
- [ ] Politico prompt notes that White Pre-Check has already handled factual verification
- [ ] Muster checklist includes White Pre-Check completion gate
- [ ] CLAUDE.md muster step list includes the Pre-Check
- [ ] Reaping mode and nano mode explicitly skip White Pre-Check

---

## What This Does NOT Include

These are explicitly out of scope for this plan:

- **SWE-bench evaluation setup** (P1 from research) — separate effort, requires Docker + evaluation
  harness, comes after these improvements are in place
- **Pattern Library from LESSONS.md** (P7) — Brown/Gold work, different pipeline stage
- **Multi-file Coordination Benchmark** (P6) — separate evaluation project
- **Full semantic codebase indexing** (the Augment Code Context Engine gap) — I3 is a
  partial close; full indexing would require a new tool with AST analysis

---

## Recommended Execution

Run as a Spectrum (4 Howlers, full mode) since all 4 improvements share SPECTRUM-OPS.md.

1. **Blue → PLAN.md**: this document
2. **Gold muster**: generate rain ID, decompose 4 Howlers, assign non-overlapping line ranges in
   SPECTRUM-OPS.md to each Howler, write CONTRACT.md with exact section/line ownership
3. **Drop 4 Howlers in parallel**: I1, I2, I3, I4
4. **Proving** (White + Gray + /diff-review per Howler)
5. **Pax + merge in line-range order** (if merging sequentially: I1 first since it changes the
   earliest sections; then I2; then I3; then I4 — this minimizes rebase conflicts)

Total wall-clock: ~4–6 hours for 4 parallel Howlers + ~30 minutes for muster + ~30 minutes for
Pax and merge.
