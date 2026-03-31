# Agentic Landscape: Multi-Agent Systems for AI Coding Assistants

**Date**: 2026-03-30
**Convoy**: convoy-eval-0330
**Author**: rider-landscape
**Version**: 1.0

---

## Executive Summary

- Multi-agent systems for AI coding have fragmented into five distinct categories: open-source orchestration frameworks, commercial IDE/cloud platforms, the Claude Code ecosystem, academic/research systems, and the Convoy custom protocol.
- Research consensus (Google/MIT, MASFT) establishes that 3-6 agents is the practical sweet spot; O(n^2) communication overhead degrades performance beyond 8; and 42%+ of failures come from specification and inter-agent coordination problems, not individual model limitations.
- No commercial platform (Cursor, Devin, Augment, Copilot Workspace, Amazon Q, Replit) implements pre-flight file ownership contracts or frozen interface specifications — the coordination guarantees that distinguish protocol-driven approaches remain absent from all commercial offerings as of March 2026.
- The most replicated academic finding is that a well-designed non-agentic pipeline can match or beat poorly coordinated multi-agent systems, validating the principle that architecture discipline matters more than agent count.
- Emerging trends in 2026 include MCP-native inter-agent communication (A2A protocol), competitive execution patterns, semantic/AST-level merge tools, and Anthropic's native Agent Teams feature entering production use.

---

## Table of Contents

