# COMPETITIVE-EVAL-V2.md — 2026 Multi-Agent Coding Systems Evaluation
**Spectrum**: eval-v2-0331
**Howler**: H4-synthesis
**Date**: 2026-03-31
**Rubric version**: evaluation/eval-v2/PLAN.md v2.0
**Prior audit**: evaluation/audit-2026/COMPETITIVE-AUDIT.md (audit-2026-0331)

---

## 1. Unified Scoring Table

Scores carried forward exactly from group reports (group-claude-code.md, group-frameworks.md, group-commercial.md). No re-scoring by H4. MetaGPT excluded from this table (included in group-frameworks.md for reference; excluded from Top 15 per PLAN.md §Scope and prior audit precedent).

| System | D1 Cost | D2 Efficiency | D3 Accuracy | D4 Workflow Rigor | D5 Security | D6 Quality Checks | D7 Setup | D8 Scalability | **Total** |
|--------|---------|---------------|-------------|-------------------|-------------|-------------------|----------|----------------|-----------|
| Spectrum Protocol | 2 | 4 | 2 | 5 | 2 | 5 | 3 | 3 | **26** |
| Citadel | 3 | 4 | 2 | 4 | 2 | 3 | 4 | 3 | **25** |
| Gas Town | 3 | 5 | 2 | 3 | 2 | 2 | 2 | 5 | **24** |
| metaswarm | 3 | 3 | 2 | 4 | 2 | 4 | 3 | 3 | **24** |
| Overstory | 3 | 4 | 2 | 3 | 2 | 2 | 3 | 4 | **23** |
| Agent Teams (Anthropic) | 3 | 4 | 3 | 2 | 2 | 2 | 4 | 3 | **23** |
| oh-my-claudecode | 3 | 4 | 2 | 2 | 1 | 1 | 5 | 3 | **21** |
| LangGraph | 4 | 3 | 2 | 3 | 1 | 2 | 3 | 3 | **21** |
| CrewAI | 4 | 4 | 2 | 2 | 2 | 2 | 4 | 3 | **23** |
| OpenAI Agents SDK | 4 | 3 | 3 | 2 | 4 | 3 | 5 | 3 | **27** |
| AutoGen / AG2 | 4 | 3 | 2 | 2 | 2 | 2 | 3 | 3 | **21** |
| Devin | 2 | 4 | 2 | 2 | 3 | 3 | 5 | 3 | **24** |
| Cursor agents | 2 | 4 | 3 | 2 | 4 | 3 | 5 | 3 | **26** |
| Augment Code/Intent | 2 | 3 | 4 | 3 | 3 | 4 | 4 | 3 | **26** |
| GitHub Copilot Workspace | 3 | 2 | 4 | 2 | 5 | 4 | 5 | 1 | **26** |
| Factory | 3 | 3 | 3 | 3 | 4 | 4 | 4 | 3 | **27** |

**Dimension key**: D1=Cost (5=cheapest), D2=Efficiency (speed + overhead ratio), D3=Accuracy (benchmark results), D4=Workflow Rigor (contracts, failure taxonomy, circuit breaker, adversarial review), D5=Security (SAST, sandboxing, security review, injection protection), D6=Quality Checks (test execution, review gates, spec compliance, coverage), D7=Setup (5=easiest), D8=Scalability (agent count ceiling, coordination overhead)

**Source reports**: group-claude-code.md (H1), group-frameworks.md (H2), group-commercial.md (H3)

---

## 2. Rankings

All 16 systems (15 Top-15 competitors + Spectrum) ranked by v2 total score.

| Rank | System | Total | v1 Total | Delta | Notable |
|------|--------|-------|----------|-------|---------|
| 1 | OpenAI Agents SDK | 27 | 25 | +2 | |
| 1 | Factory | 27 | 24 | +3 | Notable mover |
| 3 | **Spectrum Protocol** | **26** | **25** | **+1** | **Spectrum: 3rd place (tied)** |
| 3 | Cursor agents | 26 | 23 | +3 | Notable mover |
| 3 | Augment Code/Intent | 26 | 23 | +3 | Notable mover |
| 3 | GitHub Copilot Workspace | 26 | 22 | +4 | Notable mover |
| 7 | Citadel | 25 | 27 | -2 | |
| 8 | Gas Town | 24 | 26 | -2 | |
| 8 | metaswarm | 24 | 24 | 0 | |
| 8 | Devin | 24 | 23 | +1 | |
| 11 | Overstory | 23 | 26 | -3 | Notable mover |
| 11 | Agent Teams (Anthropic) | 23 | 23 | 0 | |
| 11 | CrewAI | 23 | 24 | -1 | |
| 14 | oh-my-claudecode | 21 | 23 | -2 | |
| 14 | LangGraph | 21 | 26 | -5 | Notable mover |
| 14 | AutoGen / AG2 | 21 | 22 | -1 | |

