# Commercial and IDE-Native Systems Scoring Report
**Spectrum**: audit-2026-0331
**Howler**: H4-commercial
**Date**: 2026-03-31
**Rubric version**: from evaluation/audit-2026/RUBRIC.md

---

## Systems Covered

1. Devin (Cognition AI)
2. Cursor agents
3. Augment Code / Intent
4. GitHub Copilot Workspace
5. Amazon Q Developer
6. Factory (factory.ai / Droids)
7. Windsurf (Codeium / Cascade)

---

## Scoring Table

| System | D1 Cost | D2 Speed | D3 Accuracy | D4 Workflow Rigor | D5 Observability | D6 Recovery | D7 Setup | D8 Scalability | Total |
|--------|---------|----------|-------------|-------------------|------------------|-------------|----------|----------------|-------|
| Devin (Cognition AI) | 2 | 4 | 2 | 2 | 3 | 2 | 5 | 3 | 23 |
| Cursor agents | 2 | 4 | 3 | 2 | 2 | 2 | 5 | 3 | 23 |
| Augment Code / Intent | 2 | 3 | 4 | 3 | 2 | 2 | 4 | 3 | 23 |
| GitHub Copilot Workspace | 3 | 2 | 4 | 2 | 3 | 2 | 5 | 1 | 22 |
| Amazon Q Developer | 3 | 2 | 4 | 2 | 2 | 2 | 4 | 1 | 20 |
| Factory (Droids) | 3 | 3 | 3 | 3 | 3 | 2 | 4 | 3 | 24 |
| Windsurf (Cascade) | 3 | 3 | 2 | 2 | 2 | 2 | 5 | 3 | 22 |

---

## Per-System Evidence Notes

---

### Devin (Cognition AI)

**D1 Cost** — 2: Devin 2.0 starts at $20/month but bills via Agent Compute Units (ACUs). Core plan: $2.25/ACU; one hour of Devin time = ~$9. A multi-file parallel task with Managed Devins (3–5 subagents, each in an isolated VM for 30–60 min) runs $10–$25+ per session. Community reports cost as a frequent concern relative to task throughput. Source: Devin pricing page (devin.ai/pricing, accessed 2026-03-31); VentureBeat "Devin 2.0 is here" (2025); eesel.ai Cognition AI pricing explainer.
**Uncertainty flags**: ACU-to-task conversion varies; parallel (Managed Devin) sessions multiply cost rapidly. [MEDIUM CONFIDENCE — per-ACU pricing is public; total per-parallel-run is user-dependent]

**D2 Speed** — 4: Managed Devins run each sub-task in a fully isolated cloud VM in parallel. Real-time observability allows monitoring multiple subagents simultaneously. Cognition's documentation confirms parallel VM execution. Community reports describe asynchronous workflows where tasks are submitted and PRs arrive in the background. No published wall-clock timing for 3-agent runs at scale, but architecture supports genuine simultaneous execution. Source: cognition.ai/blog/devin-2 (Devin 2.0 announcement); AnalyticsVidhya Devin 2.0 explainer; vibecoding.app Devin review 2026.
**Uncertainty flags**: [MEDIUM CONFIDENCE — parallel VM execution confirmed; no published wall-clock benchmark for 3-agent run]

**D3 Accuracy** — 2: Cognition published a SWE-bench technical report showing 13.86% end-to-end resolution. This was for Devin 1.0 architecture (2024). Cognition has not published updated SWE-bench numbers for Devin 2.0 or 2.2. Community reviews describe Devin as better-suited for well-scoped, narrowly defined tasks than complex architectural work; success rates for open-ended engineering tasks reported in the 15–30% range informally, but no audited post-2.0 benchmark exists. Cognition claims 83% more efficiency per ACU vs Devin 1.0 (internal, unaudited). Source: cognition.ai/blog/swe-bench-technical-report (original 13.86% result); eesel.ai Cognition AI review 2026; digitalapplied.com Devin AI guide.
**Uncertainty flags**: [LOW CONFIDENCE — post-Devin-2.0 SWE-bench not published; original 13.86% predates current version. Score 2 per missing-evidence rule.]

**D4 Workflow Rigor** — 2: Managed Devins provide coordinator-worker role separation (main Devin coordinates, child Devins execute). However: no pre-flight file ownership declarations, no frozen interface contracts between Devins, no formal failure taxonomy, and decomposition is entirely implicit in the LLM's reasoning. No adversarial review step. Recovery is "coordinator re-scopes on failure." Meets only 1 of 4 D4 components (role separation). Source: cognition.ai/blog/devin-2 architecture description; AGENTIC-LANDSCAPE.md §3.2 ("No frozen contract between Managed Devins"); medium.com Agent-Native Development Devin 2.0 deep dive.

