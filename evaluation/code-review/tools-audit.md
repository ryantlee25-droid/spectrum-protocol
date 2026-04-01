# Spectrum Protocol Tools Audit

Auditor: Claude Opus 4.6 (1M context)
Date: 2026-03-31
Scope: 6 tool files, ~3,300 lines total

Severity scale: **Critical** (will produce wrong results or crash in normal use), **High** (wrong results in common edge cases), **Medium** (suboptimal behavior, maintainability concern), **Low** (style, minor improvement)

---

## 1. `tools/codebase_index.py` (780 lines)

### Correctness

| # | Severity | Finding |
|---|----------|---------|
| 1.1 | **High** | `RE_TS_IMPORT` (line 61-64) is malformed. The regex has an empty alternation branch (`(?:import\s+...\|)`) which means it matches bare string literals like `'react'` anywhere in the file, not just in import statements. This regex is never actually used (only `RE_TS_IMPORT_FROM`, `RE_TS_REQUIRE`, and `RE_TS_DYNAMIC_IMPORT` are called in `extract_imports_ts`), so it is dead code that could confuse maintainers. |
| 1.2 | **High** | `RE_PY_IMPORT` / `RE_PY_FROM_IMPORT` miss Python relative imports. `from .models import User` would not match because the regex requires `[\w.]+` which does not start with a dot. The leading dot in relative imports is not a word character. |
| 1.3 | **Medium** | `_extract_brace_body` (line 303) does not account for braces inside string literals or template literals. A TS file with `const x = "{"` would desync the depth counter, potentially truncating or extending the extracted body. |
| 1.4 | **Medium** | `extract_signatures_py` skips functions where `name.startswith("_")` (line 257) but this also skips dunder methods like `__call__`, `__enter__`, `__exit__` at module level. These are rare at module level but the comment says "Skip private functions" when dunders are public API. |
| 1.5 | **Medium** | `_detect_naming_conventions` (line 513) will crash with `IndexError` on an empty `stem` string (e.g., a file named `.py`). `stem[0]` and `stem[1:]` would fail. |
| 1.6 | **Low** | `RE_TS_CLASS_METHOD` (line 168) matches any indented identifier followed by parentheses. This catches `if (`, `for (`, etc. The keyword blocklist on line 351 partially mitigates this but misses `catch`, `else`, `do`, `try`, `new`, `delete`, `typeof`, `await`, `yield`. |
| 1.7 | **Low** | `iter_source_files` type hint says `"Generator"` (string) but doesn't import `Generator` from `typing` or `collections.abc`. Works at runtime but fails static type checking. |

### Performance

| # | Severity | Finding |
|---|----------|---------|
| 1.8 | **High** | `build_import_graph` (line 555) walks the entire source tree twice: once to build `file_index` (line 566), then reads every file in the project to build `imported_by` (line 602). For a 10K+ file project, this means reading every source file's content even if only 3 target files are specified. This is O(N) in project size regardless of target count. |
| 1.9 | **Medium** | Neighbor file contents are re-read in `generate_index` (line 711-718) after already being read during import graph construction. No caching layer exists. |
| 1.10 | **Medium** | `resolve_ts_import` calls `candidate.relative_to(root.resolve())` with `root.resolve()` called fresh each time instead of caching it. `Path.resolve()` involves syscalls. |

### Robustness

| # | Severity | Finding |
|---|----------|---------|
| 1.11 | **Medium** | No handling of binary files. `read_text(errors="replace")` will silently ingest binary content and produce garbage regex matches. Should check for null bytes or use a heuristic to skip binary files. |
| 1.12 | **Low** | `_detect_test_adjacency` is defined (line 521) but the paths it constructs use the relative `filepath` argument, then tries `root / t` which could produce doubled paths if `filepath` is already relative to root. The logic around `t.is_relative_to(root)` is fragile. |

### Speed Improvements

