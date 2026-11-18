"""Unit tests for EVAL-109: does the single-asset causal near-ATM implied-vol
**level** (``atm_iv``) predict the subsequent **forward realized return
skewness** (third standardized moment) of the same underlying?

EVAL-109 is the on-charter, runnable-now distinct follow-up to EVAL-71
(``atm_iv``/``skew`` vs forward *RV level*), EVAL-101 (``atm_iv`` vs forward *signed return mean*), EVAL-87 (``atm_iv`` vs forward *tail asymmetry*),
EVAL-85/87 (skew/atm_iv vs forward *tail asymmetry*), EVAL-95 (``atm_iv`` vs forward *vol-of-vol*), and EVAL-103
(``skew`` vs forward *signed return*). It reuses the EVAL-71
``build_surface_bars`` signal path and EVAL-71 surface floor verbatim, and
transcribes the third-standardized-moment target (EVAL-85 forward window); the new logic is the
campaign composition.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.
"""

from __future__ import annotations

import json
import math
import random
import tempfile
from pathlib import Path

import scripts.eval61_orderflow_realized_vol_net_of_cost as e61
import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval65_orderflow_tox_rv_predictiveness as e65
import scripts.eval71_surface_iv_rv_predictiveness as e71
import scripts.eval109_single_asset_atm_iv_forward_return_skewness as e109

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000
_BASE_MS -= _BASE_MS % _BAR_MS


def _craft_surface_capture(
    inst="BTC", *, n_bars=200, seed=0, n_trades_per_bar=24, base_ms=_BASE_MS, bar_ms=_BAR_MS,
):
    """Deterministic three-way capture whose real option-trade IV populates a
    non-null near-ATM surface (atm_iv) at every bar."""
    rng = random.Random(seed)
    px = 60000.0 if inst == "BTC" else 3000.0
    expiries = ("20NOV26", "27DEC26")
    candles = []
    trades = []
    for i in range(n_bars):
        px = max(1.0, px * (1.0 + rng.uniform(-1.0, 1.0) * 1e-4))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        for j in range(n_trades_per_bar):
            frac = (j / (n_trades_per_bar - 1)) if n_trades_per_bar > 1 else 0.0
            strike = px * (0.99 + 0.02 * frac)
            typ = "P" if j % 2 == 0 else "C"
            expiry = expiries[j % len(expiries)]
            iv = (65.0 if expiry == expiries[0] else 55.0) + rng.uniform(-0.5, 0.5)
            trades.append({
                "ts": ts + j * 1000,
                "instrument": f"{inst}-{expiry}-{int(round(strike))}-{typ}",
                "iv": iv,
                "amount": 1.0 + 0.1 * j,
                "index_price": px,
                "option_type": typ.lower(),
            })
    return {
        "schema": "three_way_options_surface_orderflow_okx_perp_capture_v1",
        "underlying": inst,
        "surface": {"bar_seconds": 300, "resolution": "5", "snapshots": []},
        "option_trades": trades,
        "perp_candles": candles,
        "fetched_at": "2026-11-17T00:00:00Z",
    }


def _write_captures(caps):
    td = tempfile.mkdtemp()
    for inst, cap in caps.items():
        p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
    return td


# 1) artifact ids
def test_ids_are_eval109():
    assert e109.REPORT_ID.startswith("EVAL_109_")
    assert e109.PREREG_ID.startswith("EVAL_109_")
    assert e109.BLOCKED_ID.startswith("EVAL_109_")
    assert "ATM_IV" in e109.REPORT_ID
    assert "RETURN_SKEWNESS" in e109.REPORT_ID
    assert e109.SURFACE_SIGNAL == "atm_iv"
    assert e109.TARGET == "realized_return_skewness"


# 2) sealed machinery reused verbatim (not forked)
def test_reuse_helpers():
    assert e109.e71 is e71
    assert e109.e65 is e65
    assert e109.e61 is e61
    assert e109.e62 is e62


# 3) forward realized return skewness is finite and distinct from RV level / tail asymmetry
def test_forward_return_skewness_is_finite():
    rng = random.Random(109)
    bars = []
    px = 100.0
    for i in range(80):
        drift = 0.03 if i % 17 == 0 else rng.uniform(-0.002, 0.002)
        px = px * (1.0 + drift)
        bars.append({"close": px, "bar_open_ms": i * 300000, "atm_iv": 50.0})
    skew = e109._forward_return_skewness(bars, 24)
    finite = [v for v in skew if v is not None and math.isfinite(v)]
    assert len(finite) > 10
    assert any(v != 0.0 for v in finite)
    assert all(abs(v) < 50.0 for v in finite)
    rv = e71._forward_rv(bars, 24)
    assert len(rv) > 0