1. [Taxonomy of Agentic Structures](#1-taxonomy-of-agentic-structures)
2. [Open-Source Frameworks](#2-open-source-frameworks)
   - [LangGraph](#21-langgraph)
   - [CrewAI](#22-crewai)
   - [AutoGen / AG2](#23-autogen--ag2)
   - [MetaGPT](#24-metagpt)
   - [Gas Town](#25-gas-town)
   - [OpenAI Agents SDK](#26-openai-agents-sdk)
   - [Semantic Kernel](#27-semantic-kernel)
   - [PydanticAI](#28-pydanticai)
   - [Magentic-One](#29-magentic-one)
   - [Google ADK](#210-google-adk)
3. [Commercial Platforms](#3-commercial-platforms)
   - [Cursor](#31-cursor)
   - [Devin](#32-devin)
   - [Augment Code / Intent](#33-augment-code--intent)
   - [GitHub Copilot Workspace](#34-github-copilot-workspace)
   - [Amazon Q Developer](#35-amazon-q-developer)
   - [Replit Agent](#36-replit-agent)
4. [Claude Code Ecosystem](#4-claude-code-ecosystem)
   - [Agent Teams (Anthropic Official)](#41-agent-teams-anthropic-official)
   - [ruflo](#42-ruflo)
   - [oh-my-claudecode](#43-oh-my-claudecode)
   - [agent-orchestrator (Composio)](#44-agent-orchestrator-composio)
   - [parallel-worktrees](#45-parallel-worktrees)
5. [Academic and Research Systems](#5-academic-and-research-systems)
   - [Self-Organized Agents (Google/MIT)](#51-self-organized-agents-googlemit)
   - [MASFT / MAST](#52-masft--mast)
   - [AgentCoder](#53-agentcoder)
   - [Agentless (UIUC)](#54-agentless-uiuc)
   - [ChatDev / DevAll](#55-chatdev--devall)
   - [CAMEL-AI](#56-camel-ai)
   - [AgileCoder](#57-agilecoder)
6. [Cross-Cutting Comparison (12 Dimensions)](#6-cross-cutting-comparison-12-dimensions)
7. [Current Leaders by Dimension](#7-current-leaders-by-dimension)
8. [Emerging Trends](#8-emerging-trends)
9. [Sources](#9-sources)

---

## 1. Taxonomy of Agentic Structures

Multi-agent systems for software development fall into six broad architectural patterns. Systems often blend multiple patterns but usually have a dominant one.

### 1.1 Single-Agent with Tools

One agent with access to read/write/run tools. The simplest architecture. Validated by the Agentless finding: a carefully designed single-agent pipeline can match or beat poorly coordinated multi-agent systems on SWE-Bench.

**Representative systems**: GitHub Copilot (base mode), Amazon Q, Replit Agent, early Devin

**When it wins**: sequential tasks, simple bugs, single-file changes, tasks where coordination overhead would dominate

**When it fails**: genuinely parallel independent work, tasks requiring genuine reviewer independence from author

### 1.2 Orchestrator-Workers (Hub and Spoke)

A central coordinator decomposes a task and delegates sub-tasks to specialized workers. Workers report results back to the coordinator, which synthesizes and resolves conflicts. The dominant pattern recommended by both Anthropic and OpenAI.

**Representative systems**: Devin 2.0 (Managed Devins), Augment Code Intent (Coordinator/Specialist/Verifier), OpenAI Agents SDK (handoff chains), MetaGPT

**When it wins**: tasks with identifiable sub-components, when role specialization matters (reviewer ≠ author)

**When it fails**: when the coordinator becomes a bottleneck; when sub-task boundaries are unclear

### 1.3 Peer-to-Peer / Group Chat

Agents coordinate directly via shared conversation. No single coordinator. The group chat pattern (from AutoGen) allows any agent to message any other agent. Highest communication overhead.

**Representative systems**: AutoGen/AG2 GroupChat, CAMEL-AI debate, early MetaGPT

**When it wins**: open-ended research/brainstorming tasks; when optimal decomposition is unknown upfront

**When it fails**: coding tasks with clear structure; when conversation loops without convergence; when you need auditability

### 1.4 DAG-Based Parallel Dispatch

Tasks are laid out as a directed acyclic graph. Agents are dispatched as their dependencies are satisfied. No peer-to-peer messaging during execution; coordination is pre-planned. Minimizes runtime coordination overhead.

**Representative systems**: Convoy Protocol, CodeR (research), CrewAI Flows (partially), Gas Town Convoys

**When it wins**: 3-8 agents on genuinely independent tasks with known interfaces; when conflict prevention is a priority

**When it fails**: when task graph is unknown upfront; when tasks are highly interdependent; for teams of 1-2 agents (overhead dominates)

### 1.5 State Machine / Graph-Based

The workflow is encoded as a formal state machine or computational graph. Nodes are functions/agents; edges are transitions. State is persisted after every node. Enables time-travel debugging, mid-execution branching, human-in-the-loop pauses.

**Representative systems**: LangGraph, Semantic Kernel Process Framework, Google ADK

**When it wins**: long-running workflows that need replay/recovery; compliance-critical applications; when you need to audit every state transition

**When it fails**: when the overhead of defining state schemas and graph topology is larger than the problem

### 1.6 Swarm / Pull-Based

Workers pull from a shared work queue. No fixed topology. Agent count scales dynamically with queue depth. Designed for 10-30+ agents on heterogeneous tasks.

**Representative systems**: Gas Town (full mode), OpenAI Swarm (educational), some Cursor configurations

**When it wins**: enterprise-scale autonomous work; when tasks are highly heterogeneous and arrive dynamically

**When it fails**: when task interdependencies are high; when you need guarantees about which agent handles which file

---

## 2. Open-Source Frameworks

### 2.1 LangGraph

**Stars**: ~8,000 (GitHub)
**Origin**: LangChain team (Harrison Chase et al.), 2024
**Primary use case**: Stateful multi-agent workflows with checkpointing and time-travel debugging

**Architecture**: Everything is a `StateGraph`. Nodes are Python functions that receive state and return updates. Edges are transitions — conditional or unconditional. State is typed (TypedDict or Pydantic), immutable per step, and persisted after every node via pluggable checkpointers (MemorySaver, SqliteSaver, PostgresSaver).

The key architectural insight: LangGraph treats orchestration as a computer science problem, not a prompting problem. State transitions are explicit and inspectable. The framework does not try to hide the complexity of multi-agent coordination; it gives you formal tools to manage it.

**Routing/orchestration mechanism**: Explicit conditional edges. After each node, a router function determines the next node (or END). Sub-graphs can be composed as single nodes in a parent graph, enabling hierarchical orchestration.

**State management**: Persistent checkpointing after every node. Thread-level state scopes execution within a run. Store-level state is cross-thread, persistent entity memory. Time-travel debugging: step backwards through any execution and replay with different inputs.

**Error recovery**: LangGraph Cloud (hosted) provides retry policies and monitoring. In the open-source version, recovery is manual — you resume from a checkpoint. Human-in-the-loop patterns are built in: pause the graph at any node, wait for human input, resume. This is the strongest recovery model in the open-source framework category.

**Strengths**:
- Only framework where every state transition is formally defined and inspectable
- Time-travel debugging is a genuine differentiator — replay any execution from any checkpoint
- Sub-graph composition enables clean hierarchical orchestration
- LangSmith integration provides production-grade tracing and observability

**Limitations**:
- Requires upfront state schema definition — more work than role-based frameworks for ad-hoc tasks
- Debugging complex graphs requires understanding the graph topology, not just reading logs
- No built-in file conflict prevention for coding-specific use cases
- LangGraph Cloud (hosted execution with monitoring) is commercial; open-source version requires your own infrastructure for production persistence

---

### 2.2 CrewAI

**Stars**: ~44,600 (GitHub, March 2026)
**Origin**: João Moura, independent (2024), now CrewAI Inc.
**Primary use case**: Role-based autonomous agent crews with enterprise workflow orchestration

**Architecture**: Two distinct layers — **Crews** and **Flows**.

**Crews** are autonomous teams with true agency. Each agent has a `role`, `goal`, `backstory`, and access to tools. Agents decide when to delegate, when to ask questions, and how to approach tasks. Three process types: sequential (agents run in order), hierarchical (a manager agent delegates), and consensual (agents vote). Crews handle unstructured, high-agency work.

**Flows** are the enterprise/production layer — event-driven workflow orchestration with granular control, secure state management, and clean Python integration. Flows handle structured, deterministic pipelines.

**Memory system**: Three-tier memory is CrewAI's most validated innovation: short-term (RAG over current session), long-term (cross-session SQLite), and entity memory (knowledge about specific people, places, concepts encountered). The framework automatically queries all three tiers at each agent turn.

**Routing/orchestration**: In hierarchical Crews, a manager LLM determines delegation. In Flows, event-driven routing with `@listen` and `@router` decorators. Flows can embed Crews for hybrid pipelines (deterministic orchestration + autonomous execution).

**Error recovery**: Task retry with configurable max attempts. Error output fed back into next attempt. No formal failure taxonomy or circuit breaker — recovery is at the retry level, not classified by failure type.

**Strengths**:
- Most ergonomic role-assignment API in the open-source space
- Three-tier memory is empirically validated and genuinely useful
- 44k stars + 450M monthly workflows = largest adoption in open-source framework category
- Enterprise customers include DocuSign, PwC, IBM, PepsiCo — real production deployments
- 2-3x faster execution than comparable frameworks in benchmarks (company-reported)

**Limitations**:
- Autonomous agents can be unpredictable in ways that surprise users
- Memory system adds latency — triple-querying per turn has overhead
- No file ownership contracts or pre-flight conflict prevention
- "Consensual process" (agent voting) is novel but unproven for coding tasks
- Documentation quality varies significantly between Crew and Flow layers

---

### 2.3 AutoGen / AG2

**Stars**: ~35,000 (GitHub, Microsoft/AutoGen), AG2 is a community fork
**Origin**: Microsoft Research (2023); AG2 is a community-maintained fork following Microsoft's rewrite to AutoGen 0.4
**Primary use case**: Conversation-as-computation; code-execution-heavy workflows

**Architecture**: The core abstraction is **conversation-as-computation** — computation is structured as conversations between `ConversableAgent` objects. The novel claim: an agent's "thinking" can itself be a multi-agent conversation (nested chats), enabling recursive decomposition without explicit orchestration code.

AG2 (the community fork, v0.8+) rearchitected from the v0.2 pattern-library approach to an event-driven, async-first execution model with pluggable orchestration strategies. GroupChat is the primary coordination pattern: multiple agents in a shared conversation, with a selector (round-robin, LLM-based, or custom function) determining who speaks next.

**Four conversation patterns**: Two-Agent Chat (simplest, most reliable), Sequential Chat (chain of agents), Group Chat (N agents, selector-mediated), Nested Chat (package a workflow as a single agent for reuse).

**Code execution sandbox**: The best built-in code execution model in the open-source category. Docker-based isolation, configurable timeouts, output fed back into conversation. The `AssistantAgent` + `UserProxyAgent` pattern remains the most widely copied pattern for code generation + execution.

**Routing/orchestration**: In GroupChat, the `GroupChatManager` calls a selector at each turn. The selector can be a simple round-robin, an LLM deciding who should speak, or custom Python logic. No DAG — topology is determined dynamically.

**State management**: v0.4+ persists state to files/databases. Less structured than LangGraph's checkpointing — recovery is possible but not the primary design goal.

**Error recovery**: AG2's Captain Agent (influenced by Magentic-One) maintains a ledger of facts, progress, and outstanding tasks. On failure, the Captain retries or re-delegates. No formal failure taxonomy.

**Strengths**:
- Nested chats are genuinely novel — conversation-as-computation enables recursive workflows without orchestration boilerplate
- Code execution sandbox is the best in the open-source framework category
- Largest community after CrewAI — extensive examples, plugins, integrations
- Captain Agent / Magentic pattern brings ledger-based orchestration to the framework

**Limitations**:
- GroupChat conversations can loop unpredictably — convergence is not guaranteed
- Conversation-as-computation makes debugging harder than explicit state machines
- The Microsoft-to-AG2 fork created an ecosystem split; some documentation is outdated
- No pre-flight coordination mechanism; conflicts discovered at execution time

---

### 2.4 MetaGPT

**Stars**: ~47,000 (GitHub, FoundationAgents/MetaGPT)
**Origin**: FoundationAgents team, Tsinghua University (2023)
**Primary use case**: Simulating a software company with structured document pipelines

**Architecture**: The core insight is `Code = SOP(Team)`. MetaGPT encodes software development as a Standard Operating Procedure: each role (Product Manager, Architect, Engineer, QA) produces structured documents (PRD, design doc, API spec, code) that become the coordination mechanism for downstream roles.

Documents are not just outputs — they are the protocol. When the Architect produces a `SystemDesign.md`, the Engineer reads it as their specification. This is the closest open-source analog to the "interface-first contracts" pattern, but implemented as documents rather than typed interfaces.

**Pub/sub message bus**: MetaGPT 2.0 added an asynchronous pub/sub architecture. Roles subscribe to message types (e.g., Engineer subscribes to `SystemDesign` messages). When an upstream role publishes a document, all subscribed downstream roles are notified. This enables genuine parallelism within role boundaries.

**Routing/orchestration**: Role-based with SOP enforcement. The Team manager coordinates which roles run in which order. The SOP is configurable but defaults to the waterfall-style software company simulation.

**State management**: Documents on disk serve as persistent state. If execution is interrupted, roles can re-read existing documents and continue. Less structured than LangGraph but more reliable than conversation-only systems.

**Error recovery**: Limited. If an agent produces a malformed document, downstream roles may fail silently. MetaGPT 2.0 added some validation, but error recovery is primarily via retry + human review.

**Strengths**:
- Structured document outputs are genuinely useful — the PRD, design doc, and test plan are real artifacts
- Pub/sub architecture enables parallel execution within defined role boundaries
- One of the most-studied systems in the academic literature
- The "software company simulation" framing is pedagogically powerful

**Limitations**:
- Waterfall SOP is too rigid for real development (requirements change mid-execution)
- Documents as protocol works for structured software but breaks down for exploratory or maintenance work
- No file ownership prevention — multiple Engineer agents can write to the same files
- 47k stars but many are from early 2023 hype; active user base is smaller
- Performance on real-world benchmarks (SWE-Bench) lags behind newer systems

---

### 2.5 Gas Town

**Stars**: ~13,300 (GitHub, steveyegge/gastown)
**Origin**: Steve Yegge (former Googler, Sourcegraph), January 2026
**Primary use case**: Enterprise-scale multi-agent workspace for 20-30+ concurrent Claude Code agents

**Architecture**: Gas Town is built around three core primitives: **Hooks** (persistent work queues per agent), **Beads** (persistent agent identities in Git), and the **GUPP principle** (Go Until a Problem Presents). Every agent has a persistent identity stored in Git and a Hook — a work queue. When work appears on an agent's Hook, GUPP dictates that the agent must run it immediately without waiting for external instruction.

The **Town** is the coordination layer: a Mayor coordinates all workers across multiple Rigs (IDE instances). The **Deacon** is a town-level health monitor. Three-tier watchdog: Deacon detects stalls and issues escalating interventions.

**Convoys** in Gas Town are lightweight: a list of tasks assigned to a group of workers, with pull-based dispatch (workers claim tasks from the queue). This differs from Convoy Protocol's push-based DAG dispatch with pre-flight contracts.

**GUPP principle**: The heartbeat of autonomous operation. Agents do not wait for permission — they continuously execute available work. This maximizes throughput but reduces safety checkpoints.

**Routing/orchestration**: Pull-based work queues. Workers claim tasks as they become available. No DAG — task ordering is emergent, not pre-planned. Smart skip logic allows agents to skip blocked tasks and continue with unblocked ones.

**State management**: Git-backed. Every action generates provenance records. Persistent hooks survive agent restarts. Designed from the ground up for crash recovery at scale.

**Error recovery**: GUPP + stall detection + 3-tier watchdog. Autonomous recovery by default — agents execute immediately rather than waiting for human intervention. Less classified than formal failure taxonomies but more autonomous.

**Strengths**:
- Designed for 20-30+ concurrent agents — the only open-source system in this scale class
- Provenance records on every action enable rich audit trails
- GUPP principle enables maximum throughput for autonomous workloads
- Influenced Anthropic's Agent Teams design; Anthropic is reportedly productizing Gas Town patterns

**Limitations**:
- Heavy infrastructure requirements: Go daemon, multi-repo workspace, tmux coordination
- GUPP's aggressive autonomy is risky for teams without strong codebase understanding
- No pre-flight conflict prevention — file conflicts discovered at runtime via actor attribution
- No formal contract mechanism between agents
- Primarily designed for experienced teams; high operational complexity for individuals

---

### 2.6 OpenAI Agents SDK

**Stars**: ~10,000+ (GitHub, openai/openai-agents-python)
**Origin**: OpenAI (March 2025, production release 2025-2026)
**Primary use case**: Production-grade handoff chains with built-in guardrails and tracing

**Architecture**: The production successor to OpenAI Swarm (~300 lines, educational). The Agents SDK formalizes the **handoff pattern**: agents are represented as tools to the LLM. When an agent calls `transfer_to_<AgentName>`, the SDK executes a structured handoff, passing context and control to the designated agent.

**Guardrails**: Input guardrails run before agent execution (can block); output guardrails run after (can transform or reject). Guardrails run in parallel with agent execution by default (run_in_parallel=True) for minimum latency. Note: guardrails do not apply to the handoff call itself — only to tool invocations.

**Tracing**: Built-in, comprehensive. Every LLM generation, tool call, handoff, guardrail event, and custom event is captured. A `BatchTraceProcessor` exports to the OpenAI backend in batches. Production-grade from day one.

**Routing/orchestration**: Handoff chains are the primary pattern — LLM decides to transfer to another agent. Can also integrate with Codex subagents for parallel cloud execution.

**State management**: Thread/run state. No persistent checkpointing equivalent to LangGraph.

**Error recovery**: Retry at the SDK level. No formal failure taxonomy. Human oversight via approval prompts for elevated-permission actions.

**Strengths**:
- Guardrails + tracing built in from the start — not bolted on
- Seamless integration with OpenAI's ecosystem (Codex, Assistants API, TOML agent definitions)
- The handoff pattern is the most widely copied pattern in the field (Swarm popularized it)
- Production-ready: used in OpenAI's own products

**Limitations**:
- Ecosystem lock-in: optimized for OpenAI models and infrastructure
- No file ownership contracts or pre-flight planning
- Guardrail coverage gaps: handoff calls bypass tool guardrails
- Less flexible than LangGraph for complex graph topologies

---

### 2.7 Semantic Kernel

**Stars**: ~24,000 (GitHub, microsoft/semantic-kernel)
**Origin**: Microsoft (2023), now integrated with AutoGen 0.4 direction
**Primary use case**: Enterprise AI orchestration for .NET/Java/Python with Azure integration

**Architecture**: Plugin-based. AI agents are composed of "skills" (now called plugins) that encapsulate functions callable by the planner. The **Process Framework** adds durable state machine support for long-running workflows.

Microsoft's strategic direction in 2026: Semantic Kernel becomes the enterprise integration layer, AutoGen handles multi-agent conversation, and they share the same runtime. **A2A protocol integration** is a key differentiator — Semantic Kernel agents can communicate with agents built in LangGraph, CrewAI, Google ADK, or any A2A-compliant framework.

**Routing/orchestration**: Multiple planner types: sequential planner (fixed order), step-wise planner (iterative, Thought/Action/Observation), and Magentic orchestration (dynamic multi-agent coordination via ledger).

**State management**: Process Framework provides durable state machines with persistent state. Enterprise-grade: supports Azure Service Bus, Dapr for distributed coordination.

**Error recovery**: Process Framework handles retries and compensating transactions at the workflow level. Enterprise-grade reliability, not ad-hoc retry logic.

**Strengths**:
- Only framework with enterprise-grade .NET support (dominant in large organizations)
- A2A protocol integration enables cross-framework agent communication
- Process Framework brings formal state machine durable execution to agents
- Azure integration is unmatched for Microsoft-stack enterprises

**Limitations**:
- High ceremony: plugin definitions, planner configuration, and Process Framework setup have significant overhead
- Python SDK is secondary to .NET; some features arrive in C# months before Python
- Less suited for ad-hoc multi-agent coding tasks than CrewAI or LangGraph
- The AutoGen/SK integration is still in progress; architecture is in flux

---

### 2.8 PydanticAI

**Stars**: ~10,000 (GitHub)
**Origin**: Pydantic team (Samuel Colvin et al.), 2024
**Primary use case**: Type-safe, production-reliable agent development for Python

**Architecture**: Code-first, rejects complex abstractions ("Chains", "Crews") in favor of standard Python with type hints. An agent is a Python function with a typed return value, typed dependencies, and typed tool outputs. The framework guarantees that if the code compiles without type errors, the agent's inputs and outputs conform to schema.

**Dependency injection**: The most distinctive feature. Agents declare their dependencies (database clients, API keys, configuration) as typed parameters. This makes agents testable in isolation — inject a mock database for tests, real database for production.

**Model-agnostic**: Supports OpenAI, Anthropic, Gemini, Ollama, and others via a unified interface. First-class streaming support with typed partial outputs.

**Routing/orchestration**: No built-in multi-agent orchestration; agents are composed in Python. Integration with LangGraph or other frameworks for complex orchestration.

**State management**: No built-in persistence; delegates to the application layer.

**Strengths**:
- Type safety is the primary differentiator — no other framework enforces typed inputs/outputs/state this rigorously
- Testing story is excellent: dependency injection makes mocking natural
- Minimal abstraction overhead — feels like writing Python, not writing framework code
- Growing fast among production Python shops that care about reliability over velocity

**Limitations**:
- No built-in multi-agent orchestration — you must compose with another framework or Python
- No memory system, checkpointing, or cross-session learning built in
- Smaller ecosystem than CrewAI or AutoGen
- "Code-first" philosophy means less tooling for non-developer stakeholders

---

### 2.9 Magentic-One

**Stars**: N/A (Microsoft Research paper + Semantic Kernel integration, not standalone repo)
**Origin**: Microsoft Research (2024), now integrated into Semantic Kernel and AG2
**Primary use case**: General-purpose multi-agent pattern for complex open-ended tasks

**Architecture**: An orchestrator (the "Magentic") maintains an explicit **ledger**: a running record of facts established, tasks completed, and outstanding questions. At each turn, the Magentic reads the ledger and decides which agent should act next, what they should do, and what the success criterion is.

The ledger pattern forces explicit reasoning about progress — the Magentic cannot just "delegate and forget." It must maintain a consistent world model.

**Specialist agents**: WebSurfer (browser control), FileSurfer (file system), Coder (code execution), ComputerTerminal (shell access). These are general-purpose, not coding-specific.

**Routing/orchestration**: LLM-based selector that reads the ledger. The Magentic decides dynamically which agent should act next based on task state. No fixed topology.

**Error recovery**: Ledger-based — the Magentic sees when a task fails (outcome not in ledger) and can re-delegate or try a different approach.

**Strengths**:
- Ledger pattern enforces explicit progress tracking — hard to "lose state"
- Influenced AG2's Captain Agent and Semantic Kernel's orchestration; widely adopted as a pattern
- General-purpose: works for web research, file manipulation, coding, and more

**Limitations**:
- LLM calls for every routing decision add latency and cost
- Not coding-specific; missing file ownership and contract mechanisms
- Integration work required to use in production; not a standalone product
- Ledger quality depends on LLM reasoning quality at each step

---

### 2.10 Google ADK

**Stars**: ~8,000 (GitHub, google/adk-python)
**Origin**: Google (2025-2026)
**Primary use case**: Gemini-native agent development with Google Cloud integration

**Architecture**: Declarative agent definitions with a built-in runner abstraction. Agents have tools, instructions, and sub-agents. The `AgentRunner` handles session management, streaming, and tracing. First-class multimodal support: agents can natively process images, audio, and video alongside text.

**A2A protocol**: Google ADK is A2A-native. Agents built with ADK can communicate with agents built in LangGraph, CrewAI, or Semantic Kernel via the A2A protocol. This is Google's push to make the multi-agent ecosystem interoperable.

**Routing/orchestration**: Hierarchical by default. Coordinator agents delegate to specialist sub-agents. Sub-agents can have their own sub-agents. The runner handles async execution and result aggregation.

**State management**: Session-based with Google Cloud Firestore integration for persistence. Built-in evaluation tooling for testing agent behavior.

**Error recovery**: Retry policies at the runner level. Cloud-native reliability (Cloud Run, Cloud Functions for deployment).

**Strengths**:
- Native Gemini integration with multimodal capabilities
- A2A protocol support for cross-framework interoperability
- Google Cloud services integration (BigQuery, Vertex AI, Firestore) is first-class
- Built-in evaluation tooling — not common in the framework space

**Limitations**:
- Ecosystem lock-in: strongest when using Google models and Google Cloud
- Less adoption than LangGraph or CrewAI; smaller community
- A2A protocol is still early (2026); integration quality with non-Google frameworks varies
- No built-in file ownership or coding-specific coordination mechanisms

---

## 3. Commercial Platforms

### 3.1 Cursor

**Product version**: Cursor 2.0 (February 2026)
**User base**: Millions of developers; primary commercial IDE for AI-assisted coding
**Architecture pattern**: IDE-native agent composition with optional cloud background agents

**Architecture**: Cursor 2.0 is "agent-first" — the default mode is an agent that can edit files, run commands, and use browser tools, not an autocomplete. Background agents run on cloud VMs with full development environments. Up to 8 agents work in parallel using git worktree isolation — each agent gets its own worktree on its own branch.

**Competitive execution**: Cursor's most distinctive feature. You can assign the same prompt to multiple models simultaneously and compare results side by side. Alternatively, one model creates a plan and a different model builds it. No other commercial platform offers this pattern.

**BugBot Autofix**: Automated code review that can generate fix PRs directly. The review → fix → review loop is native.

**Routing/orchestration**: No coordination protocol between parallel agents. Each agent operates independently in its worktree. Conflicts are discovered at merge time. No pre-flight planning.

**State management**: Session-only. No cross-session persistence. No recovery protocol if an agent dies.

**Error recovery**: RL-trained model has implicit retry behavior. No explicit recovery protocol or failure classification.

**Strengths**:
- Zero-overhead: click to run agents, no protocol files, no pre-planning required
- Competitive execution is genuinely novel for coding assistants
- Browser tool integration enables agents to test web apps directly
- IDE-native: no context-switching between tool and editor

**Limitations**:
- No pre-flight conflict prevention — ownership collisions discovered at merge
- No shared contracts between parallel agents — each interprets task independently
- No cross-session learning or lessons mechanism
- Competitive execution doubles cost per task; no cost control mechanism
- Background agents are cloud-only (not available for air-gapped environments)

---

### 3.2 Devin

**Product version**: Devin 2.2 (as of March 2026)
**Company**: Cognition AI (acquired Windsurf)
**Pricing**: $20/month (ACU-based), down from original $500/month
**Architecture pattern**: Cloud VM sandbox with Managed Devins (coordinator/worker)

**Architecture**: Each Devin instance runs in a full cloud VM with browser, terminal, and editor access. Devin 2.0 introduced **Managed Devins**: the main Devin session acts as coordinator, spawning child sessions — each a full Devin in their own isolated VM — for parallel work. The coordinator scopes work, monitors progress, resolves conflicts, and compiles results.

**Repository indexing**: Devin automatically indexes repositories every few hours, generating architecture wikis with diagrams, source links, and documentation. Devin Search enables natural-language queries against the indexed codebase.

**Performance**: Cognition claims 83% more junior-level development tasks per ACU compared to Devin 1.0. Internal benchmarks, not independently verified.

**Routing/orchestration**: Coordinator-based. The main Devin decides task breakdown and delegation. No external coordination file or contract mechanism — decomposition is entirely implicit in the LLM's reasoning.

**State management**: Cloud VM state persists across sessions. Plans are retained and can be refined on failure. No structured HOOK.md equivalent.

**Error recovery**: Plan refinement on failure. Coordinator re-scopes tasks. No formal failure taxonomy or circuit breaker.

**Strengths**:
- Full VM (browser + shell + editor) is a genuine advantage for tasks requiring environment manipulation
- Managed Devins pattern enables true parallel execution with each subagent in an isolated VM
- Repository indexing + wiki generation adds persistent codebase understanding
- Asynchronous workflow: submit task, review PR the next morning

**Limitations**:
- Black-box coordination: no visibility into how decomposition decisions are made
- No pre-flight conflict prevention — isolation prevents runtime conflicts but merge conflicts still occur
- No frozen contract between Managed Devins — each interprets shared interfaces independently
- Cloud-only: no on-premises option
- Internal benchmarks are unaudited; independent SWE-Bench performance is not top-tier

---

### 3.3 Augment Code / Intent

**Product**: Intent (multi-agent workspace product by Augment Code)
**Architecture pattern**: Coordinator/Specialist/Verifier with deep semantic context engine

**Architecture**: Intent's architecture has three explicit roles. A **Coordinator** decomposes specs into tasks and manages execution waves without writing code directly. **Specialists** implement tasks in isolated git worktrees, choosing from built-in personas (Investigate, Implement, Verify, Critique, Debug, Code Review). A **Verifier** continuously checks results against the shared spec and acceptance criteria.

**Context Engine**: The primary differentiator. Processes 400,000+ files through semantic dependency analysis. Every agent (Coordinator, Specialists, Verifier) shares the same deep codebase understanding. Maintains specification-to-implementation traceability across large monorepos.

**Living specs**: Intent uses an evolving spec as the system of record. As specialists complete work, the spec is updated. This differs from frozen contracts — the spec can change mid-execution. (MASFT research suggests this increases mid-execution drift risk, but Augment argues continuous verification mitigates it.)

**Routing/orchestration**: Coordinator decomposes spec into tasks and dispatches to Specialists in waves. Sequential merge strategy — Specialists work in parallel, but results are merged in sequence by the Coordinator. This reduces merge conflicts compared to fully parallel merges.

**State management**: Living specs + Augment's context memory. Specs persist and update as work progresses. No per-task crash recovery file.

**Error recovery**: Coordinator identifies failure type and re-assigns to a different specialist or retries with a modified approach. No circuit breaker.

**Strengths**:
- 400,000+ file context engine is the largest in any commercial platform
- Continuous Verifier agent is a genuine quality gate absent from most systems
- Sequential merge strategy is validated — catches integration issues early
- Spec-driven development with natural language is accessible to non-specialist developers

**Limitations**:
- Living specs can drift mid-execution in unpredictable ways
- "Context Engine" specifics are proprietary; scalability claims are unaudited
- Practical ceiling is 3-4 parallel specialists with one human reviewer (per Augment's own research)
- No formal failure taxonomy or circuit breaker mechanism

---

### 3.4 GitHub Copilot Workspace

**Product version**: GA to all paid Copilot users (early 2026)
**Architecture pattern**: Auditable plan-implement-review pipeline (single orchestration thread)

**Architecture**: Copilot Workspace is not a multi-agent system — it is a single-agent pipeline with explicit, editable stages: specification → plan → implementation → review → PR. The design philosophy is maximum auditability: users can read and edit every artifact at every stage before moving forward.

**Code Review Agent** (March 2026): A new agentic code review that gathers full project context before analyzing PRs. When review identifies issues, it passes suggestions directly to the coding agent, which generates fix PRs automatically. Review → fix → review creates a closed loop.

**MCP support** (2026): Extensions ecosystem via MCP enables third-party tool integration.

**Routing/orchestration**: Sequential pipeline. One agent runs each stage. No parallelism.

**State management**: Plan and implementation artifacts persist across sessions. The full pipeline history is auditable in the Workspace interface.

**Error recovery**: Human can intervene at any stage, edit the plan, and re-run from any step.

**Strengths**:
- Most auditable system in the commercial category — every stage is human-readable and editable
- Seamless GitHub integration: PRs, issues, and code review are native
- Low barrier to entry: available to all paid GitHub Copilot users
- Closed-loop code review → fix pipeline is well-executed

**Limitations**:
- No true multi-agent parallelism
- Workspace is scoped to single-repository tasks; cross-repo work is limited
- Review agent's agentic architecture is recent (March 2026); maturity is unproven
- "Plan-before-build" workflow is slower than iterative approaches for exploratory work

---

### 3.5 Amazon Q Developer

**Architecture pattern**: Specialized agents per development task within AWS ecosystem

**Architecture**: Amazon Q Developer has evolved from a code completion tool to a multi-modal agent platform. Specialized sub-agents handle distinct tasks: `/dev` for feature implementation, `/test` for test generation (Java and Python), `/review` for SAST + secrets detection + IaC analysis, `/transform` for Java modernization. Each sub-agent is independently invokable.

**AWS integration**: Q is fine-tuned on 20+ years of AWS documentation, best practices, and internal code. It can answer account-level questions ("List my Lambda functions"), generate CLI commands, and reason across AWS service interactions. No other coding assistant has comparable depth on AWS infrastructure.

**Custom agents**: Users define agents by combining specific tools, prompts, context, and permissions. MCP integration allows querying database schemas and automating infrastructure deployments.

**Routing/orchestration**: Task-type routing: the user invokes the appropriate sub-agent by name (/dev, /test, /review). No automatic decomposition or multi-agent orchestration — the user selects which agent to invoke.

**State management**: IDE-session level. No cross-session persistence beyond what's in the repository.

**Error recovery**: Retry at the user's discretion. No formal recovery protocol.

**Strengths**:
- Deepest AWS integration of any coding assistant — unmatched for AWS-centric teams
- Security-focused sub-agents (/review) are production-grade and run SAST natively
- MCP integration enables custom tool integration
- Fine-tuned on vast AWS internal knowledge not available to other systems

**Limitations**:
- Not competitive outside the AWS ecosystem
- No multi-agent parallelism or coordination protocol
- Sub-agents are siloed — /dev does not coordinate with /test by default
- Less capable than Cursor or Devin on general coding tasks without AWS context

---

### 3.6 Replit Agent

**Architecture pattern**: Cloud-native unified environment (browser-based IDE + agent + deployment)

**Architecture**: Replit's key architectural claim is that development and deployment are the same environment. Code runs in Linux containers; agents can edit files, run tests, and deploy to production in the same session. Agent 3 (current) adds Azure partnership for autoscale infrastructure, SOC 2 compliance, and GitHub sync.

**Unique value proposition**: Idea-to-deployed-app with minimum friction. Everything runs in the cloud — databases (PostgreSQL, SQLite), deployment infrastructure (SSL, scaling), and the development environment itself. No local tooling required.

**Routing/orchestration**: Single-agent. Terminal Agents can execute commands, run tests, alter files, and perform deployments. No multi-agent coordination.

**State management**: Cloud container state persists. Always-on deployments eliminate cold start latency. Database queries execute in under 50ms on built-in PostgreSQL.

**Error recovery**: Human-in-the-loop at the terminal. No formal recovery protocol.

**Strengths**:
- Fastest path from idea to deployed app of any platform
- Genuinely unified environment: coding, testing, and deployment in one browser tab
- Built-in database and infrastructure removes a class of setup problems
- Accessible to non-developers: no local tooling, no CLI knowledge required

**Limitations**:
- Not suitable for large codebases or enterprise monorepos
- Single-agent: no parallel multi-agent coordination
- Cloud-only: not viable for air-gapped or security-sensitive environments
- Agent autonomy is limited compared to Devin or Cursor for complex refactors

---

## 4. Claude Code Ecosystem

### 4.1 Agent Teams (Anthropic Official)

**Version**: Available in Claude Code v2.1.32+ (research preview, February 2026)
**Activation**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (settings or environment)
**Architecture pattern**: Lead + teammates, each with own context window and git worktree

**Architecture**: Agent Teams was discovered in January 2026 when a developer found "TeammateTool" — a fully implemented but feature-flagged multi-agent system in the Claude Code CLI binary. Anthropic officially launched it as a research preview two weeks later with Opus 4.6 (the model this document is authored on).

The **TeammateTool** exposes 13 operations organized into four categories: team lifecycle (create, destroy team), membership (add, remove teammates), coordination (assign task, check status, send message), and shutdown. The Lead agent orchestrates; teammates work independently in isolated git worktrees with their own context windows.

Teammates merge code only when tests pass. Direct inter-agent messaging is available (not just mailbox-at-completion) — a teammate can ask another "what type did you export?" mid-execution.

**Routing/orchestration**: Lead-directed. The Lead decides task assignment and monitors progress. No external MANIFEST.md or CONTRACT.md required — coordination is handled via TeammateTool calls.

**State management**: Each teammate's context window is isolated. Git worktrees provide filesystem isolation. No structured per-teammate recovery file (unlike Convoy's HOOK.md).

**Error recovery**: Not formally documented in the research preview. Likely follows single-agent retry behavior per teammate.

**Strengths**:
- Native to Claude Code — no external tooling, no worktree setup scripts
- Direct inter-agent messaging during execution (not just at completion)
- 13 operations cover the full coordination lifecycle
- The Lead can monitor progress and re-assign tasks without a separate Mayor agent

**Limitations**:
- Still in research preview (March 2026) — production reliability unknown
- No pre-flight conflict prevention or file ownership matrix
- No frozen contract mechanism between teammates
- Opus 4.6 required for lead — cost implications for large teams
- Error recovery protocol not yet formalized

---

### 4.2 ruflo

**Stars**: 6,000+ commits, v3.5 (GitHub, ruvnet/ruflo)
**Architecture pattern**: Enterprise orchestration with swarm intelligence and RAG integration

**Architecture**: ruflo transforms Claude Code into a multi-agent swarm orchestration platform. Features enterprise-grade architecture with distributed swarm intelligence, RAG integration, and native Claude Code / Codex integration. The framework supports deploying intelligent multi-agent swarms for complex, coordinated workflows.

**Swarm intelligence**: ruflo implements swarm-style task distribution where agents can self-organize around available work. RAG integration enables agents to query project knowledge bases during execution.

**Native Codex integration**: ruflo bridges Claude Code and OpenAI Codex, enabling hybrid orchestration where tasks can be routed to either model based on capability or cost.

**Routing/orchestration**: Swarm-based with configurable orchestration strategies. Agent Teams integration (when enabled) is documented for use with ruflo workflows.

**Strengths**:
- Enterprise architecture designed for production use
- Hybrid Claude Code + Codex integration
- RAG integration is a differentiator for knowledge-heavy codebases

**Limitations**:
- Heavy: 6,000+ commits of accumulated complexity
- Documentation can lag behind development pace
- Swarm intelligence adds non-determinism that is hard to debug
- Star count is lower than community perception suggests

---

### 4.3 oh-my-claudecode

**Stars**: 858 stars in 24 hours at launch; 17,500+ (current)
**Architecture pattern**: Zero-config orchestration layer with 32 specialized agents

**Architecture**: oh-my-claudecode runs up to 5 Claude Code instances in parallel (Ultrapilot mode), each working in isolated git worktrees with a shared task list. The framework provides 32 pre-configured specialist agents covering different development domains. Claimed results: 3-5x speedup, 30-50% token savings through specialization.

**Ultrapilot mode**: The signature feature. Multiple Claude Code instances share a task list; each claims available tasks. A supervisor monitors progress. No pre-flight planning required — agents coordinate dynamically via the shared task list.

**Agent specialization**: 32 agents includes specialists for testing, documentation, security review, infrastructure, and more. The framework routes tasks to the most appropriate specialist automatically.

**Routing/orchestration**: Shared task list (pull-based). The supervisor coordinates, but agents have significant autonomy in claiming and executing tasks.

**Strengths**:
- Zero-config: works without MANIFEST.md, CONTRACT.md, or pre-flight planning
- 32 specialist agents cover a wide range of development domains
- 3-5x speedup claims are consistent with community reports (though not independently benchmarked)
- Autopilot mode for fully autonomous operation

**Limitations**:
- Autopilot removes human checkpoints — contradicts MASFT findings on spec failures requiring human judgment
- 30-50% token savings are community-reported, not independently verified
- No file ownership contracts — conflict prevention relies on task list granularity
- 5-instance practical ceiling in Ultrapilot is lower than Convoy's 8-Rider ceiling

---

### 4.4 agent-orchestrator (Composio)

**Stars**: ~5,600 (GitHub)
**Architecture pattern**: Task planning, parallel agent dispatch, CI/merge/review automation

**Architecture**: agent-orchestrator (by Composio) focuses on the full development lifecycle: plan tasks, spawn parallel agents, handle CI integration, merge coordination, and review automation. Designed to connect to existing CI/CD pipelines (GitHub Actions, GitLab CI) rather than replace them.

**Routing/orchestration**: Plan-then-execute. The orchestrator decomposes tasks and dispatches parallel agents. CI integration means agents can observe test results and iterate until green.

**Strengths**:
- CI/CD integration is rare in this ecosystem — most tools work outside CI pipelines
- Full lifecycle coverage: planning through merge review
- Composio's tool integration ecosystem (250+ connectors) extends agent capabilities

**Limitations**:
- Less documented than ruflo or oh-my-claudecode
- CI integration adds setup complexity
- No pre-flight conflict prevention

---

### 4.5 parallel-worktrees

**Architecture pattern**: Dedicated skill for worktree-isolated parallel subagent execution

**Architecture**: parallel-worktrees is a Claude Code skill/utility (not a full framework) that handles the mechanics of creating and managing git worktrees for parallel agent execution. It is the community's standardized implementation of the worktree isolation pattern documented in the incident.io blog post (the "canonical" reference for this pattern).

**Core operations**: Create worktree on a new branch, spawn Claude Code in the worktree, monitor execution, handle merge back to main. The skill encapsulates the git plumbing so developers don't have to.

**Strengths**:
- Fills the mechanical gap that all parallel agent systems face
- Composable: can be used with any orchestration strategy
- Incident.io's validation gives it credibility

**Limitations**:
- Not a coordination framework — provides isolation but not conflict prevention or contracts
- No pre-flight planning or contract mechanism

---

## 5. Academic and Research Systems

### 5.1 Self-Organized Agents (Google/MIT)

**Paper**: "Towards a Science of Scaling Agent Systems" (arxiv.org/html/2512.08296v1, December 2025)
**Affiliation**: Google Research + MIT

**Key contribution**: The first quantitative scaling principles for multi-agent systems. Evaluated 180 agent configurations in controlled experiments. Developed a predictive model (R² = 0.513) that correctly identifies the optimal coordination strategy for 87% of unseen task configurations using measurable task properties (tool count, decomposability).

**Three dominant effects**:
1. **Tool-coordination tradeoff**: Tasks requiring many tools perform worse with multi-agent overhead because context window space consumed by agent-to-agent communication crowds out tool-use budget.
2. **Capability saturation**: Adding agents yields diminishing returns when the single-agent baseline exceeds a threshold. Additional agents don't help when one agent could already solve the problem.
3. **Topology-dependent error amplification**: Centralized orchestration (hub-and-spoke) reduces error amplification compared to peer-to-peer. Each communication hop can amplify errors; fewer hops = more reliable.

**Quantitative recommendations**:
- 3-6 agents is the optimal range for most tasks
- 8 agents is the practical ceiling before coordination overhead dominates
- Communication overhead scales roughly O(n²) with agent count in peer-to-peer topologies
- Centralized orchestration is recommended for coding tasks

**Design implications for Convoy**: The findings validate Convoy's 8-Rider ceiling, DAG-based (not peer-to-peer) dispatch, and orchestrator-workers pattern. They also suggest Convoy should track "tool count per task" during pre-flight as a signal for when multi-agent coordination will backfire.

---

### 5.2 MASFT / MAST

**Paper**: "Why Do Multi-Agent LLM Systems Fail?" (arxiv.org/abs/2503.13657, March 2025)
**Venue**: ICLR 2025 (accepted)
**Affiliation**: UC Berkeley (Mert Cemri, Melissa Z. Pan, Shuyi Yang et al.)

**Dataset**: MAST-Data — 1,600+ annotated traces across 7 popular multi-agent frameworks. Inter-annotator agreement κ = 0.88 (high).

**Taxonomy**: 14 unique failure modes clustered into 3 categories:
1. **System design issues** (~42% of failures): Specification errors, role ambiguity, missing interfaces, unclear task boundaries.
2. **Inter-agent misalignment** (~37% of failures): Agents producing incompatible outputs, divergent assumptions about shared state, handoff failures.
3. **Task verification gaps** (~21% of failures): Missing or inadequate checks that allow silent failures to propagate.

**Key finding**: "Many MAS failures arise from the challenges in inter-agent interactions rather than the limitations of individual agents." The bottleneck is coordination, not capability.

**Intervention study**: Improved specification of agent roles and enhanced orchestration strategies were tested. Identified failures require "more complex solutions" than simple prompt engineering — structural changes to the coordination protocol are necessary.

**Design implications**: The 42% specification problem rate validates Convoy's frozen contracts and pre-flight file ownership verification. The 37% inter-agent misalignment rate validates Convoy's seam cross-referencing. The 21% verification gap validates Sentinel post-merge verification.

---

### 5.3 AgentCoder

**Paper**: "AgentCoder: Multi-Agent Code Generation with Effective Iteration" (arxiv.org/pdf/2312.13010, 2023)
**Key finding**: Separating test generation from code generation is the most replicated finding in the multi-agent coding literature.

**Architecture**: Three agents only: Programmer, Test Designer, Test Executor. The Programmer receives test results from the Test Executor as feedback (not open-ended chat). This "structured feedback" pattern reduces token overhead while preserving the benefit of agent separation.

**Result**: By keeping the agent count minimal (3), AgentCoder avoids O(n²) communication overhead while achieving the primary benefit of multi-agent systems (reviewer independence).

**Design implication**: The "test separately from code" finding appears in Convoy as the Inspector + Outrider pattern — code review and test execution are separate agents, neither of which is the Rider who wrote the code.

---

### 5.4 Agentless (UIUC)

**Paper**: "Agentless: Demystifying LLM-based Software Engineering Agents" (arxiv.org/abs/2407.01489, 2024)
**Affiliation**: UIUC (OpenAutoCoder team)

**Key contribution**: A non-agentic pipeline (localize → repair → validate) that matched or beat multi-agent systems on SWE-Bench at the time of publication. Achieved 32% on SWE-Bench Lite at $0.70 per issue — competitive with much more complex systems.

**Subsequent developments (2025)**: Kimi-Dev used Agentless training as a "skill prior" for SWE-agents, achieving 60.4% pass rate on SWE-Bench Verified — the best performance among workflow approaches. This partially contradicts the "agentless is competitive" framing; well-trained agentic systems exceed Agentless performance when given sufficient capability.

**Current interpretation**: Agentless is most competitive for single-file bugs in well-structured codebases. Multi-agent agentic systems outperform Agentless on complex multi-file tasks (Agentless's self-reported weakness). The paper's core lesson remains valid: don't add multi-agent complexity unless you genuinely need it.

**Design implication for Convoy**: Validates the activation criterion requiring 3+ independent tasks before spawning a convoy. Single-file or single-task work should route to single-agent.

---

### 5.5 ChatDev / DevAll

**Stars**: ~27,000 (GitHub, OpenBMB/ChatDev)
**Origin**: Tsinghua NLP Lab (2023); ChatDev 2.0 released January 2026

**Evolution**: ChatDev originated as a "waterfall simulation" — agents playing CEO, CTO, Programmer, Reviewer roles in a fixed sequence. ChatDev 2.0 (DevAll) pivots to a "zero-code multi-agent platform for developing everything," with a puppeteer-style orchestration using a learnable central orchestrator trained with reinforcement learning.

**Puppeteer orchestration**: A central orchestrator dynamically activates and sequences agents based on learned preferences rather than fixed SOPs. The RL-trained orchestrator improves over time and reduces computational costs while maintaining output quality.

**Experiential co-learning**: ChatDev's original innovation — agents accumulate knowledge from past software projects in a shared memory, informing future decisions. Cross-project learning is more structured than most systems.

**Strengths**:
- 27k stars; well-studied in academic literature
- RL-trained orchestrator is a novel approach to coordination
- Experiential co-learning enables cross-project improvement

**Limitations**:
- Original waterfall SOP is too rigid for real development
- RL training requires large datasets; custom training is not practical for most users
- Performance on SWE-Bench lags behind newer systems

---

### 5.6 CAMEL-AI

**Stars**: ~7,000 (GitHub, camel-ai/camel)
**Origin**: King Abdullah University of Science and Technology (KAUST), 2023

**Key contribution**: **Inception prompting** — a technique for establishing role-play context between agents. Two agents (a user-role and an assistant-role) conduct a task-driven conversation guided by an initial inception prompt that establishes their relative roles, constraints, and goals.

**Multi-agent debate**: CAMEL demonstrated that agents debating multiple perspectives on a problem can reach better solutions than single agents on some reasoning tasks. Not validated for coding specifically.

**Architecture**: Peer-to-peer conversation. An AI Society of Mind. No formal orchestrator. Conversations can wander; convergence is not guaranteed.

**Strengths**:
- Inception prompting is widely adopted as a technique
- Multi-agent debate has shown promise for reasoning-heavy tasks
- Active research community; CAMEL has expanded beyond the original paper

**Limitations**:
- Peer-to-peer without orchestration leads to unpredictable outcomes on coding tasks
- Multi-agent debate adds overhead without consistent improvement for code generation
- Academic research system; not production-ready for large-scale use

---

### 5.7 AgileCoder

**Stars**: ~500 (GitHub, FSoft-AI4Code/AgileCoder)
**Origin**: FPT Software AI Center (Vietnam), 2024
**Venue**: FORGE 2025

**Key contribution**: Agile methodology (sprints, standups, retrospectives) applied to multi-agent software development. Instead of fixed role assignments (MetaGPT's approach), AgileCoder creates a **dynamic task backlog** and divides work into sprints, with the backlog updated at each sprint based on what was completed and what new requirements emerged.

**Dynamic backlog**: The primary differentiator. Requirements evolve during execution — new tasks are added to the backlog as development reveals dependencies. This makes AgileCoder more adaptive than waterfall-SOP systems like MetaGPT.

**Performance**: Outperforms MetaGPT and ChatDev on HumanEval and MBPP benchmarks. Surpassing established systems on standard benchmarks while using a novel organization principle is notable.

**Design implication**: The dynamic backlog pattern is relevant for Convoy — current pre-flight planning must enumerate all tasks before dispatch. A dynamic backlog extension would allow discovering new tasks during execution without requiring a full re-plan.

---

## 6. Cross-Cutting Comparison (12 Dimensions)

Note: Systems are assessed across the 12 dimensions defined in CONTRACT.md. Scores are 0-10; higher is better except for Coordination Overhead (where lower overhead = higher score). This table covers representative systems across all categories; the full 12-dimension analysis including Convoy is in CONVOY-COMPARATIVE.md.

| System | Category | Parallel Exec | File Conflict Prev | Shared Contracts | State Persistence | Failure Classification | Quality Gates | Spec Compliance | Cross-Session Learning | Human Oversight | Coordination Overhead | Scalability | Ecosystem Integration |
|--------|----------|--------------|-------------------|-----------------|-------------------|----------------------|---------------|----------------|----------------------|----------------|----------------------|-------------|----------------------|
| LangGraph | Open-source | 7 | 2 | 5 | **10** | 4 | 5 | 6 | 4 | 8 | 5 | 7 | 7 |
| CrewAI | Open-source | 7 | 2 | 3 | 6 | 3 | 4 | 3 | **8** | 5 | 7 | 7 | 8 |
| AutoGen/AG2 | Open-source | 6 | 1 | 3 | 5 | 3 | 5 | 2 | 3 | 5 | 4 | 5 | 7 |
| MetaGPT | Open-source | 5 | 3 | 6 | 5 | 2 | 4 | 4 | 4 | 4 | 5 | 5 | 5 |
| Gas Town | Open-source | **10** | 6 | 5 | 9 | 6 | 5 | 3 | 7 | 5 | 3 | **10** | 6 |
| OpenAI Agents SDK | Open-source | 5 | 1 | 4 | 4 | 3 | 6 | 2 | 3 | 6 | 6 | 6 | **9** |
| Semantic Kernel | Open-source | 5 | 2 | 5 | 7 | 4 | 5 | 4 | 4 | 6 | 5 | 6 | **9** |
| PydanticAI | Open-source | 3 | 1 | **9** | 3 | 2 | 4 | 2 | 2 | 4 | 7 | 4 | 7 |
| Cursor | Commercial | 8 | 3 | 1 | 2 | 2 | 6 | 1 | 1 | 7 | **9** | 7 | 8 |
| Devin | Commercial | 7 | 4 | 4 | 6 | 4 | 5 | 3 | 4 | 5 | 6 | 7 | 7 |
| Augment/Intent | Commercial | 6 | 5 | 6 | 5 | 5 | **8** | 5 | 4 | 7 | 8 | 7 | 7 |
| Copilot Workspace | Commercial | 2 | 4 | 4 | 5 | 3 | 7 | 5 | 3 | 6 | **9** | 3 | **9** |
| Amazon Q | Commercial | 3 | 4 | 3 | 3 | 2 | **8** | 3 | 2 | 4 | 7 | 5 | 8 |
| Replit Agent | Commercial | 2 | 4 | 2 | 5 | 2 | 3 | 2 | 2 | 5 | 7 | 2 | 6 |
| Agent Teams | Claude Code | 8 | 4 | 4 | 5 | 3 | 5 | 3 | 3 | 6 | 7 | 7 | **9** |
| ruflo | Claude Code | 7 | 3 | 3 | 4 | 3 | 4 | 2 | 3 | 5 | 5 | 6 | 7 |
| oh-my-claudecode | Claude Code | 7 | 3 | 2 | 3 | 2 | 4 | 2 | 2 | 3 | 4 | 6 | 7 |
| ChatDev | Research | 4 | 2 | 4 | 5 | 3 | 4 | 4 | 6 | 3 | 4 | 4 | 3 |
| AgentCoder | Research | 4 | 2 | 3 | 3 | 2 | 7 | 3 | 2 | 2 | 4 | 6 | 3 |

### Dimension Notes

**Parallel Execution**: Gas Town scores 10 — the only system designed for 20-30+ concurrent agents. Cursor and Agent Teams score 8 — up to 8 parallel agents in isolated worktrees.

**File Conflict Prevention**: PydanticAI scores 9 not for multi-agent conflict prevention but because its type system enforces interface contracts that prevent a class of conflicts. No system outside Convoy has a pre-flight file ownership matrix. Augment (5) uses spec-driven boundaries; Gas Town (6) uses actor attribution. All others rely on isolation (worktrees/VMs) and discover conflicts at merge.

**Shared Contracts**: PydanticAI (9) for typed interfaces. MetaGPT (6) for document-as-protocol. Augment/Intent (6) for living specs. Most systems are at 1-4 — agents interpret tasks independently.

**State Persistence**: LangGraph (10) for per-step checkpointing with time-travel. Gas Town (9) for Git-backed provenance. Semantic Kernel (7) for Process Framework durable state machines.

**Failure Classification**: Gas Town (6) and Augment (5) have the best non-Convoy failure handling. Most systems (Cursor, Codex, AutoGen) rely on model-level retry without classification.

**Quality Gates**: Augment/Intent (8) and Amazon Q (8) score highest among non-Convoy systems. Augment's continuous Verifier agent and Amazon Q's SAST /review agent are genuine independent quality gates.

**Spec Compliance**: Augment/Intent (5) and Copilot Workspace (5) have the best non-Convoy spec tracing. No system outside Convoy has a dedicated post-merge spec verification phase equivalent to Sentinel.

**Cross-Session Learning**: CrewAI (8) has the most structured memory system (three-tier). Gas Town (7) has provenance records. ChatDev (6) has experiential co-learning across projects.

**Human Oversight**: Cursor (9) and Copilot Workspace (9) have the cleanest human oversight models — changes isolated until human explicitly merges or approves.

**Coordination Overhead**: Cursor (9) and Copilot Workspace (9) have the lowest overhead — no pre-planning required. Gas Town (3) has the highest non-Convoy overhead (infrastructure requirements).

**Scalability**: Gas Town (10) is the only system designed for 20-30+ agents. LangGraph (7), Devin (7), and Cursor (7) scale reasonably. Most systems hit practical ceilings at 3-6 agents.

**Ecosystem Integration**: OpenAI Agents SDK (9), Semantic Kernel (9), Copilot Workspace (9), and Agent Teams (9) have the strongest ecosystem integration. Semantic Kernel's A2A protocol support is a notable forward-looking capability.

---

## 7. Current Leaders by Dimension

### Parallel Execution
**Leader**: Gas Town (10) — the only system designed for 20-30+ concurrent agents with pull-based work queues and tmux-native architecture. Nearest commercial competitor is Cursor (8).

**Notable**: The Google/MIT research establishing 3-6 as the optimal range means Gas Town's 20-30+ agent capability may primarily serve edge cases.

### File Conflict Prevention
**Leader**: No open-source or commercial system has a pre-flight file ownership matrix. PydanticAI leads on typed interface enforcement (9), but this prevents interface mismatches, not file-level edit conflicts. Gas Town and Augment are best-in-class on detection; no one is best-in-class on pre-flight prevention outside Convoy.

### Shared Contracts
**Leader**: PydanticAI (9) for type-enforced interfaces, but this is a single-agent framework concern, not multi-agent. MetaGPT (6) for document-as-protocol is the best multi-agent approach in open-source. Augment/Intent (6) for living specs in commercial.

### State Persistence
**Leader**: LangGraph (10) — per-step checkpointing with time-travel debugging, multiple backend options (SQLite, Postgres), and human-in-the-loop pause/resume. No other system matches LangGraph's checkpointing depth in the open-source category.

### Failure Classification
**Leader**: No system outside Convoy has a formal failure taxonomy. Gas Town's stall detection (3-tier watchdog) is the most autonomous recovery mechanism. Augment's coordinator re-routing is the most structured in commercial systems. The field has not converged on a formal failure taxonomy.

### Quality Gates
**Leader**: Augment/Intent and Amazon Q are tied (8) — Augment's continuous Verifier agent and Amazon Q's SAST /review agent both represent independent, non-author quality gates. Copilot Workspace's closed-loop review → fix pipeline is a strong implementation.

### Spec Compliance Verification
**Leader**: Augment/Intent (5) — continuous Verifier against shared spec is the best non-Convoy approach. No commercial system has a dedicated post-merge "did we build what we planned?" verification phase.

### Cross-Session Learning
**Leader**: CrewAI (8) — three-tier memory (short-term, long-term SQLite, entity memory) is the most structured learning mechanism in the open-source space. ChatDev's experiential co-learning is notable for cross-project knowledge transfer.

### Human Oversight Balance
**Leader**: Cursor (9) and Copilot Workspace (9) — changes isolated until human explicitly merges. Neither requires constant supervision but gives humans full visibility at merge time. Augment (8) is notable for spec-editing as natural human integration.

### Coordination Overhead
**Leader**: Cursor (9) and Replit (7) — zero configuration, click-to-run. Copilot Workspace (9) — sequential pipeline with no pre-planning required.

### Scalability
**Leader**: Gas Town (10) — purpose-built for 20-30+ agents. Devin and Cursor (both 7) scale reasonably for commercial platforms. LangGraph (7) scales via sub-graph composition.

### Ecosystem Integration
**Leader**: Tie between OpenAI Agents SDK, Semantic Kernel, Copilot Workspace, and Agent Teams (all 9). Semantic Kernel's A2A protocol support for cross-framework interoperability is the most forward-looking.

---

## 8. Emerging Trends

### 8.1 A2A Protocol and Cross-Framework Interoperability

Google's Agent-to-Agent (A2A) protocol (2026) enables agents built in different frameworks (LangGraph, CrewAI, Semantic Kernel, Google ADK) to communicate using a standard protocol. Semantic Kernel adopted A2A in early 2026; Google ADK is A2A-native.

**Implication**: The "which framework" question may matter less as A2A matures — agents can be composed across framework boundaries. For Convoy, A2A integration could enable Riders built in different frameworks to participate in the same convoy via the protocol.

### 8.2 MCP (Model Context Protocol) as Infrastructure Layer

MCP has become the de facto standard for tool integration in 2026. OpenAI Agents SDK, Google ADK, Amazon Q, GitHub Copilot Workspace, and Cursor all support MCP. Claude Code's native MCP support makes it a first-class participant.

**Implication**: MCP reduces the "ecosystem integration" overhead that previously required framework-specific adapters. Systems that integrated MCP early (Semantic Kernel, OpenAI SDK) have a structural advantage.

### 8.3 Competitive Execution

Cursor's competitive execution pattern — running multiple models on the same task and picking the best result — is showing traction. CrewAI's consensual process (agent voting) is a variant. No system has formalized cost-controlled competitive execution for quality-critical tasks.

**Implication**: For security-critical code or high-stakes architectural decisions, competitive execution may become a standard quality gate — run two agents, compare outputs, escalate divergence to human. Adds 2x cost but validates correctness.

### 8.4 RL-Trained Orchestrators

ChatDev 2.0's puppeteer orchestration (RL-trained coordinator) points toward a future where coordination decisions are learned, not programmed. Current systems use rule-based routing (Convoy's DAG, LangGraph's conditional edges) or LLM-as-selector (GroupChat, Magentic). RL-trained coordinators optimize routing from experience.

**Implication**: Early. RL-trained coordination requires large training datasets and specific task distributions. Not practical for custom protocols like Convoy. Worth monitoring as foundation model training includes more multi-agent data.

### 8.5 AST-Level Merge and Semantic Conflict Resolution

Git text-level merging cannot detect semantic conflicts (two agents making individually correct changes that compose into incorrect behavior). Several projects (dkod-io/dkod-plugin, academic research) are developing AST-level merge tools that detect and resolve semantic conflicts.

**Implication**: Augment Code's research states that "semantic conflict resolution remains unsolved in general." Current mitigation (file ownership, sequential merges) avoids the problem rather than solving it. AST-level tools could enable more parallelism by allowing multiple agents to safely work on the same file in different functions.

### 8.6 Agent Teams Going Mainstream

Anthropic's Agent Teams (February 2026) is in research preview. If it exits experimental and proves reliable, it could shift the baseline for what "Claude Code multi-agent" means — from custom worktree scripts and external frameworks to native, structured orchestration with direct inter-agent messaging.

**Implication**: The Claude Code ecosystem tooling (ruflo, oh-my-claudecode, Convoy) will need to either integrate with Agent Teams or clearly differentiate why the custom approach is superior. The 13-operation TeammateTool API is rich enough to replace much of what these tools provide.

### 8.7 Benchmark Maturation

SWE-Bench Verified (independently validated) has emerged as the credible benchmark for coding agent evaluation. As of early 2026, the best systems achieve ~60% on SWE-Bench Verified (Kimi-Dev with Agentless training). Top commercial systems (Claude 3.5 Sonnet on SWE-Bench) are in the 49-60% range.

**Implication**: The benchmark is approaching the ceiling for "find and fix existing bugs in open-source repos." SWE-Bench Pro (long-horizon tasks) and new multi-file benchmarks are emerging to push systems toward the harder coordination problems that Convoy is designed to solve.

### 8.8 Claude Code's Growing Market Share

Claude Code now authors approximately 4% of all public GitHub commits (~135,000/day as of March 2026). The community and tooling ecosystem around Claude Code is growing proportionally. This creates network effects: more community tooling, more tutorials, more documented patterns.

**Implication**: The Claude Code ecosystem category (Agent Teams, ruflo, oh-my-claudecode, Convoy) benefits from this growth. Patterns that work well in the Claude Code context are more likely to be discovered, tested, and refined.

---

## 9. Sources

### Web Sources

- [LangGraph architecture overview — mager.co blog, March 2026](https://www.mager.co/blog/2026-03-12-langgraph-deep-dive/)
- [LangGraph production agents — use-apify.com, 2026](https://use-apify.com/blog/langgraph-agents-production)
- [CrewAI GitHub repository — crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
- [CrewAI unique features — vadim.blog](https://vadim.blog/crewai-unique-features)
- [AutoGen multi-agent conversation framework — microsoft.github.io](https://microsoft.github.io/autogen/docs/Use-Cases/agent_chat/)
- [AG2 conversation patterns deep dive — docs.ag2.ai](https://docs.ag2.ai/0.8.6/docs/user-guide/advanced-concepts/conversation-patterns-deep-dive/)
- [MetaGPT GitHub — FoundationAgents/MetaGPT](https://github.com/FoundationAgents/MetaGPT)
- [MetaGPT arxiv paper — arxiv.org/html/2308.00352v6](https://arxiv.org/html/2308.00352v6)
- [OpenAI Agents SDK — openai.github.io](https://openai.github.io/openai-agents-python/)
- [OpenAI Agents SDK handoffs — openai.github.io/handoffs](https://openai.github.io/openai-agents-python/handoffs/)
- [OpenAI Agents SDK tracing — openai.github.io/tracing](https://openai.github.io/openai-agents-python/tracing/)
- [Gas Town GitHub — steveyegge/gastown](https://github.com/steveyegge/gastown)
- [Gas Town glossary — gastown/docs/glossary.md](https://github.com/steveyegge/gastown/blob/main/docs/glossary.md)
- [Steve Yegge Medium — Welcome to Gas Town, January 2026](https://steve-yegge.medium.com/welcome-to-gas-town-4f25ee16dd04)
- [Semantic Kernel Magentic orchestration — Microsoft Learn](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/magentic)
- [Cursor 2.0 changelog — cursor.com/changelog/2-0](https://cursor.com/changelog/2-0)
- [Cursor background agents guide — ameany.io, 2026](https://ameany.io/blog/cursor-background-agents/)
- [Cursor best practices — cursor.com/blog/agent-best-practices](https://cursor.com/blog/agent-best-practices)
- [Devin 2.0 — cognition.ai/blog/devin-2](https://cognition.ai/blog/devin-2)
- [Devin 2.2 — cognition.ai/blog/introducing-devin-2-2](https://cognition.ai/blog/introducing-devin-2-2)
- [Augment Code Intent — augmentcode.com/product/intent](https://www.augmentcode.com/product/intent)
- [Augment Code multi-agent workspace guide — augmentcode.com/guides](https://www.augmentcode.com/guides/how-to-run-a-multi-agent-coding-workspace)
- [GitHub Copilot Workspace — githubnext.com](https://githubnext.com/projects/copilot-workspace)
- [GitHub Copilot CLI plan feature — github.blog changelog, January 2026](https://github.blog/changelog/2026-01-21-github-copilot-cli-plan-before-you-build-steer-as-you-go/)
- [Amazon Q Developer features — aws.amazon.com/q/developer/features](https://aws.amazon.com/q/developer/features/)
- [Amazon Q custom agents — dev.to/aws-builders](https://dev.to/aws-builders/understanding-amazon-q-custom-agents-concepts-architecture-inner-workings-362)
- [Replit Agent — replit.com/products/agent](https://replit.com/products/agent)
- [Claude Code Agent Teams — blog.imseankim.com, March 2026](https://blog.imseankim.com/claude-code-team-mode-multi-agent-orchestration-march-2026/)
- [Agent Teams in Claude Code — heeki.medium.com, March 2026](https://heeki.medium.com/collaborating-with-agents-teams-in-claude-code-f64a465f3c11)
- [Claude Code hidden swarm — paddo.dev](https://paddo.dev/blog/claude-code-hidden-swarm/)
- [ruflo GitHub — ruvnet/ruflo](https://github.com/ruvnet/ruflo)
- [oh-my-claudecode GitHub — yeachan-heo/oh-my-claudecode](https://github.com/yeachan-heo/oh-my-claudecode)
- [oh-my-claudecode — ohmyclaudecode.com](https://ohmyclaudecode.com/)
- [Google/MIT scaling agent systems — arxiv.org/html/2512.08296v1](https://arxiv.org/html/2512.08296v1)
- [Google research blog — scaling agent systems](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)
- [MASFT paper — arxiv.org/abs/2503.13657](https://arxiv.org/abs/2503.13657)
- [MAST GitHub — multi-agent-systems-failure-taxonomy/MAST](https://github.com/multi-agent-systems-failure-taxonomy/MAST)
- [AgentCoder paper — arxiv.org/pdf/2312.13010](https://arxiv.org/pdf/2312.13010)
- [Agentless paper — arxiv.org/abs/2407.01489](https://arxiv.org/abs/2407.01489)
- [Agentless GitHub — OpenAutoCoder/Agentless](https://github.com/OpenAutoCoder/Agentless)
- [Kimi-Dev Agentless training — openreview.net](https://openreview.net/forum?id=tYppHuGhxJ)
- [ChatDev arxiv paper — arxiv.org/html/2307.07924v5](https://arxiv.org/html/2307.07924v5)
- [ChatDev GitHub — OpenBMB/ChatDev](https://github.com/OpenBMB/ChatDev)
- [AgileCoder GitHub — FSoft-AI4Code/AgileCoder](https://github.com/FSoft-AI4Code/AgileCoder)
- [OpenAI Codex subagents — developers.openai.com/codex/subagents](https://developers.openai.com/codex/subagents)
- [Best multi-agent frameworks 2026 — gurusup.com](https://gurusup.com/blog/best-multi-agent-frameworks-2026)

### Foundational Prior Research (from RESEARCH-ANALYSIS.md and BENCHMARK.md)

- Manus context engineering post — rlancemartin.github.io/2025/10/15/manus
- Planning-with-Files — github.com/OthmanAdi/planning-with-files
- Augment Code semantic conflict research — augmentcode.com
- PwC 7x accuracy study (structured validation loops with judge agents)
