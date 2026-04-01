#!/usr/bin/env python3
"""
Load SWE-bench tasks and format them for Spectrum's pipeline.

Reads SWE-bench JSONL input, auto-detects variant based on task complexity,
and emits enriched task records with gold_prompt and mini_contract fields.

Usage:
    python3 -m tools.swe_bench.load_tasks --input swe_bench_pro.jsonl [--limit N] [--variant B] [--filter pattern]
"""

import argparse
import json
import re
import sys
from pathlib import Path


def parse_json_field(value):
    """Parse a field that may be a JSON string or already a list."""
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
            return [str(parsed)]
        except (json.JSONDecodeError, TypeError):
            # Treat as a single test name if not valid JSON
            return [value] if value.strip() else []
    return []


def estimate_complexity(task):
    """Estimate task complexity to auto-select variant.

    Returns "A" for complex multi-file tasks, "B" for typical tasks,
    "C" is never auto-selected (control baseline only).

    Heuristics (from pipeline-design.md Section "Complexity-Based Variant Selection"):
      - Route to A if failing tests span 3+ test files
      - Route to A if problem_statement mentions 3+ distinct source file paths
      - Route to A if problem_statement exceeds 500 tokens (~2000 chars)
      - Route to B otherwise
    """
    problem = task.get("problem_statement", "")
    fail_to_pass = parse_json_field(task.get("FAIL_TO_PASS", []))

    # Count distinct test files in FAIL_TO_PASS
    test_files = set()
    for test_name in fail_to_pass:
        # Extract file path portion: tests/foo/bar.py::TestClass::test_method -> tests/foo/bar.py
        parts = test_name.split("::")
        if parts:
            test_files.add(parts[0])

    if len(test_files) >= 3:
        return "A"

    # Count file path mentions in problem_statement
    file_path_pattern = r'[\w/]+\.(?:py|js|ts|go|java|rb|rs|c|cpp|h)\b'
    mentioned_files = set(re.findall(file_path_pattern, problem))
    if len(mentioned_files) >= 3:
        return "A"

    # Long problem statements suggest complexity
    if len(problem) > 2000:
        return "A"

    return "B"


def build_gold_prompt(task, variant):
    """Build the prompt Gold or a Howler receives for this task.

    Variant A: Full Spectrum prompt with mini-CONTRACT.md reference.
    Variant B: Lite Spectrum prompt with compact task brief.
    Variant C: Bare Sonnet prompt (control baseline).
    """
    instance_id = task.get("instance_id", "unknown")
    repo = task.get("repo", "unknown")
    base_commit = task.get("base_commit", "unknown")
    problem = task.get("problem_statement", "")
    fail_to_pass = parse_json_field(task.get("FAIL_TO_PASS", []))
    hints = task.get("hints_text", "")

    fail_tests_str = "\n".join(f"  - {t}" for t in fail_to_pass)

    if variant == "A":
        return (
            f"Spectrum: swe-bench evaluation run\n"
            f"Howler: H-{instance_id}\n"
            f"Task: Resolve SWE-bench Pro issue {repo}/{instance_id}\n"
            f"Base commit: {base_commit}\n"
            f"\n"
            f"CONTEXT:\n"
            f"Gold has read the issue, the failing tests, and the implicated source files.\n"
            f"The mini-CONTRACT.md below has been verified by White Pre-Check:\n"
            f"all MODIFIES files exist, all test names are real, all function signatures match.\n"
            f"\n"
            f"--- BEGIN mini-CONTRACT.md ---\n"
            f"(See mini_contract field — Gold will populate this at runtime)\n"
            f"--- END mini-CONTRACT.md ---\n"
            f"\n"
            f"INSTRUCTIONS:\n"
            f"1. Write HOOK.md before touching any source files.\n"
            f"2. Implement the fix using Codebase Context from mini-CONTRACT.md.\n"
            f"3. Run the failing tests:\n{fail_tests_str}\n"
            f"4. REVISION PASS: If tests fail, read output, identify root cause, fix (max 2 passes).\n"
            f"5. ISSUE RE-READ: After tests pass, re-read the issue and assess completeness.\n"
            f"6. Quality gates: White + Gray + /diff-review in parallel.\n"
            f"7. Extract patch: git diff {base_commit} HEAD > patch.diff\n"
        )

    if variant == "B":
        return (
            f"Spectrum: swe-bench evaluation run (Lite)\n"
            f"Task: Resolve {repo}/{instance_id}\n"
            f"Base commit: {base_commit}\n"
            f"\n"
            f"ISSUE:\n{problem}\n"
            f"\n"
            f"FAILING TESTS (must pass after fix):\n{fail_tests_str}\n"
            f"\n"
            f"TASK BRIEF (from Gold):\n"
            f"(See mini_contract field for the compact task brief)\n"
            f"\n"
            f"INSTRUCTIONS:\n"
            f"1. Read the relevant source files.\n"
            f"2. Implement the fix.\n"
            f"3. Run the failing tests.\n"
            f"4. REVISION PASS: If tests fail, revise and retry (max 2 attempts).\n"
            f"5. ISSUE RE-READ: After tests pass, re-read the issue above and assess:\n"
            f"   - Does the patch resolve the stated problem end-to-end?\n"
            f"   - Are there edge cases not yet handled?\n"
            f"6. Quality gates: White + Gray in parallel.\n"
            f"7. Extract patch: git diff {base_commit} HEAD > patch.diff\n"
        )

    # Variant C — bare Sonnet control baseline
    return (
        f"You are resolving a GitHub issue. You have access to the repository at commit {base_commit}.\n"
        f"\n"
        f"Issue:\n{problem}\n"
        f"\n"
        f"Failing tests that must pass after your fix:\n{fail_tests_str}\n"
        f"\n"
        f"Instructions:\n"
        f"1. Read the relevant source files.\n"
        f"2. Implement the fix.\n"
        f"3. Run the failing tests.\n"
        f"4. If tests fail, revise and retry (max 2 attempts).\n"
        f"5. Output a unified diff patch of all changes.\n"
    )


