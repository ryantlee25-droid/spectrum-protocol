# SWE-bench Readiness Evaluation — PLAN.md

**Date**: 2026-03-31
**Author**: Blue (Sonnet planner)
**Source research**:
- `evaluation/accuracy-research/ACCURACY-REPORT.md` — Helldiver's Opus research report
- `evaluation/accuracy-improvements/PLAN.md` — 7 improvements implementation plan
- `spectrum/SPECTRUM-OPS.md` — current protocol (post-improvements)
- `evaluation/eval-v2/COMPETITIVE-EVAL-V2.md` — competitive landscape (D3 sections)
- `evaluation/TOKEN-OPTIMIZATION.md` — token economics baseline

---

## Purpose

Spectrum Protocol scores D3=2 (Accuracy) — the single most damaging gap in a competitive field
where every serious competitor has published SWE-bench results. The accuracy-improvements spectrum
(I1–I4 + 3 additional improvements) has been planned but not executed. Before committing to a
full SWE-bench Pro run, we need to answer seven questions:

1. Are the 7 accuracy improvements implementable as documented, or are there gaps?
2. What SWE-bench infrastructure is needed (Docker, harness, adapter)?
3. How does Spectrum's pipeline map to SWE-bench's single-issue task format?
4. What's the risk that Gold's muster overhead hurts accuracy vs bare Sonnet?
5. What's the projected cost per SWE-bench task through Spectrum?
6. What competitors' SWE-bench approaches should we study?
7. What's the realistic timeline and effort to publish results?

This spectrum produces a READINESS-REPORT.md (H6 synthesis) that answers all seven and yields
a go/no-go recommendation with a concrete next-steps checklist.

---

## Background: The 7 Accuracy Improvements

The accuracy-improvements PLAN.md (dated 2026-03-31) documented 4 improvements (I1–I4). The
SPECTRUM-OPS.md review shows 7 improvements are now in the protocol:

| # | Improvement | Status in SPECTRUM-OPS.md |
|---|---|---|
| I1 | Issue Re-Read (Reflexion) — step 8b in Howler Drop Template | Present |
| I2 | Test Dependency Maps — step 8 test references + CONTRACT.md map | Present |
| I3 | Codebase Context Injection — per-Howler `## Codebase Context` in CONTRACT.md | Present |
| I4 | White Pre-Check — step 11 in Phase 1 muster | Present |
| I5 | Contract-to-Test Generation — step 12 in Phase 1 muster | Present |
| I6 | Revision Pass — step 8c in Howler Drop Template | Present |
| I7 | Pattern Library (Known Failure Patterns from LESSONS.md) — step 3 in muster | Present |

All 7 appear to be documented in SPECTRUM-OPS.md. H1 (Protocol Validation Auditor) will verify
whether the documentation is internally consistent, complete, and implementable without ambiguity.

---

## Spectrum Design

**Mode**: Full spectrum (not reaping). This is a research and analysis sprint, not a pure-create
run. H1–H5 are independent research tasks; H6 synthesizes their outputs. Full mode is appropriate
given the complexity of each task and the need for CONTRACT.md coordination on shared definitions
(e.g., what "pipeline variant" means across H3, H4, H5).

**Howler count**: 6 (H1–H5 parallel, H6 sequential after all complete).

**Rationale for full mode over reaping**:
- H1, H3, H4, H5 all MODIFY shared definitions of "pipeline variant" and "cost model" that H6
  synthesizes. A CONTRACT.md capturing these shared definitions prevents H6 from working with
  inconsistent inputs.
- White Pre-Check is valuable here: H4 references TOKEN-OPTIMIZATION.md data; H5 references
  COMPETITIVE-EVAL-V2.md scores. Both need factual accuracy checked before Howlers start.
- Politico should review the file ownership matrix — H4 and H5 both produce cost/speed data;
  ensuring they don't overlap on the same claims is the kind of contract ambiguity Politico catches.

---

## Howler Decomposition

### H1 — Protocol Validation Auditor
**Effort**: M | **Serial risk**: No | **DAG deps**: None

