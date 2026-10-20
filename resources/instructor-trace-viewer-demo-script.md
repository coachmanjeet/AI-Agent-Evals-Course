# Instructor Demo Script: Trace Viewer (5 min)

**Instructor-only.** This is the presenter's live-demo script for the Trace
Viewer, harvested from the "Traceviewer" tab of the class document. It is
not a student handout — the student steps for the Trace Viewer live in the
Week 1 Assignment 1 README (Path B) and in `docs/trace-viewer/`.

## Your live demo (5 min)

- Open the viewer, click **Load the Pronto sample** — no file juggling on
  screen.
- Click one clean trace → show the span tree → annotate `no_failure` +
  note.
- Click a failure trace (pick the over-refund one) → expand the spans and
  show the `issue_refund` call happening with no `escalate_to_human` before
  it → annotate `over_refund`.
- Hit **Export CSV**, show the file.
- Land the line: "The agent's final message said 'refund processed.' The
  trace shows it never checked the $50 rule. Don't trust the confirmation
  message — read the trace."
