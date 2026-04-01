# PLAN: Agent Visibility — Gold-Spawned Quality Gates

**Status**: Draft  
**Author**: Blues  
**Date**: 2026-03-31  
**Target files**:
- `spectrum/SPECTRUM-OPS.md` — Howler Drop Template, Phase 2 quality gate section, Phase 6 section
- `spectrum/CLAUDE.md` — Pre-PR Quality Gates section, Phase 6 Triumph section, Global Behavior Rules

---

## Problem

Quality gate agents (White, Gray, Orange, Copper, Obsidian, Brown) exist as documentation but are invisible at runtime. The current Howler Drop Template instructs Howlers to "run White + Gray + /diff-review in parallel" (step 11), but Howlers are sub-agents running in isolated worktrees — they cannot spawn visible sub-sub-agents. The result is one of two failure modes:

1. **Self-review**: Howlers perform their own code review and call it "White." No independent perspective.
2. **Skip**: Howlers declare done without running the gate at all.

10 of 14 named agents are currently invisible in the terminal agent tree. The status roster (a mandatory Gold output) lists them, but they never actually appear as spawned background agents with their own conversation threads.

---

## Solution

Restructure quality gate ownership: Howlers implement only. Gold spawns quality gate agents.

**Before**: Howler → [implement] → [White] → [Gray] → [/diff-review] → [Copper] → done  
**After**: Howler → [implement] → [write debrief] → return to Gold → Gold spawns White, Gray, /diff-review → Gold dispatches Copper

This makes all named agents appear in the terminal agent tree with their role glyphs, gives each agent a distinct visible conversation thread, and maintains the same quality standard while moving ownership to the only agent capable of spawning visible peers.

---

## Acceptance Criteria

1. Howler Drop Template steps 11-14 are removed; Howler's final step is writing the debrief and signaling completion
2. Gold post-Howler protocol explicitly spawns White, Gray, and /diff-review as separate background agents with named descriptions
3. Gold dispatches Copper only after all three gates pass
4. Phase 6 Triumph section shows Obsidian and Brown spawned as visible agents by Gold
5. CLAUDE.md Pre-PR Quality Gates section updated to describe Gold as the spawner (not Howlers)
6. CLAUDE.md Phase 6 updated to match
7. Status roster format updated to show per-Howler gate agents with individual entries
8. Reaping and Nano mode exceptions preserved (Nano still skips quality gates entirely)

---

## File Inventory

### Files Modified

| File | Section | Change |
|------|---------|--------|
| `spectrum/SPECTRUM-OPS.md` | Howler Drop Template (steps 11-14) | Remove gate steps; add "return to Gold" step |
| `spectrum/SPECTRUM-OPS.md` | Phase 2: The Drop — Quality Gate section | Replace Howler-runs-gate with Gold-spawns-gate protocol |
| `spectrum/SPECTRUM-OPS.md` | Phase 6: Triumph | Add explicit Gold spawns Obsidian + Brown as background agents |
| `spectrum/SPECTRUM-OPS.md` | Status Roster format | Add per-Howler gate agent rows with individual status |
| `spectrum/CLAUDE.md` | Pre-PR Quality Gates | Update to describe Gold as spawner |
| `spectrum/CLAUDE.md` | Phase 6 — Triumph | Update to show Gold spawning Obsidian + Brown |
| `spectrum/CLAUDE.md` | Global Behavior Rules — "Triple quality gate" | Clarify Gold (not Howler) runs triple gate |

### Files Created

None.

---

## Decomposition

### H1 — Rewrite Howler Drop Template

**Scope**: Modify steps 11-14 of the Howler Drop Template in SPECTRUM-OPS.md.

**CREATES**: nothing  
**MODIFIES**: `spectrum/SPECTRUM-OPS.md` (Howler Drop Template block, lines ~535-549)

**What changes**:

Remove steps 11-14:
```
11. When verified: run White + Gray + /diff-review in parallel (triple gate).
    Security criticals from /diff-review block the PR. High/medium = warning.
12. Fix blockers. If blockers fixed, re-run White before proceeding.
    (Max 2 Orange retries, then Status: blocked).
13. Write debrief to ~/.claude/spectrum/{rain-id}/{howler-name}.md
14. Open PR via Copper targeting main.
```

Replace with:
```
11. Write debrief to ~/.claude/spectrum/{rain-id}/{howler-name}.md
    (Use the Debrief YAML Frontmatter template. Include open_exits and warnings.)
12. Signal completion: set Status: complete in HOOK.md. Your job ends here.
    Gold will spawn White, Gray, and /diff-review — do not run these yourself.
    Do not open a PR. Gold coordinates Copper after the gates pass.
```

Also update the revision pass note at the end of step 10 — change "proceed to quality gates" to "proceed to debrief — Gold will run quality gates":

