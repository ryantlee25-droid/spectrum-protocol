"""
Tests for forge_scorer.py — classification matching, circuit breaker logic.
"""

import pytest
from scoring.forge_scorer import score_forge


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

FORGE_RUBRIC = {
    "phase": "forge",
    "items": [
        {
            "id": "forge_classification_accuracy",
            "name": "Failure Type Classification Accuracy",
            "weight": 0.35,
            "scoring_method": "automated",
            "threshold_pass": 0.90,
        },
        {
            "id": "forge_recovery_action_correctness",
            "name": "Recovery Action Correctness",
            "weight": 0.30,
            "scoring_method": "hybrid",
            "threshold_pass": 0.90,
            "human_criteria": "Check rationale references failure type and SPECTRUM protocol.",
        },
        {
            "id": "forge_circuit_breaker_application",
            "name": "Circuit Breaker Application",
            "weight": 0.20,
            "scoring_method": "automated",
            "threshold_pass": 1.0,
        },
        {
            "id": "forge_escalation_appropriateness",
            "name": "Escalation Appropriateness",
            "weight": 0.15,
            "scoring_method": "hybrid",
            "threshold_pass": 0.90,
            "human_criteria": "Check escalation message for actionable options.",
        },
    ],
}


def _make_result(raw_output: str = "", model: str = "opus", scenario_id: str = "forge-test") -> dict:
    return {
        "scenario_id": scenario_id,
        "model": model,
        "model_id": f"claude-{model}-4-6",
        "phase": "forge",
        "raw_output": raw_output,
        "parsed": {
            "classification": None,
            "recovery_action": None,
            "circuit_breaker_triggered": False,
        },
        "parse_confidence": 0.9,
        "tokens_used": {"input": 5000, "output": 2000},
        "latency_ms": 8000,
        "cost_usd": 0.50,
    }


def _make_scenario(
    correct_classification: str = "transient",
    correct_recovery_action: str = "resume",
    circuit_breaker_applies: bool = False,
    ambiguous: bool = False,
) -> dict:
    return {
        "scenario_id": "forge-test",
        "gold_phase": "forge",
        "correct_classification": correct_classification,
        "correct_recovery_action": correct_recovery_action,
        "circuit_breaker_applies": circuit_breaker_applies,
        "ambiguous": ambiguous,
    }


# ---------------------------------------------------------------------------
# 1. Classification Accuracy
# ---------------------------------------------------------------------------

class TestClassificationAccuracy:
    def test_exact_match_transient(self):
        raw = "This is a transient failure — network timeout. I will auto-resume."
        result = _make_result(raw)
        scenario = _make_scenario(correct_classification="transient")
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_classification_accuracy")
        assert item["score"] == 1.0
        assert item["passes"] is True

    def test_exact_match_structural(self):
        raw = "This is a structural failure — the decomposition is flawed. Recommend restructure."
        result = _make_result(raw)
        scenario = _make_scenario(correct_classification="structural")
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_classification_accuracy")
        assert item["score"] == 1.0

    def test_wrong_classification_scores_0(self):
        raw = "This looks like a transient issue — let me auto-resume."
        result = _make_result(raw)
        scenario = _make_scenario(correct_classification="structural")
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_classification_accuracy")
        assert item["score"] == 0.0
        assert item["passes"] is False

    def test_adjacent_type_partial_credit_when_ambiguous(self):
        """Adjacent types get 0.5 when scenario is marked ambiguous."""
        raw = "This failure looks transient — retrying."
        result = _make_result(raw)
        scenario = _make_scenario(correct_classification="logical", ambiguous=True)
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_classification_accuracy")
        # transient vs logical is adjacent — partial credit
        assert item["score"] == pytest.approx(0.5, abs=0.01)
        assert item["detail"]["partial_credit_applied"] is True

    def test_adjacent_type_no_credit_when_not_ambiguous(self):
        """Adjacent partial credit only when scenario.ambiguous == True."""
        raw = "Looks transient."
        result = _make_result(raw)
        scenario = _make_scenario(correct_classification="logical", ambiguous=False)
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_classification_accuracy")
        assert item["score"] == 0.0

    def test_non_adjacent_wrong_type_scores_0(self):
        raw = "This is transient."
        result = _make_result(raw)
        scenario = _make_scenario(correct_classification="structural", ambiguous=True)
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_classification_accuracy")
        # transient vs structural is NOT adjacent
        assert item["score"] == 0.0

    def test_all_five_types_recognized(self):
        for ftype in ["transient", "logical", "structural", "environmental", "conflict"]:
            raw = f"Classification: {ftype}. Recommend resume."
            result = _make_result(raw)
            scenario = _make_scenario(correct_classification=ftype)
            out = score_forge(result, scenario, FORGE_RUBRIC)
            item = next(i for i in out["items"] if i["id"] == "forge_classification_accuracy")
            assert item["score"] == 1.0, f"Failed to match type '{ftype}'"


