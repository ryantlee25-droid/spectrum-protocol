"""
Tests for pax_scorer.py — deviation detection precision/recall, false positive rate.
"""
from __future__ import annotations

import pytest
from scoring.pax_scorer import score_pax


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

PAX_RUBRIC = {
    "phase": "pax",
    "items": [
        {
            "id": "pax_deviation_detection_rate",
            "name": "Deviation Detection Rate",
            "weight": 0.30,
            "scoring_method": "automated",
            "threshold_pass": 0.85,
        },
        {
            "id": "pax_false_positive_rate",
            "name": "False Positive Rate on Correct Howlers",
            "weight": 0.20,
            "scoring_method": "automated",
            "threshold_pass": 0.80,
        },
        {
            "id": "pax_seam_cross_reference_accuracy",
            "name": "Seam Cross-Reference Accuracy",
            "weight": 0.20,
            "scoring_method": "automated",
            "threshold_pass": 0.85,
        },
        {
            "id": "pax_risk_classification",
            "name": "Integration Risk Classification",
            "weight": 0.15,
            "scoring_method": "hybrid",
            "threshold_pass": 0.80,
            "human_criteria": "Check merge order consistency.",
        },
        {
            "id": "pax_validation_depth",
            "name": "Validation Depth for Low-Confidence Howlers",
            "weight": 0.15,
            "scoring_method": "hybrid",
            "threshold_pass": 0.75,
            "human_criteria": "Classify file inspection as DEEP/SHALLOW/NONE.",
        },
    ],
}


def _make_result(raw_output: str = "", model: str = "opus", scenario_id: str = "pax-test") -> dict:
    return {
        "scenario_id": scenario_id,
        "model": model,
        "model_id": f"claude-{model}-4-6",
        "phase": "pax",
        "raw_output": raw_output,
        "parsed": {"deviation_flags": []},
        "parse_confidence": 0.9,
        "tokens_used": {"input": 30000, "output": 8000},
        "latency_ms": 15000,
        "cost_usd": 1.5,
    }


def _make_scenario(
    injected_deviations: list[dict] | None = None,
    correct_howlers: list[str] | None = None,
    debrief_set: list[dict] | None = None,
    confidence_levels: dict | None = None,
) -> dict:
    return {
        "scenario_id": "pax-test",
        "gold_phase": "pax",
        "injected_deviations": injected_deviations or [],
        "correct_howlers": correct_howlers or [],
        "debrief_set": debrief_set or [],
        "confidence_levels": confidence_levels or {},
    }


# ---------------------------------------------------------------------------
# Deviation Detection — Recall and Precision
# ---------------------------------------------------------------------------

