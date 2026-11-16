"""Unit tests for EVAL-69: pooled BTC+ETH OOS traded-form net-of-cost monetization
of the suggestive EVAL-65 options order-flow toxicity slice (tox/imbalance, bar60),
pooled-sample Sharpe / max-DD / permutation / bootstrap.

Thin extension of EVAL-68/EVAL-64: reuses EVAL-62 build_states + markpath_returns
(signal + spot + per-bar net-of-cost P&L) and the EVAL-64 feasible floor; requires
BOTH BTC and ETH, pools their per-bar net-of-cost returns into one sample, and
requires >=790 pooled returns for power adequacy. Reuses EVAL-68's disjoint forward
capture (no acquisition). Deterministic in-memory fixtures only (no real data, no
research_state writes, no network).
"""

from __future__ import annotations

import json
import random
import tempfile
from pathlib import Path

import pytest

import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64
import scripts.eval67_btc_oflow_tox_rv_oos as e67
import scripts.eval69_pooled_btc_eth_oflow_tox_rv_traded_oos as e69


def _craft_capture(n_bars=120, seed=0, inst="BTC", n_trades_per_bar=3,
                   n_of_instruments=150, signal_to_vol=0.0):
    rng = random.Random(seed)
    base_ms = 1_700_000_000_000
    bar_ms = 300_000
    px = 60000.0 if inst == "BTC" else 3000.0
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


def _write_pair(td, btc=None, eth=None):
    if btc is not None:
        (Path(td) / "three_way_BTC_20230101T000000Z.json").write_text(json.dumps(btc))
    if eth is not None:
        (Path(td) / "three_way_ETH_20230101T000000Z.json").write_text(json.dumps(eth))


# ---------------------------------------------------------------------------
# Constants / identifiers
# ---------------------------------------------------------------------------
def test_ids_are_eval69():
    assert e69.REPORT_ID == "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_COMBINED"
    assert e69.PREREG_ID == "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_PREREGISTRATION"
    assert e69.BLOCKED_ID == "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_BLOCKED"


def test_configs_restricted_to_suggestive_slice_and_pooled():
    assert e69.TOX_SIGNALS == ("tox", "imbalance")
    assert e69.GRID_BAR_SECONDS == (60.0,)
    assert e69.MIN_UNDERLYINGS == 2
    assert e69.UNDERLYINGS == ("BTC", "ETH")
    assert e69.MIN_POOLED_RETURNS == 790
    # Reuses EVAL-68's capture (no acquisition).
    assert e69.DEFAULT_CAPTURE_DIR == "data/raw/eval68"


def test_reuses_sealed_builders_floor_and_eval67():
    assert e69.e62.build_states is e62.build_states
    assert e69.e62.markpath_returns is e62.markpath_returns
    assert e69._underlying_floor_strict is e64._underlying_floor_strict
    assert e69.PERMUTATION_PERMS == e62.PERMUTATION_PERMS
    assert e69.FDR_ALPHA == e62.FDR_ALPHA
    assert e69.KILL_SWITCH_MAX_DD == e62.KILL_SWITCH_MAX_DD
    # Disjointness math reused verbatim from EVAL-67.
    assert e69.e67.check_disjointness is e67.check_disjointness


# ---------------------------------------------------------------------------
# extract_returns / evaluate_pooled_traded
# ---------------------------------------------------------------------------
def test_extract_returns_matches_eval62_markpath():
    cap = _craft_capture(n_bars=220, seed=1, inst="BTC", signal_to_vol=0.02)
    res = e69.extract_returns(cap, tox_signal="tox", bar_seconds=60.0)
    # Mirror eval62's own count for the same capture/config.
    states = e62.build_states(cap, tox_signal="tox", bar_seconds=60.0)
    ref = e62.markpath_returns(states)
    assert len(res["returns"]) == len(ref["returns"])
    assert res["n_states"] == len(states)
    assert res["nonzero_positions"] == ref["nonzero"]


def test_evaluate_pooled_traded_runs_btc_eth():
    caps = [
        _craft_capture(n_bars=220, seed=1, inst="BTC", signal_to_vol=0.02),
        _craft_capture(n_bars=220, seed=2, inst="ETH", signal_to_vol=0.02),
    ]
    res = e69.evaluate_pooled_traded(caps, tox_signal="tox", bar_seconds=60.0)
    assert res["underlyings"] == ["BTC", "ETH"]
    assert res["n_returns"] == sum(
        v["n_returns"] for v in res["per_underlying"].values()
    )
    assert res["n_returns"] > 0
    assert "sharpe" in res and "permutation_p" in res and "pass" in res
    assert "max_drawdown" in res and "kill_switch_breach" in res
    assert len(res["bootstrap_ci"]) == 3


