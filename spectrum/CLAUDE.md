# Claude Code — Spectrum Configuration

> Paste this into your project or global CLAUDE.md. Works standalone or with Tages memory for additional efficiency.

---

## Agent Routing

| User says... | Route to |
|---|---|
| "commit my changes" | Copper |
| "open a PR / MR" | Copper |
| "why is this test failing?" | Orange |
| "run the tests" | Gray |
| "review my changes" | White |
| "write a plan for X" | Blue |
| 3+ independent tasks | Gold (parallel dispatch) |

---

## Parallel Execution

**Spec**: `SPECTRUM.md` (~230 lines)

### Activation
- 3+ genuinely independent tasks
- PLAN.md exists (Blue writes this first)
- No file ownership conflicts between tasks

### Protocol (4 steps)
1. **Split** (~2 min) — Gold writes SPLIT.md: task list + file ownership. No contracts.
2. **Drop** (~1 min) — Gold creates worktrees, drops workers in parallel.
3. **Merge** (~3 min) — As each worker completes, merge to integration branch.
4. **Verify** (~5 min) — White + Gray on merged result. Once. Not per-worker.

### Rules
- No file may appear in two workers' ownership lists
- Workers commit to their branch when done — no HOOK.md, no scope checks
- Quality gates run ONCE on merged result, not per-worker
- Max 1 retry per failed worker. Two failures = single-agent for that task.

### Agents

| Agent | Model | What They Do |
|-------|-------|-------------|
| **Gold** | Sonnet | Splits tasks, drops workers, merges, verifies |
| **Blue** | Sonnet | Scopes work → PLAN.md (before spectrum) |
| **Workers** | Sonnet | Implement in isolated worktrees |
| **White** | Sonnet | Reviews merged diff (once, post-merge) — tiered verification |
| **Gray** | Sonnet | Runs tests + generates missing tests — batch-generate-validate |
| **Orange** | Sonnet | Root cause debugging — minimize-then-localize |
| **Copper** | Sonnet | Commits, branches, PRs — with file sensitivity filtering |

Auxiliary: **Helldivers** (research), **Primus** (strategy), **Greens** (ticket decomposition).

---

## Memory Integration (Optional)

When used with [Tages](https://github.com/ryantlee25-droid/tages) or similar project memory:

- Include a **memory brief** in each worker's drop prompt (conventions, patterns, gotchas)
- Memory sweet spot: **40-70 memories** per project, focused on patterns not facts
- Benchmark result: agents + memory compound for **-25% time, -10% tokens** vs either alone
- Memory helps most when the codebase has **few examples** of the needed pattern

Without memory, the agents still work — memory is an efficiency multiplier, not a dependency.

---

## Global Behavior Rules

- **Confirm before destructive git ops**: push, merge, branch delete, force push
- **Never use `git add -A`**: stage files explicitly
- **Never auto-merge a PR/MR**: always require user confirmation
- **Maximum 2 retries per failure**: then surface to user
- **LESSONS.md after every parallel run**: capture what worked and what didn't
