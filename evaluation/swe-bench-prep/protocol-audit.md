# Protocol Validation Audit — swe-bench-prep-0401

**Auditor**: H1 (Protocol Validation Auditor)
**Spectrum**: swe-bench-prep-0401
**Date**: 2026-03-31
**Source files reviewed**:
- `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md`
- `/Users/ryan/spectrum-protocol/spectrum/CLAUDE.md`
- `/Users/ryan/spectrum-protocol/evaluation/accuracy-improvements/PLAN.md`
- `/Users/ryan/spectrum-protocol/tools/test_impact_map.py`

**Rating key**: Green = ready to use as-is | Yellow = usable but has gaps | Red = blocked, needs fix before SWE-bench

---

## Per-Improvement Assessments

---

### I1 — Issue Re-Read (Reflexion)

**Overall: Green**

**Completeness**: All four documented changes are present:
- Instruction `8b` exists in the Howler Drop Template (SPECTRUM-OPS.md lines ~382–389)
- `## Issue Re-Read` section exists in HOOK.md Template (lines ~459–462)
- Safety Rails bullet exists: "Issue re-read mandatory after completion verification" (line ~681)
- CLAUDE.md Howler execution rules includes the issue re-read bullet (lines ~170–172)

**Consistency**: SPECTRUM-OPS.md and CLAUDE.md agree on the requirement. CLAUDE.md summarizes correctly: "re-reads the original task and writes a 3–5 line correctness assessment in HOOK.md. If a gap is found, fix before quality gates."

**Implementability**: The instruction is unambiguous. The three self-assessment prompts ("Does my implementation resolve the stated problem end-to-end?", "What edge cases...", "Is there anything I deprioritized?") give the Howler clear direction. The escape hatch ("Issue re-read: no gaps identified." and proceed) is specified.

**Ordering**: Step 8b correctly follows `8. COMPLETION VERIFICATION` and precedes `9.` (quality gates). The dependency is correct — you can only assess correctness after mechanically verifying files exist.

**Edge cases**:
- No-test projects: not relevant to this step
- Reaping/nano mode: not explicitly excluded, but the instruction is self-contained and harmless in those modes. Low risk.
- Doc-only spectrums: applies naturally (was my doc accurate end-to-end?)

**Minor finding**: The step numbering in the Drop Template is irregular: `8`, `8b`, `8c`, `9`, `10`, `11`, `12`. The plan originally called this "8b" to avoid renumbering, which was accepted. The numbering is functionally fine but would confuse a reader who expects sequential integers. This is a warning, not a blocker.

---

### I2 — Test Dependency Maps

**Overall: Green**

**Completeness**:
- `tools/test_impact_map.py` exists and is fully implemented (~273 lines)
- Muster checklist item present: "Test impact map generated for each Howler's MODIFIES/CREATES files..." (SPECTRUM-OPS.md ~line 126)
- CONTRACT.md content description includes test impact map bullet in step 10 (SPECTRUM-OPS.md ~line 56)
- Howler Drop Template instruction 8 completion verification references the test impact map: "run the specific test files listed in your ## Test Impact Map (from CONTRACT.md). If no map was provided, run tests on your owned files." (lines ~375–378)
- CLAUDE.md muster step 9 includes: "Test impact map per Howler (run `tools/test_impact_map.py`; include in CONTRACT.md)" (line ~85)

**Tool interface match**: The tool's CLI matches the documented interface exactly:
```
python3 tools/test_impact_map.py --files src/auth/login.ts --root .
```
Output format matches the documented `## Test Impact Map` block. Exit 0 always. Handles TypeScript, JavaScript, Python, empty results.

**Consistency**: SPECTRUM-OPS.md and CLAUDE.md agree. The tool path referenced in CONTRACT.md content (`python3 tools/test_impact_map.py --files {MODIFIES+CREATES} --root {project_root}`) matches the actual file location.

**Implementability**: Gold knows exactly what to run and where to put the output. Howlers know exactly what section to look for and what to do with it. The "If no map was provided" fallback handles missing maps gracefully.

