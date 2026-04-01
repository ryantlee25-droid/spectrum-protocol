# PLAN: Politico Agent Evaluation — Sonnet vs Haiku
**Author**: Blue (◎)
**Date**: 2026-03-31
**Target directory**: `~/spectrum-protocol/evaluation/politico-eval/`

---

## 1. Objective

Determine whether Haiku can replace Sonnet as the Politico agent in Phase 1.5 (The Passage) of the Spectrum Protocol.

Politico's job is narrow and well-defined: read MANIFEST.md and CONTRACT.md, then find planted or latent bugs across three axes — file ownership gaps, contract ambiguities, and decomposition flaws. The question is whether Haiku's pattern-matching on structured artifacts is sufficient for this task, or whether it requires Sonnet's deeper reasoning to catch non-obvious problems.

A successful downgrade moves Spectrum from D1=2 toward D1=3 on the cost curve and reduces per-spectrum overhead without weakening the quality gate.

---

## 2. What Politico Actually Does

From `~/.claude/agents/politicos.md` and production runs:

1. **Reads** MANIFEST.md (task list, file ownership matrix, DAG) and CONTRACT.md (shared types, naming conventions, integration points, per-Howler DbC).
2. **Attacks** across three axes:
   - **File ownership gaps**: implicit shared files (barrel exports, route registrations, config), files a Howler will need but not own, double-modification risks
   - **Contract ambiguities**: vague interface definitions that allow incompatible implementations, missing error contracts, underspecified seams
   - **Decomposition flaws**: hidden sequential dependencies in parallel tasks, oversized tasks (critical-path risk), synthesis tasks not modeled as sequential
3. **Reports**: blockers (must fix before drop), warnings (should fix), observations (FYI), and an Accepted section (things considered but found OK)
4. **Re-reviews** after Gold addresses blockers — confirms resolution before clearing

The adversarial stance is the key variable. Haiku is capable of listing what it sees. The question is whether it can reason about what's *missing* and what could go *wrong* — the adversarial gap-finding that makes Politico valuable.

**Evidence from gold-eval-0331**: Politico (Sonnet) found 3 real blockers and 6 warnings in that spectrum's muster artifacts. All 3 blockers were genuine — they would have caused Howler failures. This sets the baseline for what acceptable Politico output looks like.

---

## 3. Scope

### In scope
- Politico's ability to find planted bugs in MANIFEST.md + CONTRACT.md pairs
- Detection rate across all three finding categories (gaps, ambiguities, flaws)
- False positive rate (flagging non-issues as blockers)
- Severity accuracy (blocker vs warning vs observation classification)
- Report quality: specificity, actionability of suggested fixes

### Not in scope
- Politico's re-review behavior (confirming blockers are resolved) — this is secondary
- Cost/latency comparison (Politico is a short, focused run; cost delta is small)
- Haiku as a replacement for any other Sonnet agent (separate evals needed)
- Novel scenario types that Politico has never seen in production

### Decision this eval must answer
Is Haiku's detection rate on planted bugs ≥ 0.85 with false positive rate ≤ 0.20?

If yes: downgrade Politico to Haiku.
If no: keep Sonnet, document which bug categories Haiku misses.

---

## 4. Eval Design

### 4.1 Approach

Each test scenario is a (MANIFEST.md, CONTRACT.md) pair with **planted bugs**. Bugs are planted deliberately and documented in a ground-truth file alongside each scenario. The evaluator runs both Sonnet and Haiku against each scenario using the exact Politico prompt from `~/.claude/agents/politicos.md`, then scores output against the ground truth.

Scenarios are modeled on realistic spectrum runs — the domain changes per scenario, but the artifact structure is always the same MANIFEST + CONTRACT pair that Gold produces.

### 4.2 Bug Categories and Planted Counts

Each scenario plants exactly **one bug per category** (three bugs total), plus optionally one **clean element** (something that looks suspicious but is actually fine — tests false positive rate). A total of 7 scenarios yields 21 planted bugs.

| Category | What's planted | Why it's hard |
|---|---|---|
| Ownership Gap | A file that Howlers will obviously need to write/modify is absent from the matrix | Requires knowing implicit files (barrel exports, config, route registrations) |
| Contract Ambiguity | An interface definition vague enough that two Howlers could implement incompatible versions | Requires reasoning about what "clear enough" means for independent implementation |
| Decomposition Flaw | Two tasks marked parallel that have a hidden sequential dependency | Requires tracing data flow through the task graph, not just reading stated deps |

