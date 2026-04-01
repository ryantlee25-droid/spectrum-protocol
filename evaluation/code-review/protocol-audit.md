# Spectrum Protocol Audit Report

**Auditor**: Claude Opus 4.6 (protocol design review)
**Date**: 2026-03-31
**Files Reviewed**:
- `spectrum/CLAUDE.md` (316 lines)
- `spectrum/SPECTRUM-OPS.md` (~798 lines)
- `spectrum/SPECTRUM.md` (~1700 lines)

**Coherence Score: 6.5 / 10**

The protocol is functionally complete and internally well-reasoned, but the three-file
architecture has accumulated significant drift after rapid iterative changes. A Gold agent
following all three files simultaneously would encounter contradictions that require
judgment calls the documents don't address.

---

## 1. Consistency Findings

### 1.1 Gold Model Assignment -- CRITICAL

| File | Gold Model |
|------|-----------|
| CLAUDE.md (Agent Roster, line 10) | **Sonnet** |
| CLAUDE.md (Model Assignments table, line 277) | **Sonnet** (with eval rationale) |
| SPECTRUM-OPS.md (Roles table, line 11) | **Sonnet** |
| SPECTRUM.md (Roles table, line 15) | **Sonnet** |
| User's global CLAUDE.md (system prompt) | **Opus** |

**Severity: HIGH.** The user's global CLAUDE.md (injected via system prompt) assigns Gold
to Opus with a clear rationale ("Hardest cognitive work... Sonnet cuts corners on
integration"). The spectrum-protocol CLAUDE.md assigns Gold to Sonnet, citing a gold-eval
result (0.94 composite at 91% cost reduction) with a caveat about Pax over-flagging. These
directly contradict each other. A Gold agent would not know which model it should be
running on. The CLAUDE.md note about Pax over-flagging is the only place that acknowledges
the downgrade risk.

**Fix**: Reconcile the two CLAUDE.md files. Either the global CLAUDE.md should be updated
to reflect the Sonnet decision (with the Pax caveat), or the spectrum-protocol CLAUDE.md
should be reverted to Opus. The current state where both are active is a contradiction.

### 1.2 Phase Numbering Divergence -- HIGH

The three files use inconsistent phase numbering:

| Concept | CLAUDE.md | SPECTRUM-OPS.md | SPECTRUM.md |
|---------|-----------|-----------------|-------------|
| Muster | Phase 1 | Phase 1 | Phase 1 |
| Drop | Phase 2 | Phase 2 | Phase 2 |
| Quality Gate (Proving) | Phase 3 | (within Phase 2 template) | Phase 2 (section 2.5) |
| Failure/Recovery | Phase 4 (The Forge) | Phase 3 (The Forge) | Phase 3 (The Forge) |
| Pax | Phase 5 | Phase 4 (Pax) | Phase 4 (Pax) |
| Merge | (within Phase 5) | Phase 5 (Merge) | Phase 5 (Merge) |
| Triumph | Phase 6 | Phase 6 | Phase 6 |
| Obsidian | (within Phase 6) | (within Phase 6) | Phase 6.25 |
| Learning | (within Phase 6) | (within Phase 6) | Phase 6.5 |

**Severity: HIGH.** CLAUDE.md calls the failure recovery phase "Phase 4" and Pax "Phase 5",
while OPS and SPECTRUM call them "Phase 3" and "Phase 4" respectively. CLAUDE.md has "The
Proving" as Phase 3, but OPS folds the quality gate into the Howler drop template (Phase 2
territory). If Gold references "Phase 4" in conversation, it could mean either Forge or Pax
depending on which document it last read.

**Fix**: Adopt one numbering scheme across all three files. SPECTRUM.md's numbering (1-6
with 6.25/6.5 sub-phases) is the most granular and should be canonical. CLAUDE.md and OPS
should match it exactly.

### 1.3 CHECKPOINT.json Schema Divergence -- MEDIUM

