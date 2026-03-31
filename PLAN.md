# PLAN.md — Spectrum Protocol Competitive Audit

**Date**: 2026-03-31
**Author**: Blues (Planner)
**Task**: Impartial competitive audit of Spectrum Protocol against the top 15 multi-agent systems

---

## Context and Scope

Spectrum already has a 28-system landscape survey at `evaluation/AGENTIC-LANDSCAPE.md` (March 2026) and a 12-dimension comparison table covering 19 systems. This audit deepens and extends that work with three new requirements:

1. **Consistent scoring** on the eight evaluation dimensions specified by the user (cost, speed, accuracy, workflow rigor, observability, recovery, setup complexity, scalability) — not just the 12 landscape dimensions
2. **Impartial treatment** — Spectrum included as a peer, not the reference point
3. **Top-15 competitor identification** — ranked and justified, with closest-competitor analysis

The prior landscape survey is an asset (saves re-researching most systems) but must not substitute for the required scoring rubric or bias the framing.

---

## Competitor Candidates

From the existing survey plus the audit brief, the candidate pool is:

**Claude Code ecosystem**: Gas Town, oh-my-claudecode, Agent Teams (Anthropic), ruflo, Citadel, Overstory, metaswarm, Kiro agents, agent-orchestrator (Composio)

**General frameworks**: CrewAI, LangGraph, MetaGPT, AutoGen/AG2, Camel, ChatDev, OpenAI Agents SDK, Semantic Kernel, PydanticAI, Magentic-One, Google ADK, AgileCoder

**Commercial/IDE**: Devin, Factory, Cursor agents, Windsurf, Codex (OpenAI), Amazon Q, GitHub Copilot Workspace, Replit Agent, Augment Code/Intent

The audit must select exactly 15 finalists from this pool (plus Spectrum = 16 total in the scoring table). Selection criteria: recency, relevance to the multi-agent coding use case, and coverage across categories.

---

## Evaluation Dimensions (Scoring Rubric)

Each of the 8 dimensions uses a **1–5 scale** with anchored definitions. A separate Howler defines the rubric precisely; all scoring Howlers must use it without modification.

| # | Dimension | What it measures |
|---|-----------|-----------------|
| 1 | **Cost per run** | Token/compute cost for a representative parallel coding task |
| 2 | **Speed** | Wall-clock time for parallel task completion; parallelism ceiling |
| 3 | **Accuracy** | Plan quality, code quality, test pass rates (SWE-Bench / community evidence) |
| 4 | **Workflow rigor** | Contracts, ownership, failure handling, adversarial review |
| 5 | **Observability** | Can you see what agents are doing mid-execution? |
| 6 | **Recovery** | What happens when an agent fails? Taxonomy, automation, circuit breakers |
| 7 | **Setup complexity** | Dependencies, configuration, learning curve |
| 8 | **Scalability** | Performance at 2 agents vs 20 agents; known ceilings |

---

## Decomposition

This is a **pure-create, research/writing task**. All Howlers create new files; no project source files are modified. Reaping mode is appropriate.

### Task Graph

```
[H1: Rubric] ──────────────────────────────────────────┐
                                                        ▼
[H2: Claude Code group] ──┐                     [H5: Synthesis]
[H3: Frameworks group]  ──┤──── all complete ──▶[H5: Synthesis]
[H4: Commercial group]  ──┘                     [H5: Synthesis]
```

- **H1** defines the scoring rubric. H2, H3, H4 must read and apply it.
- **H2, H3, H4** are independent and run in parallel after H1 delivers its rubric.
- **H5** is sequential — reads all three group reports and writes the synthesis.

---

## Howlers

### H1 — Rubric Architect
**File created**: `evaluation/audit-2026/RUBRIC.md`
**Effort**: S
**Serial risk**: No (runs first, unblocks others)

Define the 1–5 scoring rubric for all 8 dimensions with:
- Precise anchor descriptions for each score (1 = worst, 5 = best)
- Evidence types acceptable for each dimension (public benchmarks, community reports, documentation, first-principles reasoning)
- Instructions for handling partial evidence (score conservatively; document uncertainty)
- Note on impartiality: Spectrum must be scored identically to all others, with no home-team adjustment

Inputs: PLAN.md, `evaluation/AGENTIC-LANDSCAPE.md` (for dimension context)

Deliverable: `evaluation/audit-2026/RUBRIC.md` — finalized rubric, ready for H2/H3/H4

Signal for unblocking H2/H3/H4: HOOK.md status = `STABLE` (rubric written and self-reviewed)

---

### H2 — Claude Code Group Scorer
**Files created**: `evaluation/audit-2026/group-claude-code.md`
**Effort**: M
**Serial risk**: No (parallel with H3, H4)
**Depends on**: H1 (RUBRIC.md must be STABLE)

