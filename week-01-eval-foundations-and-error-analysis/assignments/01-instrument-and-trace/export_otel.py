"""Week 1, Assignment 1 helper: export the 30 inputs as OTel traces.

Zero-key, zero-LangSmith path (Path B). Runs inputs.json through
CustomerServiceAgent(demo=True), records one trace per input (root span
"pronto.support_session" -> "agent.turn" spans -> "tool.*" spans), and
writes pronto-traces.json in OTLP JSON format.

Upload the file to the course Trace Viewer and annotate all 30 traces
there — no API keys, no LangSmith project needed:

    python export_otel.py
    # then open https://coachmanjeet.github.io/AI-Agent-Evals-Course/trace-viewer/
    # and upload pronto-traces.json
"""

import json
import secrets
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "agent"))
from agent import CustomerServiceAgent  # noqa: E402

TOOL_METHODS = ["get_order_status", "lookup_policy", "issue_refund", "escalate_to_human"]
TRACE_VIEWER_URL = "https://coachmanjeet.github.io/AI-Agent-Evals-Course/trace-viewer/"
MIN_DURATION_NS = 1_000_000  # 1 ms floor so every span renders in the viewer


def trunc(text, n):
    text = str(text)
    return text if len(text) <= n else text[:n] + "…"


def load_inputs(path: str = "inputs.json") -> list:
    with open(HERE / path) as f:
        inputs = json.load(f)
    assert len(inputs) == 30, f"expected 30 inputs, got {len(inputs)}"
    return inputs


class Tracer:
    """Builds OTLP-style spans for one input, with a span stack so tool
    calls parent under the turn span (and nested tool calls parent correctly)."""

    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self.spans = []
        self.stack = []  # span_ids, innermost last

    def new_span(self, name: str, attributes: list) -> dict:
        span = {
            "traceId": self.trace_id,
            "spanId": secrets.token_hex(8),
            "name": name,
            "kind": 1,
            "attributes": attributes,
            "status": {"code": 1},
        }
        if self.stack:
            span["parentSpanId"] = self.stack[-1]
        return span

    def finish(self, span: dict, start_ns: int) -> None:
        end_ns = time.time_ns()
        if end_ns - start_ns < MIN_DURATION_NS:
            end_ns = start_ns + MIN_DURATION_NS
        span["startTimeUnixNano"] = str(start_ns)
        span["endTimeUnixNano"] = str(end_ns)
        self.spans.append(span)

    def wrap_tool(self, original, method_name: str):
        """Wrap a bound tool method so each call records a child span."""

        def wrapper(*args, **kwargs):
            span = self.new_span(
                f"tool.{method_name}",
                [{"key": "tool.args",
                  "value": {"stringValue": trunc(json.dumps({"args": args, "kwargs": kwargs}, default=str), 500)}}],
            )
            self.stack.append(span["spanId"])
            start_ns = time.time_ns()
            try:
                result = original(*args, **kwargs)
                span["attributes"].append(
                    {"key": "tool.result",
                     "value": {"stringValue": trunc(json.dumps(result, default=str), 800)}})
                return result
            except Exception as e:  # record the failure, then let the input handler deal with it
                span["status"] = {"code": 2, "message": trunc(str(e), 200)}
                raise
            finally:
                self.stack.pop()
                self.finish(span, start_ns)

        return wrapper


def trace_input(agent, tracer: Tracer, item: dict, index: int) -> dict:
    """Run one input through the agent and return its OTLP resourceSpan.

    Tool calls are recorded by wrappers installed by the caller on the same
    tracer, so tool spans parent correctly under their turn span.
    """
    messages = item["messages"] if isinstance(item, dict) else [item]
    category = item.get("category", "?") if isinstance(item, dict) else "?"

    root = tracer.new_span("pronto.support_session", [
        {"key": "input.category", "value": {"stringValue": category}},
        {"key": "input.index", "value": {"stringValue": str(index)}},
    ])
    root_start = time.time_ns()
    tracer.stack.append(root["spanId"])  # turns parent under the root

    try:
        for t, msg in enumerate(messages):
            turn = tracer.new_span(f"agent.turn", [
                {"key": "turn.index", "value": {"stringValue": str(t)}},
                {"key": "user.message", "value": {"stringValue": trunc(msg, 500)}},
            ])
            tracer.stack.append(turn["spanId"])
            turn_start = time.time_ns()
            try:
                reply = agent.run(msg)
                turn["attributes"].append(
                    {"key": "agent.reply", "value": {"stringValue": trunc(reply, 800)}})
            finally:
                tracer.stack.pop()
                tracer.finish(turn, turn_start)
    except Exception as e:
        root["status"] = {"code": 2, "message": trunc(str(e), 200)}
    finally:
        tracer.stack.pop()

    tracer.finish(root, root_start)

    return {
        "resource": {
            "attributes": [
                {"key": "service.name", "value": {"stringValue": "pronto-support-agent"}}
            ]
        },
        "scopeSpans": [{"scope": {"name": "pronto-agent"}, "spans": tracer.spans}],
    }


def main() -> None:
    agent = CustomerServiceAgent(demo=True)

    # Record tool calls as child spans. Wrap per input (each input gets its
    # own tracer), restore the originals afterwards.
    originals = {name: getattr(agent, name) for name in TOOL_METHODS}

    inputs = load_inputs()
    resource_spans = []
    total_spans = 0

    for i, item in enumerate(inputs):
        category = item.get("category", "?") if isinstance(item, dict) else "?"
        messages = item["messages"] if isinstance(item, dict) else [item]

        tracer = Tracer(secrets.token_hex(16))
        for name in TOOL_METHODS:
            setattr(agent, name, tracer.wrap_tool(originals[name], name))

        resource_spans.append(trace_input(agent, tracer, item, i))
        total_spans += len(resource_spans[-1]["scopeSpans"][0]["spans"])
        print(f"[{i+1}/30] {category}: {messages[-1][:80]}")

    for name, original in originals.items():  # restore the agent's real methods
        setattr(agent, name, original)

    out = {"resourceSpans": resource_spans}
    out_path = HERE / "pronto-traces.json"
    with open(out_path, "w") as f:
        json.dump(out, f)
    print(f"Wrote pronto-traces.json ({len(resource_spans)} traces, {total_spans} spans)"
          f" — upload it at {TRACE_VIEWER_URL}")


if __name__ == "__main__":
    main()
