# Accuracy Audit — Spectrum Protocol's Seven Accuracy Improvements

**Auditor**: Accuracy Engineer (independent review)
**Date**: 2026-03-31
**Sources reviewed**:
- `spectrum/SPECTRUM-OPS.md` — current protocol text
- `evaluation/accuracy-research/ACCURACY-REPORT.md` — Helldiver/Opus research
- `evaluation/accuracy-improvements/PLAN.md` — Blue implementation plan
- `evaluation/swe-bench-prep/protocol-audit.md` — H1 validation audit

**Scope**: This is not a completeness audit (H1 already did that, rated 8.5/10). This is an
effectiveness audit — for each improvement, does the mechanic actually improve accuracy in the real
world? Where will it fail? What's missing?

---

## Per-Improvement Assessment

---

### I1 — Issue Re-Read (Reflexion)

**Claimed basis**: Reflexion achieves 91% on HumanEval vs. 80% baseline. Self-reflection on
correctness improves first-pass accuracy.

**Will it actually work?**

Partially. The Reflexion paper's gains come from iterative refinement across *multiple attempts*,
where verbal reflection from attempt N is stored as memory and used in attempt N+1. Spectrum's I1
is a single-pass reflection at the end of implementation — structurally closer to a checklist
than true Reflexion. The Howler has no ability to restart from scratch with the reflection as
context; it can only patch the existing implementation. This is weaker than the research mechanism.

That said, a single-pass correctness check is still better than no check. The three self-assessment
prompts ("Does my implementation resolve the stated problem end-to-end?", "What edge cases...",
"Is there anything I deprioritized?") are concrete enough that Sonnet will engage with them rather
than write "no gaps identified" reflexively.

**Where will it fail?**

- **"No gaps identified" rubber-stamping**: Sonnet is compliant by default. After completing a
  large implementation task, a Howler has strong implicit pressure to declare success. The issue
  re-read will frequently produce "no gaps identified" even when gaps exist, because identifying
  a gap requires the Howler to doubt its own completed work. There is no adversarial pressure in
  this step — the Howler reviews itself.

- **Gap identification without gap resolution**: Even when a gap is identified, the instruction
  says "fix it before moving to step 9." But a complex gap (e.g., "I realized I didn't handle
  the error case for concurrent writes") may require significant rework. The instruction doesn't
  say how much rework is appropriate or when to declare the gap too large to self-fix and escalate.
  A Howler might attempt a fix, introduce a new bug, and proceed.

- **Tasks where the problem statement is ambiguous**: If the original task description is vague,
  re-reading it reveals nothing new. The Howler cannot identify gaps in an implementation of an
  unclear spec. This is common in real-world tickets and exactly the case where re-reading fails.

**What's missing?**

The improvement would be stronger if the re-read included the *acceptance criteria* from PLAN.md
or CONTRACT.md postconditions, not just the task prose. "Does my implementation satisfy the
CONTRACT.md postconditions?" is more mechanically verifiable than "does it resolve the stated
problem?" The postcondition question has a binary answer; the problem statement question requires
judgment.

Also missing: a minimum standard for the assessment. "Issue re-read: no gaps identified." with
zero supporting reasoning is technically compliant but epistemically worthless. The instruction
should require at least one sentence of reasoning per bullet even for the no-gap case.

**Interaction effects**: I1 feeds I6 (Revision Pass). When I1 finds a gap, the Howler fixes it,
which may break tests, which triggers I6. The chain is correct but adds latency — each gap found
in I1 that fails tests will consume one of I6's two revision passes. Three re-read steps (REFLEXION
step 5, SCOPE ALIGNMENT CHECK step 6, issue re-read step 8b) share the same cognitive load budget.
H1 notes they serve distinct purposes, which is correct, but there's a diminishing returns curve
on how much "re-reading" adds when a Howler is already fully context-saturated from implementation.

**Effectiveness rating**: 5/10. Good signal on simple task mismatches. Low signal on complex
integration failures and ambiguous specs. Risk of false confidence from rubber-stamped assessments.

---

### I2 — Test Dependency Maps

**Claimed basis**: TDAD (arxiv 2603.17973) showed 70% regression reduction by providing contextual
test information vs. procedural mandates. The key insight: *which* tests to run matters more than
*whether* to run tests.

**Will it actually work?**

Yes, more reliably than I1. The mechanism is concrete: generate a map, include it in CONTRACT.md,
Howler runs the mapped tests. This is more mechanical than a reflexion prompt and harder to
accidentally skip. The `test_impact_map.py` tool actually does the mapping work, so Gold doesn't
need to reason about which tests to run — it delegates to the tool.

The 70% regression reduction from TDAD is contingent on the test mapping being accurate. TDAD
used semantic analysis; `test_impact_map.py` uses naming conventions and grep for import
references. This is significantly simpler and will miss:
- Tests that import through re-export barrels (`import { foo } from '@/index'` won't match
  `src/foo.ts` by grep)
