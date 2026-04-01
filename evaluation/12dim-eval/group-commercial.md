# Commercial / IDE Systems Scoring Report
**Evaluation**: 12dim-eval
**Howler**: H3-commercial
**Date**: 2026-03-31
**Rubric version**: 12dim-v1.0 (see PLAN.md)
**Prior evaluations referenced**: audit-2026/group-commercial.md, eval-v2/group-commercial.md

---

## Systems Covered

1. Devin (Cognition AI)
2. Cursor agents
3. Augment Code / Intent
4. GitHub Copilot Workspace (incl. Agent HQ / Mission Control)
5. Factory (factory.ai / Droids)

---

## Scoring Table

| System | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | Total |
|--------|----|----|----|----|----|----|----|----|----|----|-----|-----|-------|
| Devin (Cognition AI) | 2 | 4 | 2 | 2 | 4 | 4 | 4 | 6 | 4 | 6 | 2 | 4 | 44 |
| Cursor agents | 2 | 4 | 2 | 2 | 6 | 4 | 2 | 6 | 4 | 6 | 0 | 2 | 38 |
| Augment Code / Intent | 2 | 4 | 8 | 6 | 4 | 4 | 4 | 4 | 6 | 6 | 4 | 2 | 54 |
| GitHub Copilot Workspace | 4 | 4 | 6 | 2 | 6 | 4 | 2 | 8 | 6 | 10 | 4 | 2 | 58 |
| Factory (Droids) | 4 | 4 | 4 | 4 | 6 | 8 | 6 | 8 | 6 | 8 | 4 | 6 | 68 |

---

## Per-System Scoring

---

## Devin (Cognition AI)

**Category**: Commercial / IDE
**Public source**: https://devin.ai; https://cognition.ai/blog/devin-2; https://docs.devin.ai
**Prior eval scores (audit-2026)**: D1=2, D2=4, D3=2, D4=2, D5=3, D6=2, D7=5, D8=3
**Prior eval scores (eval-v2)**: D1=2, D2=4, D3=2, D4=2, D5=3, D6=3, D7=5, D8=3

---

### D1 — Task Decomposition Quality
**Score**: 2
**Evidence**: Managed Devins provide coordinator-worker role separation — a main Devin orchestrates and child Devins execute in isolated cloud VMs. However, Cognition's architecture documentation confirms no pre-flight file ownership declarations, no DAG or dependency graph, and decomposition is entirely implicit in the LLM's reasoning at runtime. No adversarial review step or hazard scan precedes execution. Source: cognition.ai/blog/devin-2; eval-v2/group-commercial.md §Devin D4.

---

### D2 — Interface Contract Enforcement
**Score**: 2
**Evidence**: No formal CONTRACT.md or equivalent frozen interface specification between Managed Devins. Workers share no common type file or frozen naming convention document at drop time. Cognition's documentation describes the coordinator as re-scoping work on failure, not as enforcing a pre-specified contract. Source: eval-v2/group-commercial.md §Devin D4; cognition.ai/blog/devin-2.

---

### D3 — Benchmark Accuracy
**Score**: 2 [LOW CONFIDENCE]
**Evidence**: Cognition's original SWE-bench Technical Report documented 13.86% for Devin 1.0 (2024). No official SWE-bench Verified score has been published for Devin 2.0 or 2.2 as of 2026-03-31. Cognition cites internal metrics (67% of Devin PRs merged, 4x faster problem-solving) from its 2025 annual performance review, but these are unaudited and not SWE-bench equivalent. Score 2 per missing-evidence rule; post-2.0 SWE-bench not published. Source: cognition.ai/blog/swe-bench-technical-report; cognition.ai/blog/devin-annual-performance-review-2025.

---

### D4 — Setup Complexity
**Score**: 8
**Evidence**: Devin is fully cloud-hosted. A developer signs up at devin.ai, provides GitHub OAuth, and assigns the first task — no local installation, no infrastructure setup, no config files. First parallel run is achievable in under 15 minutes for any developer with a GitHub account. Source: devin.ai onboarding flow; digitalapplied.com Devin AI complete guide.

---

### D5 — Parallelism and Execution Efficiency
**Score**: 4
**Evidence**: Managed Devins run each sub-task in a fully isolated cloud VM in parallel; simultaneous execution is confirmed by Cognition's documentation and community reports describing asynchronous PR delivery. No published wall-clock benchmarks for multi-Devin runs. Practical use centers on 2–5 parallel Devins; the ACU cost model disincentivizes larger fan-outs, and no dedicated dispatch-on-DAG mechanism is documented. Scores 4: structured parallelism confirmed, startup sub-5 minutes, but no lightweight mode and no published optimization for coordination overhead. Source: cognition.ai/blog/devin-2; eval-v2/group-commercial.md §Devin D2.

---

### D6 — State Durability and Resumability
**Score**: 4
**Evidence**: Devin supports explicit checkpoints: restoring a checkpoint rolls back Devin's files and memory to a prior point in time, documented in Devin Docs. Devin also auto-generates and updates repo Knowledge (structure, components) that persists across sessions and can be pinned. Session state is preserved in cloud VM state. However, the checkpoint model is user-initiated rather than automatic, and the resume procedure requires manual operator action (read checkpoint, instruct retry). Scores 4: checkpoint-based persistence at phase transitions, but no automatic resume protocol and no continuous per-worker state files updated throughout execution. Source: docs.devin.ai (checkpoint documentation); cognition.ai/blog/sept-24-product-update.

---

### D7 — Failure Handling and Recovery
**Score**: 4
**Evidence**: Devin 2.2 introduced Devin Review, which categorizes issues by severity (bugs, warnings, FYI) and iterates on CI failures until tests pass before submitting a PR. The coordinator re-scopes on failure. However, Cognition does not publish a formal failure taxonomy (transient/logical/structural), does not document a circuit breaker, and recovery escalation to the human is by timeout or user intervention rather than typed escalation. A known unremediated prompt injection vulnerability (embracethered.com, disclosed 2025) represents a failure pathway outside the recovery model. Scores 4: classified failure behavior exists (severity-tiered review + CI-iterate-until-pass) but falls short of a typed failure taxonomy with distinct handling paths. Source: docs.devin.ai/work-with-devin/devin-review; eval-v2/group-commercial.md §Devin D6.

---

### D8 — Observability and Debuggability
**Score**: 6
**Evidence**: Devin provides a live IDE view where users watch it work in its terminal, browser, and editor in real time; users can intervene, steer, and view Devin's step-by-step reasoning. The Devin Review feature (2.2) provides a structured diff-review output categorized by severity. The 2026 release notes confirm real-time session logs are available. However, no OpenTelemetry export, no timeline/trace view of phase transitions, and no per-agent cost breakdown is documented for Managed Devins. Scores 6: real-time status roster per agent (running/done/failed visible in UI) with per-agent log visibility, but no timeline view or external monitoring integration. Source: docs.devin.ai/release-notes/2026; digitalapplied.com Devin AI complete guide; eval-v2/group-commercial.md §Devin D5.

