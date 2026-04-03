#!/usr/bin/env python3
"""
Head-to-Head Benchmark Scorer

Evaluates the result of a benchmark task run by checking:
  - Correctness: tsc --noEmit + jest pass
  - Completeness: files present vs expected
  - Conflicts: pattern checks (stale refs, missing imports)
  - Cost: token count from session log (optional)
  - Time: duration in seconds (optional)

Usage:
  python score.py --task 1 --result-dir ./tmp/variant-a --expected-dir ./expected --output json
  python score.py --help
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def run_command(cmd: List[str], cwd: str, timeout: int = 120) -> tuple:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"


def check_correctness(result_dir: str) -> Dict[str, Any]:
    """Run tsc --noEmit and jest in the result directory."""
    checks = {}

    # TypeScript type check
    rc, stdout, stderr = run_command(["npx", "tsc", "--noEmit"], cwd=result_dir)
    checks["tsc_pass"] = rc == 0
    checks["tsc_output"] = stderr.strip() if stderr.strip() else stdout.strip()

    # Jest tests
    rc, stdout, stderr = run_command(["npx", "jest", "--no-coverage"], cwd=result_dir)
    checks["jest_pass"] = rc == 0

    # Parse test counts from jest output
    combined = stdout + stderr
    match = re.search(r"Tests:\s+(?:(\d+) failed,\s+)?(\d+) passed", combined)
    if match:
        checks["tests_failed"] = int(match.group(1)) if match.group(1) else 0
        checks["tests_passed"] = int(match.group(2))
    else:
        checks["tests_failed"] = -1
        checks["tests_passed"] = -1

    checks["pass"] = checks["tsc_pass"] and checks["jest_pass"]
    return checks


def check_completeness(result_dir: str, expected_dir: str, task: int) -> Dict[str, Any]:
    """Compare files present in result vs expected file list."""
    checks: Dict[str, Any] = {}
    files_txt = Path(expected_dir) / f"task{task}" / "files.txt"

    if not files_txt.exists():
        checks["pass"] = False
        checks["error"] = f"Expected file list not found: {files_txt}"
        checks["missing"] = []
        checks["extra"] = []
        return checks

    expected_files = set()
    for line in files_txt.read_text().strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            expected_files.add(line)

    result_path = Path(result_dir)
    actual_files = set()
    for f in result_path.rglob("*"):
        if f.is_file():
            rel = str(f.relative_to(result_path))
            # Skip node_modules, dist, and hidden dirs
            if any(part.startswith(".") or part == "node_modules" or part == "dist"
                   for part in Path(rel).parts):
                continue
            actual_files.add(rel)

    missing = sorted(expected_files - actual_files)
    extra = sorted(actual_files - expected_files)

    checks["expected_count"] = len(expected_files)
    checks["actual_count"] = len(actual_files)
    checks["missing"] = missing
    checks["extra"] = extra
    checks["pass"] = len(missing) == 0

    return checks


def check_conflicts(result_dir: str, expected_dir: str, task: int) -> Dict[str, Any]:
    """Run pattern-based conflict checks from checks.json."""
    checks: Dict[str, Any] = {"violations": [], "pass": True}
    checks_file = Path(expected_dir) / f"task{task}" / "checks.json"

    if not checks_file.exists():
        checks["error"] = f"Checks file not found: {checks_file}"
        checks["pass"] = False
        return checks

    try:
        spec = json.loads(checks_file.read_text())
    except json.JSONDecodeError as e:
        checks["error"] = f"Invalid JSON in checks file: {e}"
        checks["pass"] = False
        return checks

    result_path = Path(result_dir)

    # must_contain checks
    for entry in spec.get("must_contain", []):
        file_path = result_path / entry["file"]
        pattern = entry["pattern"]
        if not file_path.exists():
            checks["violations"].append({
                "type": "must_contain",
                "file": entry["file"],
                "pattern": pattern,
                "reason": "file does not exist",
            })
            checks["pass"] = False
        else:
            content = file_path.read_text()
            if not re.search(pattern, content):
                checks["violations"].append({
                    "type": "must_contain",
                    "file": entry["file"],
                    "pattern": pattern,
                    "reason": "pattern not found in file",
                })
                checks["pass"] = False

    # must_not_contain checks
    for entry in spec.get("must_not_contain", []):
        file_path = result_path / entry["file"]
        pattern = entry["pattern"]
        if file_path.exists():
            content = file_path.read_text()
            if re.search(pattern, content):
                checks["violations"].append({
                    "type": "must_not_contain",
                    "file": entry["file"],
                    "pattern": pattern,
                    "reason": "pattern found in file but should not be present",
                })
                checks["pass"] = False

    return checks


def check_cost(session_log: Optional[str]) -> Dict[str, Any]:
    """Parse token count from Claude Code session log."""
    if not session_log:
        return {"tokens": None, "available": False}

    log_path = Path(session_log)
    if not log_path.exists():
        return {"tokens": None, "available": False, "error": f"Log file not found: {session_log}"}

    content = log_path.read_text()

    # Try common patterns for token counts in Claude Code output
    patterns = [
        r"Total tokens?:\s*([\d,]+)",
        r"tokens?\s+used:\s*([\d,]+)",
        r"input_tokens.*?(\d+).*?output_tokens.*?(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                # input + output tokens
                total = int(groups[0].replace(",", "")) + int(groups[1].replace(",", ""))
            else:
                total = int(groups[0].replace(",", ""))
            return {"tokens": total, "available": True}

    return {"tokens": None, "available": False, "error": "No token count pattern matched"}


def build_result(
    task: int,
    variant: str,
    correctness: Dict[str, Any],
    completeness: Dict[str, Any],
    conflicts: Dict[str, Any],
    cost: Dict[str, Any],
    duration: Optional[float],
) -> Dict[str, Any]:
    """Build the final result dict."""
    return {
        "task": task,
        "variant": variant,
        "correctness": correctness,
        "completeness": completeness,
        "conflicts": conflicts,
        "cost_tokens": cost.get("tokens"),
        "duration_seconds": duration,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_pass": correctness["pass"] and completeness["pass"] and conflicts["pass"],
    }


def format_markdown(result: Dict[str, Any]) -> str:
    """Format result as a readable markdown section."""
    lines = []
    lines.append(f"## Task {result['task']} — Variant {result['variant']}")
    lines.append("")

    overall = "PASS" if result["overall_pass"] else "FAIL"
    lines.append(f"**Overall: {overall}**")
    lines.append("")

    # Correctness
    c = result["correctness"]
    tsc = "PASS" if c["tsc_pass"] else "FAIL"
    jest = "PASS" if c["jest_pass"] else "FAIL"
    lines.append(f"| Check | Result |")
    lines.append(f"|-------|--------|")
    lines.append(f"| tsc --noEmit | {tsc} |")
    lines.append(f"| jest | {jest} (passed: {c.get('tests_passed', '?')}, failed: {c.get('tests_failed', '?')}) |")
    lines.append(f"| Completeness | {'PASS' if result['completeness']['pass'] else 'FAIL'} |")
    lines.append(f"| Conflicts | {'PASS' if result['conflicts']['pass'] else 'FAIL'} |")
    lines.append("")

    # Details
    if result["completeness"].get("missing"):
        lines.append("**Missing files:**")
        for f in result["completeness"]["missing"]:
            lines.append(f"- `{f}`")
        lines.append("")

    if result["conflicts"].get("violations"):
        lines.append("**Conflict violations:**")
        for v in result["conflicts"]["violations"]:
            lines.append(f"- [{v['type']}] `{v['file']}`: pattern `{v['pattern']}` — {v['reason']}")
        lines.append("")

    if result["cost_tokens"] is not None:
        lines.append(f"**Cost:** {result['cost_tokens']:,} tokens")
    if result["duration_seconds"] is not None:
        lines.append(f"**Duration:** {result['duration_seconds']:.1f}s")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score a head-to-head benchmark task result",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python score.py --task 1 --result-dir ./tmp/variant-a --expected-dir ./expected
  python score.py --task 3 --result-dir ./tmp/variant-b --expected-dir ./expected --output markdown
  python score.py --task 2 --result-dir ./tmp/variant-a --expected-dir ./expected --session-log ./logs/session.txt --duration-seconds 45.2
        """,
    )
    parser.add_argument("--task", type=int, required=True, choices=[1, 2, 3, 4],
                        help="Task number (1-4)")
    parser.add_argument("--result-dir", type=str, required=True,
                        help="Path to the result directory (modified scaffold)")
    parser.add_argument("--expected-dir", type=str, required=True,
                        help="Path to the expected output directory")
    parser.add_argument("--variant", type=str, default="unknown",
                        help="Variant label (e.g., 'raw-sonnet' or 'spectrum')")
    parser.add_argument("--output", type=str, default="json", choices=["json", "markdown"],
                        help="Output format (default: json)")
    parser.add_argument("--session-log", type=str, default=None,
                        help="Path to Claude Code session log for token counting (optional)")
    parser.add_argument("--duration-seconds", type=float, default=None,
                        help="Wall-clock duration in seconds (optional)")

    args = parser.parse_args()

    result_dir = str(Path(args.result_dir).resolve())
    expected_dir = str(Path(args.expected_dir).resolve())

    if not Path(result_dir).is_dir():
        print(f"Error: result directory does not exist: {result_dir}", file=sys.stderr)
        sys.exit(1)

    correctness = check_correctness(result_dir)
    completeness = check_completeness(result_dir, expected_dir, args.task)
    conflicts = check_conflicts(result_dir, expected_dir, args.task)
    cost = check_cost(args.session_log)

    result = build_result(
        task=args.task,
        variant=args.variant,
        correctness=correctness,
        completeness=completeness,
        conflicts=conflicts,
        cost=cost,
        duration=args.duration_seconds,
    )

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_markdown(result))


if __name__ == "__main__":
    main()
