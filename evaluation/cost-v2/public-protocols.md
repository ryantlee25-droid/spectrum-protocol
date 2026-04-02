# Public Protocol Cost Optimization Techniques

**Spectrum**: cost-v2-0401
**Howler**: H1-public-protocols
**Date**: 2026-04-01
**Sources**: AGENTIC-LANDSCAPE.md (28 systems), COMPETITIVE-AUDIT.md, academic literature

---

## Executive Summary

This document catalogs cost optimization techniques observed in public multi-agent protocols, open-source frameworks, commercial platforms, and academic systems. Each technique is assessed for transferability to Spectrum Protocol. The focus is on techniques NOT already in Spectrum's T1-T3 backlog.

---

## 1. Context Window Management Techniques

### 1.1 Selective Context Injection (CrewAI, LangGraph)

**What**: Instead of injecting full system prompts and all coordination artifacts into every agent turn, inject only the context relevant to the current step. CrewAI's three-tier memory (short-term RAG, long-term SQLite, entity memory) queries each tier independently and only surfaces relevant fragments.

**How it saves cost**: Reduces per-turn input tokens by 30-60% compared to full-context injection. An agent working on file parsing does not need authentication contract details in its context.

**Impact**: high
**Estimated savings for Spectrum**: 15-25% reduction in Howler input tokens (~$0.15-0.30 per 5-Howler run) if applied to Howler session management. Requires changes to how SPECTRUM-OPS.md and CONTRACT.md are injected.

**Transferability to Spectrum**: Medium-high. Spectrum already partially does this with reaping mode's simplified CONTRACT.md. The principle could be extended: Howlers receive only their own task scope + relevant contract slice + HOWLER-OPS.md (already proposed as T1-A). The gap is that Spectrum currently injects the full system prompt (CLAUDE.md + SPECTRUM-OPS.md) on every turn due to Claude Code's architecture. Addressing this requires either per-agent CLAUDE.md sections (T3-B) or a context-aware injection layer.

### 1.2 Compressed Artifact Formats (MetaGPT, Magentic-One)

**What**: Replace verbose markdown narratives with structured data formats (JSON, YAML) for inter-agent communication. MetaGPT's document-as-protocol approach uses structured schemas. Magentic-One's ledger uses a compact fact/task/question format rather than free-text summaries.

**How it saves cost**: Structured formats are 40-60% more token-efficient than equivalent markdown prose. A YAML DAG is more compact than a prose description of the same dependency graph.

**Impact**: medium
**Estimated savings for Spectrum**: ~$0.10-0.20 per run if MANIFEST.md DAG sections, debriefs, and HOOK.md used compact YAML instead of mixed markdown/prose. Gold's conciseness directive (T1-E) partially addresses this but does not mandate format changes.

**Transferability to Spectrum**: High. Spectrum already uses YAML frontmatter in debriefs. Extending YAML/JSON to HOOK.md status sections, DAG definitions, and completion verification would reduce tokens without losing information. Risk: reduced human readability of artifacts.

### 1.3 Progressive Context Loading (Augment Code Intent)

**What**: Augment's 400K+ file context engine does not load all context upfront. It uses semantic dependency analysis to load context progressively as the agent's work narrows. Early in execution, the agent gets a broad overview; as it focuses on specific files, deeper context for those files is loaded while unrelated context is evicted.

**How it saves cost**: Avoids the "sliding window tax" where accumulated context from early turns is billed on every subsequent turn. By evicting irrelevant context, total billed input tokens can be 20-40% lower across a multi-turn session.

**Impact**: high
**Estimated savings for Spectrum**: Potentially $0.20-0.40 per 5-Howler run if Howler sessions could evict early-turn context that is no longer relevant. The "sliding window tax" is Zone 2 in TOKEN-OPTIMIZATION.md (~600K Sonnet input tokens for 5 Howlers).

**Transferability to Spectrum**: Low-medium. Claude Code does not expose context eviction APIs. The Claude API supports conversation pruning, but Claude Code manages the conversation window internally. This technique would require either Claude Code platform changes or a custom session management wrapper.

---

## 2. Model Routing and Tiering Techniques

### 2.1 Task-Complexity-Based Model Selection (Cursor 2.0, Factory)

**What**: Route simple tasks (file moves, boilerplate generation, commit messages) to cheaper/faster models and complex tasks (architectural decisions, security review) to more capable models. Cursor 2.0's competitive execution pattern assigns the same task to multiple models and selects the best result — but it also routes known-simple tasks to faster models automatically.

