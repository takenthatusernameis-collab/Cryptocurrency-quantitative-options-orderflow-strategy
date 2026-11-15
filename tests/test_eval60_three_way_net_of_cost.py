"""Unit tests for the POST-EVAL / EVAL-60 three-way (Deribit options surface x
Deribit options-venue order flow x OKX perpetual order flow) net-of-cost falsification.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.
"""

from __future__ import annotations

import math
import random

import scripts.eval60_three_way_net_of_cost as e60


def _craft_capture(n_bars=120, seed=0, inst="BTC", n_trades_per_bar=3,
                   n_okx_per_bar=3, n_snapshots=None):
    rng = random.Random(seed)
    base_ms = 1_700_000_000_000
    bar_ms = 300_000
    px = 60000.0 if inst == "BTC" else 3000.0
    candles = []
    trades = []
    okx_trades = []
    tid = 0
    oid = 0
    drifts = [rng.uniform(-1, 1) for _ in range(n_bars)]
    for i in range(n_bars):
        px = max(1.0, px * (1 + drifts[i] * 1e-4))
        candles.append({"ts": base_ms + i * bar_ms, "open": px, "high": px,
                        "low": px, "close": px})
        sign = 1.0 if drifts[i] >= 0 else -1.0
        for _ in range(n_trades_per_bar):
            tid += 1
            direction = "buy" if sign > 0 else "sell"
            opt = "call" if rng.random() < 0.5 else "put"
            strike = round(px + rng.randint(-2, 2) * 500, 2)
            trades.append({
                "ts": base_ms + i * bar_ms + rng.randint(1, bar_ms - 1),
                "instrument": f"{inst}-30DEC26-{int(strike)}-{opt[0].upper()}",
                "direction": direction,
                "amount": rng.uniform(0.1, 2.0),
                "price": 0.01,
                "index_price": px,
                "iv": 50.0,
                "option_type": opt,
                "strike": strike,
                "expiry": "2026-12-30T08:00:00Z",
            })
        for _ in range(n_okx_per_bar):
            oid += 1
            okx_trades.append({
                "ts": base_ms + i * bar_ms + rng.randint(1, bar_ms - 1),
                "px": px,
                "sz": rng.uniform(0.1, 3.0),
                "side": "buy" if sign > 0 else "sell",
                "instrument": f"{inst}-USD-SWAP",
                "trade_id": str(oid),
            })

    snaps = []
    snap_count = n_snapshots if n_snapshots is not None else n_bars
    for i in range(min(snap_count, n_bars)):
        bar_ms_i = base_ms + i * bar_ms
        spot = candles[i]["close"]
        quotes = []
        for k in (-2, -1, 0, 1, 2):
            strike = round(spot + k * 500, 2)
            for opt in ("call", "put"):
                mark = max(0.01, 0.05 * spot + (0.01 if opt == "call" else 0.02))
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
                    "timestamp": f"2023-11-14T00:{i%60:02d}:00Z",
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
        "okx_perp_trades": okx_trades,
        "source": {"authenticated": False, "public_read_only": True, "venue": "deribit+okx"},
    }


def test_build_bars_attaches_both_order_flow_legs_and_return():
    cap = _craft_capture(n_bars=40)
    surf = e60.surface_signal_series(cap, cap["perp_candles"])
    bars = e60.build_bars(cap, surf, bar_seconds=300.0)
    assert len(bars) >= 30
    ends = [b["bar_end"] for b in bars]
    assert ends == sorted(ends)
    assert all(math.isfinite(b["imbalance"]) for b in bars)
    assert all(math.isfinite(b[e60.OKX_SIGNAL]) for b in bars)
    assert all("ret" in b and "surface" in b for b in bars)
    assert bars[-1]["ret"] == 0.0


def test_deribit_signed_flow_signs_and_notional():
    cap = {
        "perp_candles": [{"ts": 0, "close": 100.0}, {"ts": 300000, "close": 100.0}],
        "option_trades": [
            {"ts": 1000, "direction": "buy", "amount": 2.0, "index_price": 100.0, "option_type": "call"},
        ],
        "okx_perp_trades": [],
        "surface": {"snapshots": []},
        "underlying": "BTC", "venue": "deribit+okx",
    }
    b = e60.build_bars(cap, [], bar_seconds=300.0)
    active = [x for x in b if x["n_trades"] > 0]
    assert active and active[0]["imbalance"] > 0

    cap2 = {
        "perp_candles": [{"ts": 0, "close": 100.0}, {"ts": 300000, "close": 100.0}],
        "option_trades": [
            {"ts": 1000, "direction": "buy", "amount": 1.0, "index_price": 200.0, "option_type": "call"},
            {"ts": 2000, "direction": "sell", "amount": 1.0, "index_price": 100.0, "option_type": "call"},
        ],
        "okx_perp_trades": [],
        "surface": {"snapshots": []},
        "underlying": "BTC", "venue": "deribit+okx",
    }
    b2 = e60.build_bars(cap2, [], bar_seconds=300.0)
    a2 = [x for x in b2 if x["n_trades"] > 0]
    assert abs(a2[0]["imbalance"]) < 1e-12
    assert a2[0]["notional_imbalance"] > 0


