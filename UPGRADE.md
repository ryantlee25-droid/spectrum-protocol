# Upgrading Spectrum Protocol: v4.0 → v5.0

This guide covers everything you need to migrate from Spectrum v4.0 (main) to v5.0 (dev). All breaking changes are listed with their impact. The upgrade itself takes about 2 minutes.

---

## Breaking Changes

### 1. Agent File Renames (Singular → Plural)

All agent definition files have been pluralized. If you have the old singular files in `~/.claude/agents/`, they will coexist with the new plural files and create duplicates — Claude Code will load both, causing duplicate agent definitions.

| v4.0 (main) | v5.0 (dev) |
|-------------|------------|
| `gold.md` | `golds.md` |
| `blue.md` | `blues.md` |
| `white.md` | `whites.md` |
| `gray.md` | `grays.md` |
| `orange.md` | `oranges.md` |
| `copper.md` | `coppers.md` |
| `howler.md` | `howlers.md` |
| `obsidian.md` | `obsidians.md` |
| `brown.md` | `browns.md` |
| `violet.md` | `violets.md` |
| `politico.md` | `politicos.md` |
| `green.md` | `greens.md` |
| `helldiver.md` | `helldivers.md` |
| `primus.md` | `primus.md` *(unchanged)* |

**Action required**: Delete the old singular files before or immediately after copying the new ones. The upgrade steps below handle this.

The `subagent_type` values in all protocol files have also been pluralized (`gold` → `golds`, `obsidian` → `obsidians`, etc.). If you have any custom prompts or scripts that hardcode the old singular `subagent_type` values, update them.

---

### 2. Gold Model Change: Opus → Sonnet

Gold now runs on Sonnet instead of Opus, based on a structured benchmark evaluation (`gold-eval-0331`): 18 scenarios, 12 head-to-head runs across Muster, Pax, and Forge phases.

**Results**: Sonnet scored 0.94 composite vs Opus 1.00, passing all phase thresholds. Cost drops 91% (~$3.50 per spectrum saved).

**The one caveat**: Sonnet over-classifies severity during Pax — it promotes observations to blockers more aggressively than Opus. This means PAX-PLAN.md may list more items as blockers than are strictly warranted.

**Action required**: Review Pax blockers manually before actioning them. The protocol flags this explicitly, but it shifts some triage work to you.

If your `~/.claude/CLAUDE.md` hardcodes `opus` for the Gold model assignment, update it to `sonnet` after copying the new CLAUDE.md.

---

### 3. Phase Numbering Shift

"The Proving" (Phase 3 on main) has been absorbed into Phase 2 (The Drop). Quality gates are no longer a standalone phase — Gold spawns them as visible background agents immediately after each Howler signals completion.

| v4.0 Phase | v5.0 Phase |
|------------|------------|
| 1 — Muster | 1 — Muster *(unchanged)* |
| 1.5 — The Passage | 1.5 — The Passage *(unchanged)* |
| 2 — The Drop | 2 — The Drop *(quality gates now included here)* |
| 3 — The Proving | *(removed as standalone phase)* |
| 4 — The Forge | 3 — The Forge |
| 5 — Pax | 4 — Pax |
| 6 — Triumph | 5 — Merge + 6 — Triumph |

**Action required**: Update any documentation, checklists, or runbooks that reference phase numbers by name (e.g., "wait for Phase 3" → "quality gates run during Phase 2").

---

### 4. Howler Template: Quality Gates and PR Opening Removed

Howlers no longer run White, Gray, or `/diff-review` themselves. They no longer open PRs via Copper. The new flow:

- **v4.0**: Howler completes work → Howler runs quality gates → Howler opens PR
- **v5.0**: Howler completes work → Howler signals `Status: complete` → Howler exits → Gold spawns quality gates as visible background agents → Gold spawns Copper after gates pass

**Action required**: If you have saved or customized Howler drop prompts that reference the old template steps 11–14 (run White, run Gray, run `/diff-review`, open PR via Copper), those steps are now dead. Remove them. The new final step for Howlers is step 12: signal completion and exit.

This is a strict improvement for large spectrums — Gold can now trigger quality gates per-Howler as they finish rather than waiting for all Howlers to complete. But if you're resuming a mid-flight spectrum from v4.0, do not drop Howlers with the old template into a v5.0 Gold session.

---

### 5. New Muster Steps (Full Mode Only)

Three new steps have been inserted into the muster sequence in full mode, between the existing contract-writing step and the Politico step:

- **Step 9**: Codebase context + test impact map written into CONTRACT.md per Howler
- **Step 10**: Issue Confirmation Gate — Gold confirms the issue/task is still valid before freezing the contract
- **Step 11**: White Pre-Check — White reviews the contract for accuracy before Howlers are dropped
- **Step 12**: Contract-to-test generation (structural postconditions only)

These add approximately 3 minutes to full-mode muster. Steps 10–15 on v4.0 have shifted to steps 13–18 on v5.0.

**Action required**: None for most users — this is automatic. The new steps require the new tools (see New Features below). If muster fails on `codebase_index.py` or `test_impact_map.py` not found, run the tool copy step in the upgrade sequence.

**Reaping and nano mode**: These three steps are skipped. Reaping mode is unchanged from v4.0.

---

### 6. CHECKPOINT.json Schema Change

Four new fields are required for Gold's session recovery protocol:

```json
{
  "locus_history": [],
  "circuit_breaker_state": {},
  "active_diagnostics": [],
  "gold_context_snapshot": {}
}
```

