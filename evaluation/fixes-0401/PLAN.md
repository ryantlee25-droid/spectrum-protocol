# PLAN: Tool Fixes and Speed Optimizations
**Date**: 2026-03-31
**Scope**: High-severity correctness fixes (tools-audit.md) + top-3 speed fixes (speed-audit.md)
**Mode**: 4-Howler parallel (all independent)

---

## Background

Yesterday's audit identified 12 High findings across the tool suite. This plan addresses:
- **H1 findings (3)**: codebase_index.py — dead regex, missing relative imports, O(N) tree walk
- **H2 findings (1)**: seam_check.py — substring false positives in `_keyword_match`
- **H3 findings (4)**: test_impact_map.py — false-positive matching + missing content cache; verify_postconditions.py — repeated tree walks
- **Speed (3)**: SPECTRUM-OPS.md — parallelize White+Politico, per-Howler gate trigger, parallelize muster reads

All four Howlers are purely independent: H1/H2/H3 touch different files, H4 touches only SPECTRUM-OPS.md. No seams, no shared types.

---

## Howlers

### H1 — Fix `codebase_index.py` (3 High findings)

**File**: `/Users/ryan/spectrum-protocol/tools/codebase_index.py`

**Findings to fix**:

**1.1 — Dead code: `RE_TS_IMPORT` (malformed regex)**
- Lines 61-64: `RE_TS_IMPORT` has an empty alternation branch that would match bare string literals anywhere. It is never called in `extract_imports_ts` (only `RE_TS_IMPORT_FROM`, `RE_TS_REQUIRE`, `RE_TS_DYNAMIC_IMPORT` are used).
- Fix: Delete the `RE_TS_IMPORT` constant entirely (lines 61-64). Add a comment above `RE_TS_IMPORT_FROM` noting it is the active TS import pattern.

**1.2 — Python relative imports missed**
- Line 73: `RE_PY_FROM_IMPORT = re.compile(r"""^from\s+([\w.]+)\s+import""", re.MULTILINE)`
- The `[\w.]+` character class does not match a leading dot, so `from .models import User` and `from ..utils import helper` are silently dropped.
- Fix: Change the pattern to `r"""^from\s+(\.?\.?[\w.]*)\s+import"""`. This captures an optional leading one or two dots (covers relative and parent-relative imports). Keep `re.MULTILINE`.
- Also update `RE_PY_IMPORT` line 72 — it is fine as-is (`import foo`) but add a comment clarifying it does not handle relative imports (relative imports always use `from`, never bare `import`).