**How it saves cost**: Using Haiku for tasks that do not require Sonnet reasoning saves 73% on input and 73% on output per task. If 30% of Howler sub-tasks are Haiku-eligible, the savings are significant.

**Impact**: high
**Estimated savings for Spectrum**: $0.30-0.60 per 5-Howler run if mechanical sub-tasks within Howler sessions (file creation scaffolding, git operations, test running) could be routed to Haiku while reasoning-heavy sub-tasks stay on Sonnet.

**Transferability to Spectrum**: Low. Claude Code does not support mid-session model switching. A Howler session runs on one model from start to finish. Achieving this would require either Claude Code platform support for model routing per tool call, or decomposing Howler work into micro-tasks with different model assignments (which increases coordination overhead).

### 2.2 Confidence-Based Routing (PydanticAI, Google ADK)

**What**: If the agent's confidence in its output is above a threshold, skip expensive validation steps. PydanticAI's typed outputs enable mechanical confidence checks: if the output conforms to the expected schema perfectly, skip the review step. Google ADK's built-in evaluation tooling provides confidence scores per agent output.

**How it saves cost**: Eliminates unnecessary validation for high-confidence outputs. If 50% of quality gate runs could be skipped due to high confidence, the savings are substantial.

**Impact**: medium
**Estimated savings for Spectrum**: $0.10-0.25 per 5-Howler run. This is already partially captured by T2-B (Confidence-Tiered Pax Validation). The additional opportunity is extending confidence-based skipping to White and Gray quality gates, not just Pax.

**Transferability to Spectrum**: Medium. T2-B already proposes this for Pax. Extending to quality gates requires a mechanical confidence signal (not just self-reported). Possible signals: test pass rate, type-check results, diff size. Risk: skipping quality gates reduces the safety net that distinguishes Spectrum from competitors.

---

## 3. Coordination Overhead Reduction

### 3.1 Pull-Based Work Queues (Gas Town, oh-my-claudecode)

**What**: Instead of a coordinator spending tokens to plan, dispatch, and monitor each agent, agents pull work from a shared queue. The coordinator's role is reduced to populating the queue and monitoring for stalls. Gas Town's GUPP principle maximizes throughput by having agents continuously execute available work.

**How it saves cost**: Eliminates coordinator output tokens for per-agent dispatch prompts. Gas Town has no MANIFEST.md or per-agent drop prompts — agents self-assign from the queue. Estimated coordinator token savings: 50-70% compared to push-based dispatch.

**Impact**: medium
**Estimated savings for Spectrum**: $0.30-0.50 per 5-Howler run if Gold's dispatch overhead could be reduced. Gold currently generates ~4,500 output tokens for MANIFEST.md + ~500 tokens per Howler drop prompt. Pull-based dispatch could eliminate the per-Howler drop prompts.

**Transferability to Spectrum**: Low. Spectrum's value proposition is pre-flight coordination — file ownership, frozen contracts, DAG-ordered dispatch. Pull-based dispatch trades coordination guarantees for cost savings. This is a philosophical trade-off, not just a technical one. However, a hybrid approach is possible: pre-flight contracts (keep) + pull-based execution within contract boundaries (new).

### 3.2 Implicit Coordination via File System (parallel-worktrees, incident.io pattern)

**What**: Use git worktree isolation as the sole coordination mechanism. Each agent works in its own worktree on its own branch. No explicit contracts or manifests. Conflicts are discovered at merge time and resolved then.

**How it saves cost**: Eliminates all coordination artifacts (MANIFEST.md, CONTRACT.md, CHECKPOINT.json, seam checks). For a 5-Howler run, this saves ~$0.50-1.00 in Gold muster + Pax overhead.

**Impact**: high (cost), low (quality)
**Estimated savings for Spectrum**: $0.50-1.00 per run, but at the cost of Spectrum's D4=5 workflow rigor score (its primary differentiator).

**Transferability to Spectrum**: Not recommended as a replacement. However, the technique validates that for pure-create tasks with no shared interfaces, coordination overhead can be safely reduced. Spectrum's reaping mode already moves in this direction. The lesson: be more aggressive about activating reaping/nano mode when tasks qualify.

### 3.3 Stateless Coordinator Checkpoints (Citadel)

**What**: Citadel uses machine-verifiable phase conditions instead of a coordinator agent maintaining state across phases. Phase transitions are checked by a script, not by Gold re-reading artifacts and reasoning about them. The coordinator is "stateless" between phases — it reads only the checkpoint file and current phase conditions.

