# Spectrum Protocol — Speed Audit

**Date**: 2026-03-31
**Auditor**: Performance Engineering Review
**Sources**: SPECTRUM-OPS.md, CLAUDE.md (project), evaluation/swe-bench-prep/pipeline-design.md

---

## Executive Summary

Full muster is documented at ~8 minutes. Reaping at ~3 minutes. Nano at ~1 minute. The core
problem is not any single step — it is that the protocol applies the same sequential ceremony
regardless of risk profile. There are 17 numbered steps before the first Howler is dispatched
in full mode, and a significant fraction of them are parallelizable or conditionally skippable
with no correctness loss. The optimizations below target an 8-minute full muster reduced to
~4.5 minutes on typical runs, with specific interventions for each phase.

**Time-saving estimates below use wall-clock minutes, not compute time.**

---

## Phase 1 — Muster

### How Many Sequential Steps Before First Howler Drops?

In full mode: **17 numbered steps** execute sequentially before a Howler is dispatched.
The mandatory human confirmation gate (step 15) is the hard wall — nothing after it can be
moved before it without design changes. But steps 1–14 contain significant slack.

Critical path to first Howler (best case, full mode):
1. Generate rain ID + create directory (~10s)
2. Read LESSONS.md + ENTITIES.md (~30s)
3. Validate PLAN.md (~60s, 3-5 file reads)
4. Update ARCHITECTURE.md (~2–3 min if creating, ~1 min if patching)
5. Decomposition hazard scan (~30s, analytical)
6. Write MANIFEST.md (~60s)
7. Write CONTRACT.md (~3–5 min — this is the single biggest step)
8. White Pre-Check (~3 min, external agent round-trip)
9. Contract-to-test generation (~60–90s, for TypeScript/Python)
10. Commit convoy-contracts.d.ts (~30s)
11. Politico adversarial review (~3–5 min, external agent round-trip)
12. Human approval gate (~variable)
13. Write CHECKPOINT.json (~15s)
14. Pre-create all worktrees (~30s per worktree)

**Measured critical path (before human gate): ~14–18 minutes in full mode.**

The protocol doc says ~8 minutes. The discrepancy is because White Pre-Check and Politico
are both external agent calls with real round-trip latency — each is 3-5 minutes minimum.

### Steps That Could Run in Parallel

| Opportunity | Current | Optimized |
|---|---|---|
| ARCHITECTURE.md update + LESSONS.md + ENTITIES.md read | Sequential (steps 3, 6) | Fully parallel — no deps between them |
| Codebase index tool run + LESSONS.md read | Sequential | Parallel — both are read operations |
| MANIFEST.md write + convoy-contracts.d.ts sketch | Sequential | MANIFEST shapes the contract, but a type skeleton can be drafted from the plan while MANIFEST is being written |
| White Pre-Check + Contract-to-test stub generation | Sequential (steps 11, 12) | White Pre-Check verifies CONTRACT.md; contract test stubs can be generated in parallel since they assert postconditions, not codebase accuracy |
| CHECKPOINT.json write + worktree pre-creation | Sequential | Parallel — CHECKPOINT.json is a write, worktrees are git operations; no dep |

**Estimated savings from parallelizing reads and post-approval writes: 2–3 minutes.**

### Steps That Could Be Skipped for Specific Task Types

| Step | Skippable When | Justification |
|---|---|---|
| ARCHITECTURE.md update | Codebase unchanged since last Spectrum on same project | If the file is <72h old and no PRs merged since, it's current — read it, skip the update pass |
| Test impact map generation (`test_impact_map.py`) | All Howlers are CREATES-only | No existing tests to map against new files |
| Codebase Context sections in CONTRACT.md | Howler is pure-create with no MODIFIES | Already documented as N/A — but Gold still spends time confirming this for each Howler |
| Contract-to-test generation | No DbC postconditions (reaping/nano), or no test infrastructure | Already in the rules but Gold still checks and writes the skip note — automate the detection |
| Politico adversarial review | Reaping mode (already skipped), OR MANIFEST has only 2 Howlers with no seams between them | Two Howler runs with independent files have near-zero ownership gap risk |
| White Pre-Check | Zero MODIFIES files across all Howlers | Pre-check's main value is verifying file existence and signature accuracy for files being modified. For all-CREATES spectrums, the files don't exist yet — White has nothing to verify |
| `convoy-contracts.d.ts` commit | No shared TypeScript interfaces (already conditional) | Already handled, but the check could be moved earlier so Gold doesn't set up the commit flow before confirming this |

