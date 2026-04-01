# General-Purpose Multi-Agent Frameworks Scoring Report
**Spectrum**: audit-2026-0331
**Howler**: H3-frameworks
**Date**: 2026-03-31
**Rubric version**: evaluation/audit-2026/RUBRIC.md v1.0

---

## Scoring Table

| System | D1 Cost | D2 Speed | D3 Accuracy | D4 Workflow Rigor | D5 Observability | D6 Recovery | D7 Setup | D8 Scalability | Total |
|--------|---------|----------|-------------|-------------------|------------------|-------------|----------|----------------|-------|
| CrewAI | 4 | 4 | 2 | 2 | 3 | 2 | 4 | 3 | 24 |
| LangGraph | 4 | 3 | 2 | 3 | 5 | 3 | 3 | 3 | 26 |
| MetaGPT | 4 | 2 | 2 | 3 | 2 | 2 | 3 | 2 | 20 |
| AutoGen / AG2 | 4 | 3 | 2 | 2 | 3 | 2 | 3 | 3 | 22 |
| ChatDev / DevAll | 4 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 19 |
| CAMEL-AI | 4 | 2 | 2 | 1 | 2 | 1 | 4 | 2 | 18 |
| OpenAI Agents SDK | 4 | 3 | 2 | 2 | 4 | 2 | 5 | 3 | 25 |

---

## Per-System Evidence Notes

---

### CrewAI

**D1 Cost** — 4: Open-source framework; users pay underlying model costs only. No orchestration surcharge for the OSS library. CrewAI Cloud paid tier starts at $99/month (crewai.com/pricing, verified March 2026), but the pure-OSS path has no platform fee. Running 3–5 agents incurs standard model API costs — at GPT-4o-class rates (~$0.005/1K tokens), a representative 5-agent run producing ~15,000 total tokens costs roughly $0.075–$0.15, placing this solidly in the $0.10–$0.50/run band. Score 4 (low cost, clearly affordable). [MEDIUM CONFIDENCE — model costs estimated from token counts; cloud orchestration tier pricing from crewai.com/pricing March 2026]

**D2 Speed** — 4: CrewAI documentation confirms simultaneous agent execution for hierarchical and consensual crew processes. Company-reported benchmarks claim 2–3x faster execution than comparable frameworks (AGENTIC-LANDSCAPE.md §2.2, citing CrewAI company data). No independent wall-clock timing for a 3-agent coding task is publicly available. The architecture supports genuine parallelism; the company claim is plausible given event-driven Flow execution. Score 4 (fast, parallelism evident), applying conservative interpretation given company-only sourcing. [MEDIUM CONFIDENCE — company-reported benchmark; no independent timing data]

**D3 Accuracy** — 2: No published SWE-Bench result for CrewAI as a framework (SWE-Bench measures per-system solutions to GitHub issues; CrewAI is a general orchestration framework, not a pre-packaged coding agent). Community reports are mixed — the framework is adopted for agentic workflows broadly, but no community consensus on code quality. The prior landscape survey notes no SWE-Bench submission. Score 2 (below-average accuracy; no benchmark data). [LOW CONFIDENCE — no public benchmark evidence for CrewAI as a coding system; community reports not coding-specific]

**D4 Workflow Rigor** — 2: CrewAI provides role separation (agent roles, goals, backstory) and task retry with configurable max_attempts. However: (a) no pre-execution interface contracts or file ownership declarations; (b) no formal failure taxonomy — failure handling is "retry the task"; (c) no automated circuit breakers; (d) review is by role designation only (a "Reviewer" agent exists but is not structurally independent in the way an adversarial review step is). Per rubric, score 3 requires role separation OR retry-with-logging; score 2 is multiple agents with informal coordination. CrewAI has both role separation and retry, but lacks contracts, taxonomy, and circuit breakers — marginally above the score-2 anchor but not achieving score-3's "no file ownership contracts, no formal failure taxonomy." Applying conservative interpretation: score 2. [MEDIUM CONFIDENCE — architecture from docs.crewai.com and AGENTIC-LANDSCAPE.md §2.2]

**D5 Observability** — 3: CrewAI provides structured logs with agent labels (task output, agent attribution). Real-time observability is available via paid CrewAI Cloud (real-time tracing per crewai.com/pricing and zenml.io/blog/crewai-pricing, March 2026). OSS version uses event emitter for LLM call tracking (docs.crewai.com/changelog) and supports third-party integrations (W&B Weave, Arize Phoenix, Opik). No replay or step-through in the OSS version. Score 3 (structured logs, agent labels, no real-time dashboard in OSS). [MEDIUM CONFIDENCE — paid tier has stronger observability; OSS tier scored here]