**How it saves cost**: Eliminates Gold's need to maintain conversational context across phases. Each phase starts fresh with only the checkpoint file and phase-specific inputs. Gold's context window never accumulates multi-phase history.

**Impact**: medium
**Estimated savings for Spectrum**: $0.15-0.30 per run by reducing Gold Pax input tokens (currently Zone 3 at ~65K tokens for 5-Howler). If Gold reads only CHECKPOINT.json + phase-specific inputs instead of accumulated conversation, input tokens drop significantly.

**Transferability to Spectrum**: Medium-high. Spectrum already uses CHECKPOINT.json for phase tracking. The gap is that Gold currently accumulates conversational context from muster through dispatch through pax. Making each Gold phase invocation independent (fresh session, reads only CHECKPOINT.json + phase-relevant artifacts) would reduce context accumulation. This requires restructuring Gold from a long-running session to multiple short sessions.

---

## 4. Quality Gate Optimization

### 4.1 Parallel Quality Gates with Early Termination (Augment Code Intent)

**What**: Augment's continuous Verifier runs in parallel with Specialists. If the Verifier detects a critical issue during execution (not after), it can signal the Specialist to stop and correct before completing. This prevents wasted tokens on work that will be rejected.

**How it saves cost**: Eliminates the "complete then reject then redo" cycle. If a Howler produces 15K output tokens but the result fails White review, that is 15K wasted tokens plus the retry cost. Early termination could catch issues at 5K tokens.

**Impact**: medium
**Estimated savings for Spectrum**: $0.05-0.15 per Howler that would otherwise fail quality gates. Depends on failure rate. If 20% of Howlers need revision after quality gates, savings are ~$0.10-0.30 per 5-Howler run.

**Transferability to Spectrum**: Low-medium. Would require running a lightweight linter/checker during Howler execution, not just after. Claude Code does not support mid-session injection of external feedback. Could be approximated by the scope alignment check (every 20 tool calls), enhanced with a mechanical check (e.g., run tsc --noEmit at the midpoint, not just at completion).

### 4.2 Tiered Review Depth (Factory, Copilot Workspace)

**What**: Not all changes need the same review depth. Factory applies different review intensities based on change type: new file creation gets a lighter review than modification of existing code. Copilot Workspace's code review agent gathers full project context only for complex PRs.

**How it saves cost**: Reduces quality gate tokens for low-risk changes. A pure documentation change does not need the same security-focused /diff-review as an authentication module change.

**Impact**: medium
**Estimated savings for Spectrum**: $0.05-0.15 per run. This is partially captured by T2-C (Conditional /diff-review by security surface). The additional opportunity is also tiering White review depth — lighter review for pure-create documentation files.

**Transferability to Spectrum**: High. T2-C already proposes this for /diff-review. Extending the principle to White (lighter review for non-code files) and Gray (skip test runs for documentation-only changes) is straightforward.

---

## 5. Caching and Deduplication

### 5.1 Prompt Caching (Claude API, OpenAI API)

**What**: Both Claude and OpenAI APIs support prompt caching — if the same prompt prefix is sent repeatedly, the cached portion is billed at a reduced rate. Claude's prompt caching charges 10% of the normal input rate for cache hits (90% savings on cached tokens).

**How it saves cost**: The system prompt (CLAUDE.md + SPECTRUM-OPS.md/HOWLER-OPS.md) is identical across all Howler sessions. If cached, the ~14K tokens of system prompt per Howler would cost $0.0042 instead of $0.042 per Howler. For 5 Howlers: $0.021 vs $0.210.

**Impact**: high
**Estimated savings for Spectrum**: $0.15-0.20 per 5-Howler run on system prompt caching alone. If CONTRACT.md and other shared artifacts are also cached across Howler sessions, savings could reach $0.25-0.35.

**Transferability to Spectrum**: Medium. Claude Code may already leverage prompt caching internally (the API supports it), but Spectrum does not explicitly design for cache-friendly prompt structures. Optimization: ensure common prefixes (system prompt, CONTRACT.md) appear first in Howler drop prompts before task-specific content. This maximizes cache hit rates.

### 5.2 Cross-Session Memory (CrewAI Long-Term Memory)

**What**: CrewAI stores successful task completions in a long-term SQLite database. When a similar task appears in a future session, the memory system retrieves the prior approach and result, allowing the agent to skip exploration and directly apply the known solution.

