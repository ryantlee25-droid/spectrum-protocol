# Protocol Evaluation: General Frameworks

> Group 2 of 3 | Evaluator: howler-frameworks | Rain: protocol-eval-0401
> Date: 2026-04-01

Scoring rubric: 1 (not addressed) to 5 (comprehensive with feedback loop).
Anti-inflation rule: claims without architectural evidence capped at 3.

---

## 6. CrewAI

**Source**: crewai.com, GitHub repository, documentation
**Type**: Python framework for multi-agent orchestration

### Scores

| # | Dimension | Score | Evidence |
|---|-----------|-------|----------|
| 1 | Task Decomposition | 4 | Explicit Task objects with descriptions, expected outputs, and agent assignments. Hierarchical process mode delegates decomposition to a manager agent. Sequential and parallel process modes. Tasks can have dependencies via `context` parameter linking outputs. |
| 2 | Conflict Prevention | 2 | No file ownership matrix. Agents can be assigned to tasks but no formal conflict prevention for shared resources. Tool-level access control exists but is not file-scoped. |
| 3 | Communication Efficiency | 4 | Agents communicate through task outputs (sequential) or delegated sub-tasks (hierarchical). Memory system enables short-term, long-term, and entity memory. Callbacks provide hooks for inter-task communication. |
| 4 | Failure Recovery | 3 | `max_retry_on_error` per agent. `human_input` flag allows human-in-the-loop intervention. Error callbacks. No typed failure classification (transient vs structural). No circuit breaker. Retry is the primary recovery mechanism. |
| 5 | Knowledge Sharing | 4 | Three-tier memory: short-term (within crew run), long-term (across runs via embeddings), entity memory (tracks entities across interactions). Knowledge sources can be attached to agents. RAG-based knowledge retrieval. |
| 6 | State Management | 3 | Crew execution state tracked during runs. `output_log_file` records execution. No checkpoint/resume system for interrupted runs. State is runtime-scoped, not durable across crashes. |
| 7 | Quality Assurance | 3 | `output_pydantic` and `output_json` enforce structured outputs. `expected_output` field defines success criteria per task. Guardrails via LLM validation. No formal quality gate pipeline (no separate reviewer/tester agents by default). |
| 8 | Scalability | 4 | Designed for multi-agent scaling. Parallel task execution. Hierarchical process for complex workflows. Can scale agent count without protocol changes. Cloud deployment options. Well-tested at production scale. |
| 9 | Mode Adaptability | 3 | Three process modes: sequential, hierarchical, and parallel. Can switch modes per crew. No automatic mode selection based on task characteristics. No cost-based mode tiers. |
| 10 | Setup Complexity | 3 | `pip install crewai`. Python-native API with decorators. Requires understanding agent/task/crew/tool abstractions. YAML-based configuration option. More setup than a CLAUDE.md file but well-documented. |
| 11 | Observability | 4 | Built-in logging with configurable verbosity. Callback system for step/task/agent events. Integration with LangSmith, AgentOps, and other observability platforms. Token usage tracking per agent. CrewAI+ dashboard for monitoring. |
| 12 | Cost Awareness | 3 | Token usage tracked per agent. `max_tokens` configurable per LLM. `max_rpm` rate limiting. CrewAI+ provides cost analytics. No built-in budget limits or automatic cost optimization through mode selection. |

**Composite Score**: 3.33 / 5.00

### Strengths
- Production-ready Python framework with strong community adoption
- Three-tier memory system (short/long/entity) is the most sophisticated knowledge sharing in this evaluation
- Scalable architecture tested at production scale
- Rich observability through integrations and callbacks

### Weaknesses
- No file ownership or conflict prevention mechanism
- No durable state management or crash recovery
- Failure recovery limited to retries without classification
- Quality assurance relies on output validation, not multi-agent review

---

## 7. LangGraph

**Source**: langchain-ai/langgraph, documentation
**Type**: Python/JS framework for stateful multi-agent graphs

### Scores

