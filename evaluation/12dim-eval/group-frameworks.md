# Group H2 — General-Purpose Frameworks: 12-Dimension Evaluation
**Spectrum**: 12dim-eval
**Howler**: H2
**Date**: 2026-03-31
**Rubric version**: 12dim-v1.0
**Prior reports**: evaluation/audit-2026/group-frameworks.md (8-dim v1), evaluation/eval-v2/group-frameworks.md (8-dim v2)

---

## Scoring Notes

**Score mapping from prior rubrics**: The prior 8-dimension rubrics are NOT directly portable. D1-D4 in this 12-dim rubric cover pre-execution planning (not cost/speed/accuracy/rigor as before). D5-D8 cover runtime coordination. D9-D12 are entirely new post-execution assurance dimensions. All 12 dimensions are scored fresh.

**Impartiality**: Scored from public documentation and specification, not marketing claims. Every score ≥6 is cited. [LOW CONFIDENCE] flagged where evidence is absent or ambiguous. Even scores only (0/2/4/6/8/10).

**Systems**: CrewAI, LangGraph, MetaGPT, AutoGen/AG2, OpenAI Agents SDK, ChatDev

---

## CrewAI

**Category**: General-Purpose Framework
**Public source**: https://docs.crewai.com, https://github.com/crewAIInc/crewAI
**Prior eval scores**: audit-2026: D1=4, D2=4, D3=2, D4=2, D5=3, D6=2, D7=4, D8=3 | eval-v2: D1=4, D2=4, D3=2, D4=2, D5=2, D6=2, D7=4, D8=3

---

### D1 — Task Decomposition Quality
**Score**: 4
**Evidence**: CrewAI supports hierarchical process with a manager LLM that decomposes work and delegates to worker agents, and sequential/parallel process modes with `async_execution=True` on individual tasks. Tasks have defined scope (description, expected_output), and a dependency system via `context` parameter allows explicit task dependency chains. However: no formal file/resource ownership matrix is enforced, no DAG artifact is written and version-controlled, no decomposition hazard scan occurs, and no human review gate of the decomposition is built into the framework before execution begins. The 2026 A2A task execution model adds agent-to-agent dynamic delegation with deterministic ordering. Source: docs.crewai.com/en/learn/sequential-process; github.com/apappascs/crewai-parallel-patterns; latenode.com CrewAI 2025 review.

### D2 — Interface Contract Enforcement
**Score**: 2
**Evidence**: CrewAI provides role separation via agent `role`, `goal`, and `backstory` fields, plus task-level tool scoping (agents restricted to designated tools). These constitute informal conventions enforced by prompt structure, not formal contracts. There is no CONTRACT.md equivalent written before execution, no frozen interface specification that workers may not modify, no factual verification pass confirming referenced files or signatures exist, and no adversarial review of interface agreements. The "Reviewer" agent designation is a role, not a structural gate. Source: docs.crewai.com/en/concepts/agents; AGENTIC-LANDSCAPE.md §2.2.

### D3 — Benchmark Accuracy
**Score**: 0
**Evidence**: No published SWE-Bench Verified score for CrewAI as a framework or system on any public leaderboard (swebench.com, epoch.ai/benchmarks/swe-bench-verified, llm-stats.com/benchmarks/swe-bench-verified, all checked March 2026). CrewAI is a general-purpose orchestration framework whose accuracy depends entirely on underlying models; no system-level coding benchmark has been submitted. The SWE-Bench leaderboard currently tracks 77 evaluated models/systems; CrewAI is absent. Source: swebench.com leaderboard March 2026; llm-stats.com/benchmarks/swe-bench-verified March 2026. [NO EVIDENCE]

### D4 — Setup Complexity
**Score**: 6
**Evidence**: `pip install crewai` with one environment variable (LLM API key) required. CrewAI's quickstart guide produces a functional crew within minutes — the `crewai create crew` CLI scaffolds a project directory with agent/task definitions in a YAML-configured structure. No infrastructure dependencies required for the OSS path. The getting-started guide is concise and the role/task YAML configuration is learnable in under 30 minutes for developers familiar with Python. Docker is optional (only needed for code execution sandbox). Score 6: package install plus minimal config; reasonable learning curve; works out of the box for most use cases. Source: docs.crewai.com quickstart; crewai.com installation docs.

### D5 — Parallelism and Execution Efficiency
**Score**: 4
**Evidence**: CrewAI supports genuine parallel execution via `Process.hierarchical` and `async_execution=True` on tasks, allowing independent tasks to execute concurrently. The 2026 A2A model adds dynamic agent-to-agent task delegation that respects dependency ordering. Company-reported benchmarks claim 2-3x faster execution than comparable frameworks (crewai.com; AGENTIC-LANDSCAPE.md §2.2). However, no independent wall-clock timing benchmarks exist for a 3-agent parallel coding task; no lightweight "reaping" mode with sub-3-minute startup; and no persistent daemon. The hierarchical manager LLM introduces orchestration overhead. Score 4: structured parallelism with dependency-aware scheduling and moderate coordination overhead; does not achieve DAG-dispatch (per-dependency unblocking) or sub-3-minute startup mode. Source: docs.crewai.com/en/learn/sequential-process; latenode.com CrewAI 2025 review; github.com/apappascs/crewai-parallel-patterns. [MEDIUM CONFIDENCE — company-reported benchmark; no independent timing]

### D6 — State Durability and Resumability
**Score**: 2
**Evidence**: CrewAI provides a Memory system backed by SQLite (long-term memory persists cross-session), but task execution state is session-local. If a session dies mid-execution, the task graph must be restarted from the beginning — no checkpoint is written at each task completion that would enable resumption from the last successful step. The `max_retry_attempts` parameter handles transient task failures within a session but does not address session-level crashes. No CHECKPOINT.json equivalent, no per-agent state file, no automated resume protocol. Memory system provides agent knowledge persistence, not execution-state persistence. Source: docs.crewai.com/en/concepts/memory; AGENTIC-LANDSCAPE.md §2.2. [MEDIUM CONFIDENCE — session-persistence behavior from architecture docs]

### D7 — Failure Handling and Recovery
**Score**: 2
**Evidence**: CrewAI provides task-level retry with configurable `max_retry_attempts`, and error output is fed back into the retry context. However, failure types are not classified — all failures are retried with no distinction between transient, logical, structural, or environmental failure classes. There is no circuit breaker that halts retrying after N failures on the same locus, and no escalation to a human for non-transient failures. The "Reviewer" agent can catch output quality issues but is not a failure-handling mechanism in the protocol sense. Score 2: basic retry with no failure taxonomy — this meets "basic retry" but not "classified retry" (D7 anchor score 4 requires at least 2 typed failure paths). Source: docs.crewai.com/en/concepts/tasks; AGENTIC-LANDSCAPE.md §2.2.

### D8 — Observability and Debuggability
**Score**: 4
**Evidence**: CrewAI OSS provides structured logs with per-agent attribution (task output labels, agent name in log lines) and an event emitter for LLM call tracking. Third-party integrations (W&B Weave, Arize Phoenix, Opik) enable external trace aggregation. CrewAI Cloud (paid tier from $99/month) provides a real-time dashboard with per-agent execution tracing. OSS version has no native real-time dashboard and no timeline/replay capability. Score 4: structured per-agent logging with third-party OTEL-compatible integrations available; status inferred from logs but no built-in real-time roster. Cloud tier would score 6 but OSS is scored here. Source: docs.crewai.com changelog; crewai.com/pricing; zenml.io/blog/crewai-pricing.

### D9 — Pre-Merge Quality Gates
**Score**: 2
**Evidence**: CrewAI provides a `crewai test` CLI command that executes the crew for a specified number of iterations and reports performance metrics in a score table. Internally this uses pytest with VCR for deterministic replay (docs.crewai.com/en/concepts/testing; deepwiki.com/crewAIInc/crewAI testing infra). However, this tests crew behavior (LLM output quality), not generated code correctness; it is not a blocking gate on code output. The "Reviewer" agent designation can add a review step via role prompt, but this is a user-configured convention, not a structural blocking gate. No built-in automated test execution, no security review step, no spec compliance check. Score 2: manual/role-based review possible but no automated blocking gate. Source: docs.crewai.com/en/concepts/testing; deepwiki.com CrewAI testing infrastructure.

### D10 — Security Posture
**Score**: 2
**Evidence**: CrewAI's CodeInterpreter tool uses Docker for sandboxed code execution when Docker is available — a genuine sandboxing design. However, four active CVEs were disclosed in 2026 (VU#221883): CVE-2026-2275 (sandbox escape via SandboxPython fallback when Docker is unreachable), CVE-2026-2287 (Docker runtime check bypass enabling RCE), CVE-2026-2285 (arbitrary local file read in JSON loader — no path validation), CVE-2026-2286 (SSRF in RAG search tools — runtime URLs not validated). At the time of scoring (March 2026), no complete patch is available for all disclosed vulnerabilities. No built-in SAST. No formal threat model in public documentation. Score 2: Docker sandboxing exists as design intent but is bypassable; active unpatched CVEs including RCE and SSRF; no SAST; no security review gate. Marginally above 0 because Docker-when-available is a documented sandboxing design rather than no sandboxing attempt. Source: vistanetinc.com/vu221883; securityweek.com/crewai-vulnerabilities-expose-devices-to-hacking; hendryadrian.com/crewai-vulnerabilities; swarmsignal.net/ai-agent-security-2026.