**Scope**: Review all 7 accuracy improvements as they appear in SPECTRUM-OPS.md. For each:
1. Is the improvement complete (is every referenced tool, file, or step actually defined)?
2. Is it internally consistent with the rest of the protocol (no contradictions with other steps)?
3. Is it implementable by Gold/Howlers without ambiguity (would a fresh Howler know what to do)?
4. Are there ordering conflicts (e.g., does step 8b depend on something not yet available)?

Also audit the Howler Drop Template holistically:
- Does instruction numbering flow correctly (8, 8b, 8c, 9, 10, 11, 12)?
- Are there redundant instructions or contradictory constraints?
- Is the template too long for practical use? (Token budget concern from TOKEN-OPTIMIZATION.md)
- Does the HOOK.md Template match the Drop Template's instructions?

And check the muster checklist:
- Does every checklist item have a corresponding muster step?
- Are there muster steps without checklist coverage?
- Is the White Pre-Check sequenced correctly (step 11, before Politico at step 14)?
- Is the Contract-to-Test step (step 12) adequately specified?

**Output**: `evaluation/swe-bench-prep/protocol-audit.md`

Format requirements:
- One section per improvement (I1–I7), each with: Completeness/Consistency/Implementability ratings
  (Green/Yellow/Red) and specific gap or issue descriptions
- One section for Howler Drop Template holistic review
- One section for HOOK.md Template review
- One section for Muster Checklist review
- Summary table: which improvements are ready to test, which need fixes before SWE-bench
- Recommended fixes list (specific file edits, not general observations)

**Files**:
- READS: `spectrum/SPECTRUM-OPS.md`, `evaluation/accuracy-improvements/PLAN.md`
- CREATES: `evaluation/swe-bench-prep/protocol-audit.md`

---

### H2 — SWE-bench Infrastructure Analyst
**Effort**: M | **Serial risk**: No | **DAG deps**: None

**Scope**: Research SWE-bench Pro infrastructure requirements and what a Spectrum adapter looks like.

**Research questions** (use WebSearch for external data):
1. **SWE-bench Pro harness**: How does the official evaluation harness work? What is `sb-cli`?
   What Docker images does it use? What does the task format look like (issue text, repo, failing
   tests)? Is it self-hosted or cloud-managed?
2. **Task format**: What does a SWE-bench Pro task instance provide to the agent?
   - The GitHub issue text
   - The failing test(s) that define "resolved"
   - The repo at a specific commit
   - Any additional context (PR, comments, linked issues)?
3. **Evaluation harness API**: How does the harness accept agent output? Patch format? Direct repo?
   What does a "resolved" verdict require?
4. **How other multi-agent systems run SWE-bench**:
   - Claude-flow: how does it submit to the harness?
   - Augment Code: any public documentation on their evaluation setup?
   - Factory: their four-phase pipeline — how does it interface with SWE-bench?
5. **Spectrum adapter design**: What does the adapter between Spectrum and SWE-bench look like?
   - Input side: how does the harness issue become Gold's input?
   - Output side: how does Howler's git diff become a patch the harness accepts?
   - What Spectrum artifacts (CONTRACT.md, HOOK.md) are needed for a single-issue run?
   - What artifacts can be skipped (Politico, Obsidian, ENTITIES.md) on a per-task run?
6. **Docker setup**: What containers are needed? Local vs. cloud evaluation trade-offs?
7. **Subset selection**: How do other systems choose which Pro tasks to run? Full 500? Random 50?
   Curated multi-file subset?

**Output**: `evaluation/swe-bench-prep/infrastructure.md`

Format requirements:
- Section: SWE-bench Pro task format (what the agent sees)
- Section: Evaluation harness API (how to submit output)
- Section: Docker/infrastructure setup
- Section: How competitors interface with the harness (Claude-flow, Augment Code, Factory)
- Section: Spectrum adapter design (concrete, with the specific Spectrum pipeline steps that map)
- Section: Recommended subset strategy (which 50-100 tasks, selection rationale)
- Sources cited for all factual claims

**Files**:
- READS: `evaluation/eval-v2/COMPETITIVE-EVAL-V2.md` (competitor pipeline descriptions)
- CREATES: `evaluation/swe-bench-prep/infrastructure.md`

---

### H3 — Pipeline Mapping Architect
**Effort**: M | **Serial risk**: No | **DAG deps**: None