### 4.3 Difficulty Distribution

| Scenario | Difficulty | Domain | Notes |
|---|---|---|---|
| S1 | easy | Static site (3 Howlers, pure-create) | Baseline — obvious ownership gap |
| S2 | easy | REST API (4 Howlers) | Obvious contract ambiguity (no error type defined) |
| S3 | medium | Auth + session management (5 Howlers) | Non-obvious decomp flaw (session store dep) |
| S4 | medium | Data pipeline (5 Howlers) | Subtle ownership gap (shared schema migration file) |
| S5 | medium | React component library (5 Howlers) | Compound ambiguity (two interfaces underspecified) |
| S6 | hard | Billing system (6 Howlers) | All three bugs planted; clean element included |
| S7 | hard | Event-driven microservice (6 Howlers) | Non-obvious dep + implicit shared file + subtle type ambiguity |

### 4.4 What "Finding a Bug" Means

A bug is **found** if the Politico output:
1. Names or clearly describes the specific file, interface, or task pair involved
2. Places it in the correct category (ownership gap / contract ambiguity / decomposition flaw)
3. Provides a concrete suggested fix (not just "this needs attention")

Partial credit: names the file/interface but wrong category = 0.5. Names the problem but no fix = 0.75. Correct finding with specific fix = 1.0.

A **false positive** is any finding classified as a blocker that does not correspond to a planted bug and is not a legitimate issue with the scenario artifacts (judged by human review).

---

## 5. Scenarios

### File Structure

```
scenarios/
  scenario-01/
    manifest.md          # The MANIFEST.md to review
    contract.md          # The CONTRACT.md to review
    ground-truth.yaml    # Planted bugs + expected findings
  scenario-02/
    ...
  ...
```

### Ground Truth Schema

```yaml
scenario_id: "politico-01"
difficulty: "easy"
domain: "static site"
description: "3-Howler pure-create Next.js blog; one planted ownership gap"

planted_bugs:
  - bug_id: "bug-01"
    category: "ownership_gap"
    severity: "blocker"
    location: "MANIFEST.md ownership matrix"
    description: "globals.css is referenced in task description but absent from ownership matrix"
    expected_finding: |
      Politico should flag that globals.css (or equivalent shared stylesheet) is needed
      by at least one Howler but not claimed by anyone.
    scoring:
      full_credit_if: "names the specific file AND notes it's unclaimed AND suggests assigning it"
      partial_credit_if: "names the general category (shared styles) but not the specific file"
      no_credit_if: "mentions styles only in passing or in an Accepted section"

  - bug_id: "bug-02"
    category: "contract_ambiguity"
    severity: "warning"
    location: "CONTRACT.md naming conventions"
    description: "Component naming section says 'use standard React conventions' without specifying PascalCase vs kebab-case for file names"
    expected_finding: |
      Politico should flag that 'standard React conventions' is ambiguous — Howlers
      could create About.tsx, about.tsx, or about/index.tsx and all would be 'standard'.
    scoring:
      full_credit_if: "identifies the specific convention gap and names the conflicting possibilities"
      partial_credit_if: "notes naming conventions are underspecified"
      no_credit_if: "accepts the naming section as adequate"

  - bug_id: "bug-03"
    category: "decomposition_flaw"
    severity: "warning"
    location: "MANIFEST.md DAG"
    description: "howler-404 is marked parallel to howler-about but both modify next.config.js"
    expected_finding: |
      Politico should flag that two parallel Howlers both need to modify next.config.js
      (for custom error page configuration), creating a file ownership conflict masked
      as a parallel decomposition.
    scoring:
      full_credit_if: "identifies next.config.js as the shared file AND names both Howlers"
      partial_credit_if: "flags the config file issue without naming both Howlers"
      no_credit_if: "misses the file conflict entirely"

clean_elements:
  - element_id: "clean-01"
    location: "CONTRACT.md shared types"
    description: "PageProps interface is defined once and both pages import from it — this looks like it could be a redundancy issue but it's actually fine"
    expected_handling: "Politico should either accept this or not mention it at all"
    false_positive_if: "Politico flags this as a blocker or warning"

false_positive_threshold: 0.20
pass_threshold: 0.85
```

### Scenario Summaries

**S1 — Static Site (easy)**
3-Howler pure-create Next.js blog. Planted: (a) shared stylesheet absent from ownership matrix, (b) ambiguous naming convention for file casing, (c) two Howlers both modify next.config.js but it's not in the matrix. Clean: shared PageProps type looks redundant but is fine.

