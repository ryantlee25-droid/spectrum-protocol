# Tutorial: Your First Spectrum Run

Build 3 features in parallel in ~15 minutes.

---

## Prerequisites

- Spectrum installed ([INSTALL.md](INSTALL.md))
- A project open in Claude Code
- ~$3 in Claude API credits

---

## Step 1: Tell Claude Code What to Build

```
Build the auth system, user API, and dashboard UI in parallel.
```

Spectrum activates when it detects 3+ independent features.

---

## Step 2: Blue Plans (automatic)

Blue scopes the work into `PLAN.md`:

```
PLAN.md written:
- Auth middleware + session types
- User/org API routes
- Dashboard shell + header
3 independent tasks. Recommending Spectrum.
```

---

## Step 3: Gold Splits

Gold reads PLAN.md and writes **SPLIT.md** — the only artifact:

```markdown
# SPLIT.md

| Worker       | Scope                  | Creates                     | Modifies          |
|-------------|------------------------|-----------------------------|--------------------|
| worker-auth | Clerk middleware       | src/middleware/auth.ts       | src/app/layout.tsx |
| worker-api  | User + org routes      | src/api/users.ts, orgs.ts   |                    |
| worker-ui   | Dashboard + header     | src/components/Dashboard.tsx | src/app/page.tsx   |

CONFLICTS: none
```

Gold asks: *"3 workers, no file conflicts. Drop?"*

---

## Step 4: You Approve

```
Yes
```

Gold creates worktrees and drops all 3 workers in parallel.

---

## Step 5: Workers Build in Parallel

```
» worker-auth  ● implementing auth middleware...
» worker-api   ● creating API routes...
» worker-ui    ● building dashboard...
```

Each worker:
1. Reads its task and file ownership
2. Implements only files in its list
3. Commits when done

**You don't need to do anything.** Workers are autonomous within their boundaries.

---

## Step 6: Gold Merges + Verifies

As workers finish, Gold merges each branch:

```
worker-ui   finished (6 min) → merged ✓
worker-auth finished (8 min) → merged ✓
worker-api  finished (7 min) → merged ✓

Running verification on merged result...
  tsc --noEmit  ✓
  vitest run    ✓
  White review  ✓ (0 blockers)

Copper → PR opened
```

**Done.** Three features built in parallel, merged cleanly, verified once.

---

## What Just Happened

```
You typed one sentence
  → Blue planned 3 features
    → Gold split into 3 workers with file ownership
      → 3 workers built in parallel
        → Gold merged all branches
          → White + Gray verified the merged result (once)
            → Copper opened the PR
```

Total time: ~13 minutes (workers ran in parallel).
Single-agent: ~25 minutes.

---

## Common Variations

### When a Worker Gets Stuck

Worker hits an error → Gold sends Orange to diagnose (max 2 retries). If 2 retries fail, that task goes single-agent as a follow-up.

### Adjusting the Split

Before approving:

```
Move the header from worker-ui to worker-auth
```

or:

```
Add a fourth worker for the test suite
```

Gold updates SPLIT.md and re-verifies file ownership.

### With Memory (Tages)

If you have [Tages](https://github.com/ryantlee25-droid/tages) set up, Gold includes a memory brief in each worker's drop prompt. Benchmark result: -25% time, -10% tokens vs no memory.

---

## Invocation Examples

| What you type | What happens |
|---|---|
| `"Write a plan for the auth system."` | Blue only → PLAN.md |
| `"Build auth, API, and dashboard in parallel."` | Full spectrum: Blue → Gold → 3 workers |
| `"Run this in parallel."` | Spectrum with existing PLAN.md |
| `"Drop workers for these 3 features."` | Spectrum (assumes PLAN.md exists) |
| `"Why is the auth test failing?"` | Orange only (no spectrum) |
| `"Review my changes."` | White only (no spectrum) |

---

## Next Steps

- [Cheat Sheet](CHEATSHEET.md) — quick reference card
- [Full Spec](spectrum/SPECTRUM.md) — complete protocol details
- [README](README.md) — benchmarks, techniques, memory integration
