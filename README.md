# AI Evals in Practice: For Engineers & PMs

Learn to build evaluation frameworks you can trust — then use them to ship AI products that survive production.

**Instructor:** Manjeet Singh · **Course:** [AI Evals in Practice](https://live.bytebytego.com/courses/ai-evals) (ByteByteGo Live, 6 live sessions)

## The 6 weeks

| Week | Theme | Key topics |
|------|-------|------------|
| 01 | Eval Foundations & Error Analysis | Quality dimensions, cost/latency metrics, traces vs logs, failure taxonomies, the eval flywheel |
| 02 | Designing Reliable LLM Judges | Evaluator types, binary rubrics, judge prompt anatomy, judge–human agreement, per-metric A/B |
| 03 | Safety & Adversarial Testing | Prompt injection, jailbreaks, red teaming with Promptfoo, guardrails, HITL approval flows |
| 04 | RAG Evaluation | Golden sets, RAGAS metrics, groundedness, bootstrap confidence intervals, repeatable harnesses |
| 05 | Multi-Agent Evaluation | Tool-call scoring, trajectory evaluation, handoff evaluation, interaction failures |
| 06 | Production Eval Infrastructure | Eval gates in CI/CD, drift detection, canary evals, cost routing, ownership |

## Prerequisites

- Python 3.10+ (Mac, Windows, or Linux, 4 GB RAM)
- Basic familiarity with Git and GitHub
- An LLM API key (OpenAI, Anthropic, or Gemini). Expect roughly **$10–20** in API usage across the course.

## Setup

```bash
git clone https://github.com/coachmanjeet/AI-Agent-Evals-Course.git
cd AI-Agent-Evals-Course
make setup          # creates .venv, installs deps, copies .env.example -> .env
```

Then edit `.env` and paste your API key. Verify with:

```bash
make agent          # runs the Week 1 agent skeleton in --demo mode (no API key needed)
```

## Repo tour

| Path | What it is |
|------|------------|
| `agent/` | The shared customer-service agent you build in Week 1 and reuse every week after |
| `datasets/` | The Pronto reference dataset: 24 support tickets, a 48-row gold eval set, a 12-row regression set, and the ticket generator |
| `skills/` | Curated AI eval agent-skills with a per-week map (install via `npx skills add`) |
| `docs/` | GitHub Pages site — hosts the Judge Calibration Game (Week 2 hands-on) |
| `week-01-...` … `week-06-...` | One folder per live session: recap README, worked `examples/`, and two `assignments/` |
| `solutions/` | Released after each live session — one folder per week |
| `resources/` | Glossary and curated links |
| `.github/workflows/eval-gate.yml` | Example CI eval gate (you wire this up for real in Week 6) |

## How assignments work

Each assignment folder has its own README with a **Goal**, numbered **Steps**, and **Acceptance criteria** — that README is the source of truth. Starter code/templates sit alongside it. Attempt the assignment before peeking at `solutions/`; the learning is in the struggle.

## Weekly rhythm

Each week: attend (or watch) the live session → read the week's README → work the two assignments → compare with the released solutions → bring your failures to office hours. Expect 4–7 hours per week.
