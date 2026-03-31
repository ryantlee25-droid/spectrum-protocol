# Installation

Spectrum Protocol requires no dependencies, no build step, and no database. It runs entirely as configuration files for Claude Code.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and working
- A `~/.claude/` directory (created automatically by Claude Code)
- A `~/.claude/agents/` directory (create it if it doesn't exist)
- A `~/.claude/hooks/` directory (create it if it doesn't exist)

## Steps

### 1. Copy the protocol files

```bash
# From the spectrum-protocol repository root:
cp spectrum/CLAUDE.md ~/.claude/CLAUDE.md
cp spectrum/SPECTRUM-OPS.md ~/.claude/SPECTRUM-OPS.md
cp spectrum/SPECTRUM.md ~/.claude/SPECTRUM.md
```

**Note:** If you already have a `~/.claude/CLAUDE.md`, back it up first. Spectrum's CLAUDE.md replaces it entirely -- it includes routing rules, model assignments, and the full protocol reference.

### 2. Copy agent definitions

```bash
mkdir -p ~/.claude/agents
cp agents/*.md ~/.claude/agents/
```

This installs all 14 agent definitions (Gold, Blue, Howler, White, Gray, Orange, Copper, Obsidian, Brown, Violet, Politico, Helldiver, Primus, Green).

### 3. Copy tooling

```bash
mkdir -p ~/.claude/hooks
cp tools/seam_check.py ~/.claude/hooks/seam_check.py
```

The seam check tool is used by Gold during the Pax phase to cross-reference seams and assumptions across Howler debriefs.

### 4. Verify

Start a new Claude Code session and ask:

```
What agents do you have available?
```

You should see the full Spectrum roster listed. Then try:

```
Plan and build [your feature] in parallel.
```

Gold will activate and begin the muster phase.

## That's It

No `npm install`. No `pip install`. No `go build`. No environment variables. No daemon to run.

The protocol lives in your `~/.claude/` directory as plain markdown files. Claude Code reads them on every session start.

## Updating

To update Spectrum, pull the latest version of this repository and re-copy the files:

```bash
cd spectrum-protocol
git pull
cp spectrum/CLAUDE.md ~/.claude/CLAUDE.md
cp spectrum/SPECTRUM-OPS.md ~/.claude/SPECTRUM-OPS.md
cp spectrum/SPECTRUM.md ~/.claude/SPECTRUM.md
cp agents/*.md ~/.claude/agents/
cp tools/seam_check.py ~/.claude/hooks/seam_check.py
```

## Uninstalling

Remove the Spectrum files:

```bash
rm ~/.claude/CLAUDE.md
rm ~/.claude/SPECTRUM-OPS.md
rm ~/.claude/SPECTRUM.md
rm ~/.claude/hooks/seam_check.py
rm ~/.claude/agents/{gold,blue,howler,white,gray,orange,copper,obsidian,brown,violet,politico,helldiver,primus,green}.md
```

This leaves your `~/.claude/` directory intact for standard Claude Code usage.
