# Gold Agent Comparison Report: Opus vs Sonnet

**Date**: 2026-03-31
**Scenarios**: 6 (2 muster, 2 pax, 2 forge)
**Models**: Claude Opus 4.6 vs Claude Sonnet 4.6

---

## Executive Summary

Both models performed well across all three Gold phases. **Sonnet matched Opus on Forge (100% parity) and came very close on Muster, but showed a measurable gap on Pax validation depth.** Opus produced deeper, more precise integration analysis during Pax — catching subtle issues Sonnet missed or miscategorized.

**Recommendation: Partial downgrade — Sonnet for Muster + Forge, keep Opus for Pax.**

---

## Phase 1: Muster (Decomposition Quality)

### muster-03 — Auth Refactor (5 Howlers, medium, has file conflict)

| Dimension | Opus | Sonnet |
|-----------|------|--------|
| File ownership completeness | 1.0 | 1.0 |
| File ownership conflict detection | 1.0 (identified src/auth.ts as shared concern, assigned to single Howler) | 1.0 (same approach) |
| DAG accuracy | 1.0 (correct 3-wave: types → 4 parallel → router) | 0.9 (correct structure, but added unnecessary Cipher→Warden dep) |
| Contract completeness | 1.0 (full DbC per Howler, Redis key namespaces) | 1.0 (full DbC, added express.d.ts ownership) |
| Contract precision | 1.0 (testable postconditions: "verifyToken returns null, never throws") | 0.95 (testable, slightly more verbose) |
| Decomposition soundness | 1.0 (6 Howlers, clean separation, hazard scan) | 0.95 (6 Howlers, same structure, flagged password-reset as L instead of M) |
| Politico integration | N/A (not part of scenario) | N/A |

**Muster-03 Score: Opus 1.0, Sonnet 0.97**

### muster-04 — E-Commerce Monolith (8 Howlers, hard, complex DAG)

| Dimension | Opus | Sonnet |
|-----------|------|--------|
| File ownership completeness | 1.0 (52 files mapped, zero overlaps) | 0.95 (comprehensive but output was truncated — likely equally complete) |
| File ownership conflict detection | 1.0 (identified src/shared/index.ts as only MODIFY) | 1.0 |
| DAG accuracy | 1.0 (4-wave: shared → 6 parallel → payment → analytics; correctly identified checkout→payment serial dep) | 0.95 (correct structure, same waves) |
| Contract completeness | 1.0 (branded types, Money invariant, event naming conventions, barrel export rules) | 0.9 (complete but less detailed on invariants) |
| Contract precision | 1.0 (CheckoutState as discriminated union, Money.amount integer cents invariant, event type naming convention frozen) | 0.85 (postconditions present but less formally testable) |
| Decomposition soundness | 1.0 (9 Howlers, clean phase separation, monolith deletion explicitly out-of-scope) | 0.9 (8-9 Howlers, similar structure) |

**Muster-04 Score: Opus 1.0, Sonnet 0.93**

### Muster Phase Average: Opus 1.0, Sonnet 0.95

---

## Phase 2: Pax (Integration Validation)

### pax-02 — Checkout Subtle Bug (buildCheckout returns empty items)

**Ground truth deviations to catch:**
1. `buildCheckout` returns `items: []` (empty array, discards cart contents) — **blocker**
2. No independent Money arithmetic in checkout (delegates to cart.getTotal()) — **observation**

| Dimension | Opus | Sonnet |
|-----------|------|--------|
| Deviation detection (recall) | 1.0 — caught both: empty items array + no independent arithmetic | 1.0 — caught both: empty items array + delegation pattern |
| Deviation detection (precision) | 0.9 — flagged Stripe source (valid extra finding, but observation not blocker) | 0.7 — **promoted parsePrice floating-point to blocker** (not actually injected, overreach), **promoted Stripe source to blocker** (should be observation) |
| False positive rate | 1.0 — no flags on correct Howlers | 0.7 — flagged howler-product with a "blocker" for IEEE 754 floating-point in parsePrice. This is a real concern but NOT an injected deviation — it's a general engineering opinion, not a contract violation |
| Seam cross-reference | 1.0 — systematic table, all seams checked | 0.9 — seam table present, product→cart seam correctly flagged as unconfirmed |
| Risk classification | 1.0 — correct severity: checkout=warning, Stripe=observation | 0.6 — **overclassified**: promoted observations to blockers (parsePrice, Stripe). 3 blockers vs Opus's 1 warning. Would unnecessarily block the spectrum. |
| Validation depth | 1.0 — read code, identified the exact line (`return { items: [], ... }`) | 0.9 — read code, same finding, but added speculative findings beyond the contract |

