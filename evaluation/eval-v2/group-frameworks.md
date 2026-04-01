# General-Purpose Multi-Agent Frameworks Scoring Report
**Spectrum**: eval-v2
**Howler**: H2-group-frameworks
**Date**: 2026-03-31
**Rubric version**: evaluation/eval-v2/PLAN.md v2.0
**Prior report**: evaluation/audit-2026/group-frameworks.md

---

## Important Note on Score Portability

**D5 and D6 are entirely new dimensions.** D5 Security replaces D5 Observability; D6 Quality Checks replaces D6 Recovery. Prior D5/D6 scores from the v1 report are NOT carried forward. All D5 and D6 scores below are fresh assessments under the new rubric anchors.

---

## Scoring Table

| System | D1 Cost | D2 Efficiency | D3 Accuracy | D4 Workflow Rigor | D5 Security | D6 Quality Checks | D7 Setup | D8 Scalability | Total |
|--------|---------|---------------|-------------|-------------------|-------------|-------------------|----------|----------------|-------|
| LangGraph | 4 | 3 | 2 | 3 | 1 | 2 | 3 | 3 | 21 |
| CrewAI | 4 | 4 | 2 | 2 | 2 | 2 | 4 | 3 | 23 |
| OpenAI Agents SDK | 4 | 3 | 3 | 2 | 4 | 3 | 5 | 3 | 27 |
| AutoGen / AG2 | 4 | 3 | 2 | 2 | 2 | 2 | 3 | 3 | 21 |
| MetaGPT | 4 | 2 | 2 | 3 | 1 | 2 | 3 | 2 | 19 |

*(MetaGPT included in group for reference; excluded from Top 15 synthesis table, consistent with prior audit.)*

---

## Score Deltas vs. v1 Audit

| System | v1 Total (D1-D8, old dims) | v2 Total | Change | Driver |
|--------|---------------------------|----------|--------|--------|
| LangGraph | 26 | 21 | -5 | D5 Security replaces D5=5 Observability with D5=1 Security (active CVEs); D6 Quality=2 replaces D6 Recovery=3 |
| CrewAI | 24 | 23 | -1 | D5 Security=2 replaces D5 Obs=3; D6 Quality=2 replaces D6 Recovery=2; net roughly flat |
| OpenAI Agents SDK | 25 | 27 | +2 | D3 Accuracy raised to 3 (Codex Security launch; benchmark evidence); D5 Security=4 replaces D5 Obs=4; D6 Quality=3 replaces D6 Recovery=2 |
| AutoGen / AG2 | 22 | 21 | -1 | D5 Security=2 replaces D5 Obs=3; D6 Quality=2 holds; D2 Efficiency=3 unchanged |
| MetaGPT | 20 | 19 | -1 | D5 Security=1 replaces D5 Obs=2; D6 Quality=2 replaces D6 Recovery=2; net flat |

---

## Per-System Evidence Notes

---

### LangGraph

#### D1 Cost — 4 (unchanged)
OSS LangGraph has no platform fee. Model costs only. Representative 3-5 agent run: $0.10-$0.50 at GPT-4o-class rates. LangSmith Developer tier free to 5,000 traces/month; Plus tier $39/seat/month (langchain.com/pricing, March 2026). Score 4: model-only costs for OSS path; LangSmith adds optional overhead. [MEDIUM CONFIDENCE — model costs estimated; LangSmith pricing from margindash.com/langsmith-pricing March 2026]

#### D2 Efficiency — 3 (unchanged)
LangGraph supports parallel node execution via async Python. Every state transition involves checkpoint writes (MemorySaver, SqliteSaver, PostgresSaver), adding orchestration overhead. No published wall-clock benchmarks for a 3-agent parallel coding task. Community reports describe LangGraph as performant for workflows but complex graphs require topology understanding. Score 3 (parallelism with constraints; checkpointing overhead; no independent timing benchmarks). [Evidence: AGENTIC-LANDSCAPE.md §2.1; mager.co deep-dive, March 2026]

#### D3 Accuracy — 2 (unchanged)
LangGraph is an orchestration framework, not a pre-packaged coding agent. No SWE-Bench Verified submission as a system. Accuracy depends entirely on underlying models. Score 2 (no benchmark data; accuracy not attributable to the framework itself). [LOW CONFIDENCE — no public benchmark for LangGraph as a coding system]