**D6 Recovery** — 2: Task retry on failure with configurable max_retry_attempts. Error output fed back into retry context. No formal failure taxonomy — failure types are not classified, only retried. No circuit breaker. State loss occurs on hard crash (no persistent checkpointing equivalent to LangGraph). Per rubric score 3 requires retry with configurable max attempts plus error feedback; that is present. However, "state persists within a run but loss occurs on hard crash" is the score-3 description, and CrewAI's state persistence is weaker — Memory system (SQLite) persists cross-session but task execution state is session-only. Applying conservative interpretation: score 2. [MEDIUM CONFIDENCE — from docs.crewai.com architecture documentation]

**D7 Setup** — 4: `pip install crewai` with one environment variable (LLM API key). No infrastructure dependencies required for local OSS use. CrewAI's quickstart produces a working crew in minutes. GitHub issues show occasional model provider configuration friction but no systematic setup failures. Score 4 (2–3 steps, first run achievable within 1 hour). Source: docs.crewai.com quickstart.

**D8 Scalability** — 3: CrewAI documentation does not provide a tested ceiling above 6–8 agents. 450M monthly workflows (company-reported) confirms production scale, but these are not necessarily large parallel agent counts per run. The framework architecture uses a manager LLM for hierarchical crews, which creates a potential orchestrator bottleneck at higher agent counts. Community reports and the prior landscape survey (AGENTIC-LANDSCAPE.md §2.2) indicate sweet spot of 3–5 agents. Score 3 (3–5 agent sweet spot; degrades beyond). [MEDIUM CONFIDENCE — architectural inference plus community reports; no empirical multi-agent scaling data]

**Uncertainty flags**: D1 (model cost estimate), D2 (company-only speed data), D3 (no benchmark), D4 (conservative rubric interpretation at boundary), D6 (conservative interpretation)

---

### LangGraph

**D1 Cost** — 4: OSS LangGraph has no platform fee. LangGraph Cloud (hosted) is commercial. Scoring the OSS path: users pay model costs only. A representative 3–5 agent run costs $0.10–$0.50 at GPT-4o-class rates. LangSmith (observability) adds overhead: Developer tier free (5,000 traces/month); Plus tier $39/seat/month (langchain.com/pricing, verified March 2026 via margindash.com/langsmith-pricing). Score 4 — OSS framework costs are model-only; LangSmith adds subscription overhead but is optional. [MEDIUM CONFIDENCE — model costs estimated; LangSmith pricing from margindash.com/langsmith-pricing March 2026]

**D2 Speed** — 3: LangGraph supports parallel node execution via async Python and sub-graph composition. However, every state transition involves checkpoint writes (MemorySaver, SqliteSaver, PostgresSaver), adding overhead. No published wall-clock benchmarks for a 3-agent parallel coding task. Community reports from the mager.co deep-dive (AGENTIC-LANDSCAPE.md §2.1 source list) describe LangGraph as performant for workflows but note that "complex graphs require understanding graph topology." Score 3 (supports parallelism with constraints; checkpointing adds overhead). [MEDIUM CONFIDENCE — architecture documentation; no independent timing benchmarks]

**D3 Accuracy** — 2: LangGraph is an orchestration framework, not a pre-packaged coding agent. No SWE-Bench submission for LangGraph as a system. The framework enables building coding agents but provides no accuracy guarantee itself — accuracy depends entirely on the underlying models and agent definitions. Score 2 (no benchmark data). [LOW CONFIDENCE — no public benchmark evidence for LangGraph as a coding system]

**D4 Workflow Rigor** — 3: LangGraph provides: (a) explicit state schema (TypedDict/Pydantic) — nearest analog to interface contracts, but not enforced between parallel agents; (b) conditional edges and human-in-the-loop pause points — some failure handling structure; (c) checkpointing enables resume after failure; (d) no formal failure taxonomy (transient/logical/structural); (e) no automated circuit breakers; (f) no file ownership contracts. Score 3: role separation exists via node specialization; retry/resume is available via checkpoints; no formal failure taxonomy or file ownership contracts. [Evidence: AGENTIC-LANDSCAPE.md §2.1; LangGraph documentation on state management]