---

### D9 — Pre-Merge Quality Gates
**Score**: 4
**Evidence**: Devin iterates on CI failures until tests pass before submitting a PR — this constitutes an automated test execution gate. Devin Review (2.2) categorizes issues by severity and feeds back to the agent before PR delivery. However, Devin Review is self-review (Devin reviewing its own output), not an independent agent review; and the review step is not confirmed as a mandatory blocking gate that prevents PR creation if issues remain. Scores 4: automated test execution with a pass/fail gate confirmed, but the review step is not architecturally independent and security-gate documentation is absent. Source: docs.devin.ai/work-with-devin/devin-review; dev.to "How to Let Devin AI Write Tests and Work Until CI Passes."

---

### D10 — Security Posture
**Score**: 6
**Evidence**: Devin operates inside isolated cloud DevBox VMs (confirmed sandboxed execution). The Devin Review feature provides a security-focused review of generated code with severity tiers. Augment Code's comparison pages confirm Devin's sandbox model. However, an unremediated prompt injection vulnerability (discovered and reported by Johann Rehberger, embracethered.com, disclosed April 2025) showed that Devin could be manipulated via GitHub issues to expose ports and leak access tokens; no confirmed remediation was announced as of 2026-03-31. No automated SAST integration is documented. Scores 6: sandboxed execution + security review gate confirmed, but known unremediated prompt injection gap prevents scoring higher. Source: embracethered.com "I Spent $500 To Test Devin AI For Prompt Injection"; cognition.ai/blog/devin-review; pillar.security "Hidden Security Risks of SWE Agents."

---

### D11 — Independent Validation and Spec Compliance
**Score**: 2
**Evidence**: Devin does not employ an independent agent to verify worker output against postconditions or acceptance criteria. The Devin Review feature is self-review by the same agent. No SENTINEL-REPORT.md equivalent, no post-merge compliance pass, and no formal traceability from spec to test to artifact is documented. Human review is required before merge. Scores 2: human spot-check is the validation mechanism; no automated independent validation step. Source: docs.devin.ai; cognition.ai/blog/devin-2.

---

### D12 — Cross-Run Learning and Memory
**Score**: 4
**Evidence**: Devin supports a persistent Knowledge system: users can create, organize, and pin knowledge notes; Devin auto-generates and auto-updates Repo Knowledge on codebase structure and components across sessions. Devin "remembers context and previous interactions" per Gartner peer reviews. However, lessons are surfaced via manually managed knowledge notes, not automatically extracted from run artifacts. No structured LESSONS.md equivalent, no entity registry, and no automated injection of past failure patterns into new run prompts is documented. Scores 4: structured lesson capture exists (Repo Knowledge + user notes persist and are available to future runs), but automatic injection and entity-level memory are absent. Source: docs.devin.ai (Knowledge documentation); Devin AI Guide 2026 (Gartner Peer Insights); cognition.ai/blog/sept-24-product-update.

---

### Narrative

Devin's strongest dimension is **setup friction** (D4=8) — cloud-native, zero-install, productive in 15 minutes. Its observability (D8=6) and security posture (D10=6) have meaningfully improved with Devin Review and VM isolation. The persistent weakness is pre-execution rigor: with no formal decomposition, no contracts, and only a self-review quality gate, Devin is best suited for well-scoped single-agent tasks rather than coordinated multi-agent delivery. The post-2.0 SWE-bench gap (D3=2) is a credibility issue that affects competitive positioning. Knowledge management (D12=4) is a genuine strength relative to most peers in this group. Devin is the right tool for asynchronous background task execution on bounded problems; it is the wrong tool for large-scale parallel delivery requiring coordination guarantees.

---

## Cursor Agents

**Category**: Commercial / IDE
**Public source**: https://cursor.com; https://cursor.com/docs/configuration/worktrees; https://cursor.com/changelog
**Prior eval scores (audit-2026)**: D1=2, D2=4, D3=3, D4=2, D5=2, D6=2, D7=5, D8=3
**Prior eval scores (eval-v2)**: D1=2, D2=4, D3=3, D4=2, D5=4, D6=3, D7=5, D8=3

---

### D1 — Task Decomposition Quality
**Score**: 2
**Evidence**: Each parallel background agent operates independently in its own git worktree with no pre-flight coordination. No task ownership contracts, no DAG, no scope statements per worker, no hazard scan, and no adversarial review step are documented. Cursor's official parallel agents documentation describes worktree isolation but says nothing about pre-execution decomposition artifacts. Conflicts are discovered at merge time. Source: cursor.com/docs/configuration/worktrees; eval-v2/group-commercial.md §Cursor D4.

---

### D2 — Interface Contract Enforcement
**Score**: 2
**Evidence**: No formal contract between parallel background agents. Workers share no type file or interface document at drop time — they are fully independent. Cursor agent best practices documentation recommends `.cursor/rules` for conventions, but these are informal prompts, not a frozen contract that workers may not modify. Source: cursor.com/blog/agent-best-practices; cursor.com/docs/rules.

---

### D3 — Benchmark Accuracy
**Score**: 2 [LOW CONFIDENCE]
**Evidence**: Cursor has not published a standalone SWE-bench Verified score for its agent architecture. Community sources note that Claude 3.7 Sonnet in Cursor achieves approximately 56% SWE-bench Verified in some configurations, but this reflects the underlying model capability, not Cursor's architecture contribution. As of March 2026, Cursor 2.4 introduced subagents but no new benchmark publication has appeared. Score 2: no Cursor-specific benchmark result published; model-level scores are not Cursor's own. Source: eval-v2/group-commercial.md §Cursor D3; memu.pro "Cursor 2.4 Introduces Subagents"; NxCode Cursor AI review 2026.

---

### D4 — Setup Complexity
**Score**: 10
**Evidence**: Download the Cursor IDE, sign in, and begin using agents immediately — no API key configuration beyond a Cursor account, no infrastructure setup, no config files required. Background agents are activated with a single toggle to MAX mode. Core concepts are discoverable in minutes. Source: cursor.com; NxCode Cursor AI review 2026.

---

### D5 — Parallelism and Execution Efficiency
**Score**: 6
**Evidence**: Cursor 2.0 supports up to 8 parallel background agents, each in a git worktree on a cloud VM, with documented simultaneous execution. Cursor auto-creates and manages worktrees. Background agents deliver PRs asynchronously while the developer continues working locally. No muster ceremony is required for agent dispatch. March 2026 release notes confirm continued background agent improvements. Scores 6: parallel execution with agents dispatched as needed (not batch-complete), startup under 5 minutes, coordinated via git worktrees. Does not score 8 because no lightweight "reaping" mode is documented and coordination overhead is moderate (no DAG dispatch, agents are fully independent). Source: cursor.com/docs/configuration/worktrees; cursor.com/changelog/2-0; releasebot.io Cursor Release Notes March 2026.

