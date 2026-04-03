# Protocol-Level Evaluation: Spectrum v5.1 vs 10 Multi-Agent Systems

> Rain: protocol-eval-0401 | Date: 2026-04-01
> Methodology: Rubric-based analysis across 12 coordination dimensions
> Sources: Public documentation, GitHub repositories, product docs
> Cost: Zero API cost (rubric-based, no live testing)

---

## Methodology

### Dimensions (12)

Derived from REALM-Bench, MultiAgentBench (MARBLE), MASEval, AgentArch, and harness-engineering assessments.

**Coordination Quality (5 dimensions):**
1. Task Decomposition -- How tasks are broken down and assigned
2. Conflict Prevention -- Mechanisms to prevent resource/file conflicts
3. Communication Efficiency -- Inter-agent information exchange
4. Failure Recovery -- What happens when agents fail
5. Knowledge Sharing -- Cross-run and cross-agent learning

**Protocol Architecture (4 dimensions):**
6. State Management -- Persistence, checkpointing, recovery
7. Quality Assurance -- Verification, review, testing pipeline
8. Scalability -- How well the system handles increasing agent count
9. Mode Adaptability -- Adapting protocol overhead to task complexity

**Operational Quality (3 dimensions):**
10. Setup Complexity -- Barrier to entry (inverted: 5 = easiest)
11. Observability -- Visibility into multi-agent execution
12. Cost Awareness -- Cost tracking, optimization, budget management

### Scoring Rubric

| Score | Meaning |
|-------|---------|
| 1 | Not addressed by the protocol |
| 2 | Acknowledged but no mechanism |
| 3 | Mechanism exists, partially documented |
| 4 | Well-documented mechanism with evidence of use |
| 5 | Comprehensive mechanism with self-correction/feedback loop |

**Anti-inflation rule**: Claims without architectural evidence are capped at 3.

### Systems Evaluated

| # | System | Category | Type |
|---|--------|----------|------|
| 1 | Spectrum Protocol v5.1 | Claude Code | CLAUDE.md coordination protocol |
| 2 | Gas Town | Claude Code | CLAUDE.md coordination protocol |
| 3 | oh-my-claudecode | Claude Code | Plugin/extension system |
| 4 | Citadel | Claude Code | CLAUDE.md coordination protocol |
| 5 | Overstory | Claude Code | Workflow configuration |
| 6 | CrewAI | Framework | Python multi-agent orchestration |
| 7 | LangGraph | Framework | Python/JS stateful agent graphs |
| 8 | AutoGen/AG2 | Framework | Python multi-agent conversations |
| 9 | MetaGPT | Framework | Python SOP-based development |
| 10 | Cursor Agents | Commercial | IDE-integrated AI agents |
| 11 | OpenAI Agents SDK | Commercial | Python agent building SDK |

---

## Overall Rankings

| Rank | System | Composite | Category |
|------|--------|-----------|----------|
| 1 | **Spectrum Protocol v5.1** | **4.50** | Claude Code |
| 2 | LangGraph | 3.58 | Framework |
| 3 | CrewAI | 3.33 | Framework |
| 4 | Gas Town | 3.25 | Claude Code |
| 5 | MetaGPT | 3.00 | Framework |
| 6 | Cursor Agents | 2.92 | Commercial |
| 7 | AutoGen/AG2 | 2.83 | Framework |
| 8 | Citadel | 2.67 | Claude Code |
| 8 | OpenAI Agents SDK | 2.67 | Commercial |
| 10 | oh-my-claudecode | 2.00 | Claude Code |
| 11 | Overstory | 1.75 | Claude Code |

**Field average**: 2.95 / 5.00
**Median**: 2.83

---

## Full Score Matrix

