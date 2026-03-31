"""CLI entry point for the Gold evaluation harness.

Usage:
    python -m harness.run_evaluation --help
    python -m harness.run_evaluation --model sonnet --phase muster --dry-run
    python -m harness.run_evaluation --model both --phase all --output-dir results
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from harness.config import DEFAULT_OUTPUT_DIR, MODEL_IDS, COST_PER_TOKEN
from harness.output_parser import parse_forge_output, parse_muster_output, parse_pax_output
from harness.prompt_builder import build_prompt
from harness.result_store import build_result, store_result
from harness.scenario_loader import load_all_scenarios, load_scenario


PARSERS = {
    "muster": parse_muster_output,
    "pax": parse_pax_output,
    "forge": parse_forge_output,
}

SCENARIOS_DIR = "scenarios"


def _make_run_id() -> str:
    """Generate a unique run ID based on current UTC time."""
    now = datetime.now(timezone.utc)
    return now.strftime("run-%Y%m%d-%H%M%S")


def _compute_cost(model_id: str, tokens_used: dict) -> float:
    """Compute cost in USD from token counts."""
    rates = COST_PER_TOKEN.get(model_id, {})
    input_cost = tokens_used.get("input", 0) * rates.get("input", 0.0)
    output_cost = tokens_used.get("output", 0) * rates.get("output", 0.0)
    return round(input_cost + output_cost, 6)


def _call_api(prompt: str, model_id: str, timeout_ms: int) -> dict:
    """Call the Anthropic API and return response dict.

    Returns:
        {
            "raw_output": str,
            "tokens_used": {"input": int, "output": int},
            "latency_ms": int,
        }
    """
    import anthropic

    client = anthropic.Anthropic()

    start_time = time.time()
    message = client.messages.create(
        model=model_id,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
        timeout=timeout_ms / 1000.0,
    )
    latency_ms = int((time.time() - start_time) * 1000)

    raw_output = "".join(
        block.text for block in message.content if hasattr(block, "text")
    )

    tokens_used = {
        "input": message.usage.input_tokens,
        "output": message.usage.output_tokens,
    }

    return {
        "raw_output": raw_output,
        "tokens_used": tokens_used,
        "latency_ms": latency_ms,
    }


def _run_scenario(
    scenario: dict,
    model_key: str,
    dry_run: bool,
    show_prompt: bool,
    output_dir: str,
    run_id: str,
) -> Optional[dict]:
    """Run a single scenario against a single model.

    Returns the result dict, or None on dry-run.
    """
    scenario_id = scenario["scenario_id"]
    phase = scenario["gold_phase"]
    model_id = MODEL_IDS[model_key]

    prompt = build_prompt(scenario, phase)

    if show_prompt or dry_run:
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario_id}  |  MODEL: {model_key}  |  PHASE: {phase}")
        print(f"{'='*60}")
        print("PROMPT:")
        print(prompt)
        print(f"{'='*60}\n")

    if dry_run:
        return None

    print(
        f"Running {scenario_id} against {model_key} ({model_id})...",
        end=" ",
        flush=True,
    )

    api_response = _call_api(prompt, model_id, timeout_ms=120000)

    raw_output = api_response["raw_output"]
    tokens_used = api_response["tokens_used"]
    latency_ms = api_response["latency_ms"]

    # Parse output — always store raw before parsing
    parser = PARSERS.get(phase, parse_muster_output)
    parsed_full = parser(raw_output)
    parse_confidence = parsed_full.pop("parse_confidence", 0.0)

    cost_usd = _compute_cost(model_id, tokens_used)

    result = build_result(
        scenario_id=scenario_id,
        model=model_key,
        phase=phase,
        raw_output=raw_output,
        parsed=parsed_full,
        parse_confidence=parse_confidence,
        tokens_used=tokens_used,
        latency_ms=latency_ms,
        cost_usd=cost_usd,
        model_id=model_id,
    )

    path = store_result(result, output_dir, run_id)
    print(f"done  (latency: {latency_ms}ms, confidence: {parse_confidence:.2f})")
    print(f"  -> {path}")

    return result


def _resolve_scenarios(
    scenarios_dir: str, phase_filter: Optional[str], scenario_filter: str
) -> list[dict]:
    """Resolve the list of scenarios to run."""
    if scenario_filter == "all":
        phase_arg = None if phase_filter == "all" else phase_filter
        return load_all_scenarios(scenarios_dir, phase=phase_arg)
    else:
        # Single scenario by ID — search recursively
        scenarios_path = Path(scenarios_dir)
        for yaml_file in sorted(scenarios_path.rglob("*.yaml")):
            try:
                s = load_scenario(str(yaml_file))
                if s.get("scenario_id") == scenario_filter:
                    return [s]
            except (ValueError, Exception):
                pass
        print(
            f"ERROR: Scenario '{scenario_filter}' not found in '{scenarios_dir}'",
            file=sys.stderr,
        )
        sys.exit(1)


def main(argv: Optional[list[str]] = None) -> int:
    """Main CLI entry point.

    Returns exit code (0 = success, 1 = error).
    """
    parser = argparse.ArgumentParser(
        prog="python -m harness.run_evaluation",
        description=(
            "Gold evaluation harness — compare Opus vs Sonnet as Gold orchestrator "
            "in the Spectrum parallel execution protocol."
        ),
    )

    parser.add_argument(
        "--model",
        choices=["opus", "sonnet", "both"],
        required=True,
        help="Which model(s) to evaluate",
    )
    parser.add_argument(
        "--phase",
        choices=["muster", "pax", "forge", "all"],
        default="all",
        help="Which Gold phase to evaluate (default: all)",
    )
    parser.add_argument(
        "--scenario",
        default="all",
        help="Scenario ID to run, or 'all' (default: all)",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        dest="output_dir",
        help=f"Output directory for results (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print constructed prompt(s) without calling the API",
    )
    parser.add_argument(
        "--show-prompt",
        action="store_true",
        default=False,
        dest="show_prompt",
        help="Display the constructed prompt before running (also shown in --dry-run)",
    )
    parser.add_argument(
        "--scenarios-dir",
        default=SCENARIOS_DIR,
        dest="scenarios_dir",
        help=f"Directory containing scenario YAML files (default: {SCENARIOS_DIR})",
    )

    args = parser.parse_args(argv)

    # Resolve model list
    if args.model == "both":
        model_keys = ["opus", "sonnet"]
    else:
        model_keys = [args.model]

    # Resolve phase filter
    phase_filter = None if args.phase == "all" else args.phase

    # Load scenarios
    scenarios = _resolve_scenarios(
        args.scenarios_dir, phase_filter, args.scenario
    )

    if not scenarios:
        if args.dry_run:
            print("No scenarios found. In dry-run mode, this is OK.")
            return 0
        print(
            f"ERROR: No scenarios found in '{args.scenarios_dir}'"
            + (f" for phase '{phase_filter}'" if phase_filter else ""),
            file=sys.stderr,
        )
        return 1

    if args.dry_run:
        print(f"DRY RUN — {len(scenarios)} scenario(s), model(s): {', '.join(model_keys)}")
        print("(No API calls will be made)\n")
        for scenario in scenarios:
            for model_key in model_keys:
                _run_scenario(
                    scenario=scenario,
                    model_key=model_key,
                    dry_run=True,
                    show_prompt=True,
                    output_dir=args.output_dir,
                    run_id="dry-run",
                )
        return 0

    run_id = _make_run_id()
    print(f"Run ID: {run_id}")
    print(f"Scenarios: {len(scenarios)}, Models: {', '.join(model_keys)}")
    print(f"Output directory: {args.output_dir}\n")

    results: list[dict] = []
    errors: list[str] = []

    for scenario in scenarios:
        for model_key in model_keys:
            try:
                result = _run_scenario(
                    scenario=scenario,
                    model_key=model_key,
                    dry_run=False,
                    show_prompt=args.show_prompt,
                    output_dir=args.output_dir,
                    run_id=run_id,
                )
                if result is not None:
                    results.append(result)
            except Exception as exc:
                scenario_id = scenario.get("scenario_id", "unknown")
                msg = f"FAILED: {scenario_id}/{model_key}: {exc}"
                print(msg, file=sys.stderr)
                errors.append(msg)

    print(f"\nCompleted: {len(results)} results, {len(errors)} errors")
    if errors:
        for err in errors:
            print(f"  ERROR: {err}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
