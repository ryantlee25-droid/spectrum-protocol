# RUBRIC.md — Scoring Rubric for Competitive Audit
**Spectrum**: audit-2026-0331
**Howler**: H1-rubric
**Date**: 2026-03-31
**Version**: 1.0

---

## Purpose and Scope

This rubric defines the 1–5 scoring anchors for all eight evaluation dimensions used in the 2026 competitive audit of multi-agent coding systems. All scoring Howlers (H2, H3, H4) must apply this rubric without modification or supplementation.

**Target reliability**: three independent scorers applying this rubric to the same system should assign scores within ±1 of each other. Anchors use concrete, observable criteria rather than qualitative labels.

---

## Impartiality Requirement (Binding)

Spectrum Protocol is scored identically to all other systems. No anchor is written to favor Spectrum's architectural choices. If Spectrum scores lower than a competitor on a dimension, that result stands. Self-reported claims in Spectrum's README or SPECTRUM-OPS.md are not evidence; they are inputs subject to the same verification standard as any other system's marketing documentation.

---

## Evidence Hierarchy

When scoring any dimension, use the highest-quality evidence available:

1. **Public benchmarks** — SWE-Bench, HumanEval, published third-party evaluations. Cite paper/publication and result.
2. **Official documentation** — README, docs site, release notes, pricing pages, changelog. Cite specific URL or document name.
3. **Community reports** — GitHub issues, Reddit threads, Hacker News posts, developer blogs. Cite source specifically (e.g., "GitHub issue #1234", "HN thread 2025-11").
4. **First-principles reasoning from architecture docs** — Acceptable when higher-quality evidence is unavailable. Label explicitly as `[First-principles reasoning]`.

**Missing evidence rule**: No evidence for a dimension → score **2** (not 1, which implies known-bad; not 3, which implies known-average). Flag as `[LOW CONFIDENCE — no public evidence]`. Partial evidence → score conservatively, flag as `[MEDIUM CONFIDENCE — limited evidence]`. Strong evidence → no flag.

---

## D1 — Cost per Run

**What it measures**: Token/compute cost for a representative parallel coding task (e.g., 3–5 agent run, ~10 files modified, ~2,000–5,000 tokens of output per agent). Scores reflect cost efficiency relative to the task completed, not raw price per token.

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | Negligible cost for parallel runs | Free tier covers meaningful parallel workloads OR documented cost under $0.10/run at representative scale. Pricing page or published benchmark confirms this. |
| **4** | Low cost, clearly affordable | Documented cost $0.10–$0.50/run at representative scale, OR free open-source with typical cloud model costs. User community reports costs as non-issue. |
| **3** | Moderate cost; noticeable but acceptable | Documented or community-reported cost $0.50–$2.00/run. No reports of cost as a blocking concern but it comes up in comparisons. |
| **2** | High cost; a frequent user complaint | Documented or community-reported cost $2–$10/run OR subscription pricing that restricts parallel usage (e.g., per-agent seat fees). Cost regularly cited as a drawback in community discussion. |
| **1** | Prohibitive cost for routine parallel use | Documented cost >$10/run at representative scale, OR pricing model that makes parallel multi-agent runs economically impractical for individual developers. Evidence: pricing page, community complaints, or published teardowns. |

**Acceptable evidence types**: Pricing pages, published cost analyses, community discussions of bills received, benchmark papers that report token counts.

**Partial evidence handling**: If only model costs are known (not orchestration overhead), use model costs as a floor and note `[MEDIUM CONFIDENCE — model costs only; orchestration overhead unknown]`.

---

## D2 — Speed

**What it measures**: Wall-clock time for parallel task completion; parallelism ceiling. Representative task: the same 3–5 agent parallel coding run used for D1.

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | Industry-leading parallel speed | Documented parallel execution with wall-clock times ≤5 minutes for a 3-agent coding task, OR architectural evidence of genuine sub-task parallelism with no artificial serialization. Community consistently cites speed as a strength. |
| **4** | Fast; parallelism evident | Wall-clock times 5–15 minutes for a 3-agent task, OR documentation confirms simultaneous agent execution with 3+ agents. No significant serialization bottlenecks reported. |
| **3** | Moderate speed; some parallelism | System supports parallel execution but with constraints (e.g., limited concurrent agents, rate-limiting, or orchestration overhead that adds 30%+ to wall time). Community reports acceptable but not fast. |
| **2** | Slow; limited parallelism | Primarily sequential execution with parallelism as a bolt-on or poorly implemented feature. Community reports frustration with speed. Documented wall-clock times >30 minutes for tasks that should parallelize. |
| **1** | No meaningful parallelism | Single-agent execution only, OR parallel architecture but all subtasks serialized in practice (e.g., single-threaded orchestrator processes one agent at a time). Wall-clock time equals or exceeds sequential single-agent time. |

