# Gold Agent Evaluation — Findings Report

> **How to use this template**: Fill in each section after running the evaluation harness.
> Placeholder text in *italics* describes what to write. Remove placeholder text when filling in.
> Do not leave placeholder text in the final report.

---

## 1. Executive Summary

*3–5 sentences. State which phases Sonnet passed or failed, the overall recommendation (full downgrade / partial downgrade / keep Opus), and the cost impact of that recommendation. Example: "Sonnet passed Muster and Forge but fell short on Pax (78% vs 80% threshold). Recommendation: partial downgrade — use Sonnet for Muster and Forge, retain Opus for Pax. Expected savings: ~$2.10 per 5-Howler spectrum run."*

**Recommendation**: [ Full downgrade | Partial downgrade — specify phases | Keep Opus ]  
**Expected cost impact**: *$X saved per 5-Howler spectrum*  
**Confidence**: [ High | Medium | Low — explain if low ]

---

## 2. Run Metadata

| Field | Value |
|-------|-------|
| **Evaluation date** | *YYYY-MM-DD* |
| **Opus model version** | *e.g., claude-opus-4-5* |
| **Sonnet model version** | *e.g., claude-sonnet-4-6* |
| **Scenario library version** | *e.g., v1.0 (check scenarios/ directory)* |
| **Number of scenarios run** | *Muster: X, Pax: X, Forge: X, Edge-cases: X* |
| **Evaluator** | *Name or handle* |
| **Human scoring items** | *List which rubric items required human scoring this run* |
| **Inter-rater reliability** | *N/A (single evaluator) or kappa score if multiple reviewers* |

---

## 3. Score Tables

### 3.1 Phase-Level Scores

| Phase | Weight | Opus Score | Sonnet Score | Pass Threshold | Sonnet Result |
|-------|--------|-----------|--------------|----------------|---------------|
| Muster | 40% | *0.XX* | *0.XX* | 0.85 | [ PASS / FAIL ] |
| Pax | 40% | *0.XX* | *0.XX* | 0.80 | [ PASS / FAIL ] |
| Forge | 20% | *0.XX* | *0.XX* | 0.90 | [ PASS / FAIL ] |
| **Composite** | 100% | *0.XX* | *0.XX* | 0.82 | [ PASS / FAIL ] |

*Note: Composite = (Muster × 0.4) + (Pax × 0.4) + (Forge × 0.2)*

### 3.2 Muster Dimension Breakdown

| Dimension | Weight | Opus | Sonnet | Delta | Method |
|-----------|--------|------|--------|-------|--------|
| File Ownership Completeness | 18% | *0.XX* | *0.XX* | *±0.XX* | Automated |
| File Ownership Conflict Detection | 15% | *0.XX* | *0.XX* | *±0.XX* | Automated |
| DAG Edge Accuracy | 15% | *0.XX* | *0.XX* | *±0.XX* | Automated |
| CONTRACT.md Completeness | 17% | *0.XX* | *0.XX* | *±0.XX* | Hybrid |
| CONTRACT.md Postcondition Testability | 12% | *0.XX* | *0.XX* | *±0.XX* | Human |
| Decomposition Soundness | 12% | *0.XX* | *0.XX* | *±0.XX* | Hybrid |
| Politico Integration Quality | 11% | *0.XX* | *0.XX* | *±0.XX* | Hybrid |
| **Muster Composite** | 100% | *0.XX* | *0.XX* | *±0.XX* | |

### 3.3 Pax Dimension Breakdown

*Fill in after Pax rubric is finalized. Dimensions expected: Deviation Detection Recall, False Positive Rate, Seam Cross-Reference Accuracy, Integration Risk Classification, PAX-PLAN Merge Order Correctness.*

| Dimension | Weight | Opus | Sonnet | Delta | Method |
|-----------|--------|------|--------|-------|--------|
| Deviation Detection Recall | *TBD%* | *0.XX* | *0.XX* | *±0.XX* | Automated |
| False Positive Rate (inverted) | *TBD%* | *0.XX* | *0.XX* | *±0.XX* | Automated |
| Seam Cross-Reference Accuracy | *TBD%* | *0.XX* | *0.XX* | *±0.XX* | Automated |
| Integration Risk Classification | *TBD%* | *0.XX* | *0.XX* | *±0.XX* | Hybrid |
| PAX-PLAN Merge Order Correctness | *TBD%* | *0.XX* | *0.XX* | *±0.XX* | Automated |
| **Pax Composite** | 100% | *0.XX* | *0.XX* | *±0.XX* | |