```
Maximum 2 revision passes. If tests still fail after 2 passes, document the
failures in HOOK.md and proceed to debrief — Gold will run the quality gate
and surface these failures to White and Gray with full context.
```

**Effort**: S  
**Serial risk**: no (this is a text edit to a template; no seam with other Howlers)

---

### H2 — Add Gold Post-Howler Dispatch Protocol

**Scope**: Add a new subsection to Phase 2: The Drop in SPECTRUM-OPS.md documenting Gold's post-Howler quality gate dispatch. Also update the "Quality Gate (per Howler)" subsection to reflect Gold as the actor.

**CREATES**: nothing  
**MODIFIES**: `spectrum/SPECTRUM-OPS.md` (Phase 2 section, quality gate subsection, lines ~635-646)

**What changes**:

Replace the existing "Quality Gate (per Howler)" subsection with a new "Gold Post-Howler Protocol" subsection:

```markdown
### Gold Post-Howler Protocol

When a Howler sets `Status: complete` in HOOK.md:

1. **Read** the Howler's debrief and HOOK.md — note any open_exits, warnings, or blockers.
2. **Spawn all three quality gate agents in parallel** (one message, three background agents):

   ```
   Agent(run_in_background=True, model="sonnet",
     description="✦ Whites — reviewing {howler-name}",
     prompt="Review the diff for branch spectrum/{rain-id}/{howler-name}. ...")

   Agent(run_in_background=True, model="sonnet",
     description="⛨ Grays — testing {howler-name}",
     prompt="Run tests for branch spectrum/{rain-id}/{howler-name}. ...")

   /diff-review on branch spectrum/{rain-id}/{howler-name}
   ```

3. **Wait** for all three to complete.
4. **If any gate has blockers**:
   - Security criticals from /diff-review: block PR, surface to human.
   - White blockers: spawn Orange for diagnosis (max 2 retries), then have Howler resume via HOOK.md.
   - Gray failures: spawn Orange for diagnosis (max 2 retries), then have Howler resume.
   - If White re-runs after fixes: re-run White before dispatching Copper.
5. **If all gates pass**: spawn Copper as a visible background agent:

   ```
   Agent(run_in_background=True, model="haiku",
     description="▶ Coppers — PR for {howler-name}",
     prompt="Open a PR for branch spectrum/{rain-id}/{howler-name} targeting main. ...")
   ```

6. **Update status roster** — mark White, Gray, /diff-review, and Copper with their outcomes.

**Per-Howler gate triggering**: Quality gates trigger immediately when each Howler declares
completion — do not wait for all Howlers to finish. On a 4-Howler run with staggered
completion, this reclaims 8-15 minutes.
```

**Also update** the Status Roster format to show per-Howler gate agents as separate rows:

```
  ✦ Whites/howler-auth  Reviewer  ● running   (auth middleware diff)
  ⛨ Grays/howler-auth   Tester    ○ queued
  ▶ Coppers/howler-auth Delivery  ○ queued
```

**Effort**: M  
**Serial risk**: no

---

### H3 — Add Gold Phase 6 Dispatch (Obsidian + Brown)

**Scope**: Update Phase 6: Triumph in SPECTRUM-OPS.md to show Gold explicitly spawning Obsidian and Brown as visible background agents, not as implied tasks.

**CREATES**: nothing  
**MODIFIES**: `spectrum/SPECTRUM-OPS.md` (Phase 6 section, lines ~739-759)

**What changes**:

Replace steps 3-4 of Phase 6 with explicit spawn language:

```markdown
3. **Spawn Obsidian** as a visible background agent:
   ```
   Agent(run_in_background=True, model="sonnet",
     description="⊘ Obsidians — spec compliance",
     prompt="Read PLAN.md and DESIGN.md (if present) for Spectrum {rain-id}.
     Verify each acceptance criterion against the merged codebase.
     Write SENTINEL-REPORT.md to ~/.claude/spectrum/{rain-id}/.")
   ```
   - COMPLIANT → proceed. PARTIAL/NON-COMPLIANT → present to human before continuing.

4. **Spawn Brown** as a visible background agent after Obsidian completes:
   ```
   Agent(run_in_background=True, model="haiku",
     description="⌂ Browns — lessons learned",
     prompt="Draft LESSONS.md + ENTITIES.md updates from Spectrum {rain-id} artifacts.
     Write LESSONS-DRAFT.md. Include a ## Known Failure Patterns section. ...")
   ```
   Gold reviews the draft before committing.
```

**Effort**: S  
**Serial risk**: no

---

### H4 — Update CLAUDE.md to Match

**Scope**: Update CLAUDE.md sections that describe quality gates and Phase 6 so they match the SPECTRUM-OPS.md changes.

**CREATES**: nothing  
**MODIFIES**: `spectrum/CLAUDE.md` (three sections: Pre-PR Quality Gates, Phase 6 Triumph, Global Behavior Rules)

**What changes**:

**Pre-PR Quality Gates section** — add one sentence clarifying who spawns:

```
Before Copper opens a PR/MR, Gold spawns all three quality gate agents in parallel:
```
(was: "Before Copper opens a PR/MR, run all three in parallel:")

**Phase 2 — The Drop, quality gate paragraph** — change "every Howler runs ALL THREE" to "Gold spawns ALL THREE per Howler":

```
**Quality gate (per Howler, coordinated by Gold)**: When a Howler signals completion,
Gold spawns all three in parallel:
```

**Phase 6 — Triumph** — steps 3 and 4 already say "Run Obsidian" and "Run Brown" — add spawn language to make explicit:

```
3. **Spawn Obsidian** as visible background agent — verifies PLAN.md (+ DESIGN.md) acceptance criteria → SENTINEL-REPORT.md
4. **Spawn Brown** as visible background agent — drafts LESSONS.md + ENTITIES.md updates → Gold reviews and commits.
```

**Global Behavior Rules — "Triple quality gate" rule** — add "(Gold spawns, not Howler)":

```
- **Triple quality gate**: Gold spawns White + Gray + /diff-review in parallel per Howler after completion (security criticals block)
```

**Effort**: S  
**Serial risk**: no

---

## DAG

```yaml
- id: H1
  deps: []
  description: Rewrite Howler Drop Template (remove steps 11-14, add debrief+signal step)

- id: H2
  deps: []
  description: Add Gold post-Howler dispatch protocol and update quality gate subsection

- id: H3
  deps: []
  description: Add Gold Phase 6 dispatch (Obsidian + Brown as visible agents)

- id: H4
  deps: [H1, H2, H3]
  description: Update CLAUDE.md to match — must apply after OPS changes are settled
```

H1, H2, H3 are fully parallel. H4 depends on all three because it mirrors language from the OPS file and should be written last to stay consistent.

---

## Key Design Decisions

### Why Gold spawns, not Howlers

The Agent tool's `description` parameter determines what label appears in the terminal agent tree. When a Howler spawns a sub-agent, that agent appears nested inside the Howler's thread and labeled as a sub-sub-agent. Howlers run in isolated worktrees as background agents themselves — they cannot produce top-level visible peers. Gold runs at the top level and can spawn named, visible, parallel agents that appear in the same tier as Howlers.

### Why the debrief moves to step 11 (before signal)

The debrief captures what the Howler built, decisions made, and open exits. If the Howler signals completion but dies before writing the debrief, Gold has no context to give White and Gray. Making debrief step 11 (write first, signal second) ensures Gold always has Howler context before spawning gate agents.

### Nano mode exception preserved

Nano mode explicitly skips White + Gray + /diff-review. This remains unchanged — Gold does not spawn gate agents for nano runs. The change only affects full mode and reaping mode. Reaping mode currently says "White + Gray + /diff-review" as a Howler responsibility; after this change, it becomes a Gold responsibility, but the requirement is preserved.

### Orange still available for gate failures

When White or Gray returns blockers, Gold's next action is to spawn Orange for diagnosis (max 2 retries), then have the Howler resume via its HOOK.md. This is consistent with Phase 3 (The Forge) logic. The only change is that the trigger is now Gold reading gate results rather than Howler reading gate results.

### Status roster impact

The per-Howler gate agents should appear as separate rows in the status roster, labeled by Howler context (e.g., "Whites/howler-auth"). This makes each gate agent's status independently trackable. The H2 change adds the format guidance for this.

---

## Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Gold prompt token cost increases (reads all Howler debriefs before spawning gates) | Low | Debriefs are already ~500 tokens; Gold reads them in Pax anyway |
| Howlers that currently self-report quality gates as "passed" will stop doing so, surfacing previously hidden failures | Medium — this is a feature, not a bug | Document in LESSONS.md as expected behavior change |
| Orange retry logic needs to reference the Howler's HOOK.md, which is in a worktree path Gold must know | Low | Gold already tracks worktree paths in CHECKPOINT.json |
| Reaping mode "Keeps: White + Gray + /diff-review" language may be read as "Howler still runs these" post-change | Low | H4 makes the CLAUDE.md reaping mode note explicit: Gold spawns, mode just determines which runs |

---

## Out of Scope

- Changing the content or evaluation criteria of White, Gray, or /diff-review prompts
- Changing Copper's PR creation behavior
- Changing the Obsidian or Brown prompt content
- Nano mode quality gate behavior (explicitly preserved as-is)
- Agent Teams / TeammateTool integration (separate future work)
- The SWE-bench and Multi-Candidate mode quality gate flow (single-Howler; Gold already coordinates directly)
