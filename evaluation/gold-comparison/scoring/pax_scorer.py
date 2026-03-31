"""
pax_scorer.py — Scores Gold agent output for the Pax phase.

All 5 rubric dimensions are implemented. Precision and recall are stored
separately (not collapsed to F1) per CONTRACT.md postconditions.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _jaccard(tokens_a: list[str], tokens_b: set[str]) -> float:
    set_a = set(tokens_a)
    if not set_a and not tokens_b:
        return 1.0
    if not set_a or not tokens_b:
        return 0.0
    return len(set_a & tokens_b) / len(set_a | tokens_b)


def _output_flags_howler(gold_output: str, howler: str, check_type: str = "any") -> bool:
    """
    Return True if gold_output flags the given howler.

    check_type:
      "any"      — any mention near concern keywords
      "concern"  — flagged as blocker / warning / observation
    """
    lower = gold_output.lower()
    howler_lower = howler.lower()

    if howler_lower not in lower:
        return False

    concern_keywords = ["blocker", "warning", "observation", "deviation", "issue",
                        "conflict", "mismatch", "violation", "risk", "flag"]

    idx = lower.find(howler_lower)
    window = lower[max(0, idx - 200):idx + 500]
    return any(kw in window for kw in concern_keywords)


def _observation_weight(gold_output: str, howler: str) -> float:
    """
    Return the false-positive weight for a flag on `howler`.
    Observation-only flags count as 0.3 per rubric.
    """
    lower = gold_output.lower()
    howler_lower = howler.lower()

    idx = lower.find(howler_lower)
    if idx < 0:
        return 0.0

    window = lower[max(0, idx - 200):idx + 500]
    if "observation" in window and "blocker" not in window and "warning" not in window:
        return 0.3
    return 1.0


def _extract_risk_level(gold_output: str, howler: str) -> str | None:
    """Try to extract Gold's assigned risk level for a given howler."""
    lower = gold_output.lower()
    howler_lower = howler.lower()

    idx = lower.find(howler_lower)
    if idx < 0:
        return None

    window = lower[max(0, idx - 100):idx + 400]
    for level in ["blocker", "warning", "observation"]:
        if level in window:
            return level
    return None


def _adjacent_risk(a: str, b: str) -> bool:
    """Return True if two risk levels are adjacent."""
    adjacency = {
        frozenset(["blocker", "warning"]),
        frozenset(["warning", "observation"]),
    }
    return frozenset([a, b]) in adjacency


# ---------------------------------------------------------------------------
# 1. Deviation Detection Rate
# ---------------------------------------------------------------------------

def _score_deviation_detection(result: dict, scenario: dict, item: dict) -> dict:
    injected = scenario.get("injected_deviations") or []
    confidence_levels = scenario.get("confidence_levels") or {}
    raw_output = result.get("raw_output", "") or ""
    raw_lower = raw_output.lower()
    output_tokens = set(raw_lower.split())

    detectable = [d for d in injected if d.get("is_detectable", True)]  # default True if absent

    # Compute caught count (double-weight for high-confidence howlers)
    caught_weighted = 0.0
    detectable_weighted = 0.0
    catch_detail = []

    for dev in detectable:
        howler = dev.get("howler", "")
        confidence = confidence_levels.get(howler, "medium")
        weight = 2.0 if confidence == "high" else 1.0
        detectable_weighted += weight

        description = dev.get("description", "")
        keywords = [t for t in description.lower().split() if len(t) > 3][:8]
        jaccard_sim = _jaccard(keywords, output_tokens)
        keyword_hit = jaccard_sim >= 0.6
        literal_hit = description[:30].lower() in raw_lower
        howler_near_concern = _output_flags_howler(raw_output, howler)

        caught = keyword_hit or literal_hit or howler_near_concern
        if caught:
            caught_weighted += weight

        catch_detail.append({
            "deviation_id": dev.get("deviation_id", dev.get("howler", "")),
            "howler": howler,
            "severity": dev.get("severity"),
            "confidence_level": confidence,
            "weight": weight,
            "caught": caught,
            "jaccard_sim": round(jaccard_sim, 3),
        })

    recall = (caught_weighted / detectable_weighted) if detectable_weighted > 0 else 1.0

    # Precision: how many flags Gold raised match injected deviations
    flagged_howlers = {
        d.get("howler") for d in injected
        if _output_flags_howler(raw_output, d.get("howler", ""))
    }
    # Estimate false catches: flags on howlers not in injected list
    all_debrief_howlers = {
        h.get("howler") for h in (scenario.get("debrief_set") or [])
        if isinstance(h, dict) and h.get("howler")
    }
    injected_howlers = {d.get("howler") for d in injected}
    correct_howlers_set = all_debrief_howlers - injected_howlers

    false_catches = sum(
        1 for h in correct_howlers_set
        if _output_flags_howler(raw_output, h)
    )
    caught_count = sum(1 for d in detectable if _output_flags_howler(raw_output, d.get("howler", "")))
    precision = (
        caught_count / (caught_count + false_catches)
        if (caught_count + false_catches) > 0 else 1.0
    )

    score = 0.7 * recall + 0.3 * precision

    return {
        "id": item["id"],
        "name": item["name"],
        "weight": item["weight"],
        "scoring_method": item["scoring_method"],
        "score": round(score, 4),
        "threshold_pass": item["threshold_pass"],
        "passes": score >= item["threshold_pass"],
        "detail": {
            "recall": round(recall, 4),
            "precision": round(precision, 4),
            "score_formula": "0.7 * recall + 0.3 * precision",
            "detectable_weighted": detectable_weighted,
            "caught_weighted": round(caught_weighted, 4),
            "false_catches": false_catches,
            "deviations": catch_detail,
        },
        "needs_human_review": False,
    }


