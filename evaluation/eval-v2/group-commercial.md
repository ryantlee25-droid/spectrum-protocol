# Commercial and IDE-Native Systems Scoring Report
**Spectrum**: eval-v2
**Howler**: H3-commercial
**Date**: 2026-03-31
**Rubric version**: eval-v2/PLAN.md (8 dimensions; D5=Security, D6=Quality Checks)

---

## Systems Covered (Top 15 scope)

1. Devin (Cognition AI)
2. Cursor agents
3. Augment Code / Intent
4. GitHub Copilot Workspace
5. Factory (factory.ai / Droids)

*Amazon Q Developer and Windsurf were present in the prior audit group report (audit-2026) but are excluded from the Top 15 synthesis table. They are omitted here per the PLAN.md scope instruction to maintain the same 15 systems as the prior audit.*

---

## Scoring Table

| System | D1 Cost | D2 Efficiency | D3 Accuracy | D4 Workflow Rigor | D5 Security | D6 Quality Checks | D7 Setup | D8 Scalability | Total |
|--------|---------|---------------|-------------|-------------------|-------------|-------------------|----------|----------------|-------|
| Devin (Cognition AI) | 2 | 4 | 2 | 2 | 3 | 3 | 5 | 3 | 24 |
| Cursor agents | 2 | 4 | 3 | 2 | 4 | 3 | 5 | 3 | 26 |
| Augment Code / Intent | 2 | 3 | 4 | 3 | 3 | 4 | 4 | 3 | 26 |
| GitHub Copilot Workspace | 3 | 2 | 4 | 2 | 5 | 4 | 5 | 1 | 26 |
| Factory (Droids) | 3 | 3 | 3 | 3 | 4 | 4 | 4 | 3 | 27 |

---

## Score Deltas from Prior Audit (v1 → v2)

D5 and D6 are entirely new dimensions — prior D5 (Observability) and D6 (Recovery) scores are not carried forward.

| System | v1 Total (D1–D4, D7–D8 only, 6 dims) | v2 Total (8 dims) | Notes |
|--------|--------------------------------------|-------------------|-------|
| Devin | 18 (of 30) | 24 (of 40) | D5=3, D6=3 added |
| Cursor agents | 19 (of 30) | 26 (of 40) | D5=4 (new sandboxing + Bugbot), D6=3 added |
| Augment Code / Intent | 19 (of 30) | 26 (of 40) | D5=3, D6=4 (Verifier architecture) |
| GitHub Copilot Workspace | 17 (of 30) | 26 (of 40) | D5=5 (strongest in group), D6=4 |
| Factory (Droids) | 19 (of 30) | 27 (of 40) | D5=4 (DroidShield + sandboxing), D6=4 |

*v1 totals above exclude prior D5 (Observability) and D6 (Recovery) to allow clean comparison of the six retained dimensions.*

---

## Per-System Evidence Notes

---

### Devin (Cognition AI)

**D1 Cost** — 2: *Unchanged from prior audit.* Devin 2.0/2.2 bills via Agent Compute Units (ACUs) at $2.25/ACU; one hour of Devin time is approximately $9. A multi-file parallel task with Managed Devins (3–5 subagents, each in an isolated VM for 30–60 min) runs $10–$25+ per session. Cost is a documented, frequently cited concern. Source: devin.ai/pricing; VentureBeat "Devin 2.0 is here" (2025); eesel.ai Cognition AI pricing explainer.
[MEDIUM CONFIDENCE — per-ACU pricing is public; total per-parallel-run is user-dependent]

**D2 Efficiency** — 4: *Unchanged from prior audit.* Managed Devins run each sub-task in a fully isolated cloud VM in parallel. Real-time observability allows monitoring multiple subagents simultaneously. Community reports describe asynchronous workflows where tasks are submitted and PRs arrive in the background. No published wall-clock benchmark for 3-agent runs. Source: cognition.ai/blog/devin-2; AnalyticsVidhya Devin 2.0 explainer.
[MEDIUM CONFIDENCE — parallel VM execution confirmed; no wall-clock benchmark]