- **Cache file contents**: Read each file once and store in a `dict[str, str]`. Eliminates redundant reads for import graph + signatures + neighbor signatures.
- **Parallelize file I/O**: Use `concurrent.futures.ThreadPoolExecutor` to read files in parallel (I/O bound).
- **Limit `imported_by` scan**: Only read files that could plausibly import a target (same directory tree or share a common package prefix) rather than the entire project.
- **Pre-resolve root once**: Cache `root.resolve()` at entry point.

---

## 2. `tools/seam_check.py` (739 lines)

### Correctness

| # | Severity | Finding |
|---|----------|---------|
| 2.1 | **High** | `_keyword_match` (line 290) uses simple substring matching (`token.lower() in search_corpus.lower()`). Tokens of length 3 characters (the minimum) produce false positives constantly. For example, a seam about "API endpoint" would match any file containing "api" anywhere. This means many seams get CONFIRMED status when the evidence is spurious. |
| 2.2 | **Medium** | The YAML parser `_cast_scalar` (line 218) treats `"yes"` as `True` and `"no"` as `False`. This is YAML 1.1 behavior, deprecated in YAML 1.2. A rider named "yes" or a seam with `what: no circular imports` would be silently converted to boolean values. |
| 2.3 | **Medium** | `check_seams` (line 346) uses `where.lower() in f.lower()` for file matching. This means `where: "auth"` would match `src/authorization/oauth.ts`, producing false confirmations. Should use path-component matching or exact suffix matching. |
| 2.4 | **Low** | `import sys` appears at module level (line 17) AND conditionally inside `load_mailboxes` (line 267). The conditional import is unnecessary. |
| 2.5 | **Low** | `_parse_yaml_block` ignores lines that don't match the `^\w[\w_-]*:` pattern (line 107). This silently drops any key containing dots, colons, or starting with special characters. |

### Performance

| # | Severity | Finding |
|---|----------|---------|
| 2.6 | **Low** | All operations are O(R*S) where R = riders, S = seams. For typical convoy sizes (3-8 riders, 0-5 seams each), this is negligible. No performance concerns for expected input sizes. |

### Robustness

| # | Severity | Finding |
|---|----------|---------|
| 2.7 | **Medium** | `_md_table` (line 473) will crash with `ValueError` if `rows` is non-empty but any row has fewer elements than `headers`. The generator expression `*(len(str(r[i])) for r in rows)` would raise `IndexError`. |
| 2.8 | **Medium** | No encoding handling for non-UTF-8 mailbox files. `path.read_text(encoding="utf-8")` will raise on files with other encodings (e.g., Latin-1 from copy-paste). Should use `errors="replace"`. |
| 2.9 | **Low** | `_parse_list` assumes consistent indentation. Mixed tabs and spaces would produce incorrect list parsing. |

### Best Practices

| # | Severity | Finding |
|---|----------|---------|
| 2.10 | **Medium** | Rolling a custom YAML parser (~150 lines) is fragile and incomplete. Consider using `yaml.safe_load()` from PyYAML or `tomli`-style minimal parser. The custom parser misses: multi-line strings, flow sequences `[a, b]`, anchors/aliases, and complex keys. |
| 2.11 | **Low** | `datetime` and `timezone` are imported but `timezone` is only used for `timezone.utc`. Could use `datetime.UTC` on Python 3.11+, but current code is fine for compatibility. |

### Speed Improvements

- Already fast for expected input sizes. No meaningful optimization needed.

---

## 3. `tools/test_impact_map.py` (272 lines)

### Correctness