def build_mini_contract(task, variant):
    """Build a mini-CONTRACT.md (Variant A) or compact task brief (Variant B).

    Variant C gets an empty string — no contract or brief.
    """
    instance_id = task.get("instance_id", "unknown")
    repo = task.get("repo", "unknown")
    base_commit = task.get("base_commit", "unknown")
    problem = task.get("problem_statement", "")
    fail_to_pass = parse_json_field(task.get("FAIL_TO_PASS", []))
    pass_to_pass = parse_json_field(task.get("PASS_TO_PASS", []))
    hints = task.get("hints_text", "")

    # Extract likely file paths from problem statement
    file_path_pattern = r'[\w/]+\.(?:py|js|ts|go|java|rb|rs|c|cpp|h)\b'
    mentioned_files = sorted(set(re.findall(file_path_pattern, problem)))

    # Extract test file paths from FAIL_TO_PASS
    test_files = sorted(set(
        t.split("::")[0] for t in fail_to_pass if "::" in t
    ))

    fail_tests_str = "\n".join(f"- {t}" for t in fail_to_pass)
    pass_tests_str = "\n".join(f"- {t}" for t in pass_to_pass[:10])
    if len(pass_to_pass) > 10:
        pass_tests_str += f"\n- ... and {len(pass_to_pass) - 10} more"

    affected_files_str = "\n".join(
        f"- {f} -- (Gold will add context at runtime)" for f in mentioned_files
    ) if mentioned_files else "- (Gold will identify affected files at runtime by reading failing tests)"

    test_map_str = "\n".join(f"- {f}" for f in test_files) if test_files else "- (to be determined from failing test imports)"

    if variant == "A":
        # Full mini-CONTRACT.md per pipeline-design.md template
        summary = problem[:300].replace("\n", " ").strip()
        if len(problem) > 300:
            summary += "..."

        return (
            f"# mini-CONTRACT.md: {repo}/{instance_id}\n"
            f"Base commit: {base_commit}\n"
            f"Generated by: Gold (Spectrum swe-bench adapter)\n"
            f"\n"
            f"## Issue Summary\n"
            f"{summary}\n"
            f"\n"
            f"## Affected Files (MODIFIES)\n"
            f"{affected_files_str}\n"
            f"\n"
            f"## Expected Behavior\n"
            f"All FAIL_TO_PASS tests pass after the fix. No PASS_TO_PASS regressions.\n"
            f"\n"
            f"## Failing Tests\n"
            f"{fail_tests_str}\n"
            f"\n"
            f"## Test Dependency Map\n"
            f"Test files covering affected source:\n"
            f"{test_map_str}\n"
            f"\n"
            f"## Codebase Context\n"
            f"(Gold populates per-file context at runtime after reading source files)\n"
            f"\n"
            f"## Preconditions (verified by White Pre-Check)\n"
            f"- All MODIFIES files exist at base commit: PENDING\n"
            f"- All test names are real: PENDING\n"
            f"- Function signatures match actual code: PENDING\n"
            f"\n"
            f"## Postconditions\n"
            f"- Failing tests pass after the fix\n"
            f"- No existing passing tests regress\n"
        )

    if variant == "B":
        # Compact task brief per pipeline-design.md Variant B
        goal = problem[:150].replace("\n", " ").strip()
        if len(problem) > 150:
            goal += "..."

        likely_files = ", ".join(mentioned_files[:3]) if mentioned_files else "(identify from failing test imports)"
        fail_names = ", ".join(fail_to_pass[:5])
        if len(fail_to_pass) > 5:
            fail_names += f" (+{len(fail_to_pass) - 5} more)"

        hint_line = ""
        if hints and hints.strip():
            hint_snippet = hints[:150].replace("\n", " ").strip()
            hint_line = f"Hint: {hint_snippet}"

        return (
            f"TASK BRIEF -- {repo}/{instance_id}\n"
            f"Likely file(s): {likely_files}\n"
            f"Failing tests: {fail_names}\n"
            f"Goal: {goal}\n"
            f"{hint_line}\n".rstrip()
        )

    # Variant C — no contract or brief
    return ""


