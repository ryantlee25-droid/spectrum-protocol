# Spectrum Protocol -- Token Optimization Guide v4.0

Generated: 2026-03-30
Sources: INTERNAL-AUDIT.md (corrected estimates), COMPETITIVE-ANALYSIS.md (12-system survey), SPECTRUM-COST-ANALYSIS.md (prior analysis)

---

## 1. Token Budget Summary

### 1.1 Total Token Budget Per Spectrum Size

All figures use corrected estimates from INTERNAL-AUDIT.md, which found the prior analysis underestimated by 30-45%.

| Spectrum Size | Total Input Tokens | Total Output Tokens | Total Tokens | Estimated Cost |
|---------------|-------------------|---------------------|-------------|----------------|
| 3-Howler Reaping | ~430,000 | ~110,000 | ~540,000 | ~$4.80 |
| 5-Howler Full | ~770,000 | ~185,000 | ~955,000 | ~$9.43 |
| 8-Howler Full | ~1,180,000 | ~280,000 | ~1,460,000 | ~$15.20 |

**Input tokens dominate volume (80% of all tokens), but output tokens dominate cost at the Opus tier.** 20k tokens of Opus output ($1.48) cost more than 490k tokens of Sonnet input ($1.47). This asymmetry is the single most important fact in Spectrum token economics.

### 1.2 Phase-by-Phase Token Breakdown (5-Howler Reference)

| Phase | Agent | Input Tokens | Output Tokens | % of Total Tokens | % of Total Cost |
|-------|-------|-------------|---------------|-------------------|-----------------|
| Blue: PLAN.md | Sonnet | 30,000 | 5,500 | 4% | 2% |
| Gold Muster | Opus | 45,500 | 17,500 | 7% | 21% |
| Politico | Sonnet | 10,000 | 2,000 | 1% | 1% |
| Howlers (x5) | Sonnet | 600,000 | 125,000 | 76% | 32% |
| White (x5) | Sonnet | 77,500 | 15,000 | 10% | 5% |
| Gray (x5) | Sonnet | 75,000 | 20,000 | 10% | 6% |
| /diff-review (x5) | Sonnet | 50,000 | 7,500 | 6% | 3% |
| Gold Pax | Opus | 64,800 | 8,000 | 8% | 17% |
| Gray per-merge (x5) | Sonnet | 50,000 | 5,000 | 6% | 3% |
| Gold self-reflect (x5) | Opus | 15,000 | 750 | 2% | 3% |
| Final Gray | Sonnet | 13,000 | 2,000 | 2% | 1% |
| Obsidian | Sonnet | 27,000 | 4,000 | 3% | 1% |
| Brown | Haiku | 32,500 | 3,000 | 4% | <1% |
| Gold reviews Brown | Opus | 10,000 | 3,000 | 1% | 4% |
| Copper (x5) | Haiku | 10,000 | 4,000 | 1% | <1% |

**Key insight**: Howlers consume 76% of all tokens but only 32% of cost (Sonnet pricing). Gold consumes 15% of tokens but 45% of cost (Opus pricing). Token reduction efforts should target Gold output tokens and Howler input tokens, in that priority order.

### 1.3 The Three Token Pressure Zones

**Zone 1 -- Opus Output (the silent killer)**
- 20k tokens total across all Gold phases
- Cost: ~$1.48 (14% of total run cost from <2% of tokens)
- Every 1k Opus output tokens saved = $0.075 saved
- Conciseness in Gold artifacts has 5x the cost impact of Sonnet conciseness

**Zone 2 -- Howler Session Context Accumulation**
- Each Howler accumulates ~120k billed input tokens across a 15-turn session
- 5 Howlers = ~600k tokens of Sonnet input (the largest single token pool)
- Context repetition across turns is the primary driver (the "sliding window tax")
- ~10k tokens per Howler are SPECTRUM-OPS.md content never used by Howlers