**D5 Observability** — 3: Devin provides a live IDE view where users can watch it work in its terminal, browser, and editor in real time. Users can intervene and edit during execution. However, this is visual observation via the Devin UI — not structured log output with trace IDs, no agent-level attribution in exportable logs, no replay capability after run completion. Missing components: structured logs with trace IDs, replay, and mid-execution inspection independent of the UI pane. Source: digitalapplied.com Devin AI complete guide; vibecoding.app Devin review 2026; Devin docs release notes (docs.devin.ai).
**Uncertainty flags**: [MEDIUM CONFIDENCE — UI-level observability confirmed; structured/exportable logging undocumented]

**D6 Recovery** — 2: Coordinator (main Devin) identifies failures and refines the plan. Cloud VM state persists across sessions. Plans are retained and can be re-entered after failure. However, failure taxonomy is not formal (no published enum of failure types), circuit breaker is not documented, and recovery is manual resume rather than automated classification + retry. Meets D6 score-2 criteria: partial persistence + manual resume. Source: cognition.ai/blog/devin-2; AGENTIC-LANDSCAPE.md §3.2 ("Plan refinement on failure. No formal failure taxonomy or circuit breaker").

**D7 Setup** — 5: Devin is fully cloud-hosted. Sign up at devin.ai, provide a GitHub connection, and assign a task. No local installation, no API key configuration beyond the sign-up OAuth, no infrastructure required. First parallel run achievable in under 15 minutes for any developer with a GitHub account. Source: devin.ai pricing and onboarding flow; digitalapplied.com Devin AI guide; VentureBeat Devin 2.0 announcement.

**D8 Scalability** — 3: Managed Devins support parallel execution across multiple isolated VMs. Architecture has no hard-coded ceiling in public documentation. However, practical use reports center on 2–5 parallel Devins for typical tasks; the ACU cost model disincentivizes large fan-outs; no published evidence of effective 8+ Devin runs. Google/MIT research finding (O(n²) overhead beyond 8 agents) applies to LLM-coordination overhead even with VM isolation. Source: cognition.ai/blog/devin-2; AGENTIC-LANDSCAPE.md §3.2; eesel.ai Cognition AI review 2026.
**Uncertainty flags**: [MEDIUM CONFIDENCE — no published evidence of runs beyond 5 parallel Devins]

---

### Cursor agents

**D1 Cost** — 2: Cursor Pro ($20/month) covers standard requests. Background agents require MAX mode, which adds a 20% surcharge and bills separately from subscription credits. Community reports document subscriptions depleting in a single day under heavy background-agent usage; a single agent run on a 50,000-line codebase can consume 22.5% of monthly Pro credits. With 8 parallel background agents, a single session can exhaust a monthly subscription. Cost is a documented, frequently cited concern in the Cursor community. Source: cursor.com/changelog/0-50 (simplified pricing + background agent announcement); Vantage.sh Cursor pricing explained 2026; cursor.com pricing page; eesel.ai Cursor pricing 2026.

**D2 Speed** — 4: Cursor 2.0 supports up to 8 parallel background agents, each in a git worktree on a cloud VM. Architecture confirms simultaneous execution. RL-trained model reported to achieve 60% latency reduction vs earlier versions. Community reports confirm agents work in the background while the developer continues coding locally. No published wall-clock benchmarks for 3-agent parallel runs. Source: cursor.com/docs/configuration/worktrees (official parallel agents docs); cursor.com/changelog/2-0; digitalapplied.com Cursor 2.0 agent-first architecture guide.
**Uncertainty flags**: [MEDIUM CONFIDENCE — 8-agent parallel architecture confirmed; no published timing benchmark]

**D3 Accuracy** — 3: No standalone SWE-bench score published by Cursor. Community reports describe high-quality output with RL-trained model improvements ("20x scaled RL"). Cursor's coding agent with Claude 3.7 Sonnet reportedly achieves ~56% on SWE-bench Verified in some configurations (from GitHub Copilot comparison), but this is model-dependent, not Cursor's own architecture contribution. Community generally rates Cursor's agent output as strong for IDE-context tasks but notes it requires review for complex multi-file refactors. Source: NxCode Cursor AI review 2026; prismic.io Cursor AI review; cursor.com changelog 2.0.
**Uncertainty flags**: [MEDIUM CONFIDENCE — no Cursor-specific SWE-bench; community reports only]

**D4 Workflow Rigor** — 2: Each parallel background agent operates independently in its own worktree. No pre-flight coordination: no task ownership contracts, no frozen interfaces, no shared specification, no adversarial review step. Conflicts are discovered at merge time. Competitive execution (same prompt to multiple models) doubles cost but adds no coordination rigor — divergent outputs are compared by the human, not resolved by a framework mechanism. Source: cursor.com/docs/configuration/worktrees; AGENTIC-LANDSCAPE.md §3.1 ("No coordination protocol between parallel agents... Conflicts are discovered at merge time").

