#!/usr/bin/env python3
"""
Politico Agent Evaluation Harness
Runs Politico (Sonnet and Haiku) against test scenarios and scores the output.

Usage:
    python3 evaluation/politico-eval/run-eval.py
    python3 evaluation/politico-eval/run-eval.py --model sonnet
    python3 evaluation/politico-eval/run-eval.py --scenario scenario-01
    python3 evaluation/politico-eval/run-eval.py --dry-run
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import subprocess
import yaml

# ── Constants ────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent.resolve()
SCENARIOS_DIR = SCRIPT_DIR / "scenarios"
RESULTS_DIR = SCRIPT_DIR / "results"

MODEL_SONNET = "claude-sonnet-4-6-20250320"
MODEL_HAIKU = "claude-haiku-4-5-20251001"

MODEL_NAMES = {
    MODEL_SONNET: "sonnet",
    MODEL_HAIKU: "haiku",
}

MAX_TOKENS = 2000

PASS_THRESHOLDS = {
    "composite": 0.85,
    "detection": 0.80,
    "fp_rate": 0.20,   # must be AT OR BELOW this value
    "severity": 0.75,
}

# Verbatim Politico system prompt from ~/.claude/agents/politicos.md
POLITICO_SYSTEM_PROMPT = """You are Politico — the Spectrum Protocol's adversarial reviewer. You run in Phase 1.5 (The Passage), between Gold writing MANIFEST.md/CONTRACT.md and Howler drop. Your job is to find problems Gold missed. You are independent from Gold and you are not trying to be agreeable.

## What You Review

Read MANIFEST.md and CONTRACT.md in the spectrum directory. Then attack them across three axes:

### 1. File Ownership Gaps
- Are there files that Howlers will obviously need to create or modify that are NOT in the ownership matrix?
- Will any Howler need to read a file owned by another Howler and potentially need to modify it too?
- Are there implicit shared files (e.g., index.ts barrel exports, route registrations, config files) that multiple Howlers will touch?

### 2. Contract Ambiguities
- Are there interface definitions vague enough that two Howlers could implement incompatible versions?
- Are error handling contracts specified? What happens when an API call fails?
- Are there naming conventions that seem obvious but could be interpreted differently?
- For each seam (integration point), is it clear enough that both sides could implement independently and connect correctly?

### 3. Decomposition Flaws
- Are there tasks marked parallel that have hidden sequential dependencies?
- Is any single task significantly larger than the others (critical-path risk)?
- Are there tasks that should be split because they span multiple logical concerns?
- Is there a task that synthesizes outputs from multiple Howlers that isn't modeled as a sequential integration step?

## Output Format

```
# Politico Review
_Rain ID: [id] | Reviewed: [date]_

## Blockers (must address before drop)

### [Issue title]
**Category**: Ownership Gap / Contract Ambiguity / Decomposition Flaw
**Finding**: [What the problem is]
**Risk**: [What goes wrong during the run if this isn't fixed]
**Suggested fix**: [Concrete change to MANIFEST.md or CONTRACT.md]

## Warnings (should address)

### [Issue title]
[Same format, lower severity]

## Accepted (no action needed)
[Anything you considered but concluded is actually fine — shows your reasoning]

## Verdict
BLOCKED — [N] blocker(s) must be resolved before drop.
OR
CLEAR — No blockers found. [N] warnings noted.
```

## Rules

- Be specific — vague concerns are useless. Point to exact section/field/interface that has the problem.
- Suggest fixes, not just problems — Gold needs to act on your findings.
- Don't invent problems — if something is actually fine, say so in the Accepted section.
- You are not Gold's editor — don't flag style or phrasing. Only flag things that could cause Howler failures or seam mismatches.
- After Gold addresses your blockers, re-read the updated artifacts and confirm each blocker is resolved before clearing the run."""


# ── Prompt Builder ────────────────────────────────────────────────────────────

def build_prompt(manifest_content: str, contract_content: str, scenario_id: str) -> str:
    """Construct the Politico user-turn prompt per PLAN.md §7.4."""
    return (
        f"You are reviewing the following spectrum artifacts:\n\n"
        f"**MANIFEST.md**\n---\n{manifest_content}\n---\n\n"
        f"**CONTRACT.md**\n---\n{contract_content}\n---\n\n"
        f"Rain ID: {scenario_id}"
    )


# ── Output Parser ─────────────────────────────────────────────────────────────

def _extract_section(text: str, heading: str) -> str:
    """Extract the text under a ## heading until the next ## heading."""
    pattern = rf"##\s+{re.escape(heading)}.*?\n(.*?)(?=\n##\s|\Z)"
    m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _parse_findings(section_text: str) -> list[dict]:
    """
    Parse individual findings from a Blockers or Warnings section.
    Each finding starts with '### Title'.
    """
    if not section_text:
        return []

    findings = []
    # Split on ### headings
    chunks = re.split(r"\n###\s+", "\n" + section_text)
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        lines = chunk.split("\n", 1)
        title = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""

        # Extract structured fields
        category_m = re.search(r"\*\*Category\*\*:\s*(.+)", body, re.IGNORECASE)
        finding_m = re.search(r"\*\*Finding\*\*:\s*(.+?)(?=\*\*|\Z)", body, re.IGNORECASE | re.DOTALL)
        fix_m = re.search(r"\*\*Suggested fix\*\*:\s*(.+?)(?=\*\*|\Z)", body, re.IGNORECASE | re.DOTALL)

        category_raw = category_m.group(1).strip() if category_m else "unknown"
        # Normalize category to one of the three canonical values
        category = _normalize_category(category_raw)

        finding = {
            "title": title,
            "category": category,
            "finding_text": finding_m.group(1).strip() if finding_m else body,
            "suggested_fix": fix_m.group(1).strip() if fix_m else "",
        }
        findings.append(finding)

    return findings


