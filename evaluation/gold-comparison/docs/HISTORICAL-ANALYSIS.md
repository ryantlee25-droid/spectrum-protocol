# Historical Analysis: Opus Gold Production Track Record

_Prepared for: gold-eval-0331 spectrum run_
_Source data: 5 LESSONS.md files from ~/.claude/projects/-Users-ryan/memory/_
_Rubric reference: rubrics/muster-rubric.yaml, rubrics/pax-rubric.yaml, rubrics/forge-rubric.yaml_

---

## Overview

This document extracts retrospective quality signal from five documented production spectrum runs executed under Opus Gold (hereafter "Gold"). The goal is to establish a factual baseline — what did Gold actually produce, where did it add real value, and which rubric dimensions have sufficient historical data to score retroactively — before comparing against Sonnet Gold in the synthetic benchmark.

**Runs covered:**

| Run ID | Date | Scale | Mode | Domain |
|--------|------|-------|------|--------|
| convoy-v3-0328 | 2026-03-28 | 6 Riders | Full | Protocol doc upgrade |
| remnant-infra-0329 | 2026-03-29 | 4 Riders | Full | Infrastructure hardening |
| remnant-narrative-0329 | 2026-03-29 | 8 Riders, 3 batches | Full | Narrative overhaul |
| remnant-ux-0329 | 2026-03-29 | 8 Riders, 2 batches | Full | UX & gameplay overhaul |
| convoy-eval-0330 | 2026-03-30 | 4 Riders | Reaping (doc-only) | Competitive evaluation |

---

## Section 1: Per-Run Analysis

### Run 1: convoy-v3-0328 — Protocol Upgrade (6 Riders)

**What Gold decomposed and whether it was correct.**
Gold decomposed a single-file upgrade problem (CONVOY.md, 10 improvements) into four parallel fragment writers plus a dedicated Stitcher Rider and a supporting-files Rider. The key decomposition insight was applying the fragment+stitch pattern to eliminate the file overlap problem: all 10 improvements touched the same file, so serial execution or naive parallelism would have produced conflicts. Gold's solution — splitting into per-phase fragment files, then a separate Stitcher to assemble — achieved 6 Riders with zero file conflicts. This was structurally sound.

**Pax observations.**
No Pax failures are recorded in the LESSONS file for this run. The clean outcome (no Rider failures, zero conflicts) meant Pax validation was low-drama. The two issues that did surface — YAML field ordering inconsistency between fragment files, and the Amendment taxonomy missing from CLAUDE.md — both appear in the lessons as post-hoc observations rather than as things caught by Gold in Pax. This is a gap: minor contract specification weaknesses (field ordering not specified) propagated through to the stitcher rather than being caught pre-merge.

**Forge decisions.**
No Rider failures occurred. No Forge decisions were required. This is expected for a documentation-only convoy with no compilation or test dependencies.

**What made this run easy or hard for Gold specifically.**
Easy: all Riders created new fragment files (no MODIFIES), so the file ownership matrix was straightforward. The domain (protocol documentation) required no TypeScript type reasoning or integration seam analysis. Hard: the decomposition pattern itself was non-obvious — recognizing that the stitcher creates an inherent serial bottleneck and sizing the critical path correctly required architectural judgment.

**Rubric dimensions stressed.**
- `muster_file_ownership_completeness`: Low stress — pure-create fragments are the simplest possible ownership matrix.
- `muster_decomposition_soundness`: Moderate stress — the stitcher dependency chain required correct DAG labeling (stitcher must wait for all fragments; `serial_risk: yes`). The LESSONS confirm this was handled correctly.
- `muster_dag_edge_accuracy`: Moderate stress — 4 parallel writers → 1 stitcher is a fan-in dependency that needed correct representation.
- `muster_contract_completeness`: Low-moderate stress — naming conventions and YAML field ordering were specified, but incompletely (field order not canonicalized).
- `pax_deviation_detection_rate`: Not significantly stressed — no injected deviations materialized as Rider failures.
- `forge_*`: Not exercised.

---

### Run 2: remnant-infra-0329 — Infrastructure Hardening (4 Riders)

