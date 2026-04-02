# Architectural Patterns for Cost Optimization

**Spectrum**: cost-v2-0401
**Howler**: H4-arch-patterns
**Date**: 2026-04-01
**Sources**: Spectrum protocol architecture, TOKEN-OPTIMIZATION.md, COST-ANALYSIS.md, swe-bench-prep/cost-model.md

---

## Executive Summary

This document analyzes cost optimization opportunities embedded in Spectrum's architectural decisions -- the structural choices about how phases connect, how agents communicate, and how the pipeline is organized. These are deeper changes than model routing or prompt optimization; they affect the protocol's shape. Each pattern is assessed for cost impact, implementation effort, and quality risk.

---

## 1. Phase Architecture Patterns

### 1.1 Stateless Phase Transitions

**Current architecture**: Gold maintains a conversational session across muster, dispatch, and sometimes Pax. Each phase transition adds to the accumulated context. By Pax time, Gold's context includes muster reasoning, dispatch decisions, and all intermediate state.

**Proposed pattern**: Make each Gold phase a separate, stateless session. Gold reads CHECKPOINT.json + phase-specific artifacts at the start of each phase. No conversational history carries over.

**Cost impact**:
- Gold Muster session: ~45K input tokens (standalone, no accumulated context)
- Gold Dispatch: ~20K input tokens per Howler drop (reads MANIFEST + CONTRACT only)
- Gold Pax: ~65K input tokens (reads all debriefs fresh, no muster/dispatch history)
- **Current**: Muster (45K) + accumulated dispatch (~90K total) + Pax with full history (~100K) = ~235K total Gold input
- **Stateless**: Muster (45K) + dispatch (5 x 20K = 100K) + Pax (65K) = ~210K total Gold input
- **Savings**: ~25K fewer Sonnet input tokens = $0.075

**The real savings are indirect**: Stateless phases prevent Gold from reasoning about irrelevant context from prior phases. This reduces output tokens (less irrelevant reasoning) and improves decision quality (focused context).

**Estimated total savings**: $0.10-0.20 per run (input + output reduction).

**Impact**: medium
**Effort**: Medium -- requires restructuring Gold from a long-running session to phase-gated sessions. CHECKPOINT.json already supports this (it tracks phase state).
**Quality risk**: Low. Each phase reads the same artifacts. The risk is losing "gut feel" that Gold develops from seeing the full muster conversation, but this is outweighed by the benefit of focused context.

### 1.2 Pipeline Short-Circuiting

**Current architecture**: Every spectrum run goes through all phases: Blue -> Muster -> Dispatch -> Quality Gates -> Pax -> Merge -> Triumph. Even reaping and nano modes still traverse most phases (with lighter artifacts).

**Proposed pattern**: Short-circuit the pipeline based on complexity signals detected during muster:

| Signal | Short-circuit action | Savings |
|--------|---------------------|---------|
| All Howlers pure-create, no deps | Skip Politico, simplified Pax | $0.06 + $0.15 = $0.21 |
| Single Howler, S effort | Skip Politico, skip Pax, skip Obsidian | $0.06 + $0.31 + $0.14 = $0.51 |
| Doc-only changes | Skip /diff-review, skip Gray, lightweight White | $0.26 + $0.53 + $0.23 = $1.02 |
| All quality gates pass first time | Skip White re-run | $0.09 per Howler |

**Note**: Nano mode already implements some of these short-circuits. The opportunity is extending them to reaping mode and even partial application in full mode.

**Estimated savings**: $0.20-0.50 per run for typical reaping-eligible spectrums.

**Impact**: medium
**Effort**: Low -- Gold already evaluates these signals during muster. Adding explicit short-circuit rules to SPECTRUM-OPS.md is straightforward.
**Quality risk**: Low for pure-create/doc-only. Medium for applying to full mode (risk of skipping a gate that would have caught an issue).

### 1.3 Deferred Quality Gates