| Field | CLAUDE.md | SPECTRUM-OPS.md | SPECTRUM.md |
|-------|-----------|-----------------|-------------|
| Valid phases | `planning`, `approved`, `dispatching`, `running`, `integrating`, `merging`, `complete` | Same as CLAUDE.md | `planning`, `muster`, `approved`, `dispatch`, `integrating`, `merging`, `complete` |
| Valid howler statuses | `pending`, `dispatching`, `running`, `blocked`, `complete`, `failed`, `auto-skipped` | Same (explicit list at line 142) | `pending`, `dispatching`, `in_progress`, `blocked`, `complete`, `failed`, `auto-skipped` |
| Valid modes | `full`, `reaping` | `full`, `reaping` | `full`, `light` |
| Howlers field type | Array of objects | Array of objects | Object (dict keyed by name) |

**Severity: MEDIUM.** Three separate discrepancies:
1. Phase enum: `running` vs `dispatch`, and SPECTRUM.md adds `muster` but drops `running`.
2. Status enum: `running` (CLAUDE.md/OPS) vs `in_progress` (SPECTRUM.md).
3. Mode enum: `reaping` (CLAUDE.md/OPS) vs `light` (SPECTRUM.md) -- "light" is an older
   term that predates the reaping/nano mode terminology.
4. Structure: CLAUDE.md/OPS use an array; SPECTRUM.md uses a dict.

**Fix**: SPECTRUM-OPS.md has the most explicit schema (lines 123-143) -- adopt it as
canonical and update SPECTRUM.md to match. Replace `light` with `reaping`/`nano`, replace
`in_progress` with `running`, add `nano` to valid modes.

### 1.4 Muster Step Count -- MEDIUM

| File | Muster Steps |
|------|-------------|
| CLAUDE.md | 17 steps (1-17) |
| SPECTRUM-OPS.md | 16 steps (1-16, then worktree post-approval) |
| SPECTRUM.md | Sections 1.1-1.5 (conceptual, not numbered 1-17) |

CLAUDE.md has the most granular numbered list. OPS mostly matches but counts differently:
- CLAUDE.md step 5 ("Evaluate scale") does not appear in the OPS numbered steps -- it is
  in the OPS activation section instead.
- OPS step 5 is "Evaluate scale" but CLAUDE.md step 5 is "Update ARCHITECTURE.md".
  Actually, OPS step 5 IS "Evaluate scale" (line 41) while CLAUDE.md jumps from step 4
  (Validate PLAN.md) directly to step 5 (Update ARCHITECTURE.md), omitting scale
  evaluation from the numbered steps.

Wait -- re-reading more carefully: OPS step 5 is "Evaluate scale: 3+ tasks = Spectrum,
2 = consider sequential, 1 = single-agent". CLAUDE.md has no equivalent numbered step;
CLAUDE.md goes from step 4 (Validate PLAN.md) to step 5 (Update ARCHITECTURE.md).

**Severity: MEDIUM.** The scale evaluation is in OPS but not in CLAUDE.md's muster
steps. An agent reading only CLAUDE.md would skip the scale evaluation gate.

**Fix**: Add scale evaluation to CLAUDE.md's muster steps (between steps 4 and 5),
or explicitly note that it is handled by activation criteria and need not repeat in muster.

### 1.5 Violet Phase Labeling -- LOW

| File | Violet Phase Label |
|------|--------------------|
| CLAUDE.md line 6 | "Optional Phase 0.5" (agent roster) |
| CLAUDE.md line 71 | "Optional Phase 0.5" (muster step 6) |
| CLAUDE.md line 97 | "Phase 1.5 -- The Passage" (Politico, step 13) |
| SPECTRUM-OPS.md line 43 | "Phase 1.5" (for Violet) |
| SPECTRUM-OPS.md line 109 | "Phase 1.5: The Passage" (for Politico) |

**Severity: LOW.** OPS calls Violet's phase "Phase 1.5" (line 43: "run Phase 1.5 ->
DESIGN.md") while CLAUDE.md calls it "Phase 0.5". Then the Politico review is ALSO called
"Phase 1.5" in both files. Two different things share the "Phase 1.5" label in OPS.

**Fix**: Standardize Violet as "Phase 0.5" everywhere (it runs optionally before muster
proper). Keep Politico as "Phase 1.5" since it runs within muster.

---

## 2. Completeness Findings

### 2.1 Seven Accuracy Improvements -- Coverage Check

The accuracy improvements referenced across the protocol are:

| Improvement | CLAUDE.md | OPS | SPECTRUM.md |
|------------|-----------|-----|-------------|
| Codebase context in CONTRACT.md | Step 9 (line 81-82) | Step 10 (lines 51-58) | Not present (1.3 has no codebase context) |
| White Pre-Check | Step 10 (line 86-88) | Step 11 (lines 62-77) | Not present |
| Contract-to-test generation | Step 11 (lines 89-95) | Step 12 (lines 78-107) | Not present |
| Issue re-read | Phase 2 Howler rules (line 175-176) | Drop template step 9 (lines 451-458) | Not present |
| Revision pass | Phase 2 Howler rules (line 177-178) | Drop template step 10 (lines 459-466) | Not present |
| Test impact map | Step 9 in CONTRACT.md (line 85) | Step 10 in CONTRACT.md (line 61) | Not present |
| Known Failure Patterns injection | Step 3 (line 68) | Step 3 (line 39) | Not present |

**Severity: HIGH.** None of the seven accuracy improvements appear in SPECTRUM.md. The
full spec (SPECTRUM.md) is the deep reference document, yet it lacks all of the accuracy
enhancements that CLAUDE.md and OPS have adopted. Anyone reading SPECTRUM.md as the
authoritative reference would implement a protocol missing these features.

**Fix**: Port all seven accuracy improvements into SPECTRUM.md's relevant sections (1.3
for contract enhancements, 2.1 for Howler template updates, 6.5 for failure pattern
extraction).

### 2.2 Nano Mode -- Coverage Check

| File | Nano Mode Documented? |
|------|-----------------------|
| CLAUDE.md | Yes (lines 133-152) |
| SPECTRUM-OPS.md | Yes (lines 245-281) |
| SPECTRUM.md | Yes (lines 69-74, brief) |

All three files document nano mode. SPECTRUM.md has only a brief mention with a forward
reference to OPS. This is acceptable for the reference hierarchy (OPS is the operational
manual, SPECTRUM.md is deep spec).

**Severity: NONE.** Consistent.

### 2.3 Multi-Candidate Mode -- Coverage Check

| File | Multi-Candidate Mode? |
|------|-----------------------|
| CLAUDE.md | Yes (lines 154-157, brief) |
| SPECTRUM-OPS.md | Yes (lines 298-318, full) |
| SPECTRUM.md | Not present |

**Severity: LOW.** Multi-candidate mode is an optimization for SWE-bench, not core
protocol. Its absence from SPECTRUM.md is acceptable, but a forward reference would help.

### 2.4 SWE-bench Mode -- Coverage Check

| File | SWE-bench Mode? |
|------|-----------------|
| CLAUDE.md | Not present |
| SPECTRUM-OPS.md | Yes (lines 285-295) |
| SPECTRUM.md | Not present |

**Severity: LOW.** SWE-bench mode is documented only in OPS. This is fine for an
operational optimization, but CLAUDE.md references `examples/mini-CONTRACT.md` nowhere.

### 2.5 Status Roster -- Coverage Check

| File | Status Roster? |
|------|---------------|
| CLAUDE.md | Yes (lines 158-160, brief with forward ref) |
| SPECTRUM-OPS.md | Yes (lines 322-363, full format) |
| SPECTRUM.md | Yes (lines 479-513, full format) |

**Severity: NONE.** Consistently documented across all three files.

### 2.6 Missing Tool References

OPS references these tools:
- `tools/test_impact_map.py` (line 61) -- EXISTS at `/Users/ryan/spectrum-protocol/tools/`
- `tools/codebase_index.py` (line 54) -- EXISTS
- `tools/verify_postconditions.py` (OPS drop template line 448) -- EXISTS
- `~/.claude/hooks/seam_check.py` (OPS Pax, line 647) -- EXISTS

SPECTRUM.md references none of these tools -- it uses Gold's manual judgment for the same
tasks.

**Severity: LOW.** Tool references are operational details appropriate for OPS only.

### 2.7 DESIGN.md (Violet Output) -- Missing from Directory Listing

OPS directory structure (line 792) lists `DESIGN.md`. SPECTRUM.md directory structure
(line 1631) does not. CLAUDE.md does not have a directory structure section.