**Edge cases**:
- No-test projects: tool exits 0 with "(no tests found)" per source file. Howlers skip map-based testing. Handled.
- Reaping/nano mode: the plan notes these should skip the test impact map. **Gap**: SPECTRUM-OPS.md's Reaping Mode section does not mention skipping the test impact map. The muster checklist item doesn't include a "skip for reaping mode" note. Since reaping mode has no MODIFIES files and skips CONTRACT.md sections, a Howler following reaping mode instructions would find no `## Test Impact Map` section and naturally fall back to the default. Low risk but worth documenting explicitly.
- CREATES files: the muster checklist says "MODIFIES/CREATES files" — but running the tool on CREATES files (which don't exist yet) will produce "(no tests found)" since the files aren't present. This is harmless but slightly misleading. The tool doesn't fail on missing source files (it just finds no tests), so no functional break. Gold could omit CREATES-only files from the tool invocation.

**Minor finding**: The tool path in the CONTRACT.md content description is `python3 tools/test_impact_map.py` (relative). This assumes the working directory is the project root. For projects with non-standard layouts, this could fail silently. Not a blocker but Gold should use `python3 {project_root}/tools/test_impact_map.py` or an absolute path.

---

### I3 — Codebase Context Injection

**Overall: Yellow**

**Completeness**: All documented changes are present:
- CONTRACT.md step 10 includes per-Howler `## Codebase Context` section with `5–15 lines per file` scope limit (SPECTRUM-OPS.md ~lines 52–53)
- Muster checklist item present: "Codebase context sections written in CONTRACT.md for each Howler's MODIFIES files (existing function signatures, patterns, gotchas — 5-15 lines per file)" (~line 128)
- Howler Drop Template instruction 0 directs Howlers to read the `## Codebase Context` section first (lines ~353–360)
- CLAUDE.md muster step 9 mentions: "Per-Howler codebase context: Gold reads each MODIFIES file and summarizes key patterns, function signatures, and gotchas (5–15 lines per file; skip for newly CREATED files)" (lines ~81–83)

**Consistency**: SPECTRUM-OPS.md and CLAUDE.md agree on scope (5–15 lines, MODIFIES only, N/A for CREATES).

**Implementability**: Yellow rating here. Two gaps:

**Gap 1 — Scope creep risk**: The instruction says "Gold reads each file in the Howler's MODIFIES list and summarizes existing function signatures relevant to the task, patterns in use..., and any gotchas observed." In a full-mode spectrum with many MODIFIES files, this could produce very large CONTRACT.md sections. The 5–15 line limit is stated but there is no enforcement mechanism. The plan notes this is "a common failure mode: Gold reads 20 files and writes 2000-token summaries" but the instruction itself doesn't provide a circuit breaker (e.g., "if MODIFIES list > 10 files, summarize only the 5 most-changed files"). For SWE-bench tasks (avg 4.1 files), this is fine. For large spectrums, it's a latent risk.

**Gap 2 — Missing N/A instruction in SPECTRUM-OPS.md**: The CLAUDE.md version says "skip for newly CREATED files." SPECTRUM-OPS.md's CONTRACT.md content description says "Skip for files being newly CREATED" (end of bullet). The SPECTRUM-OPS.md muster checklist item does NOT mention the CREATES exemption. A Gold following the checklist might write context for all files including CREATES (which don't exist). The plan's note about `## Codebase Context: N/A (all new files)` exists only in the PLAN.md, not in SPECTRUM-OPS.md.

**Recommended fix for Gap 2**: Append "(skip for files in CREATES — N/A is valid)" to the muster checklist item.

**Edge cases**:
- Reaping/nano mode: not explicitly excluded from this requirement. Since reaping mode has no MODIFIES files by definition (all pure-create), Gold would write `N/A` for all Howlers. This is harmless but wastes time verifying. Low risk.
- White Pre-Check (I4) validates the Codebase Context section against the real codebase — this is a good safeguard against Gold writing stale or incorrect summaries.

---

### I4 — White Pre-Check

**Overall: Green**

