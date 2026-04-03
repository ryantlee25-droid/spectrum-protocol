# Task 1: Rename Type (Multi-File Refactor)

## Description

Rename the `User` type to `Account` across the entire codebase. This tests the ability to make a consistent cross-file change: updating the type definition, all imports, all usage sites, type annotations, variable names where appropriate, and tests.

## Files to Touch

- `src/types.ts` — rename the interface from `User` to `Account`
- `src/api/users.ts` — update type imports, the in-memory store type, function signatures, return types
- `src/api/posts.ts` — update `authorId` references if typed against `User`
- `src/api/auth.ts` — update role type references if derived from `User`
- `tests/users.test.ts` — update any type references
- `tests/posts.test.ts` — update any type references
- `tests/auth.test.ts` — no changes expected (auth doesn't reference `User` directly)

## Expected Outcome

- The `User` interface no longer exists anywhere in the codebase
- An `Account` interface exists in `src/types.ts` with identical shape
- All imports of `User` are replaced with `Account`
- `tsc --noEmit` passes
- All tests pass
- No stale references to `User` remain (grep for `User` should return zero hits in source files, excluding comments that explain the rename)

## Done When

- [ ] `grep -r "User" src/ --include="*.ts"` returns zero results (excluding the `PaginatedResponse` generic which uses `T`)
- [ ] `tsc --noEmit` passes
- [ ] `jest` passes with all tests green
- [ ] The `Account` interface is exported from `src/types.ts`