**S2 — REST API (easy)**
4-Howler Express API with auth, routes, middleware, and tests. Planted: (a) `src/app.ts` (Express app factory) missing from matrix — needed by both routes and middleware Howlers, (b) error response type not defined in CONTRACT.md (each Howler could define its own `ApiError`), (c) test Howler is parallel to implementation Howlers but can't write integration tests until the routes exist. Clean: shared constants file is in the matrix.

**S3 — Auth + Session (medium)**
5-Howler TypeScript auth system. Planted: (a) `src/db/schema.ts` (shared session table schema) not in ownership matrix, (b) `SessionData` interface defined in CONTRACT.md but `expires` field type is `Date | string` — ambiguous serialization contract, (c) `howler-middleware` and `howler-session` are parallel but session middleware needs the session store initialized first. Clean: JWT secret handling looks like a shared ownership problem but CONTRACT.md covers it.

**S4 — Data Pipeline (medium)**
5-Howler ETL pipeline. Planted: (a) shared Alembic migration file (`migrations/versions/001_initial.py`) not in matrix but both `howler-schema` and `howler-loader` will need to create/read it, (b) `Record` type in CONTRACT.md has optional field `metadata: object` — too loose for independent implementation, (c) `howler-validate` and `howler-transform` are parallel but transform uses validate's output format. Clean: shared config.yaml is in the matrix and correctly owned.

**S5 — React Component Library (medium)**
5-Howler Storybook + React component library. Planted: (a) `src/index.ts` barrel export file not in matrix (every Howler adds their component exports to it), (b) `ComponentProps` base interface in CONTRACT.md doesn't specify whether `className` prop is required or optional — leads to incompatible implementations, (c) `howler-tokens` (design tokens) and `howler-components` are parallel but components import token values. Clean: each Howler's Storybook stories file is correctly in each Howler's ownership.

**S6 — Billing System (hard)**
6-Howler billing system with subscription, invoicing, payments, webhooks, notifications, and an integration Howler. Planted: (a) `src/types/events.ts` (shared billing event types) not in matrix but 4 Howlers emit events, (b) `PaymentIntent` type uses `amount: number` — ambiguous currency (cents vs dollars), (c) `howler-webhooks` is parallel to `howler-payments` but needs to register webhook endpoints that depend on `howler-payments` defining the routes first. Clean element: `howler-integration` is correctly marked as sequential with deps on all other Howlers — Politico should accept this and not flag it as over-constrained.

**S7 — Event-Driven Microservice (hard)**
6-Howler event-driven service (producer, consumer, schema registry, dead-letter queue, monitoring, deployment). Planted: (a) `docker-compose.yml` is referenced in deployment task description but not in ownership matrix — both `howler-deployment` and `howler-monitoring` need it, (b) event schema type `EventEnvelope` in CONTRACT.md specifies `payload: unknown` — consumer and producer could implement incompatible payload handling, (c) `howler-dlq` (dead-letter queue) is parallel to `howler-consumer` but DLQ routing depends on consumer error classification constants. Clean: Kafka topic names are consistently defined in CONTRACT.md — Politico should accept this.

---

## 6. Scoring Rubric

### 6.1 Per-Scenario Scores

**Detection Rate** (primary metric, weight 0.50):
```
For each planted bug b in scenario s:
  score(b) = 1.0 if full credit criteria met
           = 0.5 if partial credit criteria met
           = 0.0 if not found

detection_rate(s) = sum(score(b) for b in planted_bugs(s)) / len(planted_bugs(s))
```

**Severity Accuracy** (weight 0.30):
```
For each finding f that corresponds to a planted bug:
  severity_correct(f) = 1.0 if classified correctly (blocker/warning/observation)
                      = 0.5 if off by one level (blocker→warning or warning→observation)
                      = 0.0 if completely wrong (blocker→observation)

severity_accuracy(s) = sum(severity_correct(f) for matched findings) / len(matched_findings)
# If no bugs found, severity_accuracy = 0
```

**False Positive Rate** (weight 0.20, penalizes over-flagging):
```
fp_blockers = count of blockers in output that don't match any planted bug
              and are judged non-issues by human review
total_clean = count of non-bug elements in scenario (including clean_elements)

fp_rate(s) = fp_blockers / (total_clean + 1)  # +1 to avoid div/0
# fp_rate feeds into score as a penalty: score component = max(0, 1.0 - fp_rate * 2)
```

