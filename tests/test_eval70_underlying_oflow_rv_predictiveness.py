"""Unit tests for EVAL-70: wrapper-free underlying (OKX perp) order-flow ->
realized-vol / signed-return predictiveness (Spearman rank IC) falsification.

EVAL-70 is the on-charter, runnable-now complement to EVAL-65: same Spearman
rank-IC statistic (reused verbatim from EVAL-65), but a different signal source
(the underlying perp tape rather than the options tape). It needs no options
surface and no new acquisition.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin five things the next session must not break:
1. the artifact ids are EVAL-70;
2. the statistic (permutation / bootstrap / Spearman) is reused verbatim from
   EVAL-65, not forked;
3. ``build_perp_bars`` computes a causal signed-aggressor imbalance on the bar grid;
4. the pre-registered perp-tape floor blocks (never NO-GO) below floor;
5. ``run_eval70(write=False)`` reports BLOCKED below floor and produces a summary
   above floor.
"""

from __future__ import annotations

import json
import math
import random
import tempfile
from pathlib import Path

import scripts.eval61_orderflow_realized_vol_net_of_cost as e61
import scripts.eval65_orderflow_tox_rv_predictiveness as e65
import scripts.eval70_underlying_oflow_rv_predictiveness as e70


def _craft_capture(
    inst="BTC",
    *,
    n_bars=300,
    seed=0,
    signal_to_vol=0.0,
    n_trades_per_bar=40,
    ar=0.8,
):
    """In-memory capture fixture with an AR(1) latent toxicity that drives both
    the perp signed-aggressor imbalance and the forward return/volatility.

    ``signal_to_vol`` > 0 plants a persistent signal -> forward vol/return
    relationship the Spearman IC should detect.
    """
    rng = random.Random(seed)
    bar_ms = 300_000
    base_ms = 1_700_000_000_000
    base_ms -= base_ms % bar_ms
    px = 60000.0 if inst == "BTC" else 3000.0
    candles = []
    trades = []
    tox = 0.0
    for i in range(n_bars):
        tox = ar * tox + rng.uniform(-1, 1) * (1.0 - ar)
        tox = max(-1.0, min(1.0, tox))
        drift = tox * signal_to_vol + rng.uniform(-1, 1) * 1e-4
        px = max(1.0, px * (1.0 + drift))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        frac_buy = min(0.95, max(0.05, 0.5 + 0.4 * tox))
        n_buy = int(round(n_trades_per_bar * frac_buy))
        for j in range(n_trades_per_bar):
            side = "buy" if j < n_buy else "sell"
            trades.append({
                "ts": ts + rng.randint(1, bar_ms - 1),
                "px": px,
                "sz": 1.0,
                "side": side,
                "instrument": f"{inst}-USD-SWAP",
                "trade_id": str(i * n_trades_per_bar + j),
            })
    return {
        "schema": "three_way_options_surface_orderflow_okx_perp_capture_v1",
        "underlying": inst,
        "venue": "deribit+okx",
        "window_start": "2023-11-14T00:00:00Z",
        "window_end": "2023-11-15T00:00:00Z",
        "surface": {"bar_seconds": 300, "resolution": "5", "snapshots": []},
        "option_trades": [],
        "perp_candles": candles,
        "okx_inst_id": f"{inst}-USD-SWAP",
        "okx_perp_trades": trades,
        "source": {"authenticated": False, "public_read_only": True, "venue": "deribit+okx"},
    }


def test_ids_are_eval70():
    assert e70.REPORT_ID.startswith("EVAL_70_")
    assert e70.PREREG_ID.startswith("EVAL_70_")
    assert e70.BLOCKED_ID.startswith("EVAL_70_")
    assert "UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS" in e70.REPORT_ID


def test_statistic_reused_verbatim_from_eval65():
    """EVAL-70 must reuse the sealed EVAL-65 statistics, not fork them."""
    assert e70.e65._perm_p_ic is e65._perm_p_ic
    assert e70.e65._boot_ci_ic is e65._boot_ci_ic
    assert e70.e65._spearman is e65._spearman
    assert e70.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e70.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e70.SEED == e65.SEED


