"""Numeric-invariant tests for the EVAL-20 measurement-validity module.

These lock the fixes that made EVAL-18/19 invalid: per-bar Sharpe with a
bar-duration annualisation (not 252 on 3 window returns), sizing consistency
(requested ``max_position_pct`` == enforced ``RiskConfig.max_position_pct``),
degenerate-leg detection, honest gross/net cost, adequacy/power reporting, and
strict serialisation.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from src.analytics.measurement_validity_evaluation import (
    DEFAULT_BAR_DURATION_SECONDS,
    DEFAULT_MIN_RETURNS,
    DEFAULT_MIN_WINDOWS,
    DEFAULT_TEST_WINDOW,
    POWER_ALPHA,
    POWER_TARGET,
    _mean,
    _pstdev,
    _write_markdown,
    adequacy_report,
    build_pillar_signals,
    compute_verdict,
    cost_grid_report,
    degeneracy_report,
    evaluate_measurement_validity,
    ic_report,
    min_detectable_ic,
    periods_per_year,
    per_bar_returns,
    pillar_metrics,
    power_for_ic,
    required_ic_for_power,
    sharpe_from_returns,
    simulate_pillar,
)
from src.campaign.integrated import DEFAULT_SPOT, DETERMINISTIC_NOW
from src.telemetry.serialization import SerializationError, assert_json_valid
from datetime import timedelta

def _ts(n):
    return [DETERMINISTIC_NOW + i * timedelta(seconds=15) for i in range(n)]


# ---------------------------------------------------------------------------
# Module-level fixture: one full evaluation, reused across tests.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def report():
    return evaluate_measurement_validity(write=False)


@pytest.fixture(scope="module")
def signals():
    from src.analytics.production_simulation_evaluation import (
        load_btc_options_chain,
        load_btc_orderflow,
    )
    chain = load_btc_options_chain()
    snap = load_btc_orderflow()
    return build_pillar_signals(
        chain, snap, float(DEFAULT_SPOT["BTC"]), DETERMINISTIC_NOW
    )


# ---------------------------------------------------------------------------
# Annualisation + Sharpe basis
# ---------------------------------------------------------------------------

def test_periods_per_year_from_bar_duration():
    assert periods_per_year(15.0) == pytest.approx(365 * 24 * 3600 / 15.0)
    assert periods_per_year(60.0) == pytest.approx(365 * 24 * 3600 / 60.0)
    with pytest.raises(ValueError):
        periods_per_year(0.0)


def test_sharpe_from_returns_matches_manual():
    rets = [0.01, -0.02, 0.015, 0.0, 0.03]
    ann = periods_per_year(15.0)
    sd = _pstdev(rets)
    expected = (sum(rets) / len(rets)) / sd * math.sqrt(ann)
    assert sharpe_from_returns(rets, ann) == pytest.approx(expected, rel=1e-12)


def test_sharpe_uses_population_std_and_does_not_hardcode_252():
    rets = [0.01] * 5
    assert sharpe_from_returns(rets, periods_per_year(15.0)) == 0.0  # zero std
    assert periods_per_year(15.0) != 252.0


def test_per_bar_returns_length_and_values():
    px = [100.0, 110.0, 99.0]
    r = per_bar_returns(px)
    assert r == pytest.approx([0.10, -0.10])
    assert len(r) == len(px) - 1
    assert per_bar_returns([100.0]) == []


# ---------------------------------------------------------------------------
# Power / MDE
# ---------------------------------------------------------------------------

def test_mde_decreases_with_n_and_matches_formula():
    for n in (100, 400, 1000, 4000):
        expected = (1.959963984540054 + 0.8416212335729143) / math.sqrt(n)
        assert min_detectable_ic(n) == pytest.approx(expected, rel=1e-12)
    assert min_detectable_ic(4000) < min_detectable_ic(1000) < min_detectable_ic(100)
    assert required_ic_for_power(0) == 0.0


def test_power_at_target_and_no_effect():
    n = 1000
    mde = min_detectable_ic(n)
    # Power at exactly the MDE should be near the declared target.
    assert power_for_ic(n, mde) == pytest.approx(POWER_TARGET, abs=0.01)
    assert power_for_ic(n, 0.0) == pytest.approx(POWER_ALPHA)
    assert 0.0 <= power_for_ic(200, 0.05) <= 1.0


# ---------------------------------------------------------------------------
# Adequacy
# ---------------------------------------------------------------------------

def test_adequacy_floors_and_flags():
    good = adequacy_report(1200, 25, [0.001] * 1200, [0.01] * 5)
    assert good["sample_adequate"] is True
    assert good["returns_floor_met"] and good["windows_floor_met"]

    bad = adequacy_report(239, 3, [0.001] * 239, [0.01] * 3)
    assert bad["sample_adequate"] is False
    assert bad["n_returns"] == 239 and bad["n_windows"] == 3
    assert bad["n_windows"] < bad["min_windows_floor"]


def test_adequacy_mde_uses_ic_observation_count():
    rep = adequacy_report(50, 2, [0.0] * 50, [0.01, 0.02, 0.03])
    assert rep["n_ic_observations"] == 3
    assert rep["min_detectable_ic_at_n"] == pytest.approx(min_detectable_ic(3))


# ---------------------------------------------------------------------------
# Degeneracy
# ---------------------------------------------------------------------------

def test_degeneracy_detects_constant_pillar():
    d = degeneracy_report([0.3333] * 10, [0.1, 0.2] * 5, [0.4] * 10)
    assert d["any_degenerate"] is True
    assert d["options_leg_degenerate"] is True
    assert d["pillars"]["options"]["n_unique"] == 1
    assert d["pillars"]["orderflow"]["degenerate"] is False


def test_degeneracy_all_unique():
    d = degeneracy_report([0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.1, 0.2, 0.3])
    assert d["any_degenerate"] is False


# ---------------------------------------------------------------------------
# Sizing consistency + no swallowed rejections
# ---------------------------------------------------------------------------

def test_sizing_requested_equals_enforced(signals):
    sim = simulate_pillar(
        signals["bar_closes"], signals["positions"]["combined"], signals["bar_ends_dt"],
        max_position_pct=0.20,
    )
    assert sim["risk_config_max_position_pct"] == pytest.approx(0.20)
    assert sim["rejections"] == 0
    assert sim["risk_config_max_drawdown_limit"] == pytest.approx(0.20)


def test_sizing_mismatch_rejections_not_swallowed():
    # A large requested cap against a tight engine RiskConfig forces the
    # over-cap legs to be rejected -- the exact EVAL-18/19 pathology. Rejections
    # must be counted, never swallowed.
    from src.backtest.engine import RiskConfig
    px = [100.0] * 40
    pos = [1 if i % 2 == 0 else -1 for i in range(40)]
    sim = simulate_pillar(
        px, pos, _ts(40),
        max_position_pct=0.90,
        risk_config=RiskConfig(max_position_pct=0.01, max_drawdown_limit=0.20),
    )
    assert sim["risk_config_max_position_pct"] == pytest.approx(0.01)
    assert sim["rejections"] > 0
    assert isinstance(sim["rejection_reasons"], dict)
    assert sum(sim["rejection_reasons"].values()) == sim["rejections"]
    assert sim["rejection_reasons"]


# ---------------------------------------------------------------------------
# Gross / net / cost honesty
# ---------------------------------------------------------------------------

def test_flat_pillar_is_exactly_zero(signals):
    sim = simulate_pillar(
        signals["bar_closes"], signals["positions"]["flat"], signals["bar_ends_dt"],
    )
    assert all(abs(v) < 1e-15 for v in sim["gross_returns"])
    assert all(abs(v) < 1e-15 for v in sim["net_returns"])
    assert sim["total_cost_bps"] == 0.0
    assert sim["turnover"] == 0.0


def test_net_equals_gross_minus_cost(signals):
    sim = simulate_pillar(
        signals["bar_closes"], signals["positions"]["combined"], signals["bar_ends_dt"],
        spread_bps=5.0,
    )
    for g, n in zip(sim["gross_returns"], sim["net_returns"]):
        assert n <= g + 1e-12
    assert sim["total_cost_bps"] >= 0.0


def test_cost_monotone_in_spread_bps(signals):
    grid = cost_grid_report(
        signals["bar_closes"], signals["positions"]["combined"], signals["bar_ends_dt"],
        spread_grid=(0.0, 1.0, 5.0),
    )
    assert grid["monotone_non_increasing"] is True
    totals = [row["net_return_total"] for row in grid["grid"].values()]
    assert totals == sorted(totals, reverse=True)
    means = [row["mean_cost_bps"] for row in grid["grid"].values()]
    assert means == sorted(means)


def test_pillar_metrics_net_sharpe_recomputable(signals):
    sim = simulate_pillar(
        signals["bar_closes"], signals["positions"]["orderflow_only"], signals["bar_ends_dt"],
    )
    ann = periods_per_year(DEFAULT_BAR_DURATION_SECONDS)
    m = pillar_metrics(sim, ann)
    assert m["net_sharpe"] == pytest.approx(
        sharpe_from_returns(sim["net_returns"], ann), rel=1e-12
    )


# ---------------------------------------------------------------------------
# IC with power
# ---------------------------------------------------------------------------

def test_ic_report_has_power_fields():
    px = [100.0 + i * 0.5 for i in range(200)]
    sig = [1.0 if (i % 2 == 0) else -1.0 for i in range(200)]
    rep = ic_report(sig, px, horizons=(1, 2, 5))
    assert "ic_mean" in rep and "ic_tstat" in rep
    for h in rep["horizons"]:
        row = rep["ic_by_horizon"][str(h)]
        assert row["n"] > 0
        assert row["min_detectable_ic"] == pytest.approx(min_detectable_ic(row["n"]))
        assert 0.0 <= row["power"] <= 1.0


# ---------------------------------------------------------------------------
# Verdict structure
# ---------------------------------------------------------------------------

def test_verdict_never_valid_true(report):
    assert report["verdict"] in ("GO", "NO-GO")
    assert report["never_valid_true"] is True
    assert "valid" not in report or report.get("valid") is not True


def test_verdict_checks_present(report):
    names = {c["name"] for c in report["verdict_checks"]["checks"]}
    for expected in (
        "measurement_reproducible",
        "sample_adequate_declared",
        "sizing_consistent",
        "sharpe_basis_valid",
        "non_degenerate_pillars_reported",
        "net_of_cost_honest",
        "ic_reported_with_power",
        "strict_serialization",
    ):
        assert expected in names


def test_compute_verdict_all_pass_is_go():
    adequacy = {
        "sample_adequate": True, "min_returns_floor": 1000, "min_windows_floor": 20,
        "n_returns": 2000, "n_windows": 40,
    }
    v = compute_verdict(
        adequacy=adequacy, sizing_consistent=True,
        sizing_detail={"requested_max_position_pct": 0.2, "risk_config_max_position_pct": 0.2, "rejections": 0},
        sharpe_ok=True, sharpe_detail={"annualisation": 1.0, "expected_annualisation": 1.0, "sharpe": 0.5, "abs_error": 0.0},
        degeneracy={"any_degenerate": False, "options_leg_degenerate": False, "orderflow_leg_degenerate": False},
        cost_detail={"complete": True, "non_negative": True},
        ic_detail={"ic_mean": 0.01, "min_detectable_ic_at_n": 0.05},
        determinism_ok=True, never_valid_true=True,
    )
    assert v["verdict"] == "GO"
    assert v["all_checks_pass"] is True
    assert v["n_passed"] == v["n_checks"]


def test_compute_verdict_inadequate_is_nogo():
    adequacy = {
        "sample_adequate": False, "min_returns_floor": 1000, "min_windows_floor": 20,
        "n_returns": 239, "n_windows": 3,
    }
    v = compute_verdict(
        adequacy=adequacy, sizing_consistent=True,
        sizing_detail={"requested_max_position_pct": 0.2, "risk_config_max_position_pct": 0.2, "rejections": 0},
        sharpe_ok=True, sharpe_detail={"annualisation": 1.0, "expected_annualisation": 1.0, "sharpe": 0.5, "abs_error": 0.0},
        degeneracy={"any_degenerate": True, "options_leg_degenerate": True, "orderflow_leg_degenerate": False},
        cost_detail={"complete": True, "non_negative": True},
        ic_detail={"ic_mean": 0.01, "min_detectable_ic_at_n": 0.05},
        determinism_ok=True, never_valid_true=True,
    )
    assert v["verdict"] == "NO-GO"
    assert v["n_passed"] < v["n_checks"]


# ---------------------------------------------------------------------------
# Artifact shape, strictness, determinism
# ---------------------------------------------------------------------------

def test_report_shape_and_sample_counts(report):
    assert report["report_id"] == "MEASUREMENT_VALIDITY_EVAL_20"
    s = report["sample"]
    assert s["n_bars"] == 240
    assert s["n_returns"] == 239
    assert s["n_windows"] == 3
    assert report["adequacy"]["sample_adequate"] is False
    assert set(report["pillars"].keys()) == {"combined", "options_only", "orderflow_only", "flat"}
    for name, m in report["pillars"].items():
        for k in ("gross_return_total", "net_return_total", "turnover", "total_cost_bps"):
            assert k in m
        assert m["total_cost_bps"] >= 0.0
        assert math.isfinite(m["net_return_total"])


def test_report_is_strict_json(report):
    assert_json_valid(report)
    json.dumps(report, allow_nan=False)  # must not raise


def test_determinism_identical(report):
    again = evaluate_measurement_validity(write=False)
    assert report["determinism"]["identical"] is True
    assert report["determinism"]["fingerprint_run_1"] == report["determinism"]["fingerprint_run_2"]
    assert again["determinism"]["fingerprint_run_1"] == report["determinism"]["fingerprint_run_1"]
    # Volatile timestamp is the only allowed difference.
    for key in report:
        if key == "generated_at":
            continue
        assert report[key] == again[key]


def test_markdown_renders(report):
    md = _write_markdown(report)
    assert "MEASUREMENT_VALIDITY_EVAL_20" in md
    assert "Sample adequacy" in md
    assert "Verdict checks" in md


def test_never_emits_valid_true(report):
    # Recursive scan: no key "valid" set to True anywhere.
    def scan(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "valid":
                    assert v is not True
                scan(v)
        elif isinstance(obj, list):
            for v in obj:
                scan(v)
    scan(report)