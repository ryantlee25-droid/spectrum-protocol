#!/usr/bin/env python3
"""
codebase_index.py — Semantic codebase indexing tool for Spectrum Gold (Muster phase)

Given a list of source files (a Howler's MODIFIES/CREATES list), builds a structured
context index of the surrounding codebase: import graphs, function signatures, patterns.
Gold runs this during muster and includes the output in CONTRACT.md's Codebase Context.

Usage:
    python3 tools/codebase_index.py --files src/auth/login.ts src/auth/session.ts --root /path/to/project

Output (stdout):
    ## Codebase Index: src/auth/login.ts
    ### Import Graph
    Imports: session (types), bcrypt (functions)
    Imported by: routes/auth, middleware/requireAuth
    ### Signatures
    - function authenticate(token: string): Promise<Session | null>
    ### Patterns
    - Named exports only (no default exports)
    - Factory pattern: createSession()

Exit 0 always — empty output for projects with no analyzable files.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# ── Directories to skip ─────────────────────────────────────────────────────

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", "dist", "build", ".next",
    "venv", ".venv", ".tox", ".mypy_cache", ".pytest_cache", "coverage",
    ".turbo", ".cache", ".parcel-cache", "out", ".svelte-kit",
}

ANALYZABLE_EXTS = {".ts", ".tsx", ".js", ".jsx", ".py"}


# ── File discovery ───────────────────────────────────────────────────────────

def iter_source_files(root: Path) -> "Generator":
    """Yield source file paths relative to root, skipping excluded dirs."""
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skip dirs in-place to prevent descent
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fname in filenames:
            p = Path(dirpath) / fname
            if p.suffix in ANALYZABLE_EXTS:
                yield p


# ── Import parsing ───────────────────────────────────────────────────────────

# TypeScript/JavaScript import patterns
# Active TS import pattern — covers `import { x } from 'y'` and `import x from 'y'`
RE_TS_IMPORT_FROM = re.compile(
    r"""import\s+(?:type\s+)?(?:\{[^}]*\}|[\w*]+(?:\s*,\s*\{[^}]*\})?)\s+from\s+['"]([^'"]+)['"]"""
)
RE_TS_REQUIRE = re.compile(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""")
RE_TS_DYNAMIC_IMPORT = re.compile(r"""import\s*\(\s*['"]([^'"]+)['"]\s*\)""")

# Python import patterns
# RE_PY_IMPORT handles absolute imports only (`import foo.bar`).
# Relative imports always use `from`, never bare `import`.
RE_PY_IMPORT = re.compile(r"""^import\s+([\w.]+)""", re.MULTILINE)
# Matches both absolute (`from foo.bar import X`) and relative (`from .models import X`,
# `from ..utils import Y`, `from ...pkg import Z`) Python imports.
RE_PY_FROM_IMPORT = re.compile(r"""^from\s+(\.{0,3}[\w.]*)\s+import""", re.MULTILINE)


def extract_imports_ts(content: str) -> List[str]:
    """Extract import specifiers from TypeScript/JavaScript content."""
    imports = []
    imports.extend(RE_TS_IMPORT_FROM.findall(content))
    imports.extend(RE_TS_REQUIRE.findall(content))
    imports.extend(RE_TS_DYNAMIC_IMPORT.findall(content))
    return imports


def extract_imports_py(content: str) -> List[str]:
    """Extract module names from Python import statements."""
    imports = []
    imports.extend(RE_PY_IMPORT.findall(content))
    imports.extend(RE_PY_FROM_IMPORT.findall(content))
    return imports


def extract_imports(filepath: Path, content: str) -> List[str]:
    """Extract imports based on file type."""
    if filepath.suffix in (".ts", ".tsx", ".js", ".jsx"):
        return extract_imports_ts(content)
    elif filepath.suffix == ".py":
        return extract_imports_py(content)
    return []


# ── Import resolution ────────────────────────────────────────────────────────

