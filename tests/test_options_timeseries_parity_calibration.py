"""Tests for per-expiry forward-calibrated put-call parity (EVAL-28).

The EVAL-27 parity check applied one constant spot to every strike/expiry, so
the ``S - K`` term was wrong away from the ATM and every pair falsely reported a
violation. EVAL-28 fits each expiry's forward from the chain itself
(``C_mid - P_mid = F/S - K/S``). These tests lock that behaviour: a chain built
from a known forward is recovered by the fit, while the legacy constant-spot
residual is large; the real snapshots (when present) are parity-consistent.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.campaign.integrated import RealDataUnavailable
from src.data.options_timeseries import (
    REFERENCE_SPOT,
    _parity_residual,
    _matching_pairs,
    calibrate_expiry_parity,
    load_options_timeseries,
)

NOW = datetime(2026, 11, 14, 0, 0, 0, tzinfo=timezone.utc)
EXPIRY = datetime(2026, 12, 31, tzinfo=timezone.utc)


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _write_parity_chain(path: Path, spot: float, forward: float) -> Path:
    """Build a call/put chain that exactly satisfies parity for ``forward``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    quotes = []
    for strike in (60000.0, 65000.0, 70000.0, 75000.0, 80000.0):
        intrinsic = max(forward - strike, 0.0) / spot
        call_mid = intrinsic + 0.01
        put_mid = call_mid - (forward - strike) / spot
        spread = 0.0005
        for option_type, mid in (("call", call_mid), ("put", put_mid)):
            quotes.append(
                {
                    "symbol": f"BTC-USD-261231-{int(strike)}-{option_type[0].upper()}",
                    "underlying": "BTC",
                    "strike": strike,
                    "expiry": _iso(EXPIRY),
                    "option_type": option_type,
                    "venue": "okx",
                    "contract_size": 1.0,
                    "bid": mid - spread,
                    "ask": mid + spread,
                    "last": mid,
                    "mark": mid,
                    "open_interest": 1.0,
                    "volume": 1.0,
                    "timestamp": _iso(NOW),
                }
            )
    path.write_text(
        json.dumps(
            {
                "acquired_at": _iso(NOW),
                "quotes": quotes,
                "underlying": "BTC",
                "venue": "okx",
            }
        ),
        encoding="utf-8",
    )
    return path


def test_per_expiry_fit_recovers_forward_and_flags_constant_spot(tmp_path):
    spot = 70000.0
    forward = 71000.0
    path = _write_parity_chain(tmp_path / "options_okx_BTC_20261114T000000Z.json", spot, forward)

    result = calibrate_expiry_parity(paths=[path], spot=REFERENCE_SPOT)
    assert result.overall_verdict == "GO"
    assert result.parity_consistent is True
    assert result.n_snapshots == 1

    snap = result.snapshots[0]
    assert snap.n_expiries == 1
    fit = snap.expiries[0]
    # The fit recovers the spot (slope = -1/S) and the forward (intercept = F/S).
    assert fit.implied_spot == pytest.approx(spot, rel=1e-6)
    assert fit.forward_over_spot * fit.implied_spot == pytest.approx(forward, rel=1e-6)
    assert fit.r2 == pytest.approx(1.0, rel=1e-9, abs=1e-9)
    assert fit.pairs_within_spread == fit.pairs_total

    # The legacy constant-spot residual must be materially wrong for this chain.
    from src.data.loader import DataLoader

    chain = DataLoader(cache=False).load_options_chain(str(path), venue="okx", underlying="BTC")
    pairs = _matching_pairs(chain.quotes)
    assert len(pairs) == 5
    legacy = [
        abs(_parity_residual(call, put, REFERENCE_SPOT, 0.0, 1.0))
        for call, put in pairs
    ]
    assert max(legacy) > 1000.0


def test_calibration_raises_without_real_export(tmp_path):
    with pytest.raises(RealDataUnavailable):
        calibrate_expiry_parity(paths=[], data_raw=tmp_path)


def test_real_snapshots_are_parity_consistent():
    try:
        diagnostics = load_options_timeseries()
    except RealDataUnavailable:
        pytest.skip("no real option snapshots under data/raw")
    if len(diagnostics) < 1:
        pytest.skip("no real option snapshots under data/raw")

    result = calibrate_expiry_parity()
    assert result.n_snapshots == len(diagnostics)
    assert result.overall_verdict == "GO"
    assert result.parity_consistent is True
    for snap in result.snapshots:
        assert snap.pairs_within_spread == snap.n_pairs
        assert snap.min_r2 >= 0.99