# Spectrum Cheat Sheet

## Start a Spectrum

```
"Build X, Y, and Z in parallel."          → Full Spectrum (3-8 Howlers)
"Light spectrum — build these 3 things."   → Reaping Mode (~3 min muster)
```

## Phases

```
Muster        Gold plans, writes manifest + contract
The Passage   Politico challenges the plan
The Drop      Howlers deploy to worktrees
The Proving   White + Gray + security review per Howler
The Forge     Failed Howlers diagnosed + recovered
Pax           Gold validates, cross-references, writes merge plan
Triumph       Human merges, Obsidian verifies spec compliance
```

## Agents

```
Gold      ♛  Commands the spectrum          (Opus)
Blue      ◎  Plans work → PLAN.md           (Sonnet)
Howler    »  Builds in parallel worktrees   (Sonnet)
White     ✦  Reviews code before PR         (Sonnet)
Gray      ⛨  Runs tests + coverage          (Sonnet)
Orange    ✧  Debugs root causes             (Sonnet)
Copper    ▶  Commits, branches, PRs         (Haiku)
Obsidian  ⊘  Verifies spec after merge      (Sonnet)
Brown     ⌂  Records lessons learned        (Haiku)
Violet    ~  Designs API/schema specs       (Sonnet)
Politico  ⚡  Challenges plans before freeze (Sonnet)
```

## Key Artifacts

```
MANIFEST.md      Who does what, which files, DAG
CONTRACT.md      Shared types, conventions, DbC (frozen at drop)
HOOK.md          Per-Howler crash recovery state
debrief.md       Per-Howler completion report (YAML frontmatter)
CHECKPOINT.json  Convoy-wide state (resume from any point)
PAX-PLAN.md      Merge order + seam check results
```

## Approve / Adjust

```
"Yes"                                → Drop the Howlers
"Move X from howler-a to howler-b"   → Gold adjusts manifest
"Add a fourth Howler for tests"      → Gold re-plans
"Skip howler-c"                      → Gold marks skipped
```

## When Things Break

```
transient     → Gold auto-resumes
logical       → Orange diagnoses → Resume or Retry
structural    → Gold re-plans from scratch
environmental → Pause all, fix env, resume
conflict      → Freeze and escalate to human
```

2 failures on same file → auto-escalate to structural (circuit breaker)

## File Ownership Rules

```
Every CREATES/MODIFIES file → exactly one Howler
No overlaps → ever
Howler touches file outside its list → STOP, log drift
Gold restructures if conflict detected
```