---

### D6 — State Durability and Resumability
**Score**: 4
**Evidence**: Cursor auto-saves plan documents to `.cursor/plans/` as editable markdown files that persist across sessions. Cursor's Automations platform can optionally remember outcomes of previous runs to improve future runs. However, if a background agent dies mid-execution, recovery requires manually restarting from the git branch state — there is no documented automatic resume protocol. The `.cursor/plans/` persistence is plan-level, not per-worker continuous state. Source: cursor.com/blog/scaling-agents; cursor.com/blog/automations; eval-v2/group-commercial.md §Cursor D6. [LOW CONFIDENCE — per-worker recovery behavior on session death not formally documented]

---

### D7 — Failure Handling and Recovery
**Score**: 2
**Evidence**: No formal failure taxonomy is published for Cursor background agents. If an agent goes astray, the user stops or corrects it via the UI. The workflow_state.md file documents agent state but recovery is manual operator intervention, not typed classification followed by an automated recovery path. No circuit breaker is documented. Cursor 2.4's subagent model (March 2026) adds intra-task delegation but does not add a failure classification protocol for inter-agent failures. Source: cursor.com/blog/agent-best-practices; memu.pro "Cursor 2.4 Introduces Subagents"; eval-v2/group-commercial.md §Cursor D6. [LOW CONFIDENCE — failure recovery behavior not formally documented]

---

### D8 — Observability and Debuggability
**Score**: 6
**Evidence**: Background agents provide a status panel in the Cursor IDE showing which tasks are running. Automations include hooks that integrate with observability platforms. Cursor's scaling agents blog post confirms operators can monitor agent progress and reasoning via workflow_state.md. The March 2026 updates confirmed improved agent tracking. However, no dedicated timeline view, no per-agent cost breakdown, and no OpenTelemetry trace export are documented for background agent runs. Scores 6: real-time status roster per agent is available; per-agent log inspection is possible; no timeline/trace view. Source: cursor.com/blog/scaling-agents; releasebot.io Cursor Release Notes March 2026; cursor.com/blog/automations.

---

### D9 — Pre-Merge Quality Gates
**Score**: 4
**Evidence**: Cursor Automations (GA March 2026) enables event-triggered agents that run tests and propose fixes on every PR push; Bugbot Autofix automatically spawns agents to fix detected bugs. These are powerful quality features, but they are Automations platform features that teams configure — they are not blocking gates embedded in the background agent pipeline by default. A background agent creates a PR; whether quality checks run before human review depends on team-configured Automations, not the agent pipeline itself. Scores 4: automated test execution is achievable via Automations configuration, but not a default mandatory pre-merge gate. Source: cursor.com/blog/automations; techcrunch.com "Cursor is rolling out a new kind of agentic coding tool" (March 2026); eval-v2/group-commercial.md §Cursor D6.

---

### D10 — Security Posture
**Score**: 6
**Evidence**: Cursor rolled out OS-level agent sandboxing in early 2026 across macOS (Apple Seatbelt/sandbox-exec), Linux (Landlock + seccomp), and Windows (WSL2), with background agents running in Docker containers on AWS VMs. Cursor Bugbot reviews 2M+ PRs/month and includes dedicated security agents (Agentic Security Review, Vuln Hunter). However, no formal SAST tool (Semgrep, CodeQL) is integrated into the default agent pipeline; a CVE-2025-59944 (sandbox escape via case-sensitivity) was disclosed, confirming the sandboxing model has documented bypasses; prompt injection defense is not formally specified. Scores 6: sandboxed execution confirmed + security review gate (Bugbot) confirmed, but no integrated SAST and documented sandbox CVE prevent score 8. Source: adwaitx.com "Cursor AI Agent Sandboxing Explained"; cursor.com/bugbot; lakera.ai CVE-2025-59944 analysis; eval-v2/group-commercial.md §Cursor D5.

---

### D11 — Independent Validation and Spec Compliance
**Score**: 0
**Evidence**: No independent validation step is documented in the Cursor background agent workflow. Background agents create PRs; human review is the only validation against spec or acceptance criteria. No orchestrator validation, no post-merge compliance pass, and no spec traceability mechanism exists in the Cursor agent architecture. Source: cursor.com/docs/configuration/worktrees; cursor.com/blog/agent-best-practices.

---

### D12 — Cross-Run Learning and Memory
**Score**: 2
**Evidence**: Cursor's Automations platform includes a memory tool that lets agents learn from past runs and improve with repetition (per March 2026 beta notes). However, Cursor 2.4's subagent model still resets to "junior-level project understanding every session" per memu.pro analysis; there is no structured LESSONS.md equivalent, no entity registry, and no automatic extraction of failure patterns. The memory tool is a configurable Automations feature, not a built-in cross-run learning mechanism. Source: cursor.com/changelog; memu.pro "Cursor 2.4 Introduces Subagents"; markaicode.com "Cursor Beta Features 2026." [LOW CONFIDENCE — Automations memory tool is in beta; production behavior not fully documented]

---

### Narrative

Cursor's standout dimension is **setup simplicity** (D4=10) — it is the easiest entry point in this group. Parallelism (D5=6) and security (D10=6) are genuine strengths with documented 8-agent parallel execution and OS-level sandboxing. The chronic weakness is the complete absence of pre-execution rigor: no decomposition, no contracts, no independent validation (D11=0), and minimal cross-run memory (D12=2). Cursor is optimized for developer-in-the-loop IDE use where the human provides coordination judgment; it is poorly suited for autonomous large-scale parallel delivery where coordination guarantees matter. The failure handling gap (D7=2) is a significant operational risk for long-horizon tasks.

---

## Augment Code / Intent

**Category**: Commercial / IDE
**Public source**: https://augmentcode.com/product/intent; https://docs.augmentcode.com/intent/overview; https://github.com/augmentcode/augment-swebench-agent
**Prior eval scores (audit-2026)**: D1=2, D2=3, D3=4, D4=3, D5=2, D6=2, D7=4, D8=3
**Prior eval scores (eval-v2)**: D1=2, D2=3, D3=4, D4=3, D5=3, D6=4, D7=4, D8=3

---