**D3 Accuracy** — 2: *Unchanged from prior audit.* Cognition's original SWE-bench Technical Report documented 13.86% for Devin 1.0 (2024). No updated SWE-bench Verified score published for Devin 2.0 or 2.2 as of 2026-03-31. Cognition claims 67% of Devin PRs are now merged (vs 34% prior year) and 4x faster problem-solving — internal, unaudited metrics cited in the 2025 annual performance review. Score 2 per missing-evidence rule: post-2.0 SWE-bench not published. Source: cognition.ai/blog/swe-bench-technical-report; cognition.ai/blog/devin-annual-performance-review-2025.
[LOW CONFIDENCE — post-Devin-2.0 SWE-bench not published]

**D4 Workflow Rigor** — 2: *Unchanged from prior audit.* Managed Devins provide coordinator-worker role separation but no pre-flight file ownership declarations, no frozen interface contracts, no formal failure taxonomy, and no adversarial review step. Decomposition is entirely implicit in the LLM's reasoning. Recovery is "coordinator re-scopes on failure." Meets only 1 of 4 D4 components. Source: cognition.ai/blog/devin-2; AGENTIC-LANDSCAPE.md §3.2.

**D5 Security** — 3: Devin operates inside isolated cloud DevBox VMs — confirmed sandboxing, separate from host machines. This satisfies component (b). However: no documented automated SAST/vulnerability scanning of generated code within Devin's own pipeline (component a — users are advised to run their own SBOM checks and vulnerability scanners externally); no documented protection against prompt injection — a security researcher (Johann Rehberger) published a live exploitation in late 2024 showing Devin could be manipulated to expose ports to the internet, leak access tokens, and install C2 malware via prompt injection in GitHub issues; Cognition acknowledged the disclosure but no remediation timeline was confirmed as of 2026-03-31 (component d unmet). The Devin Review feature (Devin 2.2) provides automated diff scanning categorized by severity (bugs, warnings) — this is a lightweight security-focused review step, satisfying component (c) at a basic level. Verdict: sandboxed cloud execution + basic self-review step, but known unremediated prompt injection vulnerability and no automated SAST. 2 of 4 components met solidly; (c) met weakly. Score 3 per rubric: sandboxed execution OR security-focused review, but not both at full strength, and no automated vulnerability scanning. Source: embracethered.com "I Spent $500 To Test Devin AI For Prompt Injection" (2025); cognition.ai/blog/devin-review; docs.devin.ai/work-with-devin/devin-review; pillar.security "Hidden Security Risks of SWE Agents."
[MEDIUM CONFIDENCE — VM isolation confirmed; prompt injection vulnerability documented and unremediated as of 2026-03-31]

**D6 Quality Checks** — 3: Devin 2.2 introduced the Devin Review feature, which runs an automated quality pass on every PR Devin generates — categorizing issues by severity (bugs, warnings, FYI) and catching 30% more issues before human review. Devin also iterates on CI failures until tests pass: it reads CI output, addresses failures, and does not submit a PR until checks pass. This satisfies component (a) automated test execution with pass/fail gate and component (c) spec/acceptance criteria check (Devin writes to user-provided task specs and addresses review comments). However: no peer/adversarial review between independent agents (component b — Devin reviews its own PRs, not a separate independent agent); no coverage reporting (component d). Human review remains required before merge. Score 3: automated test execution AND a built-in self-review step, but coverage not enforced and self-review is not independent adversarial review. Source: digitalapplied.com "Devin 2.2: Desktop and Code Review AI Guide"; docs.devin.ai/work-with-devin/devin-review; cognition.ai/blog/devin-review; dev.to "How to Let Devin AI Write Tests and Work Until CI Passes."

**D7 Setup** — 5: *Unchanged from prior audit.* Cloud-hosted, sign up at devin.ai, provide GitHub OAuth, assign a task. No local installation. First parallel run achievable in under 15 minutes. Source: devin.ai; VentureBeat Devin 2.0 announcement.

