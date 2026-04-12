# Installation

Spectrum requires no dependencies, no build step, and no database. It runs as configuration files for Claude Code.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and working
- A `~/.claude/` directory (created automatically by Claude Code)

## One-Line Install

```bash
curl -fsSL https://raw.githubusercontent.com/ryantlee25-droid/spectrum-protocol/main/install.sh | bash
```

## Manual Install

### 1. Copy protocol files

```bash
cp spectrum/CLAUDE.md ~/.claude/CLAUDE.md
cp spectrum/SPECTRUM.md ~/.claude/SPECTRUM.md
```

**If you already have a `~/.claude/CLAUDE.md`**, back it up first:

```bash
cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup
cp spectrum/CLAUDE.md ~/.claude/CLAUDE.md
```

Then merge any custom sections from your backup into the bottom of the new file.

Alternatively, use a project-level `CLAUDE.md` at your repo root — Claude Code reads both.

### 2. Copy agent definitions

```bash
mkdir -p ~/.claude/agents
cp agents/*.md ~/.claude/agents/
```

This installs 10 agent definitions: Gold, Blue, Workers (Howlers), White, Gray, Orange, Copper, plus auxiliaries (Helldivers, Primus, Greens).

### 3. Verify

Start a new Claude Code session and ask:

```
What agents do you have available?
```

You should see the Spectrum roster. Then try:

```
Plan and build [your feature] in parallel.
```

## That's It

No `npm install`. No `pip install`. No environment variables. No daemon.

The protocol lives in `~/.claude/` as plain markdown. Claude Code reads it on every session start.

## Optional: Memory Integration

For additional efficiency (-25% time), set up [Tages](https://github.com/ryantlee25-droid/tages) for project memory. Spectrum agents automatically use memory briefs when available.

## Updating

```bash
cd spectrum-protocol
git pull
cp spectrum/CLAUDE.md ~/.claude/CLAUDE.md
cp spectrum/SPECTRUM.md ~/.claude/SPECTRUM.md
cp agents/*.md ~/.claude/agents/
```

## Uninstalling

```bash
rm ~/.claude/CLAUDE.md
rm ~/.claude/SPECTRUM.md
rm ~/.claude/agents/{golds,blues,howlers,whites,grays,oranges,coppers,helldivers,primus,greens}.md
```
