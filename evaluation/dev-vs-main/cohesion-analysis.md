# Agent Cohesion Analysis: Main vs Dev

**Analyst**: Spectrum Howler (cohesion analysis)
**Date**: 2026-03-31
**Sources**:
- Main agents: `git show main:agents/{gold,howler,white,gray,blue,copper,orange,obsidian,brown,violet,politico}.md`
- Dev agents: `/Users/ryan/spectrum-protocol/agents/{golds,howlers,whites,grays,blues,coppers,oranges,obsidians,browns,violets,politicos}.md`
- Dev protocol: `/Users/ryan/spectrum-protocol/spectrum/SPECTRUM-OPS.md` — Gold Post-Howler Protocol (lines 452–501)
- Protocol audit: `/Users/ryan/spectrum-protocol/evaluation/code-review/protocol-audit.md`

---

## 1. Agent Visibility

### Main: Selective Visibility

In main, only Gold, Blue, and the Howlers are mentioned as active participants during a spectrum run. White, Gray, Orange, Copper, Obsidian, and Brown are referenced in documentation but their lifecycle during a run is opaque — they are invoked somewhere inside the pipeline, but when and where is not surfaced to the user in real time. The main Gold agent has no instruction to print a status roster. Agent spawning happens invisibly; the user sees only Gold's prose narration.

The practical consequence: a user watching a spectrum run in main sees Gold talking about steps while unknown agents run silently. When something fails, it is unclear which agent produced the failure. The user must read Gold's prose to reconstruct the pipeline state rather than having it rendered directly.

### Dev: Full Roster Visibility

Dev introduces a mandatory Status Roster that Gold must print after every dispatch, completion, and phase transition. Every agent in the pipeline appears — not just Howlers, but Whites, Grays, Coppers, Obsidians, and Browns — each with a glyph, role label, and status symbol:

```
  » howler-auth  Worker     ✓ done
    ✦ Whites     Reviewer   ● running
    ⛨ Grays      Tester     ✓ pass
    ▶ Coppers    Delivery   ○ queued
```

The Gold Post-Howler Protocol (SPECTRUM-OPS.md lines 452–501) makes this concrete: when a Howler completes, Gold spawns White, Gray, and /diff-review as `run_in_background=True` visible agents with glyph descriptions (`"✦ Whites — reviewing {howler-name}"`). The roster updates after each gate agent returns.

Quality gates that were previously implicit steps in a prose pipeline become named, trackable agents the user can see completing in real time.

### Assessment: Significant UX Improvement

The dev visibility model resolves a core orientation problem. In a 4-Howler spectrum with staggered gate agents, a user could be watching 8–12 agents run concurrently. Without the roster, the user has no way to know what is happening without reading prose or checking individual HOOK.md files. The roster provides a real-time system map. The glyph identifiers (✦ for White, ⛨ for Gray, ▶ for Copper) create fast visual scanning that prose summaries cannot match.

One gap remains: the Status Roster is defined in SPECTRUM-OPS.md and the spectrum CLAUDE.md, but the individual agent `.md` files themselves do not change their descriptions to reflect this visibility model. The roster behavior lives entirely in Gold's instructions, so if Gold is not following the OPS manual closely, the roster disappears silently.

---

## 2. Agent Interaction Model

### Main: Flat Howler Model

In main, the interaction model is:

```
Gold → Howler (implement + self-review + open PR)
```

The main `howler.md` core protocol ends at step 6: "Write to your debrief." There is no step 7. The implication — confirmed by the absence of any post-Howler Gold coordination section — is that Howlers are expected to run quality gates inside their own session. The main White agent's session context section shows it reading from a `session.json` file managed by Gold's pipeline, but within the spectrum context the handoff is not defined.

The Copper (`git-agent`) agent in main does invoke code-reviewer and test-runner before opening an MR (lines 109–110 of `copper.md`), but this is Copper's own embedded gate-running logic, not a coordinated spawn from Gold. This means:

1. Quality gates run inside Copper's session, not as independent agents.
2. Gold has no visibility into gate results until Copper reports them.
3. If a gate fails, Orange must be invoked manually — there is no automatic routing path.
4. Gray in main runs on Haiku (model: haiku), which the protocol audit later identifies as a downgrade risk ("Haiku misdiagnoses flaky tests and writes superficial coverage").

### Dev: Separation of Concerns with Gold Coordination

In dev, the interaction model is:

```
Gold → Howler (implement only)
Howler → debrief + return to Gold
Gold → [White + Gray + /diff-review] in parallel (visible background agents)
Gold → Orange if any gate fails
Gold → Copper when all gates pass
```

This is explicitly documented in SPECTRUM-OPS.md's Gold Post-Howler Protocol (lines 452–501). Howler explicitly does NOT run quality gates: the dev CLAUDE.md states "Howlers implement and return — they do not run quality gates themselves." Gray is upgraded from Haiku to Sonnet in dev, correcting the model assignment weakness from main.

The model also introduces staggered gate triggering: gates fire immediately when each Howler completes, not after all Howlers finish. On a 4-Howler run with staggered completion, this saves 8–15 minutes (cited in OPS line 447–448).

### Assessment: Meaningful Quality Improvement

The separation is architecturally correct. Having Howlers self-review is a conflict of interest — the agent that wrote the code also decides whether it passes. Independent reviewers catch issues the author normalizes. The protocol audit's real-world validation (White caught 10 blockers in the remnant-narrative-0329 run) confirms this matters in practice.

The dev model also makes Orange's role explicit: it is the recovery path when gate agents report failures, not a manually invoked tool. This closes the implicit gap in main where failure routing depended on the user noticing a problem and manually directing agents.

One cohesion risk: Gold coordinates all gate agents, but Gold's own instructions (the CLAUDE.md muster steps) have 31 discrete checklist items. Adding per-Howler gate coordination on top of muster creates significant cognitive load on Gold. The dev model implicitly assumes Gold maintains accurate state across N simultaneous Howler lifecycles. CHECKPOINT.json partially addresses this, but the gate coordination is still driven by Gold's working memory, not a durable state machine.

---

## 3. Agent Identity

### Main: Singular Names, Color Mismatches

Main uses singular lowercase names throughout: `gold`, `white`, `gray`, `blue`, `copper`, `orange`, `obsidian`, `brown`, `violet`, `politico`, `howler`. Colors in the frontmatter do not consistently match the names:

| Agent | Name | Color (main) |
|-------|------|--------------|
| white | white | purple |
| copper | copper | gray |
| gray | gray | cyan |
| gold | gold | yellow |
| orange | orange | red |

White is purple. Copper is gray. Gray is cyan. Only Gold (yellow) and Orange (red) have plausible color-name relationships. The mismatches are not inherently harmful — these are system-level identifiers — but they create cognitive friction when the documentation describes "White reviewing" and the UI shows a purple agent.

### Dev: Plural Caste Names, Corrected Colors

Dev uses plural forms throughout: `golds`, `whites`, `grays`, `blues`, `coppers`, `oranges`, `obsidians`, `browns`, `violets`, `politicos`, `howlers`. Colors are updated:

| Agent | Name | Color (dev) |
|-------|------|-------------|
| whites | whites | purple (unchanged) |
| coppers | coppers | cyan |
| grays | grays | gray |
| golds | golds | yellow |
| oranges | oranges | red |

Gray is now gray. Copper is now cyan (promoted from gray). White stays purple — this remains semantically inconsistent but is the one holdover mismatch.

The plural forms serve a functional purpose beyond aesthetics: they are the `subagent_type` identifiers used when spawning agents. The protocol audit (section 5.3) notes that SPECTRUM.md prose mixes singular/plural incorrectly ("a Politicos agent"), but the agent files themselves are consistent.

The Red Rising naming convention — treating agents as castes rather than individuals — aligns with the multi-instance model. "A Whites" spawns multiple White reviewers across concurrent Howler completions. The singular "White" implied one reviewer. This semantic precision matters when 3 Whites are running simultaneously on 3 different Howlers.

### Assessment: Moderate Improvement with One Remaining Inconsistency

The naming alignment reduces friction. The caste framing correctly models how agents are used in practice — as spawnable role types, not named individuals. White remaining purple is the one remaining mismatch worth noting for a future cleanup pass.

---

## 4. Agent Handoff Quality

### Main: Howler-to-PR Direct (No Gold Checkpoint)

In main, after a Howler writes its debrief, the path to a PR is:

1. Howler writes debrief
2. Copper (invoked somehow) runs code-reviewer and test-runner inline
3. Copper opens the MR

Gold's role between Howler completion and PR is not defined. The main Gold agent has no "Post-Howler Protocol" section. If a Howler's debrief reveals an integration problem, there is no documented path for Gold to catch it before Copper opens the PR.

