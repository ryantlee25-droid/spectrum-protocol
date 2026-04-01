# Dev vs Main: Quality and Accuracy Comparison

**Date**: 2026-03-31
**Scope**: SPECTRUM-OPS.md accuracy pipeline, quality gates, tooling, and contract authoring
**Sources**: main branch (git show main:spectrum/SPECTRUM-OPS.md), dev branch (spectrum/SPECTRUM-OPS.md),
evaluation/code-review/accuracy-audit.md, evaluation/accuracy-research/ACCURACY-REPORT.md

---

## Summary Verdict

Dev is a substantial accuracy upgrade over main across all four dimensions examined. The
improvements are not incremental polish — they address the structural weaknesses of main's
pipeline: single-point-of-failure interpretation, self-review, and context-free contracts.
That said, the audit finds that several improvements are weaker in practice than claimed,
and two (I3, I5) carry a non-trivial risk of introducing errors that wouldn't exist in main.

---

## 1. Accuracy Pipeline

### Main Branch

Main's completion verification is a four-step mechanical checklist:

1. All CREATES files exist (`ls`)
2. All MODIFIES changed (`git diff --name-only`)
3. TypeScript type checks pass (`tsc --noEmit`)
4. Test runner passes on owned files

This is the entirety of main's in-Howler accuracy pipeline. Howlers verify their own work
mechanically. There is no correctness check — only a completeness check. A Howler that
correctly implemented the wrong thing passes all four steps.

### Dev Branch: 7 Accuracy Improvements

Dev adds seven improvements on top of main's four-step checklist. Per the accuracy audit:

| ID | Improvement | Mechanism | Audit Rating |
|----|-------------|-----------|--------------|
| I1 | Issue Re-Read (Reflexion) | After mechanical verification, Howler re-reads original task and writes a 3-5 line correctness assessment. Gaps trigger fixes before quality gates. | **5/10** |
| I2 | Test Dependency Maps | Gold runs `test_impact_map.py` during muster; output included in CONTRACT.md per Howler. Howlers run mapped tests during completion verification, not just "run all tests." | **7/10** |
| I3 | Codebase Context Injection | Gold runs `codebase_index.py` (mandatory when available) and writes per-Howler `## Codebase Context` summaries of function signatures, patterns, and gotchas. | **6/10** |
| I4 | White Pre-Check | White verifies CONTRACT.md against the actual codebase before freeze. Reports STALE/MISSING/MISMATCH. Gold patches before Howlers drop. | **8/10** |
| I5 | Contract-to-Test Generation | Gold generates structural test stubs (file existence, type exports) from CONTRACT.md postconditions before implementation. Howlers run these during completion verification. | **4/10** |
| I6 | Revision Loop | After completion verification, if tests fail: up to 2 revision passes with test output as context. Capped to prevent runaway spending. | **8/10** |
| I7 | Pattern Library | LESSONS.md `## Known Failure Patterns` section; relevant patterns injected into Howler drop prompts as `KNOWN RISKS`. Compounds over time. | **5/10 at launch → 8/10 after 10+ spectrums** |

### Dev Branch: 5 Accuracy Fixes

Dev also includes fixes to gaps or misspecifications in main's protocol:

| Fix | What It Corrects |
|-----|-----------------|
| **Issue Confirmation Gate** | After writing CONTRACT.md, Gold displays a 3-bullet interpretation summary (Problem / Desired behavior / Out of scope) to the human before running White Pre-Check or Politico. Addresses the audit's "weakest link" — Gold misreading the issue. |
| **codebase_index.py mandatory** | In main, Gold uses `codebase_index.py` only if it exists (optional). Dev makes it mandatory when available, with prose fallback. Reduces Gold hallucination risk in I3. |
| **Parallel muster reads** | Steps 3, ARCHITECTURE.md, and codebase_index.py runs are independent. Dev explicitly instructs parallel execution. Not an accuracy fix, but reduces muster latency 1-2 min, which reduces the pressure that causes Gold to rush summaries. |
| **White Pre-Check scoped correctly** | Politico prompt in dev explicitly notes "White Pre-Check has already validated factual accuracy — your role is adversarial review of decomposition logic." Prevents overlap and double-review noise. |
| **CHECKPOINT.json locus tracking** | Dev adds `locus_history` and `circuit_breaker_state` to CHECKPOINT.json schema, updated after every failure (not just phase transitions). Enables accurate recovery from mid-spectrum session death. |