**Zone 3 -- Gold Pax Input**
- 65k tokens of Opus input for 5-Howler run, scaling to 100k+ for 8-Howler
- Reads N debriefs + N HOOK.md files + N x 3 source files
- This is the phase most likely to hit context window pressure at 8-Howler scale

### 1.4 Context Window Pressure Map

| Agent | Typical Session Size | 200k Window Usage | Risk Level |
|-------|---------------------|-------------------|------------|
| Howler (15-turn session) | ~120k effective | 60% | Medium -- safe but compaction possible on large tasks |
| Gold Muster | ~63k effective | 32% | Low |
| Gold Pax (5-Howler) | ~73k effective | 37% | Medium |
| Gold Pax (8-Howler) | ~110k effective | 55% | High -- approaching compaction territory |
| White | ~16k | 8% | None |
| Gray | ~15k | 8% | None |
| Obsidian | ~31k | 16% | None |
| Brown | ~36k | 18% | None |

**Critical threshold**: Gold Pax at 8-Howler scale. If Howlers are verbose in HOOK.md and debriefs, Gold Pax can reach 120-130k tokens, leaving minimal headroom for reasoning. This is where context optimization has the highest quality impact, not just cost impact.

---

## 2. Optimization Proposals

### Tier 1: Implement Now (spec changes only, no tooling)

#### T1-A: Create HOWLER-OPS.md (~10k tokens saved per Howler)

**What**: Extract the Howler-relevant subset of SPECTRUM-OPS.md into a separate `~/.claude/HOWLER-OPS.md` (~2,500 tokens). Reference this in Howler drop prompts instead of full SPECTRUM-OPS.md.

**What to include in HOWLER-OPS.md**:
- HOOK.md template (~800 tokens)
- Quality gate instructions (~300 tokens)
- Debrief YAML frontmatter schema (~600 tokens)
- Completion verification checklist (~200 tokens)
- Reflexion/scope alignment rules (~300 tokens)
- Contract amendment procedure (~200 tokens)

**What to exclude** (10,300 tokens of Howler-irrelevant content):
- Full muster procedure (Phase 1): ~3,000 tokens
- Failure classification tables (Phase 3): ~1,500 tokens
- Pax procedure (Phase 4): ~1,500 tokens
- Merge procedure (Phase 5): ~800 tokens
- Triumph/Learning (Phase 6): ~1,200 tokens
- Reaping mode details: ~800 tokens
- Agent Teams integration: ~1,500 tokens

**Token savings**: 10,000 tokens x N Howlers of Sonnet input.
- 5-Howler: 50,000 tokens saved ($0.15)
- 8-Howler: 80,000 tokens saved ($0.24)

**Files to edit**: Create `~/.claude/HOWLER-OPS.md`. Update SPECTRUM-OPS.md Howler Drop Template to reference HOWLER-OPS.md instead of SPECTRUM-OPS.md.

**Quality risk**: Zero. Howlers never need muster/pax/merge/triumph instructions.

---

#### T1-B: Downgrade Per-PR Self-Reflect from Opus to Sonnet

**What**: Change the per-merge self-reflect invocation from Gold (Opus) to a Sonnet agent. The output is 3-5 lines: "PR N merged. TypeScript passes. Watch for X in next merge."

**Token savings**: Identical token volume, but the price-per-token drops 5x on output.
- 5-Howler: $0.14 saved (from $0.28 to $0.14)
- 8-Howler: $0.31 saved (from $0.45 to $0.14)

**Files to edit**: SPECTRUM-OPS.md Phase 5 section. CLAUDE.md model assignments note.

**Quality risk**: Low. This is structured journaling, not synthesis. Sonnet handles it.

---

#### T1-C: Eliminate Gold's Manual Seam Re-Derivation

**What**: Clarify in SPECTRUM-OPS.md Phase 4 that Gold uses SEAM-CHECK.md as the authoritative seam cross-reference. Gold reads debrief narratives only for qualitative signals (confidence, warnings, architectural decisions) -- NOT to re-derive seam cross-references that seam_check.py already computed.