### D11 — Independent Validation and Spec Compliance
**Score**: 0
**Evidence**: CrewAI has no mechanism for independent post-execution validation that a worker's output met spec or contract requirements. Worker self-reports (task completion signals) are accepted without an independent verification pass. There is no orchestrator agent that reads key output files and verifies them against documented postconditions, no SENTINEL-REPORT equivalent, no automated spec compliance check, and no traceability from requirements to test coverage. Source: docs.crewai.com architecture docs; AGENTIC-LANDSCAPE.md §2.2. [NO EVIDENCE of any independent validation mechanism]

### D12 — Cross-Run Learning and Memory
**Score**: 2
**Evidence**: CrewAI's Memory system (long-term SQLite-backed memory) persists agent knowledge across sessions — agents can recall past interactions and learned facts. This constitutes ad-hoc memory: prior run knowledge is available but there is no structured protocol for extracting lessons, no LESSONS.md equivalent written after runs, no entity registry (ENTITIES.md), no ARCHITECTURE.md updated incrementally, and no automatic injection of past-run learnings into new run prompts via pattern matching. The vector database integration announced for Q1 2026 improves recall but does not add a structured lesson extraction protocol. Score 2: cross-session memory exists but is unstructured; no defined protocol for extraction, curation, or injection into future runs. Source: docs.crewai.com/en/concepts/memory; crewai.com Q1 2026 roadmap (latenode.com CrewAI 2025 review).

---

### CrewAI Summary Table

| System | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | Total |
|--------|----|----|----|----|----|----|----|----|----|-----|-----|-----|-------|
| CrewAI | 4  | 2  | 0  | 6  | 4  | 2  | 2  | 4  | 2  | 2   | 0   | 2   | 30    |

### CrewAI Narrative
CrewAI's strongest dimension is setup friction (D4=6): `pip install crewai` with one env var and a YAML-based scaffold produces a working crew rapidly, making it the most accessible entry point in this group. Its parallelism support (D5=4) is genuine — the async_execution model and hierarchical process allow concurrent agent operation — and its logging (D8=4) is adequate for development. The framework's weaknesses are structural: it has no interface contracts (D2=2), no failure taxonomy beyond retry (D7=2), no state durability across session crashes (D6=2), no quality gates (D9=2), and no independent validation (D11=0). The four unpatched CVEs in 2026 including an RCE sandbox escape (D10=2) represent a serious production risk. CrewAI is best suited for rapid prototyping of orchestrated agent workflows where security and rigor are not primary concerns; it is not production-ready for high-stakes automated coding pipelines without significant additional hardening.

---

## LangGraph

**Category**: General-Purpose Framework
**Public source**: https://langchain.com/langgraph, https://github.com/langchain-ai/langgraph, https://docs.langchain.com/oss/python/langgraph
**Prior eval scores**: audit-2026: D1=4, D2=3, D3=2, D4=3, D5=5, D6=3, D7=3, D8=3 | eval-v2: D1=4, D2=3, D3=2, D4=3, D5=1, D6=2, D7=3, D8=3

---

### D1 — Task Decomposition Quality
**Score**: 4
**Evidence**: LangGraph's StateGraph model provides explicit node definitions with typed state schemas (TypedDict/Pydantic), conditional edges for dependency-aware routing, and parallel fan-out execution (dispatching to multiple nodes simultaneously when dependencies are satisfied). The framework supports sub-graph composition for hierarchical multi-agent architectures. However: no formal file/resource ownership matrix, no decomposition artifact written before execution (the graph is defined in code, not as a planning document reviewed by a human), no pre-decomposition hazard scan (integration bottlenecks, serial risks, effort estimation), and no per-worker preconditions/postconditions specified. The graph topology IS the decomposition, but it is code — not a versioned planning artifact reviewed before worker execution begins. Score 4: structured decomposition with dependency ordering and scope via node definitions; ownership implied but not formally enforced. Source: docs.langchain.com/oss/python/langgraph/persistence; langchain.com/langgraph; mager.co/blog/2026-03-12-langgraph-deep-dive.

### D2 — Interface Contract Enforcement
**Score**: 4
**Evidence**: LangGraph's typed state schema (TypedDict or Pydantic) provides a shared interface definition that all nodes read from and write to — the nearest analog to a contract in this group. State updates flow through defined reducers, preventing arbitrary overwrites. In LangGraph 2.0, guardrail nodes provide declarative content filtering and validation at step boundaries (dev.to LangGraph 2026 definitive guide). However: the state schema is code, not a frozen pre-execution artifact; there is no CONTRACT.md that is frozen before workers start; violations do not require formal escalation; and no adversarial review of the contract occurs. Score 4: shared type definitions via state schema with enforced update patterns; workers expected to follow it, compliance partially enforced by the type system but not verified for correctness against a codebase. Source: sparkco.ai LangGraph state management 2025; langchain.com/langgraph; dev.to LangGraph 2.0 definitive guide.

### D3 — Benchmark Accuracy
**Score**: 0
**Evidence**: No published SWE-Bench Verified score for LangGraph as a system on any public leaderboard (swebench.com, epoch.ai, llm-stats.com — all checked March 2026). LangGraph is a general-purpose orchestration framework; accuracy depends entirely on the underlying models and user-defined agent logic. The February 2026 SWE-Bench leaderboard update (simonwillison.net/2026/Feb/19/swe-bench) documents top model performance but does not include LangGraph as a framework entry. Source: swebench.com; simonwillison.net/2026/Feb/19/swe-bench. [NO EVIDENCE]

### D4 — Setup Complexity
**Score**: 4
**Evidence**: `pip install langgraph` is a single command but a productive first parallel multi-agent run requires non-trivial setup: defining a StateGraph with typed state schema, adding nodes and edges, configuring a checkpointer (MemorySaver is local; SqliteSaver requires SQLite; PostgresSaver requires a running Postgres instance), and optionally configuring LangSmith. GitHub issues document learning curve around state schema design. The LangGraph 2.0 guide (dev.to 2026 edition) acknowledges that "understanding graph topology" is a prerequisite. LangGraph Cloud adds further configuration. Score 4: standard package install; requires reading documentation to configure; non-trivial learning curve for the state schema and checkpointer setup. Source: docs.langchain.com langgraph quickstart; dev.to LangGraph 2.0 definitive guide 2026; AGENTIC-LANDSCAPE.md §2.1.

### D5 — Parallelism and Execution Efficiency
**Score**: 4
**Evidence**: LangGraph supports fan-out parallel execution — multiple nodes execute simultaneously when their graph edges allow it. The checkpoint system writes state at every super-step boundary (a tick where all scheduled nodes in that step execute in parallel), enabling concurrent execution within steps (docs.langchain.com/oss/python/langgraph/persistence). Sub-graph composition enables hierarchical parallel orchestration. LangGraph Cloud adds optimized dispatch with retry policies and monitoring. However: every state transition involves checkpoint writes (MemorySaver, SqliteSaver, PostgresSaver), which adds per-step overhead compared to in-memory-only frameworks; no lightweight "reaping" mode for small runs; and no persistent daemon (each invocation starts fresh). Score 4: structured parallelism with dependency-aware scheduling; moderate checkpointing overhead; does not achieve continuous parallel execution or sub-3-minute startup on first run. Source: docs.langchain.com/oss/python/langgraph/persistence; markaicode.com/langgraph-production-agent; use-apify.com/blog/langgraph-agents-production.

### D6 — State Durability and Resumability
**Score**: 6
**Evidence**: LangGraph's checkpointing system is a first-class architecture feature: state is written to a configured backend (MemorySaver, SqliteSaver, PostgresSaver) after every super-step, creating a snapshot at each execution boundary. Workflows can resume seamlessly after crashes, restarts, or disconnections by loading the last checkpoint from the store and continuing from the last committed super-step (use-apify.com/blog/langgraph-agents-production; markaicode.com/langgraph-production-agent). A defined resume protocol exists (graph.invoke with a thread ID retrieves the last checkpoint for that thread). Nodes can read their own prior state on restart. Score 6: automatic checkpoint-based persistence at phase/step transitions; defined resume protocol; workers skip completed steps. Does not score 8 because per-worker continuous state files (equivalent to HOOK.md) are not maintained — the checkpoint granularity is per super-step, not per sub-agent turn within a step. Source: medium.com/@vinodkrane langgraph checkpoints; markaicode.com/langgraph-production-agent; use-apify.com langgraph agents production.

