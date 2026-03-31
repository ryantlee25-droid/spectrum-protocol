---
howler: howler-auth
spectrum: auth-refactor-0329
status: complete
pr: https://github.com/example/app/pull/47
completed: 2026-03-29T11:15:00Z
confidence: high
seams:
  - id: s1
    target_howler: howler-api
    type: import
    what: "UserSession from @/types/auth"
    where: "src/app/api/users/route.ts"
  - id: s2
    target_howler: howler-ui
    type: import
    what: "UserSession from @/types/auth"
    where: "src/components/Header.tsx"
  - id: s3
    target_howler: howler-ui
    type: provider
    what: "ClerkProvider wrapping app in layout.tsx"
    where: "src/app/layout.tsx"
assumptions:
  - id: a1
    about_howler: howler-api
    what: "will import UserSession from @/types/auth for route handler type safety"
  - id: a2
    about_howler: howler-ui
    what: "will use ClerkProvider context for SignInButton and UserButton components"
files_created:
  - src/middleware/auth.ts
  - src/lib/session.ts
  - src/types/auth.ts
files_modified:
  - src/app/layout.tsx
contract_compliance: full
open_exits:
  - "No org-creation flow -- Clerk organizations API is available but not wired up"
  - "No role-based route protection beyond the middleware -- individual routes check roles themselves"
warnings:
  - "Clerk requires manual dashboard setup (API keys, redirect URLs) -- not automatable"
  - "Session token refresh happens client-side via Clerk's SDK -- server-side getSession() reads the latest valid token but does not trigger refresh"
---

## What I Built

Implemented Clerk-based authentication for the application:

1. **Auth middleware** (`src/middleware/auth.ts`): Validates session tokens on every request. Public routes (`/`, `/sign-in`, `/api/health`) bypass authentication. All other routes require a valid Clerk session.

2. **Session helper** (`src/lib/session.ts`): Exports `getSession()` which returns a `UserSession` object or `null`. This is the single entry point for all server-side auth checks. Downstream code (API routes, server components) imports this instead of using Clerk's SDK directly.

3. **UserSession type** (`src/types/auth.ts`): The shared type that howler-api and howler-ui depend on. Marked as STABLE at 10:38. Includes `userId`, `email`, `role`, `orgId`, `sessionToken`, and `expiresAt`.

4. **Layout modification** (`src/app/layout.tsx`): Added `<ClerkProvider>` as the outermost wrapper, above the existing `<ThemeProvider>`. This ensures auth context is available everywhere.

## Decisions Made

- **Clerk over raw JWT**: Using Clerk's managed auth instead of manual JWT validation. Trades vendor lock-in for correctness on token refresh, session revocation, and edge cases.
- **Decoupled session type**: `getSession()` returns a plain `UserSession` object, not Clerk's native session type. If we switch auth providers, only `session.ts` changes -- not every consumer.
- **Middleware matcher pattern**: Public routes are defined in Next.js middleware config (`config.matcher`) rather than runtime checks. More performant and fails-closed (new routes are protected by default).
