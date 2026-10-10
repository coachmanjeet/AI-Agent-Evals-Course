# Part 4 — Production (Weeks 4–5)

### Card 4.1 — CI/CD evals vs monitoring vs guardrails

**Q:** What's the difference between CI/CD evals, monitoring, and guardrails?

**A:** Three time horizons. CI/CD evals run before deploy: "is this version
safe to ship?" Monitoring watches after deploy: "is it still healthy?"
Guardrails act in real time: "stop this bad action right now." Miss any one
and you have a gap attackers and accidents walk through.

**Pronto:** Eval gate on the refund flow must pass before release. A
dashboard tracks refund amounts and escalation rates after release. A hard
rule blocks any auto-refund over $50 live, in milliseconds.

**Weeks 4–5 · FAQ:** Section 9 — Production Monitoring & Observability
Operations

---

### Card 4.2 — Effective guardrails

**Q:** What makes a guardrail effective?

**A:** It's specific (one rule, not vibes), cheap (microseconds, not a model
call), fast (runs inline, before the action), and fails closed (if the check
errors, it blocks rather than allows). And you measure how often it fires —
a guardrail that never fires is either perfect or broken.

**Pronto:** "Block any refund over $50 without an approval flag." It's a
five-line deterministic check, not an LLM call. If the flag lookup fails,
the refund is blocked. The firing rate is on the dashboard; a sudden spike
means something upstream changed.

**Weeks 4–5 · FAQ:** Section 6 — Guardrails, Trust & Safety

---

### Card 4.3 — The production → eval flywheel

**Q:** What is the production → eval flywheel?

**A:** Production failures become new eval cases, better evals make the next
version stronger, the stronger version surfaces rarer failures, and those
become eval cases too. Every incident makes the test suite smarter, so the
same failure can only happen once.

**Pronto:** Every escalated refund chat gets labeled monthly and added to
the eval set. The $80-no-approval incident became a test case; next quarter,
a novel "refund me in gift cards" bypass becomes one too. The eval set grows
with the real world.

**Weeks 4–5 · FAQ:** Section 12 — Continuous Improvement & Fine-tuning

---

### Card 4.4 — Cost per successful task

**Q:** Why track cost per successful task instead of cost per call?

**A:** Because a cheap model that fails half the time — retries, escalations,
human cleanup — costs more than an expensive model that gets it right the
first time. Cost per call measures the vendor's price; cost per successful
task measures yours.

**Pronto:** Model A costs $0.01 per chat, but 20% of chats need human review
at $2 each: about $0.41 per resolved ticket. Model B costs $0.05 per chat
with 2% escalation: about $0.09 per resolved ticket. The "expensive" model
is four times cheaper where it counts.

**Weeks 4–5 · FAQ:** Section 9 — Production Monitoring & Observability
Operations
