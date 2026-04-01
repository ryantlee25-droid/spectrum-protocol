"""
forge_scorer.py — Scores Gold agent output for the Forge phase.

All 4 rubric dimensions are implemented. Classification and circuit breaker
are purely automated. Recovery action uses an automated + human-penalty model.
Escalation appropriateness is hybrid.
"""

from __future__ import annotations

# Canonical type and action vocabularies
FAILURE_TYPES = {"transient", "logical", "structural", "environmental", "conflict"}
RECOVERY_ACTIONS = {"resume", "retry", "skip", "restructure"}

# Adjacent pairs eligible for partial credit
ADJACENT_TYPE_PAIRS = {
    frozenset(["transient", "logical"]),
    frozenset(["structural", "conflict"]),
    frozenset(["logical", "structural"]),
}

ESCALATION_KEYWORDS = ["escalate", "human confirmation", "pause", "not auto-recover",
                        "requires human", "present to human", "human review"]
AUTO_RECOVER_KEYWORDS = ["auto-recover", "auto-resume", "automatically resume",
                         "dropping a new howler", "drop a new howler", "will resume"]
RESUME_RETRY_KEYWORDS = [
    ("resume", "resume"),
    ("retry", "retry"),
    ("skip", "skip"),
    ("restructure", "restructure"),
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_classification(gold_output: str) -> str | None:
    lower = gold_output.lower()
    for ftype in FAILURE_TYPES:
        if ftype in lower:
            return ftype
    return None


def _extract_recovery_action(gold_output: str) -> str | None:
    lower = gold_output.lower()
    for action in RECOVERY_ACTIONS:
        if action in lower:
            return action
    return None


def _gold_escalated(gold_output: str) -> bool:
    lower = gold_output.lower()
    has_escalation = any(kw in lower for kw in ESCALATION_KEYWORDS)
    has_drop_instruction = any(kw in lower for kw in AUTO_RECOVER_KEYWORDS)
    return has_escalation and not has_drop_instruction


def _escalation_expected(classification: str) -> bool:
    """Per rubric: transient may auto-recover; all others require human confirmation."""
    return classification != "transient"


# ---------------------------------------------------------------------------
# 1. Classification Accuracy
# ---------------------------------------------------------------------------

def _score_classification_accuracy(result: dict, scenario: dict, item: dict) -> dict:
    raw_output = result.get("raw_output", "") or ""
    correct = (scenario.get("correct_classification") or "").lower().strip()
    ambiguous = scenario.get("ambiguous", False)

    gold_classification = _extract_classification(raw_output)

    if gold_classification == correct:
        per_scenario_score = 1.0
        match = True
    elif (ambiguous and gold_classification and
          frozenset([gold_classification, correct]) in ADJACENT_TYPE_PAIRS):
        per_scenario_score = 0.5
        match = False
    else:
        per_scenario_score = 0.0
        match = False

    return {
        "id": item["id"],
        "name": item["name"],
        "weight": item["weight"],
        "scoring_method": item["scoring_method"],
        "score": round(per_scenario_score, 4),
        "threshold_pass": item["threshold_pass"],
        "passes": per_scenario_score >= item["threshold_pass"],
        "detail": {
            "correct_classification": correct,
            "gold_classification": gold_classification,
            "exact_match": match,
            "ambiguous": ambiguous,
            "partial_credit_applied": not match and per_scenario_score == 0.5,
        },
        "needs_human_review": False,
    }


# ---------------------------------------------------------------------------
# 2. Recovery Action Correctness (hybrid with human penalty)
# ---------------------------------------------------------------------------

def _score_recovery_action(result: dict, scenario: dict, item: dict) -> dict:
    raw_output = result.get("raw_output", "") or ""
    correct = (scenario.get("correct_recovery_action") or "").lower().strip()

    gold_action = _extract_recovery_action(raw_output)

    if gold_action == correct:
        automated_score = 1.0
    elif (gold_action in {"resume", "retry"} and correct in {"resume", "retry"} and
          gold_action != correct):
        # Adjacent partial credit for resume/retry always applies
        automated_score = 0.5
    else:
        automated_score = 0.0

    # Structured excerpt for human penalty assessment
    excerpt = {
        "correct_action": correct,
        "gold_action": gold_action,
        "automated_score": automated_score,
        "review_guidance": item.get("human_criteria", ""),
        "instructions": (
            "Check whether Gold provides rationale referencing the failure type "
            "and the SPECTRUM protocol's rules. Score ADEQUATE or ABSENT."
        ),
        "classification_options": ["ADEQUATE", "ABSENT"],
        "penalty_if_absent": "automated_score - 0.15 (clamped to 0.0)",
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
            "correct_action": correct,
            "gold_action": gold_action,
        },
        "needs_human_review": {
            "type": "human_review_required",
            "item_id": item["id"],
            "excerpt": excerpt,
            "auto_human_split": "automated minus human penalty (max 0.15)",
        },
    }


