"""Smoke tier: runs on every change in a few seconds (Chapter 22)."""
import pytest
from pronto.agents import ScriptedAgent
from evals.harness import load_cases, run_case


@pytest.mark.parametrize("case", load_cases("smoke"), ids=lambda c: c["id"])
def test_careful_agent_passes_smoke(case):
    assert all(r["verdict"] == "pass" for r in run_case(ScriptedAgent(careful=True), case, trials=4))


def test_naive_agent_double_refunds_on_timeout():
    case = next(c for c in load_cases("smoke") if c["dims"]["condition"] == "timeout_after_commit")
    assert run_case(ScriptedAgent(careful=False), case)[0]["reason"] == "violated: never_twice"
