# Contract: auth-refactor-0329

**Frozen at**: 2026-03-29T10:15:00Z
**Status**: FROZEN -- do not modify. File AMENDMENT.md if changes are needed.

---

## Shared Types

All Howlers importing shared types MUST use the paths defined here. Do not re-declare these types.

### UserSession (source: howler-auth)
```typescript
// src/types/auth.ts
export interface UserSession {
  userId: string;
  email: string;
  role: "admin" | "member" | "viewer";
  orgId: string;
  sessionToken: string;
  expiresAt: Date;
}
```

### ApiResponse Envelope (source: howler-api)
```typescript
// src/types/api.ts
export interface ApiResponse<T> {
  data: T;
  meta: {
    page: number;
    pageSize: number;
    total: number;
  };
  errors: ApiError[];
}

export interface ApiError {
  code: string;
  message: string;
  field?: string;
}
```

---

## Naming Conventions

- **Files**: kebab-case for utilities (`api-utils.ts`), PascalCase for components (`Header.tsx`)
- **Types**: PascalCase, exported from `src/types/` directory
- **API routes**: Next.js App Router convention (`src/app/api/{resource}/route.ts`)
- **Tests**: `tests/{domain}.test.ts` using Vitest
- **Imports**: Use `@/` path alias for `src/`

---

## Integration Points

| From | To | Interface | Where |
|------|-----|-----------|-------|
| howler-auth | howler-api | `UserSession` type | howler-api imports from `@/types/auth` |
| howler-auth | howler-ui | `UserSession` type | howler-ui imports from `@/types/auth` |
| howler-auth | howler-ui | `ClerkProvider` wrapper | howler-auth adds to `layout.tsx`, howler-ui consumes |
| howler-api | howler-tests | API route handlers | howler-tests calls routes via `fetch` |
| howler-ui | howler-tests | Component renders | howler-tests imports components for render tests |

---

## Design-by-Contract: howler-auth

### Preconditions
- `src/app/layout.tsx` exists and exports a root layout component
- Clerk environment variables (`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`) are defined in `.env.local`

### Postconditions
- `src/middleware/auth.ts` exports `authMiddleware` that validates session tokens
- `src/lib/session.ts` exports `getSession(): Promise<UserSession | null>`
- `src/types/auth.ts` exports `UserSession` interface matching the contract definition above
- `src/app/layout.tsx` wraps children in `<ClerkProvider>`

### Invariants
- Authentication middleware never blocks public routes (`/`, `/sign-in`, `/api/health`)
- `getSession()` returns `null` for unauthenticated requests, never throws

---

## Design-by-Contract: howler-api

### Preconditions
- `howler-auth#types` checkpoint is STABLE (UserSession type is finalized)
- `src/types/auth.ts` exists with the `UserSession` interface

### Postconditions
- All API routes return `ApiResponse<T>` envelope
- All API routes validate authentication via `getSession()` before processing
- Pagination defaults: `page=1`, `pageSize=20`, `maxPageSize=100`

### Invariants
- API routes never return raw data outside the `ApiResponse` envelope
- 401 responses use `ApiError` with code `"UNAUTHORIZED"`

---

## Conventions Only: howler-ui

_(Pure-create Howler -- simplified contract)_

- Use `@clerk/nextjs` components (`SignInButton`, `UserButton`) for auth UI
- All dashboard pages are server components unless client interactivity is required
- Header includes `UserButton` from Clerk
- Sidebar navigation uses Next.js `Link` components
- Protected pages redirect to `/sign-in` if `getSession()` returns null

---

## Conventions Only: howler-tests

_(Sequential Howler -- simplified contract)_

- Use Vitest + React Testing Library
- Test files in `tests/` directory (not colocated)
- Mock `getSession()` for auth tests, not the full Clerk SDK
- API tests use `fetch` against the route handlers directly
- Minimum: 1 test per API route, 1 render test per component, 1 auth flow test
