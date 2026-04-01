"""
Tests for muster_scorer.py — all 7 rubric dimensions.

Fixtures use synthetic result and scenario dicts.
"""
from __future__ import annotations

import pytest
from scoring.muster_scorer import score_muster


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

MUSTER_RUBRIC = {
    "phase": "muster",
    "items": [
        {
            "id": "muster_file_ownership_completeness",
            "name": "File Ownership Completeness",
            "weight": 0.18,
            "scoring_method": "automated",
            "threshold_pass": 0.95,
        },
        {
            "id": "muster_file_ownership_conflict_detection",
            "name": "File Ownership Conflict Detection",
            "weight": 0.15,
            "scoring_method": "automated",
            "threshold_pass": 1.0,
        },
        {
            "id": "muster_dag_edge_accuracy",
            "name": "DAG Edge Accuracy",
            "weight": 0.15,
            "scoring_method": "automated",
            "threshold_pass": 0.90,
        },
        {
            "id": "muster_contract_completeness",
            "name": "CONTRACT.md Completeness",
            "weight": 0.17,
            "scoring_method": "hybrid",
            "threshold_pass": 0.85,
            "human_criteria": "Review shared types and naming conventions.",
        },
        {
            "id": "muster_contract_precision",
            "name": "CONTRACT.md Postcondition Testability",
            "weight": 0.12,
            "scoring_method": "human",
            "threshold_pass": 0.80,
            "human_criteria": "Classify each postcondition as TESTABLE/VAGUE/ABSENT.",
        },
        {
            "id": "muster_decomposition_soundness",
            "name": "Decomposition Soundness",
            "weight": 0.12,
            "scoring_method": "hybrid",
            "threshold_pass": 0.85,
            "human_criteria": "Review Howler scope for single-responsibility.",
        },
        {
            "id": "muster_politico_integration",
            "name": "Politico Integration Quality",
            "weight": 0.11,
            "scoring_method": "hybrid",
            "threshold_pass": 0.80,
            "human_criteria": "Review Politico issue responses.",
        },
    ],
}


def _make_result(
    raw_output: str = "",
    file_ownership: list[dict] | None = None,
    dag_edges: list[dict] | None = None,
    contract_sections: list[dict] | None = None,
    model: str = "opus",
    scenario_id: str = "muster-test",
    cost_usd: float = 1.0,
    latency_ms: int = 5000,
) -> dict:
    return {
        "scenario_id": scenario_id,
        "model": model,
        "model_id": f"claude-{model}-4-6",
        "phase": "muster",
        "raw_output": raw_output,
        "parsed": {
            "file_ownership": file_ownership or [],
            "dag_edges": dag_edges or [],
            "contract_sections": contract_sections or [],
        },
        "parse_confidence": 0.9,
        "tokens_used": {"input": 10000, "output": 3000},
        "latency_ms": latency_ms,
        "cost_usd": cost_usd,
    }


def _make_scenario(
    expected_file_ownership: list[dict] | None = None,
    known_conflicts: list[dict] | None = None,
    expected_dag_edges: list[dict] | None = None,
    expected_contract_sections: list[dict] | None = None,
    politico_injection: list[dict] | None = None,
    serial_tasks_expected: list[str] | None = None,
) -> dict:
    return {
        "scenario_id": "muster-test",
        "gold_phase": "muster",
        "expected_file_ownership": expected_file_ownership or [],
        "known_conflicts": known_conflicts or [],
        "expected_dag_edges": expected_dag_edges or [],
        "expected_contract_sections": expected_contract_sections or [],
        "politico_injection": politico_injection or [],
        "serial_tasks_expected": serial_tasks_expected or [],
    }


# ---------------------------------------------------------------------------
# 1. File Ownership Completeness
# ---------------------------------------------------------------------------