#### D4 Workflow Rigor — 3 (unchanged)
LangGraph provides: (a) explicit state schema (TypedDict/Pydantic) as nearest analog to interface contracts; (b) conditional edges and human-in-the-loop pause points; (c) checkpointing enables resume after failure; but lacks: (d) formal failure taxonomy; (e) automated circuit breakers; (f) file ownership contracts. Score 3: role separation via node specialization; retry/resume via checkpoints; no formal taxonomy or file ownership. [Evidence: AGENTIC-LANDSCAPE.md §2.1; LangGraph documentation on state management]

#### D5 Security — 1 [NEW DIMENSION]
**Critical: Three active CVEs disclosed March 2026.**

- **CVE-2026-34070** (CVSS 7.5): Path traversal in LangChain's prompt-loading API (`langchain_core/prompts/loading.py`) — arbitrary file read without validation. Patched in langchain-core 1.2.22+. [thehackernews.com/2026/03/langchain-langgraph-flaws-expose-files]
- **CVE-2025-68664** (CVSS 9.3, critical): Deserialization injection in LangChain's `dumps()`/`dumpd()` functions — enables secret extraction from env vars, class instantiation in trusted namespaces, potential arbitrary code execution via Jinja2 templates. Patched in langchain-core 1.2.5+. [cyata.ai/blog/langgrinch-langchain-core-cve-2025-68664]
- **CVE-2025-67644** (CVSS 7.3): SQL injection in LangGraph SQLite checkpoint implementation via metadata filter keys. Patched in langgraph-checkpoint-sqlite 3.0.1. [resolvedsecurity.com/vulnerability-catalog/CVE-2025-64439]

LangGraph's StateGraph runs user-defined Python code with no sandboxing by default — code executes in-process on the host. No built-in SAST or vulnerability scanning of generated code. No security-specific review step. LangSmith provides observability, not security controls. The March 2026 vulnerability disclosures confirm that LangGraph itself has been an active attack surface.

Score 1: code runs on host without sandboxing, no security review step, no SAST, recent critical CVEs unpatched in default distributions at time of scoring. [Evidence: thehackernews.com/2026/03/langchain-langgraph-flaws-expose-files; cyata.ai LangGrinch post; resolvedsecurity.com CVE-2025-64439; vulert.com/blog/langchain-langgraph-vulnerabilities-expose-files]

#### D6 Quality Checks — 2 [NEW DIMENSION]
LangGraph provides human-in-the-loop interrupt functionality: execution pauses at designated nodes, surfaces state to a UI for human review (approve/reject/modify), and resumes. This is documented for content moderation, code review, and compliance check use cases (mager.co/blog/2026-03-12-langgraph-deep-dive). However: (a) no built-in automated test execution — tests run only if the user configures them; (b) the interrupt/review mechanism is a pause point, not a structured code review gate with pass/fail criteria; (c) no spec compliance verification; (d) no coverage reporting. LangSmith adds evaluation tooling (annotation queues, performance tracking) but this is an external product requiring separate setup and payment.

Score 2: human-in-the-loop pause points exist but constitute a user-configurable mechanism, not a built-in quality gate with pass/fail blocking behavior. No built-in test execution, no coverage enforcement, no spec compliance check. [Evidence: mager.co LangGraph deep-dive March 2026; langchain.com/langsmith/evaluation; promptfoo.dev/docs/guides/evaluate-langgraph]

#### D7 Setup — 3 (unchanged)
`pip install langgraph` is straightforward, but first parallel multi-agent run requires defining a StateGraph with typed state schema, adding nodes and edges, configuring a checkpointer, and optionally setting up LangSmith. GitHub issues document learning curve around state schema design. Score 3 (4-6 steps; tutorial required; half-day to first parallel run). [Evidence: LangGraph quickstart docs; AGENTIC-LANDSCAPE.md §2.1]

#### D8 Scalability — 3 (unchanged)
Sub-graph composition enables hierarchical orchestration. Async execution supports parallel nodes. Prior landscape survey notes scaling via sub-graph composition. No empirical evidence of effective scaling beyond 5-6 parallel agents; single-orchestrator pattern creates potential bottlenecks. Score 3 (3-5 agent sweet spot; no empirical ceiling data). [MEDIUM CONFIDENCE — AGENTIC-LANDSCAPE.md §2.1 and §7]

