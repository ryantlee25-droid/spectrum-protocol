"""
composite_scorer.py — Computes weighted composite scores across phases.

Applies the 40/40/20 weighting from scoring-guide.yaml.
"""

from __future__ import annotations

from typing import Any

# Phase thresholds from scoring-guide.yaml
PHASE_THRESHOLDS = {
    "muster": 0.85,
    "pax": 0.80,
    "forge": 0.90,
}
COMPOSITE_THRESHOLD = 0.84

# Tolerance bands (relative comparison, Sonnet vs Opus)
PHASE_TOLERANCE = 0.05
COMPOSITE_TOLERANCE = 0.03


def _mean_phase_score(scored_results: list[dict]) -> float | None:
    """
    Compute the mean phase_score across a list of scored result dicts.
    Excludes results with None phase_score (pending human review).
    """
    scores = [r["phase_score"] for r in scored_results if r.get("phase_score") is not None]
    if not scores:
        return None
    return sum(scores) / len(scores)


def compute_composite(
    muster_scores: list[dict],
    pax_scores: list[dict],
    forge_scores: list[dict],
    scoring_guide: dict,
) -> dict:
    """
    Compute per-phase averages and weighted composite score.

    Args:
        muster_scores: List of score dicts from muster_scorer.score_muster().
        pax_scores:    List of score dicts from pax_scorer.score_pax().
        forge_scores:  List of score dicts from forge_scorer.score_forge().
        scoring_guide: scoring-guide.yaml loaded as dict.

    Returns:
        Dict with:
          - per_phase: {muster, pax, forge} each with score, threshold, passes, scenario_count
          - composite_score: float or None
          - composite_threshold: 0.84
          - composite_passes: bool or None
          - is_partial: bool
          - weights_used: {muster: 0.4, pax: 0.4, forge: 0.2}
    """
    weights = scoring_guide.get("composite_formula", {}).get("weights", {
        "muster": 0.40,
        "pax": 0.40,
        "forge": 0.20,
    })
    thresholds_config = scoring_guide.get("thresholds", {})

    muster_score = _mean_phase_score(muster_scores)
    pax_score = _mean_phase_score(pax_scores)
    forge_score = _mean_phase_score(forge_scores)

    muster_threshold = thresholds_config.get("muster", {}).get("pass", PHASE_THRESHOLDS["muster"])
    pax_threshold = thresholds_config.get("pax", {}).get("pass", PHASE_THRESHOLDS["pax"])
    forge_threshold = thresholds_config.get("forge", {}).get("pass", PHASE_THRESHOLDS["forge"])
    composite_threshold = thresholds_config.get("composite", {}).get("pass", COMPOSITE_THRESHOLD)

    per_phase = {
        "muster": {
            "score": muster_score,
            "threshold": muster_threshold,
            "passes": (muster_score >= muster_threshold) if muster_score is not None else None,
            "scenario_count": len(muster_scores),
        },
        "pax": {
            "score": pax_score,
            "threshold": pax_threshold,
            "passes": (pax_score >= pax_threshold) if pax_score is not None else None,
            "scenario_count": len(pax_scores),
        },
        "forge": {
            "score": forge_score,
            "threshold": forge_threshold,
            "passes": (forge_score >= forge_threshold) if forge_score is not None else None,
            "scenario_count": len(forge_scores),
        },
    }

    # Compute composite only if all phases have scores
    all_scored = all(s is not None for s in [muster_score, pax_score, forge_score])
    if all_scored:
        composite_score = (
            weights.get("muster", 0.40) * muster_score +
            weights.get("pax", 0.40) * pax_score +
            weights.get("forge", 0.20) * forge_score
        )
        composite_score = round(composite_score, 4)
        composite_passes = composite_score >= composite_threshold
    else:
        composite_score = None
        composite_passes = None

    any_partial = any(
        any(r.get("phase_score_is_partial") for r in group)
        for group in [muster_scores, pax_scores, forge_scores]
        if group
    )

    return {
        "per_phase": per_phase,
        "composite_score": composite_score,
        "composite_threshold": composite_threshold,
        "composite_passes": composite_passes,
        "is_partial": any_partial,
        "weights_used": {
            "muster": weights.get("muster", 0.40),
            "pax": weights.get("pax", 0.40),
            "forge": weights.get("forge", 0.20),
        },
    }


def within_tolerance(
    opus_composite: dict,
    sonnet_composite: dict,
) -> dict:
    """
    Check whether Sonnet scores are within the acceptable tolerance band of Opus.

    Args:
        opus_composite:   Output of compute_composite() for opus model.
        sonnet_composite: Output of compute_composite() for sonnet model.

    Returns:
        Dict with per-phase and composite within_tolerance booleans, and deltas.
    """
    tolerance_result: dict[str, Any] = {"phases": {}, "composite": {}}

    for phase in ["muster", "pax", "forge"]:
        opus_score = opus_composite["per_phase"][phase]["score"]
        sonnet_score = sonnet_composite["per_phase"][phase]["score"]
        if opus_score is not None and sonnet_score is not None:
            delta = round(sonnet_score - opus_score, 4)
            in_band = abs(delta) <= PHASE_TOLERANCE
        else:
            delta = None
            in_band = None
        tolerance_result["phases"][phase] = {
            "opus_score": opus_score,
            "sonnet_score": sonnet_score,
            "delta": delta,
            "within_tolerance": in_band,
        }

    opus_comp = opus_composite.get("composite_score")
    sonnet_comp = sonnet_composite.get("composite_score")
    if opus_comp is not None and sonnet_comp is not None:
        comp_delta = round(sonnet_comp - opus_comp, 4)
        comp_in_band = abs(comp_delta) <= COMPOSITE_TOLERANCE
    else:
        comp_delta = None
        comp_in_band = None

    tolerance_result["composite"] = {
        "opus_score": opus_comp,
        "sonnet_score": sonnet_comp,
        "delta": comp_delta,
        "within_tolerance": comp_in_band,
    }

    return tolerance_result