### 3.4 Forge Dimension Breakdown

*Fill in after Forge rubric is finalized. Dimensions expected: per-type classification accuracy, circuit breaker detection, recovery action selection.*

| Dimension | Weight | Opus | Sonnet | Delta | Method |
|-----------|--------|------|--------|-------|--------|
| Transient Classification Accuracy | *TBD%* | *0.XX* | *0.XX* | *±0.XX* | Automated |
| Logical Classification Accuracy | *TBD%* | *0.XX* | *0.XX* | *±0.XX* | Automated |
| Structural Classification Accuracy | *TBD%* | *0.XX* | *0.XX* | *±0.XX* | Automated |
| Environmental Classification Accuracy | *TBD%* | *0.XX* | *0.XX* | *±0.XX* | Automated |
| Conflict Classification Accuracy | *TBD%* | *0.XX* | *0.XX* | *±0.XX* | Automated |
| Circuit Breaker Detection | *TBD%* | *0.XX* | *0.XX* | *±0.XX* | Automated |
| Recovery Action Selection | *TBD%* | *0.XX* | *0.XX* | *±0.XX* | Hybrid |
| **Forge Composite** | 100% | *0.XX* | *0.XX* | *±0.XX* | |

---

## 4. Phase-by-Phase Analysis

### 4.1 Muster Analysis

**Where Sonnet matched Opus:**
*List 2–4 specific scenarios or dimensions where Sonnet performed within 5% of Opus. Be specific — "scenario muster-02 (medium difficulty): both models produced identical file ownership matrices with no conflicts" rather than "Sonnet did well on easy tasks."*

**Where Sonnet fell short:**
*List specific scenarios and dimensions where Sonnet underperformed. Describe the failure mode — was it missed file conflicts? Vague postconditions? Incorrect DAG edges? Citing specific scenarios (e.g., "muster-04 adversarial: Sonnet missed the shared auth module conflict injected into howler-payments and howler-users") is more useful than general observations.*

**Recurring patterns:**
*Did Sonnet's failures cluster around a particular scenario type or difficulty tier? Reaping mode vs full muster? Contracts for interface-heavy vs pure-create Howlers? Politico integration on complex injections? Identifying patterns informs whether a targeted prompt improvement could close the gap.*

**Opus surprises:**
*Note any cases where Opus underperformed expectations, or where Sonnet outperformed. These may indicate the comparison is closer than the composite score suggests.*

### 4.2 Pax Analysis

**Deviation detection comparison:**
*How did Sonnet compare to Opus on catching deliberate CONTRACT.md deviations injected into scenarios? Report recall numbers. Which deviation types were most likely to be missed (type mismatches vs missing exports vs postcondition violations)?*

**False positive comparison:**
*How often did each model raise integration risks that were not in the scenario's known issues? False positives are less bad than false negatives in Pax, but high false positive rates indicate unreliable judgment.*

**Seam cross-reference accuracy:**
*When Howler A claimed to provide X and Howler B's debrief was inconsistent, did the models catch it? This is the core Pax skill.*

### 4.3 Forge Analysis

**Classification accuracy by failure type:**
*Report per-type accuracy for both models. The five types (transient, logical, structural, environmental, conflict) may not have equal scenario coverage — note the N for each type.*

| Failure Type | N scenarios | Opus accuracy | Sonnet accuracy |
|-------------|------------|---------------|-----------------|
| Transient | *N* | *X%* | *X%* |
| Logical | *N* | *X%* | *X%* |
| Structural | *N* | *X%* | *X%* |
| Environmental | *N* | *X%* | *X%* |
| Conflict | *N* | *X%* | *X%* |
| Circuit Breaker | *N* | *X%* | *X%* |

**Most common misclassification:**
*Which types did Sonnet confuse with each other? Transient vs logical confusion is lower-cost (recoverable by Orange) than structural vs transient confusion (structural misclassified as transient leads to wasted auto-resumes).*

---

## 5. Cost and Latency Impact

### 5.1 Token Usage

| Phase | Opus input | Opus output | Sonnet input | Sonnet output |
|-------|-----------|------------|--------------|---------------|
| Muster | *Xk tokens* | *Xk tokens* | *Xk tokens* | *Xk tokens* |
| Pax | *Xk tokens* | *Xk tokens* | *Xk tokens* | *Xk tokens* |
| Forge | *Xk tokens* | *Xk tokens* | *Xk tokens* | *Xk tokens* |
| **Total** | | | | |

*Note: If Sonnet uses significantly more output tokens than Opus on the same task, explain why. Verbose reasoning may offset cost savings.*

