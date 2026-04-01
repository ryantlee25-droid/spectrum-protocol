# Dev vs Main — Final Synthesis Report

**Date**: 2026-03-31
**Sources**: H1 (protocol-diff.md), H2 (speed-comparison.md), H3 (quality-comparison.md), H4 (cohesion-analysis.md)
**Commits analyzed**: 19 commits (main..dev), +37,532 / -173 lines across 183 files

---

## 1. Executive Summary

Dev is a meaningful upgrade. The core improvements are real, address documented failure modes, and are architecturally sound. But dev is not clean enough to ship as-is.

The protocol grew from 3,113 to 3,712 lines (+19%). Three new modes were added (Nano, Multi-Candidate, SWE-bench), tripling the mode surface area from 2 to 5. Muster expanded from 15 to 18 steps, with new accuracy gates (Issue Confirmation Gate, White Pre-Check, contract-to-test generation) that address the weaknesses most responsible for Howler failure in main. Quality gate coordination moved from inside Howlers to Gold-coordinated visible background agents — a correct architectural separation that also closes the conflict-of-interest problem where Howlers self-reported completion readiness.

The speed picture is positive: mechanical muster time drops by 3-6 minutes (parallel reads, parallel White+Politico, batched worktree verification), and staggered gate triggering saves 8-15 minutes on 4+ Howler runs. Token efficiency improves modestly via contract-by-reference. Accuracy is projected to jump from D3=2 to D3=3 to D3=3.5 — a meaningful gain that brings Spectrum into Factory/Cursor tier.

What's not ready: SPECTRUM.md was not updated when the Gold Post-Howler Protocol shipped. Howler steps 11-14 in SPECTRUM.md still say Howlers run their own quality gates and open PRs, directly contradicting SPECTRUM-OPS.md and CLAUDE.md. This is a live instruction conflict that will cause Gold to follow different procedures depending on which file it reads. There are also zero test suites for 1,997 lines of new Python tooling that sits in the critical path of full-mode muster. Agent file renames (singular to plural) break existing user installations without a migration guide. The Gold downgrade from Opus to Sonnet is defensible at 91% cost reduction but introduces a documented Pax over-flagging behavior that shifts triage work to humans.

**Verdict**: Merge dev to main after fixing the SPECTRUM.md contradiction and writing agent rename migration instructions. The remaining items are risks to manage, not blockers to shipping.

---

## 2. Scorecard

| Dimension | Main | Dev | Delta | Evidence |
|-----------|------|-----|-------|----------|
| Speed (full-mode muster, mechanical) | ~17-22 min | ~13-16 min | -4 to -6 min | H2: parallel reads (-1-2 min) + parallel White+Politico (-3-4 min) + batched worktree verification (-30s) |
| Speed (quality gates, 4-Howler staggered) | Gates run inside Howlers sequentially | Gates fire per-Howler at completion (Gold-coordinated) | -8 to -15 min (PR availability) | H2: staggered gate model |
| Accuracy (D3 projection) | D3=2 | D3=3 to D3=3.5 | +1.0 to +1.5 D3 units | H3: realistic estimate applying audit confidence weights |
| Agent cohesion | 5.5/10 | 7.5/10 | +2.0 | H4: post-Howler lifecycle documented, gates visible, Gray upgraded Haiku→Sonnet |
| Agent visibility | Low (gate agents invisible) | High (Status Roster, glyphs, background agents) | Significant | H4: Status Roster with glyph identifiers, Gold Post-Howler Protocol |
| Cost per 5-Howler run (Gold model) | Opus: ~$1.50-2.00 (estimated) | Sonnet: ~$0.13-0.18 | ~91% reduction | H1: gold-eval-0331, 0.94 composite vs 1.00 |
| Protocol complexity | 2 modes, 15 muster steps, 1 tool | 5 modes, 18 muster steps, 6 tools | +3 modes, +3 steps, +5 tools | H1: structural changes table |
| Tool count | 1 (seam_check.py) | 6 (+ codebase_index, test_impact_map, verify_postconditions, SWE-bench adapters) | +5 tools, 0 with test suites | H1: tool inventory |
| Breaking changes | None | 5 categories | Agent renames, Gold model, phase renumbering, Howler template, CHECKPOINT.json schema | H1: breaking changes section |

---

## 3. Ship / Don't Ship Recommendation

**Ship — but fix the SPECTRUM.md contradiction first.**