**Token savings**: ~2,000 fewer Opus output tokens (reasoning that duplicates seam_check.py).
- Per run: 2,000 x $75/M = $0.15 saved

**Files to edit**: SPECTRUM-OPS.md Phase 4 step 3.

**Quality risk**: Zero. seam_check.py is mechanically correct. Gold adds value through qualitative interpretation, not re-computation.

---

#### T1-D: HOOK.md Compactness Rules

**What**: Add to the Howler drop template:
1. Completion Verification: log `PASS (N files)` or `FAIL (file: reason)` -- not full `ls -la` output
2. Remove empty sections before final HOOK.md write (Blockers: none, Errors: none, Cross-Domain: none)
3. Decisions: one line per decision, not paragraphs

**Token savings**: ~500-1,000 tokens per Howler at Pax input (Opus pricing).
- 5-Howler: 2,500-5,000 Opus input tokens saved = $0.04-0.08
- 8-Howler: 4,000-8,000 Opus input tokens saved = $0.06-0.12

**Files to edit**: SPECTRUM-OPS.md HOOK.md template section and Howler Drop Template.

**Quality risk**: Minimal. Gold needs pass/fail signals, not raw command output.

---

#### T1-E: Gold Conciseness Directive

**What**: Add a conciseness directive to Gold's muster and pax prompts: "Every output token costs $75/M. Be precise. Prefer structured YAML over narrative prose for MANIFEST.md DAG sections. Omit reasoning that does not inform the human or downstream agents."

**Token savings**: Estimated 10-15% reduction in Gold output tokens.
- Current: ~29k Opus output tokens across a full 5-Howler run
- Target: ~25k Opus output tokens
- Savings: 4,000 x $75/M = $0.30

**Files to edit**: Gold prompt instructions in SPECTRUM-OPS.md and CLAUDE.md.

**Quality risk**: Low, if directive is "be concise" not "be terse." Gold's reasoning is load-bearing; the waste is in verbose prose that restates what the YAML already encodes.

---

**Tier 1 Combined Savings:**
| Optimization | 5-Howler | 8-Howler |
|-------------|----------|----------|
| T1-A: HOWLER-OPS.md | $0.15 | $0.24 |
| T1-B: Self-reflect downgrade | $0.14 | $0.31 |
| T1-C: Seam re-derivation | $0.15 | $0.15 |
| T1-D: HOOK.md compactness | $0.06 | $0.09 |
| T1-E: Gold conciseness | $0.30 | $0.40 |
| **Total** | **$0.80** | **$1.19** |
| **% of total cost** | **8.5%** | **7.8%** |

---

### Tier 2: Implement Soon (minor tooling or template changes)

#### T2-A: Per-Howler CONTRACT.md Slicing

**What**: Gold constructs a per-Howler contract slice at dispatch:
1. Always: Shared Types, Constants, Conventions
2. Only own DbC section (Preconditions, Postconditions, Invariants)
3. "Seams affecting you" -- 2-3 lines extracted from neighboring Howlers' DbC
4. Exclude: all other Howlers' full DbC sections

**Token savings**: ~1,700 tokens per Howler of Sonnet input.
- 5-Howler: 8,500 tokens ($0.03)
- 8-Howler: 19,600 tokens ($0.06)

**Effort**: Minor -- Gold already writes the drop prompt. This adds a slicing step.

**Quality risk**: Low, with the "Seams affecting you" bridge. Without it, Howlers could miss seam obligations from neighboring contracts.

---

#### T2-B: Confidence-Tiered Pax Validation

**What**: Gold adjusts file-reading depth during independent validation based on Howler self-reported confidence:
- `confidence: high` + `contract_compliance: full`: read 1 file (spot check)
- `confidence: medium`: read 2-3 files (standard)
- `confidence: low` or `contract_compliance: partial`: read 3+ files (full validation)

**Token savings**: ~3,000 Opus input tokens per high-confidence Howler skipped.
- 5-Howler (3 high-confidence): 9,000 tokens = $0.14
- 8-Howler (5 high-confidence): 15,000 tokens = $0.23