**Estimated savings from conditional skips on pure-create runs: 3–5 minutes.**
(This is where reaping mode gets its advantage — it codifies most of these skips.)

### What is the Critical Path from "User Says Go" to First Howler Coding?

**Full mode (current):**
- LESSONS/ENTITIES read: ~1 min
- PLAN.md validation: ~1 min
- ARCHITECTURE.md update: ~2 min (patch) to ~4 min (create)
- CONTRACT.md write (including codebase reads): ~4 min
- White Pre-Check (external agent): ~3 min
- Contract-to-test generation: ~1.5 min
- Politico review (external agent): ~4 min
- Human approval: ~variable (not optimizable)
- CHECKPOINT.json + worktrees: ~1 min

**Critical path total (pre-human): ~17–18 min**
**With human approval (assume fast): ~20 min before first Howler writes a line of code**

**Key insight**: White Pre-Check and Politico together account for ~7–9 minutes of the pre-drop
critical path. Both are external agent round-trips that cannot be compressed without accepting
lower quality. The best approach is to overlap them rather than run them sequentially.

**White Pre-Check and Politico can run in parallel.** White verifies factual accuracy (files
exist, signatures match). Politico reviews decomposition logic and interface design. The
SPECTRUM-OPS.md already notes: "the White Pre-Check has already validated factual accuracy of
CONTRACT.md... Your role is adversarial review of the *decomposition logic and interface design*,
not re-checking file existence." These are fully orthogonal. Running them in parallel saves
~3–4 minutes.

**Optimized critical path (pre-human): ~11–13 min — a ~35% reduction.**

---

## Phase 2 — Drop

### Unnecessary Waits in Dispatch

The DAG model is already sound — Howlers dispatch as edges are satisfied, not in batches.
The `#types` checkpoint (STABLE signal unblocks deps without waiting for full completion)
is the right design. No structural waits were found in the dispatch model itself.

**Issues found:**

1. **Post-drop worktree verification adds ~5s per Howler but is done sequentially**. For an
   8-Howler run, that is ~40s of serial overhead after each drop. This is already called out
   as "adds ~5s per Howler" in the ops manual. It cannot be parallelized because each
   verification depends on the preceding drop completing, but the 5s estimate seems optimistic —
   a git worktree list + log command on a large repo can take 10–15s.

2. **Discovery relay is ad hoc**. Gold compresses findings "into a ~500-token brief" before
   each dependent Howler drop. The content of this relay depends on the dependent Howler's
   specific needs, which requires Gold to reason about the task. This is the right design, but
   it means Gold has unbounded prep time before each dependent drop. In practice, relay
   construction should take <30s, but there is no enforced ceiling.

3. **No pre-generation of Howler prompts**. Gold generates each Howler's drop prompt at
   dispatch time. For independent Howlers (no deps), Gold could draft all prompts during muster
   (after MANIFEST.md is written) so that post-approval dispatch is instant. This is the
   biggest parallelism opportunity in the drop phase.

### Could Gold Pre-Generate Howler Prompts During Muster?

Yes, with a narrow condition: **for Howlers with no dependencies (DAG root nodes), prompt
pre-generation is safe and saves real time**.

For dependent Howlers, the prompt includes a discovery relay that requires waiting for
preceding Howler output — these cannot be pre-generated.

For root Howlers (typically the majority in a wide DAG), the prompt is deterministic from
MANIFEST.md + CONTRACT.md + CHECKPOINT.json. Gold can write draft prompts to
`~/.claude/spectrum/<rain-id>/drops/<howler-name>.md` during muster, then at dispatch time
it is a file read + agent call rather than a reasoning step.

**Estimated savings: 30–60s per root Howler at dispatch time, compounded across all drops.**

### Is Worktree Pre-Creation a Bottleneck?

For large Howler counts (6–8 Howlers), pre-creating all worktrees sequentially adds
measurable latency. The protocol requires pre-creation because of the ~50% git permission
failure rate observed in production (remnant-narrative-0329, remnant-ux-0329).

