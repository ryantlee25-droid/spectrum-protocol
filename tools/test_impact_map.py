#!/usr/bin/env python3
"""
test_impact_map.py — Test dependency map tool for Spectrum Gold (Muster phase)

Given a list of source files, discovers which test files exercise them via:
  1. Naming convention matching (foo.ts → foo.test.ts, test_foo.py, etc.)
  2. Import-based discovery (grep for basename in test files)

Usage:
    python3 tools/test_impact_map.py --files src/auth/login.ts src/auth/session.ts --root .

Output (stdout):
    ## Test Impact Map
    src/auth/login.ts → tests/auth/login.test.ts, tests/integration/auth.test.ts
    src/auth/session.ts → tests/auth/session.test.ts
    Total: 3 test files to verify

Exit 0 always — no-test projects should not fail the map.
"""

import argparse
import os
import re
import sys
from pathlib import Path


# ── Test file discovery patterns ──────────────────────────────────────────────

# Suffixes and patterns that identify test files
TEST_SUFFIXES_TS = [".test.ts", ".test.tsx", ".test.js", ".test.jsx",
                   ".spec.ts", ".spec.tsx", ".spec.js", ".spec.jsx"]

TEST_DIR_PATTERNS = ["__tests__", "tests", "test", "spec"]


def is_test_file(path: Path) -> bool:
    """Return True if the path looks like a test file."""
    name = path.name
    # Check for test suffixes (TypeScript/JavaScript)
    for suffix in TEST_SUFFIXES_TS:
        if name.endswith(suffix):
            return True
    # Check for Python test naming
    if name.startswith("test_") and name.endswith(".py"):
        return True
    if name.endswith("_test.py"):
        return True
    # Check if it's in a __tests__ directory
    parts = path.parts
    if "__tests__" in parts:
        return True
    return False


def find_all_test_files(root: Path) -> list[Path]:
    """Walk the project tree and collect all test files."""
    test_files = []
    skip_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__",
                 ".pytest_cache", "dist", "build", ".next", ".nuxt"}

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune directories we should not descend into
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for filename in filenames:
            path = Path(dirpath) / filename
            if is_test_file(path):
                test_files.append(path)

    return sorted(test_files)


# ── Naming convention matching ────────────────────────────────────────────────

def convention_candidates(source_file: Path, root: Path) -> list[Path]:
    """
    Generate candidate test paths based on naming conventions.

    TypeScript/JavaScript:
      src/auth/login.ts → {anywhere}/login.test.ts, login.spec.ts,
                          __tests__/login.ts (same basename)
    Python:
      src/auth/login.py → test_login.py, tests/test_login.py,
                          login_test.py (anywhere in tree)
    """
    stem = source_file.stem  # e.g. "login" from "login.ts"
    ext = source_file.suffix  # e.g. ".ts"
    candidates = []

    if ext in (".ts", ".tsx", ".js", ".jsx", ".mts", ".cts", ".mjs", ".cjs"):
        # TypeScript / JavaScript convention candidates
        for test_suffix in [".test.ts", ".test.tsx", ".test.js", ".test.jsx",
                             ".spec.ts", ".spec.tsx", ".spec.js", ".spec.jsx"]:
            candidates.append(stem + test_suffix)
        # __tests__/login.ts (original extension)
        candidates.append(stem + ext)

    elif ext == ".py":
        # Python convention candidates
        candidates.append(f"test_{stem}.py")
        candidates.append(f"{stem}_test.py")

    return candidates


def find_by_convention(source_file: Path, all_test_files: list[Path]) -> list[Path]:
    """Return test files that match source_file by naming convention."""
    candidates = set(convention_candidates(source_file, source_file.parent))
    matches = []
    for tf in all_test_files:
        if tf.name in candidates:
            matches.append(tf)
    return matches


# ── Import-based discovery ────────────────────────────────────────────────────