### D7 — Failure Handling and Recovery
**Score**: 4
**Evidence**: LangGraph provides retry policies (configurable retry on node failure) and human-in-the-loop pause points that allow an operator to approve, reject, or modify state before execution continues (mager.co/blog/2026-03-12-langgraph-deep-dive). LangGraph Cloud adds more advanced retry policies and monitoring. However, failure types are classified into at most two categories (retriable vs. interrupt-requiring) — there is no 3+ type taxonomy (transient/logical/structural/environmental/conflict), no formal circuit breaker after N repeated failures on the same locus, and no dedicated diagnosis agent that performs root-cause analysis before recovery. Score 4: two failure handling paths (auto-retry and human interrupt); checkpoint enables resume from last state; no formal taxonomy beyond retriable/requires-interrupt. Source: mager.co LangGraph deep-dive March 2026; docs.langchain.com persistence; langchain.com langgraph.

### D8 — Observability and Debuggability
**Score**: 8
**Evidence**: LangGraph with LangSmith (Developer tier free up to 5,000 traces/month) provides: (a) structured per-node logs with trace IDs — every LLM call, tool use, and state transition is captured; (b) real-time dashboard in the LangSmith UI showing active graph execution state; (c) time-travel debugging — step backwards through any execution and replay with different inputs; (d) per-agent cost breakdown via token usage attribution per node. LangSmith tracing activates with a single environment variable (`LANGSMITH_API_KEY`). LangGraph 2.0's guardrail nodes produce observable output at each step. Score 8: real-time roster plus timeline with time-travel replay and per-agent cost breakdown — this matches the D8 score-8 anchor. Does not score 10 (no streaming dashboard or OpenTelemetry native export from LangGraph itself, though OTEL-compatible backends are usable). Source: langchain.com/langsmith/observability; analyticsvidhya.com LangGraph+LangSmith guide; mager.co LangGraph deep-dive.

### D9 — Pre-Merge Quality Gates
**Score**: 2
**Evidence**: LangGraph provides human-in-the-loop interrupt nodes where execution pauses for human review (approve/reject/modify) before continuing. LangGraph 2.0 adds guardrail nodes (declarative content filtering, rate limiting, audit logging as configuration) that validate outputs at each step (dev.to LangGraph 2026 guide). LangSmith adds evaluation tooling (annotation queues) as a separate product. However: there is no built-in automated test execution with pass/fail blocking; guardrail nodes catch content policy violations, not functional correctness of generated code; and there is no structured security review step built into the framework. The interrupt mechanism is a user-configurable pause point, not a mandatory blocking quality gate with pass/fail criteria on code output. Score 2: human-in-the-loop pause points and guardrail nodes exist but neither constitutes a built-in multi-gate quality pipeline for code output. Source: mager.co LangGraph deep-dive March 2026; dev.to LangGraph 2.0 definitive guide; langchain.com/langsmith/evaluation.

### D10 — Security Posture
**Score**: 2
**Evidence**: Three active CVEs disclosed March 2026: CVE-2026-34070 (CVSS 7.5, path traversal in langchain_core prompt-loading API — arbitrary file read); CVE-2025-68664 (CVSS 9.3 CRITICAL, deserialization injection in langchain_core dumps()/dumpd() enabling secret extraction, class instantiation, and potential arbitrary code execution via Jinja2); CVE-2025-67644 (CVSS 7.3, SQL injection in LangGraph SQLite checkpoint via metadata filter keys). Patches exist in langchain-core 1.2.22+ and langgraph-checkpoint-sqlite 3.0.1, but default installations may not be on patched versions. LangGraph itself runs user-defined Python code in-process on the host with no sandboxing by default. No built-in SAST. No security-specific review step. Score 2: code runs unsandboxed on host; three active CVEs including a CVSS 9.3 critical; no SAST; no security review gate. Scores 2 rather than 0 because guardrail nodes provide some input/output validation and LangSmith audit logging exists. Source: thehackernews.com/2026/03/langchain-langgraph-flaws-expose-files; cyata.ai/blog/langgrinch-langchain-core-cve-2025-68664; resolvedsecurity.com/vulnerability-catalog/CVE-2025-64439.

### D11 — Independent Validation and Spec Compliance
**Score**: 0
**Evidence**: LangGraph has no mechanism for independent post-execution validation that node outputs met the intended specification or contract requirements. Worker/node self-reports (successful state transitions) are accepted. There is no orchestrator-level agent that reads key output files and verifies them against postconditions, no SENTINEL-REPORT equivalent, no traceability from spec requirements to test coverage. LangSmith provides evaluation tooling for LLM output quality, but this is a separate product and does not constitute post-merge spec compliance verification for code. Source: docs.langchain.com langgraph documentation; langchain.com/langsmith. [NO EVIDENCE of independent validation mechanism in the core framework]

### D12 — Cross-Run Learning and Memory
**Score**: 2
**Evidence**: LangGraph's persistence layer (MemorySaver, SqliteSaver, PostgresSaver) stores execution state per thread but not cross-run learnings. LangGraph's Memory Store (available in LangGraph 0.2+) enables agents to persist and retrieve custom memories across threads and sessions — agents can store facts learned in one run and retrieve them in future runs. However, this is ad-hoc memory (agents write what they choose to remember), not a structured lesson extraction protocol. There is no LESSONS.md equivalent, no entity registry, no incremental ARCHITECTURE.md, and no automatic injection of past-run failure patterns into future runs. Score 2: cross-session memory store exists but is unstructured; no defined extraction or injection protocol. Source: docs.langchain.com/oss/python/langgraph/persistence; medium.com/@vinodkrane langgraph checkpoints.

---

### LangGraph Summary Table

| System    | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | Total |
|-----------|----|----|----|----|----|----|----|----|----|-----|-----|-----|-------|
| LangGraph | 4  | 4  | 0  | 4  | 4  | 6  | 4  | 8  | 2  | 2   | 0   | 2   | 40    |

### LangGraph Narrative
LangGraph's defining strength is observability (D8=8): with LangSmith, it provides the only time-travel debugging and real-time execution dashboard in this group, making it uniquely debuggable in production. Its state durability (D6=6) is the second standout — per-super-step checkpointing with a defined resume protocol is among the best built-in persistence in this group. The framework's structured typed state schema (D2=4) and graph-topology decomposition (D1=4, D5=4) represent a more rigorous coordination model than most peers. However, LangGraph's post-execution assurance (D9-D12) is nearly absent: no quality gates, no independent validation, and no structured learning. Security (D10=2) is a serious liability in 2026 given three active CVEs including a CVSS 9.3 critical deserialization attack. LangGraph is the strongest choice for production observability and crash-resilient stateful workflows; it is a poor choice for high-security environments or for teams needing automated quality assurance on generated code.

---

## MetaGPT

**Category**: General-Purpose Framework
**Public source**: https://github.com/FoundationAgents/MetaGPT, https://arxiv.org/abs/2308.00352
**Prior eval scores**: audit-2026: D1=4, D2=2, D3=2, D4=3, D5=2, D6=2, D7=3, D8=2 | eval-v2: D1=4, D2=2, D3=2, D4=3, D5=1, D6=2, D7=3, D8=2

---

### D1 — Task Decomposition Quality
**Score**: 4
**Evidence**: MetaGPT's document-as-protocol approach provides structured task decomposition: roles produce sequenced artifacts (PRD → SystemDesign → APISpec → code → tests) where each document functions as a scope statement for the next role. Role separation is enforced structurally — a PM cannot act as an Engineer. The AFlow extension (ICLR 2025 Oral, top 1.8%) automates agentic workflow generation via Monte Carlo tree search, optimizing decomposition across six QA/Code/Math datasets. However: MetaGPT's core pipeline is waterfall-sequential, not DAG-parallel; the "ownership matrix" is implicitly the role-to-document mapping rather than a formal file ownership declaration; there is no human review gate of the decomposition before execution begins; and no per-worker preconditions/postconditions/invariants. Score 4: structured decomposition with defined scope per role and implicit dependency ordering; ownership implied by role but not formally enforced. Source: MetaGPT paper arxiv.org/abs/2308.00352; github.com/FoundationAgents/AFlow; einnews.com AFlow open-source announcement.

### D2 — Interface Contract Enforcement
**Score**: 4
**Evidence**: MetaGPT's "document-as-protocol" is a genuine interface contract mechanism: the PRD, SystemDesign, and APISpec documents are structured outputs that downstream roles treat as authoritative specifications. The APISpec document, in particular, functions as a shared interface definition — Architects produce it; Engineers consume it. Documents are written to disk and serve as frozen-at-production artifacts that downstream roles cannot overwrite. However: documents are LLM-generated artifacts, not formally verified against an existing codebase; no adversarial review of the contract documents; no AMENDMENT.md protocol if the contract proves wrong mid-execution; and malformed document failures can propagate silently. Score 4: shared type/interface definitions via structured documents; downstream roles expected to follow them; compliance not formally verified. Source: MetaGPT paper §3; arxiv.org/html/2308.00352v6; AGENTIC-LANDSCAPE.md §2.4.

### D3 — Benchmark Accuracy
**Score**: 0
**Evidence**: No published SWE-Bench Verified score for MetaGPT on any public leaderboard (swebench.com, epoch.ai, llm-stats.com — checked March 2026). The AFlow paper reports average performance of 80.3% across six QA/Code/Math datasets, but this is AFlow's automated workflow optimization metric across diverse task types, not SWE-Bench Verified specifically. AgileCoder (2024 research paper) explicitly outperforms MetaGPT on HumanEval and MBPP. The SWE-Bench February 2026 leaderboard update (simonwillison.net/2026/Feb/19/swe-bench) does not include MetaGPT. Source: swebench.com leaderboard; simonwillison.net/2026/Feb/19/swe-bench; github.com/FoundationAgents/AFlow README. [NO EVIDENCE for SWE-Bench specifically]

