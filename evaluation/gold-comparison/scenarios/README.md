# Scenario Library — Authoring Guide

This directory contains 18 benchmark scenarios for evaluating Gold agent (Opus vs Sonnet)
performance across the three phases Gold is responsible for in the Spectrum protocol.

---

## Directory Structure

```
scenarios/
  muster/         scenario-01 through scenario-05  — Gold Phase 1 (Muster)
  pax/            scenario-01 through scenario-05  — Gold Phase 5 (Pax)
  forge/          scenario-01 through scenario-05  — Gold Phase 4 (Forge)
  edge-cases/     scenario-01 through scenario-03  — Phase-routed edge cases
  README.md       this file
```

---

## Required Fields (all scenario types)

Every scenario MUST include these top-level fields:

```yaml
scenario_id: "muster-01"     # Unique. Format: {phase}-{NN} or "edge-{NN}"
gold_phase: "muster"         # One of: muster, pax, forge
difficulty: "medium"         # One of: easy, medium, hard (see rating guide below)
description: "..."           # One-line summary of what discriminating behavior this tests
```

---

## Muster Scenario Schema

Muster scenarios test Gold's decomposition quality: file ownership, DAG construction,
conflict detection, and CONTRACT.md authoring.

```yaml
scenario_id: "muster-NN"
gold_phase: "muster"
difficulty: "easy|medium|hard"
description: "..."

task_description: |
  # Plain-language description of what the user asked Gold to do.
  # Should read like a real user request.

plan_excerpt: |
  # Simulated PLAN.md content. Should be realistic: include section headers,
  # file lists, and constraints. Not exhaustive — just enough context for muster.

codebase_context:          # Simulated existing files in the project
  - path: "src/foo.ts"
    content: |
      // File content (abbreviated is fine)

num_howlers: 4             # Expected Howler count in the correct decomposition

# Ground truth fields (used by scoring engine)
expected_file_ownership:
  - file: "src/auth/middleware.ts"
    howler: "howler-auth"
    action: "CREATES"        # or MODIFIES
    rationale: "..."         # optional — explains why this Howler owns this file

known_conflicts:           # Files a naive decomposition would double-assign
  - file: "src/types/shared.ts"
    naive_howlers: ["howler-auth", "howler-api"]
    correct_resolution: "Assign to howler-auth; howler-api imports from it"

expected_dag_edges:
  - from: "howler-api"     # "from" Howler DEPENDS ON "to" Howler
    to: "howler-auth"
    type: "types"          # One of: types, implementation
    note: "..."            # optional explanation

expected_contract_sections:
  - section: "shared_types"
    must_include: ["UserSession", "ApiResponse"]
  - section: "postconditions"
    howler: "howler-auth"           # optional: section scoped to one Howler
    must_include: ["exports authMiddleware"]

scoring_notes: |
  # Explanation of what this scenario specifically tests and what
  # wrong answers look like. Used by human reviewers.
```

### Muster Difficulty Guide

| Rating | Characteristics |
|--------|----------------|
| easy   | 3-4 Howlers, reaping mode or minimal deps, zero known conflicts, all tasks obviously scoped |
| medium | 4-5 Howlers, at least one non-obvious DAG edge, one injected conflict that a careful reader catches |
| hard   | 6-8 Howlers, multiple conflict types, multi-phase DAG (types dep + implementation dep), synthesizer Howler, or codegen/generated file patterns |

---

## Pax Scenario Schema

Pax scenarios test Gold's independent validation quality: detecting deviations from
CONTRACT.md postconditions and invariants, cross-referencing seam declarations, and
avoiding false positives on correct Howlers.