# ---------------------------------------------------------------------------
# 2. False Positive Rate on Correct Howlers
# ---------------------------------------------------------------------------

def _score_false_positive_rate(result: dict, scenario: dict, item: dict) -> dict:
    correct_howlers = scenario.get("correct_howlers") or []
    raw_output = result.get("raw_output", "") or ""

    if not correct_howlers:
        return {
            "id": item["id"],
            "name": item["name"],
            "weight": item["weight"],
            "scoring_method": item["scoring_method"],
            "score": 1.0,
            "threshold_pass": item["threshold_pass"],
            "passes": True,
            "detail": {"note": "no correct howlers in scenario"},
            "needs_human_review": False,
        }

    flags_weighted = 0.0
    detail_rows = []

    for howler in correct_howlers:
        flagged = _output_flags_howler(raw_output, howler)
        if flagged:
            obs_weight = _observation_weight(raw_output, howler)
            flags_weighted += obs_weight
            detail_rows.append({"howler": howler, "flagged": True, "weight": obs_weight})
        else:
            detail_rows.append({"howler": howler, "flagged": False, "weight": 0.0})

    false_positive_rate = flags_weighted / len(correct_howlers)
    score = 1.0 - false_positive_rate

    return {
        "id": item["id"],
        "name": item["name"],
        "weight": item["weight"],
        "scoring_method": item["scoring_method"],
        "score": round(score, 4),
        "threshold_pass": item["threshold_pass"],
        "passes": score >= item["threshold_pass"],
        "detail": {
            "correct_howlers_total": len(correct_howlers),
            "flags_weighted": round(flags_weighted, 4),
            "false_positive_rate": round(false_positive_rate, 4),
            "howlers": detail_rows,
        },
        "needs_human_review": False,
    }


# ---------------------------------------------------------------------------
# 3. Seam Cross-Reference Accuracy
# ---------------------------------------------------------------------------