**Effort**: Minimal -- add decision rule to Gold Pax instructions.

**Quality risk**: Low. High-confidence Howlers already passed White + Gray + /diff-review.

---

#### T2-C: Conditional /diff-review by Security Surface

**What**: Gold tags each Howler in MANIFEST.md with `security_gate: required | optional`:
- `required`: auth, session handling, external APIs, user data, env vars, config
- `optional`: internal utilities, documentation, UI components with no data access

Only drop /diff-review for `required` Howlers.

**Token savings**: ~10,000 tokens per skipped /diff-review.
- 8-Howler (4 optional): 40,000 tokens saved ($0.20)

**Effort**: Minimal -- Gold adds a tag during muster.

**Quality risk**: Low-medium. White still reviews security concerns for all Howlers. The /diff-review adds depth on security-sensitive changes specifically.

---

#### T2-D: Discovery Relay Token Cap Enforcement

**What**: The spec says ~500 tokens for discovery relay. Add mechanical enforcement: Gold must count tokens in the relay and truncate to 500. Currently, there is no enforcement mechanism -- Gold is asked to "compress" but may produce 800-1200 token relays for complex dependent Howlers.

**Token savings**: Variable. Prevents relay bloat from creeping up over time.
- Estimated: 0-500 tokens per dependent Howler

**Effort**: Add a word-count check to Gold's drop procedure.

**Quality risk**: None if the cap is respected. The relay is supplementary; CONTRACT.md is the source of truth.

---

**Tier 2 Combined Savings:**
| Optimization | 5-Howler | 8-Howler |
|-------------|----------|----------|
| T2-A: CONTRACT slicing | $0.03 | $0.06 |
| T2-B: Tiered Pax validation | $0.14 | $0.23 |
| T2-C: Conditional /diff-review | $0.05-0.10 | $0.15-0.20 |
| T2-D: Relay cap enforcement | negligible | negligible |
| **Total** | **$0.22-0.27** | **$0.44-0.49** |

---

### Tier 3: Consider Later (architectural changes)

#### T3-A: LLM Avoidance for Mechanical Dispatch

**What**: Implement pattern-matching for common Gold dispatch decisions that do not require LLM reasoning. Examples:
- If all Howlers are pure-create with no deps, skip full DAG analysis (reaping mode already partially does this)
- If CHECKPOINT.json shows a Howler completed, emit the discovery relay from a template instead of having Gold re-read and compress the debrief
- Worktree creation and verification via shell script, not Gold session

**Token savings**: Potentially 5,000-10,000 Opus tokens on dispatch mechanics.
- Estimated: $0.40-0.75 per run

**Effort**: High. Requires building shell scripts or a lightweight dispatch harness.

**Tradeoffs**: Reduces Gold's situational awareness during dispatch. Gold currently sees every artifact during muster, which informs its judgment about risk and priority. Splitting mechanical from cognitive dispatch may cause Gold to miss context.

---

#### T3-B: Per-Agent CLAUDE.md Sections

**What**: Replace the single monolithic CLAUDE.md with per-agent instruction files or agent-specific sections that Claude Code loads based on agent type. Howlers get Howler-relevant rules. White gets inspector-relevant rules. Copper gets commit rules.

**Token savings**: ~4,000-5,000 tokens per agent invocation.
- 5-Howler run (~15 agent invocations): ~65,000 tokens = $0.38 (blended rate)

**Effort**: High. May require Claude Code platform changes or creative use of project-level overrides.

**Tradeoffs**: Fragmented instruction files are harder to maintain and update. A single source of truth (CLAUDE.md) has maintenance advantages that may outweigh token savings.

---

#### T3-C: Pax Debrief Compression

**What**: Instead of Gold reading full debriefs (N x 2,500 tokens) at Pax, have each Howler produce a structured JSON summary alongside the narrative debrief. Gold reads the JSON summaries (~500 tokens each) for mechanical cross-referencing, and only reads full narratives for Howlers flagged with issues.