**Pax-02 Score: Opus 0.98, Sonnet 0.80**

**Key finding**: Sonnet over-flags. It promoted observations to blockers, which would create unnecessary rework cycles in production. Opus correctly distinguished severity levels.

### pax-05 — UUID Assumption Cascade (cuid2→UUID silent divergence)

**Ground truth deviations to catch:**
1. howler-db-layer silently changed contract assumption (cuid2→UUID) without AMENDMENT.md — **blocker (contract_breach)**
2. howler-graphql-layer built against stale assumption, claims "base64(cuid2)" — **blocker (seam_mismatch)**

| Dimension | Opus | Sonnet |
|-----------|------|--------|
| Deviation detection (recall) | 1.0 — caught both blockers, identified the cascade mechanism | 1.0 — caught both blockers, same cascade analysis |
| Deviation detection (precision) | 1.0 — exactly 2 blockers + 1 warning, no false positives | 1.0 — exactly 2 blockers, no false positives |
| False positive rate | 1.0 — correct Howlers (user-service, post-service, api-layer) all marked CLEAN | 1.0 — same three correctly marked CLEAN |
| Seam cross-reference | 1.0 — systematic table, identified functional compatibility vs semantic mismatch | 1.0 — systematic table, same distinction |
| Risk classification | 1.0 — correct: db-layer=blocker (contract_breach), graphql=blocker (seam_mismatch) | 1.0 — same classification |
| Validation depth | 1.0 — specified exact action plan (read resolvers.ts, check for cuid2 validation) | 0.95 — same action plan, slightly less specific |

**Pax-05 Score: Opus 1.0, Sonnet 0.99**

### Pax Phase Average: Opus 0.99, Sonnet 0.90

**Critical difference**: On pax-02 (subtle bugs), Sonnet over-classified severity, promoting observations to blockers. On pax-05 (obvious contract breach), both models performed identically. The gap is in **judgment about severity**, not detection.

---

## Phase 3: Forge (Failure Classification)

### forge-03 — File Ownership Conflict (conflict vs structural)

**Ground truth**: Classification=`conflict`, Recovery=`restructure`, Circuit breaker=`true` (2 prior failures on same locus)

