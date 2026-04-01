# SWE-bench Readiness Report
**Spectrum**: swe-bench-prep-0401
**Author**: H6 — Synthesis & Readiness Assessment
**Date**: 2026-03-31
**Sources**: protocol-audit.md (H1), infrastructure.md (H2), pipeline-design.md (H3), cost-model.md (H4), competitive-intel.md (H5)

---

## 1. Executive Summary

**Verdict: Go — with two pre-run fixes and a $150–200 budget.**

Spectrum is ready to run SWE-bench Pro. The protocol is coherent (8.5/10 by H1's audit), the infrastructure path is clear, three working pipeline variants are designed, the cost model is sound, and the competitive landscape is understood.

The realistic score range is **18–30% on SWE-bench Pro** — which corresponds to roughly 38–55% on SWE-bench Verified if we extrapolate. This puts Spectrum in the tier of mid-2025 commercial agents and is honest given the absence of semantic codebase retrieval, Spectrum's primary gap against the top performers.

The first run should cost $100–200 (realistic API estimates), take 7–10 days to set up and execute, and run 50 tasks at Variant B (Lite Spectrum) plus 50 tasks at Variant C (Bare Sonnet baseline), with an optional 15-task Variant A subset on the hardest multi-file problems. Two P1 protocol fixes need 30 minutes of text edits before drop.

Without a Context Engine (semantic codebase retrieval), Spectrum will not reach 50%+ Pro. The current architecture's ceiling is ~30% Pro unless a retrieval layer is added. This is not a reason to delay — the benchmark run will produce useful signal and a defensible internal result at modest cost.

---

## 2. Readiness Scorecard

| Area | Rating | Summary |
|------|--------|---------|
| **Protocol** (H1) | Warning | 7 improvements integrated and coherent; 2 P1 text fixes needed before drop; I5 (contract-to-test) underspecified but not used in SWE-bench mode |
| **Infrastructure** (H2) | Warning | Path is clear but nothing is provisioned; 7 days of setup work before first task runs; two mandatory adapters need to be built |
| **Pipeline** (H3) | Ready | Three variants fully designed with step-by-step pipelines, token estimates, and failure mode analysis; drop templates written |
| **Budget** (H4) | Ready | $150–200 covers the recommended scenario with retry buffer; cost model is well-calibrated with optimistic and realistic ranges |
| **Competitive Positioning** (H5) | Warning | Target score (18–30% Pro) is realistic and achievable; Spectrum cannot reach the top tier without semantic retrieval; benchmark choice (Pro over Verified) is correct |

**Overall**: 2 Ready, 3 Warning, 0 Blockers at the area level. No area-level blockers, but six specific blockers exist within the Warning areas that must be resolved before the first task executes.

---

## 3. Blockers

These must be resolved before running a single task.

### B1 — x86_64 Machine Not Provisioned (H2)
The SWE-bench harness has hardcoded x86 binaries and experimental ARM support. Evaluation on a Mac M-series machine will produce false failures on at least 496 instance types and take 2-4 hours for image builds that should take minutes.

**Fix**: Provision a Linux x86_64 cloud instance before starting. Minimum: AWS c5.4xlarge (16 vCPU, 32 GB RAM, ~$0.68/hr) or equivalent. Configure Docker data-root on a 200 GB volume.

### B2 — Docker Storage Not Configured (H2)
SWE-bench environment images total ~60 GB for Verified; Pro images add more. Without 200 GB of Docker-allocated storage, evaluation hangs mid-run at image build (a known hang documented in swebench GitHub Issue #157).

**Fix**: Configure Docker daemon.json `data-root` to a volume with 200+ GB free. Verify before starting any run.

### B3 — Modal Account Not Set Up (H2)
The SWE-bench Pro evaluation script (`swe_bench_pro_eval.py`) requires Modal for any run beyond ~20 tasks. The `--use_local_docker` flag is labeled beta and untested at scale. Without Modal, a 50-task Pro run takes 4-8 hours locally vs. ~1 hour on Modal.

**Fix**: Sign up for Modal and run `modal setup` to authenticate. This is free for small workloads; at $0.10–0.30 per 100 tasks in harness overhead, cost is negligible.

### B4 — Task Input Adapter Does Not Exist (H2)
Spectrum has no code to load SWE-bench Pro task fields from the HuggingFace dataset and format them for Gold's input. This is a required precondition for any run.

**Fix**: Build `load_tasks.py` + `format_gold_input.py` as specified in H2 Section 5a. Estimated effort: 1-2 days. The format is fully specified — each task maps to a structured prompt with `instance_id`, `repo`, `base_commit`, `problem_statement`, `FAIL_TO_PASS`, `PASS_TO_PASS`, and `dockerhub_tag`.

### B5 — Patch Emission Adapter Does Not Exist (H2)
Spectrum has no code to collect Howler-generated unified diffs and write them to the predictions JSONL format the harness requires. Without this, no patch can be scored.

**Fix**: Build `emit_predictions.py` (H2 Section 5d provides the exact Python snippet). Estimated effort: half a day. This is a thin wrapper around `json.dumps()` with three fields.

### B6 — I5 (Contract-to-Test) Reaping Mode Gap in Protocol (H1)
SPECTRUM-OPS.md step 12 says "Skip for doc-only spectrums and nano mode" but omits reaping mode. A Gold running in reaping mode would not know whether to generate contract tests. For SWE-bench specifically, I5 is inactive across all variants (the harness provides failing tests; generating contract stubs would create confusion). The gap needs to be patched in the protocol text regardless, and a misread here could cause Gold to waste time on an irrelevant step.

**Fix**: Edit `spectrum/SPECTRUM-OPS.md` step 12 — change "Skip for doc-only spectrums and nano mode" to "Skip for doc-only spectrums, nano mode, and reaping mode." Also add a minimal test template example (TypeScript/Python). Estimated effort: 30 minutes.

---

## 4. Warnings

These should be addressed but do not block the first run.

### W1 — H3 Cost Estimates Are Optimistic by 3-7x (H4, High Impact)
H3's per-task token estimates (Variant C: $0.23, B: $0.38, A: $0.57) assume disciplined context management with targeted file reads. Real agentic SWE-bench sessions accumulate context across multi-turn tool calls, run longer test suites, and typically consume 1-3.5M tokens vs. H3's 40-127K. H4's realistic estimates (C: $0.75, B: $1.10, A: $1.60) are better calibrated to published competitor benchmarks. H2's own independent estimate puts a 50-task Variant A run at ~$85 total, consistent with H4's realistic range.

**Recommendation**: Use H4's realistic estimates for budgeting ($150-200 for the recommended scenario with retry buffer). Do not use H3's optimistic figures to set budget expectations.

### W2 — Gold Specification Drift Risk on Simple Tasks (H3, High Impact)
On single-file bug fixes with clear stack traces (~30-35% of Pro tasks), Gold's mini-CONTRACT.md adds 5-8 minutes of latency and ~$0.09 with near-zero accuracy benefit. On these tasks, Gold may actually hurt accuracy by generating an authoritative-feeling wrong interpretation that locks the Howler in. Variant C would resolve the same task faster and cheaper.

**Recommendation**: Implement the complexity-based routing heuristic from H3 — route to Variant A only if failing tests span 3+ files, issue description exceeds 500 tokens, or traces cross 3+ modules. Route all others to Variant B. This is for the production decision post-evaluation, not the benchmark comparison itself.

### W3 — No Semantic Retrieval Layer (H5, High Impact)
Augment's Context Engine (semantic codebase index) is the single biggest differentiator in Pro performance — it beat Claude Opus 4.5 on the same scaffold by ~6 points purely through better retrieval. Without a semantic index, Spectrum's file localization will rely on Gold reading failing test imports and the Howler exploring files manually. This caps Pro performance at roughly 30%.

**Recommendation**: Accept the ceiling for this run. After initial validation, evaluate whether building or integrating a lightweight embedding-based retrieval layer (e.g., code embeddings via Voyage AI or a local ChromaDB index of the repo) is worth the engineering investment. A semantic index would likely be the single highest-ROI improvement post-evaluation.

### W4 — I3 CREATES Exemption Missing from Muster Checklist (H1, Low Impact)
SPECTRUM-OPS.md's muster checklist item 10 (Codebase Context sections) does not note that pure-CREATES Howlers should write `N/A` rather than attempting to document non-existent files. This is harmless for SWE-bench (all tasks are MODIFIES) but will cause minor friction on future pure-create spectrums.

**Recommendation**: Append "(write `## Codebase Context: N/A (all new files)` for pure-create Howlers)" to checklist item 10 during the next protocol maintenance pass.

### W5 — No Multi-Task Parallelism Orchestrator Yet (H2, Medium Impact)
The critical path estimate of 7-10 days to first results assumes sequential task execution. A 50-task Variant B run at 28 min/task sequential = ~23 hours wall-clock. Without a task orchestrator, the evaluation timeline stretches from one day to nearly two days for the run phase alone.

**Recommendation**: Build basic parallel task execution as part of `run_evaluation.py`. H2 provides the design — batch size 10-20 concurrent tasks is sufficient to bring wall-clock under 3 hours for the recommended scenario.

### W6 — Full Test Suite Not Specified for Gray (H2/H3, Medium Impact)
H5 notes that running only FAIL_TO_PASS tests (not the full project test suite) inflates solve rates by 4-7% and misses ~29.6% of "plausible but wrong" patches. The pipeline design in H3 directs Gray to "run the failing tests" — it is not explicit about running the full suite.

**Recommendation**: In the Howler drop template for SWE-bench, instruct the Howler to run PASS_TO_PASS tests (the regression guard provided by the harness) explicitly, not just FAIL_TO_PASS. The harness will catch regressions at evaluation time regardless, but surfacing them during implementation saves retry overhead.

### W7 — Muster Checklist Order Does Not Match Step Order (H1, Low Impact)
The 16-item muster checklist in SPECTRUM-OPS.md is not ordered by execution sequence (e.g., ARCHITECTURE.md at step 6 appears as checklist item 15). This creates cognitive friction for Gold using it as a progress tracker mid-muster.

**Recommendation**: Reorder the checklist to match muster step sequence during next protocol maintenance pass. No functional impact on SWE-bench runs.

---

## 5. Recommended Run Plan

### Run Order

**Phase 1 — Baseline (Days 8-9 after setup)**

Run Variant C (Bare Sonnet) on 50 tasks from the SWE-bench Pro public set.

- This establishes the baseline before any Spectrum overhead is applied
- Select from Python tasks in the public 11-repo subset
- Prioritize multi-file tasks (3+ files changed) to match Spectrum's strength profile
- Cost: ~$37–75 (H4 optimistic to realistic)
- Wall-clock: ~2-4 hours at batch size 10-15

**Phase 2 — Lite Spectrum (Days 9-10)**

Run Variant B (Lite Spectrum) on the same 50 tasks, in the same order.

- Same task set as Phase 1 is mandatory for a valid comparison
- Gold generates a 200-token compact task brief; Howler implements; White + Gray gate
- Cost: ~$55 (realistic)
- Wall-clock: ~3-4 hours at batch size 10-15

**Phase 3 — Conditional: Full Spectrum on Hard Subset**

After reviewing Phase 1 vs. Phase 2 results: if Variant B shows improvement over Variant C, run Variant A on the 15 hardest tasks from the original 50 (filter for 4+ files changed, complex issue descriptions).

- Do not run Phase 3 if Phase 2 did not beat Phase 1 by at least 3 percentage points — the overhead is harder to justify on a weak signal
- Cost: ~$24 (realistic for 15 tasks)
- Wall-clock: ~2 hours

### Timeline

| Day | Activity |
|-----|----------|
| 1 | Provision x86_64 Linux instance; install Docker + Python deps |
| 2 | Configure Docker storage; validate harness with gold patches (B2 + B3 fix) |
| 3-4 | Build `load_tasks.py`, `format_gold_input.py`, `emit_predictions.py` (B4 + B5 fix) |
| 5 | Dry run: 5 tasks end-to-end across all three variants; fix adapter bugs |
| 6 | Protocol fixes (B6: I5 reaping mode gap + test template) — 30 min |
| 7 | Finalize 50-task subset selection (Python, public set, multi-file priority) |
| 8 | Phase 1: Variant C run (50 tasks) |
| 9 | Phase 2: Variant B run (same 50 tasks) |
| 10 | Results analysis; decide whether to run Phase 3 |
| 11 | Phase 3 (optional): Variant A on 15 hardest tasks |

**Total: 10-11 days from zero to published internal results.**

### Budget

| Item | Cost |
|------|------|
| Phase 1: Variant C (50 tasks, realistic) | ~$37–75 |
| Phase 2: Variant B (50 tasks, realistic) | ~$55 |
| Phase 3: Variant A (15 tasks, realistic, conditional) | ~$24 |
| Compute (AWS c5.4xlarge, ~$0.68/hr × 10 hours) | ~$7 |
| Modal evaluation overhead | ~$3 |
| Retry buffer (15% of API costs) | ~$18 |
| **Total** | **~$144–182** |

**Recommended budget: $200** (covers all phases with buffer).

---

## 6. Realistic Score Projection

### Variant C — Bare Sonnet Baseline

**Projected Pro score: 18–22%**

H5's baseline estimate for a single Howler with minimal scaffolding is 15–30% Verified, which maps to 18–22% Pro given the 20–30 point Verified-to-Pro discount. Variant C's active improvement is only I6 (partial revision pass embedded in the prompt). The primary risks are: no scope verification (Gold is absent), no regression guard beyond self-report, and no quality gate. Variant C will solve the easiest, most unambiguous tasks cleanly and fail on anything requiring interpretation or pattern-matching to codebase conventions.

### Variant B — Lite Spectrum

**Projected Pro score: 20–27%, likely 3–6 points above Variant C**

Variant B activates I1 (Issue Re-Read) and I6 (Revision Pass) — the two improvements most directly tied to single-task correctness. H4's break-even analysis is instructive: Variant B only needs to recover 1 additional task per 50 (2 percentage points) to justify its coordination overhead. The Issue Re-Read improvement alone is documented to catch "directionally correct but edge-case-missing" patches. A 3-6 point gain is the conservative estimate; upside scenario is 8-10 points if the Gold task brief consistently improves file localization.

The downside case: if Gold's compact brief misdirects even 5% of tasks (2-3 out of 50), Variant B could match or slightly underperform Variant C. This is the primary uncertainty.

### Variant A — Full Spectrum on Hard Tasks

**Projected Pro score on 4+ file tasks: 22–30%**

Variant A activates 5/7 improvements (I1, I2, I3, I4, I6 — and partial I7). On genuinely complex multi-file tasks, the mini-CONTRACT.md's per-file codebase context (I3) and White-verified file paths (I4) are the load-bearing improvements. H3's analysis of the Augment Context Engine finding supports this: structured context before the agent writes anything is the primary differentiator at the top of the leaderboard.

The risk: on the 15 hardest tasks in the subset, Gold's interpretation has more surface area to go wrong. If Gold misidentifies root cause on 3-4 of the 15 tasks, A could underperform B on this subset even with more improvements active.

### D3 Score (Three-Digit Leaderboard Target)

A D3 score means the system resolves enough tasks to appear as a non-trivial result — the minimum threshold is roughly 10% on Pro (50 tasks resolved out of 500). All three variants comfortably exceed this threshold at their projected scores (18–30% Pro = 90–150 tasks resolved on the full 500-task set). However, submitting to the official leaderboard requires running all 500 tasks, which costs $375–800 at realistic estimates. The recommended strategy is to validate internally on 50 tasks first, then decide whether to commit to a 500-task leaderboard submission.

**Summary table:**

| Variant | Projected Pro Score | Active Improvements | Cost (50 tasks) |
|---------|--------------------|--------------------|-----------------|
| C (Bare Sonnet) | 18–22% | I6 (partial) | ~$37–75 |
| B (Lite Spectrum) | 20–27% | I1, I6, I7 (partial) | ~$55 |
| A (Full Spectrum, hard subset) | 22–30% | I1–I4, I6, I7 | ~$24 (15 tasks) |

---

## 7. Top 5 Recommendations

### R1 — Fix B4 + B5 First (Adapters)
The task input adapter and patch emission adapter are on the critical path to any run. Neither is built. No other preparation matter until these exist. Block two days specifically for building and testing them end-to-end on 5 tasks before committing to a full run. A broken adapter discovered at task 40 of 50 is expensive.

### R2 — Run Variant C Before Variant B
The Variant C baseline is not optional. Without it, Variant B's score is uninterpretable — there is no way to know whether Spectrum's overhead added value or just added cost. Run C on the exact same 50 tasks as B, in the same order, before analyzing either result.

### R3 — Invest in Semantic Retrieval Post-Validation
H5 is unambiguous: the Augment-vs-Cursor gap on Pro (51.80% vs. ~36.80%) uses the same underlying model and differs only in retrieval quality. A semantic codebase index (even a lightweight one — repo-level embeddings via Voyage AI or local ChromaDB, pre-built per task at ~$0.01/task) is the highest-ROI single investment after this benchmark run. Build it as a follow-up if the internal results justify continuing.

### R4 — Treat D3=3 as the Internal Goal, Not a Leaderboard Submission
A 500-task leaderboard submission costs $375–800 and requires held-out set access from Scale AI. The internal 50-task validation is sufficient to produce a credible publishable blog post or internal evaluation report. Defer the leaderboard submission until results show a score worth publishing publicly (competitive with current Pro midfield, not just "above zero").

### R5 — Apply Pattern Library (I7) Incrementally Across Runs
The Pattern Library improvement (I7) is the only one that compounds — it gets more valuable with each run as Brown extracts structured failure patterns from LESSONS.md. After the first 50-task run, have Brown draft failure patterns from the Howler HOOKs of failed tasks. These patterns will improve subsequent runs at zero architectural cost. Do this even before the results are fully analyzed.

---

## 8. Honest Assessment

Spectrum is ready to run SWE-bench but is not ready to compete at the top of the leaderboard.

The 7 accuracy improvements (I1-I7) are real. The protocol is well-designed. The pipeline adapter design is thorough. But the competitive landscape is clear: the top performers on SWE-bench Pro share one feature that Spectrum lacks — a semantic codebase retrieval layer. Augment's Context Engine, Factory's HyperCode graph, Sonar's static analysis context, Amazon Q's IDE-native file graph. These are not protocol improvements; they are infrastructure investments. Spectrum's Gold muster with mini-CONTRACT.md is a manual approximation of what these systems do automatically and at scale.

The projected 18–30% Pro score is honest. It is not embarrassing — it is better than most teams would achieve with a raw model call, and it will demonstrate that the Issue Re-Read and Revision Pass improvements add measurable value. But it is not competitive with Augment's 51.80% or even Cursor's 36.80%.

**The worst case**: Variant B scores at or below Variant C. This would mean Gold's compact task brief misdirects more Howlers than it helps, and the coordination overhead is net-negative on single-issue tasks. H3 identifies this as the central risk and designs the evaluation specifically to test it — if this happens, the finding is valuable. It would mean Spectrum's coordination protocol has negative transfer to single-issue benchmark tasks, and future development should focus on longer-horizon multi-task coordination where the muster ceremony is load-bearing.

**If that happens, the correct response is not to abandon Spectrum** — it is to recognize that SWE-bench tests a different regime than what Spectrum was designed for. A benchmark result where B beats C by even 2 percentage points is a proof of concept. A result where B matches or lags C is a signal to narrow the protocol scope on single-issue tasks and invest in retrieval rather than coordination.

Either outcome is worth knowing.

---

*H6 — Synthesis & Readiness Report — swe-bench-prep-0401 — 2026-03-31*
