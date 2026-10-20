# Course architecture — one fact, one home

This repo follows one rule: **every fact has exactly one home. Every
other location links to it — it never copies it.**

This rule exists because a student (Oct 2026) found assignment
information scattered and duplicated across repo markdown, `.docx`
snapshots, a Google Doc, and the course portal — and the copies had
drifted apart and contradicted each other. The fix is structural, not
editorial: if a fact can only live in one place, it cannot drift.

## The rules

1. **One entry page per week.** Each `week-0X-…/README.md` is the week's
   entry page: overview, what was covered, key takeaways, deadlines, and
   *links* to that week's assignment READMEs. It contains no assignment
   steps, judging rules, or acceptance criteria of its own.
2. **One complete file per assignment.** Each
   `week-0X-…/assignments/<assignment>/README.md` is the complete,
   self-sufficient assignment document: goal, steps, judging rules, and
   acceptance criteria all live in that one README. If a student needs a
   second file to know how an assignment is judged, the assignment
   README is incomplete — fix it there.
3. **Tools are documented once, in `docs/`.** Tool documentation (Trace
   Viewer, Judge Calibration Game) lives in `docs/` and is only ever
   *linked* from week pages, assignment READMEs, and the top-level
   README — never copied into them.
4. **No `.docx` assignment files anywhere.** Assignment instructions
   live only in this repo, as markdown. Portal posts and any other
   external surface **link to the repo assignment README**; they never
   carry an uploaded copy. If a `.docx` is ever genuinely needed, it is
   generated from the canonical markdown at publish time and discarded —
   it is never maintained as a second source.
5. **`solutions/` vs `examples/` — different things, different homes.**
   - `solutions/` = **assignment answers**, released weekly after the
     live session (one folder per week). Gated by release.
   - `examples/` (inside each week folder) = **method worked-examples** —
     worked demonstrations of a technique, always visible, not answers
     to that week's assignments.
   Never put an assignment answer in `examples/`, and never put a method
   worked-example in `solutions/`.
6. **Skills live in one place.** Agent skills live in `skills/` only.
   `resources/skills/` is a pointer to `skills/`, not a second
   collection.
7. **Every other location is a link, never a copy.** Week pages,
   resource indexes, FAQs, glossaries, and the top-level README point
   to the canonical home. A link can go stale visibly; a copy goes
   stale silently.

## Guardrail

`scripts/check_course_ia.py` enforces the mechanical parts of this
document: it fails if any `.docx` exists in the repo, if near-duplicate
instruction text appears across markdown files, if more than one
failure-code vocabulary is in use in Week 1, or if any week or
assignment folder lacks its README entry page. Run it before committing
changes to course content:

```bash
python3 scripts/check_course_ia.py
```
