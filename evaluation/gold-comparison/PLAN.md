# PLAN: Gold Agent Comparison — Opus vs Sonnet
**Author**: Blue (◎)
**Date**: 2026-03-31
**Target directory**: `~/spectrum-protocol/evaluation/gold-comparison/`

---

## 1. Objective

Determine whether Sonnet is a viable replacement for Opus as the Gold (mayor) agent in Spectrum, or whether specific Gold phases are safely downgradable while others must remain Opus.

The comparison must be **evidence-based**: not intuition about model capability, but measured output quality on the actual tasks Gold performs.

---

## 2. Scope

### In scope
- Gold Muster quality: decomposition accuracy, file ownership conflict detection, DAG construction, CONTRACT.md precision (types, preconditions, postconditions, invariants)
- Gold Pax quality: independent validation accuracy — does Sonnet catch the same "green but wrong" Howler failures that Opus would?
- Gold Forge quality: failure classification accuracy across the 5 failure types; recovery decision soundness
- Cost and latency comparison (Opus vs Sonnet for identical tasks)
- A reusable evaluation harness that can run future comparisons as the protocol evolves

### Not in scope
- Howler quality (they remain Sonnet regardless)
- White/Gray/Politico quality (not under review)
- Per-PR self-reflect (TOKEN-OPTIMIZATION.md already recommends downgrading to Sonnet; treat as decided)
- Brown's LESSONS.md drafting (already Haiku; not contested)
- Comparing against Haiku for Gold (not a serious option given task complexity)
- Benchmarking against other agent frameworks (covered in AGENTIC-LANDSCAPE.md)
- Full production spectrum runs at scale (evaluation uses synthetic + historical scenarios)

### Decision the comparison must answer
For each Gold phase independently:
1. Is Sonnet output quality within acceptable tolerance of Opus? (Pass/fail per phase)
2. If yes, what is the cost savings?
3. Are there specific scenario types where Sonnet degrades — and are those scenarios common?

---

## 3. Tasks

Six independent tasks suitable for parallel Howler execution. Dependencies are noted; Tasks 1–5 can run in parallel. Task 6 depends on Task 3.

---

### Task 1 — Benchmark Scenario Library
**Howler**: howler-scenarios
**Effort**: M
**Serial risk**: no

Build a library of 15–20 synthetic spectrum scenarios that exercise Gold's known-hard cases. Scenarios are structured inputs (a PLAN.md excerpt + codebase stub + context) that Gold agents can be asked to process, with known-correct ground-truth outputs for scoring.

**Scope**:
- 5 Muster scenarios: ranging from simple (3-Howler reaping) to complex (8-Howler full with cross-cutting types, shared files, and a DAG with real dependency edges). Must include at least one scenario where a naive decomposition would produce a file conflict, and one where the DAG has a non-obvious serial dependency.
- 5 Pax scenarios: synthetic Howler debrief sets where some Howlers have quietly deviated from CONTRACT.md (the deviation is real but not flagged by the Howler). Gold must catch it during independent validation. Includes at least one case where a Howler self-reports "confidence: high" but the output is subtly wrong.
- 5 Forge scenarios: failure classification inputs (HOOK.md excerpts with error descriptions). Covers all 5 failure types: transient, logical, structural, environmental, conflict. At least one ambiguous case per type boundary.
- 3–5 edge cases: context window pressure (large debrief sets), ambiguous task boundaries, contract amendment situations.

**Deliverables**:
- `scenarios/muster/scenario-{01..05}.yaml` — each containing: `task_description`, `plan_excerpt`, `codebase_context`, `known_conflicts` (for scoring), `expected_dag_edges`, `expected_contract_sections`
- `scenarios/pax/scenario-{01..05}.yaml` — each containing: `debrief_set` (array of synthetic HOOK.md + debrief content), `contract_md`, `injected_deviations` (list of what Gold should catch), `confidence_levels`
- `scenarios/forge/scenario-{01..05}.yaml` — each containing: `hook_md_excerpt`, `correct_classification`, `correct_recovery_action`, `rationale`
- `scenarios/edge-cases/scenario-{01..03}.yaml`
- `scenarios/README.md` — authoring guide for adding new scenarios

