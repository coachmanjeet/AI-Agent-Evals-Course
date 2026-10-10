# Eval skills

Reusable Claude Code skills for eval work, salvaged from the retired
`ai-evals-workshop` repo (Reforge-era). All five are product-agnostic —
they work with Pronto datasets just as well as they did with the Market Map
agent.

| Skill | What it does | Course week |
|---|---|---|
| `ticket-to-eval-skill` | Convert a support ticket/trace into eval dataset rows (regression + generalized), with PII stripping | 1–2 |
| `eval-code-skill` | Write deterministic code-based evaluators; audit existing ones for brittleness | 2 |
| `eval-llm-judge-skill` | Write LLM-as-judge evaluator prompts; audit for bias/vagueness | 2 |
| `llm-align-skill` | Measure LLM-judge vs human-label alignment (TPR/TNR), investigate disagreements | 2 (pairs with the judge calibration game) |
| `uig-skill` | Build a User Input Grid to audit dataset coverage and find gaps | 3 |