**Current architecture**: Quality gates (White + Gray + /diff-review) run per Howler immediately after completion. For a 5-Howler run, this is 15 quality gate invocations.

**Proposed pattern**: Defer quality gates to after integration (merge all branches, then run quality gates once on the merged result).

**Cost impact**:
- **Current**: 5 White + 5 Gray + 5 /diff-review = 15 invocations = ~$1.25
- **Deferred**: 1 White + 1 Gray + 1 /diff-review = 3 invocations on merged diff = ~$0.35 (larger diff, but only 3 invocations)
- **Savings**: ~$0.90

**Trade-off**: Per-Howler gates catch issues early (cheaper to fix). Deferred gates catch issues late (more expensive to fix, harder to attribute to a specific Howler). The early-catch benefit is highest when Howlers produce interacting code. For pure-create spectrums (reaping mode), deferred gates are safe because there are no integration points.

**Recommendation**: Use deferred gates for reaping and nano mode. Keep per-Howler gates for full mode.

**Impact**: high (reaping/nano), low (full mode)
**Effort**: Medium -- requires restructuring the quality gate phase.
**Quality risk**: Low for reaping/nano (no integration points). High for full mode (defeats early detection).

---

## 2. Communication Architecture Patterns

### 2.1 Structured Discovery Relay

**Current architecture**: When dropping a dependent Howler (like H5-synthesis), Gold compresses completed Howlers' findings into a ~500-token prose brief.

**Proposed pattern**: Replace prose relay with a structured JSON summary generated by each Howler as part of their debrief. Gold passes the JSON directly without re-reading or compressing.

**Cost impact**:
- **Current**: Gold reads N debriefs (~2,500 tokens each) and generates N compressed relays (~500 tokens each). For 4 completed Howlers feeding H5: Gold reads 10,000 input tokens and generates 2,000 output tokens. Cost at Sonnet: $0.060.
- **Structured**: Gold passes pre-generated JSON summaries without reading full debriefs. Gold reads 4 x 300 token JSON = 1,200 input tokens, generates 0 output tokens. Cost: $0.004.
- **Savings**: $0.056 per dependent Howler drop.

**For the broader pattern**: If every debrief included a machine-readable summary, Gold Pax could also read summaries instead of full narratives for initial triage (reading full narratives only for flagged issues). T3-C (Pax debrief compression) proposes this. The structured relay is the implementation mechanism.

**Impact**: low (per-drop), medium (cumulative with Pax)
**Effort**: Low -- add JSON summary to debrief template.
**Quality risk**: None. Gold can still read full debriefs when needed.

### 2.2 Contract Slicing (Per-Howler)

**Current architecture**: Each Howler receives the full CONTRACT.md (~3,500 tokens).

**Proposed pattern**: Already proposed as T2-A. Gold generates a per-Howler contract slice:
1. Shared conventions (always included, ~1,000 tokens)
2. Own preconditions/postconditions (~300-500 tokens)
3. Relevant seams from neighboring Howlers (~200-300 tokens)
4. Total: ~1,500-1,800 tokens (50% reduction)

**Cost impact**: ~1,700 fewer Sonnet input tokens per Howler x 5 = 8,500 tokens = $0.026. Modest per run.

**Impact**: low
**Effort**: Low
**Quality risk**: Low (with seam bridge).

### 2.3 Eliminate Redundant Artifact Reads

**Current architecture**: Multiple agents read the same artifacts at different phases:
- CONTRACT.md: read by Gold (muster), Politico, each Howler, each White, Gold (Pax) = 12+ reads
- MANIFEST.md: read by Gold, Politico, each Howler (partial), Gold (Pax) = 8+ reads
- HOOK.md: read by Gold (Pax) for each Howler = 5 reads