Actually, re-checking: OPS line 792 does list DESIGN.md. SPECTRUM.md line 1631 also lists
it. This is consistent.

**Severity: NONE.**

---

## 3. Instruction Quality Findings

### 3.1 Could Gold Follow Muster Without Ambiguity?

**Verdict: Mostly yes, with caveats.**

The CLAUDE.md muster steps (1-17) are the most prescriptive and form a clear checklist.
The OPS muster steps (1-16 plus post-approval) are nearly identical but have the scale
evaluation step that CLAUDE.md lacks (finding 1.4).

**Ambiguities remaining:**
- Step ordering for TypeScript setup: CLAUDE.md says step 12 is `convoy-contracts.d.ts`,
  OPS says step 13 (because OPS has an extra step 5 for scale evaluation). Gold would need
  to reconcile these numberings.
- When to use `tools/codebase_index.py` vs manual file reading for codebase context: OPS
  says "MAY use" (line 54) -- this is appropriately optional.
- The muster checklist in OPS (lines 146-162) is comprehensive and would catch omissions.
  SPECTRUM.md's checklist (lines 440-453) is shorter and misses: test impact map, codebase
  context, White Pre-Check, and contract test stubs.

### 3.2 Could a Howler Follow the Drop Template Top-to-Bottom?

**Verdict: Yes -- the OPS drop template (lines 392-482) is the strongest artifact in the
protocol.**

The 15-step instruction sequence (0-14) is clear, ordered, and actionable. Each step has
an explicit trigger and completion criterion. The REFLEXION check (step 5), SCOPE ALIGNMENT
CHECK (step 6), and COMPLETION VERIFICATION (step 8) are well-placed interrupts.

**One issue:** Step numbering jumps. OPS template goes 0-14 (15 steps), but SPECTRUM.md
template goes 0-12 (13 steps). The two extra steps in OPS are:
- Step 9: ISSUE RE-READ (accuracy improvement)
- Step 10: REVISION PASS (accuracy improvement)

SPECTRUM.md's template (lines 535-594) lacks these steps, going directly from completion
verification (step 8) to quality gate (step 9). A Howler reading SPECTRUM.md as reference
would miss the issue re-read and revision pass.

### 3.3 Edge Case Handling

| Edge Case | Handled? | Where? |
|-----------|----------|--------|
| Reaping mode | Yes | All three files |
| Nano mode | Yes | CLAUDE.md + OPS (full), SPECTRUM.md (brief) |
| Doc-only spectrum | Partially | Skip rules scattered: contract tests (OPS line 83), convoy-contracts (CLAUDE.md line 96), /diff-review (OPS line 577) |
| No-test projects | Partially | OPS drop template line 443-444: "Skip if dependencies not installed" |
| TypeScript-only features | Yes | Clearly gated with "TypeScript spectrum only" |
| Python projects | Partially | Contract tests mention `.py` files (OPS line 78) but the example is TypeScript only |

**Severity: LOW.** Edge cases are handled but rules are scattered. A consolidated
"skip matrix" (what to skip per mode/project-type) would reduce cognitive load.

---

## 4. Bloat Assessment

### 4.1 Mode Count

| Mode | Muster Time | Howler Limit | Key Difference |
|------|-------------|-------------|----------------|
| Full | ~8 min | 8 | Everything |
| Reaping | ~3 min | 3-4 | No DbC, no Politico, no ARCHITECTURE.md |
| Nano | ~1 min | 2-3 | No CONTRACT.md, no quality gates, auto-approve |
| SWE-bench | ~2 min | 1 | mini-CONTRACT.md template |
| Multi-candidate | N/A | 1 (N copies) | Selection by test pass rate |

**5 modes.** This is at the edge of manageable. The nano-to-reaping-to-full continuum is
well-motivated, but SWE-bench and multi-candidate are orthogonal concerns that could be
documented separately.

### 4.2 Muster Step Count

CLAUDE.md: 17 numbered steps + post-approval worktree creation + 14-item checklist.
That is **31 discrete items** Gold must track during muster.

OPS: 16 numbered steps + worktree + 14-item checklist = **30 items**.

This is heavy but justified -- each step addresses a real failure mode observed in
production (the lessons files confirm this). The checklist is the right mitigation for
step count: it serves as a verification pass after the steps.

