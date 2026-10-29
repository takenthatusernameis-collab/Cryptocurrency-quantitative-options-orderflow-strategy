"""Adversarial tests for the options pricing & Greeks engine.

Covers Black-Scholes pricing, analytic + finite-difference Greeks, the
deterministic implied-volatility solver, arbitrage boundary handling, extreme
strikes/expiries, zero/division guards, determinism (twice -> byte-identical),
and strict ``allow_nan=False`` serialization. No NaN/Inf may leak from any
public path; invalid inputs raise rather than silently degrading.
"""

import math

import pytest
from pydantic import ValidationError

from src.data.schemas import PricingInputs, PricingOutputs
from src.errors import FeatureError, NonFiniteResultError
from src.features.options_pricing import (
    black_scholes,
    black_scholes_greeks,
    black_scholes_price,
    batch_price,
    finite_difference_greeks,
    greeks_match_analytic,
    implied_volatility,
    price_with_implied_vol,
)
from src.telemetry import serialize_metrics_strict


def _base_inputs(option_type: str = "call") -> PricingInputs:
    return PricingInputs(
        spot=100.0,
        strike=100.0,
        rate=0.05,
        volatility=0.2,
        time_to_expiry=1.0,
        option_type=option_type,
        seed=42,
    )


# ---------------------------------------------------------------------------
# Pricing correctness & put-call parity
# ---------------------------------------------------------------------------

def test_black_scholes_atm_call_price_range():
    out = black_scholes(_base_inputs("call"))
    # ATM call S=100,K=100,r=5%,vol=20%,T=1y -> price ~ 10.45
    assert 9.0 < out.price < 12.0


def test_black_scholes_put_call_parity():
    call = black_scholes(_base_inputs("call"))
    put = black_scholes(_base_inputs("put"))
    spot = 100.0
    strike = 100.0
    rate = 0.05
    t = 1.0
    lhs = call.price - put.price
    rhs = spot - strike * math.exp(-rate * t)
    assert abs(lhs - rhs) < 1e-9


def test_black_scholes_intrinsic_at_zero_vol():
    inp = PricingInputs(spot=100.0, strike=90.0, rate=0.05, volatility=0.0,
                        time_to_expiry=1.0, option_type="call", seed=42)
    out = black_scholes(inp)
    expected = max(100.0 - 90.0 * math.exp(-0.05 * 1.0), 0.0)
    assert abs(out.price - expected) < 1e-9


def test_black_scholes_zero_time_to_expiry_call():
    inp = PricingInputs(spot=100.0, strike=90.0, rate=0.05, volatility=0.2,
                        time_to_expiry=0.0, option_type="call", seed=42)
    out = black_scholes(inp)
    assert abs(out.price - max(100.0 - 90.0, 0.0)) < 1e-9


def test_black_scholes_deep_itm_call():
    inp = PricingInputs(spot=200.0, strike=50.0, rate=0.05, volatility=0.2,
                        time_to_expiry=1.0, option_type="call", seed=42)
    out = black_scholes(inp)
    assert out.delta > 0.99
    assert out.price > 0.0


def test_black_scholes_deep_otm_call():
    inp = PricingInputs(spot=10.0, strike=200.0, rate=0.05, volatility=0.2,
                        time_to_expiry=1.0, option_type="call", seed=42)
    out = black_scholes(inp)
    assert out.delta < 0.01
    assert out.price >= 0.0
    assert out.price < 1.0


def test_black_scholes_extreme_strike():
    inp = PricingInputs(spot=100.0, strike=1e6, rate=0.05, volatility=0.2,
                        time_to_expiry=1.0, option_type="call", seed=42)
    out = black_scholes(inp)
    assert math.isfinite(out.price)
    assert out.price >= 0.0
    assert math.isfinite(out.gamma) and math.isfinite(out.vega)


# ---------------------------------------------------------------------------
# Greeks sanity
# ---------------------------------------------------------------------------

