#!/usr/bin/env python3
"""Build the 6-slide 'weekly learning tactics' deck for the AI Evals in Practice course.

Style mirrors the reference slide Manjeet supplied (Shreyas-style tactics table):
dark header band with title + subtitle, then a table of skills x learning modes.
One slide per course week; columns adapt to the week's focus.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

DARK = RGBColor(0x14, 0x24, 0x1B)      # near-black green, like the reference
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0xC9, 0xD4, 0xCC)     # subtitle gray-green
HDR_BG = RGBColor(0xEE, 0xF1, 0xED)    # column-header gray
ROW_BG = RGBColor(0xF7, 0xF9, 0xF7)    # row-label bg
GRID = RGBColor(0xD5, 0xDB, 0xD5)
INK = RGBColor(0x1A, 0x1A, 0x1A)
SUB = RGBColor(0x4A, 0x55, 0x4A)

WEEKS = [
    dict(
        title="Week 1: Eval Foundations & Error Analysis",
        subtitle="3 skills that turn production failures into datasets  (tactics matched to your learning style)",
        cols=["Read / Listen", "Do", "Shadow"],
        rows=[
            ("Error analysis &\nfailure taxonomies",
             "Hamel Husain \u201cYour AI Product Needs Evals\u201d; Eugene Yan\u2019s evals essays (eugeneyan.com); Anthropic \u201cBuilding Effective Agents\u201d (tracing section)",
             "Run 30 Pronto inputs, annotate pass/fail, cluster into 5+ binary failure codes; ship taxonomy.md with top 3 modes + 1 anomaly",
             "Sit with support triaging real tickets; watch a senior annotate production traces and narrate their codes"),
            ("Tracing &\nobservability",
             "LangSmith tracing docs; OpenAI \u201cA Practical Guide to Building Agents\u201d (observability)",
             "Trace every Pronto run in LangSmith or the course Trace Viewer; export your annotations.csv",
             "Watch an on-call engineer debug a live agent incident straight from traces"),
            ("Eval design basics",
             "Eugene Yan on why benchmarks mislead; the six quality dimensions: model, product, safety, reliability, cost, latency",
             "Score the same Pronto outputs on model quality vs product behavior vs cost/latency; answer the 2-question pre-survey",
             "Join a launch review; listen for which quality dimension blocks the ship call"),
        ],
    ),
    dict(
        title="Week 2: Designing Reliable LLM Judges",
        subtitle="3 skills that make judges you can gate on  (tactics matched to your learning style)",
        cols=["Read / Listen", "Do", "Shadow"],
        rows=[
            ("Writing binary\nrubrics",
             "Braintrust scorers docs; judge-prompt anatomy: task, criteria, output format, examples",
             "Write 3 single-criterion binary rubrics as Braintrust scorers; play the Judge Calibration Game",
             "Co-write a rubric with a teammate; argue edge cases until the criterion is airtight"),
            ("Judge\u2013human\nagreement",
             "Zheng et al. \u201cJudging LLM-as-a-Judge\u201d (MT-Bench paper); Eugene Yan\u2019s AlignEval walkthrough",
             "Hand-label 40 outputs, run the judges, build the agreement matrix, compute Cohen\u2019s kappa",
             "Adjudicate disagreements with a partner \u2014 each defended label is a rubric fix"),
            ("Trust gates &\nerror analysis",
             "False-pass vs false-fail costs; \u201cfalse passes are the expensive error\u201d",
             "Diagnose your worst judge failure, change ONE thing, A/B test, make a ship/no-ship call with numbers",
             "Watch a senior kill a judge that \u201clooked fine\u201d \u2014 ask what its false-pass rate was"),
        ],
    ),
    dict(
        title="Week 3: Safety & Adversarial Testing",
        subtitle="3 skills that keep your agent from misbehaving  (tactics matched to your learning style)",
        cols=["Read", "Do", "Shadow"],
        rows=[
            ("Attack-surface\nthinking",
             "OWASP Top 10 for LLM Applications; Simon Willison\u2019s prompt-injection archive",
             "Map every input channel, tool, and output of the Pronto agent as attacker-controlled",
             "Sit in on a security review; count how many \u201ctrusted\u201d inputs get challenged"),
            ("Red teaming",
             "Promptfoo red-teaming docs; attack categories: injection, jailbreak, leakage, bias, harmful content",
             "Play Lakera Gandalf to feel prompt injection; run a Promptfoo baseline scan + 5 hand-crafted attacks",
             "Watch an experienced red-teamer work; steal their opening 3 moves"),
            ("Guardrails & HITL",
             "Guardrail confusion matrices; layering defenses (regex \u00b7 LLM judge \u00b7 hybrid)",
             "Build 3 guardrails; score catch rate vs over-block rate; wire a human-in-the-loop approval flow",
             "Review a guardrail incident \u2014 one catch and one over-block \u2014 with the owning team"),
        ],
    ),
    dict(
        title="Week 4: RAG Evaluation",
        subtitle="3 skills that separate retrieval failures from generation failures  (tactics matched to your learning style)",
        cols=["Read", "Build", "Measure"],
        rows=[
            ("Golden-set\nconstruction",
             "RAGAS paper (Shahul et al.) on eval design; Braintrust dataset docs",
             "Build a 150+ case golden set (question \u00b7 contexts \u00b7 ground truth); hand-validate 30; pin v1",
             "Report label-correctness on your 30 hand-checked cases before trusting the rest"),
            ("Component-wise\nscoring",
             "\u201cLost in the Middle\u201d (Liu et al.) on context use; Braintrust\u2019s 4 RAG scorers",
             "Run faithfulness, answer relevance, context precision, context recall as separate scorers",
             "Attribute each failure to retrieval vs generation; fix the worse half first"),
            ("Statistical rigor",
             "Sample size, paired tests, bootstrap confidence intervals (course notes + any stats refresher)",
             "One-config reproducible harness; paired bootstrap test in one command \u2192 report.md",
             "Never report a point estimate again \u2014 CIs on every comparison, held-out re-test before claiming victory"),
        ],
    ),
    dict(
        title="Week 5: Multi-Agent Evaluation",
        subtitle="3 skills for scoring systems, not just models  (tactics matched to your learning style)",
        cols=["Read", "Do", "Shadow"],
        rows=[
            ("Trajectory\nevaluation",
             "Tau-bench paper (Sierra) on agentic evals; LangSmith trajectory docs",
             "Capture full tool trajectories on pronto_crew.py; judge properties (right tools, right order, no extra calls), not exact match",
             "Replay a failing trajectory with a senior; narrate where it went wrong before they do"),
            ("Tool-call scoring",
             "CrewAI docs (agents, tasks, tools); expected-action sets; argument validation as structured-output eval",
             "Write 15+ expected-action records with an extra-call policy; score argument validity",
             "Watch a tool-misuse failure get root-caused to a vague tool description"),
            ("Handoffs &\ninteraction failures",
             "Handoff contracts: completeness, fidelity, routing; cascading failures in pipelines",
             "Wire the A\u2192B\u2192A handoff on 10+ scenarios; write the 3-layer report (model vs agent vs system gap)",
             "Sit through a multi-agent incident review; map each failure to its handoff"),
        ],
    ),
    dict(
        title="Week 6: Production Eval Infrastructure",
        subtitle="3 skills that make evals compound in production  (tactics matched to your learning style)",
        cols=["Read", "Build", "Own"],
        rows=[
            ("Eval gates in CI",
             "GitHub Actions docs; the course starter .github/workflows/eval-gate.yml",
             "Wire eval-gate.yml (PR fast subset + nightly regression); break it on purpose and watch the gate block the PR",
             "Write your blocking-vs-logged policy where the team can see it; defend it in review"),
            ("Production\nmonitoring",
             "Google SRE Workbook (monitoring/alerting); Martin Fowler on canary releases",
             "Sampling pipeline + drift canary + alert thresholds: what pages vs what waits for morning",
             "Name the eval owner and the weekly review cadence \u2014 no owner, no flywheel"),
            ("Decision gates &\nthe flywheel",
             "Thresholds from business impact; fix prioritization by frequency \u00d7 cost",
             "Write the decision memo \u2014 one page: what evals said, what shipped, what didn\u2019t, what\u2019s fixed first and why",
             "Re-answer the Week 1 two questions; file every incident as a future regression test"),
        ],
    ),
]


def set_cell(cell, text, bold=False, size=11, color=INK, bg=None, align=PP_ALIGN.LEFT):
    cell.vertical_anchor = MSO_ANCHOR.TOP
    if bg is not None:
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg
    cell.margin_left = Inches(0.12)
    cell.margin_right = Inches(0.12)
    cell.margin_top = Inches(0.08)
    cell.margin_bottom = Inches(0.08)
    tf = cell.text_frame
    tf.word_wrap = True
    tf.clear()
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text.replace("\n", " ")
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Calibri"


for w in WEEKS:
    slide = prs.slides.add_slide(BLANK)
    # background
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = WHITE
    # dark header band
    band = slide.shapes.add_shape(1, Inches(0), Inches(0), prs.slide_width, Inches(1.55))
    band.fill.solid()
    band.fill.fore_color.rgb = DARK
    band.line.fill.background()
    # title
    tx = slide.shapes.add_textbox(Inches(0.55), Inches(0.28), Inches(12.2), Inches(0.65))
    p = tx.text_frame.paragraphs[0]
    p.text = w["title"]
    r = p.runs[0]
    r.font.size = Pt(30)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = "Calibri"
    # subtitle
    st = slide.shapes.add_textbox(Inches(0.55), Inches(0.92), Inches(12.2), Inches(0.5))
    p = st.text_frame.paragraphs[0]
    p.text = w["subtitle"]
    r = p.runs[0]
    r.font.size = Pt(15)
    r.font.italic = True
    r.font.color.rgb = MUTED
    r.font.name = "Calibri"

    n_rows = len(w["rows"]) + 1
    n_cols = len(w["cols"]) + 1
    left, top = Inches(0.45), Inches(1.85)
    width, height = Inches(12.43), Inches(5.15)
    table_shape = slide.shapes.add_table(n_rows, n_cols, left, top, width, height)
    table = table_shape.table
    # column widths: label col narrower
    table.columns[0].width = Inches(2.15)
    for i in range(1, n_cols):
        table.columns[i].width = Inches((12.43 - 2.15) / (n_cols - 1))
    # header row
    set_cell(table.cell(0, 0), "", bg=HDR_BG)
    for j, c in enumerate(w["cols"]):
        set_cell(table.cell(0, j + 1), c, bold=True, size=15, bg=HDR_BG, align=PP_ALIGN.CENTER)
    # body rows
    for i, (label, *cells) in enumerate(w["rows"], start=1):
        set_cell(table.cell(i, 0), label, bold=True, size=12, bg=ROW_BG)
        for j, text in enumerate(cells):
            set_cell(table.cell(i, j + 1), text, size=10.5, color=SUB)
    # grid lines
    for i in range(n_rows):
        for j in range(n_cols):
            cell = table.cell(i, j)
            for edge in ("top", "left", "bottom", "right"):
                ln = getattr(cell, edge + "_line", None)

    # footer
    ft = slide.shapes.add_textbox(Inches(0.55), Inches(7.08), Inches(12.2), Inches(0.3))
    p = ft.text_frame.paragraphs[0]
    p.text = "AI Evals in Practice \u00b7 ByteByteGo"
    p.alignment = PP_ALIGN.RIGHT
    r = p.runs[0]
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor(0x9A, 0xA5, 0x9A)
    r.font.name = "Calibri"

out = "/home/hatch/workspace/AI-Agent-Evals-Course/weekly-learning-tactics.pptx"
prs.save(out)
print("saved:", out)