def _normalize_category(raw: str) -> str:
    """Map free-text category to canonical slug."""
    lower = raw.lower()
    if "ownership" in lower or "gap" in lower:
        return "ownership_gap"
    if "ambiguit" in lower or "contract" in lower:
        return "contract_ambiguity"
    if "decomposition" in lower or "flaw" in lower or "sequential" in lower:
        return "decomposition_flaw"
    return "unknown"


def _parse_accepted(text: str) -> list[str]:
    """Extract accepted items (bullet or sub-heading list)."""
    section = _extract_section(text, "Accepted")
    if not section:
        return []
    items = []
    for line in section.splitlines():
        line = line.strip()
        if line.startswith(("-", "*", "•")) or re.match(r"^\d+\.", line):
            items.append(re.sub(r"^[-*•\d.]+\s*", "", line).strip())
        elif line and not line.startswith("#"):
            items.append(line)
    return [i for i in items if i]


def _parse_verdict(text: str) -> str:
    """Extract BLOCKED or CLEAR verdict."""
    verdict_section = _extract_section(text, "Verdict")
    combined = (verdict_section + "\n" + text[-500:]).upper()
    if "BLOCKED" in combined:
        return "BLOCKED"
    if "CLEAR" in combined:
        return "CLEAR"
    return "UNKNOWN"


def parse_output(raw_output: str) -> dict:
    """
    Parse a Politico response into structured findings.
    Returns parsed dict plus parse_confidence.
    """
    blockers_section = _extract_section(raw_output, "Blockers")
    warnings_section = _extract_section(raw_output, "Warnings")

    blockers = _parse_findings(blockers_section)
    warnings = _parse_findings(warnings_section)
    accepted = _parse_accepted(raw_output)
    verdict = _parse_verdict(raw_output)

    # Assess parse confidence based on what we successfully found
    expected_sections = ["Blockers", "Warnings", "Verdict"]
    found = sum([
        bool(blockers_section),
        bool(warnings_section),
        verdict != "UNKNOWN",
    ])
    parse_confidence = round(found / len(expected_sections), 2)

    return {
        "blockers": blockers,
        "warnings": warnings,
        "verdict": verdict,
        "accepted": accepted,
        "_parse_confidence": parse_confidence,
    }


# ── Scorer ────────────────────────────────────────────────────────────────────

def _finding_matches_bug(finding: dict, bug: dict) -> bool:
    """
    Heuristic: does this parsed finding correspond to this planted bug?
    Match on: key words from expected_finding + location + category.
    """
    expected_text = bug.get("expected_finding", "").lower()
    location = bug.get("location", "").lower()
    bug_category = bug.get("category", "").lower()

    finding_text = (
        finding.get("title", "") + " " +
        finding.get("finding_text", "") + " " +
        finding.get("suggested_fix", "")
    ).lower()

    finding_category = finding.get("category", "").lower()

    # Extract key nouns from expected_finding (filenames, interface names, Howler names)
    # Match at least 2 key words to avoid spurious matches
    key_words = re.findall(r'[a-z][a-z0-9_\-\.]{2,}', expected_text)
    # Filter to more distinctive tokens
    stop_words = {"the", "and", "for", "that", "this", "with", "from", "have",
                  "should", "flag", "file", "howler", "politico", "correct",
                  "named", "both", "any", "all", "not", "are", "can", "will",
                  "could", "need", "must", "each", "also", "into", "they",
                  "uses", "needs", "which", "would", "about"}
    key_words = [w for w in key_words if w not in stop_words and len(w) > 3]

    # De-duplicate and take up to 10 most distinctive
    seen = set()
    unique_keys = []
    for w in key_words:
        if w not in seen:
            seen.add(w)
            unique_keys.append(w)
    key_words = unique_keys[:10]

    if not key_words:
        return False

    matches = sum(1 for kw in key_words if kw in finding_text)
    match_ratio = matches / len(key_words)

    # Also check location keywords
    location_words = [w for w in re.findall(r'[a-z][a-z0-9_\-\.]{2,}', location) if w not in stop_words]
    location_match = any(lw in finding_text for lw in location_words) if location_words else False

    # Category match
    category_match = (bug_category in finding_category or finding_category in bug_category)

    # A finding matches if it hits enough keyword coverage OR explicit location + category
    return match_ratio >= 0.25 or (location_match and category_match)


