"""Regression tests for the integrated campaign signal path.

Guards the two defects that made every OOS evaluation vacuous:
  1. salted ``hash()`` made synthetic fallbacks non-deterministic across processes;
  2. repeating one static feature snapshot produced an all-zero signal series.
"""
from __future__ import annotations

from datetime import datetime, timezone

from src.campaign.integrated import (
    DEFAULT_SPOT,
    DEFAULT_VENUE,
    DETERMINISTIC_NOW,
    IntegratedConfig,
    _features_for_symbol,
    _finite,
    _generate_price_paths,
    _load_options_chain,
    _load_orderflow,
    _stable_seed,
    _time_varying_signal_series,
)
from src.data.schemas import PricingInputs
from src.features.iv_surface import build_iv_surface_from_chain
from src.features.options_pricing import black_scholes_greeks
from src.signals.composite import CompositeSignalGenerator


def _prices(n: int = 220) -> list[float]:
    cfg = IntegratedConfig(seed=42, n_points=n)
    prices, _ = _generate_price_paths(cfg)
    return list(prices["BTC"])


def _static_context() -> tuple[dict, object, object, dict]:
    sym = "BTC"
    spot = float(DEFAULT_SPOT[sym])
    now = DETERMINISTIC_NOW
    chain = _load_options_chain(sym, spot, now, DEFAULT_VENUE)
    of = _load_orderflow(sym, DEFAULT_VENUE)
    iv_surface = build_iv_surface_from_chain(chain, spot=spot, rate=0.0, now=now, seed=42)
    greeks = None
    if chain.quotes:
        atm = min(chain.quotes, key=lambda q: abs(float(q.contract.strike) - spot))
        texp = max((atm.contract.expiry - now).total_seconds() / 86400.0 / 365.0, 1e-6)
        g = black_scholes_greeks(
            PricingInputs(
                spot=spot,
                strike=float(atm.contract.strike),
                rate=0.0,
                volatility=_finite(getattr(atm, "mark_iv", None), 0.80),
                time_to_expiry=texp,
                option_type=atm.contract.option_type,
                seed=42,
            )
        )
        greeks = {k: g[k] for k in ("delta", "gamma", "vega", "theta", "rho")}
    features = _features_for_symbol(
        sym, spot, chain, of, iv_surface, greeks, CompositeSignalGenerator()
    )
    return features, chain, iv_surface, greeks or {}


def test_stable_seed_is_process_independent_and_key_sensitive() -> None:
    a = _stable_seed("BTC", "synthetic")
    b = _stable_seed("BTC", "synthetic")
    c = _stable_seed("ETH", "synthetic")
    assert a == b
    assert a != c
    assert 0 <= a < 2**32


def test_time_varying_series_is_nonconstant_and_bounded() -> None:
    prices = _prices()
    features, chain, iv_surface, greeks = _static_context()
    series, diagnostics = _time_varying_signal_series(
        CompositeSignalGenerator(), "BTC", prices, features, chain, iv_surface, greeks
    )
    assert len(series) == len(prices)
    assert set(series) <= {-1, 0, 1}
    assert any(s != 0 for s in series), "signal series must not be all-zero"
    assert len(diagnostics) == len(prices)


def test_time_varying_series_is_causal() -> None:
    prices = _prices()
    features, chain, iv_surface, greeks = _static_context()
    full, _ = _time_varying_signal_series(
        CompositeSignalGenerator(), "BTC", prices, features, chain, iv_surface, greeks
    )
    cut = 150
    truncated, _ = _time_varying_signal_series(
        CompositeSignalGenerator(), "BTC", prices[:cut], features, chain, iv_surface, greeks
    )
    assert truncated == full[:cut], "future prices must not change earlier signals"