### D4 — Setup Complexity
**Score**: 4
**Evidence**: `pip install metagpt` followed by API key configuration and a config file specifying role definitions and workspace paths. MetaGPT's quickstart exists but the SOP YAML configuration has a learning curve — understanding the role pipeline and how to customize it requires reading the paper and documentation. Score 4: standard package install; requires reading documentation to configure; the SOP configuration adds non-trivial learning curve beyond simple API key setup. Source: github.com/FoundationAgents/MetaGPT README; AGENTIC-LANDSCAPE.md §2.4.

### D5 — Parallelism and Execution Efficiency
**Score**: 2
**Evidence**: MetaGPT's core architecture is waterfall-sequential: PM → Architect → Engineer → QA, each blocked on the prior stage's document output. MetaGPT 2.0 added a pub/sub architecture enabling within-role parallelism (multiple Engineer agents can work simultaneously), but the inter-role pipeline remains sequential by design — the Architect cannot begin until the PM's PRD is complete. For non-trivial tasks, total wall-clock time significantly exceeds 30 minutes. AFlow provides workflow optimization but does not add genuine parallel multi-role execution. Score 2: primarily sequential execution; parallelism limited to within-role boundaries; high coordination overhead relative to parallel throughput. Source: AGENTIC-LANDSCAPE.md §2.4; MetaGPT paper arxiv.org/html/2307.07924v5; github.com/FoundationAgents/MetaGPT.

### D6 — State Durability and Resumability
**Score**: 2
**Evidence**: MetaGPT persists documents to disk as execution progresses — if interrupted, subsequent roles can re-read existing document artifacts and attempt to continue. This is partial persistence via document state, not formal checkpointing with a defined resume protocol. There is no CHECKPOINT.json equivalent, no per-role state file updated continuously, no automated resume detection, and no skip-completed-work mechanism. If the Engineer role crashes mid-file-generation, the run must be restarted from the last complete document. Score 2: partial persistence via on-disk documents; manual resume possible but no automation and no per-worker granularity. Source: AGENTIC-LANDSCAPE.md §2.4; MetaGPT GitHub documentation.

### D7 — Failure Handling and Recovery
**Score**: 2
**Evidence**: MetaGPT's primary failure handling is "retry with human review" — if a role produces a malformed document, the user must intervene. Malformed document failures can fail silently (the role outputs something formally valid but semantically incorrect) and propagate to downstream roles. There is no failure taxonomy, no circuit breaker, no automatic retry with classified failure types, and no dedicated recovery agent. Score 2: basic retry via human intervention; no failure classification. Source: AGENTIC-LANDSCAPE.md §2.4 "error recovery is primarily via retry + human review."

### D8 — Observability and Debuggability
**Score**: 4
**Evidence**: MetaGPT produces structured documents (PRD.md, SystemDesign.md, APISpec.md, code files, test files) in a workspace directory as execution progresses — role attribution is clear from file naming conventions and conversation logs. Log files are written to the workspace directory. However: there is no real-time dashboard showing which role is currently active, no trace IDs per agent turn, no timeline view, no per-agent cost breakdown, and no replay capability. Post-hoc debugging is possible by inspecting the document artifacts and conversation log. Score 4: structured per-role logging via document artifacts; status inferred from which files exist; no real-time roster, no timeline, no replay. Source: MetaGPT GitHub documentation; AGENTIC-LANDSCAPE.md §2.4; sider.ai MetaGPT review 2025.

### D9 — Pre-Merge Quality Gates
**Score**: 2
**Evidence**: MetaGPT's QA Engineer role generates test code as part of the document pipeline — test files are produced alongside implementation files as a structured quality artifact. This is a genuine design for quality assurance. However: generated tests are not automatically executed with pass/fail blocking; there is no test runner integration — tests must be run manually; spec compliance is structural (role output format) not behavioral; and no security review step. Score 2: QA role produces test artifacts (genuine quality design), but tests are not automatically run as a blocking gate. Source: MetaGPT paper §3 role descriptions; AGENTIC-LANDSCAPE.md §2.4; sider.ai MetaGPT review noting "production apps need added testing."

### D10 — Security Posture
**Score**: 0
**Evidence**: No sandboxed execution environment is documented in MetaGPT's architecture. Code generation runs in-process on the host machine; generated code is output to a workspace directory; execution of generated code depends entirely on the user's own environment. No built-in SAST or vulnerability scanning. No security-specific review step. No documented threat model. Community review sources explicitly place MetaGPT in the category of frameworks requiring users to add their own security boundaries (arsum.com 10 best AI agent frameworks 2026; sider.ai MetaGPT review). Score 0: no security features documented. [NO EVIDENCE of any security mechanism] Source: arsum.com/blog/posts/ai-agent-frameworks; sider.ai/blog/ai-tools/metagpt-review-2025; AGENTIC-LANDSCAPE.md §2.4.

### D11 — Independent Validation and Spec Compliance
**Score**: 2
**Evidence**: MetaGPT's document-as-protocol structure enables a rudimentary form of independent validation: a downstream role (QA Engineer) reviews the Engineer's output against the APISpec document, constituting human spot-check by design. The QA role generates tests intended to validate the implementation against the specification. This is closer to a human spot-check (D11 anchor score 2) than an automated contract test execution (score 4), because the QA output is a role turn — not a mechanically-enforced automated validation pass — and the generated tests are not run automatically. Score 2: QA role provides informal spec-checking by design; not automated or mechanically enforced. Source: MetaGPT paper §3 QA Engineer role description; arxiv.org/html/2308.00352v6.

### D12 — Cross-Run Learning and Memory
**Score**: 4
**Evidence**: MetaGPT's "Experiential Co-Learning" feature (documented in the 2.0 architecture) captures lessons from prior runs through a shared experience pool — agents can reference past task solutions when tackling similar problems. The workspace directory retains prior run documents. This constitutes structured lesson capture: prior run artifacts are available and the co-learning mechanism provides a defined extraction protocol. However, it is not automatic injection into new run prompts via task-type matching, there is no entity registry (ENTITIES.md equivalent), and there is no incremental ARCHITECTURE.md preserved across runs. Score 4: structured lesson capture via Experiential Co-Learning with an explicit mechanism; available for future runs but not automatically injected. Source: ChatDev/MetaGPT co-evolution papers; yuv.ai/blog/chatdev (co-learning description); AGENTIC-LANDSCAPE.md §2.4. [MEDIUM CONFIDENCE — co-learning mechanism from secondary sources; official MetaGPT 2.0 docs not fully verified]

---

### MetaGPT Summary Table

| System  | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | Total |
|---------|----|----|----|----|----|----|----|----|----|-----|-----|-----|-------|
| MetaGPT | 4  | 4  | 0  | 4  | 2  | 2  | 2  | 4  | 2  | 0   | 2   | 4   | 30    |