**Scope**: Design how Spectrum's pipeline maps to SWE-bench's single-issue task format, and
produce three concrete pipeline variant designs for comparative evaluation.

**Key insight from the research**: SWE-bench tasks are single-issue fixes (avg 4.1 files, 107.4
lines). Most don't need 3+ Howlers. The research report identifies a tension: Spectrum's value on
SWE-bench comes from quality gates and contract enforcement, not parallelism. The benchmark
strategy should use 1-2 Howlers per task. But Gold's muster overhead (reading issue, writing
CONTRACT.md, running White Pre-Check, running Politico) adds latency and potential for
specification drift if Gold misunderstands the issue.

**Design three pipeline variants**:

**Variant A — Full Spectrum (single Howler, full muster)**:
- Gold reads issue, writes mini-CONTRACT.md (affected files, expected behavior, test targets)
- White Pre-Check validates contract against repo
- Single Howler implements fix
- Gray runs failing tests + issue re-read (reflexion)
- White + Gray + /diff-review triple gate
- No Politico (single Howler), no Obsidian (not a persistent project)
- Copper opens PR / submits patch to harness
- What does the Howler drop template look like for a SWE-bench task?
- What CONTRACT.md sections are used? Which are skipped?

**Variant B — Lite Spectrum (single Howler, lightweight muster)**:
- Gold reads issue, produces a compact 200-token "task brief" instead of full CONTRACT.md
- No White Pre-Check, no Politico
- Single Howler implements (with issue re-read reflexion + revision pass)
- White + Gray triple gate (only — no Obsidian, no Copper)
- Patch submission
- How does this differ from Variant A in instruction overhead?

**Variant C — Bare Sonnet (no Spectrum overhead)**:
- Direct task: "Read issue, implement fix, run tests, output patch"
- No Gold, no CONTRACT.md, no quality gates
- Pure implementation by a single Sonnet session
- This is the control baseline: what does Spectrum add or cost?

For each variant, document:
1. Step-by-step pipeline with estimated token cost per step (use TOKEN-OPTIMIZATION.md data)
2. What accuracy improvements (I1–I7) apply (some only make sense with a contract)
3. Coordination overhead: estimated wall-clock time added vs. bare Sonnet
4. Predicted failure modes (where does this variant break on SWE-bench tasks?)
5. Which SWE-bench Pro task types benefit most from this variant?

Also address: **Does Gold's muster overhead hurt accuracy?** Analyze the risk that Gold
misinterprets the issue and writes a CONTRACT.md that leads the Howler astray. This is testable
(run A vs. C and compare), but what's the a priori risk assessment?

**Output**: `evaluation/swe-bench-prep/pipeline-design.md`

Format requirements:
- Section per variant (A, B, C) with step-by-step pipeline and cost estimate table
- Section: Accuracy improvements mapping (which improvements apply to each variant)
- Section: Gold muster risk analysis (honest assessment of specification drift risk)
- Section: Recommended variant for initial run (with rationale)
- Howler Drop Template excerpt for Variant A (the actual prompt text Gold would use)

**Shared definitions** (referenced in CONTRACT.md for H4 and H5 to use consistently):
- "Variant A", "Variant B", "Variant C" as defined above
- "Overhead ratio" = (Spectrum pipeline wall-clock) / (bare Sonnet wall-clock)
- "Per-task token cost" = sum of all API tokens across all agents for one SWE-bench task

**Files**:
- READS: `spectrum/SPECTRUM-OPS.md`, `evaluation/TOKEN-OPTIMIZATION.md`
- CREATES: `evaluation/swe-bench-prep/pipeline-design.md`

---

### H4 — Cost and Speed Modeler
**Effort**: M | **Serial risk**: No | **DAG deps**: H3#types (waits for H3's pipeline variant definitions to be STABLE before finalizing cost model)

**Note**: H4 has a soft dependency on H3's pipeline variant definitions. H4 should read H3's
HOOK.md and wait for `Checkpoints.types: STABLE` before writing the final cost table. H4 can
start research and framework setup before H3's types are stable — only the final cost table per
variant needs to wait.

**Scope**: Model token costs and wall-clock times for 50-task and 100-task SWE-bench Pro runs
through each of the three pipeline variants (A, B, C).