**Uncertainty flags**: D2 (no timing benchmarks), D3 (framework not a coding agent), D5 (CVEs documented; baseline sandboxing posture from architectural inference), D8 (no empirical scale data)

---

### CrewAI

#### D1 Cost — 4 (unchanged)
Open-source framework; no orchestration surcharge for OSS library. CrewAI Cloud paid tier from $99/month (crewai.com/pricing, March 2026). OSS path: standard model API costs. Representative 5-agent run: $0.075-$0.15 at GPT-4o-class rates. Score 4 (low cost; clearly in $0.10-$0.50/run band). [MEDIUM CONFIDENCE — model costs estimated; cloud tier pricing from crewai.com]

#### D2 Efficiency — 4 (unchanged)
CrewAI documentation confirms simultaneous agent execution for hierarchical and consensual crew processes. Company-reported benchmarks claim 2-3x faster execution than comparable frameworks (AGENTIC-LANDSCAPE.md §2.2, citing CrewAI company data). No independent wall-clock timing for a 3-agent coding task. Score 4 (fast; parallelism evident; reasonable overhead). [MEDIUM CONFIDENCE — company-reported benchmark; no independent timing data]

#### D3 Accuracy — 2 (unchanged)
No published SWE-Bench result for CrewAI as a framework. General-purpose orchestration layer; accuracy depends on underlying models. No community consensus on code quality for CrewAI specifically. Score 2 (no benchmark data). [LOW CONFIDENCE — no public benchmark evidence]

#### D4 Workflow Rigor — 2 (unchanged)
Role separation (agent roles, goals, backstory) and task retry with configurable max_attempts. But: (a) no pre-execution interface contracts or file ownership declarations; (b) failure handling is "retry the task" with no taxonomy; (c) no automated circuit breakers; (d) reviewer agent role exists but is not structurally independent. Score 2 (multiple agents with informal coordination; role designation without structural enforcement). [MEDIUM CONFIDENCE — docs.crewai.com; AGENTIC-LANDSCAPE.md §2.2]

