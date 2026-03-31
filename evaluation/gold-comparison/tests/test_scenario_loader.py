"""Tests for harness/scenario_loader.py."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from harness.scenario_loader import (
    load_all_scenarios,
    load_scenario,
    validate_scenario,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_MUSTER_SCENARIO = {
    "scenario_id": "muster-01",
    "gold_phase": "muster",
    "difficulty": "medium",
    "description": "Basic 3-howler decomposition",
    "task_description": "Build a user auth system",
    "plan_excerpt": "## Auth\n- JWT middleware\n- User model",
    "codebase_context": [
        {"path": "src/types/user.ts", "content": "export interface User { id: string; }"}
    ],
    "num_howlers": 3,
    "expected_file_ownership": [
        {"file": "src/auth/middleware.ts", "howler": "howler-auth", "action": "CREATES"}
    ],
    "known_conflicts": [],
    "expected_dag_edges": [],
    "expected_contract_sections": [],
}

VALID_PAX_SCENARIO = {
    "scenario_id": "pax-01",
    "gold_phase": "pax",
    "difficulty": "medium",
    "description": "Detect a postcondition violation",
    "contract_md": "## Postconditions\nhowler-auth exports authMiddleware",
    "debrief_set": [
        {
            "howler": "howler-auth",
            "status": "complete",
            "confidence": "high",
            "hook_md": "Status: complete",
            "debrief": "Created authMiddleware",
            "files_created": [],
        }
    ],
    "injected_deviations": [
        {
            "howler": "howler-api",
            "deviation_type": "postcondition_violation",
            "description": "Wrong function name",
            "severity": "blocker",
        }
    ],
    "correct_howlers": ["howler-auth"],
}

VALID_FORGE_SCENARIO = {
    "scenario_id": "forge-01",
    "gold_phase": "forge",
    "difficulty": "easy",
    "description": "Classify a transient failure",
    "hook_md_excerpt": "Status: failed\nError: network timeout",
    "error_context": "Timeout after 30s",
    "failure_history": [],
    "correct_classification": "transient",
    "correct_recovery_action": "resume",
    "circuit_breaker_applies": False,
    "rationale": "Simple network timeout",
}


# ---------------------------------------------------------------------------
# validate_scenario tests
# ---------------------------------------------------------------------------


def test_validate_scenario_valid_muster():
    errors = validate_scenario(VALID_MUSTER_SCENARIO)
    assert errors == []


def test_validate_scenario_valid_pax():
    errors = validate_scenario(VALID_PAX_SCENARIO)
    assert errors == []


def test_validate_scenario_valid_forge():
    errors = validate_scenario(VALID_FORGE_SCENARIO)
    assert errors == []


def test_validate_scenario_missing_scenario_id():
    s = dict(VALID_MUSTER_SCENARIO)
    del s["scenario_id"]
    errors = validate_scenario(s)
    assert any("scenario_id" in e for e in errors)


def test_validate_scenario_missing_gold_phase():
    s = dict(VALID_MUSTER_SCENARIO)
    del s["gold_phase"]
    errors = validate_scenario(s)
    assert any("gold_phase" in e for e in errors)


def test_validate_scenario_missing_difficulty():
    s = dict(VALID_MUSTER_SCENARIO)
    del s["difficulty"]
    errors = validate_scenario(s)
    assert any("difficulty" in e for e in errors)


def test_validate_scenario_invalid_phase():
    s = dict(VALID_MUSTER_SCENARIO)
    s["gold_phase"] = "invalid_phase"
    errors = validate_scenario(s)
    assert any("gold_phase" in e for e in errors)


def test_validate_scenario_invalid_difficulty():
    s = dict(VALID_MUSTER_SCENARIO)
    s["difficulty"] = "super-hard"
    errors = validate_scenario(s)
    assert any("difficulty" in e for e in errors)


def test_validate_scenario_missing_muster_field():
    s = dict(VALID_MUSTER_SCENARIO)
    del s["task_description"]
    errors = validate_scenario(s)
    assert any("task_description" in e for e in errors)


def test_validate_scenario_missing_pax_field():
    s = dict(VALID_PAX_SCENARIO)
    del s["contract_md"]
    errors = validate_scenario(s)
    assert any("contract_md" in e for e in errors)


def test_validate_scenario_missing_forge_field():
    s = dict(VALID_FORGE_SCENARIO)
    del s["correct_classification"]
    errors = validate_scenario(s)
    assert any("correct_classification" in e for e in errors)


def test_validate_scenario_multiple_errors():
    # Minimal invalid scenario
    errors = validate_scenario({"difficulty": "easy"})
    # Should have errors for scenario_id, gold_phase, description at minimum
    assert len(errors) >= 3


# ---------------------------------------------------------------------------
# load_scenario tests
# ---------------------------------------------------------------------------


def test_load_scenario_valid(tmp_path):
    scenario_file = tmp_path / "muster-01.yaml"
    scenario_file.write_text(yaml.dump(VALID_MUSTER_SCENARIO), encoding="utf-8")
    loaded = load_scenario(str(scenario_file))
    assert loaded["scenario_id"] == "muster-01"
    assert loaded["gold_phase"] == "muster"


def test_load_scenario_not_found():
    with pytest.raises(FileNotFoundError):
        load_scenario("/nonexistent/path/scenario.yaml")


def test_load_scenario_invalid_yaml(tmp_path):
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text(": invalid: yaml: [", encoding="utf-8")
    with pytest.raises(Exception):  # yaml.YAMLError or ValueError
        load_scenario(str(bad_file))


def test_load_scenario_validation_failure(tmp_path):
    bad_scenario = {"scenario_id": "muster-01"}  # Missing required fields
    scenario_file = tmp_path / "bad-scenario.yaml"
    scenario_file.write_text(yaml.dump(bad_scenario), encoding="utf-8")
    with pytest.raises(ValueError, match="validation failed"):
        load_scenario(str(scenario_file))


def test_load_scenario_non_mapping_yaml(tmp_path):
    list_file = tmp_path / "list.yaml"
    list_file.write_text("- item1\n- item2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="YAML mapping"):
        load_scenario(str(list_file))


# ---------------------------------------------------------------------------
# load_all_scenarios tests
# ---------------------------------------------------------------------------


def test_load_all_scenarios_empty_dir(tmp_path):
    result = load_all_scenarios(str(tmp_path))
    assert result == []


def test_load_all_scenarios_nonexistent_dir():
    result = load_all_scenarios("/nonexistent/scenarios/dir")
    assert result == []


def test_load_all_scenarios_mixed_phases(tmp_path):
    # Create scenario files in subdirectories
    muster_dir = tmp_path / "muster"
    pax_dir = tmp_path / "pax"
    muster_dir.mkdir()
    pax_dir.mkdir()

    (muster_dir / "scenario-01.yaml").write_text(
        yaml.dump(VALID_MUSTER_SCENARIO), encoding="utf-8"
    )
    (pax_dir / "scenario-01.yaml").write_text(
        yaml.dump(VALID_PAX_SCENARIO), encoding="utf-8"
    )

    all_scenarios = load_all_scenarios(str(tmp_path))
    assert len(all_scenarios) == 2

    ids = {s["scenario_id"] for s in all_scenarios}
    assert "muster-01" in ids
    assert "pax-01" in ids


def test_load_all_scenarios_phase_filter(tmp_path):
    muster_dir = tmp_path / "muster"
    pax_dir = tmp_path / "pax"
    muster_dir.mkdir()
    pax_dir.mkdir()

    (muster_dir / "scenario-01.yaml").write_text(
        yaml.dump(VALID_MUSTER_SCENARIO), encoding="utf-8"
    )
    (pax_dir / "scenario-01.yaml").write_text(
        yaml.dump(VALID_PAX_SCENARIO), encoding="utf-8"
    )

    muster_only = load_all_scenarios(str(tmp_path), phase="muster")
    assert len(muster_only) == 1
    assert muster_only[0]["gold_phase"] == "muster"


def test_load_all_scenarios_skips_invalid(tmp_path):
    valid_file = tmp_path / "valid.yaml"
    invalid_file = tmp_path / "invalid.yaml"

    valid_file.write_text(yaml.dump(VALID_MUSTER_SCENARIO), encoding="utf-8")
    invalid_file.write_text(yaml.dump({"broken": "scenario"}), encoding="utf-8")

    result = load_all_scenarios(str(tmp_path))
    # Only the valid one should be returned
    assert len(result) == 1
    assert result[0]["scenario_id"] == "muster-01"


def test_load_all_scenarios_sorted_by_id(tmp_path):
    # Create multiple scenarios to verify sort order
    scenarios = [
        {**VALID_MUSTER_SCENARIO, "scenario_id": "muster-03"},
        {**VALID_MUSTER_SCENARIO, "scenario_id": "muster-01"},
        {**VALID_MUSTER_SCENARIO, "scenario_id": "muster-02"},
    ]
    for s in scenarios:
        fname = f"scenario-{s['scenario_id'].split('-')[1]}.yaml"
        (tmp_path / fname).write_text(yaml.dump(s), encoding="utf-8")

    result = load_all_scenarios(str(tmp_path))
    ids = [s["scenario_id"] for s in result]
    assert ids == sorted(ids)
