"""Unit tests for EVAL-64: feasible-floor replication of the EVAL-62 namesake
hypothesis (real options order-flow toxicity -> signal-timed delta-hedged ATM
straddle, correct EVAL-57 mark-path net-of-cost P&L).

EVAL-64 keeps the EVAL-62 measurement byte-for-byte identical (it imports the
sealed EVAL-62 module) and only changes the pre-registered floor to the heaviest
floor the free Deribit/OKX public API can actually deliver.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin three things the next session must not break:
1. the **feasible split floor** (surface/perp need the full achievable window;
   options order flow is 24h-capped by Deribit retention) passes a heavy capture
   and blocks a 24h one;
2. the **measurement is reused verbatim** from sealed EVAL-62 (no divergent
   re-implementation, no re-introduced EVAL-61 dollar-P&L-as-return artifact);
3. ``run_eval64(write=False)`` reports BLOCKED (never NO-GO) below the floor.
"""

from __future__ import annotations

import json
import random
import tempfile
from pathlib import Path

import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64


def _craft_capture(n_bars=120, seed=0, inst="BTC", n_trades_per_bar=3,
                   n_of_instruments=150, n_snapshots=None):
    """In-memory capture fixture. ``n_of_instruments`` distinct trade instruments
    and one surface snapshot per bar (each with a distinct quote symbol)."""
    rng = random.Random(seed)
    base_ms = 1_700_000_000_000
    bar_ms = 300_000
    px = 60000.0 if inst == "BTC" else 3000.0
    candles = []
    trades = []
    drifts = [rng.uniform(-1, 1) for _ in range(n_bars)]
    for i in range(n_bars):
        px = max(1.0, px * (1 + drifts[i] * 1e-4))
        candles.append({"ts": base_ms + i * bar_ms, "open": px, "high": px,
                        "low": px, "close": px})
        sign = 1.0 if drifts[i] >= 0 else -1.0
        for _ in range(n_trades_per_bar):
            direction = "buy" if sign > 0 else "sell"
            opt = "call" if rng.random() < 0.5 else "put"
            strike = round(px + rng.randint(-2, 2) * 500, 2)
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
    snap_count = n_snapshots if n_snapshots is not None else n_bars
    for i in range(min(snap_count, n_bars)):
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


def test_ids_are_eval64_feasible():
    assert e64.REPORT_ID.startswith("EVAL_64_")
    assert e64.PREREG_ID.startswith("EVAL_64_")
    assert e64.BLOCKED_ID.startswith("EVAL_64_")
    assert "FEASIBLE_OFLOW_RV_MARKPATH" in e64.REPORT_ID
    assert "FEASIBLE_OFLOW_RV_MARKPATH" in e64.PREREG_ID


def test_measurement_reused_verbatim_from_eval62():
    """EVAL-64 must reuse the sealed EVAL-62 measurement, not fork it."""
    assert e64.e62.build_states is e62.build_states
    assert e64.e62.markpath_returns is e62.markpath_returns
    assert e64.e62.evaluate_config is e62.evaluate_config


def test_markpath_returns_are_spot_normalized_not_dollar_pnl():
    """Regression guard: a large mark jump yields a *return*, not EVAL-61 dollars."""
    states = [
        {"spot": 100.0, "side": 1, "exposure": 1.0, "straddle_delta": 0.5,
         "straddle_mark": 2.0, "spread_usd": 0.0, "signal_z": 1.0, "bar_ms": 0},
        {"spot": 100.0, "side": 1, "exposure": 1.0, "straddle_delta": 0.5,
         "straddle_mark": 1000.0, "spread_usd": 0.0, "signal_z": 1.0, "bar_ms": 300_000},
    ]
    out = e64.e62.markpath_returns(states, hedge_fee_bps=5.0)
    # spot-normalized: ret = (dOption + hedge*dS - cost)/S0, NOT the raw dollar P&L.
    dollar_pnl = 998.0 * 100.0 - 5.0 * 0.5 * 100.0 / 1e4  # ~99799.975
    expected = dollar_pnl / 100.0
    assert abs(out["returns"][0] - expected) < 1e-9
    # the EVAL-61 artifact would have been the un-normalized dollar P&L (~99799.975)
    assert abs(out["returns"][0] - dollar_pnl) > 1.0


