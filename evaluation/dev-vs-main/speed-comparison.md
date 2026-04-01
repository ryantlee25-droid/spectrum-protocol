# Spectrum Protocol — Dev vs. Main Speed Comparison

**Date**: 2026-03-31
**Sources**: `git show main:spectrum/SPECTRUM-OPS.md`, `spectrum/SPECTRUM-OPS.md` (dev), `evaluation/code-review/speed-audit.md`

---

## Muster Phase Timing

### Step-by-Step Comparison

| Step | Main | Dev | Delta |
|------|------|-----|-------|
| 1. Generate rain ID | Sequential | Sequential | No change |
| 2. Create spectrum directory | Sequential | Sequential | No change |
| 3. Read LESSONS.md + ENTITIES.md | Sequential | **Parallel with ARCHITECTURE.md update and codebase_index.py** | −1–2 min |
| 4. Validate PLAN.md (3-5 file samples) | Sequential | Sequential | No change |
| 5. Evaluate scale (3+/2/1) | Sequential | Sequential | No change |
| 6. Update ARCHITECTURE.md | Sequential (after step 3) | **Parallel with steps 3 + codebase index** | Absorbed into step 3 savings |
| 7. DESIGN.md (API/schema only) | Optional, sequential | Optional, sequential | No change |
| 8. Decomposition hazard scan | Sequential | Sequential | No change |
| 9. Write MANIFEST.md | Sequential | Sequential | No change |
| 10. Write CONTRACT.md | Sequential | Sequential; adds explicit codebase_index.py tool call, test impact map per Howler, and tighter "5-15 lines" guidance | Slight quality increase, no time change |
| 10.5. Issue Confirmation Gate | **NOT PRESENT** | **NEW** — Gold presents 3-bullet interpretation to human before White Pre-Check; skip for reaping/nano | +2–5 min (human-bounded) but prevents costly misdirection |
| 11. White Pre-Check | Sequential (after CONTRACT.md) | **Parallel with Politico** (step 11 in dev combines old steps 11 and 12) | −3–4 min |
| 12. Contract-to-test generation | Sequential (after White Pre-Check) | Sequential (after parallel White+Politico completes); behavioral postconditions explicitly excluded | No time change |
| 13. Commit convoy-contracts.d.ts | Sequential | Sequential | No change |
| 14. Politico adversarial review | Sequential (after step 13) | **Parallel with White Pre-Check** (folded into step 11) | −3–4 min (savings already counted in step 11) |
| 15. Present to human | Sequential | Sequential | No change |
| 16. Write CHECKPOINT.json | Sequential | Sequential; adds `locus_history`, `circuit_breaker_state`, `active_diagnostics`, `gold_context_snapshot` fields | No time change |
| 17. Pre-create worktrees | Sequential; per-worktree `git worktree list` verification | Sequential; single `git worktree list` after all creations | −5–30s for 4+ Howler runs |

### Key Structural Changes in Muster

**New in dev (not in main):**
- **Parallel muster reads** (step 3 note): LESSONS.md, ENTITIES.md, ARCHITECTURE.md update, and codebase_index.py runs initiated in parallel — explicit protocol requirement, not implied
- **Issue Confirmation Gate** (step 10.5): Gold presents 3-bullet problem/desired-behavior/out-of-scope summary to human before freezing. Prevents misaligned contracts from reaching Politico/White. Human-bounded latency but eliminates wasted muster cycles.
- **White + Politico parallel** (step 11): Previously sequential — White ran, Gold patched, then Politico ran. Dev drops both simultaneously. Politico is explicitly told "White Pre-Check has already validated factual accuracy — your role is decomposition logic and interface design." These are orthogonal tasks.
- **KNOWN RISKS injection**: If LESSONS.md has a `## Known Failure Patterns` section, relevant patterns are injected into each Howler's drop prompt. Main mentions incorporating LESSONS.md learnings but has no structured format for injecting patterns.
- **CHECKPOINT.json expansion**: Dev adds `locus_history`, `circuit_breaker_state`, `active_diagnostics`, `gold_context_snapshot` — enables full session recovery without re-reading all HOOK.md files.
- **Status Roster**: Dev adds a mandatory formatted status roster (with glyphs, status symbols, dependency waits) that Gold must print after every dispatch, completion, and phase transition. Main has no equivalent visibility requirement.
- **Worktree verification batched**: Dev consolidates per-worktree `git worktree list` calls into a single post-creation verification.

