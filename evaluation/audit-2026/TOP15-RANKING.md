# TOP15-RANKING.md — Competitive Audit Ranked List
**Spectrum**: audit-2026-0331
**Howler**: H5-synthesis
**Date**: 2026-03-31

---

## Selection Methodology

From the 20 non-Spectrum systems scored across three group reports, 15 were selected for inclusion in the final competitive set. Selection criteria, per PLAN.md H5 Step 1:

1. **Relevance to multi-agent coding** — general-purpose reasoning systems with no coding-specific machinery are lower priority
2. **Evidence quality** — systems with well-documented behavior yield more reliable scores
3. **Category balance** — minimum 3 from each of: Claude Code ecosystem, general frameworks, commercial

Systems in all three groups were scored using RUBRIC.md v1.0. Scores are carried forward exactly from H2, H3, and H4 without re-scoring.

---

## Included: Top 15

### Rank by Relevance Score (Total + Category Weight)

Ranking is by aggregate score as a proxy for overall competitiveness, with ties broken by evidence quality and category diversity.

| Rank | System | Category | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | Total | Inclusion Rationale |
|------|--------|----------|----|----|----|----|----|----|----|----|----|-------|---------------------|
| 1 | Citadel | Claude Code | 3 | 4 | 2 | 4 | 3 | 4 | 4 | 3 | 27 | Closest documented protocol peer to Spectrum; circuit breaker, campaign persistence, worktree isolation; strong evidence base |
| 2 | Gas Town | Claude Code | 3 | 5 | 2 | 3 | 3 | 3 | 2 | 5 | 26 | Primary open-source Claude Code alternative; only system designed for 20-30+ agents; direct architectural counterpoint to Spectrum |
| 3 | LangGraph | Frameworks | 4 | 3 | 2 | 3 | 5 | 3 | 3 | 3 | 26 | Strongest observability in the field (LangSmith); state management leader; most widely-adopted graph-based framework |
| 4 | Overstory | Claude Code | 3 | 4 | 2 | 3 | 4 | 3 | 3 | 4 | 26 | Pull-based architecture with tiered watchdog; strongest observability among Claude Code ecosystem systems |
| 5 | metaswarm | Claude Code | 3 | 3 | 2 | 4 | 2 | 4 | 3 | 3 | 24 | Closest competitor by Euclidean distance; adversarial review pattern; production-validated across hundreds of PRs |
| 6 | CrewAI | Frameworks | 4 | 4 | 2 | 2 | 3 | 2 | 4 | 3 | 24 | Largest OSS adoption (44k stars); event-driven Flow execution; industry adoption baseline |
| 7 | Factory | Commercial | 3 | 3 | 3 | 3 | 3 | 2 | 4 | 3 | 24 | Terminal Bench #1 (58.75%); milestone orchestration; cloud-native multi-Droid execution; best-evidenced commercial mid-tier |
| 8 | OpenAI Agents SDK | Frameworks | 4 | 3 | 2 | 2 | 4 | 2 | 5 | 3 | 25 | Official OpenAI framework; near-zero setup (D7=5); full tracing out of box; widely adopted as the baseline SDK |
| 9 | Augment Code/Intent | Commercial | 2 | 3 | 4 | 3 | 2 | 2 | 4 | 3 | 23 | Highest D3 accuracy in commercial group (70.6% SWE-bench); Coordinator/Specialist/Verifier role model; 400k file context |
| 10 | Devin | Commercial | 2 | 4 | 2 | 2 | 3 | 2 | 5 | 3 | 23 | Managed Devins; isolated VM parallelism; most-discussed commercial coding agent; reference point for the category |
| 11 | Cursor agents | Commercial | 2 | 4 | 3 | 2 | 2 | 2 | 5 | 3 | 23 | 8-agent parallel background execution; dominant IDE adoption; cost pressure is a documented data point |
| 12 | Agent Teams (Anthropic) | Claude Code | 3 | 4 | 3 | 2 | 2 | 2 | 4 | 3 | 23 | Official Anthropic product; native TeammateTool; research preview status means this will grow in relevance |
| 13 | oh-my-claudecode | Claude Code | 3 | 4 | 2 | 2 | 2 | 2 | 5 | 3 | 23 | Zero-config design (D7=5); Ultrapilot mode; represents the "ease of use" pole that Spectrum explicitly cedes |
| 14 | AutoGen / AG2 | Frameworks | 4 | 3 | 2 | 2 | 3 | 2 | 3 | 3 | 22 | Microsoft Research provenance; event-driven async rearchitecture; Captain Agent ledger; widely studied |
| 15 | GitHub Copilot Workspace | Commercial | 3 | 2 | 4 | 2 | 3 | 2 | 5 | 1 | 22 | 55-56% SWE-bench Verified (D3=4); auditable pipeline; most-used commercial coding tool by developer count |

---

## Excluded: 5 Systems (with Rationale)

| System | Total | Exclusion Rationale |
|--------|-------|---------------------|
| MetaGPT | 20 | Waterfall-sequential architecture; no multi-agent parallelism path; academic system without production multi-agent use |
| ChatDev | 19 | Fixed-role waterfall pipeline; no parallel dispatch; 2024-vintage architecture superseded by systems above |
| CAMEL-AI | 18 | Research framework for peer-to-peer reasoning; not a coding-specific system; peer-to-peer topology is the worst scaling pattern per Google/MIT research |
| Amazon Q Developer | 20 | No multi-agent architecture (sub-agents are user-invoked sequentially); AWS ecosystem lock-in limits general relevance; D8=1 |
| Windsurf | 22 | Wave 13 parallel agents are newly launched (December 2025) with minimal evidence base; no SWE-bench result; evidence too thin for reliable scoring relative to better-evidenced alternatives at the same total |

**Note on Windsurf**: Windsurf's exclusion is close — its total of 22 matches GitHub Copilot Workspace. The deciding factor is evidence quality: Copilot Workspace has a published 55-56% SWE-bench Verified score and mature documentation; Windsurf's D3=2 reflects absence of any published benchmark. If Windsurf publishes a SWE-bench result, it merits inclusion in a future audit cycle.

---

## Category Balance Check

| Category | Included | Required minimum |
|----------|----------|-----------------|
| Claude Code ecosystem | 6 (Citadel, Gas Town, Overstory, metaswarm, Agent Teams, oh-my-claudecode) | 3 |
| General frameworks | 4 (LangGraph, CrewAI, OpenAI Agents SDK, AutoGen/AG2) | 3 |
| Commercial | 5 (Factory, Augment Code/Intent, Devin, Cursor agents, GitHub Copilot Workspace) | 3 |

All three minimum thresholds satisfied.