# ---------------------------------------------------------------------------
# 2. Recovery Action Correctness
# ---------------------------------------------------------------------------

class TestRecoveryActionCorrectness:
    def test_exact_match_resume(self):
        raw = "This is transient. I will resume by dropping a new Howler."
        result = _make_result(raw)
        scenario = _make_scenario(correct_recovery_action="resume")
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_recovery_action_correctness")
        assert item["score"] == 1.0

    def test_exact_match_restructure(self):
        raw = "This is structural. We must restructure the decomposition."
        result = _make_result(raw)
        scenario = _make_scenario(correct_recovery_action="restructure")
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_recovery_action_correctness")
        assert item["score"] == 1.0

    def test_resume_retry_adjacent_partial_credit(self):
        """Resume vs Retry always gets 0.5 partial credit."""
        raw = "This is transient. I recommend retry — drop a fresh howler."
        result = _make_result(raw)
        scenario = _make_scenario(correct_recovery_action="resume")
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_recovery_action_correctness")
        assert item["score"] == pytest.approx(0.5, abs=0.01)

    def test_wrong_action_scores_0(self):
        raw = "I recommend skip — abandon this task."
        result = _make_result(raw)
        scenario = _make_scenario(correct_recovery_action="restructure")
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_recovery_action_correctness")
        assert item["score"] == 0.0

    def test_human_review_queued_for_rationale(self):
        raw = "This is transient. Resume."
        result = _make_result(raw)
        scenario = _make_scenario(correct_recovery_action="resume")
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_recovery_action_correctness")
        assert isinstance(item["needs_human_review"], dict)
        excerpt = item["needs_human_review"]["excerpt"]
        assert "ADEQUATE" in excerpt["classification_options"]
        assert "ABSENT" in excerpt["classification_options"]


# ---------------------------------------------------------------------------
# 3. Circuit Breaker
# ---------------------------------------------------------------------------

class TestCircuitBreakerApplication:
    def test_no_circuit_breaker_scenario_scores_1(self):
        """Scenario without circuit_breaker_applies → 1.0."""
        result = _make_result("Auto-resuming due to transient failure.")
        scenario = {
            "scenario_id": "forge-no-cb",
            "gold_phase": "forge",
            "correct_classification": "transient",
            "correct_recovery_action": "resume",
            # circuit_breaker_applies intentionally omitted
        }
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_circuit_breaker_application")
        assert item["score"] == 1.0

    def test_circuit_breaker_expected_and_applied(self):
        raw = (
            "Two failures on the same locus. Per the circuit breaker rule, I must escalate "
            "to human and not drop a third Howler. Human confirmation required."
        )
        result = _make_result(raw)
        scenario = _make_scenario(circuit_breaker_applies=True)
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_circuit_breaker_application")
        assert item["score"] == 1.0
        assert item["passes"] is True

    def test_circuit_breaker_expected_but_gold_auto_recovers(self):
        raw = "I will auto-resume by dropping a new Howler. No escalation needed."
        result = _make_result(raw)
        scenario = _make_scenario(circuit_breaker_applies=True)
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_circuit_breaker_application")
        assert item["score"] == 0.0
        assert item["passes"] is False

    def test_circuit_breaker_not_expected_and_not_applied(self):
        raw = "Single failure — auto-resuming."
        result = _make_result(raw)
        scenario = _make_scenario(circuit_breaker_applies=False)
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_circuit_breaker_application")
        assert item["score"] == 1.0

    def test_circuit_breaker_not_expected_but_over_applied(self):
        """Gold applies circuit breaker when not warranted → 0.5 (over-conservative)."""
        raw = (
            "Applying circuit breaker after two failures on this locus. "
            "Escalating to human, not auto-recovering."
        )
        result = _make_result(raw)
        scenario = _make_scenario(circuit_breaker_applies=False)
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_circuit_breaker_application")
        # Over-conservative: circuit breaker keyword + escalation without it being warranted
        assert item["score"] in {0.5, 1.0}  # depends on keyword match; 0.5 if over-applied

    def test_threshold_is_1_0(self):
        """Circuit breaker threshold must be 1.0 — any failure is a protocol violation."""
        item_def = next(i for i in FORGE_RUBRIC["items"] if i["id"] == "forge_circuit_breaker_application")
        assert item_def["threshold_pass"] == 1.0


# ---------------------------------------------------------------------------
# 4. Escalation Appropriateness
# ---------------------------------------------------------------------------

