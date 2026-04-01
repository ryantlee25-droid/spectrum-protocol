#!/usr/bin/env python3
"""
verify_postconditions.py — Machine-verified postcondition checker for Spectrum Howlers.

Catches "green but wrong" — a Howler passes tests but doesn't satisfy CONTRACT.md
postconditions. Reads CONTRACT.md, extracts postconditions for a specific Howler,
and mechanically verifies each one against the actual codebase. No LLM involved.

Usage:
    python3 tools/verify_postconditions.py \
      --contract ~/.claude/spectrum/{rain-id}/CONTRACT.md \
      --howler howler-auth \
      --root /path/to/project

Exit codes:
    0 — all postconditions pass
    1 — one or more postconditions failed
    2 — usage error (bad args, missing contract, etc.)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional


# ── Postcondition types ──────────────────────────────────────────────────────

class PostconditionResult:
    """Result of verifying a single postcondition."""
    __slots__ = ("description", "passed", "detail")

    def __init__(self, description: str, passed: bool, detail: str = ""):
        self.description = description
        self.passed = passed
        self.detail = detail


# ── CONTRACT.md parser ───────────────────────────────────────────────────────

def extract_howler_postconditions(contract_text: str, howler_name: str) -> list[str]:
    """
    Extract postconditions for a specific Howler from CONTRACT.md.

    Looks for sections matching patterns like:
      ## Design-by-Contract: howler-name
      ### Postconditions
    or:
      ## howler-name
      ### Postconditions

    Returns a list of postcondition strings (one per bullet point).
    """
    lines = contract_text.splitlines()
    postconditions: list[str] = []

    # Normalize howler name for matching (case-insensitive, flexible separators)
    name_pattern = re.escape(howler_name).replace(r"\-", r"[\-_ ]")

    # Find the Design-by-Contract section for this Howler
    dbc_pattern = re.compile(
        rf"^##\s+(?:Design-by-Contract\s*:\s*)?{name_pattern}\s*$", re.IGNORECASE
    )

    in_howler_section = False
    in_postconditions = False
    section_depth = 0

    for line in lines:
        stripped = line.strip()

        # Detect heading level
        heading_match = re.match(r"^(#{1,6})\s+", line)

        if heading_match:
            level = len(heading_match.group(1))

            if dbc_pattern.match(stripped):
                in_howler_section = True
                section_depth = level
                in_postconditions = False
                continue

            if in_howler_section:
                if level <= section_depth:
                    # Left the Howler's section entirely
                    in_howler_section = False
                    in_postconditions = False
                    continue

                if re.match(r"^#{2,6}\s+Postconditions?\s*$", stripped, re.IGNORECASE):
                    in_postconditions = True
                    continue
                elif level == section_depth + 1:
                    # New subsection at same depth as Postconditions — stop collecting
                    in_postconditions = False
                    continue

        if in_postconditions and stripped.startswith("- "):
            # Extract the postcondition text (strip leading "- ")
            postcondition = stripped[2:].strip()
            # Remove inline code backticks for easier matching later
            postconditions.append(postcondition)

    return postconditions


# ── Postcondition classifiers ────────────────────────────────────────────────

def classify_and_verify(
    postcondition: str,
    root: Path,
    cache: Optional["FileCache"] = None,
) -> Optional[PostconditionResult]:
    """
    Classify a postcondition string and run the appropriate static check.

    Args:
        postcondition: The postcondition string to verify.
        root: The project root directory.
        cache: Optional FileCache built once per verification run. When provided,
               all file-tree-walking helpers reuse the cached index instead of
               issuing fresh os.walk calls per postcondition.

    Returns a PostconditionResult, or None if the postcondition couldn't be parsed.
    """
    # Try each classifier in order (most specific first).
    # _check_file_exists and _check_file_export read specific known files; they
    # don't need the cache. The remaining four may walk the full tree.
    for classifier in [
        lambda pc, r: _check_no_import(pc, r, cache),
        _check_file_export,
        lambda pc, r: _check_export_exists(pc, r, cache),
        lambda pc, r: _check_function_signature(pc, r, cache),
        lambda pc, r: _check_type_shape(pc, r, cache),
        _check_file_exists,
    ]:
        result = classifier(postcondition, root)
        if result is not None:
            return result

    return None


# ── Individual check implementations ─────────────────────────────────────────

def _check_file_exists(postcondition: str, root: Path) -> Optional[PostconditionResult]:
    """
    Match: "X exists", "file X exists", "X is created"
    """
    patterns = [
        re.compile(r"^`?([^\s`]+\.\w+)`?\s+exists\b", re.IGNORECASE),
        re.compile(r"^file\s+`?([^\s`]+\.\w+)`?\s+exists\b", re.IGNORECASE),
        re.compile(r"^`?([^\s`]+\.\w+)`?\s+is\s+created\b", re.IGNORECASE),
        re.compile(r"^creates?\s+`?([^\s`]+\.\w+)`?", re.IGNORECASE),
    ]

    for pat in patterns:
        m = pat.search(postcondition)
        if m:
            filepath = m.group(1)
            full_path = root / filepath
            exists = full_path.exists()
            desc = f"{filepath} exists"
            if exists:
                return PostconditionResult(desc, True)
            else:
                return PostconditionResult(desc, False, f"file not found: {full_path}")

    return None


def _check_export_exists(
    postcondition: str,
    root: Path,
    cache: Optional["FileCache"] = None,
) -> Optional[PostconditionResult]:
    """
    Match: "exports X", "must export X"
    """
    patterns = [
        re.compile(r"^(?:must\s+)?exports?\s+`?(\w+)`?", re.IGNORECASE),
    ]

    for pat in patterns:
        m = pat.search(postcondition)
        if m:
            export_name = m.group(1)
            desc = f"exports {export_name}"

            # Search all TS/JS/PY files for the export
            found_in = _find_export(root, export_name, cache=cache)
            if found_in:
                return PostconditionResult(desc, True, f"found in {found_in}")
            else:
                return PostconditionResult(
                    desc, False, f"{export_name} not found as export in project"
                )

    return None


def _check_file_export(postcondition: str, root: Path) -> Optional[PostconditionResult]:
    """
    Match: "X exports Y", "src/types/auth.ts exports UserSession"
    """
    pat = re.compile(
        r"^`?([^\s`]+\.\w+)`?\s+exports?\s+`?(\w+)`?", re.IGNORECASE
    )
    m = pat.search(postcondition)
    if m:
        filepath = m.group(1)
        export_name = m.group(2)
        full_path = root / filepath
        desc = f"{filepath} exports {export_name}"

        if not full_path.exists():
            return PostconditionResult(desc, False, f"file not found: {full_path}")

        content = _read_file_safe(full_path)
        if content is None:
            return PostconditionResult(desc, False, f"could not read {full_path}")

        if _has_export(content, export_name, filepath):
            return PostconditionResult(desc, True)
        else:
            return PostconditionResult(
                desc, False, f"{export_name} not found as export in {filepath}"
            )

    return None


def _check_function_signature(
    postcondition: str,
    root: Path,
    cache: Optional["FileCache"] = None,
) -> Optional[PostconditionResult]:
    """
    Match: "X() return type — expected Y, found Z" style or
           "exports getSession(): Promise<UserSession | null>"
           "X has signature Y"
    """
    # Pattern: "exports funcName(...): ReturnType"
    pat = re.compile(
        r"exports?\s+`?(\w+)`?\s*\([^)]*\)\s*:\s*(.+)", re.IGNORECASE
    )
    m = pat.search(postcondition)
    if m:
        func_name = m.group(1)
        expected_return = m.group(2).strip().rstrip("`").strip()
        desc = f"{func_name}() return type matches {expected_return}"

        found_file, found_sig = _find_function_signature(root, func_name, cache=cache)
        if found_file is None:
            return PostconditionResult(
                desc, False, f"function {func_name} not found in project"
            )

        # Normalize whitespace for comparison
        norm_expected = _normalize_type(expected_return)
        norm_found = _normalize_type(found_sig) if found_sig else ""

        if norm_expected in norm_found or norm_found in norm_expected:
            return PostconditionResult(desc, True, f"found in {found_file}")
        else:
            return PostconditionResult(
                desc,
                False,
                f"expected {expected_return}, found {found_sig} in {found_file}",
            )

    return None


def _check_no_import(
    postcondition: str,
    root: Path,
    cache: Optional["FileCache"] = None,
) -> Optional[PostconditionResult]:
    """
    Match: "X never imports from Y", "no circular imports between X and Y",
           "X does not import Y", "X must not import from Y"
    """
    patterns = [
        re.compile(
            r"`?([^\s`]+)`?\s+never\s+imports?\s+from\s+`?([^\s`]+)`?",
            re.IGNORECASE,
        ),
        re.compile(
            r"no\s+circular\s+imports?\s+between\s+`?([^\s`]+)`?\s+and\s+`?([^\s`]+)`?",
            re.IGNORECASE,
        ),
        re.compile(
            r"`?([^\s`]+)`?\s+(?:does\s+not|must\s+not|should\s+not)\s+import\s+(?:from\s+)?`?([^\s`]+)`?",
            re.IGNORECASE,
        ),
    ]

    for pat in patterns:
        m = pat.search(postcondition)
        if m:
            source_pattern = m.group(1)
            forbidden_pattern = m.group(2)
            desc = f"No imports from {source_pattern} to {forbidden_pattern}"

            violations = _check_import_violation(
                root, source_pattern, forbidden_pattern, cache=cache
            )
            if not violations:
                return PostconditionResult(desc, True)
            else:
                detail = "; ".join(
                    f"{v[0]} imports {v[1]}" for v in violations[:3]
                )
                if len(violations) > 3:
                    detail += f" (and {len(violations) - 3} more)"
                return PostconditionResult(desc, False, detail)

    return None


def _check_type_shape(
    postcondition: str,
    root: Path,
    cache: Optional["FileCache"] = None,
) -> Optional[PostconditionResult]:
    """
    Match: "X.field is always Y", "X.field has type Y",
           "X includes field Y", "type X has member Y"
    """
    patterns = [
        re.compile(
            r"`?(\w+)\.(\w+)`?\s+is\s+(?:always\s+)?(.+)", re.IGNORECASE
        ),
        re.compile(
            r"`?(\w+)\.(\w+)`?\s+has\s+type\s+(.+)", re.IGNORECASE
        ),
        re.compile(
            r"type\s+`?(\w+)`?\s+has\s+member\s+`?(\w+)`?\s*(?::\s*(.+))?",
            re.IGNORECASE,
        ),
    ]

    for pat in patterns:
        m = pat.search(postcondition)
        if m:
            type_name = m.group(1)
            field_name = m.group(2)
            expected_type = m.group(3).strip().rstrip("`").strip() if m.group(3) else None
            desc = f"{type_name}.{field_name}" + (
                f" is {expected_type}" if expected_type else " exists"
            )

            found_file, found_type = _find_type_member(
                root, type_name, field_name, cache=cache
            )
            if found_file is None:
                return PostconditionResult(
                    desc,
                    False,
                    f"type {type_name} with member {field_name} not found",
                )

            if expected_type is None:
                # Just checking the member exists
                return PostconditionResult(desc, True, f"found in {found_file}")

            norm_expected = _normalize_type(expected_type)
            norm_found = _normalize_type(found_type) if found_type else ""

            if norm_expected == norm_found or norm_expected in norm_found:
                return PostconditionResult(desc, True, f"found in {found_file}")
            else:
                return PostconditionResult(
                    desc,
                    False,
                    f"expected {expected_type}, found {found_type} in {found_file}",
                )

    return None


# ── Helper functions ─────────────────────────────────────────────────────────

# File extensions to search by language
TS_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".mts"}
PY_EXTENSIONS = {".py"}
ALL_EXTENSIONS = TS_EXTENSIONS | PY_EXTENSIONS

# Directories to skip during file traversal
SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".next", "dist", "build",
    ".tox", ".venv", "venv", ".mypy_cache", ".pytest_cache", "coverage",
}


def _walk_source_files(root: Path, extensions: set[str] | None = None):
    """Yield source files under root, skipping common non-source directories."""
    if extensions is None:
        extensions = ALL_EXTENSIONS
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skipped directories in-place
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fname in filenames:
            if any(fname.endswith(ext) for ext in extensions):
                yield Path(dirpath) / fname


# ── File cache ───────────────────────────────────────────────────────────────

class FileCache:
    """
    Lazy file cache: walks the project tree once, remembers all source file
    paths, and loads file content on first access per path.

    This replaces O(N*P) os.walk calls (one per postcondition) with a single
    walk plus one read per source file regardless of how many postconditions
    reference it.

    Usage:
        cache = FileCache(root)
        for fpath, content in cache.iter_files():
            ...  # fpath is an absolute Path; content is the file text
    """

    def __init__(self, root: Path, extensions: set[str] | None = None):
        self._root = root
        self._extensions = extensions if extensions is not None else ALL_EXTENSIONS
        # Populated lazily on first iter_files() call
        self._paths: list[Path] | None = None
        self._contents: dict[Path, str] = {}

    def _ensure_index(self) -> None:
        """Walk the tree once and collect all matching paths."""
        if self._paths is not None:
            return
        self._paths = list(_walk_source_files(self._root, self._extensions))

    def iter_files(self):
        """Yield (Path, content_str) for each source file under root."""
        self._ensure_index()
        assert self._paths is not None
        for fpath in self._paths:
            if fpath not in self._contents:
                content = _read_file_safe(fpath)
                self._contents[fpath] = content if content is not None else ""
            yield fpath, self._contents[fpath]


def _read_file_safe(path: Path) -> Optional[str]:
    """Read a file, returning None on error."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _has_export(content: str, name: str, filepath: str) -> bool:
    """Check if content contains an export of `name`."""
    ext = Path(filepath).suffix

    if ext in TS_EXTENSIONS:
        # TypeScript/JavaScript export patterns
        patterns = [
            # export interface/type/class/function/const/let/var/enum Name
            rf"\bexport\s+(?:default\s+)?(?:interface|type|class|function|const|let|var|enum|abstract\s+class)\s+{re.escape(name)}\b",
            # export { Name } or export { X as Name }
            rf"\bexport\s*\{{[^}}]*\b{re.escape(name)}\b[^}}]*\}}",
            # export default Name (when Name is on same line)
            rf"\bexport\s+default\s+{re.escape(name)}\b",
        ]
    elif ext in PY_EXTENSIONS:
        # Python: check __all__ or top-level definitions
        patterns = [
            # def name or class name or name = ...
            rf"^(?:def|class)\s+{re.escape(name)}\b",
            rf"^{re.escape(name)}\b\s*[=:]",
            # In __all__ — word-boundary on name to prevent "User" matching "UserSession"
            # Fixed mismatched quotes: use symmetric ['"] on both sides
            rf"""__all__\s*=\s*\[.*['\"]\b{re.escape(name)}\b['\"]""",
        ]
    else:
        return False

    for pat in patterns:
        if re.search(pat, content, re.MULTILINE):
            return True
    return False