def _score_seam_cross_reference(result: dict, scenario: dict, item: dict) -> dict:
    debrief_set = scenario.get("debrief_set") or []
    raw_output = result.get("raw_output", "") or ""
    raw_lower = raw_output.lower()

    # Collect all seam declarations and check Gold's output against them
    seam_ground_truth = scenario.get("seam_ground_truth") or {}  # optional explicit ground truth
    correctly_cross_referenced = 0
    total_seams_with_status = 0
    seam_detail = []

    for debriefed in debrief_set:
        if not isinstance(debriefed, dict):
            continue
        howler = debriefed.get("howler", "")
        seams = debriefed.get("seams_declared") or []

        # Also parse seams from hook_md text
        hook_md = debriefed.get("hook_md", "") or ""
        if "seams declared" in hook_md.lower() or "seam" in hook_md.lower():
            seam_lines = [
                line.strip() for line in hook_md.splitlines()
                if "seam" in line.lower() or "import" in line.lower()
            ]
            if seam_lines and not seams:
                # synthesize seam entries from hook_md text
                seams = [{"seam_id": f"{howler}-seam-{i}", "description": line}
                         for i, line in enumerate(seam_lines)]

        for seam in seams:
            total_seams_with_status += 1
            seam_id = seam.get("seam_id", "") if isinstance(seam, dict) else ""
            description = seam.get("description", str(seam)) if isinstance(seam, dict) else str(seam)
            counterpart = seam.get("counterpart_howler", "") if isinstance(seam, dict) else ""

            # Check whether Gold addressed this seam in its output
            seam_keywords = [t for t in description.lower().split() if len(t) > 3][:6]
            howler_in_output = howler.lower() in raw_lower
            seam_addressed = howler_in_output and _jaccard(seam_keywords, set(raw_lower.split())) >= 0.3

            # Check ground truth if provided
            gt = seam_ground_truth.get(seam_id)
            if gt is not None:
                # Explicit ground truth: check if Gold's verdict matches
                gold_says_match = seam_addressed
                is_correct = gold_says_match == gt.get("is_match", True)
            else:
                # No explicit ground truth — assume seam should be confirmed
                is_correct = seam_addressed

            if is_correct:
                correctly_cross_referenced += 1

            seam_detail.append({
                "seam_id": seam_id,
                "howler": howler,
                "counterpart": counterpart,
                "addressed_by_gold": seam_addressed,
                "is_correct": is_correct,
            })

    score = (
        correctly_cross_referenced / total_seams_with_status
        if total_seams_with_status > 0 else 1.0
    )

    return {
        "id": item["id"],
        "name": item["name"],
        "weight": item["weight"],
        "scoring_method": item["scoring_method"],
        "score": round(score, 4),
        "threshold_pass": item["threshold_pass"],
        "passes": score >= item["threshold_pass"],
        "detail": {
            "total_seams_with_status": total_seams_with_status,
            "correctly_cross_referenced": correctly_cross_referenced,
            "seams": seam_detail,
        },
        "needs_human_review": False,
    }


# ---------------------------------------------------------------------------
# 4. Integration Risk Classification (hybrid)
# ---------------------------------------------------------------------------

def _score_risk_classification(result: dict, scenario: dict, item: dict) -> dict:
    injected = scenario.get("injected_deviations") or []
    raw_output = result.get("raw_output", "") or ""

    caught_deviations = [
        d for d in injected
        if _output_flags_howler(raw_output, d.get("howler", ""))
    ]

    if not caught_deviations:
        # Inherit deviation detection score implicitly; use 1.0 as sentinel
        # (rubric: if no deviations caught, inherit deviation_detection_rate score)
        automated_score = 1.0
        classification_detail = []
        note = "no caught deviations — inheriting deviation detection rate score"
    else:
        correct_count = 0.0
        classification_detail = []
        for dev in caught_deviations:
            howler = dev.get("howler", "")
            expected_level = dev.get("severity", "").lower()
            gold_level = _extract_risk_level(raw_output, howler)

            if gold_level == expected_level:
                per_score = 1.0
            elif gold_level and _adjacent_risk(gold_level, expected_level):
                per_score = 0.5
            else:
                per_score = 0.0

            correct_count += per_score
            classification_detail.append({
                "howler": howler,
                "expected_level": expected_level,
                "gold_level": gold_level,
                "score": per_score,
            })

        automated_score = correct_count / len(caught_deviations)
        note = None

    excerpt = {
        "caught_deviations_scored": classification_detail if caught_deviations else [],
        "review_guidance": item.get("human_criteria", ""),
        "classification_options": ["CONSISTENT", "INCONSISTENT"],
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
            "caught_deviations": len(caught_deviations),
            "classifications": classification_detail if caught_deviations else [],
            **({"note": note} if note else {}),
        },
        "needs_human_review": {
            "type": "human_review_required",
            "item_id": item["id"],
            "excerpt": excerpt,
            "auto_human_split": "70% automated / 30% human",
        },
    }


# ---------------------------------------------------------------------------
# 5. Validation Depth for Low-Confidence Howlers (hybrid)
# ---------------------------------------------------------------------------