def resolve_ts_import(specifier: str, importer: Path, resolved_root: Path, file_index: Dict[str, Path]) -> Optional[str]:
    """Resolve a TS/JS import specifier to a relative file path (from root).

    Args:
        resolved_root: Pre-resolved root path (call root.resolve() once at the
                       entry point, not per invocation — finding 1.10).
    """
    if not specifier.startswith("."):
        # Package import — return as-is (not a local file)
        return None

    importer_dir = importer.parent
    candidate_base = (importer_dir / specifier).resolve()

    # Try with extensions and /index
    for ext in [".ts", ".tsx", ".js", ".jsx"]:
        candidate = candidate_base.with_suffix(ext)
        try:
            rel = candidate.relative_to(resolved_root)
            if str(rel) in file_index:
                return str(rel)
        except ValueError:
            pass

    # Try as directory with index file
    for ext in [".ts", ".tsx", ".js", ".jsx"]:
        candidate = candidate_base / f"index{ext}"
        try:
            rel = candidate.relative_to(resolved_root)
            if str(rel) in file_index:
                return str(rel)
        except ValueError:
            pass

    return None


def resolve_py_import(module_name: str, root: Path, file_index: Dict[str, Path]) -> Optional[str]:
    """Resolve a Python module name to a relative file path (from root)."""
    parts = module_name.split(".")
    # Try as direct file
    path_as_file = os.path.join(*parts) + ".py" if parts else None
    if path_as_file and path_as_file in file_index:
        return path_as_file
    # Try as package __init__
    path_as_pkg = os.path.join(*parts, "__init__.py") if parts else None
    if path_as_pkg and path_as_pkg in file_index:
        return path_as_pkg
    return None


# ── Signature extraction ─────────────────────────────────────────────────────

# TypeScript/JavaScript signatures
RE_TS_EXPORT_FUNC = re.compile(
    r"""export\s+(?:async\s+)?function\s+(\w+)\s*(?:<[^>]*>)?\s*\(([^)]*)\)(?:\s*:\s*([^\n{]+))?"""
)
RE_TS_EXPORT_CONST_ARROW = re.compile(
    r"""export\s+const\s+(\w+)\s*(?::\s*[^=]+)?\s*=\s*(?:async\s+)?\([^)]*\)\s*(?::\s*([^\n=>{]+))?\s*=>"""
)
RE_TS_EXPORT_CLASS = re.compile(
    r"""export\s+(?:default\s+)?class\s+(\w+)(?:\s+extends\s+[\w.]+)?(?:\s+implements\s+[\w.,\s]+)?\s*\{"""
)
RE_TS_EXPORT_INTERFACE = re.compile(
    r"""export\s+(?:default\s+)?interface\s+(\w+)(?:\s+extends\s+[\w.,\s<>]+)?\s*\{"""
)
RE_TS_EXPORT_TYPE = re.compile(
    r"""export\s+type\s+(\w+)(?:\s*<[^>]*>)?\s*=\s*([^\n;]+)"""
)
RE_TS_CLASS_METHOD = re.compile(
    r"""^\s+(?:async\s+)?(\w+)\s*(?:<[^>]*>)?\s*\(([^)]*)\)(?:\s*:\s*([^\n{]+))?""",
    re.MULTILINE,
)
RE_TS_CONSTRUCTOR = re.compile(
    r"""constructor\s*\(([^)]*)\)"""
)
RE_TS_DEFAULT_EXPORT = re.compile(r"""export\s+default\s+""")
RE_TS_NAMED_EXPORT = re.compile(r"""export\s+(?:const|function|class|interface|type|enum|let|var)\s+""")

# Python signatures
RE_PY_DEF = re.compile(
    r"""^(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^\n:]+))?""",
    re.MULTILINE,
)
RE_PY_CLASS = re.compile(
    r"""^class\s+(\w+)(?:\(([^)]*)\))?\s*:""",
    re.MULTILINE,
)
RE_PY_ALL = re.compile(r"""__all__\s*=\s*\[([^\]]+)\]""")


