# Contract: auth-session-0331

**Frozen at**: 2026-03-31T10:15:00Z
**Status**: FROZEN — do not modify. File AMENDMENT.md if changes are needed.

---

## Shared Types

All Howlers importing shared types MUST use the paths defined here. Do not re-declare these types.

### User (source: howler-schema)
```typescript
// src/models/user.ts
export interface User {
  id: string;           // UUID
  email: string;
  passwordHash: string;
  role: "admin" | "member";
  createdAt: Date;
  updatedAt: Date;
}
```

### SessionData (source: howler-session)
```typescript
// src/session/serializer.ts
export interface SessionData {
  sessionId: string;
  userId: string;
  createdAt: Date;
  expires: Date | string;   // serialized as ISO string in Redis, parsed as Date in memory
  metadata: {
    userAgent?: string;
    ipAddress?: string;
  };
}
```

### AuthContext (source: howler-auth)
```typescript
// src/types/auth.ts
export interface AuthContext {
  user: Pick<User, "id" | "email" | "role">;
  session: Pick<SessionData, "sessionId" | "expires">;
  isAuthenticated: true;
}
```

---

## Naming Conventions

- **Auth module files**: verb-noun pattern (`register.ts`, `login.ts`, `logout.ts`)
- **Session module files**: noun pattern (`store.ts`, `lifecycle.ts`, `serializer.ts`)
- **Middleware files**: noun pattern (`session.ts`, `guard.ts`)
- **Types**: PascalCase interfaces exported from `src/types/` or alongside their module
- **Database**: Drizzle ORM schema in `src/db/schema.ts`; client singleton in `src/db/client.ts`
- **Environment variables**: `DATABASE_URL`, `REDIS_URL`, `SESSION_SECRET`, `JWT_SECRET`

---

## Integration Points

| From | To | Interface | Where |
|------|----|-----------|-------|
| howler-schema | howler-session | `User` model (for userId FK validation) | howler-session imports User from `@/models/user` |
| howler-schema | howler-auth | `User` model | howler-auth reads/writes User records |
| howler-session | howler-auth | `SessionData` type | howler-auth calls `createSession()` after login |
| howler-session | howler-middleware | `SessionData` type | howler-middleware deserializes session from request cookie |
| howler-auth | howler-middleware | `AuthContext` type | howler-middleware attaches AuthContext to request |
| howler-auth | howler-tests | Auth flow entry points | tests call register/login/logout |
| howler-middleware | howler-tests | Guard middleware | tests assert 401 on unguarded requests |

---

## Design-by-Contract: howler-schema

### Preconditions
- PostgreSQL is available at `DATABASE_URL`
- `drizzle-orm` and `drizzle-kit` are in `package.json`

### Postconditions
- `src/db/schema.ts` exports `usersTable` and `sessionsTable` Drizzle table definitions
- `src/db/client.ts` exports a singleton `db` client instance
- `src/models/user.ts` exports the `User` interface matching the contract definition above
- `src/db/migrations/0001_users_sessions.sql` contains the initial DDL for both tables
- Sessions table has columns: `session_id` (PK), `user_id` (FK → users), `expires_at` (timestamptz), `data` (jsonb)

### Invariants
- The `db` client is a singleton — never instantiated twice
- All schema types are inferred from Drizzle table definitions; no manual type duplication

---

## Design-by-Contract: howler-session

### Preconditions
- `howler-schema#types` checkpoint is STABLE (User model finalized)
- Redis is available at `REDIS_URL`
- `ioredis` is in `package.json`

### Postconditions
- `src/session/store.ts` exports `createSession(userId: string, metadata?: SessionData["metadata"]): Promise<SessionData>`
- `src/session/store.ts` exports `getSession(sessionId: string): Promise<SessionData | null>`
- `src/session/store.ts` exports `invalidateSession(sessionId: string): Promise<void>`
- `src/session/lifecycle.ts` exports session TTL constant: `SESSION_TTL_SECONDS = 86400` (24h)
- `src/session/serializer.ts` exports `SessionData` interface and serialization helpers

### Invariants
- Sessions stored in Redis with TTL equal to `SESSION_TTL_SECONDS`
- `getSession()` returns null for expired or nonexistent sessions, never throws
- Session IDs are generated with `crypto.randomUUID()`

---

## Design-by-Contract: howler-auth

### Preconditions
- `howler-schema#types` checkpoint is STABLE (User model finalized)
- `bcrypt` and `jsonwebtoken` are in `package.json`

### Postconditions
- `src/auth/register.ts` exports `registerUser(email: string, password: string): Promise<User>` — throws on duplicate email
- `src/auth/login.ts` exports `loginUser(email: string, password: string): Promise<AuthContext>` — throws on invalid credentials
- `src/auth/logout.ts` exports `logoutUser(sessionId: string): Promise<void>`
- `src/auth/password.ts` exports `hashPassword(plain: string): Promise<string>` and `verifyPassword(plain: string, hash: string): Promise<boolean>`
- `src/types/auth.ts` exports `AuthContext` matching the contract definition above

### Invariants
- Passwords are hashed with bcrypt at cost factor ≥ 12 before storage
- `loginUser` calls `createSession()` from howler-session's store — auth does not manage session storage directly
- Failed login attempts do not reveal whether the email exists (consistent timing + message)

---

## Design-by-Contract: howler-middleware

### Preconditions
- `howler-auth#types` checkpoint is STABLE (AuthContext finalized)
- `howler-session#types` checkpoint is STABLE (SessionData finalized)

### Postconditions
- `src/middleware/session.ts` exports `sessionMiddleware` that reads session cookie, calls `getSession()`, and attaches `SessionData` to `req.session`
- `src/middleware/guard.ts` exports `requireAuth` middleware that reads `req.session`, hydrates `AuthContext`, attaches to `req.auth`, and calls `next()` — or returns 401 if session is invalid
- Both middlewares are typed with Express augmentation (no `any` on req)

### Invariants
- `sessionMiddleware` runs before `requireAuth` in all route stacks
- `requireAuth` never calls `getSession()` directly — it reads from `req.session` (set by sessionMiddleware)

---

## Conventions Only: howler-tests

_(Sequential Howler — simplified contract)_

- Use Vitest + supertest
- Spin up a real PostgreSQL test database using `DATABASE_URL` pointing to a test schema
- Use a real Redis instance (not mocked) for session integration tests
- Test sequence: `registerUser` → `loginUser` → assert AuthContext → hit protected route → `logoutUser` → assert 401
- JWT secret handling is covered by CONTRACT.md — howler-tests reads `JWT_SECRET` from environment, not hardcoded
