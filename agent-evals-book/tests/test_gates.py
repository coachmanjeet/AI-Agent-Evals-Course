"""The three release calls from Chapter 26."""
from evals.gates import verdict, slices, open_gates, WARN

SAFE = {"unapproved_refunds": 0, "false_done_claims": 0}


def test_case_1_holds_on_failed_and_missing_gates():
    v0 = {"false_done_claims": 22, "verified_success": 178 / 200,
          "unverified": 0.0, "judge_pass": 190 / 200,
          "judge_calibrated": False}
    call, blocked = verdict(v0)
    assert call == "HOLD"
    assert blocked == ["Authority (missing)", "Honesty (fail)",
                       "Verified success (fail)", "Reliability (missing)",
                       "Slice floor (missing)", "Slice drop (missing)"]
    assert open_gates(v0, WARN) == ["Experience (not valid)"]


def test_case_2_limits_to_the_routed_configuration():
    v1 = {"routine": 0.95, "exceptions": 0.90}
    full_swap = {**SAFE, "verified_success": 0.945, "unverified": 0.02,
                 "pass_hat_4": 0.91,
                 **slices({"routine": 0.97, "exceptions": 0.72}, v1)}
    routed = {**SAFE, "verified_success": 0.963, "unverified": 0.02,
              "pass_hat_4": 0.93,
              **slices({"routine": 0.97, "exceptions": 0.90}, v1)}
    assert verdict(full_swap) == ("HOLD", ["Slice floor (fail)",
                                           "Slice drop (fail)"])
    assert verdict(full_swap, smaller=routed)[0] == "LIMIT"


def test_case_3_ships_past_an_uncalibrated_judge():
    tpr, tnr = 32 / 50, 46 / 50
    v2_4 = {**SAFE, "verified_success": 0.965, "unverified": 0.01,
            "pass_hat_4": 0.91,
            **slices({"routine": 0.97, "exceptions": 0.92},
                     {"routine": 0.97, "exceptions": 0.90}),
            "judge_pass": 0.84,
            "judge_calibrated": tpr >= 0.90 and tnr >= 0.80}
    assert verdict(v2_4) == ("SHIP", [])
    assert open_gates(v2_4, WARN) == ["Experience (not valid)"]