def load_tasks(input_path, variant_override=None, limit=None, filter_pattern=None):
    """Load and process SWE-bench JSONL tasks.

    Args:
        input_path: Path to SWE-bench JSONL file.
        variant_override: Force variant A, B, or C for all tasks.
        limit: Max number of tasks to process.
        filter_pattern: Regex pattern to match against instance_id.

    Yields:
        Enriched task dicts ready for JSON output.
    """
    filter_re = re.compile(filter_pattern) if filter_pattern else None
    count = 0

    with open(input_path, "r", encoding="utf-8") as fh:
        for line_num, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue

            try:
                task = json.loads(line)
            except json.JSONDecodeError as exc:
                print(
                    f"WARNING: Skipping line {line_num}: invalid JSON: {exc}",
                    file=sys.stderr,
                )
                continue

            instance_id = task.get("instance_id", "")
            if not instance_id:
                print(
                    f"WARNING: Skipping line {line_num}: missing instance_id",
                    file=sys.stderr,
                )
                continue

            # Apply filter
            if filter_re and not filter_re.search(instance_id):
                continue

            # Determine variant
            variant = variant_override if variant_override else estimate_complexity(task)

            # Build output record
            output = {
                "instance_id": instance_id,
                "repo": task.get("repo", ""),
                "base_commit": task.get("base_commit", ""),
                "problem_statement": task.get("problem_statement", ""),
                "fail_to_pass": parse_json_field(task.get("FAIL_TO_PASS", [])),
                "pass_to_pass": parse_json_field(task.get("PASS_TO_PASS", [])),
                "variant": variant,
                "gold_prompt": build_gold_prompt(task, variant),
                "mini_contract": build_mini_contract(task, variant),
            }

            yield output
            count += 1

            if limit and count >= limit:
                break


def main():
    parser = argparse.ArgumentParser(
        description="Load SWE-bench tasks and format for Spectrum pipeline."
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to SWE-bench JSONL file.",
    )
    parser.add_argument(
        "--variant",
        choices=["A", "B", "C"],
        default=None,
        help="Force pipeline variant for all tasks (default: auto-detect).",
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=None,
        help="Process only the first N tasks.",
    )
    parser.add_argument(
        "--filter", "-f",
        default=None,
        help="Regex pattern to filter instance_ids (e.g. 'django__django').",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    total = 0
    variant_counts = {"A": 0, "B": 0, "C": 0}

    for task in load_tasks(input_path, args.variant, args.limit, args.filter):
        print(json.dumps(task, ensure_ascii=False))
        total += 1
        variant_counts[task["variant"]] += 1

    # Summary to stderr
    print(f"\n--- Summary ---", file=sys.stderr)
    print(f"Tasks processed: {total}", file=sys.stderr)
    for v in ("A", "B", "C"):
        if variant_counts[v]:
            print(f"  Variant {v}: {variant_counts[v]}", file=sys.stderr)


if __name__ == "__main__":
    main()