### D1 — Task Decomposition Quality
**Score**: 4
**Evidence**: Intent's Coordinator agent breaks specifications into tasks and delegates to specialist implementors (Auth Agent, API Agent, Test Agent, plus six built-in roles: Investigate, Implement, Verify, Critique, Debug, Code Review). Specialists execute in isolated git worktrees. Three mandatory human gates exist: spec approval, task decomposition review, and final diff review. However, no formal file ownership matrix is produced at decomposition time, no DAG is written, no hazard scan is documented, and no adversarial review agent challenges the decomposition before freeze. Scores 4: structured decomposition with defined scope per worker and dependency ordering implied by wave structure, but no formal ownership matrix or hazard analysis. Source: augmentcode.com/product/intent; docs.augmentcode.com/intent/overview; awesomeagents.ai Augment Code Intent review.

---

### D2 — Interface Contract Enforcement
**Score**: 4
**Evidence**: Intent uses a "living specification" as a shared reference that all specialists execute against; the Context Engine tracks the full dependency graph across repositories and identifies which services need updates when contracts change. However, the spec is described as "living" (continuously updated), not frozen at drop time. No formal CONTRACT.md equivalent is written before workers start, and violations do not require a formal AMENDMENT.md escalation. Scores 4: shared type definitions and a living spec exist, but the spec is mutable during execution — it does not meet the "frozen contract" threshold for a 6. Source: augmentcode.com/guides/spec-driven-ai-code-generation-with-multi-agent-systems; augmentcode.com/blog/intent-a-workspace-for-agent-orchestration.

---

### D3 — Benchmark Accuracy
**Score**: 8
**Evidence**: Augment Code's SWE-bench agent achieves 70.6% on SWE-bench Verified (public leaderboard, github.com/augmentcode/augment-swebench-agent). Auggie on Claude Opus 4.5 scored 51.80% on SWE-bench Pro (Scale AI's harder variant). 70.6% places Augment in the 8-range anchor (60–74%). The caveat is that this benchmark reflects the base agent, not Intent's multi-agent coordinator specifically. Source: github.com/augmentcode/augment-swebench-agent; VentureBeat "Augment Code debuts AI agent with 70% win rate." [MEDIUM CONFIDENCE — benchmark is for base agent; Intent coordinator not independently benchmarked]

---

### D4 — Setup Complexity
**Score**: 6
**Evidence**: Intent is a macOS desktop application (public beta; Windows on waitlist as of 2026-03-31). Setup requires an Augment Code account and GitHub/Linear/Sentry integration configuration. The official docs confirm "package install + minimal config" — setup is achievable within one hour for a developer familiar with the integrations, but the macOS-only constraint and integration requirement create meaningful friction relative to web-native systems. Source: augmentcode.com/product/intent; docs.augmentcode.com/intent/overview.

---

### D5 — Parallelism and Execution Efficiency
**Score**: 4
**Evidence**: Intent dispatches Specialists in waves into isolated git worktrees, with parallel execution within a wave confirmed. Augment's own documentation states the practical ceiling is "3–4 parallel specialists with one human reviewer." Sequential merge strategy introduces serialization at integration time. No DAG-aware dispatch (dependency completion triggers next specialist, not batch-complete), and no lightweight mode for small runs. Scores 4: structured parallelism with dependency-aware wave structure, but sequential merge strategy and a low practical ceiling limit efficiency. Source: augmentcode.com/guides/how-to-run-a-multi-agent-coding-workspace; eval-v2/group-commercial.md §Augment D2.

---

### D6 — State Durability and Resumability
**Score**: 4
**Evidence**: Intent's living specification persists across sessions and constitutes a recoverable state artifact. Specialists work in git worktrees, so their output is preserved in git even if a session dies. However, no formal checkpoint protocol, no per-worker HOOK.md equivalent, and no documented automatic resume procedure exists. Recovery requires the developer to read the living spec and re-dispatch the failed specialist. Scores 4: checkpoint-equivalent state (living spec + git) exists at phase boundaries, but resumption is manual. Source: augmentcode.com/product/intent; docs.augmentcode.com/intent/overview.

---

### D7 — Failure Handling and Recovery
**Score**: 4
**Evidence**: Intent's Verifier agent flags inconsistencies and blocks advancement until addressed — this constitutes a detection-and-hold mechanism. The Coordinator re-scopes when specialists fail. Six built-in specialist roles include a Debug specialist for failure investigation. However, no formal failure taxonomy (transient/logical/structural) is published, no circuit breaker is documented, and the Verifier blocks rather than classifying and routing failures. Scores 4: classified failure behavior exists (block-on-spec-failure + debug specialist) but does not reach a typed taxonomy with distinct handling paths and a circuit breaker. Source: augmentcode.com/product/intent; augmentcode.com/blog/intent-a-workspace-for-agent-orchestration; awesomeagents.ai Augment Code Intent review.

---

### D8 — Observability and Debuggability
**Score**: 4
**Evidence**: Intent includes an activity feed for tracking agent progress across tasks (confirmed on official product page). The activity feed provides task status visibility per specialist. However, it is not described as providing structured logs with trace IDs, a timeline view of phase transitions, per-agent cost breakdown, or export to external monitoring tools. Internals of the Coordinator and Context Engine are proprietary. Scores 4: structured per-agent logging via activity feed; status can be inferred; no real-time roster with timeline. Source: augmentcode.com/product/intent; awesomeagents.ai Augment Code Intent review; eval-v2/group-commercial.md §Augment D5.

---

### D9 — Pre-Merge Quality Gates
**Score**: 6
**Evidence**: Intent's Verifier agent is a dedicated role architecturally separate from Specialists; it checks specialist outputs against the living specification and blocks advancement on non-compliance. Documentation confirms "verification and quality gates keep multi-agent output mergeable by converting 'looks right' into executable evidence: tests, static checks, and policy enforcement before human review." This constitutes an automated test gate plus an independent agent review — two of the three required for score 6. Security scanning (DroidShield equivalent) is not confirmed as a default gate in Intent. Scores 6: tests + independent agent review both required before merge; security gate is absent or unconfirmed as mandatory. Source: augmentcode.com/product/intent; augmentcode.com/guides/how-to-run-a-multi-agent-coding-workspace; augmentcode.com/tools/intent-vs-claude-code.

---

### D10 — Security Posture
**Score**: 6
**Evidence**: Augment Code holds ISO/IEC 42001 certification (AI management governance) and SOC 2 Type II — the first AI coding assistant to achieve ISO 42001 certification (August 2025). Intent features customer-managed encryption keys (CMEK). Augment Code documents prompt injection vulnerabilities in multi-agent systems and instruction/data-pathway separation at the orchestration layer. However, Intent runs as a macOS desktop app — specialists work in local git worktrees, not cloud VM sandboxes. SAST integration in Intent specifically is unconfirmed as a blocking gate (it appears in comparison pages but not the Intent product documentation). Scores 6: security review conceptually documented + ISO 42001/SOC 2 governance + CMEK; no cloud VM sandboxing, SAST gate unconfirmed. Source: augmentcode.com/guides/ai-coding-tools-soc2-compliance-enterprise-security-guide; ysecurity.io "ISO 42001 Augment Code Case Study"; augmentcode.com/guides/prompt-injection-vulnerabilities-threatening-ai-development.