**Acceptance criteria**:
- [ ] Muster scenarios span effort range S through L with 2+ Howlers at the L end
- [ ] At least one Muster scenario has a latent file conflict that a good decomposition catches
- [ ] Pax scenarios include at least one "high confidence, subtly wrong" Howler
- [ ] Forge scenarios cover all 5 failure types with at least one ambiguous boundary case
- [ ] All scenarios are valid YAML (parseable by PyYAML without error)
- [ ] Each scenario has a `scenario_id`, `difficulty` (easy/medium/hard), and `gold_phase` field
- [ ] `scenarios/README.md` exists and documents the schema for each scenario type

**File ownership** (CREATES only):
```
scenarios/muster/scenario-01.yaml  through  scenario-05.yaml
scenarios/pax/scenario-01.yaml     through  scenario-05.yaml
scenarios/forge/scenario-01.yaml   through  scenario-05.yaml
scenarios/edge-cases/scenario-01.yaml through scenario-03.yaml
scenarios/README.md
```

---

### Task 2 — Scoring Rubrics
**Howler**: howler-rubrics
**Effort**: M
**Serial risk**: no

Define machine-checkable and human-assessable scoring criteria for each Gold phase. The rubrics are the ground truth for evaluating model outputs — they must be unambiguous enough that two independent reviewers would score the same output identically.

**Scope**:

**Muster rubric** (`rubrics/muster-rubric.yaml`):
- File ownership completeness (every file mentioned in the task appears in the matrix)
- File ownership conflict detection (score: conflicts_found / conflicts_injected)
- DAG edge accuracy (recall and precision vs expected_dag_edges)
- CONTRACT.md completeness: shared types coverage, precondition/postcondition/invariant presence per Howler
- CONTRACT.md precision: are the postconditions testable (binary pass/fail), or are they vague prose?
- Decomposition soundness: do Howler boundaries follow single-responsibility? Are serial tasks correctly labeled?
- Politico integration: does the output include a Politico review step, and did it catch injected issues?

**Pax rubric** (`rubrics/pax-rubric.yaml`):
- Deviation detection rate: injected_deviations_caught / injected_deviations_total
- False positive rate: flags_raised_on_correct_howlers / correct_howlers_total
- Seam cross-reference accuracy: seams_correctly_cross_referenced / total_seam_declarations
- Risk classification: are integration risks classified correctly (blocker vs warning vs observation)?
- Validation depth: does Gold read actual files for low-confidence Howlers?

**Forge rubric** (`rubrics/forge-rubric.yaml`):
- Classification accuracy: correct_type / total_scenarios (per failure type)
- Recovery action correctness: correct_action / total_scenarios
- Circuit breaker application: does Gold apply the 2-failure rule correctly in multi-failure scenarios?
- Escalation appropriateness: does Gold escalate when it should vs auto-recover?

**Overall scoring** (`rubrics/scoring-guide.yaml`):
- Weighted composite score formula: Muster 40%, Pax 40%, Forge 20%
- Minimum passing threshold per phase (suggested: 85% for Muster, 80% for Pax, 90% for Forge)
- How to handle partial credit on rubric items
- Definitions of "acceptable tolerance" for recommendation purposes

**Deliverables**:
- `rubrics/muster-rubric.yaml`
- `rubrics/pax-rubric.yaml`
- `rubrics/forge-rubric.yaml`
- `rubrics/scoring-guide.yaml`

**Acceptance criteria**:
- [ ] Each rubric item has a `scoring_method` field: `automated`, `human`, or `hybrid`
- [ ] Each automated item specifies an exact computation (e.g., `precision = tp / (tp + fp)`)
- [ ] No rubric item uses subjective language ("good", "reasonable") without a defined threshold
- [ ] `scoring-guide.yaml` defines the composite formula explicitly
- [ ] Muster rubric covers all 7 dimensions listed above
- [ ] Pax rubric covers all 5 dimensions listed above
- [ ] Forge rubric covers all 4 dimensions listed above

