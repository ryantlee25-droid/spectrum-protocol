# Cost & Speed Model: Spectrum on SWE-bench Pro

**Spectrum**: swe-bench-prep-0401
**Howler**: H4 — Cost & Speed Modeler
**Date**: 2026-03-31
**Precondition**: H3 HOOK.md shows `Checkpoints.types: STABLE` — variant definitions finalized in `pipeline-design.md`

---

## 1. Pricing Reference

All calculations use Claude API list prices as of March 2026.

| Model | Input (per M tokens) | Output (per M tokens) |
|-------|---------------------|----------------------|
| Sonnet | $3.00 | $15.00 |
| Haiku | $0.80 | $4.00 |

**Sonnet per-token costs**: $0.003/K input, $0.015/K output

---

## 2. Per-Task Token Breakdown by Variant

Derived from H3's per-step estimates in `pipeline-design.md`. All token counts in thousands (K).

### Variant A — Full Spectrum

| Step | Agent | Input (K) | Output (K) | Input Cost | Output Cost | Step Total |
|------|-------|-----------|------------|------------|-------------|------------|
| A1: Issue ingestion + mini-CONTRACT | Gold (Sonnet) | 18.0 | 2.5 | $0.054 | $0.038 | $0.092 |
| A2: White Pre-Check | White (Sonnet) | 8.0 | 0.8 | $0.024 | $0.012 | $0.036 |
| A3: Howler implementation | Howler (Sonnet) | 60.0 | 8.0 | $0.180 | $0.120 | $0.300 |
| A4a: White (triple gate) | White (Sonnet) | 10.0 | 1.5 | $0.030 | $0.023 | $0.053 |
| A4b: Gray (triple gate) | Gray (Sonnet) | 8.0 | 2.0 | $0.024 | $0.030 | $0.054 |
| A4c: /diff-review (triple gate) | Sonnet | 6.0 | 0.8 | $0.018 | $0.012 | $0.030 |
| A5: Copper patch submission | Copper (Haiku) | 1.5 | 0.3 | $0.001 | $0.001 | $0.002 |
| **TOTAL — Variant A (happy path)** | | **111.5K** | **15.9K** | **$0.331** | **$0.236** | **$0.567** |

*Rounded to $0.57/task in budget tables.*

### Variant B — Lite Spectrum

| Step | Agent | Input (K) | Output (K) | Input Cost | Output Cost | Step Total |
|------|-------|-----------|------------|------------|-------------|------------|
| B1: Compact task brief | Gold (Sonnet) | 4.5 | 0.3 | $0.014 | $0.005 | $0.019 |
| B2: Howler implementation | Howler (Sonnet) | 55.0 | 7.0 | $0.165 | $0.105 | $0.270 |
| B3a: White (double gate) | White (Sonnet) | 9.0 | 1.2 | $0.027 | $0.018 | $0.045 |
| B3b: Gray (double gate) | Gray (Sonnet) | 8.0 | 2.0 | $0.024 | $0.030 | $0.054 |
| B4: Copper patch submission | Copper (Haiku) | 1.5 | 0.3 | $0.001 | $0.001 | $0.002 |
| **TOTAL — Variant B (happy path)** | | **78.0K** | **10.8K** | **$0.231** | **$0.159** | **$0.390** |

*Rounded to $0.38/task in budget tables.*

### Variant C — Bare Sonnet

| Step | Agent | Input (K) | Output (K) | Input Cost | Output Cost | Step Total |
|------|-------|-----------|------------|------------|-------------|------------|
| C1: Implementation session | Sonnet | 40.0 | 7.0 | $0.120 | $0.105 | $0.225 |
| C2: Patch extraction | Script | — | — | $0.000 | $0.000 | $0.000 |
| **TOTAL — Variant C (happy path)** | | **40.0K** | **7.0K** | **$0.120** | **$0.105** | **$0.225** |

*Rounded to $0.23/task in budget tables.*

### Token Overhead Summary