#### D5 Security — 2 [NEW DIMENSION]
**Active CVEs in 2026 (VU#221883):**
- **CVE-2026-2275**: CrewAI CodeInterpreter tool falls back to SandboxPython when Docker is unreachable; SandboxPython fallback enables arbitrary code execution through C function calls. The sandbox is bypassable when Docker is not running. [vistanetinc.com/vu221883-crewai-contains-multiple-vulnerabilities]
- **CVE-2026-2286**: SSRF vulnerability in RAG search tools — URLs provided at runtime not properly validated, enabling content acquisition from internal services and cloud metadata endpoints. [hendryadrian.com/crewai-vulnerabilities-expose-devices-to-hacking]

CrewAI's CodeInterpreter tool uses Docker for sandboxed code execution when Docker is available — this is a genuine sandboxing effort. However, the Docker-optional fallback to SandboxPython degrades the security boundary significantly. Agents are restricted to tools defined for their tasks (task-level tool scoping), which provides some privilege isolation. No built-in SAST of generated code. No security-focused code review step before merge. CrewAI maintainers are working on mitigations (blocking risky modules, fail-closed defaults), but these are not yet shipped as of March 2026.

Score 2: Docker sandboxing exists but is optional and bypassable; no SAST; no security review gate; active CVEs showing SSRF and code execution escape paths. Marginally above score 1 because Docker-when-available represents a genuine sandboxing design. [Evidence: vistanetinc.com/vu221883; hendryadrian.com/crewai-vulnerabilities; procodebase.com/article/security-considerations-in-crewai-applications; swarmsignal.net/ai-agent-security-2026]

#### D6 Quality Checks — 2 [NEW DIMENSION]
CrewAI has a `crewai test` command that executes the crew for a specified number of iterations and reports performance metrics in a score table (docs.crewai.com/en/concepts/testing). The internal test infrastructure uses pytest with VCR for deterministic replay, pytest-split for parallel workers, and network blocking (docs.crewai.com/en/concepts/testing; deepwiki.com/crewAIInc/crewAI/9.1-cli-tools). However: (a) `crewai test` tests crew behavior and agent outputs, not generated code correctness — it is an LLM output evaluator, not a code test runner; (b) no built-in code review step (a "Reviewer" agent is a role designation, not a structured gate); (c) no spec compliance verification; (d) task retry with max_retry_attempts is error recovery, not a quality gate. Score 2: testing infrastructure exists for framework testing and crew evaluation but does not constitute a blocking quality gate on generated code. Tests run only if users configure them for their specific crew. [Evidence: docs.crewai.com/en/concepts/testing; deepwiki.com CrewAI testing infra; AGENTIC-LANDSCAPE.md §2.2]

#### D7 Setup — 4 (unchanged)
`pip install crewai` with one environment variable (LLM API key). No infrastructure dependencies for local OSS use. Quickstart produces a working crew in minutes. Score 4 (2-3 steps; first run within 1 hour). [Evidence: docs.crewai.com quickstart]

#### D8 Scalability — 3 (unchanged)
No documented tested ceiling above 6-8 agents. 450M monthly workflows (company-reported) confirms production scale, but not necessarily large per-run agent counts. Manager LLM for hierarchical crews creates orchestrator bottleneck at higher counts. Sweet spot 3-5 agents per community reports and AGENTIC-LANDSCAPE.md §2.2. Score 3. [MEDIUM CONFIDENCE]

**Uncertainty flags**: D2 (company-only speed data), D3 (no benchmark), D5 (CVE details from VU#221883 advisory; Docker-availability behavior from docs and CVE description)

---

### OpenAI Agents SDK

#### D1 Cost — 4 (unchanged)
Open-source SDK; no platform fee. OpenAI model costs only. At GPT-4o rates, a 3-5 agent handoff chain producing ~15,000 tokens costs $0.075-$0.15. Codex subagent pricing (ChatCompletions API) in the $0.10-$0.50/run range. Score 4. [MEDIUM CONFIDENCE — model cost estimate; Codex pricing from developers.openai.com]

#### D2 Efficiency — 3 (unchanged)
Guardrails run in parallel with agent execution by default (run_in_parallel=True) for minimum latency (openai.github.io/openai-agents-python). Codex subagents enable parallel cloud execution. Primary pattern is sequential handoff chains (Agent A transfers to Agent B). Score 3 (parallel guardrails + Codex subagent parallelism; primary handoff pattern is sequential). [Evidence: openai.github.io/openai-agents-python/handoffs; AGENTIC-LANDSCAPE.md §2.6]

#### D3 Accuracy — 3 (raised from 2)
**New evidence**: OpenAI launched Codex Security in research preview (March 2026) — an AI agent that scanned 1.2 million commits and found 792 critical and 10,561 high-severity vulnerabilities in open-source projects including GnuPG, GnuTLS, PHP, and Chromium (openai.com/index/codex-security-now-in-research-preview; thehackernews.com/2026/03/openai-codex-security-scanned-12). The low false-positive rate (critical issues in <0.1% of scanned commits) represents genuine benchmark-quality evidence of the Codex agent stack's accuracy. GPT-5.3 Codex achieves 77.3% on Terminal-Bench 2.0 (from prior audit). While these are model and agent product benchmarks rather than a direct SDK framework benchmark, they provide stronger evidence of the underlying stack's accuracy capability than the prior "no evidence" assessment. The Agents SDK is the orchestration layer; Codex-powered agents built on it demonstrate state-of-the-art code accuracy.

Score 3 (raised from 2): strong published evidence of the Codex agent stack's accuracy on real coding tasks; the SDK framework itself lacks a dedicated SWE-Bench submission but the evidence base is materially stronger than other frameworks in this group. [MEDIUM CONFIDENCE — benchmark is for Codex agent/model stack, not the SDK in isolation; securityweek.com/openai-rolls-out-codex-security-vulnerability-scanner; thehackernews.com/2026/03/openai-codex-security-scanned-12; csoonline.com/article/4142354]

#### D4 Workflow Rigor — 2 (unchanged)
Guardrails (input/output), handoff structure, and event tracing. But: (a) no pre-execution file ownership contracts; (b) no formal failure taxonomy; (c) guardrail coverage gap — handoff calls bypass tool guardrails (AGENTIC-LANDSCAPE.md §2.6); (d) no circuit breaker. Score 2 (structured handoff + guardrails; lacks contracts, taxonomy, and circuit breakers). [Evidence: openai.github.io/openai-agents-python; AGENTIC-LANDSCAPE.md §2.6]

#### D5 Security — 4 [NEW DIMENSION]
OpenAI Agents SDK + Codex presents the strongest security posture in this group. Evidence per component:

**(a) SAST / vulnerability scanning**: Codex Security (research preview, March 2026) is an AI-powered security agent that identifies vulnerabilities in generated and existing code, producing structured threat models and classified findings (openai.com/index/codex-security-now-in-research-preview). This is a genuine automated vulnerability scanning capability.

**(b) Sandboxed execution**: Codex cloud runs in isolated OpenAI-managed containers — no host file system access, two-phase runtime (setup with network access; agent phase offline by default), secrets scrubbed before agent phase (developers.openai.com/codex/concepts/sandboxing). Codex CLI uses OS-level sandbox mechanisms with no-network and write-permissions-limited-to-workspace defaults. Documented and specific.

**(c) Security-focused review step**: Codex runs `agent approvals & security` mode — humans can require approval before Codex executes commands with potential side effects (developers.openai.com/codex/agent-approvals-security). Built-in approval gates on high-risk actions.

**(d) Prompt injection / privilege escalation protection**: SDK guardrails include jailbreak detection and PII redaction (openai.github.io/openai-agents-python/guardrails). OpenAI's safety-in-agents guide documents prompt injection threat model and mitigations (platform.openai.com/docs/guides/agent-builder-safety). Patched a Codex GitHub token vulnerability (February 2026 — thehackernews.com/2026/03/openai-patches-chatgpt-data).

Score 4 (3 of 4 components fully documented; Codex Security provides SAST in preview but not GA shipping). Full score-5 would require all four in GA production state; the SAST component is research preview. [Evidence: developers.openai.com/codex/concepts/sandboxing; developers.openai.com/codex/agent-approvals-security; openai.com/index/codex-security-now-in-research-preview; openai.github.io/openai-agents-python/guardrails; platform.openai.com/docs/guides/agent-builder-safety]

#### D6 Quality Checks — 3 [NEW DIMENSION]
The OpenAI Agents SDK has emerging quality check infrastructure:

**(a) Test execution**: `codex exec --json` captures JSONL traces with `command_execution` events; build checks can run after skill completion as end-to-end signals (developers.openai.com/blog/eval-skills). Not a blocking test gate by default.

**(b) Guardrails as review step**: Input and output guardrails run in parallel with agent execution and fail fast on violations (openai.github.io/openai-agents-python/guardrails). Tool guardrails run on every custom function-tool invocation. This is a structured, blocking review mechanism — not peer code review, but automated correctness validation.

**(c) Compliance verification**: Guardrails include policy enforcement and content moderation for HIPAA/GDPR compliance contexts; detailed audit logs are exportable (from Guardrails documentation). Enterprise governance scope is documented.

**(d) Coverage reporting**: No built-in coverage measurement for generated code.

Score 3: guardrails provide a blocking automated review step (2 of 4 quality gate components); test execution infrastructure exists but is not a blocking gate; spec compliance is advisory via guardrail configuration rather than structured acceptance-criteria checking. [Evidence: openai.github.io/openai-agents-python/guardrails; developers.openai.com/blog/eval-skills; langfuse.com/guides/cookbook/example_evaluating_openai_agents]

#### D7 Setup — 5 (unchanged)
`pip install openai-agents` (or `openai[agents]`). One environment variable (OPENAI_API_KEY). Tracing, guardrails, and handoffs work immediately. No infrastructure dependencies. Score 5 (near-zero setup; single command; first run within 15 minutes). [Evidence: openai.github.io/openai-agents-python quickstart; AGENTIC-LANDSCAPE.md §2.6]

#### D8 Scalability — 3 (unchanged)
Handoff chains scale linearly. Codex subagents enable genuine parallel cloud execution. No documented ceiling for parallel Codex subagent runs; no published evidence of runs at 8+ agents. Score 3 (Codex subagents add parallel scaling; core handoff pattern is sequential; no empirical multi-agent scale data). [MEDIUM CONFIDENCE — Codex subagent docs from developers.openai.com/codex/subagents]

**Uncertainty flags**: D3 (Codex Security is research preview; benchmark-quality evidence is strong but model-level not framework-level), D5 (Codex Security SAST is research preview not GA; sandboxing and guardrails are GA), D8 (Codex subagent scaling from docs; no empirical data)

---

### AutoGen / AG2

#### D1 Cost — 4 (unchanged)
Open-source; no platform fee. Model costs only. Docker for code execution adds compute overhead but no token cost. Representative 3-5 agent GroupChat run: $0.10-$0.50 at GPT-4o-class rates. AG2 supports Ollama and local models (zero-cost option). Score 4. [MEDIUM CONFIDENCE — model cost estimate; docs.ag2.ai]

#### D2 Efficiency — 3 (unchanged)
AG2 v0.4+ async-first architecture (Microsoft Research blog). GroupChat is turn-based by default — selector picks one agent at a time — limiting real parallelism. MemoryStream pub/sub event bus enables concurrent agent operation. Score 3 (supports parallelism with constraints; GroupChat default is turn-sequential; event-driven architecture enables concurrency but not always used). [MEDIUM CONFIDENCE — architecture supports parallelism; no independent timing benchmarks]

#### D3 Accuracy — 2 (unchanged)
No published SWE-Bench Verified score for AutoGen/AG2. AutoGenBench provides internal tooling but no published leaderboard results. Community reports note strength in code execution patterns (AssistantAgent + UserProxyAgent) but convergence on complex tasks not guaranteed. Score 2 (no public benchmark data; AGENTIC-LANDSCAPE.md §2.3 notes GroupChat conversations can loop unpredictably). [LOW CONFIDENCE]

#### D4 Workflow Rigor — 2 (unchanged)
Multiple agents with role assignment. Captain Agent (AG2, influenced by Magentic-One) maintains a facts-and-progress ledger. But: (a) no pre-execution interface contracts; (b) no formal failure taxonomy; (c) no circuit breakers; (d) no file ownership matrix. Captain retries or re-delegates but failure types are not classified. Score 2 (Captain Agent provides some progress tracking; coordination primarily conversational). [Evidence: AGENTIC-LANDSCAPE.md §2.3; docs.ag2.ai]

#### D5 Security — 2 [NEW DIMENSION]
AG2 provides code execution through Docker containerization when Docker is configured — `DockerCommandLineCodeExecutor` runs code in an isolated container. `LocalCommandLineCodeExecutor` (the default fallback) runs on the host machine with "command sanitization against a list of dangerous commands" but no true sandboxing (docs.ag2.ai/latest/docs/api-reference/autogen/coding/LocalCommandLineCodeExecutor). The YepCode extension (github.com/yepcode/ag2-ext-yepcode) provides serverless sandbox execution as an opt-in third-party integration.

No built-in SAST or vulnerability scanning of generated code. No security-specific review step. A February 2025 security study (CORBA) demonstrated that 79-100% of AutoGen agents could be forced into a completely blocked state within 1.6-1.9 dialogue turns through injected messages — a documented prompt injection/DoS vulnerability class (dev.to/tan_genie_6a51065da7b63b6/ai-agents-run-unsandboxed-code). AutoGen has better baseline security posture than some frameworks (enterprise patterns acknowledged in community) but DockerCommandLineCodeExecutor must be explicitly configured by users; the default local executor is unsandboxed.

Score 2: optional Docker sandboxing available but not default; no SAST; no security review gate; documented prompt injection vulnerability class; host execution is the default path. [Evidence: docs.ag2.ai/latest LocalCommandLineCodeExecutor; github.com/yepcode/ag2-ext-yepcode; dev.to/tan_genie unsandboxed code article; adversa.ai/blog/top-agentic-ai-security-resources-january-2026]

#### D6 Quality Checks — 2 [NEW DIMENSION]
AG2's conversational pattern supports code review via role specialization — one agent can write code, another can review it (IBM/toptenaiagents reports this is a documented strength: "conversational approach natural for code review — one agent writes, another reviews"). However: (a) this is an emergent capability from role assignment, not a structured blocking gate; (b) no built-in test execution framework; (c) no spec compliance verification; (d) no coverage reporting; (e) Captain Agent's progress ledger tracks task completion status, not quality criteria. Research shows adversarial multi-agent architectures (planner + critic) achieved 92.1% success rates on complex tasks — evidence that AG2's critique pattern improves accuracy, but this is user-configured, not built-in. Score 2: code review possible via role assignment but not a built-in blocking gate; no test execution, no coverage, no spec verification. Tests run only if users configure their agents to run them. [Evidence: toptenaiagents.co.uk/blog/langgraph-crewai-autogen-multi-agent-frameworks-uk-2026; ibm.com/think/topics/autogen; gurusup.com/blog/best-multi-agent-frameworks-2026]

#### D7 Setup — 3 (unchanged)
`pip install ag2` (or autogen-agentchat for 0.2 path). Requires API key configuration and framework familiarity for GroupChat or nested chats. Docker for code execution sandbox. Documentation fragmentation from the Microsoft-to-AG2 fork. Score 3 (installation easy; Docker for code execution; documentation friction adds learning curve). [Evidence: AGENTIC-LANDSCAPE.md §2.3; ag2.ai GitHub]

#### D8 Scalability — 3 (unchanged)
Nested chats and distributed agent networks. MemoryStream pub/sub event bus. GroupChat at 6+ agents degrades due to O(n²) conversation overhead. Event-driven async architecture provides better theoretical scalability. Score 3 (architecture supports scaling; GroupChat degrades; sweet spot 3-5 agents). [MEDIUM CONFIDENCE — AGENTIC-LANDSCAPE.md §2.3]

**Uncertainty flags**: D3 (no benchmark), D5 (Docker-as-optional is inference from architecture docs; CORBA study from security search result summary), D6 (quality-via-role-assignment is architectural inference; 92.1% figure from gurusup.com research summary)

---

### MetaGPT

*(Included in group report for reference. Excluded from Top 15 synthesis table, consistent with prior audit and PLAN.md §Scope.)*

#### D1 Cost — 4 (unchanged)
Open-source; no platform fee. Model costs only. Document-heavy pipeline (PM + Architect + Engineer + QA) consumes more tokens per run than minimal agent pairs. Community-estimated 3,000-8,000 tokens per role turn: roughly $0.15-$0.50 at GPT-4o-class rates. Score 4. [MEDIUM CONFIDENCE — token volume estimated from document pipeline description]

#### D2 Efficiency — 2 (unchanged)
MetaGPT 2.0 added pub/sub architecture but core pipeline is waterfall-sequential by design: PM → Architect → Engineer → QA, each blocked on the previous stage's document output. Total wall-clock time significantly exceeds 30 minutes for non-trivial tasks. Score 2 (primarily sequential; parallelism limited to within-role boundaries). [Evidence: AGENTIC-LANDSCAPE.md §2.4; MetaGPT arxiv paper]

#### D3 Accuracy — 2 (unchanged)
No published SWE-Bench Verified score. Prior landscape survey notes "performance on SWE-Bench lags behind newer systems." AgileCoder (2024) explicitly outperforms MetaGPT on HumanEval and MBPP. MetaGPT's AFlow paper accepted oral at ICLR 2025 (top 1.8%) — research quality, but not coding accuracy. Score 2. [Evidence: AGENTIC-LANDSCAPE.md §2.4 and §5.7; AgileCoder paper; MetaGPT ICLR 2025]

#### D4 Workflow Rigor — 3 (unchanged)
Document-as-protocol (PRD, SystemDesign, API spec) is closest to interface contracts in this group. Role separation enforced structurally. Limited failure taxonomy — malformed documents can fail silently. No circuit breaker. No file ownership matrix. Score 3 (structured coordination via document pipeline; no formal failure taxonomy; no file ownership). [Evidence: AGENTIC-LANDSCAPE.md §2.4; MetaGPT paper arxiv.org/html/2308.00352v6]

#### D5 Security — 1 [NEW DIMENSION]
No sandboxed execution environment documented in MetaGPT's architecture. Code generation runs in-process and outputs to a workspace directory; execution of generated code depends entirely on the user's environment. No built-in SAST or vulnerability scanning. No security-specific review step. Community search results explicitly place MetaGPT in the category of frameworks that "rely on your implementation for security boundaries" (arsum.com/blog/posts/ai-agent-frameworks; softmaxdata.com/blog/definitive-guide-to-agentic-frameworks-in-2026). Multiple sources note that MetaGPT-generated code requires "production hardening" and "added testing, observability, and security" before deployment (sider.ai MetaGPT review 2025). No documented threat model. Score 1: no sandboxing, no SAST, no security review step, no documented protection against prompt injection or privilege escalation. [Evidence: arsum.com 10 best AI agent frameworks 2026; sider.ai/blog/ai-tools/metagpt-review-2025; AGENTIC-LANDSCAPE.md §2.4]

#### D6 Quality Checks — 2 [NEW DIMENSION]
MetaGPT's QA Engineer role generates test code as part of the document pipeline. This is a genuine quality artifact — test files are produced alongside implementation files, representing a "review by role" design. However: (a) tests are AI-generated and not automatically executed with pass/fail blocking; (b) no test runner integration — generated tests must be run manually; (c) spec compliance is structural (role output matches expected document format) rather than behavioral; (d) no coverage reporting. The document-as-protocol pattern provides post-hoc traceability but not a blocking quality gate. Score 2: QA role produces test artifacts but they are not automatically executed; no blocking gate; tests run only if the user runs them. [Evidence: MetaGPT paper §3 (role descriptions); AGENTIC-LANDSCAPE.md §2.4; sider.ai MetaGPT review noting "production apps need added testing"]

#### D7 Setup — 3 (unchanged)
`pip install metagpt` followed by API key configuration and project directory setup. SOP configuration has a learning curve. Score 3 (4-6 steps; config file required; first run achievable within a half-day). [Evidence: MetaGPT GitHub README github.com/FoundationAgents/MetaGPT]

#### D8 Scalability — 2 (unchanged)
Architecture designed for a fixed set of software company roles (typically 5-6). Waterfall SOP becomes increasingly rigid as roles multiply. No documented effective parallel execution at 6+ agents. Score 2 (practical ceiling at 3-5 sequential roles). [MEDIUM CONFIDENCE — AGENTIC-LANDSCAPE.md §2.4]

**Uncertainty flags**: D5 (no official sandbox documentation found; inference from community review sources; scored at 1 as conservative with no contrary evidence), D6 (QA-role-generates-tests inference from MetaGPT paper; auto-execution behavior from absence of documentation)

---

## Group Summary Notes

### D5 Security: A Field in Crisis

None of the frameworks in this group receives a score above 4 for security, and three receive scores of 1 or 2. The March 2026 CVE cluster for LangChain/LangGraph (three active CVEs including a CVSS 9.3 critical deserialization injection) is the most significant finding in this re-evaluation. LangGraph's prior score-5 on Observability masked serious underlying security deficiencies that have now been directly exploited.

**Rankings on D5 Security:**
- OpenAI Agents SDK: 4 — sandboxed Codex execution (GA), guardrails, approval gates, Codex Security SAST (preview)
- CrewAI: 2 — optional Docker sandboxing, active CVEs including sandbox escape
- AutoGen / AG2: 2 — optional Docker sandboxing (not default), command sanitization only on local executor
- LangGraph: 1 — host execution, three active CVEs including CVSS 9.3 critical
- MetaGPT: 1 — no documented sandboxing, no security review, no threat model

### D6 Quality Checks: No Framework Has a Full Pipeline

No framework in this group scores above 3 on Quality Checks. The dimension distinguishes between "quality as a role" (an agent designated as a reviewer) and "quality as a gate" (a blocking mechanism that prevents code from advancing on failure). No OSS framework in this group enforces blocking quality gates natively; all are user-configurable. OpenAI Agents SDK scores highest at 3 because guardrails provide a blocking automated review step.

**Rankings on D6 Quality Checks:**
- OpenAI Agents SDK: 3 — blocking guardrails, compliance audit logging, test execution infrastructure
- LangGraph: 2 — human-in-the-loop pause points (configurable, not built-in quality gate)
- CrewAI: 2 — crew evaluation CLI (`crewai test`), task retry; neither constitutes a code quality gate
- AutoGen / AG2: 2 — critique-agent pattern improves accuracy; not a built-in blocking gate
- MetaGPT: 2 — QA Engineer role generates tests; tests not auto-executed

### SWE-Bench Gap (unchanged)
None of the frameworks in this group has a published SWE-Bench Verified score as a framework. All are general-purpose orchestration layers. OpenAI Agents SDK is partially elevated on D3 due to the Codex Security research preview demonstrating real-world vulnerability detection at scale, but this is model-level not framework-level evidence.

### OpenAI Agents SDK Notable Rise
The SDK is the only framework in this group to improve its total score v1→v2 (+2 points), driven primarily by the strong D5 Security posture (Codex sandboxing, Codex Security SAST) and the D6 Quality guardrails step. This reflects genuine capability differentiation that the prior D5 Observability dimension did not capture.

### LangGraph Notable Drop
LangGraph drops from 26 to 21 (-5 points). The prior score-5 on Observability was the highest score in the v1 group report. Under the new Security dimension, LangGraph scores 1 — the lowest in the group — due to three active CVEs, including a critical deserialization injection, and the absence of sandboxing. This is the single largest score change in the group.
