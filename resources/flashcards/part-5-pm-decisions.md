# Part 5 — PM Decisions (Week 6)

### Card 5.1 — Ship / no-ship decisions

**Q:** How do you make a ship/no-ship decision with evals?

**A:** You set the bar before you test — MVQ on each critical failure mode —
and then the numbers decide, not the demo. A great demo with a red eval is
a no-ship. Write the bar down in advance so nobody moves it after seeing
the results.

**Pronto:** The bar: 100% human-approval compliance on over-$50 refunds in
the eval set. The new version hits 99%. It demos beautifully. It's a
no-ship — one unapproved $80 refund in production costs more than a week of
delay.

**Week 6 · FAQ:** Section 13 — PM Playbook: Quick Reference

---

### Card 5.2 — The autonomy ladder

**Q:** What is the autonomy ladder?

**A:** A staircase from "suggests, human approves" up to "acts alone, human
reviews later." The agent climbs one rung at a time, and each rung is gated
on measured reliability — not on how confident the team feels.

**Pronto:** Rung 1: refunds under $10 auto-approved. Rung 2: under $50 with
random spot checks. Rung 3 (over $50): human approval, always. The agent
doesn't reach rung 2 because someone believes in it — it gets there by
clearing the error-rate bar on rung 1.

**Week 6 · FAQ:** Section 13 — PM Playbook: Quick Reference

---

### Card 5.3 — Confidence earns autonomy

**Q:** What does "confidence earns autonomy" mean in practice?

**A:** Freedom is granted by measured error rates over real traffic, not by
seniority, gut feel, or a good demo. Every new freedom has a number
attached: this error rate, over this many real cases, unlocks this action.

**Pronto:** The agent handled 500 under-$10 refunds with zero policy breaks
in production. That number — not optimism — earns it the under-$25 rung.
If the error rate ticks up, it climbs back down. Autonomy is rented, not
owned.

**Week 6 · FAQ:** Section 13 — PM Playbook: Quick Reference

---

### Card 5.4 — The launch gate

**Q:** What is a launch gate?

**A:** A checklist that must be fully green before launch: evals pass,
guardrails deployed, monitoring dashboards live, rollback plan ready, and a
named owner for every alert. If one box is unchecked, you don't launch —
you fix the box.

**Pronto:** No launch until: the $50-approval eval is at 100%, the
over-$50 block guardrail is deployed and firing correctly, the refund
dashboard is live, the rollback is one command, and one person owns the
refund alerts. Five boxes, all green, or no launch.

**Week 6 · FAQ:** Section 13 — PM Playbook: Quick Reference
