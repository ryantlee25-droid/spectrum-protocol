# Platform Opportunity Analysis: Claude Code & API Cost Levers

**Spectrum**: cost-v2-0401
**Howler**: H2-platform
**Date**: 2026-04-01
**Sources**: Claude API documentation, Claude Code architecture, Anthropic pricing, platform capabilities

---

## Executive Summary

This document catalogs cost optimization opportunities available through Claude Code platform features, Claude API capabilities, and Anthropic pricing mechanisms. These are "platform levers" -- optimizations that exploit the specific capabilities of the infrastructure Spectrum runs on, rather than protocol-level design changes. Several of these represent significant untapped savings.

---

## 1. Claude API Pricing Mechanisms

### 1.1 Prompt Caching (Anthropic Extended Thinking + Cache)

**Mechanism**: The Claude API supports prompt caching via cache control breakpoints. When the same prompt prefix is sent across multiple requests, subsequent requests pay only 10% of the normal input token rate for cached tokens. Cache lifetime is 5 minutes by default (extended to 1 hour with certain plans). Write cost: 25% premium on the first request.

**Current Spectrum usage**: Unknown. Claude Code may or may not leverage prompt caching internally. Spectrum does not explicitly structure prompts to maximize cache hits.

**Optimization opportunity**:

The system prompt structure for Howlers is:
1. CLAUDE.md (~6,000 tokens) -- identical across all Howlers
2. SPECTRUM-OPS.md or HOWLER-OPS.md (~12,000 or ~2,500 tokens) -- identical across all Howlers
3. CONTRACT.md (~3,500 tokens) -- identical across Howlers in same spectrum
4. Task-specific content (~500-2,000 tokens) -- unique per Howler

If items 1-3 are placed at the top of the prompt (before task-specific content), and cache control breakpoints are set after item 3, then:
- First Howler pays full rate + 25% write premium on items 1-3: ~22,000 tokens at $3.75/M = $0.083
- Subsequent 4 Howlers pay cached rate on items 1-3: ~22,000 tokens at $0.30/M = $0.026 (4x = $0.026)
- Savings vs. no caching: 5 Howlers at $3/M = $0.330 vs. $0.083 + $0.026 = $0.109
- **Net savings: $0.22 per 5-Howler run on system prompt alone**

**Additional caching surfaces**:
- Quality gate agents (White, Gray, /diff-review) share the same system prompt prefix. 15 quality gate invocations across 5 Howlers = significant cache opportunity.
- Gold muster and Gold Pax share the same CLAUDE.md + SPECTRUM-OPS.md prefix.

**Total estimated savings**: $0.30-0.50 per 5-Howler run across all agents.

**Impact**: high
**Effort**: Medium -- requires ensuring prompt structure places cacheable content first, and that Claude Code is configured to use API-level caching.

### 1.2 Batch API (50% Discount)

**Mechanism**: The Claude Batch API processes requests asynchronously with a 50% discount on both input and output tokens. Results are returned within 24 hours (typically much faster). The trade-off is latency: no streaming, no real-time interaction.

**Current Spectrum usage**: None. All Spectrum agents are interactive (real-time Claude Code sessions).

**Optimization opportunity**: Several Spectrum phases do not require real-time interaction:
- **Quality gates (White, Gray, /diff-review)**: These read a diff and produce a report. No interactive tool use needed if the diff and context are pre-collected. Could be submitted as batch requests.
- **Copper (commit/PR creation)**: Mechanical -- could be a batch request with pre-collected context.
- **Brown (LESSONS.md drafting)**: Post-merge, no time pressure.
- **Gold Pax**: Reads artifacts and produces PAX-PLAN.md. Could be batch if the human is not waiting for real-time output.

**Estimated savings at 50% discount**:
- Quality gates (15 invocations): ~$0.70 normally -> ~$0.35 in batch = $0.35 saved
- Copper (5 invocations): ~$0.01 normally -> negligible savings
- Brown: ~$0.04 normally -> ~$0.02 = $0.02 saved
- Gold Pax: ~$1.33 normally -> ~$0.67 = $0.66 saved (but at latency cost)

**Total estimated savings**: $0.35-1.03 per 5-Howler run, depending on which agents are moved to batch.

**Impact**: high
**Effort**: High -- requires building a batch submission pipeline and handling async result retrieval. Quality gates and Copper are the most practical candidates (no human waiting). Gold Pax is the highest-value candidate but humans usually want real-time Pax output.

### 1.3 Extended Thinking Token Costs

**Mechanism**: Claude's extended thinking tokens are billed at the same rate as output tokens. When extended thinking is enabled, the model generates internal reasoning tokens before producing the visible output. These thinking tokens can be substantial (3,000-10,000+ per response for complex tasks).

**Current Spectrum usage**: Extended thinking is likely enabled by default in Claude Code sessions. The TOKEN-OPTIMIZATION.md cost model includes ~3,000 reasoning tokens in Gold output but may undercount for complex sessions.

