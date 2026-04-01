# Accuracy Research Report: Improving Spectrum Protocol's D3 Score

**Date**: 2026-03-31
**Author**: Helldiver (Opus research agent)
**Context**: Spectrum scores D3=2 (Accuracy) in competitive evaluation. This report proposes concrete approaches to reach D3=3 or D3=4.

---

## The Problem

Spectrum Protocol scores D3=2 on accuracy because it has no published SWE-Bench results. The competitive landscape:

| System | D3 Score | Evidence |
|--------|----------|----------|
| Augment Code/Intent | 4 | 70.6% SWE-bench Verified |
| GitHub Copilot Workspace | 4 | 55-56% SWE-bench Verified |
| Factory | 3 | 58.75% SWE-bench Verified |
| Cursor agents | 3 | Community benchmarks |
| Agent Teams (Anthropic) | 3 | Platform-level benchmarks |
| **Spectrum Protocol** | **2** | **No published benchmark** |

The D3=2 score is the single most damaging gap for Spectrum's credibility. Every other weakness (cost, speed, setup) is a documented tradeoff. Accuracy is an unanswered question.

### The Fundamental Challenge: Benchmarking a Protocol vs. a Model

SWE-bench evaluates whether an AI system can resolve a GitHub issue by producing a correct patch. Most leaderboard entries are single-agent systems (a model + scaffold). Spectrum is a coordination protocol -- it wraps the underlying model (Claude Sonnet) with contracts, file ownership, adversarial review, and quality gates.

This creates two distinct questions:
1. **Does the coordination overhead improve accuracy** on multi-file tasks?
2. **What is the raw accuracy** of the Spectrum pipeline end-to-end?

Both matter. The first is Spectrum's unique hypothesis. The second is what the leaderboard measures.

---

## Research Findings

### 1. SWE-bench Verified is Contaminated; SWE-bench Pro is the New Standard

As of March 2026, OpenAI stopped reporting SWE-bench Verified scores after finding training data contamination across all frontier models. The current SWE-bench Verified leaderboard (Claude Opus 4.5 at 80.9%, Sonnet 4.6 at 79.6%) is increasingly viewed as inflated. SWE-bench Pro -- a larger, harder set requiring multi-file changes (avg 4.1 files, 107.4 lines per solution) -- is the emerging standard. Top Pro scores are ~46%, far below Verified scores.

**Implication for Spectrum**: SWE-bench Pro is a better fit. Multi-file tasks are where coordination protocols should theoretically outperform single-agent approaches. Running Spectrum against Pro tasks (rather than Verified) would test the coordination hypothesis directly.

### 2. Multi-Agent Systems Have a 41-87% Failure Rate

The MAST taxonomy (March 2025) analyzed 1,642 execution traces across 7 open-source multi-agent frameworks. Failure rates ranged from 41% to 86.7%. The largest failure category was coordination breakdowns at 36.9% of all failures. Incorrect output verification accounted for 13.48%.

**Implication for Spectrum**: Spectrum's CONTRACT.md, file ownership matrix, and Politico adversarial review directly target the two largest failure categories (coordination breakdowns and specification issues). If Spectrum can demonstrate lower failure rates than uncoordinated multi-agent systems, that is publishable evidence of coordination-as-accuracy.

### 3. Coordination Gains Plateau at 4 Agents

Research shows coordination gains plateau beyond 4 agents. Below that, adding agents to a structured system helps. Above it, coordination overhead consumes the benefits.

**Implication for Spectrum**: SWE-bench tasks are typically single-issue resolution -- most don't need 4+ agents. Spectrum's value on SWE-bench would come from its quality gates and contract enforcement, not its parallelism. The benchmark strategy should use 1-2 Howlers per task, not full spectrum runs.

### 4. TDD Reduces Regressions by 70%

TDAD (Test-Driven Agentic Development, March 2026) reduced regressions on SWE-bench Verified from 6.08% to 1.82% -- a 70% reduction. The key finding: providing contextual information about which tests to verify outperforms prescribing TDD procedures. Adding procedural "write tests first" instructions without context actually increased regressions to 9.94%.

**Implication for Spectrum**: Spectrum should integrate impact analysis (dependency maps between source and tests) into the Howler drop template, not mandate TDD as a procedure. The CONTRACT.md already specifies integration points; extending this to include test dependency maps would directly improve accuracy.