class TestFileOwnershipCompleteness:
    def test_perfect_score_all_files_found(self):
        result = _make_result(file_ownership=[
            {"file": "pages/about.tsx", "howler": "howler-about", "action": "CREATES"},
            {"file": "pages/contact.tsx", "howler": "howler-contact", "action": "CREATES"},
        ])
        scenario = _make_scenario(expected_file_ownership=[
            {"file": "pages/about.tsx", "howler": "howler-about", "action": "CREATES"},
            {"file": "pages/contact.tsx", "howler": "howler-contact", "action": "CREATES"},
        ])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_file_ownership_completeness")
        assert item["score"] == 1.0
        assert item["passes"] is True

    def test_zero_score_no_files_found(self):
        result = _make_result(file_ownership=[])
        scenario = _make_scenario(expected_file_ownership=[
            {"file": "pages/about.tsx", "howler": "howler-about", "action": "CREATES"},
        ])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_file_ownership_completeness")
        assert item["score"] == 0.0
        assert item["passes"] is False

    def test_partial_score_some_files_missing(self):
        result = _make_result(file_ownership=[
            {"file": "pages/about.tsx", "howler": "howler-about", "action": "CREATES"},
        ])
        scenario = _make_scenario(expected_file_ownership=[
            {"file": "pages/about.tsx", "howler": "howler-about", "action": "CREATES"},
            {"file": "pages/contact.tsx", "howler": "howler-contact", "action": "CREATES"},
            {"file": "pages/404.tsx", "howler": "howler-404", "action": "CREATES"},
            {"file": "pages/blog.tsx", "howler": "howler-blog", "action": "CREATES"},
        ])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_file_ownership_completeness")
        assert item["score"] == pytest.approx(0.25, abs=0.01)
        assert item["passes"] is False

    def test_no_expected_files_scores_1(self):
        result = _make_result(file_ownership=[])
        scenario = _make_scenario(expected_file_ownership=[])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_file_ownership_completeness")
        assert item["score"] == 1.0

    def test_extra_found_files_dont_penalize(self):
        """Files Gold finds beyond expected should not reduce completeness score."""
        result = _make_result(file_ownership=[
            {"file": "pages/about.tsx", "howler": "h1", "action": "CREATES"},
            {"file": "pages/extra.tsx", "howler": "h2", "action": "CREATES"},
        ])
        scenario = _make_scenario(expected_file_ownership=[
            {"file": "pages/about.tsx", "howler": "h1", "action": "CREATES"},
        ])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_file_ownership_completeness")
        assert item["score"] == 1.0


# ---------------------------------------------------------------------------
# 2. File Ownership Conflict Detection
# ---------------------------------------------------------------------------

class TestConflictDetection:
    def test_no_conflicts_scores_1(self):
        result = _make_result(raw_output="No conflicts detected.")
        scenario = _make_scenario(known_conflicts=[])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_file_ownership_conflict_detection")
        assert item["score"] == 1.0
        assert item["passes"] is True

    def test_conflict_fully_found(self):
        raw = (
            "CONFLICT on src/types/auth.ts: both howler-jwt and howler-session claim ownership."
        )
        result = _make_result(raw_output=raw)
        scenario = _make_scenario(known_conflicts=[
            {"file": "src/types/auth.ts", "howlers": ["howler-jwt", "howler-session"]},
        ])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_file_ownership_conflict_detection")
        assert item["score"] == 1.0
        assert item["passes"] is True

    def test_conflict_file_only_partial_credit(self):
        """File found but no Howler names → 0.75 partial credit."""
        raw = "src/types/auth.ts has a potential conflict."
        result = _make_result(raw_output=raw)
        scenario = _make_scenario(known_conflicts=[
            {"file": "src/types/auth.ts", "howlers": ["howler-jwt", "howler-session"]},
        ])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_file_ownership_conflict_detection")
        assert 0.5 <= item["score"] <= 1.0
        assert item["passes"] is False  # threshold is 1.0

    def test_conflict_not_found(self):
        raw = "Everything looks fine."
        result = _make_result(raw_output=raw)
        scenario = _make_scenario(known_conflicts=[
            {"file": "src/types/auth.ts", "howlers": ["howler-jwt", "howler-session"]},
        ])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_file_ownership_conflict_detection")
        assert item["score"] == 0.0
        assert item["passes"] is False

    def test_multiple_conflicts_partial_detection(self):
        raw = "Conflict on src/types/auth.ts with howler-jwt and howler-session."
        result = _make_result(raw_output=raw)
        scenario = _make_scenario(known_conflicts=[
            {"file": "src/types/auth.ts", "howlers": ["howler-jwt", "howler-session"]},
            {"file": "src/auth/index.ts", "howlers": ["howler-router", "howler-middleware"]},
        ])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_file_ownership_conflict_detection")
        # First conflict caught (1.0), second missed (0.0) → avg 0.5
        assert item["score"] == pytest.approx(0.5, abs=0.1)


# ---------------------------------------------------------------------------
# 3. DAG Edge Accuracy
# ---------------------------------------------------------------------------