def test_protocol_documents_feasible_floor_and_ceiling():
    proto = e64.build_protocol("data/raw/eval63")
    fl = proto["floor"]
    # Feasible floor constants are pinned (do not drift).
    assert fl["min_surface_snapshots_per_underlying"] == 1000
    assert fl["min_surface_bars_5m_per_underlying"] == 1000
    assert fl["min_perp_bars_5m_per_underlying"] == 1000
    assert fl["min_perp_span_seconds_per_underlying"] == 300000.0
    assert fl["min_option_trades_per_underlying"] == 2000
    assert fl["min_common_bars_per_underlying"] == 240
    assert fl["min_underlyings"] == 2
    # The floor is heavier than EVAL-62 on the achievable surface/perp legs.
    p62 = e62.build_protocol("data/raw/eval61")["floor"]
    assert fl["min_surface_snapshots_per_underlying"] > p62["min_surface_snapshots_per_underlying"]
    assert fl["min_surface_bars_5m_per_underlying"] > p62["min_bars_per_underlying"]
    assert fl["min_perp_span_seconds_per_underlying"] > p62["min_span_seconds_per_underlying"]
    # EVAL-64 must document the measured data-availability ceiling (why OF is 24h).
    assert "data_availability" in proto
    assert proto["data_availability"]["deribit_option_trade_retention_seconds_approx"] == 86400
    assert proto["data_availability"]["deribit_perp_1m_candle_retention_seconds_measured"] == 300000
    assert "duration_note" in proto
    assert "extends" in proto and "EVAL-62" in proto["extends"]


def test_feasible_floor_blocks_24h_capture():
    # ~24h capture (289 bars): below the 7d surface/perp floor.
    cap = _craft_capture(n_bars=289, seed=2)
    fl = e64._underlying_floor_strict(cap)
    assert fl["ok"] is False
    assert fl["checks"]["surface_bars_ok"] is False
    assert fl["checks"]["perp_span_ok"] is False
    assert fl["n_surface_bars_5m"] < e64.MIN_SURFACE_BARS_5M


def test_feasible_floor_passes_heavy_capture():
    # 1010 bars * 300s = 302700s perp span, 2020 trades, 150 instruments, 1010 snaps.
    cap = _craft_capture(n_bars=1010, seed=3, n_trades_per_bar=2, n_of_instruments=150)
    fl = e64._underlying_floor_strict(cap)
    assert fl["ok"] is True, fl["checks"]
    assert all(fl["checks"].values())
    assert fl["n_surface_bars_5m"] >= e64.MIN_SURFACE_BARS_5M
    assert fl["perp_span_seconds"] >= e64.MIN_PERP_SPAN_SECONDS
    assert fl["n_option_trades"] >= e64.MIN_OPTION_TRADES
    assert fl["n_of_instruments"] >= e64.MIN_OF_INSTRUMENTS
    assert fl["n_common_bars_5m"] >= e64.MIN_COMMON_BARS


def test_run_eval64_no_write_blocks_below_floor():
    cap = _craft_capture(n_bars=40, seed=7)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "three_way_BTC_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
        report = e64.run_eval63(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e64.REPORT_ID


def test_evaluate_config_via_reused_helper_runs():
    cap = _craft_capture(n_bars=80, seed=3)
    res = e64.e62.evaluate_config(cap, tox_signal="tox", bar_seconds=300.0)
    assert res["underlying"] == "BTC"
    assert res["n_returns"] > 0
    assert "sharpe" in res and "pass" in res
    assert res["max_drawdown"] <= 1.0