**Per-scenario composite**:
```
scenario_score(s) = 0.50 * detection_rate(s)
                  + 0.30 * severity_accuracy(s)
                  + 0.20 * max(0, 1.0 - fp_rate(s) * 2)
```

### 6.2 Aggregate Scores

```
composite_score(model) = mean(scenario_score(s) for s in all_scenarios)
detection_rate_overall(model) = mean(detection_rate(s) for s in all_scenarios)
fp_rate_overall(model) = mean(fp_rate(s) for s in all_scenarios)
```

### 6.3 Pass Thresholds

| Metric | Pass threshold | Rationale |
|---|---|---|
| `composite_score` | ≥ 0.85 | Same bar as Gold Muster phase in gold-eval-0331 |
| `detection_rate_overall` | ≥ 0.80 | Missing 1 in 5 planted bugs is the upper tolerance |
| `fp_rate_overall` | ≤ 0.20 | A Politico that over-blocks wastes Gold's time; false blockers erode trust |
| `severity_accuracy` | ≥ 0.75 | Misclassifying blockers as warnings (or vice versa) has real workflow impact |

### 6.4 Verdict Logic

```
PASS (downgrade Politico to Haiku) if ALL of:
  - composite_score(haiku) >= 0.85
  - detection_rate_overall(haiku) >= 0.80
  - fp_rate_overall(haiku) <= 0.20
  - severity_accuracy(haiku) >= 0.75

CONDITIONAL PASS if:
  - composite_score(haiku) >= 0.80 AND
  - haiku fails on hard scenarios only (S6, S7) AND
  - sonnet also degrades on S6, S7 (calibration failure, not model failure)

FAIL (keep Sonnet) if any threshold is not met and not explainable by calibration
```

---

## 7. Evaluation Harness

### 7.1 Approach

Unlike the gold-eval harness (which required a custom Python harness for 18 scenarios across 3 Gold phases), the Politico eval is simpler: the input is always two markdown files, and the output is a structured report. The harness can be a lightweight Python script.

The Politico prompt is taken verbatim from `~/.claude/agents/politicos.md` — no prompt engineering. This tests Politico as deployed, not a hypothetical version.

### 7.2 Script Structure

```
politico-eval/
  PLAN.md                          # This file
  scenarios/
    scenario-01/
      manifest.md
      contract.md
      ground-truth.yaml
    scenario-02/ ... scenario-07/
  rubric.yaml                      # Scoring rubric (machine-readable)
  harness/
    __init__.py
    run_eval.py                    # CLI: --model [sonnet|haiku|both] --scenario [id|all]
    prompt_builder.py              # Builds Politico prompt from manifest.md + contract.md
    output_parser.py               # Extracts findings (blockers/warnings) from Politico output
    scorer.py                      # Applies rubric.yaml against ground-truth + parsed output
    result_store.py                # Writes results/{run-id}/{scenario-id}/{model}.json
  requirements.txt                 # anthropic, pyyaml
  results/                         # Created at runtime
```

### 7.3 Harness CLI

```bash
# Run all scenarios, both models
python -m harness.run_eval --model both --scenario all

# Dry run (print prompts, no API calls)
python -m harness.run_eval --model haiku --scenario politico-01 --dry-run

# Score a completed run
python -m harness.run_eval --score --results-dir results/run-20260331-120000

# Generate comparison report
python -m harness.run_eval --report --results-dir results/run-20260331-120000
```

### 7.4 Prompt Builder

The prompt is constructed as:

```
[Politico system prompt — verbatim from politicos.md]

You are reviewing the following spectrum artifacts:

**MANIFEST.md**
---
{manifest_content}
---

**CONTRACT.md**
---
{contract_content}
---

Rain ID: {scenario_id}
```

No additional context. Politico in production only sees MANIFEST.md and CONTRACT.md — the harness must replicate this faithfully.

### 7.5 Output Parser

Extracts from Politico's free-text report:
- Blockers: list of `{title, category, finding_text, suggested_fix}`
- Warnings: same structure
- Verdict: `BLOCKED` or `CLEAR`
- Accepted items: list of titles (for false positive analysis)

Parser uses heading-level regex (`## Blockers`, `### [title]`, `**Category**:`) — the output format is tightly specified in the Politico prompt so parser fragility is low.

Store `parse_confidence` alongside results (1.0 if all sections parsed cleanly, lower if sections missing or malformed).

### 7.6 Scorer

