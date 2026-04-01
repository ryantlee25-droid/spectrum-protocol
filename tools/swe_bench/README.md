# SWE-bench Adapter Scripts

Bridges Spectrum's pipeline to the SWE-bench evaluation harness.
Stdlib only (json, os, pathlib, argparse, re) -- no external dependencies.

## Load Tasks

Parse SWE-bench JSONL and produce enriched task records with prompts and contracts:

```bash
# Load all tasks, auto-detect variant per task complexity
python3 -m tools.swe_bench.load_tasks --input swe_bench_pro.jsonl > tasks.jsonl

# Load first 50 tasks, force Variant B (Lite Spectrum)
python3 -m tools.swe_bench.load_tasks --input swe_bench_pro.jsonl --limit 50 --variant B > tasks.jsonl

# Filter to Django tasks only
python3 -m tools.swe_bench.load_tasks --input swe_bench_pro.jsonl --filter 'django__django' > django_tasks.jsonl
```

Each output line is a JSON object containing:
- `instance_id`, `repo`, `base_commit`, `problem_statement`
- `fail_to_pass`, `pass_to_pass` (parsed lists)
- `variant` (A, B, or C -- auto-detected or forced)
- `gold_prompt` (formatted prompt for Gold/Howler)
- `mini_contract` (mini-CONTRACT.md for Variant A, task brief for Variant B, empty for C)

### Variant Auto-Detection

Routes to Variant A (Full Spectrum) when any of:
- Failing tests span 3+ test files
- Problem statement mentions 3+ source file paths
- Problem statement exceeds ~500 tokens (2000 chars)

Otherwise routes to Variant B (Lite Spectrum). Variant C is control-only (use `--variant C`).

## Collect Predictions

After running Spectrum on each task, collect the git diffs into SWE-bench prediction format:

```bash
# Expects: results/{instance_id}/patch.diff for each task
python3 -m tools.swe_bench.emit_predictions --results-dir ./results --output predictions.jsonl

# Custom model name
python3 -m tools.swe_bench.emit_predictions --results-dir ./results --model-name spectrum-variant-b --output predictions.jsonl

# Output to stdout
python3 -m tools.swe_bench.emit_predictions --results-dir ./results
```

Reports to stderr: total tasks, valid patches, invalid patches, missing patches.

## Evaluate with SWE-bench

```bash
# SWE-bench Verified (local Docker)
python -m swebench.harness.run_evaluation \
  --dataset_name princeton-nlp/SWE-bench \
  --predictions_path predictions.jsonl \
  --max_workers 12

# SWE-bench Pro (requires Modal)
python swe_bench_pro_eval.py \
  --raw_sample_path=swe_bench_pro_full.csv \
  --patch_path=predictions.json \
  --output_dir=./eval_output \
  --num_workers=100

# Official leaderboard submission
sb submit --predictions predictions.jsonl
```

## Results Directory Structure

```
results/
  django__django-11099/
    patch.diff          # git diff output from Howler
  sympy__sympy-20590/
    patch.diff
  ...
```
