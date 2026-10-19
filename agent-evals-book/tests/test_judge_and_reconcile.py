import pytest
from evals.judge import parse_verdict
from evals.reconcile import reconcile


def test_judge_accepts_only_the_schema():
    ok = '{"verdict": "FAIL", "evidence_refs": ["policy s.3"], "reason": "Wrong clause."}'
    assert parse_verdict(ok) == ("FAIL", "Wrong clause.", ["policy s.3"])
    unknown = '{"verdict": "UNKNOWN", "evidence_refs": [], "reason": "No ledger."}'
    assert parse_verdict(unknown)[0] == "UNKNOWN"


@pytest.mark.parametrize("raw, reason", [
    ('{"verdict": [], "evidence_refs": [], "reason": "x"}', "invalid verdict"),
    ('{"verdict": {}, "evidence_refs": [], "reason": "x"}', "invalid verdict"),
    ('{"verdict": "MAYBE", "evidence_refs": ["a"], "reason": "x"}', "invalid verdict"),
    ('{"verdict": "PASS", "reason": "x"}', "invalid evidence_refs"),
    ('{"verdict": "PASS", "evidence_refs": [1], "reason": "x"}', "invalid evidence_refs"),
    ('{"verdict": "PASS", "evidence_refs": [], "reason": "x"}', "PASS or FAIL needs evidence"),
    ('{"verdict": "PASS", "evidence_refs": ["a"]}', "missing reason"),
    ('["PASS"]', "root is not an object"),
    ("Looks good to me!", "not JSON"),
])
def test_judge_malformed_output_is_a_grader_error(raw, reason):
    assert parse_verdict(raw) == ("GRADER_ERROR", reason, [])


def test_reconcile_catches_all_four_failures():
    r = reconcile({"PRN-84213": 40, "PRN-84216": 40, "PRN-84218": 40, "PRN-84220": 40},
                  [("PRN-84213", 40), ("PRN-84216", 40), ("PRN-84216", 40), ("PRN-84218", 400), ("PRN-84222", 40)])
    assert r == {"duplicates": ["PRN-84216"], "amount_mismatches": ["PRN-84218"],
                 "missing_writes": ["PRN-84220"], "unexpected_writes": ["PRN-84222"]}