Score the Claude Code ecosystem candidates. After reading RUBRIC.md, select and score the most relevant Claude Code ecosystem systems. Must include:
- **Gas Town** (primary Claude Code alternative; direct Spectrum competitor)
- **oh-my-claudecode** (largest community presence; zero-config alternative)
- **Agent Teams** (Anthropic official; native platform)
- **Spectrum Protocol** (the subject of this audit — scored impartially as a peer)
- At minimum 1-2 of: Citadel, Overstory, metaswarm, Kiro agents, ruflo (select those with most evidence available)

For each system:
1. Apply RUBRIC.md scores for all 8 dimensions
2. Cite the specific evidence for each score (document, community report, benchmark, or first-principles)
3. Flag low-confidence scores explicitly (no evidence → score 2 with flag, not invented score)
4. Note any score where Spectrum receives unusual treatment and justify it

Inputs: RUBRIC.md, `evaluation/AGENTIC-LANDSCAPE.md` sections 4 and 2.5, README.md, `spectrum/SPECTRUM-OPS.md`

Output format: Markdown table + per-system evidence notes

---

### H3 — Frameworks Group Scorer
**Files created**: `evaluation/audit-2026/group-frameworks.md`
**Effort**: M
**Serial risk**: No (parallel with H2, H4)
**Depends on**: H1 (RUBRIC.md must be STABLE)

Score the general-purpose multi-agent frameworks. Must include:
- **CrewAI** (largest OSS adoption, 44k stars)
- **LangGraph** (strongest state management, growing adoption)
- **MetaGPT** (document-as-protocol pattern, academic validation)
- **AutoGen/AG2** (Microsoft Research, conversation-as-computation)
- **ChatDev** (waterfall → RL orchestrator, 27k stars)
- Select 1-2 of: CAMEL, AgileCoder, Magentic-One (select those with most evidence for the 8 dimensions)

Same scoring methodology as H2. For frameworks that are not coding-specific (e.g., CAMEL for general reasoning), note the applicability gap and score accordingly — do not penalize for explicit design scope differences, but do reflect missing coding-specific features.

Inputs: RUBRIC.md, `evaluation/AGENTIC-LANDSCAPE.md` section 2

Output format: Markdown table + per-system evidence notes

---

### H4 — Commercial Group Scorer
**Files created**: `evaluation/audit-2026/group-commercial.md`
**Effort**: M
**Serial risk**: No (parallel with H2, H3)
**Depends on**: H1 (RUBRIC.md must be STABLE)

Score the commercial and IDE-native systems. Must include:
- **Devin** (Cognition AI; cloud VM with Managed Devins; $20/month)
- **Cursor agents** (IDE-native; competitive execution; 8 parallel worktrees)
- **Augment Code/Intent** (Coordinator/Specialist/Verifier; 400k file context engine)
- **GitHub Copilot Workspace** (auditable pipeline; GitHub-native)
- **Amazon Q Developer** (AWS-specialized agents)
- Select 1-2 of: Factory, Windsurf, OpenAI Codex, Replit Agent (select those with most evidence)

Note: Commercial systems often have less public technical documentation. For black-box systems, score using observable behaviors (community reports, public changelogs, pricing pages). Score uncertainty must be flagged. Do not invent capabilities.

Inputs: RUBRIC.md, `evaluation/AGENTIC-LANDSCAPE.md` section 3

Output format: Markdown table + per-system evidence notes

---

### H5 — Synthesis Author
**Files created**:
- `evaluation/audit-2026/COMPETITIVE-AUDIT.md` (main deliverable)
- `evaluation/audit-2026/TOP15-RANKING.md` (ranked competitor list with justification)
**Effort**: L
**Serial risk**: Yes (must run after H2, H3, H4 complete)
**Depends on**: H2, H3, H4 (all group reports)

The synthesis Howler reads all three group reports and produces the final audit. This is the primary deliverable.

**Step 1 — Select the Top 15**:
Identify the 15 systems (from all three group reports, excluding Spectrum) that represent the most relevant competitive set. Selection criteria:
- Relevance to the multi-agent coding use case (not general AI assistants)
- Evidence quality (systems with well-documented behavior score more reliably)
- Category balance (include at least 3 from each of: Claude Code ecosystem, frameworks, commercial)

Justify the selection: for each system included, one sentence on why it made the cut. For systems excluded from the top 15, a brief note on why (e.g., "academic research system, not production-ready" or "insufficient evidence for reliable scoring").

**Step 2 — Unified Scoring Table**:
Produce a single 16-row table (15 competitors + Spectrum) with 8 dimension columns. All scores from H2/H3/H4 must be carried over exactly — H5 does not re-score. If scores conflict (same system scored differently by different Howlers), flag the conflict and take the lower score pending resolution.

**Step 3 — Closest Competitors Analysis**:
Compute per-system proximity to Spectrum using Euclidean distance on the 8-dimension vector (normalized to 0–1). Identify the 3 closest competitors and analyze WHY they are close:
- Which specific dimensions are similar?
- Which dimensions diverge most?
- What does a developer gain (or lose) by choosing the competitor over Spectrum?