| Dimension | Spectrum | Gas Town | oh-my-cc | Citadel | Overstory | CrewAI | LangGraph | AutoGen | MetaGPT | Cursor | OAI SDK |
|-----------|----------|----------|----------|---------|-----------|--------|-----------|---------|---------|--------|---------|
| Task Decomposition | **5** | 4 | 2 | 3 | 2 | 4 | 4 | 3 | **5** | 3 | 3 |
| Conflict Prevention | **5** | 4 | 1 | 3 | 1 | 2 | 3 | 2 | 3 | 2 | 1 |
| Communication Efficiency | 4 | 4 | 2 | 3 | 1 | 4 | 4 | **4** | 4 | 3 | 3 |
| Failure Recovery | **5** | 3 | 2 | 2 | 2 | 3 | 4 | 3 | 2 | 3 | 3 |
| Knowledge Sharing | 4 | 3 | 2 | 2 | 2 | **4** | 3 | 3 | 3 | 3 | 2 |
| State Management | **5** | 4 | 2 | 3 | 1 | 3 | **5** | 2 | 3 | 3 | 2 |
| Quality Assurance | **5** | 3 | 2 | 3 | 2 | 3 | 3 | 3 | 4 | 2 | 3 |
| Scalability | 4 | 3 | 2 | 3 | 1 | **4** | **4** | 3 | 3 | 3 | 3 |
| Mode Adaptability | **5** | 2 | 2 | 2 | 2 | 3 | 3 | 3 | 2 | 2 | 2 |
| Setup Complexity | 4 | 4 | 4 | 4 | **5** | 3 | 3 | 3 | 2 | **5** | 4 |
| Observability | 4 | 3 | 2 | 2 | 1 | **4** | **4** | 3 | 3 | 3 | **4** |
| Cost Awareness | **4** | 2 | 1 | 2 | 1 | 3 | 3 | 2 | 2 | 3 | 2 |

**Bold** = tied or sole leader in that dimension.

---

## Dimension Group Analysis

### Coordination Quality (avg across 5 dimensions)

| System | Avg | Best Dimension |
|--------|-----|----------------|
| Spectrum | 4.60 | Failure Recovery (5) |
| Gas Town | 3.60 | Decomposition + Conflict + Communication (4) |
| LangGraph | 3.60 | Failure Recovery (4) |
| CrewAI | 3.40 | Knowledge Sharing (4) |
| MetaGPT | 3.40 | Task Decomposition (5) |
| AutoGen/AG2 | 3.00 | Communication (4) |
| Cursor | 2.80 | Various (3) |
| Citadel | 2.60 | Conflict Prevention (3) |
| OAI SDK | 2.40 | Failure Recovery (3) |
| oh-my-cc | 1.80 | -- |
| Overstory | 1.60 | -- |

### Protocol Architecture (avg across 4 dimensions)

| System | Avg | Best Dimension |
|--------|-----|----------------|
| Spectrum | 4.75 | State Mgmt + QA + Mode Adapt (5) |
| LangGraph | 3.75 | State Management (5) |
| CrewAI | 3.25 | Scalability (4) |
| MetaGPT | 3.00 | Quality Assurance (4) |
| Cursor | 2.50 | Scalability (3) |
| Gas Town | 3.00 | State Management (4) |
| AutoGen/AG2 | 2.75 | Mode Adaptability (3) |
| Citadel | 2.75 | State Mgmt + QA + Scalability (3) |
| OAI SDK | 2.50 | Scalability + QA (3) |
| oh-my-cc | 2.00 | -- |
| Overstory | 1.50 | -- |

### Operational Quality (avg across 3 dimensions)

| System | Avg | Best Dimension |
|--------|-----|----------------|
| Cursor | 3.67 | Setup Complexity (5) |
| Spectrum | 4.00 | All dimensions (4) |
| CrewAI | 3.33 | Observability (4) |
| LangGraph | 3.33 | Observability (4) |
| OAI SDK | 3.33 | Observability (4) |
| Gas Town | 3.00 | Setup Complexity (4) |
| Citadel | 2.67 | Setup Complexity (4) |
| oh-my-cc | 2.33 | Setup Complexity (4) |
| AutoGen/AG2 | 2.67 | Setup + Observability (3) |
| MetaGPT | 2.33 | Observability (3) |
| Overstory | 2.33 | Setup Complexity (5) |

---

## Key Findings

### 1. Spectrum leads but is not dominant in every dimension

