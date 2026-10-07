# Agent Evals & Observability FAQ

> A running FAQ for the course — the most difficult questions, answered in one place.
> Last updated: 2026-10-07. Source: Manjeet’s FAQ collection, organized by section.
> Suggest a question via PR or bring it to office hours.

## Contents

- [Section 1 — Getting Started & Fundamentals](#section-1--getting-started--fundamentals)
- [Section 2 — Agent Observability Foundations](#section-2--agent-observability-foundations)
- [Section 3 — Error Analysis & Data Collection](#section-3--error-analysis--data-collection)
- [Section 4 — Evaluation Design & Methodology](#section-4--evaluation-design--methodology)
- [Section 5 — Human Annotation & Process](#section-5--human-annotation--process)
- [Section 6 — Guardrails, Trust & Safety](#section-6--guardrails-trust--safety)
- [Section 7 — Context Engineering & RAG Evaluation](#section-7--context-engineering--rag-evaluation)
- [Section 8 — Multi-Agent & Agentic Workflow Evaluation](#section-8--multi-agent--agentic-workflow-evaluation)
- [Section 9 — Production Monitoring & Observability Operations](#section-9--production-monitoring--observability-operations)
- [Section 10 — Observability in Practice: Answering Operational Questions](#section-10--observability-in-practice-answering-operational-questions)
- [Section 11 — Tools, Frameworks & Infrastructure](#section-11--tools-frameworks--infrastructure)
- [Section 12 — Continuous Improvement & Fine-tuning](#section-12--continuous-improvement--fine-tuning)
- [Section 13 — PM Playbook: Quick Reference](#section-13--pm-playbook-quick-reference)

## Section 1 — Getting Started & Fundamentals

*Hands-on in [Week 1 — Eval Foundations and Error Analysis](../week-01-eval-foundations-and-error-analysis/)*

<details>
<summary><strong>What are AI Agent Evals?</strong></summary>

AI Agent Evals (Evaluations) are structured methods for measuring whether your AI system is actually doing what you need it to do — for your specific users, use cases, and business goals. This is distinct from foundational model benchmarks (like MMLU or HumanEval), which test general model capability.

There are three levels of evaluation, from simplest to most rigorous:

Level 1 — Unit Tests: Deterministic, code-based assertions (e.g., "did the agent return a valid JSON?", "did it avoid mentioning competitors?"). Cheap, fast, reliable.

Level 2 — Human &amp; Model Eval: A human or LLM-as-a-Judge reviews outputs and makes pass/fail judgments on subjective quality criteria. This is the backbone of a mature eval system.

Level 3 — A/B Testing: Comparing two versions of your system in production to measure real business impact (e.g., task completion rates, escalation rates).

For most teams, the highest-ROI starting point is Level 1 + Level 2 in offline development, with Level 3 reserved for significant changes.

</details>

<details>
<summary><strong>What is a trace?</strong></summary>

A trace is the complete record of all actions, messages, tool calls, and data retrievals from a single initial user query through to the final response. It includes every step across all agents, tools, and system components in a session: multiple user messages, assistant responses, retrieved documents, and intermediate tool interactions.

</details>

> ⚠️ Heads up: Different observability vendors use varying definitions of traces and spans. Standardization is improving with OpenTelemetry's GenAI semantic conventions, but always verify terminology with your specific tooling.

<details>
<summary><strong>What's the difference between an LLM, augmented LLM, LLM workflow, agent, and multi-agent system?</strong></summary>

These terms are often used interchangeably but they mean very different things:

LLM — Stateless: text in, text out with no memory or context unless specified in the input.

Augmented LLM — Adds memory, retrieval (RAG), and tool calls. Virtually all production LLMs are augmented.

LLM Workflow — LLMs and tools orchestrated through predefined code paths. The developer controls the control flow (a DAG). Predictable, debuggable.

Agent — The LLM dynamically directs its own processes and tool usage in a loop. The path is not predetermined.

Multi-Agent System — A primary orchestrating agent delegates heavy-duty subtasks to specialized sub-agents, each operating in its own context.

</details>

> PM Insight: Most production value today lives in augmented LLMs and LLM workflows. Full agents are best for open-ended problems where you cannot predict the required steps in advance (e.g., research, coding agents).

<details>
<summary><strong>What's a Minimum Viable Eval (MVE)?</strong></summary>

An MVE is a set of input-output pairs for your AI system, plus a script that runs your system's outputs against that set. The script can include code checks (regex, schema validation) and LLM-as-judge calls. Together, they form your eval harness — the thing that tells you whether a change made your system better or worse.

There is a natural ladder of evaluation maturity:

Vibe checks — Manually look at 20 input-output pairs. Before you automate anything, do this.

Failure analysis — Systematically categorize where things go wrong.

Automated eval harness — Code checks + LLM judges running in CI/CD and production monitoring.

Start with error analysis, not infrastructure. Spend 30 minutes manually reviewing 20-50 LLM outputs whenever you make significant changes.

</details>

<details>
<summary><strong>How much of my development budget should I allocate to evals?</strong></summary>

Evaluation is part of the development process, not a separate line item — similar to how debugging is part of software engineering. In practice, leading teams spend 60-80% of AI development time on error analysis and evaluation.

Key principles:

Always be doing error analysis. Many issues discovered are simple bugs fixed immediately, requiring no special eval infrastructure.

Apply cost-benefit thinking. Simple assertions and regex checks are cheap. LLM-as-Judge evaluators require 100+ labeled examples and ongoing maintenance.

Be wary of optimizing for high eval pass rates. A 70% pass rate may indicate a more meaningful eval than 100% — stress-test your system rather than making metrics look good.

</details>

<details>
<summary><strong>How do I make the case for investing in evaluations to my team?</strong></summary>

Do not try to sell "evals" as a concept. Instead, show what you find when you look at the data.

Start by doing error analysis yourself — review 50-100 real user conversations.

Present findings as: top failure modes discovered, how often they occur, surprising user behaviors, and bugs you fixed.

Frame fixes as "prevented production issues" — show how error rates for specific problems went down after fixes.

Tell stories, not just dashboards. Narrate what you're finding to build shared intuition.

Let results, not methods, lead the conversation.

</details>

<details>
<summary><strong>Will today's evaluation methods still be relevant in 5-10 years?</strong></summary>

Yes. Even with dramatically better models, you still need to verify they are solving the right problem. The need for systematic error analysis, domain-specific testing, and monitoring persists regardless of model capability.

Today's prompt engineering tricks may become obsolete, but understanding failure modes will always matter. Research shows that people need to observe model behavior in order to properly articulate their requirements — you cannot fully specify what you want without seeing the system in action.

</details>

## Section 2 — Agent Observability Foundations

*Hands-on in [Week 1 — Eval Foundations and Error Analysis](../week-01-eval-foundations-and-error-analysis/)*

<details>
<summary><strong>What is AI agent observability and why does it matter?</strong></summary>

AI agent observability is the process of monitoring and understanding the end-to-end behavior of agentic systems — including all interactions with LLMs, tools, retrieval systems, memory, and other agents.

Unlike deterministic software, agents make dynamic decisions, adapt their behavior based on context, and can produce different outputs for identical inputs. Traditional application monitoring (CPU, memory, latency) is necessary but not sufficient. You need AI-specific signals to understand whether agents are behaving correctly.

The goal: make your agent a glass box, not a black box.

Why it matters for PMs and engineering leaders:

You cannot improve what you cannot see. Observability data feeds directly into your eval and improvement loop.

Cost control. Agents autonomously chain multiple LLM and API calls, creating unpredictable token costs without real-time tracking.

Trust and safety. Enterprise customers demand audit trails, accountability, and compliance evidence.

Debugging complex failures. In multi-agent systems, failures cascade across components — distributed tracing is the only way to isolate root causes.

</details>

<details>
<summary><strong>What signals does agent observability capture?</strong></summary>

Agent observability extends traditional MELT (Metrics, Events, Logs, Traces) with AI-specific signals:

Traditional signals:

Metrics — Latency, error rates, throughput, infrastructure utilization.

Events — Discrete moments during model execution: user prompts, model responses, tool invocations.

Logs — Agent decisions, tool calls, internal state changes.

Traces — Full execution flows tracking each model interaction's lifecycle.

AI-specific signals:

Token usage — Tokens per request, cumulative cost per trace/user/feature. Essential for budget management.

Tool interactions — Which tools agents invoke, success rates, latency per tool, patterns in tool selection.

Decision path lengths — How many steps/turns an agent took to complete a task.

Retrieval quality signals — Relevance of retrieved context, chunk hit rates, embedding similarity scores.

Model parameters — Temperature, top_p, model version per call.

Agent reasoning traces — Intermediate thought steps, especially for chain-of-thought and ReAct-style agents.

</details>

<details>
<summary><strong>What is the difference between traditional observability and AI agent observability?</strong></summary>

Traditional observability monitors infrastructure and application health (is the server up, is latency acceptable?). Agent observability adds two critical layers:

</details>

| Dimension | Traditional Observability | AI Agent Observability |
| --- | --- | --- |
| Focus | Infrastructure health | Agent behavior &amp; decision quality |
| Key Metrics | CPU, memory, latency, error rate | + Token usage, tool calls, step count, cost/trace |
| Failure Mode | Service down, timeout | Wrong answer, hallucination, goal drift |
| Non-determinism | Deterministic, reproducible | Same input → different output (normal) |
| Evaluation | Pass/fail tests | + LLM-as-judge, human review, quality scores |
| Governance | SLAs, uptime | + Safety, compliance, ethical guardrails |

<details>
<summary><strong>What is OpenTelemetry and why does it matter for AI agents?</strong></summary>

OpenTelemetry (OTel) is the open-source industry standard for collecting telemetry data (traces, metrics, logs). The OpenTelemetry GenAI SIG (Special Interest Group) is actively defining semantic conventions specifically for AI agents — standardizing how frameworks report LLM calls, tool invocations, and agent decisions.

Why this matters:

Prevents vendor lock-in — standardized telemetry means you can switch observability backends (Datadog, Splunk, Langfuse, Arize) without re-instrumenting.

Framework interoperability — Frameworks like CrewAI, LangGraph, Pydantic AI, and AutoGen are converging on OTel, enabling consistent monitoring regardless of the stack.

Enterprise-grade auditability — Standardized traces satisfy enterprise security, compliance, and audit requirements.

</details>

> Action for PMs: Require OTel-compatible telemetry in your agent infrastructure from day one. Retrofitting is expensive. The OTel GenAI semantic conventions are the emerging industry standard — build to them.

<details>
<summary><strong>How does distributed tracing work for multi-agent systems?</strong></summary>

In a multi-agent system, a single user request may be processed by multiple agents — each making their own LLM calls, tool calls, and sub-agent delegations. Distributed tracing creates parent-child span relationships across all these components, giving you a unified view of the entire execution.

Key concepts:

Trace — The top-level execution record for a single user request, spanning all agents involved.

Span — A single unit of work within a trace (one LLM call, one tool call, one sub-agent invocation).

Parent-child relationships — Span hierarchy reconstructs the full context of agent operations and shows task delegation.

Session — Groups related multi-turn traces belonging to a single user session.

Best practices:

Instrument every step: LLM calls, tool invocations, RAG retrievals, memory operations, decision points. Missing any component creates blind spots.

Store sufficient detail to replay failures — include input artifacts, intermediate outputs, and configuration states.

Use sampling for high-volume systems — collect full detail for 1 in 10 requests or on errors only, to manage storage costs.

Use async instrumentation — never let telemetry collection block your agent's core execution path.

</details>

<details>
<summary><strong>What is an Agent Harness and how does it relate to observability?</strong></summary>

An agent harness is the scaffolding around the LLM that manages the agentic loop, tool execution, message history, context, safety guardrails, and state. Think of the LLM as the brain — the harness is everything else that lets it actually do things.

The harness is the primary observability surface for agents. Key harness components to instrument:

The agentic loop — each iteration of prompting the model, parsing output, executing tools, and feeding results back.

Tool execution — which tools were called, with what parameters, and what they returned.

Context management — what went into the prompt, token counts, context window utilization.

State — conversation history, files touched, memory reads/writes.

</details>

| Industry note: Be prepared to rebuild your agent harness frequently. Leading agents like Manus have been re-architected five times since 2024, and Anthropic regularly rebuilds Claude Code's harness as models improve. Instrument for observability from the start so rebuilds don't create telemetry gaps. |
| --- |

## Section 3 — Error Analysis & Data Collection

*Hands-on in [Week 1 — Eval Foundations and Error Analysis](../week-01-eval-foundations-and-error-analysis/)*

<details>
<summary><strong>Why is error analysis the single most important activity in evals?</strong></summary>

Error analysis is the foundation of everything else. It tells you what to evaluate in the first place. Without it, you end up measuring abstract qualities that may not matter for your use case.

The four-step error analysis process:

Step 1 — Create a Dataset: Gather representative traces of user interactions. If you have no data yet, generate synthetic data (see below).

Step 2 — Open Coding: A domain expert reviews traces and writes open-ended notes about issues — like journaling. Focus on the first failure in each trace, as upstream errors cause downstream problems.

Step 3 — Axial Coding: Categorize the open-ended notes into a failure taxonomy. Group similar failures into distinct categories and count occurrences. This is the most important step.

Step 4 — Iterative Refinement: Keep reviewing until new traces reveal no new failure modes (theoretical saturation). Aim for at least 100 traces per cycle.

</details>

| Key rule: Do not skip error analysis. It ensures your eval metrics are grounded in real application behavior rather than generic, platform-nudged metrics that create false confidence. |
| --- |

<details>
<summary><strong>How do I surface problematic traces for review beyond user feedback?</strong></summary>

Random sampling — Start with a random sample. If few issues appear, escalate to stress testing with queries that deliberately test your constraints.

Outlier detection — Sort by any metric (response length, latency, number of tool calls) and review the extremes.

User feedback signals — Prioritize traces with negative feedback, thumbs-down ratings, support tickets, or escalations.

Metric-based sorting — Use generic metrics as exploration signals, not quality measures. Review both high and low scores as clues, then build custom evaluators for the failure modes you find.

Stratified sampling — Group traces by user type, feature, query category, and sample from each group to ensure coverage.

Embedding clustering — Generate embeddings of queries and cluster them. Sample proportionally from clusters, but oversample small clusters for edge case coverage.

</details>

<details>
<summary><strong>How often should I re-run error analysis on my production system?</strong></summary>

After significant changes — new features, prompt updates, model switches, major bug fixes. This is mandatory.

Regularly — aim to review at least 100+ fresh traces every 2-4 weeks during active development.

Weekly — review 10-20 traces focusing on outliers: unusually long conversations, multiple retries, automated flags.

New systems — weekly analysis until failure patterns stabilize.

Mature systems — monthly, unless usage patterns change significantly.

Always after incidents — user complaint spikes, metric drift, or anomalous behavior patterns.

</details>

<details>
<summary><strong>What is the best approach for generating synthetic data?</strong></summary>

The common mistake is prompting an LLM for "test queries" without structure, resulting in generic, repetitive outputs. A structured dimension-based approach produces far better synthetic data.

The framework:

Define dimensions — categories that describe different aspects of user queries. Example for a customer support bot: Issue Type (billing, technical, general), Customer Mood (frustrated, neutral, happy), Prior Context (new issue, follow-up, resolved).

Start with failure hypotheses — use your application extensively first, then choose dimensions targeting likely failures.

Create tuples manually first — write 20 tuples by hand (e.g., frustrated + billing + follow-up). This builds understanding before you scale.

Scale with two-step generation — first generate structured tuples, then convert tuples to natural language in a separate prompt. This separation prevents repetitive phrasing.

Run synthetic queries through your actual system to capture full traces — then use those traces for error analysis.

</details>

| Pro tip: Fix obvious problems before generating synthetic data. If your prompt doesn't mention a constraint, fix the prompt first rather than generating specialized test queries around it. |
| --- |

<details>
<summary><strong>Are there scenarios where synthetic data may not be reliable?</strong></summary>

Complex domain-specific content — Legal filings, medical records, and technical forms have structural nuance LLMs often miss.

Low-resource languages or dialects — LLM-generated samples are often unrealistic and will not reflect actual performance.

When validation is impossible — If you cannot verify whether synthetic samples are realistic (due to domain complexity), use real data.

High-stakes domains — Medicine, law, emergency response. Synthetic data lacks the subtlety and edge cases that matter most here.

Underrepresented user groups — LLMs may misrepresent context, values, or challenges, reinforcing biases from training data.

</details>

<details>
<summary><strong>How can I efficiently sample production traces for review?</strong></summary>

Use stratified sampling — group by user segment, query type, feature area, then sample from each.

Prioritize by outcome signals — negative feedback, high latency, high token cost, failed tool calls.

Cluster embeddings — semantic clustering of queries reveals natural groupings and surfaces edge cases you might otherwise miss.

Sort by novelty — new trace patterns that don't match known categories warrant immediate review.

Set up automated flagging — configure your observability platform to auto-flag traces that exceed thresholds (cost, latency, error rate) for human review queues.

</details>

## Section 4 — Evaluation Design & Methodology

*Hands-on in [Week 2 — Designing Reliable LLM Judges](../week-02-designing-reliable-llm-judges/)*

<details>
<summary><strong>Why binary (pass/fail) evals instead of 1-5 ratings?</strong></summary>

Binary evaluations force clearer thinking and produce more consistent labeling. Likert scales (1-5) introduce significant problems:

The difference between adjacent scores (3 vs. 4) is subjective and inconsistent across annotators.

Detecting statistical differences requires much larger sample sizes.

Annotators default to middle values to avoid hard decisions.

If you want to track gradual improvements, measure specific sub-components with their own binary checks. Instead of rating factual accuracy 1-5, track "3 out of 4 expected facts included" as separate binary checks. You preserve granularity without sacrificing consistency.

</details>

| Start here: Begin with binary labels to understand what "bad" looks like. Numeric labels are advanced and usually unnecessary. |
| --- |

<details>
<summary><strong>Should I practice eval-driven development (writing evals before implementing features)?</strong></summary>

Generally no. Unlike traditional software where failure modes are predictable, LLMs have near-infinite failure surface area. You cannot anticipate what will break.

A better approach: start with error analysis and write evaluators for errors you discover, not errors you imagine. This prevents wasted effort on metrics that have no impact on actual system quality.

Exception: eval-driven development works for specific hard constraints where you know exactly what success looks like — e.g., "never mention competitor products."

</details>

<details>
<summary><strong>Should I build automated evaluators for every failure mode I find?</strong></summary>

No. Focus automated evaluators on failures that persist after fixing your prompts. Before building evaluation infrastructure:

Fix prompt gaps first — many failures stem from preferences you never specified. Specify them.

Use cheap checks first — regex patterns, structural validation, execution tests. Reserve LLM-as-Judge for subjective qualities.

Only build expensive evaluators for problems you will iterate on repeatedly. LLM-as-Judge requires 100+ labeled examples and ongoing maintenance.

</details>

<details>
<summary><strong>Should I use "ready-to-use" evaluation metrics from eval platforms?</strong></summary>

No — unless you are using them purely for exploration. Generic metrics (helpfulness, coherence, quality) measure abstract qualities that may not matter for your specific use case. Good scores on them do not mean your system works.

The right path: conduct error analysis to understand real failures, define binary failure modes based on what you observe, and create custom evaluators validated against human judgment.

</details>

| Exception: Experienced practitioners repurpose generic metrics as exploration signals — not quality measures. Use them to find interesting traces to review, not as your primary evaluation criteria. |
| --- |

<details>
<summary><strong>Are similarity metrics (BERTScore, ROUGE, cosine similarity) useful for evaluating agent outputs?</strong></summary>

Not for most agent applications. These metrics do not capture task-specific success. A response can be semantically similar to the reference yet completely wrong for your use case.

Where similarity metrics do have utility:

Search and retrieval evaluation — cosine similarity between query and retrieved chunks is a valid signal.

Output diversity measurement — average pairwise similarity across outputs can indicate response variety.

RAG retrieval debugging — measuring whether retrieved context is semantically relevant to the query.

For agent outputs, prefer binary pass/fail LLM-as-Judge evaluators or code-based assertions.

</details>

<details>
<summary><strong>What is an LLM Judge and how do I use it to evaluate other LLM outputs?</strong></summary>

An LLM Judge (also called LLM-as-a-Judge) is a large language model used to evaluate the outputs of another LLM — acting as an automated quality assessor in place of (or alongside) human annotators. It is the most important tool for scaling evaluation beyond what human review alone can cover.

Why it works: LLMs can perform nuanced, subjective assessments — tone, factual groundedness, task completion, appropriateness — that simple code-based assertions cannot capture.

The 7-step process for building an LLM Judge that actually drives results (from Hamel Husain's field guide):

Step 1 — Find your principal domain expert: The person with the deepest understanding of what "good" looks like for your specific application. This is your ground truth source.

Step 2 — Create a dataset: Gather a representative sample of real traces (ideally 100+) covering the range of inputs your system handles.

Step 3 — Direct the expert to make pass/fail judgments with critiques: Binary labels only (see Section 4). The written critique for each label is as important as the label itself — it teaches the judge model what matters.

Step 4 — Fix errors in the labeled dataset: Review the labeled set for inconsistencies before training your judge. Garbage in, garbage out.

Step 5 — Build your LLM Judge iteratively: Start with a prompt-based judge using the labeled examples and critiques as few-shot examples. Measure alignment against your labeled set using TPR and TNR.

Step 6 — Perform error analysis on the judge itself: Where does the judge disagree with the human expert? Understand why and refine the judge prompt or add more examples.

Step 7 — Create specialized judges if needed: A single judge rarely handles all failure modes well. Build separate judges for distinct dimensions (e.g., one for factual accuracy, one for tone, one for task completion).

Key practical rules:

Scope the task narrowly — a judge doing binary pass/fail on one specific criterion dramatically outperforms a judge asked to holistically rate "quality."

Measure judge alignment before trusting it — use a held-out labeled test set and measure True Positive Rate (caught bad outputs) and True Negative Rate (did not flag good outputs). Aim for &gt;85% on both before using in CI/CD.

Never trust a judge you have not validated — an unvalidated judge is worse than no judge at all because it creates false confidence.

Judges require maintenance — as your product evolves and your failure taxonomy changes, your judges need to be updated too. Budget ~weekly touchpoints with your domain expert.

The eval harness = code checks + LLM judges: Use code-based assertions for everything deterministic, reserve LLM judges for subjective qualities that cannot be captured by rules. LLM judges are powerful but 10-100x more expensive and slower than code checks.

</details>

| Common mistake: Using a generic off-the-shelf LLM judge (e.g., "rate this response 1-5 on helpfulness") with no domain-specific tuning or validation. These feel productive but create measurement theater — scores that do not correlate with what your users actually care about. |
| --- |

<details>
<summary><strong>Can I use the same model for both the main task and evaluation (LLM-as-Judge)?</strong></summary>

Generally yes — the judge is doing a fundamentally different task (binary classification) than your main pipeline. What ultimately matters is how well your judge aligns with human judgments, regardless of whether it is the same model.

Practical guidance:

Start with the most capable available model to establish strong alignment with human judgments. Optimize for cost later.

Measure alignment using True Positive Rate (TPR) and True Negative Rate (TNR) on a held-out labeled test set.

If you struggle to achieve good alignment, try a different model — but onboarding new providers has non-trivial organizational overhead.

</details>

<details>
<summary><strong>How do I evaluate a model's ability to express uncertainty (know what it doesn't know)?</strong></summary>

This capability — called "Abstention Ability" in the research literature — requires a carefully constructed evaluation set with two types of scenarios:

Answerable questions — Scenarios where a correct, verifiable answer exists in the model's context or knowledge.

Unanswerable questions — Questions with false premises, missing context, or topics outside the knowledge base. Designed to tempt hallucination.

Evaluation is a binary pass/fail: the model passes if it answers answerable questions correctly AND refuses to answer unanswerable ones. Fabricating an answer to an unanswerable question is a failure.

</details>

<details>
<summary><strong>How do I write deterministic tests for non-deterministic LLM outputs?</strong></summary>

You do not write deterministic tests for non-deterministic outputs. Instead:

Separate what can be checked deterministically (valid JSON, format, banned words absent) from what requires judgment (tone, accuracy).

Track pass rates over time rather than expecting 100%. An 85% pass rate may be excellent — a 100% pass rate likely means your tests are not hard enough.

Run the same call multiple times to understand variance before deciding if an output is "wrong."

Build curated datasets that define your product's boundaries — start with ~20 examples, grow to ~100 for confidence.

Run all test cases every time, even when some fail — you need the full pattern, not individual failures.

</details>

| Mindset shift: Think "evaluation" not "test." Your dev tests and production evals should be the same system — CI runs before deploy, production traces feed new cases back into development. |
| --- |

<details>
<summary><strong>How do I get reliable and consistent outputs from LLMs?</strong></summary>

You do not eliminate non-determinism — you build processes around it. The practitioners who ship reliable LLM applications invest in three things:

Prompt and context engineering with tight feedback loops — treat prompts like code: version control them, change one variable at a time, iterate based on observed failures.

Structured outputs and post-processing validation — use JSON mode, Pydantic schemas, and output parsers to enforce format consistency.

Systematic evaluation and testing — the highest-value activity is labeling traces pass/fail and categorizing failures. Start manually, then automate.

Additional tactics:

Break large tasks into smaller, more constrained subtasks — reduces variance and makes each piece independently testable.

Do not use an LLM when you do not need one — regex, fuzzy matching, and rule-based logic are deterministic, cheaper, and often more reliable for specific tasks.

Design for modularity — build so you can swap models, change prompts, and add guardrails without rewriting everything.

</details>

## Section 5 — Human Annotation & Process

*Hands-on in [Week 2 — Designing Reliable LLM Judges](../week-02-designing-reliable-llm-judges/)*

<details>
<summary><strong>How many people should annotate my LLM outputs?</strong></summary>

For most small to medium-sized companies: one domain expert as a "benevolent dictator." This person becomes the definitive voice on quality standards — a psychologist for a mental health chatbot, a lawyer for legal document analysis, a customer service director for support automation.

Why one person works:

Eliminates annotation conflicts and paralysis from "too many cooks."

Builds deep product intuition that external annotators cannot replicate.

If you feel you need five subject matter experts to judge a single interaction, it is a sign your product scope is too broad.

When to use multiple annotators: larger organizations or those operating across multiple domains (multinational companies with different cultural contexts). When you do, measure agreement using Cohen's Kappa (accounts for agreement beyond chance).

</details>

<details>
<summary><strong>Should PMs and engineers collaborate on error analysis?</strong></summary>

Yes — especially at the outset. Engineers catch technical issues (retrieval failures, tool errors, latency). PMs identify product failures (unmet user expectations, confusing responses, missing features users expect).

Over time, lean toward a single benevolent dictator — typically a domain expert or PM who understands user needs best. Empower non-technical reviewers with custom annotation tools that show system outcomes alongside traces. Ask "Has the appointment been made?" not "Did the tool call succeed?"

</details>

<details>
<summary><strong>Should I outsource annotation and labeling to a third party?</strong></summary>

Outsourcing error analysis is usually a significant mistake. You break the feedback loop between observing a failure and understanding how to improve the product.

The dangers of outsourcing:

Superficial labeling — even well-defined metrics require nuanced judgment that external teams lack.

Loss of unspoken knowledge — a principal domain expert's tacit knowledge cannot be fully captured in a rubric.

Annotation conflicts — external annotators often create more disagreement, not less, without shared product context.

Acceptable exceptions for external help:

Purely mechanical tasks — objective, unambiguous tasks like validating an email format (after an internal rubric is defined).

Tasks without product context — e.g., linguistic translation that requires expertise but not product knowledge.

Hiring SMEs as internal domain experts — this is not outsourcing; it is bringing necessary expertise in.

</details>

<details>
<summary><strong>What parts of evals can be automated with LLMs?</strong></summary>

LLMs can accelerate parts of your eval workflow when used with human oversight:

First-pass axial coding — after you have open-coded 30-50 traces yourself, use an LLM to organize your notes into proposed failure categories. Always review and refine.

Mapping annotations to failure modes — given a new trace annotation and your established failure taxonomy, suggest applicable categories.

Suggesting prompt improvements — have the LLM propose changes based on your open coding notes. Review before adopting.

Analyzing annotation data — surface patterns such as "lag complaints increase 3x during peak hours."

What you should never outsource to an LLM:

Initial open coding — always read raw traces yourself first. This is how you discover new failure types and build product intuition.

Validating failure taxonomies — LLM-generated groupings need your review to avoid category conflation.

Ground truth labeling — any data used to validate LLM-as-Judge evaluators must be hand-validated.

Root cause analysis — only human review catches patterns tied to specific workflows or edge cases.

</details>

<details>
<summary><strong>Should I stop writing prompts manually in favor of automated prompt optimization tools?</strong></summary>

Be skeptical of automated prompt tools, especially early in development. When you write a prompt, you are forced to clarify your own assumptions and externalize your requirements. Delegating this too early means you never fully understand your own product.

Automated prompt optimization hill-climbs a predefined metric — it can refine a prompt against known failures but cannot discover new ones. Research also shows that evaluation criteria shift after reviewing model outputs ("criteria drift") — evaluation is an iterative, human-driven process, not a static target.

The pragmatic approach: use LLMs to improve prompts based on your open coding notes (human in the loop looking at data). Once you have high-quality evals, prompt optimization can be effective for that last mile.

</details>

## Section 6 — Guardrails, Trust & Safety

*Hands-on in [Week 3 — Safety and Adversarial Testing](../week-03-safety-and-adversarial-testing/)*

<details>
<summary><strong>What are guardrails in LLM applications and how do I implement them?</strong></summary>

Guardrails are programmatic checks run before or after an LLM call. Two placement options:

Input guardrails (before the LLM) — prompt injection detection, PII filtering, scope validation, topic restriction.

Output guardrails (after the LLM) — hallucination detection/groundedness checks, format validation, sensitive information filtering.

Guardrail types, from cheapest to most expensive:

Static filters — regex, blocklists, bloom filter matching. Fast and cheap but brittle. Can be bypassed by simple rephrasing.

Algorithmic guardrails — classifiers (e.g., Llama Guard), LLM-as-judge evaluators. More nuanced but add latency and cost, and have their own failure modes that need evaluation.

Alignment-based guardrails — RLHF, constitutional AI. Shapes model behavior at training time. Most robust, least transparent.

Effective systems layer all three. The cheapest guardrail is a well-written system prompt — many production systems start with pages of behavioral constraints.

</details>

| Make guardrails modular: Build them so they can be ripped out and replaced. Your guardrail needs will evolve as your product evolves, models improve, and you discover new failure modes. |
| --- |

<details>
<summary><strong>What is the difference between guardrails and evaluators?</strong></summary>

These concepts overlap but serve different purposes in the lifecycle:

Guardrails are real-time, blocking checks. They run during inference and can prevent a bad response from reaching the user. Latency impact is a concern.

Evaluators are retrospective quality assessments. They run offline (development, CI) or asynchronously (production monitoring) on captured traces. No latency impact.

An evaluator can become a guardrail — once an LLM-as-Judge reaches sufficient accuracy and speed, you can move it inline to block bad outputs. However, the cost and latency of this must be justified by the risk.

</details>

<details>
<summary><strong>Can evaluators also be used to automatically fix or correct outputs in production?</strong></summary>

Yes — this is the "evaluator-optimizer" pattern. An evaluator judges an output, and if it fails, a correction loop triggers. Use with caution:

Self-correction works well for well-defined failures (format errors, missing required fields) but is unreliable for complex semantic failures.

Recursive loops are a risk — always set a maximum retry count. Unconstrained self-correction loops can be expensive and still produce wrong outputs.

Always log correction events — these are high-signal traces for error analysis and should be prioritized for human review.

</details>

<details>
<summary><strong>"Guardrails" means different things to different stakeholders — how do I bridge the gap?</strong></summary>

When engineers say "guardrails" they mean input/output validation checks. When executives ask "do we have guardrails in place?", they are asking about compliance, risk appetite, accountability, and fallback plans.

PM action: create a guardrail framework that addresses both:

Technical layer — the actual input/output checks implemented in the system.

Process layer — human review workflows for flagged interactions, escalation paths, incident response.

Governance layer — policies, risk acceptance criteria, audit logging, compliance evidence.

<details>
<summary><strong>How do I decide how much human-in-the-loop my agent needs?</strong></summary>

The principle is closed-loop human control. Responsible agents do not require a person to approve every action — that would not scale — but people must remain in control in three ways.

Authorize. A human defines the agent's mission, its permissions, and its boundaries. Nothing the agent does should surprise the person who authorized it.

Observe. People can see what the agent did, what tools and data it used, and why it made a recommendation or took an action. Observability is what makes the other two possible.

Correct. They can pause it, override it, reverse an action where possible, and use failures to improve the system. Every correction should feed the eval set.

In practice, the line is drawn by impact:

Allow autonomy for low-impact, well-scoped, visible, reversible work. A Pronto agent refunding $18.40 on a moldy-strawberry claim with a photo on file needs no human.

Require approval when money, permissions, customer commitments, or irreversible changes are involved. The $50 refund cap, issuing account credit, or changing a delivery address — a human signs off.

And if the agent is outside its mandate, uncertain, or cannot explain its intended action, it should stop and escalate. "I don't know" is a valid and safe output; guessing is not.

Calibrate over time: start strict, then widen autonomy as the evals prove each task type safe. The approval boundary is a living policy, tightened or loosened by evidence — not set once and forgotten.

</details>

## Section 7 — Context Engineering & RAG Evaluation

*Hands-on in [Week 4 — RAG Evaluation](../week-04-rag-evaluation/)*

<details>
<summary><strong>When should I use Retrieval/RAG vs. Context Engineering — are these competing approaches?</strong></summary>

No — they operate at different levels. Context engineering is the broader discipline; RAG is one technique within it.

Context engineering — the art and science of curating the optimal set of tokens for the LLM at inference time. Every production system does context engineering whether it knows it or not.

RAG (Retrieval-Augmented Generation) — one specific technique for context engineering that dynamically retrieves relevant information from external sources and adds it to the context.

Why you cannot just dump everything into long context:

Context rot is real — as input length increases, model performance degrades significantly, down to ~50% accuracy at 10,000 tokens for several simple tasks, even for frontier models claiming million-token contexts.

Cost — sending more tokens than necessary costs money. RAG evaluations running at scale can be among the largest cost drivers.

Practical threshold — if your entire corpus fits in ~100k tokens, consider full-context injection. Beyond that, retrieval remains essential.

</details>

| Best practice: Start with hybrid search — combining lexical search (BM25) with semantic vector search. Their strengths and weaknesses are complementary, delivering better recall and precision out of the box. |
| --- |

<details>
<summary><strong>Is RAG dead with the rise of long-context models?</strong></summary>

No. While long-context models reduce the need for retrieval in some scenarios, RAG remains essential for:

Corpora larger than even the largest context windows.

Freshness — retrieval allows access to documents updated after model training.

Cost efficiency — retrieving only relevant chunks is far cheaper than full-corpus injection.

Attribution and explainability — retrieved sources provide a natural audit trail.

The evolution is toward agentic RAG — the model decides when and how to search rather than retrieval being pre-baked into the application layer. The retrieval is not going away; it is moving into the model's decision loop.

</details>

<details>
<summary><strong>How should I approach evaluating my RAG system?</strong></summary>

RAG systems have two evaluation surfaces that require different approaches:

Retrieval evaluation:

Retrieval precision — are retrieved chunks relevant to the query?

Retrieval recall — are all important chunks being retrieved?

Chunk hit rate — what percentage of answers can be found in the top-k chunks?

Similarity metrics are appropriate here — cosine similarity between query and chunk embeddings is a valid optimization signal for retrieval.

Generation evaluation (given the retrieved context):

Groundedness — is the response factually supported by the retrieved context? (LLM-as-Judge)

Answer relevance — does the response actually address the user's question? (LLM-as-Judge)

Context utilization — is the retrieved context being appropriately used vs. ignored?

Frameworks like RAGAs provide pre-built metrics for RAG evaluation, though these should be validated against your specific use case rather than used blindly.

</details>

<details>
<summary><strong>How do I choose the right chunk size for my document processing tasks?</strong></summary>

Chunk size is an empirical question — evaluate it with your actual data and queries, not theoretical defaults.

Small chunks (128-256 tokens) — better retrieval precision, worse context for generation (may lack surrounding context).

Large chunks (512-1024 tokens) — more context for generation, worse retrieval precision (dilutes relevance signals).

Semantic chunking — split on natural document boundaries (paragraphs, sections) rather than fixed token counts. Often outperforms fixed-size chunking.

Run retrieval evaluation (chunk hit rate, precision) across different chunk sizes on a representative sample of your actual queries to find the optimal setting for your use case.

</details>

## Section 8 — Multi-Agent & Agentic Workflow Evaluation

*Hands-on in [Week 5 — Multi Agent Evaluation](../week-05-multi-agent-evaluation/)*

<details>
<summary><strong>How do I evaluate agentic workflows?</strong></summary>

Agentic workflows are significantly harder to evaluate than single-turn LLM calls because failures can occur at any step and cascade through subsequent steps.

Key principles:

Evaluate outcomes, not just outputs — ask "Did the task get completed correctly?" not "Was each individual LLM call good?"

Trace-level evaluation — evaluate the complete trace as a unit, not just the final response.

Focus on the first failure — upstream errors cause downstream problems. Identify and fix root causes, not symptoms.

Measure task completion rate — what percentage of agent sessions achieve the intended goal?

Measure efficiency — how many steps/tokens did the agent take? Optimal agents complete tasks in fewer steps.

Types of agentic failure modes to evaluate:

Tool misuse — calling the wrong tool, wrong parameters, or calling tools unnecessarily.

Goal drift — agent pursuing a sub-goal that diverges from the user's original intent.

Context loss — losing track of important constraints or context across a long multi-turn session.

Infinite loops — agent repeatedly attempting the same failing action.

Premature termination — agent stopping before the task is complete.

</details>

<details>
<summary><strong>How do I evaluate complex multi-step workflows?</strong></summary>

Decompose evaluation by step. For each significant step in your workflow:

Define success criteria for that specific step independently.

Create targeted test cases that isolate that step.

Build step-level evaluators before building end-to-end evaluators.

Also use intermediate checkpoints. Rather than only evaluating the final output, evaluate the quality of decisions made at key branch points. This localizes failures much faster than end-to-end evaluation alone.

</details>

<details>
<summary><strong>How do I evaluate multi-agent systems?</strong></summary>

Multi-agent evaluation requires understanding both individual agent behavior and system-level coordination. Additional considerations beyond single-agent eval:

Inter-agent communication quality — are agents passing the right information to each other?

Task delegation correctness — is the orchestrator sending tasks to the most appropriate sub-agent?

Context propagation — is relevant context preserved as tasks move across agents?

Error propagation — when one agent fails, how does that affect downstream agents?

End-to-end latency and cost — multi-agent systems can multiply token costs. Track at system level.

Distributed tracing (see Section 2) is essential — without it, you cannot isolate which agent or which step caused a system-level failure.

</details>

<details>
<summary><strong>How do I debug multi-turn conversation traces?</strong></summary>

Multi-turn traces require different debugging approaches than single-turn evaluation:

Focus on the first failure — errors compound. Find the earliest point in the conversation where behavior diverges from expectations.

Context window inspection — check what context was available to the model at each turn. Context rot or truncation is a common cause of multi-turn failures.

State reconstruction — verify that the agent correctly tracked user intent, prior decisions, and task state across turns.

Tool call sequence — review the full sequence of tool calls across the session to identify incorrect ordering or redundant calls.

</details>

<details>
<summary><strong>How do I evaluate sessions with human handoffs?</strong></summary>

Human handoff evaluation requires measuring both the quality of the agent's work before handoff and the appropriateness of the handoff decision itself:

Handoff precision — did the agent hand off to a human at the right moments (neither too early/often nor too late)?

Handoff summary quality — did the agent provide the human with sufficient context to continue effectively?

Deflection rate — what percentage of conversations the agent handles without escalation, as a business efficiency metric.

Post-handoff resolution rate — do conversations handed off to humans actually get resolved? If not, the agent may be handing off for the wrong reasons.

</details>

<details>
<summary><strong>How do I evaluate voice agents?</strong></summary>

Voice agents introduce additional evaluation dimensions beyond text-based agents:

Speech-to-text quality — transcription accuracy, especially for domain-specific terminology, accents, and noisy environments.

Latency perception — voice interactions have strict latency requirements (typically &lt;500ms for natural conversation). Measure time-to-first-token and end-to-end latency separately.

Interruption handling — does the agent gracefully handle users interrupting mid-response?

Prosody and naturalness — does the text-to-speech output sound natural in context?

Multimodal trace alignment — align transcriptions, model outputs, and tool calls in a unified trace to debug misinterpretations.

Voice agent observability platforms (Arize, Langfuse, Maxim) now support multimodal tracing that unifies these signals into a single trace view.

</details>

## Section 9 — Production Monitoring & Observability Operations

*Hands-on in [Week 6 — Production Eval Infrastructure](../week-06-production-eval-infrastructure/)*

<details>
<summary><strong>How are evaluations used differently in CI/CD vs. monitoring production?</strong></summary>

CI/CD (pre-deployment) — evaluations run against a curated test dataset before every deployment. Goal: catch regressions before they reach users. Use the same evaluation harness as development — do not build a separate pipeline.

Production monitoring (post-deployment) — continuous evaluation of live traffic. Goal: surface new failure modes, monitor quality drift, and trigger alerts. Uses sampling strategies since evaluating 100% of traffic is cost-prohibitive.

The key principle: your dev tests and production evals should be the same system. Same tests, same data format, same pass rate tracking. Production traces feed new test cases back into development — this closes the feedback loop.

</details>

<details>
<summary><strong>What metrics should I monitor in production for AI agents?</strong></summary>

Organize production metrics across four dimensions:

Quality metrics:

Task completion rate — % of sessions where the agent achieves the user's goal.

LLM-as-Judge scores — automated quality scores from your custom evaluators, tracked over time.

Human feedback signals — thumbs up/down rates, satisfaction scores, escalation rates.

Performance metrics:

End-to-end latency — time from user input to final response, by percentile (p50, p95, p99).

Time-to-first-token — critical for streaming and voice experiences.

Tool call success rate — % of tool calls that execute successfully.

Cost metrics:

Tokens per session — input and output tokens, by session type, user segment, and feature.

Cost per successful task completion — the unit economics of your agent.

Cost attribution by agent/tool/step — identify the most expensive components for optimization.

Safety and compliance metrics:

Guardrail trigger rate — how often are input/output guardrails being triggered?

Hallucination rate — % of responses containing ungrounded factual claims.

Policy violation rate — % of responses violating defined behavioral policies.

</details>

<details>
<summary><strong>How do I set up alerts and thresholds for agent monitoring?</strong></summary>

Start with threshold-based alerts on your most critical metrics (task completion rate, latency p99, error rate).

Set baselines from your first 2-4 weeks of production data before configuring regression alerts.

Alert on relative change (20% degradation from baseline) rather than absolute thresholds only — this catches regressions as your baseline improves.

Route alerts to appropriate channels — latency to on-call engineers, quality degradation to PM + engineering, cost spikes to finance + engineering.

Integrate with your incident management workflow (PagerDuty, OpsGenie, Slack) through your observability platform.

</details>

<details>
<summary><strong>How do I manage agent cost in production?</strong></summary>

Uncontrolled agent cost is one of the most common production surprises. Key practices:

Attribute cost at the trace level — every session/trace should have a cost tag so you can identify expensive conversation patterns.

Set per-session cost budgets — agents should have hard token limits per session that trigger graceful termination.

Identify and optimize expensive patterns — certain query types or workflows may consume 10x more tokens than average. Find them through cost-sorted trace analysis.

Model routing — route simple queries to smaller, cheaper models; reserve large frontier models for complex tasks. Requires a task complexity classifier.

Prompt optimization — run automated prompt compression for repetitive system prompt content that does not change between turns.

Context management strategies — reduce, offload, and isolate context (see Section 2 on context engineering) to prevent token bloat in long sessions.

<details>
<summary><strong>What does it cost to run AI evals, and how do I make it cheaper?</strong></summary>

Four things cost money, in descending order: LLM-judge calls (almost always the biggest line item), human annotation for gold sets, compute/CI time to run suites, and one-time dataset creation.

Illustrative numbers (rough — they move with model pricing): a GPT-4o-class judge runs about $2.50 per 1,000 judgments. A 100-case suite scored on 4 criteria costs on the order of $0.40 with a flash-class judge versus ~$6 with a frontier-class judge. Human annotation runs $50–125 per 1,000 labels — 20–50× the judge. A 200-case suite on every PR at mini-class pricing is roughly $4 a run, or ~$160/month at 10 PRs a week. Compare that to one bad deploy.

Six levers to bring it down:

Judge with small models. A mini/flash-class judge is 10–30× cheaper and perfectly good for binary pass/fail rubrics. Reserve frontier judges for calibrating the small ones, not for every run.

Deterministic checks first — they're free. Code assertions (valid JSON, correct order ID format, refund ≤ $50) run before any LLM call and catch a large share of failures at $0.

Tiered evals. Cheap filters gate expensive judges: only the cases the cheap checks can't decide reach the costly judge.

Cache judgments. Content-address judgments and commit them — CI re-scores from disk at $0 until you deliberately re-pin the judge.

Sample, don't exhaust. A representative 100–500 cases per PR, the full suite nightly. Cost scales linearly with cases × judges, so sampling is the fastest win.

Track tokens per point of gain on the outer loop. If the optimizer loop itself becomes your biggest line item, you're paying more to measure than to improve.

</details>

<details>
<summary><strong>What are the top agent observability platforms and how should I choose?</strong></summary>

The observability tooling landscape is consolidating rapidly around OpenTelemetry. Key platforms:

Langfuse — open-source, OTEL-compatible, strong prompt management and human annotation. Good for teams wanting full data control (self-hosted option).

LangSmith — tight LangChain/LangGraph integration, strong debugging and eval workflows. Best for teams already on LangChain.

Arize / Phoenix — enterprise-grade ML observability with strong drift detection, visualization, and MCP tracing support.

Maxim AI — end-to-end platform combining simulation, evaluation, and real-time observability with multi-agent support.

Braintrust — strong eval and prompt management capabilities with production logging.

How to choose:

Prioritize OTEL compatibility — ensures you are not locked in and can switch backends as the market evolves.

Evaluate integration with your existing stack — CI/CD, alerting, data platforms.

Prefer tools that let you bring your own evals rather than requiring you to use their pre-built metrics.

Consider your team's build vs. buy tolerance — open-source tools require operational overhead but give full control.

</details>

<details>
<summary><strong>How should I version and manage prompts?</strong></summary>

Treat prompts like code — store in version control (Git), with diffs, commit messages, and review workflows.

Tag prompt versions to eval results — when you update a prompt, record which version produced which quality metrics.

Maintain a staging/production split — test prompt changes in a non-production environment against your eval suite before deploying.

Never change a prompt and a model simultaneously — you will not know which change caused a quality shift.

Log the prompt version alongside every production trace — essential for debugging regressions introduced by prompt changes.

</details>

## Section 10 — Observability in Practice: Answering Operational Questions

*Hands-on in [Week 6 — Production Eval Infrastructure](../week-06-production-eval-infrastructure/)*

<details>
<summary><strong>"Why did this agent escalate to a human?"</strong></summary>

This is the most common question after a human handoff spike — and one of the hardest to answer without proper instrumentation. Escalation reasons are rarely stored explicitly; they must be inferred from trace data.

What your observability stack needs to answer this:

Escalation trigger logging — capture the specific condition that fired the handoff: confidence threshold crossed, intent unrecognized, explicit user request, policy rule triggered, or consecutive failed turns.

Session-level intent tracking — record what the user originally wanted and whether it was resolved before escalation.

Step-level failure tagging — tag which tool call, retrieval step, or reasoning step immediately preceded the escalation decision.

Escalation classification — use an LLM judge or rule-based classifier to auto-tag escalation reasons into a fixed taxonomy (e.g., out-of-scope, low-confidence, policy block, user frustration).

Once you have this data, track escalation reason distribution weekly. A sudden spike in one category (e.g., "intent unrecognized") is a direct signal to retrain your intent classifier or expand your knowledge base.

</details>

| PM action: Define your escalation reason taxonomy before launch. Retrofitting this taxonomy onto historical logs is possible but painful. Instrument it upfront. |
| --- |

<details>
<summary><strong>"Which agents have the highest hallucination rate this week?"</strong></summary>

Answering this requires both a hallucination detector (an eval/guardrail) and per-agent attribution in your telemetry. Without both, you can see overall hallucination rates but not isolate which agent is the source.

How to build this:

Deploy a groundedness evaluator — an LLM-as-Judge that checks whether each factual claim in the agent's response is supported by retrieved context or known facts. Run this asynchronously on a sample of production traces.

Tag every trace with its source agent — in multi-agent systems, each span should carry an agent_id attribute so hallucination events can be grouped by agent.

Build a weekly leaderboard view — a simple aggregation query over your telemetry store: COUNT(hallucination_flagged) / COUNT(total_responses) GROUP BY agent_id, week. Sort descending.

Set alert thresholds per agent — not all agents have equal hallucination risk. A retrieval-heavy research agent has different acceptable thresholds than a simple FAQ bot.

Typical root causes when one agent spikes: stale knowledge base (retrieval source not updated), prompt change that reduced grounding instructions, new query type outside training distribution, or context truncation causing the agent to fabricate rather than admit uncertainty.

</details>

<details>
<summary><strong>"What changed between Tuesday (fine) and Wednesday (broken)?"</strong></summary>

This is the incident investigation question — and it requires a change log correlated with your telemetry timeline. Most teams cannot answer this because changes are not version-tagged in their traces.

What you need in your observability infrastructure:

Prompt version tagging — every trace should carry the prompt version deployed at that time. When Wednesday's traces show a quality drop, you can immediately check if a prompt changed Tuesday night.

Model version logging — log the exact model identifier (including version/snapshot) used for each LLM call. Model providers silently update models; this is a common hidden cause of regressions.

Deployment event markers — overlay deployment events on your time-series quality charts. A vertical line at Tuesday 11pm + a quality drop starting Wednesday 8am = a strong hypothesis.

Knowledge base change log — if your RAG system's document corpus was updated, log that as a versioned event. Stale or incorrect documents are a frequent Wednesday culprit.

Diff view between trace populations — for Tuesday's traces vs. Wednesday's traces: what changed in input distributions, tool call patterns, response lengths? Your observability platform should support this comparison.

</details>

| The golden rule: Never change the model AND the prompt in the same deployment. When something breaks, you cannot isolate the cause. One change at a time, always. |
| --- |

<details>
<summary><strong>"How much did this agent cost per resolved case?"</strong></summary>

Cost-per-outcome is the unit economics metric of AI agents — and almost no team tracks it correctly out of the box. Most teams track token cost per API call; very few track cost per successful business outcome.

The formula: Cost per resolved case = (Total token cost for session) / (Sessions with successful resolution flag)

Building this requires:

Token cost attribution at the session level — sum all LLM call costs within a session (input tokens × price + output tokens × price, across all models used). Store this on the session record.

Resolution outcome tagging — define what "resolved" means for your use case (ticket closed without escalation, form submitted, confirmation sent) and tag sessions accordingly. This is business logic, not something your LLM framework does automatically.

Tool call cost inclusion — if your agent calls external APIs (search, CRM, databases) that have per-call costs, include those in the total session cost.

Segment by case type — cost per resolved case varies dramatically by case complexity. A billing dispute costs 10x more than a password reset. Tracking blended cost hides this.

Once you have cost-per-resolved-case by case type, you can make ROI conversations with finance and leadership concrete: "Our agent handles 8,000 password resets/month at $0.04/case = $320/month vs. $12,000 for human agents."

</details>

<details>
<summary><strong>"Show sessions where the customer was angry after agent interaction."</strong></summary>

Sentiment detection after interactions is one of the highest-signal inputs for identifying agent failure modes that formal evals miss — because users express frustration in natural language, not structured feedback.

Implementation approaches (pick based on your latency and cost tolerance):

Post-interaction sentiment classifier — run a lightweight sentiment model (or LLM-as-Judge prompt) on the last 2-3 user messages in a session. Flag sessions where final sentiment is negative or declining. Run asynchronously, not inline.

Frustration signal detection — train a classifier on known frustration signals: repeated rephrasing of the same question, explicit statements ("this is useless", "let me talk to a human"), short clipped responses after longer previous messages.

Post-session CSAT correlation — if you collect CSAT scores, build a training set correlating trace features with low scores. Use this to predict dissatisfied sessions without waiting for explicit feedback.

Filter and surface in your annotation tool — the primary use of this flag is to create a high-priority review queue. Annotators should see angry-customer sessions first, as they are disproportionately likely to reveal real failure modes.

</details>

| Important distinction: Customers can be angry for reasons unrelated to the agent (pre-existing frustration, situation complexity). Always distinguish between anger directed AT the agent vs. anger present in the session context. An LLM judge can make this distinction; a simple sentiment score cannot. |
| --- |

<details>
<summary><strong>"Did this agent comply with our data handling policy?"</strong></summary>

Compliance checking is a governance question that requires both technical instrumentation and policy-as-code. It is increasingly critical as enterprise AI deployments face regulatory scrutiny (GDPR, HIPAA, EU AI Act, SOC 2).

What compliance observability looks like in practice:

Policy-as-code evaluators — translate your data handling policies into explicit LLM-as-Judge prompts or rule-based checks. Examples: "Did the agent ever repeat PII back to the user that was not provided in this session?", "Did the agent cite sources for medical claims?", "Did the agent avoid storing or repeating payment card information?"

Automated compliance scoring — run policy evaluators on a sample of production traces and report a compliance rate per policy rule. This gives you an auditable compliance signal without reviewing every interaction.

Audit trail completeness — for regulated industries, every agent action must be logged with sufficient context to reconstruct what happened, why, and what data was accessed. OTel-based distributed tracing is the foundation for this.

Policy violation alerting — high-severity policy violations (PII leakage, unauthorized data access) should trigger immediate alerts and session termination, not just logging.

Governance dashboard — create a weekly summary: compliance rate by policy rule, trend over time, incidents requiring human review. This is what your legal and compliance teams need, not raw traces.

</details>

| For enterprise deployments: Compliance is not a feature you add later. Define your policy rules, build the evaluators, and instrument for audit logging from day one. Retrofitting compliance evidence after the fact is extraordinarily expensive — and in some regulatory frameworks, insufficient. |
| --- |

<details>
<summary><strong>"Which retrieval sources are causing the most hallucinations?"</strong></summary>

This is the RAG quality debugging question — and it is one of the most actionable investigations you can run, because the fix is often adding, removing, or updating specific documents rather than changing the model or prompt.

How to build source-level hallucination attribution:

Source tagging in traces — every RAG retrieval step should log which document chunks were retrieved and their source identifiers (document ID, URL, knowledge base name, last-updated timestamp).

Hallucination events linked to retrieval context — when your groundedness evaluator flags a hallucination, log which retrieved chunks were in context at that time. This creates a hallucination-to-source linkage.

Source hallucination rate aggregation — GROUP BY source_document: hallucination_rate = hallucinations_when_source_in_context / total_retrievals_of_source. Sources with high rates are your primary investigation targets.

Root cause categories for high-hallucination sources: outdated document (fact was true when indexed, now false), contradictory documents (two sources say different things), low-relevance retrieval (document retrieved but not actually useful), or document format issues (poorly structured content that confuses the model).

This analysis often reveals that 80% of hallucinations trace back to 5-10% of documents. Fixing or removing those documents is faster and cheaper than model-level interventions.

</details>

<details>
<summary><strong>"Compare success rates across agent versions after last deployment."</strong></summary>

Version comparison is the core A/B analysis for agents — the equivalent of a feature flag rollout analysis in traditional software. It requires version-tagged telemetry and a clear success metric definition.

The three-step process:

Step 1 — Define success unambiguously before deployment: task completion rate, resolution without escalation, user satisfaction score, cost per resolved case. "Success" that is defined after the fact is subject to selection bias.

Step 2 — Tag every session with agent version: your deployment must write an agent_version attribute onto every trace. Without this, you cannot separate v1 traffic from v2 traffic in your analysis.

Step 3 — Compare distributions, not just means: v2 might have a higher mean success rate but a heavier tail of catastrophic failures. Compare the full distribution: p50, p90, p99, and the worst-case outcomes.

Common pitfalls in version comparison:

Traffic mix differences — if v2 launched Tuesday and Tuesday has lower traffic volume than Wednesday, the version comparison is confounded. Normalize for time-of-day and day-of-week.

Self-fulfilling improvement — if the team is monitoring v2 more closely post-launch, manual interventions can inflate success rates. Use only automated metrics for the official comparison.

Insufficient sample size — for low-volume agents, wait until you have statistical significance before declaring v2 better. A 5% improvement on 50 sessions is noise.

</details>

| PM action: Define your primary and secondary success metrics in the deployment ticket, before the deploy. Post-hoc metric selection is a fast path to misleading yourself. |
| --- |

<details>
<summary><strong>"What was the full customer journey from agent to human to resolution?"</strong></summary>

End-to-end journey reconstruction is the highest-complexity observability query — and the one most enterprise customers demand for support quality reviews, escalation analysis, and agent ROI measurement.

This requires stitching together multiple systems into a unified session view:

Unified session ID — a single session_id that persists across the AI agent interaction, the human handoff event, the CRM ticket, and the post-resolution confirmation. This ID is the thread that lets you reconstruct the full journey.

Handoff payload logging — when the agent hands off to a human, log the full context snapshot: conversation history, extracted intent, attempted solutions, confidence scores. This is what the human agent needs and what post-incident analysis requires.

Human interaction duration and outcome — connect your contact center or ticketing system data to your session telemetry. How long did the human interaction take? What was the resolution? Was it escalated further?

Time-to-resolution by journey type — calculate total time-to-resolution for: agent-only resolved, agent-then-human-resolved, and human-only. This comparison is the core ROI metric for your agent.

Customer effort score — the full journey view lets you calculate how many steps (agent turns + handoff + human turns) the customer had to take to reach resolution. Lower is better.

Infrastructure requirements:

Cross-system trace propagation — your OTel trace context must flow from the AI agent into whatever system the human agent uses (ServiceNow, Zendesk, Salesforce, etc.). This requires integration work but is the only way to get true end-to-end visibility.

Data retention alignment — your AI telemetry and your CRM/ticketing data must have compatible retention policies so they can be joined for analysis.

</details>

| This is hard, and that is intentional: If answering this question is easy, it usually means you are missing data somewhere. Full journey reconstruction across AI + human systems is genuinely complex — budget accordingly and treat it as a 1-2 quarter infrastructure investment. |
| --- |

## Section 11 — Tools, Frameworks & Infrastructure

<details>
<summary><strong>Should I build a custom annotation tool or use something off-the-shelf?</strong></summary>

Build a custom annotation tool. This is the single most impactful investment you can make for your eval workflow. With AI-assisted development tools (Cursor, Lovable), you can build a tailored interface in hours. Teams with custom annotation tools typically iterate ~10x faster.

What custom tools enable:

All context from multiple systems in one place — traces, tool results, business outcomes, database state.

Product-specific rendering — images, widgets, markdown, buttons tailored to your domain.

Custom filtering, sorting, and progress tracking for your specific review workflow.

Keyboard shortcuts and bulk operations that dramatically increase annotation throughput.

Off-the-shelf tools may be justified when you need to coordinate dozens of distributed annotators with enterprise access controls. Even then, many teams find the configuration overhead and limitations not worth it.

</details>

<details>
<summary><strong>How do I choose which AI frameworks and tools to adopt?</strong></summary>

Start with vanilla API calls — understand what your system actually does before adding abstraction.

Only adopt a framework when it solves a specific pain point you have already experienced — premature framework adoption is the fastest path to proof-of-concept purgatory.

Choose frameworks that abstract away code you do not want to write — not frameworks that abstract away what you need to see (e.g., your prompts).

The pattern: teams adopt a framework quickly, ship something, then 6-12 months later rebuild from API calls with a real understanding of what they need.

Prioritize observability above framework features — being able to see what your system is doing is more important than which framework orchestrates it.

</details>

<details>
<summary><strong>What gaps in eval tooling should I be prepared to fill myself?</strong></summary>

Domain-specific evaluation criteria — no tool knows your business logic. Custom evaluators for your specific failure modes will always need to be built internally.

Business outcome tracking — connecting LLM quality metrics to actual business results (revenue, retention, task completion) requires custom instrumentation.

Multi-system context in annotation views — stitching together traces with CRM data, support tickets, and downstream outcomes for complete context.

Cost attribution — connecting token usage to features, users, and business value.

Continuous improvement pipeline — the loop from production traces → error analysis → eval updates → prompt changes → deployment needs custom orchestration.

</details>

<details>
<summary><strong>How much time should I spend on model selection?</strong></summary>

Less than most teams think. The best model for your use case cannot be determined from general benchmarks — it must be evaluated on your specific data and tasks. Focus on building your eval infrastructure first; model selection falls out naturally from running your evals across candidate models.

Practical guidance:

Start with the most capable models available to establish quality baselines. Optimize for cost later.

Evaluate on your actual eval dataset, not published benchmarks.

Build for modularity — make it easy to swap models without rewriting your system.

Consider the total cost: model price + latency + eval maintenance overhead.

</details>

## Section 12 — Continuous Improvement & Fine-tuning

*Hands-on in [Week 6 — Production Eval Infrastructure](../week-06-production-eval-infrastructure/)*

<details>
<summary><strong>How do I build a continuous improvement loop for AI agents?</strong></summary>

The continuous improvement loop is the flywheel that separates great AI products from stagnant ones. The core cycle:

Production traces → Error analysis → Failure taxonomy updated → New eval cases added → Prompts/code/models updated → Deployed → Back to traces.

Key enablers:

Robust observability — you cannot improve what you cannot see. Session-level telemetry is the raw material for the loop.

Fast eval turnaround — your eval suite should run in minutes, not hours. Slow evals kill iteration velocity.

Shared ownership — PMs own failure prioritization, engineers own fix implementation, domain experts own quality criteria. All three must be in the loop.

Experiment tracking — count experiments, not features. Track what changed, what you expected, and what actually happened.

Feedback flywheel — route production failures directly into your eval dataset. Every user complaint is a potential test case.

<details>
<summary><strong>How do enterprises define units of work and evaluate task completion to build a self-improving agent harness?</strong></summary>

Start with the unit of work. A "task" is one user goal with a verifiable completion condition — "resolve the refund request," not "reply to the message." Enterprises build a task taxonomy per workflow where each task type gets three things: binary completion criteria (done / not done), a quality rubric (outcome, trajectory, experience, governance), and cost/latency budgets. Task completion is judged against that contract — never vibes. This is the same rubric discipline from the course, applied as the definition of done.

The self-improving harness is the eval flywheel grown up. The loop: production runs → structured traces → weakness mining (cluster the failing traces) → a bounded proposal (a prompt edit, new few-shot examples, a memory or tool-config change — never an unbounded rewrite) → validation through the eval gate (offline eval, safety checks, regression set, cost/latency analysis) → canary or shadow on live traffic → promote or roll back. Then the new version generates new traces and the loop continues: experience → reflection → improvement → validation → learning.

Three things make this different from classic MLOps: the feedback signal is raw execution traces, not a scalar loss; the training signal is a verifier you build per goal, not a labeled dataset you already own; and you version config, not weights — so promotion is a safety event, and all the trust moves into the eval.

Four guardrails keep the loop safe. Keep a held-out gold set the optimizer never sees, or the loop Goodharts itself into looking better instead of being better. Use statistical gates (multiple samples), not single runs — non-determinism makes one-shot pass/fail lie. Contain the meta-agent: it must not expand autonomy, permissions, or budget without a human. And keep the previous version one config flip away — the rollback path is what makes the loop safe enough to run unattended.

In course terms: Week 1's flywheel is the loop, the Week 2 judge plus the Week 4 gold set are the verifier, and the Week 6 decision gate is the validation step. The eval suite is the asset that makes all of it trustworthy.

</details>

<details>
<summary><strong>When and how should I fine-tune models?</strong></summary>

Fine-tuning is a last resort, not a first option. Exhaust prompt engineering and RAG optimization before fine-tuning.

Fine-tuning makes sense when:

You have 500+ high-quality labeled examples of the target behavior.

The behavior cannot be reliably achieved through prompting alone (e.g., very specific output format, domain-specific tone).

Latency is a hard constraint — fine-tuned smaller models can match larger model quality for specific tasks.

Cost at scale — fine-tuning for high-volume repetitive tasks can significantly reduce API costs.

Fine-tuning is not the solution for:

Adding new knowledge — use RAG instead.

Patching prompt issues — fix the prompt first.

Fixing safety or alignment issues — fine-tuning for safety is complex and risky.

</details>

| Critical requirement: You need a high-quality eval suite BEFORE fine-tuning. Without it, you cannot know whether fine-tuning improved or degraded your system overall. |
| --- |

## Section 13 — PM Playbook: Quick Reference
