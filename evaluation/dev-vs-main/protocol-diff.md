# Spectrum Protocol: Dev vs Main — Comprehensive Diff Analysis

**Generated**: 2026-03-31
**Commits analyzed**: 19 commits (main..dev)
**Files changed**: 183 files, +37,532 / -173 lines

---

## 1. Structural Changes

### Document Line Counts

| File | Main | Dev | Delta | % Growth |
|------|------|-----|-------|----------|
| `spectrum/CLAUDE.md` | 269 | 358 | +89 | +33% |
| `spectrum/SPECTRUM-OPS.md` | 554 | 948 | +394 | +71% |
| `spectrum/SPECTRUM.md` | 2,290 | 2,406 | +116 | +5% |
| **Total** | **3,113** | **3,712** | **+599** | **+19%** |

### Protocol Modes

| Mode | Main | Dev | Notes |
|------|------|-----|-------|
| Full | Yes | Yes | Core mode, unchanged in concept |
| Reaping | Yes | Yes | Unchanged activation criteria |
| Nano | No | **Yes** | New: 2-3 Howlers, pure-create, <1 min muster, auto-approve, no quality gates |
| Multi-Candidate | No | **Yes** | New: N candidates (default 3) for accuracy-critical single-Howler tasks |
| SWE-bench | No | **Yes** | New: Uses mini-CONTRACT.md template for single-issue benchmark tasks |

**Mode count**: Main = 2, Dev = 5 (+3 modes)

### Muster Steps (CLAUDE.md Phase 1)

| Version | Steps | Notes |
|---------|-------|-------|
| Main | 15 | Steps 1-15 |
| Dev | 18 | Steps 1-18, with new steps 9 (codebase context + test impact map in CONTRACT.md), 10 (Issue Confirmation Gate), 11 (White Pre-Check), 12 (contract-to-test generation) inserted before the existing Politico/approval/checkpoint/worktree steps |

**Net new muster steps**: +3 (Issue Confirmation Gate, White Pre-Check, Contract-to-test generation)

### Howler Drop Template Instructions

| Version | Steps | Notes |
|---------|-------|-------|
| Main (OPS) | 12 | Steps 1-12 in INSTRUCTIONS block |
| Dev (OPS) | 12 + step 0 | Step 0 (read CONTRACT.md first), steps 1-12, with steps 8-10 expanded (issue re-read, revision pass, postcondition verification) |

**Effective instruction count**: Main = 12, Dev = 13 (step 0 added), but several existing steps gained sub-instructions.

### Muster Checklist Items (OPS)

| Version | Checklist items |
|---------|----------------|
| Main | 12 |
| Dev | 16 |

**New checklist items**: Test impact map, Codebase context sections, Issue Confirmation Gate, White Pre-Check, Contract test stubs.

### New Tools

| Tool | Purpose | Lines |
|------|---------|-------|
| `tools/codebase_index.py` | Extracts import graphs, function signatures, patterns per file | 801 |
| `tools/verify_postconditions.py` | Verifies CONTRACT.md postconditions against implementation | 863 |
| `tools/test_impact_map.py` | Maps which test files cover which source files | 333 |
| `tools/swe_bench/load_tasks.py` | Loads SWE-bench tasks for evaluation | 375 |
| `tools/swe_bench/emit_predictions.py` | Emits SWE-bench prediction format | 178 |
| `examples/mini-CONTRACT.md` | Minimal contract template for SWE-bench mode | 63 |

**Tool count**: Main = 1 (`seam_check.py`), Dev = 6 (+5 tools/templates)

---

## 2. Feature Inventory

### Protocol Modes (3 new)

1. **Nano Mode** — For 2-3 Howlers with obvious boundaries. Skips CONTRACT.md, Politico, quality gates, human approval, worktree pre-creation. Auto-approves and drops immediately. Escalates to reaping on any blocker. (commit `2075bb7`)

2. **Multi-Candidate Mode** — Runs N candidates (default 3) on the same single-Howler task, selects by test pass rate. For SWE-bench and production hotfixes. Cost = Nx single-Howler. (commit `f8ff355`)

