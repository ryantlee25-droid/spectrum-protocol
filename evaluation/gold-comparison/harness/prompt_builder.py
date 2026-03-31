"""Prompt builder for Gold evaluation scenarios.

Constructs prompts faithful to what a real Gold agent receives,
based on the Spectrum Ops Manual patterns.
"""

from typing import Any


def build_muster_prompt(scenario: dict) -> str:
    """Build a muster-phase prompt for a Gold agent.

    The muster prompt asks Gold to decompose a task, produce a file
    ownership matrix, DAG edges, and CONTRACT.md sections — just as
    a real Gold would during Phase 1 of the Spectrum protocol.
    """
    task_description = scenario.get("task_description", "")
    plan_excerpt = scenario.get("plan_excerpt", "")
    codebase_context = scenario.get("codebase_context", [])
    num_howlers = scenario.get("num_howlers", "unknown")

    # Build codebase context section
    context_lines: list[str] = []
    for entry in codebase_context:
        if isinstance(entry, dict):
            path = entry.get("path", "unknown")
            content = entry.get("content", "").rstrip()
            context_lines.append(f"### {path}\n```\n{content}\n```")

    context_section = (
        "\n\n".join(context_lines) if context_lines else "(no codebase context provided)"
    )

    prompt = f"""You are Gold (♛), the Spectrum orchestrator. Your role is to decompose a software task into parallel Howler tracks.

## Your Task

{task_description}

## PLAN.md Excerpt

{plan_excerpt}

## Codebase Context

{context_section}

## Instructions

You must decompose this work into approximately {num_howlers} Howler tracks.

Produce the following artifacts:

### 1. File Ownership Matrix

List every file that will be CREATED or MODIFIED, with exactly one owner Howler per file.
Use this format (at minimum — you may add columns):

| File | Howler | Action |
|------|--------|--------|
| path/to/file.ts | howler-name | CREATES |

### 2. Dependency DAG

List the dependency edges between Howlers. Use YAML format:

```yaml
dag_edges:
  - from: howler-b
    to: howler-a
    type: types
```

(Edge means: howler-b depends on howler-a)

### 3. CONTRACT.md Sections

Write the key CONTRACT.md sections:

**Shared Types** — TypeScript interfaces and types multiple Howlers depend on.

**Per-Howler Design-by-Contract** — For each Howler, write:
- Preconditions (what must be true before it starts)
- Postconditions (what it guarantees on completion)
- Invariants (what must remain true throughout)

Focus on: identifying file ownership conflicts, decomposition hazards, and seam interfaces.
Flag any tasks that are inherently serial (label with `serial_risk: yes`).
Flag any Howler whose effort is significantly larger than peers (label with `effort: L`).
"""
    return prompt.strip()


def build_pax_prompt(scenario: dict) -> str:
    """Build a pax-phase prompt for a Gold agent.

    The pax prompt gives Gold the debriefs + contract and asks it
    to independently validate each Howler's output against the contract.
    """
    contract_md = scenario.get("contract_md", "")
    debrief_set = scenario.get("debrief_set", [])

    # Build debrief sections
    debrief_sections: list[str] = []
    for debrief in debrief_set:
        howler_name = debrief.get("howler", "unknown")
        status = debrief.get("status", "unknown")
        confidence = debrief.get("confidence", "unknown")
        hook_content = debrief.get("hook_md", "").rstrip()
        debrief_content = debrief.get("debrief", "").rstrip()
        files_created = debrief.get("files_created", [])

        file_sections: list[str] = []
        for fc in files_created:
            fpath = fc.get("path", "unknown")
            fcontent = fc.get("content", "").rstrip()
            file_sections.append(f"#### {fpath}\n```\n{fcontent}\n```")

        files_text = "\n\n".join(file_sections) if file_sections else "(no files provided)"

        debrief_sections.append(
            f"### {howler_name} (status: {status}, confidence: {confidence})\n\n"
            f"**HOOK.md:**\n```\n{hook_content}\n```\n\n"
            f"**Debrief:**\n{debrief_content}\n\n"
            f"**Files Created:**\n{files_text}"
        )

    debriefs_text = "\n\n---\n\n".join(debrief_sections) if debrief_sections else "(no debriefs)"

    prompt = f"""You are Gold (♛), the Spectrum orchestrator. You are in Phase 5 (Pax) — independent validation.

## Frozen CONTRACT.md

{contract_md}

## Howler Debriefs

{debriefs_text}

## Instructions

Do NOT trust Howler self-reports. Independently validate each Howler's output.

For each Howler, check:
1. Do exported types match the contract postconditions?
2. Do integration points exist where claimed?
3. Were any files outside the ownership matrix touched?
4. Do seam declarations from this Howler match confirmations from the Howlers it declared seams with?

Report deviations in this structured format:

### Deviation Report

For each deviation found:
```
DEVIATION
  Howler: <howler-name>
  Type: postcondition_violation | seam_mismatch | ownership_violation | contract_breach
  Severity: blocker | warning | observation
  Description: <specific description referencing file names and function names>
```

If a Howler has NO deviations, explicitly state:
```
CLEAN: <howler-name> — no deviations found
```

Cross-reference all seam declarations. If Howler A declares a seam to Howler B, verify Howler B confirms it.
"""
    return prompt.strip()