Worktree creation is a `git worktree add` call — it is fast (~1–2s per worktree) but the
verification step (`git worktree list` + `git log -1`) adds overhead. For an 8-Howler run,
pre-creation + verification takes approximately 20–30s total.

**Optimization**: Run `git worktree list` once after all worktrees are created rather than
once per worktree. This is a single command change but cuts verification overhead by ~7×.

**Worktree creation could also be parallelized** — `git worktree add` for different branches
does not block on other `git worktree add` calls as long as the branches are distinct. This
requires a shell loop running commands in the background, but the verification would still
need to wait for all to complete.

---

## Phase 3 — Quality Gate

### Context Sharing Between White, Gray, and /diff-review

All three run in parallel, which is already optimal for wall-clock time. The redundancy is
in context loading: each of the three agents independently reads the implementation diff and
the source files. For a typical Howler that modified 4–6 files, this means roughly 3×
the source file read tokens across the three agents.

**Optimization**: Gold could write a `gate-context.md` summary (analogous to the discovery
relay) containing the diff summary and key files, then pass it as context to all three gate
agents. This does not reduce the number of agents but reduces each agent's cold-start
context-gathering time.

**Token savings estimate**: ~6,000–10,000 tokens per quality gate run across all three agents
combined (2,000–3,000 per agent), at ~$0.02–$0.04 per gate. Modest cost savings, but the
wall-clock impact of faster context-building could be meaningful if agents are tool-call
bounded.

### Could Quality Gates Run on Completed Howlers While Others Are Still Implementing?

Yes, and this is a significant opportunity currently not in the protocol.

The current model waits for a Howler to fully complete before its quality gate starts.
But Howlers in a wide DAG finish at different times. If Howler A finishes at T+25min and
Howler B finishes at T+35min, Howler A's quality gate could run from T+25 to T+33 while
Howler B is still implementing. The gate result feeds directly into Copper opening the PR —
which can also be done before Howler B finishes.

**The protocol does not block this** — the rule is "before opening a PR, every Howler runs
all three in parallel." It says nothing about waiting for other Howlers to finish before
running the gate. This optimization is available now, it is simply not explicitly stated.

**Explicit instruction to add**: "Drop the triple quality gate for each Howler immediately
upon Howler completion. Do not wait for other Howlers to finish. PRs can be opened while
other Howlers are still running, provided the PAX phase has not started."

**Estimated wall-clock savings on a 4-Howler run with staggered completion**: 8–15 minutes,
assuming quality gates take 8 minutes and the last Howler finishes 15+ minutes after the first.

### Is the Triple Gate Always Necessary?

**Current exceptions already in the protocol:**
- Nano mode: skips White + Gray + /diff-review entirely (Howlers self-verify only)
- Doc-only spectrums: skip /diff-review
- Non-security config changes: skip /diff-review

**Additional cases where gates could be reduced:**

| Case | Current | Optimized |
|---|---|---|
| Pure-create with no logic (config files, markdown docs) | Full triple gate | Single gate (Gray for test pass; skip White and /diff-review) |
| Pure-test additions (no source changes) | Full triple gate | Gray only — White has no source to review, /diff-review is low-signal |
| Benchmark/evaluation runs (SWE-bench Variant B) | Double gate per pipeline-design.md | Already optimized in the variant design |
| Reaping mode | Full triple gate (kept as invariant) | Could drop /diff-review for reaping mode pure-create runs |

**Recommendation**: Add a gate tier between nano (self-verify only) and full (triple gate):
- **Single gate**: Gray only. For pure-create config/doc Howlers with no security surface.
- **Double gate**: White + Gray. Already used in SWE-bench Variant B. Could be the default for reaping mode.
- **Triple gate**: White + Gray + /diff-review. Required for any source code Howler.

**Estimated savings per quality gate reduction**: ~3–5 minutes (eliminating one external agent
call) and ~8,000–12,000 tokens (~$0.04).

---

## Token Efficiency

### Biggest Token Wastes

**1. HOWLER-OPS.md preamble in every Howler drop prompt (~2,500 tokens)**

Every Howler receives the full HOWLER-OPS.md (or equivalent operations instructions) in its
drop prompt. For a 6-Howler run, this is ~15,000 tokens of repeated context across agents
that are all running the same protocol version. The pipeline-design.md notes this explicitly:
"~2,500 tokens saved" as a cost advantage of the bare Variant C approach.