**1.8 — O(N) full project walk for `imported_by`**
- Lines 601-618: `build_import_graph` iterates over every file in `file_index` (the entire project) to find who imports the target files. For a 10K-file project this reads every source file even when only 3 targets are specified.
- Fix: Replace the full-scan loop with a candidate-filter heuristic before reading content. For each file in `file_index`, skip it if none of the target basenames appear as a substring in `rel_path` AND none of the target stems appear in the filename. Only fall back to reading content for candidate files. This is not a perfect filter (some importers won't match by path), so after the path-based filter, do a second pass reading only `rel_path`s that did NOT already match via the path heuristic, but limit that second pass to files in the same directory tree as any target (i.e., share a common path prefix up to 2 levels).
  - Concretely: build a set `target_stems = {Path(t).stem for t in target_files}`. Before `content = abs_path.read_text(...)`, check `if not any(stem in rel_path for stem in target_stems): continue`. This eliminates most irrelevant files cheaply. Note in a comment that this heuristic may miss importers in unrelated directories — document the tradeoff.
  - Alternative (simpler and more correct): cache `file_index` content as a dict `content_cache: Dict[str, str]` built by reading all files once, then reuse it for both the `imports_of` loop and the `imported_by` loop. This changes the complexity from 2-pass to 1-pass (read each file once instead of potentially reading target files twice). Implement this cache approach instead of the heuristic filter, since caching is a net correctness improvement with zero false-negative risk.

**Implementation order within H1**: Remove RE_TS_IMPORT first (no deps), then fix RE_PY_FROM_IMPORT, then add content cache. Run the existing test suite (if any) and manually verify with a Python file containing `from .models import Foo`.

---

### H2 — Fix `seam_check.py` (1 High finding)

**File**: `/Users/ryan/spectrum-protocol/tools/seam_check.py`

**Finding to fix**:

**2.1 — `_keyword_match` substring false positives**
- Lines 290-297: `_keyword_match` uses `token.lower() in search_corpus.lower()` with a minimum token length of 3 characters. Tokens like "api", "get", "set", "src", "lib" match everywhere, producing spurious CONFIRMED seam statuses.
- Fix in two parts:
  1. **Raise minimum token length to 5**. Change `if len(t) >= 3` to `if len(t) >= 5`. This alone eliminates the worst false positives ("api", "get", "set").
  2. **Require word-boundary match**. Replace the substring check with a regex word-boundary check: `re.search(r'\b' + re.escape(token.lower()) + r'\b', search_corpus.lower())`. This prevents "auth" from matching "authorization" and "log" from matching "dialog".
  3. **Also fix finding 2.3** (related false positive in `check_seams`): Line 345-346 uses `where.lower() in f.lower()` for file matching. Replace with path-component matching: `any(component == where.lower() for component in Path(f.lower()).parts)` or suffix matching `f.lower().endswith(where.lower())`. This prevents `where: "auth"` from matching `src/authorization/oauth.ts`.

**Note on 2.3**: Although 2.3 is Medium severity, it is in the same function as 2.1 and the fix is a 2-line change. Include it in H2 to avoid a follow-up touch to the same file.

**Acceptance criteria**: After the fix, a seam with `what: "api response handler"` should NOT produce a CONFIRMED match against a rider whose files include `src/capabilities/oauth.ts` (currently it would match on "api").

---

### H3 — Fix `test_impact_map.py` + `verify_postconditions.py` (4 High findings)

**Files**:
- `/Users/ryan/spectrum-protocol/tools/test_impact_map.py`
- `/Users/ryan/spectrum-protocol/tools/verify_postconditions.py`

**Findings to fix**:

**3.1 / 3.2 — False positives in `find_by_import` (test_impact_map.py)**
- Line 148-168: The primary pattern matches `(?:import|require|from)\s+[^\n]*` followed by the stem — this is already import-context-aware and correct.
- The problem is the **fallback** on lines 164-168: `if len(token) >= 3 and token in content`. This is a raw substring scan of the entire file, not scoped to import lines. A file named `utils.py` (stem="utils") would match any test file mentioning "utils" anywhere.
- Fix: Remove the fallback substring match entirely. The primary regex pattern (import-context search) is sufficient for the cases the fallback was meant to handle. The path fragment token (e.g., "auth/login") already provides the secondary match. Document in a comment that false negatives are preferred over false positives for this tool.
- If the path fragment `path_fragment_no_ext` is also used in the fallback, keep it only for the primary import-context regex, not as a raw substring.

**3.6 — Test file contents read once per source file (test_impact_map.py)**
- Lines 154-168: `find_by_import` reads every test file's content inside the loop over `source_files`. If there are 50 source files and 500 test files, this is 25,000 file reads.
- Fix: In `build_impact_map` (line 175), read all test file contents once into a dict `test_content_cache: dict[Path, str]` before the source file loop. Pass this cache into `find_by_import` (add parameter `content_cache: dict[Path, str] | None = None`). Inside `find_by_import`, use `content_cache[tf]` instead of `tf.read_text(...)`. If `content_cache` is None, fall back to reading. This is a backward-compatible change.

**4.1 / 4.8 — Repeated full tree walks (verify_postconditions.py)**
- `_find_export`, `_find_function_signature`, `_find_type_member`, and `_check_import_violation` each call `_walk_source_files(root)`, which is a fresh `os.walk` each time. For a contract with 15 postconditions, this means up to 15 full tree traversals.
- Fix: Add a module-level (or function-local) file cache. Introduce `_build_file_cache(root: Path, extensions: set[str] | None = None) -> dict[str, str]` that walks once and returns `{relative_path: content}`. Call this once at the top of `classify_and_verify` (or `verify_contract`) and pass the cache down to all `_find_*` helpers. Each helper checks the cache dict instead of calling `_walk_source_files`.
  - `_walk_source_files` stays as-is for callers that need it, but the main verification flow uses the cache.
  - Use lazy content loading: build a `dict[str, Path]` (path index) in one pass, then load content on demand with `lru_cache` or a simple `dict[str, str]` populated on first access per file.
  - Simpler approach: build `file_index: dict[str, str]` (rel_path → content) eagerly at the start of verification, since all postconditions will read most files anyway. For contracts with few postconditions vs large codebases, a lazy dict is better — implement lazy: `file_index: dict[str, str] = {}` populated on first read per path.

**Implementation order within H3**: Fix test_impact_map.py first (remove fallback, add cache), then fix verify_postconditions.py (add lazy file cache). These are independent files with no shared state.

---

### H4 — Speed fixes in `SPECTRUM-OPS.md`

**File**: `/Users/ryan/.claude/SPECTRUM-OPS.md`

**Three changes, all in Phase 1 (Muster) and Phase 2 (Proving)**:

**S1 — Parallelize White Pre-Check and Politico**
- Currently: White Pre-Check (step 11) runs and Gold patches CONTRACT.md, then Politico (step 14) runs. Sequential: ~7-9 min combined.
- Fix: After Gold writes CONTRACT.md (step 10), drop **both White Pre-Check and Politico simultaneously** in a single message. Gold waits for both reports before taking action:
  - White findings → patch CONTRACT.md factual issues
  - Politico findings → address decomposition blockers
  - If White patches change the contract materially, note this in the Politico response (Politico reviewed a slightly earlier version — acceptable, since Politico focuses on decomposition logic, not file existence).
- SPECTRUM-OPS.md already states: "the White Pre-Check has already validated factual accuracy... Your role is adversarial review of the decomposition logic and interface design, not re-checking file existence." This confirms the two reviews are orthogonal.
- Change to apply in SPECTRUM-OPS.md: Merge steps 11 and 14 into a single step. Update the muster checklist to reflect parallel completion.

**S2 — Per-Howler quality gates on completion (do not batch)**
- Currently: The protocol implies quality gates run after all Howlers complete (Pax follows all completions). For staggered Howler completion this wastes 8-15 minutes.
- Fix: Add an explicit rule to Phase 2 (The Drop / Quality Gate section): "Drop the triple quality gate for each Howler immediately upon that Howler's completion. Do not wait for other Howlers to finish. PRs may be opened while other Howlers are still running, provided PAX has not started. PAX begins only after the last Howler completes (or fails)."
- This is a clarification, not a redesign — the protocol does not currently block this, it just doesn't state it.
- Add this as a bolded rule in the Quality Gate subsection and in the Rules list at the bottom.

**S3 — Parallelize muster reads (LESSONS.md + ENTITIES.md + ARCHITECTURE.md)**
- Currently: Steps 3 (read LESSONS.md + ENTITIES.md) and 6 (update ARCHITECTURE.md) are listed sequentially. In practice Gold reads them in the order listed.
- Fix: Add an explicit instruction at the top of the muster step list: "Steps 3 and 6 are independent. Initiate all three reads (LESSONS.md, ENTITIES.md, ARCHITECTURE.md) in parallel at muster start before beginning PLAN.md validation." Reorder steps 3 and 6 into a single parallel step or add a parenthetical "(parallel with step 3)" to step 6.
- Savings: ~1-2 min per muster, compounded across every spectrum run.

**Implementation**: All three S1/S2/S3 changes are edits to prose in SPECTRUM-OPS.md. No code changes. Edit the file in-place; do not rewrite sections wholesale — targeted insertions/modifications only.

---

## File Ownership Matrix

| File | Howler | Action |
|------|--------|--------|
| `/Users/ryan/spectrum-protocol/tools/codebase_index.py` | H1 | MODIFIES |
| `/Users/ryan/spectrum-protocol/tools/seam_check.py` | H2 | MODIFIES |
| `/Users/ryan/spectrum-protocol/tools/test_impact_map.py` | H3 | MODIFIES |
| `/Users/ryan/spectrum-protocol/tools/verify_postconditions.py` | H3 | MODIFIES |
| `/Users/ryan/.claude/SPECTRUM-OPS.md` | H4 | MODIFIES |

No file is owned by more than one Howler.

---

## DAG

```
H1 ─┐
H2 ─┼─ (all independent, no edges)
H3 ─┤
H4 ─┘
```

All four Howlers are DAG root nodes with no dependencies. Drop all four simultaneously after approval.

---

## Effort Estimates

| Howler | Effort | Serial Risk | Notes |
|--------|--------|-------------|-------|
| H1 | M | no | 3 targeted edits; content cache is the most involved |
| H2 | S | no | 2 targeted edits + the 2.3 bonus fix |
| H3 | M | no | 2 files; cache plumbing in test_impact_map; lazy cache in verify_postconditions |
| H4 | S | no | Prose edits only; no code |

---

## Acceptance Criteria

**H1**:
- `RE_TS_IMPORT` is absent from the file
- `RE_PY_FROM_IMPORT` matches `from .models import User` and `from ..utils import helper`
- `build_import_graph` reads each source file at most once (content cache in place)

**H2**:
- `_keyword_match` rejects tokens shorter than 5 characters
- `_keyword_match` uses `re.search(r'\b...\b', ...)` instead of `in`
- `check_seams` file matching uses path-component or suffix check, not substring

**H3**:
- `find_by_import` has no fallback raw substring match
- `build_impact_map` builds a content cache before the source file loop; `find_by_import` accepts and uses it
- `verify_postconditions.py` walks the file tree once per verification run, not once per postcondition

**H4**:
- SPECTRUM-OPS.md states White Pre-Check and Politico are dropped simultaneously after CONTRACT.md is written
- SPECTRUM-OPS.md has an explicit rule that quality gates trigger per Howler on completion, not after all complete
- SPECTRUM-OPS.md states LESSONS.md, ENTITIES.md, and ARCHITECTURE.md reads are initiated in parallel at muster start

---

## What Is Out of Scope

- Medium and Low severity findings from both audits
- Cross-cutting `tools/_common.py` extraction (X.5 — nice to have, not High)
- Unified `SKIP_DIRS` constant (X.4 — Medium)
- Binary file detection (X.3 — Medium)
- `swe_bench/` tools (no High findings)
- Speed optimizations P2 and below (pre-generate prompts, Micro mode, HOWLER-OPS.md by path, etc.)
- `_detect_naming_conventions` crash on empty stem (1.5 — Medium, not High; audit called it P1/fix soon, but the task brief scopes to High only)
