# Task 2: Add Rate Limiting (Shared Feature Add)

## Description

Add a rate-limiting middleware module and integrate it into all three API endpoint files (`users.ts`, `posts.ts`, `auth.ts`). This tests the ability to create a new shared module and correctly wire it into multiple consumers — a coordination-heavy task where inconsistent integration causes failures.

## Files to Touch

- `src/utils/rateLimit.ts` — **create** new file with rate-limiting logic
- `src/api/users.ts` — import and call rate limiter before processing
- `src/api/posts.ts` — import and call rate limiter before processing
- `src/api/auth.ts` — import and call rate limiter before processing (or export a wrapped middleware)
- `src/config.ts` — add rate-limit configuration (window size, max requests)
- `tests/rateLimit.test.ts` — **create** tests for the new module

## Expected Outcome

- A `rateLimit.ts` utility exists with a clear API (e.g., `checkRateLimit(key: string): void | throws`)
- Rate limit config exists in `config.ts` (e.g., `rateLimit: { windowMs: 60000, maxRequests: 100 }`)
- All three API files import from `rateLimit.ts`
- `tsc --noEmit` passes
- All existing tests still pass
- New rate-limit tests pass

## Done When

- [ ] `src/utils/rateLimit.ts` exists and exports a rate-limiting function
- [ ] `grep -l "rateLimit" src/api/users.ts src/api/posts.ts src/api/auth.ts` returns all 3 files
- [ ] `src/config.ts` contains rate-limit configuration
- [ ] `tsc --noEmit` passes
- [ ] `jest` passes with all tests green (existing + new)