| # | Severity | Finding |
|---|----------|---------|
| 3.1 | **High** | `find_by_import` (line 128) uses the bare basename as search token. A file named `utils.py` would match every test file that mentions "utils" anywhere, including comments, string literals, or unrelated imports like `test_utils`. This produces massive false positives for common names. |
| 3.2 | **High** | The fallback substring match (line 165) `token in content` with `len(token) >= 3` is extremely loose. A source file `src/api.py` (stem="api") would match any test file containing the string "api" anywhere. |
| 3.3 | **Medium** | `convention_candidates` returns filename strings, but `find_by_convention` compares them against `tf.name` (line 111). This works for flat names but would miss candidates if the convention included a directory component (e.g., `__tests__/login.ts` is generated as a candidate string but never matched because `tf.name` is just `login.ts`). The `__tests__` candidate on line 96 (`stem + ext`) is just the basename, so it would match any `login.ts` in any `__tests__` directory, not specifically the one adjacent to the source. |
| 3.4 | **Medium** | `is_test_file` (line 37) doesn't recognize `conftest.py` (pytest fixture files) or `test_*.js`/`test_*.ts` (some projects use `test_` prefix for JS too). |
| 3.5 | **Low** | `find_all_test_files` returns absolute paths, but deduplication in `build_impact_map` uses `tf.resolve()` as dict key. On case-insensitive filesystems (macOS), two paths differing only in case would not be deduplicated. |

### Performance

| # | Severity | Finding |
|---|----------|---------|
| 3.6 | **High** | `find_by_import` reads every test file's content for every source file. If you have 50 source files and 500 test files, that's 25,000 file reads. The test file contents should be read once and cached. |
| 3.7 | **Medium** | `find_all_test_files` walks the entire tree. For import-based discovery, this walk is necessary, but the results should be cached if `build_impact_map` is called multiple times (e.g., from a script iterating over Howlers). |

### Robustness

| # | Severity | Finding |
|---|----------|---------|
| 3.8 | **Low** | No handling of binary files in `find_by_import`. A binary test fixture file would be read with `errors="ignore"`, producing potentially long garbage strings to search through. |
| 3.9 | **Low** | No handling of symlink loops in `os.walk`. |

### Speed Improvements

- **Cache test file contents**: Read all test files once into a dict, then search the cached content for each source file.
- **Build inverted index**: Parse imports from all test files once, build a `basename -> [test_files]` index, then do O(1) lookups per source file instead of O(T) scans.
- **Use `mmap` for large test files**: Memory-map files instead of reading full content for substring search.

---

## 4. `tools/verify_postconditions.py` (773 lines)

### Correctness

| # | Severity | Finding |
|---|----------|---------|
| 4.1 | **High** | `_find_export` (line 427) does a full project walk for every unlocated export. If a CONTRACT.md has 10 "exports X" postconditions, each triggers a full tree walk. Combined with `_find_function_signature` and `_find_type_member` which also do full walks, a contract with N postconditions triggers up to N full project traversals. |
| 4.2 | **High** | `_has_export` Python pattern (line 416) has mismatched quotes in the `__all__` regex: `['\\"]{re.escape(name)}['\\""]` has an extra `"` at the end, making the character class `['\""]` which is `['"""]` (three chars: single quote, double quote, double quote). This is benign but indicates a copy-paste error. More importantly, this regex fails for `__all__` with line breaks (multi-line lists). |
| 4.3 | **Medium** | `_check_function_signature` comparison (line 251) uses `norm_expected in norm_found or norm_found in norm_expected`. This means a postcondition expecting return type `string` would pass if the actual return type is `string | null | undefined` (substring match). This is arguably too permissive. |
| 4.4 | **Medium** | `_find_type_member` for Python (line 589) searches for the field pattern in all content after the class definition, not just the class body. If two classes exist in the same file, a field from the second class could be falsely attributed to the first. |
| 4.5 | **Medium** | `classify_and_verify` (line 114) tries classifiers in a fixed order and returns the first match. `_check_no_import` is tried first, which means a postcondition like "auth.ts exports getSession()" could potentially be misclassified if the text happens to match a no-import pattern (unlikely but possible with creative wording). |
| 4.6 | **Low** | `_check_file_exists` patterns (line 144) only match filenames with extensions (`[^\s]+\.\w+`). A postcondition about a directory existing or an extension-less file would be silently skipped. |
| 4.7 | **Low** | `_walk_source_files` (line 383) checks `any(fname.endswith(ext) for ext in extensions)` which is O(E) per file. Using a set lookup on `Path(fname).suffix` would be faster. |