**Spectrum's position**: 3rd (tied) in v2, up from 4th in v1. However, the tie group at 3rd expanded — four systems now share the 26-point tier. Spectrum is the only open-source Claude Code ecosystem system above 25 points.

**Notable change threshold**: Systems with delta ≥ 3 or ≤ -3 are flagged. Five systems qualify: Factory (+3), Cursor agents (+3), Augment Code/Intent (+3), GitHub Copilot Workspace (+4), LangGraph (-5), Overstory (-3).

---

## 3. Closest Competitors

### Euclidean Distance from Spectrum

Normalized per rubric: `(score − 1) / 4`, then Euclidean distance = `√Σ(Δ_dim²)`.

| Rank | System | Distance | Notes |
|------|--------|----------|-------|
| 1 | **metaswarm** | **0.500** | Closest competitor |
| 2 | **Citadel** | **0.661** | Second closest |
| 3 | **Augment Code/Intent** | **0.866** | Third closest |
| 4 | Factory | 0.901 | — |
| 5 | Overstory | 0.968 | — |
| 6 | LangGraph | 1.090 | — |
| 6 | Devin | 1.061 | — |
| 8 | Gas Town | 1.118 | — |
| 9 | Agent Teams | 1.146 | — |
| 10 | Cursor agents | 1.173 | — |

Note: The prior audit's third-closest competitor was Overstory (distance 0.750). In v2, Augment Code/Intent moves to third closest (0.866), and Overstory falls to fifth (0.968). The shift is driven by Overstory's -3 total score drop (D6=2 replacing higher prior D6) pulling it away from Spectrum's profile.

---

### Closest Competitor #1: metaswarm (distance 0.500)

| Dimension | Spectrum | metaswarm | Delta |
|-----------|----------|-----------|-------|
| D1 Cost | 2 | 3 | metaswarm +1 |
| D2 Efficiency | **4** | 3 | Spectrum +1 |
| D3 Accuracy | 2 | 2 | same |
| D4 Workflow Rigor | **5** | 4 | Spectrum +1 |
| D5 Security | 2 | 2 | same |
| D6 Quality Checks | **5** | 4 | Spectrum +1 |
| D7 Setup | 3 | 3 | same |
| D8 Scalability | 3 | 3 | same |

**Why they're close**: metaswarm and Spectrum share the same philosophical position — coordination-heavy frameworks that trade raw throughput for workflow discipline. They match exactly on D3 (no benchmark), D5 (local host execution, no sandboxing), D7, and D8. Both mandate adversarial review before code merges; both enforce blocking quality gates. Both document circuit-breaker-style escalation on repeated failure. Five of eight dimensions are identical.

**Where they diverge**: Spectrum leads on D2 (4 vs. 3) because Nano mode pushes small-run wall-clock time under five minutes, where metaswarm's mandatory 9-phase workflow and blocking phase transitions create structural overhead regardless of run size. Spectrum leads on D4 (5 vs. 4) due to the formal 5-tier failure taxonomy — metaswarm's retry path does not distinguish failure types. Spectrum leads on D6 (5 vs. 4) because it adds Obsidian post-merge spec compliance verification and independent Gold Pax validation against CONTRACT.md postconditions; metaswarm has no dedicated post-merge compliance check. metaswarm leads on D1 (3 vs. 2) — its cost profile is lower because it lacks the Gold muster phase; the adversarial review in metaswarm is per-retry, not a separate pre-execution phase that consumes orchestration tokens before any work begins.

**Developer trade-off**: A developer choosing metaswarm over Spectrum gets lower cost and a simpler conceptual model (9 phases vs. 7 Spectrum phases plus 6 agent roles). They give up Nano mode's speed advantage for small runs, Spectrum's failure taxonomy, and post-merge spec verification. metaswarm's 100% coverage enforcement via `.coverage-thresholds.json` is machine-verified — a genuine advantage over Spectrum's LLM-instruction-enforced quality gates. For developers who want enforced TDD coverage and a single adversarial review model without the muster ceremony overhead, metaswarm is the correct choice.

---

### Closest Competitor #2: Citadel (distance 0.661)

| Dimension | Spectrum | Citadel | Delta |
|-----------|----------|---------|-------|
| D1 Cost | 2 | 3 | Citadel +1 |
| D2 Efficiency | 4 | 4 | same |
| D3 Accuracy | 2 | 2 | same |
| D4 Workflow Rigor | **5** | 4 | Spectrum +1 |
| D5 Security | 2 | 2 | same |
| D6 Quality Checks | **5** | 3 | Spectrum +2 |
| D7 Setup | 3 | **4** | Citadel +1 |
| D8 Scalability | 3 | 3 | same |

