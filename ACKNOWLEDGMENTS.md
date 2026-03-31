# Acknowledgments

## Naming Theme

The agent names in Spectrum Protocol are drawn from the **Color caste system** in [Red Rising](https://www.piercebrown.com/) by **Pierce Brown**. The books imagine a society stratified into Colors -- Golds who rule, Obsidians who fight, Coppers who administrate, and so on. Spectrum borrows this taxonomy because it makes agent roles instantly legible: when Gold drops Howlers, the hierarchy and intent are clear from the names alone.

Red Rising is a work of fiction and Spectrum Protocol is not affiliated with Pierce Brown or his publishers. The Color names are used as a thematic convention, not a claim of association.

## Architectural Inspiration

Spectrum Protocol would not exist without [**Gas Town**](https://github.com/steveyegge/gastown) by **Steve Yegge**. Gas Town was the first system to demonstrate that Claude Code's parallel sub-agents need persistent state, structured communication, and health monitoring to work reliably at scale.

Key patterns Spectrum inherited from Gas Town:
- **Persistent state files** (HOOK.md) that survive agent death and enable crash recovery
- **The convoy concept** -- a coordinated group of parallel workers with a shared mission
- **Structured inter-agent communication** (mailboxes/debriefs) instead of conversation-thread-only context
- **Health checks and failure detection** as first-class protocol concerns

Where Gas Town is a compiled Go binary with a daemon architecture (built for scale), Spectrum took the opposite approach: a protocol expressed entirely as CLAUDE.md configuration files (built for accessibility). Both approaches are valid for different contexts.

## Platform

Spectrum runs on [**Claude Code**](https://docs.anthropic.com/en/docs/claude-code) by **Anthropic**. The protocol depends on Claude Code's native primitives: sub-agent spawning, git worktree isolation, background execution, and the `~/.claude/` configuration system. Without these primitives, Spectrum's coordination model would not be possible.

## Ecosystem Influences

The broader Claude Code ecosystem has produced innovations that influenced Spectrum v4.0:

- [**Overstory**](https://github.com/cyanheads/claude-code-CLAUDE.md) -- demonstrated that well-structured CLAUDE.md files can encode sophisticated multi-agent behavior without any compiled tooling
- [**Citadel**](https://github.com/DigitalBuild-AU/claude-code-CLAUDE.md) -- explored fortress-pattern coordination with strict boundary enforcement, validating the file ownership concept
- [**metaswarm**](https://github.com/Ishaan-Datta/metaswarm) -- pioneered competitive execution (multiple agents solving the same task, best result wins) and atomic learning capture, influencing Spectrum's per-PR self-reflect pattern
- [**oh-my-claudecode**](https://github.com/nicekid1/oh-my-claudecode) -- proved massive community demand for Claude Code configuration sharing (17k+ stars), demonstrating that the CLAUDE.md ecosystem is real and growing

## Research

The evaluation methodology was informed by academic work on multi-agent systems:
- Google/MIT research on self-organized agents (establishing the 3-6 agent sweet spot)
- MASFT/MAST frameworks for multi-agent software testing
- AgentCoder's test-driven approach to code generation with specialized agents

## Tools

- Claude Opus, Sonnet, and Haiku by Anthropic -- the models that power every agent in the protocol
- Git worktrees -- the isolation mechanism that makes parallel execution safe