### Performance

| # | Severity | Finding |
|---|----------|---------|
| 4.8 | **High** | Each postcondition check independently walks the entire file tree. For a contract with 15 postconditions (typical), this means 15 full os.walk traversals of the project. Should walk once and cache. |
| 4.9 | **Medium** | `_walk_source_files` is a generator that cannot be reused. Each caller creates a new walk. A single cached walk result would eliminate all redundancy. |

### Robustness

| # | Severity | Finding |
|---|----------|---------|
| 4.10 | **Medium** | Many postconditions will be "unparseable" (returned as `skipped`) because the natural language patterns are quite rigid. Postconditions worded as "The UserSession type must include a `token` field" would not match any classifier. The tool should document what phrasing conventions are required. |
| 4.11 | **Low** | No protection against maliciously crafted CONTRACT.md paths (path traversal). If `--contract` points to `../../etc/passwd`, it would be read. In practice this tool is only run by Gold, so risk is minimal. |

### Speed Improvements

- **Single-pass file index**: Walk the project once, cache `(path, content)` pairs. All postcondition checks query the cache.
- **Parallel postcondition checks**: Since checks are independent, verify them concurrently with a thread pool.
- **Lazy content loading**: Build a file index (paths only) first, then load content on demand with LRU cache.

---

## 5. `tools/swe_bench/load_tasks.py` (376 lines)

### Correctness

| # | Severity | Finding |
|---|----------|---------|
| 5.1 | **Medium** | `estimate_complexity` file path regex (line 62) `[\w/]+\.(?:py|js|ts|...)` will match substrings inside words. For example, `settings.py` in a sentence like "check settings.py" is fine, but `configure.python` would also match as `.py` followed by `thon`. The `\b` anchor helps but is applied after the extension, not before. Actually, on closer inspection, the `\b` is correct -- it anchors after the extension. The real issue is matching path-like strings that aren't file paths, like URLs containing `.py` or version strings. |
| 5.2 | **Low** | `build_mini_contract` Variant B (line 252): `f"{hint_line}\n".rstrip()` -- the `\n` is added and then potentially stripped. If `hint_line` is empty, this produces `"\n"` then strips to `""`. This is cosmetic but the logic is confusing. |
| 5.3 | **Low** | `parse_json_field` (line 19) silently converts non-list parsed JSON to `[str(parsed)]`. A JSON object `{"key": "value"}` would become `["{'key': 'value'}"]` (Python repr, not JSON). Unlikely but worth noting. |

### Performance

| # | Severity | Finding |
|---|----------|---------|
| 5.4 | **Low** | Streams JSONL line by line with a generator. Efficient for large inputs. No concerns. |

### Robustness

| # | Severity | Finding |
|---|----------|---------|
| 5.5 | **Medium** | No validation that `variant_override` values match expected set when passed programmatically (CLI validates via `choices`, but `load_tasks()` API does not). Passing `variant="D"` would silently produce empty prompts from the fallback `return` paths that don't exist -- actually, `build_gold_prompt` would fall through to Variant C for unknown variants, which is wrong behavior for an explicit override. |
| 5.6 | **Low** | `load_tasks` does not close the file handle if an exception occurs mid-iteration (the generator may be abandoned). Using a context manager around the `with open()` handles this, but callers that partially consume the generator and discard it will rely on GC to close the file. This is fine in CPython but fragile in other implementations. |

### Best Practices

| # | Severity | Finding |
|---|----------|---------|
| 5.7 | **Low** | The `hints` variable is extracted (line 87, 169) but only used in Variant B's `build_mini_contract`. It's unused in `build_gold_prompt` for all variants. Either intentional (hints are only for the compact brief) or a missed feature. |