**File ownership** (CREATES only):
```
rubrics/muster-rubric.yaml
rubrics/pax-rubric.yaml
rubrics/forge-rubric.yaml
rubrics/scoring-guide.yaml
```

---

### Task 3 — Evaluation Harness (Core)
**Howler**: howler-harness
**Effort**: L
**Serial risk**: no

Build the Python evaluation harness that drives the comparison: loads scenarios, dispatches them to Gold agents (Opus and Sonnet), collects outputs, and stores results for scoring.

**Scope**:
- `harness/run_evaluation.py` — CLI entry point. Accepts `--model [opus|sonnet|both]`, `--phase [muster|pax|forge|all]`, `--scenario [id|all]`, `--output-dir`. Runs scenarios, writes raw outputs to `results/raw/`.
- `harness/scenario_loader.py` — loads and validates scenario YAML files. Raises clear errors on schema violations.
- `harness/prompt_builder.py` — constructs the Gold prompt for each scenario+phase combination. Prompts must be faithful to what a real Gold agent would receive (draw from SPECTRUM-OPS.md and CLAUDE.md Gold sections).
- `harness/output_parser.py` — extracts structured data from Gold's free-text output for scoring: file ownership tables, DAG YAML, deviation flags, failure classifications. Uses regex + heuristic parsing (not LLM-assisted, to avoid circular evaluation).
- `harness/result_store.py` — writes raw outputs and parsed fields to `results/raw/{run-id}/{scenario-id}/{model}.json`.
- `harness/config.py` — run configuration: model IDs, API endpoint, token budget limits, timeout per scenario.
- `tests/test_scenario_loader.py` — unit tests for scenario loading and schema validation
- `tests/test_prompt_builder.py` — unit tests verifying prompts contain required sections
- `tests/test_output_parser.py` — unit tests for each parser (muster table extractor, DAG extractor, etc.)

**Technical constraints**:
- Uses the Anthropic Python SDK (anthropic package)
- Each scenario dispatched independently; no session state carries between scenarios
- Gold prompt structure must match what SPECTRUM-OPS.md specifies for Muster, Pax, and Forge phases
- Raw outputs stored as-is before parsing, so human review of edge cases is always possible
- Harness must be runnable with `python -m harness.run_evaluation` from the gold-comparison directory

**Deliverables**:
- `harness/run_evaluation.py`
- `harness/scenario_loader.py`
- `harness/prompt_builder.py`
- `harness/output_parser.py`
- `harness/result_store.py`
- `harness/config.py`
- `harness/__init__.py`
- `tests/test_scenario_loader.py`
- `tests/test_prompt_builder.py`
- `tests/test_output_parser.py`
- `requirements.txt` (pinned: anthropic, pyyaml, pytest)

**Acceptance criteria**:
- [ ] `python -m harness.run_evaluation --help` runs without error
- [ ] `python -m harness.run_evaluation --model sonnet --phase muster --scenario muster-01 --dry-run` prints the constructed prompt without making an API call
- [ ] `pytest tests/` passes with zero failures
- [ ] `output_parser.py` correctly extracts file ownership tables from at least 3 distinct output format variations (tested in `test_output_parser.py`)
- [ ] `result_store.py` writes valid JSON with fields: `scenario_id`, `model`, `phase`, `raw_output`, `parsed`, `tokens_used`, `latency_ms`, `timestamp`
- [ ] Harness does not call the API when `--dry-run` is passed

**File ownership** (CREATES only):
```
harness/__init__.py
harness/run_evaluation.py
harness/scenario_loader.py
harness/prompt_builder.py
harness/output_parser.py
harness/result_store.py
harness/config.py
tests/__init__.py
tests/test_scenario_loader.py
tests/test_prompt_builder.py
tests/test_output_parser.py
requirements.txt
```

---