**How it saves cost**: Reduces token consumption on repeated or similar tasks. Spectrum runs often have repetitive patterns (e.g., quality gates follow the same protocol every time). If the quality gate "script" could be cached from prior runs, each gate invocation would require fewer reasoning tokens.

**Impact**: medium
**Estimated savings for Spectrum**: $0.05-0.15 per run, primarily from quality gate agents that follow identical protocols each time.

**Transferability to Spectrum**: Low-medium. LESSONS.md provides cross-spectrum learning at the strategic level, but not at the task-execution level. A task-level cache ("last time White reviewed a pure-create Howler, here was the checklist it used") could reduce White/Gray reasoning overhead. This is architecturally different from LESSONS.md and would require new infrastructure.

---

## 6. Architectural Patterns for Cost

### 6.1 Agentless Pipeline (UIUC Agentless)

**What**: The Agentless system (UIUC) achieves competitive SWE-Bench scores using a simple pipeline: localize → edit → validate, with NO multi-agent coordination. Each step uses a single LLM call. The system avoids the cost of coordination entirely.

**How it saves cost**: Eliminates all coordination overhead. A single-task solve costs ~$0.20-0.30 with Agentless vs. $0.57 with Spectrum Variant A (Full).

**Impact**: high
**Estimated savings for Spectrum**: N/A — this is a different architecture, not an optimization to Spectrum. However, the lesson is: for single-task solves (SWE-bench individual tasks), Spectrum's coordination overhead may not be justified. Variant C (Bare Sonnet) is Spectrum's answer to this.

**Transferability to Spectrum**: Already captured by Variant C in the SWE-bench cost model. The additional lesson: Spectrum should more aggressively route single-file, single-concept tasks to Variant C rather than defaulting to Variant A or B.

### 6.2 Document-as-Protocol (MetaGPT)

**What**: MetaGPT uses structured documents (PRD, design doc, API spec) as the coordination protocol between agents. Documents serve double duty: they are both the deliverable and the communication channel. No separate coordination artifacts are needed.

**How it saves cost**: Eliminates the token overhead of separate MANIFEST.md, CONTRACT.md, and CHECKPOINT.json by embedding coordination information in the deliverables themselves.

**Impact**: low-medium
**Estimated savings for Spectrum**: $0.05-0.10 per run. Modest because Spectrum's coordination artifacts (MANIFEST.md, CONTRACT.md) serve a different purpose than MetaGPT's documents — they encode ownership and interface contracts, not just task descriptions.

**Transferability to Spectrum**: Low. Spectrum's separation of deliverables from coordination artifacts is intentional — it prevents coordination information from polluting deliverables and vice versa. The MetaGPT approach works for waterfall-style flows but not for Spectrum's parallel dispatch model where multiple agents need to read coordination information without reading each other's deliverables.

---

## Techniques Transferable to Spectrum — Summary

| # | Technique | Source | Impact | Savings Est. (5H) | Effort | Already in Backlog? |
|---|-----------|--------|--------|-------------------|--------|-------------------|
| 1 | Selective context injection | CrewAI, LangGraph | high | $0.15-0.30 | High | Partially (T1-A, T3-B) |
| 2 | Compressed artifact formats (YAML) | MetaGPT, Magentic-One | medium | $0.10-0.20 | Low | Partially (T1-E) |
| 3 | Prompt caching optimization | Claude API | high | $0.15-0.35 | Medium | No |
| 4 | Stateless coordinator checkpoints | Citadel | medium | $0.15-0.30 | High | No |
| 5 | Confidence-based quality gate skipping | PydanticAI, ADK | medium | $0.10-0.25 | Medium | Partially (T2-B) |
| 6 | Tiered review depth (extend T2-C) | Factory, Copilot | medium | $0.05-0.15 | Low | Partially (T2-C) |
| 7 | Aggressive reaping/nano activation | parallel-worktrees | medium | $0.50-1.00 | Low | Partially (reaping mode) |
| 8 | Early termination on quality signals | Augment Intent | medium | $0.10-0.30 | High | No |
| 9 | Cache-friendly prompt structure | Claude API | medium | $0.05-0.10 | Low | No |
| 10 | Aggressive Variant C routing (SWE-bench) | Agentless (UIUC) | high | Context-dependent | Low | Partially (Variant C) |

**Top 3 new opportunities not in existing backlog:**
1. Prompt caching optimization (design prompts for maximum cache hits)
2. Stateless coordinator checkpoints (restructure Gold as short sessions)
3. Early termination on quality signals (mid-Howler mechanical checks)