def _find_export(root: Path, name: str, cache: Optional["FileCache"] = None) -> Optional[str]:
    """Search all source files for an export of `name`. Return file path or None."""
    file_iter = cache.iter_files() if cache is not None else (
        (fpath, _read_file_safe(fpath) or "") for fpath in _walk_source_files(root)
    )
    for fpath, content in file_iter:
        if content and _has_export(content, name, str(fpath)):
            try:
                return str(fpath.relative_to(root))
            except ValueError:
                return str(fpath)
    return None


def _find_function_signature(
    root: Path, func_name: str, cache: Optional["FileCache"] = None
) -> tuple[Optional[str], Optional[str]]:
    """
    Find a function/method export and extract its return type annotation.
    Returns (relative_path, return_type_string) or (None, None).
    """
    # TS pattern: export (async)? function funcName(...): ReturnType
    ts_pat = re.compile(
        rf"\bexport\s+(?:default\s+)?(?:async\s+)?function\s+{re.escape(func_name)}\b\s*"
        rf"\([^)]*\)\s*:\s*([^\{{\n]+)",
        re.MULTILINE,
    )
    # TS arrow/const pattern: export const funcName = (...): ReturnType =>
    ts_arrow_pat = re.compile(
        rf"\bexport\s+const\s+{re.escape(func_name)}\b\s*=\s*(?:async\s+)?\([^)]*\)\s*:\s*([^\s=>]+(?:<[^>]+>)?)",
        re.MULTILINE,
    )
    # Python pattern: def func_name(...) -> ReturnType:
    py_pat = re.compile(
        rf"^def\s+{re.escape(func_name)}\b\s*\([^)]*\)\s*->\s*([^:]+):",
        re.MULTILINE,
    )

    file_iter = cache.iter_files() if cache is not None else (
        (fpath, _read_file_safe(fpath) or "") for fpath in _walk_source_files(root)
    )
    for fpath, content in file_iter:
        if not content:
            continue

        for pat in [ts_pat, ts_arrow_pat, py_pat]:
            m = pat.search(content)
            if m:
                ret_type = m.group(1).strip()
                try:
                    rel = str(fpath.relative_to(root))
                except ValueError:
                    rel = str(fpath)
                return rel, ret_type

    return None, None


