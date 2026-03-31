from __future__ import annotations
"""
score_results.py — CLI entry point for the scoring engine.

Usage:
    python -m scoring.score_results \
        --results-dir results/raw/<run-id>/ \
        --rubrics-dir rubrics/ \
        --scenarios-dir scenarios/ \
        --output results/scored/<run-id>/scores.json
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml

from scoring.muster_scorer import score_muster
from scoring.pax_scorer import score_pax
from scoring.forge_scorer import score_forge
from scoring.composite_scorer import compute_composite


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_results(results_dir: Path) -> list[dict]:
    """Load all JSON result files from a directory."""
    results = []
    for p in sorted(results_dir.glob("*.json")):
        try:
            results.append(_load_json(p))
        except Exception as exc:
            print(f"Warning: could not load result {p}: {exc}", file=sys.stderr)
    return results


def _load_rubrics(rubrics_dir: Path) -> dict[str, dict]:
    """Load all rubric YAML files, keyed by phase name."""
    rubrics: dict[str, dict] = {}
    for phase in ["muster", "pax", "forge"]:
        rubric_path = rubrics_dir / f"{phase}-rubric.yaml"
        if rubric_path.exists():
            rubrics[phase] = _load_yaml(rubric_path)
        else:
            print(f"Warning: rubric not found at {rubric_path}", file=sys.stderr)
    guide_path = rubrics_dir / "scoring-guide.yaml"
    rubrics["scoring_guide"] = _load_yaml(guide_path) if guide_path.exists() else {}
    return rubrics


def _load_scenario(scenarios_dir: Path, scenario_id: str, phase: str) -> dict | None:
    """Find and load a scenario YAML by scenario_id and phase."""
    phase_dir = scenarios_dir / phase
    if not phase_dir.exists():
        return None
    for p in phase_dir.glob("*.yaml"):
        try:
            data = _load_yaml(p)
            if data.get("scenario_id") == scenario_id:
                return data
        except Exception:
            continue
    return None


# ---------------------------------------------------------------------------
# Core scoring pass
# ---------------------------------------------------------------------------

def _score_one(result: dict, scenario: dict, rubrics: dict[str, dict]) -> dict | None:
    phase = result.get("phase") or scenario.get("gold_phase", "")
    rubric = rubrics.get(phase)
    if rubric is None:
        print(
            f"Warning: no rubric for phase '{phase}' "
            f"(scenario {result.get('scenario_id')})",
            file=sys.stderr,
        )
        return None

    if phase == "muster":
        return score_muster(result, scenario, rubric)
    elif phase == "pax":
        return score_pax(result, scenario, rubric)
    elif phase == "forge":
        return score_forge(result, scenario, rubric)
    else:
        print(f"Warning: unknown phase '{phase}'", file=sys.stderr)
        return None


def _group_by_model_phase(
    scored: list[dict],
) -> dict[str, dict[str, list[dict]]]:
    """Group scored results as {model: {phase: [scored_dicts]}}."""
    grouped: dict[str, dict[str, list[dict]]] = {}
    for s in scored:
        model = s.get("model", "unknown")
        phase = s.get("phase", "unknown")
        grouped.setdefault(model, {}).setdefault(phase, []).append(s)
    return grouped


# ---------------------------------------------------------------------------
# Output structure
# ---------------------------------------------------------------------------

def _build_output(
    all_scored: list[dict],
    rubrics: dict[str, dict],
) -> dict:
    grouped = _group_by_model_phase(all_scored)
    scoring_guide = rubrics.get("scoring_guide", {})
    models_output: dict[str, Any] = {}

    for model, phases in grouped.items():
        muster_list = phases.get("muster", [])
        pax_list = phases.get("pax", [])
        forge_list = phases.get("forge", [])

        composite = compute_composite(muster_list, pax_list, forge_list, scoring_guide)
        models_output[model] = {
            "scored_results": {
                "muster": muster_list,
                "pax": pax_list,
                "forge": forge_list,
            },
            "composite": composite,
        }

    return {
        "models": models_output,
        "scenario_count": len(all_scored),
        "rubric_versions": {
            phase: rubrics[phase].get("version") for phase in ["muster", "pax", "forge"]
            if phase in rubrics
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score Gold agent evaluation results against rubrics.",
    )
    parser.add_argument(
        "--results-dir",
        required=True,
        type=Path,
        help="Path to directory containing raw result JSON files.",
    )
    parser.add_argument(
        "--rubrics-dir",
        required=True,
        type=Path,
        help="Path to directory containing rubric YAML files.",
    )
    parser.add_argument(
        "--scenarios-dir",
        default=Path("scenarios"),
        type=Path,
        help="Path to directory containing scenario YAML files. (default: scenarios/)",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output path for scored JSON.",
    )

    args = parser.parse_args(argv)

    results_dir: Path = args.results_dir
    rubrics_dir: Path = args.rubrics_dir
    scenarios_dir: Path = args.scenarios_dir
    output_path: Path = args.output

    if not results_dir.exists():
        print(f"Error: --results-dir '{results_dir}' does not exist.", file=sys.stderr)
        return 1
    if not rubrics_dir.exists():
        print(f"Error: --rubrics-dir '{rubrics_dir}' does not exist.", file=sys.stderr)
        return 1

    print(f"Loading results from {results_dir} ...", flush=True)
    raw_results = _load_results(results_dir)
    print(f"  Loaded {len(raw_results)} result(s).")

    print(f"Loading rubrics from {rubrics_dir} ...", flush=True)
    rubrics = _load_rubrics(rubrics_dir)
    print(f"  Loaded rubrics for: {[k for k in rubrics if k != 'scoring_guide']}")

    print(f"Scoring results ...", flush=True)
    all_scored: list[dict] = []
    skipped = 0

    for result in raw_results:
        scenario_id = result.get("scenario_id")
        phase = result.get("phase") or ""

        scenario = _load_scenario(scenarios_dir, scenario_id, phase)
        if scenario is None:
            print(
                f"  Warning: scenario '{scenario_id}' (phase={phase}) not found in "
                f"{scenarios_dir}; skipping.",
                file=sys.stderr,
            )
            skipped += 1
            continue

        scored = _score_one(result, scenario, rubrics)
        if scored is not None:
            all_scored.append(scored)
        else:
            skipped += 1

    print(f"  Scored {len(all_scored)} result(s), skipped {skipped}.")

    output = _build_output(all_scored, rubrics)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2)
    print(f"Scores written to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
