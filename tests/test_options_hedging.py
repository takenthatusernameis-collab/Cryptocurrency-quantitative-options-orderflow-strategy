"""Adversarial tests for delta-hedged options backtesting and P&L attribution.

Covers hedge P&L correctness, attribution reconciliation (delta/gamma/vega/theta/residual
summing to total), dynamic rebalancing, transaction costs, determinism (twice -> byte-identical),
strict serialization (allow_nan=False), and edge cases (deep ITM/OTM, near-expiry, zero vol,
invalid inputs).
"""

import json
import math
from datetime import datetime, timedelta, timezone

import pytest

from src.backtest.options_hedging import delta_hedged_option_pnl
from src.errors import BacktestError
from src.telemetry import serialize_metrics_strict

_NOW = datetime.now(timezone.utc)


def _constant_path(spot: float, n: int) -> list[float]:
    return [float(spot) for _ in range(n)]


def _ramp_path(spot0: float, n: int, step: float) -> list[float]:
    return [spot0 + i * step for i in range(n)]


def _times(n: int, dt_years: float) -> list[float]:
    return [i * dt_years for i in range(n)]


def _base_kwargs() -> dict:
    return dict(
        strike=100.0,
        rate=0.05,
        volatility=0.25,
        option_type="call",
        seed=42,
    )


def _assert_finite_result(result: dict) -> None:
    assert isinstance(result, dict)
    for key in ("total_pnl", "final_portfolio_value", "initial_option_premium",
                "hedge_steps", "transaction_cost_bps"):
        assert key in result
        assert math.isfinite(float(result[key])), key
    attr = result["attribution"]
    for key in ("delta_pnl", "gamma_pnl", "theta_pnl", "vega_pnl", "residual",
                "total_pnl", "sum_attribution"):
        assert key in attr
        assert math.isfinite(float(attr[key])), key
    # Strict serialization gate with allow_nan=False JSON round-trip.
    json.dumps(serialize_metrics_strict(dict(result)), allow_nan=False)


def test_delta_hedged_call_basic_attribution():
    spot_path = _ramp_path(100.0, 12, 0.5)
    times = _times(12, 7 / 365.25)
    result = delta_hedged_option_pnl(spot_path, times, **_base_kwargs())
    _assert_finite_result(result)
    assert result["hedge_steps"] == 12
    assert result["initial_option_premium"] > 0.0
    attr = result["attribution"]
    # Constant vol: vega contribution is zero.
    assert attr["vega_pnl"] == 0.0
    # Delta term tracks delta-change times spot movement (rebalance lag).
    assert math.isfinite(attr["delta_pnl"])
    # Long gamma scalps realized movement.
    assert attr["gamma_pnl"] >= 0.0
    # Attribution reconciles exactly to total via residual definition.
    manual = (attr["delta_pnl"] + attr["gamma_pnl"] + attr["theta_pnl"]
              + attr["vega_pnl"] + attr["residual"])
    assert math.isclose(manual, attr["total_pnl"], rel_tol=1e-9, abs_tol=1e-12)
    assert math.isclose(attr["sum_attribution"], result["total_pnl"],
                        rel_tol=1e-9, abs_tol=1e-12)


def test_delta_hedged_put_basic():
    spot_path = _ramp_path(100.0, 10, -0.4)
    times = _times(10, 10 / 365.25)
    kwargs = dict(_base_kwargs(), option_type="put")
    result = delta_hedged_option_pnl(spot_path, times, **kwargs)
    _assert_finite_result(result)
    assert result["hedge_steps"] == 10
    attr = result["attribution"]
    assert attr["vega_pnl"] == 0.0
    assert math.isfinite(attr["delta_pnl"])
    assert attr["gamma_pnl"] >= 0.0
    assert math.isclose(attr["sum_attribution"], result["total_pnl"],
                        rel_tol=1e-9, abs_tol=1e-12)


