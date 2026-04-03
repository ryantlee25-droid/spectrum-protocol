# Task 4: Parallel Pure-Create (Independent New Files)

## Description

Create three new, independent utility modules that have no dependencies on each other. This tests raw parallel creation ability — there are no coordination challenges, so both a single agent and Spectrum should succeed. The question is whether Spectrum's overhead is justified for trivially parallel work.

## Files to Create

- `src/utils/sanitize.ts` — HTML/string sanitization utilities
- `src/utils/cache.ts` — simple in-memory TTL cache
- `src/utils/retry.ts` — retry-with-backoff utility

## Requirements

### `src/utils/sanitize.ts`
- Export `sanitizeHtml(input: string): string` — strips HTML tags
- Export `escapeForLog(input: string): string` — escapes newlines, tabs, and control characters for safe logging
- No external dependencies

### `src/utils/cache.ts`
- Export `createCache<T>(ttlMs: number): Cache<T>` — creates a TTL cache instance
- Cache interface: `get(key: string): T | undefined`, `set(key: string, value: T): void`, `delete(key: string): void`, `clear(): void`
- Expired entries are lazily evicted on `get()`
- No external dependencies

### `src/utils/retry.ts`
- Export `retry<T>(fn: () => Promise<T>, options?: RetryOptions): Promise<T>`
- `RetryOptions`: `maxAttempts` (default 3), `baseDelayMs` (default 100), `backoffMultiplier` (default 2)
- Uses exponential backoff
- No external dependencies

### Tests
- `tests/sanitize.test.ts` — test both exported functions
- `tests/cache.test.ts` — test TTL expiration, get/set/delete/clear
- `tests/retry.test.ts` — test success, retry on failure, max attempts exceeded

## Expected Outcome

- All 3 utility files exist with the specified exports
- All 3 test files exist and pass
- `tsc --noEmit` passes
- No existing files were modified

## Done When

- [ ] All 6 new files exist (`ls` confirms)
- [ ] `tsc --noEmit` passes
- [ ] `jest` passes with all tests green (existing + new)
- [ ] No modifications to any existing files (`git diff --name-only` shows only new files)