### Assessment

The research report (ACCURACY-REPORT.md) estimates the underlying mechanisms:

- I1 (Reflexion): "+0.3 to +0.5 D3 impact" — the audit rates this 5/10 because Sonnet's
  single-pass self-reflection has a rubber-stamping failure mode. Low signal on complex failures.
- I2 (Test maps): "+0.5 to +1.0 D3 impact" — audit rates 7/10. Solid for well-organized
  projects; fails on monorepos with barrel exports or integration-heavy test strategies.
- I3 (Context injection): "+0.5 to +1.0 D3 impact" — audit rates 6/10. High ceiling, significant
  hallucination risk. The White Pre-Check (I4) partially mitigates but doesn't address relevance errors.
- I4 (White Pre-Check): audit rates 8/10. The most mechanically sound improvement. Clear scope,
  binary outputs, correct positioning in pipeline.
- I5 (Contract tests): "+0.3 to +0.5 D3 impact" (research estimate) — audit rates 4/10. Structural
  postcondition stubs are useful; behavioral test generation exceeds Gold's reliable capabilities.
- I6 (Revision loop): audit rates 8/10. Simple, sound, well-bounded. Flaky test sensitivity is
  the main weakness.
- I7 (Pattern library): "+0.2 to +0.3 D3 impact" — audit rates 5-8/10 depending on run count.

The Issue Confirmation Gate fix is not rated in the audit but is identified as addressing the
"single largest leak in the pipeline" — Gold's unilateral interpretation of the issue. A 30-second
human confirmation step before Politico and White Pre-Check run catches misinterpretations before
they propagate through the entire pipeline. This may have higher practical impact than any of the
seven formal improvements.

---

## 2. Quality Gates

### Main Branch

Per the main branch template, Howlers run quality gates themselves:

> "When verified: run White + Gray + /diff-review in parallel (triple gate)."

Howlers are instructed to self-initiate the triple gate. This is self-review of one's own work,
albeit with independent reviewers (White, Gray, diff-review). The structural problem: the Howler
that just implemented the feature decides when implementation is complete enough to submit for
review. A Howler under time pressure or context saturation may declare completion prematurely.

Additionally, in main, the quality gate is dropped by the Howler — meaning a failed or stalled
Howler may not run the gate at all.

### Dev Branch

Dev moves gate coordination to Gold:

> "Quality gate (per Howler, coordinated by Gold): When a Howler signals completion, Gold spawns
> ALL THREE in parallel as visible background agents."

Howlers implement and return — they do not run quality gates themselves. Gold receives the
completion signal and dispatches White, Gray, and diff-review independently. After all three
pass, Gold spawns Copper to open the PR.

Key differences:

| Dimension | Main | Dev |
|-----------|------|-----|
| Who triggers the gate | The Howler (self-initiated) | Gold (external trigger on completion signal) |
| Gate failure handling | Howler fixes and re-triggers | Gold coordinates Orange retries, circuit breaker |
| Visibility | Inline in Howler's thread | Visible background agents with status roster |
| Gate independence | Structurally independent reviewers, Howler-coordinated | Independent reviewers, Gold-coordinated (decoupled) |
| Failed Howler coverage | Howler may not run gate at all | Gold runs gate regardless of how the Howler ended |

### Assessment: How Much More Reliable Is Independent Coordination?

Moving gate coordination from Howler to Gold closes three failure modes:

1. **Premature completion**: A Howler under context pressure can declare done and skip the gate.
   With Gold coordination, the Howler signals completion and Gold decides whether to gate.

2. **Gate-skipping on stall**: A Howler that times out or runs out of context may never reach
   the gate step. Gold-coordination means the gate runs regardless.

3. **False confidence from self-coordination**: The Howler coordinating its own review introduces
   implicit pressure to present work in the best light. Gold coordinating White gives White no
   incentive to overlook issues.