| # | Dimension | Score | Evidence |
|---|-----------|-------|----------|
| 1 | Task Decomposition | 4 | Graph-based decomposition with explicit nodes and edges. Conditional routing enables dynamic task flow. Subgraphs allow hierarchical decomposition. State schema defines what each node receives and produces. |
| 2 | Conflict Prevention | 3 | State schema acts as a contract between nodes -- each node declares its state reads/writes. Reducers handle concurrent state updates (e.g., append-only lists). No file-level ownership but state-level conflict resolution is built into the graph model. |
| 3 | Communication Efficiency | 4 | State is the communication medium -- passed between nodes via typed channels. Shared state avoids redundant context passing. Human-in-the-loop nodes for interruptions. Send API for fan-out/fan-in patterns. |
| 4 | Failure Recovery | 4 | Persistent checkpointing enables replay from any state. Thread-level state persistence across sessions. Time-travel debugging allows rolling back to previous states. Human-in-the-loop for manual intervention. No typed failure classification but checkpoint-based recovery is robust. |
| 5 | Knowledge Sharing | 3 | State persistence across graph invocations (same thread). Memory stores for cross-thread knowledge. No built-in entity tracking or lessons-learned system. Knowledge sharing is state-mediated. |
| 6 | State Management | 5 | Core strength. Persistent, versioned state with checkpointing. Thread-level isolation. State schemas with type validation. Reducers for concurrent updates. Time-travel across state versions. Multiple backend options (SQLite, Postgres, Redis). |
| 7 | Quality Assurance | 3 | Conditional edges can implement validation logic. Human-in-the-loop approval gates. No dedicated reviewer/tester agent pattern by default. Quality checks are nodes in the graph, not a separate pipeline. |
| 8 | Scalability | 4 | Graph model scales well -- add nodes and edges. Fan-out/fan-in via Send API for parallel execution. Subgraph composition for complex workflows. LangGraph Platform handles deployment scaling. Horizontal scaling through stateless node execution. |
| 9 | Mode Adaptability | 3 | Conditional routing enables dynamic graph behavior. Same graph can execute different paths based on state. No explicit mode tiers (nano/reaping/full) but graph structure provides equivalent flexibility. |
| 10 | Setup Complexity | 3 | `pip install langgraph`. Requires understanding graph concepts (nodes, edges, state, reducers). Steeper learning curve than task-based frameworks. Well-documented with tutorials and examples. |
| 11 | Observability | 4 | LangSmith integration for tracing, debugging, and monitoring. Step-level visibility in graph execution. State inspection at any checkpoint. Token usage and latency tracking. Studio UI for visual graph debugging. |
| 12 | Cost Awareness | 3 | Token tracking through LangSmith. No built-in budget limits. LLM configuration per node allows cost optimization. No automatic mode selection for cost reduction. |

**Composite Score**: 3.58 / 5.00

### Strengths
- Best-in-class state management with persistent checkpointing and time-travel
- Graph model provides natural decomposition and conflict resolution via state reducers
- Robust failure recovery through checkpoint-based replay
- Strong observability via LangSmith integration

### Weaknesses
- No file ownership concept -- state-level conflict resolution only
- No typed failure classification or circuit breakers
- Quality assurance is graph-embedded, not a separate pipeline
- Graph concepts have a steeper learning curve

---

## 8. AutoGen / AG2

**Source**: microsoft/autogen (now ag2-ai/ag2), documentation
**Type**: Python framework for multi-agent conversations

### Scores

| # | Dimension | Score | Evidence |
|---|-----------|-------|----------|
| 1 | Task Decomposition | 3 | Conversation-based decomposition -- agents negotiate tasks through chat. GroupChat with speaker selection policies. No formal manifest or ownership matrix. Decomposition emerges from agent conversation rather than being planned upfront. |
| 2 | Conflict Prevention | 2 | No file ownership mechanism. Agents in GroupChat can speak in sequence but no formal conflict prevention for shared resources. Relies on conversation coordination. |
| 3 | Communication Efficiency | 4 | Core strength -- multi-agent conversation with flexible topologies. GroupChat, nested conversations, two-agent chat patterns. Agents communicate through natural language messages. Rich conversation history management. |
| 4 | Failure Recovery | 3 | `max_consecutive_auto_reply` limits runaway agents. Human proxy for intervention. Error handling in code execution. No typed failure classification. Recovery through conversation (agents can discuss and retry). |
| 5 | Knowledge Sharing | 3 | Conversation history serves as shared knowledge. Teachable agents can learn from interactions. RAG agents for external knowledge. Knowledge sharing is conversation-mediated. No persistent cross-run learning by default. |
| 6 | State Management | 2 | Conversation state tracked during runs. No persistent checkpointing or resume capability. State is ephemeral -- lost on crash. AG2 adds some state persistence improvements. |
| 7 | Quality Assurance | 3 | Critic agent pattern documented. Code execution with Docker sandboxing validates outputs. Agents can review each other's work through conversation. No formal quality gate pipeline. |
| 8 | Scalability | 3 | GroupChat supports multiple agents. Speaker selection policies manage turn-taking. Nested conversations for complexity. Performance degrades with large groups (context window pressure). No explicit scaling limits. |
| 9 | Mode Adaptability | 3 | Flexible conversation patterns: two-agent, GroupChat, nested, sequential. Can adapt topology to task. No automatic mode selection. AG2 adds workflow patterns. |
| 10 | Setup Complexity | 3 | `pip install autogen-agentchat` (or ag2). Requires understanding agent types, conversation patterns. Good documentation and examples. Multiple agent types to learn (AssistantAgent, UserProxyAgent, GroupChat). |
| 11 | Observability | 3 | Conversation logging. Integration with observability platforms (via AG2). Agent-level message tracking. No built-in dashboard. AG2 improves observability with studio. |
| 12 | Cost Awareness | 2 | Basic token counting. No budget limits or cost optimization. Context window pressure in large GroupChats can drive costs up with no mitigation strategy. |

