"""Result store for the Gold evaluation harness.

Writes result JSON to: {output_dir}/raw/{run_id}/{scenario_id}/{model}.json

Result JSON schema (per CONTRACT.md):
{
  "scenario_id": "muster-01",
  "model": "opus",
  "phase": "muster",
  "raw_output": "...",
  "parsed": {
    # muster:  file_ownership, dag_edges, contract_sections
    # pax:     deviation_flags
    # forge:   classification, recovery_action, circuit_breaker_triggered
  },
  "parse_confidence": 0.95,
  "tokens_used": {"input": 42000, "output": 15000},
  "latency_ms": 23400,
  "cost_usd": 1.73,
  "model_id": "claude-opus-4-6",
  "timestamp": "2026-03-31T05:00:00Z"
}
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# Phase-specific keys to include in the 'parsed' object
PHASE_PARSED_KEYS: dict[str, list[str]] = {
    "muster": ["file_ownership", "dag_edges", "contract_sections"],
    "pax": ["deviation_flags"],
    "forge": ["classification", "recovery_action", "circuit_breaker_triggered"],
}


def build_result(
    *,
    scenario_id: str,
    model: str,
    phase: str,
    raw_output: str,
    parsed: dict,
    parse_confidence: float,
    tokens_used: dict,
    latency_ms: int,
    cost_usd: float,
    model_id: str,
    timestamp: Optional[str] = None,
) -> dict:
    """Construct a result dict conforming to the CONTRACT.md schema.

    Args:
        scenario_id: e.g. "muster-01"
        model: e.g. "opus" or "sonnet"
        phase: One of "muster", "pax", "forge"
        raw_output: Full raw text output from the model
        parsed: Full parsed dict from output_parser (may contain all keys)
        parse_confidence: Float 0.0-1.0 from the parser
        tokens_used: {"input": int, "output": int}
        latency_ms: Round-trip latency in milliseconds
        cost_usd: Computed cost in USD
        model_id: Full model ID string, e.g. "claude-opus-4-6"
        timestamp: ISO 8601 timestamp string; defaults to current UTC time

    Returns:
        Result dict conforming to the CONTRACT.md schema.
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build the parsed sub-object with only phase-relevant keys
    relevant_keys = PHASE_PARSED_KEYS.get(phase, [])
    filtered_parsed: dict[str, Any] = {}
    for key in relevant_keys:
        if key in parsed:
            filtered_parsed[key] = parsed[key]

    return {
        "scenario_id": scenario_id,
        "model": model,
        "phase": phase,
        "raw_output": raw_output,
        "parsed": filtered_parsed,
        "parse_confidence": parse_confidence,
        "tokens_used": tokens_used,
        "latency_ms": latency_ms,
        "cost_usd": cost_usd,
        "model_id": model_id,
        "timestamp": timestamp,
    }


def store_result(result: dict, output_dir: str, run_id: str) -> str:
    """Write a result dict to disk as JSON.

    File path: {output_dir}/raw/{run_id}/{scenario_id}/{model}.json

    ALWAYS calls os.makedirs(..., exist_ok=True) before writing.

    Args:
        result: Result dict conforming to CONTRACT.md schema.
        output_dir: Root output directory (e.g. "results").
        run_id: Unique run identifier (e.g. "run-20260331-001").

    Returns:
        Absolute path to the written file.

    Raises:
        KeyError: If result is missing required fields.
        OSError: If the file cannot be written.
    """
    scenario_id = result["scenario_id"]
    model = result["model"]

    output_path = Path(output_dir) / "raw" / run_id / scenario_id / f"{model}.json"

    # INVARIANT: always makedirs before write
    os.makedirs(output_path.parent, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return str(output_path.resolve())


def load_result(path: str) -> dict:
    """Load a previously stored result JSON file.

    Args:
        path: Path to the result JSON file.

    Returns:
        Parsed result dict.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