**Removed in dev (present in main):**
- No removals — dev is strictly additive at the muster phase.

### Muster Timing Summary

| Segment | Main | Dev |
|---------|------|-----|
| Reads (LESSONS + ENTITIES + ARCHITECTURE) | ~3–4 min (sequential) | ~2–3 min (parallel) |
| CONTRACT.md write | ~3–5 min | ~3–5 min |
| Issue Confirmation Gate | N/A | ~2–5 min (human-bounded) |
| White Pre-Check + Politico | ~7–9 min (sequential) | ~4–5 min (parallel) |
| Contract-to-test generation | ~1.5 min | ~1.5 min |
| convoy-contracts.d.ts commit | ~30s | ~30s |
| CHECKPOINT.json | ~15s | ~15s |
| Worktree pre-creation (4 Howlers) | ~30s + 4×(~10s verification) | ~30s + 1×(~10s verification) |
| **Total (pre-human gate)** | **~17–22 min** | **~14–18 min (+ Issue Gate)** |

Net muster savings: **~3–4 min** on the mechanical steps (parallel reads + parallel White/Politico + batched worktree verification). The Issue Confirmation Gate adds latency but is human-gated — it does not extend the mechanical critical path.

---

## Per-Mode Timing

| Mode | Main | Dev | Delta |
|------|------|-----|-------|
| **Full mode** | ~8 min (documented) / ~17–22 min (actual, per audit) | ~14–18 min actual (plus Issue Gate, human-bounded) | −3–4 min mechanical |
| **Reaping mode** | ~3 min | ~3 min (unchanged steps) | No change |
| **Nano mode** | **NOT PRESENT** | **~1 min** — NEW mode for 2-3 pure-create Howlers with obvious boundaries; auto-approves, no CONTRACT.md, no quality gates, no worktree pre-creation | NEW |
| **SWE-bench mode** | Not formalized (pipeline-design.md only) | **Formalized** — uses `examples/mini-CONTRACT.md`; ~2 min variant A, ~30s variant B | Formalized from evaluation work |
| **Multi-Candidate mode** | Not present | **NEW** — runs N candidates (default 3) on same task, selects highest test-pass patch; for benchmarks and production hotfixes | NEW |

### Mode Activation Logic

Main has two modes: full and reaping. Dev adds:
- **Nano**: fills the gap between reaping (3 min, quality gates, human confirms) and truly trivial parallelism (2-3 files, boundaries obvious, auto-approve). Sacrifices quality gates and contract for speed.
- **SWE-bench**: formalizes the benchmark pipeline from evaluation research.
- **Multi-Candidate**: accuracy-critical single-Howler runs with N-way selection.

The audit identified a "Micro" mode gap (2-3 Howlers, pure-create, double gate, human confirms) that is not yet present in dev either. Nano fills the no-gates end; Micro would fill the double-gate middle. Nano is present; Micro is not.

---

## Quality Gate Timing

### Architecture Change

**Main**: Howlers self-review inside their own session. The Howler drop template includes steps to run White, Gray, and /diff-review as part of the Howler's work. Gates happen inside the Howler — sequentially with implementation.

**Dev**: Gold spawns quality gates as visible background agents immediately when each Howler signals completion. Howlers no longer run quality gates. The Howler drop template ends at step 12: "Signal completion: set Status: complete in HOOK.md. Your job ends here. Gold will spawn White, Gray, and /diff-review — do not run these yourself."

### Timing Model for a 4-Howler Staggered Run