**Composite Score**: 2.83 / 5.00

### Strengths
- Most natural communication model -- agents converse directly
- Flexible conversation topologies (two-agent, group, nested)
- Code execution with Docker sandboxing for validation
- Large community and Microsoft backing (though now AG2)

### Weaknesses
- No file ownership or structured conflict prevention
- Ephemeral state -- no checkpoint/resume
- Conversation-based decomposition is less predictable than manifest-based
- Context window pressure limits practical scalability

---

## 9. MetaGPT

**Source**: geekan/MetaGPT, documentation
**Type**: Python framework for multi-agent software development

### Scores

| # | Dimension | Score | Evidence |
|---|-----------|-------|----------|
| 1 | Task Decomposition | 5 | Structured Output Protocol (SOP) defines role-based decomposition: ProductManager -> Architect -> ProjectManager -> Engineer -> QAEngineer. Each role produces specific artifacts (PRD, design doc, task list, code, tests). Most structured decomposition in the framework category. |
| 2 | Conflict Prevention | 3 | Roles have defined output artifacts. ProjectManager creates task assignments. No explicit file ownership matrix but role specialization reduces overlap. ActionGraph manages action dependencies. |
| 3 | Communication Efficiency | 4 | Shared message pool (environment) -- agents subscribe to relevant messages by role. Publish-subscribe pattern avoids O(n^2) communication. Structured outputs reduce ambiguity. Action dependency graph coordinates execution order. |
| 4 | Failure Recovery | 2 | Basic error handling. Incremental development mode allows iterative fixes. No typed failure classification or circuit breakers. Recovery is manual -- re-run or modify prompts. |
| 5 | Knowledge Sharing | 3 | Shared environment acts as knowledge repository. Context management across roles. Document store for artifacts. No persistent cross-project learning or entity tracking. |
| 6 | State Management | 3 | Environment state tracked during execution. Serializable state for some persistence. No checkpoint/resume system. State management is improving in newer versions. |
| 7 | Quality Assurance | 4 | Dedicated QAEngineer role generates and runs tests. Code review is part of the SOP. Design review by Architect. Multi-stage quality process mirrors real software development. No formal triple quality gate but multi-role review is built in. |
| 8 | Scalability | 3 | Fixed role pipeline limits horizontal scaling. Good for single-project teams. ActionGraph enables some parallelism. Not designed for arbitrary agent count scaling. |
| 9 | Mode Adaptability | 2 | Single SOP pipeline. Incremental mode for existing codebases. No dynamic mode selection based on task size or complexity. |
| 10 | Setup Complexity | 2 | `pip install metagpt`. Requires configuration (API keys, optional tools). SOP understanding needed. More opinionated setup than other frameworks. Some features require additional dependencies. |
| 11 | Observability | 3 | Structured output at each SOP stage provides natural visibility. Logging and artifact generation. No dedicated observability dashboard or integration. |
| 12 | Cost Awareness | 2 | Role-based model assignment possible. No budget tracking or cost optimization. Fixed pipeline means cost is proportional to SOP stages, not adaptive. |

**Composite Score**: 3.00 / 5.00

### Strengths
- Most structured task decomposition via SOP -- mirrors real software team roles
- Dedicated QA role with test generation is unique among frameworks
- Publish-subscribe communication avoids message explosion
- Produces real artifacts (PRDs, design docs) not just code

### Weaknesses
- Fixed role pipeline limits adaptability
- Weak failure recovery -- no classification or circuit breakers
- No persistent cross-project knowledge
- Setup complexity higher than other frameworks

---

## Group Summary

| System | Composite | Rank (within group) |
|--------|-----------|---------------------|
| LangGraph | 3.58 | 1 |
| CrewAI | 3.33 | 2 |
| MetaGPT | 3.00 | 3 |
| AutoGen/AG2 | 2.83 | 4 |

**Key observations:**
- LangGraph's state management (5/5) is the strongest in the entire evaluation -- checkpoint-based replay and time-travel are architecturally superior
- CrewAI's three-tier memory system is the most sophisticated knowledge sharing mechanism
- MetaGPT's SOP-based decomposition is the most structured, mimicking real software team workflows
- AutoGen's conversation-based approach is the most natural for communication but weakest for state management
- All frameworks lack file ownership concepts -- they operate at a higher abstraction level than file-system coordination
- None match Spectrum's failure recovery depth (typed classification, circuit breakers, escalation paths)
- Framework category averages higher than commercial and lower than Spectrum on coordination quality
