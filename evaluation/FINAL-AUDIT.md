# Spectrum Protocol: Final Audit Synthesis

**Date**: 2026-03-30
**Methodology**: Five independent Howler reports cross-referenced and synthesized by Gold
**Confidence**: High overall; medium on market positioning (field moves fast)

---

## Executive Summary

- **The multi-agent coding landscape comprises 28+ systems across four categories** (Claude Code orchestrators, general-purpose frameworks, commercial autonomous agents, AI IDEs). The field is 15 months old. Everything is pre-2.0. No system exceeds 64% of the theoretical maximum score.

- **Spectrum leads the field in coordination rigor** -- failure taxonomy, contract management, merge planning, quality gates, and documentation are best-in-class by every report's assessment. This is not contested by any Howler.

- **Spectrum is invisible to the outside world.** When scored from public evidence alone, it places dead last at 26/150. The protocol has zero GitHub stars, zero external users, zero benchmarks, and zero third-party mentions. This is a publication problem, not a quality problem.

- **The honest position is: best coordination protocol for Claude Code parallel execution, not best multi-agent system overall.** Spectrum solves coordination problems that no other system addresses (file ownership matrices, frozen contracts with DbC, locus-tracked circuit breakers, adversarial plan review), but it operates in a niche of one -- Claude Code sub-agents -- with N=4 production runs by one person.

- **The field is converging on patterns Spectrum already implements**: spec-before-code, git worktree isolation, quality gates before merge, model routing by task complexity. These are validation that the design choices are correct, not evidence that Spectrum invented them.

- **Publication is warranted but positioning must be honest.** Lead with what it solves and how, not with rankings. The 2,300-line spec is simultaneously the protocol's greatest strength (exhaustive) and its biggest adoption barrier (overwhelming). A README, quick start guide, and one documented case study are prerequisites for credible publication.

- **Three capabilities are genuinely unique to Spectrum across all 28 systems surveyed**: Design-by-Contract per worker with formal pre/postconditions, adversarial plan review (Politico), and independent Gold validation of worker self-reports during integration. No other system -- open source, commercial, or research -- implements any of these.

---

## The Field

### Landscape Structure

The audit surveyed **28 systems** total:
- **12 Claude Code protocols/tools**: Gas Town, oh-my-claudecode, metaswarm, Overstory, Citadel, Ruflo, Agent-Orchestrator, Claude Code Agent Farm, Claude Squad, Anthropic Agent Teams, wshobson/agents, myclaude
- **16 external systems**: CrewAI, AutoGen/AG2, LangGraph, MetaGPT, Devin, Factory, OpenHands, Kiro, Cursor, OpenAI Codex, Google A2A/ADK, Microsoft Agent Framework, AWS Strands, Aider, Cline, Windsurf

### Category Breakdown

| Category | Count | Examples | Maturity |
|----------|-------|----------|----------|
| General-purpose frameworks | 4 | CrewAI (45.9k stars), LangGraph (28k), MetaGPT (64k) | Most mature; production deployments at scale |
| Commercial autonomous agents | 3 | Devin ($20/mo), Factory (enterprise), OpenHands (65k stars) | Funded, enterprise-validated |
| AI IDEs with agents | 4 | Cursor ($2B ARR), Kiro (AWS), Windsurf, Codex | Fastest-growing; parallel agents becoming table stakes |
| Claude Code orchestrators | 12 | Gas Town (13.3k), oh-my-claudecode (17.7k), Spectrum (0) | Youngest; 15 months old; high innovation, low maturity |
| Protocols/SDKs | 3 | A2A/ADK (17.2k), MS Agent Framework, AWS Strands | Standards-track; enterprise backing |
| CLI/extension agents | 2 | Aider, Cline (60k stars, 5M installs) | Single-agent; mature and widely adopted |

### Converging Patterns

All five Howler reports independently identified the same convergences:

1. **Git worktrees are the consensus isolation mechanism.** Every parallel agent system uses them. This is settled.
2. **Spec-before-code is winning.** Kiro, MetaGPT, Factory, and Spectrum all plan before executing. "Vibe coding" backlash is real.
3. **Model routing for cost control is becoming standard.** oh-my-claudecode, Augment Code, LangGraph, and Spectrum all route complex tasks to expensive models and mechanical tasks to cheap ones.
4. **Quality gates before merge are trending upward.** The question is how many layers, not whether to have them.
5. **No system has solved merge.** Overstory's 4-level conflict resolution is the most sophisticated attempt. Spectrum's PAX-PLAN.md with ordered merging and seam verification is the most documented attempt. Neither is complete.

### Unsolved Frontiers

Three problems remain open across all 28 systems:

1. **Cross-session architectural coherence** -- maintaining design decisions across weeks of agent sessions
2. **Formal verification of agent output** -- bridging "tests pass" to "this is correct"
3. **Multi-vendor agent coordination** -- mixing Claude, GPT, and Gemini agents in one workflow (Google A2A is the leading attempt)

---

## Spectrum's Position

### Where Spectrum Leads (high confidence)

These claims are supported by all five Howler reports without contradiction:

| Dimension | Evidence | Nearest Competitor |
|-----------|----------|-------------------|
| **Error recovery / failure taxonomy** | 5 classified failure types, 3 Erlang-style supervision strategies, locus-tracked circuit breaker | No competitor has typed failure classification for coding agents |
| **Contract management** | Frozen CONTRACT.md with Design-by-Contract per worker, adversarial Politico review, typed amendments | Kiro has mutable specs; no one else has frozen contracts |
| **Merge process** | PAX-PLAN.md with merge ordering, seam cross-reference, incremental integration testing | Overstory has 4-level conflict resolution but no seam verification |
| **Quality gates** | Triple gate (White + Gray + /diff-review) per worker, in parallel | metaswarm scores 9/10 on quality gates but uses a different approach (cross-model adversarial review) |
| **Documentation** | 2,300-line spec + 550-line ops manual; every phase, failure mode, and template documented | LangGraph and CrewAI have comparable documentation volume but for different domains |
| **File conflict prevention** | Ownership matrix verified at planning time by both Gold and Politico | Cursor and Codex use worktrees but allow file overlap; conflicts discovered at merge time |
| **Crash recovery** | CHECKPOINT.json + HOOK.md at every phase transition; resume-from-any-point | Gas Town's git-backed event logs are comparable; LangGraph has durable state |

### Where Spectrum is Competitive (medium confidence)

| Dimension | Spectrum | Leader | Gap |
|-----------|----------|--------|-----|
| Task decomposition | DAG-based with hazard scanning, effort estimation | MetaGPT/metaswarm (8/10 in scoring) | Spectrum's is more sophisticated but unscored due to invisibility |
| Agent specialization | 11 named roles with model routing (Opus/Sonnet/Haiku) | metaswarm (18 agents, cross-model) | Comparable approaches; metaswarm adds cross-model review |
| Human-in-the-loop | Manifest approval, PR review, merge confirmation | LangGraph (8/10), Kiro (spec-driven) | Spectrum operates at strategic level; Kiro at spec level |
| Scale | 3-8 Howlers with reaping mode for small jobs | Gas Town (20-30 agents), Cursor (8) | Gas Town scales higher; Spectrum prioritizes coordination quality |

### Where Spectrum Trails (high confidence)