### 5.2 Cost Comparison

| Phase | Opus cost | Sonnet cost | Savings | Savings % |
|-------|----------|------------|---------|-----------|
| Muster | *$X.XX* | *$X.XX* | *$X.XX* | *XX%* |
| Pax | *$X.XX* | *$X.XX* | *$X.XX* | *XX%* |
| Forge | *$X.XX* | *$X.XX* | *$X.XX* | *XX%* |
| **Total Gold phases** | *~$4.25 baseline* | *$X.XX* | *$X.XX* | *XX%* |

*Reference: TOKEN-OPTIMIZATION.md estimates Gold phases cost ~$4.25 for a 5-Howler run using Opus. Sonnet downgrade should reduce this to ~$0.75 if all phases are downgraded.*

### 5.3 Latency

| Phase | Opus p50 latency | Sonnet p50 latency | Delta |
|-------|-----------------|-------------------|-------|
| Muster | *Xs* | *Xs* | *±Xs* |
| Pax | *Xs* | *Xs* | *±Xs* |
| Forge | *Xs* | *Xs* | *±Xs* |

*Note: Latency differences may affect spectrum wall-clock time. Muster latency matters more than Pax latency since Muster blocks Howler dispatch.*

---

## 6. Scenario-Level Detail

*This section is optional for scenarios where the two models produced similar results. Focus on scenarios where models diverged by more than 10 percentage points, or where Sonnet failed a threshold that Opus passed.*

### Divergent Scenarios

| Scenario ID | Phase | Difficulty | Opus score | Sonnet score | Delta | Primary failure dimension |
|-------------|-------|-----------|-----------|--------------|-------|--------------------------|
| *muster-XX* | Muster | *Easy/Med/Hard* | *0.XX* | *0.XX* | *-0.XX* | *e.g., Conflict Detection* |
| *pax-XX* | Pax | *Easy/Med/Hard* | *0.XX* | *0.XX* | *-0.XX* | *e.g., Deviation Detection* |

### Notable Failures

*For each scenario where Sonnet failed a threshold it should have passed, or where its failure was qualitatively informative, provide 2–4 sentences: what the scenario tested, what the correct answer was, what Sonnet produced instead, and what this implies for production risk.*

---

## 7. Recommendation

### 7.1 Per-Phase Verdict

| Phase | Sonnet threshold met? | Recommendation | Expected savings |
|-------|----------------------|----------------|-----------------|
| Muster | [ YES / NO / MARGINAL ] | [ Downgrade / Keep Opus / Conditional ] | *$X.XX per run* |
| Pax | [ YES / NO / MARGINAL ] | [ Downgrade / Keep Opus / Conditional ] | *$X.XX per run* |
| Forge | [ YES / NO / MARGINAL ] | [ Downgrade / Keep Opus / Conditional ] | *$X.XX per run* |

### 7.2 Overall Recommendation

*State the recommendation clearly. Reference DECISION-FRAMEWORK.md for the decision tree. Use the exact outcome labels from that document (e.g., "Outcome 1: Full Downgrade", "Outcome 2: Muster-Only Downgrade").*

**Outcome**: *[Outcome N from DECISION-FRAMEWORK.md]*  
**Action**: *Specific changes to CLAUDE.md model assignments and SPECTRUM-OPS.md*  
**Monitoring requirement**: *What to watch in the first N production runs after the change*

---

## 8. Caveats

*Limitations specific to this evaluation run. Complement the known limitations in METHODOLOGY.md with anything specific to this run's execution — e.g., "Scenario muster-03 was run against an older codebase snapshot that predates the auth refactor; results for that scenario may not reflect current production task shapes" or "Human scoring for Pax integration risk items was done by a single evaluator with limited familiarity with the auth module."*

---

## 9. Next Steps

*Based on the recommendation, what happens next? Use the options from DECISION-FRAMEWORK.md. Include specific files to change and a timeline.*

| Action | Owner | Target date | Notes |
|--------|-------|------------|-------|
| *Update CLAUDE.md model assignment for Gold* | *TBD* | *YYYY-MM-DD* | *If full or partial downgrade* |
| *Update SPECTRUM-OPS.md phase model overrides* | *TBD* | *YYYY-MM-DD* | *If partial downgrade* |
| *Run 3 production spectrums with Sonnet Gold* | *TBD* | *YYYY-MM-DD* | *Required for any downgrade* |
| *Re-evaluation cadence* | *TBD* | *Quarterly* | *After major model updates* |