class TestDagEdgeAccuracy:
    def test_perfect_dag_score(self):
        result = _make_result(dag_edges=[
            {"from": "howler-a", "to": "howler-b"},
        ])
        scenario = _make_scenario(expected_dag_edges=[
            {"from": "howler-a", "to": "howler-b"},
        ])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_dag_edge_accuracy")
        assert item["score"] == 1.0
        assert item["detail"]["precision"] == 1.0
        assert item["detail"]["recall"] == 1.0

    def test_empty_expected_and_found_scores_1(self):
        result = _make_result(dag_edges=[])
        scenario = _make_scenario(expected_dag_edges=[])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_dag_edge_accuracy")
        assert item["score"] == 1.0

    def test_phantom_edge_penalizes_precision(self):
        result = _make_result(dag_edges=[
            {"from": "howler-a", "to": "howler-b"},
            {"from": "howler-c", "to": "howler-d"},  # phantom
        ])
        scenario = _make_scenario(expected_dag_edges=[
            {"from": "howler-a", "to": "howler-b"},
        ])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_dag_edge_accuracy")
        assert item["detail"]["precision"] < 1.0
        assert item["detail"]["recall"] == 1.0

    def test_missing_edge_penalizes_recall(self):
        result = _make_result(dag_edges=[])
        scenario = _make_scenario(expected_dag_edges=[
            {"from": "howler-a", "to": "howler-b"},
        ])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_dag_edge_accuracy")
        assert item["detail"]["recall"] == 0.0
        assert item["score"] == 0.0

    def test_f1_stored_as_score(self):
        """F1 is the item score; precision and recall stored separately."""
        result = _make_result(dag_edges=[
            {"from": "a", "to": "b"},
            {"from": "b", "to": "c"},
            {"from": "x", "to": "y"},  # phantom
        ])
        scenario = _make_scenario(expected_dag_edges=[
            {"from": "a", "to": "b"},
            {"from": "b", "to": "c"},
            {"from": "c", "to": "d"},  # missing
        ])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_dag_edge_accuracy")
        detail = item["detail"]
        # tp=2, fp=1, fn=1
        expected_precision = 2 / 3
        expected_recall = 2 / 3
        expected_f1 = 2 * expected_precision * expected_recall / (expected_precision + expected_recall)
        assert item["score"] == pytest.approx(expected_f1, abs=0.001)
        assert detail["precision"] == pytest.approx(expected_precision, abs=0.001)
        assert detail["recall"] == pytest.approx(expected_recall, abs=0.001)


# ---------------------------------------------------------------------------
# 4. Contract Completeness (hybrid)
# ---------------------------------------------------------------------------

class TestContractCompleteness:
    def test_sections_found_raises_score(self):
        raw = (
            "## naming_conventions\nUse PascalCase for all exports.\n"
            "## postconditions\n### howler-auth\nprecondition: user exists\n"
            "postcondition: session created\n"
        )
        result = _make_result(raw_output=raw)
        scenario = _make_scenario(
            expected_contract_sections=[
                {"section": "naming_conventions", "must_include": ["PascalCase"]},
                {"section": "postconditions", "must_include": ["session created"]},
            ],
            expected_file_ownership=[
                {"file": "src/auth.ts", "howler": "howler-auth", "action": "CREATES"},
            ],
        )
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_contract_completeness")
        assert item["score"] > 0.0
        assert item["needs_human_review"] is not False

    def test_empty_output_scores_low(self):
        result = _make_result(raw_output="")
        scenario = _make_scenario(
            expected_contract_sections=[
                {"section": "shared_types", "must_include": ["UserSession"]},
                {"section": "postconditions", "must_include": ["exports createSession"]},
            ],
        )
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_contract_completeness")
        assert item["score"] < 0.5


# ---------------------------------------------------------------------------
# 5. Contract Precision (human-only)
# ---------------------------------------------------------------------------

class TestContractPrecision:
    def test_returns_pending_human_review(self):
        result = _make_result(raw_output="exports validateRequest(): ApiResponse\npostcondition: exports UserSession")
        scenario = _make_scenario()
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_contract_precision")
        assert item["score"] is None
        assert item["detail"]["status"] == "pending_human_review"
        assert isinstance(item["needs_human_review"], dict)
        assert item["needs_human_review"]["type"] == "human_only"

    def test_excerpt_contains_postcondition_lines(self):
        raw = (
            "postcondition: exports createSession(userId: string): UserSession\n"
            "postcondition: the module should handle errors gracefully\n"
        )
        result = _make_result(raw_output=raw)
        scenario = _make_scenario()
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_contract_precision")
        excerpt = item["needs_human_review"]["excerpt"]
        assert len(excerpt["postcondition_lines"]) > 0
        assert "TESTABLE" in excerpt["classification_options"]


# ---------------------------------------------------------------------------
# 6. Decomposition Soundness (hybrid)
# ---------------------------------------------------------------------------