def _check_import_violation(
    root: Path,
    source_pattern: str,
    forbidden_pattern: str,
    cache: Optional["FileCache"] = None,
) -> list[tuple[str, str]]:
    """
    Check that files matching source_pattern don't import from files matching
    forbidden_pattern. Returns list of (source_file, imported_module) violations.
    """
    violations: list[tuple[str, str]] = []

    # Normalize patterns — they might be directory paths or glob-like
    source_pat = source_pattern.rstrip("/")
    forbidden_pat = forbidden_pattern.rstrip("/")

    file_iter = cache.iter_files() if cache is not None else (
        (fpath, _read_file_safe(fpath) or "") for fpath in _walk_source_files(root)
    )
    for fpath, content in file_iter:
        try:
            rel = str(fpath.relative_to(root))
        except ValueError:
            rel = str(fpath)

        # Check if this file is in the source pattern
        if source_pat not in rel:
            continue

        if not content:
            continue

        ext = fpath.suffix

        if ext in TS_EXTENSIONS:
            # Find all import/require statements
            import_pats = [
                re.compile(r"""(?:import|from)\s+['"]([^'"]+)['"]"""),
                re.compile(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)"""),
            ]
            for ipat in import_pats:
                for im in ipat.finditer(content):
                    imported = im.group(1)
                    if forbidden_pat in imported:
                        violations.append((rel, imported))

        elif ext in PY_EXTENSIONS:
            import_pats = [
                re.compile(r"^import\s+(\S+)", re.MULTILINE),
                re.compile(r"^from\s+(\S+)\s+import", re.MULTILINE),
            ]
            for ipat in import_pats:
                for im in ipat.finditer(content):
                    imported = im.group(1)
                    if forbidden_pat in imported:
                        violations.append((rel, imported))

    return violations


def _find_type_member(
    root: Path,
    type_name: str,
    field_name: str,
    cache: Optional["FileCache"] = None,
) -> tuple[Optional[str], Optional[str]]:
    """
    Find a type/interface definition and extract the type of a specific field.
    Returns (relative_path, field_type_string) or (None, None).
    """
    # TS: interface/type TypeName { ... fieldName: FieldType; ... }
    # We need to find the type block and then the field within it.
    # Use word boundaries so "User" does not match "UserSession".
    type_start_pat = re.compile(
        rf"\b(?:export\s+)?(?:interface|type)\s+{re.escape(type_name)}\b"
    )
    # Word boundary on field_name so "token" doesn't match "tokenExpiry"
    field_pat = re.compile(
        rf"^\s*{re.escape(field_name)}\b\s*[?]?\s*:\s*(.+?)[\s;,]*$", re.MULTILINE
    )

    # Python: class TypeName(TypedDict/BaseModel): ... field_name: FieldType
    py_type_start_pat = re.compile(
        rf"^class\s+{re.escape(type_name)}\b", re.MULTILINE
    )
    py_field_pat = re.compile(
        rf"^\s+{re.escape(field_name)}\b\s*:\s*(.+?)$", re.MULTILINE
    )

    file_iter = cache.iter_files() if cache is not None else (
        (fpath, _read_file_safe(fpath) or "") for fpath in _walk_source_files(root)
    )
    for fpath, content in file_iter:
        if not content:
            continue

        ext = fpath.suffix

        if ext in TS_EXTENSIONS:
            m = type_start_pat.search(content)
            if m:
                # Extract the block after the type definition
                rest = content[m.end():]
                # Find the opening brace
                brace_pos = rest.find("{")
                if brace_pos == -1:
                    # Could be a type alias with = { ... }
                    eq_pos = rest.find("=")
                    if eq_pos != -1:
                        brace_pos = rest.find("{", eq_pos)
                if brace_pos != -1:
                    block = _extract_brace_block(rest[brace_pos:])
                    fm = field_pat.search(block)
                    if fm:
                        try:
                            rel = str(fpath.relative_to(root))
                        except ValueError:
                            rel = str(fpath)
                        return rel, fm.group(1).strip()

        elif ext in PY_EXTENSIONS:
            m = py_type_start_pat.search(content)
            if m:
                # Extract the class body (indented lines after the class def)
                rest = content[m.end():]
                fm = py_field_pat.search(rest)
                if fm:
                    try:
                        rel = str(fpath.relative_to(root))
                    except ValueError:
                        rel = str(fpath)
                    return rel, fm.group(1).strip()

    return None, None


def _extract_brace_block(text: str) -> str:
    """Extract text between the first { and its matching }, handling nesting."""
    if not text or text[0] != "{":
        return ""
    depth = 0
    for i, ch in enumerate(text):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[1:i]
    # Unmatched — return everything after the opening brace
    return text[1:]


def _normalize_type(type_str: str) -> str:
    """Normalize a type string for comparison (strip whitespace, backticks, quotes)."""
    s = type_str.strip().strip("`").strip("'").strip('"')
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s)
    # Remove trailing semicolons/commas
    s = s.rstrip(";,")
    return s


# ── Output formatting ────────────────────────────────────────────────────────

def format_results(
    howler_name: str, results: list[PostconditionResult], skipped: list[str]
) -> str:
    """Format verification results for terminal output."""
    lines = [
        f"Postcondition Verification: {howler_name}",
        "\u2501" * 44,
    ]

    for r in results:
        icon = "\u2713" if r.passed else "\u2717"
        line = f"  {icon} {r.description}"
        if not r.passed and r.detail:
            line += f" -- {r.detail}"
        lines.append(line)

    for s in skipped:
        lines.append(f"  ? {s} (unparseable -- skipped)")

    lines.append("\u2501" * 44)

    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    total = len(results)
    status = "PASS" if failed == 0 else "FAIL"

    summary = f"Result: {passed}/{total} PASS"
    if failed > 0:
        summary += f" ({failed} FAIL)"
    if skipped:
        summary += f" ({len(skipped)} skipped)"
    lines.append(summary)

    return "\n".join(lines)


# ── Main entry point ─────────────────────────────────────────────────────────

def run_verification(
    contract_path: str, howler_name: str, root_path: str
) -> tuple[list[PostconditionResult], list[str]]:
    """
    Run postcondition verification.

    Returns (results, skipped) where:
      - results: list of PostconditionResult
      - skipped: list of unparseable postcondition strings
    """
    contract_file = Path(contract_path).expanduser().resolve()
    if not contract_file.is_file():
        raise FileNotFoundError(f"CONTRACT.md not found: {contract_file}")

    root = Path(root_path).expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Project root not found: {root}")

    contract_text = contract_file.read_text(encoding="utf-8")
    postconditions = extract_howler_postconditions(contract_text, howler_name)

    if not postconditions:
        print(
            f"Warning: no postconditions found for '{howler_name}' in {contract_file}",
            file=sys.stderr,
        )
        return [], []

    # Build a single lazy file cache for the entire verification run.
    # All postcondition checks reuse this cache instead of each triggering a
    # fresh os.walk traversal — reducing N full tree walks to at most 1.
    file_cache = FileCache(root)

    results: list[PostconditionResult] = []
    skipped: list[str] = []

    for pc in postconditions:
        result = classify_and_verify(pc, root, cache=file_cache)
        if result is not None:
            results.append(result)
        else:
            skipped.append(pc)

    return results, skipped


def main():
    parser = argparse.ArgumentParser(
        description="Verify CONTRACT.md postconditions for a Howler against the codebase."
    )
    parser.add_argument(
        "--contract",
        required=True,
        help="Path to CONTRACT.md",
    )
    parser.add_argument(
        "--howler",
        required=True,
        help="Howler name (e.g. howler-auth)",
    )
    parser.add_argument(
        "--root",
        required=True,
        help="Path to project root",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON",
    )
    args = parser.parse_args()

    try:
        results, skipped = run_verification(args.contract, args.howler, args.root)
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        import json

        output = {
            "howler": args.howler,
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "skipped": len(skipped),
            "results": [
                {
                    "description": r.description,
                    "passed": r.passed,
                    "detail": r.detail,
                }
                for r in results
            ],
            "skipped_postconditions": skipped,
        }
        print(json.dumps(output, indent=2))
    else:
        print()
        print(format_results(args.howler, results, skipped))

    has_failure = any(not r.passed for r in results)
    sys.exit(1 if has_failure else 0)


if __name__ == "__main__":
    main()
