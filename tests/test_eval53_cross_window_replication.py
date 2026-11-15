"""Unit tests for EVAL-53 cross-window surface x options-venue order-flow
replication.

Deterministic in-memory fixtures only. No real data, no network, no
research_state writes.
"""

from __future__ import annotations

import json
import math

import scripts.eval52_options_surface_orderflow_net_of_cost as e52
import scripts.eval53_cross_window_replication as e53


def _craft_capture(n_bars=20, n_instruments=6, n_trades_per_bar=2, seed=0,
                   inst="BTC"):
    """Small, deliberately below-floor capture mirroring the eval52 fixture
    shape (v1 schema)."""
    import random
    rng = random.Random(seed)
    base_ms = 1_700_000_000_000
    bar_ms = 300_000
    px = 60000.0 if inst == "BTC" else 3000.0
    candles, trades, tid = [], [], 0
    drifts = [rng.uniform(-1, 1) for _ in range(n_bars)]
    for i in range(n_bars):
        px = max(1.0, px * (1 + drifts[i] * 1e-4))
        candles.append({
            "ts": base_ms + i * bar_ms, "open": px, "high": px,
            "low": px, "close": px,
        })
        sign = 1.0 if drifts[i] >= 0 else -1.0
        for _ in range(n_trades_per_bar):
            tid += 1
            opt = "call" if rng.random() < 0.5 else "put"
            strike = round(px + rng.randint(-2, 2) * 500, 2)
            trades.append({
                "ts": base_ms + i * bar_ms + rng.randint(1, bar_ms - 1),
                "instrument": f"{inst}-30DEC26-{int(strike)}-{'C' if opt=='call' else 'P'}",
                "direction": "buy" if sign > 0 else "sell",
                "amount": rng.uniform(0.1, 2.0),
                "price": 0.01, "index_price": px, "iv": 50.0,
                "option_type": opt, "strike": strike,
                "expiry": "2026-12-30T08:00:00Z",
            })
    snaps = []
    for i in range(n_bars):
        spot = candles[i]["close"]
        bar_ms_i = base_ms + i * bar_ms
        quotes = []
        for k in range(n_instruments):
            strike = round(spot + (k - n_instruments // 2) * 500, 2)
            opt = "call" if k % 2 == 0 else "put"
            mark = max(0.01, 0.05 * spot)
            quotes.append({
                "symbol": f"{inst}-OPT-{int(strike)}-{opt[0].upper()}-{i}-{k}",
                "underlying": inst, "strike": strike,
                "expiry": "2026-12-30T08:00:00Z", "option_type": opt,
                "bid": mark * 0.98, "ask": mark * 1.02, "mark": mark,
                "open_interest": 100.0, "volume": 10.0,
                "timestamp": f"2023-11-14T00:{i%60:02d}:00Z",
            })
        snaps.append({"bar_ms": bar_ms_i, "spot": spot, "quotes": quotes})
    return {
        "schema": "deribit_options_surface_orderflow_capture_v1",
        "underlying": inst, "venue": "deribit",
        "window_start": "2023-11-14T00:00:00Z",
        "window_end": "2023-11-15T00:00:00Z",
        "surface": {"bar_seconds": 300, "resolution": "5", "snapshots": snaps},
        "option_trades": trades, "perp_candles": candles,
        "source": {"authenticated": False, "public_read_only": True,
                   "venue": "deribit"},
    }


def _write_capture(tmp_path, cap, stamp_suffix="00000000T000000Z"):
    path = tmp_path / f"options_surface_orderflow_{cap['underlying']}_{stamp_suffix}.json"
    path.write_text(json.dumps(cap, separators=(",", ":")))
    return path


def _synth_report(floor_ok, config_pass, pbo=0.1, underlyings=("BTC", "ETH")):
    return {
        "floor_ok": floor_ok, "underlyings": list(underlyings),
        "per_underlying_floor": {},
        "per_config": [],
        "per_underlying": [],
        "pooled": {"overall_pbo": pbo, "bh_fdr": {"rejected": []},
                   "all_underlyings_pass": True},
        "errors": [], "verdict": "NO-GO CONFIRMED (PASS)" if floor_ok else "BLOCKED",
        "config_pass": list(config_pass),
        "generated_at": "2026-11-15T17:00:00Z",
        "task": "INIT-TEST",
        "capture_dir": "data/raw/evalXX",
    }


def test_constants_match_e52_no_fitting():
    assert e53.GRID_BAR_SECONDS == e52.GRID_BAR_SECONDS
    assert e53.OF_SIGNALS == e52.OF_SIGNALS
    assert e53.FUSION_RULES == e52.FUSION_RULES
    assert e53.ZWINDOW == e52.ZWINDOW == 20
    assert e53.COST_BPS == e52.COST_BPS == 5.0
    assert e53.PERMUTATION_PERMS == e52.PERMUTATION_PERMS == 1000
    assert e53.BOOTSTRAP_RESAMPLES == e52.BOOTSTRAP_RESAMPLES == 1000
    assert e53.BOOTSTRAP_BLOCK == e52.BOOTSTRAP_BLOCK == 2
    assert e53.PBO_K_FOLDS == e52.PBO_K_FOLDS == 4
    assert e53.FDR_ALPHA == e52.FDR_ALPHA == 0.1
    assert e53.SEED == e52.SEED == 42
    assert e53.KILL_SWITCH_MAX_DD == e52.KILL_SWITCH_MAX_DD == 0.20
    assert e53.MIN_TRADES == e52.MIN_TRADES == 2000
    assert e53.MIN_UNDERLYINGS == e52.MIN_UNDERLYINGS == 2


def test_measure_window_small_below_floor_structure(tmp_path):
    cap = _craft_capture(n_bars=20)
    _write_capture(tmp_path, cap, "20260101T000000Z")
    rep = e53.measure_window(str(tmp_path), "INIT-T", "2026-11-15T17:00:00Z")
    assert rep["floor_ok"] is False
    assert rep["verdict"] == "BLOCKED"
    assert set(rep) >= {
        "capture_dir", "generated_at", "task", "floor_ok", "underlyings",
        "per_underlying_floor", "per_config", "per_underlying", "pooled",
        "errors", "verdict", "config_pass",
    }
    assert isinstance(rep["config_pass"], list)
    pbo = rep["pooled"]["overall_pbo"]
    assert 0.0 <= pbo <= 1.0


def test_measure_window_missing_dir():
    rep = e53.measure_window("/nonexistent/dir/eval53", "INIT-T",
                             "2026-11-15T17:00:00Z")
    assert rep["floor_ok"] is False
    assert rep["verdict"] == "BLOCKED"
    assert rep["errors"]


def test_cross_window_meta_go_when_replicated():
    shared = ["BTC::sign_agreement::imbalance::bar300.0",
              "ETH::regime_filter::call_minus_put::bar60.0"]
    ra = _synth_report(True, shared)
    rb = _synth_report(True, shared)
    meta = e53.cross_window_meta(ra, rb)
    assert meta["verdict"] == "GO CONFIRMED"
    assert meta["go"] is True
    assert meta["floor_ok_a"] and meta["floor_ok_b"]
    assert set(meta["replicated_underlyings"]) == {"BTC", "ETH"}
    assert meta["n_replicated"] == 2


def test_cross_window_meta_nogo_when_not_replicated():
    ra = _synth_report(True, ["BTC::sign_agreement::imbalance::bar300.0"])
    rb = _synth_report(True, ["ETH::sign_agreement::imbalance::bar300.0"])
    meta = e53.cross_window_meta(ra, rb)
    assert meta["verdict"] == "NO-GO CONFIRMED (PASS)"
    assert meta["go"] is False
    assert meta["n_replicated"] == 0


def test_cross_window_meta_blocked_when_window_b_below_floor():
    ra = _synth_report(True, ["BTC::sign_agreement::imbalance::bar300.0"])
    rb = _synth_report(False, [])
    meta = e53.cross_window_meta(ra, rb)
    assert meta["verdict"] == "BLOCKED"
    assert meta["go"] is False
    assert meta["floor_ok_b"] is False


def test_cross_window_meta_pbo_blocks_go():
    shared = ["BTC::sign_agreement::imbalance::bar300.0",
              "ETH::regime_filter::call_minus_put::bar60.0"]
    ra = _synth_report(True, shared, pbo=0.9)
    rb = _synth_report(True, shared, pbo=0.9)
    meta = e53.cross_window_meta(ra, rb)
    assert meta["verdict"] == "NO-GO CONFIRMED (PASS)"
    assert meta["go"] is False


def test_floor_short_reuse():
    cap = _craft_capture(n_bars=20)
    fl = e52._underlying_floor(cap)
    assert fl["ok"] is False


def test_evaluate_config_reuse_small():
    cap = _craft_capture(n_bars=40)
    surf = e52.surface_signal_series(cap, cap["perp_candles"])
    res = e52.evaluate_config(cap, surf, fusion="sign_agreement",
                              of_signal="imbalance", bar_seconds=300.0)
    assert res["underlying"] == "BTC"
    assert "sharpe" in res and "pass" in res
    assert math.isfinite(res["sharpe"])
