"""
muster_scorer.py — Scores Gold agent output for the Muster phase.

All 7 rubric dimensions are implemented. Automated scores are floats in [0.0, 1.0].
Human-review items produce structured excerpts in `needs_human_review`.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_found_files(result: dict) -> set[str]:
    """Extract file names from the parsed file_ownership list."""
    ownership = result.get("parsed", {}).get("file_ownership", []) or []
    return {entry["file"] for entry in ownership if isinstance(entry, dict) and "file" in entry}


def _get_expected_files(scenario: dict) -> set[str]:
    efo = scenario.get("expected_file_ownership") or []
    return {entry["file"] for entry in efo if isinstance(entry, dict) and "file" in entry}


def _get_found_edges(result: dict) -> set[tuple[str, str]]:
    """Extract (from, to) DAG edges from parsed output."""
    dag_edges = result.get("parsed", {}).get("dag_edges", []) or []
    return {
        (e["from"], e["to"])
        for e in dag_edges
        if isinstance(e, dict) and "from" in e and "to" in e
    }


def _get_expected_edges(scenario: dict) -> set[tuple[str, str]]:
    expected = scenario.get("expected_dag_edges") or []
    return {
        (e["from"], e["to"])
        for e in expected
        if isinstance(e, dict) and "from" in e and "to" in e
    }


def _get_contract_sections_found(result: dict) -> set[str]:
    """Extract section names from parsed contract_sections."""
    sections = result.get("parsed", {}).get("contract_sections", []) or []
    return {s["section"] for s in sections if isinstance(s, dict) and "section" in s}


# ---------------------------------------------------------------------------
# 1. File Ownership Completeness
# ---------------------------------------------------------------------------

def _score_file_ownership_completeness(result: dict, scenario: dict, item: dict) -> dict:
    found = _get_found_files(result)
    expected = _get_expected_files(scenario)
    if not expected:
        score = 1.0
    else:
        score = len(found & expected) / len(expected)
    return {
        "id": item["id"],
        "name": item["name"],
        "weight": item["weight"],
        "scoring_method": item["scoring_method"],
        "score": round(score, 4),
        "threshold_pass": item["threshold_pass"],
        "passes": score >= item["threshold_pass"],
        "detail": {
            "found_files": sorted(found),
            "expected_files": sorted(expected),
            "matched": sorted(found & expected),
            "missing": sorted(expected - found),
        },
        "needs_human_review": False,
    }


# ---------------------------------------------------------------------------
# 2. File Ownership Conflict Detection
# ---------------------------------------------------------------------------

def _score_conflict_detection(result: dict, scenario: dict, item: dict) -> dict:
    known_conflicts = scenario.get("known_conflicts") or []
    if not known_conflicts:
        return {
            "id": item["id"],
            "name": item["name"],
            "weight": item["weight"],
            "scoring_method": item["scoring_method"],
            "score": 1.0,
            "threshold_pass": item["threshold_pass"],
            "passes": True,
            "detail": {"conflicts_injected": 0, "conflicts_found": 0, "note": "no conflicts to find"},
            "needs_human_review": False,
        }

    raw_output = result.get("raw_output", "") or ""
    ownership = result.get("parsed", {}).get("file_ownership", []) or []
    ownership_text = " ".join(str(e) for e in ownership)
    full_text = (raw_output + " " + ownership_text).lower()

    conflicts_found = 0.0
    detail_rows = []

    for conflict in known_conflicts:
        cfile = conflict.get("file", "")
        naive_howlers = conflict.get("naive_howlers", conflict.get("howlers", []))

        file_mentioned = cfile.lower() in full_text
        howler_mentions = [h for h in naive_howlers if h.lower() in full_text]

        if file_mentioned and len(howler_mentions) >= 2:
            per_conflict = 1.0
        elif file_mentioned and len(howler_mentions) == 1:
            per_conflict = 0.5
        elif file_mentioned:
            per_conflict = 0.75
        else:
            per_conflict = 0.0

        conflicts_found += per_conflict
        detail_rows.append({
            "file": cfile,
            "found": file_mentioned,
            "howlers_mentioned": howler_mentions,
            "per_conflict_score": per_conflict,
        })

    score = conflicts_found / len(known_conflicts)
    return {
        "id": item["id"],
        "name": item["name"],
        "weight": item["weight"],
        "scoring_method": item["scoring_method"],
        "score": round(score, 4),
        "threshold_pass": item["threshold_pass"],
        "passes": score >= item["threshold_pass"],
        "detail": {
            "conflicts_injected": len(known_conflicts),
            "conflicts_found_weighted": round(conflicts_found, 4),
            "conflicts": detail_rows,
        },
        "needs_human_review": False,
    }


# ---------------------------------------------------------------------------
# 3. DAG Edge Accuracy
# ---------------------------------------------------------------------------

def _score_dag_edge_accuracy(result: dict, scenario: dict, item: dict) -> dict:
    found_edges = _get_found_edges(result)
    expected_edges = _get_expected_edges(scenario)

    # Both empty → perfect score
    if not expected_edges and not found_edges:
        precision = recall = f1 = 1.0
    else:
        tp = len(found_edges & expected_edges)
        fp = len(found_edges - expected_edges)
        fn = len(expected_edges - found_edges)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "id": item["id"],
        "name": item["name"],
        "weight": item["weight"],
        "scoring_method": item["scoring_method"],
        "score": round(f1, 4),
        "threshold_pass": item["threshold_pass"],
        "passes": f1 >= item["threshold_pass"],
        "detail": {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "found_edges": [{"from": e[0], "to": e[1]} for e in sorted(found_edges)],
            "expected_edges": [{"from": e[0], "to": e[1]} for e in sorted(expected_edges)],
            "phantom_edges": [{"from": e[0], "to": e[1]} for e in sorted(found_edges - expected_edges)],
            "missing_edges": [{"from": e[0], "to": e[1]} for e in sorted(expected_edges - found_edges)],
        },
        "needs_human_review": False,
    }


# ---------------------------------------------------------------------------
# 4. Contract Completeness (hybrid)
# ---------------------------------------------------------------------------

def _score_contract_completeness(result: dict, scenario: dict, item: dict) -> dict:
    expected_sections = scenario.get("expected_contract_sections") or []
    raw_output = result.get("raw_output", "") or ""
    sections_found = _get_contract_sections_found(result)

    # Structural check: find expected section names in output
    found_section_names: set[str] = set()
    for sec_entry in expected_sections:
        sec_name = sec_entry.get("section", "") if isinstance(sec_entry, dict) else str(sec_entry)
        text_check = (sec_name.lower().replace("_", " ") in raw_output.lower() or
                      sec_name.lower() in raw_output.lower() or
                      sec_name in sections_found)
        if text_check:
            found_section_names.add(sec_name)

    unique_section_names = {
        (s.get("section") if isinstance(s, dict) else str(s))
        for s in expected_sections
    }
    structural_score = (
        len(found_section_names) / len(unique_section_names)
        if unique_section_names else 1.0
    )

    # must_include check: scan raw output for required keywords
    must_include_hits = 0
    must_include_total = 0
    for sec_entry in expected_sections:
        if not isinstance(sec_entry, dict):
            continue
        for keyword in sec_entry.get("must_include", []):
            must_include_total += 1
            if keyword.lower() in raw_output.lower():
                must_include_hits += 1

    must_include_score = must_include_hits / must_include_total if must_include_total > 0 else 1.0

    # DBC check: look for precondition / postcondition / invariant blocks per Howler
    howlers = {
        entry.get("howler") for entry in (scenario.get("expected_file_ownership") or [])
        if isinstance(entry, dict) and entry.get("howler")
    }
    howler_metadata = scenario.get("howler_metadata") or {}

    howlers_with_precondition = sum(
        1 for h in howlers if h and f"precondition" in raw_output.lower() and h.lower() in raw_output.lower()
    )
    howlers_with_postcondition = sum(
        1 for h in howlers if h and f"postcondition" in raw_output.lower() and h.lower() in raw_output.lower()
    )
    interface_heavy = [h for h, meta in howler_metadata.items() if meta.get("interface_heavy")]
    howlers_with_invariant = sum(
        1 for h in interface_heavy if h.lower() in raw_output.lower() and "invariant" in raw_output.lower()
    )

    n_howlers = max(len(howlers), 1)
    n_interface_heavy = max(len(interface_heavy), 1)

    dbc_score = (
        (howlers_with_precondition / n_howlers) * 0.4 +
        (howlers_with_postcondition / n_howlers) * 0.4 +
        (howlers_with_invariant / n_interface_heavy) * 0.2
    )

    automated_score = 0.5 * structural_score + 0.5 * dbc_score

    # Human review excerpt
    missing_sections = unique_section_names - found_section_names
    excerpt = {
        "structural_score": round(structural_score, 4),
        "must_include_score": round(must_include_score, 4),
        "dbc_score": round(dbc_score, 4),
        "missing_sections": sorted(missing_sections),
        "review_guidance": item.get("human_criteria", ""),
    }

    return {
        "id": item["id"],
        "name": item["name"],
        "weight": item["weight"],
        "scoring_method": item["scoring_method"],
        "score": round(automated_score, 4),
        "score_is_partial": True,
        "threshold_pass": item["threshold_pass"],
        "passes": automated_score >= item["threshold_pass"],
        "detail": {
            "automated_score": round(automated_score, 4),
            "structural_score": round(structural_score, 4),
            "must_include_score": round(must_include_score, 4),
            "dbc_score": round(dbc_score, 4),
        },
        "needs_human_review": {
            "type": "human_review_required",
            "item_id": item["id"],
            "excerpt": excerpt,
            "auto_human_split": "60% automated / 40% human",
        },
    }


# ---------------------------------------------------------------------------
# 5. Contract Precision (human-only)
# ---------------------------------------------------------------------------

def _score_contract_precision(result: dict, scenario: dict, item: dict) -> dict:
    raw_output = result.get("raw_output", "") or ""

    # Extract postcondition snippets from the raw output for human review
    lines = raw_output.splitlines()
    postcondition_lines = [
        line.strip() for line in lines
        if "postcondition" in line.lower() or "exports" in line.lower()
    ][:30]  # cap at 30 lines to avoid raw dump

    return {
        "id": item["id"],
        "name": item["name"],
        "weight": item["weight"],
        "scoring_method": item["scoring_method"],
        "score": None,
        "threshold_pass": item["threshold_pass"],
        "passes": None,
        "detail": {"status": "pending_human_review"},
        "needs_human_review": {
            "type": "human_only",
            "item_id": item["id"],
            "excerpt": {
                "postcondition_lines": postcondition_lines,
                "review_guidance": item.get("human_criteria", ""),
                "classification_options": ["TESTABLE", "VAGUE", "ABSENT"],
            },
        },
    }


# ---------------------------------------------------------------------------
# 6. Decomposition Soundness (hybrid)
# ---------------------------------------------------------------------------

def _score_decomposition_soundness(result: dict, scenario: dict, item: dict) -> dict:
    raw_output = result.get("raw_output", "") or ""
    serial_tasks_expected = set(scenario.get("serial_tasks_expected") or [])

    if not serial_tasks_expected:
        serial_recall = 1.0
        serial_detail = {"note": "no serial tasks expected in this scenario"}
    else:
        serial_patterns = ["serial_risk: yes", "must run after", "sequential", "blocked until", "serial"]
        labeled_count = 0
        labeled_tasks = []
        for task_id in serial_tasks_expected:
            task_lower = task_id.lower()
            section_start = raw_output.lower().find(task_lower)
            if section_start >= 0:
                context_window = raw_output[section_start:section_start + 300].lower()
                if any(p in context_window for p in serial_patterns):
                    labeled_count += 1
                    labeled_tasks.append(task_id)
        serial_recall = labeled_count / len(serial_tasks_expected)
        serial_detail = {
            "expected": sorted(serial_tasks_expected),
            "labeled": labeled_tasks,
            "recall": round(serial_recall, 4),
        }

    automated_score = serial_recall

    # Howler scope review excerpt
    howlers = sorted({
        entry.get("howler") for entry in (scenario.get("expected_file_ownership") or [])
        if isinstance(entry, dict) and entry.get("howler")
    })
    excerpt = {
        "serial_tasks_detail": serial_detail,
        "howlers_to_review": howlers,
        "review_guidance": item.get("human_criteria", ""),
    }

    return {
        "id": item["id"],
        "name": item["name"],
        "weight": item["weight"],
        "scoring_method": item["scoring_method"],
        "score": round(automated_score, 4),
        "score_is_partial": True,
        "threshold_pass": item["threshold_pass"],
        "passes": automated_score >= item["threshold_pass"],
        "detail": {
            "automated_score": round(automated_score, 4),
            "serial_recall": round(serial_recall, 4),
            **serial_detail,
        },
        "needs_human_review": {
            "type": "human_review_required",
            "item_id": item["id"],
            "excerpt": excerpt,
            "auto_human_split": "50% automated / 50% human",
        },
    }


# ---------------------------------------------------------------------------
# 7. Politico Integration (hybrid)
# ---------------------------------------------------------------------------

def _score_politico_integration(result: dict, scenario: dict, item: dict) -> dict:
    raw_output = result.get("raw_output", "") or ""
    raw_lower = raw_output.lower()

    politico_keywords = ["politico", "adversarial review", "phase 1.5", "the passage"]
    politico_present = int(any(kw in raw_lower for kw in politico_keywords))

    injected_issues = scenario.get("politico_injection") or []
    if not injected_issues:
        catch_rate = 1.0
        issues_detail = []
    else:
        issues_caught = 0
        issues_detail = []
        for issue in injected_issues:
            description = issue.get("description", "")
            keywords = description.lower().split()[:8]
            # Jaccard-style overlap: count shared tokens
            output_tokens = set(raw_lower.split())
            overlap = len(set(keywords) & output_tokens) / len(set(keywords)) if keywords else 0.0
            caught = overlap >= 0.6 or description[:30].lower() in raw_lower
            if caught:
                issues_caught += 1
            issues_detail.append({
                "issue_id": issue.get("issue_id", ""),
                "description": description[:80],
                "caught": caught,
                "overlap": round(overlap, 3),
            })
        catch_rate = issues_caught / len(injected_issues)

    automated_score = 0.3 * politico_present + 0.7 * catch_rate

    excerpt = {
        "politico_step_present": bool(politico_present),
        "issues_injected": len(injected_issues),
        "issues_detail": issues_detail,
        "review_guidance": item.get("human_criteria", ""),
        "classification_options": ["ADDRESSED", "IGNORED", "NOT_REACHED"],
    }

    return {
        "id": item["id"],
        "name": item["name"],
        "weight": item["weight"],
        "scoring_method": item["scoring_method"],
        "score": round(automated_score, 4),
        "score_is_partial": True,
        "threshold_pass": item["threshold_pass"],
        "passes": automated_score >= item["threshold_pass"],
        "detail": {
            "automated_score": round(automated_score, 4),
            "politico_present": bool(politico_present),
            "catch_rate": round(catch_rate, 4),
        },
        "needs_human_review": {
            "type": "human_review_required",
            "item_id": item["id"],
            "excerpt": excerpt,
            "auto_human_split": "60% automated / 40% human",
        },
    }


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

_SCORER_MAP = {
    "muster_file_ownership_completeness": _score_file_ownership_completeness,
    "muster_file_ownership_conflict_detection": _score_conflict_detection,
    "muster_dag_edge_accuracy": _score_dag_edge_accuracy,
    "muster_contract_completeness": _score_contract_completeness,
    "muster_contract_precision": _score_contract_precision,
    "muster_decomposition_soundness": _score_decomposition_soundness,
    "muster_politico_integration": _score_politico_integration,
}


def score_muster(result: dict, scenario: dict, rubric: dict) -> dict:
    """
    Score a Muster result against its scenario ground-truth and rubric.

    Args:
        result:   Raw result dict (from result_store / results/raw JSON).
        scenario: Scenario YAML loaded as dict.
        rubric:   muster-rubric.yaml loaded as dict.

    Returns:
        Dict with keys: scenario_id, model, phase, items (list), phase_score,
        phase_score_is_partial, needs_human_review (list of structured excerpts).
    """
    items_scored = []
    human_review_queue = []

    for item in rubric.get("items", []):
        item_id = item.get("id", "")
        scorer_fn = _SCORER_MAP.get(item_id)
        if scorer_fn is None:
            items_scored.append({
                "id": item_id,
                "name": item.get("name", item_id),
                "weight": item.get("weight", 0.0),
                "score": None,
                "error": f"no scorer registered for {item_id}",
            })
            continue

        scored = scorer_fn(result, scenario, item)
        items_scored.append(scored)
        if scored.get("needs_human_review") and isinstance(scored["needs_human_review"], dict):
            human_review_queue.append(scored["needs_human_review"])

    # Compute phase score from items that have a numeric score (None = pending human)
    scored_items = [i for i in items_scored if i.get("score") is not None]
    total_weight = sum(i["weight"] for i in scored_items)
    if total_weight > 0:
        phase_score = sum(i["score"] * i["weight"] for i in scored_items) / total_weight
    else:
        phase_score = None

    is_partial = any(i.get("score") is None for i in items_scored)

    return {
        "scenario_id": result.get("scenario_id"),
        "model": result.get("model"),
        "model_id": result.get("model_id"),
        "phase": "muster",
        "items": items_scored,
        "phase_score": round(phase_score, 4) if phase_score is not None else None,
        "phase_score_is_partial": is_partial,
        "needs_human_review": human_review_queue,
        "tokens_used": result.get("tokens_used"),
        "latency_ms": result.get("latency_ms"),
        "cost_usd": result.get("cost_usd"),
    }