def test_okx_perp_signed_flow_signs():
    cap = {
        "perp_candles": [{"ts": 0, "close": 100.0}, {"ts": 300000, "close": 100.0}],
        "option_trades": [],
        "okx_perp_trades": [
            {"ts": 1000, "px": 100.0, "sz": 5.0, "side": "buy", "trade_id": "1"},
            {"ts": 2000, "px": 100.0, "sz": 1.0, "side": "sell", "trade_id": "2"},
        ],
        "surface": {"snapshots": []},
        "underlying": "BTC", "venue": "deribit+okx",
    }
    b = e60.build_bars(cap, [], bar_seconds=300.0)
    active = [x for x in b if x["okx_n_trades"] > 0]
    assert active and active[0][e60.OKX_SIGNAL] > 0


def test_three_way_fusion_rules():
    s = [1.0, -1.0, 1.0, 0.0]
    f = [1.0, -1.0, -1.0, 1.0]
    o = [1.0, -1.0, 1.0, 0.0]
    assert e60.fuse_three_way_sign_agreement(s, f, o) == [1.0, -1.0, 0.0, 0.0]
    assert e60.fuse_three_way_regime_filter(s, f, o) == [1.0, 1.0, 0.0, 0.0]
    cz = e60.fuse_three_way_continuous_zscore(s, f, o)
    assert len(cz) == 4 and all(-1.0 <= v <= 1.0 for v in cz)


def test_expanding_zscore_and_strategy_returns():
    zs = e60.expanding_zscore([1, 1, 1, 5, 1], window=5)
    assert len(zs) == 5
    bars = [{"ret": 0.01}, {"ret": -0.01}, {"ret": 0.0}]
    out = e60.strategy_returns(bars, [1.0, 1.0, 0.0], cost_bps=5.0)
    assert len(out["returns"]) == 2
    assert out["nonzero"] == 2
    assert out["returns"][0] < 0.01


def test_floor_blocks_short_capture():
    cap = _craft_capture(n_bars=30, seed=2)  # far below floor
    fl = e60._underlying_floor(cap)
    assert fl["ok"] is False
    assert any(not v for v in fl["checks"].values())
    # OKX-leg floor checks are present and fail on a short capture.
    assert "okx_trades_ok" in fl["checks"]
    assert fl["checks"]["okx_trades_ok"] is False


def test_floor_blocks_missing_okx_leg():
    cap = _craft_capture(n_bars=80, seed=5)
    cap["okx_perp_trades"] = []  # remove the third leg
    fl = e60._underlying_floor(cap)
    assert fl["ok"] is False
    assert fl["checks"]["okx_trades_ok"] is False
    assert fl["checks"]["common_overlap_ok"] is False


def test_evaluate_config_runs():
    cap = _craft_capture(n_bars=80, seed=3)
    surf = e60.surface_signal_series(cap, cap["perp_candles"])
    res = e60.evaluate_config(
        cap, surf, fusion="three_way_sign_agreement",
        of_signal="imbalance", bar_seconds=300.0,
    )
    assert res["underlying"] == "BTC"
    assert res["n_returns"] > 0
    assert "sharpe" in res and "pass" in res


def test_protocol_and_floor_constants():
    p = e60.build_protocol("data/raw/eval60")
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_surface_snapshots_per_underlying"] == 100
    assert p["floor"]["min_okx_perp_trades_per_underlying"] == 2000
    assert set(p["fusion_rules"]) == {
        "three_way_sign_agreement",
        "three_way_regime_filter",
        "three_way_continuous_zscore",
    }
    assert p["okx_orderflow_signal"] == "okx_imbalance"


def test_run_eval60_no_write_blocks_below_floor():
    # A single short capture: floor must be False and no verdict sealed (write=False).
    cap = _craft_capture(n_bars=40, seed=7)
    import json
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "three_way_BTC_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
        report = e60.run_eval60(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"