**D5 Observability** — 5: LangGraph with LangSmith provides all four score-5 components: (a) structured logs with trace IDs per agent/node — every LLM call, tool use, and state transition is captured; (b) real-time dashboard via LangSmith UI showing active graph execution state; (c) time-travel debugging — step backwards through any execution and replay with different inputs; (d) mid-execution inspection without interrupting the run. LangSmith tracing activates with a single environment variable for LangGraph apps (docs.langchain.com/langsmith/observability, confirmed March 2026 via analyticsvidhya.com LangGraph+LangSmith guide). Score 5 — this is the LangSmith-class reference level cited in the rubric. [Evidence: LangSmith docs langchain.com/langsmith/observability; analyticsvidhya.com/blog/2025/10/a-guide-to-langgraph-and-langsmith]

**D6 Recovery** — 3: LangGraph checkpoints persist state after every node — recovery is possible by resuming from the last checkpoint. Human-in-the-loop patterns enable pause and resume at any node. LangGraph Cloud (hosted) adds retry policies and monitoring. In the OSS version, recovery requires manual resume from checkpoint — no automated retry loop. No formal failure taxonomy. Score 3 (retry/resume via checkpoint; no formal taxonomy; no circuit breaker in OSS). [Evidence: AGENTIC-LANDSCAPE.md §2.1; LangGraph documentation on checkpointers]

**D7 Setup** — 3: `pip install langgraph` is straightforward, but first parallel multi-agent run requires: defining a StateGraph with typed state schema, adding nodes and edges, configuring a checkpointer (MemorySaver is local; SqliteSaver requires SQLite), and setting up LangSmith if observability is needed. This is more than a 1-hour setup for a developer unfamiliar with the framework. GitHub issues document learning curve friction around state schema design. Score 3 (4–6 steps; tutorial required; half-day to first parallel run). [Evidence: LangGraph quickstart docs; AGENTIC-LANDSCAPE.md §2.1 notes "requires upfront state schema definition"]

**D8 Scalability** — 3: LangGraph's sub-graph composition enables hierarchical orchestration, and async execution supports parallel nodes. The prior landscape survey notes "LangGraph (7) scales via sub-graph composition" in its scalability section. However, no empirical evidence of scaling beyond 5–6 parallel agents, and the single-orchestrator pattern creates potential bottlenecks. Score 3 (3–5 agent sweet spot; architecture supports more but no empirical ceiling data). [MEDIUM CONFIDENCE — architectural inference from AGENTIC-LANDSCAPE.md §2.1 and §7]

**Uncertainty flags**: D1 (LangSmith adds optional overhead), D2 (no timing benchmarks), D3 (no benchmark — framework not a coding agent), D8 (no empirical scale data)

---

### MetaGPT

**D1 Cost** — 4: Open-source framework; no platform fee. Users pay model costs. A software company simulation (PM + Architect + Engineer + QA) with document outputs will consume more tokens per run than a minimal agent pair — community reports suggest 3,000–8,000 tokens per role turn, meaning a full run is $0.15–$0.50 at GPT-4o-class rates. Score 4. [MEDIUM CONFIDENCE — token volume estimated from document-heavy pipeline description; no published cost data]

**D2 Speed** — 2: MetaGPT 2.0 added a pub/sub architecture enabling parallel execution within role boundaries. However, the core pipeline is waterfall-sequential by design: PM → Architect → Engineer → QA, each blocked on the previous stage's document output. Even with pub/sub, the sequential SOP means total wall-clock time for a full run significantly exceeds 30 minutes for non-trivial tasks. Community reports in the prior landscape survey characterize MetaGPT as having an inherently rigid sequential structure. Score 2 (primarily sequential execution; parallelism limited to within-role boundaries). [Evidence: AGENTIC-LANDSCAPE.md §2.4; MetaGPT arxiv paper arxiv.org/html/2307.07924v5]

**D3 Accuracy** — 2: MetaGPT has no published SWE-Bench Verified score on the current leaderboard (confirmed via SWE-Bench leaderboard review). The prior landscape survey notes "Performance on real-world benchmarks (SWE-Bench) lags behind newer systems." AgileCoder (2024 paper, FORGE 2025) explicitly reports outperforming MetaGPT on HumanEval and MBPP. MetaGPT's AFlow paper was accepted oral at ICLR 2025 (top 1.8%), demonstrating research quality but not coding task accuracy. Score 2 (below-average accuracy; lags newer systems on benchmarks). [Evidence: AGENTIC-LANDSCAPE.md §2.4 and §5.7; AgileCoder paper FSoft-AI4Code; MetaGPT ICLR 2025 acceptance — producthunt.com/products/metagpt-x/launches]