### 5. Augment Code's Edge is Context, Not Architecture

Augment Code's 70.6% SWE-bench Verified score comes primarily from its Context Engine -- a semantic index of the full codebase that identifies precisely the right code subset before the agent writes anything. The gap between Augment and competitors is "what context the agent sees before writing code," not the agent architecture itself.

**Implication for Spectrum**: Spectrum's CONTRACT.md and ARCHITECTURE.md already provide structured context to Howlers. But this context is authored by Gold (a planning agent), not derived from semantic analysis of the codebase. Adding codebase-aware context to the Howler drop template -- relevant file paths, dependency graphs, test maps -- would close part of the gap.

### 6. Reflexion Achieves 91% on HumanEval

The Reflexion pattern (verbal self-reflection stored in episodic memory, used to improve subsequent attempts) achieves 91% pass@1 on HumanEval. Spectrum already implements a weaker version: scope alignment checks every 20 tool calls, and completion verification. But Spectrum's version is compliance-focused ("am I on track?"), not accuracy-focused ("did I get it right?").

**Implication for Spectrum**: Strengthen the reflexion loop. After completion verification, Howlers should re-read the original issue/task and ask "does my implementation actually solve the stated problem?" before declaring done.

---

## Proposals Ranked by Expected Impact

### Proposal 1: Run SWE-bench Pro Evaluation (Minimum Viable Benchmark)

**What**: Run Spectrum against a 50-100 task subset of SWE-bench Pro. Use a simplified pipeline: single Howler per task with CONTRACT.md (issue -> contract -> implement -> verify). Publish results.

**Expected D3 impact**: D3=2 -> D3=3 (if results are 35%+ on Pro, which is competitive). D3=4 requires 45%+ on Pro or 72%+ on Verified.

**Effort**: Medium (2-3 weeks). SWE-bench infrastructure exists (Docker-based, `sb-cli` for cloud evaluation). The work is adapting Spectrum's pipeline to the benchmark harness.

**Evidence it works**: Every system that publishes a benchmark score gets a D3 boost. Claude-flow published SWE-bench results and claims 85% on its coordination modes. Even a modest score is better than no score.