**Completeness**: All documented changes are present:
- New step 11 exists in SPECTRUM-OPS.md Phase 1 muster sequence (lines ~57–72), between step 10 (CONTRACT.md) and step 13 (convoy-contracts.d.ts). Wait — step 13 is `convoy-contracts.d.ts` in SPECTRUM-OPS.md, but step 12 is contract-to-test generation (I5). The ordering matches the PLAN.md intent: Pre-Check (11) → contract tests (12) → convoy-contracts.d.ts (13) → Politico (14). Correct.
- White Pre-Check prompt explicitly excludes CREATES files: "Skip for files in CREATES (they don't exist yet by design)" — present in the prompt text (line ~67).
- Politico prompt notes White Pre-Check has already handled factual verification (lines ~88–91): "Note: the White Pre-Check (step 11) has already validated factual accuracy of CONTRACT.md against the codebase. Your role is adversarial review of the *decomposition logic and interface design*, not re-checking file existence."
- Muster checklist includes: "White Pre-Check completed — all STALE/MISSING/MISMATCH findings patched or documented as ASSUMPTION in CONTRACT.md (skip for reaping mode and nano mode)" (line ~128)
- CLAUDE.md muster step 10 includes the White Pre-Check (lines ~86–88): "White Pre-Check — after writing CONTRACT.md, before freezing: drop White to verify all referenced files exist and documented signatures match the actual codebase. Gold patches CONTRACT.md based on findings. Skip for reaping mode and nano mode."

**Consistency**: SPECTRUM-OPS.md and CLAUDE.md agree. Both specify reaping/nano mode skip. SPECTRUM-OPS.md's version is much more detailed (full prompt text, STALE/MISSING/MISMATCH taxonomy, ASSUMPTION documentation). CLAUDE.md summarizes correctly.

**Implementability**: The White Pre-Check prompt is specific enough to run without ambiguity. The three checks (a, b, c) are concrete. The reporting taxonomy (STALE/MISSING/MISMATCH) tells White exactly how to structure its output. Gold knows exactly what to do with the output (patch or document as ASSUMPTION).

**One tension**: The PLAN.md specified this runs before Politico to ensure Politico reviews a factually accurate contract. SPECTRUM-OPS.md implements this correctly (step 11 before step 14). However, I5 (contract-to-test generation, step 12) also depends on an accurate CONTRACT.md. The ordering (White Pre-Check → contract tests → Politico) is correct: Pre-Check validates → contract tests are generated based on validated contract → Politico reviews the final contract. No ordering bug.