**D4 Workflow Rigor** — 3: MetaGPT provides: (a) document-as-protocol — roles produce structured documents (PRD, SystemDesign, API spec) that serve as downstream specifications — closest to interface contracts in this category; (b) role separation is enforced structurally (roles cannot act outside their SOP step); (c) limited failure taxonomy — malformed documents can fail silently; (d) no circuit breaker; (e) no file ownership matrix. The document-as-protocol pattern is a genuine workflow discipline absent from most frameworks. Score 3 (structured coordination via document pipeline; no formal failure taxonomy; no file ownership contracts). [Evidence: AGENTIC-LANDSCAPE.md §2.4; MetaGPT paper arxiv.org/html/2308.00352v6]

**D5 Observability** — 2: MetaGPT produces structured documents (PRD.md, SystemDesign.md, code files) as outputs, and logs are written to the workspace directory. No real-time dashboard. No trace IDs per agent. No replay capability. Users inspect output files post-hoc. Score 2 (structured document outputs provide post-hoc attribution but no real-time status, no trace IDs, no dashboard). [MEDIUM CONFIDENCE — from MetaGPT GitHub documentation and AGENTIC-LANDSCAPE.md §2.4]

**D6 Recovery** — 2: Documents on disk serve as persistent state — if interrupted, roles can re-read existing documents and continue. This is partial persistence, not formal checkpointing. Error recovery is "retry with human review" — if a malformed document is produced, the user must intervene. No automated retry loop, no failure taxonomy, no circuit breaker. Score 2 (manual resume from document state; no automation). [Evidence: AGENTIC-LANDSCAPE.md §2.4 — "error recovery is primarily via retry + human review"]

**D7 Setup** — 3: `pip install metagpt` followed by API key configuration and project directory setup. MetaGPT requires configuration of the software company roles, typically via a config file. The prior landscape survey notes setup is not complex but the SOP configuration has a learning curve. Score 3 (4–6 steps; config file required; first run achievable within a half-day). [Evidence: MetaGPT GitHub README — github.com/FoundationAgents/MetaGPT]

**D8 Scalability** — 2: MetaGPT's architecture is designed for a fixed set of software company roles (typically 5–6). Scaling beyond this role count is not the design intent; the waterfall SOP becomes increasingly rigid as roles multiply. No documented evidence of effective parallel execution at 6+ agents. Score 2 (architecture practical ceiling at 3–5 agents in sequential mode). [MEDIUM CONFIDENCE — architectural inference from AGENTIC-LANDSCAPE.md §2.4; no empirical scale data]

**Uncertainty flags**: D1 (token volume estimated), D3 (no SWE-Bench submission), D5 (no documentation of runtime tracing features), D8 (architectural inference)

---

### AutoGen / AG2

**D1 Cost** — 4: Open-source framework; no platform fee. Model costs only. Code execution sandbox (Docker) adds compute overhead but not token cost. Representative 3–5 agent GroupChat run: model costs in the $0.10–$0.50 range at GPT-4o-class rates. AG2 supports Ollama and local models, enabling zero-cost runs with local inference. Score 4. [MEDIUM CONFIDENCE — model cost estimate; AG2 multi-provider support from docs.ag2.ai]

**D2 Speed** — 3: AutoGen/AG2 supports parallel execution via async-first architecture (AG2 v0.4+ rearchitected to event-driven, async-first per Microsoft Research blog). GroupChat is turn-based by default — the selector picks one agent at a time — limiting real parallelism. The MemoryStream pub/sub event bus enables real-time streaming and concurrent agent operation (docs.ag2.ai 2026, confirmed via AutoGen AG2 observability search). Score 3 (supports parallelism with constraints; GroupChat default is turn-sequential; event-driven architecture enables concurrency but not always used). [MEDIUM CONFIDENCE — architecture supports parallelism; no independent timing benchmarks]

