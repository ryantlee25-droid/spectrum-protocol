# White Agent Eval — Sonnet vs Haiku Comparison Report
**Run**: `run-20260331-191200`  
**Date**: 2026-04-01 01:20 UTC  
**Scenarios**: 5  
**Models**: sonnet, haiku

---

## Decision

**RECOMMENDATION: Keep White at Sonnet.**

Haiku does not meet one or more pass thresholds. Downgrade risks missing real issues in production PRs.

---

## Aggregate Scores

| Metric | Sonnet | Haiku | Threshold | Pass/Fail |
|--------|--------|-------|-----------|-----------|
| Composite Score | 0.800 ✗ | 0.670 ✗ | ≥ 0.85 | — |
| Detection Rate | 0.900 ✓ | 0.800 ✓ | ≥ 0.80 | — |
| Severity Accuracy | 0.900 ✓ | 0.900 ✓ | ≥ 0.75 | — |
| False Positive Rate | 0.700 ✗ | 1.300 ✗ | ≤ 0.20 | — |

---

## Per-Scenario Breakdown

| Scenario | Difficulty | Sonnet Composite | Haiku Composite | Sonnet Detection | Haiku Detection |
|----------|------------|-----------------|-----------------|-----------------|-----------------|
| scenario-01 | easy | 0.800 | 0.600 | 0.750 | 0.750 |
| scenario-02 | easy | 0.800 | 0.800 | 1.000 | 1.000 |
| scenario-03 | medium | 0.725 | 0.800 | 1.000 | 1.000 |
| scenario-04 | medium | 0.800 | 0.600 | 1.000 | 0.750 |
| scenario-05 | hard | 0.875 | 0.550 | 0.750 | 0.500 |

---

## Per-Bug Detection

Shows whether each planted bug was caught by each model.

| Scenario | Bug | Expected Severity | Sonnet Found | Haiku Found |
|----------|-----|------------------|-------------|-------------|
| scenario-01 | Null deref (findOne) | blocker | ✓ | ✓ |
| scenario-01 | PII in console.log | blocker | ✓ | ✓ |
| scenario-02 | SQL injection (search) | blocker | ✓ | ✓ |
| scenario-02 | SQL injection (autocomplete) | blocker | ✓ | ✓ |
| scenario-02 | result.analytics bug | blocker | ✓ | ✓ |
| scenario-03 | Off-by-one offset | blocker | ✓ | ✓ |
| scenario-03 | Missing page >= 1 validation | warning | ✓ | ✓ |
| scenario-04 | N+1 query pattern | warning | ✓ | ✓ |
| scenario-04 | Null deref on findById | blocker | ✓ | ✓ |
| scenario-05 | Circular dependency | blocker | ✓ | ✓ |
| scenario-05 | Missing error handling in login() | warning | ✓ | ✗ |

---

## Analysis

**Detection gap (Sonnet − Haiku)**: +0.100
**Composite gap**: +0.130

**Haiku failed on**: composite (0.670 < 0.85), false positive rate (1.300 > 0.20)

These gaps indicate Haiku lacks the reasoning depth required for reliable pre-PR review.
Recommend keeping White at Sonnet until a targeted eval shows improvement on these metrics.

---

## Thresholds Reference

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Composite Score | ≥ 0.85 | Same bar as Politico eval (gold-eval-0331 baseline) |
| Detection Rate | ≥ 0.80 | Missing 1 in 5 bugs is the upper tolerance for a quality gate |
| Severity Accuracy | ≥ 0.75 | Misclassifying blockers as warnings has direct workflow impact |
| False Positive Rate | ≤ 0.20 | Over-blocking wastes developer time and erodes trust |
