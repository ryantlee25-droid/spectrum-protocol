# Spectrum Protocol -- Cost Improvements V2: Prioritized Improvement Stack

**Date**: 2026-04-01
**Spectrum**: cost-v2-0401
**Sources**: H1 (public-protocols.md), H2 (platform-opportunities.md), H3 (model-routing.md), H4 (architectural-patterns.md), TOKEN-OPTIMIZATION.md (T1-T3 backlog)
**Baseline**: 5-Howler full run at ~$6.50 (Gold on Sonnet, post-gold-eval-0331)

---

## Executive Summary

This document consolidates cost optimization opportunities from four research tracks (public protocols, platform levers, model routing, architectural patterns) and integrates them with the existing T1-T3 backlog from TOKEN-OPTIMIZATION.md. The result is a unified, prioritized stack of 30+ cost improvements, de-duplicated and ranked by impact-to-effort ratio.

**Key findings:**
- The existing T1 optimizations ($0.80/run) remain the highest-ROI immediate actions
- Three V2 discoveries rival T1 in impact: Batch API ($0.35-1.03), Gray split ($0.70), and deferred quality gates ($0.90 for reaping)
- Combined potential savings if all recommended changes are implemented: **$2.50-4.00 per 5-Howler run (38-62% cost reduction)**
- The most impactful single change post-gold-eval is Gray split (Haiku-run / Sonnet-diagnose): $0.70 savings with zero quality risk on pass cases
- Several V2 findings overlap with T2/T3 backlog items -- these are noted and the higher-fidelity estimate is used

---

## Unified Priority Stack

All items ranked by **impact-to-effort ratio** (savings per unit of implementation effort). Items are tagged with their source: `[T1]` = existing Tier 1, `[T2]` = existing Tier 2, `[T3]` = existing Tier 3, `[V2-H1]` through `[V2-H4]` = new V2 research.

### Priority 1: Implement Now (spec/instruction changes only)

| # | Item | Source | Savings/5H | Effort | Quality Risk |
|---|------|--------|-----------|--------|-------------|
| P1-1 | Create HOWLER-OPS.md | [T1-A] | $0.15 | Low | None |
| P1-2 | Gold conciseness directive | [T1-E] | $0.30 | Low | Low |
| P1-3 | HOOK.md compactness rules | [T1-D] | $0.06 | Low | None |
| P1-4 | Gold self-reflect on Haiku | [T1-B]+[V2-H3] | $0.05 | Low | None |
| P1-5 | Eliminate Gold seam re-derivation | [T1-C] | $0.15 | Low | None |
| P1-6 | /diff-review on Haiku (non-security) | [V2-H3] | $0.14 | Low | Low |
| P1-7 | Artifact size limits | [V2-H4] | $0.05-0.10 | Low | None |
| P1-8 | Read-once instruction for Howlers | [V2-H4] | $0.03-0.05 | Low | None |
| P1-9 | Compressed artifact formats (YAML) | [V2-H1] | $0.10-0.20 | Low | None |
| P1-10 | Cache-friendly prompt ordering | [V2-H1]+[V2-H2] | $0.05-0.10 | Low | None |
| | **P1 Subtotal** | | **$1.08-1.30** | | |

### Priority 2: Implement Soon (minor tooling or template changes)

| # | Item | Source | Savings/5H | Effort | Quality Risk |
|---|------|--------|-----------|--------|-------------|
| P2-1 | **Gray split (Haiku-run / Sonnet-diagnose)** | [V2-H3] | **$0.70** | Medium | None (pass cases) |
| P2-2 | Per-Howler CONTRACT.md slicing | [T2-A] | $0.03 | Low | Low |
| P2-3 | Confidence-tiered Pax validation | [T2-B] | $0.14 | Low | Low |
| P2-4 | Conditional /diff-review by security surface | [T2-C] | $0.05-0.10 | Low | Low-medium |
| P2-5 | Discovery relay token cap enforcement | [T2-D] | negligible | Low | None |
| P2-6 | Pipeline short-circuiting rules | [V2-H4] | $0.20-0.50 | Low | Low |
| P2-7 | Cost-aware Howler count (coordination tax rule) | [V2-H4] | $0.50-1.00 | Low | None |
| P2-8 | Adaptive cost-aware mode selection | [V2-H4] | $0.50-2.00 | Low | Low |
| P2-9 | Proportional quality gate investment | [V2-H3]+[V2-H4] | $0.50-0.75 | Medium | Low-medium |
| P2-10 | White on Haiku (reaping mode only) | [V2-H3] | $0.42 (reaping) | Low | Low |
| P2-11 | Structured JSON debrief summary | [T3-C]+[V2-H4] | $0.15 | Low | None |
| P2-12 | Howler turn count reduction (batch ops) | [V2-H2] | $0.60 | Medium | Low |
| | **P2 Subtotal** | | **$3.79-5.97** | | |

