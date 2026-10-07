# AI Eval Skills

Agent skills that help you (and your AI coding agent) do the course's hands-on
work with fewer footguns. They come from the
[ai-evals-course/evals-skills](https://github.com/ai-evals-course/evals-skills)
repo — install once, then invoke by name in any agent that supports skills
(Claude Code, Codex, etc.).

## Install

```bash
# all nine skills
npx skills add https://github.com/ai-evals-course/evals-skills

# or just one
npx skills add https://github.com/ai-evals-course/evals-skills --skill error-discovery
```

Then ask your agent, e.g.: *"Can you help me do error analysis on
datasets/pronto-support-tickets.csv?"*

## The top 3 for this course

| # | Skill | Use it in | Why |
|---|-------|-----------|-----|
| 1 | `error-discovery` | Week 1 | Point it at your traces: it builds a review app, picks diverse samples, and organizes your notes into failure modes. This is Assignments 1–2 with scaffolding. The course rule stands: no evals before error analysis. |
| 2 | `write-judge-prompt` | Week 2 | Designs binary pass/fail LLM judges — one failure mode per judge. Enforces the judge anatomy the course teaches, and tells you to exhaust code-based checks first. |
| 3 | `validate-evaluator` | Week 2 | Calibrates your judge against human labels (TPR/TNR gating, bias correction). The rigorous version of the "validate on the 40-label set" assignment — uncalibrated judges are the silent killer. |

## Also useful

| Skill | Use it in | One-liner |
|-------|-----------|-----------|
| `ticket-to-eval` | Weeks 1, 4, 6 | **Course-native.** Turns one real Pronto ticket or trace into two dataset rows: a regression row (exact input, tagged with one of the 14 failure modes) and a generalized coverage row. Strips PII first. This is the Week 6 flywheel made concrete — production failures become tests. |
| `generate-synthetic-data` | Week 4 | Dimension-based synthetic input generation — compare its output against `datasets/generate_pronto_tickets.py`. Use when you need coverage the real world hasn't given you; use `ticket-to-eval` when production hands you real failures. |
| `evaluate-rag` | Week 4 | Retrieval vs. generation scoring for the RAG week. |
| `write-code-eval` | Weeks 1–2 | Code checks for objective failure modes — always try these before reaching for an LLM judge. |
| `evals-start` | Anytime | Entry point: describe your situation and it routes you to the right skill. |
| `eval-audit` | Week 6 | Audits an existing eval pipeline and prioritizes what's broken — a second opinion on your production harness. |

> **Why `ticket-to-eval` and not `error-discovery`?** `error-discovery` finds failure
> *patterns* across many traces (Week 1, Assignments 1–2). `ticket-to-eval` converts
> *one* ticket into dataset rows. Discovery first, conversion after — they compose,
> they don't compete.

## Pairs well with the AI Skills Lab

No agent CLI? Manjeet's [AI Skills Lab](https://coachmanjeet.github.io/AI-Skills-Lab/)
covers the same muscles with no installs — same ideas, two doors in:

| Agent skill (here) | Lab builder (no install) |
|--------------------|--------------------------|
| `error-discovery` | Trace Analysis Builder (Eval 101) |
| `write-judge-prompt` | Rubric Builder (Eval 201) |
| `validate-evaluator` | Automated Scoring Builder (Eval 101) |
| `generate-synthetic-data` | Test Data Builder (Eval 101) |
| `eval-audit` | CI Scoring Builder (Eval 201) |

## Try it on Pronto

Every skill above can run against this repo's own data — no setup beyond the
skill install:

- `error-discovery` → `datasets/pronto-support-tickets.csv` (24 tickets, 14 failure modes)
- `ticket-to-eval` → pick any row of `datasets/pronto-support-tickets.csv` and convert it:
  regression row appends to `datasets/pronto-regression.csv`, generalized row to `datasets/pronto-eval-gold.csv`
- `write-judge-prompt` + `validate-evaluator` → `datasets/pronto-eval-gold.csv`
  (48 rows; the `expected` column is your human-label proxy)
- `generate-synthetic-data` → extend the ticket set; diff against the generator