---

## 6. `tools/swe_bench/emit_predictions.py` (179 lines)

### Correctness

| # | Severity | Finding |
|---|----------|---------|
| 6.1 | **Medium** | `validate_patch` (line 30) rejects patches not starting with `diff --git` or `---`. Some valid patches start with `commit` headers, `From` headers (git format-patch), or `Index:` lines (svn-style). For SWE-bench this is probably fine since patches are `git diff` output, but the validation is more restrictive than necessary. |
| 6.2 | **Medium** | `collect_predictions` yields `(None, "missing", instance_id)` for missing patches but `(prediction, "invalid", instance_id)` for read errors. The caller handles `None` correctly by checking `status == "missing"`, but the asymmetric return type (None vs dict) is fragile. |

### Performance

| # | Severity | Finding |
|---|----------|---------|
| 6.3 | **Low** | `results_path.iterdir()` loads all directory entries into a sorted list (line 63). For very large result sets (10K+), this is fine -- directory listing is fast. |

### Robustness

| # | Severity | Finding |
|---|----------|---------|
| 6.4 | **Medium** | The output file handle (line 131) is opened but if writing fails mid-way, the `finally` block closes it. However, a partial output file would be left on disk with no indication it's incomplete. Should write to a temp file and rename on success, or at minimum print a warning. |
| 6.5 | **Low** | No handling of symlinks in `results_path.iterdir()`. A symlink to a non-directory would be silently skipped (the `entry.is_dir()` check handles it). A symlink to a directory would be followed, which is probably desired behavior. |
| 6.6 | **Low** | `instance_id` is derived from directory name without sanitization. If a directory is named with special characters, the JSONL output would contain them. |

### Best Practices

| # | Severity | Finding |
|---|----------|---------|
| 6.7 | **Low** | Clean, well-structured code. Functions are small and focused. Good error reporting to stderr. The only style concern is the bare `open()` on line 131 instead of a context manager pattern (it uses try/finally instead, which is functionally equivalent but less idiomatic). |

---

## Cross-Cutting Concerns

### Shared Patterns Needing Attention

| # | Severity | Finding | Files Affected |
|---|----------|---------|----------------|
| X.1 | **High** | **Repeated full tree walks without caching.** `codebase_index.py`, `verify_postconditions.py`, and `test_impact_map.py` all independently walk the project tree and read file contents. If these tools are run sequentially during muster (which they are), the same files are read 3+ times. A shared file cache or a single "project snapshot" step would dramatically reduce I/O. | codebase_index, verify_postconditions, test_impact_map |
| X.2 | **High** | **Regex-based import parsing is incomplete.** All three analysis tools use regex to parse imports but miss: TypeScript `export * from`, `export { x } from`, Python relative imports (`from .foo import bar`), re-exports, barrel files, dynamic imports with variables, and conditional imports. | codebase_index, verify_postconditions, test_impact_map |
| X.3 | **Medium** | **No binary file detection.** None of the tools detect or skip binary files. A `.py` file that is actually a compiled `.pyc` renamed, or a `.js` file that is minified/bundled (thousands of chars on one line), would cause regex timeouts or garbage results. | All analysis tools |
| X.4 | **Medium** | **Inconsistent `SKIP_DIRS` lists.** Each tool defines its own set of directories to skip, and they differ: `codebase_index` skips `.turbo`, `.cache`, `.parcel-cache`, `out`, `.svelte-kit`; `test_impact_map` skips `.nuxt` but not `.turbo`; `verify_postconditions` matches `codebase_index`. These should be a shared constant. | codebase_index, test_impact_map, verify_postconditions |
| X.5 | **Low** | **No `__init__.py` or shared module.** These tools share patterns (file walking, import parsing, skip dirs) but don't share code. Extracting a `tools/_common.py` module would reduce duplication and ensure consistency. | All |

