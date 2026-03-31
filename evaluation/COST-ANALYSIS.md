# Spectrum Protocol — Token Cost & Optimization Analysis

Generated: 2026-03-30

---

## Pricing Reference

| Model | Input $/M | Output $/M |
|-------|-----------|------------|
| Opus | $15.00 | $75.00 |
| Sonnet | $3.00 | $15.00 |
| Haiku | $0.80 | $4.00 |

---

## Analysis 1: Token Cost Inventory

### Document Size Assumptions

| Artifact | Lines | Est. Tokens |
|----------|-------|-------------|
| SPECTRUM-OPS.md (ops manual) | 550 | ~12,000 |
| SPECTRUM.md (full spec) | 2,300 | ~50,000 |
| CLAUDE.md (routing rules) | 270 | ~6,000 |
| PLAN.md (typical) | 150 | ~3,500 |
| LESSONS.md (after 3 runs) | 200 | ~4,500 |
| ENTITIES.md (medium project) | 100 | ~2,500 |
| ARCHITECTURE.md | 75 | ~2,000 |
| MANIFEST.md | 200 | ~4,500 |
| CONTRACT.md (full DbC) | 150 | ~3,500 |
| HOOK.md (completed) | 80 | ~2,000 |
| Debrief (YAML + narrative) | 100 | ~2,500 |
| SEAM-CHECK.md | 60 | ~1,500 |
| PAX-PLAN.md | 80 | ~2,000 |
| SENTINEL-REPORT.md | 80 | ~2,000 |
| convoy-contracts.d.ts | 50 | ~1,200 |
| Howler drop prompt template | 100 | ~2,500 |
| Discovery relay | — | ~500 |
| Key source files (2-3 per Howler) | — | ~3,000 |

### Phase-by-Phase Inventory

**N = number of Howlers; assume each Howler produces one debrief, one HOOK.md, opens one PR.**

---

#### Phase 0 — Blue (Sonnet): PLAN.md

| | Tokens |
|-|--------|
| Input | System prompt (~2k) + codebase context (grep/read passes ~15k) + LESSONS.md (~4.5k) = ~22,000 |
| Output | PLAN.md ~3,500 |
| Model | Sonnet |
| Cost | Input: 22k × $3/M = $0.066 · Output: 3.5k × $15/M = $0.053 · **Total: ~$0.12** |

---

#### Phase 1 — Gold Muster (Opus)

Gold reads a lot before writing anything. This is the most expensive single invocation.

| Input Component | Tokens |
|----------------|--------|
| System prompt + CLAUDE.md | ~8,000 |
| SPECTRUM-OPS.md (included in Gold prompt) | ~12,000 |
| PLAN.md | ~3,500 |
| LESSONS.md | ~4,500 |
| ENTITIES.md | ~2,500 |
| ARCHITECTURE.md (read + patch) | ~2,000 |
| File sampling (3-5 source files for PLAN.md validation) | ~6,000 |
| Conversation overhead | ~2,000 |
| **Total Input** | **~40,500** |

| Output Component | Tokens |
|-----------------|--------|
| MANIFEST.md | ~4,500 |
| CONTRACT.md | ~3,500 |
| convoy-contracts.d.ts (TypeScript) | ~1,200 |
| CHECKPOINT.json initial | ~800 |
| ARCHITECTURE.md updates (patching) | ~2,000 |
| Reasoning/thinking tokens | ~3,000 |
| **Total Output** | **~15,000** |

Cost: Input 40.5k × $15/M = $0.608 · Output 15k × $75/M = $1.125 · **Total: ~$1.73**

---

#### Phase 1.5 — Politico (Sonnet): Adversarial Review

| | Tokens |
|-|--------|
| Input | System prompt (~2k) + MANIFEST.md (~4.5k) + CONTRACT.md (~3.5k) = ~10,000 |
| Output | Blockers/warnings report ~2,000 |
| Model | Sonnet |
| Cost | Input: 10k × $3/M = $0.030 · Output: 2k × $15/M = $0.030 · **Total: ~$0.06** |

---

#### Phase 2 — Each Howler Drop (Sonnet, × N)

The Howler drop template includes the FULL CONTRACT.md. This is significant.

| Input Component | Tokens |
|----------------|--------|
| System prompt + SPECTRUM-OPS.md context | ~14,000 |
| Task scope (from MANIFEST.md) | ~500 |
| File ownership (from MANIFEST.md) | ~300 |
| CONTRACT.md (full, all DbC sections) | ~3,500 |
| Discovery relay (if dependent Howler) | ~500 |
| **Total Input per Howler (at dispatch)** | **~18,800** |

