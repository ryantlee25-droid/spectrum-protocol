# SWE-bench Infrastructure Analysis

**Author**: H2 — SWE-bench Infrastructure Analyst
**Spectrum**: swe-bench-prep-0401
**Date**: 2026-03-31

---

## 1. SWE-bench Pro Task Format (What the Agent Sees)

Each SWE-bench Pro task instance provides the following fields:

| Field | Description |
|---|---|
| `instance_id` | Unique identifier, format: `repo_owner__repo_name-issue_number` |
| `repo` | GitHub repository slug (e.g., `sympy/sympy`) |
| `base_commit` | The exact commit hash the agent must apply its patch on top of |
| `problem_statement` | The GitHub issue text (title + body) |
| `hints_text` | Optional — linked PR comments or hints (some tasks include; some don't) |
| `FAIL_TO_PASS` | JSON list of test names that must change from FAIL to PASS |
| `PASS_TO_PASS` | JSON list of test names that must remain PASS (regression guard) |
| `environment_setup_commit` | Commit hash for setting up the test environment |
| `dockerhub_tag` | Pre-built Docker image for this task's language/env configuration |

**What SWE-bench Pro adds over Verified**:
- Multi-file tasks: avg 4.1 files per solution, 107.4 lines per solution
- Multi-language: Python, Go, TypeScript, JavaScript
- 1,865 tasks across 41 actively maintained repositories
- Partitioned into: public set (11 repos, open access), held-out set (12 repos), commercial set (18 proprietary repos)
- Contamination resistance: GPL-style copyleft and private repositories make training data inclusion improbable

**What "resolved" means**: The harness applies the agent's patch to the repo at `base_commit`, builds the test environment, and runs the tests. A task is "resolved" if all `FAIL_TO_PASS` tests now pass AND all `PASS_TO_PASS` tests still pass (no regressions).

**Sources**: [SWE-bench Pro GitHub (scaleapi)](https://github.com/scaleapi/SWE-bench_Pro-os), [SWE-bench Pro Paper (arxiv 2509.16941)](https://arxiv.org/pdf/2509.16941), [SWE-bench Evaluation Guide](https://www.swebench.com/SWE-bench/guides/evaluation/)

---

## 2. Evaluation Harness API (How to Submit Output)

### 2a. Patch Submission Format

The harness accepts a **JSONL predictions file**. Each line is a JSON object:

```json
{
  "instance_id": "sympy__sympy-20590",
  "model_name_or_path": "spectrum-variant-a",
  "model_patch": "diff --git a/sympy/core/sympify.py b/sympy/core/sympify.py\n..."
}
```

- `instance_id`: must match the task's instance_id exactly
- `model_name_or_path`: a label for reporting; does not affect scoring
- `model_patch`: a **unified diff** (standard `git diff` output) applied cleanly to `base_commit`

The patch must apply cleanly with `git apply` to the repo at the task's `base_commit`. No other formats are accepted.

### 2b. Running Local Evaluation (SWE-bench Verified / standard)

```bash
python -m swebench.harness.run_evaluation \
  --dataset_name princeton-nlp/SWE-bench \
  --predictions_path <path_to_predictions.jsonl> \
  --max_workers 12 \
  --run_id my_evaluation_run
```

Key flags:
- `--max_workers`: set to approximately `min(0.75 * cpu_count, 24)` — exceeding this causes resource contention
- `--namespace ''`: required for ARM (Mac M1/M2) — causes images to build locally instead of pulling from DockerHub
- `--modal true`: offloads evaluation to Modal cloud (requires `pip install modal swebench[modal]` and `modal setup`)

### 2c. Running SWE-bench Pro Evaluation

SWE-bench Pro uses its own evaluation script (not the standard harness):

```bash
# Step 1: Gather patches from agent output files into a JSON
python helper_code/gather_patches.py \
  --directory <path_to_pred_files> \
  --prefix <model_name> \
  --output <output_file>.json

# Step 2: Run evaluation
python swe_bench_pro_eval.py \
  --raw_sample_path=swe_bench_pro_full.csv \
  --patch_path=<your_patches>.json \
  --output_dir=<output_directory> \
  --scripts_dir=run_scripts \
  --num_workers=100 \
  --dockerhub_username=jefzda
```

SWE-bench Pro **requires Modal** for scaled evaluation. The `--num_workers=100` assumes Modal cloud workers — local evaluation without Modal is supported via `--use_local_docker` flag (beta, not recommended for runs >20 tasks).

Pre-built Docker images are at `hub.docker.com/r/jefzda/sweap-images`. Each task's `dockerhub_tag` column identifies the exact image.

### 2d. Leaderboard Submission via `sb-cli`

For official leaderboard submission:

```bash
pip install sb-cli
sb login
sb submit --predictions <path_to_predictions.jsonl>
```

`sb-cli` submits to AWS-managed evaluation infrastructure. This is the path for publishing a verified leaderboard score. For internal/experimental runs, local Docker or Modal is used instead.

**Sources**: [SWE-bench Evaluation Guide](https://www.swebench.com/SWE-bench/guides/evaluation/), [SWE-bench GitHub](https://github.com/SWE-bench/SWE-bench), [SWE-bench Pro GitHub](https://github.com/scaleapi/SWE-bench_Pro-os), [sb-cli PyPI](https://pypi.org/project/swebench/)

---

## 3. Infrastructure Requirements Checklist

### 3a. Hardware Requirements

| Requirement | Minimum | Recommended | Notes |
|---|---|---|---|
| Architecture | x86_64 | x86_64 | ARM64/Mac M-series is "experimental" — hardcoded x86 binaries in some Dockerfiles |
| Storage | 120 GB free | 200 GB | Docker images alone are ~60 GB for full env coverage; Pro images add more |
| RAM | 16 GB | 32 GB | Each Docker container may use 2-4 GB; 8 parallel workers = 16-32 GB |
| CPU cores | 8 | 16+ | `max_workers` is capped at `0.75 * cpu_count`; more cores = faster parallel eval |
| Docker Desktop | 120 GB virtual disk | 200 GB | Must be manually allocated in Docker Desktop preferences |

**ARM/Mac note**: Evaluation on Mac M-series machines is possible but slow and error-prone. Images are built for Linux x86_64. The `--namespace ''` flag rebuilds locally, which takes hours for 60+ environment images. **Strongly recommended**: use a Linux x86_64 VM or cloud instance for evaluation runs.

### 3b. Software Requirements

```bash
# Python environment
python >= 3.10
pip install swebench          # Standard harness
pip install swebench[modal]   # For Modal cloud evaluation
pip install sb-cli            # For leaderboard submission

# SWE-bench Pro specific
pip install modal
modal setup                   # Authenticate with Modal

# Dataset access
pip install datasets          # Hugging Face datasets

# SWE-agent (for patch generation with SWE-bench Pro)
git clone --recurse-submodules https://github.com/scaleapi/SWE-bench_Pro-os
# SWE-agent is included as a git submodule
```

### 3c. Environment Variables / Credentials

```bash
# Anthropic API key (for Claude models)
export ANTHROPIC_API_KEY=<key>

# Modal credentials (stored in ~/.modal.toml after `modal setup`)
# Token ID + secret required for cloud evaluation

# Docker Hub (for SWE-bench Pro images)
# No auth needed for public jefzda/sweap-images pulls
```

### 3d. Docker Image Build Strategy

SWE-bench evaluates in three Docker layers:
1. **Base image**: common dependencies (pulled from DockerHub)
2. **Environment images**: ~60 images for different Python/Node/Go configurations
3. **Instance images**: per-task dependency snapshots

For Verified/Lite: images are pulled from DockerHub automatically (x86_64 hosts only).
For Pro: use `dockerhub_tag` field per task instance. Pre-built at `jefzda/sweap-images`.
For ARM: `--namespace ''` causes local builds — expect 2-4 hours to build all images.

---

## 4. How Competitors Interface with the Harness

### Augment Code

**Pipeline**: Context Engine semantic index → Claude Sonnet 3.7 agent → patch → harness

**Infrastructure**: Docker containers for agent runs (isolated per task), Kubernetes pods for scale (10 shards × 8 processes = 80 parallel workers). Their published 65.4% Verified score used:
- Claude Sonnet 3.7 as core driver
- OpenAI o1 as ensembler (majority vote across multiple candidate solutions)
- `--num-candidate-solutions` parameter to generate multiple patches per task
- `--shard-ct` / `--shard-id` for distributed execution across Kubernetes pods

**Open-source implementation**: [augmentcode/augment-swebench-agent](https://github.com/augmentcode/augment-swebench-agent) — full pipeline including Docker containers, ensembling, and evaluation. A full 500-task Verified run with 1 candidate per problem took "a couple hours" with 10 shards × 8 processes.

**Key technique**: Context Engine pre-indexes the codebase semantically before the agent writes code. This is the primary accuracy driver — not multi-agent coordination.

### Claude-flow (now Ruflo)

**Claims**: "85% on SWE-bench" across its coordination modes. **Credibility: low**. Claude Sonnet 4.6 alone scores 79.6% on Verified. A system built on top of Claude claiming 85% would require meaningful net-positive overhead — possible but requires scrutiny. No independently verified leaderboard entry found.

**Pipeline**: Multi-agent swarm orchestration via MCP protocol. Isolated Docker environments per agent run. Native Claude Code integration.

**Interface**: Standard JSONL prediction format via the `swebench` harness. The SWE-bench Quick Reference in their wiki covers installation and submission steps.

**Source**: [Claude-flow SWE-Bench Evaluation Wiki](https://github.com/ruvnet/claude-flow/wiki/SWE-Bench-Evaluation)

### Factory (Droids)

**Pipeline**: HyperCode representation (semantic code graph) → Code Droid (multi-model: Anthropic + OpenAI) → patch generation → harness. Four-phase internally: Spec → Test → Implement → Verify.

**Infrastructure**: Revoked internet access during evaluation (to prevent Droid from searching for solution hints). Built HyperCode graph per repo at the evaluation commit. Multiple trajectory generation + test-based selection.

**Published scores**: 31.67% SWE-bench Lite (300 tasks), 58.75% SWE-bench Verified (500 tasks). These are self-reported to the leaderboard — no independent verification noted.

**Key technique**: Spec-first approach (generate tests from spec before implementing) and multi-trajectory selection.

### AI21 Maestro (at scale)

AI21 ran 200,000+ evaluation instances when applying Maestro to SWE-bench Verified. Their infrastructure insights:
- Decoupled **Generation** (patch creation) from **Evaluation** (test execution) to enable granular resumability — losing a 2-hour trajectory at 99% is a massive waste
- Extended MCP protocol with dedicated client for isolated environments
- TractoAI (not Kubernetes) for fair resource distribution — Kubernetes allowed one massive eval job to starve others
- Supports up to 8,000 parallel runs; full 500-task Verified evaluation wall-clock ≈ 20 minutes at that scale

**Source**: [AI21: Lessons from 200,000 SWE-bench runs](https://www.ai21.com/blog/scaling-agentic-evaluation-swe-bench/)

### Nebius SWE-rebench

Runs each agent 5+ times per task (2,500+ solutions for 500-task Verified). Uses TractoAI for cluster management. Publishes cost-per-problem and tokens-per-problem columns on their leaderboard.

**Source**: [Nebius: Infrastructure behind SWE-rebench](https://nebius.com/blog/posts/infrastructure-behind-swe-rebench)

---

## 5. Spectrum Adapter Design

This section maps Spectrum's pipeline to SWE-bench's single-issue task format.

### 5a. Input Side: Issue → Gold's Input

A SWE-bench task instance is presented to Gold as:

```
## SWE-bench Task: <instance_id>

**Repository**: <repo> at commit <base_commit>
**Problem Statement**:
<problem_statement>

**Failing Tests** (must pass after fix):
<FAIL_TO_PASS>

**Regression Guard** (must still pass):
<PASS_TO_PASS>

**Docker environment**: <dockerhub_tag>
```

Gold's muster for a SWE-bench task is **significantly lighter than a full Spectrum run**:
- No MANIFEST.md (single Howler — no DAG needed)
- No ENTITIES.md, no ARCHITECTURE.md (ephemeral per-task context)
- No Politico (single Howler — no inter-Howler seam conflicts to review)
- No CHECKPOINT.json (single task, no resume needed)
- No convoy-contracts.d.ts (single-task run, not a project spectrum)

What Gold DOES produce:
- A **mini-CONTRACT.md** (see 5b below)
- A single **Howler drop prompt** with the task context

### 5b. Mini-CONTRACT.md for SWE-bench Tasks

Gold writes a compact contract scoped to the single issue:

```markdown
## Task: <instance_id>

### Affected Files (MODIFIES)
- <file_path_1> — <reason>
- <file_path_2> — <reason>

### Expected Behavior (from issue)
<2-4 sentences distilling the issue into expected post-fix behavior>

### Test Targets
FAIL_TO_PASS: <test list>
PASS_TO_PASS: <regression guard — do not break these>

### Codebase Context (I3)
<Key function signatures, patterns, and conventions observed in affected files>

### Test Impact Map (I2)
<Which test files cover the affected source files>

### Known Failure Patterns (I7)
<Relevant patterns from LESSONS.md for this task type>
```

Gold skips: file ownership matrix, DAG, Howler assignments, DbC per-Howler sections, integration points between Howlers. These sections exist for multi-Howler coordination — they're irrelevant for single-task runs.

**Risk**: Gold's mini-contract could introduce specification drift — if Gold misinterprets the issue, the Howler implements the wrong thing. This is the primary risk of Variant A over bare Sonnet. The White Pre-Check (I4) partially mitigates this by validating the contract against the actual codebase before the Howler starts.

### 5c. Howler Execution

The Howler receives:
- The mini-CONTRACT.md
- The full problem statement
- The repo context (either via Docker environment or by cloning at `base_commit`)

The Howler:
1. Reads the issue and mini-CONTRACT.md
2. Explores affected files (using codebase context from I3)
3. Implements the fix
4. Runs `FAIL_TO_PASS` tests to verify the fix
5. Runs `PASS_TO_PASS` tests to check for regressions
6. **Issue re-read (I1)**: Re-reads the problem statement and writes a 3-5 line assessment: "Does my implementation resolve the stated problem? What edge cases might I have missed?"
7. **Revision pass (I6)**: If re-read reveals gaps, fixes them
8. Generates a `git diff` against `base_commit`

### 5d. Output Side: Patch Submission

The Howler's `git diff` output is the patch. Spectrum wraps it into the JSONL format:

```python
# submission_adapter.py
import json

def emit_prediction(instance_id: str, patch: str, model_label: str) -> str:
    return json.dumps({
        "instance_id": instance_id,
        "model_name_or_path": model_label,
        "model_patch": patch
    })
```

This is appended to the predictions JSONL file. After all tasks are processed, the file is submitted to the harness.

### 5e. Quality Gates — What Applies

| Gate | Applies in SWE-bench context? | Notes |
|---|---|---|
| White (post-implementation review) | Yes — lightweight | Reviews the diff for logical correctness, not style. Skip contract compliance checks (no cross-Howler contracts). |
| Gray (test runner) | Yes — already embedded | The Howler runs FAIL_TO_PASS + PASS_TO_PASS during implementation. Gray's role is confirming the pass/fail status before patch submission. |
| /diff-review (security) | Optional | Security criticals on a SWE-bench patch would be unusual. Can skip for speed on initial runs. |
| Obsidian (spec compliance) | No | No persistent PLAN.md for a benchmark run. |
| Copper (PR/branch) | No | No PR opened — patch is submitted directly to harness. |
| Politico (adversarial plan review) | No | Single Howler; no inter-Howler seams to review. |

### 5f. Artifacts Skipped in SWE-bench Mode

The following Spectrum artifacts are produced in full spectrum runs but are unnecessary for single-task SWE-bench evaluation:

- MANIFEST.md, CHECKPOINT.json, ARCHITECTURE.md, ENTITIES.md, convoy-contracts.d.ts
- Politico review, Obsidian compliance check, Brown LESSONS.md draft
- Copper branch + PR creation

---

## 6. Step-by-Step Setup Guide

### Phase 0: Environment Preparation

```bash
# 1. Provision an x86_64 Linux machine (see hardware requirements above)
#    Recommended: AWS c5.4xlarge (16 vCPU, 32 GB RAM) or equivalent
#    Cost: ~$0.68/hr on AWS. For a 100-task run taking 4 hours: ~$2.72 compute.

# 2. Install Docker
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER

# 3. Configure Docker storage
# Edit /etc/docker/daemon.json:
# { "data-root": "/path/to/large/volume" }
# Ensure 200 GB available

# 4. Install Python dependencies
python3 -m venv swebench-env
source swebench-env/bin/activate
pip install swebench "swebench[modal]" sb-cli datasets

# 5. Clone SWE-bench Pro (for Pro evaluation)
git clone --recurse-submodules https://github.com/scaleapi/SWE-bench_Pro-os
cd SWE-bench_Pro-os
pip install -r requirements.txt

# 6. Configure Modal (for scaled Pro evaluation)
modal setup
# Follow prompts; credentials stored in ~/.modal.toml

# 7. Set API credentials
export ANTHROPIC_API_KEY=<your_key>
```

### Phase 1: Validate Setup

```bash
# Test local harness with a single task (SWE-bench Verified)
python -m swebench.harness.run_evaluation \
  --dataset_name SWE-bench/SWE-bench_Verified \
  --predictions_path /dev/null \
  --instance_ids "sympy__sympy-20590" \
  --max_workers 1 \
  --run_id validation_test

# For SWE-bench Pro: test with gold patches
python helper_code/gather_patches.py \
  --directory helper_code/gold_patches \
  --prefix gold \
  --output gold_test.json

python swe_bench_pro_eval.py \
  --raw_sample_path=swe_bench_pro_full.csv \
  --patch_path=gold_test.json \
  --output_dir=./test_output \
  --scripts_dir=run_scripts \
  --num_workers=4 \
  --dockerhub_username=jefzda
# Gold patches should score 100% — if not, Docker or Modal is misconfigured
```

### Phase 2: Spectrum Adapter

Build the adapter that connects SWE-bench task instances to Spectrum's pipeline:

```
spectrum-swebench-adapter/
  load_tasks.py          # Loads tasks from HuggingFace dataset
  format_gold_input.py   # Converts task fields to Gold's input format
  run_task.py            # Invokes Gold muster + Howler for one task
  emit_predictions.py    # Collects diffs and writes predictions JSONL
  run_evaluation.py      # Calls harness after all tasks complete
```

Each task is an independent Gold+Howler invocation. Parallelism at the task level (not within a task) is the main lever for wall-clock time.

### Phase 3: Subset Selection and Run

```bash
# Load SWE-bench Pro public set
python -c "
from datasets import load_dataset
ds = load_dataset('ScaleAI/SWE-bench_Pro', split='test')
print(f'Total tasks: {len(ds)}')
# Filter to public subset, then to subset strategy (see Section 7)
"

# Run Spectrum adapter on selected tasks
python run_evaluation.py \
  --tasks selected_tasks.jsonl \
  --variant A \       # or B or C
  --max_parallel 8 \
  --output predictions.jsonl

# Evaluate predictions
python swe_bench_pro_eval.py \
  --patch_path predictions.json \
  --num_workers 50 \
  ...
```

### Phase 4: Leaderboard Submission

```bash
sb login
sb submit --predictions predictions.jsonl
# Results published to official leaderboard after validation
```

---

## 7. Subset Selection Strategy

### Recommended: SWE-bench Pro Public Set, 50 Tasks

**Why SWE-bench Pro over Verified**:

SWE-bench Verified is contaminated. OpenAI stopped reporting Verified scores after finding training data contamination across all frontier models. The current Verified leaderboard (Claude Sonnet 4.6 at 79.6%) is inflated. SWE-bench Pro:
- Harder (top score ~46% vs. 81% on Verified)
- Multi-language (better tests Spectrum's multi-file coordination)
- Contamination-resistant (GPL + proprietary repos)
- Increasingly the standard OpenAI recommends

**Why 50 tasks to start**:
- 50+ tasks is the minimum for statistically meaningful SWE-bench results (standard practice across published evals)
- A 100-task run doubles cost with limited marginal statistical value for a first run
- 50 tasks allows a fast iteration cycle: run, identify failures, fix pipeline, re-run

**Task selection criteria for the 50-task subset**:

1. **Public set only**: Use SWE-bench Pro's public 11-repo subset (not the held-out or commercial sets). The public set is the only one accessible without Scale AI partnership.

2. **Multi-file tasks first**: Filter for tasks with solutions spanning 3+ files. This is where Spectrum's CONTRACT.md and quality gates provide the most value — single-file fixes are won or lost on model quality alone.

3. **Python tasks first**: Python has the most mature tooling in the harness and is Spectrum's most tested language. Avoid Go/TypeScript for the initial run (more Docker complexity, less harness maturity).

4. **Avoid known unstable tasks**: Some SWE-bench Pro instances have known issues (extended eval times, year-sensitive tests). Check the repo's issue tracker and filter out flagged instances.

5. **Representative mix**: Include bug fixes, feature requests, and optimizations — not just one category.

**Alternative: SWE-bench Lite (300 tasks)**

SWE-bench Lite is a 300-task curated subset of the original SWE-bench. It's well-established, many teams have scores on it, and it's cheaper to evaluate than Pro. However, it's Verified-level contamination risk. For Spectrum's purposes — demonstrating coordination protocol value on multi-file tasks — Pro is a better fit.

**Sources**: [SWE-bench Pro Leaderboard (Morph)](https://www.morphllm.com/swe-bench-pro), [OpenAI: Why we no longer evaluate SWE-bench Verified](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/), [Scale Labs Pro Leaderboard](https://labs.scale.com/leaderboard/swe_bench_pro_public)

---

## 8. Estimated Compute and API Costs

### Per-Task API Cost (Claude Sonnet 4.6: $3/$15 per M input/output tokens)

SWE-bench agents typically consume 1–3.5M tokens per task across all turns (based on SWE-rebench leaderboard data). Optimized runs with experience reuse drop to ~$0.77–0.98 per task. Unconstrained agents run $5–8 per task.

Spectrum adds Gold muster (mini-CONTRACT.md, ~5k input + 2k output tokens ≈ $0.05) and White/Gray gates (~10k tokens each ≈ $0.05 combined). The Howler session dominates.

| Pipeline Component | Input Tokens | Output Tokens | Cost (Sonnet) |
|---|---|---|---|
| Gold muster (mini-contract) | ~5,000 | ~2,000 | ~$0.05 |
| Howler implementation session | ~300,000 | ~30,000 | ~$1.35 |
| White post-review | ~40,000 | ~3,000 | ~$0.17 |
| Gray test confirmation | ~20,000 | ~2,000 | ~$0.09 |
| **Total per task (Variant A)** | ~365,000 | ~37,000 | **~$1.66** |

These are median estimates. Hard/complex Pro tasks (multi-file, deep dependency chains) could run 3-5x higher.

### Run-Level Cost Estimates

| Run Size | Variant A (full Spectrum) | Variant B (lite) | Variant C (bare Sonnet) |
|---|---|---|---|
| 50 tasks | ~$83 API + ~$1.40 compute | ~$70 | ~$60 |
| 100 tasks | ~$166 API + ~$2.72 compute | ~$140 | ~$120 |

**Compute**: An AWS c5.4xlarge at $0.68/hr running 8 parallel tasks. A 50-task run at median 20 min/task with 8 workers = ~2 hrs = ~$1.36 compute. A 100-task run ≈ ~$2.72.

**Modal**: Modal's serverless containers are priced by GPU/CPU time. For CPU-only evaluation (the harness, not the agent), Modal costs are approximately $0.10–0.30 per 100 tasks in evaluation overhead.

**Total estimated cost for a 50-task Variant A run: ~$85** (API + compute + Modal overhead).
**Total estimated cost for a 100-task Variant A run: ~$170**.

These figures assume no retries. A 20% retry rate (Orange invocations for failed tasks) adds ~$17–34.

**Sources**: [SWE-rebench leaderboard (tokens/cost columns)](https://swe-rebench.com/), [Claude Sonnet 4.6 pricing](https://www.nxcode.io/resources/news/claude-sonnet-4-6-complete-guide-benchmarks-pricing-2026), [Epoch AI: Run SWE-bench in one hour](https://epoch.ai/blog/swebench-docker)

---

## 9. Known Gotchas

### Gotcha 1: ARM/Mac M-series — Not Production Ready

The SWE-bench harness has hardcoded x86 binaries in some Dockerfiles. `USE_X86` defines 496 instance IDs requiring x86, but the variable is never referenced in evaluation logic (unmerged `force_x86` branch). The README calls ARM support "experimental."

**Mitigation**: Do not run evaluation on Mac M1/M2/M3. Use a Linux x86_64 VM or cloud instance. If local testing is needed, use `--namespace ''` flag and budget 2-4 hours for initial image builds.

**Source**: [SWE-bench Verified Is Broken (Grey Newell)](https://greynewell.com/blog/swe-bench-verified-broken-5-things-source-code/)

### Gotcha 2: Docker Evaluation Hangs

Docker evaluation can hang mid-run for some users, with image builds getting stuck on the last image even after hours. This appears to be resource exhaustion (disk or memory).

**Mitigation**: Ensure 200 GB+ free disk space before starting. Monitor with `docker stats`. If a build hangs >30 min, kill and rebuild with `--namespace ''`. For scale runs, prefer Modal over local Docker.

**Source**: [GitHub Issue #157: docker evaluation gets stuck](https://github.com/SWE-bench/SWE-bench/issues/157)

### Gotcha 3: Patch Must Apply Cleanly to base_commit

The patch must `git apply` cleanly to the exact `base_commit`. If the Howler edits the repo in a way that doesn't match a clean patch (e.g., modifies files not in the diff, uses absolute paths), the harness will fail to apply and score the task as unresolved.

**Mitigation**: After the Howler finishes, generate the patch with `git diff <base_commit> HEAD` from within the repo. Verify with `git apply --check <patch_file>` on a clean clone before submission.

### Gotcha 4: SWE-bench Pro Requires Modal for Scale

The Pro evaluation script (`swe_bench_pro_eval.py`) is designed to run with `--num_workers=100` on Modal. Local Docker (via `--use_local_docker`) is labeled beta and untested for large runs. Running 100 tasks locally with limited workers takes much longer than the Modal path.

**Mitigation**: Budget Modal setup time and cost. For a 50-task run, even with `--num_workers=10` locally, expect 4-8 hours wall-clock vs. ~1 hour on Modal.

### Gotcha 5: Some Pro Instances Have Extended Evaluation Times

Certain Pro instances (notably some Tutao repository tasks) previously caused extended evaluation times due to test suite characteristics. The repo notes these have been "resolved in updated run scripts," but the underlying issue (long-running test suites per task) is inherent to some repos.

**Mitigation**: Run a single-task dry run with one known-stable instance before committing to a full batch. Check the SWE-bench Pro GitHub issues for any current flagged instances.

### Gotcha 6: Contamination is Only Partially Resolved by Pro

While Pro is contamination-resistant, the held-out and commercial sets are not publicly accessible. The public set (11 repos) is available but represents a smaller surface area. A score on the public set alone is less authoritative than a full Pro evaluation.

**Mitigation**: Acknowledge in any published results which subset was used. For initial evaluation, the public set is sufficient for internal validation. For leaderboard publication, coordinate with Scale AI for held-out set access.

### Gotcha 7: Gold Specification Drift Risk

Gold's muster for a SWE-bench task adds an intermediate interpretation step. If Gold misreads the issue and writes a mini-CONTRACT.md that leads the Howler in the wrong direction, the task will fail even if the Howler executes perfectly.

**Mitigation**: White Pre-Check (I4) validates the contract against the actual codebase before the Howler starts. For baseline comparison, also run Variant C (bare Sonnet, no Gold) on the same task set to quantify how often Gold's interpretation helps vs. hurts.

### Gotcha 8: Test Environment Isolation Is Critical

Agents that modify shared state (environment variables, global config, filesystem outside the repo) can cause cross-contamination between tasks if running in parallel without proper isolation.

**Mitigation**: Run each task in a separate Docker container. Do not share Docker volumes between parallel tasks. The official harness handles this correctly — don't bypass its containerization.

---

## 10. Blockers vs. Nice-to-Haves

### Blockers (Must Resolve Before First Run)

| Blocker | Description | Resolution |
|---|---|---|
| **x86_64 machine** | Cannot run reliable evaluation on ARM/Mac | Provision AWS/GCP/Azure Linux x86_64 instance |
| **Docker 200 GB storage** | Evaluation hangs or fails with insufficient disk | Configure Docker data-root on large volume |
| **Modal account** | SWE-bench Pro eval script requires Modal for scale | Sign up and run `modal setup` |
| **Anthropic API key** | Required for all Spectrum agents | Ensure key has sufficient quota for ~$200 in API calls |
| **SWE-bench Pro dataset access** | Public set via HuggingFace is free; held-out requires Scale AI | Use public set for initial run |
| **Patch generation adapter** | Spectrum does not yet have code to format output as predictions JSONL | Build `emission_adapter.py` (1-2 days) |
| **Task input adapter** | Spectrum does not yet have code to load and format SWE-bench task fields for Gold | Build `load_tasks.py` + `format_gold_input.py` (1-2 days) |

### Nice-to-Haves (Do Not Block Initial Run)

| Feature | Benefit | Effort |
|---|---|---|
| Multi-task parallelism | Reduces wall-clock time from ~8 hrs to ~1 hr for 50 tasks | Medium — task orchestrator needed |
| Retry handler | Auto-retries failed/hung tasks | Low — wrap run_task.py with retry logic |
| Cost tracker | Per-task token usage logged alongside patch output | Low — log Anthropic API usage per invocation |
| Variant A/B/C runner | Run all three pipeline variants on the same task set for comparison | Medium — config param in run_task.py |
| SWE-bench Lite as warm-up | Faster, well-established alternative for initial pipeline validation | None — same adapter works |
| Dedicated evaluation machine | Persistent x86_64 cloud VM for repeated evaluation runs | Low operational overhead |

---

## Summary

**Recommended target**: SWE-bench Pro public set, 50-task initial run.

**Recommended pipeline for initial run**: Variant B (Lite Spectrum) — compact task brief, single Howler, White + Gray gates, no full muster ceremony. Variant A (full muster) can be added in a second run once the adapter is validated.

**Infrastructure minimum**: Linux x86_64 machine, 200 GB Docker storage, 16 GB RAM, Modal account, Anthropic API key. Budget ~$85 for a 50-task run.

**Critical path to first run**:
1. Provision x86_64 Linux machine (1 day)
2. Install and validate Docker + harness (1 day)
3. Build task input adapter + patch emission adapter (2 days)
4. Dry run on 5 tasks to validate pipeline end-to-end (1 day)
5. Full 50-task run (1 day, mostly wall-clock)
6. Evaluate and publish results (1 day)

**Total estimated timeline from zero to published score: 7-10 days** (excluding Spectrum accuracy improvements I1–I7, which can be applied incrementally).

---

## Sources

- [SWE-bench GitHub Repository](https://github.com/SWE-bench/SWE-bench)
- [SWE-bench Evaluation Guide](https://www.swebench.com/SWE-bench/guides/evaluation/)
- [SWE-bench Docker Setup Guide](https://www.swebench.com/SWE-bench/guides/docker_setup/)
- [SWE-bench FAQ](https://www.swebench.com/SWE-bench/faq/)
- [swebench PyPI package](https://pypi.org/project/swebench/)
- [SWE-bench Pro GitHub (Scale AI)](https://github.com/scaleapi/SWE-bench_Pro-os)
- [SWE-bench Pro Paper (arxiv 2509.16941)](https://arxiv.org/pdf/2509.16941)
- [Scale Labs Pro Leaderboard](https://labs.scale.com/leaderboard/swe_bench_pro_public)
- [SWE-bench Pro Leaderboard (Morph — why 46% beats 81%)](https://www.morphllm.com/swe-bench-pro)
- [OpenAI: Why we no longer evaluate SWE-bench Verified](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/)
- [Epoch AI: Run SWE-bench Verified in one hour on one machine](https://epoch.ai/blog/swebench-docker)
- [Epoch AI: SWE-bench Verified Leaderboard](https://epoch.ai/benchmarks/swe-bench-verified)
- [Augment Code: #1 open-source agent on SWE-bench Verified](https://www.augmentcode.com/blog/1-open-source-agent-on-swe-bench-verified-by-combining-claude-3-7-and-o1)
- [Augment Code: Auggie tops SWE-bench Pro](https://www.augmentcode.com/blog/auggie-tops-swe-bench-pro)
- [augment-swebench-agent (open source)](https://github.com/augmentcode/augment-swebench-agent)
- [Factory: Code Droid Technical Report](https://factory.ai/news/code-droid-technical-report)
- [Claude-flow SWE-Bench Evaluation Wiki](https://github.com/ruvnet/claude-flow/wiki/SWE-Bench-Evaluation)
- [AI21: Lessons from 200,000 SWE-bench runs](https://www.ai21.com/blog/scaling-agentic-evaluation-swe-bench/)
- [Nebius: Infrastructure behind SWE-rebench](https://nebius.com/blog/posts/infrastructure-behind-swe-rebench)
- [SWE-rebench Leaderboard](https://swe-rebench.com/)
- [SWE-bench Verified Is Broken — Grey Newell](https://greynewell.com/blog/swe-bench-verified-broken-5-things-source-code/)
- [GitHub Issue #157: docker evaluation gets stuck](https://github.com/SWE-bench/SWE-bench/issues/157)
- [Claude Sonnet 4.6 pricing guide (NxCode)](https://www.nxcode.io/resources/news/claude-sonnet-4-6-complete-guide-benchmarks-pricing-2026)
- [ScaleAI/SWE-bench_Pro dataset (HuggingFace)](https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro)