def _credit_for_finding(finding: dict, bug: dict) -> float:
    """
    Apply partial credit rules from PLAN.md §6.1:
      1.0 — full credit criteria met (correct category + concrete fix)
      0.75 — correct finding, no fix
      0.5 — names file/issue but wrong category
      0.0 — not found
    The caller already confirmed this finding matches the bug.
    """
    expected_category = bug.get("category", "").lower()
    finding_category = finding.get("category", "").lower()
    has_fix = bool(finding.get("suggested_fix", "").strip())

    category_correct = (expected_category in finding_category or finding_category in expected_category)

    if category_correct and has_fix:
        return 1.0
    if category_correct and not has_fix:
        return 0.75
    # Wrong category but still named the file/issue (we only get here when matched)
    return 0.5


def _severity_credit(finding_severity: str, bug_severity: str) -> float:
    """
    Per PLAN.md §6.1:
      1.0 — exact match
      0.5 — off by one level
      0.0 — completely wrong (blocker↔observation)
    """
    order = {"blocker": 0, "warning": 1, "observation": 2}
    f = order.get(finding_severity.lower(), 1)
    b = order.get(bug_severity.lower(), 1)
    diff = abs(f - b)
    if diff == 0:
        return 1.0
    if diff == 1:
        return 0.5
    return 0.0


def score_scenario(parsed: dict, ground_truth: dict) -> dict:
    """
    Score one model's parsed output against a scenario's ground truth.
    Returns the full scores dict matching the result JSON schema.
    """
    planted_bugs = ground_truth.get("planted_bugs", [])
    clean_elements = ground_truth.get("clean_elements", [])

    all_findings = (
        [("blocker", f) for f in parsed.get("blockers", [])] +
        [("warning", f) for f in parsed.get("warnings", [])]
    )

    bug_scores = {}
    matched_finding_indices = set()
    severity_credits = []

    for bug in planted_bugs:
        bug_id = bug["bug_id"]
        bug_severity = bug.get("severity", "warning")

        best_credit = 0.0
        best_severity_credit = 0.0
        found = False

        for idx, (sev_label, finding) in enumerate(all_findings):
            if idx in matched_finding_indices:
                continue
            if _finding_matches_bug(finding, bug):
                credit = _credit_for_finding(finding, bug)
                sev_credit = _severity_credit(sev_label, bug_severity)
                if credit > best_credit:
                    best_credit = credit
                    best_severity_credit = sev_credit
                    found = True
                    best_idx = idx

        if found:
            matched_finding_indices.add(best_idx)
            severity_credits.append(best_severity_credit)
        else:
            severity_credits.append(0.0)

        bug_scores[bug_id] = {
            "found": found,
            "credit": best_credit,
            "severity_correct": best_severity_credit == 1.0,
        }

    # Detection rate
    if planted_bugs:
        detection_rate = sum(bs["credit"] for bs in bug_scores.values()) / len(planted_bugs)
    else:
        detection_rate = 0.0

    # Severity accuracy (only over matched findings)
    found_count = sum(1 for bs in bug_scores.values() if bs["found"])
    if found_count > 0:
        severity_accuracy = sum(severity_credits) / len(planted_bugs)
    else:
        severity_accuracy = 0.0

    # False positive rate
    # fp_blockers = blockers that don't match any planted bug and aren't clean elements
    clean_descriptions = [ce.get("description", "").lower() for ce in clean_elements]
    blocker_findings = parsed.get("blockers", [])

    fp_blockers = 0
    for finding in blocker_findings:
        idx = None
        # Check if this blocker matched any planted bug
        matched_any_bug = False
        for bug in planted_bugs:
            if _finding_matches_bug(finding, bug):
                matched_any_bug = True
                break
        if matched_any_bug:
            continue

        # Check if it matches a clean element (which would make it a FP)
        finding_text = (finding.get("title", "") + " " + finding.get("finding_text", "")).lower()
        matches_clean = any(
            any(w in finding_text for w in re.findall(r'[a-z][a-z0-9_\-\.]{3,}', cd))
            for cd in clean_descriptions
            if cd
        )
        # Any blocker that doesn't match a planted bug is counted as FP
        # (In production, human reviewer would classify; harness conservatively counts all)
        fp_blockers += 1

    total_clean = len(clean_elements)
    fp_rate = fp_blockers / (total_clean + 1)

    # FP penalty component
    fp_component = max(0.0, 1.0 - fp_rate * 2)

    # Per-scenario composite
    scenario_score = (
        0.50 * detection_rate +
        0.30 * severity_accuracy +
        0.20 * fp_component
    )

    return {
        "detection_rate": round(detection_rate, 4),
        "severity_accuracy": round(severity_accuracy, 4),
        "fp_rate": round(fp_rate, 4),
        "scenario_score": round(scenario_score, 4),
        "bug_scores": bug_scores,
    }


