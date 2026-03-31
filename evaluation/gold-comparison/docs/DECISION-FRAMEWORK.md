# Gold Agent Evaluation — Decision Framework

**Version**: 1.0  
**Date**: 2026-03-31  
**How to use**: After filling in FINDINGS-TEMPLATE.md, find the outcome below that matches your per-phase results. Follow the decision tree for implementation steps, monitoring requirements, and rollback triggers.

---

## Decision Tree

```
                        ┌─────────────────────────────┐
                        │  Did Sonnet pass all three   │
                        │  phase thresholds?           │
                        │  (Muster ≥85, Pax ≥80,       │
                        │   Forge ≥90)                 │
                        └──────────┬──────────────────┘
                                   │
               ┌─── YES ───────────┴───────── NO ──────────────────────┐
               ▼                                                         ▼
     ┌──────────────────┐                              ┌────────────────────────────┐
     │  OUTCOME 1       │                              │  Which phases did Sonnet   │
     │  Full Downgrade  │                              │  pass?                     │
     └──────────────────┘                              └──────────┬─────────────────┘
                                                                   │
                       ┌───────────────────────────────────────────┤
                       │                       │                   │
              Muster only                Pax only           Forge only
                       │                       │                   │
                       ▼                       ▼                   ▼
             ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
             │  OUTCOME 2       │  │  OUTCOME 3       │  │  OUTCOME 4       │
             │  Muster Downgrade│  │  Pax Downgrade   │  │  Forge Downgrade │
             └──────────────────┘  └──────────────────┘  └──────────────────┘
                       │
                       │ None of the above
                       ▼
             ┌──────────────────┐
             │  OUTCOME 5       │
             │  Keep Opus       │
             └──────────────────┘

     For any result where a phase score is within 5% of threshold:
     ┌──────────────────────────────┐
     │  OUTCOME 6                   │
     │  Conditional Downgrade       │
     │  (monitoring-gated)          │
     └──────────────────────────────┘
```

---

## Outcome 1: Full Downgrade to Sonnet Gold

**Trigger**: Sonnet meets all three phase thresholds (Muster ≥0.85, Pax ≥0.80, Forge ≥0.90).

**Cost impact**:
- 5-Howler spectrum: ~$3.50 saved per run (Gold phases drop from ~$4.25 to ~$0.75)
- 8-Howler spectrum: ~$5–6 saved per run
- Break-even: This downgrade pays for the evaluation itself after 3–4 spectrum runs

**Implementation**:

1. Update `~/.claude/CLAUDE.md` Model Assignments table:
   ```
   Gold (mayor): sonnet  # was: opus
   ```

2. Update SPECTRUM-OPS.md to remove any Opus-specific Gold conciseness directives (T1-E from TOKEN-OPTIMIZATION.md becomes less critical at Sonnet pricing, though brevity is still good practice).

3. No SPECTRUM-OPS.md structural changes needed — the Gold phases are the same; only the model changes.

**Monitoring (first 3 production spectrums)**:
- After each spectrum, record: were any integration failures discovered post-merge that PAX-PLAN.md did not flag?
- After each spectrum, record: did any Howler encounter a CONTRACT.md ambiguity that a tighter contract would have prevented?
- After each spectrum, record: were any Forge classifications wrong (i.e., a Howler was auto-resumed as `transient` but then failed again)?

**Rollback trigger**: Any of the following in the first 3 production spectrums:
- An integration failure that Pax should have caught and didn't
- A file ownership conflict that Muster should have detected and didn't
- A Forge misclassification that led to wasted recovery cycles (specifically: structural failure classified as transient, then auto-resumed and failed again)

**Rollback procedure**: Revert the CLAUDE.md model assignment. No spectrum artifacts are affected; the change is purely in the model selection.

---

## Outcome 2: Muster-Only Downgrade (Most Likely Split Outcome)

**Trigger**: Sonnet passes Muster (≥0.85) but fails Pax (<0.80).

**Why this is the most likely split**: Muster is the most structured of the three phases. File ownership matrices, DAG edges, and CONTRACT.md sections have clear templates and validation criteria. Pax requires adversarial skepticism about Howler self-reports and the ability to detect "green but wrong" integration issues from limited source file samples — a judgment task that more closely tracks capability differences between Opus and Sonnet.

**Cost impact**:
- 5-Howler spectrum: ~$1.58 saved per run (Muster drops from ~$3.18 to ~$0.55; Pax stays at Opus)
- Note: Gold Muster is the single most expensive Gold phase at ~21% of total run cost