```yaml
scenario_id: "pax-NN"
gold_phase: "pax"
difficulty: "easy|medium|hard"
description: "..."

contract_md: |
  # The frozen CONTRACT.md for this spectrum run.
  # Include shared types, postconditions per Howler, and key invariants.

debrief_set:
  - howler: "howler-name"
    status: "complete"       # or "blocked"
    confidence: "high"       # or "medium" or "low"
    hook_md: |
      # Full HOOK.md content (status, files created, seams declared,
      # completion verification, cross-domain observations)
    debrief: |
      # Howler's own narrative summary
    files_created:
      - path: "src/foo.ts"
        content: |
          # Actual file content — this is what Gold must verify
          # against CONTRACT.md postconditions

# Ground truth fields
injected_deviations:
  - howler: "howler-name"
    deviation_type: "postcondition_violation"  # see deviation types below
    description: "What is wrong and why it matters"
    severity: "blocker"      # or "warning" or "observation"
    location: "file:line hint"
    detection_method: "How Gold should find this (file inspection, seam mismatch, etc.)"

correct_howlers:             # Howlers with NO deviations — for false positive scoring
  - "howler-auth"

false_positive_traps:        # optional — common wrong flags that are actually correct
  - howler: "howler-name"
    trap_description: "What a weak Gold might flag incorrectly, and why it's valid"

scoring_notes: |
  # What makes this scenario hard, what correct detection looks like,
  # what incorrect detection looks like.
```

### Deviation Types

| Type | Description |
|------|-------------|
| `postcondition_violation` | Exported name, type signature, or return value doesn't match CONTRACT |
| `invariant_violation` | A CONTRACT invariant is broken (e.g., cents vs dollars, per-request ID) |
| `seam_mismatch` | Howler A's declared seam doesn't match Howler B's implementation |
| `assumption_invalidation_cascade` | A discovery by one Howler invalidates a CONTRACT assumption that other Howlers built against |
| `silent_contract_amendment` | Howler diverged from contract without filing AMENDMENT.md |

### Pax Difficulty Guide

| Rating | Characteristics |
|--------|----------------|
| easy   | Deviation is directly visible in the exported function name or obvious type mismatch; debrief confidence is low or medium |
| medium | Deviation requires reading a specific function body; high-confidence debrief; OR cross-domain hint available in another Howler's HOOK.md |
| hard   | Deviation is in a non-first-read code path (e.g., one function of many is wrong); all debriefers report high confidence; no cross-domain hints; OR assumption invalidation cascade across multiple Howlers |

---

## Forge Scenario Schema

Forge scenarios test Gold's failure classification and recovery decision quality.

```yaml
scenario_id: "forge-NN"
gold_phase: "forge"
difficulty: "easy|medium|hard"
description: "..."

hook_md_excerpt: |
  # The HOOK.md showing the failure state. Include:
  # - Status: failed or Status: blocked
  # - Errors Encountered
  # - Work Completed checklist
  # - Work NOT Started

error_context: |
  # Additional context: error codes, environment info, related files,
  # what other Howlers did (succeeded or failed), etc.

failure_history:             # Prior failures on this locus (for circuit breaker testing)
  - attempt: 1
    classification: "transient"    # what Gold classified it as (or null if first attempt)
    locus: "src/db/connection.ts"
    error: "connection timeout"
    gold_action: "auto-resume"     # optional

# Ground truth fields
correct_classification: "logical"
  # One of: transient, logical, structural, environmental, conflict

correct_recovery_action: "resume"
  # One of: resume, retry, skip, restructure

circuit_breaker_applies: false
  # true if failure_history has 2+ prior failures on the same locus

rationale: |
  # Why this is the correct classification and recovery.
  # Must explain: which signals point to this type, why other types are wrong,
  # what the ambiguous boundary cases are.

scoring_notes: |
  # What makes this scenario discriminating. What a weak classifier misses.
```

### The Five Failure Types

| Type | Definition | Recovery |
|------|-----------|----------|
| `transient` | Momentary infrastructure blip (network timeout, flaky CI, rate limit). Deterministic rerun would likely succeed. | resume (auto) |
| `logical` | The Howler's code is wrong but fixable without changing the contract or task scope. TypeScript errors, test failures from wrong logic, API calls with wrong params. | resume (with Orange) or retry |
| `structural` | The decomposition is wrong: contract mismatch, file ownership conflict, task scope is impossible as written. Cannot be fixed by rerunning. | restructure |
| `environmental` | Infrastructure is broken in a way that blocks all Howlers or requires admin action: disk full, missing tool, wrong language version, broken CI image. | skip until fixed |
| `conflict` | Git merge conflict from concurrent branch edits to the same file. | resume with conflict resolution (or restructure if root cause is ownership) |