Dev is production-ready on the merits. The accuracy improvements are grounded in real failure analysis. The speed gains are concrete. The cohesion improvements make the system observable in ways main never was. The cost reduction (91% on Gold) is not a gimmick — it is backed by the gold-eval-0331 benchmark.

### What Must Be Fixed First

**SPECTRUM.md Howler template contradiction (blocker)**

SPECTRUM.md lines 638-644 still contain the old Howler steps 11-14: Howler runs White + Gray + /diff-review, Howler opens PR via Copper. SPECTRUM-OPS.md and CLAUDE.md have the new Gold Post-Howler Protocol: Howler signals completion and exits, Gold coordinates all gate agents. These are direct, irreconcilable contradictions in instructions Gold may read during a spectrum run. Gold following SPECTRUM.md will cause Howlers to self-review and open PRs. Gold following SPECTRUM-OPS.md will cause Howlers to exit after signaling completion. The behavior difference is substantial.

Fix: Update SPECTRUM.md Howler template steps to match the Gold Post-Howler Protocol already in SPECTRUM-OPS.md and CLAUDE.md. Remove old steps 11-14. Add step 12 (signal completion, exit). This is a targeted edit, not a rewrite.

**Agent file rename migration guide (blocker for existing users)**

The singular-to-plural rename (`gold.md` -> `golds.md`, etc.) breaks every existing user's `~/.claude/agents/` directory. There is no migration script and no documentation explaining which `subagent_type` values changed. A user merging dev without guidance will find their agents silently undetected.

Fix: Write a one-page migration note covering: (1) the rename mapping for all 11 agent files, (2) updated `subagent_type` values, (3) any `convoy_roles.py` changes. A shell one-liner to rename existing files would eliminate most of the upgrade friction.

### Risks That Remain After Fix

1. **Gold Pax over-flagging**: Sonnet over-classifies Pax observations as blockers at a documented rate. The protocol acknowledges this and asks for human triage. In practice, this means users will see more false-positive blockers in PAX-PLAN.md and must spend time distinguishing real integration risks from Sonnet conservatism. This is an acceptable tradeoff given the 91% cost reduction, but users should be warned explicitly.

2. **Untested tooling in critical path**: `codebase_index.py` (801 lines) and `test_impact_map.py` (333 lines) run during full-mode muster and their output feeds directly into CONTRACT.md. Neither has a test suite. Failures or incorrect output from these tools will produce stale or wrong CONTRACT.md sections that pass White Pre-Check because the tool output itself is wrong. The first few full-mode spectrum runs post-merge should be monitored.

3. **Nano mode has no quality gates**: Nano skips CONTRACT.md, Politico, quality gates, and human approval. The auto-approve + no gates combination means errors in nano mode reach the merge queue without any independent review. The escalation-to-reaping on any blocker is a safety valve, but the happy path has no review. This is an intentional design choice, but users adopting nano mode for non-trivial work may be surprised.

4. **Gold cognitive load**: 18 muster steps plus concurrent Howler lifecycle coordination plus Status Roster maintenance is a significant working memory demand. CHECKPOINT.json mitigates session death but not working memory saturation during a live run with 4+ Howlers completing concurrently.

5. **Contract drift for sequential Howlers**: Codebase Context sections in CONTRACT.md are written at muster time. For dependent Howlers running after earlier Howlers have modified shared files, the context is stale. Dev has no mechanism for updating codebase context mid-run.

### Upgrade Path for Existing Users

1. Pull dev branch to local.
2. Rename agent files using the migration mapping (see migration guide to be written as part of merge prep).
3. Update any global `~/.claude/CLAUDE.md` that hardcodes `model: opus` for Gold to `model: sonnet`.
4. Run `python tools/codebase_index.py --help` and `python tools/test_impact_map.py --help` to verify tool availability before the first spectrum run.
5. On first full-mode run: expect the Issue Confirmation Gate (new human confirmation step before Politico/White Pre-Check freeze).
6. On Pax findings: apply the "human-review for severity" caveat — Sonnet over-flags observations as blockers.

---

## 4. Top Issues to Fix Before Merge

Issues are prioritized by blast radius: blockers first, then structural risks, then polish.

**P0 — Merge Blockers**