**Edge cases**:
- Doc-only spectrums: not explicitly excluded. However, a doc-only spectrum may have no MODIFIES files with function signatures to check. White would check file existence (MODIFIES) and report MISSING if referenced docs don't exist. This is valid and useful. Not a gap.
- No-codebase projects (pure new): White Pre-Check on a pure-create spectrum would check file existence (all CREATES don't exist, but those are explicitly excluded). White would have little to report. Harmless.

---

### I5 — Contract-to-Test Generation

**Overall: Yellow**

**Completeness**:
- Step 12 exists in SPECTRUM-OPS.md: "for each Howler with postconditions in CONTRACT.md, Gold generates a stub test file at `tests/spectrum/<howler-name>.contract.test.{ts|py}` that asserts each postcondition is satisfied..." (lines ~73–78)
- Skip conditions specified: "Skip for doc-only spectrums and nano mode"
- Muster checklist item present: "Contract test stubs generated and committed for each Howler with postconditions (skip for doc-only and nano mode)" (~line 130)
- Howler Drop Template instruction 8 (completion verification) references contract tests: "Contract tests: run `tests/spectrum/{howler-name}.contract.test.{ts|py}` — these verify your CONTRACT.md postconditions are satisfied. All must pass before quality gates." (~lines ~379–381)
- CLAUDE.md includes: "Contract tests: Howlers run contract test stubs (generated by Gold) as part of completion verification. These test postconditions, not business logic." (~line 174)

**Consistency**: SPECTRUM-OPS.md and CLAUDE.md agree.

**Implementability**: Yellow rating for three reasons:

**Gap 1 — What does a Gold-generated contract test look like?** The instruction says Gold "generates a stub test file... that asserts each postcondition is satisfied (file exists, type exports correctly, function signatures match)." But there is no example test stub, no template, and no specification of what test framework to use. A Gold following these instructions must infer: which test framework? (jest/vitest for TS, pytest for Python — but the project may use either). What assertion patterns for "file exists"? What does "type exports correctly" mean as a runnable test vs. a TypeScript type check? This is underspecified for implementation.

**Gap 2 — Reaping mode exclusion is incomplete**. Step 12 says "Skip for doc-only spectrums and nano mode." But reaping mode is not mentioned. The rationale in the plan (I5 wasn't in the original PLAN.md, it was added separately) presumably intended to skip for reaping mode too. The muster checklist's phrasing "skip for doc-only and nano mode" also omits reaping mode. Since reaping mode is for pure-create Howlers with simplified contracts (no DbC sections), there are no postconditions to test — but the instruction doesn't say this explicitly. A Gold in reaping mode would not know whether to generate contract tests.

**Recommended fix for Gap 1**: Add a minimal example to step 12 or reference a template. At minimum, specify: "For TypeScript: use jest/vitest import assertions. For Python: use pytest. Test assertions: (1) `expect(existsSync('{file}')).toBe(true)` for CREATES files, (2) `import type { X } from '{module}'` with tsc type check for exported types."

**Recommended fix for Gap 2**: Add "and reaping mode" to the skip conditions in step 12 and the checklist item.

**Gap 3 — Commit logistics**: Step 12 says "Commit alongside convoy-contracts.d.ts." But step 13 is commit convoy-contracts.d.ts. The instruction to commit contract tests is attached to step 12, while the actual commit action happens at step 13. A literal reader might try to commit at step 12 before convoy-contracts.d.ts is written. The ordering is: write tests (12) → write convoy-contracts.d.ts (13) → commit both. This is implied but not stated. Low risk, worth clarifying.

**Edge cases**:
- SWE-bench tasks: The swe-bench-prep PLAN.md explicitly notes "No contract tests (I5)" for doc-only spectrums. But for SWE-bench code tasks, contract tests would apply. This is handled by the TypeScript/Python restriction.
- Projects without test infrastructure: the instruction says "commit alongside convoy-contracts.d.ts" but if the project has no `tests/` directory and no test framework, running the contract test stubs requires setting up infrastructure. This isn't addressed. A Howler could fail trying to run `tests/spectrum/howler-name.contract.test.ts` in a project with no jest/vitest config.

---

### I6 — Revision Pass

**Overall: Green**

**Completeness**:
- Step `8c` exists in Howler Drop Template: "REVISION PASS: If completion verification or contract tests revealed failures: Read the test output and error messages carefully... Maximum 2 revision passes..." (lines ~392–398)
- HOOK.md Template includes `## Revision Pass` section with "Pass 1: {...}" and "Pass 2: {if needed...}" fields (lines ~463–465)
- Safety Rails bullet present: "Revision pass: max 2 attempts to fix test failures before escalating to quality gates" (~line 683)
- CLAUDE.md includes: "Revision pass: After completion verification, if tests fail, Howlers get up to 2 revision passes with test output as context. Max 2 attempts before escalating to quality gates." (~lines 172–174)

**Consistency**: SPECTRUM-OPS.md and CLAUDE.md agree. Both say max 2 revision passes.

**Implementability**: The step is clear. The escape hatch for passing tests is explicit: "If all tests passed on first try: skip this step." The escalation path is clear: after 2 passes, proceed to quality gates and document failures.

**Ordering**: `8c` correctly follows `8b` (issue re-read) and precedes `9` (quality gates). The dependency makes sense: fix test failures after the issue re-read assessment, before escalating to White/Gray.

**One potential confusion**: Step 8c says "If completion verification or contract tests revealed failures." But the order in the template is:
- Step 8: Completion verification (run tests)
- Step 8b: Issue re-read
- Step 8c: Revision pass (if failures from step 8)

A Howler who finds test failures in step 8 must remember to do step 8b (issue re-read) before 8c (revision pass). The instruction text of 8c doesn't reference 8b. This is a minor coherence issue — a Howler might skip 8b if tests fail and go straight to 8c. The HOOK.md template forces both sections to be filled, which mitigates this. Low risk.

**Edge cases**:
- If issue re-read (8b) reveals a gap and the Howler fixes it, but the fix causes new test failures: 8c would cover this. The revision pass counts apply regardless of why tests fail.
- Nano mode: revision pass is not excluded, but nano mode Howlers "self-verify only" with no type checks or test runner (unless test infrastructure). Step 8c references test failures — nano Howlers with no test runner would skip naturally.

---

### I7 — Pattern Library (Known Failure Patterns from LESSONS.md)

**Overall: Green**

**Completeness**:
- Muster step 3 in SPECTRUM-OPS.md includes: "If LESSONS.md contains a `## Known Failure Patterns` section, scan for patterns matching the current spectrum's task types and include relevant ones in each Howler's drop prompt under `KNOWN RISKS (from prior spectrums)`." (lines ~39)
- CLAUDE.md muster step 3 matches: "If LESSONS.md has a `## Known Failure Patterns` section, inject patterns matching the current task types into Howler drop prompts as `KNOWN RISKS`." (~line 68)
- Howler Drop Template has the `KNOWN RISKS` section at the bottom (~lines 411–413): "KNOWN RISKS (from prior spectrums — if any match this task type): {Gold injects 0-3 relevant failure patterns from LESSONS.md ## Known Failure Patterns. If none match, omit this section.}"
- Triumph phase (Phase 6) instructs Brown to extract patterns: "Additionally, extract any recurring failure patterns into a `## Known Failure Patterns` section at the bottom of LESSONS.md. Each pattern entry follows this format: ### Pattern: {short name} - Task type: ... - Failure mode: ... - Signal: ... - Mitigation: ..." (lines ~604–615)
- CLAUDE.md Triumph (Phase 6) matches: "Brown also extracts structured failure patterns into `## Known Failure Patterns` in LESSONS.md for injection into future Howler drop prompts." (~line 228)

**Consistency**: SPECTRUM-OPS.md and CLAUDE.md agree.

**Implementability**: Green. The full round-trip is specified:
1. Brown extracts patterns from LESSONS.md artifacts (Triumph)
2. Pattern format is defined (short name, task type, failure mode, signal, mitigation)
3. Gold scans patterns during muster step 3
4. Gold injects 0-3 matching patterns into drop prompts
5. "Omit this section" if none match — clean escape

The pattern format is concrete enough for Brown to produce and Gold to parse. The "0-3 patterns" limit prevents bloat. The "if any match this task type" gives Gold clear selection criteria.

**One gap**: How does Gold determine if a pattern "matches" the current task type? The criterion is fuzzy — "task types" is not a defined vocabulary. A pattern might say `Task type: doc-only` and the current spectrum is a mixed code+doc run. Gold would need to make a judgment call. This is acceptable (Gold is the reasoning-heavy agent), but the absence of a matching heuristic means two different Gold invocations might inject different patterns for the same task. This is low risk but could reduce reproducibility.

**Edge cases**:
- New project with no LESSONS.md: step 3 says "if present" — handled gracefully.
- Reaping/nano mode: not excluded. Since patterns inject into the drop prompt (which reaping/nano Howlers also receive), this is fine and potentially valuable.

---

## Howler Drop Template — Holistic Review

**Instruction numbering**: The final instruction sequence is: `0, 1, 2, 3, 4, 5, 6, 7, 8, 8b, 8c, 9, 10, 11, 12`. This is the result of two insertions (8b and 8c) added without renumbering. It works but is jarring. A reader following the instructions must understand that 8b and 8c are substeps of 8, not a different numbering scheme. The HOOK.md Template reinforces this structure with separate sections (`## Completion Verification`, `## Issue Re-Read`, `## Revision Pass`), which helps.

**Step 0 placement**: Step 0 is "Read CONTRACT.md FIRST." This is the correct first action, but numbering it 0 (while git index confusion aside) works as a "before you start" signal. Acceptable and intentional.

**Coherence top-to-bottom**: The template reads coherently. Steps 1-7 are setup and ongoing maintenance. Step 8 and its substeps (8b, 8c) form a completion verification block. Steps 9-12 are quality gates and delivery. The `DISCOVERY RELAY` and `KNOWN RISKS` sections at the bottom are context-injection sections, not action steps — this is appropriate.

**Template length**: The template is long (~90 lines of instruction text). For a SWE-bench single-task run, this is significant overhead. The swe-bench-prep PLAN.md notes this concern under H1's scope. At Sonnet rates, the drop template adds approximately 2,000–3,000 input tokens per Howler. For a 50-task SWE-bench run, this is roughly $1.50–$2.50 in template overhead alone. Not a blocker but relevant to H4's cost model.

**Redundancy check**: The REFLEXION step (5) and SCOPE ALIGNMENT CHECK (6) both ask the Howler to re-read the task. They serve different purposes: REFLEXION is per-file-write (am I touching the right files?); SCOPE ALIGNMENT CHECK is every 20 tool calls (am I on track globally?). These are not redundant — one is granular, one is periodic. The issue re-read (8b) is a third re-read, but it's post-completion and correctness-focused. Three re-read steps is aggressive but defensible given the reflexion research basis.

**DISCOVERY RELAY positioning**: The relay appears after the `KNOWN RISKS` section at the very bottom of the template. This means it appears *after* all instructions. A Howler reads the instructions, then the relay context. This is the correct order (instructions first, then background context). No issue.

**HOOK.md cross-reference**: Every section mentioned in the drop template (`## Completion Verification`, `## Issue Re-Read`, `## Revision Pass`, `## Decisions`, `## Seams`, `## Cross-Domain Observations`, `## Progress`, `## Blockers`, `## Errors Encountered`) exists in the HOOK.md template. Complete coverage.

---

## HOOK.md Template — Review

**Completeness against drop template instructions**:

| Drop template instruction | HOOK.md section | Present? |
|---------------------------|-----------------|----------|
| Write HOOK.md immediately | Full template header | Yes |
| Update continuously | Updated: timestamp + Status fields | Yes |
| STABLE checkpoint | `## Checkpoints` | Yes |
| REFLEXION (step 5) | Implicitly via `## File Ownership` | Partial — no explicit reflexion log |
| SCOPE ALIGNMENT CHECK (6) | `## Progress` (write alignment entry) | Partial — no dedicated section |
| COMPLETION VERIFICATION (8) | `## Completion Verification` | Yes |
| ISSUE RE-READ (8b) | `## Issue Re-Read` | Yes |
| REVISION PASS (8c) | `## Revision Pass` | Yes |
| Seams | `## Seams` | Yes |
| Cross-domain | `## Cross-Domain Observations` | Yes |
| Blockers | `## Blockers` | Yes |
| Errors | `## Errors Encountered` | Yes |

**Gap**: Steps 5 (REFLEXION) and 6 (SCOPE ALIGNMENT CHECK) both instruct the Howler to write in HOOK.md, but neither has a dedicated section. Step 5 says "STOP and log drift" (but where?), and step 6 says "Write a 1-line 'Alignment: on-track' or 'Alignment: drifted — [reason]' entry in HOOK.md under Progress." The `## Progress` section exists, so step 6 has a home. Step 5's drift logging is implicitly captured under `## Blockers` or `## Errors Encountered` but this is not stated. Low risk — most Howlers would naturally put drift under Progress or Blockers.

**git_status field**: Present and documented below the HOOK.md template: "`git_status` values: `ok` (default), `needs_operator_commit`." Correct.

**Heartbeat instruction**: Present in SPECTRUM-OPS.md below the HOOK.md template: "Every 30 tool calls or ~1 hour (whichever comes first), update HOOK.md with current status." The HOOK.md template itself doesn't have a dedicated heartbeat section — Howlers would update the `Updated:` timestamp and `Status:` field. This is sufficient.

**Alignment check**: The `Confidence` and `Confidence-Note` fields in the HOOK.md header are good but not referenced by any drop template instruction. They appear to be carried forward from a pre-improvement version of the template. They're harmless and potentially useful, but they're orphaned (no instruction tells the Howler when to update them).

---

## Muster Checklist — Review

**Full checklist items** (from SPECTRUM-OPS.md ~lines 117–133):
1. PLAN.md validated (sampled files confirm gap claims are current)
2. DAG is acyclic
3. Zero overlapping CREATES/MODIFIES in file matrix
4. Decomposition hazard scan completed (no unaddressed integration bottlenecks)
5. Every Howler has effort/risk tags in MANIFEST.md
6. Every Howler has Preconditions/Postconditions/Invariants (full DbC for interface-heavy; conventions-only for pure-create)
7. Every checkpoint dep name exists in the contract
8. LESSONS.md + ENTITIES.md incorporated
9. Test impact map generated for each Howler's MODIFIES/CREATES files (run tools/test_impact_map.py; include output in CONTRACT.md per Howler)
10. Codebase context sections written in CONTRACT.md for each Howler's MODIFIES files (existing function signatures, patterns, gotchas — 5-15 lines per file)
11. White Pre-Check completed — all STALE/MISSING/MISMATCH findings patched or documented as ASSUMPTION in CONTRACT.md (skip for reaping mode and nano mode)
12. Contract test stubs generated and committed for each Howler with postconditions (skip for doc-only and nano mode)
13. Adversarial Politico review completed (blockers addressed, warnings documented) — skip for reaping mode
14. High-risk seams and accepted Politico concerns flagged for human review
15. ARCHITECTURE.md updated (persistent, incremental — never regenerated)
16. CHECKPOINT.json written with defined schema

**Coverage against muster steps**:

| Muster step | Checklist item? | Notes |
|-------------|-----------------|-------|
| 1. Generate rain ID | No | Trivially verifiable; omission acceptable |
| 2. Create spectrum directory | No | Trivially verifiable; omission acceptable |
| 3. Read LESSONS.md + ENTITIES.md | Item 8 (partially) | Item 8 says "incorporated" but doesn't check Known Failure Patterns injection |
| 4. Validate PLAN.md | Item 1 | Covered |
| 5. Evaluate scale | No | Judgment call; no checklist gate needed |
| 6. Update ARCHITECTURE.md | Item 15 | Covered |
| 7. DESIGN.md (optional) | No | Optional step; acceptable to skip |
| 8. Decomposition hazard scan | Item 4 | Covered |
| 9. Write MANIFEST.md | Items 2, 3, 4, 5 | Partially covered by related checks |
| 10. Write CONTRACT.md | Items 6, 9, 10 | Covered |
| 11. White Pre-Check | Item 11 | Covered |
| 12. Contract-to-test generation | Item 12 | Covered |
| 13. convoy-contracts.d.ts | No | Gap — no checklist item for TypeScript type file |
| 14. Politico review | Item 13 | Covered |
| 15. Present to human | Item 14 | Covered |
| 16. Write CHECKPOINT.json | Item 16 | Covered |

**Gap**: No checklist item for `convoy-contracts.d.ts` (step 13 in SPECTRUM-OPS.md, step 12 in CLAUDE.md). This is a TypeScript-only artifact, and omitting it would mean Howlers start without shared type definitions. This is a pre-existing gap (predates the 7 improvements) but worth flagging.

**Ordering concern — checklist vs. muster steps**: The muster checklist items are not in the same order as the muster steps. For example, ARCHITECTURE.md (muster step 6) is checklist item 15. Zero overlapping CREATES/MODIFIES (MANIFEST.md check, muster step 9) is checklist item 3. This makes the checklist harder to use as a sequential verification tool. It reads more as a "did you remember everything?" list than a "did you do these in order?" list. This is acceptable for an end-of-muster checklist (verify all before presenting to human), but could be confusing if a Gold uses it to track progress through muster.

**Checklist item 11 (White Pre-Check) ordering note**: The checklist correctly specifies "skip for reaping mode and nano mode." However, it does not specify the ordering constraint (must run before Politico). This is captured in the muster steps themselves (step 11 before step 14) but not in the checklist. Minor.

---

## Summary Table

| Improvement | Complete? | Consistent? | Implementable? | Rating | SWE-bench ready? |
|-------------|-----------|-------------|----------------|--------|-----------------|
| I1 — Issue Re-Read | Yes | Yes | Yes | Green | Yes |
| I2 — Test Dependency Maps | Yes | Yes | Yes (minor path caveat) | Green | Yes |
| I3 — Codebase Context | Yes | Yes | Mostly (CREATES caveat in checklist) | Yellow | Yes (minor fix) |
| I4 — White Pre-Check | Yes | Yes | Yes | Green | Yes |
| I5 — Contract-to-Test | Yes | Yes | Partial (no test stub template, reaping mode gap) | Yellow | No — fix first |
| I6 — Revision Pass | Yes | Yes | Yes (minor 8b→8c ordering note) | Green | Yes |
| I7 — Pattern Library | Yes | Yes | Yes (fuzzy matching criterion) | Green | Yes |

---

## Recommended Fixes

Listed in priority order. Bold = fix before SWE-bench run.

### P1 — Must fix before SWE-bench

**Fix 1: I5 — Add reaping mode skip to contract-to-test step**
- File: `spectrum/SPECTRUM-OPS.md`, step 12
- Current: "Skip for doc-only spectrums and nano mode."
- Fix: "Skip for doc-only spectrums, nano mode, and reaping mode."
- Also update: muster checklist item 12 — add "and reaping mode" to skip note

**Fix 2: I5 — Add minimal contract test template or framework guidance**
- File: `spectrum/SPECTRUM-OPS.md`, step 12
- Current: "Gold generates a stub test file... that asserts each postcondition is satisfied (file exists, type exports correctly, function signatures match)"
- Fix: Add a 5-line example or reference. Example addition:
  ```
  TypeScript example: `import { existsSync } from 'fs'; test('file exists', () => expect(existsSync('src/foo.ts')).toBe(true));`
  Python example: `def test_file_exists(): import os; assert os.path.exists('src/foo.py')`
  Use the project's existing test framework (jest/vitest/pytest). If no test infrastructure exists, skip this step and document as ASSUMPTION.
  ```

### P2 — Fix before the next full-mode spectrum (not a SWE-bench blocker)

**Fix 3: I3 — Add CREATES exemption to muster checklist item**
- File: `spectrum/SPECTRUM-OPS.md`, muster checklist item 10
- Current: "Codebase context sections written in CONTRACT.md for each Howler's MODIFIES files (existing function signatures, patterns, gotchas — 5-15 lines per file)"
- Fix: Append "(write `## Codebase Context: N/A (all new files)` for pure-create Howlers)"

**Fix 4: I2 — Add reaping mode skip note to test impact map checklist item**
- File: `spectrum/SPECTRUM-OPS.md`, muster checklist item 9
- Current: "Test impact map generated for each Howler's MODIFIES/CREATES files..."
- Fix: Append "(skip for reaping mode and nano mode)"

**Fix 5: Add convoy-contracts.d.ts checklist item**
- File: `spectrum/SPECTRUM-OPS.md`, muster checklist (after item 12)
- Add: "- [ ] `convoy-contracts.d.ts` committed to base branch before Howler drop (TypeScript spectrum only; skip for doc-only and nano mode)"

### P3 — Low risk, fix when convenient

**Fix 6: I5 — Clarify commit ordering for contract tests and convoy-contracts.d.ts**
- File: `spectrum/SPECTRUM-OPS.md`, step 12
- Current: "Commit alongside convoy-contracts.d.ts"
- Fix: "Stage alongside convoy-contracts.d.ts and commit together in step 13"

**Fix 7: HOOK.md — Add alignment log home for step 5 drift**
- File: `spectrum/SPECTRUM-OPS.md`, HOOK.md Template
- Add under `## Progress`: "(Alignment check log: write 'Alignment: on-track' or 'Alignment: drifted — [reason]' entries here during scope alignment checks)"

---

## Protocol Coherence Score

**Overall score: 8.5 / 10**

The protocol is not a mess. Seven additions by different agents integrated without major contradictions. The core logic (muster → drop → verify → quality gate → pax → merge) is intact. The additions reinforce each other correctly: I3 (context injection) feeds I4 (White Pre-Check validates that context), I2 (test maps) feeds I6 (revision pass uses the same tests), I7 (pattern library) feeds I1 (reflexion is the most common pattern to inject).

**Points deducted**:
- **-0.5**: I5 (contract-to-test) is underspecified for implementation — Gold would need to make unsupported inferences about test framework and assertion patterns. This is the single most significant gap.
- **-0.5**: Step numbering irregularity (8, 8b, 8c) and muster checklist ordering don't match step ordering. These create cognitive friction but not functional failures.
- **-0.5**: Three minor cross-cutting gaps (CREATES exemption not in checklist item 10, reaping mode not in step 12 skip conditions, no checklist item for convoy-contracts.d.ts) that could cause avoidable mistakes in edge cases.

**Points in favor**:
- I1, I2, I4, I6, I7 are clean — complete, consistent, and unambiguous
- The round-trip for I7 (Pattern Library) is the most sophisticated improvement: production → LESSONS.md → next drop → better behavior. All four phases are correctly specified
- White Pre-Check (I4) correctly positions itself between Codebase Context (I3) and Politico, and explicitly hands off to Politico with the right scope division
- HOOK.md template coverage is excellent — every major drop template instruction has a corresponding section

**Ready to run SWE-bench**: Yes, with P1 fixes (I5 reaping mode gap + test template). The P1 fixes are small (3–4 lines of text changes). Estimated fix time: 30 minutes. The protocol as written would produce correct behavior on the vast majority of SWE-bench tasks — the gaps are in edge-case modes (reaping mode) and optional features (contract test generation when no test infrastructure exists).

---

*H1 — Protocol Validation Auditor, swe-bench-prep-0401, 2026-03-31*
