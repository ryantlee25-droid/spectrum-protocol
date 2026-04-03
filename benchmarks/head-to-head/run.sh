#!/usr/bin/env bash
set -euo pipefail

# Head-to-Head Benchmark Runner
#
# Drives both variants (raw Sonnet vs Spectrum) against a temp copy of the scaffold,
# then scores each result. Claude is NOT auto-invoked — prompts are printed for manual use.
#
# Usage:
#   ./run.sh --task <1-4> [--variant <a|b|both>] [--skip-prompt]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCAFFOLD_DIR="${SCRIPT_DIR}/scaffold"
EXPECTED_DIR="${SCRIPT_DIR}/expected"
RESULTS_DIR="${SCRIPT_DIR}/results"
TMP_DIR="${SCRIPT_DIR}/tmp"

# --- Defaults ---
TASK=""
VARIANT="both"
SKIP_PROMPT=false

# --- Parse args ---
while [[ $# -gt 0 ]]; do
  case $1 in
    --task)
      TASK="$2"
      shift 2
      ;;
    --variant)
      VARIANT="$2"
      shift 2
      ;;
    --skip-prompt)
      SKIP_PROMPT=true
      shift
      ;;
    --help|-h)
      echo "Usage: ./run.sh --task <1-4> [--variant <a|b|both>] [--skip-prompt]"
      echo ""
      echo "Options:"
      echo "  --task <1-4>       Task number to run (required)"
      echo "  --variant <a|b|both>  Which variant to run (default: both)"
      echo "                        a = raw Sonnet, b = Spectrum"
      echo "  --skip-prompt      Skip printing prompts (useful for scoring only)"
      echo ""
      echo "Workflow:"
      echo "  1. Run this script — it creates a tmp/ copy of the scaffold"
      echo "  2. The script prints the exact claude prompt to use"
      echo "  3. You run claude manually in the tmp/ directory"
      echo "  4. Press Enter when done — the script scores the result"
      echo "  5. Repeat for variant B if --variant both"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [[ -z "$TASK" ]]; then
  echo "Error: --task is required"
  echo "Usage: ./run.sh --task <1-4>"
  exit 1
fi

if [[ "$TASK" != "1" && "$TASK" != "2" && "$TASK" != "3" && "$TASK" != "4" ]]; then
  echo "Error: --task must be 1, 2, 3, or 4"
  exit 1
fi

# --- Task descriptions ---
declare -A TASK_NAMES
TASK_NAMES[1]="Rename User type to Account"
TASK_NAMES[2]="Add rate-limiting middleware"
TASK_NAMES[3]="Fix pagination off-by-one bug"
TASK_NAMES[4]="Create 3 independent utility modules"

TASK_FILE="${SCRIPT_DIR}/tasks/task${TASK}-*.md"
TASK_FILE_PATH=$(ls ${TASK_FILE} 2>/dev/null | head -1)

if [[ -z "$TASK_FILE_PATH" ]]; then
  echo "Error: Task definition file not found for task ${TASK}"
  exit 1
fi

# --- Variant A prompt (raw Sonnet) ---
VARIANT_A_PROMPT="Read the task file at ${TASK_FILE_PATH} and complete it. Work in the current directory. Do not use any multi-agent coordination — complete the task as a single agent. When done, verify: tsc --noEmit passes and jest passes."

# --- Variant B prompt (Spectrum) ---
VARIANT_B_PROMPT="Read the task file at ${TASK_FILE_PATH}. Use the Spectrum protocol to complete this task: decompose it, drop Howlers if applicable, run quality gates, and verify completion. Work in the current directory."

# --- Helper functions ---
create_tmp_copy() {
  local variant_label=$1
  local dest="${TMP_DIR}/variant-${variant_label}"

  echo "Creating fresh scaffold copy at ${dest}..."
  rm -rf "${dest}"
  mkdir -p "${dest}"
  # Copy scaffold (excluding node_modules)
  rsync -a --exclude='node_modules' --exclude='.git' "${SCAFFOLD_DIR}/" "${dest}/"

  # Install dependencies
  echo "Installing dependencies..."
  (cd "${dest}" && npm install --silent 2>/dev/null)

  echo "Scaffold ready at ${dest}"
  echo ""
}

score_variant() {
  local variant_label=$1
  local variant_name=$2
  local result_dir="${TMP_DIR}/variant-${variant_label}"

  echo ""
  echo "=== Scoring ${variant_name} ==="
  python3 "${SCRIPT_DIR}/score.py" \
    --task "${TASK}" \
    --result-dir "${result_dir}" \
    --expected-dir "${EXPECTED_DIR}" \
    --variant "${variant_name}" \
    --output json
}

save_results() {
  local timestamp
  timestamp=$(date +%Y%m%d-%H%M%S)
  local result_file="${RESULTS_DIR}/run-${timestamp}.md"

  mkdir -p "${RESULTS_DIR}"

  echo "# Head-to-Head Results: Task ${TASK} — ${TASK_NAMES[$TASK]}" > "${result_file}"
  echo "" >> "${result_file}"
  echo "**Run:** ${timestamp}" >> "${result_file}"
  echo "" >> "${result_file}"

  # Score both variants in markdown
  if [[ "$VARIANT" == "both" || "$VARIANT" == "a" ]]; then
    echo "" >> "${result_file}"
    python3 "${SCRIPT_DIR}/score.py" \
      --task "${TASK}" \
      --result-dir "${TMP_DIR}/variant-a" \
      --expected-dir "${EXPECTED_DIR}" \
      --variant "raw-sonnet" \
      --output markdown >> "${result_file}" 2>/dev/null || true
  fi

  if [[ "$VARIANT" == "both" || "$VARIANT" == "b" ]]; then
    echo "" >> "${result_file}"
    python3 "${SCRIPT_DIR}/score.py" \
      --task "${TASK}" \
      --result-dir "${TMP_DIR}/variant-b" \
      --expected-dir "${EXPECTED_DIR}" \
      --variant "spectrum" \
      --output markdown >> "${result_file}" 2>/dev/null || true
  fi

  echo ""
  echo "Results saved to ${result_file}"
}

run_variant() {
  local variant_label=$1
  local variant_name=$2
  local prompt=$3

  create_tmp_copy "${variant_label}"

  if [[ "$SKIP_PROMPT" != true ]]; then
    echo "============================================================"
    echo "  VARIANT ${variant_label^^}: ${variant_name}"
    echo "  Task ${TASK}: ${TASK_NAMES[$TASK]}"
    echo "============================================================"
    echo ""
    echo "Run the following in a new terminal:"
    echo ""
    echo "  cd ${TMP_DIR}/variant-${variant_label}"
    echo "  claude \"${prompt}\""
    echo ""
    echo "Press Enter when the variant has completed..."
    read -r
  fi

  score_variant "${variant_label}" "${variant_name}"
}

# --- Main ---
echo ""
echo "Head-to-Head Benchmark — Task ${TASK}: ${TASK_NAMES[$TASK]}"
echo "================================================================"
echo ""

if [[ "$VARIANT" == "both" || "$VARIANT" == "a" ]]; then
  run_variant "a" "raw-sonnet" "${VARIANT_A_PROMPT}"
fi

if [[ "$VARIANT" == "both" || "$VARIANT" == "b" ]]; then
  run_variant "b" "spectrum" "${VARIANT_B_PROMPT}"
fi

save_results

# Cleanup
echo ""
echo "Cleaning up tmp/ copies..."
rm -rf "${TMP_DIR}"
echo "Done."
