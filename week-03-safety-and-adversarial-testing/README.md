# Week 3 — Safety & Adversarial Testing

Adversarial eval is a different discipline from quality eval: you're not
asking "does it work?" but "can someone make it misbehave?" — then building
the guardrails that catch it.

## What we covered

- Adversarial evaluation vs. quality evaluation
- The agent attack surface: every input channel, every tool, every output
- Attack categories: prompt injection, jailbreaks, data leakage, harmful content, bias
- Direct vs. indirect prompt injection
- Jailbreak techniques: role-play, hypotheticals, emotional framing, encoding
- Data leakage targets; bias testing via demographic prompt variation; harmful-content testing
- Manual vs. automated red teaming; automated red teaming with Promptfoo
- Test suite schema: attack type, target, expected behavior
- Guardrail confusion matrices; guardrail composition (layering defenses)
- Human-in-the-loop approval flows

## Key takeaways

1. **Your agent's inputs are attacker-controlled.** Treat every user message, doc, and tool result as untrusted until proven otherwise.
2. **Automate the boring attacks, hand-craft the clever ones.** Promptfoo covers breadth; your 5 hand-written attacks cover your actual product.
3. **Guardrails have two error rates, not one.** Catch rate without over-block rate is a vanity metric — a guardrail that blocks everything is useless.
4. **Some actions should never be autonomous.** HITL approval flows are a design choice, not an admission of failure.

## Links

- Promptfoo docs — red teaming, scans, config: https://promptfoo.dev
- LangSmith docs: https://docs.langchain.com/langsmith

## In this folder

- `examples/` — worked examples from the live session (added after the session)
- `assignments/01-scan-and-triage/` — Promptfoo baseline scan + hand-crafted attacks
- `assignments/02-build-and-score-guardrails/` — 3 guardrails, scored on catch vs over-block