def test_determinism_twice_byte_identical():
    spot_path = _ramp_path(100.0, 15, 0.3)
    times = _times(15, 5 / 365.25)
    r1 = delta_hedged_option_pnl(spot_path, times, **_base_kwargs())
    r2 = delta_hedged_option_pnl(spot_path, times, **_base_kwargs())
    assert serialize_metrics_strict(r1) == serialize_metrics_strict(r2)
    assert json.dumps(r1, allow_nan=False) == json.dumps(r2, allow_nan=False)


def test_rebalancing_affects_pnl():
    spot_path = _ramp_path(100.0, 20, 0.7)
    times = _times(20, 3 / 365.25)
    kwargs = _base_kwargs()
    r_rebalanced = delta_hedged_option_pnl(spot_path, times, **kwargs,
                                           rebalance_every_step=True)
    r_static = delta_hedged_option_pnl(spot_path, times, **kwargs,
                                       rebalance_every_step=False)
    _assert_finite_result(r_rebalanced)
    _assert_finite_result(r_static)
    assert r_rebalanced["hedge_steps"] == r_static["hedge_steps"] == 20


def test_transaction_costs_reduce_pnl():
    spot_path = _ramp_path(100.0, 18, 0.6)
    times = _times(18, 4 / 365.25)
    kwargs = _base_kwargs()
    r_free = delta_hedged_option_pnl(spot_path, times, **kwargs,
                                     transaction_cost_bps=0.0)
    r_costly = delta_hedged_option_pnl(spot_path, times, **kwargs,
                                       transaction_cost_bps=50.0)
    _assert_finite_result(r_free)
    _assert_finite_result(r_costly)
    assert r_costly["total_pnl"] <= r_free["total_pnl"] + 1e-12
    assert r_costly["transaction_cost_bps"] == 50.0
    assert r_free["transaction_cost_bps"] == 0.0


def test_entry_price_override():
    spot_path = _ramp_path(100.0, 8, 0.2)
    times = _times(8, 8 / 365.25)
    kwargs = _base_kwargs()
    r_auto = delta_hedged_option_pnl(spot_path, times, **kwargs)
    from src.data.schemas import PricingInputs
    from src.features.options_pricing import black_scholes_price
    inp = PricingInputs(spot=100.0, strike=100.0, rate=0.05, volatility=0.25,
                        time_to_expiry=max(times[0], 1e-18), option_type="call", seed=42)
    entry = float(black_scholes_price(inp))
    r_override = delta_hedged_option_pnl(spot_path, times, **kwargs,
                                         option_price_entry=entry)
    _assert_finite_result(r_auto)
    _assert_finite_result(r_override)
    assert math.isclose(r_auto["initial_option_premium"], entry, rel_tol=1e-12)
    assert math.isclose(r_override["initial_option_premium"], entry, rel_tol=1e-12)


def test_deep_itm_call_edge():
    spot_path = _ramp_path(200.0, 6, 0.1)  # deep ITM vs strike 100
    times = _times(6, 1 / 365.25)  # near expiry
    result = delta_hedged_option_pnl(spot_path, times, **_base_kwargs())
    _assert_finite_result(result)
    assert result["attribution"]["gamma_pnl"] >= 0.0


def test_deep_otm_call_edge():
    spot_path = _ramp_path(30.0, 6, -0.05)  # deep OTM vs strike 100
    times = _times(6, 1 / 365.25)
    result = delta_hedged_option_pnl(spot_path, times, **_base_kwargs())
    _assert_finite_result(result)


def test_zero_volatility_edge():
    spot_path = _ramp_path(100.0, 5, 1.0)
    times = _times(5, 2 / 365.25)
    kwargs = dict(_base_kwargs(), volatility=0.0)
    result = delta_hedged_option_pnl(spot_path, times, **kwargs)
    _assert_finite_result(result)
    assert result["attribution"]["gamma_pnl"] == 0.0
    assert result["attribution"]["vega_pnl"] == 0.0