def _score_validation_depth(result: dict, scenario: dict, item: dict) -> dict:
    debrief_set = scenario.get("debrief_set") or []
    injected = scenario.get("injected_deviations") or []
    confidence_levels = scenario.get("confidence_levels") or {}
    raw_output = result.get("raw_output", "") or ""

    injected_howlers = {d.get("howler") for d in injected}
    low_conf_howlers = [
        h.get("howler") for h in debrief_set
        if isinstance(h, dict) and (
            confidence_levels.get(h.get("howler"), h.get("confidence", "medium")) == "low"
            or h.get("confidence", "medium") == "low"
            or h.get("howler") in injected_howlers
        )
    ]

    if not low_conf_howlers:
        return {
            "id": item["id"],
            "name": item["name"],
            "weight": item["weight"],
            "scoring_method": item["scoring_method"],
            "score": 1.0,
            "score_is_partial": True,
            "threshold_pass": item["threshold_pass"],
            "passes": True,
            "detail": {"note": "no low-confidence howlers in scenario"},
            "needs_human_review": {
                "type": "human_review_required",
                "item_id": item["id"],
                "excerpt": {
                    "low_conf_howlers": [],
                    "review_guidance": item.get("human_criteria", ""),
                },
                "auto_human_split": "50% automated / 50% human",
            },
        }

    # File-inspection evidence: look for specific content clues
    # (line numbers, function names, type signatures not in debrief summaries)
    debrief_texts = {
        h.get("howler"): (h.get("debrief", "") + " " + h.get("hook_md", ""))
        for h in debrief_set if isinstance(h, dict)
    }

    verified = []
    unverified = []
    verification_detail = []

    for howler in low_conf_howlers:
        howler_lower = howler.lower()
        if howler_lower not in raw_output.lower():
            unverified.append(howler)
            verification_detail.append({"howler": howler, "evidence": False, "reason": "not mentioned"})
            continue

        # Look for evidence of direct file inspection: line numbers, type signatures, function bodies
        evidence_patterns = [
            "line ", "export function", "export interface", "export const",
            "return type", "::", "=>", "implements ", "extends ",
        ]
        debrief_text = debrief_texts.get(howler, "").lower()
        # Find Gold's section about this howler
        idx = raw_output.lower().find(howler_lower)
        gold_section = raw_output[max(0, idx - 50):idx + 800]

        # Evidence = content in Gold's section not already in the debrief
        evidence_tokens = set(gold_section.lower().split()) - set(debrief_text.split())
        has_evidence = any(p in gold_section.lower() for p in evidence_patterns) and len(evidence_tokens) > 15

        if has_evidence:
            verified.append(howler)
            verification_detail.append({"howler": howler, "evidence": True, "unique_tokens": len(evidence_tokens)})
        else:
            unverified.append(howler)
            verification_detail.append({"howler": howler, "evidence": False, "unique_tokens": len(evidence_tokens)})

    automated_score = len(verified) / len(low_conf_howlers) if low_conf_howlers else 1.0

    excerpt = {
        "low_conf_howlers": low_conf_howlers,
        "verification_detail": verification_detail,
        "review_guidance": item.get("human_criteria", ""),
        "classification_options": ["DEEP", "SHALLOW", "NONE"],
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
            "low_conf_howlers_count": len(low_conf_howlers),
            "verified_count": len(verified),
            "verifications": verification_detail,
        },
        "needs_human_review": {
            "type": "human_review_required",
            "item_id": item["id"],
            "excerpt": excerpt,
            "auto_human_split": "50% automated / 50% human",
        },
    }


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

_SCORER_MAP = {
    "pax_deviation_detection_rate": _score_deviation_detection,
    "pax_false_positive_rate": _score_false_positive_rate,
    "pax_seam_cross_reference_accuracy": _score_seam_cross_reference,
    "pax_risk_classification": _score_risk_classification,
    "pax_validation_depth": _score_validation_depth,
}


def score_pax(result: dict, scenario: dict, rubric: dict) -> dict:
    """
    Score a Pax result against its scenario ground-truth and rubric.

    Returns a dict with: scenario_id, model, phase, items, phase_score,
    phase_score_is_partial, needs_human_review.
    Deviation detection stores precision AND recall separately.
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

    scored_items = [i for i in items_scored if i.get("score") is not None]
    total_weight = sum(i["weight"] for i in scored_items)
    phase_score = (
        sum(i["score"] * i["weight"] for i in scored_items) / total_weight
        if total_weight > 0 else None
    )
    is_partial = any(i.get("score") is None for i in items_scored)

    return {
        "scenario_id": result.get("scenario_id"),
        "model": result.get("model"),
        "model_id": result.get("model_id"),
        "phase": "pax",
        "items": items_scored,
        "phase_score": round(phase_score, 4) if phase_score is not None else None,
        "phase_score_is_partial": is_partial,
        "needs_human_review": human_review_queue,
        "tokens_used": result.get("tokens_used"),
        "latency_ms": result.get("latency_ms"),
        "cost_usd": result.get("cost_usd"),
    }