**Implementation**:

1. SPECTRUM-OPS.md needs per-phase model overrides. Add to the Gold Muster drop prompt header:
   ```
   Model: sonnet
   ```
   Retain Opus for Gold Pax and Gold Forge invocations.

2. If CLAUDE.md is used to select the Gold model globally, add a per-phase override mechanism. The simplest approach: document in SPECTRUM-OPS.md that Muster uses Sonnet and Pax/Forge use Opus, and ensure the model is specified in the drop prompt for each phase.

**Monitoring (first 3 production spectrums)**:
- Focus monitoring on muster output quality: were CONTRACT.md postconditions testable? Were all file ownerships correct?
- Pax continues on Opus — no regression risk there
- Watch for Muster latency changes (Sonnet may be faster for Muster's structured output)

**Rollback trigger**:
- A file ownership conflict discovered at merge time (Muster missed it)
- A Howler blocked due to CONTRACT.md ambiguity that a more careful Muster would have prevented
- Politico issues injected in the scenario library that are now being missed in production (if periodic re-evaluation is in place)

---

## Outcome 3: Pax-Only Downgrade (Unlikely)

**Trigger**: Sonnet fails Muster (<0.85) but passes Pax (≥0.80).

**Why this is unlikely**: Muster is more structured than Pax. If Sonnet handles Pax's adversarial validation, it almost certainly handles Muster's template-driven planning. A Pax-only pass suggests something specific about the scenario library calibration rather than a genuine capability inversion. Treat this result as a signal to audit the scenario difficulty before acting on it.

**Audit steps before implementing**:
1. Review Muster scenarios for calibration errors — were scenarios set at a difficulty level that doesn't represent production tasks?
2. Check whether the failure was concentrated in one Muster dimension (e.g., all Politico integration failures) that might be fixable with a prompt adjustment
3. If the failure pattern is explainable by a correctable cause, do not implement a partial downgrade — fix the prompt and re-run

**If the result holds after audit**:
- Keep Opus for Muster (cascade risk too high)
- Downgrade Pax to Sonnet
- Cost impact: ~$1.50 saved per spectrum (Pax drops from ~$1.50 to ~$0.20)

**Implementation**: Same per-phase override approach as Outcome 2, but inverted.

**Monitoring**: Focus on Pax quality — integration failure rate post-merge, seam issues in the merged codebase.

---

## Outcome 4: Forge-Only Downgrade

**Trigger**: Sonnet passes Forge (≥0.90) but fails both Muster and Pax.

**Cost impact**: Smallest savings of any partial downgrade — ~$0.50 per spectrum. Forge is a relatively small share of Gold's token budget.

**When to implement**: Only when budget pressure is acute. The risk/reward ratio is less favorable here than Outcomes 1–3 because the savings are modest and Muster/Pax remain at Opus, which already accounts for the bulk of the cost.

**Implementation**:
- Downgrade Forge invocations to Sonnet
- Keep Opus for Muster and Pax
- Document the per-phase model selection in SPECTRUM-OPS.md

**Monitoring**: Watch for Forge misclassifications in production — particularly the structural-vs-transient confusion, which has the highest recovery cost.

---

## Outcome 5: Keep Opus Gold

**Trigger**: Sonnet fails all three phase thresholds.

**Action**: No changes to model assignments.

**Documentation**: Record the largest capability gaps to guide future re-evaluation.

For each failed phase, note:
- Which dimensions had the largest Sonnet-vs-Opus gap?
- Was the gap concentrated in a specific scenario tier (adversarial, edge-cases) or present across all difficulties?
- Is the pattern consistent with known Sonnet limitations (e.g., consistent underperformance on multi-step reasoning, or isolated to a specific rubric method like human-scored items)?

**Re-evaluation trigger**: Re-run this evaluation after:
- A major Sonnet model update (new training run, not a patch)
- Significant protocol changes that alter what Gold is asked to produce
- At minimum: quarterly

**Is the gap narrowing?** If records exist from a previous evaluation, compare:
- Did Sonnet improve more on Muster, Pax, or Forge between evaluations?
- If the Muster gap is narrowing faster (as the task becomes more template-driven), the next evaluation may yield an Outcome 2 even if Outcome 5 applies today.

---

## Outcome 6: Conditional Downgrade (Marginal Results)

**Trigger**: One or more phases scored within 5% of threshold (e.g., Sonnet Muster = 0.81, threshold = 0.85).

Marginal means the evidence is insufficient to decide confidently in either direction. The right response is conditional deployment with monitoring.

**What "within 5%" means in practice**:
- Muster marginal zone: 0.80–0.84 (threshold 0.85)
- Pax marginal zone: 0.75–0.79 (threshold 0.80)
- Forge marginal zone: 0.85–0.89 (threshold 0.90)

**Decision for marginal phases**:

If the phase is marginal AND no other phase failed outright, proceed with conditional downgrade:

1. Implement the downgrade for the marginal phase
2. Require 3 production validation spectrums before committing
3. Weekly check-in for the first month: review spectrum artifacts for evidence of the specific failure modes that brought the phase score below threshold

If the phase is marginal AND another phase also failed (below marginal zone), apply Outcome 5 or the appropriate partial downgrade for the passing phase(s) only.

**Weekly check-in criteria** (first month after conditional downgrade):
- Review MANIFEST.md from each production spectrum: are file ownership matrices complete and conflict-free?
- Review PAX-PLAN.md from each production spectrum: were integration risks correctly classified?
- Review any Forge decisions: was the failure type correctly identified?
- If 2+ check-ins show no issues → confirm the downgrade as permanent
- If any check-in reveals a production issue → roll back and re-evaluate

**Committing a conditional downgrade**: After 3 clean production spectrums and 1 month of clean check-ins, remove the "conditional" status. Update CLAUDE.md and SPECTRUM-OPS.md with the permanent assignment.

---

## After Any Downgrade: Monitoring Reference

Regardless of which outcome applies, use these signals to detect regression after a downgrade:

### Leading Indicators (catch early)

| Signal | Where to look | What it indicates |
|--------|--------------|------------------|
| Howler blocked on CONTRACT.md ambiguity | Howler HOOK.md, Status: blocked | Muster contract quality degraded |
| Merge conflict at PR time | git merge output, GitHub PR | Muster file ownership matrix missed a conflict |
| Politico finds issues Muster missed | Politico output, Phase 1.5 | Muster Politico integration weakened |
| PAX-PLAN.md recommends merge order that causes integration failure | Gray post-merge output | Pax merge ordering degraded |
| Forge auto-resume followed by second identical failure | CHECKPOINT.json errors array | Forge classified structural as transient |

### Lagging Indicators (catch after the fact)

| Signal | Where to look | What it indicates |
|--------|--------------|------------------|
| Integration test failures post-full-merge | Gray final run (Phase 6) | Pax missed seam issues |
| Obsidian SENTINEL-REPORT flags spec violations | SENTINEL-REPORT.md | Muster decomposition didn't capture all PLAN.md requirements |
| LESSONS.md records recurring seam issue | LESSONS.md after each spectrum | Systematic Pax weakness |

### Rollback Procedure

1. Revert CLAUDE.md model assignment to Opus for the affected phase(s)
2. Revert any SPECTRUM-OPS.md per-phase model overrides
3. Document the regression in LESSONS.md: what the signal was, which production spectrum it appeared in, and what the cost of the failure was
4. Re-run the evaluation with an updated scenario library that captures the failure pattern

### Re-Evaluation Cadence

- **Quarterly**: run the full evaluation against the current model versions
- **After major model update**: re-run within 2 weeks of a new Sonnet or Opus release
- **After protocol changes**: re-run if SPECTRUM-OPS.md Phase 1, 4, or 5 procedures change significantly (these are the phases being evaluated)
- **After a documented regression**: re-run with updated scenarios that capture the failure pattern before re-attempting the downgrade

---

## Reference: Expected Cost Figures by Outcome

All figures reference TOKEN-OPTIMIZATION.md cost analysis (5-Howler full spectrum baseline: ~$9.43 total, Gold phases: ~$4.25).

| Outcome | Phases downgraded | Savings per 5-Howler run | Savings per 8-Howler run |
|---------|------------------|--------------------------|--------------------------|
| 1: Full | Muster + Pax + Forge | ~$3.50 | ~$5.00 |
| 2: Muster only | Muster | ~$1.58 | ~$2.20 |
| 3: Pax only | Pax | ~$1.50 | ~$2.00 |
| 4: Forge only | Forge | ~$0.50 | ~$0.70 |
| 5: None | — | $0 | $0 |
| 6: Conditional | Varies | Varies | Varies |

*Note: Forge savings are estimated; Forge token budget is smaller than Muster or Pax. Figures are approximate and will vary based on actual task complexity and token usage.*