### 4.3 Howler Instruction Count

OPS drop template: 15 instructions (0-14) + 4 sections of context (WORKTREE NOTE,
DISCOVERY RELAY, KNOWN RISKS, CONTRACT reference).

SPECTRUM.md drop template: 13 instructions (0-12) + 3 sections of context.

**Recommendation:** The OPS template is the right size. The SPECTRUM.md template should
be updated to match. 15 instructions is near the cognitive limit for a single prompt
block, but the REFLEXION and SCOPE ALIGNMENT checks act as built-in pauses that prevent
runaway execution.

### 4.4 Quality Gate Count

Per Howler:
1. Reflexion check (every 5 file writes)
2. Scope alignment check (every 20 tool calls)
3. Completion verification (mechanical: ls, git diff, tsc, tests)
4. Contract test run
5. Postcondition verification (`verify_postconditions.py`)
6. Issue re-read
7. Revision pass (up to 2)
8. White review
9. Gray test run
10. /diff-review security scan

**10 quality gates per Howler.** Items 1-2 are lightweight (re-read + one-line log).
Items 3-7 are the Howler's self-verification. Items 8-10 are the external triple gate.

This is a lot, but items 4-5 (contract tests, postcondition verification) overlap
significantly. They both verify CONTRACT.md postconditions -- one via test stubs, one via
a Python script.

**Recommendation: MEDIUM priority.** Consider merging contract tests and postcondition
verification into a single step. Running both is redundant unless they check different
things (the docs don't clarify how they differ).

### 4.5 Redundant Checks

| Check A | Check B | Overlap |
|---------|---------|---------|
| Contract test stubs (step 12 of muster, run by Howler) | `verify_postconditions.py` (Howler completion) | Both verify CONTRACT.md postconditions |
| White Pre-Check (muster step 11) | Politico (muster step 14) | White checks factual accuracy; Politico checks decomposition logic. Distinct but adjacent -- could be parallel |
| Independent validation (Pax step 1) | Seam check (Pax step 2) | Independent validation reads files; seam check cross-references YAML. Distinct |

**Recommendation:** White Pre-Check and Politico could run in parallel (both read
CONTRACT.md, neither modifies it). This would save ~2 min in full muster. The contract
test / postcondition verification overlap should be resolved by defining their distinct
scopes.

---

## 5. Cross-Reference Integrity

### 5.1 Step Number References

OPS Politico prompt (line 117): "the White Pre-Check (step 11) has already validated
factual accuracy." This reference is correct -- OPS step 11 is the White Pre-Check.
If OPS steps are renumbered, this reference would break.

**Severity: LOW.** Currently correct, but fragile. Consider using step names instead of
numbers in cross-references.

### 5.2 File Path References

| Reference | Location | Exists? |
|-----------|----------|---------|
| `tools/test_impact_map.py` | OPS line 61, CLAUDE.md line 85 | YES |
| `tools/codebase_index.py` | OPS line 54 | YES |
| `tools/verify_postconditions.py` | OPS drop template line 448 | YES |
| `~/.claude/hooks/seam_check.py` | OPS line 647 | YES |
| `examples/mini-CONTRACT.md` | OPS line 287 | YES |
| `evaluation/swe-bench-prep/pipeline-design.md` | OPS line 293 | YES |
| `~/.claude/AGENTS.md` | CLAUDE.md line 23, SPECTRUM.md line 33 | Not verified (user home dir) |
| `~/.claude/SPECTRUM-OPS.md` | CLAUDE.md line 48 | Not verified (user home dir) |
| `~/.claude/SPECTRUM.md` | CLAUDE.md line 49 | Not verified (user home dir) |

**Severity: NONE for project-local files.** All tool and example references resolve. The
`~/.claude/` references are deployment-specific and cannot be verified from the project
repo alone.

### 5.3 Agent Name Pluralization

The spectrum-protocol CLAUDE.md consistently uses plural forms with the `s` suffix in the
Model Assignments table: Golds, Blues, Whites, Grays, Oranges, Coppers, Obsidians, Browns,
Violets, Politicos. The Agent Roster section also uses plurals.

The user's global CLAUDE.md uses **singular** forms: Gold, Blue, White, Gray, Orange,
Copper, Obsidian, Brown, Violet, Politico.

SPECTRUM.md and OPS both use plurals in tables and mix singular/plural in prose (e.g.,
"Gold spawns a Politicos agent" at SPECTRUM.md line 408 -- note the mismatch: "a" + plural
form).

**Severity: LOW.** The plural forms in tables are the subagent_type identifiers. Prose
should use singular when referring to one instance ("a Politico", "the Gold") and plural
for the role class ("Politicos review contracts"). SPECTRUM.md line 408 says "a Politicos
agent" -- should be "a Politico agent".

### 5.4 OPS vs SPECTRUM.md Phase Naming

| Phase | OPS Name | SPECTRUM.md Name |
|-------|----------|-----------------|
| Phase 3 | "The Forge" | "The Forge" |
| Phase 4 | "Pax" | "Pax" |
| Phase 5 | "Merge" | "Merge" |
| Phase 6 | "Triumph" | "Triumph" |

**Severity: NONE.** Phase names are consistent between OPS and SPECTRUM.md.

---

## 6. Summary of Recommendations

### Critical (fix before next spectrum run)

1. **Reconcile Gold model assignment** between global CLAUDE.md (Opus) and spectrum-protocol
   CLAUDE.md (Sonnet). One must be authoritative.

2. **Unify phase numbering** across all three files. CLAUDE.md's "Phase 3: The Proving /
   Phase 4: The Forge / Phase 5: Pax" conflicts with OPS/SPECTRUM's "Phase 3: The Forge /
   Phase 4: Pax". Pick one scheme.

3. **Port accuracy improvements to SPECTRUM.md.** All seven improvements (codebase context,
   White Pre-Check, contract tests, issue re-read, revision pass, test impact map, known
   failure patterns) are missing from the deep spec.

### High (fix soon)

4. **Standardize CHECKPOINT.json schema.** Resolve the `running` vs `in_progress`,
   `reaping` vs `light`, array vs dict, and phase enum discrepancies.

5. **Align Howler drop template** between OPS (15 steps) and SPECTRUM.md (13 steps). The
   two missing steps (issue re-read, revision pass) are significant accuracy improvements.

### Medium (improve when convenient)

6. **Add scale evaluation** to CLAUDE.md's muster steps (present in OPS, absent in
   CLAUDE.md).