During execution, each Howler reads/writes files and accumulates context. Typical mid-run context window for a medium task (S/M scope):

| Execution Context | Tokens |
|-----------------|--------|
| Tool call outputs (file reads, git, ls, tests) | ~20,000 |
| Conversation history (messages back and forth) | ~8,000 |
| HOOK.md writes (multiple updates) | ~3,000 |
| **Total Execution Context** | **~31,000** |

| Output (per Howler) | Tokens |
|-------------------|--------|
| Code written (medium task ~300 lines) | ~8,000 |
| HOOK.md (written + updated) | ~2,000 |
| Debrief entry | ~2,500 |
| Tool calls + reasoning | ~5,000 |
| **Total Output per Howler** | **~17,500** |

Cost per Howler: Input (18.8k + 31k) × $3/M = $0.149 · Output 17.5k × $15/M = $0.263 · **Total: ~$0.41 per Howler**

---

#### Phase 3a — Per Howler: White (Sonnet)

| | Tokens |
|-|--------|
| Input | System prompt (~2k) + git diff (~8k for medium PR) + HOOK.md (~2k) + CONTRACT.md (~3.5k) = ~15,500 |
| Output | Review report ~3,000 |
| Model | Sonnet |
| Cost | Input: 15.5k × $3/M = $0.047 · Output: 3k × $15/M = $0.045 · **Total: ~$0.09 per Howler** |

If blockers found and White re-runs: add 50% → ~$0.14 per Howler.

---

#### Phase 3b — Per Howler: Gray (Sonnet)

| | Tokens |
|-|--------|
| Input | System prompt (~2k) + test runner output (~5k) + relevant files (~6k) + HOOK.md (~2k) = ~15,000 |
| Output | Test report + any new test code ~4,000 |
| Model | Sonnet |
| Cost | Input: 15k × $3/M = $0.045 · Output: 4k × $15/M = $0.060 · **Total: ~$0.11 per Howler** |

---

#### Phase 3c — Per Howler: /diff-review (Sonnet)

| | Tokens |
|-|--------|
| Input | System prompt (~2k) + diff (~8k) = ~10,000 |
| Output | Security report ~1,500 |
| Model | Sonnet |
| Cost | Input: 10k × $3/M = $0.030 · Output: 1.5k × $15/M = $0.023 · **Total: ~$0.05 per Howler** |

---

#### Phase 4 — Gold Pax (Opus)

| Input Component | Tokens |
|----------------|--------|
| System prompt + SPECTRUM-OPS.md | ~14,000 |
| All N debriefs (2,500 × N) | N × 2,500 |
| All N HOOK.md files (2,000 × N) | N × 2,000 |
| CONTRACT.md | ~3,500 |
| SEAM-CHECK.md | ~1,500 |
| Key source files (2-3 per Howler) | N × 3,000 |
| CHECKPOINT.json | ~800 |
| **Total Input (5-Howler example)** | **~51,300** |

| Output | Tokens |
|--------|--------|
| PAX-PLAN.md | ~2,000 |
| SEAM-CHECK.md | ~1,500 |
| CHECKPOINT.json updates | ~500 |
| Per-PR self-reflect entries (N × 100) | N × 100 |
| Reasoning | ~3,000 |
| **Total Output (5-Howler)** | **~7,500** |

Cost (5-Howler): Input 51.3k × $15/M = $0.770 · Output 7.5k × $75/M = $0.563 · **Total: ~$1.33**

For 3-Howler: Input ~37.8k → $0.567 · Output ~6.8k → $0.510 · **Total: ~$1.08**
For 8-Howler: Input ~71.3k → $1.070 · Output ~9.3k → $0.698 · **Total: ~$1.77**

---

#### Phase 5 — Per-PR Merge: Gray Integration (Sonnet, × N merges)

| | Tokens |
|-|--------|
| Input | System prompt (~2k) + test output (~5k) + context (~3k) = ~10,000 |
| Output | Pass/fail report ~1,000 |
| Model | Sonnet |
| Cost per merge | Input: 10k × $3/M = $0.030 · Output: 1k × $15/M = $0.015 · **Total: ~$0.05 per merge** |

---

#### Phase 5b — Per-PR Self-Reflect: Gold (Opus, × N merges)

This is a Gold invocation for a 3-5 line note in CHECKPOINT.json. Very light but Opus-priced.

| | Tokens |
|-|--------|
| Input | Context (CHECKPOINT.json + merge result ~3k) = ~3,000 |
| Output | 3-5 line reflection ~150 |
| Model | Opus |
| Cost per merge | Input: 3k × $15/M = $0.045 · Output: 0.15k × $75/M = $0.011 · **Total: ~$0.056 per merge** |