**D3 Accuracy** — 2: No published SWE-Bench Verified score for AutoGen/AG2 as a coding framework. AutoGenBench (released January 2024) provides internal benchmarking tooling but no published leaderboard results. Community reports note AutoGen's strength is code execution patterns (AssistantAgent + UserProxyAgent) but convergence on complex tasks is not guaranteed. Score 2. [LOW CONFIDENCE — no public benchmark data; AGENTIC-LANDSCAPE.md §2.3 notes "GroupChat conversations can loop unpredictably"]

**D4 Workflow Rigor** — 2: AutoGen provides multiple agents and role assignment. Captain Agent (AG2, influenced by Magentic-One) maintains a ledger of facts and progress, which is more than ad-hoc coordination. However: (a) no pre-execution interface contracts; (b) no formal failure taxonomy (Captain retries or re-delegates, but failure types are not classified); (c) no circuit breakers; (d) no file ownership matrix. Score 2 (agents share conversation/state with Captain Agent providing some progress tracking, but coordination is primarily conversational). [Evidence: AGENTIC-LANDSCAPE.md §2.3; AG2 docs docs.ag2.ai]

**D5 Observability** — 3: AG2 supports OpenTelemetry tracing (Jaeger, Honeycomb, OTEL-compatible backends) and AgentOps integration (VentureBeat article, confirmed via AG2 observability search March 2026). Python standard logging integration with agent-level event capture. No built-in real-time dashboard — users integrate third-party backends. Score 3 (structured logs with agent labels; third-party OTEL integration; no native real-time dashboard). [Evidence: docs.ag2.ai observability docs; Microsoft/AutoGen VentureBeat update]

**D6 Recovery** — 2: AG2 v0.4+ persists state to files/databases (Microsoft Research AutoGen v0.4 blog). Recovery is possible but requires manual intervention to resume from persisted state. Captain Agent re-delegates on failure but without formal failure classification. No automated circuit breaker. Score 2 (partial state persistence; manual recovery; no failure taxonomy). [Evidence: AGENTIC-LANDSCAPE.md §2.3; Microsoft Research blog — microsoft.com/en-us/research/blog/autogen-v0-4]

**D7 Setup** — 3: `pip install ag2` (or autogen-agentchat for the 0.2 path). Requires API key configuration and some framework familiarity to set up GroupChat or nested chats correctly. Docker setup required for code execution sandbox. The Microsoft-to-AG2 fork created documentation fragmentation — some docs are outdated (AGENTIC-LANDSCAPE.md §2.3). Score 3 (installation easy; Docker for code execution; documentation friction adds learning curve). [Evidence: AGENTIC-LANDSCAPE.md §2.3; ag2.ai GitHub]

**D8 Scalability** — 3: AG2 supports nested chats and distributed agent networks. MemoryStream pub/sub event bus "enables real-time streaming and makes agents safely reusable across concurrent users" (AG2 2026 docs). GroupChat default is turn-sequential; scaling to 6+ agents in GroupChat degrades due to O(n²) conversation overhead. Event-driven async architecture provides better theoretical scalability. Score 3 (architecture supports scaling but GroupChat pattern degrades; sweet spot 3–5 agents for coding tasks). [MEDIUM CONFIDENCE — architectural inference; no empirical multi-agent scaling benchmarks for AG2]

**Uncertainty flags**: D2 (parallelism depends on usage pattern), D3 (no benchmark), D6 (recovery capability from architecture docs, not community verification at scale)

---

### ChatDev / DevAll

**D1 Cost** — 4: Open-source; no platform fee. Model costs only. The waterfall pipeline runs each role in sequence, but the per-run token count is moderate — structured documents and role-specific prompts are more concise than open-ended chat. Score 4 (model costs only; comparable to MetaGPT). [MEDIUM CONFIDENCE — estimated from documented architecture]

**D2 Speed** — 2: ChatDev's original architecture is explicitly waterfall-sequential: CEO → CTO → Programmer → Reviewer in fixed order. ChatDev 2.0's RL-trained orchestrator (puppeteer) is more dynamic but still fundamentally sequential — one role acts at a time. No parallel execution model. The prior landscape survey places ChatDev at 4/10 on parallel execution (AGENTIC-LANDSCAPE.md §6). Score 2 (primarily sequential; no meaningful parallelism for multi-file coding tasks). [Evidence: AGENTIC-LANDSCAPE.md §5.5; ChatDev paper arxiv.org/html/2307.07924v5]