**Why they're close**: Citadel and Spectrum are the two most rigor-conscious systems in the Claude Code ecosystem. Both share D2=4 (genuine parallel execution with managed overhead), D3=2 (no published benchmark), D5=2 (local host execution without sandboxing), and D8=3 (moderate scalability ceiling). Spectrum's README explicitly acknowledges Citadel in its acknowledgments. Both employ circuit breakers, structured state persistence (HOOK.md / campaign persistence), and orchestrator oversight with distinct roles.

**Where they diverge**: The largest gap is D6 (5 vs. 3) — Spectrum's triple quality gate (White + Gray + /diff-review) is blocking with zero-failures required before any PR opens, plus post-merge Obsidian spec compliance. Citadel's D6=3 reflects circuit breaker and lifecycle hooks that prevent failure spirals without implementing dedicated test execution or spec compliance verification. Spectrum also leads on D4 (5 vs. 4) because the Politico adversarial review phase has no equivalent in Citadel's documented architecture. Citadel leads on D1 (3 vs. 2) because it lacks Spectrum's Gold muster overhead. Citadel leads on D7 (4 vs. 3) due to plugin-based installation.

**Developer trade-off**: Choosing Citadel over Spectrum delivers lower cost, easier setup, and no learning curve from a 550-line ops manual. The trade-off is giving up Spectrum's comprehensive quality gate pipeline and Politico's adversarial CONTRACT.md review. Citadel's "machine-verifiable phase conditions" claim suggests mechanistic enforcement strength; if this is substantiated with evidence, it would narrow the D4 gap. The current evidence does not yet confirm it.

---

### Closest Competitor #3: Augment Code/Intent (distance 0.866)

| Dimension | Spectrum | Augment Code/Intent | Delta |
|-----------|----------|---------------------|-------|
| D1 Cost | 2 | 2 | same |
| D2 Efficiency | **4** | 3 | Spectrum +1 |
| D3 Accuracy | 2 | **4** | Augment Code/Intent +2 |
| D4 Workflow Rigor | **5** | 3 | Spectrum +2 |
| D5 Security | 2 | **3** | Augment Code/Intent +1 |
| D6 Quality Checks | **5** | 4 | Spectrum +1 |
| D7 Setup | 3 | **4** | Augment Code/Intent +1 |
| D8 Scalability | 3 | 3 | same |

**Why they're close**: Augment Code/Intent enters the top-3 closest competitors (previously Overstory held this position) primarily because of cost and scalability alignment (D1=2, D8=3). Both systems cost approximately the same per representative run, both cap practical parallelism at 3-4 agents, and both have a multi-agent architecture with named agent roles (Coordinator/Specialist/Verifier vs. Gold/Howlers/White/Gray/Obsidian). Both enforce a dedicated verification/review phase before code is considered complete.

**Where they diverge**: Augment Code leads on D3 (4 vs. 2) — its base SWE-Bench agent achieves 70.6% on SWE-Bench Verified, the strongest accuracy evidence in this evaluation. Spectrum has no published benchmark. Augment Code leads on D5 (3 vs. 2) because the Context Engine incorporates SAST security scanning and the platform holds ISO/IEC 42001 certification. Spectrum leads on D4 (5 vs. 3) — Spectrum's pre-execution CONTRACT.md with per-Howler preconditions/postconditions and Politico adversarial review have no equivalent in Intent's architecture; the Verifier role is ongoing verification, not pre-execution contract enforcement. Spectrum leads on D6 (5 vs. 4) because it adds the Obsidian post-merge spec compliance phase and independent Gold Pax validation; Intent's Verifier role is strong but does not produce a dedicated post-merge SENTINEL-REPORT.md.

**Developer trade-off**: Augment Code/Intent is the right choice for developers who need published accuracy guarantees (70.6% SWE-Bench) and a managed commercial platform with ISO governance. It is a macOS desktop app with GitHub/Linear/Sentry integrations — optimized for product development workflows. Spectrum is the right choice for developers who need audit-trail-quality coordination artifacts (CONTRACT.md, CHECKPOINT.json, HOOK.md, MANIFEST.md) and formal failure classification. Spectrum's workflow rigor is unmatched; Augment Code's accuracy is unmatched among systems with comparable cost profiles.

---

## 4. Delta from Prior Audit

### Score Delta Table (all 15 systems)