def test_call_greeks_signs_and_bounds():
    out = black_scholes(_base_inputs("call"))
    g = black_scholes_greeks(_base_inputs("call"))
    assert 0.0 < out.delta < 1.0
    assert 0.0 < g["delta"] < 1.0
    assert g["gamma"] > 0.0
    assert g["vega"] > 0.0
    assert g["theta"] < 0.0  # call time decay
    assert math.isfinite(g["rho"])


def test_put_greeks_signs_and_bounds():
    g = black_scholes_greeks(_base_inputs("put"))
    assert -1.0 < g["delta"] < 0.0
    assert g["gamma"] > 0.0
    assert g["vega"] > 0.0
    assert math.isfinite(g["theta"])
    assert math.isfinite(g["rho"])


def test_greek_finite_guards():
    for ot in ("call", "put"):
        g = black_scholes_greeks(_base_inputs(ot))
        for k, v in g.items():
            assert math.isfinite(v), f"{k} non-finite for {ot}: {v}"


# ---------------------------------------------------------------------------
# Finite-difference cross-check
# ---------------------------------------------------------------------------

def test_finite_difference_matches_analytic():
    inp = _base_inputs("call")
    m = greeks_match_analytic(inp)
    assert m["all_match"] is True, m
    for key in ("delta", "gamma", "vega", "theta", "rho"):
        assert m[key]["match"] is True, (key, m[key])


def test_finite_difference_put_matches_analytic():
    inp = _base_inputs("put")
    m = greeks_match_analytic(inp)
    assert m["all_match"] is True, m


# ---------------------------------------------------------------------------
# Implied volatility solver
# ---------------------------------------------------------------------------

def test_iv_solver_round_trip_call():
    inp = _base_inputs("call")
    price = black_scholes_price(inp)
    iv = implied_volatility(price, 100.0, 100.0, 0.05, 1.0, "call", seed=42)
    assert abs(iv - 0.2) < 1e-8


def test_iv_solver_round_trip_put():
    price = black_scholes_price(_base_inputs("put"))
    iv = implied_volatility(price, 100.0, 100.0, 0.05, 1.0, "put", seed=42)
    assert abs(iv - 0.2) < 1e-8


def test_iv_solver_deterministic_twice_byte_identical():
    price = black_scholes_price(_base_inputs("call"))
    iv1 = implied_volatility(price, 100.0, 100.0, 0.05, 1.0, "call", seed=42)
    iv2 = implied_volatility(price, 100.0, 100.0, 0.05, 1.0, "call", seed=42)
    assert iv1 == iv2
    # Different seed must not change result (deterministic bisection + Newton).
    iv3 = implied_volatility(price, 100.0, 100.0, 0.05, 1.0, "call", seed=999)
    assert abs(iv3 - iv1) < 1e-9


def test_iv_solver_price_at_intrinsic_returns_floor():
    # Call price exactly at intrinsic -> IV collapses to floor.
    intrinsic = max(100.0 - 100.0 * math.exp(-0.05 * 1.0), 0.0)
    iv = implied_volatility(intrinsic, 100.0, 100.0, 0.05, 1.0, "call", seed=42)
    assert iv == 1e-6


def test_iv_solver_call_above_spot_raises():
    with pytest.raises(NonFiniteResultError):
        implied_volatility(150.0, 100.0, 100.0, 0.05, 1.0, "call", seed=42)


def test_iv_solver_put_above_discounted_strike_raises():
    upper = 100.0 * math.exp(-0.05 * 1.0)
    with pytest.raises(NonFiniteResultError):
        implied_volatility(upper + 1.0, 100.0, 100.0, 0.05, 1.0, "put", seed=42)


def test_iv_solver_zero_time_to_expiry_raises():
    with pytest.raises(NonFiniteResultError):
        implied_volatility(10.0, 100.0, 100.0, 0.05, 0.0, "call", seed=42)


def test_iv_solver_negative_spot_raises():
    with pytest.raises(NonFiniteResultError):
        implied_volatility(10.0, -100.0, 100.0, 0.05, 1.0, "call", seed=42)


def test_iv_solver_non_finite_price_raises():
    with pytest.raises(NonFiniteResultError):
        implied_volatility(float("nan"), 100.0, 100.0, 0.05, 1.0, "call", seed=42)


