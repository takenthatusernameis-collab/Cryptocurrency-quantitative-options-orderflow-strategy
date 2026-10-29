"""Adversarial tests for IV surface construction and calibration.

Covers surface building from chains, interpolation, arbitrage guards,
calibration with smoothing/residuals, determinism (twice -> byte-identical),
serialization invariants (allow_nan=False), and edge cases.
"""

import math
from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from src.data.schemas import OptionContract, OptionQuote, OptionsChain, IVPoint, IVSurfaceSnapshot
from src.errors import FeatureError, NonFiniteResultError
from src.features.iv_surface import (
    IVSurface,
    SurfacePoint,
    build_iv_surface_from_chain,
    calibrate_iv_surface,
)
from src.features.options_pricing import black_scholes_price, implied_volatility
from src.telemetry import serialize_metrics_strict


def _make_contract(symbol: str, underlying: str, strike: float, expiry: datetime,
                   option_type: str, venue: str = "deribit") -> OptionContract:
    return OptionContract(
        symbol=symbol,
        underlying=underlying,
        strike=float(strike),
        expiry=expiry,
        option_type=option_type,
        venue=venue,
        contract_size=1.0,
    )


def black_scholes_price_from_inputs(spot, strike, rate, vol, texp, ot, seed=42):
    from src.data.schemas import PricingInputs
    from src.features.options_pricing import black_scholes_price
    inp = PricingInputs(spot=spot, strike=strike, rate=rate, volatility=vol,
                        time_to_expiry=texp, option_type=ot, seed=seed)
    return black_scholes_price(inp)


def _make_chain(underlying: str = "BTC", venue: str = "deribit",
                spot: float = 100.0, rate: float = 0.05, seed: int = 42,
                now: datetime | None = None) -> OptionsChain:
    if now is None:
        now = datetime.now(timezone.utc)
    quotes = []
    for days, texp_years in [(7, 7/365.25), (30, 30/365.25)]:
        expiry = now + timedelta(days=days)
        for strike in [80.0, 90.0, 100.0, 110.0, 120.0]:
            for ot in ["call", "put"]:
                try:
                    price = black_scholes_price_from_inputs(spot, strike, rate, 0.25, texp_years, ot, seed)
                except Exception:
                    price = max(spot - strike if ot == "call" else strike - spot, 0.01)
                q = OptionQuote(
                    contract=_make_contract(f"{underlying}-{strike}-{ot}", underlying, strike, expiry, ot, venue),
                    bid=max(price - 0.01, 0.0),
                    ask=price + 0.01,
                    last=price,
                    mark=price,
                    mark_iv=0.25,
                    timestamp=now,
                )
                quotes.append(q)
    return OptionsChain(underlying=underlying, venue=venue, quotes=quotes, timestamp=now)


def test_build_iv_surface_from_chain_basic():
    now = datetime.now(timezone.utc)
    chain = _make_chain(now=now)
    surf = build_iv_surface_from_chain(chain, spot=100.0, rate=0.05, now=now, seed=42)
    assert isinstance(surf, IVSurface)
    assert surf.underlying == "BTC"
    iv = surf.get_iv(100.0, 7/365.25, "call")
    assert math.isfinite(iv)
    assert 1e-6 <= iv <= 5.0


def test_surface_interpolation_strike_and_expiry():
    now = datetime.now(timezone.utc)
    points = []
    for days in [10, 60]:
        exp = now + timedelta(days=days)
        texp = days / 365.25
        for k in [90.0, 100.0, 110.0]:
            for ot in ["call", "put"]:
                points.append(SurfacePoint(strike=k, expiry=exp, time_to_expiry=texp,
                                           option_type=ot, iv=0.2 + 0.01 * abs(k - 100.0)/10.0))
    surf = IVSurface("BTC", "deribit", points, spot=100.0, rate=0.05, seed=42)
    iv1 = surf.get_iv(95.0, 20/365.25, "call")
    iv2 = surf.get_iv(105.0, 30/365.25, "put")
    assert 1e-6 <= iv1 <= 5.0
    assert 1e-6 <= iv2 <= 5.0


def test_surface_determinism_twice_byte_identical():
    now = datetime.now(timezone.utc)
    chain = _make_chain(now=now)
    s1 = build_iv_surface_from_chain(chain, spot=100.0, rate=0.05, now=now, seed=123)
    s2 = build_iv_surface_from_chain(chain, spot=100.0, rate=0.05, now=now, seed=123)
    d1 = serialize_metrics_strict(s1.to_dict())
    d2 = serialize_metrics_strict(s2.to_dict())
    assert d1 == d2


def test_surface_to_dict_serialization_allow_nan_false():
    now = datetime.now(timezone.utc)
    chain = _make_chain(now=now)
    s = build_iv_surface_from_chain(chain, spot=100.0, rate=0.05, now=now, seed=7)
    payload = s.to_dict()
    out = serialize_metrics_strict(payload)
    assert isinstance(out, dict)
    # must be JSON serializable with allow_nan=False
    import json
    json.dumps(out, allow_nan=False)


def test_calibrate_iv_surface_residuals_and_stability():
    now = datetime.now(timezone.utc)
    points = []
    for days in [14, 45]:
        exp = now + timedelta(days=days)
        texp = days / 365.25
        for k in [80.0, 90.0, 100.0, 110.0, 120.0]:
            for ot in ["call", "put"]:
                iv = 0.22 + 0.0005 * (k - 100.0) ** 2
                points.append(SurfacePoint(strike=k, expiry=exp, time_to_expiry=texp,
                                           option_type=ot, iv=iv))
    surf, report = calibrate_iv_surface(points, spot=100.0, rate=0.05,
                                        smoothing=0.01, seed=42,
                                        underlying="BTC", venue="deribit")
    assert isinstance(surf, IVSurface)
    assert report["num_points"] == len(points)
    assert math.isfinite(report["residual_mean"])
    assert math.isfinite(report["residual_std"])
    assert math.isfinite(report["residual_max_abs"])
    assert report["residual_max_abs"] >= 0.0