1. **SPECTRUM.md Howler template not updated for Gold Post-Howler Protocol** (H1, section 4, contradiction #2). Old steps 11-14 directly contradict SPECTRUM-OPS.md and CLAUDE.md. Gold following SPECTRUM.md will run the wrong pipeline. Fix: update SPECTRUM.md Howler template section (lines ~638-644) to match the dev model.

2. **No agent file rename migration guide** (H1, section 5). The singular-to-plural rename breaks existing `~/.claude/agents/` installations silently. Fix: write migration instructions before or alongside the merge.

**P1 — Structural Risks (Fix Soon After Merge)**

3. **No test suites for new Python tooling** (H1, section 5). `codebase_index.py` (801 lines) and `verify_postconditions.py` (863 lines) are in the critical path with zero test coverage. At minimum, add smoke tests covering the most likely failure modes (missing files, unparseable imports, empty output).

4. **`subagent_type` dual naming** (H1, contradiction #3). SPECTRUM.md still references old aliases (`mayor`, `scout`, `inspector`, `rider`) in the CMUX integration section while OPS uses new pluralized names (`golds`, `blues`, `whites`, `riders`). Clarify which is authoritative or remove the old aliases.

5. **Orange retry count not persisted in CHECKPOINT.json** (H4). After session restart, circuit breaker retry history per Howler is lost. The circuit breaker fires on 2 failures per locus, but if a session dies between failures, the counter resets. Fix: add `orange_retry_count` per Howler to CHECKPOINT.json schema.

**P2 — Quality and Usability**

6. **Quality gate skip conditions not documented in SPECTRUM.md** (H1, contradiction #5). SPECTRUM.md section 2.5 (Quality Gate) does not mention nano mode exceptions. A user reading SPECTRUM.md for nano mode guidance will not know quality gates are skipped.

7. **Politico step 14 placeholder** (H1, contradiction #4). OPS step 14 says "see step 11 above" instead of containing actual instructions. Consolidate or remove the placeholder.

8. **Contract test vs. postcondition verification overlap** (H4). Howler contract test stubs and Gray's full test run both verify CONTRACT.md postconditions. Their distinct scopes are not defined. Clarify what each is checking and why both are needed.

9. **HOWLER-OPS.md path-reference not implemented** (H2). Still inlined (12,500 tokens per 5-Howler run). Marked P2 in the speed audit but straightforward to implement.

**P3 — Polish**

10. **White agent color mismatch** (H4). White is purple in both main and dev. The one remaining color/name inconsistency from main. Minor friction, easy fix.

---

## 5. What We Gained

### Accuracy

- **Issue Confirmation Gate**: The only mechanism in either version that catches Gold's interpretation of the task before it propagates through the entire pipeline. Catches the class of failures where Gold builds the wrong thing perfectly.
- **White Pre-Check**: Independent factual verification of CONTRACT.md against the actual codebase before Howlers drop. Rated 8/10 by the accuracy audit — the most mechanically sound improvement in dev.
- **Codebase context injection via codebase_index.py**: Replaces Gold's prose recall of signatures and imports with AST-derived structural facts. Eliminates the most common class of hallucination in contract authoring.
- **Test impact maps via test_impact_map.py**: Howlers run targeted tests against the files they own, not "all tests." Reduces false-negative test passes on changes that break covered files outside the Howler's scope.
- **Revision loop (up to 2 passes)**: Howlers fix test failures before escalating to White/Gray. Reduces the volume of White blocker escalations for issues the Howler could have caught itself.
- **Pattern library from LESSONS.md**: Known failure patterns injected into Howler drop prompts as `KNOWN RISKS`. Value compounds with each spectrum run.
- **Reflexion check after completion**: Howlers re-read the original task and write a 3-5 line correctness assessment before signaling done. Catches cases where the implementation is internally consistent but diverges from what was asked.

### Speed

- **Parallel muster reads**: LESSONS.md, ENTITIES.md, ARCHITECTURE.md, and codebase_index.py run concurrently. Saves 1-2 minutes per full-mode muster.
- **Parallel White Pre-Check + Politico**: Previously sequential; now concurrent. Saves 3-4 minutes per full-mode muster.
- **Batched worktree verification**: Single `git worktree list` after all creations instead of per-worktree checks. Saves ~30 seconds on 4+ Howler runs.
- **Staggered gate triggering**: Quality gates fire per-Howler at completion rather than waiting for all Howlers. On staggered 4-Howler runs, PRs open 8-15 minutes earlier, enabling human review and incremental integration testing during the run.
- **Nano mode**: ~1-minute muster for 2-3 Howler pure-create runs with obvious boundaries. Reduces coordination overhead to near zero for trivial parallelism.
- **Contract-by-reference**: CONTRACT.md referenced by path instead of inlined in Howler prompts. Saves ~10,000 tokens per 5-Howler spectrum (~$0.03 at current Sonnet rates).

### Cohesion and Observability

- **Gold Post-Howler Protocol**: Explicit spawn sequence between Howler completion and PR creation. Gold now reads HOOK.md, coordinates White+Gray+/diff-review, routes failures to Orange, and spawns Copper only after all gates pass. Closes the undocumented post-Howler gap in main.
- **Status Roster with glyphs**: Real-time visibility into every agent in the pipeline during a run. In a 4-Howler spectrum with staggered gates, the user can see 8-12 concurrent agents without reading prose.
- **HOOK.md context relay to White**: Gate agents receive Howler self-assessment of uncertain areas. White reviews with context rather than running a cold diff.
- **Staggered gate independence**: Gates can run on completed Howlers while other Howlers are still implementing. The pipeline is no longer a synchronous barrier.
- **Gray upgraded Haiku to Sonnet**: Corrects a documented capability mismatch. Haiku misdiagnoses flaky tests; Sonnet does not.
- **Caste framing (plural names)**: Plural `subagent_type` values accurately model multi-instance spawning. Three Whites running simultaneously on three different Howlers requires a different mental model than "White reviewing."
- **Quality gate coordination moved to Gold**: Removes the conflict of interest where Howlers decided when their own work was ready for review. Gate-skip failures (Howlers reaching context limits before running gates) are eliminated.
- **Gold Recovery Protocol**: CHECKPOINT.json expanded with `locus_history`, `circuit_breaker_state`, `active_diagnostics`, `gold_context_snapshot`. Session death during a spectrum run is recoverable without re-reading all HOOK.md files.

### Cost

- **Gold model: Opus to Sonnet**: 91% cost reduction (gold-eval-0331 benchmark: 0.94 composite vs 1.00). The 6% quality gap concentrates in Pax severity classification, not muster or drop quality.
- **Multi-Candidate mode**: For accuracy-critical single-Howler tasks, N-way selection by test pass rate provides a precision lever when cost is not the constraint.

---

## 6. What We Lost or Risked

### Direct Losses

- **Howler self-sufficiency**: Howlers can no longer complete a full cycle (implement, review, open PR) independently. They depend on Gold being alive and coordinating. A Gold session that dies after Howler completion but before gate spawning leaves work in limbo. The CHECKPOINT.json recovery protocol addresses this, but a Howler that could close its own loop is more resilient to Gold failure.

- **Howler simplicity**: The new Howler template has more steps, reflexion checks every 5 file writes, an issue re-read step, a revision loop, and a postcondition assessment. The Howler is more capable but more cognitively loaded. Howlers that were previously lightweight implementors now carry protocol overhead.

### Complexity Growth

- **33 mode-specific skip conditions**: 11 features across 3 modes (full, reaping, nano) create a decision matrix Gold must evaluate correctly at muster time. Gold choosing the wrong mode for a task will silently skip quality gates (nano mode) or architecture documentation (reaping mode) for work that warranted them.

- **5 new modes of failure for the Gold Post-Howler Protocol**: If Gold's context window fills during a large spectrum with concurrent Howler completions, gate coordination may fail silently. Main's model (Howlers coordinate their own gates) fails loudly — the Howler session errors. Gold-coordinated failure is quieter and harder to detect.

- **Phase number drift**: Main has 6 phases with The Proving as Phase 3. Dev absorbs The Proving into The Drop, renumbering Forge to Phase 3 and Pax to Phase 4. SPECTRUM.md was not fully updated. Phase references in documentation are now inconsistent, creating navigation confusion.

### Under-Tested Features

- **Nano mode** has no production runs documented. Auto-approve + no quality gates on a misclassified task (something that was not actually pure-create with obvious boundaries) could reach the merge queue without any independent review.

- **Multi-Candidate mode** has no benchmark results in the repo. The selection algorithm (test pass rate, then fewer files, then first-to-complete) is plausible but unvalidated against actual SWE-bench tasks.

- **New tools** (2,000+ lines of Python) have no test suites. `codebase_index.py` and `verify_postconditions.py` are in the critical path for full-mode muster. Wrong output from these tools produces a wrong CONTRACT.md that then passes White Pre-Check, because White verifies the contract against the codebase — not against the tool's output.

- **Gold Recovery Protocol** has no documented test runs. The recovery path (read CHECKPOINT.json, reconstruct DAG state, resume from current phase) is theoretically sound but untested in practice.

### Residual Accuracy Gaps (Known, Not Fixed)

- **Contract drift for sequential Howlers**: Codebase Context is written at muster time. If Howler A modifies a file that Howler B depends on, Howler B's codebase context is stale from the moment Howler A completes. No mechanism updates it.

- **Behavioral test generation gap**: Dev generates structural test stubs (file existence, type exports). Factory-style Spec → Test → Implement → Verify generates behavioral tests before implementation. The gap is documented but unaddressed.

- **Semantic indexing gap**: `codebase_index.py` uses static analysis of import graphs and function signatures. It cannot capture concurrency invariants, subtle API contracts, or semantic relationships that live in documentation or convention rather than code structure.

---

## 7. Recommended Merge Plan

This plan assumes the P0 blockers are fixed before merge. All other items can be addressed post-merge.

### Step 1: Pre-Merge Fixes (in this order)

**1a. Fix SPECTRUM.md Howler template** (estimated: 30 minutes)

Edit SPECTRUM.md section 2.1 (Howler Drop Template), lines ~638-644. Replace old steps 11-14 (self-review + PR open) with the new step 12 from SPECTRUM-OPS.md: "Signal completion: set `Status: complete` in HOOK.md. Your job ends here. Gold will spawn White, Gray, and /diff-review." While in SPECTRUM.md, also fix: phase numbering (The Proving absorbed into The Drop), quality gate skip condition table (add nano mode column), and CMUX alias references (`mayor`/`scout`/`inspector`/`rider` → update or annotate as legacy aliases).

**1b. Write agent rename migration instructions** (estimated: 20 minutes)

Create a one-page `MIGRATION.md` at the repo root covering: (1) the rename mapping for all 11 agent files, (2) shell one-liner to rename `~/.claude/agents/` files in place, (3) `subagent_type` value changes, (4) Gold model change (Opus → Sonnet) and how to update global CLAUDE.md if it hardcodes opus.

**1c. Run a smoke test on the new Python tools** (estimated: 1 hour)

Write minimal smoke tests for `codebase_index.py` and `test_impact_map.py` covering: valid input with known fixture, missing file input (graceful error, not crash), empty directory input. This does not need to be comprehensive — the goal is confirming the tools run without crashing on normal inputs.

### Step 2: Merge

Merge dev to main. Prefer a merge commit (not squash) so the 19-commit history is preserved for attribution.

### Step 3: Immediate Post-Merge Validation (within 1-2 days)

**3a. Run a full-mode spectrum on a low-stakes task** to validate the Gold Post-Howler Protocol end-to-end. Confirm: Status Roster appears, White + Gray + /diff-review spawn as background agents after Howler completion, Copper opens PR only after all gates pass. If any step is silent or missing, pause and investigate before running a high-stakes spectrum.

**3b. Verify Issue Confirmation Gate fires** during muster. It should appear after CONTRACT.md is written but before White Pre-Check runs. If it does not appear, check whether Gold is following CLAUDE.md muster step 10 correctly.

**3c. Check Pax output quality on the first merged run**. Compare PAX-PLAN.md blocker list against your own assessment. If Sonnet is over-flagging observations as blockers, document the pattern and add it to LESSONS.md `## Known Failure Patterns` immediately — this feeds the pattern library that compounds over time.

### Step 4: Post-Merge Backlog (schedule within 1-2 weeks)

- Add Orange retry count to CHECKPOINT.json schema (P1, prevents circuit breaker reset on session restart)
- Add HOWLER-OPS.md path-reference to reduce Howler prompt size by ~12,500 tokens per 5-Howler spectrum (P2)
- Expand smoke tests for `verify_postconditions.py` (P2)
- Fix White agent color to white (P3)
- Investigate Nano mode escalation behavior by running a test nano spectrum (P2, before recommending nano to others)

### Step 5: LESSONS.md Update After First Successful Merged Spectrum

After the first successful full-mode spectrum run on the merged main branch, have Brown draft and Gold review a LESSONS.md update capturing: Gold Post-Howler Protocol observations, Pax over-flagging rate observed in practice, and any issues encountered with the new tools. This converts first-run observations into future Howler knowledge automatically.

---

*DEV-VS-MAIN-REPORT.md — Spectrum Howler synthesis — 2026-03-31*
