# Model Routing Optimization Analysis

**Spectrum**: cost-v2-0401
**Howler**: H3-model-routing
**Date**: 2026-04-01
**Sources**: CLAUDE.md model assignments, gold-eval-0331, TOKEN-OPTIMIZATION.md, COST-ANALYSIS.md

---

## Executive Summary

Spectrum's model assignment table (CLAUDE.md) is the single highest-leverage cost control surface. The gold-eval-0331 decision to move Gold from Opus to Sonnet saved ~$2.00 per 5-Howler run (21% of total cost). This document analyzes remaining model routing opportunities: which agents could use cheaper models, where the current assignments leave money on the table, and what trade-offs each change implies.

---

## 1. Current Model Assignment Costs

### Per-Agent Cost Breakdown (5-Howler Reference Run)

| Agent | Model | Invocations | Input Tokens (total) | Output Tokens (total) | Cost | % of Total |
|-------|-------|-------------|---------------------|----------------------|------|------------|
| Gold Muster | Sonnet | 1 | 45,500 | 17,500 | $0.40 | 4.2% |
| Politico | Sonnet | 1 | 10,000 | 2,000 | $0.06 | 0.6% |
| Howlers | Sonnet | 5 | 600,000 | 125,000 | $3.68 | 39.0% |
| White | Sonnet | 5 | 77,500 | 15,000 | $0.46 | 4.9% |
| Gray | Sonnet | 5 | 75,000 | 20,000 | $0.53 | 5.6% |
| /diff-review | Sonnet | 5 | 50,000 | 7,500 | $0.26 | 2.8% |
| Gold Pax | Sonnet | 1 | 64,800 | 8,000 | $0.31 | 3.3% |
| Gray per-merge | Sonnet | 5 | 50,000 | 5,000 | $0.23 | 2.4% |
| Gold self-reflect | Sonnet | 5 | 15,000 | 750 | $0.06 | 0.6% |
| Final Gray | Sonnet | 1 | 13,000 | 2,000 | $0.07 | 0.7% |
| Obsidian | Sonnet | 1 | 27,000 | 4,000 | $0.14 | 1.5% |
| Brown | Haiku | 1 | 32,500 | 3,000 | $0.04 | 0.4% |
| Gold reviews Brown | Sonnet | 1 | 10,000 | 3,000 | $0.08 | 0.8% |
| Copper | Haiku | 5 | 10,000 | 4,000 | $0.02 | 0.2% |
| **TOTAL** | | | | | **$6.34** | **66.9%** |

**Note**: This table reflects Gold on Sonnet (post-gold-eval-0331). The original TOKEN-OPTIMIZATION.md figures used Opus for Gold. Remaining ~$3.09 (33.1%) is from non-agent costs: Blue PLAN.md, infrastructure overhead, and rounding.

**Updated total estimated run cost (Gold on Sonnet)**: ~$6.34 for agent tokens + ~$0.12 for Blue + overhead = ~$6.50-7.00 per 5-Howler run. This is down from ~$9.43 with Gold on Opus.

### Cost Distribution by Model Tier

| Tier | Total Cost | % of Agent Cost |
|------|-----------|-----------------|
| Sonnet agents | $6.28 | 99.1% |
| Haiku agents (Brown, Copper) | $0.06 | 0.9% |

With Gold on Sonnet, the cost structure is radically simplified: **99% of agent cost is Sonnet**. Further optimization requires either (a) moving Sonnet agents to Haiku, or (b) reducing token volume to Sonnet agents.

---

## 2. Agent-by-Agent Haiku Feasibility Analysis

For each Sonnet agent, I assess whether Haiku could perform the task with acceptable quality.

### 2.1 Howlers (39% of cost) -- Haiku: NOT RECOMMENDED

**Task**: Implementation -- write code, create files, modify existing code, follow contract specifications, run type checks and tests.

**Haiku feasibility**: Low. The CLAUDE.md rationale states: "Haiku passes tests but misses architectural intent from the contract." This is empirically validated -- Haiku generates syntactically correct code but:
- Misses subtle contract requirements (e.g., naming conventions, integration point shapes)
- Produces less idiomatic code that is harder to maintain
- Requires more revision passes (increasing total cost)