**Optimization opportunity**: For agents where extended thinking adds little value (Copper, Brown, simple quality gate invocations), disabling or limiting extended thinking could save output tokens. The Claude API supports `max_tokens_to_think` to cap thinking budget.

**Estimated savings**: If thinking tokens represent 15-20% of total output and could be disabled for mechanical agents:
- Copper: ~500 thinking tokens x 5 invocations x $4/M = $0.01
- Brown: ~1,000 thinking tokens x $4/M = $0.004
- Simple White/Gray gates: ~1,000 thinking tokens x 10 invocations x $15/M = $0.15

**Total: ~$0.15 per run**. Modest, but zero-effort if Claude Code exposes a thinking budget control.

**Impact**: low-medium
**Effort**: Low if Claude Code exposes the control; N/A if not.

---

## 2. Claude Code Platform Features

### 2.1 Tool Result Caching

**Mechanism**: Claude Code caches tool results within a session. If an agent reads the same file twice, the second read may use a cached result (implementation-dependent). This is distinct from API-level prompt caching.

**Optimization opportunity**: Spectrum Howlers often read the same files multiple times during a session: CONTRACT.md at dispatch, then again during scope alignment checks, then again during completion verification. If tool result caching is active, these re-reads are free.

**Action item**: Verify whether Claude Code implements tool result caching. If yes, no action needed. If no, consider restructuring Howler prompts to read artifacts once and reference the cached content in subsequent turns.

**Impact**: low (likely already happening)
**Effort**: Verification only

### 2.2 Conversation Compaction

**Mechanism**: Claude Code automatically compacts conversation history when the context window approaches capacity. Old messages are summarized into a compact form to free context space. This happens transparently.

**Optimization opportunity**: Compaction is a double-edged sword:
- **Good**: Prevents context overflow and keeps sessions functional
- **Bad**: Compaction loses detail. If important context is compacted, the agent may repeat work or make contradictory decisions.

Spectrum can influence compaction by keeping early messages concise. If the Howler drop prompt is compact (per T1-A HOWLER-OPS.md, T1-D HOOK.md compactness), there is less pressure on the context window and compaction happens later (or not at all), preserving full fidelity.

**Impact**: medium (indirect -- compaction quality affects Howler accuracy, not just cost)
**Effort**: Already captured by T1-A and T1-D

### 2.3 Model Selection Per Agent

**Mechanism**: Claude Code sessions can be started with a specific model selection. The `--model` flag or `ANTHROPIC_MODEL` environment variable controls which model the session uses. Different agents can use different models.

**Current Spectrum usage**: The model assignment table in CLAUDE.md specifies models per agent type. Copper and Brown use Haiku; all others use Sonnet or Opus.

**Optimization opportunity**: The current assignments are already cost-optimized based on the gold-eval-0331 evaluation. The remaining opportunity is:

1. **Gold on Sonnet instead of Opus**: Already implemented per gold-eval-0331. Saves ~$2.00 per 5-Howler run (the single largest optimization in Spectrum's history).
2. **Quality gate agents on Haiku**: White, Gray, and /diff-review currently run on Sonnet. Could any run on Haiku?
   - White: Sonnet is justified -- subtle bug detection requires reasoning depth.
   - Gray: Sonnet is justified -- test diagnosis and generation require reasoning.
   - /diff-review: **Possible Haiku candidate**. Security-focused diff review against a checklist. If the review is structured (checklist-driven, not open-ended reasoning), Haiku may be sufficient.

**Estimated savings if /diff-review moves to Haiku**: 5 invocations x ($0.05 Sonnet - $0.01 Haiku) = $0.20 per 5-Howler run.

**Impact**: medium
**Effort**: Low -- change model assignment and validate quality.

### 2.4 Session Duration and Turn Count

**Mechanism**: Claude Code sessions accumulate billed input tokens with each turn (the "sliding window tax" from TOKEN-OPTIMIZATION.md Zone 2). Each turn re-sends the full conversation history. A 15-turn Howler session bills ~120K input tokens total, even though only ~20K of unique content was generated.

**Optimization opportunity**: Reduce Howler turn count. Each eliminated turn saves ~8-10K input tokens (the accumulated history sent to the API). If Howlers can be designed to work in fewer, larger turns:
- 15 turns -> 10 turns: ~40-50K fewer input tokens per Howler = $0.12 saved
- 5 Howlers: $0.60 saved per run

**How to reduce turns**:
1. Batch multiple file writes into single tool calls where possible
2. Combine read + modify into single-turn operations
3. Pre-collect all needed context before starting modifications (read phase -> write phase)
4. Use the `/compact` command to manually trigger compaction at strategic points

**Impact**: high
**Effort**: Medium -- requires changes to Howler prompt instructions to encourage batch operations.

---

## 3. Infrastructure and Operational Savings

### 3.1 Worktree Reuse Across Spectrum Runs

**Mechanism**: Git worktrees are created fresh for each spectrum run and deleted afterward. Creating and verifying worktrees involves multiple git operations and Gold reasoning tokens.

**Optimization opportunity**: For sequential spectrum runs on the same base branch, worktrees could be recycled:
1. After a spectrum completes, keep worktrees but reset branches to the new base commit
2. Skip worktree creation in the next spectrum's muster phase
3. Only create new worktrees when the count changes

**Estimated savings**: ~$0.05-0.10 per run (Gold's worktree creation reasoning + shell operations). Modest, but simplifies muster.

**Impact**: low
**Effort**: Low

### 3.2 Pre-built Agent Prompt Templates

**Mechanism**: Instead of Gold generating drop prompts by reading MANIFEST.md + CONTRACT.md and composing a prompt in real-time (Opus/Sonnet output tokens), pre-build prompt templates that Gold fills in with variables. The template is a file; Gold only generates the variable values.

**Estimated savings**: ~1,000-2,000 fewer Gold output tokens per Howler drop = $0.075-0.15 per Howler x 5 = $0.375-0.75 per 5-Howler run if Gold is Opus. With Gold on Sonnet: $0.075-0.15 per run. Already less impactful post-gold-eval.

**Impact**: low-medium (was medium-high when Gold was Opus)
**Effort**: Low -- create template files referenced by Gold during dispatch

### 3.3 Parallel Agent Session Management

**Mechanism**: Claude Code sessions are currently managed manually (or via spectrum protocol scripts). Each agent session is a separate Claude Code process.

**Optimization opportunity**: If agent sessions could be managed more efficiently:
1. **Connection pooling**: Reuse API connections across agent sessions
2. **Parallel request batching**: Submit multiple agent requests in a single API batch
3. **Session lifecycle hooks**: Automatic cleanup when agents complete, freeing resources

These are infrastructure-level optimizations that depend on Claude Code's implementation.

**Impact**: low (implementation-dependent)
**Effort**: High (requires Claude Code platform work)

---

## 4. Anthropic Pricing Structure Opportunities

### 4.1 Volume Discounts and Tier Pricing

**Mechanism**: Anthropic offers volume-based pricing tiers for high-usage customers. As of March 2026:
- Standard tier: list prices (as in CONTRACT.md)
- Usage-based tier commitment: potentially 10-20% discounts at sustained high volume
- Enterprise agreements: custom pricing

**Relevance to Spectrum**: A single 5-Howler spectrum run costs ~$9.43. A team running 3-5 spectrums per week would spend ~$150-240/month on API costs. This is below typical volume discount thresholds but worth monitoring as usage scales.

**Impact**: low (current usage level)
**Effort**: None (monitoring only)

### 4.2 Token-Efficient Model Versions

**Mechanism**: Anthropic periodically releases model versions that are more token-efficient (same quality, fewer tokens) or cheaper (lower per-token pricing). Claude 3.5 Sonnet was 5x cheaper than Claude 3 Opus at equivalent quality for many tasks.

**Relevance to Spectrum**: Spectrum's cost model is inherently tied to the current pricing table. Every model generation change resets the cost baseline. The most impactful "cost optimization" may simply be waiting for the next model generation.

**Historical precedent**:
- Sonnet replacing Opus for Gold (gold-eval-0331): 91% cost reduction on Gold phases
- Haiku price drops since initial release

**Action item**: Update cost models when new pricing is announced. Maintain the per-phase cost table in TOKEN-OPTIMIZATION.md so the impact of pricing changes is immediately visible.

**Impact**: high (but not actionable -- depends on Anthropic)
**Effort**: Monitoring + updating cost models

---

## Techniques Transferable to Spectrum -- Summary

| # | Technique | Impact | Savings Est. (5H) | Effort | Already in Backlog? |
|---|-----------|--------|-------------------|--------|-------------------|
| 1 | Prompt caching (cache-friendly prompt structure) | high | $0.30-0.50 | Medium | No |
| 2 | Batch API for quality gates + Copper | high | $0.35-1.03 | High | No |
| 3 | /diff-review on Haiku | medium | $0.20 | Low | No |
| 4 | Reduce Howler turn count (batch operations) | high | $0.60 | Medium | No |
| 5 | Extended thinking budget control | low-medium | $0.15 | Low | No |
| 6 | Pre-built agent prompt templates | low-medium | $0.08-0.15 | Low | Partially (T3-A) |
| 7 | Worktree reuse across runs | low | $0.05-0.10 | Low | No |
| 8 | Monitor volume discounts | low | TBD | None | No |

**Top 3 new opportunities not in existing backlog:**
1. Batch API for non-interactive agents (quality gates, Copper, Brown) -- up to $1.03 savings
2. Howler turn count reduction through batch operations -- $0.60 savings
3. Prompt caching optimization with cache-friendly prompt ordering -- $0.30-0.50 savings