def test_iv_solver_invalid_option_type_raises():
    with pytest.raises(FeatureError):
        implied_volatility(10.0, 100.0, 100.0, 0.05, 1.0, "forward", seed=42)


# ---------------------------------------------------------------------------
# price_with_implied_vol round trip + serialization
# ---------------------------------------------------------------------------

def test_price_with_implied_vol_round_trip():
    inp = _base_inputs("call")
    price = black_scholes_price(inp)
    out = price_with_implied_vol(price, 100.0, 100.0, 0.05, 1.0, "call", seed=42)
    assert isinstance(out, PricingOutputs)
    assert abs(out.implied_vol - 0.2) < 1e-8
    assert abs(out.price - price) < 1e-8
    assert out.converged is True


def test_outputs_strict_serialization():
    out = black_scholes(_base_inputs("call"))
    payload = serialize_metrics_strict(out.model_dump())
    assert isinstance(payload, dict)
    # Re-emit with allow_nan=False to guarantee JSON validity.
    import json
    json.dumps(payload, allow_nan=False)


def test_batch_price_outputs_serializable():
    inputs = [_base_inputs("call"), _base_inputs("put")]
    outputs = batch_price(inputs)
    assert len(outputs) == 2
    for out in outputs:
        payload = serialize_metrics_strict(out.model_dump())
        import json
        json.dumps(payload, allow_nan=False)


# ---------------------------------------------------------------------------
# Invalid inputs rejected (zero/division guards)
# ---------------------------------------------------------------------------

def test_negative_spot_rejected():
    with pytest.raises(ValidationError):
        PricingInputs(spot=-100.0, strike=100.0, rate=0.05, volatility=0.2,
                      time_to_expiry=1.0, option_type="call", seed=42)


def test_negative_strike_rejected():
    with pytest.raises(ValidationError):
        PricingInputs(spot=100.0, strike=-100.0, rate=0.05, volatility=0.2,
                      time_to_expiry=1.0, option_type="call", seed=42)


def test_negative_volatility_rejected():
    with pytest.raises(ValidationError):
        PricingInputs(spot=100.0, strike=100.0, rate=0.05, volatility=-0.2,
                      time_to_expiry=1.0, option_type="call", seed=42)


def test_negative_time_rejected():
    with pytest.raises(ValidationError):
        PricingInputs(spot=100.0, strike=100.0, rate=0.05, volatility=0.2,
                      time_to_expiry=-1.0, option_type="call", seed=42)


def test_non_finite_inputs_rejected():
    with pytest.raises(ValidationError):
        PricingInputs(spot=float("inf"), strike=100.0, rate=0.05, volatility=0.2,
                      time_to_expiry=1.0, option_type="call", seed=42)


def test_invalid_option_type_rejected():
    with pytest.raises(ValidationError):
        PricingInputs(spot=100.0, strike=100.0, rate=0.05, volatility=0.2,
                      time_to_expiry=1.0, option_type="binary", seed=42)


# ---------------------------------------------------------------------------
# Pydantic schema serialization invariants
# ---------------------------------------------------------------------------

def test_pricing_inputs_validation_rejects_nonfinite():
    with pytest.raises(ValidationError):
        PricingInputs(spot=float("nan"), strike=100.0, rate=0.05, volatility=0.2,
                      time_to_expiry=1.0, option_type="call", seed=42)


def test_pricing_inputs_validation_rejects_negative_spot():
    with pytest.raises(ValidationError):
        PricingInputs(spot=0.0, strike=100.0, rate=0.05, volatility=0.2,
                      time_to_expiry=1.0, option_type="call", seed=42)


def test_pricing_inputs_validation_rejects_bad_option_type():
    with pytest.raises(ValidationError):
        PricingInputs(spot=100.0, strike=100.0, rate=0.05, volatility=0.2,
                      time_to_expiry=1.0, option_type="nonsense", seed=42)


def test_pricing_outputs_all_finite():
    out = black_scholes(_base_inputs("call"))
    dumped = out.model_dump()
    for k, v in dumped.items():
        if v is None:
            continue
        assert math.isfinite(v), f"{k} non-finite: {v}"