---

#### Phase 6 — Final Gray Run (Sonnet)

| | Tokens |
|-|--------|
| Input | System prompt (~2k) + full test suite output (~8k) + context (~3k) = ~13,000 |
| Output | Report ~2,000 |
| Model | Sonnet |
| Cost | Input: 13k × $3/M = $0.039 · Output: 2k × $15/M = $0.030 · **Total: ~$0.07** |

---

#### Phase 6.25 — Obsidian (Sonnet)

| | Tokens |
|-|--------|
| Input | System prompt (~2k) + PLAN.md (~3.5k) + MANIFEST.md (~4.5k) + key files from merged codebase (~10k) = ~20,000 |
| Output | SENTINEL-REPORT.md ~2,000 |
| Model | Sonnet |
| Cost | Input: 20k × $3/M = $0.060 · Output: 2k × $15/M = $0.030 · **Total: ~$0.09** |

---

#### Phase 6.5 — Brown (Haiku): LESSONS.md Draft

| | Tokens |
|-|--------|
| Input | All debriefs (N × 2.5k) + MANIFEST.md (~4.5k) + SEAM-CHECK.md (~1.5k) + PAX-PLAN.md (~2k) + SENTINEL-REPORT.md (~2k) = ~(10k + 2.5N)k |
| Output | LESSONS-DRAFT.md ~3,000 |
| Model | Haiku |
| Cost (5-Howler) | Input: 22.5k × $0.80/M = $0.018 · Output: 3k × $4/M = $0.012 · **Total: ~$0.03** |

---

#### Phase 6.5b — Copper (Haiku): PR/Commit Operations (per Howler + post-merge)

| | Tokens |
|-|--------|
| Input | Staged files list + commit message template ~2,000 |
| Output | Git commands + PR description ~800 |
| Model | Haiku |
| Cost per invocation | Input: 2k × $0.80/M = $0.002 · Output: 0.8k × $4/M = $0.003 · **Total: ~$0.005 per PR** |

---

## Analysis 2: Estimated Total Cost Per Spectrum Run

### Scenario A: 3-Howler Reaping (Light Mode)

Reaping skips: Politico, Obsidian, ENTITIES.md, ARCHITECTURE.md, full DbC, LESSONS.md skimmed-only.
Gold Muster is simplified (~50% input reduction).

| Phase | Agent | Model | Cost |
|-------|-------|-------|------|
| Blue: PLAN.md | Blue | Sonnet | $0.12 |
| Muster (simplified) | Gold | Opus | $0.95 |
| Howler × 3 | Howlers | Sonnet | $1.23 |
| White × 3 | White | Sonnet | $0.27 |
| Gray × 3 | Gray | Sonnet | $0.33 |
| /diff-review × 3 | — | Sonnet | $0.15 |
| Gray per-merge × 3 | Gray | Sonnet | $0.15 |
| Gold self-reflect × 3 | Gold | Opus | $0.17 |
| Final Gray run | Gray | Sonnet | $0.07 |
| Brown LESSONS.md | Brown | Haiku | $0.02 |
| Copper × 3 PRs | Copper | Haiku | $0.015 |
| **Total** | | | **~$3.49** |

### Scenario B: 5-Howler Full Spectrum

| Phase | Agent | Model | Count | Unit Cost | Total |
|-------|-------|-------|-------|-----------|-------|
| Blue: PLAN.md | Blue | Sonnet | 1 | $0.12 | $0.12 |
| Gold Muster | Gold | Opus | 1 | $1.73 | $1.73 |
| Politico | Politico | Sonnet | 1 | $0.06 | $0.06 |
| Howlers | Howlers | Sonnet | 5 | $0.41 | $2.05 |
| White | White | Sonnet | 5 | $0.09 | $0.45 |
| Gray (per Howler) | Gray | Sonnet | 5 | $0.11 | $0.55 |
| /diff-review | — | Sonnet | 5 | $0.05 | $0.25 |
| Gold Pax | Gold | Opus | 1 | $1.33 | $1.33 |
| Gray per-merge | Gray | Sonnet | 5 | $0.05 | $0.25 |
| Gold self-reflect per-merge | Gold | Opus | 5 | $0.056 | $0.28 |
| Final Gray run | Gray | Sonnet | 1 | $0.07 | $0.07 |
| Obsidian | Obsidian | Sonnet | 1 | $0.09 | $0.09 |
| Brown LESSONS.md | Brown | Haiku | 1 | $0.03 | $0.03 |
| Copper PRs | Copper | Haiku | 5 | $0.005 | $0.025 |
| **Total** | | | | | **~$7.29** |

