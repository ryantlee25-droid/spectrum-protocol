# Contract: express-api-0331

**Frozen at**: 2026-03-31T09:30:00Z
**Status**: FROZEN — do not modify. File AMENDMENT.md if changes are needed.

---

## Shared Types

All Howlers importing shared types MUST use the paths defined here. Do not re-declare these types.

### AuthenticatedRequest (source: howler-auth)
```typescript
// src/types/auth.ts
import { Request } from "express";

export interface AuthenticatedRequest extends Request {
  user: {
    userId: string;
    email: string;
    role: "admin" | "user" | "readonly";
    orgId: string;
  };
}
```

### AppConstants (source: howler-middleware)
```typescript
// src/constants.ts
export const RATE_LIMIT_WINDOW_MS = 15 * 60 * 1000; // 15 minutes
export const RATE_LIMIT_MAX = 100;
export const CORS_ORIGINS = ["http://localhost:3000"];
export const JWT_ALGORITHM = "HS256";
```

---

## Naming Conventions

- **Middleware files**: camelCase function exports, kebab-case filenames (`errorHandler.ts`, `rateLimiter.ts`)
- **Route files**: grouped by resource, one file per resource (`users.ts`, `projects.ts`)
- **Types**: PascalCase interfaces, exported from `src/types/`
- **Tests**: `tests/{resource}.test.ts` using Jest + supertest
- **Error handling**: all errors propagate to the central error handler via `next(err)` — never `res.json()` directly in catch blocks

---

## Integration Points

| From | To | Interface | Where |
|------|----|-----------|-------|
| howler-auth | howler-routes | `AuthenticatedRequest` type | howler-routes imports from `@/types/auth` |
| howler-auth | howler-middleware | `JWT_ALGORITHM` constant | howler-middleware imports from `@/constants` |
| howler-middleware | howler-routes | `errorHandler` middleware | routes registered before error handler in app factory |
| howler-middleware | howler-tests | `errorHandler`, `logger` | tests verify middleware behavior |
| howler-routes | howler-tests | Route handlers | tests call routes via supertest |

---

## Design-by-Contract: howler-auth

### Preconditions
- `JWT_SECRET` environment variable is defined in `.env`
- Express and `jsonwebtoken` are in `package.json`

### Postconditions
- `src/middleware/auth.ts` exports `requireAuth` middleware function with signature `(req: AuthenticatedRequest, res: Response, next: NextFunction) => void`
- `src/middleware/jwt.ts` exports `verifyToken(token: string): Promise<JwtPayload>` — throws on invalid token
- `src/types/auth.ts` exports `AuthenticatedRequest` matching the contract definition above
- Authentication failures return HTTP 401 with a structured error body

### Invariants
- `requireAuth` never mutates `req.body` or `req.query`
- Token expiry is enforced; expired tokens return 401, not 403

---

## Design-by-Contract: howler-routes

### Preconditions
- `howler-auth#types` checkpoint is STABLE (`AuthenticatedRequest` finalized)
- `src/types/auth.ts` exists with the `AuthenticatedRequest` interface

### Postconditions
- `src/routes/users.ts` exports an Express Router with `GET /`, `GET /:id`, `POST /`, `PUT /:id`, `DELETE /:id`
- `src/routes/projects.ts` exports an Express Router with `GET /`, `GET /:id`, `POST /`, `PUT /:id`
- `src/routes/health.ts` exports an Express Router with `GET /` returning `{ status: "ok", timestamp: string }`
- All protected routes use `requireAuth` middleware before the handler
- Request validation uses `zod` schemas; invalid requests return HTTP 400

### Invariants
- `/health` route requires no authentication
- All authenticated routes call `requireAuth` as the first middleware

---

## Design-by-Contract: howler-middleware

### Preconditions
- Express is in `package.json`
- `src/constants.ts` is owned by this Howler (self-dependency — constants written and consumed here)

### Postconditions
- `src/middleware/logger.ts` exports `logger` middleware using `morgan` or equivalent
- `src/middleware/errorHandler.ts` exports `errorHandler(err, req, res, next)` — Express error middleware signature (4 arguments)
- `src/middleware/rateLimiter.ts` exports `rateLimiter` using `express-rate-limit`
- `src/constants.ts` exports all constants listed in the Shared Types section above
- CORS configured for origins in `CORS_ORIGINS`

### Invariants
- `errorHandler` always returns a JSON response, never HTML
- Rate limiter applies to all routes except `/health`

---

## Conventions Only: howler-tests

_(Sequential Howler — simplified contract)_

- Use Jest + supertest; test files in `tests/` directory
- Create an Express app instance in a `tests/helpers/app.ts` test helper — do not import from `src/app.ts`
- Mock `verifyToken` for auth tests, not the full JWT library
- Each route must have at minimum: one happy path test, one auth failure test (401), one validation failure test (400)
- `tests/middleware.test.ts` covers error handler format (JSON body, correct status codes) and rate limiter headers