**Recommendation**: Keep Sonnet. Howlers are the core value creation step. Downgrading them saves $2.49/run but likely increases failure rates and revision costs, making the net savings negative.

### 2.2 White (4.9% of cost) -- Haiku: NOT RECOMMENDED

**Task**: Diff review for blockers, warnings, and suggestions. Requires reasoning about code quality, contract compliance, and subtle bugs.

**Haiku feasibility**: Low-medium. White reviews catch real blockers (per LESSONS remnant-infra-0329: "Inspector caught 3 real blockers"). Haiku would catch obvious issues (syntax errors, missing files) but miss:
- Subtle logic errors in complex diffs
- Contract compliance violations that require understanding the full CONTRACT.md
- Security issues that require reasoning about data flow

**Recommendation**: Keep Sonnet. Quality gate integrity is a core Spectrum differentiator.

### 2.3 Gray (5.6% of cost) -- Haiku: PARTIALLY RECOMMENDED

**Task**: Run tests, diagnose failures, write missing tests.

**Haiku feasibility**: Medium. Gray has two sub-tasks:
1. **Running tests and reporting results**: Mechanical. Haiku can run `pytest` or `jest` and report pass/fail.
2. **Diagnosing failures and writing tests**: Requires reasoning. Haiku misdiagnoses flaky tests and writes superficial coverage.

**Recommendation**: Split Gray into two tiers:
- **Gray-run (Haiku)**: Execute test suite, report pass/fail, collect coverage numbers. Cost: ~$0.01 per invocation vs. $0.11.
- **Gray-diagnose (Sonnet)**: Only invoked when Gray-run reports failures. Diagnose root cause, write missing tests.

**Expected outcome**: 70% of Gray invocations are pass (no failures to diagnose). Those 70% could run on Haiku.

**Estimated savings**: 7 of 10 Gray invocations (5 per-Howler + 5 per-merge) on Haiku: 7 x ($0.11 - $0.01) = $0.70 saved. Remaining 3 on Sonnet: no change.

### 2.4 /diff-review (2.8% of cost) -- Haiku: RECOMMENDED

**Task**: Security-focused differential review of code changes. Checks against a structured checklist: secrets exposure, injection vulnerabilities, auth bypass, dependency risks.

**Haiku feasibility**: Medium-high. Security diff review against a checklist is a structured task:
- Input: git diff + security checklist
- Output: findings report (typically "no critical issues" for most Howlers)
- Reasoning depth: Low to medium -- pattern matching against known vulnerability patterns

**Risk**: Haiku may miss subtle security issues that require cross-file reasoning. However, White already catches most reasoning-dependent issues. /diff-review is a specialized secondary gate.

**Recommendation**: Move to Haiku. If a Howler touches auth/session/external API code (security_gate: required per T2-C), escalate that specific /diff-review to Sonnet.

**Estimated savings**: 3-4 of 5 invocations on Haiku: 3.5 x ($0.05 - $0.01) = $0.14 saved.

### 2.5 Gold Self-Reflect (0.6% of cost) -- Haiku: RECOMMENDED

**Task**: Write 3-5 lines after each merge: "PR N merged. TypeScript passes. Watch for X in next merge."

**Haiku feasibility**: High. This is structured journaling, not synthesis. The output is short and follows a template. Already identified as T1-B (downgrade from Opus to Sonnet); with Gold now on Sonnet, the next step is Haiku.

**Recommendation**: Move to Haiku.

**Estimated savings**: 5 x ($0.012 - $0.002) = $0.05. Modest but zero-effort.

### 2.6 Obsidian (1.5% of cost) -- Haiku: NOT RECOMMENDED

**Task**: Verify PLAN.md acceptance criteria against merged code. Produces SENTINEL-REPORT.md.

**Haiku feasibility**: Low-medium. Spec compliance verification requires:
- Reading PLAN.md criteria (structured)
- Reading merged code and determining if criteria are met (reasoning-dependent)
- Producing a compliance assessment with evidence

Haiku could handle criteria that are binary checks ("file X exists", "test suite passes") but would struggle with qualitative criteria ("API follows RESTful conventions", "error handling is comprehensive").

**Recommendation**: Keep Sonnet. Obsidian is the final quality check -- downgrading it undermines the verification chain.