For each scenario + model result:
1. Load `ground-truth.yaml`
2. For each planted bug, search parsed findings for a match (keyword + file name matching against `expected_finding` text)
3. Apply partial credit rules from ground truth `scoring` fields
4. Compute `detection_rate`, `severity_accuracy`, `fp_rate`, `scenario_score`
5. Write to `results/{run-id}/{scenario-id}/{model}.json`

After all scenarios:
1. Compute `composite_score`, `detection_rate_overall`, `fp_rate_overall` per model
2. Apply verdict logic
3. Write `results/{run-id}/COMPARISON-REPORT.md`

### 7.7 Result JSON Schema

```json
{
  "scenario_id": "politico-03",
  "model": "haiku",
  "model_id": "claude-haiku-4-5",
  "raw_output": "...",
  "parsed": {
    "blockers": [{"title": "...", "category": "ownership_gap", "finding_text": "...", "suggested_fix": "..."}],
    "warnings": [...],
    "verdict": "BLOCKED",
    "accepted": [...]
  },
  "parse_confidence": 0.95,
  "scores": {
    "detection_rate": 0.67,
    "severity_accuracy": 0.80,
    "fp_rate": 0.0,
    "scenario_score": 0.58,
    "bug_scores": {
      "bug-01": {"found": true, "credit": 1.0, "severity_correct": true},
      "bug-02": {"found": true, "credit": 0.5, "severity_correct": true},
      "bug-03": {"found": false, "credit": 0.0, "severity_correct": false}
    }
  },
  "tokens_used": {"input": 2400, "output": 800},
  "latency_ms": 3200,
  "cost_usd": 0.0012,
  "timestamp": "2026-03-31T12:00:00Z"
}
```

---

## 8. Tasks

Four tasks with clean file ownership. All can run in parallel.

### Task 1 — Scenarios
**Effort**: M
Build the 7 scenario pairs (manifest.md + contract.md + ground-truth.yaml). Each scenario must have exactly 3 planted bugs, a clean element, and a completed ground-truth.yaml per the schema above.

**Deliverables**: `scenarios/scenario-01/` through `scenarios/scenario-07/`

**Acceptance criteria**:
- [ ] All 7 scenarios are complete with all three files present
- [ ] Each ground-truth.yaml is valid YAML and passes schema check
- [ ] Difficulty distribution matches the plan: 2 easy, 3 medium, 2 hard
- [ ] Planted bugs span all 3 categories across the scenario set (all categories represented)
- [ ] Each scenario's domain is distinct from the others

### Task 2 — Rubric
**Effort**: S
Write `rubric.yaml` with machine-readable scoring definitions matching Section 6.

**Deliverables**: `rubric.yaml`

**Acceptance criteria**:
- [ ] All scoring formulas match Section 6 exactly (no interpretation required)
- [ ] Pass thresholds for all 4 metrics are present
- [ ] Verdict logic is encoded as explicit conditionals

### Task 3 — Harness
**Effort**: M
Build `harness/run_eval.py`, `harness/prompt_builder.py`, `harness/output_parser.py`, `harness/scorer.py`, `harness/result_store.py`.

**Deliverables**: `harness/` directory, `requirements.txt`

**Acceptance criteria**:
- [ ] `python -m harness.run_eval --dry-run --model haiku --scenario politico-01` prints prompt without API call
- [ ] Output parser correctly extracts blockers/warnings from at least 2 Politico output format variations (tested manually or in unit tests)
- [ ] Scorer produces all score fields in result JSON schema
- [ ] `--report` flag generates `COMPARISON-REPORT.md` with a binary verdict

