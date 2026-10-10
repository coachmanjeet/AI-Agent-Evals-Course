# Judge Calibration Game

A gamified, hands-on exercise for **Week 2 — Designing Reliable LLM Judges**:
label Pronto customer-support responses as PASS/FAIL, then write an LLM-judge
prompt and measure how well your judge agrees with your own labels
(accuracy, precision, recall, F1, Cohen's κ). Finish with a gold-check that
shows where *your* labels disagreed with the answer key — label quality matters.

Wondering how much to trust those metrics once the judge scores unlabeled
data? `week-02-designing-reliable-llm-judges/assignments/01-build-and-validate-judge/judge_stats.py`
bias-corrects the judge's pass rate from your hand labels and puts a 95%
confidence interval on it.

## Run locally

```bash
cd docs && python3 -m http.server 8000
# open: http://localhost:8000/judge-calibration-game/
```

## Test mode (no API key needed)

Append `?mock=1` to run the entire flow — setup, labeling, judge run, metrics,
gold check, export — against a deterministic simulated judge:

```
http://localhost:8000/judge-calibration-game/?mock=1
```

## With a real key

Pick **Braintrust** in the Setup step and paste your Braintrust API key —
course students get free Braintrust credit for the duration of the course, so
this costs you nothing. (The game calls Braintrust's OpenAI-compatible proxy.)
You can also bring your own OpenAI or Anthropic key instead. Keys stay in your
browser's localStorage and are sent only to the provider's API — there is no
backend. A full judge run over your labeled items costs well under $0.10 on a
paid key.

## Live URL (once Pages is enabled)

`https://coachmanjeet.github.io/AI-Agent-Evals-Course/judge-calibration-game/`

To enable: repo Settings → Pages → Deploy from a branch → `main` → `/docs`.

## Files

| File | What it is |
|------|------------|
| `index.html` | Standalone page shell — all styles inlined, no dependency on any other site |
| `game.js` | The full game (setup → label → evaluate → gold check → export) |
| `pronto-calibration-items.json` | 24 Pronto items (14 pass / 10 fail across 10 failure modes) |

Fully self-contained: the only external requests are public CDNs
(Google Fonts, Salesforce Lightning Design System) and the LLM provider APIs
you choose to call.