### MetaGPT Narrative
MetaGPT's distinctive value is its document-as-protocol coordination model (D1=4, D2=4): structured PRD/SystemDesign/APISpec artifacts function as interface contracts that discipline the sequential pipeline, making it one of the most rigorous coordination models in this group despite its waterfall nature. The Experiential Co-Learning mechanism (D12=4) is the only structured cross-run learning system in this group, a genuine differentiator. MetaGPT's primary liabilities are its sequential-only architecture (D5=2, constraining parallel throughput), complete absence of security features (D10=0 — no sandboxing, no threat model), and lack of any automated quality gates (D9=2 — QA role generates tests but doesn't run them). MetaGPT is best suited for research and structured software design tasks where the document-pipeline discipline is valued over execution speed; it requires substantial production hardening (security sandboxing, test automation, observability) before deployment in automated CI pipelines.

---

## AutoGen / AG2

**Category**: General-Purpose Framework
**Public source**: https://ag2.ai, https://docs.ag2.ai, https://github.com/ag2ai/ag2
**Prior eval scores**: audit-2026: D1=4, D2=3, D3=2, D4=2, D5=3, D6=2, D7=3, D8=3 | eval-v2: D1=4, D2=3, D3=2, D4=2, D5=2, D6=2, D7=3, D8=3

---

### D1 — Task Decomposition Quality
**Score**: 4
**Evidence**: AG2's Captain Agent (influenced by Magentic-One) maintains a facts-and-progress ledger and decomposes tasks by delegating sub-tasks to specialist agents. Nested chats enable hierarchical decomposition — a top-level GroupChat orchestrates sub-conversations. The AG2 v0.4+ async-first event-driven architecture enables concurrent agent execution. However: there is no formal ownership matrix, no decomposition artifact reviewed by a human before execution, no DAG written as a pre-execution planning document, no hazard scan, and no per-worker preconditions/postconditions. The Captain's ledger is a runtime artifact, not a pre-execution planning document. Score 4: structured decomposition via Captain Agent delegation with dependency awareness; ownership implied but not formally enforced before execution. Source: docs.ag2.ai; AGENTIC-LANDSCAPE.md §2.3; softmaxdata.com definitive guide to agentic frameworks 2026.

### D2 — Interface Contract Enforcement
**Score**: 2
**Evidence**: AG2 provides role assignment (each agent has a system message defining its function) and task-level tool scoping (agents restricted to designated tools). GroupChat's selector mechanism enforces turn-taking but does not enforce interface contracts between agents. There is no shared types file, no CONTRACT.md equivalent, no frozen pre-execution interface specification, and no adversarial review. Captain Agent tracks facts and progress in a ledger, but this is a runtime state tracker, not a pre-execution interface contract. Score 2: informal conventions via role prompts and tool scoping; no formal contract mechanism. Source: docs.ag2.ai; AGENTIC-LANDSCAPE.md §2.3.

### D3 — Benchmark Accuracy
**Score**: 0
**Evidence**: No published SWE-Bench Verified score for AutoGen/AG2 as a framework or system on any public leaderboard (swebench.com, epoch.ai — checked March 2026). AutoGenBench provides internal benchmarking tooling but no leaderboard results are published. Community reports note strength in code execution patterns but convergence on complex tasks is not guaranteed; AGENTIC-LANDSCAPE.md §2.3 notes "GroupChat conversations can loop unpredictably." Source: swebench.com; docs.ag2.ai. [NO EVIDENCE]

### D4 — Setup Complexity
**Score**: 4
**Evidence**: `pip install ag2` (or `autogen-agentchat` for the 0.2 path) is straightforward. However, a productive first GroupChat or nested-chat coding run requires configuring agent system messages, tool definitions, and Docker for safe code execution. The Microsoft-to-AG2 fork created documentation fragmentation — some docs reference the 0.2 API while others document 0.4+ (AGENTIC-LANDSCAPE.md §2.3; medium.com/@ashu_don autogen versions guide). AutoGen Studio provides a low-code GUI interface that reduces configuration friction for prototyping. Score 4: standard package install; Docker required for code execution sandbox; documentation fragmentation adds learning curve friction. Source: docs.ag2.ai; AGENTIC-LANDSCAPE.md §2.3; autogen versions Medium article.

### D5 — Parallelism and Execution Efficiency
**Score**: 4
**Evidence**: AG2 v0.4+ was rearchitected with an async-first, event-driven core using a MemoryStream pub/sub event bus that "enables real-time streaming and makes agents safely reusable across concurrent users" (docs.ag2.ai 2026). Nested chats and distributed agent networks support hierarchical parallel orchestration. GroupChat default is turn-sequential (the selector picks one agent per turn), but the event-driven architecture enables true concurrency for agents built on the async API. AutoGen Studio (2026) adds real-time agent updates and mid-execution control. Score 4: async-first architecture with genuine concurrency support; GroupChat default is turn-sequential (limiting throughput in the most common pattern); no lightweight startup mode; no persistent daemon. Source: docs.ag2.ai; AGENTIC-LANDSCAPE.md §2.3; spaceo.ai agentic AI frameworks 2026.

### D6 — State Durability and Resumability
**Score**: 2
**Evidence**: AG2 v0.4+ persists state to files/databases (Microsoft Research AutoGen v0.4 blog). Conversation history is persisted in-memory by default; configurable backends can write to disk. Recovery requires manual intervention — there is no automated resume protocol, no per-worker state file maintained continuously, and no checkpoint-per-step mechanism equivalent to LangGraph. The Captain Agent's progress ledger exists in memory and is lost on session death. Score 2: partial state persistence possible with custom configuration; no automated resume protocol; session death requires partial or full restart. Source: docs.ag2.ai; AGENTIC-LANDSCAPE.md §2.3 "conversation history in-memory by default"; towardsai.net AutoGen AG2 complete guide.

### D7 — Failure Handling and Recovery
**Score**: 4
**Evidence**: AG2's Captain Agent maintains a progress ledger and re-delegates on failure — this constitutes a basic "classified" retry where the Captain can distinguish task-not-done from task-attempted-wrong and re-assign. The framework supports configurable retry counts on tool calls. AutoGen Studio (2026) adds mid-execution control — "pause conversations, redirect agent actions, adjust team composition" (docs.ag2.ai/docs/autogen-studio/usage), which constitutes manual interrupt-based recovery. A February 2025 security study (CORBA) demonstrated that injected messages could force agents into a blocked state — a known class of failure not yet handled by the framework's recovery protocol. Score 4: two recovery paths (auto-retry via Captain re-delegation and manual interrupt via AutoGen Studio); no formal 3+ type taxonomy; no circuit breaker after N failures on same locus. Source: docs.ag2.ai/docs/autogen-studio/usage; spaceo.ai agentic frameworks enterprise guide 2026; AGENTIC-LANDSCAPE.md §2.3.

### D8 — Observability and Debuggability
**Score**: 6
**Evidence**: AG2 provides OpenTelemetry tracing (Jaeger, Honeycomb, OTEL-compatible backends) and AgentOps integration for real-time agent monitoring and compliance (docs.ag2.ai observability; AGENTIC-LANDSCAPE.md §2.3). AutoGen Studio (2026) adds a real-time visual interface: "real-time agent updates, mid-execution control (pause conversations, redirect agent actions, adjust team composition), interactive feedback through the UI, and message flow visualization" (docs.ag2.ai/docs/autogen-studio/usage). This constitutes a real-time status roster with agent-level attribution. No native time-travel debugging or per-agent cost breakdown built into the framework itself. Score 6: real-time status roster via AutoGen Studio + OTEL trace export; per-agent log attribution; no time-travel replay or cost breakdown natively. Source: docs.ag2.ai/latest/docs/blog/category/observability; docs.ag2.ai/docs/autogen-studio/usage; spaceo.ai agentic frameworks 2026.

### D9 — Pre-Merge Quality Gates
**Score**: 2
**Evidence**: AG2's conversational pattern supports code review via role specialization — one agent writes code, another reviews it. Research shows adversarial multi-agent architectures (planner + critic) achieve improved accuracy (gurusup.com 2026 multi-agent frameworks). However: code review via role assignment is an emergent capability, not a built-in blocking gate; no built-in test execution framework; no spec compliance verification; no coverage reporting; and Captain Agent's progress ledger tracks completion, not quality criteria. Score 2: code review possible via role assignment but not a built-in blocking gate; no test execution, no coverage, no spec verification. Source: docs.ag2.ai; gurusup.com/blog/best-multi-agent-frameworks-2026; AGENTIC-LANDSCAPE.md §2.3.

### D10 — Security Posture
**Score**: 2
**Evidence**: AG2 provides `DockerCommandLineCodeExecutor` for containerized code execution — a genuine sandboxing option when Docker is configured. `LocalCommandLineCodeExecutor` (the default fallback) runs on the host with "command sanitization against a list of dangerous commands" but no true sandboxing (docs.ag2.ai LocalCommandLineCodeExecutor reference). A February 2025 security study (CORBA) demonstrated that 79-100% of AutoGen agents could be forced into a completely blocked state within 1.6-1.9 dialogue turns via injected messages — a documented prompt injection/DoS vulnerability. No built-in SAST. No formal security review gate. Score 2: optional Docker sandboxing (not default); command sanitization on local executor (not true sandboxing); documented prompt injection vulnerability; no SAST, no security review gate. Source: docs.ag2.ai LocalCommandLineCodeExecutor; dev.to/tan_genie AI agents run unsandboxed code; AGENTIC-LANDSCAPE.md §2.3.

### D11 — Independent Validation and Spec Compliance
**Score**: 0
**Evidence**: AG2 has no mechanism for independent post-execution validation that agent outputs met the intended specification. Captain Agent tracks progress completion but does not verify that outputs are correct against a formal specification. There is no orchestrator-level agent that reads key output files and verifies them against documented postconditions, no SENTINEL-REPORT equivalent, and no automated spec compliance check. Source: docs.ag2.ai; AGENTIC-LANDSCAPE.md §2.3. [NO EVIDENCE of independent validation mechanism]

### D12 — Cross-Run Learning and Memory
**Score**: 2
**Evidence**: AG2 supports memory agents (agents that can read/write from a memory store) and the Reflexion pattern (agents that self-reflect and store learnings for subsequent tries). However, there is no structured cross-run lesson extraction protocol — memory stores capture what agents choose to write, with no defined schema for lessons learned, no ENTITIES.md equivalent, no incremental ARCHITECTURE.md, and no automatic injection of past-run failure patterns into new runs. Score 2: ad-hoc cross-session memory possible via memory agents; no structured protocol for extraction, curation, or automatic injection. Source: docs.ag2.ai memory documentation; towardsai.net AutoGen AG2 complete guide.

---

### AutoGen / AG2 Summary Table

| System       | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | Total |
|--------------|----|----|----|----|----|----|----|----|----|-----|-----|-----|-------|
| AutoGen / AG2| 4  | 2  | 0  | 4  | 4  | 2  | 4  | 6  | 2  | 2   | 0   | 2   | 32    |

### AutoGen / AG2 Narrative
AG2's strongest dimensions are observability (D8=6) — AutoGen Studio's real-time visual interface and OTEL integration provide genuine runtime visibility — and failure handling (D7=4), where the Captain Agent's re-delegation and AutoGen Studio's mid-execution intervention give two distinct recovery paths. The async-first event-driven architecture (D5=4) enables genuine concurrency beyond the GroupChat default pattern. The framework's weaknesses are contract enforcement (D2=2, informal role prompts only), state durability (D6=2, in-memory by default), independent validation (D11=0, none), and cross-run learning (D12=2, ad-hoc). The CORBA-demonstrated prompt injection DoS vulnerability and default-unsandboxed local executor (D10=2) are production risks. AG2 is best suited for conversational multi-agent workflows and research prototypes where the Captain Agent's re-delegation and AutoGen Studio's interactivity are valued; for production coding pipelines it requires explicit Docker configuration and additional quality gate engineering.

---

## OpenAI Agents SDK

**Category**: General-Purpose Framework
**Public source**: https://openai.github.io/openai-agents-python, https://github.com/openai/openai-agents-python
**Prior eval scores**: audit-2026: D1=4, D2=3, D3=2, D4=2, D5=4, D6=2, D7=5, D8=3 | eval-v2: D1=4, D2=3, D3=3, D4=2, D5=4, D6=3, D7=5, D8=3

---

### D1 — Task Decomposition Quality
**Score**: 4
**Evidence**: The OpenAI Agents SDK supports handoff chains — Agent A transfers to Agent B with context — and the 2026 multi-agent v2 API adds structured inter-agent messaging with readable path-based addresses (`/root/agent_a`) and agent listing for discovery (releasebot.io/updates/openai March 2026). Codex subagents enable parallel cloud execution of independent tasks. However: there is no formal decomposition planning step, no ownership matrix artifact written before execution, no DAG documented as a pre-execution planning document, no human review gate of the decomposition, and no hazard scan. The handoff chain IS the decomposition, defined in code. Score 4: structured decomposition via handoff chains with dependency ordering; multi-agent v2 adds explicit inter-agent structure; ownership implied but not formally enforced before execution. Source: openai.github.io/openai-agents-python/handoffs; releasebot.io/updates/openai March 2026; developers.openai.com/codex/subagents.

### D2 — Interface Contract Enforcement
**Score**: 2
**Evidence**: The Agents SDK uses guardrails (input/output validation via Pydantic models or custom functions) to validate what agents receive and produce — the nearest analog to interface contracts. Agents define their tools and handoff targets explicitly in code. However: there is no CONTRACT.md equivalent frozen before workers start, no shared types file that is version-controlled separately, handoff calls bypass tool guardrails (AGENTIC-LANDSCAPE.md §2.6 — a documented gap), and no adversarial review of interface agreements. Score 2: guardrails provide type validation at input/output boundaries; informal conventions in code; no pre-execution frozen contract artifact. Source: openai.github.io/openai-agents-python/guardrails; AGENTIC-LANDSCAPE.md §2.6.

### D3 — Benchmark Accuracy
**Score**: 4
**Evidence**: Codex (OpenAI's coding-specialized model/agent stack, built on the Agents SDK's infrastructure) achieves 77.3% on Terminal-Bench 2.0 (prior audit). Codex Security (research preview, March 2026) scanned 1.2 million commits and found 792 critical and 10,561 high-severity vulnerabilities with a <0.1% false-positive rate on critical findings (openai.com/index/codex-security-now-in-research-preview). These results demonstrate state-of-the-art coding accuracy for the underlying Codex agent stack. However, this evidence is model-level and agent-product-level, not a direct SDK framework benchmark — the SDK itself is an orchestration layer whose accuracy depends on the model used. Score 4: community-reported and product-level benchmark evidence demonstrates high coding accuracy for the Codex stack built on the SDK infrastructure; stops short of 6 because no official SWE-Bench Verified submission has been made for the SDK as a framework. [MEDIUM CONFIDENCE — benchmark is for Codex model/agent stack, not the SDK in isolation] Source: openai.com/index/codex-security-now-in-research-preview; releasebot.io/updates/openai/codex March 2026; prior audit-2026.

### D4 — Setup Complexity
**Score**: 8
**Evidence**: `pip install openai-agents` with one environment variable (`OPENAI_API_KEY`). Built-in tracing, guardrails, and handoffs work immediately out of the box with no additional infrastructure dependencies. The TypeScript SDK (`openai-agents-js`) was released in 2026, expanding language support. The SDK also gained websocket transport and realtime agent support (releasebot.io/updates/openai March 2026). Core concepts (Agents, Handoffs, Guardrails, Tracing) are documented with a quickstart that produces a working multi-agent system in minutes. Score 8: copy install plus one env var; core concepts understandable in under 30 minutes; no infrastructure dependencies. Source: openai.github.io/openai-agents-python quickstart; pypi.org/project/openai-agents; releasebot.io/updates/openai March 2026.

### D5 — Parallelism and Execution Efficiency
**Score**: 4
**Evidence**: Guardrails execute in parallel with agent execution by default (`run_in_parallel=True`) for minimum latency. Codex subagents enable genuine parallel cloud execution — independent tasks can be dispatched to separate Codex instances simultaneously. The primary handoff pattern is sequential (Agent A transfers to Agent B), but the 2026 multi-agent v2 API improves structured concurrent coordination. No lightweight reaping mode for sub-3-minute startup. Score 4: structured parallelism via Codex subagent dispatch and parallel guardrails; sequential handoff is the primary pattern; coordination overhead is managed but no continuous parallel execution with near-zero overhead. Source: openai.github.io/openai-agents-python/handoffs; developers.openai.com/codex/subagents; releasebot.io/updates/openai March 2026.

### D6 — State Durability and Resumability
**Score**: 2
**Evidence**: The OpenAI Agents SDK has no built-in persistent checkpointing mechanism. Conversation context is passed via the messages array in each API call; state does not automatically survive session death. Memory consolidation patterns are possible via custom implementation (developers.openai.com/cookbook context personalization example), but there is no framework-native checkpoint-per-step or automated resume protocol. Codex subagents in cloud execution have their own session management, but inter-agent state coordination on crash is not handled automatically. Score 2: state survives within a session; no built-in cross-session checkpoint; session death requires restart or custom state reconstruction. Source: openai.github.io/openai-agents-python; developers.openai.com/cookbook/examples/agents_sdk/context_personalization; agentwiki.org/openai_agents_sdk.

### D7 — Failure Handling and Recovery
**Score**: 2
**Evidence**: The SDK provides retry at the API call level (configurable retry for rate limits and transient errors). Guardrails can block agent execution on validation failure. However, there is no formal failure taxonomy (transient/logical/structural/environmental), no circuit breaker after N failures on the same locus, no dedicated diagnosis agent, and no escalation protocol for non-transient failures. Approval gates (for Codex high-risk actions) constitute a human-in-the-loop interrupt, but this is a security mechanism rather than a failure recovery protocol. Score 2: SDK-level retry for transient API failures; no failure classification or circuit breaker. Source: openai.github.io/openai-agents-python; AGENTIC-LANDSCAPE.md §2.6; developers.openai.com/codex/agent-approvals-security.

### D8 — Observability and Debuggability
**Score**: 6
**Evidence**: The SDK provides built-in comprehensive tracing: every LLM generation, tool call, handoff, guardrail event, and custom event is captured via BatchTraceProcessor to the OpenAI backend (openai.github.io/openai-agents-python/tracing). Real-time status is visible in the OpenAI dashboard. The SDK supports custom trace processors enabling export to external backends. Custom events and spans can be added via the tracing API. No native time-travel debugging or per-step replay equivalent to LangSmith. Score 6: real-time status roster in OpenAI dashboard plus structured per-agent trace export; lacks time-travel debugging and per-agent cost breakdown at the framework level. Source: openai.github.io/openai-agents-python/tracing; releasebot.io/updates/openai March 2026; AGENTIC-LANDSCAPE.md §2.6.

### D9 — Pre-Merge Quality Gates
**Score**: 4
**Evidence**: Guardrails run in parallel with agent execution and fail fast on violations — tool guardrails run on every custom function-tool invocation, providing a blocking automated check on agent outputs (openai.github.io/openai-agents-python/guardrails). Codex's `agent approvals & security` mode requires human approval before commands with potential side effects execute. Test execution infrastructure exists via `codex exec --json` capturing JSONL traces with command_execution events; build checks can run after skill completion (developers.openai.com/blog/eval-skills). However: guardrails check policy compliance, not functional code correctness; test execution is not a blocking gate by default; and there is no built-in security review step as a mandatory pipeline stage. Score 4: automated blocking guardrail gate + approval gates for high-risk actions constitute two gates; does not achieve the triple gate (tests + review + security) simultaneously required for score 6. Source: openai.github.io/openai-agents-python/guardrails; developers.openai.com/codex/agent-approvals-security; developers.openai.com/blog/eval-skills.

### D10 — Security Posture
**Score**: 6
**Evidence**: (a) Sandboxed execution: Codex cloud runs in OpenAI-managed isolated containers with no host file system access; secrets scrubbed before the agent phase; offline by default during the agent phase (developers.openai.com/codex/concepts/sandboxing). Codex CLI uses OS-level sandbox with no-network and limited write permissions. (b) Prompt injection protection: SDK guardrails include jailbreak detection and PII redaction (openai.github.io/openai-agents-python/guardrails); OpenAI's agent builder safety guide documents prompt injection threat model and mitigations (platform.openai.com/docs/guides/agent-builder-safety). (c) SAST: Codex Security (research preview March 2026) provides AI-powered vulnerability scanning with structured threat models; scanned 1.2M commits finding 792 criticals with <0.1% false-positive rate (openai.com/index/codex-security-now-in-research-preview). (d) Approval gates: human approval required before Codex executes high-risk commands. Score 6: sandboxed execution (GA in cloud), guardrails with prompt injection protection (GA), and a security review gate via approvals — three of four components are GA; Codex Security SAST is research preview, not yet GA. Full score-8 would require SAST in GA and sandboxing verified locally. Source: developers.openai.com/codex/concepts/sandboxing; openai.github.io/openai-agents-python/guardrails; openai.com/index/codex-security-now-in-research-preview; platform.openai.com/docs/guides/agent-builder-safety.

### D11 — Independent Validation and Spec Compliance
**Score**: 0
**Evidence**: The OpenAI Agents SDK has no mechanism for independent post-execution validation that agent outputs met a pre-defined specification. Guardrails validate policy compliance (content moderation, PII) but not functional spec compliance. There is no SENTINEL-REPORT equivalent, no orchestrator that independently reads and verifies output files against documented postconditions, and no requirement traceability mechanism. Source: openai.github.io/openai-agents-python; developers.openai.com/api/docs/guides/agents-sdk. [NO EVIDENCE of independent spec validation mechanism]

### D12 — Cross-Run Learning and Memory
**Score**: 2
**Evidence**: The SDK supports memory consolidation patterns where agents can write and retrieve structured notes across sessions (developers.openai.com/cookbook context personalization — two-phase memory: session notes + global memory consolidation via merging and pruning). However, this is a recipe/cookbook pattern, not a built-in framework feature. There is no structured LESSONS.md extraction protocol, no entity registry, no incremental ARCHITECTURE.md, and no automatic injection of past-run failure patterns into new run prompts. Score 2: ad-hoc cross-session memory via custom implementation; no built-in structured learning or injection protocol. Source: developers.openai.com/cookbook/examples/agents_sdk/context_personalization; openai.github.io/openai-agents-python.

---

### OpenAI Agents SDK Summary Table

| System              | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | Total |
|---------------------|----|----|----|----|----|----|----|----|----|-----|-----|-----|-------|
| OpenAI Agents SDK   | 4  | 2  | 4  | 8  | 4  | 2  | 2  | 6  | 4  | 6   | 0   | 2   | 44    |

### OpenAI Agents SDK Narrative
The OpenAI Agents SDK leads this group in total score (44), driven by three standout dimensions: setup friction (D4=8, the lowest in the group), security posture (D10=6, the highest in the group with sandboxed cloud execution and prompt injection guardrails), and benchmark accuracy (D3=4, the highest in the group with Codex performance evidence). The blocking guardrails pipeline (D9=4) is the only quality gate mechanism in this group to score above 2. The SDK's primary weaknesses are structural: no pre-execution interface contracts (D2=2), no failure taxonomy or circuit breaker (D7=2), no state durability across session crashes (D6=2), and complete absence of independent validation (D11=0) and cross-run learning (D12=2). The SDK excels for rapid deployment of well-understood agent patterns leveraging OpenAI's model stack; it is not designed for the kind of rigorous pre-execution planning, contract enforcement, or post-execution assurance that complex multi-agent coding pipelines require.

---

## ChatDev

**Category**: General-Purpose Framework
**Public source**: https://github.com/OpenBMB/ChatDev
**Prior eval scores**: audit-2026: D1=4, D2=2, D3=2, D4=2, D5=2, D6=2, D7=3, D8=2 | eval-v2: (not included in v2 group report; CAMEL was substituted)

---

**Note on ChatDev 2.0 (DevAll)**: ChatDev 2.0 (DevAll) was officially released January 7, 2026, representing a major architectural evolution from the original waterfall chatroom model. The original ChatDev (fixed-role SOP pipeline) and ChatDev 2.0 (zero-code DAG-based multi-agent platform) are scored together with version distinctions where material. Where evidence is version-specific, this is noted.

---

### D1 — Task Decomposition Quality
**Score**: 4
**Evidence**: ChatDev 2.0 (DevAll) introduced DAG topology support — Agent A can feed results to both Agent B and Agent C simultaneously while Agent D waits for both to complete (x-cmd.com blog Jan 2026 ChatDev 2.0 release; github.com/OpenBMB/ChatDev 2026 README). Nodes support a `sibling` field for parallel processing and a Map Mode that splits list inputs into parallel execution units. This is a significant upgrade from the original sequential SOP waterfall. However: the DAG is configured by users, not generated by a planning agent with a formal hazard scan; there is no formal file ownership matrix enforced; no human review gate of the decomposition before execution; and no per-worker preconditions/postconditions. Score 4: structured DAG decomposition with dependency ordering and explicit parallelism (ChatDev 2.0); ownership implied by node assignments but not formally enforced. Score reflects ChatDev 2.0; original ChatDev would score 2. Source: x-cmd.com/blog/260110; github.com/OpenBMB/ChatDev; yuv.ai/blog/chatdev.

### D2 — Interface Contract Enforcement
**Score**: 2
**Evidence**: ChatDev 2.0's workflow configuration (YAML/JSON node definitions with input/output schema per node) provides structured interface definitions between nodes — what each node receives and produces is declared in configuration. However: these are user-configured declarations, not formally frozen pre-execution contracts written by a planning agent; there is no adversarial review of interface agreements; there is no AMENDMENT.md protocol if a contract proves wrong mid-execution; and in the original ChatDev, "coordination is primarily conversational" with role separation enforced via prompt only (AGENTIC-LANDSCAPE.md §5.5). Score 2: ChatDev 2.0 improves on original by adding typed node I/O schemas; does not reach formal frozen contract with factual verification. Source: github.com/OpenBMB/ChatDev workflow_authoring.md; yuv.ai/blog/chatdev; AGENTIC-LANDSCAPE.md §5.5.

### D3 — Benchmark Accuracy
**Score**: 0
**Evidence**: No published SWE-Bench Verified score for ChatDev on any public leaderboard (swebench.com, epoch.ai — checked March 2026). AgileCoder (2024 research paper) explicitly outperforms ChatDev on HumanEval and MBPP. The 2026 SWE-Bench February update (simonwillison.net) does not include ChatDev. No official benchmark submission has been made for ChatDev 1.x or 2.0. Source: swebench.com; simonwillison.net/2026/Feb/19/swe-bench; AgileCoder FSoft-AI4Code paper. [NO EVIDENCE]

### D4 — Setup Complexity
**Score**: 4
**Evidence**: ChatDev 2.0 (DevAll) is a zero-code multi-agent platform marketed for rapid workflow configuration via drag-and-drop (x-cmd.com blog Jan 2026). The underlying system still requires API key configuration and an understanding of the node-based workflow configuration format. The original ChatDev required `pip install` plus SOP YAML configuration with a learning curve. ChatDev 2.0's no-code interface reduces the barrier for non-developers but does not eliminate configuration requirements. Score 4: standard install / web interface access; requires reading documentation to build meaningful workflows; non-trivial learning curve for the DAG workflow format. Source: x-cmd.com/blog/260110; github.com/OpenBMB/ChatDev README; aitoolsatlas.ai ChatDev review 2026.

### D5 — Parallelism and Execution Efficiency
**Score**: 4
**Evidence**: ChatDev 2.0 introduces DAG topology with explicit parallel execution — independent nodes execute simultaneously when their dependencies are satisfied, and Map Mode splits list inputs into parallel execution units (x-cmd.com blog Jan 2026; github.com/OpenBMB/ChatDev). WebSocket pushes real-time state, log, and artifact events during execution. This is a substantial improvement over the original ChatDev's sequential-only SOP waterfall. However: no published timing benchmarks; no lightweight "reaping" mode for small runs; no persistent daemon; and "thousands of agents" capability cited is a design claim, not an empirically validated production figure. Score 4: structured DAG-based parallel execution (ChatDev 2.0); dependency-aware dispatch; coordination overhead is moderate; no sub-3-minute startup mode. Source: x-cmd.com/blog/260110; github.com/OpenBMB/ChatDev; yuv.ai/blog/chatdev. [Score reflects ChatDev 2.0; original ChatDev would score 2]

### D6 — State Durability and Resumability
**Score**: 4
**Evidence**: ChatDev 2.0 provides execution session isolation — every execution creates an isolated session where "attachments, Python workspace, context snapshots, and summary outputs are downloadable for later review" (x-cmd.com blog Jan 2026). JSON logs are stored in `logs/` and run assets in `WareHouse/`. WebSocket pushes state transitions in real-time and stores them. Context snapshots constitute checkpoint-like artifacts. However: there is no defined automated resume protocol (reading the last checkpoint and continuing from it); recovery would require manual inspection of the snapshot and restarting from a known-good state; there is no per-worker granularity state file maintained continuously; and no automated orchestrator detection of session death. Score 4: checkpoint-based persistence via session snapshots; resumption is possible but requires manual reconstruction from stored artifacts. Source: x-cmd.com/blog/260110; github.com/OpenBMB/ChatDev/blob/main/docs/user_guide/en/workflow_authoring.md.

### D7 — Failure Handling and Recovery
**Score**: 2
**Evidence**: No formal failure taxonomy is documented for ChatDev 1.x or 2.0. The original ChatDev's waterfall design meant failure mid-pipeline required restarting from the beginning. ChatDev 2.0's DAG structure allows partial reruns from a failed node in principle (since completed upstream nodes have stored outputs), but no automated circuit breaker, no failure classification protocol, and no documented retry mechanism with typed failure paths. Score 2: basic retry via manual restart; DAG structure enables partial reruns in principle; no failure classification. Source: AGENTIC-LANDSCAPE.md §5.5; github.com/OpenBMB/ChatDev; aitoolsatlas.ai ChatDev review 2026.

### D8 — Observability and Debuggability
**Score**: 4
**Evidence**: ChatDev 2.0 provides real-time event streaming via WebSocket — state, logs, and artifact events are pushed during execution (x-cmd.com blog Jan 2026). JSON logs are stored in `logs/` with per-role attribution. Run assets (context snapshots, workspace artifacts) are downloadable. However: there is no built-in dashboard equivalent to LangSmith or AutoGen Studio; no trace IDs per LLM call; no timeline view showing phase transitions with timing; and no per-agent cost breakdown. Score 4: structured per-role logging with real-time WebSocket event streaming; status inferable from logs and stored artifacts; no built-in dashboard or timeline. Source: x-cmd.com/blog/260110; github.com/OpenBMB/ChatDev docs.

### D9 — Pre-Merge Quality Gates
**Score**: 2
**Evidence**: ChatDev 2.0's workflow configuration can include a QA/review node as part of the DAG — the user designs in a quality step. The original ChatDev had a Reviewer role. However: these are user-configured role nodes, not a built-in blocking multi-gate quality pipeline; no automated test execution framework is built into the platform; no spec compliance verification; no security review gate. Score 2: quality review via role/node designation is possible but user-configured, not a built-in blocking gate. Source: github.com/OpenBMB/ChatDev/blob/main/docs/user_guide/en/workflow_authoring.md; aitoolsatlas.ai ChatDev review 2026; AGENTIC-LANDSCAPE.md §5.5.

### D10 — Security Posture
**Score**: 0
**Evidence**: No sandboxed execution environment is documented for ChatDev 1.x or 2.0. Generated code is output to a workspace directory; execution depends on the user's environment. No built-in SAST, no vulnerability scanning, no security review gate, no documented threat model. Security search results for ChatDev explicitly do not surface ChatDev-specific security features — only general AI agent security recommendations apply (iain.so/security-for-production-ai-agents-in-2026). Score 0: no security features documented. [NO EVIDENCE of any security mechanism] Source: github.com/OpenBMB/ChatDev; aitoolsatlas.ai ChatDev review 2026; iain.so security for production AI agents 2026.

### D11 — Independent Validation and Spec Compliance
**Score**: 0
**Evidence**: ChatDev has no mechanism for independent post-execution validation that agent outputs met the intended specification. Role/node self-reports (task completion) are accepted. No orchestrator-level verification pass, no SENTINEL-REPORT equivalent, no automated spec compliance check, no traceability from requirements to generated tests. Source: github.com/OpenBMB/ChatDev; AGENTIC-LANDSCAPE.md §5.5. [NO EVIDENCE]

### D12 — Cross-Run Learning and Memory
**Score**: 4
**Evidence**: ChatDev's "Experiential Co-Learning" mechanism (shared across ChatDev and MetaGPT's codebase lineage) captures lessons from prior runs through a cross-project experience pool — agents can reference past solutions when tackling similar problems (yuv.ai/blog/chatdev; aiagents.wiki/agents/chatdev). ChatDev 2.0 stores run assets in `WareHouse/` including context snapshots and summary outputs, providing structured artifacts from each run that could be referenced in future runs. Score 4: structured lesson capture via Experiential Co-Learning with explicit mechanism; artifacts available for future runs; not automatic injection via pattern matching. [MEDIUM CONFIDENCE — co-learning mechanism from secondary sources; full ChatDev 2.0 documentation not independently verified for this feature] Source: yuv.ai/blog/chatdev; aiagents.wiki/agents/chatdev; github.com/OpenBMB/ChatDev.