### Task 4 — Methodology Note
**Effort**: S
Write `METHODOLOGY.md` covering: what this eval measures, what it does NOT measure (Politico's re-review behavior, production artifact realism), and how to interpret a conditional pass.

**Deliverables**: `docs/METHODOLOGY.md`

**Acceptance criteria**:
- [ ] Explains why detection rate is weighted higher than fp rate
- [ ] Identifies the main validity threat (are planted bugs realistic enough?)
- [ ] Documents the conditional pass interpretation
- [ ] Written for someone who knows Spectrum but hasn't read this PLAN.md

---

## 9. File Ownership Matrix

| File | Task | Action |
|------|------|--------|
| `scenarios/scenario-01/manifest.md` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-01/contract.md` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-01/ground-truth.yaml` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-02/manifest.md` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-02/contract.md` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-02/ground-truth.yaml` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-03/manifest.md` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-03/contract.md` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-03/ground-truth.yaml` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-04/manifest.md` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-04/contract.md` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-04/ground-truth.yaml` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-05/manifest.md` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-05/contract.md` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-05/ground-truth.yaml` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-06/manifest.md` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-06/contract.md` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-06/ground-truth.yaml` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-07/manifest.md` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-07/contract.md` | Task 1 — Scenarios | CREATES |
| `scenarios/scenario-07/ground-truth.yaml` | Task 1 — Scenarios | CREATES |
| `rubric.yaml` | Task 2 — Rubric | CREATES |
| `harness/__init__.py` | Task 3 — Harness | CREATES |
| `harness/run_eval.py` | Task 3 — Harness | CREATES |
| `harness/prompt_builder.py` | Task 3 — Harness | CREATES |
| `harness/output_parser.py` | Task 3 — Harness | CREATES |
| `harness/scorer.py` | Task 3 — Harness | CREATES |
| `harness/result_store.py` | Task 3 — Harness | CREATES |
| `requirements.txt` | Task 3 — Harness | CREATES |
| `docs/METHODOLOGY.md` | Task 4 — Methodology | CREATES |

No conflicts. Every file appears in exactly one task's ownership column.

---

## 10. Risks

### R1 — Planted bugs too obvious (MEDIUM)
If the bugs are too easy to spot (e.g., a missing file that's explicitly referenced in the task description), both Sonnet and Haiku will find them and the eval won't discriminate. The medium/hard scenarios must require inference across the artifact pair.

**Mitigation**: Hard scenarios (S6, S7) plant bugs that require cross-referencing MANIFEST.md's DAG against CONTRACT.md's type definitions — not findable from either artifact alone.

### R2 — Planted bugs not realistic (MEDIUM)
If the artifacts look synthetic, both models may behave differently than on production manifests. Politico in production sees Gold-authored artifacts with Gold's specific writing style and structure.

**Mitigation**: Scenario artifacts are modeled on the gold-eval-0331 MANIFEST.md and CONTRACT.md structure (which was real Gold output). The domain changes but the format is faithful.

### R3 — Output parser fragility (LOW-MEDIUM)
Politico's output format is tightly specified in its prompt, so format variation should be low. But Haiku may produce slightly different section structures than Sonnet.

**Mitigation**: Store raw output alongside parsed output. `parse_confidence` field flags low-confidence parses for human review before scoring.

### R4 — False positive measurement is human-dependent (LOW)
Determining whether a blocker is a "false positive" requires human judgment — a model might find a real issue that wasn't planted. The ground truth records planted bugs, but a sophisticated model might find other legitimate problems.

**Mitigation**: Human reviewer classifies all non-planted blockers before scoring. Legitimate findings that weren't planted count as true positives (detection credit for finding a real issue). Only non-issues classified as blockers count as false positives.

---

## 11. Expected Outcome

Based on prior evals and Haiku's known profile:

- **Easy scenarios (S1, S2)**: Haiku likely finds obvious gaps and ambiguities. Ownership gaps that require only "is this file in the list?" are Haiku-sized pattern matching.
- **Medium scenarios (S3–S5)**: Mixed. Decomposition flaws (hidden sequential deps) require tracing data flow, which Haiku may miss. Contract ambiguities that require knowing "what does incompatible implementation look like in practice" may degrade.
- **Hard scenarios (S6, S7)**: Haiku likely misses the cross-artifact bugs where the decomposition flaw only becomes visible when reading the CONTRACT.md type definition alongside the MANIFEST.md DAG.

**Hypothesis**: Haiku will pass detection on ownership gaps (≥ 0.85), degrade on decomposition flaws (est. 0.55–0.65), and be mixed on contract ambiguities (est. 0.65–0.75). Overall composite will be 0.72–0.78 — below the 0.85 threshold.

This is a hypothesis. The eval exists to test it. A result significantly above 0.85 for Haiku would be a meaningful cost win.

---

## 12. What Success Looks Like

After the eval runs:

1. A **COMPARISON-REPORT.md** with composite scores for both models and a binary verdict
2. **Per-bug breakdown**: which categories Haiku misses vs finds — useful even if Haiku fails overall
3. A **decision**: downgrade to Haiku, keep Sonnet, or conditional (Haiku on easy/medium, Sonnet on hard)
4. If Haiku fails: which specific bug categories drove the failure — informs whether a future Haiku with better prompting could close the gap

Estimated total cost: ~$0.20–0.40 for all 7 scenarios × 2 models at Politico's short context window (~2–3k tokens input).