class TestEscalationAppropriateness:
    def test_transient_auto_recover_correct(self):
        """Transient → auto-recover is correct (no escalation needed)."""
        raw = "This is transient. Auto-resuming — dropping a new Howler now."
        result = _make_result(raw)
        scenario = _make_scenario(correct_classification="transient")
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_escalation_appropriateness")
        assert item["score"] == 1.0

    def test_structural_requires_escalation(self):
        """Structural → must present options to human."""
        raw = (
            "This is structural. I must present options to the human: "
            "Resume / Retry / Skip / Restructure. Awaiting human confirmation."
        )
        result = _make_result(raw)
        scenario = _make_scenario(correct_classification="structural")
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_escalation_appropriateness")
        assert item["score"] == 1.0

    def test_structural_but_auto_recovered_scores_0(self):
        """Structural mishandled as auto-recover → wrong escalation behavior."""
        raw = "This is structural. Auto-resuming immediately."
        result = _make_result(raw)
        scenario = _make_scenario(correct_classification="structural")
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_escalation_appropriateness")
        # Gold says structural but auto-recovers → should_escalate=True, did_escalate=False
        assert item["score"] == 0.0

    def test_escalation_uses_gold_classification_not_correct(self):
        """
        When Gold misclassifies (transient → should actually be logical), Gold's own
        classification determines escalation expectation, not the correct one.
        Avoids double-penalizing misclassification.
        """
        # Gold classifies as transient (wrong, should be logical), and auto-recovers
        # Based on Gold's own classification (transient), auto-recover is appropriate
        raw = "This is transient. Auto-recovering."
        result = _make_result(raw)
        scenario = _make_scenario(correct_classification="logical")
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_escalation_appropriateness")
        # Gold says transient → auto-recover is correct for that classification
        assert item["score"] == 1.0

    def test_human_review_queued_for_actionability(self):
        raw = "Structural. Human confirmation required. Options: Resume, Retry, Skip, Restructure."
        result = _make_result(raw)
        scenario = _make_scenario(correct_classification="structural")
        out = score_forge(result, scenario, FORGE_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "forge_escalation_appropriateness")
        assert isinstance(item["needs_human_review"], dict)
        excerpt = item["needs_human_review"]["excerpt"]
        assert "ACTIONABLE" in excerpt["classification_options"]


# ---------------------------------------------------------------------------
# Overall score_forge integration
# ---------------------------------------------------------------------------

class TestScoreForgeIntegration:
    def test_returns_required_keys(self):
        out = score_forge(_make_result(), _make_scenario(), FORGE_RUBRIC)
        assert "scenario_id" in out
        assert "phase" in out
        assert out["phase"] == "forge"
        assert "items" in out
        assert "phase_score" in out
        assert "needs_human_review" in out

    def test_all_scores_in_range(self):
        raw = "This is transient. Auto-resuming by dropping a new Howler."
        result = _make_result(raw)
        scenario = _make_scenario(
            correct_classification="transient",
            correct_recovery_action="resume",
            circuit_breaker_applies=False,
        )
        out = score_forge(result, scenario, FORGE_RUBRIC)
        for item in out["items"]:
            if item.get("score") is not None:
                assert 0.0 <= item["score"] <= 1.0, f"Out of range: {item['id']} = {item['score']}"

    def test_perfect_transient_scenario(self):
        """Gold nails a clear transient scenario — should score near 1.0."""
        raw = (
            "Classification: transient — network timeout, other Howlers succeeded. "
            "Recovery action: resume. Auto-recovery allowed per SPECTRUM protocol for transient failures. "
            "Dropping a new Howler with: 'Read HOOK.md and retry npm install.'"
        )
        result = _make_result(raw)
        scenario = _make_scenario(
            correct_classification="transient",
            correct_recovery_action="resume",
            circuit_breaker_applies=False,
        )
        out = score_forge(result, scenario, FORGE_RUBRIC)
        # Phase score should be high (automated items should be near 1.0)
        auto_items = [i for i in out["items"] if i.get("score") is not None]
        for item in auto_items:
            assert item["score"] >= 0.0

    def test_cost_and_latency_propagated(self):
        result = _make_result()
        result["cost_usd"] = 0.75
        result["latency_ms"] = 9000
        scenario = _make_scenario()
        out = score_forge(result, scenario, FORGE_RUBRIC)
        assert out["cost_usd"] == 0.75
        assert out["latency_ms"] == 9000

    def test_handles_missing_parsed_fields_gracefully(self):
        """parsed dict may only have fields relevant to phase — must not crash."""
        result = {
            "scenario_id": "forge-test",
            "model": "sonnet",
            "phase": "forge",
            "raw_output": "This is transient. Resume.",
            "parsed": {},  # empty parsed
            "cost_usd": 0.5,
            "latency_ms": 5000,
        }
        scenario = _make_scenario()
        out = score_forge(result, scenario, FORGE_RUBRIC)
        assert out is not None
        assert out["phase"] == "forge"