def extract_signatures_ts(content: str) -> List[str]:
    """Extract exported signatures from TypeScript/JavaScript."""
    sigs = []

    # Exported functions
    for m in RE_TS_EXPORT_FUNC.finditer(content):
        name, params, ret = m.group(1), m.group(2).strip(), (m.group(3) or "").strip()
        params = _compact_params(params)
        sig = f"function {name}({params})"
        if ret:
            sig += f": {ret}"
        sigs.append(sig)

    # Exported arrow functions
    for m in RE_TS_EXPORT_CONST_ARROW.finditer(content):
        name = m.group(1)
        ret = (m.group(2) or "").strip()
        sig = f"const {name} = (...) =>"
        if ret:
            sig += f" {ret}"
        sigs.append(sig)

    # Exported interfaces
    for m in RE_TS_EXPORT_INTERFACE.finditer(content):
        name = m.group(1)
        # Extract interface body (first few fields)
        start = m.end()
        body = _extract_brace_body(content, start)
        fields = _extract_interface_fields(body)
        if fields:
            sigs.append(f"interface {name} {{ {'; '.join(fields)} }}")
        else:
            sigs.append(f"interface {name}")

    # Exported types
    for m in RE_TS_EXPORT_TYPE.finditer(content):
        name, definition = m.group(1), m.group(2).strip().rstrip(";")
        if len(definition) > 80:
            definition = definition[:77] + "..."
        sigs.append(f"type {name} = {definition}")

    # Exported classes with key methods
    for m in RE_TS_EXPORT_CLASS.finditer(content):
        cls_name = m.group(1)
        start = m.end()
        body = _extract_brace_body(content, start)
        methods = _extract_class_methods_ts(body)
        if methods:
            sigs.append(f"class {cls_name} {{ {'; '.join(methods)} }}")
        else:
            sigs.append(f"class {cls_name}")

    return sigs


def extract_signatures_py(content: str) -> List[str]:
    """Extract signatures from Python files."""
    sigs = []

    # Module-level functions (not indented)
    for m in RE_PY_DEF.finditer(content):
        # Check if it's at module level (line starts at column 0)
        line_start = content.rfind("\n", 0, m.start()) + 1
        indent = m.start() - line_start
        if indent > 0:
            continue  # Skip methods — they'll be captured with their class
        name, params, ret = m.group(1), m.group(2).strip(), (m.group(3) or "").strip()
        if name.startswith("_") and not name.startswith("__"):
            continue  # Skip private functions
        params = _compact_params(params)
        sig = f"def {name}({params})"
        if ret:
            sig += f" -> {ret}"
        sigs.append(sig)

    # Classes with key methods
    for m in RE_PY_CLASS.finditer(content):
        cls_name = m.group(1)
        bases = (m.group(2) or "").strip()
        # Find methods inside the class
        cls_start = m.end()
        methods = _extract_class_methods_py(content, cls_start)
        cls_sig = f"class {cls_name}"
        if bases:
            cls_sig += f"({bases})"
        if methods:
            cls_sig += f" {{ {'; '.join(methods)} }}"
        sigs.append(cls_sig)

    return sigs


def extract_signatures(filepath: Path, content: str) -> List[str]:
    """Extract signatures based on file type."""
    if filepath.suffix in (".ts", ".tsx", ".js", ".jsx"):
        return extract_signatures_ts(content)
    elif filepath.suffix == ".py":
        return extract_signatures_py(content)
    return []


# ── Helpers for signature extraction ─────────────────────────────────────────

def _compact_params(params: str) -> str:
    """Shorten parameter strings that are too long."""
    params = re.sub(r"\s+", " ", params).strip()
    if len(params) > 100:
        # Count params and abbreviate
        count = params.count(",") + 1
        return f"...{count} params..."
    return params


