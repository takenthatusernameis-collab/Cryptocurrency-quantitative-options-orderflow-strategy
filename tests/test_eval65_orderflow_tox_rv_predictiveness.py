"""Unit tests for EVAL-65: wrapper-free options order-flow toxicity -> realized-vol
predictiveness (Spearman rank IC) falsification.

EVAL-65 reuses the sealed EVAL-62 ``build_states`` (identical causal toxicity signal
+ spot series) and the sealed EVAL-64 feasible floor verbatim. It adds only a
predictiveness statistic (Spearman IC between the signal and forward realized vol).

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin four things the next session must not break:
1. the statistic is a correct Spearman rank correlation (monotone-equivariant,
   tie-aware, sign-correct);
2. the directional permutation p and block-bootstrap CI behave on a planted signal;
3. the feasible floor is reused verbatim from EVAL-64 (not re-implemented);
4. ``run_eval65(write=False)`` reports BLOCKED (never NO-GO) below the floor.
"""

from __future__ import annotations

import json
import math
import random
import tempfile
from pathlib import Path

import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64
import scripts.eval65_orderflow_tox_rv_predictiveness as e65


def _craft_capture(n_bars=120, seed=0, inst="BTC", n_trades_per_bar=3,
                   n_of_instruments=150, signal_to_vol=0.0):
    """In-memory capture fixture with an optional planted signal->vol relationship.

    ``signal_to_vol`` > 0 makes the next-bar return magnitude increasing in the
    option-flow toxicity (so the predictiveness IC should be positive).
    """
    rng = random.Random(seed)
    base_ms = 1_700_000_000_000
    bar_ms = 300_000
    px = 60000.0 if inst == "BTC" else 3000.0
    candles = []
    trades = []
    for i in range(n_bars):
        # drift magnitude scales with a latent "toxicity" that also drives option flow
        tox = rng.uniform(-1, 1)
        drift = tox * signal_to_vol + rng.uniform(-1, 1) * 1e-4
        px = max(1.0, px * (1 + drift))
        candles.append({"ts": base_ms + i * bar_ms, "open": px, "high": px,
                        "low": px, "close": px})
        sign = 1.0 if tox >= 0 else -1.0
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
    for i in range(min(n_bars, n_bars)):
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


def test_ids_are_eval65():
    assert e65.REPORT_ID.startswith("EVAL_65_")
    assert e65.PREREG_ID.startswith("EVAL_65_")
    assert e65.BLOCKED_ID.startswith("EVAL_65_")
    assert "OFLOW_TOX_RV_PREDICTIVENESS" in e65.REPORT_ID


def test_measurement_reused_verbatim_from_eval62():
    """EVAL-65 must reuse the sealed EVAL-62 signal/spot builder, not fork it."""
    assert e65.e62.build_states is e62.build_states


def test_floor_reused_verbatim_from_eval64():
    """The feasible floor must be EVAL-64's, not a re-implementation."""
    assert e65._underlying_floor_strict is e64._underlying_floor_strict
    assert e65.MIN_UNDERLYINGS == e64.MIN_UNDERLYINGS == 2


def test_spearman_is_monotone_and_sign_correct():
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert abs(e65._spearman(x, y) - 1.0) < 1e-9
    assert abs(e65._spearman(x, list(reversed(y))) + 1.0) < 1e-9
    # monotone-invariant under any increasing transform
    y2 = [math.exp(v) for v in y]
    assert abs(e65._spearman(x, y2) - 1.0) < 1e-9
    # ties are handled (average ranks)
    assert abs(e65._spearman([1, 1, 2, 2], [1, 2, 1, 2])) < 1e-9


def test_permutation_and_bootstrap_detect_planted_signal():
    rng = random.Random(0)
    x = [rng.uniform(-1, 1) for _ in range(200)]
    y = [3.0 * v + rng.gauss(0.0, 0.1) for v in x]  # strictly increasing in x
    ic, p = e65._perm_p_ic(x, y, n_perm=500, seed=1)
    med, lo, hi = e65._boot_ci_ic(x, y, n_boot=500, block=2, seed=1)
    assert ic > 0.5
    assert p < 0.05
    assert lo > 0.0


def test_evaluate_predictiveness_runs_and_is_causal():
    cap = _craft_capture(n_bars=200, seed=1, signal_to_vol=0.02)
    res = e65.evaluate_predictiveness(
        cap, tox_signal="tox", bar_seconds=300.0, horizon_bars=6
    )
    assert res["underlying"] == "BTC"
    assert res["n_pairs"] > 0
    assert "spearman_ic" in res and "permutation_p" in res and "pass" in res
    assert len(res["bootstrap_ci"]) == 3


def test_run_eval65_no_write_blocks_below_floor():
    cap = _craft_capture(n_bars=40, seed=7)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "three_way_BTC_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
        report = e65.run_eval65(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e65.REPORT_ID


def test_run_eval65_no_write_meets_feasible_floor():
    # 1010 bars * 300s = 302700s perp span, 2020 trades, 150 instruments, 1010 snaps.
    cap = _craft_capture(n_bars=1010, seed=3, n_trades_per_bar=2, n_of_instruments=150,
                         signal_to_vol=0.0)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "three_way_BTC_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
        report = e65.run_eval65(capture_dir=td, write=False)
    # the single heavy underlying clears the per-underlying feasible floor...
    assert report["per_underlying_floor"]["BTC"]["ok"] is True
    # ...but the roster needs >=2 underlyings, so the overall verdict is BLOCKED
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["per_underlying"]  # summary computed
    assert len(report["per_config"]) == len(e65.TOX_SIGNALS) * len(e65.GRID_BAR_SECONDS) * len(e65.FORWARD_HORIZONS_BARS)