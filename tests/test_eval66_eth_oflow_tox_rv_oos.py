"""Unit tests for EVAL-66: ETH-only OOS replication of the suggestive EVAL-65
options order-flow toxicity -> realized-vol predictiveness slice
(tox/imbalance, bar60, horizon 72).

Copy-and-retarget of sealed EVAL-65: reuses EVAL-62 build_states and EVAL-64
feasible floor; ETH-only, 2 pre-registered configs. Deterministic in-memory
fixtures only (no real data, no research_state writes, no network).
"""

from __future__ import annotations

import json
import math
import random
import tempfile
from pathlib import Path

import pytest

import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64
import scripts.eval65_orderflow_tox_rv_predictiveness as e65
import scripts.eval66_eth_oflow_tox_rv_oos as e66


def _craft_capture(n_bars=120, seed=0, inst="ETH", n_trades_per_bar=3,
                   n_of_instruments=150, signal_to_vol=0.0):
    rng = random.Random(seed)
    base_ms = 1_700_000_000_000
    bar_ms = 300_000
    px = 3000.0 if inst == "ETH" else 60000.0
    candles = []
    trades = []
    for i in range(n_bars):
        tox = rng.uniform(-1, 1)
        drift = tox * signal_to_vol + rng.uniform(-1, 1) * 1e-4
        px = max(1.0, px * (1 + drift))
        candles.append({"ts": base_ms + i * bar_ms, "open": px, "high": px,
                        "low": px, "close": px})
        sign = 1.0 if tox >= 0 else -1.0
        for _ in range(n_trades_per_bar):
            direction = "buy" if sign > 0 else "sell"
            opt = "call" if rng.random() < 0.5 else "put"
            strike = round(px + rng.randint(-2, 2) * 50, 2)
            amt = rng.uniform(0.1, 2.0)
            inst_name = f"{inst}-OPT-{i % max(1, n_of_instruments)}"
            trades.append({
                "ts": base_ms + i * bar_ms + rng.randint(1, bar_ms - 1),
                "instrument": inst_name,
                "direction": direction,
                "amount": amt,
                "price": 0.01,
                "index_price": px,
                "iv": 0.8,
                "option_type": opt,
                "strike": strike,
                "expiry": "2026-12-30T08:00:00Z",
            })

    snaps = []
    for i in range(n_bars):
        bar_ms_i = base_ms + i * bar_ms
        spot = candles[i]["close"]
        strike = round(spot, 2)
        mark = 0.1
        quotes = []
        for opt in ("call", "put"):
            quotes.append({
                "symbol": f"{inst}-OPT-{int(strike)}-{opt[0].upper()}-{i}",
                "underlying": inst,
                "strike": strike,
                "expiry": "2026-12-30T08:00:00Z",
                "option_type": opt,
                "bid": mark * 0.98,
                "ask": mark * 1.02,
                "mark": mark,
                "open_interest": 100.0,
                "volume": 10.0,
                "timestamp": "2023-11-14T00:00:00Z",
            })
        snaps.append({"bar_ms": bar_ms_i, "spot": spot, "quotes": quotes})

    return {
        "schema": "three_way_options_surface_orderflow_okx_perp_capture_v1",
        "underlying": inst,
        "venue": "deribit+okx",
        "window_start": "2023-11-14T00:00:00Z",
        "window_end": "2023-11-15T00:00:00Z",
        "surface": {"bar_seconds": 300, "resolution": "5", "snapshots": snaps},
        "option_trades": trades,
        "perp_candles": candles,
        "okx_inst_id": f"{inst}-USD-SWAP",
        "okx_perp_trades": [],
        "source": {"authenticated": False, "public_read_only": True, "venue": "deribit+okx"},
    }


def test_ids_are_eval66():
    assert e66.REPORT_ID == "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED"
    assert e66.PREREG_ID == "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION"
    assert e66.BLOCKED_ID == "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED"


def test_configs_restricted_to_suggestive_slice():
    assert e66.TOX_SIGNALS == ("tox", "imbalance")
    assert e66.GRID_BAR_SECONDS == (60.0,)
    assert e66.FORWARD_HORIZONS_BARS == (72,)
    assert e66.MIN_UNDERLYINGS == 1


def test_reuses_sealed_builders_and_floor():
    assert e66.e62.build_states is e62.build_states
    assert e66._underlying_floor_strict is e64._underlying_floor_strict
    assert e66.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e66.FDR_ALPHA == e65.FDR_ALPHA


def test_evaluate_predictiveness_runs_eth():
    cap = _craft_capture(n_bars=220, seed=1, inst="ETH", signal_to_vol=0.02)
    res = e66.evaluate_predictiveness(
        cap, tox_signal="tox", bar_seconds=60.0, horizon_bars=72
    )
    assert res["underlying"] == "ETH"
    assert res["n_pairs"] > 0
    assert "spearman_ic" in res and "permutation_p" in res and "pass" in res
    assert len(res["bootstrap_ci"]) == 3


def test_run_eval66_no_write_blocks_below_floor():
    cap = _craft_capture(n_bars=40, seed=7, inst="ETH")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "three_way_ETH_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
        report = e66.run_eval66(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e66.REPORT_ID


def test_run_eval66_refuses_to_seal_empty_capture_dir():
    with tempfile.TemporaryDirectory() as td:
        with pytest.raises(e66.NoRealCaptureError):
            e66.run_eval66(capture_dir=td, write=True)


def test_run_eval66_refuses_to_seal_dir_with_only_btc_capture():
    btc = _craft_capture(n_bars=1010, seed=8, inst="BTC")
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "three_way_BTC_20230101T000000Z.json").write_text(json.dumps(btc))
        with pytest.raises(e66.NoRealCaptureError):
            e66.run_eval66(capture_dir=td, write=True)


def test_run_eval66_filters_to_eth_only_and_counts_configs():
    eth = _craft_capture(n_bars=1010, seed=3, inst="ETH", n_trades_per_bar=2,
                         n_of_instruments=150, signal_to_vol=0.0)
    btc = _craft_capture(n_bars=1010, seed=4, inst="BTC", n_trades_per_bar=2,
                         n_of_instruments=150, signal_to_vol=0.0)
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "three_way_ETH_20230101T000000Z.json").write_text(json.dumps(eth))
        (Path(td) / "three_way_BTC_20230101T000000Z.json").write_text(json.dumps(btc))
        report = e66.run_eval66(capture_dir=td, write=False)
    assert report["underlyings"] == ["ETH"]
    # 2 signals * 1 bar grid * 1 horizon = 2 configs, ETH only
    assert len(report["per_config"]) == 2
    assert all(r["underlying"] == "ETH" for r in report["per_config"])


def test_run_eval66_meets_floor_for_single_eth():
    eth = _craft_capture(n_bars=1010, seed=5, inst="ETH", n_trades_per_bar=2,
                         n_of_instruments=150, signal_to_vol=0.0)
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "three_way_ETH_20230101T000000Z.json").write_text(json.dumps(eth))
        report = e66.run_eval66(capture_dir=td, write=False)
    assert report["per_underlying_floor"]["ETH"]["ok"] is True
    assert report["floor_ok"] is True
    assert report["verdict"] in ("NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    assert len(report["per_config"]) == 2