**What Gold decomposed and whether it was correct.**
Gold decomposed infrastructure hardening into 4 parallel Riders with distinct domains (Supabase client, CI configuration, middleware hardening, and related work). The LESSONS report zero file overlap conflicts, which confirms the ownership matrix was correct. However, the run exposed two worktree setup errors that originated in Gold's pre-drop verification: Rider C's worktree was created from `main` (31 commits behind `staging` instead of `staging`), and Rider A's worktree auto-generated a branch name instead of using the naming convention. These are Gold operational failures in Phase 2 post-drop verification.

**File conflicts: reported 0, verified.** The LESSONS state "4 parallel Riders with zero file overlap worked cleanly" except for Rider A's Supabase conflict — which was caused by the wrong base branch on the worktree, not by a file ownership matrix error. Gold's ownership matrix was correct; the execution environment deviated from what the manifest specified.

**Pax observations.**
The LESSONS record that the Inspector (White) caught 3 real blockers: RLS without policies (documentation gap), pnpm version unpinned in CI, and non-null assertions in middleware. Cross-rider seam check caught a valid concern: Rider A removed an admin client import but the mock layer was different between branches, requiring manual synthesis. These are legitimate integration issues that a Pax validation pass should surface. However, there is no explicit record of Gold running a structured Pax validation pass after the Riders completed — the Inspector is White (a Howler-level quality gate), not Gold's Pax analysis. The gap between Inspector findings and Gold's Pax synthesis is not documented for this run.

**Forge decisions.**
No Rider failures are recorded. The Supabase conflict required manual merge resolution by the operator, but this was classified as an environmental/worktree issue, not a Howler logical failure. No formal Forge decisions were taken.

**What made this run easy or hard for Gold specifically.**
Hard: Gold failed to verify the base branch for two worktrees, allowing stale code to contaminate Rider C's output. The worktree issue with `app/layout.tsx` (metadata overwritten with `main` defaults) was a real content regression that required manual repair. Easy: the 4-domain decomposition was clean and the domain boundaries were well-defined (infrastructure subdomains don't overlap).

**Rubric dimensions stressed.**
- `muster_file_ownership_completeness`: Low stress — 4 clean domains, straightforward matrix.
- `muster_decomposition_soundness`: Low stress — parallel infrastructure work with no serial dependencies.
- `pax_deviation_detection_rate`: Moderate stress — the mock layer mismatch and stale base branch consequences were real deviations that Gold should have caught in Pax.
- `pax_false_positive_rate`: Not documented.
- `forge_*`: Not exercised.
- **Unlabeled dimension (Gold operational)**: Post-drop worktree verification — Gold failed this on 2 of 4 Riders. This maps to `muster_file_ownership_completeness` only indirectly; it is better captured as an execution quality dimension not currently in the rubric.

---

### Run 3: remnant-narrative-0329 — Narrative Overhaul (8 Riders, 3 Batches)

**What Gold decomposed and whether it was correct.**
Gold decomposed a 7-pillar narrative system into 8 Riders (A-H) across 3 batches, with Rider H serving as the integration Rider in the final batch. Batch 1 (6 Riders, all pure-create) produced zero merge conflicts. The integration approach — Rider H creates stubs for all 7 systems, real implementations replace stubs during merge — was structurally sound and was borrowed from prior spectrum experience.

**File conflicts: reported 0 for Batch 1; complications in final merge.** The LESSONS record that Rider H's stubs conflicted with real implementations during final merge (7 conflicts requiring manual resolution), and that both Rider D and Rider H added exports to echoes.ts, producing duplicate function declarations post-merge. These are Gold decomposition errors: the echoes.ts dual modification is a direct file ownership matrix failure (two Riders modifying the same file without sequencing).

**Pax observations.**
Inspector caught 10 real blockers: pipeline ordering (actionsTaken increment), auth error removal, save retry removal, module-level mutable state, pool exhaustion, and smart quotes in generated content. The LESSONS describe these as "would have been production bugs" — quality gates were worth their cost. However, as with infra, the Inspector (White) is not the same as Gold's Pax. The depth of Gold's independent Pax validation pass is not explicitly documented. What is documented: the stub-conflict integration risk was a known consequence of the architecture, not something Gold independently surfaced.