def find_by_import(source_file: Path, all_test_files: list[Path]) -> list[Path]:
    """
    Scan test files for import/require statements referencing the source file.

    Uses basename (without extension) as the search token — AST-free, grep-style.
    This catches cases like:
      import { login } from '../auth/login'
      from src.auth.login import login_user
      const login = require('./auth/login')
    """
    # Use stem (no extension) as the token to search for
    basename = source_file.stem  # e.g. "login"

    # For Python, also try the full dotted module path fragment
    # e.g. src/auth/login.py → "auth.login" and "login"
    search_tokens = {basename}

    # Build a path fragment (last 2-3 components without extension) for more precision
    parts = source_file.parts
    if len(parts) >= 2:
        # e.g. "auth/login" from "src/auth/login.ts"
        path_fragment = "/".join(parts[-2:])
        # Strip extension from last segment
        last_no_ext = parts[-1].rsplit(".", 1)[0]
        path_fragment_no_ext = "/".join(list(parts[-2:-1]) + [last_no_ext])
        search_tokens.add(path_fragment_no_ext)

    # Compile a regex that looks for the basename in import/require contexts
    # Matches: import ... from '...basename...', require('...basename...')
    # from basename import ..., import basename
    pattern = re.compile(
        r'(?:import|require|from)\s+[^\n]*' + re.escape(basename),
        re.IGNORECASE
    )

    matches = []
    for tf in all_test_files:
        try:
            content = tf.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        if pattern.search(content):
            matches.append(tf)
            continue

        # Fallback: plain substring match for any token (catches Python dotted imports)
        for token in search_tokens:
            if len(token) >= 3 and token in content:
                matches.append(tf)
                break

    return matches


# ── Main mapping logic ────────────────────────────────────────────────────────

def build_impact_map(source_files: list[str], root: str) -> dict[str, list[Path]]:
    """
    For each source file, return the set of test files that cover it.

    Returns dict: source_file_str → sorted list of test file Paths (relative to root).
    """
    root_path = Path(root).expanduser().resolve()
    all_test_files = find_all_test_files(root_path)

    result: dict[str, list[Path]] = {}

    for src_str in source_files:
        src_path = Path(src_str).expanduser()
        if not src_path.is_absolute():
            src_path = (root_path / src_path).resolve()
        else:
            src_path = src_path.resolve()

        # Convention-based matches
        convention_matches = find_by_convention(src_path, all_test_files)

        # Import-based matches (excluding already-found convention matches)
        import_matches = find_by_import(src_path, all_test_files)

        # Merge and deduplicate
        combined = list({tf.resolve(): tf for tf in convention_matches + import_matches}.values())
        combined.sort(key=lambda p: str(p))

        # Make paths relative to root for clean output
        relative = []
        for tf in combined:
            try:
                rel = tf.relative_to(root_path)
                relative.append(rel)
            except ValueError:
                relative.append(tf)

        result[src_str] = relative

    return result


def format_output(impact_map: dict[str, list[Path]]) -> str:
    """Format the impact map as a ## Test Impact Map block."""
    lines = ["## Test Impact Map"]

    all_test_files: set[str] = set()

    if not impact_map:
        lines.append("(no source files provided)")
        lines.append("Total: 0 test files to verify")
        return "\n".join(lines)

    for src, tests in impact_map.items():
        if tests:
            test_list = ", ".join(str(t) for t in tests)
            lines.append(f"{src} → {test_list}")
            for t in tests:
                all_test_files.add(str(t))
        else:
            lines.append(f"{src} → (no tests found)")

    total = len(all_test_files)
    lines.append(f"Total: {total} test file{'s' if total != 1 else ''} to verify")
    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate a test impact map for a set of source files. "
            "Used by Spectrum Gold during muster to populate CONTRACT.md."
        )
    )
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        metavar="FILE",
        help="Source files to map (paths relative to --root or absolute)",
    )
    parser.add_argument(
        "--root",
        default=".",
        metavar="DIR",
        help="Project root directory (default: current directory)",
    )
    args = parser.parse_args()

    impact_map = build_impact_map(args.files, args.root)
    print(format_output(impact_map))
    sys.exit(0)


if __name__ == "__main__":
    main()
