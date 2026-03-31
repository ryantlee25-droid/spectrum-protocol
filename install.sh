#!/usr/bin/env bash
set -euo pipefail

# Spectrum Protocol installer
# Usage: curl -fsSL https://raw.githubusercontent.com/ryantlee25-droid/spectrum-protocol/main/install.sh | bash

REPO="https://raw.githubusercontent.com/ryantlee25-droid/spectrum-protocol/main"
CLAUDE_DIR="$HOME/.claude"
AGENTS_DIR="$CLAUDE_DIR/agents"
HOOKS_DIR="$CLAUDE_DIR/hooks"

echo ""
echo "  ╔════════════════════════════════════════╗"
echo "  ║  Spectrum Protocol v4.0 — Installer    ║"
echo "  ║  Drop the Howlers.                     ║"
echo "  ╚════════════════════════════════════════╝"
echo ""

# Check prerequisites
if ! command -v claude &> /dev/null; then
    echo "  [!] Claude Code CLI not found."
    echo "      Install it first: https://docs.anthropic.com/en/docs/claude-code"
    echo ""
    exit 1
fi

echo "  [1/5] Checking directories..."
mkdir -p "$AGENTS_DIR"
mkdir -p "$HOOKS_DIR"

# Backup existing CLAUDE.md
if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
    echo "  [!] Existing CLAUDE.md found — backing up to CLAUDE.md.backup"
    cp "$CLAUDE_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md.backup"
    echo "      To merge your custom rules, edit ~/.claude/CLAUDE.md after install."
fi

echo "  [2/5] Downloading protocol files..."
curl -fsSL "$REPO/spectrum/CLAUDE.md" -o "$CLAUDE_DIR/CLAUDE.md"
curl -fsSL "$REPO/spectrum/SPECTRUM-OPS.md" -o "$CLAUDE_DIR/SPECTRUM-OPS.md"
curl -fsSL "$REPO/spectrum/SPECTRUM.md" -o "$CLAUDE_DIR/SPECTRUM.md"

echo "  [3/5] Downloading agent definitions (14 agents)..."
for agent in gold blue howler white gray orange copper obsidian brown violet politico helldiver primus green; do
    curl -fsSL "$REPO/agents/$agent.md" -o "$AGENTS_DIR/$agent.md"
done

echo "  [4/5] Downloading tooling..."
curl -fsSL "$REPO/tools/seam_check.py" -o "$HOOKS_DIR/seam_check.py"
chmod +x "$HOOKS_DIR/seam_check.py"

echo "  [5/5] Verifying installation..."
MISSING=0
for f in "$CLAUDE_DIR/CLAUDE.md" "$CLAUDE_DIR/SPECTRUM-OPS.md" "$CLAUDE_DIR/SPECTRUM.md" "$HOOKS_DIR/seam_check.py"; do
    if [ ! -f "$f" ]; then
        echo "  [!] Missing: $f"
        MISSING=1
    fi
done

AGENT_COUNT=$(ls "$AGENTS_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$AGENT_COUNT" -lt 14 ]; then
    echo "  [!] Only $AGENT_COUNT/14 agent files found"
    MISSING=1
fi

if [ "$MISSING" -eq 0 ]; then
    echo ""
    echo "  ╔════════════════════════════════════════╗"
    echo "  ║  Spectrum Protocol installed.          ║"
    echo "  ║                                        ║"
    echo "  ║  14 agents ready. 0 dependencies.      ║"
    echo "  ║                                        ║"
    echo "  ║  Start a new Claude Code session and   ║"
    echo "  ║  tell it to build something in         ║"
    echo "  ║  parallel. Gold will take it from      ║"
    echo "  ║  there.                                ║"
    echo "  ╚════════════════════════════════════════╝"
    echo ""
    echo "  Quick start:"
    echo "    \"Build the auth system, API, and dashboard in parallel.\""
    echo ""
    echo "  Tutorial:  https://github.com/ryantlee25-droid/spectrum-protocol/blob/main/TUTORIAL.md"
    echo "  Docs:      https://github.com/ryantlee25-droid/spectrum-protocol"
    echo ""
else
    echo ""
    echo "  [!] Installation incomplete. Check errors above."
    exit 1
fi