**D8 Scalability** — 3: *Unchanged from prior audit.* Managed Devins support parallel execution across multiple isolated VMs. Practical use centers on 2–5 parallel Devins; ACU cost model disincentivizes large fan-outs; no published evidence of effective 8+ Devin runs. Source: cognition.ai/blog/devin-2; AGENTIC-LANDSCAPE.md §3.2.
[MEDIUM CONFIDENCE — no published evidence of runs beyond 5 parallel Devins]

---

### Cursor agents

**D1 Cost** — 2: *Unchanged from prior audit.* Cursor Pro ($20/month) covers standard requests. Background agents require MAX mode (20% surcharge, separate billing from subscription credits). Heavy background-agent usage depletes monthly subscriptions rapidly; a single large codebase session can consume 22.5% of monthly Pro credits. Cost is a documented, frequently cited concern. Source: cursor.com/changelog/0-50; cursor.com pricing page; eesel.ai Cursor pricing 2026.

**D2 Efficiency** — 4: *Unchanged from prior audit.* Cursor 2.0 supports up to 8 parallel background agents, each in a git worktree on a cloud VM. Simultaneous execution confirmed. Background agents deliver PRs asynchronously. No published wall-clock benchmark for 3-agent parallel runs. Source: cursor.com/docs/configuration/worktrees; cursor.com/changelog/2-0.
[MEDIUM CONFIDENCE — 8-agent parallel architecture confirmed; no timing benchmark]

**D3 Accuracy** — 3: *Unchanged from prior audit.* No standalone SWE-bench score published by Cursor. Community reports describe high-quality output with RL-trained model improvements. Claude 3.7 Sonnet in Cursor reportedly achieves ~56% SWE-bench Verified in some configurations, but this is model-dependent, not Cursor's own architecture contribution. Community generally rates Cursor's agent output as strong for IDE-context tasks. Source: NxCode Cursor AI review 2026; cursor.com changelog 2.0.
[MEDIUM CONFIDENCE — no Cursor-specific SWE-bench; community reports only]

**D4 Workflow Rigor** — 2: *Unchanged from prior audit.* Each parallel background agent operates independently. No pre-flight coordination, no task ownership contracts, no frozen interfaces, no shared specification, no adversarial review step. Conflicts are discovered at merge time. Source: cursor.com/docs/configuration/worktrees; AGENTIC-LANDSCAPE.md §3.1.

**D5 Security** — 4: Significant improvement from the prior Observability score. Cursor rolled out OS-level agent sandboxing in early 2026 across macOS (Apple Seatbelt/sandbox-exec), Linux (Landlock + seccomp), and Windows (WSL2). Background agents run in Docker containers on AWS VMs. Enterprise customers including NVIDIA are confirmed users of the sandboxing system. This satisfies component (b) documented sandboxed execution. Cursor Bugbot reviews 2M+ PRs/month for security vulnerabilities, bugs, and performance issues, achieving a 70% resolution rate; its Automations platform includes dedicated security agents (Agentic Security Review, Vuln Hunter) that run on every PR push — satisfying component (c) security-focused review step before merge. Cursor released security automation templates enabling scalable vulnerability detection; four autonomous security agents catch 200+ vulnerabilities/week across 3,000+ PRs — approaching component (a). However: no documented automated SAST/SCA tool integrated into the core agent pipeline (Bugbot is behavior-heuristic, not SAST); no published threat model for prompt injection protection in background agents (a CVE-2025-59944 was disclosed for a case-sensitivity sandbox escape). 3 of 4 components met: sandboxed execution + security review step + partial vulnerability detection automation. Score 4. Source: adwaitx.com "Cursor AI Agent Sandboxing Explained"; cursor.com/blog/security-agents; cursor.com/bugbot; adwaitx.com "Cursor Bugbot Deploys..."; snyk.io "Cursor's AI Security Agents"; lakera.ai CVE-2025-59944 analysis.
[MEDIUM CONFIDENCE — sandboxing and Bugbot confirmed; SAST integration and prompt injection defense not formally documented in public security model]