### Task 4 — Scoring Engine
**Howler**: howler-scorer
**Effort**: M
**Serial risk**: no
**Dependency**: howler-harness (types/interfaces for result format)

Note: howler-scorer depends only on the result JSON schema that howler-harness defines. It does not need howler-harness to have run actual API calls. The dependency is a `#types` checkpoint — howler-scorer can start as soon as howler-harness's `result_store.py` schema is stable.

**Scope**:
- `scoring/score_results.py` — CLI entry point. Accepts `--results-dir`, `--rubrics-dir`, `--output`. Loads all result JSONs from a run, applies rubrics, produces scored output.
- `scoring/muster_scorer.py` — applies `rubrics/muster-rubric.yaml` to parsed muster outputs. Computes per-item scores. Automated items computed directly; human items emit a `needs_human_review` flag with the relevant output excerpt.
- `scoring/pax_scorer.py` — applies `rubrics/pax-rubric.yaml`. Deviation detection rate is the key metric; compute precision and recall separately.
- `scoring/forge_scorer.py` — applies `rubrics/forge-rubric.yaml`. Classification accuracy is a simple exact-match against `correct_classification` field in scenario YAML.
- `scoring/composite_scorer.py` — applies the composite formula from `rubrics/scoring-guide.yaml`. Produces a per-model, per-phase, and overall composite score.
- `scoring/comparison_report.py` — generates `results/COMPARISON-REPORT.md`: a structured markdown report with score tables, cost/latency comparison, per-phase analysis, and a recommendation section. The recommendation section must state clearly: "Sonnet meets threshold" or "Sonnet does not meet threshold" with the scores that drove the conclusion.
- `tests/test_muster_scorer.py`
- `tests/test_pax_scorer.py`
- `tests/test_forge_scorer.py`

**Deliverables**:
- `scoring/score_results.py`
- `scoring/muster_scorer.py`
- `scoring/pax_scorer.py`
- `scoring/forge_scorer.py`
- `scoring/composite_scorer.py`
- `scoring/comparison_report.py`
- `scoring/__init__.py`
- `tests/test_muster_scorer.py`
- `tests/test_pax_scorer.py`
- `tests/test_forge_scorer.py`

**Acceptance criteria**:
- [ ] `python -m scoring.score_results --results-dir results/raw/run-001 --rubrics-dir rubrics/ --output results/scored/run-001.json` runs without error on synthetic result fixtures
- [ ] `pytest tests/test_muster_scorer.py tests/test_pax_scorer.py tests/test_forge_scorer.py` passes with zero failures
- [ ] Deviation detection recall and precision are computed separately in pax scorer (not collapsed to F1 alone)
- [ ] `comparison_report.py` emits a `## Recommendation` section with a binary Sonnet pass/fail conclusion
- [ ] All automated rubric items produce a numeric score in [0.0, 1.0]
- [ ] Human-review items produce structured excerpts, not raw model output dumps

**File ownership** (CREATES only):
```
scoring/__init__.py
scoring/score_results.py
scoring/muster_scorer.py
scoring/pax_scorer.py
scoring/forge_scorer.py
scoring/composite_scorer.py
scoring/comparison_report.py
tests/test_muster_scorer.py
tests/test_pax_scorer.py
tests/test_forge_scorer.py
```

---

### Task 5 — Methodology Document
**Howler**: howler-methodology
**Effort**: S
**Serial risk**: no

Write the evaluation methodology document that explains what is being measured and why, so the results can be interpreted correctly and the evaluation can be reproduced.

**Scope**:
- `docs/METHODOLOGY.md` — the primary document. Covers:
  - Why this comparison matters (cost profile from TOKEN-OPTIMIZATION.md: Gold = 45% of cost at 15% of tokens)
  - What Gold actually does in each phase (Muster, Pax, Forge, self-reflect)
  - Why self-reflect is excluded from this comparison (already decided in TOKEN-OPTIMIZATION.md T1-B)
  - Evaluation design choices: why synthetic scenarios rather than live production runs, what bias this introduces, how to mitigate
  - Scoring design choices: why the Muster/Pax/Forge weighting is 40/40/20, how thresholds were set
  - Known limitations: Sonnet may behave differently on novel scenarios not in the library; evaluation is point-in-time
  - How to re-run the evaluation after model updates or protocol changes