The improvement is meaningful but not transformational — White, Gray, and diff-review are the
same agents doing the same work. The coordination change prevents gate-skipping failures (which
are correctness-invisible in main) and makes gate results visible to the human through the status
roster. Estimated failure rate reduction from gate-coordination change alone: 15-25% on tasks
where Howlers previously reached context limits before completing the gate.

---

## 3. Tool Quality

### Main Branch

Main has one tool:

- **seam_check.py**: Checks that seams declared by Howlers in their debriefs have matching
  confirmations in the counterpart Howler's debrief. A coordination integrity check.

That's it. No codebase analysis, no test mapping, no postcondition verification. Gold authors
CONTRACT.md entirely from its reading of the repository.

### Dev Branch

Dev adds four tools and fixes seam_check.py:

| Tool | What It Does | Contribution to Accuracy |
|------|-------------|--------------------------|
| **seam_check.py (fixed)** | Unchanged function, but referenced correctly in Phase 5 (Pax). Main had inconsistencies in when it was invoked. | Coordination integrity; catches seam mismatches post-completion. Moderate impact — seam errors are already caught by Politico earlier. |
| **codebase_index.py** | Extracts import graphs, function signatures, and patterns for each file in the Howler's MODIFIES list. Output pastes directly into CONTRACT.md's per-Howler Codebase Context section. | High for context accuracy. Replaces Gold's prose-from-memory with AST-derived structural facts. Eliminates the hallucination vector in I3 for files it can analyze. Unavailable for files without static structure (generated, complex generics). |
| **test_impact_map.py** | Given a list of files to modify/create, returns the set of test files that exercise those files. Uses naming conventions and import-grep discovery. | Medium-High. The audit rates I2 (which this tool enables) at 7/10. Key limitation: naming-convention-based matching misses barrel exports and indirect integration paths. A project with 80% file-per-test coverage gets 80% of the tool's benefit. |
| **verify_postconditions.py** | Not directly described in SPECTRUM-OPS.md but referenced in the evaluation artifacts. Supports Phase 4 (Pax) independent validation of Howler claims against CONTRACT.md postconditions. | Medium. Reduces Gold's manual file-reading burden in Pax. Improves coverage of the independent validation step by automating postcondition checks. |
| **SWE-bench adapters** | Pipeline variants (Variant A mini-CONTRACT, Variant B 200-token task brief) for running Spectrum against SWE-bench Pro tasks. Multi-Candidate Mode (N=3 default). | High for benchmark accuracy. Not relevant to production spectrum runs. The multi-candidate mode — run N Howlers, select highest test pass rate — is the most powerful single accuracy mechanism in dev, but is opt-in and cost-constrained. |

### Assessment

The tool additions address Spectrum's single largest context accuracy gap: Gold authoring CONTRACT.md
from prose recall. `codebase_index.py` and `test_impact_map.py` replace two judgment steps
(what are the relevant signatures? which tests cover these files?) with deterministic tool output.
This is the right approach — judgment is error-prone under time pressure during muster.

The tools have the limitations the audit identifies:

- `codebase_index.py` produces structural facts, not semantic meaning. It can tell Gold that
  `foo(a: str, b: int) -> bool` exists; it cannot tell Gold that this function has a subtle
  concurrency invariant that the Howler must not violate.
- `test_impact_map.py` is a naming-convention heuristic, not a semantic dependency analyzer.
  The 70% regression reduction from TDAD came from semantic analysis; this tool's simpler
  approach will achieve a fraction of that improvement.

Still, structured tool output with known limitations is strictly better than Gold's prose recall
with unknown limitations. The tools reduce the variance in Gold's codebase summaries, even if
they don't eliminate errors.

---

## 4. Contract Quality

### Main Branch

Gold writes CONTRACT.md from intuition:

- Reads PLAN.md, ARCHITECTURE.md, and samples 3-5 files
- Writes shared types, interfaces, naming conventions, and per-Howler Design-by-Contract sections
- Politico adversarially reviews the result for decomposition logic errors

