# Part 2 — Judges (Week 2)

### Card 2.1 — Generator → judge → router

**Q:** What is the generator → judge → router pattern?

**A:** Three roles. The generator does the work, the judge grades it against
your rules, and the router decides what happens with the grade — ship it,
retry it, or escalate it to a human. Grading and acting are separate jobs.

**Pronto:** The generator drafts the refund reply. The judge checks it
against the policy bible (photo? approval? opt-in?). The router sends clean
replies straight to the customer and escalates anything the judge flagged.

**Week 2 · FAQ:** Section 4 — Evaluation Design & Methodology

---

### Card 2.2 — Trusting your judge

**Q:** How do you know you can trust an LLM judge?

**A:** You don't — until you measure it. Have humans grade a sample, compute
agreement (kappa), and then read every disagreement one by one. The pattern
in the disagreements tells you exactly what the judge is blind to.

**Pronto:** The judge grades 100 refund chats; humans graded them too. Kappa
looks okay, but every disagreement is the same shape: the judge approves
replies that are polite but skip the $50 approval rule. Now you know its
blind spot — politeness over policy.

**Week 2 · FAQ:** Section 5 — Human Annotation & Process

---

### Card 2.3 — Judge biases

**Q:** What biases do LLM judges have?

**A:** They favor long answers over short correct ones, confident tone over
correct content, the first option over the second, and writing that sounds
like their own. If you don't correct for this, your judge rewards style and
calls it quality.

**Pronto:** The judge gave full marks to a long, warm, beautifully written
reply that refunded $80 with no human approval. Length and charm are not
policy compliance — the judge needs the policy as a checklist, not a vibe.

**Week 2 · FAQ:** Section 4 — Evaluation Design & Methodology

---

### Card 2.4 — Binary beats Likert

**Q:** Why prefer binary pass/fail over 1–5 Likert scales?

**A:** Because two graders rarely agree on "3 vs 4," but they usually agree
on "broke the rule or not." Binary questions are checkable; Likert scales
measure the grader's mood. Checkable beats arguable.

**Pronto:** "Did the agent get human approval for the $80 refund?" — yes or
no, anyone can verify. "Rate the reply 1–5" gives you a 3 from one grader
and a 4 from another, and you've learned nothing about the $80.

**Week 2 · FAQ:** Section 4 — Evaluation Design & Methodology