### Scenario C: 8-Howler Full Spectrum

| Phase | Agent | Model | Count | Unit Cost | Total |
|-------|-------|-------|-------|-----------|-------|
| Blue: PLAN.md | Blue | Sonnet | 1 | $0.12 | $0.12 |
| Gold Muster | Gold | Opus | 1 | $2.10* | $2.10 |
| Politico | Politico | Sonnet | 1 | $0.07* | $0.07 |
| Howlers | Howlers | Sonnet | 8 | $0.41 | $3.28 |
| White | White | Sonnet | 8 | $0.09 | $0.72 |
| Gray (per Howler) | Gray | Sonnet | 8 | $0.11 | $0.88 |
| /diff-review | — | Sonnet | 8 | $0.05 | $0.40 |
| Gold Pax | Gold | Opus | 1 | $1.77 | $1.77 |
| Gray per-merge | Gray | Sonnet | 8 | $0.05 | $0.40 |
| Gold self-reflect per-merge | Gold | Opus | 8 | $0.056 | $0.45 |
| Final Gray run | Gray | Sonnet | 1 | $0.07 | $0.07 |
| Obsidian | Obsidian | Sonnet | 1 | $0.09 | $0.09 |
| Brown LESSONS.md | Brown | Haiku | 1 | $0.04 | $0.04 |
| Copper PRs | Copper | Haiku | 8 | $0.005 | $0.04 |
| **Total** | | | | | **~$10.43** |

*Muster input grows with larger MANIFEST.md; Politico input grows slightly.

---

## Analysis 3: Model Assignment Optimization

### Question 1: Does Gold NEED Opus for every phase?