| Dimension | Spectrum | Leaders | Severity |
|-----------|----------|---------|----------|
| **Ease of adoption** | 2,300-line spec, no README, no quick start | Cursor (9/10), oh-my-claudecode (9/10) | Critical -- adoption barrier is the biggest risk to relevance |
| **Platform portability** | Claude Code only | CrewAI, LangGraph, AutoGen (any LLM) | High -- limits addressable market to Claude Code users |
| **Community / ecosystem** | 0 stars, 0 external users, 0 third-party mentions | Cline (60k stars), CrewAI (45.9k) | Critical -- protocol is invisible |
| **Real-world validation** | 4 production runs, 1 user, 1 project type | Factory (MongoDB, EY, Zapier), Devin (67% PR merge rate) | Critical -- no benchmarks, no case studies |
| **Cost efficiency** | Model routing exists but no measured costs | oh-my-claudecode (30-50% token savings claimed) | Medium -- ceremony overhead unmeasured |
| **Real-time inter-agent communication** | Howlers fully isolated until completion | Agent Teams (peer-to-peer), AutoGen (GroupChat) | Medium -- limits mid-task knowledge sharing |
| **Visual monitoring** | Read markdown files; no dashboard | LangGraph (LangSmith), AutoGen Studio | Low -- adequate for 3-5 Howlers, limiting for 8 |

---

## The Blind Score Problem

### What Happened

howler-dimensions designed a 15-dimension evaluation framework and scored all 21 systems using **only publicly available evidence**. For fairness, it did not consult internal Spectrum documentation. The result: Spectrum scored **26/150 (1.7 average)**, dead last among all systems surveyed.

### What It Means

This is not a statement about Spectrum's quality. It is a statement about Spectrum's visibility. The scoring methodology was correct -- if you cannot verify a capability exists from public evidence, you cannot score it. Spectrum has:

- No GitHub repository
- No documentation site
- No npm/pip package
- No third-party reviews or mentions
- No conference talks or blog posts
- No benchmarks or case studies

A system that does not exist publicly cannot be evaluated publicly. The 26/150 score is what Spectrum deserves from an outsider's perspective today.

### The Gap

howler-spectrum, which had full access to the protocol, assessed Spectrum as leading in 7 of 15 dimensions. howler-leaders, working from a mix of internal knowledge and external research, ranked Spectrum #1 overall. howler-dimensions, working from public evidence only, ranked it last.

The gap between 26/150 (public) and the internal assessment is not a contradiction -- it is the cost of being unpublished. Every day Spectrum remains private, this gap persists.

### If Publicly Visible