def test_calibrate_deterministic_twice():
    now = datetime.now(timezone.utc)
    points = []
    for days in [7, 21]:
        exp = now + timedelta(days=days)
        texp = days / 365.25
        for k in [90, 95, 100, 105, 110]:
            for ot in ["call", "put"]:
                points.append(SurfacePoint(strike=float(k), expiry=exp, time_to_expiry=texp,
                                           option_type=ot, iv=0.25))
    s1, r1 = calibrate_iv_surface(points, spot=100.0, rate=0.05, smoothing=0.05, seed=5)
    s2, r2 = calibrate_iv_surface(points, spot=100.0, rate=0.05, smoothing=0.05, seed=5)
    assert serialize_metrics_strict(s1.to_dict()) == serialize_metrics_strict(s2.to_dict())
    assert serialize_metrics_strict(r1) == serialize_metrics_strict(r2)


def test_surface_arbitrage_guards_finite_bounds():
    now = datetime.now(timezone.utc)
    points = []
    for days in [7, 30, 90]:
        exp = now + timedelta(days=days)
        texp = days / 365.25
        for k in [70, 80, 90, 100, 110, 120, 130]:
            for ot in ["call", "put"]:
                iv = 0.2 + 0.1 * abs(math.log(k / 100.0))
                iv = max(1e-6, min(5.0, iv))
                points.append(SurfacePoint(strike=float(k), expiry=exp, time_to_expiry=texp,
                                           option_type=ot, iv=iv))
    surf = IVSurface("ETH", "binance", points, spot=100.0, rate=0.01, seed=1)
    for k in [75.0, 100.0, 125.0]:
        for ot in ["call", "put"]:
            iv = surf.get_iv(k, 45/365.25, ot)
            assert 1e-6 <= iv <= 5.0


def test_surface_iv_bounds_enforced_across_expiries():
    now = datetime.now(timezone.utc)
    exp1 = now + timedelta(days=10)
    exp2 = now + timedelta(days=30)
    points = [
        SurfacePoint(strike=100.0, expiry=exp1, time_to_expiry=10/365.25, option_type="call", iv=0.2),
        SurfacePoint(strike=100.0, expiry=exp2, time_to_expiry=30/365.25, option_type="call", iv=10.0),
    ]
    with pytest.raises(FeatureError):
        IVSurface("BTC", "deribit", points, spot=100.0, rate=0.05, seed=42)


def test_build_iv_surface_solves_from_prices_when_iv_missing():
    now = datetime.now(timezone.utc)
    chain_quotes = []
    spot, rate, vol = 100.0, 0.05, 0.2
    texp = 30 / 365.25
    expiry = now + timedelta(days=30)
    for strike in [90.0, 100.0, 110.0]:
        for ot in ["call", "put"]:
            price = black_scholes_price_from_inputs(spot, strike, rate, vol, texp, ot, seed=123)
            q = OptionQuote(
                contract=_make_contract(f"BTC-{strike}-{ot}", "BTC", strike, expiry, ot, "deribit"),
                bid=price * 0.99,
                ask=price * 1.01,
                mark=price,
                mark_iv=None,
                bid_iv=None,
                ask_iv=None,
                timestamp=now,
            )
            chain_quotes.append(q)
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=chain_quotes, timestamp=now)
    surf = build_iv_surface_from_chain(chain, spot=spot, rate=rate, now=now, seed=123)
    iv = surf.get_iv(100.0, texp, "call")
    assert abs(iv - vol) < 1e-6


def test_build_iv_surface_edge_cases_empty_or_bad():
    now = datetime.now(timezone.utc)
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[], timestamp=now)
    with pytest.raises(FeatureError):
        build_iv_surface_from_chain(chain, spot=100.0, rate=0.05, now=now)


def test_iv_point_schema_validation():
    now = datetime.now(timezone.utc)
    pt = IVPoint(strike=100.0, expiry=now, time_to_expiry=0.1, option_type="call", iv=0.25)
    assert pt.iv == 0.25
    with pytest.raises(Exception):
        IVPoint(strike=-1.0, expiry=now, time_to_expiry=0.1, option_type="call", iv=0.25)
    with pytest.raises(Exception):
        IVPoint(strike=100.0, expiry=now, time_to_expiry=-0.1, option_type="call", iv=0.25)
    with pytest.raises(Exception):
        IVPoint(strike=100.0, expiry=now, time_to_expiry=0.1, option_type="call", iv=-0.1)
    with pytest.raises(Exception):
        IVPoint(strike=100.0, expiry=now, time_to_expiry=0.1, option_type="xyz", iv=0.25)


def test_iv_surface_snapshot_schema():
    now = datetime.now(timezone.utc)
    pts = [IVPoint(strike=100.0, expiry=now, time_to_expiry=0.1, option_type="call", iv=0.25)]
    snap = IVSurfaceSnapshot(underlying="BTC", venue="deribit", spot=100.0, rate=0.05,
                             timestamp=now, points=pts, seed=42)
    assert snap.spot == 100.0
    with pytest.raises(Exception):
        IVSurfaceSnapshot(underlying="BTC", venue="deribit", spot=-1.0, rate=0.05, points=pts)
