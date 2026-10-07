# AI Evals in Practice: For Engineers & PMs

Learn to build evaluation frameworks you can trust — then use them to ship AI products that survive production.

**Instructor:** Manjeet Singh · **Course:** [AI Evals in Practice](https://live.bytebytego.com/courses/ai-evals) (ByteByteGo Live, 6 live sessions)

## Course map

```mermaid
flowchart TD
    W1["Week 1 · Foundations<br/>30 traced runs → failure taxonomy"]
    W2["Week 2 · LLM Judges<br/>binary rubrics → judge–human agreement"]
    W3["Week 3 · Safety & Adversarial<br/>red teaming → guardrails"]
    W4["Week 4 · RAG Evaluation<br/>golden set → RAGAS → confidence intervals"]
    W5["Week 5 · Multi-Agent Eval<br/>tool trajectories → handoffs"]
    W6["Week 6 · Production Infra<br/>CI gates → drift → canaries"]
    W1 --> W2 --> W3 --> W4 --> W5 --> W6

    AG["agent/<br/>one Pronto support agent,<br/>reused all 6 weeks"]
    DS["datasets/<br/>24 tickets · 48-row gold set<br/>12-row regression set"]
    W1 -.-> AG
    AG -.-> DS
    DS -.-> W2
    DS -.-> W4

    TV["Trace Viewer<br/>annotate traces in your browser<br/>Week 1"]
    JG["Judge Calibration Game<br/>calibrate your judge vs gold labels<br/>Week 2"]
    W1 -.-> TV
    W2 -.-> JG

    SOL["solutions/ + resources/<br/>released weekly · glossary + links"]
    W6 --> SOL
```

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
- An LLM API key — any provider works (OpenAI, Anthropic, or Gemini); **$5** is enough to start. **Not needed for Week 1** (Path B below is fully keyless), but required from Week 2 onward.

## Setup

```bash
git clone https://github.com/coachmanjeet/AI-Agent-Evals-Course.git
cd AI-Agent-Evals-Course
make setup          # creates .venv, installs core deps, copies .env.example -> .env
```

Then edit `.env` and paste your API key. Verify with:

```bash
make agent          # runs the Week 1 agent skeleton in --demo mode (no API key needed)
```

Later, as the weeks need them:

```bash
npm install -g promptfoo   # before Week 3: adversarial scans (Node-based)
```

## Repo tour

| Path | What it is |
|------|------------|
| `agent/` | The shared customer-service agent you build in Week 1 and reuse every week after |
| `datasets/` | The Pronto reference dataset: 24 support tickets, a 48-row gold eval set, a 12-row regression set, and the ticket generator |
| `skills/` | Curated AI eval agent-skills with a per-week map (symlink into `~/.claude/skills/`) |
| `docs/` | GitHub Pages site — the Judge Calibration Game (Week 2 hands-on) and the Trace Viewer (Week 1 error-analysis tool) |
| `week-01-...` … `week-06-...` | One folder per live session: recap README, worked `examples/`, and two `assignments/` |
| `solutions/` | Released after each live session — one folder per week |
| `resources/` | Glossary and curated links |
| `.github/workflows/eval-gate.yml` | Example CI eval gate (you wire this up for real in Week 6) |

## The tools

| | |
|---|---|
| ![Trace Viewer with 30 Pronto traces loaded — trace list, span waterfall, annotation panel](docs/images/trace-viewer.png) | ![Judge Calibration Game — label Pronto responses, earn XP](docs/images/judge-game.png) |
| **[Trace Viewer](https://coachmanjeet.github.io/AI-Agent-Evals-Course/trace-viewer/)** — explore OTel traces and annotate failures in your browser (Week 1) | **[Judge Calibration Game](https://coachmanjeet.github.io/AI-Agent-Evals-Course/judge-calibration-game/)** — label 24 Pronto responses, then score your judge vs your labels (Week 2) |

## How assignments work

Each assignment folder has its own README with a **Goal**, numbered **Steps**, and **Acceptance criteria** — that README is the source of truth. Starter code/templates sit alongside it. Attempt the assignment before peeking at `solutions/`; the learning is in the struggle.

## Troubleshooting

- **Setup seems stuck:** it's the 3–5 minute pip install — don't Ctrl-C. If you did, just rerun `make setup`; it resumes.
- **Windows:** native Windows works fine — all Python deps are Windows-friendly. WSL2 also works if you prefer it.
- **LangSmith 401:** check `LANGSMITH_API_KEY` in `.env` (not committed — that's the point), and that your project is named `ai-evals-course`.
- **`make agent` fails:** did `make setup` finish? Look for the `[3/3]` line.
- **Judge game API errors:** 401 → check the key; 429 → wait 30s and retry; anything else → append `?mock=1` to the URL for keyless practice.
- **promptfoo not found:** it's Node-based — `npm install -g promptfoo` (Week 3).

## Weekly rhythm

Each week: attend (or watch) the live session → read the week's README → work the two assignments → compare with the released solutions → bring your failures to office hours. Expect 4–7 hours per week.