**D3 Accuracy** — 2: No published SWE-Bench Verified score for ChatDev. The prior landscape survey notes "Performance on SWE-Bench lags behind newer systems" (§5.5). AgileCoder (2024) explicitly outperforms ChatDev on HumanEval and MBPP. Experiential co-learning across projects is ChatDev's accuracy-relevant differentiator, but no benchmark validation of this claim is publicly available. Score 2. [MEDIUM CONFIDENCE — negative comparative evidence from AgileCoder paper; AGENTIC-LANDSCAPE.md §5.5]

**D4 Workflow Rigor** — 2: ChatDev's SOP provides role separation and a fixed sequence. The RL orchestrator (v2.0) adds dynamic sequencing. However: (a) no interface contracts between roles; (b) no formal failure taxonomy; (c) no circuit breaker; (d) no file ownership matrix. Role separation exists but is enforced only via prompt, not structural mechanism. Score 2 (multiple agents with role separation but informal coordination; "consensual process" in original design; no contracts or taxonomy). [Evidence: AGENTIC-LANDSCAPE.md §5.5; ChatDev arxiv paper]

**D5 Observability** — 2: ChatDev logs execution to a project directory (structured output files). No real-time dashboard, no trace IDs, no replay. Users inspect output files and the conversation log post-hoc. Score 2 (unstructured logging with some post-hoc attribution via role labels in conversation). [MEDIUM CONFIDENCE — from ChatDev GitHub documentation and prior survey §5.5]

**D6 Recovery** — 2: No documented recovery mechanism beyond retry. ChatDev's waterfall design means failure mid-pipeline typically requires restarting from the beginning. Experiential co-learning stores cross-project knowledge but does not function as crash recovery. Score 2 (no formal recovery; manual restart on failure). [Evidence: AGENTIC-LANDSCAPE.md §5.5 — "error recovery is primarily via retry + human review"]

**D7 Setup** — 3: `pip install chatdev` or clone + install from GitHub. Requires API key configuration and understanding of the SOP YAML configuration. Quickstart exists but customizing the waterfall SOP requires documentation study. Score 3 (installation straightforward; customization requires tutorial). [Evidence: ChatDev GitHub — github.com/OpenBMB/ChatDev]

**D8 Scalability** — 2: ChatDev's architecture is fixed-role: CEO, CTO, Programmer, Reviewer. Scaling to more parallel agents is not the design intent — the SOP is a fixed pipeline. Even with the RL orchestrator in v2.0, the agent count is bounded by the defined roles. Score 2 (architecture practical ceiling at 4–5 roles; no parallel scaling path). [Evidence: AGENTIC-LANDSCAPE.md §5.5; ChatDev paper architecture description]

**Uncertainty flags**: D3 (no SWE-Bench; comparative evidence only), D5 (observability features from GitHub docs, not independently verified)

---

### CAMEL-AI

**Note on applicability**: CAMEL is a general multi-agent research framework, not a coding-specific system. The inception prompting technique and multi-agent debate patterns were validated primarily on reasoning and research tasks, not software development. Scores reflect this gap honestly — coding-specific features (file ownership, code execution sandbox, dev-workflow integration) are absent, and this is scored as missing capability, not unfairly penalized.

**D1 Cost** — 4: Open-source framework; no platform fee. Model costs only. Peer-to-peer conversation pattern generates more back-and-forth than structured pipelines, potentially increasing token costs for equivalent output. Score 4 (model costs only; conversation overhead may push toward upper end of $0.10–$0.50 range). [MEDIUM CONFIDENCE — token overhead estimated from peer-to-peer architecture]

**D2 Speed** — 2: CAMEL's peer-to-peer conversation architecture is inherently turn-sequential — agents alternate in dialogue. No parallel execution model. The multi-agent debate pattern (one of CAMEL's primary use cases) requires multiple rounds of back-and-forth before convergence. OWL (built on CAMEL) adds multi-browser and toolkit integration, but the core framework remains sequential. Score 2 (primarily sequential; no parallel dispatch for independent tasks). [Evidence: AGENTIC-LANDSCAPE.md §5.6; camel-ai.org documentation]

**D3 Accuracy** — 2: CAMEL's OWL achieved 69.09% on the GAIA benchmark (ranked #1 among open-source, April 2025 — camel-ai/owl GitHub README). GAIA is a general assistant benchmark, not a coding benchmark. No SWE-Bench or HumanEval submission for CAMEL as a coding system. The multi-agent debate improvement "not validated for coding specifically" (AGENTIC-LANDSCAPE.md §5.6). Score 2 (strong general reasoning benchmark; no coding-specific benchmark data). [MEDIUM CONFIDENCE — GAIA score confirmed via camel-ai/owl GitHub; no coding benchmark]