**Token savings**: (N x 2,000) Opus input tokens saved.
- 5-Howler: 10,000 tokens = $0.15
- 8-Howler: 16,000 tokens = $0.24

**Effort**: Medium. Add JSON summary format to debrief template.

**Tradeoffs**: Gold loses qualitative context from narrative sections. Mitigation: Gold reads full narratives only for medium/low confidence Howlers.

---

#### T3-D: Idle Monitoring with Shell Polling

**What**: Replace Gold's LLM-based monitoring of Howler progress with a shell script that checks HOOK.md file modification times. Only invoke Gold when a Howler signals completion or failure.

**Token savings**: Eliminates Gold polling overhead (currently minimal in Spectrum because Gold is event-driven via Agent tool completion, but could prevent future creep).

**Effort**: Low-medium. A cron or watch script.

**Tradeoffs**: Spectrum already uses Agent tool's background completion notification, making this largely unnecessary today.

---

**Tier 3 Combined Potential Savings:**
| Optimization | 5-Howler | 8-Howler |
|-------------|----------|----------|
| T3-A: LLM avoidance | $0.40-0.75 | $0.50-0.90 |
| T3-B: Per-agent CLAUDE.md | $0.38 | $0.50 |
| T3-C: Pax debrief compression | $0.15 | $0.24 |
| T3-D: Shell polling | negligible | negligible |
| **Total** | **$0.93-1.28** | **$1.24-1.64** |

---

## 3. Per-Agent Token Budget

### Gold (Opus)

| Metric | Muster | Pax | Self-Reflect | Brown Review |
|--------|--------|-----|-------------|-------------|
| **Input budget** | 45k tokens | 65k (5H) / 100k (8H) | 3k per merge | 10k |
| **Output budget** | 17k tokens | 8k tokens | 150 per merge | 3k |
| **Model** | Keep Opus | Keep Opus | **Change to Sonnet** | Keep Opus (marginal) |

**What to include in Gold Muster context**: SPECTRUM-OPS.md (full), CLAUDE.md, PLAN.md, LESSONS.md, ENTITIES.md, ARCHITECTURE.md, 3-5 sampled source files.

**What to exclude**: Nothing -- Muster needs full context to decompose correctly.

**What to include in Gold Pax context**: SEAM-CHECK.md, all debriefs, all HOOK.md files, CONTRACT.md, CHECKPOINT.json, 1-3 source files per Howler (tiered by confidence).

**What to exclude from Pax**: SPECTRUM-OPS.md muster/drop/quality-gate sections (if Pax is a new session). Full source file reads for high-confidence Howlers.

**Conciseness target**: Reduce Opus output by 15% through structured YAML preference and reasoning discipline. Current ~29k output target: ~25k.

---

### Howler (Sonnet)

| Metric | Current | Optimized |
|--------|---------|-----------|
| **Input at dispatch** | ~27k tokens | ~17k tokens (with HOWLER-OPS.md + contract slicing) |
| **Effective billed input (full session)** | ~120k tokens | ~100k tokens |
| **Output budget** | ~25k tokens | ~25k tokens (no change) |
| **Model** | Keep Sonnet (floor) | Keep Sonnet (floor) |

**What to include in Howler context**: HOWLER-OPS.md (2,500 tokens), own CONTRACT.md slice (1,800 tokens), task scope, file ownership, discovery relay (500 tokens max).

**What to exclude**: Full SPECTRUM-OPS.md (10k savings), other Howlers' DbC sections (1,700 savings), muster/pax/merge/triumph procedures.

**HOOK.md discipline**: Final write should be under 1,500 tokens. Remove empty sections. Log verification as PASS/FAIL with counts only.

---

### White (Sonnet)

| Metric | Budget |
|--------|--------|
| **Input** | ~16k tokens (system + diff + HOOK.md + contract) |
| **Output** | ~3k tokens (review report) |
| **Model** | Keep Sonnet |

**Include**: git diff, HOOK.md (for context), Howler's CONTRACT.md slice (not full contract).
**Exclude**: Full SPECTRUM-OPS.md, unrelated CLAUDE.md sections.

