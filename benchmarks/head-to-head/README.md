# Head-to-Head Benchmark: Raw Sonnet vs Spectrum Protocol

A controlled experiment comparing raw single-agent Claude Sonnet against the Spectrum multi-agent coordination protocol on 4 synthetic TypeScript tasks.

## Quick Start

```bash
# Run a single task (both variants)
./run.sh --task 1

# Run only Variant A (raw Sonnet)
./run.sh --task 3 --variant a

# Score an already-completed run without prompts
./run.sh --task 2 --skip-prompt
```

## How It Works

1. **`run.sh`** copies the scaffold to `tmp/variant-a` and `tmp/variant-b`
2. It prints the exact `claude` prompt for each variant
3. You run `claude` manually in each tmp directory
4. Press Enter when done -- the script scores both variants automatically
5. Results are saved to `results/run-<timestamp>.md`

## Tasks

| Task | Type | Difficulty | What It Tests |
|------|------|-----------|---------------|
| 1 | Multi-file refactor | Medium | Consistent cross-file rename (User -> Account) |
| 2 | Shared feature add | Hard | New module + wire into 3 consumers (rate limiting) |
| 3 | Bug fix + test | Easy | Find and fix off-by-one in pagination validation |
| 4 | Parallel pure-create | Easy | 3 independent utility modules (sanitize, cache, retry) |

## Scoring

Each task is scored on 5 dimensions:

### Correctness
- **tsc --noEmit**: Does the TypeScript code type-check?
- **jest**: Do all tests pass?

### Completeness
- Are all expected files present? Compared against `expected/task<N>/files.txt`.

### Conflicts
- Pattern-based checks from `expected/task<N>/checks.json`:
  - **must_contain**: Required patterns that must exist (e.g., rate-limit import in all consumers)
  - **must_not_contain**: Forbidden patterns (e.g., stale `User` references after rename)

### Cost (optional)
- Token count parsed from a `--session-log` file (Claude Code output)
- Gracefully omitted if no log is provided

### Time (optional)
- Wall-clock duration via `--duration-seconds` argument
- Gracefully omitted if not provided

## Output Format

### JSON
```json
{
  "task": 1,
  "variant": "raw-sonnet",
  "correctness": { "tsc_pass": true, "jest_pass": true, "pass": true },
  "completeness": { "pass": true, "missing": [], "extra": [] },
  "conflicts": { "pass": true, "violations": [] },
  "cost_tokens": null,
  "duration_seconds": null,
  "timestamp": "2026-04-01T12:00:00+00:00",
  "overall_pass": true
}
```

### Markdown
Human-readable table with per-check detail, saved to `results/run-<timestamp>.md`.

## Adding a New Task

1. Create `tasks/task<N>-<name>.md` with description, files to touch, expected outcome, and done-when checklist
2. Create `expected/task<N>/files.txt` with one relative path per line (all files that should exist after the task)
3. Create `expected/task<N>/checks.json` with `must_contain` and `must_not_contain` pattern checks
4. Update this README's task table

## Known Limitations

- **Manual Claude invocation**: `run.sh` prints prompts but does not auto-invoke `claude`. Automation is a follow-up.
- **Token cost parsing**: Depends on Claude Code output format, which may change. Falls back gracefully.
- **No CI integration**: Designed for local interactive use.
- **Static scoring only**: No live API calls. Correctness is tsc + jest; no runtime behavior testing beyond what jest covers.
- **4 tasks only**: Initial version. More tasks can be added following the pattern above.

## Directory Structure

```
benchmarks/head-to-head/
  README.md          # This file
  run.sh             # Test runner (bash)
  score.py           # Scoring engine (Python, stdlib only)
  scaffold/          # Canonical TypeScript project (10 source + 3 test files)
  tasks/             # Task definition markdown files
  expected/          # Per-task expected output manifests
    task1/
      files.txt      # Expected file list
      checks.json    # Pattern checks
    task2/
    task3/
    task4/
  results/           # Scored run outputs (gitignored)
  tmp/               # Working copies during runs (auto-cleaned)
```