- `docs/FINDINGS-TEMPLATE.md` — pre-structured document for recording results. Sections: Executive Summary, Score Tables, Phase-by-Phase Analysis, Cost/Latency Impact, Recommendation, Caveats. Designed to be filled in after running the harness.
- `docs/DECISION-FRAMEWORK.md` — a decision tree for interpreting results. Covers: "Sonnet passes all phases → full downgrade", "Sonnet passes Muster only → downgrade Muster, keep Opus for Pax/Forge", "Sonnet passes no phase → keep Opus", and mixed cases. Includes guidance on monitoring after any downgrade (what signals indicate regression).

**Acceptance criteria**:
- [ ] `METHODOLOGY.md` explains the 40/40/20 weighting rationale
- [ ] `METHODOLOGY.md` acknowledges the synthetic-scenario bias and names at least one mitigation
- [ ] `FINDINGS-TEMPLATE.md` has placeholder sections for all score table dimensions defined in rubrics
- [ ] `DECISION-FRAMEWORK.md` covers the case where Sonnet passes Muster but fails Pax (the most likely split outcome given task complexity differences)
- [ ] All three documents are written for an audience that knows Spectrum but has not read this PLAN.md

**File ownership** (CREATES only):
```
docs/METHODOLOGY.md
docs/FINDINGS-TEMPLATE.md
docs/DECISION-FRAMEWORK.md
```

---

### Task 6 — Historical Run Analysis
**Howler**: howler-history
**Effort**: S
**Serial risk**: no
**Dependency**: howler-rubrics (Task 2) must be complete first — rubrics define what to look for in historical data

Analyze the 5 documented spectrum runs to extract retrospective quality signal. This provides a baseline: "here is what Opus Gold actually produced in production." The historical analysis is complementary to the synthetic benchmark — it grounds the evaluation in real outputs.

**Scope**:
- `docs/HISTORICAL-ANALYSIS.md` — structured analysis of the 5 known runs:
  1. utils-test-0330 (Reaping, 3 Howlers, 100% success)
  2. taskmgr-0330 (Full, 3 Howlers, 32/32 tests)
  3. remnant-infra-0329 (4 Riders, 3 Inspector blockers)
  4. remnant-narrative-0329 (8 Riders, 10 blockers, smart quote gotcha)
  5. remnant-ux-0329 (8 Riders, zero conflicts, color-first sequencing)

  For each run, extract (from LESSONS.md files, MEMORY.md context, and public record):
  - What did Gold decompose, and was it correct? (file conflicts: 0 across all runs — note this)
  - What did Gold catch during Pax? (integration risks, seam failures)
  - Were there Forge decisions? What were they?
  - What made this run easy or hard for Gold specifically?

- A cross-run pattern analysis: what task characteristics correlate with Gold doing more vs less cognitive work? (e.g., "pure-create reaping mode = easy Muster, no Pax"; "8-Rider full with shared types = hard Muster + hard Pax")

- A gap analysis: where is the historical record insufficient to score retroactively? (These gaps inform which scenario types to prioritize in the synthetic library.)

- Explicit extraction of the "Gold adds value" moments from LESSONS files — cases where Gold's judgment prevented an integration failure. These are the cases Sonnet must be able to replicate.

**Acceptance criteria**:
- [ ] All 5 historical runs are covered with at least one paragraph each
- [ ] Cross-run pattern analysis names at least 3 distinguishing task characteristics that affect Gold's cognitive load
- [ ] Gap analysis identifies which scenario types have insufficient historical data
- [ ] At least 3 specific "Gold adds value" moments are extracted and described concretely
- [ ] Document does not rely on files that don't exist — all claims are traceable to MEMORY.md or publicly available LESSONS files referenced there

**File ownership** (CREATES only):
```
docs/HISTORICAL-ANALYSIS.md
```

