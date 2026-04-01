# Pipeline Design: Spectrum → SWE-bench Mapping

**Spectrum**: swe-bench-prep-0401
**Howler**: H3 — Pipeline Mapping Architect
**Date**: 2026-03-31
**Status**: Final (H3#types STABLE)

---

## Overview

SWE-bench Pro tasks are single-issue GitHub fixes averaging 4.1 files changed and 107.4 lines
per solution. They are structurally unlike the 5-8 Howler multi-file features Spectrum was
designed for. This document answers the fundamental question: **how do you run a coordination
protocol on tasks that don't need coordination?**

The answer is three variants of varying overhead, designed to isolate what Spectrum's individual
components contribute to accuracy when coordination parallelism is not the primary value driver.

---

## Variant A — Full Spectrum

**When to use**: Multi-file SWE-bench Pro tasks (4+ files changed, complex behavioral change,
task description requires disambiguating scope). Roughly 25-30% of Pro tasks by file count.

**Core insight**: On single-issue tasks, Gold does not decompose across Howlers. Instead, Gold
acts as a **structured context builder**: it reads the issue, reads the relevant codebase files,
and distills structured context (affected files, expected behavior, test targets, codebase
patterns) into a mini-CONTRACT.md. The Howler receives richer, verified context than it would
from the raw issue text alone.

### Step-by-Step Pipeline

**Step A1 — Gold: Issue Ingestion and Scope Analysis** (~5 min)

Input to Gold:
- SWE-bench task: issue text, repo identifier, failing test names, base commit hash
- SPECTRUM-OPS.md (muster reference)

Gold actions:
1. Read the GitHub issue text and the failing test file(s)
2. Identify which source files are implicated (use the failing test imports and stack traces)
3. Read each implicated source file (typically 3-6 files for a Pro task)
4. Check that the referenced files actually exist at the base commit (catches harness environment
   discrepancies before the Howler starts)
5. Generate test dependency map: which test files exercise the implicated source files
   (equivalent to `test_impact_map.py` output — derived by reading test imports)

Output: mini-CONTRACT.md (structure below)

*Token estimate (Gold)*:
- Input: ~18,000 tokens (issue text ~500, SPECTRUM-OPS.md muster excerpt ~3,000, source file reads
  ~12,000 across 4-6 files at ~2,000 each, failing test files ~2,500)
- Output: ~2,500 tokens (mini-CONTRACT.md)
- Total: ~20,500 tokens at Sonnet rates = ~$0.09

**Step A2 — White Pre-Check** (~3 min, parallel with A1's final write)

White reads the mini-CONTRACT.md and verifies:
- All files listed in MODIFIES actually exist in the repo at the base commit
- All function signatures documented in Codebase Context match what's actually in those files
- All referenced test names are real (no hallucinated test identifiers)

Gold patches mini-CONTRACT.md for any STALE/MISSING/MISMATCH findings before dropping Howler.

*Token estimate (White Pre-Check)*:
- Input: ~8,000 tokens (mini-CONTRACT.md ~2,000, implicated source files ~6,000)
- Output: ~800 tokens (findings report — typically brief on a well-scoped mini-CONTRACT.md)
- Total: ~8,800 tokens at Sonnet rates = ~$0.04

**Step A3 — Howler: Implementation** (~15-25 min)

Howler receives (via drop prompt):
- SWE-bench task issue text (verbatim)
- mini-CONTRACT.md contents (inlined — small enough to inline at ~2,500 tokens)
- Failing test names and test file paths
- Instructions: implement the fix, run the failing tests, verify behavior

Accuracy improvements active in this step:
- **I1 (Issue Re-Read)**: After completion verification, Howler re-reads the issue and writes
  a 3-5 line assessment of whether the patch resolves the stated problem
- **I2 (Test Dependency Maps)**: Howler runs the specific tests listed in mini-CONTRACT.md's
  test map, not a broad test suite
- **I3 (Codebase Context)**: mini-CONTRACT.md provides per-file context (function signatures,
  patterns, gotchas) — Howler uses this rather than re-deriving patterns from scratch
- **I6 (Revision Pass)**: If tests fail after initial implementation, Howler does up to 2
  revision passes using test output as feedback

*Token estimate (Howler)*:
- Input at dispatch: ~15,000 tokens (HOWLER-OPS.md ~2,500, mini-CONTRACT.md ~2,500,
  drop prompt + task brief ~3,000, source files read during implementation ~7,000)
- Effective billed input (session accumulation): ~60,000 tokens (median Pro task —
  shorter than a typical Spectrum Howler session because scope is single-issue, not multi-feature)
- Output: ~8,000 tokens (implementation + HOOK.md + verification notes)
- Total: ~68,000 tokens at Sonnet rates = ~$0.32

**Step A4 — Triple Quality Gate** (~8 min, all parallel)

White + Gray + /diff-review run in parallel.

- White reviews the implementation diff for logical correctness and contract compliance
- Gray runs the failing tests (those provided by the harness) and reports pass/fail
- /diff-review checks for security issues (usually low-signal on algorithmic fixes, but required)

If blockers found, Howler fixes and White re-runs before patch extraction.

*Token estimate (triple gate)*:
- White: ~10,000 input, ~1,500 output = ~$0.05
- Gray: ~8,000 input, ~2,000 output = ~$0.04 (test output + source context)
- /diff-review: ~6,000 input, ~800 output = ~$0.02
- Total: ~28,300 tokens = ~$0.11

**Step A5 — Copper: Patch Extraction and Submission** (~1 min)

Copper runs `git diff` against the base commit to produce a unified diff patch.
Submits to SWE-bench harness (via `sb-cli apply-patch` or equivalent).

*Token estimate (Copper)*:
- Input: ~1,500 tokens, Output: ~300 tokens = negligible (~$0.003)

### Variant A Total Token Estimate

| Step | Agent | Input (K) | Output (K) | Cost |
|------|-------|-----------|------------|------|
| A1: Issue ingestion + mini-CONTRACT | Gold (Sonnet) | 18.0 | 2.5 | $0.09 |
| A2: White Pre-Check | White (Sonnet) | 8.0 | 0.8 | $0.04 |
| A3: Howler implementation | Howler (Sonnet) | 60.0 | 8.0 | $0.32 |
| A4: Triple gate (White+Gray+/diff-review) | Sonnet x3 | 24.0 | 4.3 | $0.11 |
| A5: Patch extraction | Copper (Haiku) | 1.5 | 0.3 | $0.003 |
| **Total (happy path)** | | **111.5K** | **15.9K** | **~$0.57** |

*Overhead ratio vs. Variant C (bare Sonnet)*: ~2.0–2.5x wall-clock (Gold muster ~8 min +
White Pre-Check ~3 min + triple gate ~8 min = ~19 min overhead on top of ~20 min Howler work)

### mini-CONTRACT.md Structure for SWE-bench

```markdown
# mini-CONTRACT.md: <repo>/<issue-id>
Base commit: <hash>
Generated by: Gold (Spectrum swe-bench adapter)

## Issue Summary
<2-3 sentence distillation of the bug or requested behavior change>

## Affected Files (MODIFIES)
- path/to/file1.py — <what this file does, relevant to the issue>
- path/to/file2.py — <what this file does, relevant to the issue>

## Expected Behavior
<What should happen after the fix, derived from issue text and failing tests>

## Failing Tests
- tests/test_module.py::TestClass::test_specific_case — <what this tests>
- tests/test_module.py::TestClass::test_edge_case — <what this tests>

## Test Dependency Map
Source files → test files that cover them:
- path/to/file1.py → tests/test_module.py, tests/integration/test_file1.py
- path/to/file2.py → tests/test_module.py

## Codebase Context

### path/to/file1.py
<5-10 lines: key function signatures, class hierarchy, patterns used, known gotchas>
Example: "Uses ABC metaclass pattern. Key method: `process(self, data: dict) -> Result`.
The Result type is imported from utils.types. File has a known circular import with config.py
— do not add new imports from config.py."

### path/to/file2.py
<5-10 lines of context>

## Preconditions (verified by White Pre-Check)
- All MODIFIES files exist at base commit: VERIFIED
- All test names are real: VERIFIED
- Function signatures match actual code: VERIFIED

## Postconditions
- Failing tests pass after the fix
- No existing passing tests regress
```

### Variant A Failure Modes

1. **Gold misidentifies affected files** (risk: medium): If the issue description is ambiguous and
   Gold reads the wrong source files, the mini-CONTRACT.md Codebase Context will be for the wrong
   files. The Howler will implement against incorrect context. White Pre-Check reduces but does not
   eliminate this risk — White verifies signatures match files, not that the right files were chosen.

2. **Gold's behavioral summary diverges from harness definition** (risk: low-medium): The harness
   defines "resolved" via test pass/fail, not behavioral description. If Gold's summary adds
   constraints beyond what the failing tests check, the Howler may over-engineer the fix.

3. **White Pre-Check latency** (risk: low): On tasks where mini-CONTRACT.md is straightforward,
   White Pre-Check adds 3-4 minutes with near-zero value. For simple single-file fixes with an
   obvious failing test, this overhead is pure cost.

4. **Triple gate over-blocks** (risk: low): White may flag code style issues as blockers on
   implementations that correctly pass the failing tests. Need to scope White's blocker criteria
   to correctness and contract compliance, not style.

---

## Variant B — Lite Spectrum

**When to use**: Typical single-file SWE-bench Pro tasks. The majority of Pro tasks (roughly 60-70%)
are single-file or have a clearly isolated change surface. Lite Spectrum trades contract enforcement
for speed while keeping the two accuracy improvements that matter most for correctness: Issue Re-Read
(I1) and Revision Pass (I6).

**Core insight**: The minimum viable Spectrum contribution on a single-file task is not a contract
or pre-check — it's a **structured task brief** that front-loads context that the Howler would
otherwise need to gather itself, plus a reflexion loop and a post-implementation review pass.

### Step-by-Step Pipeline

**Step B1 — Gold: Compact Task Brief** (~2 min)

Gold reads the issue and produces a ~200-token brief. This is not a CONTRACT.md — it's a
structured annotation of the raw issue.

Task brief format:
```
TASK BRIEF — <repo>/<issue-id>
Likely file(s): <2-3 file paths Gold identified from issue + test imports>
Failing tests: <test names verbatim from harness>
Goal: <one sentence: what behavior must change>
Hint: <one sentence about codebase pattern, if obvious from reading the issue>
```

Gold actions:
1. Read the issue text
2. Read the failing test file (to identify which source files are imported/tested)
3. Write the brief (not the full source files — just the brief)

The brief directs the Howler's attention without locking in Gold's interpretation.

*Token estimate (Gold, B1)*:
- Input: ~4,500 tokens (issue text ~500, failing test file ~2,500, brief writing context ~1,500)
- Output: ~300 tokens (the task brief itself)
- Total: ~4,800 tokens at Sonnet rates = ~$0.02

**Step B2 — Howler: Implementation** (~15-25 min)

Howler receives:
- SWE-bench task issue text (verbatim)
- Gold's task brief (~200 tokens)
- Failing test names

Howler reads the codebase itself (without a pre-built Codebase Context section from Gold).

Accuracy improvements active:
- **I1 (Issue Re-Read)**: After implementation, Howler re-reads issue and assesses correctness
- **I6 (Revision Pass)**: Up to 2 revision passes if tests fail

NOT active (because no CONTRACT.md):
- I2 (Test Dependency Maps — no map generated; Howler uses failing test names directly)
- I3 (Codebase Context Injection — Howler derives patterns itself)
- I4 (White Pre-Check — no contract to check)
- I5 (Contract-to-Test Generation — no contract)
- I7 (Pattern Library — injected into Gold brief if LESSONS.md has relevant patterns; minimal)

*Token estimate (Howler)*:
- Input at dispatch: ~10,000 tokens (HOWLER-OPS.md ~2,500, drop prompt + issue + brief ~4,000,
  initial source file reads ~3,500)
- Effective billed input (session): ~55,000 tokens (Howler reads more files itself vs. Variant A,
  where Gold pre-read them — roughly comparable total)
- Output: ~7,000 tokens
- Total: ~62,000 tokens at Sonnet rates = ~$0.28

**Step B3 — Double Quality Gate** (~5 min, parallel)

White + Gray (no /diff-review — Lite Spectrum omits it per CONTRACT.md Section 1.1).

- White reviews the implementation diff
- Gray runs the failing tests

*Token estimate (double gate)*:
- White: ~9,000 input, ~1,200 output = ~$0.04
- Gray: ~8,000 input, ~2,000 output = ~$0.04
- Total: ~20,200 tokens = ~$0.08

**Step B4 — Patch Submission** (~1 min)

Copper extracts the patch and submits to the harness.

### Variant B Total Token Estimate

| Step | Agent | Input (K) | Output (K) | Cost |
|------|-------|-----------|------------|------|
| B1: Compact task brief | Gold (Sonnet) | 4.5 | 0.3 | $0.02 |
| B2: Howler implementation | Howler (Sonnet) | 55.0 | 7.0 | $0.28 |
| B3: Double gate (White+Gray) | Sonnet x2 | 17.0 | 3.2 | $0.08 |
| B4: Patch submission | Copper (Haiku) | 1.5 | 0.3 | $0.003 |
| **Total (happy path)** | | **78.0K** | **10.8K** | **~$0.38** |

*Overhead ratio vs. Variant C*: ~1.4–1.6x wall-clock (Gold brief ~2 min + double gate ~5 min =
~7 min overhead on top of ~20 min Howler work)

### Variant B Failure Modes

1. **Gold brief misdirects the Howler** (risk: low-medium): The brief is advisory, not authoritative.
   A 200-token brief that points to the wrong file will waste Howler time but the Howler can
   correct course by reading the actual failing tests. Risk is lower than Variant A because the
   Howler isn't locked in by a CONTRACT.md.

2. **Howler spends extra tokens re-deriving context** (risk: low): Without Codebase Context (I3),
   the Howler reads source files without guidance on patterns and gotchas. This adds tokens but
   also means the Howler isn't constrained by Gold's potentially incorrect characterization of
   the codebase.

3. **/diff-review gap** (risk: low): The omission of /diff-review means no security review.
   SWE-bench Pro tasks are algorithmic fixes — security issues are rare, and /diff-review's
   value here is mostly noise. Acceptable tradeoff.

---

## Variant C — Bare Sonnet

**Purpose**: Control baseline. Measures the accuracy and cost of raw Claude Sonnet on SWE-bench
Pro tasks with no coordination overhead whatsoever. Variant C is **not a proposed production
pipeline** — it is the comparison point against which Variants A and B are evaluated.

**When to use**: In the benchmark evaluation as the control condition.

### Step-by-Step Pipeline

**Step C1 — Single Sonnet Session: Read, Implement, Verify** (~15-25 min)

Single Sonnet session. No agents. No orchestration.

Prompt (the entirety of Spectrum's involvement):
```
You are resolving a GitHub issue. You have access to the repository at commit <hash>.

Issue title: <title>
Issue body:
<full issue text>

Failing tests that must pass after your fix:
<test names>

Instructions:
1. Read the relevant source files.
2. Implement the fix.
3. Run the failing tests: <test commands>
4. If tests fail, revise and retry (max 2 attempts).
5. Output a unified diff patch of all changes.
```

Accuracy improvements active:
- **I6 (Revision Pass)**: Embedded in the prompt (up to 2 retry attempts)

NOT active:
- I1 (Issue Re-Read — not prompted)
- I2 (Test Dependency Maps — no map provided)
- I3 (Codebase Context — no context injection)
- I4 (White Pre-Check — no contract)
- I5 (Contract-to-Test — no contract)
- I7 (Pattern Library — no injection mechanism without Gold)

**Step C2 — Patch Submission**

The session output (unified diff) is submitted to the SWE-bench harness directly.
No Copper agent — the diff is extracted from the session output by a thin script.

### Variant C Total Token Estimate

| Step | Agent | Input (K) | Output (K) | Cost |
|------|-------|-----------|------------|------|
| C1: Implementation session | Sonnet | 40.0 | 7.0 | $0.23 |
| C2: Patch extraction | Script | — | — | $0.00 |
| **Total (happy path)** | | **40.0K** | **7.0K** | **~$0.23** |

*Overhead ratio*: 1.0x (this IS the baseline)

*Note on token count*: Variant C has lower effective input tokens than Variants A and B because:
(a) no HOWLER-OPS.md preamble (~2,500 tokens saved), (b) no CONTRACT.md or task brief injected,
(c) the session prompt is lean. The Howler in Variants A/B also has a larger billed session because
it writes HOOK.md and reads more carefully — the discipline costs tokens.

### Variant C Failure Modes

1. **No scope verification** (risk: high): Sonnet may implement the wrong fix if the issue
   description is ambiguous. No Gold reads the failing tests and maps them to source files.

2. **No codebase context** (risk: medium): Sonnet must derive patterns from reading files
   without guidance. On tasks with non-obvious codebase conventions, this leads to
   implementations that pass the specific failing tests but violate broader patterns.

3. **No quality gate** (risk: medium): No White review for logical correctness beyond "tests
   pass." Regressions that aren't caught by the specified failing tests are not detected.

4. **Self-reported completion** (risk: medium): Without a separate Gray agent, test execution
   is self-reported within the Sonnet session. The model may assert tests pass without running
   them, or may not catch harness-specific test runner differences.

---

## Accuracy Improvements Mapping

This table maps the 7 accuracy improvements (I1–I7 from PLAN.md) to each pipeline variant.
Active = improvement runs as documented in SPECTRUM-OPS.md. Partial = improvement applies but
in reduced form. Inactive = not applicable given the variant's architecture.

| Improvement | Variant A (Full) | Variant B (Lite) | Variant C (Bare) |
|-------------|-----------------|-----------------|-----------------|
| **I1** Issue Re-Read (Reflexion) | Active | Active | Inactive |
| **I2** Test Dependency Maps | Active (Gold generates map) | Partial (Howler uses failing test names directly; no source→test map) | Inactive |
| **I3** Codebase Context Injection | Active (mini-CONTRACT.md per-file context) | Inactive (no CONTRACT.md) | Inactive |
| **I4** White Pre-Check | Active (verifies mini-CONTRACT.md against repo) | Inactive | Inactive |
| **I5** Contract-to-Test Generation | Inactive (doc-only benchmark run; skip) | Inactive | Inactive |
| **I6** Revision Pass | Active (up to 2 passes) | Active (up to 2 passes) | Partial (embedded in prompt, 1 implied retry) |
| **I7** Pattern Library | Active (Gold injects relevant known failures from LESSONS.md if any match) | Partial (Gold may inject 1-2 known failures into brief) | Inactive |

**Active count**: A = 5/7, B = 3/7 (2 partial), C = 1/7 (1 partial)

**I5 is inactive across all variants**: Contract-to-test generation requires a persistent test
infrastructure. SWE-bench tasks already provide the failing tests — generating additional contract
stubs would create confusion about which tests to run. I5 is not a useful accuracy driver on
benchmark evaluation tasks.

**I7 scope on SWE-bench**: Pattern Library is most valuable when LESSONS.md has seen the same
type of task fail before. In the first 50-task run, the library will be sparse. As the benchmark
run accumulates failures, Brown should update LESSONS.md so subsequent runs benefit from
accumulated patterns. This is a compounding improvement — weak in run 1, valuable in run N.

---

## Gold Muster Risk Analysis: When CONTRACT.md Helps vs. Hurts

The central risk for Variant A is **specification drift**: Gold reads the issue, misinterprets
it, and writes a mini-CONTRACT.md that leads the Howler astray. This section assesses that risk
honestly.

### The Case That Gold Helps

**Structured context reduces ambiguity on complex issues.** SWE-bench Pro's hardest tasks
involve issues with ambiguous scope — "sometimes X fails" without a clear repro path, or
multi-component behavioral changes where the failing tests don't fully characterize the
expected behavior. For these tasks (roughly 20-25% of Pro), Gold's structured scope analysis
has positive expected value: Gold reads the failing tests, maps them to source files, and
distills a behavioral goal. The Howler receives this context directly instead of spending
the first third of its session reconstructing it.

**White Pre-Check catches hallucinated file paths.** SWE-bench repos are diverse and unfamiliar.
Sonnet's file path suggestions in Variant C are sometimes wrong on first attempt. Gold's
White-verified mini-CONTRACT.md provides file paths that have been confirmed to exist at the
base commit. This eliminates a class of early Howler failures that waste implementation time.

**Codebase context prevents pattern violations.** For repos with non-standard patterns
(e.g., unusual metaclass usage, internal DSLs, custom error hierarchies), Gold's
5-10 line per-file context in the mini-CONTRACT.md prevents the Howler from writing
technically correct code that doesn't match the repo's patterns and consequently fails
integration tests that aren't in the failing test set.

**ACCURACY-REPORT.md finding supports structured context.** Augment Code attributes its
70.6% Verified score primarily to its Context Engine — structured codebase context before
the agent writes anything. Variant A is a lightweight approximation of this approach.

### The Case That Gold Hurts

**Gold can amplify misinterpretation.** If Gold misidentifies the root cause (e.g., the issue
says "X is broken" but the real problem is in module Y, not X), the mini-CONTRACT.md will
steer the Howler toward the wrong area. A bare Sonnet in Variant C would at minimum read the
failing test and trace the actual error, not rely on Gold's scoping. The CONTRACT.md creates
an authoritative-feeling wrong answer.

**Overhead without gain on trivial tasks.** For issues where the failing test clearly
identifies the line to fix (e.g., a one-line off-by-one error with a clear stack trace),
Gold's muster adds 8+ minutes and ~$0.13 with near-zero accuracy benefit. Variant C would
get the right answer faster and cheaper. Approximately 30-35% of Pro tasks are in this
category — clear, localized fixes with unambiguous test output.

**Gold's summary introduces abstraction.** When Gold writes "goal: fix the edge case in
`parse_config()` when the key is missing," it loses information present in the raw
issue (e.g., user comments clarifying behavior, discussion threads, linked PRs). Variant B's
approach of passing the verbatim issue text while adding only a minimal annotation preserves
this information.

**Serial latency matters for batch evaluation.** A 50-task run with Variant A requires Gold
to run for each task. If tasks are batched in parallel (e.g., 5 tasks at once), Gold adds
~8 minutes of serial latency per task, which is ~40 minutes of wall-clock cost on a
50-task batch. This doesn't affect accuracy but affects evaluation timeline.

### The Testable Hypothesis

The risk is testable and should be tested. The benchmark design should include all three
variants on the same task subset:

- Tasks where Gold muster helps: multi-file, ambiguous scope, non-obvious codebase patterns
- Tasks where Gold muster hurts or is neutral: single-file, clear error, obvious failing test

**Predicted A vs. C accuracy gap by task type**:

| Task Type | Predicted A > C | Predicted C >= A |
|-----------|----------------|-----------------|
| 4+ files changed, complex | Yes (I3 context is load-bearing) | — |
| 1-2 files, clear stack trace | — | Yes (muster adds noise) |
| Ambiguous issue, multi-component | Yes (Gold scoping reduces confusion) | — |
| Missing feature (not a bug) | Possibly (Gold can extract acceptance criteria) | — |

**A priori risk assessment**: Variant A has **positive expected value on Pro tasks overall**
because Pro tasks skew harder and more multi-file than Verified tasks. The muster overhead
hurts on the easiest quartile of tasks and helps on the hardest quartile. The middle 50% is
a toss-up. This makes Variant B the better initial run choice: it retains Gold's lightweight
attention-directing (the task brief) while avoiding the risk of Gold authoritatively
mis-scoping the problem via a full CONTRACT.md.

### Mitigation: Complexity-Based Variant Selection

An auto-detection heuristic can reduce the muster overhead risk by routing simple tasks to
Variant B and complex tasks to Variant A:

**Route to Variant A if ANY of the following are true**:
1. The failing test suite spans 3+ test files (indicates multi-module impact)
2. The issue mentions or links to multiple source files explicitly
3. The issue description is over 500 tokens (complexity proxy)
4. The harness provides multi-line failing test output with traces across 3+ modules

**Route to Variant B otherwise**.

**Route to Variant C never in production** (Variant C is the control baseline, not a
production pipeline). In the benchmark evaluation, all three variants should run on the
same tasks for comparison — routing is for a production deployment decision, not the evaluation.

This heuristic should correctly route ~70% of tasks to Variant B and ~30% to Variant A,
cutting Gold muster overhead across the run while preserving Variant A's accuracy benefit
where it matters.

---

## Recommended Variant for Initial Benchmark Run

**Recommendation: Run all three variants on a 50-task subset of SWE-bench Pro.**

**Primary run**: Variant B (Lite Spectrum)
- Lowest muster overhead risk
- 3 of 7 accuracy improvements active (the two highest-impact ones: I1 Issue Re-Read and I6
  Revision Pass, plus partial I7 Pattern Library)
- Overhead ratio ~1.4-1.6x vs. bare Sonnet — defensible tradeoff
- $0.38/task projected cost — reasonable for a 50-task run ($19 total)

**Control run**: Variant C (Bare Sonnet) on the same 50 tasks
- Required to measure what Spectrum adds
- $0.23/task projected cost ($11.50 total)
- Without this baseline, Variant B's score is uninterpretable

**Exploratory run**: Variant A on a 15-task subset of the hardest Pro tasks (4+ file changes)
- Tests the coordination hypothesis where it should be strongest
- $0.57/task projected cost for 15 tasks = ~$8.55
- Results will show whether mini-CONTRACT.md helps on complex multi-file tasks

**Total 50-task evaluation budget estimate**:
- Variant B: 50 tasks × $0.38 = $19.00
- Variant C: 50 tasks × $0.23 = $11.50
- Variant A (15-task): 15 tasks × $0.57 = $8.55
- Total: ~$39.05

**Rationale for not leading with Variant A**: The ACCURACY-REPORT.md's central finding is that
"Spectrum's muster overhead introduces specification errors that wouldn't exist with a bare agent.
This is testable: run with and without CONTRACT.md and compare." Running Variant B as the primary
condition directly tests the minimum viable Spectrum contribution. If Variant B outperforms
Variant C, that is the proof case for Spectrum adding value even without full muster. If Variant A
then outperforms Variant B on the hard subset, that validates the full muster ceremony for
complex tasks.

---

## Howler Drop Template Excerpt for Variant A

This is the actual prompt text Gold would use to drop the Howler for a SWE-bench task in
Variant A. It is a reduced version of the standard Spectrum Howler Drop Template, adapted
for single-issue benchmark tasks.

```
Spectrum: swe-bench-prep (evaluation run)
Howler: H-<task-id>
Task: Resolve SWE-bench Pro issue <repo>/<issue-id>
Base commit: <hash>
Branch: swe-bench/<run-id>/<task-id>

CONTEXT:
Gold has read the issue, the failing tests, and the implicated source files.
The mini-CONTRACT.md below is the result. It has been verified by White Pre-Check:
all MODIFIES files exist, all test names are real, all function signatures match.

--- BEGIN mini-CONTRACT.md ---
<inlined mini-CONTRACT.md contents here>
--- END mini-CONTRACT.md ---

INSTRUCTIONS:
1. Write HOOK.md before touching any source files.
   Minimal format: status, task summary, MODIFIES files, progress checklist.

2. Implement the fix. Use the Codebase Context in mini-CONTRACT.md as your guide
   for patterns and conventions — do not re-derive what Gold has already documented.

3. Run the failing tests listed in the mini-CONTRACT.md Test Dependency Map:
   <test commands>
   Tests must pass before proceeding.

4. REVISION PASS: If tests fail, read the test output, identify root cause, fix.
   Maximum 2 revision passes. After 2 failures, document and proceed to step 5.

5. ISSUE RE-READ: After tests pass, re-read the original issue text above.
   Write a 3-5 line assessment in HOOK.md:
   - "Does my patch resolve the stated problem end-to-end?"
   - "Are there edge cases in the issue description I haven't handled?"
   - "Does my change match the expected behavior described in the issue?"
   If you identify a gap, fix it before proceeding.

6. Quality gates (run in parallel):
   - Drop White to review your implementation diff
   - Drop Gray to run the full test file: <test file path>
   If White finds blockers, fix and re-run White before proceeding.

7. Extract patch: git diff <base-commit> HEAD > patch.diff
   Output the patch to HOOK.md under "## Patch" for Copper to submit.

8. Write completion note in HOOK.md: status, test results, issue re-read assessment.

KNOWN RISKS (from prior spectrums, if any apply):
<Gold injects 0-2 relevant failure patterns from LESSONS.md here — omit if none>
```

---

## Summary Tables for H4

The following tables consolidate the data H4 needs for the cost model.

### Per-Step Token Estimates by Variant

| Variant | Step | Agent | Input (K) | Output (K) |
|---------|------|-------|-----------|------------|
| A | Gold: Issue ingestion + mini-CONTRACT | Sonnet | 18.0 | 2.5 |
| A | White Pre-Check | Sonnet | 8.0 | 0.8 |
| A | Howler implementation | Sonnet | 60.0 | 8.0 |
| A | White (triple gate) | Sonnet | 10.0 | 1.5 |
| A | Gray (triple gate) | Sonnet | 8.0 | 2.0 |
| A | /diff-review (triple gate) | Sonnet | 6.0 | 0.8 |
| A | Copper submission | Haiku | 1.5 | 0.3 |
| **A** | **TOTAL** | | **111.5K** | **15.9K** |
| B | Gold: Compact task brief | Sonnet | 4.5 | 0.3 |
| B | Howler implementation | Sonnet | 55.0 | 7.0 |
| B | White (double gate) | Sonnet | 9.0 | 1.2 |
| B | Gray (double gate) | Sonnet | 8.0 | 2.0 |
| B | Copper submission | Haiku | 1.5 | 0.3 |
| **B** | **TOTAL** | | **78.0K** | **10.8K** |
| C | Sonnet session (read + implement + verify) | Sonnet | 40.0 | 7.0 |
| C | Patch extraction (script) | — | — | — |
| **C** | **TOTAL** | | **40.0K** | **7.0K** |

### Overhead Ratios

| Variant | Wall-Clock Estimate | Overhead Ratio vs. C |
|---------|---------------------|---------------------|
| A (Full Spectrum) | ~40-50 min per task | ~2.0–2.5x |
| B (Lite Spectrum) | ~28-35 min per task | ~1.4–1.6x |
| C (Bare Sonnet) | ~18-25 min per task | 1.0x (baseline) |

*Wall-clock estimates assume serial execution of a single task. Batch parallel runs
(multiple tasks concurrently) reduce total run time but do not change per-task ratios.*

---

## Completion Verification

- [x] Three variant sections (A, B, C) with step-by-step pipelines
- [x] Per-step token estimate tables by agent role (in Summary Tables for H4)
- [x] Per-variant accuracy improvement mapping (I1-I7 table)
- [x] Gold muster risk analysis (honest assessment with both cases)
- [x] Recommended variant for initial run with rationale
- [x] Howler drop template excerpt for Variant A (actual prompt text)
- [x] Overhead ratio estimates for H4

---

*H3 — Pipeline Mapping Architect — swe-bench-prep-0401 — 2026-03-31*