# ---------------------------------------------------------------------------
# 3. Circuit Breaker Application
# ---------------------------------------------------------------------------

def _score_circuit_breaker(result: dict, scenario: dict, item: dict) -> dict:
    raw_output = result.get("raw_output", "") or ""
    raw_lower = raw_output.lower()

    circuit_breaker_expected = scenario.get("circuit_breaker_applies", scenario.get("circuit_breaker_expected"))
    if circuit_breaker_expected is None:
        # No circuit breaker scenario — score 1.0
        return {
            "id": item["id"],
            "name": item["name"],
            "weight": item["weight"],
            "scoring_method": item["scoring_method"],
            "score": 1.0,
            "threshold_pass": item["threshold_pass"],
            "passes": True,
            "detail": {"note": "circuit_breaker_applies not specified in scenario"},
            "needs_human_review": False,
        }

    gold_escalated = _gold_escalated(raw_output)
    has_drop_instruction = any(kw in raw_lower for kw in AUTO_RECOVER_KEYWORDS)

    if circuit_breaker_expected:
        # Gold must escalate and must NOT drop a third Howler
        if gold_escalated and not has_drop_instruction:
            per_scenario_score = 1.0
        else:
            per_scenario_score = 0.0
    else:
        # Gold must NOT apply circuit breaker
        if gold_escalated and any(kw in raw_lower for kw in ["circuit breaker", "two failures", "2 failures"]):
            # Unnecessarily applied — over-conservative
            per_scenario_score = 0.5
        else:
            per_scenario_score = 1.0

    return {
        "id": item["id"],
        "name": item["name"],
        "weight": item["weight"],
        "scoring_method": item["scoring_method"],
        "score": round(per_scenario_score, 4),
        "threshold_pass": item["threshold_pass"],
        "passes": per_scenario_score >= item["threshold_pass"],
        "detail": {
            "circuit_breaker_expected": circuit_breaker_expected,
            "gold_escalated": gold_escalated,
            "has_drop_instruction": has_drop_instruction,
        },
        "needs_human_review": False,
    }


# ---------------------------------------------------------------------------
# 4. Escalation Appropriateness (hybrid)
# ---------------------------------------------------------------------------

def _score_escalation_appropriateness(result: dict, scenario: dict, item: dict) -> dict:
    raw_output = result.get("raw_output", "") or ""

    gold_classification = _extract_classification(raw_output)
    correct_classification = (scenario.get("correct_classification") or "").lower().strip()

    # Use gold's own classification for escalation expectation (avoid double-penalising
    # misclassification)
    effective_classification = gold_classification or correct_classification
    should_escalate = _escalation_expected(effective_classification)
    did_escalate = _gold_escalated(raw_output)

    correct_escalation = (did_escalate == should_escalate)
    automated_score = 1.0 if correct_escalation else 0.0

    # Actionability excerpt for human review (only relevant if Gold escalated)
    excerpt = {
        "should_escalate": should_escalate,
        "did_escalate": did_escalate,
        "gold_classification": gold_classification,
        "correct_escalation": correct_escalation,
        "review_guidance": item.get("human_criteria", ""),
        "classification_options": ["ACTIONABLE", "INCOMPLETE", "NOT_ESCALATED"],
        "instructions": (
            "If Gold escalated, check whether it presented at least 2 of the 4 "
            "recovery options (Resume / Retry / Skip / Restructure) with tradeoffs."
        ),
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
            "should_escalate": should_escalate,
            "did_escalate": did_escalate,
            "gold_classification_used": effective_classification,
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
    "forge_classification_accuracy": _score_classification_accuracy,
    "forge_recovery_action_correctness": _score_recovery_action,
    "forge_circuit_breaker_application": _score_circuit_breaker,
    "forge_escalation_appropriateness": _score_escalation_appropriateness,
}


def score_forge(result: dict, scenario: dict, rubric: dict) -> dict:
    """
    Score a Forge result against its scenario ground-truth and rubric.

    Returns a dict with: scenario_id, model, phase, items, phase_score,
    phase_score_is_partial, needs_human_review.
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
        "phase": "forge",
        "items": items_scored,
        "phase_score": round(phase_score, 4) if phase_score is not None else None,
        "phase_score_is_partial": is_partial,
        "needs_human_review": human_review_queue,
        "tokens_used": result.get("tokens_used"),
        "latency_ms": result.get("latency_ms"),
        "cost_usd": result.get("cost_usd"),
    }