class TestDecompositionSoundness:
    def test_no_serial_tasks_scores_1(self):
        result = _make_result()
        scenario = _make_scenario(serial_tasks_expected=[])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_decomposition_soundness")
        assert item["score"] == 1.0
        assert item["needs_human_review"] is not False

    def test_serial_task_labeled_correctly(self):
        raw = "howler-auth-types: serial_risk: yes\nAll other howlers depend on types."
        result = _make_result(raw_output=raw)
        scenario = _make_scenario(serial_tasks_expected=["howler-auth-types"])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_decomposition_soundness")
        # serial recall should be > 0 since label present
        assert item["score"] > 0.0

    def test_serial_task_not_labeled(self):
        raw = "All howlers run in parallel."
        result = _make_result(raw_output=raw)
        scenario = _make_scenario(serial_tasks_expected=["howler-auth-types"])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_decomposition_soundness")
        assert item["score"] == 0.0


# ---------------------------------------------------------------------------
# 7. Politico Integration (hybrid)
# ---------------------------------------------------------------------------

class TestPoliticoIntegration:
    def test_no_politico_no_issues_scores_high(self):
        """No injected issues → catch_rate=1.0; Politico absent → presence=0.
        Score = 0.3 * 0 + 0.7 * 1.0 = 0.7"""
        result = _make_result(raw_output="Great manifest, no issues.")
        scenario = _make_scenario(politico_injection=[])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_politico_integration")
        assert item["score"] == pytest.approx(0.7, abs=0.01)

    def test_politico_step_present_no_issues_scores_high(self):
        raw = "Phase 1.5 — The Passage: Politico adversarial review completed. No issues found."
        result = _make_result(raw_output=raw)
        scenario = _make_scenario(politico_injection=[])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_politico_integration")
        assert item["score"] == pytest.approx(1.0, abs=0.01)

    def test_politico_absent_issue_injected_scores_low(self):
        raw = "Here is the manifest."
        result = _make_result(raw_output=raw)
        scenario = _make_scenario(politico_injection=[
            {"issue_id": "gap-001", "description": "file ownership gap on barrel file", "severity": "high"},
        ])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_politico_integration")
        # presence=0, catch_rate=0 → score=0
        assert item["score"] == pytest.approx(0.0, abs=0.05)

    def test_politico_present_catches_issue(self):
        raw = (
            "Phase 1.5 adversarial review by Politico: "
            "Found file ownership gap on barrel file — two Howlers both list index.ts."
        )
        result = _make_result(raw_output=raw)
        scenario = _make_scenario(politico_injection=[
            {"issue_id": "gap-001", "description": "file ownership gap on barrel file", "severity": "high"},
        ])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        item = next(i for i in out["items"] if i["id"] == "muster_politico_integration")
        assert item["score"] > 0.5


# ---------------------------------------------------------------------------
# Overall score_muster integration
# ---------------------------------------------------------------------------

class TestScoreMusterIntegration:
    def test_returns_required_keys(self):
        result = _make_result()
        scenario = _make_scenario()
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        assert "scenario_id" in out
        assert "model" in out
        assert "phase" in out
        assert out["phase"] == "muster"
        assert "items" in out
        assert "phase_score" in out
        assert "needs_human_review" in out

    def test_phase_score_is_float_when_partial_items_scored(self):
        """Phase score is computed from items with non-None scores."""
        result = _make_result(file_ownership=[
            {"file": "pages/about.tsx", "howler": "h1", "action": "CREATES"},
        ])
        scenario = _make_scenario(expected_file_ownership=[
            {"file": "pages/about.tsx", "howler": "h1", "action": "CREATES"},
        ])
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        # phase_score may be partial (human items = None), but should be a float
        if out["phase_score"] is not None:
            assert 0.0 <= out["phase_score"] <= 1.0

    def test_all_automated_scores_in_range(self):
        result = _make_result(
            raw_output="Politico phase 1.5 adversarial review. serial_risk: yes for howler-auth-types.",
            file_ownership=[{"file": "src/types/auth.ts", "howler": "howler-auth-types", "action": "CREATES"}],
            dag_edges=[{"from": "howler-jwt", "to": "howler-auth-types"}],
        )
        scenario = _make_scenario(
            expected_file_ownership=[{"file": "src/types/auth.ts", "howler": "howler-auth-types", "action": "CREATES"}],
            expected_dag_edges=[{"from": "howler-jwt", "to": "howler-auth-types"}],
        )
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        for item in out["items"]:
            if item["score"] is not None:
                assert 0.0 <= item["score"] <= 1.0, f"Score out of range for {item['id']}: {item['score']}"

    def test_cost_and_latency_propagated(self):
        result = _make_result(cost_usd=2.5, latency_ms=12345)
        scenario = _make_scenario()
        out = score_muster(result, scenario, MUSTER_RUBRIC)
        assert out["cost_usd"] == 2.5
        assert out["latency_ms"] == 12345