**Research questions**:
1. **Per-task token breakdown** (use TOKEN-OPTIMIZATION.md as the baseline):
   - Gold muster for a single issue (smaller than a full Spectrum muster — no MANIFEST.md DAG,
     no Politico, no ARCHITECTURE.md). Estimate input/output tokens.
   - Howler implementation session for a median SWE-bench Pro task (4.1 files, 107 lines).
     How does this compare to a typical Spectrum Howler session (~120k billed input tokens)?
   - White + Gray quality gate (per-task, not per-Spectrum)
   - Copper patch submission
2. **Variant cost comparison**:
   - Variant A (full muster): per-task token cost and wall-clock estimate
   - Variant B (lite muster): per-task token cost and wall-clock estimate
   - Variant C (bare Sonnet): per-task token cost and wall-clock estimate
   - Overhead ratio per variant (defined in H3 CONTRACT.md)
3. **Run-level costs**:
   - 50-task run through each variant: total cost, total wall-clock (assuming parallel runs)
   - 100-task run through each variant
   - What's the budget ceiling before results become statistically meaningful? (Standard practice:
     50+ tasks for meaningful SWE-bench scores; Augment Code ran all 500 Verified tasks)
4. **Competitor cost comparison** (research via WebSearch):
   - Factory, Augment Code, Claude-flow: any published per-task cost data?
   - Published benchmark reports sometimes include token or compute cost estimates
5. **Cost sensitivity analysis**:
   - If Howler sessions run longer than estimated (complex tasks), how does cost scale?
   - What's the cost if 30% of tasks require a revision pass (step 8c)?
   - What's the cost of a failed task (Howler marks blocked, Orange retry)?

**Output**: `evaluation/swe-bench-prep/cost-model.md`

Format requirements:
- Section: Per-task token breakdown by variant (table with input/output tokens per agent role)
- Section: 50-task and 100-task run cost table (3 variants × 2 run sizes = 6 cells)
- Section: Wall-clock time model (parallel task execution assumptions)
- Section: Competitor cost comparison (cite sources, note if estimates or reported figures)
- Section: Cost sensitivity analysis (revision pass impact, failure rate impact)
- Section: Budget recommendation (minimum viable run size for statistically meaningful results)

**Files**:
- READS: `evaluation/TOKEN-OPTIMIZATION.md`, H3's HOOK.md (for variant definitions)
- CREATES: `evaluation/swe-bench-prep/cost-model.md`

---

### H5 — Competitive Intelligence
**Effort**: M | **Serial risk**: No | **DAG deps**: None

**Scope**: Research how the top competitors run their SWE-bench evaluations, focusing on the
five systems that score D3=3 or D3=4 in the competitive evaluation.

**Competitors to study** (from COMPETITIVE-EVAL-V2.md D3 leaders):
- **Augment Code/Intent** (D3=4, 70.6% SWE-bench Verified): What pipeline? What context engine?
  How many tasks? How is the Context Engine integrated with the evaluation harness?
- **GitHub Copilot Workspace** (D3=4, 55-56% SWE-bench Verified): What's the evaluation setup?
  How does a workspace-based agent interface with SWE-bench?
- **Factory** (D3=3, 58.75% SWE-bench Verified): Four-phase Spec→Test→Implement→Verify — how
  does this map to SWE-bench task format? What does their "Droids" agent infrastructure look like?
