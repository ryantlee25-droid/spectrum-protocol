# HOWLER-OPS.md — Howler Operational Reference

> **READ-ONCE**: Read this file exactly once at session start. Internalize the key points.
> Do not re-read unless checking a specific postcondition or convention.
> Full spec: ~/.claude/SPECTRUM.md | Gold/Howler ops: ~/.claude/SPECTRUM-OPS.md

---

## File Operation Discipline

- **Batch reads**: When you need to read multiple files, read them in a single tool call batch.
- **Batch writes**: When creating multiple files, write them consecutively without interleaving reads.
- **Minimize round-trips**: Each tool call adds ~2k tokens of context accumulation. Plan your reads and writes to minimize total tool calls.
- **Read-once for reference files**: HOWLER-OPS.md and CONTRACT.md should each be read once. Do not re-read as a crutch.

---

## Scope Alignment and Reflexion Rules

- **REFLEXION**: After every 5th file write, re-read CONTRACT.md scope and your
  File Ownership list. If touching files outside ownership, STOP and log drift.
- **SCOPE ALIGNMENT CHECK**: After every 20 tool calls, re-read your original
  Task and CONTRACT.md. Write a 1-line `Alignment: on-track` or
  `Alignment: drifted — [reason]` entry in HOOK.md under Progress.
  If drifted, STOP and correct before continuing.

---

## Completion Verification Checklist

Before declaring done, verify mechanically:

1. Every file in CREATES exists: `ls -la {each file}`
2. Every file in MODIFIES has been changed: `git diff --name-only`
3. For TypeScript (if `node_modules` exists): `tsc --noEmit` passes
   (Skip if node_modules not installed — type checking defers to the quality gate)
4. For tests (if test framework installed): run the specific test files listed in your
   `## Test Impact Map` (from CONTRACT.md). If no map was provided, run tests on your
   owned files. Tests must pass; coverage gaps are warnings, not blockers.
   For files marked `[none-found]` in the impact map, run the full test suite rather
   than relying on the impact map — no targeted tests were found for those files.
   (Skip if dependencies not installed — testing defers to the quality gate)
5. Contract tests: run `tests/spectrum/{howler-name}.contract.test.{ts|py}` — these
   verify your CONTRACT.md postconditions are satisfied. All must pass before quality gates.
6. Postcondition verification (if CONTRACT.md has DbC for this Howler):
   run `python3 tools/verify_postconditions.py --contract {path} --howler {name} --root {project}`
   All postconditions must pass. Failures are blockers.

Write verification results in HOOK.md under `## Completion Verification`.

**ISSUE RE-READ**: After mechanical verification, re-read your CONTRACT.md postconditions
section. For each postcondition, write a one-line assessment in HOOK.md under `## Issue Re-Read`:
- State the postcondition
- State whether your implementation satisfies it (YES/NO/PARTIAL)
- If NO or PARTIAL: what's missing and can you fix it now?

If all postconditions are satisfied: write "All postconditions verified."
For Howlers without postconditions (pure-create, nano mode): fall back to the original
prose-based re-read. If no gaps: write "Issue re-read: no gaps identified." and proceed.

**REVISION PASS**: If completion verification or contract tests revealed failures:
- Read the test output and error messages carefully
- Identify the root cause (not just the symptom)
- Fix the issue and re-run the failing tests
- Update HOOK.md with what you fixed and why

Maximum 2 revision passes. If tests still fail after 2 passes, document the failures in
HOOK.md and proceed to debrief — Gold will run the quality gate and surface these failures
to White and Gray with full context. If all tests passed on first try: skip this step.

---

## Quality Gate

Gold drops **all three in parallel** after you signal completion — do not run these yourself:
1. White — zero blockers (code quality)
2. Gray — zero failures (tests; coverage gaps = warning)
3. /diff-review — zero criticals (security; high/medium = warning)

Do not open a PR. Gold coordinates Copper after the gates pass.

---

## HOOK.md Template

```markdown
# Hook: {task title}
Spectrum: {id}
Howler: {name}
Branch: spectrum/{id}/{name}
Worktree: ~/.claude/spectrum/{id}/worktrees/{name}
Started: {ISO timestamp}
Updated: {ISO timestamp}
Status: in_progress
git_status: ok
Confidence: medium
Confidence-Note: {what's uncertain}

## Task
{scope statement}

## File Ownership
CREATES: {files}
MODIFIES: {files}

## Checkpoints
- types: PENDING

## Progress
- [x] Step 1
- [ ] Step 2

## Decisions
- {key decisions and rationale}

## Seams
- exports: {what this Howler produces} → consumed_by: {howler-name}
- imports: {what this Howler needs} → produced_by: {howler-name}

## Cross-Domain Observations
- {anything noticed outside your ownership boundary — bugs, inconsistencies, opportunities in other Howlers' domains. Flag it here even if you can't fix it.}

## Completion Verification
- [ ] All CREATES files exist: {ls results}
- [ ] All MODIFIES files changed: {git diff --name-only results}
- [ ] Type check passes: {tsc --noEmit or N/A}
- [ ] Tests pass on owned files: {test results or N/A}
- [ ] Postcondition verification passes: {verify_postconditions.py results or N/A if no DbC}

## Issue Re-Read
- [ ] Re-read CONTRACT.md postconditions (or original task if no postconditions)
- {postcondition}: {YES/NO/PARTIAL} — {one-line evidence or what's missing}
- Summary: {"All postconditions verified." | "Issue re-read: no gaps identified." | gaps and fix plan}

## Revision Pass
- Pass 1: {what failed, what was fixed, or "all tests passed — no revision needed"}
- Pass 2: {if needed — what failed, what was fixed}

## Blockers
- (none)

## Errors Encountered
- (none)
  locus: {file path}
```

**`git_status` values**: `ok` (default), `needs_operator_commit` (git failed — Gold commits on your behalf).

---

## HOOK.md Compactness Rules

Apply when writing and updating HOOK.md:
- **Completion Verification**: write `PASS (N files)` or `FAIL (file: reason)` — not full `ls -la` output
- **Empty sections**: omit entirely if empty (`Blockers: (none)` → remove the section; `Errors: (none)` → remove; `Cross-Domain: (none)` → remove)
- **Decisions**: one line per decision, not paragraphs
- **Target**: HOOK.md under 1,500 tokens at submission

---

## Debrief YAML Frontmatter

```yaml
---
howler: howler-auth
spectrum: auth-refactor-0329
status: complete
pr: https://github.com/org/repo/pull/47
completed: 2026-03-29T15:20:00Z
confidence: medium
seams:
  - id: s1
    target_howler: howler-ui
    type: import
    what: "SignInButton from @clerk/nextjs"
    where: "Header.tsx"
assumptions:
  - id: a1
    about_howler: howler-ui
    what: "will add SignInButton to the header"
files_created:
  - src/middleware/auth.ts
files_modified:
  - src/app/layout.tsx
contract_compliance: full
open_exits:
  - "No org-creation flow"
warnings:
  - "Clerk requires manual dashboard setup"
---

## What I Built
{narrative}

## Decisions Made
{narrative}
```

---

## Contract Amendment Procedure

**Non-breaking** (additive): Write AMENDMENT.md, continue working.
**Breaking** (rename/remove): Write AMENDMENT.md, set Status: blocked, stop.

CONTRACT.md is frozen at drop. If you discover the contract is wrong, set `Status: blocked`
in HOOK.md and describe the needed change. Gold will re-run muster with the updated contract.
Never modify CONTRACT.md directly.