---

### ChatDev Summary Table

| System  | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | Total |
|---------|----|----|----|----|----|----|----|----|----|-----|-----|-----|-------|
| ChatDev | 4  | 2  | 0  | 4  | 4  | 4  | 2  | 4  | 2  | 0   | 0   | 4   | 30    |

### ChatDev Narrative
ChatDev 2.0 (DevAll, January 2026) represents a significant architectural leap from the original sequential SOP waterfall — the DAG topology (D1=4, D5=4), session isolation with stored artifacts (D6=4), and Experiential Co-Learning (D12=4) bring it substantially closer to peer frameworks. The zero-code interface reduces integration friction for non-developer users. The framework's persistent weaknesses are structural: no interface contracts (D2=2), no failure taxonomy (D7=2), no security features whatsoever (D10=0), and no independent validation (D11=0). With no published benchmark results (D3=0) and no automated quality gates (D9=2), ChatDev is best suited for zero-code rapid prototyping of collaborative multi-agent workflows where the DAG flexibility and co-learning are valued; it is not suitable for production coding pipelines or security-sensitive environments.

---

## Group H2 — Summary Table

| System              | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | Total |
|---------------------|----|----|----|----|----|----|----|----|----|-----|-----|-----|-------|
| OpenAI Agents SDK   | 4  | 2  | 4  | 8  | 4  | 2  | 2  | 6  | 4  | 6   | 0   | 2   | 44    |
| AutoGen / AG2       | 4  | 2  | 0  | 4  | 4  | 2  | 4  | 6  | 2  | 2   | 0   | 2   | 32    |
| LangGraph           | 4  | 4  | 0  | 4  | 4  | 6  | 4  | 8  | 2  | 2   | 0   | 2   | 40    |
| CrewAI              | 4  | 2  | 0  | 6  | 4  | 2  | 2  | 4  | 2  | 2   | 0   | 2   | 30    |
| MetaGPT             | 4  | 4  | 0  | 4  | 2  | 2  | 2  | 4  | 2  | 0   | 2   | 4   | 30    |
| ChatDev             | 4  | 2  | 0  | 4  | 4  | 4  | 2  | 4  | 2  | 0   | 0   | 4   | 30    |