**Optimization**: Host HOWLER-OPS.md at a known path and reference it by path rather than
inlining it. The drop template already does this for CONTRACT.md ("Read
`~/.claude/spectrum/{rain-id}/CONTRACT.md` before starting"). Apply the same pattern to the
Howler operations instructions.

**Token savings: ~2,500 tokens × N Howlers per spectrum.**

**2. CONTRACT.md path-reference already implemented, but not for muster artifacts**

The drop template correctly says "CONTRACT.md is referenced by path, not inlined. For a
5-Howler run with a 2000-token contract this saves ~10,000 input tokens (~$0.03 at Sonnet
rates)." Good. But the DISCOVERY RELAY (~500 tokens per dependent Howler) and KNOWN RISKS
(0–3 patterns from LESSONS.md) are inlined. For large LESSONS.md files with many patterns,
KNOWN RISKS could grow beyond the ~50-token estimate implied by "0–3 patterns."

**Optimization**: Cap KNOWN RISKS at 150 tokens (2–3 tightly written patterns max). Anything
beyond that is noise that reduces Howler attention on the actual task.

**3. Debrief YAML frontmatter is verbose for simple Spectrums**

The debrief schema includes: howler, spectrum, status, pr, completed, confidence, seams
(with id/target/type/what/where), assumptions (with id/about/what), files_created,
files_modified, contract_compliance, open_exits, warnings. For a nano or reaping mode
Howler that created 2 markdown files, this schema is 10× the content of the actual debrief.

**Optimization**: Scaled debrief schema by mode:
- Full mode: full YAML frontmatter
- Reaping mode: simplified (howler, status, files_created, seams, warnings)
- Nano mode: minimal (howler, status, files_created) — already effectively this since nano
  Howlers only write HOOK.md and a one-line completion note, but the schema expectation is
  never stated as reduced

**Token savings**: Minor per Howler but accumulates in Gold's Pax phase, which reads all
debriefs. A simpler schema means Gold reads less to validate.

**4. Gold reads 2-3 key files per Howler during Pax independent validation**

Pax requires Gold to read 2-3 key files per Howler and verify against CONTRACT.md
postconditions. For a 6-Howler run, this is 12-18 file reads. If each file averages
2,000 tokens, Pax consumes ~24,000–36,000 tokens in file reads alone, before Gold writes
PAX-PLAN.md.

**Optimization**: Howlers could include file hashes (or short snippets of key exports) in
their HOOK.md Completion Verification section. Gold would then validate the snapshot rather
than re-reading full files, unless the snapshot raises a concern. This is a selective read
pattern rather than full file reads for every Howler.

**Estimated savings: ~15,000–25,000 tokens in Pax, roughly $0.06–$0.10 per spectrum.**

**5. Contract-to-test stubs are generated by Gold and then read by Howlers**

Gold writes stub test files to `tests/spectrum/<howler-name>.contract.test.{ts|py}` and
commits them. Howlers then run these tests as part of completion verification. This means
the test files exist in the worktree and the Howler reads them. The token cost is:
Gold writes ~200-500 tokens per stub; Howler reads the same. For 5 Howlers, that is
~1,000–2,500 tokens of stub content read redundantly.

**Not a significant optimization target.** The value of contract-to-test generation is
correctness assurance, not token efficiency. Mention for completeness only.

### Contract-by-Reference: What Other Prompt Compression Opportunities Exist?

The ops manual already implements the most impactful one (CONTRACT.md by path, not inlined).
The next opportunities in priority order:

| Opportunity | Current | Savings |
|---|---|---|
| HOWLER-OPS.md by path reference | Inlined (~2,500 tokens) | ~2,500 tokens × N Howlers |
| KNOWN RISKS token cap (150 tokens) | Uncapped | Variable, ~100–500 tokens per Howler |
| ARCHITECTURE.md shared link vs. copy | Copied to spectrum dir | 0 token savings (it's a file read, not in prompt) |
| Pax file snapshot validation | Full file reads | ~15,000–25,000 tokens per spectrum |
| Debrief schema by mode | Uniform full schema | Minor; ~1,000 tokens per Howler in Gold's Pax reads |

### Could Gold's Muster Output Be More Concise Without Losing Information?

**CONTRACT.md is the main verbosity target.** The spec requires:
- Shared types and interfaces
- Naming conventions
- Per-Howler Codebase Context (5-15 lines per file)
- Integration points
- Design-by-Contract per Howler

For a 5-Howler spectrum modifying 3 files each, this is 5 × 3 × 10 = 150 lines of codebase
context alone, plus DbC sections. CONTRACT.md is typically 2,000–4,000 tokens.

The per-Howler Codebase Context is the section with the most variance. The "5-15 lines per
file" guidance has a 3× range. Tightening this to "5-8 lines per file" with a strict
maximum would reduce CONTRACT.md size by ~20–30% without losing the core value, which is
flagging gotchas and patterns — not reproducing function signatures in full.

**Specific conciseness improvement**: Replace full function signatures in Codebase Context
with a 1-line function list + flag any gotchas. Example:

Current style:
```
Key functions: `process(self, data: dict) -> Result` (takes a dict, returns Result from
utils.types). `validate(self, data: dict) -> bool`. `__init__(self, config: Config)`.
Uses ABC metaclass. File has circular import with config.py.
```

Tighter style:
```
Key functions: process, validate, __init__. ABC metaclass. GOTCHA: circular import with config.py — do not add imports from config.py.
```

**Estimated reduction**: ~30% smaller Codebase Context sections, ~15% smaller CONTRACT.md
overall. At 3,000 tokens per contract and a 5-Howler run, that is ~450 tokens × 5 = ~2,250
tokens saved in Howler context loading.

---

## Mode Efficiency

### Is Nano Mode Fast Enough?

Nano mode targets "muster + drop in under 1 minute." Its current step list is:
1. Generate rain ID (~10s)
2. Create spectrum directory (~5s)
3. Write NANO-MANIFEST.md (~30s)
4. Write CHECKPOINT.json (~10s)
5. Auto-approve + drop Howlers (~15s per Howler)

**For 2 Howlers: ~65–80s total. For 3 Howlers: ~75–90s.**

This is legitimately fast. The primary overhead is Gold's token budget — writing
NANO-MANIFEST.md still requires Gold to reason about task boundaries and file ownership.
For truly obvious tasks (the activation criterion says "boundaries are obvious"), this is
15–30s of reasoning at most.

**One speed gap in nano**: Howlers create their own branches (no worktree pre-creation).
This means each Howler spends 15–30s on branch setup before starting work, and branch
failures are unrecovered (escalate to reaping). This is noted in the spec: "Nano mode has
no structural recovery path." For 2-Howler nano runs, branch failures waste the entire
muster investment. A lightweight pre-check ("can this repo create branches?") at the start
of nano mode would take ~5s and prevent the most common failure mode.

**Verdict**: Nano mode is appropriately fast. Its bottleneck is Howler branch setup, not
Gold overhead.

### Is There a Gap Between Nano and Reaping?

**Yes.** The gap is real and worth addressing:

| Mode | Activation | Muster time | Key differentiator |
|---|---|---|---|
| Nano | 2-3 Howlers, obvious boundaries, auto-approve | ~1 min | No contract, no quality gates, no worktrees |
| Reaping | 3-4 Howlers, pure-create, human confirms | ~3 min | LIGHT-MANIFEST + simplified contract + quality gates |
| Full | 3+ Howlers, any modification | ~8–18 min | Full ceremony |

The gap between nano and reaping is primarily: quality gates and human confirmation.

**Missing mode: "Micro"** — 2-3 Howlers, pure-create, human confirms, includes White + Gray
(double gate), but skips Politico, ARCHITECTURE.md, DbC, and contract-to-test generation.

Micro would be faster than reaping (skip Politico's 3-5 min round-trip) and safer than nano
(includes quality gates). For the most common use case of "2-3 small features I want to
parallelize without the full ceremony," this mode would be the right default.

**Proposed Micro mode (~2 min muster):**
- Activation: 2-3 Howlers, pure-create, human confirms (same as nano but with quality gates)
- Write: NANO-MANIFEST.md (same format), CHECKPOINT.json with `"mode": "micro"`
- Skips: CONTRACT.md, Politico, ARCHITECTURE.md, DbC, contract-to-test, /diff-review
- Keeps: White + Gray per Howler, HOOK.md, debrief, worktree pre-creation, LESSONS.md
- No auto-approve (unlike nano)

### For the Most Common Use Case (3-4 Howlers, Simple Feature), What Is the Optimal Path?

**Currently**: Reaping mode (~3 min muster, triple quality gate per Howler).

**Optimized**: Reaping mode with the following changes:
1. Drop /diff-review from the quality gate (pure-create, no security surface) → double gate
2. Pre-generate root Howler drop prompts during muster while waiting for human approval
3. Run quality gates immediately on Howler completion, not after all Howlers finish
4. Worktree creation: single `git worktree list` verification after all creations, not per-worktree

These four changes together reduce a 3-4 Howler simple feature run from:
- Current: ~3 min muster + ~8 min gate × N sequential = ~20 min total (assuming staggered)
- Optimized: ~3 min muster + gates run in parallel with other Howlers + double gate = ~13 min total

**Largest single opportunity**: Running quality gates as each Howler completes rather than
batching them after all Howlers finish. This saves up to 8 minutes per Howler (one full
triple gate round-trip) if early Howlers finish significantly before later ones.

---

## Prioritized Fix List

Ranked by (impact × implementation effort):

### Priority 1 — High Impact, Low Effort

**P1-A: Parallelize White Pre-Check and Politico**
- Current: sequential (~3–4 min White, then ~4–5 min Politico = ~7–9 min combined)
- Change: drop both simultaneously after CONTRACT.md is written; Gold waits for both reports
- Savings: ~3–4 min per full muster
- Risk: none — they are already confirmed to be orthogonal in the ops manual text

**P1-B: Trigger quality gates per Howler on completion, not after all complete**
- Current: implied batch (PAX happens after all Howlers complete; gates must precede Pax)
- Change: add explicit protocol rule: "Drop triple gate immediately on Howler completion.
  Do not wait for other Howlers. Pax begins only after the last Howler completes."
- Savings: 8–15 min on any run with staggered Howler completion
- Risk: PRs opened before all Howlers complete adds some complexity to PAX seam-checking,
  but Pax already requires reading all debrief entries — the PR being open is not a blocker

**P1-C: Parallelize ARCHITECTURE.md update + LESSONS.md + ENTITIES.md reads**
- Current: steps 3 and 6 in muster are sequential
- Change: Gold initiates all three reads/updates in parallel at muster start
- Savings: ~1–2 min per muster
- Risk: none — these are all independent reads/updates

### Priority 2 — High Impact, Medium Effort

**P2-A: Pre-generate drop prompts for root Howlers during muster**
- Current: Gold generates each prompt at dispatch time (post-approval)
- Change: Gold writes `drops/<howler-name>.md` files during muster for all DAG root nodes;
  at dispatch, Gold reads and uses the pre-written prompt (updating with any approval-gate
  feedback if the human flagged concerns)
- Savings: ~30–60s per root Howler at dispatch; 2–4 min on a 4-Howler run where 3 are roots
- Risk: if human approval changes the plan, pre-generated prompts need to be patched. Mitigated
  by treating them as drafts that Gold revises after approval if needed.

**P2-B: Add Micro mode (2-3 Howlers, pure-create, double gate, human confirms)**
- Current: gap between nano (no gates, auto-approve) and reaping (triple gate, human confirms)
- Change: define Micro mode as described in the Mode Efficiency section
- Savings: ~1 min vs. reaping (skip Politico) on the most common use case
- Addresses the "2 small features I want to parallelize" scenario with safety but without
  the overhead of the full 3+ mode reaping ceremony

**P2-C: Enforce HOWLER-OPS.md by path reference in drop prompts**
- Current: HOWLER-OPS.md (operations instructions) appear to be inlined in drop prompts
  based on the template (~2,500 tokens per Howler)
- Change: store at a stable path, reference by path as CONTRACT.md already is
- Savings: ~2,500 tokens × N Howlers per spectrum; at Sonnet rates and a 5-Howler run,
  that is ~$0.06 in input token cost
- Risk: Howlers must have filesystem access to read the file (they do, already reading CONTRACT.md by path)

### Priority 3 — Medium Impact, Low Effort

**P3-A: Skip White Pre-Check for pure-create Spectrums (all CREATES, zero MODIFIES)**
- Current: runs for all full-mode spectrums; skipped only for reaping and nano
- Change: auto-skip when Gold confirms during decomposition hazard scan that all Howlers are
  pure-create. The pre-check verifies file existence and signatures of MODIFIES files — there
  is nothing to verify on files that will be created.
- Savings: ~3 min per spectrum on pure-create full-mode runs
- Risk: minimal; the check's value on CREATES files is already acknowledged as near-zero in the spec

**P3-B: Tighten Codebase Context to 5-8 lines per file (not 5-15)**
- Current: "5-15 lines per file" gives Gold a 3× verbosity range
- Change: enforce "5-8 lines per file, GOTCHA-only bullets for anything beyond 8 lines"
- Savings: ~20% reduction in CONTRACT.md size, better Howler focus
- Risk: none — the value of context is in flagging gotchas, not exhaustive signature lists

**P3-C: Single `git worktree list` verification after all pre-creations (not per-worktree)**
- Current: implied per-worktree verification
- Change: batch the verification command to run once after all `git worktree add` commands
- Savings: ~5–10s per Howler above the first; ~30s on a 6-Howler run
- Risk: none — the list command is idempotent and reads all worktrees at once

**P3-D: Add double gate as reaping mode default (replace triple gate)**
- Current: reaping mode "keeps" the full triple gate (White + Gray + /diff-review)
- Change: reaping mode default to double gate (White + Gray); /diff-review only if Howlers
  modify authentication, cryptography, or user input handling (explicit classification)
- Savings: ~3–5 min per reaping run (one fewer external agent per Howler)
- Risk: low — reaping mode already activates only on pure-create, no-interface-dep runs.
  Security surface on "new markdown files" or "new config schemas" is minimal.

### Priority 4 — Medium Impact, Higher Effort

**P4-A: Pax file snapshot validation (Howlers write key export hashes)**
- Current: Gold reads 2-3 key files per Howler during Pax (independent validation)
- Change: Howlers include a `## Export Snapshot` section in HOOK.md with the first 5 lines
  of each key created/modified file. Gold validates the snapshot first; only reads the full
  file if the snapshot raises a concern.
- Savings: ~15,000–25,000 tokens in Gold's Pax phase (~$0.06–$0.10 per spectrum)
- Risk: Howler adds a small step (snapshot write), but it can be part of Completion Verification

**P4-B: Mode-scaled debrief schema (reduce for reaping/nano)**
- Current: full YAML frontmatter required for all modes
- Change: define a "simplified debrief" for reaping/nano (5 fields vs. 12+)
- Savings: minor per Howler, more meaningful in Gold's Pax reads over time
- Risk: LESSONS.md quality degrades slightly for reaping/nano spectrums; Brown gets less data

---

## Summary Table

| Fix | Phase | Time Saved | Tokens Saved | Priority |
|---|---|---|---|---|
| Parallelize White Pre-Check + Politico | Muster | 3–4 min | 0 | P1 |
| Quality gates per Howler on completion | Proving | 8–15 min total | 0 | P1 |
| Parallelize ARCH + LESSONS reads | Muster | 1–2 min | 0 | P1 |
| Pre-generate root Howler drop prompts | Drop | 2–4 min | 0 | P2 |
| Add Micro mode | Mode Design | 1–2 min vs. reaping | 0 | P2 |
| HOWLER-OPS.md by path reference | Drop | 0 | ~2,500 × N | P2 |
| Skip White Pre-Check on all-CREATES | Muster | ~3 min | ~8,800 | P3 |
| Tighten Codebase Context (5-8 lines) | Muster | ~30s | ~2,000+ | P3 |
| Single worktree list verification | Drop | ~30s | 0 | P3 |
| Double gate for reaping mode | Proving | 3–5 min/run | ~12,000 | P3 |
| Pax export snapshot validation | Pax | 0 | 15,000–25,000 | P4 |
| Mode-scaled debrief schema | Pax | 0 | ~1,000 × N | P4 |

**If only one change is made**: Trigger quality gates per Howler on completion (P1-B). It
requires no protocol redesign — only an explicit rule addition — and it saves the most wall-
clock time on the most common multi-Howler run pattern.

**If three changes are made**: P1-A (parallel White+Politico) + P1-B (gates on completion) +
P1-C (parallel reads at muster start) — these together cut full muster wall-clock time from
~17 min to ~11 min, and reduce total run time on a 4-Howler staggered run by 15–20 minutes.

---

*Speed Audit — Spectrum Protocol — 2026-03-31*
