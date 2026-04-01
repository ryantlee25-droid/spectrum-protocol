#!/usr/bin/env python3
"""
Collect Howler output (git diffs) into SWE-bench's JSONL prediction format.

Walks a results directory where each subdirectory is named by instance_id
and contains a patch.diff file. Emits JSONL suitable for SWE-bench evaluation.

Usage:
    python3 -m tools.swe_bench.emit_predictions --results-dir ./results [--output predictions.jsonl] [--model-name spectrum-protocol-v4]
"""

import argparse
import json
import os
import sys
from pathlib import Path


def validate_patch(patch_content):
    """Validate that a patch looks like a valid unified diff.

    Returns:
        (is_valid, reason) tuple.
    """
    if not patch_content or not patch_content.strip():
        return False, "empty patch"

    stripped = patch_content.strip()

    if not stripped.startswith("diff --git"):
        # Also accept patches starting with --- (some git diff formats)
        if not stripped.startswith("---"):
            return False, f"does not start with 'diff --git' (starts with: {stripped[:40]!r})"

    return True, "ok"


def collect_predictions(results_dir, model_name):
    """Walk results directory and collect predictions.

    Expected structure:
        results_dir/
            instance_id_1/
                patch.diff
            instance_id_2/
                patch.diff
            ...

    Args:
        results_dir: Path to the results directory.
        model_name: Model name label for the predictions.

    Yields:
        (prediction_dict, status) tuples where status is "valid", "invalid", or "missing".
    """
    results_path = Path(results_dir)

    if not results_path.is_dir():
        print(f"ERROR: Results directory not found: {results_path}", file=sys.stderr)
        sys.exit(1)

    # Iterate over subdirectories sorted by name for deterministic output
    entries = sorted(
        entry for entry in results_path.iterdir()
        if entry.is_dir()
    )

    for task_dir in entries:
        instance_id = task_dir.name
        patch_file = task_dir / "patch.diff"

        if not patch_file.is_file():
            yield None, "missing", instance_id
            continue

        try:
            patch_content = patch_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(
                f"WARNING: Could not read {patch_file}: {exc}",
                file=sys.stderr,
            )
            yield None, "invalid", instance_id
            continue

        is_valid, reason = validate_patch(patch_content)

        prediction = {
            "instance_id": instance_id,
            "model_name_or_path": model_name,
            "model_patch": patch_content,
        }

        if is_valid:
            yield prediction, "valid", instance_id
        else:
            print(
                f"WARNING: Invalid patch for {instance_id}: {reason}",
                file=sys.stderr,
            )
            yield prediction, "invalid", instance_id


def main():
    parser = argparse.ArgumentParser(
        description="Collect Howler diffs into SWE-bench JSONL prediction format."
    )
    parser.add_argument(
        "--results-dir", "-r",
        required=True,
        help="Directory containing per-instance_id subdirectories with patch.diff files.",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path. Defaults to stdout.",
    )
    parser.add_argument(
        "--model-name", "-m",
        default="spectrum-protocol-v4",
        help="Model name label for predictions (default: spectrum-protocol-v4).",
    )

    args = parser.parse_args()

    # Determine output destination
    output_fh = sys.stdout
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_fh = open(output_path, "w", encoding="utf-8")

    total = 0
    valid = 0
    invalid = 0
    missing = 0

    try:
        for prediction, status, instance_id in collect_predictions(args.results_dir, args.model_name):
            total += 1

            if status == "missing":
                missing += 1
                print(
                    f"SKIP: {instance_id} — no patch.diff found",
                    file=sys.stderr,
                )
                continue

            if status == "invalid":
                invalid += 1
                # Still emit the prediction (harness will reject it, but it's traceable)
                output_fh.write(json.dumps(prediction, ensure_ascii=False) + "\n")
                continue

            # Valid
            valid += 1
            output_fh.write(json.dumps(prediction, ensure_ascii=False) + "\n")

    finally:
        if output_fh is not sys.stdout:
            output_fh.close()

    # Report to stderr
    print(f"\n--- Prediction Collection Report ---", file=sys.stderr)
    print(f"Total tasks found:    {total}", file=sys.stderr)
    print(f"Valid patches:        {valid}", file=sys.stderr)
    print(f"Invalid patches:      {invalid}", file=sys.stderr)
    print(f"Missing patch.diff:   {missing}", file=sys.stderr)

    if args.output:
        print(f"Output written to:    {args.output}", file=sys.stderr)
    else:
        print(f"Output written to:    stdout", file=sys.stderr)


if __name__ == "__main__":
    main()
