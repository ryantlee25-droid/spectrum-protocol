# Manifest: auth-session-0331

**Rain ID**: auth-session-0331
**Mode**: full
**Base Branch**: main
**Base Commit**: 2d8f1ac

## Task List

| Howler | Scope | Effort | Serial Risk |
|--------|-------|--------|-------------|
| howler-schema | Define database schema for users and sessions tables, write Drizzle ORM models, and generate initial migration | M | no |
| howler-session | Implement server-side session store using Redis, session lifecycle (create, read, invalidate), and session serialization | M | no |
| howler-auth | Build authentication flows: registration, login, logout, password hashing, and token issuance | L | no |
| howler-middleware | Implement session validation middleware, protected route guards, and request context injection | S | no |
| howler-tests | Write integration tests for the full auth lifecycle: register → login → protected route → logout | M | yes |

## File Ownership Matrix

| File | Howler | Action |
|------|--------|--------|
| `src/db/schema.ts` | howler-schema | CREATES |
| `src/db/client.ts` | howler-schema | CREATES |
| `src/db/migrations/0001_users_sessions.sql` | howler-schema | CREATES |
| `src/models/user.ts` | howler-schema | CREATES |
| `src/session/store.ts` | howler-session | CREATES |
| `src/session/lifecycle.ts` | howler-session | CREATES |
| `src/session/serializer.ts` | howler-session | CREATES |
| `src/auth/register.ts` | howler-auth | CREATES |
| `src/auth/login.ts` | howler-auth | CREATES |
| `src/auth/logout.ts` | howler-auth | CREATES |
| `src/auth/password.ts` | howler-auth | CREATES |
| `src/types/auth.ts` | howler-auth | CREATES |
| `src/middleware/session.ts` | howler-middleware | CREATES |
| `src/middleware/guard.ts` | howler-middleware | CREATES |
| `tests/auth.integration.test.ts` | howler-tests | CREATES |
| `tests/session.integration.test.ts` | howler-tests | CREATES |

**CONFLICTS**: none (verified — no file appears in more than one Howler's ownership)

## Dependency Graph (DAG)

```yaml
- id: howler-schema
  deps: []
  branch: spectrum/auth-session-0331/howler-schema
  base_branch: main
  base_commit: 2d8f1ac

- id: howler-session
  deps: [howler-schema#types]
  branch: spectrum/auth-session-0331/howler-session
  base_branch: main
  base_commit: 2d8f1ac

- id: howler-auth
  deps: [howler-schema#types]
  branch: spectrum/auth-session-0331/howler-auth
  base_branch: main
  base_commit: 2d8f1ac

- id: howler-middleware
  deps: [howler-auth#types, howler-session#types]
  branch: spectrum/auth-session-0331/howler-middleware
  base_branch: main
  base_commit: 2d8f1ac

- id: howler-tests
  deps: [howler-auth, howler-session, howler-middleware]
  branch: spectrum/auth-session-0331/howler-tests
  base_branch: main
  base_commit: 2d8f1ac
```

## Decomposition Rationale

I chose 5 Howlers because schema, session store, auth logic, middleware, and tests are separable concerns. howler-schema runs first (no deps) and provides the database models to both howler-session and howler-auth via #types checkpoints. howler-middleware depends on both auth and session types before it can build the validation middleware. howler-tests is sequential on all three implementation Howlers. Alternative: merging howler-session into howler-auth — rejected because the Redis session store is an independent infrastructure concern that could be swapped without touching auth logic.

## Politico Review

_Not yet conducted — pre-freeze review scheduled._