3. **SWE-bench Mode** — Uses `examples/mini-CONTRACT.md` (50-100 lines) instead of full CONTRACT.md. Optimized for single-issue accuracy runs with two variants (A: mini-contract, B: 200-token task brief). (commit `f8ff355`)

### Accuracy Improvements

**I-series (improvements to information Gold gives Howlers):**

| ID | Feature | Where | Commit |
|----|---------|-------|--------|
| I1 | Codebase context per Howler in CONTRACT.md | CLAUDE.md step 9, OPS step 10 | `2f64454` |
| I2 | Test impact map per Howler | CONTRACT.md + OPS step 10 | `2f64454` |
| I3 | White Pre-Check (contract accuracy gate) | CLAUDE.md step 11, OPS step 11 | `2f64454` |
| I4 | Issue Confirmation Gate | CLAUDE.md step 10, OPS step 10.5 | `16cec93` |
| I5 | Known Failure Patterns injection from LESSONS.md | CLAUDE.md step 3, Howler template KNOWN RISKS | `733a189` |
| I6 | Contract-to-test generation (structural postconditions only) | CLAUDE.md step 12, OPS step 12 | `733a189` |
| I7 | CONTRACT.md by reference (not inlined) | Howler template, token savings note | `f8ff355` |

**A-series (improvements to Howler self-correction):**

| ID | Feature | Where | Commit |
|----|---------|-------|--------|
| A1 | Reflexion check every 5 file writes | Howler template step 5 | `2f64454` |
| A2 | Issue re-read after completion | CLAUDE.md Howler rules, OPS step 9 | `f8ff355` |
| A3 | Revision pass (max 2 attempts) | CLAUDE.md Howler rules, OPS step 10 | `733a189` |
| A4 | Postcondition verification via verify_postconditions.py | OPS step 8 | `f8ff355` |
| A5 | Contract test stubs (structural only) | OPS step 12, Howler step 8 | `733a189` |

### Speed Optimizations