If Spectrum were published with its current spec, a fair external scorer would likely assign scores in these ranges (based on what the spec documents and cross-referencing howler-spectrum's analysis):

| Dimension | Public Score | Estimated If Published | Rationale |
|-----------|-------------|----------------------|-----------|
| D1: Task Decomposition | 2 | 8-9 | DAG-based with hazard scanning, Politico review |
| D2: File Conflict Prevention | 2 | 9-10 | Ownership matrix at planning time, Politico verification |
| D3: Contract/Interface Management | 2 | 9-10 | Frozen DbC contracts, adversarial review, typed amendments |
| D4: State Persistence & Recovery | 2 | 8-9 | CHECKPOINT.json + HOOK.md, resume-from-any-point |
| D5: Error Recovery & Classification | 2 | 9-10 | 5-type classification, Erlang supervision, circuit breaker |
| D6: Quality Gates | 2 | 9-10 | Triple parallel gate, re-run after fixes |
| D7: Merge Process | 2 | 9-10 | PAX-PLAN.md, seam verification, incremental integration testing |
| D8: Agent Specialization | 2 | 8 | 11 roles, model routing, but agents are ephemeral |
| D9: Scale | 2 | 6-7 | 3-8 Howlers; reaping mode; lower than Gas Town's 20-30 |
| D10: Human-in-the-Loop | 2 | 7-8 | Strategic-level control, graduated autonomy |
| D11: Ease of Adoption | 1 | 3-4 | 2,300 lines, no README, no quick start (publishing alone does not fix this) |
| D12: Documentation Quality | 1 | 8-9 | Exhaustive spec + ops manual (but needs README and guide) |
| D13: Cost Efficiency | 2 | 6-7 | Model routing, reaping mode, but no measured costs |
| D14: Community & Ecosystem | 1 | 2-3 | Publication alone does not create community |
| D15: Real-World Validation | 1 | 3-4 | 4 runs, 1 user -- publishing does not add validation |
| **Total** | **26** | **~105-118** | **Avg: ~7.0-7.9** |

This estimate places Spectrum in the 70-79% range of the theoretical maximum -- above every currently surveyed system (Kiro leads at 96/150 = 64%). The caveat: dimensions D11, D14, and D15 will remain low until the protocol gains users, a community, and independent validation. The spec alone moves Spectrum from last to first on paper; sustained real-world use is required to make those scores credible.

---

## Comparative Scorecard

The master scorecard from howler-dimensions, with Spectrum's estimated-if-published scores annotated:

| System | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | D13 | D14 | D15 | Total | Avg |
|--------|----|----|----|----|----|----|----|----|----|----|-----|-----|-----|-----|-----|-------|-----|
| **Spectrum (est.)** | **9** | **9** | **9** | **8** | **9** | **9** | **9** | **8** | **7** | **8** | **3** | **8** | **6** | **2** | **3** | **~107** | **~7.1** |
| **Kiro** | 7 | 5 | 7 | 7 | 6 | 7 | 5 | 7 | 4 | 6 | 8 | 8 | 5 | 8 | 6 | **96** | **6.4** |
| **Factory** | 7 | 6 | 5 | 6 | 5 | 7 | 6 | 7 | 6 | 7 | 7 | 7 | 5 | 7 | 7 | **95** | **6.3** |
| **LangGraph** | 7 | 3 | 6 | 8 | 6 | 4 | 2 | 7 | 7 | 8 | 6 | 8 | 5 | 9 | 8 | **94** | **6.3** |
| **metaswarm** | 8 | 5 | 6 | 5 | 5 | 9 | 7 | 8 | 5 | 6 | 5 | 7 | 6 | 4 | 7 | **93** | **6.2** |
| **Devin** | 7 | 6 | 4 | 7 | 6 | 6 | 6 | 5 | 4 | 6 | 8 | 7 | 6 | 7 | 8 | **93** | **6.2** |
| **Cursor** | 6 | 7 | 3 | 5 | 4 | 4 | 5 | 5 | 7 | 6 | 9 | 7 | 6 | 9 | 8 | **91** | **6.1** |
| **Codex** | 5 | 7 | 4 | 5 | 4 | 5 | 5 | 5 | 6 | 7 | 8 | 7 | 5 | 8 | 6 | **87** | **5.8** |
| **Citadel** | 7 | 6 | 4 | 8 | 6 | 5 | 5 | 7 | 5 | 7 | 7 | 6 | 7 | 3 | 4 | **87** | **5.8** |
| **CrewAI** | 7 | 3 | 5 | 6 | 4 | 4 | 2 | 7 | 7 | 5 | 7 | 8 | 5 | 9 | 7 | **86** | **5.7** |
| **MetaGPT** | 8 | 5 | 7 | 4 | 5 | 6 | 4 | 8 | 5 | 4 | 6 | 7 | 5 | 7 | 5 | **86** | **5.7** |
| **oh-my-cc** | 6 | 6 | 3 | 4 | 3 | 4 | 5 | 7 | 7 | 5 | 9 | 6 | 7 | 8 | 5 | **85** | **5.7** |
| **Gas Town** | 7 | 6 | 4 | 8 | 5 | 4 | 5 | 6 | 6 | 6 | 5 | 6 | 4 | 6 | 5 | **83** | **5.5** |
| **Overstory** | 6 | 7 | 5 | 6 | 4 | 4 | 7 | 7 | 7 | 5 | 5 | 7 | 4 | 5 | 4 | **83** | **5.5** |
| **OpenHands** | 6 | 5 | 4 | 5 | 4 | 4 | 4 | 6 | 6 | 6 | 7 | 7 | 5 | 8 | 6 | **83** | **5.5** |
| **Agt-Orch** | 6 | 7 | 3 | 4 | 6 | 6 | 6 | 5 | 7 | 7 | 6 | 6 | 4 | 5 | 4 | **82** | **5.5** |
| **Ruflo** | 6 | 5 | 4 | 5 | 4 | 4 | 4 | 7 | 7 | 5 | 4 | 6 | 5 | 6 | 4 | **76** | **5.1** |
| **Agent Teams** | 6 | 7 | 4 | 3 | 3 | 3 | 5 | 5 | 5 | 5 | 7 | 6 | 4 | 7 | 5 | **75** | **5.0** |
| **AutoGen/AG2** | 6 | 2 | 4 | 4 | 3 | 3 | 1 | 6 | 6 | 6 | 6 | 6 | 4 | 7 | 5 | **69** | **4.6** |
| **ClaudeSquad** | 4 | 7 | 2 | 5 | 2 | 2 | 4 | 3 | 6 | 6 | 8 | 5 | 4 | 5 | 5 | **68** | **4.5** |
| **AgentFarm** | 5 | 6 | 3 | 4 | 3 | 4 | 4 | 4 | 8 | 4 | 5 | 5 | 3 | 4 | 5 | **67** | **4.5** |
| **Spectrum (public)** | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 2 | 1 | 1 | **26** | **1.7** |

**Reading the table**: Spectrum's estimated scores assume the spec is published and a reviewer can read it. They do not assume community adoption, benchmarks, or external validation -- those dimensions (D11, D14, D15) remain low because publishing a spec does not create a community or prove real-world results.

---

## What Spectrum Does That Nobody Else Does

Cross-referenced across all five Howler reports. An item appears here only if at least three reports independently confirmed its uniqueness.

### 1. Design-by-Contract per Worker (confirmed by 5/5 reports)

Each Howler receives formal preconditions (what must be true before starting), postconditions (what must be true when done), and invariants (what must never change) in CONTRACT.md. Traditional software engineering (Eiffel, Ada SPARK) uses DbC, but applying it to coordinate LLM workers is original. No other multi-agent system for LLM coding agents does this.

**Caveat (from howler-spectrum)**: The "Design-by-Contract" label is somewhat aspirational. Verification is Gold reading files and checking informally -- there are no formal proof obligations or automated postcondition checking beyond `tsc --noEmit`. The framing implies more rigor than the execution delivers.

### 2. Adversarial Plan Review (confirmed by 4/5 reports)

The Politico agent reviews Gold's decomposition before CONTRACT.md is frozen, specifically looking for file ownership gaps, contract ambiguities, and decomposition flaws. This is adversarial by design -- the reviewer's job is to find problems with the plan itself, not confirm it.

**Unique because**: CI/CD systems review code changes; no multi-agent system has a dedicated adversary for the task decomposition.

### 3. Independent Validation of Worker Self-Reports (confirmed by 4/5 reports)

During Pax (integration), Gold does not trust Howler debriefs. Gold reads 2-3 key files each Howler created/modified and verifies against CONTRACT.md postconditions. A Howler can claim `contract_compliance: full` but Gold will verify independently.

**Unique because**: metaswarm has validation steps but they rely on test results. Spectrum's Gold reads actual code against formal postconditions.

### 4. Locus-Tracked Circuit Breaker with Erlang Supervision (confirmed by 4/5 reports)

Failure tracking is per-file, not per-worker. Two failures on the same file auto-escalate from transient to structural regardless of individual failure classification. The supervision strategies (one-for-one, one-for-all, rest-for-one) are borrowed from Erlang/OTP.

**Unique because**: No other LLM agent system tracks failure loci or uses formal supervision strategies.

### 5. Compiler-Enforced Shared Types (confirmed by 3/5 reports)

For TypeScript projects, shared types are committed as `convoy-contracts.d.ts` before workers fork. `tsc --noEmit` catches contract violations at compile time. No other multi-agent system commits shared type declarations to the base branch before worker dispatch.

### 6. Structured YAML Debrief with Automated Seam Checking (confirmed by 3/5 reports)

Debriefs use machine-readable YAML frontmatter with typed seam declarations. Gold can algorithmically cross-reference seams between workers rather than relying on narrative reading.

---

## What We're Missing

Cross-referenced across all five reports. Items appear here only if at least two reports flagged the gap.

### Critical Gaps (adoption blockers)

| Gap | Who Does It Better | Impact |
|-----|-------------------|--------|
| **No public repository** | Everyone (even Ruflo with documented broken features has 28.7k stars) | Cannot be adopted, evaluated, or contributed to |
| **No README or quick start** | Cursor (start in minutes), Copilot (assign issue, get PR) | 2,300-line spec with no entry point overwhelms new users |
| **No benchmarks or case studies** | Devin (67% PR merge rate), Factory (MongoDB, EY, Zapier in production) | Cannot justify ceremony overhead without measured results |
| **Platform lock-in to Claude Code** | CrewAI, LangGraph, AutoGen (any LLM) | Limits addressable market to Claude Code users only |
| **No license** | All open-source systems have one | Cannot be legally adopted by others |

### Significant Gaps (competitive disadvantages)

| Gap | Who Does It Better | Impact |
|-----|-------------------|--------|
| **No real-time inter-agent communication** | Agent Teams (peer-to-peer), AutoGen (GroupChat), CrewAI (delegation) | Howlers cannot share mid-task discoveries |
| **No dynamic task rebalancing** | metaswarm, some AutoGen configs | Fast Howler cannot help slow one; frozen ownership |
| **No visual monitoring / dashboard** | LangGraph (LangSmith), AutoGen Studio, Overstory (TUI) | Monitoring 8 Howlers by reading markdown is limiting |
| **No incremental context management** | Devin (long-running sessions) | Howlers hit context limits and fail; recovery is reactive |
| **Ceremony overhead unmeasured** | oh-my-claudecode (zero-config), Claude Squad (session manager) | 8-minute muster for a 3-Howler run may not be worth it |

### Known Gaps Accepted by Design

| Gap | Why Accepted | howler-spectrum Assessment |
|-----|-------------|--------------------------|
| **Formal verification weak despite DbC framing** | No system does this well yet; field-wide limitation | "Claiming Design-by-Contract while relying on informal verification is an overstatement of rigor" |
| **Max 8 Howlers** | Coordination overhead dominates beyond 8; Gas Town's 20-30 is chaos-tolerant by design | Correct tradeoff for coordination quality |
| **Howler isolation (no mid-task messaging)** | Simplifies coordination; prevents cascading confusion | High impact but principled choice |

---

## Cross-Reference: Report Agreement and Contradictions

### Where All 5 Reports Agree

1. Spectrum's failure taxonomy and recovery protocol is the most sophisticated in the field
2. File ownership enforcement at planning time is genuinely unique
3. The protocol needs external validation, benchmarks, and better onboarding
4. The field is converging on patterns Spectrum implements (spec-before-code, worktrees, quality gates)
5. Platform lock-in to Claude Code is the biggest strategic limitation

### Where Reports Appear to Contradict

**Contradiction 1: howler-dimensions scored Spectrum 26/150; howler-leaders ranked it #1**

- **Resolution**: Not a contradiction. howler-dimensions scored from public evidence only (correct methodology -- fairness rule). howler-leaders had access to internal documentation and cross-referenced capability claims against the survey data. Both are accurate given their inputs. The gap IS the finding: Spectrum's internal quality far exceeds its external visibility.

**Contradiction 2: howler-spectrum said "publish as battle-tested protocol, not #1 system"; howler-leaders said "#1 overall"**

- **Resolution**: Partial contradiction. howler-leaders' #1 ranking is defensible on the coordination dimensions (D1-D7) where Spectrum genuinely leads. howler-spectrum's caution is defensible on the adoption dimensions (D11, D14, D15) where Spectrum is weakest. The honest framing is: "most complete coordination protocol" (true and verifiable from the spec) rather than "#1 multi-agent system" (requires external validation to be credible). howler-spectrum's recommendation is more defensible for publication positioning.

**Contradiction 3: howler-claude says "no system has solved merge"; howler-leaders says Spectrum leads merge process**

- **Resolution**: Compatible. Spectrum's merge process (PAX-PLAN.md, seam verification, incremental testing) is the most structured attempt, but "leads" and "solved" are different claims. Even the best merge process scores 9/10 at most -- the remaining gap (formal verification that merged output satisfies the spec) is an unsolved frontier for everyone.

### Report Quality Assessment

| Report | Completeness | Confidence |
|--------|-------------|------------|
| howler-claude (CLAUDE-PROTOCOLS.md) | Excellent -- 12 systems with deep analysis | High |
| howler-external (EXTERNAL-SYSTEMS.md) | Excellent -- 16 systems, four categories, comparative tables | High |
| howler-dimensions (SCORING-FRAMEWORK.md) | Excellent -- rigorous methodology, fair scoring, honest about Spectrum | High |
| howler-leaders (LEADERS-ANALYSIS.md) | Very good -- comprehensive analysis, slight optimism toward Spectrum in top-5 ranking | Medium-high (Spectrum #1 claim is defensible but requires caveat) |
| howler-spectrum (SPECTRUM-POSITION.md) | Excellent -- most honest and self-critical report; the skeptic's voice the audit needed | High |

No report was incomplete or contained factual errors detectable from cross-referencing.

---

## Publication Recommendation

### Publish: Yes

The protocol is complete, internally consistent, and solves real problems that no other system addresses. The four production runs (remnant-narrative, remnant-ux, remnant-infra, convoy-v3) produced specific lessons that are codified in the spec. This is not vaporware.

### Positioning: Honest and Specific

**Do say:**
- "A coordination protocol for parallel Claude Code sub-agents"
- "Addresses file ownership, contract management, failure recovery, and merge planning"
- "Battle-tested across 4 production runs with specific failure lessons codified"
- "The most documented multi-agent coordination protocol for LLM coding agents (2,300 lines)"

**Do not say:**
- "#1 multi-agent system" (not earned without external validation)
- "Best overall" (best coordination, but worst adoption and community)
- "Enterprise-grade" (N=4, 1 user, 1 project type)
- "Design-by-Contract" without caveat (verification is informal, not formal)

### Prerequisites Before Publication

1. **README.md** (2 pages) -- what it is, who it is for, how to start
2. **Quick Start Guide** -- "Run your first Spectrum on a sample project in 15 minutes"
3. **License** -- choose one and declare it
4. **One documented case study** -- timing, token costs, outcomes for one real run vs sequential baseline
5. **The seam_check.py script** -- referenced in ops manual but not included; readers cannot run the protocol without it

### Recommended Framing for the README

> **Spectrum** is a coordination protocol for running 3-8 parallel Claude Code sub-agents on a shared codebase without merge conflicts, lost state, or inconsistent implementations.
>
> It solves three problems:
> 1. **File conflicts** -- an ownership matrix at planning time ensures no two agents touch the same file
> 2. **Lost work** -- crash-recovery state (HOOK.md + CHECKPOINT.json) at every phase transition means you can resume from where you stopped
> 3. **Integration failures** -- frozen contracts, seam verification, and ordered merge planning catch mismatches before they reach main
>
> Spectrum requires Claude Code and works best on TypeScript projects with clear module boundaries. It has been tested on 4 production runs by its author. It is not yet validated by external users or benchmarks.

### What Success Looks Like (6 months post-publication)

- 5+ external users who have run a full Spectrum and filed issues or improvements
- 1 benchmark: time-to-complete and token cost for a defined task, Spectrum vs sequential execution
- 1 non-TypeScript case study (Python, React, or Go)
- Community contributions to CONTRACT.md templates or agent prompt improvements
- The 26/150 public score moves to 80+ as documentation, community, and validation materialize