No codebase tool is run. No human confirms Gold's interpretation. No White review of factual
accuracy before freeze. The contract is as good as Gold's understanding of the codebase — which
is a function of how thoroughly Gold read the relevant files during muster.

### Dev Branch: Three Contract Quality Upgrades

**Upgrade 1: codebase_index.py (mandatory)**

Gold must run `codebase_index.py` before writing the per-Howler Codebase Context section. This
directly reduces the "Gold misreads the codebase" failure mode by substituting tool output for
recall. The tool cannot catch everything (semantic invariants, generated files, complex generics),
but it catches signature mismatches and import structure errors — the most common codebase context
errors in contract authoring.

**Upgrade 2: White Pre-Check (factual accuracy gate)**

After Gold writes CONTRACT.md, before Politico runs, White verifies:
- Do all files listed in MODIFIES actually exist?
- Do the documented function signatures match the actual codebase?
- Are any interface names or constants referenced in the contract missing from the codebase?

This is a second reader applying independent verification to Gold's work. The audit rates I4 at
8/10 — the most reliable improvement in the pipeline. It directly reduces the "Gold misreads a
file and writes an incorrect signature" failure mode.

**Upgrade 3: Issue Confirmation Gate**

After writing CONTRACT.md but before White Pre-Check and Politico, Gold displays:

> "Here is what I understood this issue to require:
> - Problem: [one sentence]
> - Desired behavior: [one sentence]
> - Out of scope: [what was excluded and why]"

Human confirms or corrects before the contract freezes.

This is the most important contract quality change in dev. The audit's weakest link analysis
identifies Gold's unilateral issue interpretation as the pipeline's primary failure mode —
it's the one error that passes all other quality gates (White Pre-Check validates the contract
against the codebase, not against the issue; Politico challenges decomposition logic, not
interpretation; White at quality gate reviews implementation against contract, not against issue).

### Assessment: How Much Does This Reduce Gold Misreading the Issue?