class TestDeviationDetectionRate:
    def test_no_deviations_scores_1(self):
        result = _make_result("Everything looks good.")
        scenario = _make_scenario(
            injected_deviations=[],
            debrief_set=[{"howler": "howler-auth", "hook_md": "", "debrief": "Done."}],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_deviation_detection_rate")
        assert item["score"] == 1.0

    def test_deviation_caught_by_howler_flag(self):
        raw = (
            "howler-api has a blocker: the function is named validateReq not validateRequest. "
            "This breaks any caller using the contract name."
        )
        result = _make_result(raw)
        scenario = _make_scenario(
            injected_deviations=[{
                "howler": "howler-api",
                "deviation_type": "postcondition_violation",
                "description": "CONTRACT requires export named validateRequest but function is named validateReq.",
                "severity": "blocker",
                "is_detectable": True,
            }],
            correct_howlers=["howler-auth", "howler-ui"],
            debrief_set=[
                {"howler": "howler-api", "debrief": "Done.", "hook_md": ""},
                {"howler": "howler-auth", "debrief": "Done.", "hook_md": ""},
                {"howler": "howler-ui", "debrief": "Done.", "hook_md": ""},
            ],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_deviation_detection_rate")
        assert item["detail"]["recall"] == 1.0
        assert item["score"] > 0.7

    def test_deviation_missed_scores_low(self):
        raw = "All howlers look clean. No issues found."
        result = _make_result(raw)
        scenario = _make_scenario(
            injected_deviations=[{
                "howler": "howler-api",
                "deviation_type": "postcondition_violation",
                "description": "validateRequest function named validateReq instead.",
                "severity": "blocker",
                "is_detectable": True,
            }],
            correct_howlers=["howler-auth"],
            debrief_set=[
                {"howler": "howler-api", "debrief": "Done.", "hook_md": ""},
                {"howler": "howler-auth", "debrief": "Done.", "hook_md": ""},
            ],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_deviation_detection_rate")
        assert item["detail"]["recall"] == 0.0

    def test_high_confidence_howler_double_weight(self):
        """High-confidence howler deviations count double in recall numerator/denominator."""
        raw = "howler-api blocker: wrong export name."
        result = _make_result(raw)
        scenario = _make_scenario(
            injected_deviations=[{
                "howler": "howler-api",
                "deviation_type": "postcondition_violation",
                "description": "export name mismatch in api module.",
                "severity": "blocker",
                "is_detectable": True,
            }],
            correct_howlers=["howler-auth"],
            debrief_set=[
                {"howler": "howler-api", "debrief": "Done.", "hook_md": ""},
                {"howler": "howler-auth", "debrief": "Done.", "hook_md": ""},
            ],
            confidence_levels={"howler-api": "high"},
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_deviation_detection_rate")
        detail = item["detail"]
        # high-confidence howler caught → weight=2, detectable_weighted=2, caught=2
        assert detail["detectable_weighted"] == 2.0
        assert detail["caught_weighted"] == pytest.approx(2.0, abs=0.01)
        assert detail["recall"] == 1.0

    def test_precision_and_recall_stored_separately(self):
        raw = "howler-api has an issue: blocker on validateRequest export."
        result = _make_result(raw)
        scenario = _make_scenario(
            injected_deviations=[{
                "howler": "howler-api",
                "deviation_type": "postcondition_violation",
                "description": "validateRequest not exported.",
                "severity": "blocker",
                "is_detectable": True,
            }],
            correct_howlers=["howler-auth"],
            debrief_set=[
                {"howler": "howler-api", "debrief": "Done.", "hook_md": ""},
                {"howler": "howler-auth", "debrief": "Done.", "hook_md": ""},
            ],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_deviation_detection_rate")
        assert "recall" in item["detail"]
        assert "precision" in item["detail"]
        assert item["detail"]["score_formula"] == "0.7 * recall + 0.3 * precision"


# ---------------------------------------------------------------------------
# False Positive Rate
# ---------------------------------------------------------------------------

class TestFalsePositiveRate:
    def test_no_flags_on_correct_howlers_scores_1(self):
        raw = "howler-api: blocker — wrong export name."
        result = _make_result(raw)
        scenario = _make_scenario(
            injected_deviations=[{"howler": "howler-api", "description": "export mismatch", "severity": "blocker"}],
            correct_howlers=["howler-auth", "howler-ui"],
            debrief_set=[
                {"howler": "howler-api", "debrief": "", "hook_md": ""},
                {"howler": "howler-auth", "debrief": "", "hook_md": ""},
                {"howler": "howler-ui", "debrief": "", "hook_md": ""},
            ],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_false_positive_rate")
        assert item["score"] == 1.0
        assert item["passes"] is True

    def test_false_flag_on_correct_howler_reduces_score(self):
        # Gold flags howler-auth (which is correct) as a blocker
        raw = (
            "howler-api: blocker — export name mismatch. "
            "howler-auth: warning — suspicious import pattern."
        )
        result = _make_result(raw)
        scenario = _make_scenario(
            injected_deviations=[{"howler": "howler-api", "description": "export mismatch", "severity": "blocker"}],
            correct_howlers=["howler-auth"],
            debrief_set=[
                {"howler": "howler-api", "debrief": "", "hook_md": ""},
                {"howler": "howler-auth", "debrief": "", "hook_md": ""},
            ],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_false_positive_rate")
        assert item["score"] < 1.0

    def test_observation_on_correct_howler_counts_030(self):
        """Observations are penalized at 30% weight, not full 1.0."""
        raw = "howler-auth: observation — minor style note, no action required."
        result = _make_result(raw)
        scenario = _make_scenario(
            injected_deviations=[],
            correct_howlers=["howler-auth"],
            debrief_set=[{"howler": "howler-auth", "debrief": "", "hook_md": ""}],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_false_positive_rate")
        # observation → 0.3 flag weight → score = 1 - 0.3 = 0.7
        assert item["score"] == pytest.approx(0.7, abs=0.05)

    def test_no_correct_howlers_scores_1(self):
        result = _make_result("Issues found.")
        scenario = _make_scenario(correct_howlers=[])
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_false_positive_rate")
        assert item["score"] == 1.0


# ---------------------------------------------------------------------------
# Seam Cross-Reference Accuracy
# ---------------------------------------------------------------------------

class TestSeamCrossReference:
    def test_no_seams_scores_1(self):
        result = _make_result("All seams confirmed.")
        scenario = _make_scenario(
            debrief_set=[{"howler": "howler-auth", "debrief": "", "hook_md": ""}],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_seam_cross_reference_accuracy")
        assert item["score"] == 1.0

    def test_seam_addressed_in_output_counts_correct(self):
        raw = (
            "howler-auth exports UserSession from src/auth/index.ts. "
            "howler-ui correctly imports UserSession — seam confirmed."
        )
        result = _make_result(raw)
        scenario = _make_scenario(
            debrief_set=[{
                "howler": "howler-auth",
                "debrief": "Exports UserSession.",
                "hook_md": (
                    "## Seams Declared\n"
                    "- howler-ui imports UserSession from src/auth/index.ts"
                ),
                "seams_declared": [
                    {"seam_id": "auth-seam-1", "counterpart_howler": "howler-ui",
                     "description": "howler-ui imports UserSession from src/auth/index.ts"},
                ],
            }],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_seam_cross_reference_accuracy")
        assert item["score"] >= 0.5  # at least some seams addressed


# ---------------------------------------------------------------------------
# Risk Classification
# ---------------------------------------------------------------------------

class TestRiskClassification:
    def test_correct_risk_level_scores_1(self):
        # Gold flags howler-api as blocker, which matches scenario expectation
        raw = "howler-api: blocker — validateRequest not exported as contracted."
        result = _make_result(raw)
        scenario = _make_scenario(
            injected_deviations=[{
                "howler": "howler-api",
                "deviation_type": "postcondition_violation",
                "description": "validateRequest export missing.",
                "severity": "blocker",
            }],
            correct_howlers=["howler-auth"],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_risk_classification")
        assert item["score"] >= 0.8

    def test_no_caught_deviations_inherits_1(self):
        raw = "All clean."
        result = _make_result(raw)
        scenario = _make_scenario(
            injected_deviations=[{
                "howler": "howler-api",
                "description": "export mismatch.",
                "severity": "blocker",
            }],
            correct_howlers=["howler-auth"],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_risk_classification")
        # No deviations caught → inherits 1.0 (sentinel)
        assert item["score"] == 1.0


# ---------------------------------------------------------------------------
# Validation Depth
# ---------------------------------------------------------------------------

class TestValidationDepth:
    def test_no_low_confidence_howlers_scores_1(self):
        result = _make_result("All good.")
        scenario = _make_scenario(
            debrief_set=[{"howler": "howler-auth", "confidence": "high", "debrief": "", "hook_md": ""}],
            injected_deviations=[],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_validation_depth")
        assert item["score"] == 1.0

    def test_low_confidence_howler_with_file_evidence_scores_high(self):
        raw = (
            "howler-analytics (low confidence): inspected src/features/analytics/AnalyticsCollector.ts. "
            "export function initAnalytics(): () => void — confirmed wildcard subscription via '*'. "
            "Line 8: bus.subscribe<DomainEvent>('*', handler) matches contract. "
            "PASS — implementation matches CONTRACT.md postcondition."
        )
        result = _make_result(raw)
        scenario = _make_scenario(
            debrief_set=[{
                "howler": "howler-analytics",
                "confidence": "low",
                "debrief": "Analytics collector implemented.",
                "hook_md": "## Status: complete",
            }],
            confidence_levels={"howler-analytics": "low"},
            injected_deviations=[],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_validation_depth")
        assert item["score"] > 0.0
        assert isinstance(item["needs_human_review"], dict)

    def test_human_review_excerpt_includes_howlers(self):
        result = _make_result("Summary only, no file evidence.")
        scenario = _make_scenario(
            debrief_set=[{"howler": "howler-analytics", "confidence": "low", "debrief": "", "hook_md": ""}],
            confidence_levels={"howler-analytics": "low"},
            injected_deviations=[],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_validation_depth")
        excerpt = item["needs_human_review"]["excerpt"]
        assert "howler-analytics" in excerpt["low_conf_howlers"]
        assert "DEEP" in excerpt["classification_options"]


# ---------------------------------------------------------------------------
# Overall score_pax integration
# ---------------------------------------------------------------------------

class TestScorePaxIntegration:
    def test_returns_required_keys(self):
        out = score_pax(_make_result(), _make_scenario(), PAX_RUBRIC)
        assert "scenario_id" in out
        assert "phase" in out
        assert out["phase"] == "pax"
        assert "items" in out
        assert "needs_human_review" in out

    def test_all_scores_in_range(self):
        raw = "howler-api: blocker — export mismatch."
        result = _make_result(raw)
        scenario = _make_scenario(
            injected_deviations=[{
                "howler": "howler-api",
                "description": "export name mismatch.",
                "severity": "blocker",
                "is_detectable": True,
            }],
            correct_howlers=["howler-auth"],
            debrief_set=[
                {"howler": "howler-api", "debrief": "", "hook_md": ""},
                {"howler": "howler-auth", "debrief": "", "hook_md": ""},
            ],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        for item in out["items"]:
            if item.get("score") is not None:
                assert 0.0 <= item["score"] <= 1.0, f"Out of range: {item['id']} = {item['score']}"

    def test_deviation_detection_stores_precision_and_recall_separately(self):
        """Core contract: precision and recall must be stored separately."""
        raw = "howler-api: blocker — export mismatch."
        result = _make_result(raw)
        scenario = _make_scenario(
            injected_deviations=[{
                "howler": "howler-api",
                "description": "export name mismatch.",
                "severity": "blocker",
                "is_detectable": True,
            }],
            correct_howlers=["howler-auth"],
            debrief_set=[
                {"howler": "howler-api", "debrief": "", "hook_md": ""},
                {"howler": "howler-auth", "debrief": "", "hook_md": ""},
            ],
        )
        out = score_pax(result, scenario, PAX_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "pax_deviation_detection_rate")
        assert "recall" in item["detail"]
        assert "precision" in item["detail"]
        # Neither should be derived from the other (stored as distinct values)
        assert isinstance(item["detail"]["recall"], float)
        assert isinstance(item["detail"]["precision"], float)