def _extract_brace_body(content: str, start: int, max_chars: int = 2000) -> str:
    """Extract content inside braces starting from position (after opening brace)."""
    depth = 1
    end = min(start + max_chars, len(content))
    for i in range(start, end):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth == 0:
                return content[start:i]
    return content[start:end]


def _extract_interface_fields(body: str) -> List[str]:
    """Extract field signatures from an interface body."""
    fields = []
    for line in body.split("\n"):
        line = line.strip().rstrip(";,")
        if not line or line.startswith("//") or line.startswith("/*"):
            continue
        # Match field: name[?]: type
        m = re.match(r"(readonly\s+)?(\w+)(\?)?:\s*(.+)", line)
        if m:
            readonly = "readonly " if m.group(1) else ""
            name = m.group(2)
            optional = "?" if m.group(3) else ""
            ftype = m.group(4).strip()
            if len(ftype) > 40:
                ftype = ftype[:37] + "..."
            fields.append(f"{readonly}{name}{optional}: {ftype}")
        if len(fields) >= 8:
            fields.append("...")
            break
    return fields


def _extract_class_methods_ts(body: str) -> List[str]:
    """Extract public method signatures from a TS class body."""
    methods = []
    # Constructor
    m = RE_TS_CONSTRUCTOR.search(body)
    if m:
        params = _compact_params(m.group(1))
        methods.append(f"constructor({params})")
    # Methods (skip private/protected)
    for m in RE_TS_CLASS_METHOD.finditer(body):
        name = m.group(1)
        if name in ("constructor", "if", "for", "while", "switch", "return", "throw"):
            continue
        params = _compact_params(m.group(2))
        ret = (m.group(3) or "").strip()
        sig = f"{name}({params})"
        if ret:
            sig += f": {ret}"
        methods.append(sig)
        if len(methods) >= 8:
            methods.append("...")
            break
    return methods


def _extract_class_methods_py(content: str, cls_start: int) -> List[str]:
    """Extract public method signatures from a Python class."""
    methods = []
    # Find methods that are indented (belong to this class)
    remaining = content[cls_start:cls_start + 3000]
    for m in RE_PY_DEF.finditer(remaining):
        line_start = remaining.rfind("\n", 0, m.start()) + 1
        indent = m.start() - line_start
        if indent <= 0:
            break  # No longer inside the class
        name = m.group(1)
        if name.startswith("_") and name != "__init__":
            continue
        params = _compact_params(m.group(2))
        ret = (m.group(3) or "").strip()
        sig = f"{name}({params})"
        if ret:
            sig += f" -> {ret}"
        methods.append(sig)
        if len(methods) >= 8:
            methods.append("...")
            break
    return methods


# ── Pattern detection ────────────────────────────────────────────────────────

def detect_patterns(filepath: Path, content: str) -> List[str]:
    """Detect common code patterns in a file."""
    patterns = []

    if filepath.suffix in (".ts", ".tsx", ".js", ".jsx"):
        patterns.extend(_detect_patterns_ts(content))
    elif filepath.suffix == ".py":
        patterns.extend(_detect_patterns_py(content))

    # Naming convention detection
    patterns.extend(_detect_naming_conventions(filepath))

    return patterns