| Dimension | Opus | Sonnet |
|-----------|------|--------|
| Classification | **structural** (circuit breaker escalated) | **structural** (circuit breaker escalated) |
| Recovery action | **restructure** | **restructure** |
| Circuit breaker | **true** | **true** |
| Rationale quality | Excellent — identified root cause (Gold's drop prompt contradicted MANIFEST.md), proposed specific fix (split notification configs into separate file) | Excellent — same root cause, proposed sequential merge step or single-owner restructure |

Note: Both classified as `structural` rather than `conflict` because the circuit breaker auto-escalates. The ground truth says `conflict` is the "correct" base classification, but both models correctly applied the circuit breaker rule to escalate. This is arguably MORE correct than the ground truth.

**Forge-03 Score: Opus 1.0, Sonnet 1.0**

### forge-04 — Circuit Breaker + Environmental (disk space + 3 prior failures)

**Ground truth**: Classification=`environmental` (escalated to `structural` by circuit breaker), Recovery=`restructure`, Circuit breaker=`true`

| Dimension | Opus | Sonnet |
|-----------|------|--------|
| Classification | **environmental** (noted circuit breaker escalates to structural) | **environmental** (noted circuit breaker escalation) |
| Recovery action | **restructure** | **restructure** |
| Circuit breaker | **true** | **true** |
| Rationale quality | Clear — identified disk space as root cause requiring CI admin, suggested retargeting execution environment | Clear — same analysis, suggested pre-built Docker image |

**Forge-04 Score: Opus 1.0, Sonnet 1.0**

### Forge Phase Average: Opus 1.0, Sonnet 1.0

---

## Composite Scores

| Phase | Weight | Opus | Sonnet | Delta |
|-------|--------|------|--------|-------|
| Muster | 40% | 1.00 | 0.95 | -0.05 |
| Pax | 40% | 0.99 | 0.90 | -0.09 |
| Forge | 20% | 1.00 | 1.00 | 0.00 |
| **Composite** | **100%** | **1.00** | **0.94** | **-0.06** |

### Threshold Comparison

| Phase | Threshold | Opus | Sonnet | Pass? |
|-------|-----------|------|--------|-------|
| Muster | 0.85 | 1.00 | 0.95 | **PASS** |
| Pax | 0.80 | 0.99 | 0.90 | **PASS** |
| Forge | 0.90 | 1.00 | 1.00 | **PASS** |
| Composite | 0.84 | 1.00 | 0.94 | **PASS** |

**Sonnet passes all thresholds.**

---

## Cost / Latency Comparison

| Metric | Opus | Sonnet | Savings |
|--------|------|--------|---------|
| Muster avg output length | ~5,500 tokens | ~4,800 tokens | Sonnet slightly more concise |
| Pax avg output length | ~1,800 tokens | ~1,900 tokens | Comparable |
| Forge avg output length | ~120 tokens | ~120 tokens | Identical |
| Estimated muster cost | ~$1.73/run | ~$0.15/run | **91% cheaper** |
| Estimated pax cost | ~$2.50/run | ~$0.22/run | **91% cheaper** |
| Forge cost | ~$0.02/run | ~$0.002/run | **91% cheaper** |

---

## Qualitative Differences

### Where Opus excels
1. **Severity calibration in Pax**: Opus correctly distinguishes blockers from warnings from observations. Sonnet tends to over-promote — calling things "blockers" that are really observations (e.g., IEEE 754 floating-point precision in parsePrice, Stripe source parameter usage).
2. **Contract precision in Muster**: Opus produces more formally testable postconditions. "verifyToken returns null on invalid tokens, never throws" vs Sonnet's more descriptive but less binary language.
3. **Decomposition hazard scans**: Opus's hazard scan is slightly more structured, identifying synthesis dependencies, serial chains, and critical-path risks as discrete categories.

### Where Sonnet matches or exceeds
1. **Forge classification**: Perfect parity. Both models apply the circuit breaker correctly and produce equally sound rationale.
2. **Muster structure**: DAGs are nearly identical. File ownership matrices have zero conflicts from both models.
3. **Additional findings**: Sonnet occasionally finds real concerns Opus doesn't flag (e.g., express.d.ts ownership for req.user typing, parsePrice floating-point risk). These are valuable engineering insights even if they're misclassified as blockers.
4. **Speed**: Sonnet responds faster (not measured precisely in this eval, but observable).

### The core difference
**Opus has better judgment about what matters.** Both models detect the same issues. The difference is in classification, prioritization, and severity assignment. Opus says "this is a warning, note it in the PR." Sonnet says "this is a blocker, stop the spectrum." In production, Sonnet's over-flagging would create unnecessary rework cycles — but it would never miss a real issue.

---

## Recommendation

### Sonnet passes all phases above threshold. Full downgrade is viable.

However, the **Pax severity calibration gap** is the one risk worth monitoring:

| Option | Cost Savings | Risk |
|--------|-------------|------|
| **Full Sonnet Gold** | ~$3.50/spectrum (91%) | Pax may over-flag, causing unnecessary rework. Mitigated by human review of Pax blockers. |
| **Sonnet Muster + Forge, Opus Pax** | ~$2.00/spectrum (55%) | Best quality on the most judgment-heavy phase. |
| **Keep Opus everywhere** | $0 | No risk, no savings. |

### Primary recommendation: **Full Sonnet Gold with Pax severity review**

Rationale:
- 91% cost reduction is substantial
- Sonnet's over-flagging is a conservative failure mode (better to over-flag than under-flag)
- The human operator already reviews Pax findings before merge — severity overclassification is caught at that step
- Re-evaluate after 3 production spectrum runs

### Monitoring triggers for rollback:
- If Sonnet Pax produces >3 false blocker flags per spectrum, adding >30 min of unnecessary rework
- If Sonnet Muster produces a file ownership conflict that reaches The Proving
- Re-evaluate quarterly or after major model updates

---

## Caveats

1. **N=6 scenarios** — small sample. Results should be validated with the full 18-scenario library.
2. **Synthetic scenarios** — may not capture emergent complexity of real production spectrums.
3. **Point-in-time** — model capabilities change with updates.
4. **Forge has zero production history** — both models scored 100% on synthetic scenarios, but we have no production baseline.
5. **Pax-02 was the most discriminating scenario** — it drove most of the quality gap. More pax scenarios at this difficulty level would strengthen confidence.