### 2.7 Politico (0.6% of cost) -- Haiku: NOT RECOMMENDED

**Task**: Adversarial review of CONTRACT.md and MANIFEST.md. Finds ownership gaps, contract ambiguities, decomposition flaws.

**Haiku feasibility**: Low. Adversarial reasoning is exactly where model capability matters most. The Politico must think like an attacker finding weaknesses in a plan. Haiku would produce surface-level observations, not genuine adversarial findings.

**Recommendation**: Keep Sonnet.

### 2.8 Summary: Recommended Model Changes

| Agent | Current | Proposed | Savings/Run | Quality Risk |
|-------|---------|----------|-------------|-------------|
| /diff-review (non-security) | Sonnet | Haiku | $0.14 | Low (White still catches reasoning issues) |
| Gray-run (pass cases) | Sonnet | Haiku | $0.70 | None (mechanical test execution) |
| Gold self-reflect | Sonnet | Haiku | $0.05 | None (structured journaling) |
| **Total** | | | **$0.89** | |

---

## 3. Dynamic Model Routing Strategies

### 3.1 Complexity-Based Routing

**Concept**: Before dispatching an agent, estimate task complexity and route to the appropriate model tier.

**Complexity signals available to Gold at dispatch time**:
- **Diff size**: Small diffs (< 50 lines) are lower complexity
- **File count**: Single-file changes are lower complexity
- **File type**: Documentation, configuration, and test files are lower complexity than core business logic
- **Contract complexity**: Howlers with no seam obligations are lower complexity
- **Historical data**: If LESSONS.md records that similar tasks consistently pass quality gates, lower complexity

**Implementation**: Gold tags each agent invocation with `complexity: low/medium/high` at dispatch time. Low-complexity invocations use Haiku; medium and high use Sonnet.

**Estimated savings**: If 30% of all agent invocations are low-complexity and routable to Haiku:
- 30% x $6.28 Sonnet cost x 73% Haiku discount = $1.38 saved
- Realistic estimate (accounting for quality failures): $0.80-1.00 saved

**Impact**: high
**Effort**: Medium -- requires complexity estimation logic in Gold dispatch

### 3.2 Retry Escalation Routing

**Concept**: Start agents on Haiku. If the output fails quality checks, retry on Sonnet. This exploits the fact that many agent tasks (especially mechanical ones) succeed on the first Haiku attempt.

**Trade-off**: Failed Haiku attempts waste tokens. If the failure rate is >30%, retry escalation costs MORE than running Sonnet from the start.

**Break-even analysis**:
- Haiku attempt cost: $0.01-0.02 per invocation
- Sonnet attempt cost: $0.05-0.11 per invocation
- If Haiku succeeds 70%+ of the time: retry escalation saves money
- If Haiku succeeds <50% of the time: retry escalation wastes money

**Recommendation**: Only viable for agents with high Haiku success rates (>70%). /diff-review and Gray-run qualify. White and Howlers do not.

**Estimated savings**: Already captured in the per-agent analysis above.

### 3.3 Cascade Routing (Haiku -> Sonnet -> Opus)

**Concept**: Three-tier routing with escalation at each level:
1. Start with Haiku for all simple/mechanical tasks
2. Escalate to Sonnet for tasks requiring reasoning
3. Escalate to Opus only for tasks where Sonnet demonstrably fails (currently: none identified post-gold-eval)

**Current state**: Spectrum already uses two tiers (Sonnet + Haiku). Adding a third tier (Opus) is not justified by current data -- Sonnet performs at 0.94 composite vs. Opus 1.00 for Gold (the most demanding role). No agent role currently requires Opus.

**Recommendation**: Two-tier routing (Sonnet + Haiku) is sufficient. Three-tier adds complexity without demonstrated benefit.

---

## 4. Per-Spectrum-Mode Routing Profiles

### 4.1 Full Mode (5-8 Howlers)

**Optimal routing**: Current assignments with the three changes from Section 2.8.