---

### D11 — Independent Validation and Spec Compliance
**Score**: 4
**Evidence**: Intent's Verifier agent reads specialist outputs against the living specification and flags deviations — this constitutes orchestrator-level validation of worker output against documented postconditions. The Verifier is architecturally separate from Specialists. However, no post-merge compliance report (SENTINEL-REPORT.md equivalent) is documented, no formal spec-to-test traceability artifact is produced, and the Verifier operates pre-merge rather than as a post-merge independent compliance pass. Scores 4: automated contract test execution against a living spec is confirmed, but no post-merge spec compliance report. Source: augmentcode.com/product/intent; augmentcode.com/guides/how-to-run-a-multi-agent-coding-workspace.

---

### D12 — Cross-Run Learning and Memory
**Score**: 2
**Evidence**: No structured cross-run learning mechanism is documented for Intent. The living specification persists within a run but is not described as accumulating lessons across runs. No LESSONS.md equivalent, no entity registry, and no automated injection of past failure patterns are mentioned in Intent's documentation or comparison pages as of 2026-03-31. Source: augmentcode.com/product/intent; docs.augmentcode.com/intent/overview. [LOW CONFIDENCE — cross-run memory features not documented; absence of evidence scored conservatively]

---

### Narrative

Augment Code / Intent's headline strength is **benchmark accuracy** (D3=8) — 70.6% on SWE-bench Verified is the highest published result in this commercial group. The Verifier architecture provides genuinely superior quality gates (D9=6) and independent validation (D11=4) relative to most peers. Intent's weakness is the ceiling on parallelism (D5=4) due to sequential merge strategy, and the near-complete absence of cross-run memory (D12=2). The ISO 42001 certification gives it a defensible enterprise security posture (D10=6). Intent is best suited for mid-sized feature development where spec compliance matters more than raw throughput; it is the wrong choice for teams that need 6+ parallel workers or automated cross-session learning.

---

## GitHub Copilot Workspace (incl. Agent HQ / Mission Control)

**Category**: Commercial / IDE
**Public source**: https://github.com/features/copilot; https://docs.github.com/en/copilot/concepts/agents; https://github.blog/ai-and-ml/github-copilot/
**Prior eval scores (audit-2026)**: D1=3, D2=2, D3=4, D4=2, D5=3, D6=2, D7=5, D8=1
**Prior eval scores (eval-v2)**: D1=3, D2=2, D3=4, D4=2, D5=5, D6=4, D7=5, D8=1

**Note**: As of February 2026, GitHub launched Agent HQ with Mission Control in public preview (GA per community discussions March 2026). This materially changes D1, D5, and D8 scores relative to prior evaluations.

---

### D1 — Task Decomposition Quality
**Score**: 4
**Evidence**: Agent HQ / Mission Control (GA March 2026) allows assigning tasks to Copilot across multiple repositories in parallel, with a unified interface to pick agents, watch real-time session logs, and steer mid-run. The coding agent turns issues into PRs working autonomously in the background. However, no formal file ownership matrix, no DAG, no hazard scan, and no adversarial review of decomposition are documented — the human assigns tasks but no pre-execution decomposition artifact is produced by the system. Scores 4: structured decomposition is now available via Mission Control with task scope per agent and dependency ordering implied by sequential issue assignment, but no formal ownership matrix or hazard analysis. Source: github.blog/news-insights/company-news/welcome-home-agents/; github.blog/ai-and-ml/github-copilot/how-to-orchestrate-agents-using-mission-control/; creati.ai "GitHub Agent HQ with Claude and Codex AI Integration."

---

### D2 — Interface Contract Enforcement
**Score**: 2
**Evidence**: No formal CONTRACT.md or frozen interface specification between agents is produced by GitHub Copilot's coordination layer. Agents are assigned individual issues or tasks; no shared type file or naming convention document is enforced before workers start. Mission Control provides routing and visibility but not contract authoring or enforcement. Source: github.blog/ai-and-ml/github-copilot/how-to-orchestrate-agents-using-mission-control/; docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent.

---

### D3 — Benchmark Accuracy
**Score**: 6
**Evidence**: GitHub Copilot coding agent scored 55–56% on SWE-bench Verified (multiple community sources, including NxCode and ucstrategies.com, citing March 2025 results). 55–56% places it in the 6-range anchor (40–59% SWE-bench Verified). No updated official SWE-bench score for 2026 has been published by GitHub. Source: nxcode.io "GitHub Copilot 2026: Complete Guide"; ucstrategies.com GitHub Copilot Review 2026; eval-v2/group-commercial.md §Copilot D3. [MEDIUM CONFIDENCE — 55–56% SWE-bench cited by multiple community sources; no official GitHub publication]

---

### D4 — Setup Complexity
**Score**: 8
**Evidence**: GitHub Copilot is bundled into GitHub and web-accessible to all paid Copilot users. No local installation required for Copilot Workspace or Agent HQ. Agent mode requires only a VS Code or JetBrains extension (one click). Mission Control is accessible from the GitHub web interface. First productive run is achievable in under 15 minutes. Source: github.com/features/copilot/plans; nxcode.io GitHub Copilot 2026 guide.

---

### D5 — Parallelism and Execution Efficiency
**Score**: 6
**Evidence**: Agent HQ / Mission Control (GA March 2026) enables assigning tasks to multiple Copilot agents in parallel across repositories, with real-time tracking of all running sessions. Agents are dispatched as tasks are assigned (not batch-complete), with per-session log visibility. However, no DAG dispatch based on dependency completion is documented — the human assigns tasks; there is no automated dependency-aware sequencing. No lightweight mode equivalent is documented. Scores 6: parallel execution with a real-time management interface confirmed; startup under 5 minutes; no automated DAG dispatch. Source: github.blog/news-insights/company-news/welcome-home-agents/; eficode.com "Why GitHub Agent HQ matters for engineering teams in 2026"; medium.com "Mastering Multi-Agent Orchestration with GitHub Copilot Mission Control."

---

### D6 — State Durability and Resumability
**Score**: 4
**Evidence**: The Copilot coding agent operates via GitHub Actions infrastructure, so run state is persisted in GitHub Actions logs and the git branch. Mission Control's real-time session logs provide post-hoc visibility. However, no explicit checkpoint protocol is documented — if an agent session dies mid-execution, recovery requires manually reviewing the Actions log and re-assigning. No automatic resume procedure, no per-worker continuous state files. Scores 4: phase-level state survives in git and Actions logs, but resumption is manual. Source: docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent; github.blog/changelog/2026-03-18-configure-copilot-coding-agents-validation-tools/. [LOW CONFIDENCE — per-session resume behavior on mid-execution failure not documented explicitly]

