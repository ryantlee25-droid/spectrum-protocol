"""Scenario loader for the Gold evaluation harness."""

import os
from pathlib import Path
from typing import Optional

import yaml

# Required fields for all scenario types
COMMON_REQUIRED_FIELDS = {"scenario_id", "gold_phase", "difficulty", "description"}

VALID_PHASES = {"muster", "pax", "forge"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}

# Phase-specific required fields
PHASE_REQUIRED_FIELDS: dict[str, set[str]] = {
    "muster": {
        "task_description",
        "plan_excerpt",
        "codebase_context",
        "num_howlers",
        "expected_file_ownership",
    },
    "pax": {
        "contract_md",
        "debrief_set",
        "injected_deviations",
        "correct_howlers",
    },
    "forge": {
        "hook_md_excerpt",
        "error_context",
        "failure_history",
        "correct_classification",
        "correct_recovery_action",
        "circuit_breaker_applies",
    },
}


def validate_scenario(scenario: dict) -> list[str]:
    """Validate a scenario dict and return a list of validation errors.

    Returns an empty list if the scenario is valid.
    """
    errors: list[str] = []

    # Check common required fields
    for field in COMMON_REQUIRED_FIELDS:
        if field not in scenario:
            errors.append(f"Missing required field: '{field}'")

    # Validate gold_phase value
    phase = scenario.get("gold_phase")
    if phase is not None and phase not in VALID_PHASES:
        errors.append(
            f"Invalid gold_phase '{phase}'. Must be one of: {sorted(VALID_PHASES)}"
        )

    # Validate difficulty value
    difficulty = scenario.get("difficulty")
    if difficulty is not None and difficulty not in VALID_DIFFICULTIES:
        errors.append(
            f"Invalid difficulty '{difficulty}'. Must be one of: {sorted(VALID_DIFFICULTIES)}"
        )

    # Phase-specific validation (only if phase is known)
    if phase in PHASE_REQUIRED_FIELDS:
        for field in PHASE_REQUIRED_FIELDS[phase]:
            if field not in scenario:
                errors.append(f"Missing required field for {phase} scenario: '{field}'")

    return errors


def load_scenario(path: str) -> dict:
    """Load and validate a single scenario YAML file.

    Args:
        path: Path to the scenario YAML file.

    Returns:
        Parsed scenario dict.

    Raises:
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: If the file is not valid YAML.
        ValueError: If the scenario fails validation.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Scenario file not found: {path}")

    with open(path_obj, "r", encoding="utf-8") as f:
        scenario = yaml.safe_load(f)

    if not isinstance(scenario, dict):
        raise ValueError(f"Scenario file must be a YAML mapping, got: {type(scenario)}")

    errors = validate_scenario(scenario)
    if errors:
        error_list = "\n  - ".join(errors)
        raise ValueError(
            f"Scenario validation failed for '{path}':\n  - {error_list}"
        )

    return scenario


def load_all_scenarios(
    scenarios_dir: str, phase: Optional[str] = None
) -> list[dict]:
    """Load all scenarios from a directory, optionally filtered by phase.

    Walks scenarios_dir recursively, loading any *.yaml file.
    Skips files that fail validation (logs a warning to stderr).

    Args:
        scenarios_dir: Root directory containing scenario YAML files.
        phase: If provided, only return scenarios with gold_phase == phase.

    Returns:
        List of valid scenario dicts, sorted by scenario_id.
    """
    import sys

    scenarios_path = Path(scenarios_dir)
    if not scenarios_path.exists():
        return []

    scenarios: list[dict] = []
    yaml_files = sorted(scenarios_path.rglob("*.yaml"))

    for yaml_file in yaml_files:
        try:
            scenario = load_scenario(str(yaml_file))
            if phase is None or scenario.get("gold_phase") == phase:
                scenarios.append(scenario)
        except (ValueError, yaml.YAMLError) as exc:
            print(
                f"WARNING: Skipping '{yaml_file}': {exc}",
                file=sys.stderr,
            )
        except FileNotFoundError:
            pass  # Race condition — file removed during walk

    # Sort by scenario_id for deterministic ordering
    scenarios.sort(key=lambda s: s.get("scenario_id", ""))
    return scenarios