| System | v1 Total | v2 Total | Delta | Primary Drivers |
|--------|----------|----------|-------|-----------------|
| GitHub Copilot Workspace | 22 | 26 | **+4** | D5 Security 3→5 (CodeQL + Advisory DB + secret scanning + Copilot Code Review); D6 Quality Checks new (4) |
| Factory | 24 | 27 | **+3** | D5 Security new (4, DroidShield + cloud VM); D6 Quality Checks new (4, four-phase Spec→Test→Implement→Verify) |
| Cursor agents | 23 | 26 | **+3** | D5 Security new (4, OS-level sandboxing + Bugbot); D6 Quality Checks new (3) |
| Augment Code/Intent | 23 | 26 | **+3** | D5 Security new (3); D6 Quality Checks new (4, Verifier blocking gate) |
| OpenAI Agents SDK | 25 | 27 | **+2** | D3 Accuracy 2→3 (Codex Security benchmark evidence); D5 Security new (4); D6 Quality Checks new (3) |
| Devin | 23 | 24 | **+1** | D5 Security new (3); D6 Quality Checks new (3, Devin Review + CI iteration) |
| **Spectrum Protocol** | **25** | **26** | **+1** | D2 Efficiency 3→4 (Nano mode); D5 Security new (2); D6 Quality Checks new (5, triple gate + Obsidian) |
| metaswarm | 24 | 24 | 0 | D5/D6 replace D5 Obs=2/D6 Recovery=4; new D5=2, D6=4; net neutral |
| Agent Teams (Anthropic) | 23 | 23 | 0 | D5/D6 replace D5 Obs=2/D6 Recovery=2; new D5=2, D6=2; net neutral |
| CrewAI | 24 | 23 | **-1** | D5 Security new (2) replaces D5 Obs=3; net -1 |
| AutoGen / AG2 | 22 | 21 | **-1** | D5 Security new (2) replaces D5 Obs=3; net -1 |
| Citadel | 27 | 25 | **-2** | D5 Security new (2) replaces D5 Obs=3; D6 Quality Checks new (3) replaces D6 Recovery=4 |
| Gas Town | 26 | 24 | **-2** | D5 Security new (2) replaces D5 Obs=3; D6 Quality Checks new (2) replaces D6 Recovery=3 |
| oh-my-claudecode | 23 | 21 | **-2** | D5 Security new (1) replaces D5 Obs=2; D6 Quality Checks new (1) replaces D6 Recovery=2 |
| Overstory | 26 | 23 | **-3** | D5 Security new (2) replaces D5 Obs=4; D6 Quality Checks new (2) replaces D6 Recovery=3 |
| LangGraph | 26 | 21 | **-5** | D5 Security new (1, three active CVEs including CVSS 9.3 critical) replaces D5 Obs=5; D6 Quality Checks new (2) replaces D6 Recovery=3 |

### Analysis of the Five Largest Movers

**GitHub Copilot Workspace (+4)**: The largest gainer. Its deep integration with GitHub's security infrastructure — CodeQL, Advisory Database, secret scanning, and Copilot Code Review all run automatically on every coding agent task — translates directly into D5=5, the highest security score in this evaluation. The prior D5 Observability dimension gave Copilot Workspace no particular advantage; the new Security dimension reveals its genuine structural strength. D8=1 (no parallelism) remains a hard ceiling on its total.

**Factory (+3) / Cursor agents (+3) / Augment Code/Intent (+3)**: All three commercial systems benefited from the new dimensions for the same reason — commercial products with cloud VM execution and dedicated security/quality engineering teams score higher on D5 Security and D6 Quality Checks than local-execution open-source systems. Factory's DroidShield SAST and four-phase quality loop, Cursor's OS-level agent sandboxing and Bugbot, and Augment Code's Verifier architecture each score 3-4 on both new dimensions. The prior audit's D5 Observability and D6 Recovery dimensions systematically underweighted commercial systems' infrastructure investments.