---

### D7 — Failure Handling and Recovery
**Score**: 2
**Evidence**: The Copilot coding agent iterates on errors found during execution (it does not stop at first failure) and can steer from Mission Control (pause, refine, or restart). However, no formal failure taxonomy is published, no circuit breaker is documented, and the recovery model is manual operator intervention (steer/restart) rather than typed classification with distinct paths. Scores 2: basic retry-like behavior (iterate on errors) without failure classification. Source: github.blog/ai-and-ml/github-copilot/how-to-orchestrate-agents-using-mission-control/; docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent.

---

### D8 — Observability and Debuggability
**Score**: 8
**Evidence**: Mission Control provides a unified interface to watch real-time session logs for all running agents, steer mid-run, and jump directly to resulting PRs. The platform shows all agents' pending/running/done/failed states in one view. Copilot coding agent runs within GitHub Actions, which provides a full execution timeline with per-step timing. Per-agent log export is available via GitHub Actions logs. GitHub's security tooling (CodeQL, secret scanning, Copilot Code Review) provides additional structured output per run. However, no OpenTelemetry trace export and no per-agent cost breakdown is documented. Scores 8: real-time roster + timeline view (via Actions) confirmed; per-agent log export confirmed; no streaming dashboard or external monitoring integration. Source: github.blog/ai-and-ml/github-copilot/how-to-orchestrate-agents-using-mission-control/; github.blog/news-insights/company-news/welcome-home-agents/; eficode.com "Why GitHub Agent HQ matters."

---

### D9 — Pre-Merge Quality Gates
**Score**: 6
**Evidence**: The Copilot coding agent automatically runs tests, linter, and validation tools (configurable per the March 2026 changelog) before requesting human review. Copilot Code Review (GA March 2026) provides a dedicated review step that gathers full project context and can pass suggestions directly to the coding agent to generate fix PRs. These constitute automated test execution plus an agent-reviewed code review gate. Security gate (CodeQL, secret scanning) is also built in. However, the code review step is Copilot reviewing its own code (not a fully independent agent). Scores 6: tests + code review both required before merge; the review is not fully architecturally independent, and coverage thresholds are not enforced. Source: github.blog/changelog/2026-03-18-configure-copilot-coding-agents-validation-tools/; nxcode.io "GitHub Copilot 2026: Complete Guide."

---

### D10 — Security Posture
**Score**: 10
**Evidence**: The Copilot coding agent integrates GitHub's full security stack as default blocking gates: (a) CodeQL (SAST), (b) GitHub Advisory Database for dependency vulnerabilities, (c) secret scanning — all confirmed as automatic, default, free-of-charge validation tools per the March 2026 changelog; (d) Copilot Code Review with security focus; (e) cloud-hosted sandboxed execution within GitHub Actions infrastructure with repository-scoped permissions; (f) Copilot Autofix resolved 460,000+ security alerts with a 0.66-hour average resolution time; (g) GitHub is the only system in this group that holds both GitHub Advanced Security certification and runs all security checks as non-optional default gates rather than team-configured add-ons. GitHub's SOC 2 and compliance posture is inherited by all Copilot users. Scores 10: SAST + sandboxed execution + formal security certification + supply chain controls (Advisory DB + secret scanning) all confirmed as default pipeline components. Source: github.blog/changelog/2026-03-18-configure-copilot-coding-agents-validation-tools/; docs.github.com/en/code-security/responsible-use/responsible-use-autofix-code-scanning; eval-v2/group-commercial.md §Copilot D5.

---

### D11 — Independent Validation and Spec Compliance
**Score**: 4
**Evidence**: Copilot Code Review (March 2026 GA) provides a dedicated review pass that verifies the coding agent's output against the task spec and can generate fix PRs. Mission Control allows the operator to view progress against the original task. However, no post-merge spec compliance report is generated, no SENTINEL-REPORT.md equivalent exists, and Copilot Code Review is Copilot reviewing Copilot (not a fully independent third agent). Scores 4: automated contract-like review against task spec confirmed, but no post-merge compliance pass and no full independence. Source: github.blog/ai-and-ml/github-copilot/whats-new-with-github-copilot-coding-agent/; nxcode.io "GitHub Copilot 2026: Complete Guide."

---

### D12 — Cross-Run Learning and Memory
**Score**: 2
**Evidence**: No cross-run learning mechanism is documented in Copilot Workspace or Agent HQ. Each task starts from the current repository state. GitHub repositories accumulate learnings in code and issues over time, but no structured LESSONS.md equivalent, no entity registry, and no automated injection of past run outcomes into future agent prompts is documented. Source: github.com/features/copilot; docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent. [LOW CONFIDENCE — absence of documented cross-run learning scored conservatively]

---

### Narrative

GitHub Copilot Workspace / Agent HQ's dominant strength is **security** (D10=10) — the only commercial system in this group with SAST, dependency scanning, secret scanning, and sandboxed execution all operating as default, non-optional pipeline gates. The February–March 2026 Agent HQ launch materially improved parallelism (D5=6) and observability (D8=8) with Mission Control's real-time multi-agent dashboard. The critical weakness remains pre-execution rigor: no decomposition contracts, no interface enforcement, and weak failure handling (D7=2). Cross-run memory (D12=2) is essentially absent. Copilot Workspace is the right choice for security-sensitive enterprises and GitHub-native teams; it is the wrong choice for teams requiring explicit coordination contracts or cross-run learning.

---

## Factory (Droids)

**Category**: Commercial / IDE
**Public source**: https://factory.ai; https://factory.ai/news/missions; https://factory.ai/news/code-droid-technical-report; https://docs.factory.ai
**Prior eval scores (audit-2026)**: D1=3, D2=3, D3=3, D4=3, D5=3, D6=2, D7=4, D8=3
**Prior eval scores (eval-v2)**: D1=3, D2=3, D3=3, D4=3, D5=4, D6=4, D7=4, D8=3

---

### D1 — Task Decomposition Quality
**Score**: 4
**Evidence**: Factory's Droid decomposes high-level problems into subtasks with explicit step-level planning: "a Droid is only as good as its plan," with separate plan steps for frontend, backend, tests, and feature flags. The Missions feature breaks projects into features, spawns worker sessions per feature, and coordinates handoffs through git. Human approval is required for the plan before execution begins. However, no formal file ownership matrix is produced, no DAG artifact is written, no hazard scan is documented, and no adversarial review agent challenges the plan. Scores 4: structured decomposition with defined scope statements and dependency ordering, but no formal ownership matrix or hazard analysis. Source: factory.ai/news/missions; factory.ai/news/code-droid-technical-report; zenml.io "Factory.ai: Autonomous Software Development."

