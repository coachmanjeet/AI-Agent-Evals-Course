# Build notes — Pronto datasets (2026-10-06)

## Row counts

**pronto-support-tickets.csv — 24 rows** (failure_type):
- refund_policy_misquote: 4, missing_escalation: 4, ignored_constraint: 3,
  prompt_injection_compliance: 3 (doubled-up: most instructive per the brief)
- wrong_order_status, over_refund, pii_leak, tone_failure, tool_misuse,
  stale_data, refused_valid_query, warranty_misinfo, jailbreak_compliance,
  hallucinated_policy: 1 each
- All 14 taxonomy values covered ≥ once. Timestamps spread Sep 1–21, 2026
  (seed=42); names/emails fictitious (@example.com).

**pronto-eval-gold.csv — 48 rows** (intent):
- order_status 8, refund_request 11, warranty_claim 4, delivery_issue 6,
  substitution_request 4, product_question 4, account_help 4, feedback 3,
  adversarial 4
- 29 clean rows (failure_mode null) + 19 failure rows; 10 multi-turn;
  4 adversarial (2 prompt injection, 1 PII extraction, 1 jailbreak).

**pronto-regression.csv — 12 rows**, source tickets:
TKT-020, TKT-021 (prompt injection) · TKT-007, TKT-008 (missing escalation) ·
TKT-006 (over_refund) · TKT-011 (pii_leak) · TKT-002, TKT-003 (refund misquote) ·
TKT-014 (ignored_constraint) · TKT-023 (jailbreak) · TKT-019 (warranty_misinfo) ·
TKT-024 (hallucinated_policy). All `regression=true`, tags=`regression`.

## Judgment calls

1. **Gold `expected` is the correct behavior, not the ticket's behavior.**
   E.g. the TKT-006 ticket input ("refund my $85 order") appears in the gold set
   with `expected` = escalate for human approval — the response the agent
   *should* have given.
2. **Adversarial gold rows double as failure rows.** The 4 adversarial rows carry
   both `tags=adversarial` and a `failure_mode`, so W2/W3 can slice either way.
3. **PII-extraction adversarial row uses failure_mode=pii_leak** (the attempt),
   sourced from TKT-009 (the missing-escalation ticket about a roommate's order)
   — the correct response both refuses *and* escalates, per the bible.
4. **Regression `expected` is populated** (gold-standard response), unlike the
   workshop's regression file which leaves it empty — so the CI gate can do
   judge-scored comparison, not just input replay.
5. **Multi-turn inputs use `Customer:`/`Agent:` lines** with real newlines inside
   quoted CSV fields (valid per RFC 4180; verified round-trip).
6. **Ticket generator is template+slots, not fully random text.** The 24
   scenarios are hand-written templates; seed=42 drives only dates and
   name/email assignment. This keeps failures pedagogically sharp while still
   demonstrating the synthetic-generation pattern for Week 4.
7. **Dates are Sep 2026** to match the course timeline; ids are deterministic
   uuid5 (`pronto-gold-NNN` / `pronto-reg-NNN`), so rebuilds are stable.
8. **Policy edge interpreted strictly:** the $50 rule is "refunds OVER $50 need
   approval" — a $50.00 refund would not need approval, but no gold row sits
   exactly on the boundary; the $65/$85/$90/$150/$200 cases all clearly exceed it.
