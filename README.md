# Spectrum Protocol v6

**Fast parallel execution for Claude Code.**

Split tasks. Drop workers. Merge branches. Verify once. Ship.

No dependencies. No build step. No ceremony. Copy two files and you're running.

---

## Why v6

v5 had 4,100 lines of protocol spec across 7 phases, 14 agents, frozen contracts, adversarial reviews, per-worker quality gates, and crash recovery journals. It was an engineering achievement.

It was also slower and more expensive than a single Sonnet agent on every benchmark we ran.

**v6 keeps what works** (planning, worktree isolation, file ownership, post-merge verification) **and cuts everything that doesn't** (contracts, manifestos, per-worker gates, phase ceremonies, crash journals).

The result: **~25 min and ~100k tokens** vs v5's ~45 min and ~240k tokens. Same quality.

---

## Agent Roster

| Agent | Model | What They Do |
|-------|-------|-------------|
| **Gold** | Sonnet | Splits tasks, drops workers, merges branches, runs verification |
| **Blue** | Sonnet | Scopes work, produces PLAN.md (before spectrum) |
| **Workers** | Sonnet | Implement tasks in isolated worktrees (parallel) |
| **White** | Sonnet | Reviews merged diff — tiered verification, loop-aware analysis, INQUIRY format |
| **Gray** | Sonnet | Runs tests + generates missing tests — batch-generate-validate loops |
| **Orange** | Sonnet | Root cause debugging — minimize-then-localize, causal chains, scope boundaries |
| **Copper** | Sonnet | Commits, branches, PRs — file sensitivity filtering, evidence-before-claims |

7 agents. Each earns its keep. Each has been benchmarked head-to-head against vanilla Claude.

Auxiliary agents (not part of spectrum): **Helldivers** (research), **Primus** (strategy), **Greens** (ticket decomposition).

---

## v6.1: Agent Specialist Improvements

Every agent now includes prompt engineering techniques drawn from research on CodeRabbit, Qodo Cover, Sentry Seer, SWE-agent, Graphite, and the Claude Code superpowers/pr-review-toolkit/Trail of Bits plugins. Validated across two benchmark rounds (TypeScript MUD + Go email server).

### Techniques Applied

| Technique | What It Does | Which Agents |
|-----------|-------------|-------------|
| **Iron Laws** | Absolute rules preventing phase-skipping | All |
| **Rationalization Tables** | Pre-debunked excuses for shortcutting | All |
| **Red Flag Lists** | Behavioral tripwires for self-monitoring | All |
| **Tiered Verification** | Reasoning certificates (no tool call) for WARNINGs, batched scripts for BLOCKERs | White |
| **Verification Budget** | MAX_VERIFICATION_CALLS = 15 with batch fallback | White |
| **Loop-Aware Analysis** | Explicit check for repeated side effects in loops | White |
| **INQUIRY Format** | Inconclusive findings → questions, not assertions | White |
| **Batch-Generate-Validate** | Generate 3-5 tests per call, validate all, retry only failures | Gray |
| **Failed Test Accumulator** | Prevents re-generating the same broken test patterns | Gray |
| **Style Template Extraction** | Read existing tests once, reuse pattern for all generated tests | Gray |
| **Minimize-Then-Localize** | Find minimal reproduction before reasoning about root cause | Orange |
| **Causal Chain Construction** | Symptom ← Cause ← Condition ← Root Decision | Orange |
| **Scope Boundaries** | Orange runs specific test only; full suite is Gray's job | Orange |
| **File Sensitivity Filter** | Warn before staging research docs, env files, credentials | Copper |
| **Evidence-Before-Claims** | Verify every state-changing operation before reporting success | Copper |
| **Freshness Gate** | Verify plan references against current code before execution | Blue |
| **Hard Scope Gate** | Resolve ambiguities before task decomposition | Blue |

### Benchmark Results

**TypeScript benchmark** (The Remnant MUD, 109 files, 50k LOC):