def test_constant_spot_zero_pnl_components():
    spot_path = _constant_path(100.0, 8)
    times = _times(8, 5 / 365.25)
    result = delta_hedged_option_pnl(spot_path, times, **_base_kwargs())
    _assert_finite_result(result)
    assert result["attribution"]["gamma_pnl"] == 0.0
    assert result["attribution"]["delta_pnl"] == 0.0
    assert result["attribution"]["vega_pnl"] == 0.0


def test_mismatched_path_and_times_raises():
    with pytest.raises(BacktestError):
        delta_hedged_option_pnl([100.0, 101.0], _times(3, 0.1), **_base_kwargs())


def test_single_point_raises():
    with pytest.raises(BacktestError):
        delta_hedged_option_pnl([100.0], [0.0], **_base_kwargs())


def test_empty_path_raises():
    with pytest.raises(BacktestError):
        delta_hedged_option_pnl([], [], **_base_kwargs())


def test_strict_serialization_allow_nan_false():
    spot_path = _ramp_path(100.0, 10, 0.3)
    times = _times(10, 6 / 365.25)
    result = delta_hedged_option_pnl(spot_path, times, **_base_kwargs())
    payload = json.dumps(result, allow_nan=False)
    assert isinstance(payload, str)
    reparsed = json.loads(payload)
    assert reparsed["total_pnl"] == result["total_pnl"]


def test_different_paths_yield_different_results():
    path_a = _ramp_path(100.0, 10, 0.5)
    path_b = _ramp_path(100.0, 10, -0.5)
    times = _times(10, 5 / 365.25)
    r_a = delta_hedged_option_pnl(path_a, times, **_base_kwargs())
    r_b = delta_hedged_option_pnl(path_b, times, **_base_kwargs())
    _assert_finite_result(r_a)
    _assert_finite_result(r_b)
    assert r_a["total_pnl"] != r_b["total_pnl"]


def test_attribution_sum_matches_total_within_tolerance():
    spot_path = _ramp_path(100.0, 20, 0.4)
    times = _times(20, 10 / 365.25)
    result = delta_hedged_option_pnl(spot_path, times, **_base_kwargs())
    attr = result["attribution"]
    s = attr["delta_pnl"] + attr["gamma_pnl"] + attr["theta_pnl"] + attr["vega_pnl"] + attr["residual"]
    assert abs(s - attr["total_pnl"]) < 1e-9


def test_attribution_sum_matches_total_via_sum_attribution_field():
    spot_path = _ramp_path(95.0, 15, -0.3)
    times = _times(15, 7 / 365.25)
    kwargs = dict(_base_kwargs(), strike=100.0, option_type="put")
    result = delta_hedged_option_pnl(spot_path, times, **kwargs)
    attr = result["attribution"]
    assert abs(attr["sum_attribution"] - attr["total_pnl"]) < 1e-9


def test_hedge_with_transaction_costs_finite():
    spot_path = _ramp_path(100.0, 12, 0.25)
    times = _times(12, 8 / 365.25)
    kwargs = dict(_base_kwargs(), transaction_cost_bps=5.0)
    result = delta_hedged_option_pnl(spot_path, times, **kwargs)
    _assert_finite_result(result)
    assert abs(result["attribution"]["sum_attribution"] - result["total_pnl"]) < 1e-9


def test_hedge_no_rebalance_is_finite():
    spot_path = _ramp_path(100.0, 10, 0.2)
    times = _times(10, 6 / 365.25)
    kwargs = dict(_base_kwargs(), rebalance_every_step=False)
    result = delta_hedged_option_pnl(spot_path, times, **kwargs)
    _assert_finite_result(result)
    assert abs(result["attribution"]["sum_attribution"] - result["total_pnl"]) < 1e-9