---

## 4. Dependency Graph

```yaml
- id: howler-scenarios
  deps: []
  effort: M
  serial_risk: no

- id: howler-rubrics
  deps: []
  effort: M
  serial_risk: no

- id: howler-harness
  deps: []
  effort: L
  serial_risk: no

- id: howler-scorer
  deps: [howler-harness#types, howler-rubrics]
  effort: M
  serial_risk: no
  note: "howler-harness#types = result_store.py schema stable; does not need live API runs"

- id: howler-methodology
  deps: []
  effort: S
  serial_risk: no

- id: howler-history
  deps: [howler-rubrics]
  effort: S
  serial_risk: no
  note: "rubrics define scoring dimensions; history analysis applies them retroactively"
```

**Parallel drop**: howler-scenarios, howler-rubrics, howler-harness, howler-methodology all start simultaneously.

**Second wave**: howler-scorer starts when howler-harness signals `#types` stable AND howler-rubrics is complete. howler-history starts when howler-rubrics is complete.

---

## 5. File Ownership Matrix

| File | Howler | Action |
|------|--------|--------|
| `scenarios/muster/scenario-01.yaml` through `scenario-05.yaml` | howler-scenarios | CREATES |
| `scenarios/pax/scenario-01.yaml` through `scenario-05.yaml` | howler-scenarios | CREATES |
| `scenarios/forge/scenario-01.yaml` through `scenario-05.yaml` | howler-scenarios | CREATES |
| `scenarios/edge-cases/scenario-01.yaml` through `scenario-03.yaml` | howler-scenarios | CREATES |
| `scenarios/README.md` | howler-scenarios | CREATES |
| `rubrics/muster-rubric.yaml` | howler-rubrics | CREATES |
| `rubrics/pax-rubric.yaml` | howler-rubrics | CREATES |
| `rubrics/forge-rubric.yaml` | howler-rubrics | CREATES |
| `rubrics/scoring-guide.yaml` | howler-rubrics | CREATES |
| `harness/__init__.py` | howler-harness | CREATES |
| `harness/run_evaluation.py` | howler-harness | CREATES |
| `harness/scenario_loader.py` | howler-harness | CREATES |
| `harness/prompt_builder.py` | howler-harness | CREATES |
| `harness/output_parser.py` | howler-harness | CREATES |
| `harness/result_store.py` | howler-harness | CREATES |
| `harness/config.py` | howler-harness | CREATES |
| `tests/__init__.py` | howler-harness | CREATES |
| `tests/test_scenario_loader.py` | howler-harness | CREATES |
| `tests/test_prompt_builder.py` | howler-harness | CREATES |
| `tests/test_output_parser.py` | howler-harness | CREATES |
| `requirements.txt` | howler-harness | CREATES |
| `scoring/__init__.py` | howler-scorer | CREATES |
| `scoring/score_results.py` | howler-scorer | CREATES |
| `scoring/muster_scorer.py` | howler-scorer | CREATES |
| `scoring/pax_scorer.py` | howler-scorer | CREATES |
| `scoring/forge_scorer.py` | howler-scorer | CREATES |
| `scoring/composite_scorer.py` | howler-scorer | CREATES |
| `scoring/comparison_report.py` | howler-scorer | CREATES |
| `tests/test_muster_scorer.py` | howler-scorer | CREATES |
| `tests/test_pax_scorer.py` | howler-scorer | CREATES |
| `tests/test_forge_scorer.py` | howler-scorer | CREATES |
| `docs/METHODOLOGY.md` | howler-methodology | CREATES |
| `docs/FINDINGS-TEMPLATE.md` | howler-methodology | CREATES |
| `docs/DECISION-FRAMEWORK.md` | howler-methodology | CREATES |
| `docs/HISTORICAL-ANALYSIS.md` | howler-history | CREATES |

**Conflicts**: none. Every file appears in exactly one Howler's ownership column.