**Forge decisions.**
Approximately 50% of Riders failed to run git commands in worktrees (git permission issues), requiring manual commits by the operator. The LESSONS classify this as an environmental failure type — the `isolation: worktree` setting creates worktrees but Riders often lack Bash permissions. No formal Forge classification/recovery is documented. The ad hoc resolution (operator commits manually) is consistent with the Forge "environmental" classification, but there is no documented Gold decision on whether to Resume, Retry, or treat as a worktree operational issue.

**What made this run easy or hard for Gold specifically.**
Hard: largest scale tested (8 Riders), required cross-batch dependency management, and the integration Rider (H) created seam complexity. The echoes.ts ownership gap indicates Gold's ownership matrix missed a dual-modification scenario. The worktree permission failures added environmental noise. Easy: narrative content in separate data files (additive, no modification of existing data) kept most of the ownership matrix clean.

**Rubric dimensions stressed.**
- `muster_file_ownership_completeness`: Stressed and partially failed — echoes.ts was claimed by both Rider D and Rider H without sequencing.
- `muster_file_ownership_conflict_detection`: Stressed and failed — Gold did not detect or resolve the echoes.ts dual-modification before drop.
- `muster_decomposition_soundness`: Moderately stressed — integration Rider pattern requires correct serial labeling of H's dependency on A-G.
- `muster_dag_edge_accuracy`: Stressed — 3-batch DAG with fan-in to integration Rider.
- `pax_deviation_detection_rate`: Stressed — 10 Inspector blockers and stub conflicts; unclear how much Gold independently caught vs Inspector.
- `forge_classification_accuracy`: Not formally exercised — worktree failures handled ad hoc rather than via the Forge protocol.
- `forge_escalation_appropriateness`: Not formally exercised.

---

### Run 4: remnant-ux-0329 — UX & Gameplay Overhaul (8 Riders, 2 Batches)

**What Gold decomposed and whether it was correct.**
Gold decomposed a UX overhaul into 8 Riders with Rider A (color palette) as a deliberate solo first batch, then Riders B-H in parallel. The color-first sequencing decision was correct: all other Riders inherited the new palette and zero color conflicts occurred. Three potential file ownership conflicts (movement.ts, trade.ts, PipBoyFrame.tsx) were resolved by function-level ownership splits — itemsLine vs exitsLine, wares display vs buy/sell behavior, colors vs tabs vs spacing. All merged without conflicts.

**File conflicts: 0.** This is the cleanest large-scale run in the dataset. The ownership matrix was correctly constructed and the function-level splits were precise enough to avoid any conflict.

**Pax observations.**
The LESSONS record zero post-merge conflicts and 433 tests passing. No Pax blockers are explicitly documented — the quality gate outcome was clean. Cross-rider coordination artifacts (contract boundary comments left by Rider D in trade.ts) were documented as a reusable pattern. One operational issue: leftover worktrees caused Vitest to discover duplicate test files (8 copies of trade.test.ts), which would have polluted test results. Worktree cleanup before tests is now a documented protocol requirement.

**Forge decisions.**
Same worktree git permission failures as the narrative run (~50% of Riders). The LESSONS recommend pre-creating branches before dispatching Riders so they just write files. No formal Forge decisions documented — operator manual commits again.

**What made this run easy or hard for Gold specifically.**
Easy: the color-first sequencing insight was correct and Gold applied it as a deliberate architectural decision. The function-level ownership splits were more fine-grained than previous runs and worked cleanly. Hard: the UX domain required accurate prediction of which files would be multi-Rider contention points (PipBoyFrame.tsx is a three-way ownership magnet). Gold correctly identified and split all three. The quest-audit scope was labeled as optimistic post-hoc — Rider E (quest-audit) ran longest, and the LESSONS suggest it should have been flagged as a single-rider task with a larger time budget (serial risk). This is a `muster_decomposition_soundness` failure: the task was not labeled `serial_risk: yes` despite being inherently serial.

