"""Unit tests for EVAL-46 integrated options+orderflow audit (pure helpers)."""

from __future__ import annotations

import math

from scripts.eval46_integrated_options_orderflow_audit import (
    FUSION_RULES,
    _expanding_zscore,
    _gated_positions,
    _mean,
    _sharpe_of_returns,
    fuse_continuous_zscore,
    fuse_regime_filter,
    fuse_sign_agreement,
    kill_switch_breach,
    pooled_verdict,
)


def test_fusion_rules_registered():
    assert FUSION_RULES == ("sign_agreement", "regime_filter", "continuous_zscore")


def test_gated_positions_toxicity_gate():
    sig = [0.5, 0.5, 0.5]
    tox = [0.1, 0.9, 0.1]
    assert _gated_positions(sig, tox) == [1, 0, 1]


def test_sign_agreement_requires_both_signs():
    opt = [0.5, -0.5, 0.5, -0.5]
    of = [0.5, 0.5, -0.5, -0.5]
    tox = [0.0, 0.0, 0.0, 0.0]
    # agree long, disagree, disagree, agree short
    assert fuse_sign_agreement(opt, of, tox) == [1, 0, 0, -1]


def test_regime_filter_product():
    opt = [0.5, 0.5, -0.5, -0.5]
    of = [0.5, -0.5, 0.5, -0.5]
    tox = [0.0, 0.0, 0.0, 0.0]
    # +1*+1=+1, +1*-1=-1, -1*+1=-1, -1*-1=+1
    assert fuse_regime_filter(opt, of, tox) == [1, -1, -1, 1]


def test_regime_filter_toxicity_gate():
    opt = [0.5]
    of = [0.5]
    tox = [0.9]
    assert fuse_regime_filter(opt, of, tox) == [0]


def test_expanding_zscore_causal_and_zero_warmup():
    xs = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    zs = _expanding_zscore(xs, min_periods=5)
    assert len(zs) == len(xs)
    # first 4 are warmup zeros
    assert zs[:4] == [0.0, 0.0, 0.0, 0.0]
    # value 5 vs mean(1..5)=3, std=sqrt(2)-> ~1.414 ; value 6 vs mean(1..6)=3.5
    assert zs[4] > 0.0
    assert zs[5] > 0.0


def test_continuous_zscore_thresholds():
    opt = [0.0] * 10 + [5.0]
    of = [0.0] * 10 + [5.0]
    tox = [0.0] * 11
    pos = fuse_continuous_zscore(opt, of, tox, z_threshold=0.5)
    # the last bar has a large positive combined z -> long
    assert pos[-1] == 1
    # early bars are flat (warmup / small z)
    assert pos[0] == 0


def test_kill_switch_breach():
    assert kill_switch_breach(0.21) is True
    assert kill_switch_breach(0.20) is False
    assert kill_switch_breach(0.0) is False


def test_sharpe_and_mean():
    assert _mean([1.0, 2.0, 3.0]) == 2.0
    assert _sharpe_of_returns([0.0, 0.0]) == 0.0
    assert math.isfinite(_sharpe_of_returns([0.01, -0.02, 0.03, 0.0]))


def _mk_tape_result(rule, sharpe, dd, perm_p, ci_lower, breach):
    return {
        "rule": rule,
        "combined": {"oos_sharpe": sharpe, "oos_max_drawdown": dd},
        "permutation_p": perm_p,
        "bootstrap_ci": [0.0, ci_lower, 0.0],
        "kill_switch_breach": breach,
    }


def test_pooled_verdict_nogo_when_one_tape_fails():
    tapes = [
        {"name": "a", "rule_results": [
            _mk_tape_result("sign_agreement", 2.0, 0.1, 0.01, 0.5, False),
        ]},
        {"name": "b", "rule_results": [
            _mk_tape_result("sign_agreement", -1.0, 0.3, 0.4, -0.2, True),
        ]},
    ]
    v = pooled_verdict(tapes)
    assert v["passed"] is False
    assert v["verdict"].startswith("NO-GO")


def test_pooled_verdict_go_when_both_tapes_pass():
    tapes = [
        {"name": "a", "rule_results": [
            _mk_tape_result("regime_filter", 2.0, 0.1, 0.01, 0.5, False),
        ]},
        {"name": "b", "rule_results": [
            _mk_tape_result("regime_filter", 1.5, 0.12, 0.02, 0.3, False),
        ]},
    ]
    v = pooled_verdict(tapes)
    assert v["passed"] is True
    assert v["go_rule"] == "regime_filter"
    assert v["verdict"].startswith("FALSIFIED")


def test_pooled_verdict_go_requires_ci_lower_positive():
    tapes = [
        {"name": "a", "rule_results": [
            _mk_tape_result("sign_agreement", 2.0, 0.1, 0.01, 0.0, False),
        ]},
        {"name": "b", "rule_results": [
            _mk_tape_result("sign_agreement", 1.5, 0.12, 0.02, 0.3, False),
        ]},
    ]
    v = pooled_verdict(tapes)
    assert v["passed"] is False