# SWE-bench Competitive Intelligence

**Spectrum**: swe-bench-prep-0401
**Howler**: H5 Competitive Intelligence
**Date**: 2026-03-31

---

## Executive Summary

The SWE-bench Verified leaderboard has matured past 79% (Sonar Foundation Agent, Feb 2026). The frontier has moved to SWE-bench Pro — a harder, contamination-resistant benchmark where the current leader (Augment Code's Auggie) sits at 51.80%. The gap between Verified and Pro scores is stark: agents that claim 70-80% on Verified often score 20-30 points lower on Pro. This compression is the most important signal: **scaffold and context quality now dominate model choice**.

---

## 1. Competitor Pipeline Breakdowns

### 1.1 Augment Code / Auggie — 70.6% Verified, 51.80% Pro (current #1 Pro)

**Architecture overview:**
1. **Context Engine ingestion** — semantic index of the full codebase, handling 400,000+ files with semantic dependency analysis. Not keyword matching: understands call graphs, symbol relationships, and cross-file dependencies.
2. **Issue parsing** — extracts reproduction steps, affected symbols, expected vs. actual behavior from the GitHub issue.
3. **Targeted retrieval** — Context Engine narrows the search space to semantically relevant files and functions before the agent ever sees them.
4. **Claude Sonnet 3.7 agent loop** — tool-calling agent with read/write/run tools inside a Docker container. The agent drives the main implementation loop.
5. **Ensembling (open-source version)** — generates multiple candidate patches, then an OpenAI o1 model acts as an ensembler to pick the best via majority vote. The ensembler prompt and model are configurable.
6. **Evaluation harness** — end-to-end Docker-based; runs the existing test suite against the candidate patch to verify resolution.

**What makes it work:** The Context Engine is the primary differentiator. On SWE-bench Pro — where the average solution touches 4.1 files and 107 lines — semantic navigation outperforms BM25/keyword retrieval by a large margin. Auggie solved 15 more problems on Pro than Cursor and 17 more than Claude Code using the same underlying model (Claude Opus 4.5).

**Cost per task:** Not published. Estimated ~$3–18/task for the agent loop (1–3.5M tokens at Sonnet/Opus pricing); ensembling adds another pass with o1, roughly doubling cost on contested tasks.

**Open-source:** The scaffold is public at `augmentcode/augment-swebench-agent`.

---

### 1.2 GitHub Copilot Workspace — ~55–56% Verified

**Architecture overview:**
1. **Repository vector indexing** — up to 1M tokens of code stored in Azure Cognitive Search.
2. **Multi-model routing** — task complexity determines model: Claude for reasoning-heavy planning, GPT-4o for speed-critical edits, Gemini for multimodal tasks (reading diagrams in docs).
3. **Task planning layer** — Workspace generates a structured plan before writing any code; the user can inspect and modify the plan.
4. **Multi-file patch generation** — edits are coordinated across files with the plan as the guide.
5. **Test validation** — runs existing tests against the produced patch.

**Notable numbers:** On tasks touching 3+ files, Workspace reaches 78% accuracy vs. 62% for Cursor — the planning layer appears to pay off specifically on multi-file scope.

**Cost per task:** Not published. Covered under GitHub Copilot Enterprise pricing ($39/user/month); not exposed as a per-task API.

**Weakness:** Verified score stalled around 55–56% while competitors moved to 70%+. The multi-model routing adds latency and coordination overhead; the planner is still largely interactive (human-in-the-loop), which penalizes it in fully automated benchmark settings.

---

### 1.3 Factory / Droids — 58.75% Terminal-Bench; SWE-bench Lite: 31.67% pass@1

**Architecture overview — the "Droid Army" pattern:**
1. **Delegator** — orchestrates a hierarchy of specialist Droids; receives a natural-language task, decomposes it, and dispatches subtasks.
2. **Spec Droid** — reads the issue and writes a structured specification including test criteria.
3. **test-writer Droid** — generates failing tests from the spec (TDD-first).
4. **coding-agent Droid** — implements code to make the failing tests pass.
5. **Verifier** — runs the test suite; if tests fail, loops back to the coding-agent.
6. **Droid Exec** — headless, one-shot execution mode for CI/CD and batch benchmark runs.

**What their Terminal-Bench result means:** The 58.75% on Terminal-Bench (Droid holds 3 of the top 5 spots across models) measures broader software engineering — build/test management, dependency resolution, data pipelines, systems tasks — not just issue patching. Factory positions Terminal-Bench as a harder, more real-world signal than SWE-bench.

**SWE-bench Lite improvement with sampling:** pass@1 = 31.67%, pass@2 = 37.67%, pass@6 = 42.67%. The sampling gain is notable — each additional attempt recovers ~3–5 points.

**Key insight:** Factory's claim is that agent design, not model choice, is the decisive factor. They achieve leading Terminal-Bench results across multiple underlying models (Opus, GPT-5, Sonnet).

**Cost per task:** Not published. TDD loop with multiple Droids likely runs 3–6 passes per task; estimate $10–40/task at current Opus pricing.

---

### 1.4 Amazon Q Developer — 66% Verified (April 2025)

**Architecture overview:**
1. **IDE-native environment** — the agent runs with full IDE access: file read/write, terminal, test runner, debugger.
2. **Planning + reasoning tools** — explicit planning step before implementation; uses advanced model capacity for plan quality.
3. **Multi-candidate generation** — generates several candidate solutions for each problem, selects the most promising one before returning to the developer.
4. **AWS Bedrock multi-model routing** — Claude for complex reasoning, Titan for code synthesis, other models based on prompt type.
5. **Test-driven validation** — executes existing and generated tests against candidates.
6. **SWE-bench submission** — the April 2025 agent (v20250405-dev) resolved 330 of 500 Verified instances (66.0%).

**What separates them:** The multi-candidate + selection loop is the clearest signal. Instead of committing to the first plausible patch, the agent generates a set and applies a quality-selection heuristic. This alone is responsible for a significant share of the score improvement over single-attempt systems.

**Pro score:** Not published as of research date.

**Cost per task:** Not published. The multi-candidate approach multiplies base inference cost by the number of candidates; likely $15–50/task.

---

### 1.5 Claude-flow — Claimed 85% (SWE-bench Lite, not Verified)

**Important caveat: this is SWE-bench Lite, not Verified. These are not comparable.**

**Architecture overview:**
1. **Coordination modes** — multiple topologies: hierarchical (queen/workers), mesh (peer-to-peer), and distributed with monitoring.
2. **"optimization-mesh" mode** — 8 agents running in mesh topology with optimization strategy; this is the mode that produced the 85% claim.
3. **swarm scaling** — agents spawn sub-workers, share context, divide work automatically.
4. **Benchmark system** — 300 instances evaluated; 255 successful patches; average task duration 420 seconds.

**Verifiability assessment: LOW.** The 85% figure comes from the project's own wiki documentation, not from a submission on the official swebench.com leaderboard. Key issues:
- **SWE-bench Lite vs. Verified** — Lite is a 300-instance subset; Verified is the current industry standard. Agents routinely score 15–25 points higher on Lite than on Verified due to easier instance selection.
- **No independent reproduction** — no third-party has replicated the 85% result on Lite, let alone on Verified.
- **Documentation is self-reported** — the "submission-ready predictions" referenced in the wiki have not been submitted to the official leaderboard.
- **Context**: The same model, same scaffold, shows ~23% on a basic SWE-Agent scaffold vs. 45%+ on an optimized 250-turn scaffold. Scaffold optimization alone can swing ±20 points. The 85% claim likely reflects heavy scaffold tuning on Lite, not general capability.

**Bottom line:** Claude-flow demonstrates interesting multi-agent coordination concepts. The 85% claim should be treated as unverified. The realistic equivalent Verified score, if it were submitted, would likely be in the 50–65% range based on the Lite-to-Verified discount historically observed.

---

## 2. Score Comparison Table

| System | SWE-bench Verified | SWE-bench Pro | Notes |
|---|---|---|---|
| Sonar Foundation Agent | 79.2% | — | Feb 2026, Claude Opus 4.5 |
| Claude Opus 4.5 (Live-SWE-agent) | 79.2% | — | Official Anthropic-adjacent scaffold |
| Gemini 3 Pro (Live-SWE-agent) | 77.4% | — | |
| **Augment Code / Auggie** | ~70.6% | **51.80% (#1)** | Context Engine; open-source scaffold |
| Warp | 71% | — | Single-agent, single-attempt |
| Amazon Q Developer | 66% | — | April 2025; multi-candidate |
| Claude Opus 4.5 (SWE-Agent scaffold) | — | 45.89% | Scale AI SEAL standardized scaffold |
| Factory / Droids | 31.67% (Lite) | — | Terminal-Bench: 58.75% |
| GitHub Copilot Workspace | ~55–56% | — | Multi-model routing, planning layer |
| Claude-flow | ~85% (Lite) | — | **UNVERIFIED; Lite only, self-reported** |

**SWE-bench Pro current top:**
| Rank | System | Score |
|---|---|---|
| 1 | Augment Code / Auggie | 51.80% |
| 2 | Cursor (standardized) | ~36.80% |
| 3 | Claude Code (standardized) | ~34.80% |

*Note: SWE-bench Pro public dataset scores from Scale AI leaderboard.*

---

## 3. Cost Per Task Comparison

| System | Estimated Cost/Task | Basis |
|---|---|---|
| Single-agent, single-attempt (Sonnet) | $1–5 | 1–3.5M tokens × $3/M input |
| Single-agent, single-attempt (Opus) | $3–18 | Same token range, higher rate |
| Augment Code (with ensembling) | $6–35 | Agent loop + o1 ensembler pass |
| Amazon Q (multi-candidate, 3–5 candidates) | $15–50 | Multiplied by candidate count |
| Factory Droids (TDD loop, 3–6 passes) | $10–40 | Multiple Droid passes per task |
| Claude-flow (8-agent mesh) | $20–80 | 8× agent cost + coordination |
| DGM (self-improving training run) | ~$22,000 | Cited in original paper; training, not inference |

**Key observations:**
- A full SWE-bench Verified run (500 tasks) costs roughly $500–$9,000 depending on approach.
- Ensembling and multi-candidate approaches multiply costs 2–5×.
- The DGM ($22K) is an outlier — that is a *training* run, not an inference benchmark.
- Budget-conscious teams use Sonnet for exploration and reserve Opus for final submission runs.

---

## 4. Techniques That Improve Scores

### 4.1 Semantic Context Retrieval (High Impact)
BM25/keyword retrieval is a hard ceiling. File-path accuracy on Verified vs. held-out sets shows 3–6× advantage for systems using semantic indexes. Augment's Context Engine demonstrates this most clearly: it beat Claude Opus 4.5 + standard scaffold by ~6 points on Pro using the *same model* purely through better retrieval.

**Spectrum adoption:** A semantic index of the target repo before the agent loop begins — even a lightweight one using embeddings — is the highest-ROI single improvement.

### 4.2 Multi-Candidate Generation with Selection (Medium-High Impact)
Amazon Q's approach: generate N candidates, select the best. Factory's pass@k data confirms the trend — each additional sample recovers 3–5 points. The selection heuristic matters; naive majority vote is weaker than a reasoning model as judge.

**Spectrum adoption:** Run 3 candidates per task for contested problems; use a separate judge (o1, Opus) to select. Budget accordingly.

### 4.3 TDD Loop — Failing Tests Before Implementation (Medium Impact)
Factory's Spec→test-writer→coding-agent→verify loop ensures the agent has a concrete success criterion before writing code. This reduces "plausible but wrong" patches. The loop exit condition (tests pass) is mechanical, not just LLM judgment.

**Spectrum adoption:** For tasks where a reproduction case exists in the issue, generate a failing test first. Use it as a hard gate for patch acceptance.

### 4.4 Multi-Attempt with Environment Feedback (Medium Impact)
72% of passing tasks on SWE-bench take over 10 minutes, suggesting iterative refinement is normal. Agents that reset on failure and retry with different context rather than persisting on a dead-end approach score higher.

**Spectrum adoption:** Give the agent explicit retry budget with different retrieval/approach on each attempt. Track which approaches were tried.

### 4.5 Explicit Planning Before Coding (Medium Impact)
Copilot Workspace's structured plan before edit generation explains its multi-file advantage (78% vs. 62% for Cursor at 3+ files). Even if overall scores lag, the planning layer prevents scope drift on complex tasks.

**Spectrum adoption:** For multi-file tasks, require an explicit change plan (files to touch, expected changes, expected test outcomes) before any edits begin.

### 4.6 Use a Reasoning Model as Ensembler/Judge (Medium Impact)
Augment uses o1 as the ensembler. The asymmetry — fast model generates, slow reasoning model selects — is efficient. The reasoning model doesn't need to regenerate; it just reads candidates and picks.

**Spectrum adoption:** Claude Opus or o1 as a judge across 3–5 Sonnet-generated candidates is likely cost-effective at current prices.

---

## 5. Techniques That Inflate Scores (Avoid)

### 5.1 Evaluating on SWE-bench Lite and Reporting as Comparable to Verified
Lite is a 300-instance subset; Verified is the 500-instance human-validated standard. Agents routinely score 10–25 points higher on Lite. Claude-flow's 85% Lite claim is the clearest example. Always specify the split.

### 5.2 Using Test-Only Evaluation (Not Full Test Suite)
Standard SWE-bench evaluation runs only the tests modified in the original PR. Running the full test suite catches regressions that the partial suite misses. The partial evaluation overstates solve rates by 4–7% and misses ~29.6% of "plausible but wrong" patches.

**Mitigation:** Run full test suites, not just the gold-patch tests. Use differential patch testing to identify behavioral divergence.

### 5.3 Benchmark-Aware Training / Data Contamination
Over 94% of SWE-bench Verified issues predate LLM knowledge cutoffs. Models can memorize issue–solution pairs. File-path accuracy is 3–6× higher on Verified vs. held-out sets — a contamination signal. Reported contamination rates reach 8–10% on some evaluations, inflating scores by up to 6.2 percentage points.

**Mitigation:** Use SWE-bench Pro (constructed from copyleft/private repos), SWE-rebench (automated decontamination pipeline), or time-filter to post-cutoff issues.

### 5.4 Oracle-Assisted Retrieval
Providing the agent with the exact file(s) to edit ("oracle file localization") inflates scores by 3–5× vs. realistic retrieval. Any system that pre-populates the context with ground-truth file pointers is not measuring real-world capability.

### 5.5 Self-Reported Benchmarks Without Leaderboard Submission
Without a submission to the official swebench.com leaderboard with verifiable instance-level results, scores cannot be audited. Claude-flow's wiki documentation is the pattern to avoid. Always submit to the official leaderboard or publish instance-level predictions publicly.

### 5.6 Running on Unrepresentative Problem Subsets
Cherry-picking "easy" or repo-familiar problems. Cross-repository generalization is significantly lower than within-distribution. Any evaluation should span multiple repositories and problem types.

---

## 6. Honest Assessment: Realistic Score Range for Spectrum

**Context:** Spectrum is a multi-agent parallel execution framework, not a purpose-built SWE-bench agent. The mapping is not 1:1.

### Baseline (Howler with minimal SWE-bench scaffolding)
- Single Howler, basic file tools, no semantic retrieval: **15–30% Verified**
- This is approximately where Factory Droids landed on Lite before their TDD improvements.

### With targeted improvements
| Improvement | Expected Gain |
|---|---|
| Semantic repo index (embeddings) | +10–15 pts |
| TDD loop (failing test before patch) | +5–8 pts |
| 3-candidate generation + judge | +5–8 pts |
| Explicit planning step | +3–5 pts |
| Full test suite evaluation | -2 pts (surface regressions, not inflate) |

**Realistic ceiling with all improvements:** **38–55% Verified**

This puts Spectrum in the tier of:
- Factory Droids (after improvements): ~42% Lite / ~35% Verified equivalent
- Amazon Q early 2025 performance (~50–55% Verified)
- Below the current top tier (Augment 70%, Sonar 79%) without a proprietary Context Engine

### Why Spectrum won't reach 70%+ without a Context Engine
The semantic index is the differentiator. The top performers share this: Augment has it as a first-class product feature. Sonar integrates static analysis context. Warp built codebase-aware context into their terminal. Without similar infrastructure, retrieval quality caps out around 50–55% on Verified.

### What the SWE-bench Pro number would look like
Pro scores run ~20–30 points below Verified for the same system. At 38–55% Verified, Spectrum would likely score **18–30% Pro** — competitive with where most commercial agents were on Pro in mid-2025.

---

## 7. Key Takeaways for Spectrum Development

1. **Semantic retrieval is the lever** — more than model choice, more than multi-agent coordination. The Augment-vs-Cursor gap on Pro (51.80% vs. ~36.80%) uses the same model and differs only in retrieval.

2. **Multi-agent coordination has weak SWE-bench signal** — Warp achieved 71% with a single primary agent. The multi-agent benefit shows on *long-horizon* tasks (SWE-bench Pro's 4+ file edits), not individual issue resolution. Spectrum's parallel model is better suited to batching tasks than to coordinating on a single issue.

3. **Sampling > coordination for individual tasks** — pass@k scaling (Factory: +3–5 pts per additional attempt) is cheaper and more reliable than coordinating N agents on one problem.

4. **SWE-bench Pro is the honest benchmark** — Verified is saturating (79%+). Any evaluation worth publishing should target Pro or a decontaminated set.

5. **Full test suite evaluation is mandatory** — the 4–7% inflation from partial suites is material; any internal benchmark should run the complete project test suite.

6. **Budget a full Verified run** — 500 tasks × $5–15/task = $2,500–$7,500. Budget before committing to a submission run.

---

## Sources

- [Auggie tops SWE-Bench Pro | Augment Code](https://www.augmentcode.com/blog/auggie-tops-swe-bench-pro)
- [#1 open-source agent on SWE-Bench Verified — Augment Code blog](https://www.augmentcode.com/blog/1-open-source-agent-on-swe-bench-verified-by-combining-claude-3-7-and-o1)
- [augmentcode/augment-swebench-agent — GitHub](https://github.com/augmentcode/augment-swebench-agent)
- [VentureBeat: Augment Code debuts AI agent with record-breaking SWE-bench score](https://venturebeat.com/ai/augment-code-debuts-ai-agent-with-70-win-rate-over-github-copilot-and-record-breaking-swe-bench-score)
- [GitHub Next | Copilot Workspace](https://githubnext.com/projects/copilot-workspace)
- [Copilot SWE model rolling out to VS Code Insiders — GitHub Changelog](https://github.blog/changelog/2025-09-22-copilot-swe-model-rolling-out-to-visual-studio-code-insiders/)
- [Droid: The #1 Software Development Agent on Terminal-Bench | Factory.ai](https://factory.ai/news/terminal-bench)
- [Code Droid: A Technical Report | Factory.ai](https://factory.ai/news/code-droid-technical-report)
- [How to make Droids code for hours using TDD — Medium](https://medium.com/@silas_27632/how-to-make-droids-code-for-hours-using-test-driven-development-and-smart-orchestration-in-factory-a-40838d66e048)
- [Reinventing the Amazon Q Developer agent for software development — AWS Blog](https://aws.amazon.com/blogs/devops/reinventing-the-amazon-q-developer-agent-for-software-development/)
- [April 2025: A month of innovation for Amazon Q Developer — AWS Blog](https://aws.amazon.com/blogs/devops/april-2025-amazon-q-developer/)
- [SWE Bench Evaluation · ruvnet/claude-flow Wiki](https://github.com/ruvnet/claude-flow/wiki/SWE-Bench-Evaluation)
- [SWE Bench Quick Reference · ruvnet/claude-flow Wiki](https://github.com/ruvnet/claude-flow/wiki/SWE-Bench-Quick-Reference)
- [Scale Labs Leaderboard: SWE-Bench Pro (Public Dataset)](https://labs.scale.com/leaderboard/swe_bench_pro_public)
- [SWE-Bench Pro Leaderboard — Morph LLM](https://www.morphllm.com/swe-bench-pro)
- [SWE-Bench Verified Leaderboard — llm-stats.com](https://llm-stats.com/benchmarks/swe-bench-verified)
- [The SWE-Bench Illusion: When SoTA LLMs Remember Instead of Reason — arXiv](https://arxiv.org/html/2506.12286v3)
- [Why SWE-bench Verified no longer measures frontier coding capabilities — OpenAI](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/)
- [SWE-rebench: Automated Pipeline for Decontaminated Evaluation — Medium](https://artgor.medium.com/paper-review-swe-rebench-an-automated-pipeline-for-task-collection-and-decontaminated-evaluation-8741b3ebd712)
- [Many SWE-bench-Passing PRs Would Not Be Merged into Main — METR](https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/)
- [Warp: Warp scores 71% on SWE-bench Verified](https://www.warp.dev/blog/swe-bench-verified)
- [SWE-Effi: Re-Evaluating Software AI Agent System — arXiv](https://arxiv.org/pdf/2509.09853)
- [Sonar Claims Top Spot on SWE-bench leaderboard](https://www.sonarsource.com/company/press-releases/sonar-claims-top-spot-on-swe-bench-leaderboard/)
- [SOTA on swebench-verified: relearning the bitter lesson — aide.dev](https://aide.dev/blog/sota-bitter-lesson)
- [Are "Solved Issues" in SWE-bench Really Solved Correctly? — arXiv](https://arxiv.org/html/2503.15223v1)