- **Amazon Q** (D3=3 equivalent, 66% — cited in research report): What's their evaluation approach?
- **Claude-flow** (claimed 85% — cite with skepticism; research what's verifiable): What do they
  actually report? What pipeline do they use? Is 85% on SWE-bench Verified plausible given Sonnet
  4.6's baseline is 79.6%?

**Research questions per competitor** (use WebSearch):
1. What exact SWE-bench variant did they run? (Verified vs. Pro, subset size)
2. What is their per-task pipeline? (Planning → implementation → verification steps)
3. What is their per-task cost? (Token counts or dollar amounts if published)
4. What tricks or techniques explain their score? (Beyond the model baseline)
5. What subset of tasks did they choose? (Full set, random, curated?)
6. Were results independently verified? (Or self-reported to the leaderboard?)

**Techniques to extract**: What specific techniques from each competitor are candidates for
Spectrum adoption? (See ACCURACY-REPORT.md "What Competitors Do That Spectrum Should Steal"
table as a starting point — update with any new findings.)

**Score credibility assessment**: For each competitor's published score, assess credibility:
- Self-reported to leaderboard vs. independently verified
- SWE-bench Verified (contaminated) vs. SWE-bench Pro (harder, cleaner)
- Full 500-task run vs. curated subset

**Output**: `evaluation/swe-bench-prep/competitive-intel.md`

Format requirements:
- One section per competitor (5 competitors) with: pipeline description, evaluation setup,
  per-task cost (if available), score credibility assessment, techniques to steal
- Section: Technique extraction table (what Spectrum should adopt, effort, expected impact)
- Section: Score credibility ranking (which scores are most and least credible)
- Section: What Spectrum's realistic score range is given the competitive data
- Sources cited for all factual claims (WebSearch results with URLs)

**Files**:
- READS: `evaluation/eval-v2/COMPETITIVE-EVAL-V2.md`, `evaluation/accuracy-research/ACCURACY-REPORT.md`
- CREATES: `evaluation/swe-bench-prep/competitive-intel.md`

---

### H6 — Synthesis and Readiness Report (Sequential — waits for H1–H5)
**Effort**: L | **Serial risk**: Yes | **DAG deps**: H1, H2, H3, H4, H5 (all complete)

**Scope**: Synthesize H1–H5 outputs into a go/no-go readiness assessment.

**Seven questions to answer** (one section each):

**Q1 — Protocol readiness** (from H1):
Are the 7 accuracy improvements implementable as documented? What needs to be fixed before
running SWE-bench? Specific list of blockers vs. warnings.

**Q2 — Infrastructure feasibility** (from H2):
What does the adapter look like? Is it buildable in 1-2 weeks? What are the blockers?
Docker setup complexity? Harness API stability?

**Q3 — Pipeline mapping** (from H3):
Which variant (A, B, or C) should we use for the initial run? What does the Howler drop
template look like for a SWE-bench task? Are there unsolvable mapping problems?

**Q4 — Gold muster overhead risk** (from H3 + H4):
Synthesize H3's risk analysis with H4's cost model. Does the overhead ratio justify the
quality gate benefit? Is there a case for Variant B (lite) as the initial run?
What's the breakeven: how much accuracy improvement from quality gates is needed to
justify the cost premium over bare Sonnet?

**Q5 — Cost projection** (from H4):
What is the projected cost for a 50-task and 100-task run through the recommended variant?
What's the budget to publish competitive results? Is this feasible given Spectrum's context
(a protocol, not a commercial product with evaluation budget)?

**Q6 — Competitive intelligence** (from H5):
Which competitor techniques should be adopted before the benchmark run? Which are
already in the protocol (H1's audit informs this)? Is there a technique we're missing
that's a high-ROI addition?

**Q7 — Timeline and effort** (synthesis across all):
Given infrastructure build time (H2), protocol fixes (H1), and run costs (H4), what's
the realistic timeline to publish results? What are the critical path items?

**Go/No-Go Recommendation**:
- **Go**: Protocol is ready, infrastructure is buildable, cost is feasible, timeline is realistic
- **Go with prerequisites**: List specific blockers to address first
- **No-go**: Fundamental problem that makes SWE-bench evaluation unviable now

**Next steps checklist** (regardless of go/no-go):
- Ordered list of specific actions with owners (Gold, a Howler, Brown, the human)
- Milestone dates based on the timeline estimate
- Dependencies between actions

**Output**: `evaluation/swe-bench-prep/READINESS-REPORT.md`

Format requirements:
- Executive summary (3-5 lines: go/no-go recommendation + critical path)
- Seven sections (one per question above)
- Go/No-Go section with clear recommendation
- Next steps checklist with ordering and owners

**Files**:
- READS: `evaluation/swe-bench-prep/protocol-audit.md`, `evaluation/swe-bench-prep/infrastructure.md`,
  `evaluation/swe-bench-prep/pipeline-design.md`, `evaluation/swe-bench-prep/cost-model.md`,
  `evaluation/swe-bench-prep/competitive-intel.md`
- CREATES: `evaluation/swe-bench-prep/READINESS-REPORT.md`

---

## File Ownership Matrix

| File | H1 | H2 | H3 | H4 | H5 | H6 |
|------|----|----|----|----|----|----|
| `evaluation/swe-bench-prep/protocol-audit.md` | CREATES | — | — | — | — | READS |
| `evaluation/swe-bench-prep/infrastructure.md` | — | CREATES | — | — | — | READS |
| `evaluation/swe-bench-prep/pipeline-design.md` | — | — | CREATES | READS | — | READS |
| `evaluation/swe-bench-prep/cost-model.md` | — | — | — | CREATES | — | READS |
| `evaluation/swe-bench-prep/competitive-intel.md` | — | — | — | — | CREATES | READS |
| `evaluation/swe-bench-prep/READINESS-REPORT.md` | — | — | — | — | — | CREATES |
| `spectrum/SPECTRUM-OPS.md` | READS | — | READS | READS | — | — |
| `evaluation/TOKEN-OPTIMIZATION.md` | — | — | — | READS | — | — |
| `evaluation/accuracy-improvements/PLAN.md` | READS | — | — | — | — | — |
| `evaluation/eval-v2/COMPETITIVE-EVAL-V2.md` | — | READS | — | — | READS | — |
| `evaluation/accuracy-research/ACCURACY-REPORT.md` | — | — | — | — | READS | — |

**Conflict check**: H4 READS pipeline-design.md (H3 CREATES) — this is the H3#types checkpoint
dependency. No two Howlers write to the same file. Clean.

---

## DAG

```yaml
- id: H1-protocol-auditor
  deps: []
  effort: M
  serial_risk: no
  branch: spectrum/<rain-id>/H1-protocol-auditor
  base_branch: main
  base_commit: <to-be-set-at-muster>

- id: H2-infra-analyst
  deps: []
  effort: M
  serial_risk: no
  branch: spectrum/<rain-id>/H2-infra-analyst
  base_branch: main
  base_commit: <to-be-set-at-muster>

- id: H3-pipeline-architect
  deps: []
  effort: M
  serial_risk: no
  branch: spectrum/<rain-id>/H3-pipeline-architect
  base_branch: main
  base_commit: <to-be-set-at-muster>

- id: H4-cost-modeler
  deps: [H3#types]
  effort: M
  serial_risk: no
  branch: spectrum/<rain-id>/H4-cost-modeler
  base_branch: main
  base_commit: <to-be-set-at-muster>

- id: H5-competitive-intel
  deps: []
  effort: M
  serial_risk: no
  branch: spectrum/<rain-id>/H5-competitive-intel
  base_branch: main
  base_commit: <to-be-set-at-muster>

- id: H6-synthesis
  deps: [H1-protocol-auditor, H2-infra-analyst, H3-pipeline-architect, H4-cost-modeler, H5-competitive-intel]
  effort: L
  serial_risk: yes
  branch: spectrum/<rain-id>/H6-synthesis
  base_branch: main
  base_commit: <to-be-set-at-muster>
```

**Drop order**:
1. Drop H1, H2, H3, H5 in parallel (no deps, no shared files)
2. Drop H4 once H3 signals `Checkpoints.types: STABLE` (pipeline variant definitions frozen)
3. Drop H6 once H1–H5 all complete

---

## CONTRACT.md Seed (for Gold to expand)

Gold must define these shared terms in CONTRACT.md before drop:

### Shared Definitions

**Pipeline variants** (H3 defines authoritatively; H4 and H5 must use these terms):
- **Variant A** — Full Spectrum with single Howler: full muster (CONTRACT.md, White Pre-Check) +
  single Howler + triple quality gate (White + Gray + /diff-review)
- **Variant B** — Lite Spectrum: compact task brief (no full CONTRACT.md) + single Howler +
  double quality gate (White + Gray, skip /diff-review)
- **Variant C** — Bare Sonnet: no Gold, no CONTRACT.md, no quality gates; single Sonnet session

**Metrics** (all Howlers must use consistent definitions):
- **Per-task token cost**: sum of all API tokens (input + output) across all agents for one
  SWE-bench task instance, from issue ingestion through patch submission
- **Overhead ratio**: (Variant A or B per-task wall-clock) / (Variant C per-task wall-clock)
- **Accuracy**: percentage of SWE-bench Pro task instances resolved (harness verdict = "resolved")
- **Coverage**: number of task instances attempted vs. full Pro set (500 tasks)

**Protocol terminology** (H1 uses these; H6 must match):
- "Ready" improvement: documented, internally consistent, implementable without gaps
- "Blocker": a gap that would cause incorrect behavior in a SWE-bench run
- "Warning": a gap that would degrade the protocol but not cause incorrect behavior

### Integration Points

- H3 → H4: H3's pipeline variant step-by-step sequences are the input to H4's token model.
  H3 must signal `Checkpoints.types: STABLE` in HOOK.md when variant definitions are frozen.
- H1 → H6: H1's readiness table (Green/Yellow/Red per improvement) feeds Q1 in READINESS-REPORT.
- H4 → H6: H4's cost tables feed Q5. H6 uses H4's recommended variant as one input to Q4.
- H5 → H6: H5's technique extraction table feeds Q6. H5's score credibility assessments inform
  the competitive framing in H6.
- H2 → H6: H2's adapter design and infrastructure complexity assessment feeds Q2.

---

## Acceptance Criteria

### H1 — Protocol Validation Auditor
- [ ] One section per improvement (I1–I7) with Green/Yellow/Red rating and specific findings
- [ ] Howler Drop Template holistic review (numbering, coherence, length)
- [ ] HOOK.md Template review (matches drop template instructions)
- [ ] Muster Checklist review (every step covered, no orphan items)
- [ ] Summary table of readiness ratings
- [ ] Specific recommended fixes (not generic observations)

### H2 — SWE-bench Infrastructure Analyst
- [ ] SWE-bench Pro task format documented (what the agent receives per task)
- [ ] Evaluation harness API documented (how to submit, what "resolved" means)
- [ ] Docker/infrastructure setup documented
- [ ] Competitor harness integration documented (at least Claude-flow + one commercial system)
- [ ] Spectrum adapter design documented (concrete mapping of Spectrum pipeline steps)
- [ ] Subset selection strategy recommended with rationale
- [ ] All factual claims cite sources (URLs)

### H3 — Pipeline Mapping Architect
- [ ] Three pipeline variants documented (A, B, C) with step-by-step pipelines
- [ ] Per-variant cost estimate table (input to H4)
- [ ] Per-variant accuracy improvement mapping (which of I1–I7 apply)
- [ ] Gold muster risk analysis (specification drift risk, honest assessment)
- [ ] Recommended variant identified with rationale
- [ ] Howler drop template excerpt for Variant A
- [ ] Checkpoints.types: STABLE signaled in HOOK.md when variant definitions are frozen

### H4 — Cost and Speed Modeler
- [ ] Per-task token breakdown by variant (table format)
- [ ] 50-task and 100-task run cost table (3 variants × 2 sizes)
- [ ] Wall-clock time model documented
- [ ] Competitor cost comparison (with sources)
- [ ] Sensitivity analysis (revision pass impact, failure rate impact)
- [ ] Budget recommendation (minimum meaningful run size)

### H5 — Competitive Intelligence
- [ ] Five competitor sections (Augment Code, GitHub Copilot Workspace, Factory, Amazon Q,
  Claude-flow) with pipeline, cost, credibility assessment
- [ ] Technique extraction table (what Spectrum should adopt)
- [ ] Score credibility ranking
- [ ] Realistic Spectrum score range estimate
- [ ] All factual claims cite WebSearch sources

### H6 — Synthesis and Readiness Report
- [ ] Seven question sections answered (Q1–Q7)
- [ ] Go/No-Go recommendation with clear rationale
- [ ] Next steps checklist with ordering, owners, and milestone estimates
- [ ] Executive summary (3-5 lines)

---

## Quality Gates

Standard triple gate per Howler before PR open:
1. **White** — zero blockers required (these are research/analysis docs; White checks for logical
   consistency, unsupported claims, and missing citations)
2. **Gray** — zero test failures required (no code in this spectrum; Gray checks that all
   referenced files exist and that output documents are well-formed markdown)
3. **/diff-review** — zero security criticals required (doc-only spectrum; criticals would be
   very unusual — would flag only if Howler included API keys or sensitive data in docs)

Coverage gaps and high/medium security findings are warnings in the PR description.

---

## Decomposition Hazard Scan

**Does any Howler synthesize outputs from others?**
H6 synthesizes H1–H5. This is explicitly sequential (H6 has full deps on all). No barrel file
or fragment+stitch pattern needed — H6 reads completed documents and synthesizes.

**Are any tasks inherently serial?**
H6 is serial by design. H4 has a soft serial dep on H3#types (variant definitions). All others
are genuinely parallel.

**Is any task significantly larger than peers?**
H6 is `effort: L` — it reads five documents (potentially 30-50 pages of research) and synthesizes
them into a coherent assessment. Gold should flag this as critical-path risk: if H6 context
accumulation is large, ensure the Howler doesn't start until all H1–H5 PRs are merged (not just
completed), so H6 reads the final versions of documents, not in-progress drafts.

**H4 bottleneck risk**: H4 cannot finalize its cost tables until H3 signals STABLE. If H3 runs
long, H4's completion is delayed. Mitigation: H4 starts with framework and research (external
competitor cost data) before H3#types is ready. Only the per-variant cost table (the key H6
input) needs to wait.

