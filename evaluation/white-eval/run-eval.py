#!/usr/bin/env python3
"""
White Agent Eval Harness — Sonnet vs Haiku
Feeds unified diffs to claude -p and scores against ground truth.

Usage:
    python run-eval.py                          # run both models, all scenarios
    python run-eval.py --model sonnet           # one model only
    python run-eval.py --scenario white-01      # one scenario only
    python run-eval.py --dry-run                # print prompts, no API calls
    python run-eval.py --score-only             # re-score existing results dir
    python run-eval.py --results-dir results/run-xxx  # use specific run dir
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
EVAL_DIR = Path(__file__).parent
SCENARIOS_DIR = EVAL_DIR / "scenarios"
RESULTS_DIR = EVAL_DIR / "results"

# ---------------------------------------------------------------------------
# White's system prompt (verbatim from whites.md — the core review persona)
# ---------------------------------------------------------------------------
WHITE_SYSTEM_PROMPT = """You are a senior code reviewer. You analyze diffs before a GitLab MR is opened and produce a structured terminal report. You are thorough, specific, and direct — no filler, no praise for ordinary code.

## Your Review Categories

Every finding must be classified as one of:

- **BLOCKER** — Must be fixed before merging. Bugs, security vulnerabilities, broken logic, missing error handling on critical paths, data loss risk.
- **WARNING** — Should be addressed. Performance issues, unclear logic, missing tests for non-trivial code, deprecated patterns, type safety gaps.
- **SUGGESTION** — Nice to have. Style improvements, better naming, minor refactors, documentation gaps.

## What to review

Review the provided unified diff across five lenses:

### Lens 1: Bugs & Logic Errors
- Off-by-one errors, incorrect conditionals, unreachable code
- Incorrect operator precedence or boolean logic
- Mutation of shared state, race conditions
- Incorrect assumptions about nullability or undefined values
- Wrong function called, wrong argument order
- Edge cases not handled: empty arrays, zero, negative numbers, empty strings
- Async/await misuse: missing awaits, unhandled promises, incorrect error propagation

### Lens 2: Security
- Secrets, tokens, API keys, passwords hardcoded or logged
- SQL injection, NoSQL injection, command injection
- XSS — unsanitized user input rendered as HTML
- Path traversal — user-controlled file paths
- Insecure direct object references — missing authorization checks
- Overly broad CORS, missing CSRF protection
- Sensitive data in logs, error messages, or URLs
- TypeScript/React specific: `dangerouslySetInnerHTML`, `eval()`, unsafe type assertions with `as any`

### Lens 3: Code Style & Conventions
- Naming: variables, functions, and classes should be clear and consistent
- Dead code: commented-out blocks, unused imports, unused variables
- Magic numbers/strings: unexplained literals that should be constants
- TypeScript specific: `any` types, non-null assertions (`!`) without justification

### Lens 4: Performance
- N+1 query patterns (loop containing a DB/API call)
- Missing pagination on potentially large result sets
- Unnecessary re-computation inside loops
- React specific: missing `useMemo`/`useCallback` for expensive computations

### Lens 5: Test Coverage
- New functions or classes with no corresponding test
- Changed logic with no updated tests
- Edge cases in business logic that have no test coverage

## Output format

Output this exact format:

