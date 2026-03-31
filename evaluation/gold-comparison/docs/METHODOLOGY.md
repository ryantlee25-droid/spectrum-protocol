# Gold Agent Evaluation Methodology

**Version**: 1.0  
**Date**: 2026-03-31  
**Study**: Opus vs Sonnet for the Gold (coordinator) role in Spectrum Protocol  

---

## 1. Why This Comparison Matters

In the Spectrum Protocol, Gold is the coordinator agent responsible for planning, validation, and recovery. Every spectrum run uses Gold at three distinct phases. Gold is currently assigned to Opus — the highest-capability, highest-cost model tier.

The cost asymmetry is significant:

| Metric | Gold (Opus) | Howlers (Sonnet x5) |
|--------|------------|---------------------|
| % of total tokens | ~15% | ~76% |
| % of total cost | ~45% | ~32% |

A 5-Howler full spectrum run costs approximately **$9.43 total**. Gold phases account for approximately **$4.25** of that. By comparison, five Howlers doing the bulk of the implementation work account for roughly $3.02.

This inversion — 15% of tokens costing 45% of the budget — exists because Opus output tokens cost $75/M versus Sonnet's $15/M. Gold generates ~29,000 output tokens per full spectrum run; those tokens alone cost more than 490,000 Sonnet input tokens.

**If Sonnet can perform Gold's role acceptably**, the cost savings are material:

- Gold Muster: ~$3.18 (Opus) → ~$0.55 (Sonnet) = **~$1.58 saved per muster**
- Full 5-Howler spectrum: ~$4.25 (Gold phases, Opus) → ~$0.75 (Sonnet) = **~$3.50 saved per run**
- 8-Howler spectrum: savings scale to ~$5–6 per run

The question this study answers: **can Sonnet do Gold's job well enough to justify the downgrade?**

---

## 2. What Gold Actually Does

Gold's role has three distinct phases being evaluated. A fourth phase (per-PR self-reflect) was already decided in TOKEN-OPTIMIZATION.md (T1-B) and is not contested here.

### 2.1 Muster (Phase 1) — The Planning Phase

Muster is Gold's most complex task. Given a PLAN.md and codebase context, Gold must:

1. **Decompose the work** into Howler tasks with clear scope statements
2. **Build a file ownership matrix** — every file that will be created or modified must appear exactly once, owned by exactly one Howler
3. **Construct a DAG** — identify which Howlers depend on which, encoding checkpoint dependencies (a Howler that provides types can unblock dependents before it fully completes)
4. **Write CONTRACT.md** — shared types, naming conventions, and per-Howler Design-by-Contract sections (preconditions, postconditions, invariants)
5. **Integrate Politico review** — spawn an adversarial reviewer (Phase 1.5) and address its findings before freezing the contract
6. **Detect decomposition hazards** — flag serial risks, critical-path Howlers, and synthesis patterns before committing to a parallel structure

Muster errors cascade. A missed file conflict means two Howlers touch the same file and one's work is lost at merge. A missing DAG edge means a Howler starts before its dependency is ready. A vague CONTRACT.md means Howlers implement the same interface differently. The downstream cost of a muster error is typically $2–5 in recovery (re-running Howlers, resolving conflicts, re-running quality gates).

**Phase weight in composite score: 40%**

### 2.2 Pax (Phase 5) — The Validation Phase

After all Howlers complete, Gold performs independent validation. It does not trust Howler self-reports. For each Howler, Gold:

1. Reads 1–3 source files the Howler created or modified
2. Verifies the implementation against CONTRACT.md postconditions
3. Checks that exported types match what the contract specified
4. Confirms integration points exist where claimed
5. Cross-references seam declarations: if Howler A claims it provides X to Howler B, Howler B's debrief should confirm it consumes X
6. Classifies integration risks and writes PAX-PLAN.md with merge order recommendations

Pax is the last line of defense before merge. Issues that Pax misses go to production. The failure mode for a weak Pax is not a crash — it is a "green but wrong" scenario where tests pass but the integration is subtly broken at the seams between Howlers.

**Phase weight in composite score: 40%**

### 2.3 Forge (Phase 4) — The Recovery Phase

When a Howler fails, Gold classifies the failure and chooses a recovery path. The taxonomy has five types:

| Type | Description | Recovery action |
|------|-------------|----------------|
| `transient` | Flaky tool call, network hiccup | Auto-resume without human confirmation |
| `logical` | Implementation logic wrong | Orange diagnosis → resume or retry |
| `structural` | Contract/boundaries wrong | Re-plan with updated decomposition |
| `environmental` | Tooling, auth, missing dependency | Fix environment, then resume |
| `conflict` | File ownership violated | Restructure → cannot auto-resolve |

Gold must also manage the circuit breaker: two failures on the same Howler auto-escalate to `structural` regardless of individual classification. Getting this wrong in either direction has costs: over-classifying as `transient` burns recovery budget on auto-resumes that will fail again; under-classifying as `transient` when the failure is `structural` wastes an Orange diagnosis cycle.

Forge is well-defined compared to Muster and Pax. There is a clear taxonomy, a clear decision tree, and the ground truth in each scenario specifies the correct classification. This is why Forge carries a lower weight despite its importance.

**Phase weight in composite score: 20%**

---

## 3. Why Self-Reflect Is Excluded

The per-PR self-reflect invocation (Gold writes 3–5 lines after each PR merges: "PR N merged, TypeScript passes, watch for X in next merge") was already analyzed in TOKEN-OPTIMIZATION.md section T1-B. It was reclassified from Opus to Sonnet as a decided optimization — not contested — because the output is structured journaling rather than synthesis. This study evaluates only the three phases where the Opus-vs-Sonnet question is genuinely open.

---

## 4. Evaluation Design Choices

### 4.1 Synthetic Scenarios vs Live Production Runs

This study uses synthetic scenarios rather than running live spectrums with Opus and Sonnet in parallel. The reasons:

**Why not live runs:**
- Cost: $9–15 per 5-Howler run, times N iterations for statistical confidence, is prohibitive
- Non-reproducibility: live runs on a real codebase produce different inputs each time (codebase changes between runs, task selection varies, Howler outputs differ)
- Non-comparability: Opus and Sonnet muster outputs cannot be compared fairly if they receive different inputs — and in a live run, subsequent phases receive the muster's output as their input

**Why synthetic:**
- Fixed inputs: both models receive identical scenario YAML, making outputs directly comparable
- Controlled difficulty: scenarios are calibrated across easy/medium/hard/adversarial tiers
- Ground truth: scenarios specify expected file ownership, DAG edges, contract sections, and failure classifications — enabling automated scoring on the dimensions that matter most
- Re-runnable: the same scenarios can be re-run after model updates or protocol changes

**Known bias this introduces:**
Synthetic scenarios may be simpler than production tasks in ways that favor both models equally and mask capability differences that only emerge from emergent complexity (novel codebases, unusual task shapes, multi-domain interactions). The scenario library was constructed by analyzing 5 historical Spectrum runs, but 5 runs is insufficient to represent the full distribution of production tasks.

### 4.2 Mitigations for Synthetic Bias

1. **Historical run analysis**: Scenario difficulty and structure were calibrated against artifacts from the 5 historical runs (`lessons_convoy_v3_0328`, `lessons_remnant_infra_0329`, `lessons_remnant_narrative_0329`, `lessons_remnant_ux_0329`, `lessons_convoy_eval_0330`). Scenario complexity targets the patterns seen in those runs.

2. **Adversarial tier**: The scenario library includes deliberately tricky cases (edge-cases directory) designed to surface capability differences that easy/medium scenarios would miss.

3. **Injected defects**: Muster scenarios inject known file ownership conflicts and Politico issues; Pax scenarios inject CONTRACT.md deviations; Forge scenarios inject deliberate misclassification traps. These ground-truth injections make it possible to measure precision, not just recall.

4. **Re-runnable framework**: The evaluation harness is designed to be re-run after model updates or new production run data becomes available. A point-in-time result should not be treated as permanent.

---

## 5. Scoring Design

### 5.1 Phase Weights: 40% Muster / 40% Pax / 20% Forge

The 40/40/20 split reflects two asymmetries:

**Why Muster and Pax each receive 40%:**
- Both are judgment-heavy synthesis tasks where model capability most clearly differentiates
- Muster errors are cascading (bad decomposition → all Howlers affected)
- Pax errors are last-line-of-defense (missed issues go to production undetected)
- Both involve open-ended reasoning against a specification, not a lookup task with a fixed answer