**D6 Quality Checks** — 3: Cursor Automations (March 2026 GA, TechCrunch) enables event-triggered agents that run on every PR open/push. Bugbot Autofix automatically spawns cloud agents to test code and propose fixes when bugs are detected, processing 2M+ PRs/month. Automations support PR risk classification (auto-approve low-risk PRs, assign reviewers for high-risk). A morning test-coverage automation reviews recently merged code and adds missing tests. However: these are Automations platform features that teams configure — they are not built-in blocking gates in the background agent pipeline itself. Background agents create PRs but the quality checks (Bugbot, Automations) run as separate triggers, not as pre-submission gates within the agent. Coverage enforcement is a configured automation, not enforced by default. Score 3: automated test execution and code review capabilities exist, but they are platform-layer opt-in rather than blocking pre-merge gates embedded in the agent workflow. Source: cursor.com/blog/automations; techcrunch.com "Cursor is rolling out a new kind of agentic coding tool"; adwaitx.com "Cursor Bugbot Autofix Now Live"; helpnetsecurity.com "Cursor Automations turns code review and ops into background tasks."
[MEDIUM CONFIDENCE — Bugbot and Automations confirmed; whether they constitute a mandatory gate in background agent workflow vs. configurable add-on requires documentation clarification]

**D7 Setup** — 5: *Unchanged from prior audit.* Download Cursor IDE, sign in, begin using agents immediately. MAX mode requires one toggle. No infrastructure setup. First parallel run achievable in under 15 minutes. Source: cursor.com.

**D8 Scalability** — 3: *Unchanged from prior audit.* Hard ceiling of 8 parallel background agents, documented. Practical sweet spot in community reports is 3–5; cost model disincentivizes 8-agent runs; agents are completely independent with no coordination mechanism. Source: cursor.com/docs/configuration/worktrees; AGENTIC-LANDSCAPE.md §3.1.

---

### Augment Code / Intent

**D1 Cost** — 2: *Unchanged from prior audit.* Indie plan: $20/month (40,000 credits); Standard: $60/developer/month (130,000 credits); Max: $200/developer/month (450,000 credits). A complex multi-service feature costs ~4,300 credits; at Indie pricing, ~9 complex tasks per month. For a 3–5 agent run on a complex feature, estimated $7–$22 per run depending on plan tier. Source: awesomeagents.ai Augment Code Intent review; augmentcode.com/product/intent.

**D2 Efficiency** — 3: *Unchanged from prior audit.* Intent's Coordinator dispatches Specialists in waves into isolated git worktrees. Parallel execution within a wave is confirmed. Practical ceiling of "3–4 parallel specialists with one human reviewer." Sequential merge strategy introduces serialization at integration time. No published wall-clock benchmarks. Source: AGENTIC-LANDSCAPE.md §3.3; augmentcode.com/product/intent.
[MEDIUM CONFIDENCE — parallel dispatch confirmed; merge serialization documented; no wall-clock timing]

**D3 Accuracy** — 4: *Unchanged from prior audit.* Augment Code's SWE-bench agent achieves 70.6% on SWE-bench Verified (public leaderboard). Auggie on Claude Opus 4.5 scored 51.80% on SWE-bench Pro (Scale AI's harder variant). These scores are for the base agent; Intent's multi-agent coordinator is not independently benchmarked. Source: github.com/augmentcode/augment-swebench-agent; VentureBeat "Augment Code debuts AI agent with 70% win rate."
[MEDIUM CONFIDENCE — benchmark is for base agent; Intent coordinator not independently benchmarked]

**D4 Workflow Rigor** — 3: *Unchanged from prior audit.* Intent provides Coordinator / Specialist / Verifier — 3 distinct roles. Verifier continuously checks results against a shared spec. Specialists execute in isolated git worktrees. Satisfies role separation and ongoing verification. Missing: frozen contracts, pre-flight file ownership matrix, formal failure taxonomy, circuit breaker. Source: AGENTIC-LANDSCAPE.md §3.3; augmentcode.com/product/intent.