# ── API Caller ────────────────────────────────────────────────────────────────

def call_politico(client, model_id: str, prompt: str) -> dict:
    """
    Call Claude CLI with Politico system prompt and the constructed user prompt.
    Uses `claude -p --model <model>` instead of the API directly.
    Returns dict with raw_output, tokens_used, latency_ms, cost_usd.
    """
    # Map model IDs to CLI model names
    cli_model = "sonnet" if "sonnet" in model_id.lower() else "haiku"

    # Combine system prompt and user prompt for CLI
    full_prompt = f"{POLITICO_SYSTEM_PROMPT}\n\n---\n\n{prompt}"

    t0 = time.monotonic()
    result = subprocess.run(
        ["claude", "-p", "--model", cli_model],
        input=full_prompt,
        capture_output=True,
        text=True,
        timeout=300,
    )
    latency_ms = round((time.monotonic() - t0) * 1000)

    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {result.stderr[:500]}")

    raw_output = result.stdout.strip()

    # Estimate tokens from character count (rough: ~4 chars per token)
    est_input_tokens = len(full_prompt) // 4
    est_output_tokens = len(raw_output) // 4

    # Approximate cost
    if "haiku" in model_id.lower():
        cost_usd = (est_input_tokens * 0.80 + est_output_tokens * 4.0) / 1_000_000
    else:
        cost_usd = (est_input_tokens * 3.0 + est_output_tokens * 15.0) / 1_000_000

    return {
        "raw_output": raw_output,
        "tokens_used": {"input": est_input_tokens, "output": est_output_tokens},
        "latency_ms": latency_ms,
        "cost_usd": round(cost_usd, 6),
    }


# ── Result Store ──────────────────────────────────────────────────────────────

def save_result(run_dir: Path, scenario_id: str, model_name: str, result: dict) -> Path:
    """Write per-scenario/model result JSON."""
    scenario_dir = run_dir / scenario_id
    scenario_dir.mkdir(parents=True, exist_ok=True)
    out_path = scenario_dir / f"{model_name}.json"
    out_path.write_text(json.dumps(result, indent=2))
    return out_path


# ── Report Generator ──────────────────────────────────────────────────────────