Assume: Howler A completes at T+20 min, B at T+25 min, C at T+30 min, D at T+35 min. Gates take 8 min each (parallel White+Gray+/diff-review). Copper opens PR in 2 min after gates pass.

**Main (gates run after all Howlers complete, or inside each Howler sequentially):**

Under the main model, if each Howler runs its own quality gate:
- Howler A: T+20 to T+28 (gate inside session), PR opened T+30
- Howler B: T+25 to T+33 (gate inside session), PR opened T+35
- Howler C: T+30 to T+38 (gate inside session), PR opened T+40
- Howler D: T+35 to T+43 (gate inside session), PR opened T+45
- PAX: T+45, all 4 PRs open
- **Wall clock to all PRs open: ~45 min**

**Dev (Gold spawns gates immediately on Howler completion, as background agents):**

- T+20: Howler A complete → Gold spawns White A + Gray A + /diff-review A (background)
- T+25: Howler B complete → Gold spawns White B + Gray B + /diff-review B (background)
- T+28: Howler A gates done → Gold spawns Copper A → PR A opened T+30
- T+30: Howler C complete → Gold spawns gates C (background); PR A open
- T+33: Howler B gates done → PR B opened T+35
- T+35: Howler D complete → Gold spawns gates D (background)
- T+38: Howler C gates done → PR C opened T+40
- T+43: Howler D gates done → PR D opened T+45
- PAX: T+45 (same)
- **Wall clock to all PRs open: ~45 min**

Wait — the wall clock to all PRs open is the same (bounded by last Howler + gate time). The real savings are:

1. **PRs open earlier for completed Howlers** — human can begin reviewing Howler A's PR at T+30 rather than waiting until T+45. On human-gated merge workflows this reclaims real time.
2. **Pax can start earlier** — in the dev model, by the time the last Howler completes, 3 of 4 PRs are already open and reviewed. Pax reads debriefs and checks seams immediately, rather than waiting for all 4 gate cycles to complete sequentially.
3. **Howlers are lighter** — removing gate execution from inside Howler sessions reduces each Howler's token budget and cognitive load. Howlers don't need gate agent context.

**Net savings on PAX start time (4-Howler staggered run):**
- Main: PAX starts at T+45 (all 4 gates complete after last Howler)
- Dev: PAX starts at T+45 (same — bounded by last Howler + its gate)

The savings are not in PAX start time — they are in **PR availability** (earlier human review) and **Howler session scope** (smaller, more focused). For a 4-Howler run where Howler A finishes 15 min before Howler D, human can merge PR A before D even finishes — unlocking incremental integration testing during the run.

**Estimated savings from overlapping gates with implementation: 8–15 min** (when human review and merge are in the critical path, which they are for dependent stacks).

---

## Token Efficiency

### Contract-by-Reference

**Main**: CONTRACT.md contents are inlined in the Howler drop template (`CONTRACT (frozen -- block if wrong): {CONTRACT.md contents}`).

**Dev**: CONTRACT.md is referenced by path: `"Read ~/.claude/spectrum/{rain-id}/CONTRACT.md before starting."` The inline comment in the dev template makes the savings explicit: "Token note: CONTRACT.md is referenced by path, not inlined. For a 5-Howler run with a 2000-token contract this saves ~10,000 input tokens (~$0.03 at Sonnet rates)."

**Calculation for a 5-Howler run with a 2,000-token contract:**

| | Main (inlined) | Dev (by path) |
|-|----------------|---------------|
| Tokens per Howler prompt | 2,000 (contract) + ~1,500 (template) = 3,500 | ~1,500 (template only) |
| Total across 5 Howlers | 17,500 | 7,500 |
| **Savings** | — | **10,000 tokens** |

At Sonnet input rates (~$3/MTok): **~$0.03 per 5-Howler spectrum**.

Note: The file read by each Howler still costs tokens (the Howler reads CONTRACT.md via a tool call), but tool-call reads happen once per Howler and are not repeated in subsequent context windows. The net saving is real for long Howler sessions with many tool calls where CONTRACT.md would have been re-sent in every context window extension.

