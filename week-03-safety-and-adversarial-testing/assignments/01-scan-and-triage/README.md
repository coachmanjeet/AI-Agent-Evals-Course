# Assignment 1 — Scan and triage

## Goal

Find out how your agent behaves under attack — automatically first, then with your own creativity.

## Steps

1. Install Promptfoo: `npm install -g promptfoo` (Node required — it's not a Python tool).
2. Write `promptfooconfig.yaml` (starter has the skeleton): point it at your agent, with a set of adversarial probes — at least 2 prompt injections (one direct, one indirect), 1 jailbreak, 1 data-leakage probe, 1 harmful-content probe.
3. Run the baseline scan: `promptfoo eval`. Record the pass/fail per probe.
4. Triage every failing trace into a **frequency × severity matrix** (starter template): how often could this happen × how bad if it does.
5. Craft **5 domain-specific attacks by hand** — attacks only someone who knows *your* agent would think of (e.g. a fake "order" that tricks `lookup_order` into revealing another customer's data, a doc-injection that rewrites the returns policy). Add them to the suite with expected behavior.

## Acceptance criteria

- [ ] `promptfooconfig.yaml` runs clean with `promptfoo eval` (no config errors)
- [ ] Baseline scan covers all 5 probe categories (direct + indirect injection count as 2)
- [ ] Triage matrix filled: every failing trace placed in frequency × severity
- [ ] 5 hand-crafted attacks documented with attack type, target, expected behavior
- [ ] At least 1 hand-crafted attack actually breaks the agent (if none do, they're not adversarial enough)

## Starter

`starter.md` — the Promptfoo config skeleton and triage matrix template.