**Implementation details**:
- Use SWE-bench's Docker evaluation infrastructure
- For each task: Gold reads the issue, writes a mini-CONTRACT.md (affected files, expected behavior, test targets), drops a single Howler
- Howler implements the fix, Gray runs tests
- Skip Politico, Pax, and other multi-Howler coordination (single-task doesn't need it)
- This tests whether CONTRACT.md + completion verification + quality gates improve single-task accuracy over bare Sonnet

**Key decision**: Whether to also run a multi-Howler variant on the subset of Pro tasks that span 4+ files. This would test the coordination hypothesis but is more expensive and complex.

### Proposal 2: Integrate Test Dependency Maps (TDAD-Style Impact Analysis)

**What**: Before dropping a Howler, Gold generates a test dependency map: which source files are covered by which tests. Include this in the Howler drop template as a `## Test Impact Map` section. The Howler uses this to know which tests to run after making changes.

**Expected D3 impact**: +0.5 to +1.0 on the D3 rubric (indirect -- improves benchmark scores). TDAD showed 70% regression reduction. Applied to Spectrum's pipeline, this means fewer "passes locally, fails in integration" outcomes.

**Effort**: Low-Medium (1 week). The dependency map can be generated with static analysis (`pytest --collect-only`, `jest --listTests`, or AST-based import tracing). No protocol changes needed -- it's additional context in the drop template.

**Evidence it works**: TDAD paper (arxiv 2603.17973) demonstrated 70% regression reduction on SWE-bench Verified. The key insight: contextual information (which tests to check) beats procedural mandates (write tests first).

**Implementation**:
- Add a `test_impact_map.py` tool that, given a list of files to modify, returns the set of test files that exercise those files
- Gold runs this during muster and includes the output in each Howler's drop template
- Howlers run these specific tests during completion verification (not just "run all tests")

### Proposal 3: Strengthen Completion Verification with Issue Re-Read (Reflexion)

**What**: After mechanical completion verification (ls, git diff, tsc, tests), add a mandatory "issue re-read" step: the Howler re-reads the original task/issue and writes a 3-5 line assessment of whether the implementation actually resolves the stated problem. If the assessment reveals a gap, the Howler fixes it before declaring done.

**Expected D3 impact**: +0.3 to +0.5. Reflexion-style self-correction is proven to catch logical errors that pass syntactic verification. The improvement is incremental but consistent.

**Effort**: Low (2-3 days). This is a prompt change to the Howler drop template, not a protocol change.

**Evidence it works**: Reflexion achieves 91% on HumanEval vs. 80% for GPT-4 without reflexion. The pattern is well-established across multiple benchmarks. Spectrum already has the infrastructure (scope alignment checks); this extends it to correctness.

**Implementation**: Add to the Howler drop template after completion verification:
```
ISSUE RE-READ: Before declaring done, re-read the original Task above.
Write a 3-5 line assessment: "Does my implementation resolve the stated
problem? What edge cases might I have missed?" If you identify a gap,
fix it before proceeding to quality gates.
```

### Proposal 4: Pre-Implementation Codebase Context Injection

**What**: Before a Howler starts implementing, inject structured codebase context: relevant file contents (not just paths), dependency graphs, and existing patterns in the affected area. This mimics Augment Code's Context Engine approach using Spectrum's existing ARCHITECTURE.md + Gold's file sampling.

**Expected D3 impact**: +0.5 to +1.0. Augment Code's primary accuracy advantage is context quality. Closing this gap on context would close part of the accuracy gap.

**Effort**: Medium (1-2 weeks). Requires Gold to do deeper codebase analysis during muster -- not just "sample 3-5 files" but "read the implementation of every file the Howler will modify and summarize key patterns."

**Evidence it works**: Augment Code attributes its 70.6% score primarily to context quality. SWE-bench Pro research notes that "deep contextual understanding" is the key differentiator for multi-file tasks.

**Implementation**:
- During muster, Gold reads each file in the Howler's MODIFIES list and writes a `## Codebase Context` section in CONTRACT.md per Howler
- Context includes: existing function signatures, patterns used (e.g., "this module uses factory pattern"), naming conventions observed (not just prescribed), and adjacent file summaries
- For SWE-bench: Gold reads the failing test to understand expected behavior, reads the relevant source files, and distills this into structured context

### Proposal 5: White-Before-Implementation (Contract Compliance Pre-Check)

**What**: Run a lightweight White review BEFORE the Howler implements -- reviewing the CONTRACT.md against the codebase to catch stale assumptions, missing files, or incorrect interface specifications. Currently White only runs post-implementation.

**Expected D3 impact**: +0.3 to +0.5. Catches specification errors before they cascade into implementation errors. The MAST taxonomy shows specification issues are a top-3 failure category.

**Effort**: Low-Medium (1 week). White already exists. The change is running it at an additional point in the pipeline with a different prompt (review contract against codebase, not review implementation against contract).

**Evidence it works**: Factory's pipeline uses Spec -> Test -> Implement -> Verify. The spec verification step catches issues before implementation begins. Spectrum's Politico serves a similar role but reviews the contract in isolation (adversarial review of the plan), not against the codebase.

**Implementation**:
- After Gold writes CONTRACT.md, before dropping Howlers, run a "Pre-White" check
- Pre-White reads CONTRACT.md + the actual codebase files referenced in the contract
- Flags: stale function signatures in contract, files that don't exist, interfaces that don't match reality
- Gold updates CONTRACT.md to fix flagged issues before freezing

### Proposal 6: Multi-File Coordination Benchmark (Spectrum-Specific Metric)

**What**: Create a Spectrum-specific benchmark that measures coordination accuracy: given a multi-file task decomposed across N Howlers, what percentage of seams integrate correctly on first merge? This measures what SWE-bench cannot: the accuracy of the coordination protocol itself.

**Expected D3 impact**: +0.5 (indirect). This doesn't improve the SWE-bench score, but it provides an alternative accuracy metric that Spectrum can publish. Combined with a SWE-bench score, it tells a complete story.

**Effort**: Medium-High (3-4 weeks). Requires building a task suite, defining the metric, running multiple spectrum runs, and publishing results.

**Evidence it works**: No competitor publishes coordination-specific accuracy metrics. This would be a first-mover advantage and directly support Spectrum's value proposition (coordination rigor -> accuracy).

**Implementation**:
- Define 10-20 multi-file tasks that require 3-5 Howlers each (e.g., "add auth middleware + API routes + UI components + tests")
- Run each task with Spectrum (full mode) and measure: seam integration success rate, merge conflict rate, post-merge test pass rate, rework rate
- Run the same tasks with uncoordinated parallel agents (no CONTRACT.md, no file ownership) as a baseline
- Publish the comparison: "Spectrum's coordination reduces integration failures by X% compared to uncoordinated parallel agents"

### Proposal 7: LESSONS.md-Driven Pattern Library (Learning Loop)

**What**: Transform LESSONS.md from a retrospective document into an active accuracy tool. Extract recurring failure patterns from past spectrums and inject them as warnings in Howler drop prompts. "In past runs, this type of task commonly fails because X. Watch for Y."

**Expected D3 impact**: +0.2 to +0.3. Marginal per-run improvement, but compounds over time.

**Effort**: Low (3-5 days). LESSONS.md already exists. The change is structured extraction + injection into the drop template.

**Evidence it works**: TDAD showed that contextual information about likely failure modes improves agent accuracy. LESSONS.md is Spectrum's version of episodic memory. Making it active (injected) rather than passive (read on request) follows the same principle.

**Implementation**:
- Add a `## Known Failure Patterns` section to LESSONS.md with structured entries: task type, failure mode, mitigation
- Gold reads this during muster and includes relevant patterns in each Howler's drop template
- Brown updates this section after every spectrum based on what actually failed

---

## Recommended Implementation Order

| Priority | Proposal | D3 Impact | Effort | Rationale |
|----------|----------|-----------|--------|-----------|
| **1** | P1: SWE-bench Pro Evaluation | 2->3 | Medium | **Gate-opener**. Without a published score, nothing else matters for D3. |
| **2** | P3: Issue Re-Read (Reflexion) | +0.3-0.5 | Low | Cheapest accuracy win. 2-3 days, prompt-only change. |
| **3** | P2: Test Dependency Maps | +0.5-1.0 | Low-Med | Proven 70% regression reduction. Directly improves benchmark scores. |
| **4** | P4: Codebase Context Injection | +0.5-1.0 | Medium | Closes the Augment Code context gap. |
| **5** | P5: White Pre-Check | +0.3-0.5 | Low-Med | Catches spec errors before they cascade. |
| **6** | P7: Pattern Library | +0.2-0.3 | Low | Compounds over time. Quick to implement. |
| **7** | P6: Coordination Benchmark | +0.5 | Med-High | Important for narrative but doesn't directly move D3. |

**Critical path**: P1 must happen first. P2 and P3 should be implemented before P1's benchmark run to maximize the score. P4 should be implemented for a second benchmark run if the first score is below target.

---

## Realistic D3 Score Assessment

### What D3=3 Requires
Per the evaluation rubric, D3=3 requires published benchmark evidence showing competitive accuracy. For SWE-bench Pro, this means ~35-40% (which would place Spectrum in the competitive range given the top score is ~46%). For SWE-bench Verified, this means ~72%+ (Claude Sonnet 4.6 alone scores 79.6%, so Spectrum's overhead shouldn't reduce this much).

### What D3=4 Requires
D3=4 requires top-tier published results: 45%+ on Pro or 75%+ on Verified.

### Honest Assessment

**Spectrum can realistically reach D3=3 within 4-6 weeks.** Here's why:

1. Claude Sonnet 4.6 (Spectrum's Howler model) scores 79.6% on SWE-bench Verified as a bare model. Spectrum adds CONTRACT.md, completion verification, and quality gates on top. If these don't reduce accuracy (and they shouldn't -- they're additive checks), Spectrum should score at least 75%+ on Verified.

2. On SWE-bench Pro, the picture is less certain. The coordination overhead (Gold reads issue, writes contract, drops Howler) adds latency and potential for specification drift. But the quality gates (completion verification, Gray test execution) should catch regressions that bare Sonnet misses. A reasonable estimate: 35-42% on Pro.

3. The risk is that Spectrum's muster overhead introduces specification errors that wouldn't exist with a bare agent. Gold might misunderstand the issue and write a contract that leads the Howler astray. This is testable: run with and without CONTRACT.md and compare.

**D3=4 is possible but requires P2+P3+P4 all working together, plus a favorable benchmark run.** The gap between Sonnet's 79.6% Verified and Augment's 70.6% Verified suggests that model quality is already competitive -- the question is whether Spectrum's protocol adds or subtracts from the base model's accuracy.

### The Coordination Hypothesis

The most important finding from this research: **Spectrum's accuracy story is not "we score higher on SWE-bench" but "we prevent the integration failures that multi-agent systems typically suffer."** The MAST taxonomy shows 41-87% failure rates in multi-agent systems. If Spectrum can publish data showing significantly lower failure rates on multi-file tasks, that is a stronger and more defensible accuracy claim than a SWE-bench score alone.

The recommended strategy is dual: publish a SWE-bench score (to get D3=3) AND publish coordination accuracy metrics (to differentiate from every other system on the leaderboard).

---

## What Competitors Do That Spectrum Should Steal

| Technique | Who Uses It | Spectrum Equivalent | Gap |
|-----------|-------------|--------------------|----|
| Semantic codebase indexing | Augment Code | ARCHITECTURE.md | Augment's is automated; Spectrum's is Gold-authored |
| Test-first verification | Factory, TDAD | Gray (post-implementation) | No pre-implementation test targeting |
| Impact analysis maps | TDAD | None | Spectrum has no test-to-source dependency mapping |
| Reflexion/self-correction | Reflexion, multiple | Scope alignment check | Spectrum's checks are compliance-focused, not correctness-focused |
| Spec -> Test -> Implement -> Verify | Factory | Contract -> Implement -> Verify | Missing the "generate tests from spec before implementing" step |
| Hierarchical Planner/Worker/Judge | Google research | Gold/Howler/White | White only judges post-implementation |

The single most impactful technique to adopt is **test dependency mapping** (from TDAD). It is proven, low-effort, and directly compatible with Spectrum's existing pipeline.

---

## Sources

- [SWE-bench Verified Leaderboard - Epoch AI](https://epoch.ai/benchmarks/swe-bench-verified)
- [SWE-bench GitHub Repository](https://github.com/SWE-bench/SWE-bench)
- [SWE-Bench Pro Leaderboard](https://www.morphllm.com/swe-bench-pro)
- [SWE-Bench Pro Paper](https://arxiv.org/abs/2509.16941)
- [Augment Code: #1 open-source agent on SWE-bench Verified](https://www.augmentcode.com/blog/1-open-source-agent-on-swe-bench-verified-by-combining-claude-3-7-and-o1)
- [Augment Code: Auggie tops SWE-Bench Pro](https://www.augmentcode.com/blog/auggie-tops-swe-bench-pro)
- [TDAD: Test-Driven Agentic Development (arxiv 2603.17973)](https://arxiv.org/abs/2603.17973)
- [MAST: Why Do Multi-Agent LLM Systems Fail? (arxiv 2503.13657)](https://arxiv.org/pdf/2503.13657)
- [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
- [Why Multi-Agent Systems Fail: The 17x Error Trap](https://towardsdatascience.com/why-your-multi-agent-system-is-failing-escaping-the-17x-error-trap-of-the-bag-of-agents/)
- [Factory.ai Agent Readiness](https://factory.ai/news/agent-readiness)
- [FeatureBench: Benchmarking Agentic Coding](https://arxiv.org/html/2602.10975v1)
- [Claude-flow SWE-bench Evaluation](https://github.com/ruvnet/claude-flow/wiki/SWE-Bench-Evaluation)
- [TDD for AI Coding: Why It Works](https://codemanship.wordpress.com/2026/01/09/why-does-test-driven-development-work-so-well-in-ai-assisted-programming/)
- [Coordination Gains Plateau Beyond 4 Agents](https://mikemason.ca/writing/ai-coding-agents-jan-2026/)
- [Multi-Agent Coordination Strategies - Galileo](https://galileo.ai/blog/multi-agent-coordination-strategies)
- [SWE-bench Verified Technical Report - Verdent](https://www.verdent.ai/blog/swe-bench-verified-technical-report)