**Acceptable evidence types**: Official benchmarks, community timing reports, architecture documentation confirming concurrent execution, GitHub issues about speed.

**Partial evidence handling**: If the system claims parallelism but no timing data exists, score 3 with `[MEDIUM CONFIDENCE — architecture supports parallelism but no timing benchmarks available]`.

---

## D3 — Accuracy

**What it measures**: Plan quality, code quality, and test pass rates. Primary benchmark is SWE-Bench (% of real GitHub issues resolved). Secondary: community reports of code quality, plan coherence, and error rates.

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | State-of-the-art accuracy | SWE-Bench score ≥50%, OR top-3 published ranking on a recognized coding benchmark. Community reports consistently high-quality output. Minimal hallucination and specification-drift reports. |
| **4** | Strong accuracy | SWE-Bench score 30–50%, OR second-tier published benchmark ranking. Community reports high quality with occasional failures. Plan quality described as detailed and coherent by users. |
| **3** | Acceptable accuracy | SWE-Bench score 15–30%, OR community consensus that output requires moderate review/correction. Plans are coherent but miss edge cases. Failures are non-catastrophic. |
| **2** | Below-average accuracy | SWE-Bench score <15%, OR community reports frequent correction cycles. Plans are shallow or miss requirements. Code quality variable; tests pass at lower rates. |
| **1** | Poor accuracy | No published benchmark, OR SWE-Bench <5%. Community reports consistent failure to complete tasks correctly. Significant hallucination, specification drift, or code that does not compile. |

**Acceptable evidence types**: Published SWE-Bench or HumanEval results with citation; third-party evaluation papers; community analysis threads with concrete examples; GitHub issues documenting systematic failures.

**Partial evidence handling**: For systems without any benchmark data, use community reports as the evidence base with `[MEDIUM CONFIDENCE — no benchmark data; community reports only]`. Score conservatively — community satisfaction ≠ benchmark performance.

---

## D4 — Workflow Rigor

**What it measures**: The degree to which the system enforces disciplined multi-agent coordination — contracts, file ownership, failure taxonomy, adversarial review, and prevention of silent divergence.

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | Comprehensive rigor with enforcement | System provides ALL of: (a) pre-execution interface contracts or ownership declarations, (b) explicit failure taxonomy with distinct handling paths, (c) automated circuit breakers or escalation, (d) independent review step (adversarial or reviewer-author separation). These are enforced by the framework, not merely recommended. |
| **4** | Strong rigor; most components present | System provides at least 3 of the 4 components above. The missing component is documented as a known gap. Contracts or ownership mechanisms exist but may be convention-based rather than enforced. |
| **3** | Moderate rigor; some structure | System provides task decomposition with role separation OR retry-on-failure with logging. No file ownership contracts. No formal failure taxonomy. Reviewer-author separation may exist but is not enforced. |
| **2** | Minimal rigor | System supports multiple agents but coordination is informal — shared conversation or ad-hoc delegation. No documented failure modes. Recovery is "try again." Task boundaries rely entirely on prompt wording. |
| **1** | No workflow rigor | Single agent or agents sharing state without coordination mechanisms. No separation of concerns. Failure handling is uncaught exceptions or silent context loss. |

**Acceptable evidence types**: Architecture documentation describing coordination mechanisms; README sections on failure handling; academic papers measuring inter-agent conflict rates; GitHub issues documenting coordination failures.

**Partial evidence handling**: If documentation describes rigor mechanisms but implementation is unverified, score 3 maximum with `[MEDIUM CONFIDENCE — documented but unverified in practice]`.

---

## D5 — Observability