**D4 Workflow Rigor** — 1: CAMEL's core is peer-to-peer conversation with inception prompting. No orchestrator, no formal role separation enforced by structure, no failure taxonomy, no file ownership, no circuit breaker, no contracts. Inception prompting establishes roles via prompt only. Convergence is not guaranteed. Score 1 (agents sharing conversation state without coordination mechanisms; failure is conversation loop or context loss). [Evidence: AGENTIC-LANDSCAPE.md §5.6 — "Peer-to-peer without orchestration leads to unpredictable outcomes on coding tasks"]

**D5 Observability** — 2: CAMEL framework logs conversations. No real-time dashboard. No trace IDs per agent. Post-hoc inspection of conversation logs. Score 2 (unstructured conversation log; no agent-level attribution beyond role labels; no mid-execution status). [MEDIUM CONFIDENCE — from camel-ai.org documentation and prior survey §5.6]

**D6 Recovery** — 1: No documented recovery mechanism. CAMEL conversations that diverge or loop do not have a recovery protocol — the run ends or requires human intervention to restart. No checkpoint, no retry taxonomy, no partial-result preservation. Score 1 (no recovery mechanism; hard failure or human restart). [Evidence: AGENTIC-LANDSCAPE.md §5.6 — "convergence is not guaranteed"; no recovery documentation found]

**D7 Setup** — 4: `pip install camel-ai` with API key configuration. CAMEL's 2025–2026 updates added MCPToolkit, TerminalToolkit, and browser support (camel-ai.org, verified via March 2026 search). The framework is well-documented with examples. First parallel run — to the extent CAMEL supports "parallel" — achievable within 1 hour for an inception-prompted two-agent conversation. Score 4 (low setup; minimal dependencies for basic use). [Evidence: camel-ai.org docs; GitHub README]

**D8 Scalability** — 2: CAMEL's architecture "simulate up to 1M agents" claim (camel-ai.org, 2026) refers to simulation research, not production task execution. In practice, peer-to-peer conversation with N agents scales as O(n²) in communication overhead. The Google/MIT research (arxiv.org/html/2512.08296v1) specifically identifies peer-to-peer topology as the worst scaling pattern. Production CAMEL deployments are typically 2-agent (inception prompting) or small group debates. Score 2 (practical ceiling 2–3 agents before communication overhead dominates). [Evidence: Google/MIT scaling paper via AGENTIC-LANDSCAPE.md §5.1; CAMEL architecture from camel-ai.org]

**Uncertainty flags**: D1 (token overhead estimated), D3 (GAIA score is not a coding benchmark), D5 (observability from docs; no community reports of debugging experience), D6 (no recovery documentation found; score 1 may be harsh but no contrary evidence available)

---

### OpenAI Agents SDK

**D1 Cost** — 4: Open-source SDK; no platform fee. Users pay OpenAI model costs. At GPT-4o rates, a 3–5 agent handoff chain producing ~15,000 tokens costs $0.075–$0.15. Integration with Codex subagents for parallel cloud execution adds Codex pricing (ChatCompletions API), which is in the $0.10–$0.50/run range for representative tasks. Score 4. [MEDIUM CONFIDENCE — model cost estimate; Codex pricing from developers.openai.com]

**D2 Speed** — 3: The Agents SDK supports handoff chains natively. Guardrails run in parallel with agent execution by default (run_in_parallel=True) for minimum latency (openai.github.io/openai-agents-python, confirmed via AGENTIC-LANDSCAPE.md §2.6). Codex subagents enable parallel cloud execution. However, the primary pattern is sequential handoff chains (Agent A transfers to Agent B), not simultaneously parallel agents. Score 3 (parallel guardrails + Codex subagent parallelism; primary handoff pattern is sequential). [Evidence: openai.github.io/openai-agents-python/handoffs; AGENTIC-LANDSCAPE.md §2.6]

**D3 Accuracy** — 2: The Agents SDK is an orchestration framework, not a coding agent. Accuracy depends on underlying model. GPT-5.3 Codex achieves 77.3% on Terminal-Bench 2.0 (confirmed via March 2026 search); however, this is Codex model performance, not Agents SDK framework performance. The SDK itself adds no accuracy-relevant mechanism beyond guardrails. Score 2 (no benchmark for the framework as a coding system; model-level performance is high but not attributable to the SDK). [LOW CONFIDENCE — framework vs. model distinction; Codex benchmark from openai.com/index/introducing-gpt-5-3-codex]