def _detect_patterns_ts(content: str) -> List[str]:
    """Detect patterns in TypeScript/JavaScript files."""
    patterns = []

    # Export style
    has_default = bool(RE_TS_DEFAULT_EXPORT.search(content))
    has_named = bool(RE_TS_NAMED_EXPORT.search(content))
    if has_named and not has_default:
        patterns.append("Named exports only (no default exports)")
    elif has_default and not has_named:
        patterns.append("Default export only")
    elif has_default and has_named:
        patterns.append("Mixed named + default exports")

    # Factory pattern
    factory_funcs = re.findall(r"(?:export\s+)?(?:async\s+)?function\s+(create\w+)", content)
    if factory_funcs:
        patterns.append(f"Factory pattern: {', '.join(factory_funcs[:3])}()")

    # Singleton
    if re.search(r"getInstance\s*\(", content) or re.search(r"private\s+static\s+instance", content):
        patterns.append("Singleton pattern: getInstance()")

    # Observer / Event emitter
    if re.search(r"(?:addEventListener|on\s*\(|emit\s*\(|subscribe\s*\()", content):
        patterns.append("Observer/Event pattern detected")

    # Middleware chain
    if re.search(r"(?:app\.use|router\.use|\.use\s*\()", content):
        patterns.append("Middleware chain pattern (app.use/router.use)")

    # React component
    if re.search(r"(?:React\.FC|React\.Component|useState|useEffect|jsx|tsx)", content):
        if re.search(r"forwardRef", content):
            patterns.append("React component with forwardRef")
        else:
            patterns.append("React component")

    # Error handling style
    custom_errors = re.findall(r"class\s+(\w+Error)\s+extends\s+Error", content)
    if custom_errors:
        patterns.append(f"Custom error classes: {', '.join(custom_errors[:3])}")
    if re.search(r"throw\s+new\s+\w+Error", content):
        patterns.append("Throws custom errors (not null/undefined returns)")

    # Zod/validation schemas
    if re.search(r"z\.\w+\(", content):
        patterns.append("Uses Zod schemas for validation")

    return patterns


def _detect_patterns_py(content: str) -> List[str]:
    """Detect patterns in Python files."""
    patterns = []

    # __all__ exports
    if RE_PY_ALL.search(content):
        patterns.append("Explicit __all__ exports")

    # Factory pattern
    factory_funcs = re.findall(r"def\s+(create_\w+|make_\w+|build_\w+)", content)
    if factory_funcs:
        patterns.append(f"Factory pattern: {', '.join(factory_funcs[:3])}()")

    # Singleton
    if re.search(r"_instance\s*=\s*None", content) or re.search(r"@classmethod.*\n.*def\s+get_instance", content):
        patterns.append("Singleton pattern")

    # Decorator usage
    decorators = re.findall(r"^@(\w+)", content, re.MULTILINE)
    unique_decorators = list(dict.fromkeys(decorators))[:5]
    if unique_decorators:
        patterns.append(f"Decorators in use: @{', @'.join(unique_decorators)}")

    # Dataclass / pydantic
    if re.search(r"@dataclass", content):
        patterns.append("Uses dataclasses")
    if re.search(r"class\s+\w+\(BaseModel\)", content):
        patterns.append("Uses Pydantic BaseModel")

    # Error handling
    custom_errors = re.findall(r"class\s+(\w+Error)\s*\(", content)
    if custom_errors:
        patterns.append(f"Custom exceptions: {', '.join(custom_errors[:3])}")

    # Async
    if re.search(r"async\s+def", content):
        patterns.append("Async functions present")

    return patterns


def _detect_naming_conventions(filepath: Path) -> List[str]:
    """Detect naming convention from the file name."""
    patterns = []
    stem = filepath.stem
    # Remove known suffixes
    for suffix in [".test", ".spec", ".d"]:
        if stem.endswith(suffix):
            stem = stem[:-len(suffix)]

    if "-" in stem:
        patterns.append("File naming: kebab-case")
    elif "_" in stem:
        patterns.append("File naming: snake_case")
    elif stem[0].isupper() and any(c.isupper() for c in stem[1:]):
        patterns.append("File naming: PascalCase")
    elif stem[0].islower() and any(c.isupper() for c in stem[1:]):
        patterns.append("File naming: camelCase")

    return patterns