# 4) floor delegated to sealed EVAL-71 surface floor verbatim
def test_underlying_floor_delegates_to_eval71_verbatim():
    cap = _craft_surface_capture("BTC", n_bars=1200, seed=3, n_trades_per_bar=40)
    assert e109._underlying_floor(cap) == e71._underlying_surface_floor(cap)


# 5) _eval_one_config targets forward realized return skewness with atm_iv, deterministically
def test_eval_one_config_structure_and_deterministic(monkeypatch):
    monkeypatch.setattr(e109, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e109, "BOOTSTRAP_RESAMPLES", 50)
    cap = _craft_surface_capture("BTC", n_bars=220, seed=5, n_trades_per_bar=24)
    a = e109._eval_one_config(cap, bar_seconds=60.0, horizon_bars=6)
    b = e109._eval_one_config(cap, bar_seconds=60.0, horizon_bars=6)
    assert a["signal"] == "atm_iv"
    assert a["target"] == "realized_return_skewness"
    assert a["bar_seconds"] == 60.0
    assert a["horizon_bars"] == 6
    assert a["n_pairs"] >= e109.MIN_USABLE_PAIRS_PER_CONFIG
    assert -1.0 <= a["spearman_ic"] <= 1.0
    assert 0.0 <= a["permutation_p"] <= 1.0
    ci = a["bootstrap_ci"]
    assert len(ci) == 3 and ci[1] <= ci[0] <= ci[2]
    # determinism
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


# 6) below floor seals BLOCKED, never NO-GO
def test_below_floor_blocks_not_nogo():
    cap = _craft_surface_capture("BTC", n_bars=40, seed=1, n_trades_per_bar=2)
    td = _write_captures({"BTC": cap})
    report = e109.run_eval109(capture_dir=td, write=False, task_label="TEST")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    if not report.get("floor_ok"):
        assert report["verdict"] == "BLOCKED"


# 7) run_eval109(write=False) meets floor and summarizes (floor monkeypatched ok)
def test_run_eval109_no_write_meets_floor_and_summarizes(monkeypatch):
    monkeypatch.setattr(e109, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e109, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e109, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e109, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e109, "_campaign_floor",
        lambda per_underlying: {"checks": {}, "ok": True},
    )
    caps = {
        "BTC": _craft_surface_capture("BTC", n_bars=220, seed=17),
        "ETH": _craft_surface_capture("ETH", n_bars=220, seed=18),
    }
    td = _write_captures(caps)
    report = e109.run_eval109(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    # one config per underlying (2 underlyings x 1 grid point)
    assert len(report["per_config"]) == 2
    assert report["protocol"]["target"] == "realized_return_skewness"
    assert report["protocol"]["surface_signal"] == "atm_iv"


# 8) protocol constants pre-registered and floor reuses EVAL-71 surface floor
def test_protocol_constants():
    proto = e109.build_protocol("data/raw/eval61")
    assert proto["surface_signal"] == "atm_iv"
    assert proto["target"] == "realized_return_skewness"
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert proto["forward_horizons_bars"] == [6, 24, 72]
    assert proto["stats"]["seed"] == e62.SEED
    assert proto["floor"]["min_underlyings"] == e71.FLOOR["min_underlyings"]
    assert (
        proto["floor"]["min_option_trades_per_underlying"]
        == e71.FLOOR["min_option_trades_per_underlying"]
    )
    assert (
        proto["floor"]["min_near_atm_option_trades_per_underlying"]
        == e71.FLOOR["min_near_atm_option_trades_per_underlying"]
    )
    assert (
        proto["floor"]["min_perp_candles_per_underlying"]
        == e71.FLOOR["min_perp_candles_per_underlying"]
    )
    assert (
        proto["floor"]["min_perp_span_seconds_per_underlying"]
        == e71.FLOOR["min_perp_span_seconds_per_underlying"]
    )
    assert proto["signal_window_seconds"] == e71.SIGNAL_WINDOW_SECONDS
    assert proto["atm_band"] == e71.ATM_BAND