---

### D2 — Interface Contract Enforcement
**Score**: 4
**Evidence**: Factory's Droid uses the spec and plan as shared reference artifacts that all workers execute against. The spec-driven workflow ("you describe what you want and approve the plan") functions as a shared interface document. Custom Droids (subagents) can be configured with specific roles, and git is the source of truth for integration. However, the spec is not frozen at drop time in a formal CONTRACT.md structure — it can be revised during execution. No formal AMENDMENT.md escalation path for contract deviations is documented. Scores 4: shared spec artifact functions as a de facto contract that workers reference, but it is not frozen and violations do not require formal escalation. Source: factory.ai/news/missions; docs.factory.ai/cli/configuration/custom-droids; sidbharath.com "Factory.ai Guide."

---

### D3 — Benchmark Accuracy
**Score**: 4
**Evidence**: Factory's Droids achieved #1 on Terminal Bench with 58.75%. No SWE-bench Verified score has been published by Factory as of 2026-03-31. Terminal Bench is a CLI task completion benchmark measuring different capabilities than SWE-bench Verified. Community production reports are positive, but no SWE-bench equivalent result exists to anchor a score above 4. Scores 4: strong community-reported results and a leading Terminal Bench position, but no SWE-bench Verified equivalent published. Source: factory.ai/news/terminal-bench; eval-v2/group-commercial.md §Factory D3. [MEDIUM CONFIDENCE — Terminal Bench #1 confirmed; SWE-bench equivalent absent]

---

### D4 — Setup Complexity
**Score**: 6
**Evidence**: Factory is web-based with a CLI component. Signup at factory.ai, connect GitHub/GitLab, and assign the first Droid task — free tier requires no payment information. Full integration setup (Jira, Sentry, Linear, Notion) may take a half-day. The first Droid run is achievable within one hour for a developer familiar with the integrations. Scores 6: package install + minimal config; works out of the box with a short getting-started guide. Source: factory.ai; fritz.ai Factory review 2026; eval-v2/group-commercial.md §Factory D7.

---

### D5 — Parallelism and Execution Efficiency
**Score**: 6
**Evidence**: Factory explicitly supports parallel Droid execution ("script and parallelize Droids at massive scale") with confirmed concurrent execution in the Groq case study. Missions break projects into features and spawn worker sessions per feature, dispatching as dependencies are satisfied rather than batch-complete. Median mission runs ~2 hours; 14% run longer than 24 hours. No documented practical ceiling on parallel Droids, unlike Cursor's 8-agent hard limit. However, each milestone ends with a validation phase before proceeding, which introduces serialization between milestones. No sub-3-minute "reaping" mode is documented. Scores 6: parallel execution with dependency-aware dispatch within missions, startup under 5 minutes, no hard ceiling on parallelism. Source: factory.ai/news/missions; factory.ai (case studies/groq); rimusz.net Droids overview; eval-v2/group-commercial.md §Factory D2.

---

### D6 — State Durability and Resumability
**Score**: 8
**Evidence**: Factory provides two distinct state durability mechanisms. First, Droid Computers are persistent compute environments that retain state (installed packages, files, running services, configuration) between sessions — explicitly documented as "unlike ephemeral cloud templates that are destroyed after each session." Second, Factory maintains Org and User-level Memory capturing decisions, docs, and runbooks so "every Droid remembers your context across sessions." Missions recover from failures automatically per documentation: "Droid breaks projects into features, spawns worker sessions for each one, coordinates handoffs through git, validates at every step, and recovers from failures automatically." This satisfies per-worker state files updated continuously during execution plus recovery at the per-worker level. Does not reach 10: automated orchestrator-level session death detection and fully idempotent state transitions are not confirmed. Source: docs.factory.ai/cli/features/droid-computers; factory.ai/news/factory-is-ga; factory.ai/news/missions.

---

### D7 — Failure Handling and Recovery
**Score**: 6
**Evidence**: Factory's failure recovery is multi-layered: (a) Droid validates at every step and recovers from failures automatically within a mission; (b) git is the source of truth, and every command is classified by risk level (Droid Shield scans for secrets before anything reaches a model); (c) the four-phase Spec → Test → Implement → Verify loop means failures at the Verify phase block advancement and trigger a return to Implement. Factory's documentation describes missions as recovering from failures automatically. However, no formal typed failure taxonomy (transient/logical/structural/environmental/conflict) is published, and no circuit breaker with explicit escalation to human after N failures is documented. Scores 6: typed failure behavior with detect-block-retry exists across 3+ distinct categories (step failure, validation failure, git-level conflict), and an automatic recovery path is documented — but no formal named taxonomy or circuit breaker. Source: factory.ai/news/missions; factory.ai/news/code-droid-technical-report; docs.factory.ai/enterprise.

---

### D8 — Observability and Debuggability
**Score**: 8
**Evidence**: Factory provides JSON event streams, detailed logging, session persistence with full debugging and audit capabilities, and — most notably — native OpenTelemetry integration: "every action is logged, and telemetry flows through OpenTelemetry." Droid emits OpenTelemetry metrics, traces, and logs that can be sent to existing collectors (Prometheus, Datadog, Splunk, Jaeger). This constitutes a streaming observability platform with external monitoring integration. Enterprise documentation confirms comprehensive audit trails with all Droid actions traceable and reversible. However, a purpose-built streaming dashboard (vs. sending to external tools) and time-travel debugging are not confirmed as first-party features. Scores 8: real-time roster + execution timeline + per-agent log export + OpenTelemetry confirmed; no first-party streaming dashboard. Source: factory.ai/enterprise; docs.factory.ai/enterprise; latent.space Factory profile; eval-v2/group-commercial.md §Factory D5.

---

### D9 — Pre-Merge Quality Gates
**Score**: 6
**Evidence**: Factory implements a four-phase loop: Spec → Test → Implement → Verify. The QA Droid executes tests (automated test execution gate). The Review Droid provides independent code review before merge (an architecturally separate agent, not self-review). DroidShield runs static analysis on code before it is committed. These constitute tests + independent code review + a security-adjacent static analysis gate. However, DroidShield is described as real-time scanning during implementation, not as a formal post-implementation security gate, and mandatory coverage thresholds are not documented. Scores 6: automated tests + independent Review Droid review both required; security scanning present but not confirmed as a formal blocking security gate separate from the quality pass. Source: factory.ai/news/missions; factory.ai/news/code-droid-technical-report; eval-v2/group-commercial.md §Factory D6.

---