def _detect_test_adjacency(filepath: Path, root: Path) -> List[str]:
    """Detect adjacent test files for the given source file."""
    patterns = []
    stem = filepath.stem
    parent = filepath.parent

    # Check for co-located tests
    test_patterns_ts = [
        parent / f"{stem}.test{filepath.suffix}",
        parent / f"{stem}.spec{filepath.suffix}",
        parent / "__tests__" / filepath.name,
    ]
    test_patterns_py = [
        parent / f"test_{filepath.name}",
        parent / "tests" / f"test_{filepath.name}",
    ]

    candidates = test_patterns_ts if filepath.suffix != ".py" else test_patterns_py
    found = []
    for t in candidates:
        full_path = root / t if not t.is_absolute() else t
        if full_path.exists():
            try:
                found.append(str(t.relative_to(root) if t.is_relative_to(root) else t))
            except (ValueError, AttributeError):
                found.append(str(t))

    if found:
        patterns.append(f"Adjacent test files: {', '.join(found)}")
    return patterns


# ── Import graph building ────────────────────────────────────────────────────

def build_import_graph(
    root: Path,
    target_files: Set[str],
) -> Tuple[Dict[str, List[str]], Dict[str, List[str]], Dict[str, str]]:
    """
    Build import graph for target files.
    Returns (imports_of, imported_by, content_cache) dicts keyed by relative path.
    Only resolves one level deep in each direction.
    content_cache maps relative path -> file content (read once, reused downstream).
    """
    # Cache root.resolve() to avoid repeated syscalls (finding 1.10)
    resolved_root = root.resolve()

    # Build file index: relative path -> absolute path
    file_index: Dict[str, Path] = {}
    for filepath in iter_source_files(root):
        try:
            rel = str(filepath.relative_to(root))
            file_index[rel] = filepath
        except ValueError:
            pass

    # Read every source file once into a content cache (finding 1.8).
    # This eliminates the O(N) second pass — both imports_of and imported_by
    # loops read from the cache instead of hitting the filesystem separately.
    content_cache: Dict[str, str] = {}
    for rel_path, abs_path in file_index.items():
        try:
            content_cache[rel_path] = abs_path.read_text(errors="replace")
        except (OSError, IOError):
            pass

    # For target files: find what they import
    imports_of: Dict[str, List[str]] = {}
    for target in target_files:
        if target not in file_index or target not in content_cache:
            continue
        abs_path = file_index[target]
        content = content_cache[target]

        raw_imports = extract_imports(abs_path, content)
        resolved = []
        for spec in raw_imports:
            if abs_path.suffix == ".py":
                resolved_path = resolve_py_import(spec, root, file_index)
            else:
                resolved_path = resolve_ts_import(spec, abs_path, resolved_root, file_index)
            if resolved_path:
                resolved.append(resolved_path)
            else:
                # Keep package name for external deps
                pkg = spec.split("/")[0] if "/" in spec else spec.split(".")[0]
                if not pkg.startswith("."):
                    resolved.append(f"[pkg]{pkg}")
        imports_of[target] = resolved

    # For all files in the project: find who imports target files (using cached content)
    imported_by: Dict[str, List[str]] = {t: [] for t in target_files}

    for rel_path, abs_path in file_index.items():
        if rel_path in target_files:
            continue  # Skip self-references
        if rel_path not in content_cache:
            continue

        content = content_cache[rel_path]
        raw_imports = extract_imports(abs_path, content)
        for spec in raw_imports:
            if abs_path.suffix == ".py":
                resolved_path = resolve_py_import(spec, root, file_index)
            else:
                resolved_path = resolve_ts_import(spec, abs_path, resolved_root, file_index)
            if resolved_path and resolved_path in target_files:
                imported_by[resolved_path].append(rel_path)

    return imports_of, imported_by, content_cache


# ── Output formatting ────────────────────────────────────────────────────────

def format_import_list(imports: List[str]) -> str:
    """Format a list of imports for display."""
    if not imports:
        return "(none)"
    # Separate local from package imports
    local = [i for i in imports if not i.startswith("[pkg]")]
    pkgs = [i.replace("[pkg]", "") for i in imports if i.startswith("[pkg]")]

    parts = []
    for l in local:
        # Show just the filename stem
        parts.append(Path(l).stem)
    for p in pkgs:
        parts.append(f"{p} (pkg)")

    return ", ".join(parts[:10]) + (" ..." if len(parts) > 10 else "")