**D4 Workflow Rigor** — 2: The Agents SDK provides: (a) guardrails (input/output); (b) handoff structure; (c) tracing of all events. However: (a) no pre-execution file ownership contracts; (b) no formal failure taxonomy (retry at SDK level only); (c) guardrail coverage gap — handoff calls bypass tool guardrails (AGENTIC-LANDSCAPE.md §2.6); (d) no circuit breaker. Score 2 (structured handoff + guardrails constitutes more than ad-hoc delegation, but lacks contracts, taxonomy, and circuit breakers). [Evidence: openai.github.io/openai-agents-python; AGENTIC-LANDSCAPE.md §2.6]

**D5 Observability** — 4: Built-in comprehensive tracing: every LLM generation, tool call, handoff, guardrail event, and custom event is captured via BatchTraceProcessor to OpenAI backend (openai.github.io/openai-agents-python/tracing). Real-time status visible in OpenAI dashboard. No time-travel/replay capability equivalent to LangSmith. Score 4 (structured traces with full agent attribution and real-time dashboard; replay limited). [Evidence: openai.github.io/openai-agents-python/tracing; AGENTIC-LANDSCAPE.md §2.6]

**D6 Recovery** — 2: SDK-level retry on failure. Human oversight via approval prompts for elevated-permission actions. No formal failure taxonomy, no circuit breaker, no persistent checkpointing equivalent to LangGraph. Score 2 (single retry; no failure classification). [Evidence: AGENTIC-LANDSCAPE.md §2.6 — "Retry at the SDK level. No formal failure taxonomy"]

**D7 Setup** — 5: `pip install openai-agents` (or `openai[agents]`). One environment variable (OPENAI_API_KEY). The SDK is production-ready from day one — tracing, guardrails, and handoffs work immediately. No infrastructure dependencies. The handoff pattern is intuitive. Score 5 (near-zero setup; single command; first run within 15 minutes). [Evidence: openai.github.io/openai-agents-python quickstart; AGENTIC-LANDSCAPE.md §2.6]

**D8 Scalability** — 3: Handoff chains scale linearly — each handoff adds one step. Codex subagents enable parallel cloud execution, which provides genuine scalability for parallel tasks. However, the primary pattern (sequential handoffs) does not scale beyond the chain length. No documented ceiling for parallel Codex subagent runs, but also no published evidence of runs at 8+ agents. Score 3 (Codex subagents add parallel scaling; core handoff pattern is sequential; no empirical multi-agent scale data). [MEDIUM CONFIDENCE — architectural inference; Codex subagent docs from developers.openai.com/codex/subagents]

**Uncertainty flags**: D2 (parallel vs. sequential depends on usage pattern), D3 (model vs. framework distinction), D8 (Codex subagent scaling capability from docs; no empirical data)

---

## Summary Notes

**SWE-Bench gap**: None of the systems in this group has a published SWE-Bench Verified score as a framework. All are general-purpose orchestration layers; accuracy depends entirely on underlying models. D3 scores of 2 for all systems reflect this honestly — it is not a penalty, it is an absence of evidence. Future submissions to SWE-Bench by CrewAI Enterprise, LangGraph-based agents, or AG2 Captain would raise these scores if results were published.

**Workflow Rigor ceiling**: The highest D4 score in this group is 3 (LangGraph, MetaGPT). No general-purpose framework achieves score 4 or 5 because none implements pre-execution file ownership contracts, formal failure taxonomy with distinct handling paths, and automated circuit breakers simultaneously. MetaGPT comes closest on interface contracts (document-as-protocol) but lacks the other components.

**LangGraph observability outlier**: LangGraph + LangSmith earns the only D5 score of 5 in this group. The rubric specifically cites "LangSmith-class" as the score-5 reference; LangGraph's native LangSmith integration is the reference implementation.

**CAMEL applicability note**: CAMEL scores low across execution and rigor dimensions (D2, D4, D6). This reflects its architecture honestly — it is a research framework for peer-to-peer agent dialogue with inception prompting, not a coding-specific pipeline. Comparing it to CrewAI or LangGraph on coding workflow rigor unfairly framed; the low scores reflect missing coding-specific machinery rather than fundamental inadequacy for its intended use cases.
