# Trace Viewer

A static, in-browser **OTel trace viewer for error analysis** — a **Week 1**
tool. Upload an agent's OpenTelemetry trace JSON, browse the span waterfall,
inspect attributes/events, and annotate each trace with a failure mode from the
course's Pronto taxonomy. Annotations export as JSON/CSV — the seed of the
eval dataset you build next.

## Run locally

```bash
cd docs && python3 -m http.server 8000
# open: http://localhost:8000/trace-viewer/
```

Click **Load the Pronto sample** (or open the sample directly) to try it with
no setup: 6 Pronto support-agent traces covering 5 failure modes plus one clean
trace.

## Live URL (once Pages is enabled)

`https://coachmanjeet.github.io/AI-Agent-Evals-Course/trace-viewer/`

To enable: repo Settings → Pages → Deploy from a branch → `main` → `/docs`.

## What it accepts

Be liberal in what you read — any of:

- **OTLP JSON**: `{"resourceSpans":[{"resource":{},"scopeSpans":[{"spans":[...]}]}]}`
- Flat `{"spans":[...]}` · a bare `[...]` span array · a single span object

Each span needs `traceId`, `spanId`, `name`, and start/end times
(`startTimeUnixNano`/`endTimeUnixNano`, also ISO strings). Attributes in OTLP
`[{key, value:{stringValue|intValue|boolValue|…}}]` form are flattened; missing
values are shown as "—", never dropped. Unrecognized files get a friendly
error naming exactly what was expected.

## Exporting traces from common tools

- **Arize Phoenix**: open a trace → ⋯ menu → **Export trace as JSON**
  (or use the Phoenix client's `px.Client().get_trace_dataset` and save the
  OTLP JSON).
- **Langfuse**: traces can be exported in OpenTelemetry format —
  use the Langfuse OTel endpoint / API to pull `resourceSpans` JSON and save
  it to a file.
- **Any OTel SDK / collector**: export spans as OTLP JSON
  (`otlpjson` exporter or the `/v1/traces` HTTP endpoint payload) and open the
  file here.

## Workflow (Week 1 error analysis)

1. Upload traces (or load the sample).
2. Scan the trace list — **Errors only** surfaces spans with `ERROR` status.
3. Click a trace: the waterfall shows the span tree with durations; red spans
   failed. Click any span for attributes (gen_ai/llm/tool first), events,
   status, and timestamps.
4. **Annotate this trace**: pick the failure mode + a free-text note.
   Annotations auto-save in your browser (`localStorage`, keyed by trace ID)
   and survive file re-uploads.
5. **Export JSON/CSV** — 📦 these annotations are the seed of your eval
   dataset: each labeled trace becomes a gold example for the evals you build
   next (Week 2+).

## Files

| File | What it is |
|------|------------|
| `index.html` | Standalone page shell — all styles inlined, no dependency on any other site |
| `viewer.js` | All logic: OTel parsing, tree/waterfall rendering, annotation, export |
| `sample-pronto-otel-traces.json` | 6 sample traces (clean, over_refund, prompt_injection_compliance, wrong_order_status, missing_escalation, pii_leak) |

Fully self-contained: the only external requests are public CDNs
(Google Fonts, Salesforce Lightning Design System). Nothing you upload ever
leaves your browser.