def format_dependents(dependents: List[str]) -> str:
    """Format a list of dependent files for display."""
    if not dependents:
        return "(none)"
    stems = [Path(d).stem for d in dependents]
    return ", ".join(stems[:10]) + (" ..." if len(stems) > 10 else "")


def generate_index(
    root: Path,
    target_files: List[str],
) -> str:
    """Generate the full codebase index output."""
    output_parts = []

    # Normalize target file paths
    normalized = []
    for f in target_files:
        # Strip leading ./ or /
        f = f.lstrip("./")
        normalized.append(f)

    target_set = set(normalized)

    # Build import graph (returns content cache — each file read once)
    imports_of, imported_by, content_cache = build_import_graph(root, target_set)

    # Collect neighbor files (direct imports + dependents) for signature extraction
    neighbor_files: Set[str] = set()
    for target in normalized:
        for imp in imports_of.get(target, []):
            if not imp.startswith("[pkg]"):
                neighbor_files.add(imp)
        for dep in imported_by.get(target, []):
            neighbor_files.add(dep)

    # Generate index per target file
    for target in normalized:
        abs_path = root / target
        if not abs_path.exists():
            output_parts.append(f"## Codebase Index: {target}\n")
            output_parts.append("*File does not exist yet (CREATES)*\n")
            continue

        # Reuse cached content instead of re-reading from disk
        content = content_cache.get(target)
        if content is None:
            try:
                content = abs_path.read_text(errors="replace")
            except (OSError, IOError):
                continue

        output_parts.append(f"## Codebase Index: {target}\n")

        # Import Graph
        output_parts.append("### Import Graph")
        output_parts.append(f"Imports: {format_import_list(imports_of.get(target, []))}")
        output_parts.append(f"Imported by: {format_dependents(imported_by.get(target, []))}")
        output_parts.append("")

        # Signatures for this file
        sigs = extract_signatures(abs_path, content)
        if sigs:
            output_parts.append("### Signatures")
            for sig in sigs:
                output_parts.append(f"- {sig}")
            output_parts.append("")

        # Neighbor signatures (condensed) — reuse content cache
        neighbor_sigs = []
        for nf in sorted(neighbor_files):
            nf_path = root / nf
            nf_content = content_cache.get(nf)
            if nf_content is None:
                if not nf_path.exists():
                    continue
                try:
                    nf_content = nf_path.read_text(errors="replace")
                except (OSError, IOError):
                    continue
            ns = extract_signatures(nf_path, nf_content)
            if ns:
                neighbor_sigs.append((nf, ns))

        if neighbor_sigs:
            output_parts.append("### Neighbor Signatures")
            for nf, ns in neighbor_sigs[:5]:  # Limit to 5 neighbors
                stem = Path(nf).stem
                condensed = "; ".join(ns[:4])
                if len(ns) > 4:
                    condensed += "; ..."
                output_parts.append(f"- **{stem}**: {condensed}")
            output_parts.append("")

        # Patterns
        patterns = detect_patterns(abs_path, content)
        test_adj = _detect_test_adjacency(Path(target), root)
        patterns.extend(test_adj)
        if patterns:
            output_parts.append("### Patterns")
            for p in patterns:
                output_parts.append(f"- {p}")
            output_parts.append("")

    return "\n".join(output_parts)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Semantic codebase index for Spectrum CONTRACT.md context",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="Source files to index (relative to --root)",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Project root directory (default: current directory)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Warning: root directory does not exist: {root}", file=sys.stderr)
        sys.exit(0)

    try:
        output = generate_index(root, args.files)
        if output.strip():
            print(output)
    except Exception as e:
        print(f"Warning: codebase index failed: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