| Variant | Total Tokens | vs. Variant C | Cost | vs. Variant C |
|---------|-------------|---------------|------|---------------|
| C (Bare Sonnet) | 47.0K | 1.0× | $0.23 | 1.0× |
| B (Lite Spectrum) | 88.8K | 1.9× | $0.38 | 1.65× |
| A (Full Spectrum) | 127.4K | 2.7× | $0.57 | 2.48× |

*Note: Token overhead ratio (1.9×, 2.7×) differs from wall-clock overhead ratio because wall-clock time is bounded by serial dependencies, not total token volume.*

---

## 3. Run Scenario Cost Models

### Scenario Definitions

| Scenario | Description | Variant A Tasks | Variant B Tasks | Variant C Tasks | Total API Calls |
|----------|-------------|-----------------|-----------------|-----------------|-----------------|
| **Minimum viable** | Small exploratory run | 0 | 50 | 50 | 100 |
| **Recommended** | Balanced evaluation with A subset | 15 | 50 | 50 | 115 |
| **Full** | High-confidence evaluation | 30 | 100 | 100 | 230 |

### Scenario Cost Breakdown

#### Scenario 1 — Minimum Viable (100 API calls)

| Component | Tasks | Cost/Task | Total |
|-----------|-------|-----------|-------|
| Variant B (Lite Spectrum) | 50 | $0.38 | $19.00 |
| Variant C (Bare Sonnet) | 50 | $0.23 | $11.50 |
| Docker compute (see §3.1) | 100 tasks | ~$0.03 | $3.00 |
| **TOTAL** | | | **$33.50** |

#### Scenario 2 — Recommended (115 API calls)

| Component | Tasks | Cost/Task | Total |
|-----------|-------|-----------|-------|
| Variant A (Full Spectrum) | 15 | $0.57 | $8.55 |
| Variant B (Lite Spectrum) | 50 | $0.38 | $19.00 |
| Variant C (Bare Sonnet) | 50 | $0.23 | $11.50 |
| Docker compute | 115 tasks | ~$0.03 | $3.45 |
| **TOTAL** | | | **$42.50** |

#### Scenario 3 — Full (230 API calls)

| Component | Tasks | Cost/Task | Total |
|-----------|-------|-----------|-------|
| Variant A (Full Spectrum) | 30 | $0.57 | $17.10 |
| Variant B (Lite Spectrum) | 100 | $0.38 | $38.00 |
| Variant C (Bare Sonnet) | 100 | $0.23 | $23.00 |
| Docker compute | 230 tasks | ~$0.03 | $6.90 |
| **TOTAL** | | | **$85.00** |

### 3.1 Docker Compute Cost

SWE-bench Pro requires running full test suites in isolated Docker containers. Containers are pre-built per-repo by the harness; the cost is compute time, not build time.

**Estimate basis:**
- Average task wall-clock time including test execution: ~20–30 minutes
- Typical cloud VM rate for a 4-core instance adequate for Python test suites: ~$0.05–$0.10/hour
- Cost per task: ~$0.017–$0.050; using $0.03 as central estimate

This estimate assumes running on a single developer-tier cloud instance (e.g., AWS t3.xlarge at ~$0.166/hr, one task at a time). Parallel execution on larger instances improves throughput but the per-task compute cost is roughly constant. Docker compute is a small fraction of total cost (<10% in all scenarios).

---

## 4. Wall-Clock Time Model

### Per-Task Timing by Variant

H3 provides the wall-clock breakdown per step. Times below are per-task, single-task serial execution.

| Variant | Gold/Brief | White Pre-Check | Howler Impl | Quality Gate | Copper | Total |
|---------|-----------|-----------------|-------------|--------------|--------|-------|
| A (Full Spectrum) | ~5 min | ~3 min | ~15–25 min | ~8 min (parallel) | ~1 min | **~32–42 min** |
| B (Lite Spectrum) | ~2 min | — | ~15–25 min | ~5 min (parallel) | ~1 min | **~23–33 min** |
| C (Bare Sonnet) | — | — | ~18–25 min | — | <1 min | **~18–26 min** |