*Sorted by total score descending. Ties listed in alphabetical order.*

---

## Group H2 — Field Observations

**D3 (Benchmark Accuracy) is the hardest zero in this group.** Five of six systems score 0 on D3. These frameworks are general-purpose orchestration layers; accuracy is a property of the underlying model, not the framework. Only the OpenAI Agents SDK earns a 4 by virtue of the Codex agent stack's published results — and even that is a model-level attribution, not a framework benchmark. This is not a scoring flaw; it reflects the genuine gap: no general-purpose multi-agent framework has submitted to SWE-Bench as a system.

**D11 (Independent Validation) is universally 0, except MetaGPT at 2.** No framework in this group builds independent post-execution verification of spec compliance into its core architecture. MetaGPT's QA Engineer role earns a 2 because the role provides human-level spot-check by design. All other frameworks accept worker self-reports unconditionally. This is the clearest gap in the general-purpose framework field.

**Security (D10) stratifies the group sharply.** OpenAI Agents SDK (D10=6) leads by a wide margin — the only framework with GA sandboxed execution, GA guardrails with prompt injection protection, and a security review gate. LangGraph (D10=2) dropped from its prior observability dominance due to three active CVEs including a CVSS 9.3 critical. MetaGPT and ChatDev (D10=0) have no documented security mechanisms whatsoever.

**State durability (D6) is LangGraph's defining advantage.** LangGraph's per-super-step checkpointing (D6=6) is the only framework in this group with a documented automatic resume protocol. ChatDev 2.0 earns D6=4 via session isolation snapshots (partial but structured persistence). All other frameworks score D6=2.

**Observability (D8) shows the LangGraph/AG2 lead.** LangGraph with LangSmith (D8=8, the highest in the group) and AG2 with AutoGen Studio + OTEL (D8=6) provide genuine real-time visibility. The observability gap between these frameworks and the rest is significant.

**Cross-run learning (D12) is uniformly weak.** Only MetaGPT and ChatDev score D12=4 via their Experiential Co-Learning mechanism. All other frameworks score D12=2 (ad-hoc memory). No framework scores D12=6 or above — no framework in this group automatically injects past-run learnings into new run prompts via pattern matching. This is a field-wide gap.
