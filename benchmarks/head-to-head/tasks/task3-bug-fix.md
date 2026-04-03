# Task 3: Fix Pagination Bug (Bug Fix + Test)

## Description

There is an off-by-one bug in `src/utils/validate.ts` in the `validatePagination` function. The limit check incorrectly rejects `limit=100` (the maximum allowed value) because it uses `>=` instead of `>` when comparing against the max limit. Find the bug, fix it, and ensure the test that catches this edge case passes.

## Files to Touch

- `src/utils/validate.ts` — fix the off-by-one in the limit boundary check
- `tests/users.test.ts` — the "should accept limit of 100" test should already exist and be failing; verify it passes after the fix

## Expected Outcome

- `validatePagination(1, 100)` no longer throws (100 is a valid limit)
- `validatePagination(1, 101)` still throws (101 exceeds the max)
- The boundary is `limit > config.api.maxLimit`, not `limit >= config.api.maxLimit`
- `tsc --noEmit` passes
- All tests pass (the previously-failing pagination edge case test now passes)

## Done When

- [ ] The line in `validate.ts` reads `limit > config.api.maxLimit` (not `>=`)
- [ ] `jest` passes with all tests green
- [ ] `tsc --noEmit` passes
- [ ] No other files were modified unnecessarily
