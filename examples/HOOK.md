# Hook: Implement Clerk authentication

Spectrum: auth-refactor-0329
Howler: howler-auth
Branch: spectrum/auth-refactor-0329/howler-auth
Worktree: ~/.claude/spectrum/auth-refactor-0329/worktrees/howler-auth
Started: 2026-03-29T10:22:00Z
Updated: 2026-03-29T11:05:00Z
Status: complete
git_status: ok
Confidence: high
Confidence-Note: All postconditions verified. Clerk integration is straightforward.

## Task

Implement Clerk authentication middleware, session management, and protected route wrappers. Create the UserSession type that other Howlers depend on.

## File Ownership

CREATES: src/middleware/auth.ts, src/lib/session.ts, src/types/auth.ts
MODIFIES: src/app/layout.tsx

## Checkpoints

- types: STABLE (marked at 10:38 -- UserSession interface finalized and exported)

## Progress

- [x] Write HOOK.md
- [x] Read CONTRACT.md and verify preconditions
- [x] Create src/types/auth.ts with UserSession interface
- [x] Mark types checkpoint STABLE
- [x] Create src/middleware/auth.ts with authMiddleware
- [x] Create src/lib/session.ts with getSession()
- [x] Modify src/app/layout.tsx to wrap in ClerkProvider
- [x] Verify all postconditions
- [x] Alignment check (20 tool calls): on-track
- [x] Completion verification

## Decisions

- Used Clerk's `auth()` helper from `@clerk/nextjs/server` instead of raw JWT validation. Rationale: Clerk handles token refresh, session revocation, and edge cases. Raw JWT would duplicate this.
- Public routes defined as a matcher array in middleware config rather than a runtime check. Rationale: Next.js middleware config.matcher is more performant and explicit.
- getSession() returns a plain object (not the Clerk session object) to decouple downstream code from Clerk's SDK types.

## Seams

- howler-api depends on UserSession type from src/types/auth.ts (checkpoint: STABLE)
- howler-ui depends on UserSession type from src/types/auth.ts (checkpoint: STABLE)
- howler-ui depends on ClerkProvider being in layout.tsx (verified: added)

## Cross-Domain Observations

- The existing layout.tsx has a `<ThemeProvider>` wrapper. ClerkProvider was added outside ThemeProvider to ensure auth context is available to themed components. howler-ui should be aware of this nesting order.
- There is no `src/app/api/health/route.ts` yet -- it's in the public routes list but doesn't exist. howler-api may want to create it.

## Completion Verification

- [x] All CREATES files exist:
  - src/types/auth.ts: exists (ls confirmed)
  - src/middleware/auth.ts: exists (ls confirmed)
  - src/lib/session.ts: exists (ls confirmed)
- [x] All MODIFIES files changed:
  - src/app/layout.tsx: modified (git diff --name-only confirmed)
- [x] Type check passes: tsc --noEmit: 0 errors
- [x] Tests pass on owned files: N/A (tests are howler-tests responsibility)

## Blockers

- (none)

## Errors Encountered

- (none)