**Wall-clock overhead ratios** (using midpoint estimates):

| Variant | Midpoint Wall-Clock | Overhead Ratio vs. C |
|---------|--------------------|-----------------------|
| C | ~22 min | 1.0× (baseline) |
| B | ~28 min | ~1.3× |
| A | ~37 min | ~1.7× |

*These ratios are lower than H3's range estimates (1.4–1.6× for B, 2.0–2.5× for A) because this model uses midpoint wall-clock estimates. H3's stated ratios reflect the range. At worst case (short Howler, long overhead), A approaches 2.5×; at best case (long Howler, fast overhead), A approaches 1.5×.*

### Total Run Time by Scenario

Run time depends critically on the parallelization strategy. Two models:

**Sequential** (one task at a time): impractical for >10 tasks; included for reference.

**Parallel batch** (N tasks running concurrently): the practical model. Each "batch" is a set of tasks started simultaneously. Wall-clock = (total tasks / batch size) × per-task time.

| Scenario | Tasks | Batch Size | Per-Task (avg) | Total Wall-Clock |
|----------|-------|------------|----------------|------------------|
| Minimum viable | 100 | 10 | ~25 min | **~4.2 hours** |
| Minimum viable | 100 | 20 | ~25 min | **~2.1 hours** |
| Recommended | 115 | 10 | ~27 min | **~5.2 hours** |
| Recommended | 115 | 20 | ~27 min | **~2.6 hours** |
| Full | 230 | 20 | ~27 min | **~5.2 hours** |
| Full | 230 | 40 | ~27 min | **~2.6 hours** |

*Batch size is constrained by API rate limits and available Docker container slots, not cost. With a 20-task batch, the recommended scenario completes in under 3 hours.*

**Key observation**: Total wall-clock scales linearly with tasks and inversely with batch size. A 50-task Variant B run at batch size 10 takes ~2 hours. Increasing to batch size 20 halves the time but does not change cost. Parallelization is essentially free — the bottleneck is the Docker harness slots available, not API concurrency.

### Overhead Ratio: The Real Question

The overhead ratio matters for two different questions:

1. **"Is Spectrum too slow for my evaluation timeline?"** — Answer: No. Even at 1.7× overhead for Variant A, a 50-task run completes in 1.5–3 hours at batch size 10–20. This is acceptable for an evaluation context.

2. **"Does the overhead pay for itself in accuracy?"** — This is the cost-effectiveness question, addressed in §6.

---

## 5. Sensitivity Analysis

### 5.1 Revision Pass Impact

Variant C embeds a single retry; Variants A and B allow up to 2 revision passes. When the Howler hits revision passes, the effective token cost increases.

**Revision pass token cost model:**
- Each revision pass re-reads test output (~1K tokens) and re-implements (~5K output tokens)
- Approximate cost per revision pass: $0.078 (Sonnet: 1K in × $0.003 + 5K out × $0.015)
- This cost is incremental — added only when revision occurs

| Revision Rate | Variant A adj. | Variant B adj. | Variant C adj. |
|---------------|---------------|---------------|---------------|
| 0% (no revisions) | $0.57 | $0.38 | $0.23 |
| 30% (1 revision on 30% of tasks) | $0.59 | $0.40 | $0.25 |
| 60% (1 revision on 60% of tasks) | $0.62 | $0.43 | $0.28 |
| 30% (2 revisions on 30% of tasks) | $0.61 | $0.42 | $0.25 |

**Finding**: Revision passes add at most $0.05–$0.10/task at realistic revision rates (30–60%). This is a rounding error relative to base task cost. Revision pass costs are not a meaningful budget risk.

### 5.2 Failure Rate Impact

"Failure" here means the Howler session terminates without producing a patch (context exhaustion, API error, environment failure). This is distinct from producing a patch that fails the harness.

**Cost model for session failures:**
- If a session fails mid-way, approximately 50% of expected tokens were consumed (conservative estimate)
- Failed sessions must be retried; retry cost = full base cost