7. **Clarify contract test vs postcondition verification overlap.** Either merge them
   or document their distinct scopes.

8. **Run White Pre-Check and Politico in parallel** during muster to save ~2 min.

9. **Create a skip matrix** -- a single table showing what each mode (full/reaping/nano/
   SWE-bench) skips, rather than scattering skip rules across sections.

### Low (nice to have)

10. Fix "a Politicos agent" to "a Politico agent" in SPECTRUM.md line 408.

11. Use step names instead of step numbers in cross-references to prevent breakage on
    renumbering.

12. Add a forward reference in SPECTRUM.md for multi-candidate mode and SWE-bench mode.

13. Standardize Violet as "Phase 0.5" everywhere (OPS calls it "Phase 1.5" in one place).

---

## 7. Scoring Breakdown

| Dimension | Score | Notes |
|-----------|-------|-------|
| Internal consistency (within each file) | 8/10 | Each file is internally coherent |
| Cross-file consistency | 5/10 | Phase numbering, CHECKPOINT schema, model assignment diverge |
| Completeness | 7/10 | SPECTRUM.md missing 7 accuracy improvements; other coverage good |
| Instruction clarity | 8/10 | OPS drop template is excellent; muster steps are followable |
| Bloat management | 6/10 | 5 modes, 31 muster items, 10 quality gates -- justified but approaching ceiling |
| Cross-reference integrity | 8/10 | All file paths resolve; step number refs currently correct but fragile |

**Overall Coherence: 6.5 / 10**

The protocol is battle-tested and well-designed at the operational level (OPS is strong),
but the three-file architecture has accumulated enough drift that the files now partially
contradict each other. The most urgent fix is aligning phase numbers and the Gold model
assignment. After that, porting the accuracy improvements to SPECTRUM.md would bring the
deep spec up to parity with the operational manual.