The Issue Confirmation Gate is the only mechanism in either main or dev that catches interpretation
errors before they propagate. Without it (main's behavior), a Gold that misunderstands an ambiguous
issue produces a well-specified, internally consistent contract that implements the wrong thing.
That contract passes White Pre-Check (factually accurate about the codebase), passes Politico
(logically decomposed), passes the Howler quality gate (White reviews implementation against
contract, not against issue), and produces a PR that looks correct until a human or integration
test notices the wrong behavior.

The confirmation gate adds ~30 seconds to muster. It eliminates the class of failures where Gold's
interpretation diverges from intent — which the research report identifies as occurring when issues
are ambiguous, have implicit context, or assume domain knowledge. For well-specified issues, the
gate is a trivial confirm. For ambiguous issues, it's the difference between building the right
thing and building the wrong thing perfectly.

Combined impact of all three upgrades: the "Gold misreads the issue" failure mode is caught by the
confirmation gate (intent); the "Gold misreads a file" failure mode is caught by codebase_index.py
(structure) and White Pre-Check (signature accuracy). Dev's CONTRACT.md will be factually more
accurate and interpretively more aligned than main's in the majority of cases.

---

## 5. Projected Accuracy Improvement: Main → Dev

### Per-Improvement Research Estimates vs. Audit Ratings

| ID | Research D3 Impact | Audit Rating | Assessment |
|----|--------------------|--------------|------------|
| I1 | +0.3 to +0.5 | 5/10 | Apply 50% confidence. ~+0.2 expected value. |
| I2 | +0.5 to +1.0 | 7/10 | Apply 70% confidence. ~+0.5 expected value. |
| I3 | +0.5 to +1.0 | 6/10 | Apply 60% confidence + hallucination risk offset. ~+0.4 expected value. (I4 pairing required to get full benefit.) |
| I4 | +0.3 to +0.5 | 8/10 | Apply 80% confidence. ~+0.35 expected value. (Acts as a multiplier for I3.) |
| I5 | +0.3 to +0.5 | 4/10 | Apply 40% confidence. ~+0.15 expected value. Note: audit flags non-trivial risk of adding noise. Net may be lower. |
| I6 | Not separately estimated; subsumed in benchmark score | 8/10 | Catches mechanical errors the checklist misses. Estimated ~+0.3 expected value (conservative — prevents gate failures, not semantic errors). |
| I7 | +0.2 to +0.3 | 5→8/10 | Apply 50% confidence (launch state). ~+0.12 expected value now, ~+0.25 after 10 spectrums. |
| Issue Confirmation Gate | Not estimated (fix, not proposal) | Identified as "weakest link" fix | Binary: catches Gold misinterpretation or doesn't. Estimated ~+0.3 expected value on ambiguous issues; negligible on well-specified issues. |
| Quality gate coordination | Not estimated | 15-25% gate-skip prevention | ~+0.2 expected value (prevents silent gate-skipping failures). |

### Cumulative Estimate

Treating improvements as partially independent (they share some failure modes — see audit's
interaction effects analysis), and discounting for correlation:

| Scenario | Method | Estimate |
|----------|--------|---------|
| **Optimistic** | Sum research estimates at upper bound | +3.7 to +4.8 total D3 units |
| **Realistic** | Apply audit ratings as confidence weights, sum expected values | **+2.5 to +2.8 total D3 units** |
| **Conservative** | Apply audit ratings, assume 40% correlation between improvements | **+1.5 to +2.0 total D3 units** |

The research report's baseline: Spectrum main scores D3=2 (accuracy). The realistic estimate
would bring dev to approximately D3=3 to D3=3.5 — entering the competitive range alongside
Factory (D3=3) and Cursor agents (D3=3).

Reaching D3=4 (Augment Code / GitHub Copilot Workspace tier) would require the SWE-bench
evaluation run (P1 in the research report) plus favorable benchmark results. The protocol
improvements in dev are necessary but not sufficient for D3=4 — a published benchmark score
is also required.

### What Dev Does Not Fix

The audit's weakest link analysis identifies several gaps that dev does not fully close:

1. **Issue clarification before implementation**: The Issue Confirmation Gate helps, but it's
   a human-confirmation step, not an automated clarification loop. Issues with genuinely
   ambiguous requirements still require the human to know what to correct.

2. **Behavioral test generation**: Dev generates structural test stubs (I5). Factory's
   Spec → Test → Implement → Verify generates behavioral tests before implementation. The gap
   is documented but not closed.

3. **Semantic codebase indexing**: `codebase_index.py` uses static analysis of import graphs
   and function signatures. Augment Code's Context Engine uses semantic analysis. Gold-authored
   summaries with `codebase_index.py` output are better than Gold alone, but behind Augment's
   automated approach.

4. **Contract drift for sequential Howlers**: For Howlers that run after an earlier Howler has
   modified shared files, the Codebase Context in CONTRACT.md is stale (written at muster time).
   No mechanism in dev addresses this. Dependent task graphs accumulate context error at each
   DAG level.

5. **Multi-candidate as default**: Multi-Candidate Mode (run N Howlers, pick highest test pass
   rate) is the single most powerful accuracy mechanism in dev — but it's opt-in and not part
   of the standard pipeline. If integrated as the default for accuracy-critical tasks, projected
   accuracy improvement would be significantly higher.

---

## Summary Table

| Dimension | Main | Dev | Delta |
|-----------|------|-----|-------|
| Completion verification | 4-step mechanical checklist | 4-step checklist + I1 (reflexion) + I2 (test maps) + I5 (contract tests) + I6 (revision loop) | +4 accuracy mechanisms |
| Quality gate coordination | Howler self-initiates | Gold-coordinated, visible background agents | Gate-skip failure eliminated |
| Tool support | seam_check.py only | seam_check.py (fixed) + codebase_index.py + test_impact_map.py + verify_postconditions.py + SWE-bench adapters | 4 new tools, 1 fixed |
| Contract authoring | Gold from intuition | Gold + codebase_index.py (mandatory) + White Pre-Check + Issue Confirmation Gate | "Gold misreads" failure mode addressed |
| Issue interpretation gate | None | Issue Confirmation Gate (3-bullet human confirm before freeze) | Weakest link partially closed |
| Projected D3 score | D3=2 | D3=3 to D3=3.5 (realistic estimate) | +1.0 to +1.5 D3 units |