def build_forge_prompt(scenario: dict) -> str:
    """Build a forge-phase prompt for a Gold agent.

    The forge prompt gives Gold a failing Howler's HOOK.md and asks it
    to classify the failure and recommend a recovery action.
    """
    hook_md_excerpt = scenario.get("hook_md_excerpt", "")
    error_context = scenario.get("error_context", "")
    failure_history = scenario.get("failure_history", [])

    # Build failure history section
    history_lines: list[str] = []
    for entry in failure_history:
        attempt = entry.get("attempt", "?")
        classification = entry.get("classification", "unknown")
        locus = entry.get("locus", "unknown")
        history_lines.append(
            f"  - Attempt {attempt}: classified as '{classification}', locus: {locus}"
        )

    history_text = (
        "\n".join(history_lines)
        if history_lines
        else "  (no prior failures on this locus)"
    )

    prompt = f"""You are Gold (♛), the Spectrum orchestrator. A Howler has failed. You must classify the failure and recommend recovery.

## Failure HOOK.md

{hook_md_excerpt}

## Error Context

{error_context}

## Prior Failure History on This Locus

{history_text}

## Instructions

Classify this failure and recommend a recovery action.

**Failure Classifications:**
- `transient` — Flaky test, network blip, tool timeout. Retry is safe.
- `logical` — Bug in the Howler's implementation. May need Orange diagnosis.
- `structural` — Contract/boundaries wrong. Requires re-planning.
- `environmental` — Missing dependency, wrong environment. External fix needed.
- `conflict` — File ownership collision with another Howler.

**Recovery Actions:**
- `resume` — Drop new Howler with HOOK.md context to continue from checkpoint
- `retry` — Drop fresh Howler with original task (fresh approach)
- `skip` — Task no longer needed or can be follow-up
- `restructure` — Re-plan with different decomposition

**Circuit Breaker Rule:** If there have been 2 or more prior failures on the SAME locus, the failure type MUST escalate to `structural` and recovery MUST be `restructure`, regardless of the individual failure classification.

Respond in this exact format:

```
CLASSIFICATION: <one of: transient, logical, structural, environmental, conflict>
RECOVERY_ACTION: <one of: resume, retry, skip, restructure>
CIRCUIT_BREAKER_TRIGGERED: <true or false>
RATIONALE: <1-3 sentences explaining your reasoning>
```
"""
    return prompt.strip()


def build_prompt(scenario: dict, phase: str) -> str:
    """Construct the Gold prompt for a scenario.

    Args:
        scenario: Loaded and validated scenario dict.
        phase: The gold phase to build a prompt for ('muster', 'pax', 'forge').

    Returns:
        The constructed prompt string.

    Raises:
        ValueError: If phase is not recognized.
    """
    builders = {
        "muster": build_muster_prompt,
        "pax": build_pax_prompt,
        "forge": build_forge_prompt,
    }

    if phase not in builders:
        raise ValueError(
            f"Unknown phase '{phase}'. Must be one of: {sorted(builders.keys())}"
        )

    return builders[phase](scenario)