**Step 4 — Spectrum Honest Assessment**:
Write a section titled "Spectrum: Honest Strengths and Weaknesses" that treats Spectrum as if it were a competitor being evaluated, not the home team. This section must:
- List genuine strengths with evidence (not self-reported claims)
- List genuine weaknesses with evidence — particularly where competitors score higher on specific dimensions
- Identify the use cases where Spectrum is clearly the wrong choice
- Identify the use cases where Spectrum is clearly the right choice

The prior landscape survey noted: "The most replicated academic finding is that a well-designed non-agentic pipeline can match or beat poorly coordinated multi-agent systems." Apply this skeptically to Spectrum's muster overhead.

**Step 5 — Recommendations**:
Based on the scoring data, identify 3–5 specific, actionable improvements Spectrum could make to close gaps with competitors. Prioritize improvements that address genuine weaknesses surfaced in the scoring (not features Spectrum already has). Each recommendation should reference the dimension it addresses and the competitor that leads on that dimension.

**Step 6 — Executive Summary**:
Write a 300–400 word executive summary suitable for the README: who are the top 3 closest competitors, what are Spectrum's genuine differentiators, and what are its honest limitations.

Output files:
- `evaluation/audit-2026/COMPETITIVE-AUDIT.md` — full audit (~2,000–3,000 words)
- `evaluation/audit-2026/TOP15-RANKING.md` — the ranked list with justification (~500 words)

---

## File Ownership Matrix

| File | Owner |
|------|-------|
| `evaluation/audit-2026/RUBRIC.md` | H1 |
| `evaluation/audit-2026/group-claude-code.md` | H2 |
| `evaluation/audit-2026/group-frameworks.md` | H3 |
| `evaluation/audit-2026/group-commercial.md` | H4 |
| `evaluation/audit-2026/COMPETITIVE-AUDIT.md` | H5 |
| `evaluation/audit-2026/TOP15-RANKING.md` | H5 |

No overlaps. No existing files are modified.

---

## Impartiality Requirements (All Howlers)

This is a binding constraint, not a suggestion.

1. **Spectrum is a peer, not the reference**. Scores for Spectrum are derived from the same evidence types and rubric anchors as any other system. No home-team adjustments.
2. **Weaknesses must appear in the output**. If a competitor scores higher than Spectrum on a dimension, that must be stated clearly with a specific example of what the competitor does better.
3. **Self-reported claims are not evidence**. Spectrum's README claims are marketing until independently validated. Score only what can be verified from the rubric evidence guidelines.
4. **When in doubt, score lower**. A conservative score with an uncertainty flag is more useful than a confident score with thin evidence.
5. **The prior landscape survey is a starting point, not the answer**. AGENTIC-LANDSCAPE.md was written under a Convoy contract that included Convoy itself as the reference system. Treat its assessments as working hypotheses that require verification, especially where Convoy is scored favorably.

---

## Acceptance Criteria

The audit is complete when:

- [ ] RUBRIC.md exists with 1–5 anchor definitions for all 8 dimensions
- [ ] All three group reports exist with complete scoring tables and evidence notes
- [ ] COMPETITIVE-AUDIT.md exists with: unified 16-system table, closest competitors analysis, honest Spectrum assessment, and improvement recommendations
- [ ] TOP15-RANKING.md exists with justified selection of exactly 15 competitors
- [ ] Spectrum's weaknesses section contains at least 3 genuine limitations with competitive evidence (not "areas to improve" hedging)
- [ ] At least one dimension exists where a competitor scores higher than Spectrum, surfaced honestly
- [ ] No file outside the ownership matrix has been created or modified

---

## Notes for Gold (Muster)

**Reaping mode eligibility**: All 5 Howlers create new files only. No shared TypeScript interfaces. Tasks are independent within the parallel group (H2/H3/H4). Reaping mode is appropriate — skip ARCHITECTURE.md, full DAG, per-Howler DbC sections. Do include CHECKPOINT.json and LIGHT-MANIFEST.md.

**DAG structure**: H1 → (H2 ∥ H3 ∥ H4) → H5. H5 is the only sequential phase. H1 must signal STABLE before H2/H3/H4 start.

**H5 effort note**: H5 is significantly larger than H2/H3/H4. Flag as critical-path risk. If H5 approaches context limits, it may split into two passes: first produces the scoring table and closest-competitor analysis, second produces the honest assessment and recommendations.

**Prior survey as resource**: All Howlers should read the relevant sections of `evaluation/AGENTIC-LANDSCAPE.md` as their primary research source for systems already covered there. New entrants (Citadel, Overstory, metaswarm, Kiro agents, Factory, Windsurf) may require WebSearch to supplement the survey.

**Spectrum's self-description**: `README.md` and `spectrum/SPECTRUM-OPS.md` are the authoritative sources for what Spectrum claims to do. Use these as inputs to scoring, but apply the rubric's evidence standards (claims ≠ verified capability).
