# Assignment 1 — Scan and triage

## Goal

Find out how your agent behaves under attack — automatically first, then with your own creativity.

## Steps

1. Install Promptfoo: `npm install -g promptfoo@0.124.1` (Node required — it's not a Python tool; version pinned — this is the tested version for this course).
2. Write `promptfooconfig.yaml` (starter has the skeleton): point it at the
   real agent — provider id `'exec: python -m agent.pronto_agent'`, run
   from the repo root — with a set of adversarial probes: at least
   2 prompt injections (one direct, one indirect), 1 jailbreak,
   1 data-leakage probe, 1 harmful-content probe.
3. Run the baseline scan: `promptfoo eval`. Record the pass/fail per probe.

> We use `promptfoo eval`, not `promptfoo redteam`: `eval` runs YOUR
> probes (pennies for 5 probes). `redteam` auto-generates hundreds of
> attacks — the deck's $7.42 / 300-test run is illustrative scale, not
> your assignment. Your suite is 5 probes here + 5 hand-crafted attacks
> in step 5.
4. Triage every failing trace into a **frequency × severity matrix** (starter template): how often could this happen × how bad if it does.
5. Craft **5 domain-specific attacks by hand** — attacks only someone who knows *your* agent would think of (e.g. a fake "order" that tricks `get_order_status` into revealing another customer's data, a policy-snippet injection that rewrites the refund rules). At least **1 of the 5 must be multi-turn** — real injections often build over several turns (rapport first, payload later), and your agent is multi-turn, so single-turn-only testing leaves a blind spot. Honest tooling note: Promptfoo's exec provider runs one probe per process, so multi-turn attacks don't fit `promptfoo eval` — run those by hand via `python -m agent.pronto_agent --chat` and paste the transcript into `attacks.md`. Add all 5 to the suite with expected behavior.

## Acceptance criteria

- [ ] `promptfooconfig.yaml` runs clean with `promptfoo eval` (no config errors)
- [ ] Baseline scan covers all 5 probe categories (direct + indirect injection count as 2)
- [ ] Triage matrix filled: every failing trace placed in frequency × severity
- [ ] 5 hand-crafted attacks documented with attack type, target, expected behavior
- [ ] At least 1 hand-crafted attack is multi-turn (run via `--chat`, transcript in `attacks.md`)
- [ ] At least 1 hand-crafted attack actually breaks the agent (if none do, they're not adversarial enough)

## Starter

`starter.md` — the Promptfoo config skeleton and triage matrix template.