| Phase | Agent | Model |
|-------|-------|-------|
| Muster | Gold | Sonnet |
| Politico | Politico | Sonnet |
| Dispatch | Howlers | Sonnet |
| Quality gate | White | Sonnet |
| Quality gate | Gray-run | Haiku |
| Quality gate | Gray-diagnose | Sonnet (on failure only) |
| Quality gate | /diff-review (security) | Sonnet |
| Quality gate | /diff-review (non-security) | Haiku |
| Pax | Gold | Sonnet |
| Post-merge | Gray-run | Haiku |
| Post-merge | Gold self-reflect | Haiku |
| Triumph | Final Gray | Sonnet |
| Triumph | Obsidian | Sonnet |
| Triumph | Brown | Haiku |
| Delivery | Copper | Haiku |

### 4.2 Reaping Mode (3-4 Howlers, Pure-Create)

Reaping mode tasks are simpler (no MODIFIES, no integration). More agents can safely use Haiku:

| Phase | Agent | Model | Change from Full |
|-------|-------|-------|-----------------|
| Muster | Gold | Sonnet | Same |
| Dispatch | Howlers | Sonnet | Same |
| Quality gate | White | **Haiku** | Downgrade (pure-create, no subtle bug risk) |
| Quality gate | Gray-run | Haiku | Same |
| Quality gate | /diff-review | **Skip** | T2-C: pure-create docs have no security surface |
| Post-merge | Gray-run | Haiku | Same |
| Delivery | Copper | Haiku | Same |

**Additional reaping savings**: White on Haiku saves ~$0.27 (3 invocations). /diff-review skip saves ~$0.15 (3 invocations). Total: ~$0.42 on top of full-mode savings.

### 4.3 Nano Mode (2-3 Howlers, Obvious Boundaries)

Nano mode already skips most agents. The remaining cost is dominated by Howlers:

| Phase | Agent | Model | Notes |
|-------|-------|-------|-------|
| Muster | Gold | Sonnet | Minimal (writes NANO-MANIFEST only) |
| Dispatch | Howlers | Sonnet | Core work |
| Delivery | Copper | Haiku | Commit only |

No further model routing optimization is practical -- Howlers must stay on Sonnet, and Gold's muster in nano mode is already minimal.

---

## 5. Cost Impact of Model Routing Changes

### Cumulative Savings Estimate

| Change | Savings/5H Run | Effort | Risk |
|--------|---------------|--------|------|
| Gray split (run on Haiku, diagnose on Sonnet) | $0.70 | Medium | None for pass cases |
| /diff-review on Haiku (non-security) | $0.14 | Low | Low |
| Gold self-reflect on Haiku | $0.05 | Low | None |
| White on Haiku (reaping mode only) | $0.42 (reaping) | Low | Low |
| Complexity-based dynamic routing | $0.80-1.00 | High | Medium |
| **Total (conservative, full mode)** | **$0.89** | | |
| **Total (with reaping optimization)** | **$1.31** | | |
| **Total (with dynamic routing)** | **$1.69-1.89** | | |

### Percentage Impact

- Current 5-Howler cost (Gold on Sonnet): ~$6.50
- Conservative routing savings: $0.89 = **13.7%**
- With reaping optimization: $1.31 = **20.2%**
- With dynamic routing: $1.69-1.89 = **26-29%**

---

## Techniques Transferable to Spectrum -- Summary

| # | Technique | Impact | Savings Est. (5H) | Effort | Already in Backlog? |
|---|-----------|--------|-------------------|--------|-------------------|
| 1 | Gray split (Haiku run / Sonnet diagnose) | high | $0.70 | Medium | No |
| 2 | /diff-review on Haiku (non-security) | medium | $0.14 | Low | Partially (T2-C) |
| 3 | Gold self-reflect on Haiku | low | $0.05 | Low | Partially (T1-B) |
| 4 | White on Haiku (reaping mode) | medium | $0.42 | Low | No |
| 5 | Complexity-based dynamic routing | high | $0.80-1.00 | High | No |
| 6 | Two-tier sufficient (no Opus needed) | validated | ~$2.00 already saved | Done | Yes (gold-eval) |

**Top 3 new opportunities not in existing backlog:**
1. Gray split into Haiku-run + Sonnet-diagnose ($0.70)
2. White on Haiku for reaping-mode pure-create tasks ($0.42)
3. Complexity-based dynamic routing framework ($0.80-1.00 potential)