Information that travels across this gap:
- Debrief content: available in the spectrum directory but no agent is specified to read it before PR
- HOOK.md: available but only the Howler wrote it; no downstream agent reads it before PR
- Seam declarations: written to debrief but not cross-referenced before merge

The Copper agent does gate on code-reviewer and test-runner, but it does not read HOOK.md or the debrief. Debrief content — the richest source of Howler self-knowledge — is only consumed during Pax, which runs after all PRs are opened. This means integration risks documented in debriefs are surfaced after PRs exist, not before.

### Dev: Gold Checkpoint Between Howler and Gates

In dev, the handoff is explicit:

1. Howler writes debrief, signals completion
2. Gold reads HOOK.md (confirming the Howler's self-assessment)
3. Gold spawns White + Gray + /diff-review in parallel
4. Gold processes gate results, routes failures to Orange if needed
5. Gold spawns Copper only after all three gates pass

HOOK.md is the key artifact. The dev Gold Post-Howler Protocol explicitly says Gold reads HOOK.md for confidence areas before spawning White. White receives this context in its prompt: "Read HOOK.md for confidence areas." This means the reviewer is directed to the areas the Howler flagged as uncertain — a significant efficiency improvement over a cold diff review.

The debrief-to-Pax path is unchanged between main and dev, but the pre-PR gate now sits between implementation and PR rather than being embedded inside Copper. Information that previously bypassed Gold (debrief seam declarations) now passes through the Gold checkpoint before the PR is opened.

One gap remains: Gold's independent validation (verifying CONTRACT.md postconditions by reading 2-3 key files) is a Pax step, not a post-Howler step. The post-Howler checkpoint reads HOOK.md but does not mechanically verify the Howler's claimed postconditions. This means a Howler that misreports its completion state could pass through White + Gray and still produce a flawed PR if the implementation subtly diverges from the contract without causing test failures.

### Assessment: Handoff Substantially Improved, One Verification Gap Remains

The dev model closes the most serious gap: Gold now stands between Howler completion and PR creation. HOOK.md context flows into gate agents. Failures route through Orange before escalating.

The remaining gap is contract postcondition verification, which is deferred to Pax. For high-stakes seams, a lightweight postcondition check at the post-Howler stage (before opening PR) would catch the class of errors where implementation is internally consistent but diverges from the contract without test failures. This is documented in the protocol audit as a medium-priority finding but not yet acted on in the dev agent files.

---

## 5. Cohesion Score

### Scoring Dimensions

**Responsibilities are clear and non-overlapping:**
Measured by whether each agent has a defined, exclusive role with no overlap ambiguity.

**Communication flow is documented and followable:**
Measured by whether a new user can trace information from task input to PR output without reading source code.

**New user can understand who does what:**
Measured by whether the agent descriptions and CLAUDE.md routing table are sufficient for onboarding.

**System degrades gracefully when agents fail:**
Measured by whether failure paths are documented and do not require human judgment to navigate.

---

### Main: 5.5 / 10

| Dimension | Score | Notes |
|-----------|-------|-------|
| Clear, non-overlapping responsibilities | 6/10 | Gold, Blue, Howler roles are clear. White/Gray/Orange/Copper overlap ambiguously — Copper embeds gate-running logic that belongs to Gray and White. |
| Communication flow documented | 4/10 | Gold's pipeline routing is documented in prose but the spectrum path is unclear. No post-Howler Gold checkpoint documented. Howler-to-PR information flow has a gap. |
| New user comprehension | 6/10 | Gold's agent teams table and pipeline routing are followable. But invisible gate agents mean a new user would not know White and Gray exist during a spectrum run. |
| Graceful failure degradation | 6/10 | Pipeline A-E failure routing is clear. Orange is documented. Spectrum failure paths rely on Gold's judgment with no structured escalation checklist. |

**Overall: 5.5 / 10**

Main is a functioning system with a coherent single-agent pipeline (Pipelines A–E via Gold). Its spectrum extension is underspecified — the post-Howler lifecycle is not documented, quality gates are embedded in Copper rather than coordinated by Gold, and the full agent roster is invisible to users during runs. For simple pipelines, main works well. For parallel spectrum runs with multiple Howlers, the system lacks the coordination layer to remain coherent.

---

### Dev: 7.5 / 10

| Dimension | Score | Notes |
|-----------|-------|-------|
| Clear, non-overlapping responsibilities | 8/10 | Each agent has a single declared role. Quality gates are no longer embedded in Copper. Gray model upgraded to Sonnet, eliminating the main-branch model mismatch. One remaining overlap: the Howler's contract test run (completion verification) and Gray's full test run (quality gate) both test postconditions — their distinct scopes are not fully defined. |
| Communication flow documented | 8/10 | Gold Post-Howler Protocol gives an explicit spawn sequence. Status Roster creates real-time visibility. HOOK.md flows into gate agents. Information path from Howler debrief to Pax is documented. Gap: debrief seam cross-referencing still deferred to Pax. |
| New user comprehension | 7/10 | The Status Roster makes the full agent lifecycle visible. CLAUDE.md routing table is clear. Agent names (plural castes) are explained in the roster section. Gap: the plural naming convention is not explained in the individual agent `.md` files — a user encountering `golds.md` without CLAUDE.md context might not know why it's plural. |
| Graceful failure degradation | 7/10 | The Forge (Phase 3) failure classification matrix is well-documented: transient/logical/structural/environmental/conflict with escalation paths. Circuit breaker (2 failures = structural escalation) prevents infinite retry loops. Gap: the handoff from Orange diagnosis back to Gold decision is clear in prose but CHECKPOINT.json does not have a field tracking Orange retry count per Howler, so a session restart would lose retry history. |

**Overall: 7.5 / 10**

Dev substantially closes the coordination gaps in main. The Gold Post-Howler Protocol, Status Roster, and model corrections together make the spectrum system observable and recoverable in ways main was not. The remaining 2.5-point gap reflects three specific areas: the contract test vs. postcondition verification overlap (medium priority per audit), the CHECKPOINT.json retry count gap (medium), and the Gold cognitive load risk from coordinating 31-step muster + N concurrent Howler lifecycles simultaneously (low-medium — mitigated by CHECKPOINT.json but not eliminated).

---

## 6. Summary of Findings

### What Dev Gets Right

1. **Quality gate independence**: Moving White + Gray from inside Copper to Gold-coordinated visible agents eliminates the conflict of interest in main's self-reviewing pipeline.

2. **Real-time observability**: The Status Roster with glyphs gives users a live system map. During a 4-Howler run, this is the difference between watching a black box and watching a process.

3. **HOOK.md as context relay**: Gate agents (White) receive HOOK.md context from Howlers, directing review effort toward uncertain areas rather than running blind.

4. **Staggered gate triggering**: Gates fire per-Howler at completion rather than after all Howlers finish — a concrete time saving documented in OPS.

5. **Model corrections**: Gray upgraded from Haiku to Sonnet. Blue upgraded from Haiku to Sonnet. These correct real capability mismatches identified through production observation.

6. **Caste framing**: Plural names accurately model multi-instance spawning. Functional, not just aesthetic.

### What Remains Unresolved

1. **Gold cognitive load**: 31 muster steps + N concurrent Howler lifecycles + roster maintenance. CHECKPOINT.json mitigates session death but not working memory saturation during a live run.

2. **Contract test vs. postcondition verification**: Both verify CONTRACT.md postconditions. Their distinct scopes are undocumented. Running both is redundant unless differentiated.

3. **Orange retry count not persisted**: CHECKPOINT.json tracks Howler status but not per-Howler Orange attempt count. After session restart, circuit breaker history is lost.

4. **White stays purple**: The one color/name mismatch surviving from main. Minor friction but worth resolving in a future cleanup.

5. **Protocol cross-file drift**: The protocol audit found 6 critical/high inconsistencies between CLAUDE.md, SPECTRUM-OPS.md, and SPECTRUM.md. Agent cohesion is only as strong as the instructions agents receive — three files with divergent phase numbers and CHECKPOINT.json schemas create judgment ambiguity for Gold at phase transitions.

### Cohesion Score Comparison

| System | Score | Primary Bottleneck |
|--------|-------|--------------------|
| Main   | 5.5 / 10 | Post-Howler lifecycle undocumented; gate agents invisible; Gray on Haiku |
| Dev    | 7.5 / 10 | Gold cognitive load; cross-file protocol drift; contract test overlap |

The 2-point delta is real and earned. Dev is a meaningfully more cohesive system. The remaining gap is primarily documentation-layer drift (solvable by the protocol-audit fixes) rather than structural design problems.
