# Experiment pre-registration

## The idea in one sentence
Write down what would change your mind *before* you run the experiment —
because after you see the results, you'll rationalize whatever they say.

## The template (fill before collecting any data)
- **Change being tested:** (one line)
- **Hypothesis:** If [change], then [primary metric] will [direction] by
  [roughly how much], because [reason].
- **Primary metric:** (exactly one — the one the decision rides on)
- **Decision rule:** "If the metric moves by ≥ X with 95% confidence, we ship.
  Otherwise we don't." Written before data exists.
- **Guardrails:** metrics that must not regress (e.g., safety eval pass rate,
  p95 latency).
- **Novelty window:** how long after the change before you trust the numbers
  (users behave differently in week one).

## The rule that matters
Once results are visible, the decision follows the pre-committed rule — not a
re-analysis. If you want a different rule, you register a new experiment.

## Pronto example
- Change: raise the refund auto-approval limit from $50 to $75.
- Hypothesis: if we raise the limit, median resolution time drops ~20% because
  fewer cases wait on human approval, without raising wrong-refund rate.
- Primary metric: median resolution time on refund tickets.
- Decision rule: ship if resolution time drops ≥ 15% AND wrong-refund eval
  pass rate stays ≥ 98%.
- Guardrails: escalation rate, CSAT.
