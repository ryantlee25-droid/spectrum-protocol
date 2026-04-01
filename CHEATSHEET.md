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

## Agents & Colors

Each agent displays with a background color highlight in Claude Code's terminal UI.
Shared colors are between agents that never run concurrently.

```
Agent      Glyph  Color     Model    Role
─────────  ─────  ────────  ───────  ─────────────────────────────────
Golds      ♛      yellow    Opus     Commands the spectrum
Blues       ◎      blue      Sonnet   Plans work → PLAN.md
Howlers    »      orange    Sonnet   Builds in parallel worktrees
Whites     ✦      purple    Sonnet   Reviews code before PR
Grays      ⛨      gray      Sonnet   Runs tests + coverage
Oranges    ✧      red       Sonnet   Debugs root causes
Coppers    ▶      cyan      Haiku    Commits, branches, PRs
Obsidians  ⊘      teal      Sonnet   Verifies spec after merge
Browns     ⌂      overlay   Haiku    Records lessons learned
Violets    ~      pink      Sonnet   Designs API/schema specs
Politicos  ⚡      red       Sonnet   Challenges plans before freeze
─────────  ─────  ────────  ───────  ─────────────────────────────────
Helldivers ◈      yellow    Sonnet   Problem research (auxiliary)
Primus     ⊕      green     Sonnet   Product strategy (auxiliary)
Greens     ≡      green     Sonnet   Breaks specs into tickets (auxiliary)
```

Shared colors: Oranges/Politicos (red) — Phase 4 vs 1.5.
Golds/Helldivers (yellow) — pipeline vs auxiliary.
Greens/Primus (green) — both auxiliary.

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