def test_evaluate_pooled_traded_power_flag_below_threshold():
    caps = [
        _craft_capture(n_bars=120, seed=1, inst="BTC"),
        _craft_capture(n_bars=120, seed=2, inst="ETH"),
    ]
    res = e69.evaluate_pooled_traded(caps, tox_signal="tox", bar_seconds=60.0)
    assert res["n_returns"] < e69.MIN_POOLED_RETURNS
    assert res["n_returns_power_adequate"] is False
    # Even a huge Sharpe cannot pass without power adequacy.
    assert res["pass"] is False


def test_evaluate_pooled_traded_power_flag_above_threshold():
    caps = [
        _craft_capture(n_bars=1010, seed=1, inst="BTC", signal_to_vol=0.02),
        _craft_capture(n_bars=1010, seed=2, inst="ETH", signal_to_vol=0.02),
    ]
    res = e69.evaluate_pooled_traded(caps, tox_signal="tox", bar_seconds=60.0)
    assert res["n_returns"] >= e69.MIN_POOLED_RETURNS
    assert res["n_returns_power_adequate"] is True


# ---------------------------------------------------------------------------
# run_eval69 orchestration
# ---------------------------------------------------------------------------
def test_run_eval69_no_write_blocks_below_floor():
    btc = _craft_capture(n_bars=40, seed=7, inst="BTC")
    eth = _craft_capture(n_bars=40, seed=8, inst="ETH")
    with tempfile.TemporaryDirectory() as td:
        _write_pair(td, btc=btc, eth=eth)
        report = e69.run_eval69(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e69.REPORT_ID


def test_run_eval69_refuses_to_seal_empty_capture_dir():
    with tempfile.TemporaryDirectory() as td:
        with pytest.raises(e69.NoRealCaptureError):
            e69.run_eval69(capture_dir=td, write=True)


def test_run_eval69_blocks_when_eth_missing():
    btc = _craft_capture(n_bars=1010, seed=5, inst="BTC")
    with tempfile.TemporaryDirectory() as td:
        _write_pair(td, btc=btc)
        report = e69.run_eval69(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["missing_underlyings"] == ["ETH"]
    assert report["verdict"] == "BLOCKED"


def test_run_eval69_pooled_meets_floor_and_counts_configs():
    btc = _craft_capture(n_bars=1010, seed=3, inst="BTC", signal_to_vol=0.02)
    eth = _craft_capture(n_bars=1010, seed=4, inst="ETH", signal_to_vol=0.02)
    with tempfile.TemporaryDirectory() as td:
        _write_pair(td, btc=btc, eth=eth)
        report = e69.run_eval69(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["disjointness_ok"] is True
    assert report["underlyings"] == ["BTC", "ETH"]
    assert report["verdict"] in ("NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    # 2 signals * 1 bar grid = 2 pooled configs.
    assert len(report["per_config"]) == 2
    assert report["pooled"]["power_adequate"] is True


def test_run_eval69_pooled_returns_are_sum_of_underlyings():
    btc = _craft_capture(n_bars=1010, seed=3, inst="BTC")
    eth = _craft_capture(n_bars=1010, seed=4, inst="ETH")
    with tempfile.TemporaryDirectory() as td:
        _write_pair(td, btc=btc, eth=eth)
        report = e69.run_eval69(capture_dir=td, write=False)
    for cfg in report["per_config"]:
        s = {k: v["n_returns"] for k, v in cfg["per_underlying"].items()}
        assert cfg["n_returns"] == s["BTC"] + s["ETH"]


def test_run_eval69_blocks_non_disjoint_even_if_floor_ok():
    btc = _craft_capture(n_bars=1010, seed=9, inst="BTC", signal_to_vol=0.0)
    eth = _craft_capture(n_bars=1010, seed=10, inst="ETH", signal_to_vol=0.0)
    btc["window_start"] = "2026-11-10T00:00:00Z"
    btc["window_end"] = "2026-11-13T00:00:00Z"
    eth["window_start"] = "2026-11-10T00:00:00Z"
    eth["window_end"] = "2026-11-13T00:00:00Z"
    with tempfile.TemporaryDirectory() as td:
        _write_pair(td, btc=btc, eth=eth)
        report = e69.run_eval69(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["disjointness_ok"] is False
    assert report["floor_and_disjoint_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["pooled"]["campaign_state"] == "EVAL_69_BLOCKED_FLOOR_OR_DISJOINTNESS"


# ---------------------------------------------------------------------------
# Prereg emission (design; no capture)
# ---------------------------------------------------------------------------
def test_build_prereg_document_has_power_and_floor():
    prereg = e69.build_prereg_document()
    p = prereg["protocol"]
    assert p["underlyings_required"] == ["BTC", "ETH"]
    assert p["min_pooled_returns"] == 790
    assert p["min_underlyings"] == 2
    assert prereg["prereg_id"] == e69.PREREG_ID
    assert "pooled" in p["statistic"].lower() or "pooled" in p["title"].lower()
    # EVAL-69 must document that it reuses EVAL-68's capture (no acquisition).
    assert "EVAL-68" in p["capture_window_rule"]