| ID | Feature | Savings | Commit |
|----|---------|---------|--------|
| S1 | Parallel muster reads (LESSONS.md + ENTITIES.md + ARCHITECTURE.md + codebase_index in parallel) | ~1-2 min per muster | `3deb9f3` |
| S2 | Parallel White Pre-Check + Politico (previously sequential) | ~3-4 min per full muster | `3deb9f3` |
| S3 | Per-Howler quality gate triggering (don't wait for all Howlers) | 8-15 min on staggered 4-Howler runs | `3deb9f3` |

### Architectural Changes

1. **Gold Post-Howler Protocol** — Quality gates are now spawned by Gold as visible background agents after Howler completion, replacing the old model where Howlers self-reviewed. Howlers now signal `Status: complete` and exit; Gold coordinates White, Gray, /diff-review, and Copper. (commit `27ee789`)

2. **Visible Agent Spawning** — All agents (Obsidian, Brown, White, Gray, Copper) are spawned with `Agent(description="glyph Role -- task", run_in_background=True)` so they appear in Claude Code's sidebar. (commit `27ee789`)

3. **Gold Recovery Protocol** — New section in OPS and CLAUDE.md: on session start, Gold checks CHECKPOINT.json for incomplete spectrum runs. CHECKPOINT.json expanded with `locus_history`, `circuit_breaker_state`, `active_diagnostics`, `gold_context_snapshot`. (commit `7de81b3`)

4. **Expanded CHECKPOINT.json Schema** — Four new fields for recovery: `locus_history` (circuit breaker persistence across sessions), `circuit_breaker_state`, `active_diagnostics`, `gold_context_snapshot` (pending DAG edges, manifest/contract paths). (commit `7de81b3`)

### New Tools

| Tool | Purpose | Commit |
|------|---------|--------|
| `tools/codebase_index.py` (801 lines) | Semantic indexer: extracts import graphs, function signatures, patterns for CONTRACT.md codebase context sections | `f8ff355` |
| `tools/verify_postconditions.py` (863 lines) | Automated postcondition verification against CONTRACT.md | `f8ff355` |
| `tools/test_impact_map.py` (333 lines) | Maps source files to covering test files for targeted test runs | `2f64454` |
| `tools/swe_bench/load_tasks.py` (375 lines) | SWE-bench task loader and formatter | `f8ff355` |
| `tools/swe_bench/emit_predictions.py` (178 lines) | SWE-bench prediction output formatter | `f8ff355` |
| `examples/mini-CONTRACT.md` (63 lines) | Minimal contract template for SWE-bench/single-issue runs | `f8ff355` |

### Resilience Improvements

1. **CHECKPOINT.json expansion** — Now persists `locus_history` and `circuit_breaker_state` after every failure classification (not just phase transitions), enabling mid-spectrum session recovery.
2. **Gold recovery from session death** — Explicit recovery protocol: read CHECKPOINT.json + MANIFEST.md + all HOOK.md files to reconstruct state. Phase-aware resumption (dispatching/running/integrating/merging).
3. **Known Failure Patterns** — LESSONS.md gains a `## Known Failure Patterns` section (pattern name, trigger condition, fix). Gold injects matching patterns into Howler drop prompts as `KNOWN RISKS`.

### Naming/UX Changes

1. **Pluralized agent names** — `Gold` -> `Golds`, `Obsidian` -> `Obsidians`, `Brown` -> `Browns`, etc. throughout all three files. `subagent_type` values also pluralized (`gold` -> `golds`, `obsidian` -> `obsidians`). (commit `8b34116`)

2. **Status Roster** — New mandatory inline display Gold prints after every dispatch, completion, and phase transition. Uses glyphs (`♛`, `◎`, `»`, `✦`, `⛨`, `✧`, `▶`, `⊘`, `⌂`, `⚡`) and status symbols (`●` running, `✓` done, `✗` failed, `■` blocked, `○` pending). (commit `eeb7043`)

3. **Glyph descriptions in Roles table** — OPS and SPECTRUM.md role tables now include `Color` column with valid Claude Code palette values. (commit `771287a`)

4. **Pax severity caveat** — Gold entry in Agent Roster and Model Assignments table notes that Pax findings should be human-reviewed for severity (Sonnet tends to over-classify observations as blockers).

---

## 3. Complexity Assessment

### Protocol Document Growth

| Metric | Main | Dev | Delta |
|--------|------|-----|-------|
| Total lines (3 files) | 3,113 | 3,712 | +599 (+19%) |
| Modes | 2 | 5 | +3 |
| Muster steps (CLAUDE.md) | 15 | 18 | +3 |
| Muster checklist items (OPS) | 12 | 16 | +4 |
| Howler template steps | 12 | 13 (+ sub-steps) | +1 (+ expansions) |
| Tools | 1 | 6 | +5 |
| CHECKPOINT.json fields | ~8 | ~12 | +4 |

### Skip Conditions and Mode Exceptions

The following features have mode-specific skip conditions:

| Feature | Full | Reaping | Nano |
|---------|------|---------|------|
| CONTRACT.md | Required | Simplified | **Skipped** |
| Politico | Required | Skipped | **Skipped** |
| Issue Confirmation Gate | Required | **Skipped** | **Skipped** |
| White Pre-Check | Required | **Skipped** | **Skipped** |
| Contract-to-test generation | Required | **Skipped** | **Skipped** |
| Quality gates (White+Gray+/diff-review) | Required | Required | **Skipped** |
| Human approval gate | Required | Required | **Skipped** |
| Worktree pre-creation | Required | Required | **Skipped** |
| ARCHITECTURE.md | Required | Skipped | **Skipped** |
| Obsidian | Required | Skipped | **Skipped** |
| ENTITIES.md | Required | Skipped | **Skipped** |

**Total skip conditions across 3 modes**: ~33 (11 features x 3 modes). This is a significant cognitive load for Gold to evaluate correctly.

### Is the Complexity Justified?

**Yes, mostly.** The complexity breaks into three categories:

1. **Justified additions** (accuracy): Codebase context, test impact maps, White Pre-Check, Issue Confirmation Gate, revision passes, and contract tests all address real failure modes observed in production spectrum runs. These directly improve Howler first-pass success rates.

2. **Justified additions** (speed): Parallel muster reads, parallel White+Politico, per-Howler quality gate triggering are pure speed wins with no correctness risk.

3. **Questionable additions** (modes): Nano mode and SWE-bench mode add protocol surface area but serve narrow use cases. Multi-candidate mode is purely for benchmarks. These three modes together add ~100 lines to OPS and ~50 lines to SPECTRUM.md. The mode continuum (nano -> reaping -> full) is elegant in theory but creates a branching decision tree Gold must navigate.

---

## 4. Breaking Changes

### Agent File Renames

| Main | Dev |
|------|-----|
| `gold.md` agent file | `golds.md` (implied by `subagent_type: golds`) |
| `obsidian.md` | `obsidians.md` |
| `brown.md` | `browns.md` |
| All singular agent types | All pluralized |

**Impact**: Any existing `~/.claude/agents/*.md` files with singular names will not be detected by the pluralized `subagent_type` values. The `convoy_roles.py` role detection table also changes (`mayor` -> `golds`, `sentinel` -> `obsidians`, etc.).

### Model Changes

| Agent | Main | Dev | Impact |
|-------|------|-----|--------|
| **Gold** | **Opus** | **Sonnet** | Most significant change. Based on gold-eval-0331 (0.94 composite vs Opus 1.00, 91% cost reduction). Pax severity over-flagging noted as the one caveat. |

**All other agents**: Unchanged (Sonnet for most, Haiku for Copper/Brown).

### Step Number Shifts (CLAUDE.md Muster)

Steps 9-15 on main become steps 9-18 on dev due to three insertions:
- New step 9: Codebase context + test impact map in CONTRACT.md
- New step 10: Issue Confirmation Gate
- New step 11: White Pre-Check
- New step 12: Contract-to-test generation
- Steps 10-15 on main shift to steps 13-18 on dev

### Quality Gate Ownership Change

| Aspect | Main | Dev |
|--------|------|-----|
| Who runs quality gates | Howlers self-run White+Gray+/diff-review | Gold spawns them as visible background agents |
| Phase name | Phase 3 — The Proving | Removed as standalone phase; quality gates are now part of Phase 2 (The Drop) |
| Howler step 11-12 | Run quality gates, fix blockers, open PR | Signal completion, exit. Gold handles the rest. |

**Impact**: The phase numbering changes. Main has 6 phases (Muster, Drop, Proving, Forge, Pax, Triumph). Dev has 6 phases (Muster, Drop, Forge, Pax, Merge, Triumph) with The Proving absorbed into The Drop. Phase numbers shift: Forge goes from Phase 4 to Phase 3, Pax from Phase 5 to Phase 4, etc.

### Removed Behaviors

1. **Howler self-review** — Howlers no longer run White/Gray/diff-review themselves. They signal completion and Gold coordinates.
2. **Howler PR opening** — Howlers no longer open PRs via Copper. Gold spawns Copper after quality gates pass.
3. **Howler steps 11-14 (old template)** → replaced with step 12 (signal completion, exit).

### CHECKPOINT.json Schema Changes

New required fields: `locus_history`, `circuit_breaker_state`, `active_diagnostics`, `gold_context_snapshot`. Old CHECKPOINT.json files without these fields may fail Gold recovery logic.

---

## 5. Risk Assessment

### Biggest Risk: Gold Model Downgrade (Opus -> Sonnet)

Gold on Sonnet has a 0.94 composite score vs Opus 1.00. The 6% gap concentrates in **Pax severity classification** — Sonnet over-flags observations as blockers. In production, this means:

- Human gets more false-positive blockers in PAX-PLAN.md
- Merge process slows as human must triage over-classified findings
- The protocol notes this caveat but relies on human vigilance to catch it

**Mitigation**: The protocol explicitly states "Pax findings should be human-reviewed for severity before actioning blockers." But this shifts cognitive load to the human, partially negating the cost savings.

### Under-Tested Features

1. **Nano Mode** — No production runs documented. The auto-approve + no quality gates combination means errors in nano mode go undetected until merge. The escalation to reaping mode on any block is a safety valve, but the happy path has no review.

2. **Multi-Candidate Mode** — Designed for SWE-bench but no benchmark results in the repo. The selection algorithm (test pass rate, then fewer files, then first-to-complete) is plausible but unvalidated.

3. **New Tools** — `codebase_index.py` (801 lines), `verify_postconditions.py` (863 lines), `test_impact_map.py` (333 lines) are substantial Python tools. No test suites visible for any of them. They are in the critical path for full-mode muster.

4. **Gold Post-Howler Protocol** — The new architecture where Gold spawns quality gates as separate visible agents is a significant workflow change. If Gold's context window fills during a large spectrum, the quality gate coordination could fail silently.

5. **Gold Recovery** — CHECKPOINT.json expansion enables recovery but the recovery protocol itself has no documented test runs.

### Potential Contradictions Across 19 Commits

1. **Phase numbering inconsistency** — CLAUDE.md refers to "Phase 3 - The Forge" and "Phase 4 - Pax" (dev numbering), while SPECTRUM.md still uses "Phase 3: The Forge" at line 909 but earlier references "Phase 2: The Drop" quality gates. The Proving phase name appears in some places but not others.

2. **Howler template divergence** — SPECTRUM.md section 2.1 still contains old steps 11-14 (Howler runs quality gates, opens PR) at lines 638-644, while SPECTRUM-OPS.md and CLAUDE.md have the new Gold Post-Howler Protocol where Howlers signal completion and exit. **This is a direct contradiction** — SPECTRUM.md was not fully updated for commit `27ee789`.

3. **`subagent_type` pluralization inconsistency** — The OPS role table shows `golds`, `blues`, `whites`, etc., but the CMUX integration section in SPECTRUM.md still references `mayor`, `scout`, `inspector`, `rider` at lines 2244-2258. These appear to be the old aliases preserved for backward compatibility, but it is unclear which is authoritative for new code.

4. **Politico step numbering** — OPS step 14 says "Politico runs in parallel with White Pre-Check in step 11 -- see step 11 above" but the actual parallel spawn is in step 11. Step 14 is a placeholder pointing back, which could confuse Gold.

5. **Quality gate skip conditions** — CLAUDE.md says nano mode skips "White + Gray + /diff-review" and the OPS nano section confirms this, but the SPECTRUM.md section 2.5 (Quality Gate) does not mention nano mode exceptions at all.

### Migration Path Gaps

There is no migration guide for upgrading from main to dev. Specific gaps:

- No script to rename agent files from singular to plural
- No CHECKPOINT.json migration for the new fields
- No documentation of which `subagent_type` values changed
- The Gold model change (Opus -> Sonnet) may require updating the user's global `~/.claude/CLAUDE.md` if it hardcodes Opus for Gold

---

## Summary Table

| Dimension | Main | Dev | Assessment |
|-----------|------|-----|------------|
| Protocol modes | 2 | 5 | +3 modes, justified for SWE-bench but adds decision complexity |
| Muster steps | 15 | 18 | +3 accuracy gates, each addresses a real failure mode |
| Muster checklist items | 12 | 16 | +4, proportional to new steps |
| Howler instructions | 12 | 13+ | Expanded self-correction, justified by accuracy goals |
| Tools | 1 | 6 | +5, all untested, some in critical path |
| Line count | 3,113 | 3,712 | +19%, moderate growth |
| Gold model | Opus | Sonnet | 91% cost reduction, 6% quality gap in Pax |
| Breaking changes | -- | 5 categories | Agent renames, model change, phase renumbering, template change, CHECKPOINT schema |
| Internal contradictions | -- | 2-3 | SPECTRUM.md Howler template not updated; subagent_type dual naming |
| Test coverage | -- | 0 for new tools | High risk for 2,000+ lines of untested Python |