**Why Forge receives 20% despite being critical:**
- Forge is well-defined: five failure types, a documented decision tree, a clear circuit breaker rule
- Ground truth is unambiguous: each scenario specifies the correct classification
- The well-defined nature means both models are more likely to be comparable, making the weight less decision-relevant
- A model that passes Muster and Pax but fails Forge can be given more structured Forge prompts (the taxonomy is in the protocol spec); the same remediation is harder for Muster and Pax

**Why this weighting rather than equal thirds:**
Equal weighting (33/33/33) would overweight Forge relative to its decision-relevance. The primary question is whether Sonnet can handle the judgment-intensive work; a correct Forge classification in a clear-cut scenario tells us less about that than a correct muster decomposition in a complex scenario.

### 5.2 Thresholds

| Phase | Pass Threshold | Rationale |
|-------|----------------|-----------|
| Muster | 85% | Cascade risk: below 85% means meaningful structural errors in roughly 1-in-6 dimensions |
| Pax | 80% | Last-line-of-defense: allows some deviation detection misses but not systematic failure |
| Forge | 90% | Well-defined task: high expected accuracy; below 90% suggests systematic misclassification |

Forge's threshold is highest because the task is most constrained. A model that cannot correctly classify failure types 90% of the time on scenarios with clear ground truth would be concerning regardless of its Muster/Pax performance.

The composite pass threshold is **82%** (weighted average of 0.85 × 0.4 + 0.80 × 0.4 + 0.90 × 0.2).

### 5.3 Scoring Methods

Each rubric item uses one of three methods:

- **Automated**: computed from Gold's structured output against scenario ground truth (file ownership sets, DAG edge sets, classification labels)
- **Human**: requires a reviewer to read Gold's prose and apply criteria (postcondition testability, scope coherence)
- **Hybrid**: automated component for structural presence + human component for content quality

Human-scored items use conservative tie-breaking: when two reviewers disagree on TESTABLE vs VAGUE for a postcondition, it is scored VAGUE.

---

## 6. Known Limitations

1. **Point-in-time evaluation**: Model capabilities change with updates. A Sonnet result from March 2026 does not predict Sonnet's performance after the next training run. The evaluation should be re-run quarterly or after major model updates.

2. **Synthetic scenarios may not capture emergent complexity**: Production spectrums involve novel codebases, ambiguous task descriptions, and emergent interactions between Howlers that are difficult to replicate in synthetic form. The scenario library is calibrated against 5 historical runs, which is insufficient for statistical significance.

3. **N=5 historical runs**: The historical run corpus used to calibrate scenarios is small. Edge cases not represented in those 5 runs are likely underrepresented in the scenario library. Adversarial scenarios mitigate but do not eliminate this gap.

4. **Single evaluator**: Human-scored items (postcondition testability, decomposition soundness, Politico integration quality) do not have inter-rater reliability measurement in this study. A single evaluator's classifications are not validated against an independent reviewer. Findings based heavily on human-scored items should be treated with lower confidence.

5. **No latency measurement under load**: The cost comparison assumes similar token volumes between Opus and Sonnet for the same task. If Sonnet requires significantly more output tokens to complete the same task (e.g., more verbose reasoning), the cost savings would be partially offset.

---

## 7. How to Re-Run This Evaluation

To repeat the evaluation after model updates or protocol changes:

1. **Update scenario library if needed**: Review historical runs since the last evaluation. If new patterns appear (new failure types, new task shapes), add scenarios to the appropriate tier directory under `scenarios/`.

2. **Run the harness against both models**:
   ```
   cd ~/spectrum-protocol/evaluation/gold-comparison
   python harness/run_evaluation.py --model opus --phase all
   python harness/run_evaluation.py --model sonnet --phase all
   ```

3. **Automated scoring**: The harness outputs per-item scores for all automated dimensions. Review `results/` for raw output.

4. **Human scoring**: For hybrid and human-scored items, use the rubric criteria in `rubrics/` to score Gold's outputs. Populate the `human_scores` fields in each result JSON.

5. **Compute composite scores**: Use the scoring module:
   ```
   python scoring/compute_composite.py --results results/
   ```

6. **Apply DECISION-FRAMEWORK.md**: Compare composite and per-phase scores against thresholds. Follow the decision tree for the appropriate outcome.

7. **Update FINDINGS-TEMPLATE.md**: Fill in all sections with the run results. Record the scenario library version and any scenarios that were added since the previous run.

**Estimated time**: 2–4 hours for scenario execution (model API time), 1–2 hours for human scoring, 30 minutes for composite computation and framework application.