**LangGraph (-5)**: The largest loser. LangGraph scored D5=5 on Observability (LangSmith's dashboard and trace export were the best in the field). Under Security, it scores D5=1 — three active CVEs disclosed March 2026, including a CVSS 9.3 critical deserialization injection and a SQL injection in the SQLite checkpoint implementation. High observability and active critical vulnerabilities coexist without contradiction; the rubric change exposed this gap. The drop from 26 to 21 moves LangGraph from 4th to 14th.

**Overstory (-3)**: Overstory's D5=4 Observability score (driven by the `trace` command and per-agent cost breakdown) was its distinguishing feature in v1. The new Security dimension gives it D5=2 (local host execution, no sandboxing, no SAST). Its D6=2 Quality Checks (architecture focused on execution orchestration rather than quality gates) replaces D6=3 Recovery. Combined, the two new dimensions cost Overstory 3 points net — consistent with other Claude Code ecosystem systems whose prior D5/D6 scores were higher than their new Security/Quality Checks scores.

**Spectrum Protocol (+1)**: Spectrum's gain is modest by comparison. D2 Efficiency moved from 3 to 4 on the strength of Nano mode (sub-1-minute overhead for 2-3 Howler runs). The new D6 Quality Checks produces a score of 5 — the highest in this evaluation — because Spectrum's triple quality gate (White + Gray + /diff-review, all blocking) plus Obsidian post-merge spec compliance satisfies more D6 components than any competitor. The new D5 Security score of 2 is held back by local-host execution without sandboxing, consistent with all other Claude Code ecosystem systems. The net +1 is the smallest gain among systems that improved — Spectrum's pre-existing rigor was already capturing dimensions that the v2 rubric formalizes.

---

## 5. Spectrum: Honest Assessment

### Strengths with Evidence

**D4 Workflow Rigor — Score 5, sole leader across all 16 systems**

Spectrum is the only system in this evaluation to document all four D4=5 components as enforced protocol elements: (a) pre-execution CONTRACT.md with per-Howler preconditions, postconditions, and invariants; (b) formal failure taxonomy — 5 distinct types (transient, logical, structural, environmental, conflict) with different handling paths; (c) circuit breaker — 2 failures on the same locus auto-escalates to structural, Gold pauses and escalates to human; (d) independent adversarial review — Politico challenges CONTRACT.md and MANIFEST.md before freeze, with no remaining blockers permitted. No competitor reaches D4=5. Citadel and metaswarm are at D4=4.

The caveat applies: for a CLAUDE.md-based protocol, enforcement means LLM instruction adherence, not machine verification. This is a genuine qualifier on the score, and metaswarm's machine-enforced `.coverage-thresholds.json` represents a stronger constraint on its specific quality dimension than Spectrum's LLM-instructed quality gates represent on theirs.

**D6 Quality Checks — Score 5, tied for highest in this evaluation**

Spectrum's triple quality gate (White code review, zero blockers required; Gray test runner, zero failures required; /diff-review security review, zero security criticals required) blocks PR opening on failure. This is 3 of 4 D6=5 components as fully blocking gates. The fourth — post-merge spec compliance — is covered by Obsidian's SENTINEL-REPORT.md (Phase 6) and Gold Pax independent validation against CONTRACT.md postconditions (Phase 5). No other system in the Top 15 implements an equivalent post-merge spec compliance verification agent. Factory (D6=4) and GitHub Copilot Workspace (D6=4) are the closest competitors; neither includes a post-merge acceptance-criteria verification agent. Augment Code/Intent's Verifier (D6=4) is ongoing verification during execution, not a post-merge audit.

**D2 Efficiency — Score 4, improved from v1**

Nano mode (introduced post-v1) targets muster + drop in under 1 minute for 2-3 Howler runs. A 3-Howler Nano run completes wall-clock in under 5 minutes total — matching the D2=4 anchor. Full-mode 8-Howler runs remain slower (8+ minutes muster plus human approval gate), but Nano and Reaping modes represent the majority of practical Spectrum use cases. The prior D2=3 score reflected full-mode only; the updated score reflects the mode mix available to users. Gas Town (D2=5) and oh-my-claudecode/Cursor/Agent Teams/Overstory (D2=4) remain competitive or equivalent.

---

### Weaknesses with Evidence — Competitor Names and Specific Dimensions

**D1 Cost — Score 2, the lowest score among open-source systems**

Spectrum remains at D1=2 despite the Gold→Sonnet migration. The updated 5-Howler full-mode cost estimate is approximately $6.06 (recalculated from TOKEN-OPTIMIZATION.md after removing Opus-Gold premium). This is still within the D1=2 anchor ($2-$10/run). Every other open-source system in this evaluation scores D1=3 or higher: Gas Town (3), metaswarm (3), oh-my-claudecode (3), Agent Teams (3), Citadel (3), Overstory (3), LangGraph (4), CrewAI (4), OpenAI Agents SDK (4), AutoGen/AG2 (4). Nano mode reaches approximately $1.50-$2.00 per run (D1=3 territory), but the representative 5-Howler full-mode case anchors the score. Spectrum is structurally more expensive than every open-source alternative because the muster ceremony — the source of D4=5 — consumes orchestration tokens before any Howler executes.

**D3 Accuracy — Score 2, behind Augment Code/Intent (4), GitHub Copilot Workspace (4), Cursor agents (3), OpenAI Agents SDK (3), Factory (3), Agent Teams (3)**

No published SWE-Bench result exists for Spectrum Protocol. Augment Code/Intent's base agent achieves 70.6% on SWE-Bench Verified — the highest in this evaluation. GitHub Copilot Workspace reports 55-56% from multiple sources. Factory's Droids achieved #1 on Terminal Bench at 58.75%. Cursor agents are associated with model-level evidence of ~56%. Spectrum's coordination rigor may improve accuracy on multi-file parallel tasks, but this remains an untested hypothesis. Under the rubric's missing-evidence rule, D3=2 applies. This is the most damaging gap for Spectrum's competitive credibility — it cannot be resolved by protocol documentation.

**D5 Security — Score 2, behind GitHub Copilot Workspace (5), OpenAI Agents SDK (4), Factory (4), Cursor agents (4), Augment Code/Intent (3), Devin (3)**

Spectrum runs in local git worktrees on the host machine. There is no sandboxing — this is a structural characteristic of Claude Code orchestrators that run locally. The /diff-review security gate is a genuine security-focused review step, but it is LLM-based code review, not automated SAST. GitHub Copilot Workspace runs automated CodeQL, Advisory Database scanning, and secret scanning on every coding agent task by default — a capability Spectrum does not have and cannot replicate without tool integration. Factory's DroidShield provides real-time static analysis before code is committed. Cursor's OS-level sandboxing (Apple Seatbelt on macOS, Landlock + seccomp on Linux) operates at a level that local git worktrees do not approach.

**D7 Setup — Score 3, behind oh-my-claudecode (5), OpenAI Agents SDK (5), Devin (5), Cursor agents (5), GitHub Copilot Workspace (5), Agent Teams (4), Citadel (4), CrewAI (4), Augment Code/Intent (4), Factory (4)**

The setup burden is inherent to Spectrum's complexity: SPECTRUM-OPS.md (~550 lines), SPECTRUM.md (~2,300 lines), multiple agent definition files, and a 7-phase protocol with 6 named agent roles. Nano mode reduces ceremony for experienced users but does not reduce the first-run learning curve. Five systems score D7=5. The README's own framing acknowledges this: "Not For: Zero-config quick start — use oh-my-claudecode."

---

### Use Cases Where Spectrum Is Right

1. **High-stakes parallel coding where file conflicts are expensive**: CONTRACT.md + file ownership matrix + Politico adversarial review prevents interface mismatches before they happen. No competitor in this evaluation provides pre-execution adversarial review of decomposition and ownership decisions.

2. **Runs requiring formal failure classification**: The 5-tier failure taxonomy (transient/logical/structural/environmental/conflict) with distinct handling paths is unmatched. For expensive parallel runs where re-work cost is high, knowing whether a failure is transient (auto-resume) or structural (requires re-planning) before acting saves both tokens and time.

3. **Teams needing full coordination audit trails**: CHECKPOINT.json, HOOK.md, MANIFEST.md, CONTRACT.md, and per-PR debrief artifacts create a complete paper trail. For team environments, regulated industries, or post-mortems, Spectrum produces more structured coordination artifacts than any competitor.

4. **3-8 agent runs of medium complexity with clear interface boundaries**: The DAG-based dispatch and per-Howler scope management is well-matched to features spanning 3-8 logical components. This is the documented sweet spot.

---

### Use Cases Where Spectrum Is Wrong

1. **Time-critical work or quick-turn tasks**: Even with Nano mode, full-mode Spectrum's 8+ minute muster plus human approval gate makes it slower to start than oh-my-claudecode, Agent Teams (Anthropic), or Cursor agents. If the task can be completed in under 30 minutes, the muster overhead is disproportionate.

2. **Teams on tight token budgets**: At $6.06 for a 5-Howler full-mode run, Spectrum is more expensive than every open-source alternative. Citadel, metaswarm, Gas Town, and LangGraph all deliver parallel execution at D1=3 cost or better.

3. **When a published accuracy guarantee is required**: Augment Code/Intent publishes 70.6% SWE-Bench Verified. GitHub Copilot Workspace publishes 55-56%. Spectrum publishes nothing. Teams evaluating on benchmark evidence cannot place Spectrum in the top tier.

4. **Large-scale (20+ agent) parallel execution**: Spectrum explicitly documents the 8-agent ceiling. Gas Town (D8=5) is the correct choice for swarm-scale execution.

5. **Zero-configuration environments**: oh-my-claudecode, OpenAI Agents SDK, Devin, Cursor agents, and GitHub Copilot Workspace all score D7=5. Spectrum requires mastery of a 7-phase protocol before the first productive run.

---

## 6. New Dimension Analysis — D5 Security and D6 Quality Checks

### D5 Security — Full Field Comparison

| Score | Systems | Notes |
|-------|---------|-------|
| 5 | GitHub Copilot Workspace | CodeQL + Advisory DB + secret scanning + Copilot Code Review, all default and automatic |
| 4 | OpenAI Agents SDK, Factory, Cursor agents | Sandboxed cloud/VM execution + dedicated security review step + partial SAST |
| 3 | Augment Code/Intent, Devin | Cloud isolation (worktrees/VMs) + partial security review; gaps in SAST or injection protection |
| 2 | Spectrum, Citadel, Gas Town, metaswarm, Overstory, Agent Teams, CrewAI, AutoGen/AG2 | Local host execution without sandboxing; security review present only in Spectrum (/diff-review) |
| 1 | oh-my-claudecode, LangGraph | No sandboxing, no review step; LangGraph has active CVSS 9.3 critical CVE |

**Key findings**: The security dimension creates a clear split between cloud-native commercial systems and local-execution open-source systems. No CLAUDE.md-based protocol (Spectrum, Citadel, metaswarm, Gas Town, Overstory, oh-my-claudecode) reaches D5=3 because local git worktrees do not constitute sandboxing. The single security component that Spectrum contributes — the /diff-review gate — is the most security-relevant feature in the Claude Code ecosystem group, but it is LLM-based review, not automated tooling. LangGraph's D5=1 is the most significant security finding in this evaluation: three active CVEs, including a CVSS 9.3 critical deserialization injection, were disclosed in March 2026.

**Who leads**: GitHub Copilot Workspace leads outright (D5=5). OpenAI Agents SDK, Factory, and Cursor agents share second (D5=4). The commercial systems' cloud VM execution environments are the primary differentiator — a structural architectural advantage that open-source local-execution systems cannot match without fundamental re-architecture.

### D6 Quality Checks — Full Field Comparison

| Score | Systems | Notes |
|-------|---------|-------|
| 5 | Spectrum Protocol | Triple blocking gate (White + Gray + /diff-review) + Obsidian post-merge spec compliance |
| 4 | Factory, GitHub Copilot Workspace, Augment Code/Intent, metaswarm | Three of four D6=5 components; strong blocking gate architecture |
| 3 | OpenAI Agents SDK, Devin, Cursor agents | Two of four components; test execution and review step both present but one is partial or advisory |
| 2 | Citadel, Gas Town, Overstory, Agent Teams, CrewAI, AutoGen/AG2, LangGraph | Single component or no blocking gates; tests run only if user configures them |
| 1 | oh-my-claudecode | No quality checks; no test execution, no review step |

**Key findings**: D6 Quality Checks is the dimension where Spectrum's protocol rigor most directly translates to score advantage. The critical distinction at each score level is "blocking vs. configurable" — systems that enforce quality gates as protocol-mandated blocking steps score higher than systems where quality mechanisms exist but are optional. Spectrum's triple gate is the clearest implementation of blocking quality enforcement in this evaluation. Factory's Spec→Test→Implement→Verify four-phase loop and GitHub Copilot Workspace's automatic validation tool execution are the closest comparators.

**Who leads**: Spectrum leads at D6=5. Four systems share D6=4 (Factory, GitHub Copilot Workspace, Augment Code/Intent, metaswarm). The gap between D6=5 and D6=4 is primarily the post-merge spec compliance component: only Spectrum implements a dedicated post-merge compliance verification agent (Obsidian + SENTINEL-REPORT.md). The D6=4 cluster all satisfy test execution, review, and partial spec compliance, but none runs a separate post-merge compliance verification step.

---

## 7. Recommendations

### Recommendation 1: Publish a SWE-Bench evaluation to address D3 Accuracy (Carried forward from prior audit — not yet acted on)

**Dimension**: D3 Accuracy (Spectrum=2; Augment Code/Intent=4, GitHub Copilot Workspace=4, Cursor agents=3, OpenAI Agents SDK=3, Factory=3)

Augment Code's 70.6% SWE-Bench Verified score is the competitive reference. Spectrum's D3=2 (no benchmark data) is the most damaging gap against commercial competitors — it prevents Spectrum from being placed in the top tier on the dimension that product teams most frequently use for vendor evaluation. Even a 50-task SWE-Bench Verified subset run would be publishable and would test Spectrum's core hypothesis: that pre-execution interface contracts reduce specification drift and improve accuracy on multi-file parallel tasks. If the result is above 30%, Spectrum closes to D3=3 and directly competes with Cursor, Factory, and OpenAI Agents SDK on accuracy. If below 30%, that is actionable signal for where Howler-level accuracy investment is needed.

### Recommendation 2: Reduce 5-Howler full-mode cost below the D1=2/D1=3 boundary

**Dimension**: D1 Cost (Spectrum=2; every open-source competitor scores D1=3+)

The Gold→Sonnet migration reduces the representative 5-Howler full-mode cost from $9.43 to approximately $6.06. This is still in D1=2 territory ($2-$10). To reach D1=3, the per-run estimate must fall below $2.00 for the representative case. Two paths exist: (a) evaluate Politico downgrade from Sonnet to Haiku — the adversarial review criteria are well-specified, and Haiku may be sufficient for CONTRACT.md gap detection; (b) evaluate whether Pax (Gold-phase post-merge reconciliation) can be consolidated or streamlined without losing the independent validation value. Both changes directly address the muster overhead that is the structural cause of D1=2.

### Recommendation 3: Add automated SAST integration to the /diff-review gate to address D5 Security

**Dimension**: D5 Security (Spectrum=2; GitHub Copilot Workspace=5, OpenAI Agents SDK=4, Factory=4, Cursor agents=4)

Spectrum currently holds 1 of 4 D5=5 components (security-focused review step via /diff-review). Sandboxing is not achievable without fundamental re-architecture. But SAST integration is: if the /diff-review gate were extended to invoke a static analysis tool (e.g., semgrep, bandit for Python, or eslint with security rules for TypeScript) on each Howler's diff before the PR opens, Spectrum would satisfy 2 of 4 D5=5 components and move to D5=3. The `differential-review:diff-review` and `static-analysis:semgrep` skills are already available in the Claude Code environment — incorporating them into the Phase 3 triple gate is a protocol-level change, not a tooling change. This would give Spectrum the only SAST-backed security gate in the Claude Code ecosystem group.

### Recommendation 4: Document a post-merge recovery guide to leverage D6 advantage in marketing materials

**Dimension**: D6 Quality Checks (Spectrum=5, sole leader)

Spectrum leads D6 by the widest margin of any dimension. However, this advantage is not currently visible to developers evaluating systems at a glance — the README does not foreground the White + Gray + /diff-review + Obsidian pipeline as the primary quality differentiator. A dedicated section in the README and SPECTRUM-OPS.md explaining the quality gate architecture (what each gate checks, what constitutes a blocker, how Obsidian differs from per-PR review) would help developers who are selecting a system on quality-gate posture — a growing concern in enterprise contexts — identify Spectrum as the correct choice without reading the full protocol.

### Recommendation 5: Retire the D5 Observability recommendation from the prior audit

The prior audit (Recommendation 4) called for OpenTelemetry integration to address D5 Observability (Spectrum=3 vs. LangGraph=5). D5 Observability no longer exists as a dimension in v2. Under D5 Security, LangGraph has dropped from a competitor to a laggard (D5=1). Implementing OTEL would not improve Spectrum's D5 Security score (security requires sandboxing or SAST, not observability). This recommendation is retired. The token budget enforcement mechanism (prior Recommendation 5) remains relevant for cost transparency but is lower priority than the SAST integration (Recommendation 3) for score impact.

---

## 8. Executive Summary

Spectrum Protocol moves from 4th to 3rd place (tied) in v2, with a total score of 26/40. The improvement is modest — a net +1 driven by Nano mode's D2 Efficiency gain and a high D6 Quality Checks score of 5 under the new rubric. Four systems share the 26-point tier (Spectrum, Cursor agents, Augment Code/Intent, GitHub Copilot Workspace), and two systems score above it: OpenAI Agents SDK and Factory, both at 27/40.

The new D5 Security and D6 Quality Checks dimensions reveal a clear architectural divide. Commercial cloud-native systems (GitHub Copilot Workspace, Factory, Cursor agents, OpenAI Agents SDK) benefit from VM-level sandboxing that is structurally unavailable to local-execution Claude Code orchestrators. GitHub Copilot Workspace scores D5=5 — uniquely, because CodeQL, Advisory Database, secret scanning, and Copilot Code Review all run automatically on every coding agent task. Spectrum and every other Claude Code ecosystem system score D5=2 or D5=1 on Security, a ceiling imposed by local git worktree execution. The single exception in favor of Spectrum: its /diff-review security gate is the only formal security-focused review step in the Claude Code ecosystem group.

On Quality Checks, Spectrum leads the entire field at D6=5. The triple blocking gate (White + Gray + /diff-review, all requiring zero failures before any PR opens) plus Obsidian post-merge spec compliance verification has no equivalent in any other system. Factory (D6=4), GitHub Copilot Workspace (D6=4), Augment Code/Intent (D6=4), and metaswarm (D6=4) are the nearest competitors — all missing the post-merge spec compliance component.

Spectrum's three closest competitors by Euclidean distance are metaswarm (0.500), Citadel (0.661), and Augment Code/Intent (0.866). metaswarm remains the closest architectural analog — same cost, same scalability ceiling, same security posture, same accuracy evidence gap. Spectrum leads metaswarm on D4, D6, and D2; metaswarm leads on D1. Augment Code/Intent enters the top-3 closest (replacing Overstory) because of cost and scalability alignment, but the accuracy gap is significant: Augment Code publishes 70.6% SWE-Bench Verified versus Spectrum's zero published benchmarks.

Spectrum's clearest differentiator remains D4 Workflow Rigor at 5 — the sole top score across all 16 systems. The pre-execution CONTRACT.md, Politico adversarial review, formal failure taxonomy, and circuit breaker have no equivalent anywhere in this evaluation. Combined with D6 Quality Checks at 5, Spectrum's coordination discipline and quality gate architecture are genuinely best-in-class for open-source multi-agent systems.

The most important remaining gaps are D3 Accuracy (no published benchmark — Augment Code leads at 70.6% SWE-Bench, Spectrum at 2 with no evidence), D5 Security (local execution without sandboxing — cannot match commercial cloud VM systems without SAST tool integration), and D1 Cost (5-Howler full-mode at ~$6.06 still places Spectrum as the most expensive open-source option). Publishing a SWE-Bench evaluation and integrating an automated SAST tool into the /diff-review gate are the two highest-leverage actions available to close these gaps in v3.

---

*All scores carried forward from group-claude-code.md (H1), group-frameworks.md (H2), group-commercial.md (H3) without modification. No conflicts detected. Euclidean distances computed using normalized 0–1 values: (score−1)/4.*
