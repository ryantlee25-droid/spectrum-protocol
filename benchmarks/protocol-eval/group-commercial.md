# Protocol Evaluation: Commercial Systems

> Group 3 of 3 | Evaluator: howler-commercial | Rain: protocol-eval-0401
> Date: 2026-04-01

Scoring rubric: 1 (not addressed) to 5 (comprehensive with feedback loop).
Anti-inflation rule: claims without architectural evidence capped at 3.

---

## 10. Cursor Agents

**Source**: cursor.com product, public documentation and observed behavior
**Type**: IDE-integrated AI coding agents

### Scores

| # | Dimension | Score | Evidence |
|---|-----------|-------|----------|
| 1 | Task Decomposition | 3 | Background agents can decompose tasks into steps. Agent creates a plan visible in the UI. User can guide decomposition through conversation. Less formal than manifest-based systems -- plans are conversational, not structured artifacts. |
| 2 | Conflict Prevention | 2 | Single-agent operation for most workflows. Multi-file edits are serialized by the agent. No formal file ownership when using background agents in parallel. Relies on IDE-level undo rather than protocol-level prevention. |
| 3 | Communication Efficiency | 3 | Agent communicates through IDE UI -- inline diffs, chat panel, terminal output. Rich UX for single-agent interaction. Multi-agent communication (between background agents) is limited -- no structured inter-agent messaging. |
| 4 | Failure Recovery | 3 | Checkpoint system allows reverting agent changes. IDE-level undo for granular rollback. Agents can retry failed operations. No typed failure classification but checkpoint-based recovery is practical. Yolo mode bypasses confirmation for faster iteration. |
| 5 | Knowledge Sharing | 3 | `.cursorrules` for project-level conventions. Codebase indexing provides context. Conversation history within sessions. No cross-session learning or entity tracking by default. Notepads for persistent context. |
| 6 | State Management | 3 | Checkpoint system tracks agent state within sessions. Session persistence for conversation continuity. No cross-session resume for interrupted multi-step work. State is session-scoped. |
| 7 | Quality Assurance | 2 | Agent can run tests and linters. No dedicated quality gate pipeline. Quality depends on user prompting the agent to verify work. No formal reviewer role or contract-based verification. |
| 8 | Scalability | 3 | Background agents enable parallel work. Max agents limited by plan tier. Each agent operates independently. No DAG-based coordination between agents. Practical for 2-3 parallel tasks. |
| 9 | Mode Adaptability | 2 | Normal mode vs Yolo mode (auto-apply changes). Agent mode vs standard chat. No automatic mode selection based on task complexity. Mode is user-selected. |
| 10 | Setup Complexity | 5 | Download IDE, open project, start coding. Zero configuration required. AI capabilities are built into the editor experience. Lowest barrier to entry for AI-assisted development. |
| 11 | Observability | 3 | IDE UI shows agent reasoning, file changes, terminal output in real time. Visual diff previews. No multi-agent dashboard. Session-scoped visibility. |
| 12 | Cost Awareness | 3 | Model selection (fast/smart) allows cost tradeoff. Usage limits per plan tier. Token usage visible in UI. No per-task budget tracking or automatic model optimization. |

**Composite Score**: 2.92 / 5.00

### Strengths
- Lowest setup complexity -- AI coding is built into the IDE
- Visual diff previews and inline editing provide excellent single-agent UX
- Checkpoint system enables practical rollback
- Codebase indexing provides rich project context

### Weaknesses
- Limited multi-agent coordination -- agents operate independently
- No file ownership or structured conflict prevention
- No formal quality gate pipeline
- Session-scoped state with no cross-session persistence for multi-step work

---

## 11. OpenAI Agents SDK

**Source**: openai/openai-agents-python, documentation
**Type**: Python SDK for building multi-agent applications

### Scores