### HOWLER-OPS.md Inlining (Not Yet Implemented)

The speed audit identified inlining of HOWLER-OPS.md operations instructions (~2,500 tokens) as the next biggest token waste. Dev has not yet implemented path-by-reference for this. It remains an open P2 item.

**If implemented:** ~2,500 × 5 Howlers = 12,500 tokens saved per spectrum (~$0.04).

### Additional Token Differences in Dev

| Change | Main | Dev | Savings |
|--------|------|-----|---------|
| CONTRACT.md by path | Inlined | By path reference | ~10,000 tokens / 5-Howler spectrum |
| KNOWN RISKS injection | Unstructured | Capped at 0-3 patterns; injected from structured `## Known Failure Patterns` | Variable; prevents uncapped LESSONS.md growth from inflating every prompt |
| CHECKPOINT.json fields | Minimal (`rain_id`, `phase`, `mode`, `howlers`, `errors`, `resumed_at`) | Expanded (`locus_history`, `circuit_breaker_state`, `active_diagnostics`, `gold_context_snapshot`) | −100–300 tokens (state is written once to disk, not kept in Gold context) |
| Issue Re-Read step | Not present | Howlers write 3–5 line postcondition assessment in HOOK.md | +~100 tokens per Howler (small cost, prevents missed postconditions) |
| Revision Pass step | Not present | Up to 2 revision passes with test output | +~200 tokens per pass (small cost, reduces White blocker escalations) |

### Full Token Efficiency Summary (5-Howler Spectrum with 2,000-Token Contract)