### Forge Difficulty Guide

| Rating | Characteristics |
|--------|----------------|
| easy   | Clear single-type signals; no ambiguity with adjacent types; no circuit breaker |
| medium | Plausible alternative classification; first-attempt failure; requires reading error details carefully |
| hard   | Ambiguous type boundary (e.g., conflict vs structural, logical vs structural); OR circuit breaker scenario; OR correct block (Howler correctly stopped) vs actual failure |

---

## Edge Case Schema

Edge cases use standard phase schemas (muster, pax, or forge) but test boundary conditions
that don't fit neatly into difficulty ratings. Set `gold_phase` to the appropriate phase
so the harness routes the scenario to the correct rubric.

```yaml
scenario_id: "edge-NN"
gold_phase: "muster|pax|forge"   # routes to the appropriate phase rubric
difficulty: "hard"                # edge cases are typically hard
description: "..."

# Use the appropriate phase schema (muster, pax, or forge) for remaining fields.
# Document the edge condition being tested in scoring_notes.
```

### Current Edge Cases

| ID | Phase | Edge Condition Tested |
|----|-------|-----------------------|
| edge-01 | pax | Context window pressure — critical deviation in last of 8 Howlers |
| edge-02 | muster | Ambiguous task boundary — join entity with two equally valid owners |
| edge-03 | forge | Contract amendment — Howler correctly blocked; tests Gold's amendment handling |

---

## Difficulty Distribution Requirements

Per CONTRACT.md conventions, each phase's 5 scenarios must include:

- At least 2 easy scenarios (muster-01 is easy, pax-01 is easy, forge-01 is easy)
- At least 2 hard scenarios (muster-04 and muster-05 are hard; pax-04 and pax-05 are hard; forge-03 and forge-04 are hard)
- Edge cases are all hard by convention

Current distribution:

| Phase | Easy | Medium | Hard |
|-------|------|--------|------|
| Muster | 2 (01, 02) | 1 (03) | 2 (04, 05) |
| Pax | 1 (01) | 2 (02, 03) | 2 (04, 05) |
| Forge | 1 (01) | 1 (02) | 3 (03, 04, 05) |
| Edge | — | — | 3 (all) |

---

## Adding New Scenarios

1. Choose the target phase and pick the next available number (e.g., `muster-06.yaml`)
2. Copy the appropriate schema template from this README
3. Set `scenario_id`, `gold_phase`, and `difficulty` first
4. For muster: ensure `known_conflicts` has at least one entry if `difficulty: medium` or `hard`
5. For pax: ensure at least one `injected_deviations` entry with `severity: blocker`
6. For forge: pick a failure type from the 5-type taxonomy and document the ambiguous boundary
7. Run `python -c "import yaml; yaml.safe_load(open('scenarios/muster/scenario-06.yaml'))"` to verify YAML validity
8. Add the scenario to the difficulty distribution table above

### Calibration Checklist

Before committing a new scenario, verify:

- [ ] The scenario is parseable by PyYAML without error
- [ ] `scenario_id` matches the filename (e.g., `muster-06` in `muster/scenario-06.yaml`)
- [ ] Ground truth fields are present and unambiguous (no "it depends" answers)
- [ ] `scoring_notes` explains what a correct vs incorrect Gold response looks like
- [ ] The scenario is not trivially easy (both models would score 100%) or impossibly hard (both models score 0%)
- [ ] For pax: `correct_howlers` list is accurate (all Howlers without deviations are listed)
- [ ] For forge: `circuit_breaker_applies` is set correctly (true only if failure_history has 2+ entries on the same locus)

---

## Schema Validation

The harness validates scenarios at load time using `harness/scenario_loader.py`.
Required top-level fields: `scenario_id`, `gold_phase`, `difficulty`, `description`.
Phase-specific required fields are validated per `gold_phase` value.
See `harness/scenario_loader.py` for the full validation logic.