---

## Priority-Ordered Fix Recommendations

### P0 -- Fix Now (blocks correct results)

1. **Add Python relative import support** to `codebase_index.py` regex patterns. Change `RE_PY_FROM_IMPORT` to `r"""^from\s+(\.?[\w.]*)\s+import"""`. (Finding 1.2)

2. **Tighten `_keyword_match` in `seam_check.py`** to require whole-word matching and a minimum token length of 5, or switch to matching against the structured `files_created`/`files_modified` fields only (not free-text body). (Finding 2.1)

3. **Add file content caching to `test_impact_map.py`**. Read all test files once into a dict before iterating over source files. (Finding 3.6)

4. **Add project-wide file cache to `verify_postconditions.py`**. Walk once at startup, cache paths and lazily load content. (Finding 4.8)

### P1 -- Fix Soon (wrong results in edge cases)

5. **Tighten import-based test discovery** in `test_impact_map.py`. Replace bare substring matching with import-context-aware matching: require the basename to appear within an import/require/from statement, not anywhere in the file. Remove the fallback substring match or increase minimum token length to 6+. (Findings 3.1, 3.2)

6. **Fix `_detect_naming_conventions` crash** on empty stem in `codebase_index.py`. Add `if not stem: return []` guard. (Finding 1.5)

7. **Fix `_md_table` crash** in `seam_check.py` when row length doesn't match header length. Add defensive `row + [''] * (len(headers) - len(row))` padding. (Finding 2.7)

8. **Add encoding error handling** to `seam_check.py` `load_mailboxes`. Use `errors="replace"` in `read_text`. (Finding 2.8)

### P2 -- Improve (better accuracy and performance)

9. **Unify `SKIP_DIRS`** across all tools into a shared constant. (Finding X.4)

10. **Add binary file detection** -- skip files with null bytes in the first 8KB. (Finding X.3)

11. **Add TypeScript re-export parsing** (`export * from`, `export { x } from`) to `codebase_index.py`. (Finding X.2)

12. **Validate variant in `load_tasks` API** -- raise `ValueError` for unknown variants instead of silently falling through. (Finding 5.5)

13. **Use atomic writes in `emit_predictions.py`** -- write to temp file, rename on success. (Finding 6.4)

### P3 -- Nice to Have (maintainability, performance ceiling)

14. Extract shared `tools/_common.py` with file walking, import parsing, and skip dirs. (Finding X.5)

15. Add `concurrent.futures.ThreadPoolExecutor` for parallel file I/O in `codebase_index.py` and `verify_postconditions.py`.

16. Consider replacing the custom YAML parser in `seam_check.py` with `yaml.safe_load()` (add PyYAML as optional dependency with fallback to custom parser). (Finding 2.10)

17. Remove dead `RE_TS_IMPORT` regex from `codebase_index.py`. (Finding 1.1)

---

## Summary Statistics

| Tool | Critical | High | Medium | Low |
|------|----------|------|--------|-----|
| codebase_index.py | 0 | 3 | 4 | 3 |
| seam_check.py | 0 | 1 | 4 | 4 |
| test_impact_map.py | 0 | 3 | 2 | 2 |
| verify_postconditions.py | 0 | 3 | 4 | 3 |
| swe_bench/load_tasks.py | 0 | 0 | 2 | 3 |
| swe_bench/emit_predictions.py | 0 | 0 | 2 | 3 |
| Cross-cutting | 0 | 2 | 2 | 1 |
| **Total** | **0** | **12** | **20** | **19** |

No critical (crash-in-normal-use) bugs found. The 12 High findings cluster around two themes: **false positive matching** (substring/keyword matching that is too loose) and **redundant file I/O** (repeated full tree walks without caching). Fixing these two patterns would address 8 of the 12 High findings and meaningfully improve both correctness and performance on large codebases.
