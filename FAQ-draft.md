# FAQ — draft (not committed; for Manjeet's review)

Answers marked **[answer]** are grounded in the repo as of 2026-10-07.
Items marked **[MANJEET]** need his answer — only he knows.

---

**Do I really need an LLM API key?**
**[answer]** Week 1 is fully doable with zero keys — pick Path B (Trace Viewer in the
browser) and `make agent` runs in `--demo` mode. The $10–20 estimate in the
README is for the whole course. Add a key before Week 2 for real judge
calibration instead of mock mode; Week 3's Promptfoo red-teaming runs against
a live provider, so plan on having a key by then. The repo never pins the
exact week a key becomes mandatory — **[MANJEET: confirm this timing, or
state it explicitly in the README]**.

**If I pick Path B in Week 1, am I stuck later?**
**[MANJEET]** Design call. Facts: the Judge Game (Week 2) has a keyless
`?mock=1` mode, so Week 2 partially works keyless. Weeks 3+ run the agent
and DeepEval/RAGAS with real API calls — no keyless path documented. Options:
(a) give Path B an explicit keyless story through the course (mock/simulation
wherever a key is needed), or (b) state up front that Path B ends at Week 2
and everyone needs a key by Week 3. **[MANJEET: pick (a) or (b)]**

**Gold set (48 rows) vs regression set (12 rows) — when do I reach for which?**
**[answer]** The 48-row gold set is your human-label proxy: calibrate judges
against it (Week 2), extend it with synthetic rows (Week 4). The 12-row
regression set is the 12 most instructive failing inputs — wire it into the
CI eval gate as the blocking set (Week 6). Building: gold set. Guarding: the 12.

**The `skills/` folder — required or optional? When do I install them?**
**[answer]** Optional scaffolding, not required reading. Install once at the
start (`ln -s` loop in `skills/README.md`), then invoke by name when you're
doing the work — `error-discovery` for Week 1, `write-judge-prompt` +
`validate-evaluator` for Week 2, `ticket-to-eval`/`generate-synthetic-data`
for Week 4, `eval-audit` for Week 6. No agent CLI? The AI Skills Lab covers
the same muscles with no installs (mapping table in `skills/README.md`).

**`solutions/` are "released weekly" — where, and exactly when?**
**[answer]** In this repo, `solutions/week-01/` … `week-06/`, one folder per
week, released after each live session. **[MANJEET: exact timing — how many
hours after the session? Announced where?]**

**Is 24 tickets / 30 traces a toy, or will this transfer to my real product?**
**[answer]** Honest version: Pronto is fictional (invented names, @example.com
emails, seeded generator), deliberately small so a full error-analysis →
judge → CI loop fits in one week. What transfers: the workflow, the 14-mode
failure taxonomy, judge calibration math, the CI gate pattern. What doesn't:
scale, your domain's failure modes, real production traces. **[MANJEET: edit
this paragraph if you want a different claim]**

**Judge game mock mode vs a real key — do I learn the same thing?**
**[answer]** Mock mode teaches the full loop (label → judge prompt → agreement
stats) for free. A real key adds what mock can't: real cost per run, latency,
and the variance of actual provider responses. **[MANJEET: confirm this is the
intended framing]**

**Which LLM provider should I choose — does it matter?**
**[answer]** The repo works with OpenAI, Anthropic, or Gemini. The Judge Game
takes OpenAI or Anthropic keys (Gemini not wired there). DeepEval and RAGAS
(Weeks 2/4) are provider-agnostic in the course's usage. Pick whichever you
already have a key for. **[MANJEET: add a recommendation if you have one —
e.g. cheapest path for students]**

**Windows: is WSL2 required or just recommended — what breaks on native?**
**[answer]** Effectively required: `ragas` and `deepeval` are painful on
native Windows. Use WSL2 before Week 2 (`make setup-extra` week).

**When are the live sessions and office hours?**
**[MANJEET]** Dates, times, and timezone — currently nowhere in the repo.

**Do I need to be enrolled on ByteByteGo, or is this repo fully self-serve?**
**[MANJEET]** Repo never says.

**Where do I ask questions between sessions? Where do recordings go?**
**[MANJEET]** No Q&A channel or recordings location in the repo.

**How do I submit assignments? Where does "Show Your Work" live?**
**[MANJEET]** Repo says assignments have Goal/Steps/Acceptance in their
READMEs, but never how (or where) to submit.

**Is anything graded? Certificate?**
**[MANJEET]** Repo is self-assessed against acceptance checkboxes; no
grading or certificate language anywhere.

**The DOCX mentions earning a "white belt" — is there a belt system?**
**[MANJEET]** Repo never mentions belts. Confirm or cut.

**I'm a PM who doesn't code — what's my path?**
**[MANJEET]** "For Engineers & PMs" is the title, but the repo is Python +
CLIs with zero no-code guidance. Design call: no-code track, pair-with-AI
path, or honest "basic Python comfort expected."