### Priority 3: Consider Later (platform/architectural changes)

| # | Item | Source | Savings/5H | Effort | Quality Risk |
|---|------|--------|-----------|--------|-------------|
| P3-1 | **Batch API for quality gates + Copper** | [V2-H2] | **$0.35-1.03** | High | None (async ok) |
| P3-2 | **Deferred quality gates (reaping/nano)** | [V2-H4] | **$0.90** | Medium | Low (reaping only) |
| P3-3 | Stateless Gold phase transitions | [V2-H1]+[V2-H4] | $0.10-0.20 | Medium | Low |
| P3-4 | LLM avoidance for mechanical dispatch | [T3-A] | $0.40-0.75 | High | Medium |
| P3-5 | Per-agent CLAUDE.md sections | [T3-B]+[V2-H1] | $0.38 | High | Low |
| P3-6 | Prompt caching optimization (API-level) | [V2-H1]+[V2-H2] | $0.30-0.50 | Medium | None |
| P3-7 | Progressive context loading | [V2-H1] | $0.20-0.40 | High | Low |
| P3-8 | Output budget enforcement (max_tokens) | [V2-H4] | $0.10-0.20 | Low | Low |
| P3-9 | Complexity-based dynamic model routing | [V2-H3] | $0.80-1.00 | High | Medium |
| P3-10 | Extended thinking budget control | [V2-H2] | $0.15 | Low | Low |
| P3-11 | Early termination on quality signals | [V2-H1] | $0.10-0.30 | High | Medium |
| P3-12 | Cross-session task-level cache | [V2-H1] | $0.05-0.15 | High | Low |
| | **P3 Subtotal** | | **$3.83-6.61** | | |

---

## Implementation Roadmap

### Phase A: Immediate (next spectrum run)

**Targets**: P1-1 through P1-10 (all spec/instruction changes)

**Combined savings**: $1.08-1.30 per 5-Howler run (17-20% reduction)

**Actions**:
1. Create `HOWLER-OPS.md` with Howler-relevant subset of SPECTRUM-OPS.md (P1-1)
2. Add Gold conciseness directive to SPECTRUM-OPS.md muster/pax sections (P1-2)
3. Add HOOK.md compactness rules to Howler drop template (P1-3)
4. Change Gold self-reflect model assignment to Haiku (P1-4)
5. Clarify in Phase 4 that Gold uses SEAM-CHECK.md, not manual re-derivation (P1-5)
6. Add `/diff-review` model routing: Haiku for non-security, Sonnet for security (P1-6)
7. Add artifact size targets to SPECTRUM-OPS.md templates (P1-7)
8. Add "read-once" instruction to Howler drop template (P1-8)
9. Convert HOOK.md status sections and MANIFEST.md DAG to YAML format (P1-9)
10. Document cache-friendly prompt ordering convention (P1-10)

### Phase B: Near-term (1-2 weeks)

**Targets**: P2-1, P2-6 through P2-12 (highest-impact P2 items)

**Combined savings**: Additional $1.50-3.00 per 5-Howler run

**Key actions**:
1. Implement Gray split: create Gray-run (Haiku) and Gray-diagnose (Sonnet) agent roles (P2-1)
2. Add coordination tax formula to Gold muster decision rules (P2-7)
3. Add cost-aware mode selection thresholds (P2-8)
4. Define proportional quality gate profiles (P2-9)
5. Update reaping mode to use White on Haiku (P2-10)
6. Refactor Howler drop prompts to encourage batch operations (P2-12)

### Phase C: Medium-term (1-2 months)

**Targets**: P3-1, P3-2, P3-6 (highest-impact P3 items)

**Combined savings**: Additional $1.55-2.43 per 5-Howler run

**Key actions**:
1. Build Batch API submission pipeline for quality gates (P3-1)
2. Implement deferred quality gate mode for reaping/nano (P3-2)
3. Design and test cache-friendly prompt structures for API-level caching (P3-6)

---

## Cumulative Savings Projection

| Phase | Cumulative Savings/5H | Cumulative % Reduction | Estimated Run Cost |
|-------|----------------------|------------------------|-------------------|
| Baseline (current) | $0 | 0% | $6.50 |
| Phase A (immediate) | $1.08-1.30 | 17-20% | $5.20-5.42 |
| Phase B (near-term) | $2.58-4.30 | 40-66% | $2.20-3.92 |
| Phase C (medium-term) | $4.13-6.73 | 64-103%* | $0-2.37 |