| Failure Rate | Scenario 2 (Recommended) effective cost |
|---|---|
| 0% (no failures) | $42.50 |
| 5% failure rate | $44.61 (5% tasks retry at full base cost + partial consumed tokens) |
| 10% failure rate | $47.72 |
| 15% failure rate | $50.83 |

**Finding**: At realistic session failure rates (5–10%), total run cost increases by 5–12%. The recommended scenario budget should include a 10–15% buffer for retries: **$47–49 for the recommended scenario** rather than $42.50.

### 5.3 Quality Gate Iteration Impact

When White or Gray finds blockers and the Howler must fix and re-run, each White re-run costs ~$0.03–0.04. In practice, multi-pass quality gate iterations are rare on focused single-issue fixes (estimated <15% of tasks), and the incremental cost is small:

- One additional White re-run: +$0.04
- Impact across 50 tasks at 15% rate: +$0.30 total run cost

Quality gate iteration is not a material budget driver.

### 5.4 Parallelization and Batch Size

| Batch Size | Recommended Scenario Wall-Clock | Cost Impact |
|---|---|---|
| 5 concurrent | ~5.2 hours | No cost change |
| 10 concurrent | ~2.6 hours | No cost change |
| 20 concurrent | ~1.3 hours | No cost change |
| API rate limit hit | Retries at 1–2 min delay | +1–3% cost |

API cost is independent of parallelization. The only risk is API rate limit throttling on high-batch runs, which adds latency but negligible cost.

---

## 6. Competitor Cost Comparison

### 6.1 Published and Estimated Per-Task Costs

From H5's competitive-intel.md (all figures are estimates; no competitors publish per-task API costs):