**Proposed pattern**: Identify which reads are genuinely needed vs. inherited from the protocol template:
- **Howlers need CONTRACT.md**: Yes (contract compliance)
- **White needs CONTRACT.md**: For contract compliance checking, yes. But White could receive a summary instead of the full contract.
- **Politico needs both MANIFEST + CONTRACT**: Yes (adversarial review)
- **Gold Pax re-reads MANIFEST.md**: Unnecessary if CHECKPOINT.json tracks all relevant manifest data.

**Eliminable reads**: Gold Pax re-reading MANIFEST.md (~4,500 Sonnet input tokens), White receiving full CONTRACT.md instead of relevant slice (~2,000 tokens x 5 = 10,000 tokens).

**Estimated savings**: ~14,500 Sonnet input tokens = $0.044. Modest.

**Impact**: low
**Effort**: Low
**Quality risk**: Minimal.

---

## 3. Scale-Dependent Architecture Patterns

### 3.1 Howler Count Optimization (Right-Sizing)

**Current architecture**: The task decomposition determines Howler count. Gold decomposes based on logical task boundaries. There is no explicit cost-aware decomposition.

**Proposed pattern**: Add a cost-aware decomposition step during muster. Gold considers:
- **Merge cost**: Each additional Howler adds ~$0.25 in quality gate overhead + ~$0.10 in merge/integration cost. Total marginal cost per Howler: ~$0.35.
- **Marginal benefit**: A Howler is justified only if it saves more than $0.35 in parallelism benefit (wall-clock time reduction) or enables work that a single Howler cannot complete.
- **Decision rule**: If two tasks could be done sequentially by one Howler in under 30 minutes total, combine them into one Howler. The coordination overhead of two Howlers ($0.70) exceeds the parallelism benefit.

**Example**: In this spectrum run (cost-v2-0401), H1-H4 are four independent research tasks. Each is ~15 minutes. Running them as 4 parallel Howlers costs 4 x $0.41 = $1.64 for Howlers + 4 x $0.25 = $1.00 for quality gates = $2.64. Running them as 2 Howlers (2 topics each) costs 2 x $0.60 = $1.20 + 2 x $0.25 = $0.50 = $1.70. Savings: $0.94, at the cost of ~15 minutes more wall time.

**Impact**: medium-high
**Effort**: Low -- add decision rule to Gold muster instructions.
**Quality risk**: None. Fewer Howlers means less coordination overhead and fewer seam risks.

### 3.2 Adaptive Mode Selection

**Current architecture**: Mode selection (full/reaping/nano) is based on fixed criteria: Howler count, create-vs-modify, and interface dependencies. The human or Gold judges which mode to use.

**Proposed pattern**: Add cost as an explicit input to mode selection:

| Cost Signal | Mode Implication |
|-------------|-----------------|
| Estimated run cost < $3 | Prefer nano mode (coordination overhead dominates) |
| Estimated run cost $3-8 | Prefer reaping mode if criteria met |
| Estimated run cost > $8 | Full mode justified (coordination overhead is proportional) |
| All Howlers effort: S | Prefer nano regardless of count |
| Any Howler effort: L | Full mode (L tasks need stronger contracts) |

**Cost impact**: More aggressive nano/reaping activation reduces coordination overhead by $0.50-2.00 per run when applicable.

**Impact**: medium
**Effort**: Low -- add cost-aware rules to mode selection criteria in CLAUDE.md.
**Quality risk**: Low. The existing mode criteria already capture the quality-relevant signals (create vs. modify, interface deps). Cost is an additional tie-breaker.

### 3.3 Proportional Quality Gate Investment

**Current architecture**: Every Howler gets the same quality gate treatment: White + Gray + /diff-review, regardless of task size or risk.

**Proposed pattern**: Scale quality gate investment proportional to task risk and size:

| Task Profile | Quality Gates | Savings vs. Full |
|-------------|---------------|-----------------|
| S effort, pure-create, no security | Gray-run (Haiku) only | $0.20/Howler |
| M effort, pure-create, no security | White (Haiku) + Gray-run (Haiku) | $0.15/Howler |
| M effort, MODIFIES, no security | White (Sonnet) + Gray (Sonnet) | $0.05/Howler |
| Any effort, security surface | Full triple gate (Sonnet) | $0.00 (baseline) |
| L effort, complex integration | Full triple gate + extended White | -$0.09 (extra cost) |

**Estimated savings**: For a typical 5-Howler reaping run (S-M effort, pure-create): ~$0.50-0.75.

**Impact**: medium-high
**Effort**: Medium -- requires Gold to tag each Howler with a quality gate profile during muster.
**Quality risk**: Low-medium. The risk is under-gating a task that turns out to be more complex than estimated. Mitigated by the "any security surface = full gate" rule.

---

## 4. Token Flow Architecture

### 4.1 Read-Once Architecture

**Current architecture**: Agents re-read the same files across turns within a session. A Howler might read CONTRACT.md three times (dispatch, alignment check, completion verification).

**Proposed pattern**: Instruct agents to read artifacts exactly once (at session start) and reference the cached content thereafter. Add to the Howler drop template: "Read CONTRACT.md and HOWLER-OPS.md once at the start. Do not re-read unless you encounter a discrepancy. Reference these documents from memory for subsequent checks."

**Cost impact**: Eliminates ~2,000-3,000 tokens of redundant reads per Howler (tool call overhead + response injection). 5 Howlers: ~10,000-15,000 Sonnet input tokens saved = $0.03-0.05.

**Impact**: low
**Effort**: Low (prompt instruction change).
**Quality risk**: Minimal. If compaction has not occurred, the agent still has the content in context.

### 4.2 Output Budget Enforcement

**Current architecture**: No per-agent output budget. Agents generate as many output tokens as needed. Gold's conciseness directive (T1-E) is instructional, not enforced.

**Proposed pattern**: Set explicit output token budgets per agent type using the `max_tokens` API parameter:

| Agent | Current Avg Output | Proposed Budget | Headroom |
|-------|-------------------|-----------------|----------|
| Gold Muster | 17,500 | 20,000 | 14% |
| Howler | 25,000 | 30,000 | 20% |
| White | 3,000 | 4,000 | 33% |
| Gray | 4,000 | 5,000 | 25% |
| /diff-review | 1,500 | 2,000 | 33% |
| Gold Pax | 8,000 | 10,000 | 25% |
| Copper | 800 | 1,500 | 88% |

**Cost impact**: Prevents token runaway. Current estimates are averages; some sessions produce 2-3x average output. Budget enforcement caps the tail.

**Estimated savings**: Prevents the worst-case scenarios. If 10% of sessions produce 2x average output, budgets save: 10% x excess tokens x price = ~$0.10-0.20 per run.

**Impact**: low-medium
**Effort**: Low if Claude Code exposes `max_tokens` per session.
**Quality risk**: Low with adequate headroom (20%+). Risk of truncation if budgets are too tight.

### 4.3 Artifact Size Limits

**Current architecture**: No size limits on spectrum artifacts (MANIFEST.md, CONTRACT.md, HOOK.md, debriefs). These grow with spectrum complexity.

**Proposed pattern**: Set target size limits:

| Artifact | Target Size | Enforcement |
|----------|-------------|-------------|
| MANIFEST.md | 5,000 tokens max | Gold instruction |
| CONTRACT.md (full) | 4,000 tokens max | Gold instruction |
| CONTRACT.md (reaping) | 2,000 tokens max | Gold instruction |
| HOOK.md | 2,000 tokens max (at completion) | Howler instruction |
| Debrief | 2,500 tokens max | Howler instruction |
| Discovery relay | 500 tokens max (already specified) | Gold instruction |

**Cost impact**: Prevents artifact bloat that cascades through downstream reads. If CONTRACT.md grows to 6,000 tokens (happened in complex spectrums), every Howler and White reads the excess. 5 Howlers + 5 Whites = 10 reads x 2,500 excess = 25,000 extra Sonnet input tokens = $0.075.