**D5 Observability** — 2: Background agents operate on cloud VMs and return results via PR. Mid-execution visibility is limited to the agent status panel in the Cursor IDE showing which tasks are running. No structured logs with trace IDs, no replay, no per-agent attribution in exportable format. Users cannot distinguish which agent produced which file change without reading the PR diff. Source: cursor.com/changelog/0-50 (background agent announcement); NxCode Cursor review 2026; prismic.io Cursor AI review 2026.
**Uncertainty flags**: [MEDIUM CONFIDENCE — cloud VM internal logging undocumented; UI status panel confirmed]

**D6 Recovery** — 2: RL-trained model has implicit retry behavior. No published failure taxonomy, no circuit breaker, no formal crash recovery mechanism. If a background agent fails mid-run, the task is abandoned and must be manually restarted. Session state is not persisted in a recoverable form beyond what's in the git branch. Source: AGENTIC-LANDSCAPE.md §3.1 ("No explicit recovery protocol or failure classification"); cursor.com changelog; community reports.
**Uncertainty flags**: [LOW CONFIDENCE — recovery behavior not formally documented]

**D7 Setup** — 5: Download the Cursor IDE, sign in, and begin using agents immediately. No API key configuration beyond the Cursor account. First parallel run achievable in under 15 minutes. Background agents require MAX mode enablement (one toggle), but no infrastructure setup. Source: cursor.com; NxCode Cursor AI review 2026; checkthat.ai Cursor pricing 2026.

**D8 Scalability** — 3: Hard ceiling of 8 parallel background agents, documented by Cursor. 8 is within the D8 score-4 range, but: no documented guidance on coordination overhead at 8 agents, practical sweet spot in community reports is 3–5, cost model strongly disincentivizes 8-agent runs, and the 8 agents have no coordination mechanism (they are completely independent). Effective scalability for coordinated work is closer to 3–5. Source: cursor.com/docs/configuration/worktrees; medium.com "How to Run Cursor Subagents in Parallel" 2026.

---

### Augment Code / Intent

**D1 Cost** — 2: Intent uses Augment Code's credit system. Indie plan: $20/month (40,000 credits). Standard: $60/developer/month (130,000 credits). Max: $200/developer/month (450,000 credits). A complex multi-service feature costs ~4,300 credits; at Indie pricing, that is ~9 complex tasks per month. For a 3–5 agent run on a complex feature, cost is approximately $7–$22 per run depending on plan tier. Per-run cost frequently cited as a consideration in comparisons. Source: awesomeagents.ai Augment Code Intent review; augmentcode.com/product/intent; Intent vs Windsurf comparison (augmentcode.com, 2026-03-31).

**D2 Speed** — 3: Intent's Coordinator dispatches Specialists in waves into isolated git worktrees. Parallel execution within a wave is confirmed. However, Augment's own research states the practical ceiling is "3–4 parallel specialists with one human reviewer." Sequential merge strategy (specialists work in parallel, results merged in sequence) introduces serialization at integration time. No published wall-clock benchmarks. Source: AGENTIC-LANDSCAPE.md §3.3 ("Sequential merge strategy... Practical ceiling is 3–4 parallel specialists"); awesomeagents.ai Intent review; augmentcode.com/product/intent.
**Uncertainty flags**: [MEDIUM CONFIDENCE — parallel dispatch confirmed; merge serialization documented; no wall-clock timing]