- Tests that exercise the target code indirectly through integration paths
- Test suites organized by feature rather than by source file (common in Django, Rails)

**Where will it fail?**

- **Monorepo projects with complex import graphs**: barrel exports and cross-package imports will
  produce systematically incomplete maps. A Howler who trusts "these are the only tests to run"
  when the map is incomplete will miss regressions in integration paths.

- **Projects with minimal unit test coverage but comprehensive integration tests**: the tool will
  find few unit tests, and the Howler will conclude "run 2 test files" when the real safety net is
  a 200-test integration suite. The instruction's fallback ("run tests on your owned files") is
  only marginally better.

- **Dynamic test generation**: pytest fixtures and Jest test factories that generate test cases
  at runtime don't have stable file names to map to. The tool would miss all dynamically generated
  tests.

- **False confidence from an incomplete map**: A complete but incorrect map ("I ran all the tests
  for these files and they pass") is more dangerous than no map at all, because it creates
  documented evidence of correct testing that is actually partial.

**What's missing?**

A confidence indicator on the map output: how many of the source files had name-matched tests vs.
how many relied on import-grep discovery vs. how many found nothing? A Howler reading "3 test
files to verify" with no indication that 5 of 8 source files found no tests would overestimate
coverage.

The tool should also indicate when a project uses a test runner it doesn't understand
(e.g., Cargo test, Go test, Gradle) and emit a "coverage unknown — run full test suite" fallback
rather than an empty map.

**Interaction effects**: I2 feeds I6 (revision pass uses the same mapped tests). This is the
correct design — the mapped tests become the Howler's feedback signal during revision. However,
if the map is incomplete, both I2 and I6 operate on a biased test signal. The two improvements
share the same weak point.

**Effectiveness rating**: 7/10. Solid improvement for well-organized projects with file-per-test
conventions. Significant failure modes in monorepos and projects with integration-heavy test
strategies. Incomplete maps create false confidence — which may be worse than no map.

---

### I3 — Codebase Context Injection

**Claimed basis**: Augment Code's 70.6% SWE-bench Verified score is primarily attributable to its
Context Engine (semantic codebase indexing). Pre-digesting patterns into the contract closes the
context gap.

**Will it actually work?**

This is the improvement with the highest ceiling and highest risk. Done well, it eliminates the
most common cause of Howler failure: implementing something that conflicts with existing patterns
because the Howler discovered the pattern too late. Done badly, it produces incorrect or
outdated summaries that actively mislead Howlers.

The 5–15 line scope limit is the right instinct, but it assumes Gold can reliably distill a complex
file into 5–15 accurate lines. For files with complex logic, Gold's summary will necessarily omit
things — and what it omits may be exactly what the Howler needs to know. Gold is also a Sonnet
agent, not a purpose-built code indexer. Its summaries are as reliable as Sonnet's reading
comprehension under time pressure during muster.

**Where will it fail?**

- **Gold misreads complex files**: This is the central risk. If Gold summaries a file with a subtle
  invariant incorrectly ("this module uses factory pattern" when it actually uses builder pattern),
  the Howler follows the incorrect guidance with confidence. A Howler who would have read the file
  carefully and noticed the pattern is worse off with a confident wrong summary from Gold.

- **Stale summaries after initial writes**: The codebase context is written once during muster.
  If a dependent Howler (one that runs after another) modifies files that appear in a later
  Howler's codebase context, the later Howler's context is now stale — but it's frozen in
  CONTRACT.md. White Pre-Check (I4) runs before any Howler drops, so it validates the initial
  state, not the state after earlier Howlers have made changes. This creates a race condition for
  dependent task graphs where earlier Howlers modify files that later Howlers reference.

- **Large MODIFIES lists**: H1 notes the scope creep risk (Gold writes 2000-token summaries for
  20-file tasks). The 5–15 line limit is stated but unenforced. In SWE-bench Pro tasks (avg 4.1
  files), this is bounded. For internal spectrums with 10+ MODIFIES files per Howler, Gold will
  regularly exceed the limit, making CONTRACT.md unwieldy.

- **Misaligned relevance**: Gold summarizes "existing function signatures relevant to the task,"
  but relevance is Gold's judgment call. Gold may summarize the wrong 5–15 lines for what the
  Howler actually needs. A Howler's task may touch side effects of functions that Gold didn't
  consider relevant.

**What's missing?**

The codebase_index.py tool is mentioned in SPECTRUM-OPS.md as an option ("Gold MAY use
`tools/codebase_index.py` to generate structured codebase context automatically"). This tool, if
it exists, would produce more reliable structural context (import graphs, function signatures) than
Gold's prose summaries. The tool is optional and its existence is not verified in the protocol.
Making it mandatory when available would reduce Gold hallucination risk.

Also missing: a validity window. "Context was accurate as of base_commit X" should be stated in
the contract so dependent Howlers know when the context was generated and how stale it might be.

**Interaction effects**: I3 feeds I4 (White Pre-Check validates I3's output). This is the most
important interaction in the pipeline — it partially mitigates I3's hallucination risk by
catching STALE/MISSING/MISMATCH errors before the contract freezes. However, White Pre-Check is
limited to factual verification (does the file exist, do the signatures match). It cannot catch
relevance errors (did Gold summarize the right functions?). The I3–I4 pairing closes the factual
accuracy gap but leaves the relevance accuracy gap open.

**Effectiveness rating**: 6/10. High potential impact when it works. Significant Gold hallucination
risk in complex codebases. The I4 pairing partially mitigates this but doesn't address relevance.
The improvement is better than nothing but requires more guardrails to be reliable in production.

---

### I4 — White Pre-Check

**Claimed basis**: MAST taxonomy shows specification errors are a top-3 failure category. Politico
reviews contracts adversarially but in isolation — not against the codebase. White Pre-Check
fills the factual accuracy gap.

**Will it actually work?**

Yes, and more reliably than I1 or I3. White Pre-Check's task is mechanical: check if files exist,
check if signatures match. These are binary questions with unambiguous answers. The three-category
output taxonomy (STALE, MISSING, MISMATCH) is concrete enough that White won't drift into style
observations or subjective judgments. The scope exclusion for CREATES files is explicit.

The key constraint is that this is *another Sonnet agent reading the codebase during muster*. If
the codebase is large and the contract references many files, White's reading window may be
insufficient to check all of them. White will read the files it can fit in context and may silently
skip the rest — which is worse than not checking, because it gives false confidence that all files
were verified.

**Where will it fail?**

- **Large codebases**: White reads files and compares against CONTRACT.md. For projects with 50+
  files in the MODIFIES list (common in large refactors), White will hit context limits before
  checking all files. The protocol doesn't specify what White should do when it can't check
  everything ("I verified 15 of 23 files"). A silent partial check is a reliability failure.

- **Generated code**: If the codebase has generated files (from codegen tools, protobuf, etc.),
  White may flag the generated file's actual signatures as MISMATCH against what Gold documented
  (which might be the source spec, not the generated output). White needs to understand that
  generated files require special handling.

- **Type aliases and overloaded signatures**: TypeScript with conditional types, overloaded
  function signatures, or complex generics may match in behavior but differ syntactically from
  what Gold summarized. White flagging these as MISMATCH would create false positives that
  waste Gold's time resolving.

- **Second-pass staleness**: White validates the contract at muster time. The contract is frozen
  at drop. Between muster and a late-DAG Howler's execution (potentially hours later in a long
  spectrum), the codebase might have changed (from earlier Howlers' merges, from developers
  working in parallel). White's certification has an expiry that the protocol doesn't acknowledge.

**What's missing?**

A size limit or sampling strategy when White can't check all files. "Prioritize files with the
most postconditions and those in the critical path of the DAG" would be better than implicit
partial coverage.

Also missing: a "White Pre-Check confidence" field in CONTRACT.md. "Files verified: 15/23. Files
not verified due to context limits: [list]" would tell downstream Howlers which parts of the
contract are certified and which are unverified assumptions.

**Interaction effects**: I4 is correctly positioned between I3 (produces the contract context to
verify) and Politico (reviews the now-verified contract's logic). The ordering is right. The
Politico hand-off note ("White Pre-Check has already validated factual accuracy — focus on
decomposition logic") is a clear scope division that reduces Politico overlap.

**Effectiveness rating**: 8/10. The most mechanically sound of the seven improvements. Clear
scope, concrete output taxonomy, correct positioning in the pipeline. Main risk is silent partial
coverage on large codebases. Would rate 9/10 with a coverage confidence indicator.

---

### I5 — Contract-to-Test Generation

**Claimed basis**: Factory's pipeline uses Spec → Test → Implement → Verify. Generating tests from
the contract spec before implementation catches postcondition violations automatically.

**Will it actually work?**

This is the most ambitious improvement and the least reliable in practice. The gap H1 identified
(no example test stubs, no template, Gold must infer framework and assertion patterns) is the
central problem. Gold is being asked to do three things it's not specialized for:
1. Read CONTRACT.md postconditions written in prose
2. Translate prose postconditions into runnable test assertions
3. Select the correct test framework and assertion syntax

Each step introduces error. A Gold that writes a test with the wrong import path, the wrong
assertion style, or tests a property that wasn't actually the postcondition will create a
contract test that either always passes (useless) or intermittently fails for reasons unrelated
to the Howler's work (noise).

The example in SPECTRUM-OPS.md (`expect(mod.UserSession).toBeDefined()`) tests that the export
exists, not that it has the correct type. A Howler that exports `UserSession = {}` (an empty
object) would pass this test. The test verifies existence, not correctness. For postconditions
that are behavioral ("the auth middleware rejects requests with expired tokens"), an export check
is not a meaningful test.

**Where will it fail?**

- **Behavioral postconditions**: If the contract says "the API route returns 401 for unauthenticated
  requests," a Gold-generated test stub cannot meaningfully test this without setting up request
  mocking, auth fixtures, and a test server. Gold will either write a trivially passing test
  (wrong) or a syntactically complex test that the project's setup doesn't support (failing noise).

- **Projects without test infrastructure**: H1 flags this correctly — if the project has no
  `tests/` directory or test framework config, running contract tests requires setup. The
  instruction says "skip and document as ASSUMPTION," but this is the failure mode for most
  greenfield projects where Howlers are creating new files.

- **Gold-generated tests that fail correctly, blocking Howlers**: If Gold writes a contract test
  that accurately tests a postcondition and the Howler fails to satisfy it, the Howler enters the
  I6 revision loop. But if Gold's test has a bug (wrong assertion, wrong fixture setup), the
  Howler is debugging Gold's mistake, not its own implementation. This is a net-negative
  contribution to accuracy.

- **Test framework version mismatches**: The example uses vitest/jest `import()` syntax. Projects
  using CommonJS `require()`, older jest versions, or other test frameworks will require different
  patterns. Gold must detect and adapt — which it will do inconsistently.

**What's missing?**

The entire premise of this improvement is that postconditions can be mechanically tested. For
structural postconditions (file exists, type is exported), this is true. For behavioral
postconditions (the function behaves correctly under X conditions), it requires a test that
simulates the condition — which is real implementation work, not stub generation. The improvement
should be scoped to structural postconditions only: existence, export presence, type shape.
Behavioral postconditions should remain in the quality gate (Gray).

Also missing: a review step on Gold-generated tests. Currently, Gold writes the tests and Howlers
are expected to run them. There is no step where anyone verifies that Gold's tests are correct.
A test that trivially passes or incorrectly fails is invisible to the pipeline.

**Interaction effects**: I5 feeds I6 (revision pass triggered by contract test failures). If I5
produces noisy contract tests, I6 will waste revision passes on Gold's test bugs. This creates a
compounding failure path: I5 bug → I6 false revision → Howler drifts → quality gate failures.

**Effectiveness rating**: 4/10. Correct in theory, unreliable in practice. The structural
postcondition subset (file existence, type exports) is implementable and useful. The behavioral
postcondition subset is either trivially weak or requires Gold to write meaningful tests, which
is beyond its role. Recommend scoping I5 to structural postconditions only and removing the
implication that Gold can generate meaningful behavioral tests.

---

### I6 — Revision Loop

**Claimed basis**: Providing test output as context for a retry reduces failure rates. Maximum 2
revision passes prevents infinite loops.

**Will it actually work?**

Yes, with the highest confidence of any improvement. The revision loop is the simplest and most
mechanically sound: if tests fail, try again with the failure output as context. The 2-attempt cap
prevents runaway spending. The escape hatch (proceed to quality gates after 2 failures) is correct
— White and Gray will catch what the Howler couldn't fix.

The question is whether 2 attempts is the right limit. Research on multi-attempt scaffolds
(SWE-bench agents, AlphaCode) suggests diminishing returns after the first retry — the second
attempt typically succeeds if the first attempt's error was a simple syntax error or off-by-one,
but rarely succeeds if the first attempt misunderstood the problem. The revision loop is most
effective for mechanical errors, least effective for conceptual errors.

**Where will it fail?**

- **Flaky tests**: If the test suite has flaky tests, a Howler may burn both revision passes on
  tests that would have passed on retry without any code change. The protocol has no mechanism to
  distinguish "test failed because my code is wrong" from "test failed because it's flaky." This
  is a known problem in CI/CD and equally a problem here.

- **Test environment issues**: If tests fail because of a missing environment variable, wrong
  working directory, or missing test database, revision passes won't help. The Howler will make
  code changes that don't address the environmental failure. The protocol should distinguish
  "test runner error" from "test assertion failure."

- **Cascading failures from I1 gap fixes**: If the issue re-read (I1) finds a gap and the Howler
  implements a fix that breaks existing tests, I6's revision passes are consumed fixing the gap
  introduced in I1, not the original implementation. The total revision budget is shared across
  all sources of failure.

**What's missing?**

A flakiness detector: if the same test fails and passes on rerun without code changes, flag it as
potentially flaky and don't count the pass against the revision budget. This is implementable as a
"rerun with no changes first" step before spending a revision pass.

Also missing: a classification of why revision passes failed. After 2 failed passes, the Howler
proceeds to quality gates and writes "Revision Pass 2: failed." But the reason (environmental?
flaky? conceptual misunderstanding?) is not captured in a structured way. Gray's diagnosis in the
quality gate phase has to re-derive this from scratch.

**Interaction effects**: I6 is the most cleanly isolated improvement. Its main interactions are
with I1 (which may trigger it) and I2 (which provides the test list it operates on). Both
interactions are correct. The 2-attempt cap acts as a natural circuit breaker for the I1→I6 chain.

**Effectiveness rating**: 8/10. Simple, sound, and well-bounded. Main weaknesses are flaky test
sensitivity and environmental failure misclassification. Both are solvable with a pre-revision
"no-change rerun" step.

---

### I7 — Pattern Library (Known Failure Patterns from LESSONS.md)

**Claimed basis**: TDAD showed contextual information about likely failure modes improves accuracy.
LESSONS.md is Spectrum's episodic memory — making it active (injected) rather than passive
(read on request) should improve accuracy over time.

**Will it actually work?**

Yes, but the ramp-up time is long. The improvement is only valuable after enough spectrums have
run to populate `## Known Failure Patterns` with real patterns. For new projects or teams running
their first spectrums, I7 contributes nothing. For teams with 10+ spectrums in their history,
it could be the most valuable improvement — a pattern library that warns "doc-only spectrums
commonly fail when Howlers use smart quotes (curly apostrophes) in markdown — see
remnant-narrative-0329" would prevent a class of errors that would otherwise be rediscovered.

The fuzzy matching problem H1 identifies is real: "task type" is not a controlled vocabulary.
Gold must decide whether "auth refactor" matches a pattern typed as "middleware tasks." This
is judgment, not lookup. Two Golds on identical tasks might inject different patterns.

**Where will it fail?**

- **Pattern generalization errors**: A pattern extracted from a specific failure ("this React
  component failed because it used class syntax in a hooks-only codebase") might be incorrectly
  applied to unrelated tasks ("all React tasks") by Gold's fuzzy matching. Overly broad injection
  of inapplicable patterns wastes Howler context budget and creates noise.

- **Pattern library staleness**: If the codebase or team conventions change, old patterns in
  LESSONS.md may become incorrect. There is no expiry or review mechanism for patterns. A pattern
  from 12 months ago may now be actively misleading.

- **Brown's extraction quality**: Brown (Haiku) extracts patterns from spectrum artifacts. Haiku
  is chosen for cost efficiency, not reasoning depth. The pattern extraction step is where the
  quality of the entire I7 improvement is determined, and it's done by the cheapest model in the
  roster. Gold reviews Brown's draft, but this is another Sonnet review of Haiku output — not
  an independent high-quality extraction.

**What's missing?**

A pattern confidence score and age timestamp. Patterns should include when they were extracted,
from which spectrum, and how many times they've been observed. A pattern seen in 5 spectrums is
more reliable than one seen once.

Also missing: a deprecation mechanism. When a pattern is no longer relevant (e.g., the team
migrated from class components to hooks), there should be a way to mark it inactive without
deleting historical information.

**Interaction effects**: I7 feeds I1 (the most useful patterns to inject would be "common
reflexion gaps for this task type"). The interaction is implicit rather than designed — there's
no guidance on what pattern types are most useful to inject into the issue re-read vs. the
implementation phase.

**Effectiveness rating**: 5/10 at launch (no patterns yet), scaling to 8/10 after 10+ spectrums
with disciplined Brown extraction. Fuzzy matching and Haiku extraction quality are the main risks.
Value compounds over time in a way the other improvements do not.

---

## Accuracy Pipeline Analysis

### Tracing a Task: Issue → Contract → Implement → Verify → Merge

**Stage 1: Issue → Contract (Gold muster, ~8 minutes)**

Errors introduced:
- Gold misreads the issue and writes an incorrect CONTRACT.md scope
- Gold summarizes codebase files incorrectly (I3)
- Gold generates incorrect contract tests (I5)

Errors caught:
- White Pre-Check catches STALE/MISSING/MISMATCH in contract (I4)
- Politico catches decomposition logic errors

*Error retention after muster*: Specification errors that are internally consistent and factually
correct about the codebase pass through. Politico and White Pre-Check are adversarial about
*logic* and *factual accuracy* respectively, but neither can catch "Gold misunderstood the intent
of the issue." This is the single largest leak in the pipeline: Gold's interpretation of the
issue is never independently validated against the issue author's intent.

**Stage 2: Contract → Implement (Howler, variable duration)**

Errors introduced:
- Howler misreads CONTRACT.md and implements something subtly different
- Howler encounters a pattern not captured in codebase context (I3 incompleteness)
- Howler makes a correct implementation of an incorrect spec (carrying Gold's error forward)

Errors caught:
- Scope alignment checks every 20 tool calls (compliance)
- Issue re-read after completion (I1, correctness — limited effectiveness)
- Contract test stubs (I5, structural postconditions only)

*Error retention after implementation*: Errors from Gold's contract propagate here. Errors in
Howler's interpretation of the contract also propagate. The issue re-read (I1) is the only
mechanism that checks against the original issue rather than the contract — but its effectiveness
is limited by the single-pass constraint and rubber-stamping risk.

**Stage 3: Implement → Verify (Completion verification, revision loop)**

Errors introduced:
- Test maps are incomplete (I2), causing regressions to go undetected
- Revision passes fix symptoms rather than root causes

Errors caught:
- Contract tests (I5)
- Test impact map-targeted tests (I2)
- Revision loop with test output context (I6)

*Error retention after verification*: Regressions in untested code paths survive. Tests that
don't cover the exact edge case the implementation gets wrong survive. The verification stage
catches *mechanical* errors (missing files, broken tests) better than *semantic* errors (wrong
behavior).

**Stage 4: Verify → Quality Gate (White + Gray + diff-review)**

Errors introduced: None (read-only phase)

Errors caught:
- White catches implementation errors against contract
- Gray catches test failures with fresh test execution
- diff-review catches security issues

*Error retention after quality gate*: White and Gray are the strongest filters in the pipeline.
But White reviews implementation against *contract*, not against the *original issue*. If the
contract is wrong, White's approval is meaningless for accuracy purposes. Gray catches regression
failures but cannot catch "the implementation is technically correct but doesn't solve the right
problem."

**Stage 5: Quality Gate → Merge (Pax, human review)**

Errors introduced:
- Pax over-classifies observations as blockers (known Gold/Sonnet tendency, noted in CLAUDE.md)
- Merge order risks if Pax gets the seam topology wrong

Errors caught:
- Pax's independent validation of Howler self-reports
- Gray runs after each merge (integration testing)
- Human review (the ultimate filter)

---

### Weakest Link Analysis

**The weakest link is Gold's issue interpretation during muster.**

Every downstream stage assumes the contract is an accurate representation of what needs to be
built. The entire accuracy pipeline — I2, I3, I4, I5, I6 — operates on the contract as ground
truth. White Pre-Check validates the contract against the codebase, not against the issue. Politico
challenges the decomposition logic, not the interpretation. If Gold misunderstands the issue
(which happens when issues are ambiguous, have implicit context, or assume domain knowledge),
no improvement in the pipeline catches it.

The research report identifies this risk: "The risk is that Spectrum's muster overhead introduces
specification errors that wouldn't exist with a bare agent. Gold might misunderstand the issue and
write a contract that leads the Howler astray." This is the most dangerous failure mode precisely
because it's silent — a well-specified contract that implements the wrong thing passes all quality
gates.

**The second weakest link is test coverage for non-standard code paths.**

I2 (test maps) helps Howlers know which tests to run, but it doesn't improve the tests themselves.
If the codebase has poor coverage of edge cases, error paths, or concurrent code, the test suite
won't catch errors in those paths regardless of which tests are mapped. The protocol has no
mechanism to assess or improve test coverage quality — only to identify which existing tests are
relevant.

**Where does the protocol ADD errors?**

1. **Gold's codebase context summaries (I3)**: A confident incorrect summary is worse than no
   summary. If Gold writes "this module uses factory pattern" when it uses builder pattern, the
   Howler implements factory pattern against a builder pattern codebase — an error that wouldn't
   exist without I3.

2. **Gold's contract test stubs (I5)**: A trivially passing test creates false evidence of
   correctness. A Howler that passes Gold's test stubs may proceed to quality gates with false
   confidence that postconditions are satisfied.

3. **Contract drift for dependent Howlers**: After Howler A modifies files, Howler B's codebase
   context (written at muster time) is stale. Howler B operates on Gold's description of the
   pre-A state of the codebase. For sequential task graphs, this is a systematic accuracy
   degradation that grows with DAG depth.

---

## Missing Accuracy Mechanisms

### What Competitors Do That Spectrum Doesn't

| Competitor technique | Spectrum gap | Severity |
|---|---|---|
| **Semantic codebase indexing** (Augment Code) | Gold-authored prose summaries (I3) vs. automated AST analysis | High — prose summaries are unreliable at scale |
| **Spec → Test → Implement → Verify** (Factory) | Spectrum does Contract → Implement → Verify + spot test stubs | Medium — behavioral test generation is missing |
| **Multi-candidate selection** (SWE-bench top performers) | Added as Multi-Candidate Mode but optional and underspecified | Medium — not integrated into standard pipeline |
| **Issue clarification before implementation** | None — Gold interprets issue unilaterally | High — the weakest link identified above |
| **Hierarchical verification** (Planner/Worker/Judge all phases) | White only reviews post-implementation | Medium — pre-implementation behavioral spec check missing |
| **Independent oracle** (separate agent to re-solve problem from scratch and compare) | None | Low — expensive but catches interpretation errors |

### Issue Clarification (The Biggest Missing Mechanism)

The research report and all seven improvements assume the issue is well-specified. In practice,
GitHub issues, JIRA tickets, and internal task descriptions frequently have ambiguity. No system
in the accuracy pipeline asks "does Gold's interpretation of this issue match what the issue
author intended?" The closest is I1's issue re-read, but that checks the *implementation* against
the *issue text*, not Gold's *interpretation* against the *issue intent*.

A simple addition: after Gold writes CONTRACT.md, display a 3-line summary of "what I understood
this issue to require" to the human for confirmation before running White Pre-Check and Politico.
This 30-second confirmation step would catch Gold misinterpretations before they propagate through
the entire pipeline.

### Behavioral Test Generation (The Missing Factory Step)

Factory's Spec → Test → Implement → Verify sequence generates *behavioral* tests from the spec
before implementation begins. Spectrum's I5 generates structural tests (file exists, type exported)
after the contract is written but before implementation. This is closer than before but still
doesn't produce behavioral tests that would fail before implementation and pass after correct
implementation.

A behavioral pre-test ("the auth middleware returns 401 for expired tokens") is the most direct
measure of whether the implementation solved the right problem. Neither Gold nor any current
improvement generates these tests. Gray generates tests *after* reviewing implementation — which
is coverage improvement, not TDD.

### What a Purpose-Built Accuracy-First Spectrum Variant Would Look Like

An accuracy-first variant would prioritize correctness over throughput with these changes:

1. **Issue confirmation gate** (2 minutes): Gold presents a 3-line interpretation summary before
   contract writing. Human confirms or corrects. Eliminates the weakest link.

2. **Behavioral test first** (before implementation): For each postcondition, Gold (or a
   specialized agent) writes a failing test that will pass when the postcondition is satisfied.
   Howlers implement against failing tests, not against prose contracts.

3. **Automated codebase context** via `codebase_index.py` (mandatory, not optional): Replace
   Gold's prose summaries with AST-derived function signatures and import graphs. Eliminates
   I3's hallucination risk.

4. **Multi-candidate selection** (N=2 minimum for accuracy-critical tasks): Two Howlers
   implement independently; Gray selects the patch with higher test pass rate. Eliminates
   single-point implementation failures.

5. **Post-merge behavioral validation** (Obsidian against original issue, not PLAN.md): Run
   Obsidian against the original issue text ("does the merged code do what the issue asked?"),
   not just against PLAN.md acceptance criteria. Closes the issue-interpretation leak at the end
   of the pipeline.

This variant would run 2–3× slower and cost 2–3× more per task. It's the right tradeoff for
SWE-bench benchmark runs and production hotfixes.

---

## If You Could Only Keep 3 of the 7 Improvements

**Keep I4, I2, and I6. Cut I1, I3, I5, I7.**

**I4 (White Pre-Check)**: The highest mechanical reliability of any improvement. Verifies facts,
not judgment. Clear scope, clear output taxonomy, clear remediation path. Catches a top-3 MAST
failure category (specification errors) at the point in the pipeline where fixes are cheapest.
No other improvement provides an independent verification step before the contract freezes.

**I2 (Test Dependency Maps)**: TDAD's 70% regression reduction is the strongest empirical
evidence base of any improvement. The mechanism (targeted test execution rather than full suite)
directly reduces false negatives in completion verification. The tool is implemented and its
interface is concrete. While the grep-based mapping has completeness limitations, even a 60%
complete map reduces blind verification compared to "run all tests" or "run tests on your files."

**I6 (Revision Loop)**: The most pragmatically sound improvement. Simple mechanism, bounded cost,
correct circuit breaker. Independently valuable regardless of what the other improvements do.
Catches mechanical implementation errors that survive completion verification but would fail the
quality gate. The 2-attempt cap is the right balance between correction opportunity and cost.

**Why cut I1**: Single-pass reflexion without restart is a weak version of the research mechanism.
High rubber-stamping risk. The three re-read steps (steps 5, 6, and 8b) are overlapping in effect.
If forced to keep a reflexion step, make it check against CONTRACT.md postconditions rather than
the prose task description — that's a more mechanically verifiable question.

**Why cut I3**: High Gold hallucination risk. Confident wrong summaries are worse than no summaries.
Without mandatory `codebase_index.py` (automated) replacing Gold's prose, the improvement adds
an error vector. The I4 dependency on I3 (White validates I3's output) is the only safeguard, and
it only catches factual errors, not relevance errors.

**Why cut I5**: Underspecified implementation, behavioral postconditions are untestable via stubs,
trivially passing tests create false confidence. Scope to structural postconditions only if kept.

**Why cut I7**: Zero value at launch. Compounds over time, but the compounding requires disciplined
Brown extraction (Haiku quality), controlled pattern vocabulary, and pattern expiry — none of which
are specified. The improvement is sound in theory; it needs the infrastructure to work reliably.

---

## Top 5 Accuracy Recommendations

### Recommendation 1: Add an Issue Confirmation Gate

**Mechanism**: After Gold writes CONTRACT.md, before running White Pre-Check, display to the
human: "Here is what I understood this issue to require: [3 bullet summary]. Confirm or correct
before I freeze the contract."

**Why this is the top recommendation**: It addresses the weakest link (Gold's issue
interpretation) with the lowest cost (30 seconds of human time, zero additional tokens for agents).
Every other improvement operates downstream of this interpretation. A confirmed interpretation
eliminates the most dangerous silent failure mode.

**Implementation**: Add one step to the muster sequence between CONTRACT.md writing and White
Pre-Check. Gold writes a `## Issue Interpretation` block at the top of CONTRACT.md with 3 bullets:
"What I understood the problem to be", "What I understood the desired behavior to be", "What I
decided is out of scope and why." Human confirms or redirects before the step proceeds.

### Recommendation 2: Mandatory codebase_index.py for I3

**Mechanism**: Make `tools/codebase_index.py` (currently "Gold MAY use") mandatory when the tool
exists, and block Gold's prose summaries as the primary context source. Prose summaries become
fallback only when the tool is unavailable.

**Why**: Gold's prose summaries of complex files are the primary error vector added by I3. AST-
derived function signatures and import graphs are factually correct by construction; Gold's
summaries are not. The tool is already mentioned in the protocol — promoting it from optional to
required eliminates the hallucination risk without changing the improvement's intent.

**Implementation**: Change the muster step 10 codebase_index.py reference from "Gold MAY use" to
"Gold MUST run when `tools/codebase_index.py` exists. If the tool is unavailable, Gold writes
prose summaries as fallback (5–15 lines per file)."

### Recommendation 3: Scope I5 to Structural Postconditions Only

**Mechanism**: Limit contract-to-test generation to postconditions of the form "file X exists" or
"module X exports type Y." Explicitly exclude behavioral postconditions. For behavioral
postconditions, document them in CONTRACT.md but do not generate tests — leave behavioral
verification to Gray.

**Why**: The current I5 implies Gold can generate meaningful behavioral tests ("the auth
middleware returns 401 for expired tokens"). It cannot, reliably. Attempting to do so produces
either trivially passing tests (false confidence) or complex tests with Gold-introduced bugs.
The structural subset is well-defined, implementable, and genuinely useful. The behavioral subset
should be handled by Gray after implementation.

**Implementation**: Rewrite step 12 to explicitly separate structural postconditions
("file/export existence, type shape assertions") from behavioral postconditions ("runtime behavior,
business logic"). Generate tests only for structural postconditions. Document behavioral
postconditions as Gray's verification targets.

### Recommendation 4: Add Test Map Confidence Indicators to I2

**Mechanism**: Modify `test_impact_map.py` to output a per-file confidence indicator alongside
each mapping entry: `source: name-match` (high confidence), `source: import-grep` (medium
confidence), or `source: none-found` (no coverage detected). Include in the `## Test Impact Map`
output so Howlers can distinguish reliable mappings from uncertain ones.

**Why**: An incomplete test map used with full confidence is worse than a complete-but-uncertain
map used cautiously. The current tool produces a flat list with no indication of how the mappings
were derived. Howlers treating all entries as equally reliable will miss regressions in the
"import-grep" and "none-found" categories. The confidence indicator shifts behavior: for
"none-found" files, Howlers should run the full test suite rather than skipping.

**Implementation**: 5–10 lines added to `test_impact_map.py` output format. Update the
CONTRACT.md section template to include the confidence column. Update Howler Drop Template
instruction 8 to say "for files marked `source: none-found`, run the full test suite rather
than relying on the impact map."

### Recommendation 5: Issue Re-Read Against Postconditions, Not Prose

**Mechanism**: Modify I1's self-assessment prompts to check implementation against CONTRACT.md
postconditions rather than the prose task description. Replace the three generic questions
with: "For each postcondition in my CONTRACT.md section, state whether my implementation
satisfies it and how you verified this."

**Why**: CONTRACT.md postconditions are more mechanically verifiable than prose task descriptions.
"Does my auth middleware export a function matching the signature in CONTRACT.md?" has a binary
answer. "Does my implementation resolve the stated problem end-to-end?" requires judgment. The
current I1 prompts require judgment; the postcondition prompts require verification. The
postcondition framing also directly mirrors what I5's contract tests check, creating redundancy
that reinforces rather than duplicates (I5 runs the test; I1 reasons about it).

**Implementation**: Replace the three issue re-read bullet prompts in Howler Drop Template
step 8b with: "For each postcondition listed in your CONTRACT.md section, write one line:
'[postcondition]: [satisfied/not satisfied] — [one sentence of evidence]'. If no postconditions
are listed, assess against the original task prose."

---

## Diminishing Returns Assessment

At 7 improvements, the pipeline has reached diminishing returns on the implementation side. The
quality gates (I4, I2, I6) are the most effective and most reliable. The generation improvements
(I3, I5) add error vectors alongside their benefits. The reflexion improvements (I1, I7) are
either weak in mechanism or slow to produce value.

The accuracy ceiling for the current 7 improvements, fully working, is approximately:
- I4 catches 60–70% of specification errors introduced during muster
- I2 catches 40–60% of regressions in tested code paths (with incomplete maps)
- I6 recovers 50–70% of mechanical implementation errors
- I1 catches 20–30% of correctness gaps (accounting for rubber-stamping)
- I3 provides value in ~60% of cases and introduces errors in ~20% of cases
- I5 provides value for structural postconditions, neutral/harmful for behavioral ones
- I7 provides no value until the pattern library is populated (3–5 spectrums minimum)

The next accuracy gains require addressing the weakest link (issue interpretation, Recommendation 1)
and improving test infrastructure (Recommendations 2 and 4). These are upstream of where all 7
current improvements operate.

---

*Accuracy Engineer — 2026-03-31*