### D10 — Security Posture
**Score**: 8
**Evidence**: Factory's security stack includes: (a) DroidShield — a real-time static code analysis algorithm that detects security vulnerabilities, bugs, and IP breaches before code is committed (SAST-equivalent); (b) sandboxed execution — each Code Droid runs in a "strictly defined sandboxed environment that isolates its operational scope from main development environments" (cloud VM isolation confirmed); (c) Review Droid as an independent security review gate; (d) enterprise-grade audit trails with all actions traceable and reversible; (e) Factory holds ISO 42001, SOC 2, and ISO 27001 certifications, with regular penetration testing and internal red-teaming documented. The gap for score 10: no formal supply chain controls (SBOM, dependency pinning as a pipeline gate) and no documented prompt injection defense architecture. Scores 8: SAST (DroidShield) + sandboxed execution + formal security certifications (SOC 2, ISO 27001, ISO 42001) confirmed. Source: factory.ai/enterprise; factory.ai/news/code-droid-technical-report; eval-v2/group-commercial.md §Factory D5.

---

### D11 — Independent Validation and Spec Compliance
**Score**: 4
**Evidence**: Factory's Verify phase (the fourth phase of the Spec → Test → Implement → Verify loop) constitutes orchestrator-level validation of worker output against the original spec at each milestone boundary. The QA Droid and Review Droid both read the spec and validate compliance. However, no formal post-merge spec compliance report is documented, no SENTINEL-REPORT.md equivalent is produced, and spec-to-test traceability artifacts are not described. Scores 4: automated spec-compliance check at each verify phase confirmed, but no post-merge compliance pass or formal report. Source: factory.ai/news/missions; eval-v2/group-commercial.md §Factory D6.

---

### D12 — Cross-Run Learning and Memory
**Score**: 6
**Evidence**: Factory maintains two types of persistent cross-run memory: (a) Org and User-level Memory — "every Droid remembers your context across sessions" via captured decisions, docs, and runbooks; users can explicitly save facts ("Remember that our staging environment is at staging.company.com") and Factory persists them; (b) Droid Computers retain installed packages, files, running services, and configuration between sessions. This constitutes structured lesson capture (persisted context notes) that is automatically injected into new run prompts where relevant. However, no entity-level registry (ENTITIES.md equivalent), no incremental ARCHITECTURE.md, and no automated failure pattern extraction into future prompts are documented. Scores 6: structured lesson capture + automatic injection into future runs confirmed; entity memory and architectural knowledge base absent. Source: factory.ai/news/factory-is-ga; docs.factory.ai/cli/features/droid-computers; sidbharath.com "Factory.ai Guide."

---

### Narrative

Factory is the strongest overall performer in this commercial group (total 68), with a notably balanced profile. Its decisive advantages are **state durability** (D6=8), **observability** (D8=8 — the only system with native OpenTelemetry integration and external collector support), and **cross-run memory** (D12=6 — the only system with documented persistent Org/User memory injected into future runs). Security (D10=8) is class-leading among commercial systems that are not GitHub-native. The relative weaknesses are the absence of formal pre-execution contracts (D2=4) and no adversarial decomposition review (D1=4). Factory is the right choice for teams running long-horizon, multi-day autonomous missions that require durable state and enterprise observability; it is less well-suited for teams that prioritize pre-execution coordination guarantees or need explicit interface contracts between parallel workers.

---

## Summary Comparison

| System | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | Total |
|--------|----|----|----|----|----|----|----|----|----|----|-----|-----|-------|
| Devin (Cognition AI) | 2 | 2 | 2 | 8 | 4 | 4 | 4 | 6 | 4 | 6 | 2 | 4 | 48 |
| Cursor agents | 2 | 2 | 2 | 10 | 6 | 4 | 2 | 6 | 4 | 6 | 0 | 2 | 46 |
| Augment Code / Intent | 4 | 4 | 8 | 6 | 4 | 4 | 4 | 4 | 6 | 6 | 4 | 2 | 56 |
| GitHub Copilot Workspace | 4 | 2 | 6 | 8 | 6 | 4 | 2 | 8 | 6 | 10 | 4 | 2 | 62 |
| Factory (Droids) | 4 | 4 | 4 | 6 | 6 | 8 | 6 | 8 | 6 | 8 | 4 | 6 | 70 |

---

## Cross-Group Observations

**Category A (Pre-Execution, D1–D4)**: All five commercial systems score weakly on D1 and D2. No commercial system publishes a formal file ownership matrix, DAG artifact, or frozen interface contract. Commercial systems uniformly treat pre-execution coordination as an LLM-reasoning problem rather than a structural engineering problem. The highest D1 score in this group is 4 (Augment, Copilot, Factory), compared to rigor-first systems elsewhere.

**Category B (Runtime, D5–D8)**: Factory leads on durability (D6=8) and observability (D8=8); Copilot leads on observability (D8=8) via Actions timeline. Cursor and Copilot lead on parallelism setup simplicity. Failure handling (D7) is the weakest dimension across the group — only Factory reaches 6.

**Category C (Post-Execution, D9–D12)**: Security (D10) is where commercial systems invest most visibly — Copilot (10), Factory (8), and Cursor/Augment/Devin (6) all have documented security mechanisms. Independent validation (D11) is weak across the board — the best score is 4 (Augment, Copilot, Factory), with no system producing a formal post-merge compliance report. Cross-run memory (D12) is almost universally neglected; only Factory reaches 6.

---

## Research Notes

**Search date**: 2026-03-31. Evidence gathered from official product pages, changelogs, benchmark repositories, and community review sites.

**Key delta from prior evaluations (12dim vs eval-v2)**:

- **GitHub Copilot D5**: Upgraded from 2 to 6 due to Agent HQ / Mission Control GA (February–March 2026), which adds genuine parallel multi-agent execution. Prior evaluations scored Copilot Workspace as single-agent sequential; this is no longer accurate.
- **GitHub Copilot D8**: Upgraded from 4 to 8. Mission Control provides a real-time unified roster with per-session log streams and the GitHub Actions timeline view.
- **Factory D6**: Upgraded from 4 to 8. Droid Computers (persistent compute environments) and Org/User Memory are now documented features, representing a materially stronger durability story than prior evaluations captured.
- **Factory D12**: Upgraded from implicit 2 to 6. Factory's persistent Org/User Memory with automatic injection into future Droid runs constitutes a structured lesson capture + automatic injection mechanism.
- **Cursor D3**: Held at 2 (not 3 from eval-v2). Cursor 2.4 introduced subagents in March 2026, but no Cursor-specific SWE-bench score has been published. Model-level scores from the underlying LLM are not Cursor's architecture contribution.
- **D11 (new dimension)**: Uniformly weak across the group. The highest score is 4, and Cursor scores 0. Commercial systems do not produce post-merge spec compliance artifacts.
- **D12 (new dimension)**: Only Factory reaches 6. All other commercial systems score 2 or below.
