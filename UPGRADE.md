# Upgrading Spectrum Protocol

## v6.0 → v6.1 (Current)

```bash
cd spectrum-protocol && git pull
cp spectrum/CLAUDE.md ~/.claude/CLAUDE.md
cp spectrum/SPECTRUM.md ~/.claude/SPECTRUM.md
cp agents/*.md ~/.claude/agents/
```

### What Changed in v6.1

**All 7 core agents rewritten** with prompt engineering techniques validated on TypeScript and Go benchmarks:

- **White**: Tiered verification (reasoning certificates + batched tool calls), loop-aware analysis, INQUIRY format for inconclusive findings, 15-call verification budget
- **Gray**: Batch-generate-validate (3-5 tests per call), style template extraction, failed test accumulator
- **Orange**: Minimize-then-localize, causal chain construction, scope boundaries (specific test only)
- **Blue**: Freshness gate, type system audit, hard scope gate, serial task multiplier
- **Copper**: Upgraded Haiku → Sonnet, file sensitivity filter, evidence-before-claims
- **Gold**: Simplified to thin dispatcher
- **Workers**: Simplified to implement-and-commit (no HOOK.md)

**Memory integration documented**: Agents + Tages memory compound for -25% time, -10% tokens.

**No breaking changes.** The protocol (SPLIT.md, 4 steps) is unchanged. Only agent prompt quality improved.

### Cleanup (optional)

Remove dead agents from v5 if they still exist:

```bash
rm -f ~/.claude/agents/{obsidians,browns,violets,politicos,workers,grays-run}.md
```

---

## v5.x → v6.0

v6.0 was a complete rewrite. The simplest upgrade path:

```bash
# Back up
cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.v5-backup

# Fresh install
cd spectrum-protocol && git pull
cp spectrum/CLAUDE.md ~/.claude/CLAUDE.md
cp spectrum/SPECTRUM.md ~/.claude/SPECTRUM.md

# Remove all old agents and copy new ones
rm ~/.claude/agents/{golds,blues,howlers,whites,grays,oranges,coppers,obsidians,browns,violets,politicos,greens,helldivers,primus}.md 2>/dev/null
cp agents/*.md ~/.claude/agents/

# Remove v5 artifacts
rm -f ~/.claude/SPECTRUM-OPS.md ~/.claude/HOWLER-OPS.md
rm -f ~/.claude/hooks/seam_check.py
```

### What Changed v5 → v6

| | v5 | v6 |
|---|---|---|
| Spec size | 4,100 lines | ~200 lines |
| Phases | 7 (Muster → Triumph) | 4 (Split → Verify) |
| Agents | 14 | 7 |
| Artifacts | CONTRACT.md, MANIFEST.md, HOOK.md, CHECKPOINT.json, etc. | SPLIT.md only |
| Quality gates | Per-worker | Once on merged result |
| Muster time | 8-15 min | ~2 min |

**What was cut**: CONTRACT.md, Politico, Skeptic, Obsidian, Violet, Brown, HOOK.md, CHECKPOINT.json, Pax phase, Issue Confirmation Gate, per-worker quality gates.

**What was kept**: Blue planning, worktree isolation, file ownership, post-merge verification, LESSONS.md.

---

## Rollback

To revert to any prior version:

```bash
cd spectrum-protocol
git log --oneline  # find the commit you want
git checkout <commit> -- spectrum/ agents/
cp spectrum/CLAUDE.md ~/.claude/CLAUDE.md
cp spectrum/SPECTRUM.md ~/.claude/SPECTRUM.md
cp agents/*.md ~/.claude/agents/
```