**Not in this matrix** (operator-created after Howlers complete):
- `results/raw/` — created at runtime by the harness
- `results/scored/` — created at runtime by the scorer
- `results/COMPARISON-REPORT.md` — generated output, not a source file

---

## 6. Risks

### R1 — Output parser fragility (HIGH)
Gold's outputs are free-form prose + structured sections. The output parser in howler-harness must extract structured data from unstructured text. If Gold formats file ownership tables differently across runs, precision will appear lower than it actually is (a measurement artifact, not a real quality difference).

**Mitigation**: Test `output_parser.py` against at least 3 format variations. Store raw outputs alongside parsed outputs so human review can correct misparsings. Add a `parse_confidence` field to result JSON.

### R2 — Scenario difficulty calibration (MEDIUM)
If all scenarios are too easy, Sonnet and Opus will score identically (both perfect). If all are too hard, both will fail. The comparison needs discriminating scenarios in the medium-hard range.

**Mitigation**: Require at least 3 of 15 scenarios to be rated `difficulty: hard`. Pilot scenarios against the harness's dry-run output before committing to the full library. The historical analysis (Task 6) will surface which real cases were actually challenging.

### R3 — Prompt fidelity (MEDIUM)
If `prompt_builder.py` does not faithfully reproduce what a real Gold agent would receive (missing context from SPECTRUM-OPS.md, CLAUDE.md, etc.), the evaluation tests a hypothetical Gold, not the real one. Sonnet might score higher on the simplified prompt than it would in production.

**Mitigation**: `prompt_builder.py` must be reviewed against current SPECTRUM-OPS.md Phase 1 (Muster), Phase 4 (Forge), and Phase 5 (Pax) before the harness runs. howler-harness should include a `--show-prompt` flag for manual inspection.

### R4 — Single-point-in-time evaluation (LOW-MEDIUM)
Both models will be evaluated on a fixed scenario library at a point in time. Model updates may change results. The evaluation framework is designed to be re-runnable, but the initial results should be labeled with model version/date.

**Mitigation**: `result_store.py` records model ID and API response metadata. `METHODOLOGY.md` (Task 5) documents this limitation explicitly.

### R5 — Token cost of running the evaluation (LOW)
Running 15–20 scenarios × 2 models × 3 phases could be expensive if Opus is called for all of them. At ~45k input + 17.5k output per Muster scenario, 5 Muster scenarios × Opus ≈ $0.75 in Gold tokens alone.

**Mitigation**: The harness supports `--model sonnet` to run Sonnet-only first (cheaper), identify which scenarios need Opus comparison, then run targeted Opus runs. Total estimated evaluation cost: ~$3–5 if all scenarios run both models.

### R6 — Subjectivity in human-scored rubric items (LOW)
Some rubric items (contract precision, decomposition soundness) require human judgment. Two reviewers may disagree.

**Mitigation**: `rubrics/scoring-guide.yaml` (Task 2) must define specific thresholds and examples for each human-scored item. The rubric items should lean toward binary (pass/fail per criterion) rather than Likert scales.

---

## 7. What Success Looks Like

After all tasks complete, the operator has:

1. A **scenario library** they can extend and re-run as the protocol evolves
2. A **harness** they can run today with `python -m harness.run_evaluation --model both --phase all`
3. **Scored results** with a machine-generated recommendation: "Sonnet meets threshold for Muster (score: X). Sonnet does not meet threshold for Pax (score: Y). Recommendation: downgrade Muster to Sonnet only."
4. A **decision framework** for what to do with mixed results (partial downgrade per phase)
5. An **estimated cost impact** for each configuration option (full Opus, full Sonnet, hybrid)

The expected outcome, based on task complexity analysis: Sonnet will likely pass Muster for simple-to-medium scenarios but show measurable degradation on 8-Howler DAG construction and CONTRACT.md Design-by-Contract precision. Pax validation (catching "green but wrong") is the highest-risk phase for Sonnet downgrade. Forge classification may be achievable with Sonnet given the 5-type taxonomy is well-defined.

This is a hypothesis. The evaluation exists to test it, not confirm it.
