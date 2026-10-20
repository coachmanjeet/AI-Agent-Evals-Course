# Eval-Driven AI PRD Template

*Created by: Manjeet Singh*

Lightweight AI PRD. Written before you build/Prototype. Read by leadership and
cross-functional partners.

## The mental model

An eval is just your taste, written down as checks a machine can run. Every
check exists because something went wrong once.

## Spec + eval: two halves of one PRD

Spec-driven answers what we build (tools, actions, scope, working bottom-up).
Eval-driven answers what good means (bars, failure modes, gates, working
top-down from outcomes). Like TDD: the tests do not replace the design, they
complete it.

---

## 1. One-liner

What are we building, for whom, and why now?

**Template:**

> An AI agent for [user] that [core job] so [outcome] is under [constraint].

**Example (Agentforce):** An Agentforce Service Agent that resolves Tier-1
retail service cases — order status, returns, and subscription changes — end
to end in Messaging, so customers get a resolution in under a minute and
support capacity shifts to complex work.

## 2. What "good" means

Three bars. One number each. If you can't name a number yet, write when you
know it.

**Worked example (Agentforce):**

| Bar | Target | Why this number |
| --- | --- | --- |
| Business outcome | Tier-1 case deflection ≥ 35% at 90 days post-GA | Below 35% the agent doesn't change staffing math, so the program doesn't pay for itself |
| Quality floor | Zero ungrounded policy claims; ≤ 2% wrong-action executions | A wrongly initiated return is a refund we cannot claw back |
| Cost & latency | p95 first token < 3.0s; ≤ $0.12 per resolved case | Must feel live in Messaging, and must beat blended human cost per case |

Latency and cost live here and nowhere else. Don't restate them in the eval
plan.

## 3. Prototype plan

**Template prompts, with Agentforce examples:**

- **In scope**
  - e.g. Order status, return initiation, subscription plan change. Messaging
    channel only, authenticated customers.
- **Explicitly out, for now**
  - e.g. Billing disputes, warranty claims, unauthenticated chat, voice.
- **Model / reasoning**
  - e.g. Atlas reasoning engine on the default LLM. No fine-tuning at
    prototype stage.
- **Grounding & data sources**
  - e.g. Knowledge articles (retail policy set, active versions only), Order
    and Subscription objects.
- **Actions**
  - e.g. Get Order Status, Initiate Return, Change Subscription Plan,
    Escalate to Human.
- **Orchestration**
  - e.g. Single service agent, four topics, escalation on out-of-scope
    classification or low retrieval confidence.
- **What we build first**
  - e.g. Order status only — read-only, no write actions. Proves topic
    routing and grounding before the agent is allowed to touch a record.
- **Timeline to first usable prototype**
  - e.g. 1 week to a working agent, 3 days to first error analysis on 50
    traces, 1 week to iterate.

## 4. Top three ways this fails

Your best guess today, in one line each. The real taxonomy comes out of error
analysis in the Eval Plan (see `eval-plan-template.md`) — don't try to write
it here.

**Worked example (Agentforce):**

| Suspected failure | Sev | Why we think so |
| --- | --- | --- |
| Agent asserts a return policy that isn't in Knowledge | P0 | Customer acts on it and we owe the refund |
| Agent initiates a return against the wrong order line | P0 | Irreversible write to a customer record |
| Agent keeps trying instead of escalating out-of-scope cases | P2 | Handle time gets worse, not better — the opposite of the point |

## 5. Open decisions before we scale

- **[Decision 1]**
  - e.g. Do write actions (returns, plan changes) require explicit customer
    confirmation, or can the agent execute unilaterally?
- **[Decision 2]**
  - e.g. Messaging only at GA, or Messaging + Email?
- **[Decision 3]**
  - e.g. Confidence-based escalation threshold, or fixed topic-based
    escalation rules?

## 6. AI-specific non-negotiables

Three questions, not a section. Everything else — full GTM, pricing, legal —
stays in the standard PRD.

**Worked example (Agentforce):**

| Question | Answer | Owner |
| --- | --- | --- |
| Does customer data leave the tenant or trust boundary? | No — grounding and inference stay in-org | [Security] |
| Do prompts or traces retain PII after the session? | Masked at capture; 30-day trace retention | [Privacy] |
| What is the rollout gate? | Internal org → 3 design partners → GA behind permission set | [PM] |

---

## What is next

- Eval detail lives in the Eval Plan (see `eval-plan-template.md`).
- Build your prototype and fill additional details after the prototype
  produces real outputs.