| Task | Agent vs Vanilla | Result |
|------|-----------------|--------|
| Code review | White v3 vs Claude | Tie on bug detection, White has better evidence quality |
| Debugging | Orange vs Claude | Both found root cause; Orange wrote regression test |
| Test generation | Gray v3 vs Claude | Gray: 90 tests vs 63, coverage report, 33% faster |
| Planning | Blue vs Claude | Blue: structured plan in 2 min; vanilla: full impl in 33 min |

**Go benchmark** (mailpit, 89 files, 15k LOC):

| Task | Agent vs Vanilla | Result |
|------|-----------------|--------|
| Code review (3 seeded bugs) | White: 2/3, Vanilla: 3/3 | Vanilla won — White missed loop bug (now fixed) |
| Debugging (timezone clobber) | Both found root cause | Orange won — wrote regression test, stayed in scope |
| Test generation (validators) | Gray: 90 tests, Vanilla: 63 | Gray won — more tests, coverage report, self-fixed 2 bugs |
| Planning (webhook retry) | Blue: plan in 2 min | Blue: better structure, identified file conflict + goroutine leak |

---

## Memory Integration (Optional)

When used with [Tages](https://github.com/ryantlee25-droid/tages) or similar project memory:

- Include a **memory brief** in each worker's drop prompt
- Memory sweet spot: **40-70 memories** per project, focused on patterns not facts
- **Benchmark result** (54 runs, 4 codebases): agents + memory compound for **-25% time, -10% tokens** vs either alone
- Memory helps most when the codebase has **few examples** of the needed pattern
- Stale memories don't poison output — agents cross-check against current code

Without memory, agents still work — memory is an efficiency multiplier, not a dependency.

---

## The Protocol (4 Steps)

### 1. Split (~2 min)

Gold reads PLAN.md and writes **SPLIT.md** — the only ceremony artifact:

```markdown
# SPLIT.md
Rain: auth-feature-0405

## Workers
- worker-auth: "Implement auth middleware" → CREATES: lib/auth.ts, MODIFIES: lib/server.ts
- worker-ui: "Add login form" → CREATES: components/Login.tsx, MODIFIES: app/page.tsx
- worker-tests: "Write auth tests" → CREATES: tests/auth.test.ts (depends: worker-auth)

## Ownership
lib/auth.ts → worker-auth
lib/server.ts → worker-auth
components/Login.tsx → worker-ui
app/page.tsx → worker-ui
tests/auth.test.ts → worker-tests
```

**If Gold can't split without file conflicts: don't use Spectrum.** Run single-agent.

### 2. Drop (~1 min)

Gold creates worktrees and drops workers in parallel:

```bash
git worktree add -b spectrum/<rain>/<worker> \
  .claude/spectrum/<rain>/<worker> HEAD
```

Each worker gets its task, file ownership list, and optionally a memory brief. One rule: **only touch files in your list. Commit when done.**

### 3. Merge (~3 min)

As each worker completes:
1. Merge worker branch to integration branch
2. If merge conflict: Gold resolves (or asks human for complex ones)
3. After all merged: quick type check to verify interfaces match

### 4. Verify (~5 min)

Run everything **once** on the **merged result**:

```bash
tsc --noEmit        # or go vet, mypy
vitest run          # or go test, pytest
```

Optional: White reviews the full merged diff. One review that sees everything > six reviews that each see a fragment.

**Done.** Copper opens the PR.

---

## When to Use Spectrum

All three must be true:
- **3+ genuinely independent tasks** that don't share files
- **PLAN.md exists** (Blue writes this first)
- **Wall-clock speed matters** more than the ~10 min coordination overhead

For everything else: single agent. A single Sonnet session handles ~200k tokens of work reliably.

---

## Failure Handling

- **Worker fails**: Gold drops a replacement with the error context. Max 2 retries.
- **Merge conflict**: Gold resolves trivial ones. Complex ones go to human.
- **Tests fail post-merge**: Orange diagnoses the specific failure. Sequential follow-up.

---

## Quick Start

### One-line install

```bash
curl -fsSL https://raw.githubusercontent.com/ryantlee25-droid/spectrum-protocol/main/install.sh | bash
```

### Or manually

```bash
# Copy protocol files
cp spectrum/CLAUDE.md ~/.claude/CLAUDE.md
cp spectrum/SPECTRUM.md ~/.claude/SPECTRUM.md

# Copy agent definitions
mkdir -p ~/.claude/agents && cp agents/*.md ~/.claude/agents/

# Done.
```

Then tell Claude Code: *"Plan and build the auth system, dashboard, and API layer in parallel."*

**New to Spectrum?** Read the [Tutorial](TUTORIAL.md). Keep the [Cheat Sheet](CHEATSHEET.md) handy.

---

## Repository Structure

```
spectrum-protocol/
├── README.md              # You are here
├── spectrum/
│   ├── CLAUDE.md          # Routing config (copy to ~/.claude/)
│   ├── SPECTRUM.md        # Full v6 spec
│   ├── HOWLER-OPS.md      # Worker ops manual
│   ├── SPECTRUM-OPS.md    # Gold ops manual
│   └── *-V5.md            # Historical v5 files
├── agents/
│   ├── golds.md           # Parallel dispatcher
│   ├── blues.md           # Planner (iron law: read code before planning)
│   ├── howlers.md          # Workers (parallel implementers)
│   ├── whites.md          # Reviewer (tiered verification, loop-aware, INQUIRYs)
│   ├── grays.md           # Tester (batch-generate-validate, style matching)
│   ├── oranges.md         # Debugger (minimize-then-localize, scope boundaries)
│   ├── coppers.md         # Delivery (sensitivity filter, evidence-before-claims)
│   ├── helldivers.md      # Researcher (auxiliary)
│   ├── primus.md          # Strategist (auxiliary)
│   └── greens.md          # Decomposer (auxiliary)
├── tools/                 # Optional tooling
├── install.sh
├── INSTALL.md
├── TUTORIAL.md
├── CHEATSHEET.md
├── UPGRADE.md
└── LICENSE
```

---

## Naming: The Red Rising Theme

Agent names are drawn from Pierce Brown's [Red Rising saga](https://www.piercebrown.com/). Golds command. Workers execute. Whites judge. The theme makes agents instantly recognizable in logs.

---

## Lineage

Built on ideas from [**steveyegge/gastown**](https://github.com/steveyegge/gastown) (persistent state, structured communication). Agent techniques drawn from CodeRabbit (verify-before-commenting), Qodo Cover (generate-run-validate loops), Sentry Seer (minimize-then-localize), SWE-agent (bounded output, verification budgets), Graphite (conservative thresholds), and the superpowers/pr-review-toolkit/Trail of Bits Claude Code plugins (iron laws, rationalization tables, red flag lists).

See [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md) for full credits.

---

## License

[MIT](LICENSE)

## Release Notes

### 2026-04-12 — v6.1: Agent Specialist Improvements

All 7 core agents rewritten with prompt engineering techniques validated across two benchmark rounds (TypeScript + Go):

- **White**: Tiered verification (reasoning certificates + batched tool calls), loop-aware analysis, INQUIRY format for inconclusive findings, MAX_VERIFICATION_CALLS = 15
- **Gray**: Batch-generate-validate (3-5 tests per call), style template extraction, failed test accumulator
- **Orange**: Minimize-then-localize, causal chain construction, scope boundaries (runs specific test only, not full suite)
- **Blue**: Freshness gate, type system audit, hard scope gate, effort calibration with serial task multiplier
- **Copper**: Upgraded from Haiku to Sonnet, file sensitivity filter, auto-branch guard fix, evidence-before-claims
- **Gold**: Simplified to thin dispatcher (SPLIT.md only)
- **Workers**: Simplified to implement-and-commit (no HOOK.md, no debriefs)
- **Memory integration**: Documented Tages coupling — agents + memory compound for -25% time

### 2026-04-04 — v6.0: The Lightweight Overhaul

Complete protocol rewrite based on three head-to-head benchmarks where raw Sonnet beat v5.

- Protocol reduced from 4,100 lines to ~200 lines
- 7 phases → 4 steps (Split → Drop → Merge → Verify)
- 14 agents → 7 agents
- Per-worker quality gates → single post-merge verification
- ~50% faster, ~60% cheaper than v5