**Rubric dimensions stressed.**
- `muster_file_ownership_completeness`: Stressed and passed — three multi-Rider files correctly split.
- `muster_file_ownership_conflict_detection`: Not stressed (no injected conflicts; Gold's splits preempted them).
- `muster_decomposition_soundness`: Partially failed — quest audit not labeled as serial risk.
- `muster_dag_edge_accuracy`: Moderate stress — 2-batch DAG with A as prerequisite; correctly represented.
- `pax_deviation_detection_rate`: Low stress — clean outcome, no major deviations to detect.
- `forge_*`: Not formally exercised.

---

### Run 5: convoy-eval-0330 — Competitive Evaluation (4 Riders, Reaping)

**What Gold decomposed and whether it was correct.**
Gold decomposed a competitive analysis of the Convoy protocol against 30+ systems into 4 doc-only Riders under reaping mode. The LESSONS report "clean execution" with a score of 82/120 on 12 evaluation dimensions. File conflicts: none (reaping mode, pure-create). The reaping mode activation was appropriate — 4 Riders, all creating new files, no shared interfaces.

**Pax observations.**
Reaping mode skips full Pax (by design). No integration risks were documented. The key findings — spec drift across three files (CLAUDE.md, CONVOY-OPS.md, CONVOY.md) with differing phase numbering and dispatch templates — were surfaced by the evaluation itself, not by a Gold Pax pass. These are pre-existing debt items, not run-time integration failures.

**Forge decisions.**
No Rider failures. No Forge decisions.

**What made this run easy or hard for Gold specifically.**
Easy: doc-only, reaping mode, no compilation, no runtime failures, no shared types. Gold's cognitive load in this run was minimal — light manifest, simplified contract, no DAG. The hardest part was the muster decision itself: recognizing that reaping mode was appropriate (overhead would exceed work time) rather than applying full ceremony unnecessarily.

**Rubric dimensions stressed.**
- `muster_file_ownership_completeness`: Not stressed (reaping mode, light manifest).
- `muster_decomposition_soundness`: Low stress — 4 independent pure-create tasks.
- `muster_politico_integration`: Not exercised (reaping mode skips Politico).
- `pax_*`: Not exercised (reaping mode skips Pax).
- `forge_*`: Not exercised.
- **Reaping mode judgment**: Correctly applied. Overhead was estimated at ~8 min for full ceremony vs ~3 min for reaping — consistent with recorded timing across all runs.

---

## Section 2: Cross-Run Pattern Analysis

**Three distinguishing task characteristics that predict Gold cognitive load:**

### Characteristic 1: Pure-create vs. modify-heavy ownership matrix
Pure-create runs (convoy-v3-0328, convoy-eval-0330, narrative Batch 1) had zero file conflicts in every case. Modify-heavy runs (infra, ux, narrative integration) introduced contention points requiring function-level splits, careful sequencing, and worktree verification. The correlation is strong enough to treat pure-create spectrum as a distinct category: Gold's Muster effort is low, Pax is minimal, and Forge is unlikely. The synthetic benchmark must weight modify-heavy scenarios more heavily if it wants to stress Gold.

### Characteristic 2: Scale x integration depth (Rider count times shared-interface count)
Runs with 8 Riders and an integration Rider (narrative, UX) show qualitatively more Gold cognitive work than 4-Rider or 6-Rider runs. The narrative run's echoes.ts dual-modification failure occurred at the boundary between a creative-content Rider and the integration Rider — a seam that is easy to miss in a large manifest. The UX run's clean outcome required Gold to correctly split three multi-Rider files. The pattern: above 6 Riders, the probability of a missed seam or an under-specified ownership split increases. Pax validation depth matters more at scale.

### Characteristic 3: Serial risk labeling correctness
Two runs recorded post-hoc "should have been serial" observations that were not labeled as such in the manifest: the stitcher in convoy-v3-0328 (labeled correctly — this is the positive case) and the quest-audit task in remnant-ux-0329 (not labeled, ran overtime as a result). The infra run's worktree issues, while environmental, also created an unintended serialization where the operator had to commit for ~50% of Riders. When a task requires reading the complete output of many other tasks (stitcher, quest-audit, integration Rider) before synthesizing, it is inherently serial and must be labeled. Gold correctly identified this in convoy-v3-0328 but missed it for quest-audit. This is a `muster_decomposition_soundness` signal.

### Characteristic 4 (additional): Doc-only vs. code runs and the Forge gap
All five production runs had zero formal Forge decisions. Every run that encountered failures handled them ad hoc (operator manual commits, manual merge resolution) rather than through the Forge protocol taxonomy. This creates a significant gap: we have no historical data on Gold's failure classification accuracy, recovery action selection, or circuit breaker application. The synthetic Forge benchmark has no historical baseline to calibrate against.

---

## Section 3: "Gold Adds Value" Moments

The following are specific moments where Gold's judgment prevented an integration failure. These are the cases Sonnet must replicate to justify a downgrade.

### Moment 1: Fragment+stitch pattern selection (convoy-v3-0328)

**Situation:** 10 improvements needed across a single file (CONVOY.md). Naive decomposition would have had 4-6 Riders each modifying the same file — a direct file ownership violation that would produce merge conflicts and lost work.

**What Gold did:** Recognized the single-file-many-writers problem and invented (or applied from prior knowledge) the fragment+stitch pattern: each Rider writes to its own isolated fragment file, and a dedicated Stitcher Rider assembles all fragments into the final output. This gave 6 Riders zero conflicts.

**What would have happened without it:** Either a sequential run (losing the parallelism benefit entirely) or merge conflicts across 4-6 CONVOY.md forks, requiring manual resolution of 10 interleaved improvements in a 1,500+ line document. Given the structural complexity of the document (YAML DAG, phase sections, rule lists), manual resolution would have had a high error rate.

**Rubric dimension:** `muster_decomposition_soundness` — correctly identifying the single-file synthesis problem and applying the stitch pattern is a decomposition judgment call, not a mechanical rule. The benchmark scenario library should include a case where the naive decomposition produces a conflict; a score of 1.0 requires the model to recognize the pattern and apply fragment+stitch or an equivalent.

### Moment 2: Color-first sequencing as a deliberate dependency (remnant-ux-0329)

**Situation:** UX overhaul with 8 Riders, all touching UI components. Color palette changes (Rider A) would propagate to every other Rider's visual output. If Rider A ran in parallel with B-H, the color variables would be missing or inconsistent during parallel development, causing every other Rider to embed either old colors or hardcoded hex values.

**What Gold did:** Identified the palette as a foundational dependency and decomposed into two batches: Rider A first (solo, completes before B-H), then B-H parallel. This is a non-obvious serial dependency — the "file ownership" interpretation would say A and B-H modify different files, so there's no conflict. The actual dependency is semantic: B-H need the new CSS variables to exist before they write their component code. Gold recognized the semantic dependency, not just the file-level one.

**What would have happened without it:** Multiple Riders would have written components using either hardcoded colors or references to variables that didn't exist yet. Post-merge, visual inconsistencies would have been scattered across all 7 components, requiring a follow-up pass to standardize. The LESSONS note: "No color conflicts, no visual inconsistencies. When doing visual overhauls, always merge the palette/theme first."

**Rubric dimension:** `muster_dag_edge_accuracy` — the A→B-H dependency was a correct edge that required semantic understanding of the domain, not structural analysis of file ownership. A model that only reasons about file conflicts would have dropped A in parallel with B-H and produced the DAG incorrectly.

### Moment 3: Function-level ownership splits for three-way contention files (remnant-ux-0329)

**Situation:** Three files (movement.ts, trade.ts, PipBoyFrame.tsx) were needed by multiple Riders. Movement.ts needed both exit-display changes (navigation Rider) and item-line changes (item-stacking Rider). Trade.ts needed both vendor wares display (vendor Rider) and buy/sell behavior changes (trade Rider). PipBoyFrame.tsx needed color updates, tab-list changes, and spacing changes from three different Riders.

**What Gold did:** Split each file's ownership by function scope — itemsLine vs exitsLine for movement.ts, wares display vs buy/sell for trade.ts, and colors vs tabs vs spacing for PipBoyFrame.tsx. Each split produced clean ownership with no overlap. The result: all 8 Riders merged without conflicts, even across these three high-contention files.

**What would have happened without it:** Any of the three unsplit files would have generated merge conflicts with 2-3 competing modifications. PipBoyFrame.tsx with three concurrent modifiers would have been the most complex — a three-way conflict in a UI component with interleaved style, layout, and logic changes. Even with careful manual resolution, the risk of silent regressions (one Rider's changes dropped or overwritten) would be high.

**Rubric dimension:** `muster_file_ownership_conflict_detection` and `muster_file_ownership_completeness` — Gold detected potential conflicts before they occurred and resolved them through decomposition rather than flagging them as blockers. This is the proactive form of conflict detection: seeing that two Riders' scopes would overlap if naively assigned and preemptively splitting ownership. A Sonnet replacement must demonstrate the same capability, not just flag conflicts reactively.

### Moment 4 (additional): PLAN.md staleness detection (remnant-infra-0329)

**Situation:** Before the infrastructure run, a 4-agent review reported W-1/W-2/W-3 wiring gaps as open. If these had been included in the convoy scope, Riders would have spent time implementing already-completed work.

**What Gold did (or should have done, per the LESSONS lesson):** The LESSONS record this as a failure case where Gold did not verify the review findings against actual source. However, the observation itself — "review data can be stale, always verify against actual code before scoping convoy work" — became an explicit protocol addition (PLAN.md validation, Muster step 4). The lesson is that Gold needs to sample actual source files before trusting any input plan.

**What would have happened without it:** Riders assigned to "implement W-1/W-2/W-3" would have discovered the implementations already existed, producing either no-op PRs or (worse) reimplementations that overwrote the existing correct code.

**Rubric dimension:** `muster_file_ownership_completeness` is upstream of this — Gold must validate that claimed gaps are real before building a manifest that includes them. The synthetic benchmark should include scenarios where the PLAN.md claims a gap that has already been filled.

---

## Section 4: Gap Analysis

### Rubric dimensions with insufficient historical data

**`forge_classification_accuracy` (weight: 0.35 of Forge phase, 0.07 composite):**
Zero documented production Forge decisions across all 5 runs. The worktree permission failures in narrative and UX were handled ad hoc. There is no historical baseline for how Gold classifies `transient` vs `logical` vs `environmental` failures. The synthetic Forge benchmark has nothing to calibrate against.

**`forge_recovery_action_correctness` (weight: 0.30 of Forge phase, 0.06 composite):**
Same gap — no historical Resume/Retry/Skip/Restructure decisions documented. We cannot estimate Sonnet vs Opus performance on this dimension from production data.

**`forge_circuit_breaker_application` (weight: 0.20 of Forge phase, 0.04 composite):**
No multi-failure scenarios occurred across any run. The circuit breaker (2 failures on same locus = escalate) was never triggered. This dimension is entirely synthetic with no historical grounding.

**`forge_escalation_appropriateness` (weight: 0.15 of Forge phase, 0.03 composite):**
The environmental failures (worktree git permissions) were the closest analog to non-transient failures, but they were handled by the operator without a formal Gold escalation decision. No data.

**`pax_false_positive_rate` (weight: 0.20 of Pax phase, 0.08 composite):**
No run documents Gold incorrectly flagging a correct Howler. The absence of documented false positives could mean Gold had zero false positives, or it could mean the historical record doesn't distinguish Gold's Pax output from Inspector (White) findings. The runs don't clearly separate Gold's independent validation from the quality gate results.

**`muster_contract_precision` — postcondition testability (weight: 0.12 of Muster phase, 0.048 composite):**
The LESSONS documents don't quote CONTRACT.md postconditions verbatim. We know contracts existed and were followed (fragment naming conventions, YAML field naming), but we cannot retroactively score whether the postconditions were TESTABLE vs VAGUE.

**`muster_politico_integration` (weight: 0.11 of Muster phase, 0.044 composite):**
Politico (Phase 1.5) is specced but has zero documented production uses (confirmed in convoy-eval-0330 LESSONS: "AMENDMENT.md, ENTITIES.md, seam_check.py, and Designer (Phase 0.5) are all specced but have zero documented production uses"). The adversarial review step was added to the spec as a recommended improvement, not as something Gold demonstrably executed in any of the 5 runs.

### Scenario types absent from history that the synthetic library must cover

1. **Forge scenarios (all subtypes):** The synthetic library needs full coverage of all 5 failure types with documented ground truth. There is no historical analog to calibrate against — the synthetic scenarios are the only source of Forge data.

2. **Politico catch-rate scenarios:** No production run exercised Politico. Scenarios must inject deliberate CONTRACT.md weaknesses (file ownership gaps, underspecified interfaces, incorrect parallelism) and measure whether Gold's Politico step catches them.

3. **PLAN.md staleness scenarios:** One run (infra) surfaced this as a lesson but Gold failed to apply it in-run. A scenario where the input PLAN.md contains stale claims (gaps that are already implemented, features that no longer exist) would test `muster_file_ownership_completeness` under realistic conditions.

4. **High-confidence subtly-wrong Howler scenarios (Pax):** The `pax_deviation_detection_rate` rubric double-weights deviations from Howlers that self-report high confidence. No production run has a documented case of Gold independently verifying a self-confident but wrong Howler. This is the highest-value Pax scenario type.

5. **Cross-batch dependency management at scale (8+ Riders):** The narrative run had the closest analog, but the echoes.ts dual-modification failure was not caught pre-drop. A scenario with deliberate cross-batch dependency injections would test whether Gold can hold the full dependency graph in working context across multiple drop batches.

6. **Environmental failure + Forge decision tree:** Scenarios simulating the worktree permission failure pattern — Rider writes files but cannot commit — should exercise the `forge_classification_accuracy` (environmental) and `forge_escalation_appropriateness` (non-transient = requires human confirmation) dimensions.

---

## Section 5: Baseline Quality Summary

### Track record across 5 runs

| Dimension | Production Evidence | Assessment |
|-----------|--------------------|-----------| 
| File ownership matrix — no conflicts (pure-create) | 5/5 runs, 0 conflicts in pure-create batches | Strong |
| File ownership matrix — modify-heavy | 1 miss (echoes.ts, narrative), 3 correct splits (UX) | Moderate |
| DAG edge accuracy | Stitcher dep correct; color-first correct; quest-audit serial missed once | Moderate |
| Contract completeness | Field ordering gap (v3); no field canonicalization | Moderate |
| Politico integration | Zero documented uses | No data |
| Pax deviation detection | 10 Inspector blockers (narrative), but Gold/White separation unclear | Insufficient |
| Forge decisions | Zero formal Forge decisions across all 5 runs | No data |
| Post-drop worktree verification | 2 failures in infra (wrong base branch for 2 Riders) | Weak |
| Mode selection (reaping vs full) | Correctly applied reaping for eval-0330 | Strong |

**Success rate:** All 5 runs completed and merged. Zero spectrum runs were abandoned or required full restructure. Integration failures (echoes.ts duplicate exports, worktree base branch errors) were resolved manually by the operator, not via the Forge protocol.

**Integration failure rate:** Approximately 2 integration failures per large run (8 Riders): one file ownership gap (echoes.ts), and multiple worktree setup errors per run. Small runs (4 Riders, reaping) had zero integration failures.

**Missed issues by phase:**
- Muster: 1 file ownership gap (echoes.ts dual-modification), 1 serial risk miss (quest-audit), 1 incomplete contract (field ordering not canonicalized), 0 Politico executions
- Pax: unclear separation from Inspector; no documented Gold-caught deviations that Inspector missed
- Forge: no documented executions

### Phases showing the strongest Opus signal

**Muster — decomposition soundness and conflict preemption** is where the historical record shows the most distinctive Gold reasoning. The fragment+stitch pattern, color-first sequencing, and function-level ownership splits are all judgment calls that required understanding the domain semantics and the downstream integration consequences — not just mechanical application of "files must be unique." These three moments are the clearest evidence that Gold is doing something more than rule-following during Muster.

**Pax — independent validation** is the phase where Sonnet replacement carries the highest latent risk, even though the historical data is thin. The `pax_deviation_detection_rate` rubric's double-weight for high-confidence subtly-wrong Howlers reflects a real failure mode that Gold has not been tested against in production. If Sonnet Pax misses a deviation that a self-confident Howler falsely reports as complete, the consequence is a broken merge — and there is no historical evidence that Opus Gold would catch it either.

**Forge** presents the most critical gap for the benchmark: zero production Forge decisions means we have no signal on whether Opus Gold's failure classification is meaningfully better than Sonnet Gold. The entire 20% Forge phase weight in the composite score rests on synthetic scenarios alone.

### Implications for the Sonnet comparison benchmark

The benchmark should weight the Muster scenarios most heavily in terms of difficulty and coverage, since this is where historical Gold performance is best-documented and most distinctive. Pax scenarios should focus on the high-confidence deviation case (underrepresented in history but highest consequence). Forge scenarios are a clean slate — design them from first principles against the taxonomy, since there is no historical Gold baseline to compare against.

---

_Document complete. All claims are traceable to the 5 LESSONS.md files listed in the Source Data section._