| System | Est. Cost/Task | Score (Verified) | Score (Pro) | Cost Basis |
|--------|---------------|------------------|-------------|------------|
| Augment Code / Auggie | $6–35 | 70.6% | 51.80% (#1) | Agent loop (1–3.5M tokens) + o1 ensembler |
| Amazon Q Developer | $15–50 | 66% | N/A | Multi-candidate, 3–5 passes |
| Factory Droids | $10–40 | 31.67% (Lite) | N/A | TDD loop, 3–6 Droid passes |
| Claude-flow (8-agent mesh) | $20–80 | ~85% (Lite, unverified) | N/A | 8× agent coordination cost |
| Single-agent Sonnet | $1–5 | ~35–45% (estimate) | ~20–30% | 1–3.5M tokens × $3/M |
| **Variant C (Bare Sonnet)** | **$0.23** | TBD | TBD | 47K tokens at Sonnet rates |
| **Variant B (Lite Spectrum)** | **$0.38** | TBD | TBD | 88.8K tokens at Sonnet rates |
| **Variant A (Full Spectrum)** | **$0.57** | TBD | TBD | 127.4K tokens at Sonnet rates |

**The cost gap is striking.** This spectrum's Variant C at $0.23/task is 4–20× cheaper than competitor single-agent estimates ($1–5/task) for what should be a comparable Sonnet implementation. The discrepancy requires scrutiny.

### 6.2 Reconciling the Cost Gap

**Why Spectrum's estimate is lower than competitor estimates:**

The competitor estimates ($1–5/task for single-agent Sonnet) assume 1–3.5 million tokens per task, while Variant C estimates 47K tokens. This is a 20–75× difference in token volume. The gap likely comes from:

1. **Multi-turn agentic loops**: Competitors run long agentic sessions with tool-calling loops — read file, observe, write, run test, observe, repeat. Each tool call adds input context (the growing conversation history). A 50-turn session with 2K context per turn = 100K tokens minimum just from conversation growth, before any source files are read.

2. **Full test suite execution**: Competitors run complete project test suites and read the output. A Django test suite output can be 50K+ tokens alone.

3. **Codebase indexing**: Systems with semantic retrieval read many files during indexing. Augment's Context Engine processes the entire codebase.

4. **Our Variant C is optimistic**: The 40K input token estimate for Variant C assumes a disciplined single-session prompt with targeted file reads. A real agentic SWE-bench session will likely accumulate more context. A more realistic estimate for Variant C in practice is **100–200K tokens** ($0.60–$1.50/task), which aligns with the lower end of competitor estimates.

**Revised realistic cost estimates (marked as such throughout):**

| Variant | Optimistic (H3 estimate) | Realistic (adjusted) | Conservative (upper bound) |
|---------|--------------------------|---------------------|---------------------------|
| C (Bare Sonnet) | $0.23 | $0.75 | $1.50 |
| B (Lite Spectrum) | $0.38 | $1.10 | $2.00 |
| A (Full Spectrum) | $0.57 | $1.60 | $3.00 |

The H3 estimates represent minimum viable token usage with disciplined context management. The realistic estimates assume a production agentic loop. The conservative estimates assume long-horizon agentic exploration with some backtracking.

**For scenario planning, this document presents both the H3 (optimistic) and realistic estimates.** The optimistic figures are used in the standard scenario tables; realistic adjustments are shown in §6.3.

### 6.3 Run Scenarios at Realistic Costs

| Scenario | Tasks | Optimistic (H3) | Realistic | Conservative |
|----------|-------|-----------------|-----------|--------------|
| Minimum viable | 100 | $33.50 | $100 | $180 |
| Recommended | 115 | $42.50 | $126 | $225 |
| Full | 230 | $85.00 | $252 | $450 |

Even at realistic estimates, a 115-task run costs ~$126. This remains dramatically lower than a Augment-style run (115 tasks × $20 avg = $2,300).

---

## 7. Cost-Effectiveness Analysis

### 7.1 Cost Per SWE-bench Pro Point

This metric measures how many dollars it costs to earn one percentage point of accuracy on SWE-bench Pro.

**Setup**: For a 50-task evaluation run (10% coverage of 500-task Pro set), accuracy is measured as percent of 50 tasks resolved.

Using H5's projected score range for Spectrum (18–30% Pro, §6 of competitive-intel.md):

| Variant | Cost (50 tasks, optimistic) | Cost (50 tasks, realistic) | Projected Pro Score | $/Pro-point (optimistic) | $/Pro-point (realistic) |
|---------|------------------------------|---------------------------|---------------------|--------------------------|-------------------------|
| C | $11.50 | $37.50 | ~18–22% | $0.52–$0.64 | $1.70–$2.08 |
| B | $19.00 | $55.00 | ~20–25% | $0.76–$0.95 | $2.20–$2.75 |
| A | $8.55 (15 tasks) | $24.00 | ~22–28% (hard tasks) | (15-task subset; not comparable) | |

*Note: "$/Pro-point" is cost per percentage point of accuracy on the 50-task subset. At 10% coverage, each percentage point on the subset corresponds to 0.1 percentage points on the full Pro leaderboard.*

**Normalized cost per full-leaderboard Pro point** (50-task run, scaling to 500-task equivalent):

| Variant | Realistic cost per Pro-leaderboard point |
|---------|----------------------------------------|
| C | $17–$21 |
| B | $22–$28 |
| A | (subset only; not directly comparable) |

For comparison, Augment's estimated cost to run 500 tasks: $10,000–$17,500. If Augment scores 51.80%, their cost per Pro point = $193–$338. Spectrum's Variant C at realistic costs is **10–20× more cost-efficient per Pro point** — even if it scores far lower in absolute terms.

### 7.2 Break-Even Analysis: When Does Spectrum's Overhead Justify Its Cost?

The question: at what accuracy improvement does Variant B's coordination overhead (cost premium over Variant C) justify itself?

**Cost premium model** (realistic estimates):
- Variant C: $0.75/task
- Variant B: $1.10/task
- Premium: $0.35/task = 47% cost premium

**Break-even in tasks resolved:**
- A 50-task run at Variant C resolves an expected ~9–11 tasks (18–22% Pro score)
- Variant B must resolve at least 1 additional task per 50 to justify the extra $17.50 (50 × $0.35)
- That is an accuracy gain of 2 percentage points (1 additional task out of 50)

**The break-even threshold is very low.** If Variant B's I1 (Issue Re-Read) and I6 (Revision Pass) improvements together recover even a single additional task per 50, the coordination overhead pays for itself. This is a plausible outcome — Issue Re-Read alone has been shown to recover tasks where the initial patch was directionally correct but missed an edge case in the issue description.

**For Variant A vs. Variant C** (realistic estimates):
- Variant A: $1.60/task, Variant C: $0.75/task, premium: $0.85/task (113%)
- On a 15-task Variant A run: must resolve ~2 additional tasks vs. Variant C to break even
- That is ~13 percentage points better accuracy on the hard task subset

This is a substantially higher bar. Variant A is only worth its overhead if it demonstrably improves accuracy on complex multi-file tasks by 10+ points. This is uncertain — the break-even analysis is the primary reason Variant B is the recommended primary condition rather than Variant A.

### 7.3 Marginal Cost of Additional Tasks

As a run scales from 50 to 100 to 500 tasks, fixed costs (harness setup, Docker environment build) become proportionally smaller. The marginal cost of each additional task is approximately constant at the per-task API cost plus compute.

**Statistical significance threshold:**
- To detect a 5 percentage point accuracy difference (e.g., 20% vs. 25%) with 80% power at p=0.05, approximately 380 tasks are needed (standard chi-squared power analysis).
- To detect a 10 point difference: approximately 95 tasks.
- To detect a 15 point difference: approximately 43 tasks.

**Implication**: The 50-task run per variant (Minimum Viable scenario) can only reliably detect accuracy differences of ~15 points or larger. If Variant B outperforms Variant C by 7–10 points, a 50-task run may not reach statistical significance. The Recommended scenario (50+50+15) is the minimum for a publishable comparison between B and C.

---

## 8. Budget Recommendation

### 8.1 Minimum Budget for a Publishable D3=3 Score

The D3=3 target (three-digit score on SWE-bench Pro, i.e., ≥10%) requires resolving at least 50 tasks from the 500-task Pro set. This is the minimum to appear on the leaderboard as a non-trivial result.

**Minimum run for a D3=3-equivalent result:**
- 50 tasks at Variant C to establish the baseline
- H5 projects 18–22% Pro score for Variant C, which corresponds to 9–11 tasks resolved out of 50
- This is well above the 5% threshold for D3=3 on a 50-task run, but 50 tasks is 10% coverage

**However**: the SWE-bench Pro leaderboard scores are over 500 tasks. A 50-task run produces a 50-task accuracy figure, not a leaderboard entry. To submit to the leaderboard, all 500 tasks must be attempted.

**A publishable result** in the sense of "credible evidence for a conference/blog post" (not a leaderboard submission) requires:
- Variant C + Variant B on the same 50-task subset: ~$91 realistic total
- Or the Minimum Viable scenario at realistic costs: ~$100

**For a leaderboard-submittable result (500 tasks, single variant):**
- 500 tasks × $0.75 realistic (Variant C) = $375 + $15 compute = ~$390
- 500 tasks × $1.10 realistic (Variant B) = $550 + $15 compute = ~$565

### 8.2 Budget Tiers

| Budget | What you get | Recommended allocation |
|--------|-------------|----------------------|
| **$50** | Proof of concept only. 30–40 tasks total. Accuracy estimate with ±15 pt margin of error. Not publishable. | 20× Variant B + 20× Variant C |
| **$100** | Minimum viable evaluation. 100 tasks (50 B + 50 C). Can detect ≥15 pt difference between variants. Publishable as a blog post. | Minimum Viable scenario |
| **$150–200** | Recommended evaluation. Includes 15-task Variant A subset on hardest tasks. Adequate to compare all three variants, detect ≥10 pt differences. | Recommended scenario + 10% retry buffer |
| **$500** | Full 100-task run (100 B + 100 C + 30 A). Statistical power to detect 5–8 pt differences. Strong foundation for a paper or leaderboard submission pilot. | Full scenario |
| **$1,000–2,000** | 500-task run (single variant). Full leaderboard submission. | 500× Variant B or equivalent |

### 8.3 Recommended Budget and Strategy

**Recommended budget: $150–200 (realistic estimate)**

This covers the Recommended scenario (50 B + 50 C + 15 A) with a 15% retry buffer. It provides:
- A defensible comparison between Variant B and Variant C
- An initial signal on whether Full Spectrum (Variant A) helps on complex multi-file tasks
- Enough tasks to detect a 10 pt accuracy difference with 80% power
- A publishable result for an internal evaluation report or blog post

**Run strategy:**
1. Run Variant C (50 tasks) first — this is the fastest and cheapest. Establishes the baseline.
2. Run Variant B on the same 50 tasks — same task set is critical for a valid comparison.
3. After reviewing B vs. C results, decide whether to run Variant A on the 15 hardest tasks (4+ files changed). If B already beats C by 15+ points, A is less urgent. If B barely beats C, A may not close the gap either.

**Defer**: A full 500-task leaderboard run until internal results validate the approach. Spending $400–600 on a leaderboard submission before internal validation is premature given the score range uncertainty (H5 projects 18–30% Pro, which may not be competitively distinguishable from the current baseline).

---

## 9. Summary Tables for H6

### Per-Task Cost Comparison

| Variant | Tokens (K) | Cost (H3 optimistic) | Cost (realistic) | Active Improvements |
|---------|-----------|----------------------|-----------------|---------------------|
| C (Bare Sonnet) | 47.0K | $0.23 | $0.75 | I6 (partial) |
| B (Lite Spectrum) | 88.8K | $0.38 | $1.10 | I1, I6, I7 (partial) |
| A (Full Spectrum) | 127.4K | $0.57 | $1.60 | I1, I2, I3, I4, I6, I7 |

### Run Scenario Summary

| Scenario | Tasks | API Cost (H3 opt.) | API Cost (realistic) | Compute | Total (realistic) | Wall-Clock (batch 10) |
|----------|-------|-------------------|---------------------|---------|------------------|-----------------------|
| Minimum viable | 100 | $30.50 | $93 | $3 | ~$96 | ~4.2 hours |
| Recommended | 115 | $39.05 | $117 | $3.45 | ~$120 | ~5.2 hours |
| Full | 230 | $78.10 | $235 | $6.90 | ~$242 | ~10.4 hours |

*H3 optimistic costs exclude Docker compute. Realistic costs based on adjusted estimates in §6.2.*

### Wall-Clock Overhead Ratios

| Variant | Wall-Clock (midpoint) | Overhead vs. C |
|---------|----------------------|----------------|
| C | ~22 min | 1.0× |
| B | ~28 min | ~1.3× |
| A | ~37 min | ~1.7× |

### Break-Even Accuracy Thresholds

| Comparison | Extra cost/task (realistic) | Accuracy gain to break even (50 tasks) |
|------------|-----------------------------|-----------------------------------------|
| B vs. C | +$0.35 | +2 pp (1 additional task resolved) |
| A vs. C | +$0.85 | +13 pp (6–7 additional tasks resolved) |

---

## Completion Verification

- [x] Per-task token breakdown by variant (tables: input/output per agent role)
- [x] 50-task and 100-task run cost tables (3 variants × run sizes)
- [x] Wall-clock time model with parallelization assumptions documented
- [x] Competitor cost comparison with source (H5's competitive-intel.md)
- [x] Cost sensitivity analysis (revision pass, failure rate, parallelization)
- [x] Budget recommendation with minimum viable and recommended tiers
- [x] D3=3 publishability threshold analysis
- [x] Reconciliation of H3 optimistic vs. realistic token estimates
- [x] Break-even analysis for B vs. C and A vs. C

---

*H4 — Cost & Speed Modeler — swe-bench-prep-0401 — 2026-03-31*
