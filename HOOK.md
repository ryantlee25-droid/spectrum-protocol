# Hook: Plant bug + create expected-output reference files
Spectrum: h2h-benchmark-0401
Howler: howler-expected
Branch: spectrum/h2h-benchmark-0401/howler-expected
Worktree: ~/.claude/spectrum/h2h-benchmark-0401/worktrees/howler-expected
Started: 2026-04-03T15:26:00Z
Updated: 2026-04-03T15:28:00Z
Status: complete
git_status: ok
Confidence: high
Confidence-Note: Clear spec, scaffold available

## Task
Plant the off-by-one bug in validate.ts and create per-task expected output manifests (files.txt + checks.json for tasks 1-4).

## File Ownership
CREATES:
- benchmarks/head-to-head/expected/task1/files.txt
- benchmarks/head-to-head/expected/task1/checks.json
- benchmarks/head-to-head/expected/task2/files.txt
- benchmarks/head-to-head/expected/task2/checks.json
- benchmarks/head-to-head/expected/task3/files.txt
- benchmarks/head-to-head/expected/task3/checks.json
- benchmarks/head-to-head/expected/task4/files.txt
- benchmarks/head-to-head/expected/task4/checks.json
MODIFIES:
- benchmarks/head-to-head/scaffold/src/utils/validate.ts

## Checkpoints
- types: N/A

## Progress
- Scaffold merged from howler-scaffold
- Bug planted: `>` changed to `>=` in validate.ts limit check
- All 8 expected output files created
- Verified: tsc passes, jest has exactly 1 failure (limit=100 test)

## Completion Verification
- All 8 CREATES files exist: PASS
- MODIFIES (validate.ts) changed: PASS (git diff confirms)
- tsc --noEmit on bugged scaffold: PASS
- jest on bugged scaffold: 1 failed, 26 passed (exactly as expected)
- Task 3 checks.json must_contain `limit > config.api.maxLimit` will match the FIXED version
- Task 3 checks.json must_not_contain `limit >= config.api.maxLimit` will catch the bugged version

## Issue Re-Read
Issue re-read: no gaps identified. Bug is subtle (logic error, not type error), exactly 1 test catches it, and the fix is unambiguous (`>=` to `>`).