Spectrum scores highest overall (4.50) with sole leadership in 6 of 12 dimensions: Conflict Prevention, Failure Recovery, Quality Assurance, Mode Adaptability, Cost Awareness, and Task Decomposition (tied with MetaGPT). But it ties or trails on:
- **State Management**: LangGraph matches Spectrum's 5/5 with checkpoint-based time-travel
- **Knowledge Sharing**: CrewAI's three-tier memory (short/long/entity) is more sophisticated
- **Setup Complexity**: Cursor (5/5) and Overstory (5/5) are simpler to start with
- **Observability**: Four systems tie at 4/5 (CrewAI, LangGraph, OpenAI SDK alongside Spectrum)

### 2. File ownership is Spectrum's unique advantage

No other system in this evaluation enforces file-level conflict prevention. Frameworks operate at a higher abstraction (task outputs, state channels). Commercial systems rely on single-agent serialization. Spectrum's file ownership matrix, verified by the Politico and enforced at drop time, eliminates a class of merge conflicts that other systems must handle post-hoc.

### 3. Typed failure recovery is rare

Only Spectrum classifies failures (transient/logical/structural/environmental/conflict) with distinct recovery paths per type. LangGraph's checkpoint-based replay is robust but untyped. Most systems offer retry-or-fail. The circuit breaker (2 failures = auto-escalate) is unique to Spectrum.

### 4. The accessibility-vs-depth tradeoff is real

Commercial systems (Cursor 2.92, OpenAI SDK 2.67) score lower on coordination but higher on setup complexity. This is not a flaw -- it is a deliberate design choice for broad market adoption. A protocol that requires reading 3,700 lines of spec will never compete on accessibility with "download IDE, start coding."

### 5. Frameworks occupy the middle ground

The four frameworks (3.58-2.83 range) provide general-purpose multi-agent coordination without domain-specific optimization. They are more portable than CLAUDE.md protocols (not locked to Claude Code) but less specialized for the coding-agent use case.

### 6. The Claude Code ecosystem shows a maturity gradient

From Overstory (1.75, workflow config) through Gas Town (3.25, pioneer coordination) to Spectrum (4.50, full protocol), the ecosystem shows progressive formalization. Gas Town pioneered patterns (HOOK.md, mailboxes) that Spectrum formalized. This suggests the ecosystem is converging toward more structured coordination.

---

## What Spectrum Should Learn From Others

| System | Lesson | Dimension |
|--------|--------|-----------|
| LangGraph | Time-travel debugging (rollback to any state version) | State Management |
| CrewAI | Three-tier memory with RAG-based long-term retrieval | Knowledge Sharing |
| Cursor | Zero-config setup -- AI as invisible infrastructure | Setup Complexity |
| OpenAI SDK | Structured tracing with spans for every agent action | Observability |
| MetaGPT | SOP-based role pipeline produces intermediate artifacts (PRDs, design docs) | Task Decomposition |
| Gas Town | Real-time mailbox communication (vs Spectrum's async-only) | Communication |

---

## Methodology Limitations

1. **Self-evaluation bias**: Spectrum is evaluated by a system running on Spectrum. Scores were cross-validated against published documentation and architectural evidence, but unconscious bias toward familiar mechanisms is possible.

2. **Documentation vs. reality**: Scores are based on documented capabilities, not live testing. A system's documented 5/5 feature may be buggy in practice.

3. **Scope mismatch**: oh-my-claudecode and Overstory are not multi-agent coordination protocols. Their low scores reflect evaluating a fish on tree-climbing ability. They excel at their intended purpose.

4. **Point-in-time**: All systems are actively evolving. Scores reflect documented state as of April 2026.

5. **Single rubric**: The 12 dimensions were derived from multi-agent benchmarks and harness engineering. A different rubric (e.g., weighted toward developer experience) would produce different rankings.

---

## Detailed Scores

Full per-system breakdowns with evidence are in the group reports:
- [Claude Code Ecosystem](group-claude-code.md) -- Spectrum, Gas Town, oh-my-claudecode, Citadel, Overstory
- [General Frameworks](group-frameworks.md) -- CrewAI, LangGraph, AutoGen/AG2, MetaGPT
- [Commercial Systems](group-commercial.md) -- Cursor Agents, OpenAI Agents SDK

Machine-readable scores: [scores.json](scores.json)