**Muster (Phase 1):** Yes — Opus is justified here. Muster requires:
- Decomposition hazard scanning (detecting subtle ownership conflicts across N tasks)
- Contract authoring (defining per-Howler DbC invariants that won't be renegotiated)
- File ownership conflict detection across potentially hundreds of files
- Incorporating LESSONS.md patterns into task decomposition

Sonnet has been observed in prior convoy work to "cut corners on integration" (per CLAUDE.md rationale). A bad MANIFEST.md cascades into circuit-breaker failures downstream, costing far more than the ~$0.80 saved. **Keep Opus here.**

**Pax (Phase 4):** Yes — Opus is justified here too. Independent validation requires reading 2-3 files per Howler and cross-checking them against CONTRACT.md postconditions without being fooled by a plausible-but-wrong Howler self-report. This is the "green but wrong" check that no other system does. Sonnet may pass superficial checks. **Keep Opus here.**

**Per-PR self-reflect (Phase 5b, × N merges):** No — this is a 3-5 line note. It does not require Opus reasoning depth. The content is mechanical: "PR N merged cleanly. Watch for X in the next merge." **Can be downgraded to Sonnet (see Optimization #1 below) or even structured as a Gold CHECKPOINT.json append with a fixed template, effectively free.**

### Question 2: Could any Sonnet agents be downgraded to Haiku?

**White (Inspector):** No. White's value is catching subtle contract compliance issues and security bugs. Haiku misses these — it validates surface-level style while approving broken interfaces. The remnant-infra-0329 LESSONS note that "Inspector caught 3 real blockers" supports keeping Sonnet. A false-pass from White means a broken PR opens and Gray is the only backstop.

**Gray (Outrider):** No. Diagnosing test failures and writing missing coverage requires reasoning about what the test is actually asserting vs. what the code does. Haiku writes superficial coverage (per CLAUDE.md rationale) and misdiagnoses flaky tests.

**/diff-review:** This is a skill invocation, not a model-selectable agent — model is determined by the skill implementation. No change possible here.

**Obsidian:** No. Spec compliance verification requires reading acceptance criteria from PLAN.md and making a judgment call about whether the merged code satisfies intent vs. letter. Haiku lacks the judgment depth to distinguish PARTIAL from PASS on ambiguous criteria.

**Politico:** Marginal. Politico is adversarial review of MANIFEST.md + CONTRACT.md — a focused read of two short documents. Haiku might work here, but the value-add of Politico is finding non-obvious gaps (e.g., a file that will be needed but isn't in the ownership matrix). This requires anticipatory reasoning. Risk: Haiku Politico would be worse than no Politico (false confidence). Keep Sonnet or skip (see Optimization #4).

### Question 3: Is Politico worth its cost?

**Politico costs ~$0.06 on a 5-Howler run.** It is one of the cheapest invocations in the whole protocol. The question is whether it catches something.

**What Politico uniquely catches that White doesn't:**
- File ownership gaps (files that will be needed but aren't assigned to any Howler) — White reviews per-Howler diffs and can't see cross-Howler gaps
- Decomposition flaws (task A should wait for task B but the DAG shows them parallel) — White never sees the DAG
- Contract ambiguities that lead to seam mismatches before any code is written — White catches post-hoc

**What Politico does NOT catch (that White catches instead):**
- Implementation bugs within a Howler's scope
- Contract violations at the code level
- Security issues in the actual diff

**Verdict:** At $0.06, Politico is one of the highest ROI invocations in the protocol. A single structural failure caught pre-dispatch saves ~$1-3 in recovery work (re-muster + re-dispatch). Skip only in reaping mode (which the spec already prescribes). **No change recommended.**

### Question 4: Is Obsidian (post-merge Sentinel) worth its cost?

**Obsidian costs ~$0.09.** It runs after all PRs merge and all quality gates have passed.

**What the triple gate catches:** Implementation bugs, contract violations in code, test failures, security issues in each PR individually.

**What Obsidian uniquely catches:** Whether the system as a whole satisfies the original PLAN.md acceptance criteria. The triple gate is Howler-scoped; Obsidian is spectrum-scoped. Examples of what it catches:
- "User can export data as CSV" was in PLAN.md but no Howler claimed ownership of it — it fell through the cracks
- An acceptance criterion was split across Howlers and neither half alone satisfies it

**Verdict:** The skip in reaping mode is correct (pure-create with no interface deps is less likely to have cross-Howler gap failures). For full spectrum runs, $0.09 to close the plan-vs-delivery loop is justified. **No change recommended for full mode.**

### Question 5: Could the triple gate be reduced to double for low-risk Howlers?

The spec already has an implicit "skip /diff-review for doc-only spectrums, test-only changes, non-security config." For pure-create Howlers with no external data handling:

- Removing /diff-review saves ~$0.05 per Howler
- For an 8-Howler run where 4 Howlers are pure-create internal utilities: saves ~$0.20

This is a reasonable conditional: **apply /diff-review only to Howlers that touch authentication, authorization, external API calls, user data handling, or configuration with security implications.** Gold can tag these in MANIFEST.md as `security_gate: required` vs `security_gate: optional`.

---

## Analysis 4: Context Window Optimization

### Finding 1: Full CONTRACT.md in every Howler dispatch — HIGH IMPACT

The Howler drop template injects the **full CONTRACT.md** into every Howler's prompt. For a 5-Howler run with a 3,500-token CONTRACT.md:
- Total tokens wasted: 5 × 3,500 = 17,500 tokens
- Cost: 17,500 × $3/M = **$0.053 additional per 5-Howler run**

More importantly, full CONTRACT.md includes ALL Howlers' DbC sections, not just the receiving Howler's. A Howler sees `howler-api`'s preconditions even when it's `howler-auth`.

**Optimization:** Inject per-Howler CONTRACT.md slice into drop prompt:
- Global sections (Shared Types, Constants, Conventions): always included
- DbC section: only the receiving Howler's Preconditions/Postconditions/Invariants
- Other Howlers' DbC: omit entirely

Savings per Howler: reduces CONTRACT.md payload from ~3,500 tokens to ~1,800 tokens.
5-Howler savings: 5 × 1,700 × $3/M = **~$0.026 per 5-Howler run**. Modest cost savings but meaningful context reduction that reduces Howler drift risk.

**Caution:** Howlers need to understand what neighboring Howlers expect from them (seam awareness). The current full-CONTRACT approach ensures Howlers see seam requirements even if they're under another Howler's DbC section. Mitigation: extract a "Seams affecting you" section from neighboring Howlers' DbC and inject that into the prompt. This preserves seam awareness while cutting unrelated DbC noise.

### Finding 2: SPECTRUM-OPS.md in Gold's system context — MEDIUM IMPACT

Gold receives SPECTRUM-OPS.md (~12,000 tokens) as part of its invocation context. This is necessary for Muster to follow the protocol correctly. However, SPECTRUM-OPS.md includes the Howler drop template verbatim (~2,500 tokens of template text), section headers for phases Gold isn't executing yet, and the Agent Teams integration preview sections (~2,000 tokens).

**Optimization:** The Howler drop template is copy-pasted from SPECTRUM-OPS.md — it does not need to live in both. If SPECTRUM-OPS.md were structured so Gold can reference specific sections, the total prompt context could be reduced. However, this is an authoring concern, not a runtime concern — the protocol spec can't easily be chunked at runtime. **Low feasibility. Skip.**

### Finding 3: Discovery relay — WELL-CALIBRATED

The ~500-token cap on discovery relay is explicitly set and described as "compressed." This is well-designed. No optimization needed.

### Finding 4: HOOK.md verbosity — MEDIUM IMPACT

The HOOK.md template includes sections that are often empty (`## Cross-Domain Observations: (none)`, `## Errors Encountered: (none)`, `## Blockers: (none)`). These empty sections add ~200 tokens per HOOK.md write. Across N Howlers doing multiple HOOK.md updates (each update repeats the full file), this accumulates.

More importantly: when Gold reads N HOOK.md files during Pax (Phase 4), it reads N × ~2,000 tokens. If Howlers are verbose in the completed HOOK.md (e.g., pasting full output from `ls -la` into Completion Verification), this can balloon to 4,000-6,000 tokens per HOOK.md.

**Optimization:** Instruct Howlers to keep Completion Verification results brief (e.g., `ls: PASS` not the full listing output) and to remove empty sections before final HOOK.md write. Savings: ~500-1,000 tokens per Howler at Pax input.

### Finding 5: Debrief YAML frontmatter — EFFICIENT

The debrief YAML frontmatter is well-structured and compact (~800-1,200 tokens). The field names are short. No wasted space. The narrative section is useful context for Gold during seam-checking. **No optimization needed.**

### Finding 6: Gold Pax reads key source files — MANAGEABLE

Independent validation requires Gold to read 2-3 key files per Howler (~3,000 tokens per Howler). For an 8-Howler run: up to 24,000 tokens of source file context in the Pax prompt. This is load-bearing — it's what makes the "don't trust Howler self-reports" guarantee meaningful.

**Optimization:** Gold can apply judgment on which Howlers need independent validation:
- Howlers with `confidence: high` + `contract_compliance: full` in their debrief: read 1 file (spot check)
- Howlers with `confidence: medium`: read 2 files (standard)
- Howlers with `confidence: low` or `contract_compliance: partial`: read 3+ files (full validation)

This saves ~3,000 tokens × (number of high-confidence Howlers) at Pax time. For a well-executed 5-Howler run where 3 are high-confidence, saves ~9,000 tokens of Opus input = **~$0.14**.

---

## Analysis 5: Invocation Count Optimization

### Finding 1: Per-PR self-reflect — HIGH SAVINGS POTENTIAL

Each merge triggers a Gold (Opus) invocation to write 3-5 lines in CHECKPOINT.json. For an 8-Howler run with 8 merges:
- Current cost: 8 × $0.056 = **$0.45 in Opus invocations for 3-5 lines each**

These 3-5 line reflections have value (they compound into informed merge decisions) but the invocation cost is disproportionate to the output size. Three options:

**Option A:** Downgrade to Sonnet. Cost: 8 × ~$0.03 = $0.24. Savings: $0.21 on an 8-Howler run.

**Option B:** Batch all self-reflects into Gold's Pax invocation (Phase 4) instead of per-merge. Gold already has all the context at Pax time. Write 3-5 lines per completed Howler as retrospective rather than per-merge. Cost: $0 additional (absorbed into Pax). Savings: full $0.45.

**Option C:** Provide a fixed template that Copper (Haiku) fills in post-merge from structured data in CHECKPOINT.json. Cost: ~$0.005 per merge. Savings: ~$0.43 for 8-Howler run.

**Recommendation: Option A (Sonnet).** The per-merge timing is what makes self-reflect valuable — "reflection N informs merge N+1" — so batching into Pax loses the real-time benefit. But Sonnet is sufficient for "what worked, what surprised, what to watch for." No deep reasoning required.

### Finding 2: White re-run after blocker fixes — CONDITIONAL COST

When White finds blockers and the Howler fixes them, White re-runs before Copper opens the PR. This is the right policy but adds ~$0.09 per re-run. The current spec allows up to 2 Orange retries, each potentially requiring a White re-run.

**In the worst case:** 2 Orange retries + 2 White re-runs per Howler = 3 White invocations × $0.09 = $0.27 per Howler extra. For an 8-Howler run where 3 Howlers have issues: +$0.81.

**No optimization recommended here** — White re-run is a correctness guarantee, not a waste.

### Finding 3: Combined White+Gray for small diffs — MARGINAL SAVINGS

Could White and Gray be one agent for diffs under, say, 100 lines?

**Verdict: No.** White and Gray have fundamentally different concerns:
- White: contract compliance, code quality, subtle bugs
- Gray: test correctness, coverage, flaky test diagnosis

Running them in a single invocation would require one agent to context-switch between two different evaluation frameworks. More importantly, they're parallel — merging them would make them sequential with the same total time. The $0.11 per-Howler savings is real but not worth the quality risk.

### Finding 4: Obsidian for reaping mode — ALREADY OPTIMIZED

The spec already skips Obsidian in reaping mode. The current policy is correct.

### Finding 5: Final Gray + Obsidian + Brown — EFFICIENT SEQUENCE

These three phase-6 agents are already correctly ordered: Gray → Obsidian → Brown. They can't be meaningfully parallelized (each depends on the prior), and they're already using the cheapest models appropriate to each task. No optimization.

---

## Top 5 Optimization Recommendations

### Rank 1: Per-PR Self-Reflect — Downgrade Gold → Sonnet
**Savings per run:**
- 3-Howler: 3 × ($0.056 - $0.028) = **$0.08**
- 5-Howler: 5 × $0.028 = **$0.14**
- 8-Howler: 8 × $0.028 = **$0.22**

**Implementation:** Change Gold self-reflect invocation to Sonnet. Input is small (~3k tokens), output is 3-5 lines — no Opus reasoning required.

**Quality risk:** Low. Self-reflect is a structured note about what just happened, not complex synthesis. Sonnet is more than adequate.

**Estimated annual savings** (assuming 2 full 5-Howler runs/month): ~$3.36/year. Not dramatic in absolute terms, but zero quality tradeoff.

---

### Rank 2: Per-Howler CONTRACT.md Slicing
**Savings per run:**
- 5-Howler: ~$0.026
- 8-Howler: ~$0.041

**Implementation:** Gold constructs a per-Howler contract section at dispatch time:
1. Always include: Shared Types, Shared Constants, Conventions, `convoy-contracts.d.ts` note
2. Include only: the target Howler's own DbC section (Preconditions, Postconditions, Invariants)
3. Include: a "Seams affecting you" summary from neighboring Howlers' DbC (Gold synthesizes 2-3 lines max)
4. Exclude: other Howlers' full DbC sections

**Quality risk:** Low, with the "Seams affecting you" bridge. The main risk is a Howler missing a seam requirement from a neighboring Howler's DbC. The bridge section mitigates this.

**Compounding benefit:** Reduces Howler's context window pressure during long runs, lowering the risk of context-limit failures that trigger costly recovery.

---

### Rank 3: Confidence-Tiered Independent Validation (Pax)
**Savings per run:**
- 5-Howler (3 high-confidence Howlers): 3 × 3,000 tokens Opus input saved = 9k × $15/M = **$0.135**
- 8-Howler (5 high-confidence): 5 × 3,000 × $15/M = **$0.225**

**Implementation:** Gold applies the following rule during Pax independent validation:
- `confidence: high` + `contract_compliance: full` → read 1 file (spot check)
- `confidence: medium` OR `contract_compliance: partial` → read 2-3 files (standard)
- `confidence: low` OR `contract_compliance: none/partial` + any seam warnings → read 3+ files

**Quality risk:** Low. High-confidence Howlers with full compliance have already passed White + Gray + /diff-review. The spot-check is adequate to detect gross contract violations.

---

### Rank 4: Conditional /diff-review Based on Security Surface
**Savings per run:**
- For an 8-Howler run with 4 pure-create internal Howlers: 4 × $0.05 = **$0.20**

**Implementation:** Gold tags each Howler in MANIFEST.md with `security_gate: required | optional`:
- `required`: Howlers touching auth, session handling, external API calls, user data, env vars, config
- `optional`: Howlers creating pure internal utilities, documentation, UI components with no data access

Gold drops /diff-review only for `required` Howlers. For `optional` Howlers, White covers security concerns adequately.

**Quality risk:** Low-medium. White reviews security as part of diff review but is not specifically security-oriented. For genuinely internal utilities, the risk is acceptable. The project should use its own judgment about what counts as "internal."

---

### Rank 5: HOOK.md Verbosity Discipline
**Savings per run:**
- 5-Howler: ~500 tokens × 5 Howlers = 2.5k Opus input tokens at Pax = 2.5k × $15/M = **$0.038**
- 8-Howler: **~$0.060**

**Implementation:** Add to HOOK.md instructions in the drop template:
- Completion Verification: log `PASS/FAIL + count` only, not full `ls -la` output
- Remove empty sections (Blockers, Errors Encountered, Cross-Domain Observations) before writing final HOOK.md
- Keep Decisions concise (one line per decision, not a paragraph)

**Quality risk:** Minimal. The full output is not needed for Gold's Pax review; Gold needs to know what passed/failed, not every listed file.

---

## Optimizations That Would Degrade Quality (Flagged, Not Recommended)

### A: Downgrade Gold Muster from Opus to Sonnet

**Potential savings:** Muster costs ~$1.73; Sonnet version would cost ~$0.35. **Savings: ~$1.38 per run.**

**Why not recommended:** Muster is the highest-leverage decision point in the entire protocol. Errors here cascade: a wrong CONTRACT.md triggers AMENDMENT.md filings, circuit breaker trips, recovery invocations, and potentially a full re-muster. The CLAUDE.md rationale explicitly states "Sonnet cuts corners on integration." LESSONS.md entries from multiple prior convoys confirm that contract/decomposition errors are the most expensive failure mode. The savings don't justify the risk.

### B: Downgrade Gold Pax from Opus to Sonnet

**Potential savings:** Pax costs ~$1.33 (5-Howler); Sonnet version: ~$0.28. **Savings: ~$1.05 per run.**

**Why not recommended:** Pax's independent validation step is the only check that catches "green but wrong" — a Howler that passes all quality gates but doesn't satisfy the contract postconditions. This requires reading source files and comparing them against CONTRACT.md with adversarial skepticism. Sonnet risks passing plausible-but-wrong Howler output, allowing integration failures to reach the merged codebase.

### C: Eliminate Politico

**Potential savings:** $0.06 per full run.

**Why not recommended:** The cost is negligible. Politico's value is preventing structural failures that cost ~$1-3 each in re-muster + recovery. A single structural failure detected pre-dispatch recoups 15-50 Politico invocations. Even a 5% catch rate is break-even.

### D: Skip White for Pure-Create Howlers

**Potential savings:** ~$0.09 per pure-create Howler.

**Why not recommended:** "Pure-create" does not mean "no bugs." White catches contract compliance issues that Gray (test-focused) misses. A Howler can create all its files, pass all tests, but export a function with the wrong signature — White catches this, Gray doesn't if there are no cross-Howler tests yet.

### E: Eliminate per-Howler Gray, Replace with Single Post-Merge Gray

**Potential savings:** (N-1) × $0.11 per run.

**Why not recommended:** Per-Howler Gray catches test failures before the PR opens, while it's cheap to fix. A post-merge failure requires additional commits, re-review, and potentially a hotfix PR. The per-Howler gate catches failures at the cheapest possible moment.

---

## Summary Table

| Optimization | 3-Howler Reaping | 5-Howler Full | 8-Howler Full | Quality Risk |
|-------------|-----------------|--------------|--------------|-------------|
| 1. Self-reflect: Gold → Sonnet | $0.08 | $0.14 | $0.22 | Low |
| 2. Per-Howler CONTRACT.md slicing | $0.015 | $0.026 | $0.041 | Low |
| 3. Confidence-tiered Pax validation | $0.05–0.10 | $0.135 | $0.225 | Low |
| 4. Conditional /diff-review | $0.05–0.10 | $0.10–0.15 | $0.15–0.20 | Low-medium |
| 5. HOOK.md verbosity discipline | $0.02 | $0.038 | $0.060 | Minimal |
| **Combined savings** | **~$0.17–0.30** | **~$0.44–0.49** | **~$0.75–0.75** | |

**Combined savings as % of total run cost:**
- 3-Howler Reaping: $0.24 / $3.49 = **~7%**
- 5-Howler Full: $0.47 / $7.29 = **~6%**
- 8-Howler Full: $0.75 / $10.43 = **~7%**

---

## Key Observations

1. **Gold (Opus) dominates cost.** Muster + Pax account for ~$3.06 of a 5-Howler run (~42%). These are also the two phases where Opus is most justified.

2. **Howlers are surprisingly cheap.** At ~$0.41 per Howler including all execution context, the parallel worker cost scales linearly and reasonably. The overhead phases (Muster, Pax) don't scale linearly — this means the 8-Howler run is relatively more cost-efficient per feature than the 3-Howler run when measured as $/Howler.

3. **The triple quality gate is cost-efficient.** White + Gray + /diff-review at ~$0.25 per Howler is a modest insurance policy against expensive re-work. The asymmetry strongly favors keeping the gate.

4. **Reaping mode delivers good savings.** The ~3 min / ~$3.49 reaping run vs ~8 min / ~$7.29 full run reflects roughly a 50% cost reduction for the appropriate use case. The protocol's existing guidance to use reaping for pure-create 3-4 Howler runs is well-calibrated.

5. **Per-PR self-reflect is the clearest optimization.** It is the one case where an Opus invocation is used for output that clearly doesn't require Opus-level reasoning. Every other Opus invocation is defensible on quality grounds.