*Phase C upper bound exceeds 100% due to overlapping savings that are not fully additive. Realistic combined maximum is ~70% reduction ($1.95/run).

**Realistic combined target**: $4.00 savings per 5-Howler run = **$2.50/run (62% reduction from $6.50)**.

---

## Cross-Reference: V2 Findings vs. Existing Backlog

Several V2 findings reinforce or extend existing T1-T3 items:

| V2 Finding | Existing Item | Relationship |
|-----------|---------------|-------------|
| Prompt caching (H1, H2) | T3-B (per-agent CLAUDE.md) | Different mechanisms, same goal |
| /diff-review on Haiku (H3) | T2-C (conditional /diff-review) | Complementary: T2-C skips, H3 downgrades |
| Gold self-reflect on Haiku (H3) | T1-B (downgrade to Sonnet) | H3 extends T1-B further to Haiku |
| Structured debrief JSON (H4) | T3-C (Pax debrief compression) | H4 is the implementation mechanism for T3-C |
| Stateless Gold phases (H1, H4) | T3-A (LLM avoidance) | Overlapping: both reduce Gold context accumulation |
| Proportional quality gates (H3, H4) | T2-C (conditional /diff-review) | H3/H4 generalize T2-C to all quality gates |

---

## Top 10 Changes by Impact-to-Effort Ratio

The "best buys" -- changes that deliver the most savings per unit of implementation work:

| Rank | Item | Savings | Effort | Ratio |
|------|------|---------|--------|-------|
| 1 | P2-7: Coordination tax decision rule | $0.50-1.00 | Low | Very High |
| 2 | P2-8: Cost-aware mode selection | $0.50-2.00 | Low | Very High |
| 3 | P1-2: Gold conciseness directive | $0.30 | Low | High |
| 4 | P2-1: Gray split (Haiku-run/Sonnet-diagnose) | $0.70 | Medium | High |
| 5 | P1-1: HOWLER-OPS.md | $0.15 | Low | High |
| 6 | P1-5: Eliminate seam re-derivation | $0.15 | Low | High |
| 7 | P1-6: /diff-review on Haiku | $0.14 | Low | High |
| 8 | P3-2: Deferred quality gates (reaping) | $0.90 | Medium | High |
| 9 | P2-12: Howler turn count reduction | $0.60 | Medium | Medium-High |
| 10 | P3-6: Prompt caching optimization | $0.30-0.50 | Medium | Medium-High |

---

## Risk Assessment

### Changes with Zero Quality Risk
- P1-1 (HOWLER-OPS.md): Howlers never needed muster/pax instructions
- P1-3 (HOOK.md compactness): Gold needs signals, not raw output
- P1-4 (self-reflect on Haiku): Structured journaling, not reasoning
- P1-5 (seam re-derivation): seam_check.py is mechanically correct
- P1-7, P1-8 (artifact limits, read-once): Discipline improvements
- P2-1 Gray-run on Haiku: Mechanical test execution
- P2-7 (coordination tax rule): Prevents unnecessary Howlers

### Changes Requiring Validation
- P1-6 (/diff-review on Haiku): Validate Haiku catches security patterns in checklist-driven review
- P2-9 (proportional gates): Validate that reduced gates catch the same issues as full gates on a sample spectrum
- P3-9 (dynamic model routing): Requires empirical testing across task types

### Changes to Monitor After Implementation
- P2-8 (aggressive mode selection): Watch for under-specifying full-mode spectrums
- P3-2 (deferred gates): Watch for late-caught integration issues in reaping mode
- P3-7 (progressive context loading): Requires Claude Code platform support

---

## Comparison: Cost Position After Optimization

| System | Cost Score (Rubric) | Notes |
|--------|-------------------|-------|
| **Spectrum (current)** | **2/5** | Per COMPETITIVE-AUDIT.md |
| **Spectrum (Phase A)** | **2/5** | 17-20% savings, still above median |
| **Spectrum (Phase A+B)** | **3/5** | 40-66% savings, reaches competitive median |
| **Spectrum (Full optimization)** | **3-4/5** | 62% savings, competitive with CrewAI, LangGraph |
| CrewAI | 4/5 | Lower per-agent overhead, simpler coordination |
| LangGraph | 4/5 | No multi-agent ceremony overhead |
| Citadel | 3/5 | Plugin-based, lower muster cost |

**Key insight**: Full implementation of Phase A+B improvements would move Spectrum from D1=2 (below median, a weakness) to D1=3 (competitive median). Phase C could reach D1=4 but requires platform support. The 2-point improvement in D1 would raise Spectrum's total competitive score from 25 to 26-27, matching Citadel and approaching Gas Town/LangGraph.
