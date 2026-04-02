# Tutorial: Your First Spectrum Run

This walks you through a real Spectrum run in ~20 minutes. You'll build an authentication system with 3 parallel Howlers.

---

## Prerequisites

- Spectrum installed ([INSTALL.md](INSTALL.md))
- A Next.js or similar project open in Claude Code
- ~$5 in Claude API credits

---

## Invocation Examples

Here are concrete prompts you can type in Claude Code to trigger each mode:

| What you type | What it triggers |
|---|---|
| `"Write a plan for the auth system."` | Blue only → PLAN.md (no spectrum) |
| `"Build the auth system, API, and dashboard in parallel."` | Full spectrum: Blue → Gold → 3 Howlers |
| `"Run this in parallel."` | Spectrum with existing PLAN.md |
| `"Drop howlers for auth, API, and dashboard."` | Spectrum (Gold skips Blue, uses existing PLAN.md) |
| `"Plan and build these 3 features. Keep it lean."` | Reaping mode (3-4 Howlers, pure-create only) |
| `"Why is the auth test failing?"` | Orange only (no spectrum) |
| `"Review my changes."` | White only (no spectrum) |

Spectrum activates automatically when Gold detects 3+ independent features and PLAN.md exists. You can always ask Blue to write a plan first before kicking off a spectrum run.

---

## Step 1: Tell Claude Code What to Build

Type this (or something like it) in Claude Code:

```
Build the auth system, user API, and dashboard UI in parallel.
```

Spectrum activates automatically when it detects 3+ independent features.

---

## Step 2: Blues Plans (automatic)

Blues (the planner) scopes the work into a `PLAN.md`:

```
PLAN.md written:
- Auth middleware + session types (auth)
- User/org API routes (api)
- Dashboard shell + header (ui)
3 independent tracks identified. Recommending Spectrum.
```

You'll see the plan and can adjust before Gold takes over.

---

## Step 3: Muster (Gold plans the Spectrum)

Gold reads the plan and produces two artifacts:

**MANIFEST.md** — who does what, touching which files:
```
| Howler       | Scope                    | Creates                    | Modifies         |
|--------------|--------------------------|----------------------------|------------------|
| howler-auth  | Clerk middleware + types  | src/types/auth.ts          | src/app/layout.tsx|
|              |                          | src/middleware/auth.ts      |                  |
| howler-api   | User and org routes      | src/api/users.ts           |                  |
|              |                          | src/api/orgs.ts            |                  |
| howler-ui    | Dashboard + header       | src/components/Dashboard.tsx|                  |
|              |                          | src/components/Header.tsx  | src/app/page.tsx |

CONFLICTS: none (every file appears exactly once)
```

**CONTRACT.md** — shared types and rules:
```
Shared Types:
  UserSession { userId: string; orgId: string; role: 'admin' | 'member' }

Conventions:
  All API routes use auth() for session access
  All new components use named exports
  Error responses follow { error: string; code: number }
```

Gold presents both and asks:

> "Here is the manifest for 3 Howlers. File ownership verified, no conflicts. Drop the Howlers?"

---

## Step 4: You Approve

Type:

```
Yes
```

That's it. Gold pre-creates worktrees and drops all 3 Howlers in parallel.

---

## Step 5: The Drop (Howlers work in parallel)

You'll see status updates as each Howler works:

```
  >> howler-auth   — Writing HOOK.md... implementing Clerk middleware...
  >> howler-api    — Writing HOOK.md... creating user routes...
  >> howler-ui     — Writing HOOK.md... building Dashboard component...
```

Each Howler:
1. Writes HOOK.md immediately (crash recovery state)
2. Implements only the files in its ownership matrix
3. Checks scope alignment every 20 tool calls
4. Runs completion verification (files exist, types check, tests pass)
5. Runs the triple quality gate (White + Gray + security review)
6. Opens a PR via Copper

**You don't need to do anything during this phase.** The Howlers work autonomously within their boundaries.

---

## Step 6: Pax (Gold Integrates)

After all Howlers finish, Gold:

1. Reads all 3 debriefs
2. Independently validates each Howler's work against the contract
3. Cross-references seams (howler-auth created types → howler-api imports them)
4. Writes PAX-PLAN.md with merge order

You'll see:

```
PAX-PLAN.md:
  Merge order:
    1. howler-auth (PR #1) — no dependencies, merge first
    2. howler-api  (PR #2) — depends on auth types
    3. howler-ui   (PR #3) — depends on auth types

  Seam check: 2/2 seams confirmed
  Independent validation: all postconditions met
  Conflicts: none
```

---

## Step 7: Triumph (You Merge)

Gold presents the merge plan. You merge each PR in order:

1. Merge PR #1 (howler-auth) → Gray runs tests → pass
2. Merge PR #2 (howler-api) → Gray runs tests → pass
3. Merge PR #3 (howler-ui) → Gray runs tests → pass

Then Obsidian verifies the merged result against the original PLAN.md:

```
SENTINEL-REPORT.md:
  Auth middleware: PASS
  User API routes: PASS
  Dashboard UI: PASS
  Overall: COMPLIANT
```

Brown captures lessons learned. Gold cleans up the spectrum directory.

**Done.** Three features built in parallel, merged cleanly, verified against spec.

---

## What Just Happened

```
You typed one sentence
  → Blue planned 3 features
    → Gold decomposed into 3 Howlers with file ownership
      → Politico challenged the plan (The Passage)
        → 3 Howlers built in parallel (The Drop)
          → White + Gray + security reviewed each (The Proving)
            → Gold validated and planned the merge (Pax)
              → You merged 3 PRs (Triumph)
                → Obsidian verified spec compliance
                  → Brown captured lessons for next time
```

Total time: ~15-25 minutes (vs 2-3 hours sequential).

---

## Common Variations

### Reaping Mode (smaller runs)

For 3-4 Howlers that only create new files:

```
Light spectrum — build these 3 things in parallel
```

Gold uses Reaping Mode: ~3 minutes of muster instead of ~8. Same quality gates.

### When a Howler Gets Stuck

If a Howler hits a blocker, it sets `Status: blocked` in HOOK.md and stops. Gold classifies the failure (transient? logical? structural?) and presents recovery options:

- **Resume** — new Howler continues from the HOOK.md checkpoint
- **Retry** — fresh Howler with the original task
- **Skip** — defer this feature as a follow-up
- **Restructure** — re-plan with different decomposition

### Adjusting the Plan

Before approving the manifest, you can say:

```
Move the header component from howler-ui to howler-auth
```

or:

```
Add a fourth Howler for the test suite
```

Gold will update the manifest and re-verify file ownership before dropping.

---

## Next Steps

- Read the [Feature Highlights](README.md#feature-highlights) for deeper explanations
- Browse the [examples/](examples/) directory for sample artifacts
- See [SPECTRUM-OPS.md](spectrum/SPECTRUM-OPS.md) for the full operator's manual
- Check [evaluation/](evaluation/) for how Spectrum compares to other systems