\`\`\`
══════════════════════════════════════════════
  CODE REVIEW REPORT
  Files changed: <N> | Lines added: <+N> | Lines removed: <-N>
══════════════════════════════════════════════

── BLOCKERS (<N>) ──────────────────────────

[B1] <file>:<line> — <one-line summary>
     <Specific explanation of the problem. What is wrong and why it matters.>
     Fix: <Concrete suggestion for how to fix it.>

[B2] ...

── WARNINGS (<N>) ──────────────────────────

[W1] <file>:<line> — <one-line summary>
     <Explanation>
     Suggestion: <What to do>

── SUGGESTIONS (<N>) ───────────────────────

[S1] <file>:<line> — <one-line summary>
     <Explanation>

── VERDICT ─────────────────────────────────

  ✗ NOT READY — <N> blocker(s) must be resolved before merging.

  OR

  ~ NEEDS REVIEW — No blockers, but <N> warning(s) worth addressing.

  OR

  ✓ READY TO MERGE — No blockers or warnings found.

══════════════════════════════════════════════
\`\`\`

Rules for the report:
- Every finding must cite a specific file and line number from the diff
- Be concrete — "this could cause a null pointer exception on line 42 when `user` is undefined" not "handle null values"
- If there are zero findings in a category, omit that section entirely
- Cap suggestions at 5 — prioritize the most impactful ones
- Do not praise ordinary, expected code quality

After the human-readable report, always append a machine-readable verdict block:

\`\`\`
── ORCHESTRATOR SUMMARY ────────────────────────
{"blockers": <N>, "warnings": <N>, "suggestions": <N>, "verdict": "<NOT_READY|NEEDS_REVIEW|READY>"}
────────────────────────────────────────────────
\`\`\`
"""

# ---------------------------------------------------------------------------
# Model config
# ---------------------------------------------------------------------------
MODEL_IDS = {
    "sonnet": "claude-sonnet-4-5",
    "haiku": "claude-haiku-4-5",
}

# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_prompt(diff_content: str, scenario_id: str) -> str:
    return f"""You are reviewing the following code diff before a PR is opened.

**Diff:**
```
{diff_content}
```

Scenario ID: {scenario_id}

Analyze this diff thoroughly and produce your structured CODE REVIEW REPORT."""


# ---------------------------------------------------------------------------
# Output parser
# ---------------------------------------------------------------------------

def parse_output(raw: str) -> dict:
    """Extract blockers, warnings, suggestions, and verdict from White's output."""
    result = {
        "blockers": [],
        "warnings": [],
        "suggestions": [],
        "verdict": "UNKNOWN",
        "orchestrator_json": None,
    }

    # Extract orchestrator JSON
    orch_match = re.search(
        r'ORCHESTRATOR SUMMARY\s*[-─]+\s*(\{[^}]+\})',
        raw, re.DOTALL
    )
    if orch_match:
        try:
            result["orchestrator_json"] = json.loads(orch_match.group(1))
            result["verdict"] = result["orchestrator_json"].get("verdict", "UNKNOWN")
        except json.JSONDecodeError:
            pass

    # Fallback verdict detection
    if result["verdict"] == "UNKNOWN":
        if "NOT_READY" in raw or "NOT READY" in raw:
            result["verdict"] = "NOT_READY"
        elif "NEEDS_REVIEW" in raw or "NEEDS REVIEW" in raw:
            result["verdict"] = "NEEDS_REVIEW"
        elif "READY TO MERGE" in raw or "READY" in raw:
            result["verdict"] = "READY"

    # Extract blockers
    blocker_section = re.search(
        r'BLOCKERS\s*\([^)]*\)\s*[-─]+(.+?)(?:WARNINGS|SUGGESTIONS|VERDICT|ORCHESTRATOR|══)',
        raw, re.DOTALL | re.IGNORECASE
    )
    if blocker_section:
        result["blockers"] = _parse_findings(blocker_section.group(1), "B")

    # Extract warnings
    warning_section = re.search(
        r'WARNINGS\s*\([^)]*\)\s*[-─]+(.+?)(?:SUGGESTIONS|VERDICT|ORCHESTRATOR|══)',
        raw, re.DOTALL | re.IGNORECASE
    )
    if warning_section:
        result["warnings"] = _parse_findings(warning_section.group(1), "W")

    # Extract suggestions
    suggestion_section = re.search(
        r'SUGGESTIONS\s*\([^)]*\)\s*[-─]+(.+?)(?:VERDICT|ORCHESTRATOR|══)',
        raw, re.DOTALL | re.IGNORECASE
    )
    if suggestion_section:
        result["suggestions"] = _parse_findings(suggestion_section.group(1), "S")

    return result


def _parse_findings(section_text: str, prefix: str) -> list:
    """Parse individual finding entries from a section."""
    findings = []
    # Match [B1], [W2], [S3] etc.
    pattern = rf'\[{prefix}\d+\]\s+(.+?)(?=\[{prefix}\d+\]|$)'
    matches = re.findall(pattern, section_text, re.DOTALL)
    for m in matches:
        lines = m.strip().split('\n')
        title_line = lines[0].strip() if lines else ""
        body = "\n".join(l.strip() for l in lines[1:] if l.strip())
        findings.append({
            "title": title_line,
            "body": body,
            "raw": m.strip(),
        })
    return findings


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------

def score_scenario(parsed: dict, ground_truth: dict) -> dict:
    """Score parsed output against ground truth. Returns score breakdown."""
    bugs = ground_truth.get("planted_bugs", [])
    clean_elements = ground_truth.get("clean_elements", [])

    all_findings_text = _get_all_findings_text(parsed)
    bug_scores = {}

    for bug in bugs:
        bug_id = bug["bug_id"]
        score = _score_bug(bug, parsed, all_findings_text)
        bug_scores[bug_id] = score

    # Detection rate
    if bugs:
        detection_rate = sum(s["credit"] for s in bug_scores.values()) / len(bugs)
    else:
        detection_rate = 1.0

    # Severity accuracy — only for found bugs
    found_bugs = [b for b in bugs if bug_scores[b["bug_id"]]["found"]]
    if found_bugs:
        severity_scores = [bug_scores[b["bug_id"]]["severity_correct"] for b in found_bugs]
        severity_accuracy = sum(severity_scores) / len(severity_scores)
    else:
        severity_accuracy = 0.0

    # False positive rate — blockers that don't match any planted bug
    total_blockers = len(parsed.get("blockers", []))
    matched_blocker_count = sum(
        1 for b in bugs
        if bug_scores[b["bug_id"]]["found"] and b.get("severity") == "blocker"
    )
    fp_blockers = max(0, total_blockers - matched_blocker_count)

    # Also check clean elements for false positives
    for clean in clean_elements:
        if _is_false_positive(clean, parsed, all_findings_text):
            fp_blockers += 1

    total_clean = len(clean_elements) + 1  # +1 to avoid div/0
    fp_rate = fp_blockers / total_clean

    # Composite
    composite = (
        0.50 * detection_rate
        + 0.30 * severity_accuracy
        + 0.20 * max(0.0, 1.0 - fp_rate * 2)
    )

    return {
        "detection_rate": round(detection_rate, 3),
        "severity_accuracy": round(severity_accuracy, 3),
        "fp_rate": round(fp_rate, 3),
        "fp_blockers": fp_blockers,
        "composite": round(composite, 3),
        "bug_scores": bug_scores,
    }


def _get_all_findings_text(parsed: dict) -> str:
    """Concatenate all finding text for keyword search."""
    parts = []
    for finding in parsed.get("blockers", []) + parsed.get("warnings", []) + parsed.get("suggestions", []):
        parts.append(finding.get("title", "") + " " + finding.get("body", ""))
    return " ".join(parts).lower()


def _score_bug(bug: dict, parsed: dict, all_findings_text: str) -> dict:
    """
    Determine if a bug was found and how much credit to award.
    Uses keyword matching against expected_finding text + location hints.
    """
    expected = bug.get("expected_finding", "").lower()
    location = bug.get("location", "").lower()
    description = bug.get("description", "").lower()
    scoring = bug.get("scoring", {})

    # Extract keywords from location and description
    keywords = _extract_keywords(bug)

    # Check for full credit criteria
    full_credit_text = scoring.get("full_credit_if", "").lower()
    partial_credit_text = scoring.get("partial_credit_if", "").lower()
    no_credit_text = scoring.get("no_credit_if", "").lower()

    # Score the detection
    keyword_hits = sum(1 for kw in keywords if kw in all_findings_text)
    keyword_hit_rate = keyword_hits / len(keywords) if keywords else 0.0

    found = keyword_hit_rate >= 0.4  # At least 40% of keywords present
    credit = 0.0

    if found:
        if keyword_hit_rate >= 0.7:
            credit = 1.0  # Strong match = full credit
        else:
            credit = 0.5  # Weak match = partial credit

    # Severity accuracy
    expected_severity = bug.get("severity", "blocker")
    severity_correct = 0.0
    if found:
        # Check which section the finding appeared in
        if expected_severity == "blocker":
            in_blockers = any(
                sum(1 for kw in keywords if kw in (f.get("title","") + f.get("body","")).lower()) >= len(keywords) * 0.4
                for f in parsed.get("blockers", [])
            )
            in_warnings = any(
                sum(1 for kw in keywords if kw in (f.get("title","") + f.get("body","")).lower()) >= len(keywords) * 0.4
                for f in parsed.get("warnings", [])
            )
            if in_blockers:
                severity_correct = 1.0
            elif in_warnings:
                severity_correct = 0.5  # Off by one level
            else:
                severity_correct = 0.5  # Found but in suggestions or unclear
        elif expected_severity == "warning":
            in_warnings = any(
                sum(1 for kw in keywords if kw in (f.get("title","") + f.get("body","")).lower()) >= len(keywords) * 0.4
                for f in parsed.get("warnings", [])
            )
            in_blockers = any(
                sum(1 for kw in keywords if kw in (f.get("title","") + f.get("body","")).lower()) >= len(keywords) * 0.4
                for f in parsed.get("blockers", [])
            )
            in_suggestions = any(
                sum(1 for kw in keywords if kw in (f.get("title","") + f.get("body","")).lower()) >= len(keywords) * 0.4
                for f in parsed.get("suggestions", [])
            )
            if in_warnings:
                severity_correct = 1.0
            elif in_blockers or in_suggestions:
                severity_correct = 0.5
            else:
                severity_correct = 0.5

    return {
        "found": found,
        "credit": credit,
        "severity_correct": severity_correct,
        "keyword_hit_rate": round(keyword_hit_rate, 2),
    }


def _extract_keywords(bug: dict) -> list:
    """Extract discriminating keywords from bug metadata for matching."""
    category = bug.get("category", "")
    location = bug.get("location", "")
    description = bug.get("description", "")
    expected = bug.get("expected_finding", "")

    # Category-specific keywords
    category_keywords = {
        "null_dereference": ["null", "undefined", "findone", "null check", "null pointer"],
        "sql_injection": ["sql", "injection", "interpolat", "parameterized", "sanitize"],
        "off_by_one": ["off-by-one", "offset", "pagination", "(page - 1)", "page * limit", "1-indexed"],
        "n_plus_one": ["n+1", "n+1", "loop", "batch", "nested", "query in a loop"],
        "circular_dependency": ["circular", "cycle", "circular dependency", "cartstore", "userstore"],
        "missing_error_handling": ["error handling", "try/catch", "throw", "unhandled", "catch"],
        "security": ["sql injection", "xss", "pii", "console.log", "sensitive", "log"],
        "bug": ["result.rows", "analytics", "wrong property", "undefined"],
        "missing_validation": ["validation", "validate", "page >= 1", "negative", "invalid"],
    }

    keywords = category_keywords.get(category, [])

    # Add file-specific keywords from location
    if "userProfile" in location:
        keywords += ["userprofile", "findone", "user"]
    if "search.ts" in location:
        keywords += ["search", "query", "sql"]
    if "posts.ts" in location:
        keywords += ["posts", "pagination", "offset", "page"]
    if "dashboard.ts" in location:
        keywords += ["dashboard", "order", "product"]
    if "CartStore" in location or "UserStore" in location:
        keywords += ["cart", "user", "import", "module"]

    return list(set(kw.lower() for kw in keywords if kw))


def _is_false_positive(clean: dict, parsed: dict, all_findings_text: str) -> bool:
    """Check if a clean element was incorrectly flagged as a blocker."""
    fp_criteria = clean.get("false_positive_if", "").lower()
    if not fp_criteria:
        return False

    # Extract the key subject from false_positive_if
    # e.g. "White flags joinedAt.toLocaleDateString() as a blocker"
    subjects = re.findall(r'`([^`]+)`', fp_criteria)
    if not subjects:
        # Try to extract meaningful terms
        words = fp_criteria.split()
        subjects = [w for w in words if len(w) > 5 and w not in
                    {"flags", "white", "blocker", "warning", "issue"}]

    for subject in subjects:
        subject_lower = subject.lower()
        for finding in parsed.get("blockers", []):
            finding_text = (finding.get("title", "") + " " + finding.get("body", "")).lower()
            if subject_lower in finding_text:
                return True

    return False


# ---------------------------------------------------------------------------
# API caller
# ---------------------------------------------------------------------------

def call_claude(model_key: str, system_prompt: str, user_prompt: str,
                dry_run: bool = False, timeout: int = 300) -> tuple[str, dict]:
    """Call claude CLI and return (raw_output, metadata)."""
    model_id = MODEL_IDS[model_key]
    start = time.time()

    if dry_run:
        print(f"\n{'='*60}")
        print(f"[DRY RUN] Model: {model_id}")
        print(f"[DRY RUN] System prompt length: {len(system_prompt)} chars")
        print(f"[DRY RUN] User prompt length: {len(user_prompt)} chars")
        print(f"[DRY RUN] First 200 chars of user prompt:")
        print(user_prompt[:200])
        print(f"{'='*60}\n")
        return "[DRY RUN — no API call made]", {"latency_ms": 0, "model_id": model_id}

    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    try:
        result = subprocess.run(
            ["claude", "-p", "--model", model_id],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        latency_ms = int((time.time() - start) * 1000)

        if result.returncode != 0:
            stderr = result.stderr.strip()
            print(f"  [WARN] claude returned non-zero exit code: {result.returncode}", file=sys.stderr)
            if stderr:
                print(f"  [WARN] stderr: {stderr[:200]}", file=sys.stderr)

        raw = result.stdout.strip()
        return raw, {"latency_ms": latency_ms, "model_id": model_id}

    except subprocess.TimeoutExpired:
        return f"[TIMEOUT after {timeout}s]", {"latency_ms": timeout * 1000, "model_id": model_id}
    except FileNotFoundError:
        print("[ERROR] 'claude' CLI not found. Is Claude Code installed?", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Result storage
# ---------------------------------------------------------------------------

def save_result(run_dir: Path, scenario_id: str, model: str, data: dict):
    scenario_dir = run_dir / scenario_id
    scenario_dir.mkdir(parents=True, exist_ok=True)
    out_path = scenario_dir / f"{model}.json"
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Saved: {out_path}")


def load_result(run_dir: Path, scenario_id: str, model: str) -> Optional[dict]:
    path = run_dir / scenario_id / f"{model}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------

def generate_report(run_dir: Path, scenarios: list, models: list) -> str:
    """Generate COMPARISON-REPORT.md from scored results."""

    aggregate = {m: {"composites": [], "detections": [], "fps": [], "severities": []} for m in models}
    per_scenario_rows = []

    for scenario_id in scenarios:
        row = {"scenario": scenario_id, "models": {}}
        for model in models:
            result = load_result(run_dir, scenario_id, model)
            if result and "scores" in result:
                s = result["scores"]
                row["models"][model] = s
                aggregate[model]["composites"].append(s["composite"])
                aggregate[model]["detections"].append(s["detection_rate"])
                aggregate[model]["fps"].append(s["fp_rate"])
                aggregate[model]["severities"].append(s["severity_accuracy"])
            else:
                row["models"][model] = None
        per_scenario_rows.append(row)

    # Compute aggregates
    agg_summary = {}
    for model in models:
        a = aggregate[model]
        if a["composites"]:
            agg_summary[model] = {
                "composite": round(sum(a["composites"]) / len(a["composites"]), 3),
                "detection": round(sum(a["detections"]) / len(a["detections"]), 3),
                "fp_rate": round(sum(a["fps"]) / len(a["fps"]), 3),
                "severity": round(sum(a["severities"]) / len(a["severities"]), 3),
            }
        else:
            agg_summary[model] = {"composite": 0, "detection": 0, "fp_rate": 0, "severity": 0}

    # Thresholds
    THRESHOLDS = {
        "composite": 0.85,
        "detection": 0.80,
        "fp_rate": 0.20,  # must be <=
        "severity": 0.75,
    }

    def verdict_for_model(model):
        s = agg_summary.get(model, {})
        passes = (
            s.get("composite", 0) >= THRESHOLDS["composite"]
            and s.get("detection", 0) >= THRESHOLDS["detection"]
            and s.get("fp_rate", 1) <= THRESHOLDS["fp_rate"]
            and s.get("severity", 0) >= THRESHOLDS["severity"]
        )
        return "PASS" if passes else "FAIL"

    # Build report
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# White Agent Eval — Sonnet vs Haiku Comparison Report",
        f"**Run**: `{run_dir.name}`  ",
        f"**Date**: {now}  ",
        f"**Scenarios**: {len(scenarios)}  ",
        f"**Models**: {', '.join(models)}",
        "",
        "---",
        "",
        "## Decision",
        "",
    ]

    haiku_verdict = verdict_for_model("haiku") if "haiku" in models else "N/A"
    if haiku_verdict == "PASS":
        lines += [
            "**RECOMMENDATION: Downgrade White to Haiku.**",
            "",
            "Haiku meets all four thresholds for code review quality. The cost reduction is justified.",
            "",
        ]
    elif haiku_verdict == "FAIL":
        lines += [
            "**RECOMMENDATION: Keep White at Sonnet.**",
            "",
            "Haiku does not meet one or more pass thresholds. Downgrade risks missing real issues in production PRs.",
            "",
        ]
    else:
        lines += ["**RECOMMENDATION: Incomplete data — rerun eval.**", ""]

    lines += [
        "---",
        "",
        "## Aggregate Scores",
        "",
        "| Metric | Sonnet | Haiku | Threshold | Pass/Fail |",
        "|--------|--------|-------|-----------|-----------|",
    ]

    metric_labels = [
        ("composite", "Composite Score", "≥ 0.85"),
        ("detection", "Detection Rate", "≥ 0.80"),
        ("severity", "Severity Accuracy", "≥ 0.75"),
        ("fp_rate", "False Positive Rate", "≤ 0.20"),
    ]

    for key, label, threshold in metric_labels:
        sonnet_val = agg_summary.get("sonnet", {}).get(key, "—")
        haiku_val = agg_summary.get("haiku", {}).get(key, "—")

        def fmt(v, k):
            if isinstance(v, float):
                is_pass = (v <= THRESHOLDS[k] if k == "fp_rate" else v >= THRESHOLDS[k])
                marker = "✓" if is_pass else "✗"
                return f"{v:.3f} {marker}"
            return str(v)

        lines.append(f"| {label} | {fmt(sonnet_val, key)} | {fmt(haiku_val, key)} | {threshold} | {'PASS' if haiku_verdict == 'PASS' else '—'} |")

    lines += [
        "",
        "---",
        "",
        "## Per-Scenario Breakdown",
        "",
        "| Scenario | Difficulty | Sonnet Composite | Haiku Composite | Sonnet Detection | Haiku Detection |",
        "|----------|------------|-----------------|-----------------|-----------------|-----------------|",
    ]

    difficulties = {
        "scenario-01": "easy",
        "scenario-02": "easy",
        "scenario-03": "medium",
        "scenario-04": "medium",
        "scenario-05": "hard",
    }

    for row in per_scenario_rows:
        sid = row["scenario"]
        diff_label = difficulties.get(sid, "—")
        sonnet_s = row["models"].get("sonnet")
        haiku_s = row["models"].get("haiku")

        def fmts(s, key):
            return f"{s[key]:.3f}" if s and key in s else "—"

        lines.append(
            f"| {sid} | {diff_label} "
            f"| {fmts(sonnet_s, 'composite')} "
            f"| {fmts(haiku_s, 'composite')} "
            f"| {fmts(sonnet_s, 'detection_rate')} "
            f"| {fmts(haiku_s, 'detection_rate')} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Per-Bug Detection",
        "",
        "Shows whether each planted bug was caught by each model.",
        "",
    ]

    scenario_metadata = {
        "scenario-01": ("easy", [("bug-01", "Null deref (findOne)", "blocker"), ("bug-02", "PII in console.log", "blocker")]),
        "scenario-02": ("easy", [("bug-01", "SQL injection (search)", "blocker"), ("bug-02", "SQL injection (autocomplete)", "blocker"), ("bug-03", "result.analytics bug", "blocker")]),
        "scenario-03": ("medium", [("bug-01", "Off-by-one offset", "blocker"), ("bug-02", "Missing page >= 1 validation", "warning")]),
        "scenario-04": ("medium", [("bug-01", "N+1 query pattern", "warning"), ("bug-02", "Null deref on findById", "blocker")]),
        "scenario-05": ("hard", [("bug-01", "Circular dependency", "blocker"), ("bug-02", "Missing error handling in login()", "warning")]),
    }

    lines += [
        "| Scenario | Bug | Expected Severity | Sonnet Found | Haiku Found |",
        "|----------|-----|------------------|-------------|-------------|",
    ]

    for sid, (diff_label, bugs) in scenario_metadata.items():
        for bug_id, bug_desc, severity in bugs:
            sonnet_r = load_result(run_dir, sid, "sonnet")
            haiku_r = load_result(run_dir, sid, "haiku")

            def bug_found(result, bid):
                if not result or "scores" not in result:
                    return "—"
                bs = result["scores"].get("bug_scores", {})
                if bid in bs:
                    return "✓" if bs[bid]["found"] else "✗"
                return "—"

            lines.append(
                f"| {sid} | {bug_desc} | {severity} "
                f"| {bug_found(sonnet_r, bug_id)} "
                f"| {bug_found(haiku_r, bug_id)} |"
            )

    lines += [
        "",
        "---",
        "",
        "## Analysis",
        "",
    ]

    if "haiku" in agg_summary and "sonnet" in agg_summary:
        h = agg_summary["haiku"]
        s = agg_summary["sonnet"]
        detection_gap = round(s["detection"] - h["detection"], 3)
        composite_gap = round(s["composite"] - h["composite"], 3)

        lines += [
            f"**Detection gap (Sonnet − Haiku)**: {detection_gap:+.3f}",
            f"**Composite gap**: {composite_gap:+.3f}",
            "",
        ]

        if haiku_verdict == "FAIL":
            # Identify where Haiku failed
            failed_metrics = []
            if h["composite"] < THRESHOLDS["composite"]:
                failed_metrics.append(f"composite ({h['composite']:.3f} < 0.85)")
            if h["detection"] < THRESHOLDS["detection"]:
                failed_metrics.append(f"detection rate ({h['detection']:.3f} < 0.80)")
            if h["fp_rate"] > THRESHOLDS["fp_rate"]:
                failed_metrics.append(f"false positive rate ({h['fp_rate']:.3f} > 0.20)")
            if h["severity"] < THRESHOLDS["severity"]:
                failed_metrics.append(f"severity accuracy ({h['severity']:.3f} < 0.75)")

            if failed_metrics:
                lines += [
                    "**Haiku failed on**: " + ", ".join(failed_metrics),
                    "",
                    "These gaps indicate Haiku lacks the reasoning depth required for reliable pre-PR review.",
                    "Recommend keeping White at Sonnet until a targeted eval shows improvement on these metrics.",
                ]
        else:
            lines += [
                "Haiku meets all thresholds. The detection gap is within acceptable tolerance.",
                "Downgrading White to Haiku is safe for production use.",
            ]

    lines += [
        "",
        "---",
        "",
        "## Thresholds Reference",
        "",
        "| Metric | Threshold | Rationale |",
        "|--------|-----------|-----------|",
        "| Composite Score | ≥ 0.85 | Same bar as Politico eval (gold-eval-0331 baseline) |",
        "| Detection Rate | ≥ 0.80 | Missing 1 in 5 bugs is the upper tolerance for a quality gate |",
        "| Severity Accuracy | ≥ 0.75 | Misclassifying blockers as warnings has direct workflow impact |",
        "| False Positive Rate | ≤ 0.20 | Over-blocking wastes developer time and erodes trust |",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def get_scenarios(scenario_filter: Optional[str]) -> list:
    if scenario_filter:
        return [scenario_filter]
    # Auto-discover
    return sorted([
        d.name for d in SCENARIOS_DIR.iterdir()
        if d.is_dir() and (d / "diff.patch").exists()
    ])


def get_models(model_filter: str) -> list:
    if model_filter == "both":
        return ["sonnet", "haiku"]
    return [model_filter]


def run_eval(args):
    scenarios = get_scenarios(args.scenario)
    models = get_models(args.model)

    if not scenarios:
        print("[ERROR] No scenarios found. Check scenarios/ directory.", file=sys.stderr)
        sys.exit(1)

    # Create run directory
    run_id = datetime.now().strftime("run-%Y%m%d-%H%M%S")
    run_dir = (Path(args.results_dir) if args.results_dir else RESULTS_DIR) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Run ID: {run_id}")
    print(f"Scenarios: {scenarios}")
    print(f"Models: {models}")
    print(f"Results dir: {run_dir}")
    print()

    for scenario_id in scenarios:
        scenario_dir = SCENARIOS_DIR / scenario_id
        diff_path = scenario_dir / "diff.patch"
        gt_path = scenario_dir / "ground-truth.yaml"

        if not diff_path.exists():
            print(f"[SKIP] {scenario_id}: no diff.patch found")
            continue
        if not gt_path.exists():
            print(f"[SKIP] {scenario_id}: no ground-truth.yaml found")
            continue

        diff_content = diff_path.read_text()
        ground_truth = yaml.safe_load(gt_path.read_text())

        for model in models:
            print(f"Running {model} on {scenario_id}...")

            user_prompt = build_prompt(diff_content, scenario_id)
            raw_output, meta = call_claude(
                model,
                WHITE_SYSTEM_PROMPT,
                user_prompt,
                dry_run=args.dry_run,
            )

            if args.dry_run:
                continue

            parsed = parse_output(raw_output)
            scores = score_scenario(parsed, ground_truth)

            result = {
                "scenario_id": scenario_id,
                "model": model,
                "model_id": meta["model_id"],
                "raw_output": raw_output,
                "parsed": parsed,
                "scores": scores,
                "latency_ms": meta["latency_ms"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            save_result(run_dir, scenario_id, model, result)

            print(f"  composite={scores['composite']:.3f} "
                  f"detection={scores['detection_rate']:.3f} "
                  f"fp={scores['fp_rate']:.3f}")

    if args.dry_run:
        print("[DRY RUN complete — no results written]")
        return

    # Generate report
    print("\nGenerating comparison report...")
    report = generate_report(run_dir, scenarios, models)
    report_path = run_dir / "COMPARISON-REPORT.md"
    report_path.write_text(report)
    print(f"Report: {report_path}")

    # Also copy to canonical location
    canonical = EVAL_DIR / "results" / "COMPARISON-REPORT.md"
    canonical.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_text(report)
    print(f"Canonical copy: {canonical}")


def score_only(args):
    """Re-score an existing results directory."""
    if not args.results_dir:
        print("[ERROR] --score-only requires --results-dir", file=sys.stderr)
        sys.exit(1)

    run_dir = Path(args.results_dir)
    scenarios = get_scenarios(args.scenario)
    models = get_models(args.model)

    for scenario_id in scenarios:
        gt_path = SCENARIOS_DIR / scenario_id / "ground-truth.yaml"
        if not gt_path.exists():
            continue
        ground_truth = yaml.safe_load(gt_path.read_text())

        for model in models:
            result = load_result(run_dir, scenario_id, model)
            if not result:
                print(f"[SKIP] {scenario_id}/{model}: no result file")
                continue

            parsed = parse_output(result["raw_output"])
            scores = score_scenario(parsed, ground_truth)
            result["scores"] = scores
            result["parsed"] = parsed
            save_result(run_dir, scenario_id, model, result)
            print(f"Re-scored {scenario_id}/{model}: composite={scores['composite']:.3f}")

    report = generate_report(run_dir, scenarios, models)
    report_path = run_dir / "COMPARISON-REPORT.md"
    report_path.write_text(report)
    print(f"Report: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="White agent eval harness")
    parser.add_argument("--model", default="both", choices=["sonnet", "haiku", "both"])
    parser.add_argument("--scenario", default=None, help="Scenario ID (e.g. white-01) or omit for all")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts, no API calls")
    parser.add_argument("--score-only", action="store_true", help="Re-score existing results")
    parser.add_argument("--results-dir", default=None, help="Override results directory")
    args = parser.parse_args()

    if args.score_only:
        score_only(args)
    else:
        run_eval(args)


if __name__ == "__main__":
    main()