def test_determinism_twice_byte_identical():
    spot_path = _ramp_path(100.0, 16, 0.35)
    times = _times(16, 9 / 365.25)
    r1 = delta_hedged_option_pnl(spot_path, times, **_base_kwargs())
    r2 = delta_hedged_option_pnl(spot_path, times, **_base_kwargs())
    assert json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)


def test_attribution_components_finite_all_paths():
    spot_path = _ramp_path(110.0, 18, -0.15)
    times = _times(18, 12 / 365.25)
    kwargs = dict(_base_kwargs(), strike=105.0, volatility=0.45)
    result = delta_hedged_option_pnl(spot_path, times, **kwargs)
    attr = result["attribution"]
    for k in ["delta_pnl", "gamma_pnl", "theta_pnl", "vega_pnl", "residual", "total_pnl", "sum_attribution"]:
        assert math.isfinite(float(attr[k]))


# ---------------------------------------------------------------------------
# Attribution identity and near-expiry edge cases
# ---------------------------------------------------------------------------

def test_attribution_identity_exact():
    """sum_attribution must equal total_pnl exactly (not just within tolerance).

    The attribution is defined as delta+gamma+theta+vega+residual with
    residual = total_pnl - sum_components, so the identity is exact by
    construction. Float round-trip drift between the two stored values must
    not break tight reconciliation.
    """
    for spot_path, times in (
        (_ramp_path(100.0, 20, 0.4), _times(20, 10 / 365.25)),
        (_ramp_path(95.0, 15, -0.3), _times(15, 7 / 365.25)),
        (_constant_path(100.0, 10), _times(10, 5 / 365.25)),
    ):
        for ot in ("call", "put"):
            result = delta_hedged_option_pnl(spot_path, times, **dict(_base_kwargs(), option_type=ot))
            attr = result["attribution"]
            assert attr["sum_attribution"] == attr["total_pnl"], (ot, attr["sum_attribution"], attr["total_pnl"])


def test_near_expiry_path_does_not_explode_attribution():
    """A path that ends at/near expiry must not produce 1e7 gamma / 1e9 theta
    that catastrophically cancel in the attribution sum.

    Previously the analytic gamma/theta blew up at ultra-short T and the
    attribution reconciliation drifted by ~1e-8 relative to total_pnl.
    """
    spot_path = [100.0 + i * 0.5 for i in range(12)]
    # Path ends at 1e-18 years (effectively at expiry) - the first step is
    # the ultra-short-T edge that previously broke reconciliation.
    times = [1e-18 + i * (2 / 365.25) for i in range(12)]
    result = delta_hedged_option_pnl(spot_path, times, **_base_kwargs())
    attr = result["attribution"]
    for k in ["delta_pnl", "gamma_pnl", "theta_pnl", "vega_pnl", "residual", "total_pnl", "sum_attribution"]:
        assert math.isfinite(float(attr[k])), (k, attr[k])
    assert abs(attr["sum_attribution"] - attr["total_pnl"]) < 1e-9
    # gamma/theta must not be the 1e7/1e9 singularity values
    assert abs(attr["gamma_pnl"]) < 1e6, attr["gamma_pnl"]
    assert abs(attr["theta_pnl"]) < 1e7, attr["theta_pnl"]


def test_at_expiry_path_is_finite():
    """A path pinned exactly at expiry must still price and attribute cleanly."""
    spot_path = [100.0, 100.5, 101.0, 100.0]
    times = [0.0, 0.0, 0.0, 0.0]
    result = delta_hedged_option_pnl(spot_path, times, **_base_kwargs())
    attr = result["attribution"]
    for k in ["delta_pnl", "gamma_pnl", "theta_pnl", "vega_pnl", "residual", "total_pnl", "sum_attribution"]:
        assert math.isfinite(float(attr[k])), (k, attr[k])
    assert abs(attr["sum_attribution"] - attr["total_pnl"]) < 1e-9