---

### Gray (Sonnet)

| Metric | Budget |
|--------|--------|
| **Input** | ~15k tokens (system + test output + source files + HOOK.md) |
| **Output** | ~4k tokens (test report + any new test code) |
| **Model** | Keep Sonnet |

**Include**: Test runner output, relevant source files, HOOK.md.
**Exclude**: CONTRACT.md (Gray checks tests, not contract compliance).

---

### Politico (Sonnet)

| Metric | Budget |
|--------|--------|
| **Input** | ~10k tokens (system + MANIFEST.md + CONTRACT.md) |
| **Output** | ~2k tokens (blockers/warnings) |
| **Model** | Keep Sonnet |

No optimization needed. Already one of the most efficient invocations ($0.06). ROI is among the highest in the protocol -- a single structural catch saves $1-3 in recovery.

---

### Obsidian (Sonnet)

| Metric | Budget |
|--------|--------|
| **Input** | ~27k tokens (system + PLAN.md + MANIFEST.md + merged files) |
| **Output** | ~4k tokens (SENTINEL-REPORT.md + tool calls) |
| **Model** | Keep Sonnet |

**Include**: PLAN.md, DESIGN.md (if present), MANIFEST.md, merged source files (grep-targeted).
**Exclude**: Full SPECTRUM-OPS.md, CONTRACT.md (Obsidian checks plan compliance, not contract compliance).

---

### Brown (Haiku)

| Metric | Budget |
|--------|--------|
| **Input** | ~33k tokens (debriefs + HOOK.md files + artifacts) |
| **Output** | ~3k tokens (LESSONS-DRAFT.md) |
| **Model** | Keep Haiku |

Cheapest LLM-based agent in the protocol at ~$0.04. Gold reviews the draft, so Haiku's limitations are backstopped.

---

### Copper (Haiku)

| Metric | Budget |
|--------|--------|
| **Input** | ~2k tokens per PR |
| **Output** | ~0.8k tokens per PR |
| **Model** | Keep Haiku |

At $0.005 per invocation, Copper is negligible. No optimization needed.

---

### Orange (Sonnet, conditional)

| Metric | Budget |
|--------|--------|
| **Input** | ~13k tokens (system + HOOK.md + source + error logs) |
| **Output** | ~3k tokens (root cause + fix proposal) |
| **Model** | Keep Sonnet |

Only invoked on failure. Max 2 per Howler. Expected cost: ~$0.17 per 5-Howler run (25% failure probability).

---

## 4. Competitive Benchmark

### Token Efficiency Comparison

| System | Tokens per Agent Task | Coordination Overhead | Context Management | Overall Efficiency |
|--------|----------------------|----------------------|-------------------|--------------------|
| **Spectrum (current)** | ~145k (120k in + 25k out) | ~170k (Gold muster+pax) | Discovery relay, HOOK.md | Medium-High |
| **Spectrum (optimized)** | ~125k (100k in + 25k out) | ~150k | + HOWLER-OPS.md, contract slicing | High |
| **Gas Town** | ~100-200k (estimated) | High (Mayor + Refinery) | Per-agent windows, no compression | Medium |
| **oh-my-claudecode** | Unknown (proprietary) | Low (rule-based routing) | Inherited from Claude Code | Medium-High |
| **Cursor Agents** | ~50-100k per background run | Low (single orchestrator) | Inherited from Cursor | High (but limited parallel scale) |
| **CrewAI** | ~3x baseline (measured) | Very High (ReAct ceremony) | Full broadcast default | Low |
| **AutoGen/AG2** | O(N*M) group chat | Medium-High | TransformMessages (opt-in) | Low-Medium |
| **LangGraph** | Variable (graph-dependent) | Low (structured state) | Structured state passing | High |
| **Citadel** | Variable (4-tier router) | Very Low (60-80% no LLM) | Campaign persistence | Very High |

### Detailed Comparisons