**D3 Accuracy** — 4: Augment Code's SWE-bench agent achieves 70.6% on SWE-bench Verified (public leaderboard, augmentcode/augment-swebench-agent on GitHub). Auggie running on Claude Opus 4.5 scored 51.80% on SWE-bench Pro (Scale AI's harder variant, averaging 4.1 files and 107 code changes). Note: these scores reflect Augment's base agent/model, not Intent's multi-agent coordinator architecture specifically. Intent as a standalone product has no separate published benchmark. Augment's 70.6% is strong evidence for underlying capability; multi-agent coordination quality cannot be independently verified from these scores alone. Source: github.com/augmentcode/augment-swebench-agent (public repo with leaderboard entry); VentureBeat "Augment Code debuts AI agent with 70% win rate" article; awesomeagents.ai Intent review.
**Uncertainty flags**: [MEDIUM CONFIDENCE — benchmark is for base agent; Intent's coordinator architecture not independently benchmarked]

**D4 Workflow Rigor** — 3: Intent provides explicit role separation (Coordinator / Specialist / Verifier — 3 distinct roles). Verifier continuously checks results against a shared spec. Specialists execute in isolated git worktrees. These components satisfy: (a) role separation and (b) ongoing verification. However: specs are "living" (not frozen), no pre-flight file ownership matrix, no formal failure taxonomy, no circuit breaker. Meets D4 criteria for score 3 (role separation OR retry-with-logging); has a genuine Verifier role that is absent from most competitors, but missing the frozen-contract and failure-taxonomy components required for score 4. Source: AGENTIC-LANDSCAPE.md §3.3; awesomeagents.ai Intent review; augmentcode.com/product/intent feature page.

**D5 Observability** — 2: Intent includes an "activity feed" for tracking agent progress across tasks (per official product page). The activity feed provides visibility into task status but is not described as providing structured logs with trace IDs, per-agent output attribution, or replay capability. Internal observability of the Context Engine and coordination layer is proprietary. Source: augmentcode.com/product/intent; awesomeagents.ai Intent review.
**Uncertainty flags**: [MEDIUM CONFIDENCE — activity feed confirmed; structured logging / replay undocumented; internal observability proprietary]

**D6 Recovery** — 2: Coordinator identifies failures and re-assigns to a different Specialist or retries with a modified approach. No circuit breaker, no formal failure taxonomy. No per-task crash recovery file equivalent to HOOK.md. Recovery is Coordinator-directed manual re-delegation. Source: AGENTIC-LANDSCAPE.md §3.3 ("Coordinator identifies failure type and re-assigns... No circuit breaker"); awesomeagents.ai Intent review.

**D7 Setup** — 4: Intent is a standalone macOS desktop app (public beta, February 2026; Windows on waitlist). Requires Augment Code account and GitHub/Linear/Sentry integration setup. First parallel run requires connecting a repository and configuring specialist personas. No infrastructure required. Setup is 2–3 steps beyond download: account creation, repo connection, spec authoring. Achievable within one hour for a developer familiar with the integrations. Source: augmentcode.com/product/intent; awesomeagents.ai Intent review.
**Uncertainty flags**: [MEDIUM CONFIDENCE — macOS only; Windows unavailable as of 2026-03-31]

**D8 Scalability** — 3: Intent's documented practical ceiling is 3–4 parallel Specialists. Sequential merge strategy adds coordination overhead beyond 3 simultaneous agents. Context Engine claims 400,000+ file support, but agent count is the limit, not file count. No evidence of effective runs at 6+ agents. Source: AGENTIC-LANDSCAPE.md §3.3; augmentcode.com/product/intent; awesomeagents.ai Intent review.

---

### GitHub Copilot Workspace

**D1 Cost** — 3: GitHub Copilot Pro is $10/month (300 premium requests); Pro+ is $39/month (1,500 premium requests). Overage billing introduced June 2025: $0.04 per additional premium request. Workspace tasks consume multiple premium requests but are included in subscription tiers. For a 3–5 file parallel task, cost is typically within monthly allocation for Pro+ users. Single-agent sequential architecture limits per-run cost compared to true multi-agent systems. Source: github.com/features/copilot/plans (official pricing page); docs.github.com/en/copilot/get-started/plans; pecollective.com GitHub Copilot Pricing March 2026; checkthat.ai Copilot pricing.

**D2 Speed** — 2: GitHub Copilot Workspace is a sequential pipeline: specification → plan → implementation → review → PR. No parallelism between pipeline stages. The coding agent (issue-to-PR) and the code review agent are sequential, not simultaneous. Agent mode in VS Code and JetBrains (GA March 2026) is single-threaded. Agent HQ for multi-agent orchestration is roadmapped but not GA as of 2026-03-31. This is a single-agent sequential architecture; parallelism is absent. Source: AGENTIC-LANDSCAPE.md §3.4 ("Sequential pipeline... No parallelism"); github.blog "GitHub Copilot: meet the new coding agent"; github.blog "The agent awakens"; NxCode GitHub Copilot complete guide 2026.

**D3 Accuracy** — 4: Copilot Workspace scored 55% on SWE-bench Verified (community-cited figure, March 2025). More recent reports cite 56% with Claude 3.7 Sonnet in agent mode. When modifying 3+ files in a single task, Workspace achieves 78% accuracy vs 62% for Cursor (per NxCode comparison). These figures place Copilot in the D3 score-4 range (30–50% SWE-bench, or second-tier benchmark ranking). Note: the 55–56% figure is the highest consistently cited for Copilot Workspace specifically; the 78% multi-file figure is from a third-party comparison, methodology unspecified. Source: ucstrategies.com GitHub Copilot Review 2026; NxCode Copilot complete guide 2026; vibecoding.app GitHub Copilot Workspace Review 2026.
**Uncertainty flags**: [MEDIUM CONFIDENCE — 55–56% SWE-bench cited by multiple sources but methodology of benchmark run not fully verified independently]

**D4 Workflow Rigor** — 2: Copilot Workspace provides an auditable pipeline with human-editable stages (specification → plan → implementation → review). This is the strongest auditability story in the commercial group. However, it is a single-agent sequential pipeline, not a multi-agent coordination framework. There are no inter-agent contracts, no file ownership matrix, no failure taxonomy, no adversarial review step between independent agents. The human IS the reviewer, not a separate agent. Agent mode (March 2026 GA) adds autonomous multi-step execution but no formal rigor mechanisms. Source: AGENTIC-LANDSCAPE.md §3.4; github.blog coding agent announcement; vibecoding.app Workspace review 2026.

**D5 Observability** — 3: Workspace provides a fully auditable pipeline interface where every artifact (spec, plan, implementation, review) is human-readable and editable between stages. GitHub Actions CI integration provides structured CI logs. However, mid-execution agent visibility is limited to the Workspace UI; no structured per-agent logs with trace IDs; no replay at a sub-step level; Agent HQ observability controls are roadmapped, not GA. Source: github.blog "The agent awakens"; github.blog "GitHub Copilot: meet the new coding agent"; NxCode Copilot guide 2026.
**Uncertainty flags**: [MEDIUM CONFIDENCE — pipeline artifact visibility confirmed; structured log export and per-agent tracing undocumented]

**D6 Recovery** — 2: Human can intervene at any pipeline stage, edit the plan, and re-run from any step. This is manual resume from a named checkpoint — meeting D6 score-2 criteria. No automated failure classification, no circuit breaker, no automated recovery for any failure class. Source: AGENTIC-LANDSCAPE.md §3.4 ("Human can intervene at any stage"); github.blog coding agent; github docs Copilot features.

**D7 Setup** — 5: GitHub Copilot is bundled into GitHub and accessible to all paid Copilot users directly from github.com. No local installation required for Workspace (web-based). Agent mode requires VS Code or JetBrains IDE with the Copilot extension, but extensions install in one click. Familiar to any GitHub user. First run achievable in under 15 minutes. Source: github.com/features/copilot/plans; github.blog Copilot agent mode rollout; docs.github.com Copilot features.

**D8 Scalability** — 1: GitHub Copilot Workspace is a single-agent pipeline. No parallelism. Multiple agents (Agent HQ, coordinated agent workflows) are on the 2026 roadmap but are not GA. The current product has no meaningful parallel execution path. Scores 1 per rubric anchor: single-agent execution or parallelism architecture that degrades to effectively sequential at 2+ agents. Source: AGENTIC-LANDSCAPE.md §3.4 ("Sequential pipeline... No parallelism"); github.blog "The agent awakens"; NxCode Copilot 2026 guide.

---

### Amazon Q Developer

**D1 Cost** — 3: Amazon Q Developer Pro tier: $19/user/month. Free tier available with monthly caps (50 agent tasks/month). Code transformation billing: $0.003/line of code beyond 4,000 lines/month for Pro. For a 3–5 agent parallel coding task (not natively supported — Q is single-agent per invocation), cost is within the flat subscription for most use cases. Q does not support parallel multi-agent sessions natively, so per-run cost for a single task is low (subscription-inclusive); however, Q lacks the parallel execution that makes per-run cost comparison meaningful. Source: aws.amazon.com/q/developer/pricing/ (official pricing page); superblocks.com Amazon Q Developer pricing 2026; cloudvisor.co Amazon Q pricing guide 2026.

**D2 Speed** — 2: Amazon Q Developer sub-agents (/dev, /test, /review) are invoked sequentially by the user. There is no automatic multi-agent dispatch or parallel execution across sub-agents. The autonomous feature-development agent runs a single plan-generate-test cycle per invocation. No parallelism architecture. Community reports no speed advantages over sequential single-agent completion. Source: AGENTIC-LANDSCAPE.md §3.5 ("No multi-agent parallelism or coordination protocol. Sub-agents are siloed"); aws.amazon.com/q/developer/features/; aitoolsdevpro.com Amazon Q review 2026.

**D3 Accuracy** — 4: Amazon Q Developer's April 2025 agent update achieved 66% on SWE-bench Verified and 49% on SWT-Bench (announced via AWS what's new page and confirmed via SWE-bench experiments GitHub PR #205). This is a strong, independently verifiable result. Source: aws.amazon.com/about-aws/whats-new/2025/04/amazon-q-developer-releases-state-art-agent-feature-development/ (official AWS what's new); github.com/SWE-bench/experiments/pull/205 (SWE-bench submission PR); aws.amazon.com/blogs/devops/april-2025-amazon-q-developer/.
**Note**: 66% SWE-bench Verified places Amazon Q in D3 score-5 territory (≥50%). However, this result is from April 2025 (a year-old snapshot); it is the last published SWE-bench result from Amazon for Q Developer. Given the rubric's conservative interpretation rule and that the broader leaderboard has advanced substantially since April 2025, score 4 is the conservative assignment. If this result were confirmed current-as-of-2026, score 5 would apply.
**Uncertainty flags**: [MEDIUM CONFIDENCE — April 2025 benchmark result; no updated 2026 SWE-bench publication confirmed]

**D4 Workflow Rigor** — 2: Q Developer has specialized sub-agents (/dev, /test, /review) with distinct functional roles — the closest thing to role separation in this lineup. However, sub-agent invocation is entirely manual (user selects which to invoke). Sub-agents do not coordinate, share contracts, or operate on a shared task graph. No pre-flight conflict prevention, no failure taxonomy, no adversarial review between independent agents. The /review sub-agent is a genuine quality gate, but it operates independently of /dev, not as an integrated workflow. Source: AGENTIC-LANDSCAPE.md §3.5 ("No multi-agent parallelism or coordination protocol. Sub-agents are siloed"); aws.amazon.com/q/developer/features/.

**D5 Observability** — 2: Q Developer operates within IDE sessions and the AWS Console. No real-time dashboard for agent execution. No structured per-agent logs with trace IDs. Users can see output in the IDE chat panel, but there is no replay, no mid-execution status panel, and no agent-level attribution beyond the sub-agent name. AWS CloudWatch integration is available for Q's AWS API actions, but not for the coding agent's file-editing workflow. Source: aws.amazon.com/q/developer/features/; aitoolsdevpro.com Amazon Q review 2026.
**Uncertainty flags**: [LOW CONFIDENCE — internal logging behavior not publicly documented; IDE output only confirmed]

**D6 Recovery** — 2: Retry at user's discretion. No formal recovery protocol, no automated failure classification, no circuit breaker. If the /dev agent fails mid-task, the user re-invokes. Source: AGENTIC-LANDSCAPE.md §3.5 ("Retry at the user's discretion. No formal recovery protocol"); aws.amazon.com/q/developer/.

**D7 Setup** — 4: Q Developer installs as an IDE plugin (VS Code, JetBrains, Visual Studio, Eclipse) or is accessible via the AWS Console. Requires an AWS account and IAM configuration for Pro tier. Free tier requires only an AWS Builder ID. Setup requires 2–3 steps beyond IDE install: AWS account creation or Builder ID, plugin install, authentication. Achievable within one hour. Not as frictionless as Copilot (no AWS account required for Copilot). Source: aws.amazon.com/q/developer/; aitoolsdevpro.com Amazon Q guide 2026; superblocks.com Amazon Q pricing 2026.

**D8 Scalability** — 1: Amazon Q Developer has no multi-agent parallelism architecture. Each sub-agent is invoked independently by the user. There is no orchestration layer, no parallel dispatch, and no coordination between sub-agents. This is a single-agent-per-invocation model. Scores 1 per rubric anchor. Source: AGENTIC-LANDSCAPE.md §3.5; aws.amazon.com/q/developer/features/.

---

### Factory (Droids)

**D1 Cost** — 3: Factory pricing starts free (20M tokens included). Paid plans: $20/month (Starter), scaling to $2,000/month (Enterprise). Per-task billing beyond free tier is token-based across the user's chosen model (Factory is model-agnostic: supports Claude Sonnet 4, GPT-5, Gemini 2.5 Pro, Claude Opus 4.1, o3, etc.). At standard model rates, a 3–5 agent parallel run with a capable model (e.g., Claude Opus) runs $2–$8 depending on task size — within the D1 score-3 range ($0.50–$2/run at the lower end; $2–$10 for larger runs). Community review ("I Canceled Two AI Max Plans for Factory's Coding Agent Droid," every.to) describes value relative to Cursor Pro+ and similar tiers. Source: factory.ai/pricing; docs.factory.ai/pricing; every.to Vibe Check Factory review; fritz.ai Factory AI review 2026.
**Uncertainty flags**: [MEDIUM CONFIDENCE — model costs are user-chosen; orchestration overhead is unknown; token costs floor is estimable but total is model-dependent]

**D2 Speed** — 3: Factory's Droids are cloud-native and parallelizable. Multiple Droids can run concurrently (confirmed by Groq case study: "engineers run multiple Droids in parallel"). The orchestrator breaks large projects into milestones; within a milestone, workers can execute in parallel. However, each milestone ends with a validation phase before proceeding — this introduces serialization between milestones. No published wall-clock timing for 3-agent runs. Source: factory.ai/news/missions; factory.ai case study with Groq; rimusz.net Factory.ai Droids overview.
**Uncertainty flags**: [MEDIUM CONFIDENCE — parallel Droid execution confirmed; milestone-based serialization documented; no wall-clock benchmark]

**D3 Accuracy** — 3: Factory's Droids achieved #1 on Terminal Bench with a score of 58.75%. Terminal Bench is a different benchmark from SWE-bench; it focuses on CLI/terminal task completion. Factory has not published a SWE-bench Verified score. The latent.space profile of Factory ("Factory.ai: The A-SWE Droid Army") cites strong results on coding tasks in production. The 58.75% Terminal Bench score and community reports of production quality place Factory at the upper end of the D3 score-3 range (acceptable accuracy, requires moderate review), trending toward score 4. Score 3 assigned conservatively per rubric rule: no SWE-bench equivalent result, community consensus of strong but not exceptional accuracy. Source: factory.ai/news/terminal-bench; booststash.com Factory AI review; latent.space Factory profile; fritz.ai Factory review 2026.
**Uncertainty flags**: [MEDIUM CONFIDENCE — Terminal Bench #1 confirmed; SWE-bench equivalent absent; conservative score applied]

**D4 Workflow Rigor** — 3: Factory implements an orchestrator that breaks projects into milestones with validation phases. Specialized Droids exist: CodeDroid, Review Droid, QA Droid. Each milestone ends with worker validation before moving forward. This provides role separation (implementer ≠ reviewer) and checkpoint-based verification. However: no pre-flight file ownership contracts, no frozen interface specification, no formal failure taxonomy, and no adversarial review step at planning time. Meets D4 score-3 criteria (role separation + retry-with-validation). Source: factory.ai/news/missions (orchestrator + milestone architecture); factory.ai case study Groq; latent.space Factory profile; rimusz.net Factory Droids overview.

**D5 Observability** — 3: Factory's web dashboard allows users to inspect every line of the diff, understand why code changed, and accept or reject results after a Droid completes. The dashboard provides post-execution review with structured diff output. Mid-execution: Droids report progress asynchronously; the dashboard shows running status. No published evidence of structured log export with trace IDs or replay capability. The review-first dashboard is stronger than most commercial systems' logging but falls short of LangSmith-class observability. Source: factory.ai (product page); fritz.ai Factory review 2026; booststash.com review.
**Uncertainty flags**: [MEDIUM CONFIDENCE — dashboard confirmed via product page and reviews; structured log/trace export undocumented]

**D6 Recovery** — 2: Factory's orchestrator runs validation at each milestone boundary and creates follow-up tasks when validation surfaces issues. This is milestone-level retry — the system detects validation failures and continues with fixes. However, no formal failure taxonomy (transient/logical/structural), no circuit breaker documented, and recovery is "create follow-up tasks" rather than classified failure handling. Meets D6 score-2 criteria (partial checkpoint + framework-directed retry without classification). Source: factory.ai/news/missions ("when validation surfaces issues, the orchestrator creates follow-up work"); latent.space Factory profile.
**Uncertainty flags**: [MEDIUM CONFIDENCE — milestone validation recovery documented; formal taxonomy and circuit breaker absent from public docs]

**D7 Setup** — 4: Factory is web-based with a CLI component. Sign up at factory.ai, connect GitHub/GitLab, and assign a task to a Droid. Free tier requires no payment information. CLI install adds 1 step. Integration with Jira, Sentry, Linear, and Notion adds optional configuration. First Droid run achievable within one hour; full integration setup with all connectors may take a half-day. Source: factory.ai; sidbharath.com Factory.ai guide; fritz.ai Factory review 2026.

**D8 Scalability** — 3: Factory explicitly supports parallel Droid execution at scale for CI/CD and migrations ("script and parallelize Droids at massive scale"). The Groq case study confirms multiple simultaneous Droids in production. However, milestone-based serialization limits effective parallelism within a single project — parallelism is across independent tasks more than within a coordinated feature. No published ceiling; practical evidence centers on 3–6 parallel Droids. Source: factory.ai (parallel Droids at scale claim); factory.ai/case-studies/groq; rimusz.net Droids overview.
**Uncertainty flags**: [MEDIUM CONFIDENCE — parallel execution confirmed; scaling ceiling undocumented; milestone serialization limits within-project parallelism]

---

### Windsurf (Cascade)

**D1 Cost** — 3: Windsurf pricing (March 2026): Free ($0, limited credits), Pro ($20/month, 500 credits), Teams ($30/user/month), Enterprise ($60/user/month). March 2026 pricing overhaul moved to fixed quota tiers. With SWE-1.5 free for all users, basic Cascade usage costs are low. Parallel agents (Wave 13) run within the credit allocation. Community reports "best value per dollar among paid IDEs" but notes unhappiness with the shift from the variable credit system. For a 3–5 agent parallel run via Cascade, cost stays within Pro subscription for typical tasks. Source: windsurf.com/pricing; digitalapplied.com Windsurf pricing March 2026; verdent.ai Windsurf pricing 2026; byteiota.com Wave 13 free SWE-1.5 announcement.

**D2 Speed** — 3: Windsurf Wave 13 (December 2025) introduced parallel multi-agent sessions with git worktrees and side-by-side Cascade panes. Up to 5 parallel Cascade agents confirmed. SWE-1.5 proprietary model runs at ~950 tokens/second — faster than comparable models. However, Wave 13 parallel agents are newly launched and documentation describes 5 agents as the demonstrated ceiling. No published wall-clock benchmarks for parallel runs. Feature is recent; community reports of parallel use are positive but early. Source: windsurf.com/blog/windsurf-wave-13; byteiota.com Wave 13; testingcatalog.com Wave 13 parallel agents; digitalapplied.com Wave 13 guide.
**Uncertainty flags**: [MEDIUM CONFIDENCE — 5-agent parallel confirmed as of Wave 13; no timing benchmarks; feature is recent (Dec 2025)]

**D3 Accuracy** — 2: Windsurf's SWE-1.5 model page discusses SWE-bench-Pro performance but does not publish a specific verified SWE-bench score for the Windsurf agent as a system. The prior landscape survey (AGENTIC-LANDSCAPE.md) does not include a SWE-bench figure for Windsurf/Cascade. Community reviews praise Windsurf's completion speed and contextual awareness but do not establish benchmark-level accuracy claims. SWE-1.5 is described as optimized for speed, not top accuracy. Augment Code's own comparison page ("Intent vs Windsurf") describes Windsurf as "single-agent Cascade" without published SWE-bench numbers for Windsurf's agent layer. Score 2 per missing-evidence rule for SWE-bench; community reports suggest acceptable but not top-tier quality. Source: windsurf.com/blog/swe-1-5; augmentcode.com/tools/intent-vs-windsurf; pinklime.io Windsurf review 2026; aitoolshaven.com Windsurf review 2026.
**Uncertainty flags**: [LOW CONFIDENCE — no SWE-bench score published for Windsurf/Cascade as an agent system; speed model (SWE-1.5) not positioned as accuracy-first]

**D4 Workflow Rigor** — 2: Windsurf Wave 13 adds parallel multi-agent sessions but these are independent Cascade instances with no inter-agent contract, no file ownership matrix, no shared specification, and no adversarial review. Git worktree isolation prevents runtime conflicts but not merge conflicts or semantic divergence. Cascade is a single-agent tool running in parallel instances — not a coordinated multi-agent system with defined roles. Source: windsurf.com/blog/windsurf-wave-13; byteiota.com Wave 13; testingcatalog.com Wave 13.

**D5 Observability** — 2: Cascade runs within the Windsurf IDE. Side-by-side Cascade panes (Wave 13) allow monitoring multiple agents simultaneously in the IDE. No structured log export with trace IDs, no replay capability, no external observability integration documented. Mid-execution visibility is limited to the Cascade chat panel per agent. Source: windsurf.com/blog/windsurf-wave-13; pinklime.io Windsurf review 2026; aitoolshaven.com Windsurf review 2026.
**Uncertainty flags**: [MEDIUM CONFIDENCE — side-by-side monitoring confirmed; structured logging undocumented]

**D6 Recovery** — 2: Cascade handles errors by iterating in the same session; it retries commands that fail and can read error output to adjust its approach. This is implicit retry within a session — no formal failure taxonomy, no circuit breaker, no cross-session crash recovery. Source: capacity.so "What is Windsurf?" explainer; pinklime.io Windsurf review 2026.
**Uncertainty flags**: [MEDIUM CONFIDENCE — in-session retry confirmed; formal recovery protocol undocumented]

**D7 Setup** — 5: Windsurf is a standalone IDE download (macOS, Windows, Linux). Install, sign in with a Windsurf account, and begin using Cascade immediately. Free plan available with no payment required for initial use. SWE-1.5 is free and enabled by default. No API key configuration beyond the account sign-in. First run achievable in under 15 minutes. Source: windsurf.com; pinklime.io Windsurf review 2026; NxCode Windsurf review 2026.

**D8 Scalability** — 3: Wave 13 introduces up to 5 parallel Cascade agents via git worktrees. This is within the D8 score-3 range (3–5 agent sweet spot). No published evidence of effective runs beyond 5 agents; feature is newly released (December 2025). No coordination between agents at scale — scalability is limited to independent parallel execution, not coordinated scale. Source: windsurf.com/blog/windsurf-wave-13; byteiota.com Wave 13.

---

## Research Notes

**Search date**: 2026-03-31. Evidence gathered from official product pages, community review sites, and benchmark repositories current as of this date.

**Systems not scored** (rationale): OpenAI Codex CLI and Replit Agent were omitted in favor of Factory and Windsurf, which had stronger evidence for multi-agent capabilities and more current documentation. Replit Agent remains single-agent (covered in AGENTIC-LANDSCAPE.md §3.6). OpenAI Codex CLI is a code-editing tool, not a multi-agent system.

**Key impartiality notes**:
- Amazon Q Developer's April 2025 SWE-bench Verified score (66%) would qualify for D3 score 5 if current, but conservative interpretation assigns score 4 given the 11-month lag and no updated 2026 benchmark.
- GitHub Copilot Workspace scores 1 on D8 (no parallelism), which is lower than most systems in this group — this stands per the evidence.
- Windsurf's D3 score of 2 reflects the absence of any published SWE-bench result for the Cascade agent system, not a known-bad result. If Windsurf publishes a SWE-bench score before H5 integration, this should be revisited.
