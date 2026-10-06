# Week 1 — Eval Foundations & Error Analysis

Why AI products need evals, the six quality dimensions, and the error-analysis
workflow that turns production failures into datasets.

## What we covered

- Production failure case studies: how AI products actually break in the wild
- Model benchmarks vs. product evals (benchmarks don't measure your product)
- Non-determinism and how to approach it
- Traditional QA vs. AI evals; evals as core infrastructure
- The six quality dimensions: model quality, product behavior, safety, reliability, cost, latency
- Cost metrics: per-task cost tracking, token and retry accounting
- Latency metrics: time-to-first-token, span timing, percentile tracking
- Eval harness architecture and pipeline components
- Built a real customer-service agent (`agent/`) with logging and observability
- Traces vs. logs; the error-analysis workflow; failure taxonomies
- Frequency-based prioritization
- The eval flywheel: deploy → analyze → build dataset → improve → monitor

## Key takeaways

1. **Benchmarks measure models; evals measure your product.** A high MMLU score tells you nothing about your agent's refund flow.
2. **You can't improve what you can't see.** Tracing every run is the prerequisite for everything else in this course.
3. **Fix by frequency, not by loudness.** Failure taxonomies with counts beat anecdote-driven debugging.
4. **The flywheel is the product.** Deploy → analyze → dataset → improve → monitor is a loop, not a phase.

## Links

- LangSmith docs — tracing, datasets, annotation: https://docs.langchain.com/langsmith
- LangSmith concepts (traces, spans, runs): https://docs.langchain.com/langsmith/observability-concepts

## Tool: Trace Viewer

**[Trace Viewer](https://coachmanjeet.github.io/AI-Agent-Evals-Course/trace-viewer/)** —
a static, in-browser OTel trace explorer built for this week's error-analysis
workflow. Upload any OTel trace JSON (OTLP `resourceSpans` or flat `spans`),
browse the span waterfall, inspect attributes/events, and annotate each trace
with a failure mode from the course taxonomy. Annotations auto-save in your
browser and export as JSON/CSV — the seed of the eval dataset you build in
later weeks. Ships with a 6-trace Pronto sample (5 failure modes + 1 clean
trace) so it works end-to-end with zero setup. No backend; nothing you upload
leaves your browser.

## In this folder

- `examples/` — worked examples from the live session (added after the session)
- `assignments/01-instrument-and-trace/` — wire up tracing, run 30 inputs, annotate traces
- `assignments/02-failure-taxonomy/` — cluster failures into codes, report top modes