def test_build_perp_bars_is_causal_and_signed():
    cap = _craft_capture("BTC", n_bars=10, seed=1, n_trades_per_bar=20)
    bars = e70.build_perp_bars(cap, bar_seconds=300.0)
    assert len(bars) == 10
    # strictly ascending, non-overlapping bar opens
    opens = [b["bar_open_ms"] for b in bars]
    assert opens == sorted(opens)
    assert len(set(opens)) == len(opens)
    for b in bars:
        assert b["buy_vol"] + b["sell_vol"] > 0.0
        assert -1.0 <= b["imbalance"] <= 1.0
        assert abs(b["tox"] - abs(b["imbalance"])) < 1e-12


def test_forward_targets_are_causal():
    bars = [
        {"close": 100.0},
        {"close": 110.0},
        {"close": 121.0},
        {"close": 133.1},
    ]
    out = e70._forward_targets(bars, 2)
    # log returns: log(1.1), log(1.1), log(1.1)
    lr = math.log(1.1)
    assert len(out["rv"]) == 2
    assert abs(out["rv"][0] - lr) < 1e-9
    assert abs(out["signed_return"][0] - 2.0 * lr) < 1e-9


def test_evaluate_predictiveness_runs_and_is_causal():
    cap = _craft_capture("BTC", n_bars=200, seed=1, signal_to_vol=0.02)
    res = e70.evaluate_predictiveness(
        cap, tox_signal="imbalance", bar_seconds=300.0,
        horizon_bars=6, target="rv",
    )
    assert res["underlying"] == "BTC"
    assert res["n_pairs"] > 0
    assert "spearman_ic" in res and "permutation_p" in res and "pass" in res
    assert len(res["bootstrap_ci"]) == 3


def test_floor_blocks_below_floor():
    cap = _craft_capture("BTC", n_bars=40, seed=7, n_trades_per_bar=3)
    fl = e70._underlying_oflow_floor(cap)
    assert fl["ok"] is False
    assert fl["checks"]["trades_ok"] is False
    assert fl["checks"]["candles_ok"] is False


def test_floor_passes_on_heavy_capture():
    # 1010 bars * 300s = 303000s span, 1010 candles, 1010*50 = 50500 trades.
    cap = _craft_capture("BTC", n_bars=1010, seed=3, n_trades_per_bar=50)
    fl = e70._underlying_oflow_floor(cap)
    assert fl["n_perp_trades"] >= e70.FLOOR["min_perp_trades_per_underlying"]
    assert fl["perp_span_seconds"] >= e70.FLOOR["min_perp_span_seconds_per_underlying"]
    assert fl["n_perp_bars_5m"] >= e70.FLOOR["min_perp_bars_5m_per_underlying"]
    assert fl["ok"] is True


def test_run_eval70_no_write_blocks_below_floor():
    cap = _craft_capture("BTC", n_bars=40, seed=7, n_trades_per_bar=3)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "three_way_BTC_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
        report = e70.run_eval70(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e70.REPORT_ID


def test_run_eval70_no_write_meets_floor_and_summarizes(monkeypatch):
    # Keep the orchestration path fast: one signal/target pair, one bar grid, one
    # horizon, few permutations. The floor itself is NOT weakened (real 50500-trade
    # fixtures above).
    monkeypatch.setattr(e70, "SIGNAL_TARGETS", (("tox", "rv"),))
    monkeypatch.setattr(e70, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e70, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e70, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e70, "BOOTSTRAP_RESAMPLES", 50)

    caps = {
        "BTC": _craft_capture("BTC", n_bars=1010, seed=3, n_trades_per_bar=50),
        "ETH": _craft_capture("ETH", n_bars=1010, seed=4, n_trades_per_bar=50),
    }
    with tempfile.TemporaryDirectory() as td:
        for inst, cap in caps.items():
            p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
            p.write_text(json.dumps(cap))
        report = e70.run_eval70(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert len(report["per_underlying"]) == 2
    assert len(report["per_config"]) == 2  # 2 underlyings * 1 config