**Spectrum vs Gas Town (comparable 5-8 agent scale)**

Gas Town runs 12-30 parallel agents (Pole Cats), generating a reported $100/hour burn rate at full fleet. Spectrum's 5-Howler run costs ~$9.43 total, executing in 15-30 minutes. Gas Town compensates with idle patrol effort tuning (66% savings on dormant agents) and cost-tier systems -- optimizations that Spectrum does not need because Spectrum's agents are task-scoped (they run, complete, and terminate) rather than polling-based.

Spectrum's structural advantage: agents are ephemeral. Gas Town's structural advantage: real-time monitoring and adaptation.

**Spectrum vs oh-my-claudecode (comparable task complexity)**

OMC's 3-tier model routing (Haiku/Sonnet/Opus by task complexity) is more granular within individual agent sessions than Spectrum's per-agent model assignment. OMC's Ecomode (Haiku-first, Sonnet only when needed) trades quality for cost more aggressively than Spectrum allows. OMC does not implement independent validation (Gold Pax equivalent) or checkpoint-based crash recovery (HOOK.md), which means OMC's quality floor is lower but its token ceiling is also lower.

Spectrum's advantage: quality guarantees (triple gate, independent validation, contract system). OMC's advantage: sub-agent model tiering, real-time cost HUD.

**Spectrum vs Cursor Parallel Agents**

Cursor Background Agents operate in a subscription/credit model that hides token costs. A single 50k-line codebase run can consume 22.5% of a $20 monthly credit pool. Cursor provides unlimited tab completions (zero-cost for the most frequent operation) but charges a 20% MAX mode surcharge for background agents. Spectrum has no equivalent zero-cost tier, but also has no hidden surcharges.

Cursor's advantage: zero-cost tab completions, simpler mental model (credits, not tokens). Spectrum's advantage: transparent per-invocation cost tracking, crash recovery, quality gates.

**Spectrum vs CrewAI**

CrewAI's mandatory ReAct ceremony (Thought-Action-Observation) adds 300-800 tokens per tool call that Spectrum agents do not generate. Across 50 tool calls per Howler, this would add 15,000-40,000 tokens per agent -- a 12-33% overhead that Spectrum avoids entirely. CrewAI's 3x measured token consumption (vs LangChain baseline) would translate to ~$28 for a 5-Howler equivalent, nearly 3x Spectrum's corrected cost.

Spectrum's decisive advantage: no mandatory reasoning ceremony. Claude Code's native tool calling is dramatically more token-efficient than ReAct loops.

---

## 5. Context Window Survival Guide

### 5.1 HOWLER-OPS.md (Trimmed Spec for Howlers)

Create `~/.claude/HOWLER-OPS.md` containing only:

```
## Sections to Include (~2,500 tokens total):
1. HOOK.md Template (with compactness rules)
2. Completion Verification Checklist
3. Quality Gate Instructions (White + Gray + /diff-review, in parallel)
4. Debrief YAML Frontmatter Schema
5. Reflexion Check Rules (every 5 writes)
6. Scope Alignment Check Rules (every 20 tool calls)
7. Contract Amendment Procedure (non-breaking vs breaking)
8. git_status values and operator commit fallback

## Sections to EXCLUDE (~10,000 tokens saved):
- Full Muster procedure (Phase 1)
- Reaping mode activation criteria
- Failure classification tables (Phase 3)
- Pax procedure (Phase 4)
- Merge procedure (Phase 5)
- Triumph/Learning (Phase 6)
- Agent Teams integration (Phase A/B/C)
- Safety Rails (Gold-specific constraints)
- Scaling observations
```

### 5.2 CONTRACT.md Slicing

At dispatch, Gold constructs per-Howler contract slices:

```
Per-Howler CONTRACT.md (~1,800 tokens):
  - Shared Types section (always)
  - Shared Constants section (always)
  - Naming Conventions section (always)
  - Own Preconditions/Postconditions/Invariants
  - "Seams affecting you" (2-3 lines from neighboring DbC)

Excluded (~1,700 tokens per Howler):
  - All other Howlers' full DbC sections
```