**What it measures**: The degree to which a user can inspect what agents are doing mid-execution — structured logs, dashboards, trace IDs, real-time status, and replay capability.

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | Full real-time observability with replay | ALL of: (a) structured logs with trace IDs per agent, (b) real-time dashboard or terminal UI showing agent status, (c) ability to replay or step through execution history, (d) mid-execution inspection without interrupting the run. LangSmith-class or equivalent. |
| **4** | Strong observability; most components | Provides structured logs with agent identification AND real-time status display. Replay may be limited (checkpoint restore but not step-through). Missing one of the four components listed in score 5. |
| **3** | Moderate observability | System outputs structured logs with agent labels and timestamps. No real-time dashboard. User must inspect log files post-hoc. Status during execution is limited to stdout/stderr. |
| **2** | Minimal observability | Unstructured logging only (print statements or raw LLM output concatenated). No agent-level attribution in logs. No mid-execution status. User cannot distinguish which agent produced which output without manual parsing. |
| **1** | No observability | Black-box execution. No logs accessible during or after run. User sees only final output (or error). No ability to diagnose failures from available information. |

**Acceptable evidence types**: Product documentation describing logging/dashboard features; screenshots or demos of dashboards; community reports of debugging experience; integration documentation for observability platforms (LangSmith, OpenTelemetry, etc.).

**Partial evidence handling**: Commercial systems may not document internal logging. For black-box commercial systems, score based on what is externally observable (UI indicators, email notifications) with `[MEDIUM CONFIDENCE — internal observability undocumented]`.

---

## D6 — Recovery

**What it measures**: What happens when an agent fails. Scores reflect the sophistication of failure detection, classification, and automated recovery — from "crash and lose everything" to "classify failure type, auto-recover transient failures, escalate others with context."

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | Sophisticated multi-tier recovery | ALL of: (a) formal failure taxonomy (≥3 distinct failure types with different handling paths), (b) automated recovery for at least one failure class without human intervention, (c) circuit breakers that escalate after N failures on the same locus, (d) failure state is persisted so recovery can resume rather than restart. |
| **4** | Strong recovery; most tiers present | Provides at least 3 of the 4 components above. Failure state is preserved across recovery attempts. Documentation explicitly describes failure types and handling. Missing one tier (e.g., circuit breaker present but failure taxonomy is implicit). |
| **3** | Moderate recovery | Retry-on-failure with configurable max attempts. Failure output fed back into retry context. No formal taxonomy. Circuit breaker absent or undocumented. State persists within a run but loss occurs on hard crash. |
| **2** | Basic recovery | Single retry on failure OR manual resume from checkpoint. No failure classification. User must inspect logs to understand what went wrong. State is partially persisted but recovery requires manual intervention. |
| **1** | No recovery mechanism | Hard failure terminates the run. No retry, no checkpoint, no partial-result preservation. User must restart from the beginning. |

**Acceptable evidence types**: Architecture documentation on failure handling; README sections on retry/recovery; academic papers measuring recovery success rates; community reports of what happens when an agent crashes mid-run.

**Partial evidence handling**: If a system documents retry-on-failure but does not describe failure classification, score 3 maximum.

---

## D7 — Setup Complexity

**What it measures**: The dependencies, configuration burden, and learning curve required to run a first parallel multi-agent task. Score 5 means near-zero friction; score 1 means days of environment setup.

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | Near-zero setup | Single command installation (e.g., `pip install` or app download). No API key configuration beyond the primary LLM. First parallel run achievable within 15 minutes by a developer unfamiliar with the system. Zero infrastructure dependencies (no database, no hosted service, no container). |
| **4** | Low setup | Installation requires 2–3 steps. API keys for 1–2 services required. First parallel run achievable within 1 hour. Optional infrastructure (e.g., persistence layer) but functional without it. |
| **3** | Moderate setup | Installation requires 4–6 steps or a tutorial. Environment variables or config files required. First parallel run achievable within a half-day. May require basic familiarity with the framework's abstractions before writing tasks. |
| **2** | High setup | Multiple dependencies beyond core LLM (vector store, message broker, database). Requires framework-specific knowledge to define tasks. First parallel run typically takes a full day including documentation study. Documented community frustration with setup. |
| **1** | Very high setup | Requires infrastructure provisioning (Docker, cloud services, self-hosted components). More than one day to first run. Frequent community reports of failed installations, environment conflicts, or missing documentation. |

**Acceptable evidence types**: Official quickstart documentation; community reports of time-to-first-run; GitHub issues about installation failures; dependency count from package manifests.