| # | Dimension | Score | Evidence |
|---|-----------|-------|----------|
| 1 | Task Decomposition | 3 | Agents can hand off to other agents via `handoff()`. Orchestrator agent pattern decomposes tasks to specialized agents. No structured manifest -- decomposition is conversational/programmatic. Triage pattern for routing tasks to appropriate agents. |
| 2 | Conflict Prevention | 1 | Not addressed. SDK provides primitives (agents, tools, handoffs) but no file ownership or conflict prevention. Developers must build their own coordination layer. |
| 3 | Communication Efficiency | 3 | Handoff mechanism passes conversation context between agents. Tool outputs provide structured communication. Guardrails validate inputs/outputs. Context is conversation-scoped -- agents share the message thread. |
| 4 | Failure Recovery | 3 | `max_turns` prevents infinite loops. Guardrails catch invalid states. Tracing enables debugging. No typed failure classification or circuit breakers. Error handling is SDK-level (try/except), not protocol-level. |
| 5 | Knowledge Sharing | 2 | Conversation context carries knowledge between handoffs. No persistent memory across sessions. No entity tracking. Knowledge sharing must be built on top of the SDK. |
| 6 | State Management | 2 | Conversation state (RunContext) passed through agent chain. No persistent checkpointing. State is runtime-scoped. Developers can add persistence but it's not built in. |
| 7 | Quality Assurance | 3 | Guardrails (input/output) provide validation. Structured outputs via Pydantic models. No dedicated quality gate pipeline. Quality checking is guardrail-based, not multi-agent review. |
| 8 | Scalability | 3 | Agent chains can be composed. Handoffs enable routing to specialized agents. Async execution supported. No DAG-based scheduling or parallel agent coordination built in. Scales through composition. |
| 9 | Mode Adaptability | 2 | Single operational mode. Agent behavior configured at definition time. Triage/routing patterns allow dynamic agent selection. No automatic mode adaptation based on task complexity. |
| 10 | Setup Complexity | 4 | `pip install openai-agents`. Clean Python API. Fewer abstractions than CrewAI or LangGraph. Well-documented with clear examples. Requires OpenAI API key. Minimal boilerplate. |
| 11 | Observability | 4 | Built-in tracing with spans for agents, tools, handoffs, and guardrails. Trace export to observability platforms. OpenAI dashboard integration. Structured trace data with timing, token usage, and agent decisions. |
| 12 | Cost Awareness | 2 | Token usage tracked in traces. Model selection per agent. No budget limits or automatic cost optimization. Cost management is developer responsibility. |

**Composite Score**: 2.67 / 5.00

### Strengths
- Clean, minimal SDK design -- low abstraction overhead
- Built-in tracing with structured observability
- Guardrails provide input/output validation
- Handoff mechanism is intuitive for agent-to-agent delegation

### Weaknesses
- SDK provides primitives, not a coordination protocol -- developers must build coordination themselves
- No file ownership, conflict prevention, or state persistence
- No failure recovery beyond retries and guardrails
- No knowledge persistence across sessions

---

## Group Summary

| System | Composite | Rank (within group) |
|--------|-----------|---------------------|
| Cursor Agents | 2.92 | 1 |
| OpenAI Agents SDK | 2.67 | 2 |

**Key observations:**
- Both commercial systems prioritize developer experience over multi-agent coordination depth
- Cursor excels at setup complexity (5/5) -- AI is invisible infrastructure, not a protocol to learn
- OpenAI Agents SDK excels at observability (4/5) with built-in structured tracing
- Neither system addresses file ownership or structured conflict prevention
- Both provide building blocks (agents, tools) rather than end-to-end coordination protocols
- Commercial systems are designed for broad adoption; protocol complexity would limit market
- The gap between commercial systems and Spectrum reflects a fundamental design tradeoff: accessibility vs coordination depth
- Cursor's checkpoint system is the closest commercial equivalent to Spectrum's CHECKPOINT.json but operates at session scope, not protocol scope
