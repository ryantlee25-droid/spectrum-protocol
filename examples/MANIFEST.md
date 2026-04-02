# Manifest: auth-refactor-0329

**Rain ID**: auth-refactor-0329
**Mode**: full
**Base Branch**: main
**Base Commit**: a1b2c3d

## Task List

| Howler | Scope | Effort | Serial Risk |
|--------|-------|--------|-------------|
| howler-auth | Implement Clerk authentication middleware, session management, and protected route wrappers | M | no |
| howler-api | Build REST API layer with pagination, filtering, and error envelope | L | no |
| howler-ui | Dashboard components: header, sidebar, protected pages, sign-in flow | M | no |
| howler-tests | Integration tests for auth + API + UI flows | M | yes |

## File Ownership Matrix

| File | Howler | Action |
|------|--------|--------|
| `src/middleware/auth.ts` | howler-auth | CREATES |
| `src/lib/session.ts` | howler-auth | CREATES |
| `src/app/layout.tsx` | howler-auth | MODIFIES |
| `src/types/auth.ts` | howler-auth | CREATES |
| `src/app/api/users/route.ts` | howler-api | CREATES |
| `src/app/api/projects/route.ts` | howler-api | CREATES |
| `src/lib/api-utils.ts` | howler-api | CREATES |
| `src/types/api.ts` | howler-api | CREATES |
| `src/components/Header.tsx` | howler-ui | CREATES |
| `src/components/Sidebar.tsx` | howler-ui | CREATES |
| `src/app/dashboard/page.tsx` | howler-ui | CREATES |
| `src/app/sign-in/page.tsx` | howler-ui | CREATES |
| `tests/auth.test.ts` | howler-tests | CREATES |
| `tests/api.test.ts` | howler-tests | CREATES |
| `tests/dashboard.test.ts` | howler-tests | CREATES |

**CONFLICTS**: none (verified -- no file appears in more than one Howler's ownership)

## Dependency Graph (DAG)

<!-- DAG format: YAML list. Each node declares its own edges. deps use howler-name for full completion, howler-name#checkpoint for partial. -->
```yaml
- id: howler-auth
  deps: []
  branch: spectrum/auth-refactor-0329/howler-auth
  base_branch: main
  base_commit: a1b2c3d

- id: howler-api
  deps: [howler-auth#types]
  branch: spectrum/auth-refactor-0329/howler-api
  base_branch: main
  base_commit: a1b2c3d

- id: howler-ui
  deps: [howler-auth#types]
  branch: spectrum/auth-refactor-0329/howler-ui
  base_branch: main
  base_commit: a1b2c3d

- id: howler-tests
  deps: [howler-auth, howler-api, howler-ui]
  branch: spectrum/auth-refactor-0329/howler-tests
  base_branch: main
  base_commit: a1b2c3d
```

## Decomposition Rationale

I chose 4 Howlers because the auth, API, and UI layers have clear file boundaries with minimal interface overlap. The test Howler is sequential (depends on all three) because integration tests need the actual implementations to exist. Alternative: 3 Howlers with tests inline -- rejected because test Howler can run the full integration suite rather than each Howler testing in isolation.

## Politico Review

- **Blocker (addressed)**: `howler-api` originally had no dependency on `howler-auth#types` -- would have duplicated the `UserSession` type. Fixed: added `#types` dependency.
- **Warning (accepted)**: `howler-tests` is on the critical path and blocked by all three other Howlers. Accepted because integration tests genuinely need all implementations.
- **Observation**: `howler-ui` scope is larger than other Howlers due to 4 component files. Flagged as `effort: M` (not L) because components are straightforward.