**Impact**: low-medium (prevents worst cases)
**Effort**: Low (instruction changes).
**Quality risk**: Minimal if limits have adequate headroom.

---

## 5. Cost-Aware Architecture Decisions

### 5.1 The Coordination Tax Formula

Based on TOKEN-OPTIMIZATION.md and COST-ANALYSIS.md data, the coordination tax per Howler can be precisely quantified:

```
Coordination tax per Howler = 
  Gold dispatch overhead ($0.08) +
  Quality gates ($0.25) +
  Gold Pax per-Howler read ($0.04) +
  Per-merge Gray ($0.05) +
  Gold self-reflect ($0.01) +
  Copper ($0.004) = $0.434 per Howler
```

**This means**: Every Howler must deliver at least $0.43 of value (parallelism benefit, quality improvement, or risk reduction) to justify its existence. For a Howler that takes 15 minutes and costs $0.41 in direct execution, the total cost is $0.41 + $0.43 = $0.84.

**Decision rule**: If a task can be appended to an existing Howler without adding more than 10 minutes of execution time, it should be. The marginal cost of extra work in an existing Howler (~$0.10 for 10 min of Sonnet) is far less than the coordination tax of a new Howler ($0.43).

### 5.2 Break-Even Analysis: When to Use Spectrum

| Scenario | Bare Sonnet Cost | Spectrum Cost | Break-Even? |
|----------|-----------------|---------------|-------------|
| 1 task, 15 min | $0.23 | $0.57 (Variant A) | No -- bare Sonnet wins |
| 1 task, 60 min | $0.92 | $1.05 (Variant A) | Marginal -- quality gates may justify |
| 3 tasks, 15 min each, independent | $0.69 (serial, 45 min) | $1.71 (3H reaping, 15 min) | Yes if wall-clock matters |
| 5 tasks, 15 min each, independent | $1.15 (serial, 75 min) | $2.85 (5H reaping, 15 min) | Yes for parallelism |
| 5 tasks, 15 min each, 2 deps | $1.15 (serial, 75 min) | $3.50 (5H full, 30 min) | Yes for parallelism + contracts |

**Key insight**: Spectrum's cost premium is justified by either (a) wall-clock time savings from parallelism or (b) quality assurance from contracts and gates. If neither applies (single sequential task with low risk), bare Sonnet is cheaper.

---

## Techniques Transferable to Spectrum -- Summary

| # | Technique | Impact | Savings Est. (5H) | Effort | Already in Backlog? |
|---|-----------|--------|-------------------|--------|-------------------|
| 1 | Cost-aware Howler count optimization | medium-high | $0.50-1.00 | Low | No |
| 2 | Proportional quality gate investment | medium-high | $0.50-0.75 | Medium | Partially (T2-C) |
| 3 | Deferred quality gates (reaping/nano) | high | $0.90 (reaping) | Medium | No |
| 4 | Pipeline short-circuiting | medium | $0.20-0.50 | Low | Partially (nano mode) |
| 5 | Stateless phase transitions | medium | $0.10-0.20 | Medium | No |
| 6 | Adaptive cost-aware mode selection | medium | $0.50-2.00 | Low | No |
| 7 | Coordination tax formula (decision rule) | medium | Prevents waste | Low | No |
| 8 | Artifact size limits | low-medium | $0.05-0.10 | Low | No |
| 9 | Output budget enforcement | low-medium | $0.10-0.20 | Low | No |
| 10 | Read-once architecture | low | $0.03-0.05 | Low | No |

**Top 3 new opportunities not in existing backlog:**
1. Cost-aware Howler count optimization with coordination tax formula ($0.50-1.00)
2. Deferred quality gates for reaping/nano mode ($0.90)
3. Proportional quality gate investment by task profile ($0.50-0.75)
