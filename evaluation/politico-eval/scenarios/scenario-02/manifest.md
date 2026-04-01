# Manifest: express-api-0331

**Rain ID**: express-api-0331
**Mode**: full
**Base Branch**: main
**Base Commit**: 9c3f7de

## Task List

| Howler | Scope | Effort | Serial Risk |
|--------|-------|--------|-------------|
| howler-auth | Implement JWT authentication middleware, token validation, and user session extraction | M | no |
| howler-routes | Build REST routes for `/users`, `/projects`, and `/health` endpoints with request validation | M | no |
| howler-middleware | Implement request logging, error handling middleware, rate limiting, and CORS configuration | S | no |
| howler-tests | Write integration tests for all routes and middleware using supertest | M | yes |

## File Ownership Matrix

| File | Howler | Action |
|------|--------|--------|
| `src/middleware/auth.ts` | howler-auth | CREATES |
| `src/middleware/jwt.ts` | howler-auth | CREATES |
| `src/types/auth.ts` | howler-auth | CREATES |
| `src/routes/users.ts` | howler-routes | CREATES |
| `src/routes/projects.ts` | howler-routes | CREATES |
| `src/routes/health.ts` | howler-routes | CREATES |
| `src/middleware/logger.ts` | howler-middleware | CREATES |
| `src/middleware/errorHandler.ts` | howler-middleware | CREATES |
| `src/middleware/rateLimiter.ts` | howler-middleware | CREATES |
| `src/constants.ts` | howler-middleware | CREATES |
| `tests/users.test.ts` | howler-tests | CREATES |
| `tests/projects.test.ts` | howler-tests | CREATES |
| `tests/auth.test.ts` | howler-tests | CREATES |
| `tests/middleware.test.ts` | howler-tests | CREATES |

**CONFLICTS**: none (verified — no file appears in more than one Howler's ownership)

## Dependency Graph (DAG)

```yaml
- id: howler-auth
  deps: []
  branch: spectrum/express-api-0331/howler-auth
  base_branch: main
  base_commit: 9c3f7de

- id: howler-routes
  deps: [howler-auth#types]
  branch: spectrum/express-api-0331/howler-routes
  base_branch: main
  base_commit: 9c3f7de

- id: howler-middleware
  deps: []
  branch: spectrum/express-api-0331/howler-middleware
  base_branch: main
  base_commit: 9c3f7de

- id: howler-tests
  deps: [howler-auth, howler-routes, howler-middleware]
  branch: spectrum/express-api-0331/howler-tests
  base_branch: main
  base_commit: 9c3f7de
```

## Decomposition Rationale

I chose 4 Howlers because auth, routing, and middleware are cleanly separable concerns in Express. howler-auth and howler-middleware run in parallel (no dependency between them). howler-routes takes a #types checkpoint on howler-auth to get the AuthenticatedRequest type before building route handlers. howler-tests is sequential on all three because integration tests require the full server to exist. Alternative: merging routes + middleware — rejected because middleware is cross-cutting and best implemented independently.

## Politico Review

_Not yet conducted — pre-freeze review scheduled._