**D5 Security** — 3: Intent Specialists run in isolated git worktrees (macOS desktop app). Workspaces are per-task isolated environments — this provides local filesystem scoping, though it is not a cloud VM sandbox. Augment Code's Context Engine incorporates SAST security scanning and dependency vulnerability scanning as part of automated pre-merge checks per search results from augmentcode.com; this would satisfy component (a) if confirmed as a blocking gate. Augment Code publishes guidance on prompt injection vulnerabilities in multi-agent systems and documents instruction/data-pathway separation at the orchestration layer (per the ICLR 2025 StruQ paper citation). However: Intent is a macOS desktop app — code runs locally on the developer's machine, not in isolated cloud VMs. Worktree isolation is git-level scope control, not OS-level sandboxing. The SAST claim appears on comparison pages and guides (not in Intent's own feature documentation); its integration as a blocking gate in Intent specifically is [LOW CONFIDENCE]. Augment Code holds ISO/IEC 42001 certification (AI management governance) — the first AI coding tool to do so. Score 3: some isolation (worktrees) + partial evidence for automated scanning + documented security guidance, but no cloud VM sandboxing and SAST integration into Intent specifically is uncertain. Source: augmentcode.com/guides/ai-code-vulnerability-audit-fix-the-45-security-flaws-fast; augmentcode.com/guides/prompt-injection-vulnerabilities-threatening-ai-development; augmentcode.com/tools/intent-vs-claude-code; augmentcode.com/product/intent.
[MEDIUM CONFIDENCE — worktree isolation confirmed; SAST claim on comparison pages but not Intent product docs specifically; prompt injection defense documented at conceptual level]

**D6 Quality Checks** — 4: Intent's Verifier agent is a dedicated role that checks Specialist outputs against the living specification before work is considered complete. Augment Code documentation confirms "verification and quality gates keep multi-agent output mergeable by converting 'looks right' into executable evidence: tests, static checks, and policy enforcement before human review, with a layered pipeline that blocks most regressions automatically." This satisfies component (a) automated test execution, component (b) independent review step (Verifier is architecturally separate from Specialists), and component (c) spec/acceptance criteria compliance check (Verifier reads the same living spec). Coverage reporting (component d) is not documented. The Verifier is not merely advisory — it flags inconsistencies and blocks advancement until addressed, per the architecture description. Score 4: 3 of 4 components met with a genuine blocking Verifier role. Source: augmentcode.com/product/intent; augmentcode.com/guides/how-to-run-a-multi-agent-coding-workspace; augmentcode.com/tools/intent-vs-claude-code; augmentcode.com/tools/intent-vs-cline.
[MEDIUM CONFIDENCE — Verifier role confirmed by official docs and comparison pages; blocking behavior described but implementation details proprietary]

**D7 Setup** — 4: *Unchanged from prior audit.* Intent is a macOS desktop app (public beta; Windows on waitlist as of 2026-03-31). Requires Augment Code account and GitHub/Linear/Sentry integration setup. Setup achievable within one hour for developers familiar with the integrations. Source: augmentcode.com/product/intent.
[MEDIUM CONFIDENCE — macOS only; Windows unavailable as of 2026-03-31]

**D8 Scalability** — 3: *Unchanged from prior audit.* Documented practical ceiling of 3–4 parallel Specialists. Sequential merge strategy adds coordination overhead beyond 3 simultaneous agents. No evidence of effective runs at 6+ agents. Source: AGENTIC-LANDSCAPE.md §3.3; augmentcode.com/product/intent.

---

### GitHub Copilot Workspace

**D1 Cost** — 3: *Unchanged from prior audit.* GitHub Copilot Pro is $10/month (300 premium requests); Pro+ is $39/month (1,500 premium requests). Overage billing at $0.04 per additional premium request (introduced June 2025). Workspace tasks are typically within monthly allocation for Pro+ users. Single-agent sequential architecture limits per-run cost compared to multi-agent systems. Source: github.com/features/copilot/plans; pecollective.com GitHub Copilot Pricing March 2026.

**D2 Efficiency** — 2: *Unchanged from prior audit.* GitHub Copilot Workspace is a sequential pipeline: specification → plan → implementation → review → PR. No parallelism between stages. Agent mode in VS Code and JetBrains (GA March 2026) is single-threaded. Agent HQ for multi-agent orchestration is roadmapped but not GA. Source: AGENTIC-LANDSCAPE.md §3.4; github.blog "GitHub Copilot: meet the new coding agent."

**D3 Accuracy** — 4: *Unchanged from prior audit.* Copilot Workspace scored 55–56% on SWE-bench Verified (multiple community sources, March 2025). NxCode comparison reports 78% accuracy vs 62% for Cursor on multi-file tasks (methodology unspecified). Source: ucstrategies.com GitHub Copilot Review 2026; NxCode Copilot 2026 guide.
[MEDIUM CONFIDENCE — 55–56% SWE-bench cited by multiple sources; NxCode 78% figure is third-party, methodology unverified]

**D4 Workflow Rigor** — 2: *Unchanged from prior audit.* Copilot Workspace provides an auditable sequential pipeline with human-editable stages. Single-agent sequential architecture — no inter-agent contracts, no file ownership matrix, no failure taxonomy, no adversarial review between independent agents. The human is the reviewer. Source: AGENTIC-LANDSCAPE.md §3.4; github.blog coding agent announcement.

**D5 Security** — 5: GitHub Copilot Workspace's coding agent is uniquely integrated with GitHub's security infrastructure. When the coding agent writes code, it automatically runs: (a) CodeQL (SAST — satisfies component a), (b) the GitHub Advisory Database for dependency vulnerability checks (component a), (c) secret scanning (component a), and (d) Copilot Code Review (security-focused review step — component c). These validation tools are enabled by default, free of charge, and do not require a GitHub Advanced Security license. The coding agent runs in a cloud-hosted environment (sandboxed from the host machine — component b). GitHub is additionally expanding to AI-powered security scanning beyond CodeQL, covering Shell/Bash, Dockerfiles, Terraform, PHP (public beta Q2 2026). The Copilot Autofix feature resolved 460,000+ security alerts with a 0.66-hour average resolution time. The March 2026 changelog confirmed admins can configure which validation tools the coding agent runs. For prompt injection / privilege escalation (component d): GitHub's security model runs the coding agent within GitHub Actions infrastructure with repository-scoped permissions; no explicit prompt injection defense model is published, but the sandboxed GitHub Actions environment and repository permission model mitigate privilege escalation. Score 5: all four components met — automated SAST (CodeQL + Advisory DB + secret scanning) + sandboxed cloud execution + security review step (Copilot Code Review) + architectural privilege containment via GitHub Actions scoping. This is the strongest security posture in the commercial group. Source: github.blog/changelog/2026-03-18-configure-copilot-coding-agents-validation-tools/; docs.github.com/en/code-security/responsible-use/responsible-use-autofix-code-scanning; github.blog "Found means fixed: Introducing code scanning autofix"; we-fix-pc.com "GitHub adds AI-powered bug detection" (March 2026).
[HIGH CONFIDENCE — CodeQL + Advisory DB + secret scanning + Copilot Code Review all confirmed by official GitHub documentation and changelog]

**D6 Quality Checks** — 4: The Copilot coding agent automatically runs tests and linter on every task (component a — pass/fail gate). Copilot Code Review (shipped March 2026) provides a dedicated review step that gathers full project context and can pass suggestions directly to the coding agent to generate fix PRs (component b — peer review step, though it is Copilot reviewing Copilot rather than an independent agent). The coding agent iterates on issues found before stopping work and requesting human review — it does not deliver code that fails its own validation gates. The living specification / task brief forms an acceptance criteria check (component c — partial). Coverage reporting is not built into the default pipeline (component d missing). Score 4: 3 of 4 components met; the review step (component b) is partially non-independent (Copilot reviewing its own code) but is architecturally separated from the coding step. Source: github.blog/changelog/2026-03-18-configure-copilot-coding-agents-validation-tools/; docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent; nxcode.io "GitHub Copilot 2026: Complete Guide."
[HIGH CONFIDENCE — validation tool automation confirmed by official docs]

**D7 Setup** — 5: *Unchanged from prior audit.* GitHub Copilot is bundled into GitHub, web-based, accessible to all paid Copilot users. No local installation required for Workspace. Agent mode requires VS Code or JetBrains extension (one click). First run achievable in under 15 minutes. Source: github.com/features/copilot/plans.

**D8 Scalability** — 1: *Unchanged from prior audit.* Single-agent pipeline. Agent HQ (multi-agent coordination) is roadmapped, not GA. No meaningful parallel execution path in the current product. Source: AGENTIC-LANDSCAPE.md §3.4; github.blog "The agent awakens."

---

### Factory (Droids)

**D1 Cost** — 3: *Unchanged from prior audit.* Factory pricing: free tier (20M tokens included), Starter ($20/month), scaling to Enterprise ($2,000/month). Model-agnostic: supports Claude Sonnet 4, GPT-5, Gemini 2.5 Pro, Claude Opus 4.1, o3. At standard model rates with a capable model, a 3–5 agent parallel run runs $2–$8 depending on task size — within D1 score-3 range. Source: factory.ai/pricing; every.to Vibe Check Factory review; fritz.ai Factory review 2026.
[MEDIUM CONFIDENCE — model costs are user-chosen; orchestration overhead is unknown]

**D2 Efficiency** — 3: *Unchanged from prior audit.* Factory's Droids are cloud-native and parallelizable. Multiple Droids confirmed running concurrently (Groq case study). Orchestrator breaks large projects into milestones; within a milestone, workers execute in parallel. However, each milestone ends with a validation phase before proceeding — serialization between milestones. No published wall-clock timing. Source: factory.ai/news/missions; factory.ai case study with Groq; rimusz.net Factory.ai Droids overview.
[MEDIUM CONFIDENCE — parallel Droid execution confirmed; milestone serialization documented]

**D3 Accuracy** — 3: *Unchanged from prior audit.* Factory's Droids achieved #1 on Terminal Bench with 58.75%. No SWE-bench Verified score published. Terminal Bench is a CLI task completion benchmark, not SWE-bench. Community production reports are positive. Conservative score 3 per rubric: no SWE-bench equivalent, strong Terminal Bench result. Source: factory.ai/news/terminal-bench; latent.space Factory profile; fritz.ai Factory review 2026.
[MEDIUM CONFIDENCE — Terminal Bench #1 confirmed; SWE-bench equivalent absent]

**D4 Workflow Rigor** — 3: *Unchanged from prior audit.* Factory implements orchestrator + milestone-based validation phases + specialized Droids (CodeDroid, Review Droid, QA Droid). Role separation + checkpoint-based verification. Missing: frozen interface contracts, pre-flight file ownership declarations, formal failure taxonomy (transient/logical/structural), adversarial review at planning time. Meets D4 score-3 criteria. Source: factory.ai/news/missions; latent.space Factory profile.

**D5 Security** — 4: Factory operates a strong security posture. Each Code Droid runs in a strictly defined sandboxed environment that isolates its operational scope from main development environments (component b — cloud VM sandboxing confirmed). Factory developed DroidShield, an internal real-time static code analysis algorithm that detects security vulnerabilities, bugs, and IP breaches before code is committed — satisfying component (a) automated vulnerability scanning. Factory employs enterprise-grade audit trails with all Droid actions traceable and reversible. Factory is one of the first AI platforms certified with ISO 42001 (AI management governance) and holds SOC 2 and ISO 27001 certifications; regular penetration testing and internal red-teaming are documented. A dedicated Review Droid provides independent code review as a quality/security gate (component c — security-focused review step). The primary gap is component (d): no specific published documentation on prompt injection defense architecture or formal privilege escalation threat model. Score 4: 3 of 4 components met — sandboxed execution + DroidShield SAST + Review Droid security gate. Source: factory.ai/news/code-droid-technical-report; factory.ai/enterprise; docs.factory.ai (DroidShield documentation); apidog.com "Vibe Coding and Factory AI"; stackoverflow.blog Q&A with Eno Reyes of Factory (Feb 2026).
[MEDIUM CONFIDENCE — DroidShield and sandboxing confirmed in technical report and docs; prompt injection defense not publicly specified]

**D6 Quality Checks** — 4: Factory implements a four-phase loop: Spec → Test → Implement → Verify. The QA Droid executes tests during the Test phase (component a — automated test execution with pass/fail gate). The Review Droid provides independent code review before merge (component b — peer review by a separate agent, not the implementing agent). The Delegator/orchestrator verifies results against the spec at each milestone boundary (component c — spec compliance verification). Factory's DroidShield runs static analysis on code before it is committed (additional quality gate). The Spec-mode default requires read-only operations before the --auto flag enables writes, adding a risk-tiered gate. The gap is coverage reporting (component d) — not documented as a built-in output. However, the Spec → Test → Implement → Verify loop with dedicated QA and Review Droids is the most systematic quality architecture in the commercial group outside of Copilot Workspace's GitHub-native integrations. Score 4: 3 of 4 components met with a genuine multi-stage, multi-agent quality pipeline. Source: factory.ai/news/missions ("four-phase loop"); factory.ai/news/code-droid-technical-report; factory.ai/enterprise; medium.com "How to make Droids code for hours using Test-Driven Development"; stackoverflow.blog Q&A with Eno Reyes.
[MEDIUM CONFIDENCE — QA Droid and Review Droid confirmed; four-phase loop documented; coverage reporting not confirmed]

**D7 Setup** — 4: *Unchanged from prior audit.* Web-based with CLI component. Sign up at factory.ai, connect GitHub/GitLab, assign a Droid task. Free tier requires no payment. Full integration setup (Jira, Sentry, Linear, Notion) may take a half-day. First Droid run achievable within one hour. Source: factory.ai; fritz.ai Factory review 2026.

**D8 Scalability** — 3: *Unchanged from prior audit.* Factory explicitly supports parallel Droid execution ("script and parallelize Droids at massive scale"). Groq case study confirms multiple simultaneous Droids in production. Milestone-based serialization limits within-project parallelism; parallelism is more effective across independent tasks. Practical evidence centers on 3–6 parallel Droids; no published ceiling. Source: factory.ai (parallel Droids claim); factory.ai/case-studies/groq; rimusz.net Droids overview.
[MEDIUM CONFIDENCE — parallel execution confirmed; scaling ceiling undocumented]

---

## Research Notes

**Search date**: 2026-03-31. Evidence gathered from official product pages, changelogs, benchmark repositories, and community review sites.

**Key findings on new dimensions**:

- **D5 Security leadership**: GitHub Copilot Workspace scores 5 — uniquely, because it integrates CodeQL, Advisory Database, secret scanning, and Copilot Code Review as default, automatic gates on every coding agent run. No other commercial system in this group runs SAST and a dedicated security review as default blocking steps. Cursor achieves 4 through Bugbot + OS-level sandboxing + Automations security templates. Factory achieves 4 through DroidShield + cloud VM isolation + Review Droid.

- **D6 Quality Checks leadership**: Factory scores 4 through a principled four-phase Spec → Test → Implement → Verify loop with dedicated QA and Review Droids. GitHub Copilot Workspace also scores 4 through automatic test + linter execution, CodeQL, and Copilot Code Review before requesting human review. Augment Code / Intent scores 4 through the Verifier agent that blocks on spec non-compliance.

- **Devin prompt injection caveat**: The unremediated prompt injection vulnerability (embracethered.com, disclosed April 2025, no fix confirmed by 2026-03-31) is a concrete, documented security gap. This is not speculative — it was exploited live and reported to Cognition. This directly affects Devin's D5 score ceiling.

- **Cursor Automations distinction**: Cursor's quality and security features in 2026 are powerful but are largely Automations platform features that teams configure — they are not enforced blocking gates in the background agent workflow by default. This is the key reason D5=4 (sandboxing is default) but D6=3 (quality gates are configurable, not embedded in the agent pipeline by default).

- **D8 note**: GitHub Copilot Workspace retains D8=1 (no parallel execution architecture). Agent HQ is roadmapped but not GA as of 2026-03-31.

**Systems not in Top 15 scope** (Amazon Q Developer, Windsurf): Excluded per PLAN.md instruction to maintain the same Top 15 composition as the prior audit. Their scores from audit-2026/group-commercial.md are not carried forward to the synthesis table.