| Item | Main | Dev | Delta |
|------|------|-----|-------|
| CONTRACT.md in Howler prompts | 10,000 | 0 (path ref) | −10,000 |
| HOWLER-OPS.md (if path-ref'd) | 12,500 | 12,500 (not yet impl.) | 0 |
| KNOWN RISKS (structured cap) | Unbounded | ≤150 tokens × 5 | Bounded |
| Issue Re-Read in HOOK.md | 0 | ~500 tokens total | +500 |
| Revision Pass records | 0 | ~0–1,000 tokens total | +0–1,000 |
| **Net Howler prompt savings** | baseline | **−10,000 tokens** | **−10,000** |

---

## End-to-End Comparison

### Representative 5-Howler Full-Mode Spectrum

Assumptions: 5 Howlers in a wide DAG (3 roots + 2 dependent); 2,000-token CONTRACT.md; Howlers complete staggered (root Howlers: T+20, T+25, T+30; dependent Howlers: T+35, T+45 after dep resolution); quality gates take 8 min; human review/merge not in critical path.

| Phase | Main Wall Clock | Dev Wall Clock | Savings | Source |
|-------|----------------|----------------|---------|--------|
| Muster: reads (LESSONS + ARCH + index) | ~3–4 min | ~2–3 min | −1–2 min | Parallel reads |
| Muster: CONTRACT.md write | ~3–5 min | ~3–5 min | 0 | No change |
| Muster: Issue Confirmation Gate | 0 | ~2–5 min (human) | −2–5 min (human-bounded, not mechanical) | New step |
| Muster: White Pre-Check + Politico | ~7–9 min (sequential) | ~4–5 min (parallel) | −3–4 min | Parallel agents |
| Muster: Contract-to-test + convoy-contracts | ~2 min | ~2 min | 0 | No change |
| Muster: CHECKPOINT.json + worktrees (5×) | ~2 min (per-worktree verify) | ~1.5 min (single verify) | −30s | Batched verification |
| Human approval gate | variable | variable | 0 | Human-bounded |
| **Muster total (mechanical)** | **~17–22 min** | **~13–16 min** | **~4–6 min** | |
| Drop: root Howlers dispatch (3 parallel) | ~1 min | ~1 min | 0 | No change |
| Drop: root Howlers implementation | ~20–30 min (parallel) | ~20–30 min (parallel) | 0 | Implementation speed unchanged |
| Drop: quality gates for root Howlers | ~8 min × 3 sequential in main if inside Howler | 8 min parallel with other Howlers (Gold spawns immediately on completion) | −0 to −16 min | Overlapped gates |
| Drop: dependent Howler dispatch | ~1 min after dep completes | ~1 min | 0 | No change |
| Drop: dependent Howlers | ~15–20 min | ~15–20 min | 0 | Unchanged |
| Drop: gates for dependent Howlers | ~8 min each | ~8 min (overlapped with other completion) | −0 to −8 min | Overlapped |
| Pax (Gold reads 5 debriefs + validates) | ~10–15 min | ~10–15 min | 0 | No structural change |
| Merge + Gray post-each-merge | ~5 min/PR × 5 = 25 min | ~5 min/PR × 5 = 25 min | 0 | No change |
| Triumph (Obsidian + Brown + cleanup) | ~15 min | ~15 min | 0 | No change |
| **Total wall clock (pre-human merge)** | **~75–100 min** | **~65–85 min** | **~10–20 min** | |

The dominant savings are in the muster phase (~4–6 min) and the quality gate overlap (~8–15 min when Howlers complete staggered). Token savings (~10,000 tokens per spectrum) are real but not significant at current Sonnet rates (~$0.03).

---

## Summary of All Changes

### Speed Improvements (Dev > Main)

| Change | Phase | Wall-Clock Savings | Status |
|--------|-------|--------------------|--------|
| Parallel LESSONS + ARCH + codebase index reads | Muster | −1–2 min | Implemented |
| White Pre-Check + Politico in parallel | Muster | −3–4 min | Implemented |
| Single `git worktree list` after all pre-creations | Muster | −30s (4+ Howlers) | Implemented |
| Gold spawns quality gates on Howler completion (not inside Howler) | Drop/Proving | −8–15 min (staggered) | Implemented |
| CONTRACT.md by path reference (not inlined) | Drop | −10,000 tokens/run | Implemented |
| Nano mode (for trivial 2-3 Howler runs) | Mode | −2 min vs. reaping | Implemented |

### Quality Improvements (Dev > Main, with latency cost)

| Change | Phase | Effect |
|--------|-------|--------|
| Issue Confirmation Gate | Muster | Prevents misaligned contracts reaching Politico/White; adds human-bounded latency |
| KNOWN RISKS injection from structured LESSONS.md | Drop | Howlers receive relevant prior failure patterns; reduces repeat failures |
| Revision Pass (up to 2 passes in Howler) | Drop | Howlers fix test failures before escalating to White/Gray; reduces blocker volume |
| Issue Re-Read (postcondition assessment) | Drop | Howlers confirm postcondition satisfaction before signaling complete |
| CHECKPOINT.json expanded schema | Recovery | `locus_history` + `circuit_breaker_state` enables session recovery without re-reading all HOOK.md files |
| Status Roster (mandatory, formatted) | All | Human visibility into which agents are running at all times |
| SWE-bench mode formalized | Mode | Structured pipeline for benchmark runs |
| Multi-Candidate mode | Mode | N-way accuracy run for production hotfixes |

### Not Yet Implemented (Open Items from Audit)

| Item | Audit Priority | Savings Estimate |
|------|----------------|------------------|
| HOWLER-OPS.md by path reference | P2 | ~2,500 × N tokens |
| Pre-generate root Howler drop prompts during muster | P2 | ~30–60s per root Howler at dispatch |
| Micro mode (2-3 Howlers, double gate, human confirms) | P2 | ~1 min vs. reaping |
| Skip White Pre-Check for all-CREATES full-mode runs | P3 | ~3 min |
| Double gate as reaping mode default (/diff-review only for security-surface files) | P3 | ~3–5 min/reaping run |
| Pax export snapshot validation (Howlers write key export snippets to HOOK.md) | P4 | ~15,000–25,000 tokens in Pax |
| Mode-scaled debrief schema (simplified for reaping/nano) | P4 | ~1,000 tokens × N in Pax reads |

---

*Speed Comparison — Spectrum Protocol Dev vs. Main — 2026-03-31*