### 5.3 Discovery Relay Token Cap

**Hard cap: 500 tokens per relay.**

Content priority (in order, stop when cap reached):
1. Key decisions made (from completed Howler's HOOK.md Decisions)
2. File paths created that the new Howler imports from
3. Warnings or surprises encountered
4. Cross-domain observations relevant to the new Howler

Do NOT include: full debrief content, error logs, anything CONTRACT.md already covers.

### 5.4 HOOK.md Compactness Rules

1. **Completion Verification**: `PASS (5 files created)` or `FAIL (auth.ts: missing export)` -- never paste full `ls -la` output
2. **Empty sections**: Remove before final write. Do not write `## Blockers: (none)` -- omit the section entirely
3. **Decisions**: One line per decision with rationale. Not paragraphs.
4. **Progress**: Check off completed items. Do not add narrative descriptions of completed work.
5. **Target**: Final HOOK.md under 1,500 tokens (currently averaging ~2,000-2,500)

### 5.5 When to Use Each Model

| Situation | Model | Rationale |
|-----------|-------|-----------|
| Task decomposition, contract authoring | Opus | Cascade risk -- bad decomposition costs $2-5 in recovery |
| Independent validation of Howler output | Opus | Must catch "green but wrong" with adversarial skepticism |
| Code implementation | Sonnet | Sweet spot of capability and cost. Haiku misses architectural intent |
| Code review (White) | Sonnet | Needs reasoning for subtle bugs and contract compliance |
| Test diagnosis (Gray) | Sonnet | Needs reasoning to distinguish real failures from flaky tests |
| Root cause analysis (Orange) | Sonnet | Cross-stack reasoning required |
| Adversarial plan review (Politico) | Sonnet | Must anticipate non-obvious gaps. Haiku rubber-stamps |
| Spec compliance (Obsidian) | Sonnet | Intent-vs-letter judgment calls |
| Per-PR self-reflect | **Sonnet (changed from Opus)** | Structured journaling, not complex synthesis |
| LESSONS.md drafting (Brown) | Haiku | Gold reviews the draft. Haiku is adequate |
| Commits, PRs (Copper) | Haiku | Mechanical operations |

### 5.6 The 8-Howler Survival Checklist

At 8-Howler scale, Gold Pax approaches 55% context window usage. Apply all of these:

- [ ] HOWLER-OPS.md in Howler drops (saves 80k tokens of Howler input)
- [ ] Per-Howler CONTRACT.md slicing (saves 20k tokens of Howler input)
- [ ] HOOK.md compactness rules enforced (saves 8k tokens of Opus Pax input)
- [ ] Confidence-tiered Pax validation (saves 15k tokens of Opus Pax input)
- [ ] Gold conciseness directive active (saves 4k tokens of Opus output)
- [ ] Discovery relay capped at 500 tokens (prevents creep)
- [ ] Conditional /diff-review for non-security Howlers (saves 40k tokens)

**Total context reduction at 8-Howler scale**: ~167,000 tokens saved across the full run.

---

## Appendix: Token Economics Cheat Sheet

```
Token-to-Dollar Conversion (per 1,000 tokens):

  Opus  input:  $0.015    Opus  output:  $0.075
  Sonnet input: $0.003    Sonnet output: $0.015
  Haiku  input: $0.0008   Haiku  output: $0.004

Impact multipliers:
  1k Opus output saved    = 5x the value of 1k Sonnet output saved
  1k Opus output saved    = 18.75x the value of 1k Haiku output saved
  1k Opus output saved    = 25x the value of 1k Sonnet input saved
  1k Opus output saved    = 93.75x the value of 1k Haiku input saved

Priority order for token reduction:
  1. Opus output tokens   (highest $/token)
  2. Opus input tokens    (5x Sonnet input)
  3. Sonnet output tokens (5x Sonnet input)
  4. Sonnet input tokens  (baseline)
  5. Haiku tokens         (negligible)
```