**Action required**: Existing `CHECKPOINT.json` files from v4.0 spectrum runs will not have these fields. If a v4.0 spectrum run is mid-flight when you upgrade, Gold's recovery logic may fail. Either complete any in-flight spectrum runs before upgrading, or manually add the missing fields with empty values.

---

## Upgrade Steps

```bash
# 1. Back up your existing config
cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.v4-backup

# 2. Pull the latest version
cd /path/to/spectrum-protocol && git pull

# 3. Remove old singular agent files
#    (skip any that don't exist — primus.md is unchanged)
rm -f ~/.claude/agents/{gold,blue,white,gray,orange,copper,howler,obsidian,brown,violet,politico,green,helldiver}.md

# 4. Copy new protocol files
cp spectrum/CLAUDE.md ~/.claude/CLAUDE.md
cp spectrum/SPECTRUM-OPS.md ~/.claude/SPECTRUM-OPS.md
cp spectrum/SPECTRUM.md ~/.claude/SPECTRUM.md

# 5. Copy new agent definitions
cp agents/*.md ~/.claude/agents/

# 6. Copy new tools (optional — required for full-mode muster accuracy features)
cp tools/*.py ~/.claude/hooks/

# 7. Verify
#    Start a new Claude Code session and ask:
#    "What agents do you have available?"
#    You should see the pluralized roster (Golds, Blues, Howlers, etc.)
```

If you had custom sections in your v4.0 `~/.claude/CLAUDE.md` (project conventions, personal routing rules, etc.), merge them back in after step 4. Spectrum's CLAUDE.md has clear section headers — add your customizations at the bottom or in a project-level `CLAUDE.md` at your repo root.

---

## New Features After Upgrade

### Nano Mode
For 2–3 Howlers with obvious, non-overlapping boundaries. Skips CONTRACT.md, Politico, quality gates, human approval gate, and worktree pre-creation. Auto-approves and drops immediately. Muster takes under 1 minute. Escalates to reaping mode automatically if any Howler hits a blocker.

Use it for: throwaway scripts, isolated doc updates, small refactors that don't touch shared interfaces.

### Visible Agent Spawning
All background agents (Whites, Grays, Obsidians, Browns, Coppers) now appear in Claude Code's sidebar during a spectrum run. You can see which agents are active, which have completed, and which are blocked — without reading CHECKPOINT.json.

### Accuracy Improvements
Full-mode spectrums now get:
- Per-Howler codebase context (import graphs, function signatures) injected into CONTRACT.md
- Test impact maps showing which tests cover which source files
- White Pre-Check on the contract before Howlers are dropped (catches ambiguous contracts before they cause Howler failures)
- Issue Confirmation Gate (verifies the task is still valid before freezing the contract)
- Revision pass: Howlers re-read the original issue after completing work and do up to 2 revision cycles
- Known Failure Patterns from LESSONS.md injected into Howler drop prompts

### Speed Improvements
- Muster reads (LESSONS.md, ENTITIES.md, ARCHITECTURE.md, codebase index) now run in parallel: saves 1–2 minutes per muster
- White Pre-Check and Politico now run in parallel (previously sequential): saves 3–4 minutes per full muster
- Quality gates trigger per-Howler as each finishes, not after all Howlers complete: saves 8–15 minutes on staggered 4-Howler runs

### Session Recovery
Gold now has an explicit recovery protocol for session death mid-spectrum. On session start, Gold checks CHECKPOINT.json and can resume from any phase (dispatching, running, integrating, merging). The expanded CHECKPOINT.json schema persists circuit breaker state and pending DAG edges across sessions.

### New Tools
Five new Python tools are available in `tools/`:
- `codebase_index.py` — extracts import graphs and function signatures for CONTRACT.md codebase context
- `verify_postconditions.py` — automated postcondition verification against CONTRACT.md
- `test_impact_map.py` — maps source files to their covering test files
- `tools/swe_bench/load_tasks.py` + `emit_predictions.py` — SWE-bench evaluation support

Copy them to `~/.claude/hooks/` if you want the accuracy features in full mode.

---

## Known Issues in v5.0

Two internal inconsistencies exist in the current dev branch that do not affect normal use but are worth knowing:

1. **SPECTRUM.md Howler template not fully updated** — SPECTRUM.md still describes the old Howler steps 11–14 (self-run quality gates, open PR) in section 2.1. The authoritative template is in SPECTRUM-OPS.md. If SPECTRUM.md and SPECTRUM-OPS.md disagree on Howler behavior, follow SPECTRUM-OPS.md.

2. **Dual `subagent_type` naming** — Some sections of SPECTRUM.md still reference the old role aliases (`mayor`, `scout`, `inspector`, `rider`). These appear to be preserved for backward compatibility. The authoritative names are the pluralized Colors (`golds`, `blues`, `whites`, `howlers`).

---

## Rollback

If you need to revert to v4.0:

```bash
# Restore protocol files
cp ~/.claude/CLAUDE.md.v4-backup ~/.claude/CLAUDE.md
git checkout main -- spectrum/SPECTRUM-OPS.md spectrum/SPECTRUM.md
cp spectrum/SPECTRUM-OPS.md ~/.claude/SPECTRUM-OPS.md
cp spectrum/SPECTRUM.md ~/.claude/SPECTRUM.md

# Remove plural agent files and restore singular ones
rm ~/.claude/agents/{golds,blues,whites,grays,oranges,coppers,howlers,obsidians,browns,violets,politicos,greens,helldivers}.md
git checkout main -- agents/
cp agents/*.md ~/.claude/agents/
```