**Partial evidence handling**: For commercial/hosted systems where setup is hidden behind a login, score based on the signup-to-first-run experience described in documentation with `[MEDIUM CONFIDENCE — internal complexity undocumented]`.

---

## D8 — Scalability

**What it measures**: Performance degradation (or lack thereof) when scaling from 2 to 8+ parallel agents. Documented ceilings, known coordination overhead growth, and architecture-imposed limits.

| Score | Anchor | Observable Criteria |
|-------|--------|---------------------|
| **5** | Scales to 10+ agents with documented evidence | Published evidence or architecture documentation confirming effective parallel execution at 8+ agents with sub-linear coordination overhead growth. No documented ceiling below 10 agents. Community reports of large-scale runs confirming expected behavior. |
| **4** | Scales to 6–8 agents effectively | Architecture supports 6–8 agents with documented guidance. Coordination overhead is acknowledged but managed (e.g., explicit DAG limits, guidance on optimal batch size). Performance at 8 agents is acceptable relative to 2 agents. |
| **3** | Scales to 3–5 agents; degrades beyond | Documented or community-reported sweet spot of 3–5 agents. Performance degrades noticeably beyond 5–6 agents due to coordination overhead, context limits, or orchestrator bottleneck. Acknowledged but not addressed in current version. |
| **2** | Scales to 2–3 agents only | Architecture supports parallelism but practical ceiling is 2–3 agents before failures or quality degradation become frequent. Community reports or documentation acknowledge limited scale ceiling. |
| **1** | No scalability beyond single agent | Single-agent execution or parallelism architecture that degrades to effectively sequential at 2+ agents. No documented path to meaningful parallel execution. |

**Acceptable evidence types**: Official documentation on concurrency limits; architecture papers quantifying coordination overhead; community reports of runs at scale; published benchmarks at varying agent counts.

**Partial evidence handling**: For systems with no published large-scale evidence, score based on architectural reasoning: a pull-queue architecture scores higher than a single-orchestrator architecture for theoretical scalability. Label `[MEDIUM CONFIDENCE — architectural inference; no empirical evidence at scale]`.

---

## Score Format Rules

These rules apply to all scoring Howlers (H2, H3, H4):

1. **Scores are integers 1–5.** No decimals, ranges, or qualitative labels in the scoring table.
2. **Uncertainty flags belong in evidence notes, not table cells.** The table cell contains only the integer score.
3. **Every score requires at least one specific citation** in the evidence notes — a document name, URL, GitHub issue number, or community source. "General knowledge" is not a citation.
4. **Score 2 for unknown dimensions.** Do not assign score 3 ("average") as a default for unknown systems — 2 reflects genuine uncertainty more honestly.
5. **Score Spectrum identically.** No anchor interpretation may favor Spectrum's documented approach. The same evidence standards apply.
6. **Conservative interpretation for ambiguous evidence.** When an anchor boundary is unclear, assign the lower score.

---

## Quick Reference — Score Summaries

| Dimension | Score 1 (Worst) | Score 3 (Middle) | Score 5 (Best) |
|-----------|-----------------|------------------|----------------|
| D1 Cost | >$10/run or prohibitive pricing | $0.50–$2.00/run | <$0.10/run or free |
| D2 Speed | No real parallelism | Some parallelism with constraints | ≤5 min, genuinely parallel |
| D3 Accuracy | <5% SWE-Bench or systematic failure | 15–30% SWE-Bench or moderate review needed | ≥50% SWE-Bench or top-3 ranking |
| D4 Workflow Rigor | No coordination mechanisms | Role separation or retry-logging | All 4 rigor components, enforced |
| D5 Observability | Black-box, no logs | Structured logs, post-hoc only | Real-time dashboard + replay |
| D6 Recovery | Hard failure, no retry | Retry with max-attempts | Multi-tier taxonomy + circuit breaker |
| D7 Setup | >1 day, infrastructure required | Half-day, config files needed | 15 min, single command |
| D8 Scalability | Single-agent only | 3–5 agent sweet spot | 10+ agents with sub-linear overhead |

---

*Rubric version 1.0 — frozen for audit-2026-0331. H2, H3, H4 must not supplement or reinterpret anchors. If an anchor is ambiguous for a specific system, apply the conservative interpretation (lower score) and note the ambiguity in evidence notes.*
