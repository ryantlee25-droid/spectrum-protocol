# Spectrum Cheat Sheet

## Start a Spectrum

```
"Build X, Y, and Z in parallel."   → Gold splits, drops workers, merges, verifies
"Write a plan for X."              → Blue only → PLAN.md (no spectrum)
```

## The Protocol (4 Steps)

```
1. Split     Gold writes SPLIT.md (file ownership matrix)
2. Drop      Workers deploy to worktrees in parallel
3. Merge     Workers merge to integration branch as they finish
4. Verify    White + Gray on merged result, once — Copper opens PR
```

## Agents

```
Agent      Color     Model    Role
─────────  ────────  ───────  ─────────────────────────────────────────
Gold       yellow    Sonnet   Splits tasks, drops workers, merges
Blue       blue      Sonnet   Plans work → PLAN.md
Workers    orange    Sonnet   Implement in parallel worktrees
White      purple    Sonnet   Reviews merged diff (tiered verification)
Gray       gray      Sonnet   Runs tests + generates missing tests
Orange     red       Sonnet   Debugs root causes (minimize-then-localize)
Copper     cyan      Sonnet   Commits, branches, PRs
─────────  ────────  ───────  ─────────────────────────────────────────
Helldivers yellow    Sonnet   Problem research (auxiliary)
Primus     green     Sonnet   Product strategy (auxiliary)
Greens     green     Sonnet   Breaks specs into tickets (auxiliary)
```

## The Only Artifact

```
SPLIT.md    Who does what, which files — the only ceremony artifact
```

That's it. No CONTRACT.md. No MANIFEST.md. No HOOK.md. No CHECKPOINT.json.

## Approve / Adjust

```
"Yes"                               → Drop the workers
"Move X from worker-a to worker-b"  → Gold adjusts SPLIT.md
"Add a fourth worker for tests"     → Gold re-plans
"Skip worker-c"                     → Gold marks skipped
```

## When Things Break

```
Worker fails     → Orange diagnoses, Gold retries (max 2)
Merge conflict   → Gold resolves or asks human
Tests fail       → Orange diagnoses specific failure
2 failures       → Go single-agent for that task
```

## File Ownership Rules

```
Every file → exactly one worker
No overlaps → ever
Worker touches file outside its list → STOP
Gold restructures if conflict detected
Can't split cleanly → don't use Spectrum
```

## Agent Techniques (v6.1)

```
White    Tiered verification (reasoning certs + batched tool calls)
         Loop-aware analysis, INQUIRY format, 15-call budget
Gray     Batch-generate-validate (3-5 tests per call)
         Style template extraction, failed test accumulator
Orange   Minimize-then-localize, causal chains
         Scope boundaries (specific test only, not full suite)
Blue     Freshness gate, type audit, hard scope gate
Copper   File sensitivity filter, evidence-before-claims
```

## Memory Integration (Optional)

```
With Tages:  -25% time, -10% tokens (40-70 memories per project)
Without:     Agents still work — memory is a multiplier, not a dependency
```