**Alternative decompositions considered**:
- *7 parallel Howlers (H1–H7, no synthesis Howler)*: Rejected. Without a synthesis Howler, the
  seven research outputs don't produce a go/no-go recommendation — they're a pile of documents.
  H6 is critical-path work that requires a dedicated pass.
- *2 Howlers (research + synthesis)*: Rejected. Research scope is too broad for 2 Howlers.
  The research questions (infrastructure, pipeline design, cost modeling, competitive intel,
  protocol audit) are genuinely distinct and benefit from parallel investigation.

---

## Execution Order

1. **Blue → PLAN.md**: This document.
2. **Gold muster**: Generate rain ID, validate PLAN.md, write MANIFEST.md + CONTRACT.md (with
   shared definitions seeded above), run White Pre-Check, run Politico, present for approval.
3. **Drop H1, H2, H3, H5 in parallel** (H4 pending H3#types).
4. **Drop H4** once H3 signals `Checkpoints.types: STABLE`.
5. **Triple quality gate** (White + Gray + /diff-review) per Howler as each completes.
6. **Pax** after H1–H5 complete: Gold reads all debriefs, validates documents exist, checks
   seam cross-references between H3→H4 and H5→H6.
7. **Human merges H1–H5 PRs** (recommended order: H1, H3, H2, H5, H4).
8. **Drop H6** after all H1–H5 PRs merged (H6 reads final document versions).
9. **H6 triple quality gate** + Copper PR.
10. **Triumph**: Gray on merged main, Obsidian verifies acceptance criteria, Brown drafts
    LESSONS.md update, Gold reviews and commits.

---

## Notes for Gold Muster

- **No ARCHITECTURE.md needed**: This project has no persistent source code architecture.
  The evaluation directory is documents, not code. Skip ARCHITECTURE.md.
- **No convoy-contracts.d.ts**: Doc-only spectrum. Skip.
- **No contract tests (I5)**: Doc-only spectrum. Contract-to-test generation is for TypeScript/
  Python spectrums. Skip.
- **White Pre-Check**: Valuable here. H4 references TOKEN-OPTIMIZATION.md figures; H5 references
  COMPETITIVE-EVAL-V2.md scores. White Pre-Check should verify these files exist and the specific
  sections referenced in CONTRACT.md are accurate.
- **Politico**: Should focus on: (1) does the H3→H4 interface (variant definitions) adequately
  specify what H4 needs? (2) does H6's synthesis task have enough specificity in its reading list?
  (3) are any research tasks likely to yield insufficient data for H6 to answer its question?
- **LESSONS.md patterns to check**: The remnant-ux-0329 lesson about "worktree cleanup before
  tests" is irrelevant (no tests). The convoy-v3-0328 "stitcher bottleneck timing" lesson is
  relevant: H6 is the stitcher here. Allow adequate time and context window for H6.
- **Reaping mode is NOT appropriate**: H3's pipeline design and H4's cost model require
  CONTRACT.md coordination on shared definitions. Reaping mode skips CONTRACT.md.

---

*Blue (Sonnet), 2026-03-31*