def _verdict_symbol(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def generate_report(
    all_results: dict[str, dict[str, dict]],  # scenario_id -> model_name -> result
    ground_truths: dict[str, dict],
    run_id: str,
) -> str:
    """
    Generate COMPARISON-REPORT.md content.
    all_results[scenario_id][model_name] = full result dict
    """
    models = [MODEL_NAMES[MODEL_SONNET], MODEL_NAMES[MODEL_HAIKU]]
    scenarios = sorted(all_results.keys())

    lines = [
        f"# Politico Eval — Comparison Report",
        f"**Run ID**: {run_id}",
        f"**Date**: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "---",
        "",
        "## Per-Scenario Results",
        "",
    ]

    # Table header
    header = "| Scenario | Difficulty | " + " | ".join(
        f"{m.title()} Score | {m.title()} Det. | {m.title()} Sev. | {m.title()} FP"
        for m in models
    ) + " |"
    sep = "|---|---|" + "|---|---|---|---|" * len(models)
    lines += [header, sep]

    # Per-scenario aggregate metrics
    model_agg: dict[str, list[dict]] = {m: [] for m in models}

    for scenario_id in scenarios:
        gt = ground_truths.get(scenario_id, {})
        difficulty = gt.get("difficulty", "?")
        row_parts = [f"| {scenario_id}", difficulty]

        for model_name in models:
            result = all_results.get(scenario_id, {}).get(model_name)
            if result:
                s = result["scores"]
                model_agg[model_name].append(s)
                row_parts.append(
                    f"{s['scenario_score']:.2f} | "
                    f"{s['detection_rate']:.2f} | "
                    f"{s['severity_accuracy']:.2f} | "
                    f"{s['fp_rate']:.2f}"
                )
            else:
                row_parts.append("N/A | N/A | N/A | N/A")

        lines.append("| " + " | ".join(row_parts) + " |")

    lines += ["", "---", "", "## Aggregate Scores", ""]

    # Aggregate table
    agg_header = "| Metric | " + " | ".join(m.title() for m in models) + " | Threshold |"
    agg_sep = "|---|" + "|---|" * len(models) + "---|"
    lines += [agg_header, agg_sep]

    def _mean(lst: list[float]) -> float:
        return sum(lst) / len(lst) if lst else 0.0

    agg_scores: dict[str, dict[str, float]] = {}
    for model_name in models:
        scores_list = model_agg[model_name]
        agg_scores[model_name] = {
            "composite": _mean([s["scenario_score"] for s in scores_list]),
            "detection": _mean([s["detection_rate"] for s in scores_list]),
            "severity": _mean([s["severity_accuracy"] for s in scores_list]),
            "fp_rate": _mean([s["fp_rate"] for s in scores_list]),
        }

    metrics = [
        ("Composite Score", "composite", "≥ 0.85"),
        ("Detection Rate", "detection", "≥ 0.80"),
        ("Severity Accuracy", "severity", "≥ 0.75"),
        ("False Positive Rate", "fp_rate", "≤ 0.20"),
    ]

    for label, key, threshold in metrics:
        row = f"| {label} |"
        for model_name in models:
            val = agg_scores[model_name][key]
            row += f" {val:.3f} |"
        row += f" {threshold} |"
        lines.append(row)

    lines += ["", "---", "", "## Pass/Fail Verdicts", ""]

    for model_name in models:
        a = agg_scores[model_name]
        composite_pass = a["composite"] >= PASS_THRESHOLDS["composite"]
        detection_pass = a["detection"] >= PASS_THRESHOLDS["detection"]
        fp_pass = a["fp_rate"] <= PASS_THRESHOLDS["fp_rate"]
        severity_pass = a["severity"] >= PASS_THRESHOLDS["severity"]
        overall_pass = composite_pass and detection_pass and fp_pass and severity_pass

        lines += [
            f"### {model_name.title()}",
            f"- Composite ({a['composite']:.3f} ≥ 0.85): **{_verdict_symbol(composite_pass)}**",
            f"- Detection ({a['detection']:.3f} ≥ 0.80): **{_verdict_symbol(detection_pass)}**",
            f"- Severity ({a['severity']:.3f} ≥ 0.75): **{_verdict_symbol(severity_pass)}**",
            f"- False Positive ({a['fp_rate']:.3f} ≤ 0.20): **{_verdict_symbol(fp_pass)}**",
            "",
            f"**Overall: {_verdict_symbol(overall_pass)}**",
            "",
        ]

    # Decision section
    lines += ["---", "", "## Decision", ""]
    haiku_agg = agg_scores.get("haiku", {})
    sonnet_agg = agg_scores.get("sonnet", {})

    haiku_passes = (
        haiku_agg.get("composite", 0) >= PASS_THRESHOLDS["composite"] and
        haiku_agg.get("detection", 0) >= PASS_THRESHOLDS["detection"] and
        haiku_agg.get("fp_rate", 1) <= PASS_THRESHOLDS["fp_rate"] and
        haiku_agg.get("severity", 0) >= PASS_THRESHOLDS["severity"]
    )

    if "haiku" not in agg_scores or "sonnet" not in agg_scores:
        lines.append("Insufficient data for full decision (requires both models).")
    elif haiku_passes:
        lines += [
            "**DOWNGRADE APPROVED** — Haiku meets all thresholds.",
            "",
            "Recommendation: Downgrade Politico from Sonnet to Haiku.",
            "Expected cost reduction: ~D1 cost moves from 2 toward 3.",
        ]
    else:
        # Check conditional pass: composite ≥ 0.80 and Haiku only fails on hard scenarios
        haiku_composite = haiku_agg.get("composite", 0)
        conditional = haiku_composite >= 0.80

        if conditional:
            # Check if failures are only on hard scenarios
            hard_scenarios = {"scenario-06", "scenario-07"}
            haiku_hard_scores = [
                all_results.get(s, {}).get("haiku", {}).get("scores", {}).get("scenario_score", 0)
                for s in hard_scenarios if s in all_results
            ]
            haiku_easy_med_scores = [
                all_results.get(s, {}).get("haiku", {}).get("scores", {}).get("scenario_score", 0)
                for s in scenarios if s not in hard_scenarios and s in all_results
            ]
            sonnet_hard_scores = [
                all_results.get(s, {}).get("sonnet", {}).get("scores", {}).get("scenario_score", 0)
                for s in hard_scenarios if s in all_results
            ]

            haiku_hard_avg = _mean(haiku_hard_scores) if haiku_hard_scores else 0
            haiku_easy_avg = _mean(haiku_easy_med_scores) if haiku_easy_med_scores else 0
            sonnet_hard_avg = _mean(sonnet_hard_scores) if sonnet_hard_scores else 0

            both_degrade_on_hard = haiku_hard_avg < 0.80 and sonnet_hard_avg < 0.80

            if both_degrade_on_hard:
                lines += [
                    "**CONDITIONAL PASS** — Haiku composite ≥ 0.80 and both models degrade on hard scenarios.",
                    "",
                    f"Haiku easy/medium avg: {haiku_easy_avg:.3f} | Haiku hard avg: {haiku_hard_avg:.3f}",
                    f"Sonnet hard avg: {sonnet_hard_avg:.3f}",
                    "",
                    "Recommendation: Consider Haiku for easy/medium complexity spectrums only.",
                    "Keep Sonnet for billing, event-driven, or similarly complex spectrums.",
                ]
            else:
                failed_metrics = []
                if haiku_agg.get("composite", 0) < PASS_THRESHOLDS["composite"]:
                    failed_metrics.append(f"composite ({haiku_agg.get('composite', 0):.3f} < 0.85)")
                if haiku_agg.get("detection", 0) < PASS_THRESHOLDS["detection"]:
                    failed_metrics.append(f"detection ({haiku_agg.get('detection', 0):.3f} < 0.80)")
                if haiku_agg.get("fp_rate", 1) > PASS_THRESHOLDS["fp_rate"]:
                    failed_metrics.append(f"fp_rate ({haiku_agg.get('fp_rate', 1):.3f} > 0.20)")
                if haiku_agg.get("severity", 0) < PASS_THRESHOLDS["severity"]:
                    failed_metrics.append(f"severity ({haiku_agg.get('severity', 0):.3f} < 0.75)")
                lines += [
                    f"**FAIL** — Keep Sonnet as Politico.",
                    "",
                    f"Failed metrics: {', '.join(failed_metrics)}",
                    "",
                    "Haiku did not meet all thresholds for Politico downgrade.",
                ]
        else:
            failed_metrics = []
            if haiku_agg.get("composite", 0) < PASS_THRESHOLDS["composite"]:
                failed_metrics.append(f"composite ({haiku_agg.get('composite', 0):.3f} < 0.85)")
            if haiku_agg.get("detection", 0) < PASS_THRESHOLDS["detection"]:
                failed_metrics.append(f"detection ({haiku_agg.get('detection', 0):.3f} < 0.80)")
            if haiku_agg.get("fp_rate", 1) > PASS_THRESHOLDS["fp_rate"]:
                failed_metrics.append(f"fp_rate ({haiku_agg.get('fp_rate', 1):.3f} > 0.20)")
            if haiku_agg.get("severity", 0) < PASS_THRESHOLDS["severity"]:
                failed_metrics.append(f"severity ({haiku_agg.get('severity', 0):.3f} < 0.75)")
            lines += [
                f"**FAIL** — Keep Sonnet as Politico.",
                "",
                f"Failed metrics: {', '.join(failed_metrics)}",
                "",
                "Haiku did not meet all thresholds for Politico downgrade.",
            ]

    # Bug category breakdown
    lines += ["", "---", "", "## Bug Category Breakdown", ""]
    for model_name in models:
        lines.append(f"### {model_name.title()}")
        category_credits: dict[str, list[float]] = {
            "ownership_gap": [],
            "contract_ambiguity": [],
            "decomposition_flaw": [],
        }
        for scenario_id in scenarios:
            result = all_results.get(scenario_id, {}).get(model_name)
            if not result:
                continue
            gt = ground_truths.get(scenario_id, {})
            bug_scores = result["scores"].get("bug_scores", {})
            for bug in gt.get("planted_bugs", []):
                cat = bug.get("category", "")
                bid = bug.get("bug_id", "")
                if cat in category_credits and bid in bug_scores:
                    category_credits[cat].append(bug_scores[bid]["credit"])

        for cat, credits in category_credits.items():
            avg = _mean(credits) if credits else 0.0
            label = cat.replace("_", " ").title()
            lines.append(f"- {label}: {avg:.2f} avg credit ({len(credits)} bugs)")
        lines.append("")

    # Cost summary
    lines += ["---", "", "## Cost Summary", ""]
    for model_name in models:
        total_cost = sum(
            all_results.get(s, {}).get(model_name, {}).get("cost_usd", 0)
            for s in scenarios
        )
        total_tokens_in = sum(
            all_results.get(s, {}).get(model_name, {}).get("tokens_used", {}).get("input", 0)
            for s in scenarios
        )
        total_tokens_out = sum(
            all_results.get(s, {}).get(model_name, {}).get("tokens_used", {}).get("output", 0)
            for s in scenarios
        )
        lines.append(
            f"- {model_name.title()}: ${total_cost:.4f} "
            f"({total_tokens_in} in / {total_tokens_out} out tokens)"
        )

    lines += ["", "---", f"_Generated by run-eval.py | Run ID: {run_id}_"]

    return "\n".join(lines) + "\n"


# ── Main ──────────────────────────────────────────────────────────────────────

def load_scenario(scenario_dir: Path) -> tuple[str, str, dict]:
    """Load manifest, contract, and ground truth from a scenario directory."""
    manifest_path = scenario_dir / "manifest.md"
    contract_path = scenario_dir / "contract.md"
    gt_path = scenario_dir / "ground-truth.yaml"

    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing manifest.md in {scenario_dir}")
    if not contract_path.exists():
        raise FileNotFoundError(f"Missing contract.md in {scenario_dir}")
    if not gt_path.exists():
        raise FileNotFoundError(f"Missing ground-truth.yaml in {scenario_dir}")

    manifest = manifest_path.read_text()
    contract = contract_path.read_text()
    with open(gt_path) as f:
        ground_truth = yaml.safe_load(f)

    return manifest, contract, ground_truth


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    def fmt_row(r):
        return "  ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(r))

    print(fmt_row(headers))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(fmt_row(row))


def main():
    parser = argparse.ArgumentParser(
        description="Politico Agent Evaluation Harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--model",
        choices=["sonnet", "haiku", "both"],
        default="both",
        help="Which model(s) to run (default: both)",
    )
    parser.add_argument(
        "--scenario",
        default="all",
        help="Scenario dir name (e.g. scenario-01) or 'all' (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompts without making API calls",
    )

    args = parser.parse_args()

    # Determine models to run
    if args.model == "both":
        model_ids = [MODEL_SONNET, MODEL_HAIKU]
    elif args.model == "sonnet":
        model_ids = [MODEL_SONNET]
    else:
        model_ids = [MODEL_HAIKU]

    # Discover scenarios
    if not SCENARIOS_DIR.exists():
        print(f"ERROR: scenarios/ directory not found at {SCENARIOS_DIR}", file=sys.stderr)
        print("Create scenario directories before running the harness.", file=sys.stderr)
        sys.exit(1)

    if args.scenario == "all":
        scenario_dirs = sorted(
            d for d in SCENARIOS_DIR.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        )
    else:
        target = SCENARIOS_DIR / args.scenario
        if not target.exists():
            print(f"ERROR: Scenario directory not found: {target}", file=sys.stderr)
            sys.exit(1)
        scenario_dirs = [target]

    if not scenario_dirs:
        print("ERROR: No scenario directories found.", file=sys.stderr)
        sys.exit(1)

    print(f"Politico Eval Harness")
    print(f"  Scenarios: {len(scenario_dirs)}")
    print(f"  Models:    {', '.join(MODEL_NAMES[m] for m in model_ids)}")
    print(f"  Dry run:   {args.dry_run}")
    print()

    # Set up results directory
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    run_dir = RESULTS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # CLI-based — no API client needed
    client = None

    all_results: dict[str, dict[str, dict]] = {}
    ground_truths: dict[str, dict] = {}

    for scenario_dir in scenario_dirs:
        scenario_id = scenario_dir.name
        print(f"── {scenario_id} ──────────────────────────────")

        try:
            manifest, contract, ground_truth = load_scenario(scenario_dir)
        except FileNotFoundError as e:
            print(f"  SKIP: {e}")
            continue

        ground_truths[scenario_id] = ground_truth
        all_results[scenario_id] = {}

        gt_id = ground_truth.get("scenario_id", scenario_id)
        difficulty = ground_truth.get("difficulty", "?")
        domain = ground_truth.get("domain", "?")
        n_bugs = len(ground_truth.get("planted_bugs", []))
        print(f"  Difficulty: {difficulty} | Domain: {domain} | Bugs: {n_bugs}")

        prompt = build_prompt(manifest, contract, gt_id)

        if args.dry_run:
            print(f"\n  ── DRY RUN PROMPT PREVIEW ({scenario_id}) ──")
            print(f"  [System prompt: {len(POLITICO_SYSTEM_PROMPT)} chars]")
            preview = prompt[:500] + ("..." if len(prompt) > 500 else "")
            print(f"  [User prompt preview]:\n{preview}\n")
            continue

        for model_id in model_ids:
            model_name = MODEL_NAMES[model_id]
            print(f"  Running {model_name}...", end="", flush=True)

            try:
                api_result = call_politico(client, model_id, prompt)
            except Exception as e:
                print(f" ERROR: {e}")
                continue

            print(f" done ({api_result['latency_ms']}ms, ${api_result['cost_usd']:.5f})")

            parsed = parse_output(api_result["raw_output"])
            scores = score_scenario(parsed, ground_truth)

            result = {
                "scenario_id": scenario_id,
                "model": model_name,
                "model_id": model_id,
                "raw_output": api_result["raw_output"],
                "parsed": {
                    "blockers": parsed["blockers"],
                    "warnings": parsed["warnings"],
                    "verdict": parsed["verdict"],
                    "accepted": parsed["accepted"],
                },
                "parse_confidence": parsed["_parse_confidence"],
                "scores": scores,
                "tokens_used": api_result["tokens_used"],
                "latency_ms": api_result["latency_ms"],
                "cost_usd": api_result["cost_usd"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            all_results[scenario_id][model_name] = result
            out_path = save_result(run_dir, scenario_id, model_name, result)

            # Per-bug summary
            bug_scores = scores["bug_scores"]
            for bug in ground_truth.get("planted_bugs", []):
                bid = bug["bug_id"]
                bs = bug_scores.get(bid, {})
                status = "FOUND" if bs.get("found") else "MISS "
                credit = bs.get("credit", 0.0)
                sev_ok = "sev-ok" if bs.get("severity_correct") else "sev-wrong"
                print(f"    {bid}: {status} credit={credit:.1f} {sev_ok}")

            print(
                f"    Score: composite={scores['scenario_score']:.3f} "
                f"det={scores['detection_rate']:.3f} "
                f"sev={scores['severity_accuracy']:.3f} "
                f"fp={scores['fp_rate']:.3f}"
            )

    if args.dry_run:
        print("\nDry run complete. No API calls made.")
        return

    if not all_results:
        print("\nNo results to aggregate.")
        return

    # Generate and save comparison report
    print("\n── Generating COMPARISON-REPORT.md ──")
    report_content = generate_report(all_results, ground_truths, run_id)
    report_path = RESULTS_DIR / "COMPARISON-REPORT.md"
    report_path.write_text(report_content)
    # Also write to run-specific directory
    (run_dir / "COMPARISON-REPORT.md").write_text(report_content)
    print(f"Report written to: {report_path}")

    # Print aggregate summary to terminal
    print()
    scenarios = sorted(all_results.keys())
    models_ran = [MODEL_NAMES[m] for m in model_ids]

    def _mean(lst):
        return sum(lst) / len(lst) if lst else 0.0

    print("── Aggregate Results ──")
    headers = ["Model", "Composite", "Detection", "Severity", "FP Rate", "Verdict"]
    rows = []
    for model_name in models_ran:
        s_list = [
            all_results[s][model_name]["scores"]
            for s in scenarios
            if model_name in all_results.get(s, {})
        ]
        if not s_list:
            continue
        composite = _mean([s["scenario_score"] for s in s_list])
        detection = _mean([s["detection_rate"] for s in s_list])
        severity = _mean([s["severity_accuracy"] for s in s_list])
        fp_rate = _mean([s["fp_rate"] for s in s_list])
        passed = (
            composite >= PASS_THRESHOLDS["composite"] and
            detection >= PASS_THRESHOLDS["detection"] and
            fp_rate <= PASS_THRESHOLDS["fp_rate"] and
            severity >= PASS_THRESHOLDS["severity"]
        )
        rows.append([
            model_name.title(),
            f"{composite:.3f}",
            f"{detection:.3f}",
            f"{severity:.3f}",
            f"{fp_rate:.3f}",
            "PASS" if passed else "FAIL",
        ])

    print_table(headers, rows)
    print()
    print(f"Results saved to: {run_dir}")
    print(f"Report:           {report_path}")


if __name__ == "__main__":
    main()
