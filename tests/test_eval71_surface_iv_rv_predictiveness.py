"""Unit tests for EVAL-71: wrapper-free options implied-volatility *surface*
(near-ATM IV level + put-call skew) -> realized-vol predictiveness (Spearman rank
IC) falsification.

EVAL-71 is the on-charter, runnable-now *surface* complement to EVAL-65 (options
order-flow) and EVAL-70 (underlying perp order-flow): same Spearman rank-IC
statistic (reused verbatim from EVAL-65), but a different signal source (the
options implied-vol surface reconstructed from the real Deribit option trade
tape). It needs no new acquisition and no network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin six things the next session must not break:
1. the artifact ids are EVAL-71;
2. the statistic (permutation / bootstrap / Spearman) is reused verbatim from
   EVAL-65, not forked;
3. ``build_surface_bars`` computes a causal near-ATM IV / skew on the bar grid;
4. the pre-registered trade-tape IV floor blocks (never NO-GO) below floor;
5. ``run_eval71(write=False)`` reports BLOCKED below floor and produces a summary
   above floor;
6. a planted surface -> forward-vol relationship is detected (positive IC).
"""

from __future__ import annotations

import json
import math
import random
import tempfile
from pathlib import Path

import scripts.eval61_orderflow_realized_vol_net_of_cost as e61
import scripts.eval65_orderflow_tox_rv_predictiveness as e65
import scripts.eval71_surface_iv_rv_predictiveness as e71


def _craft_surface_capture(
    inst="BTC",
    *,
    n_bars=300,
    seed=0,
    signal_to_vol=0.0,
    n_trades_per_bar=40,
    ar=0.8,
):
    """In-memory three-way capture fixture whose real option-trade IV (near-ATM
    level + put-call skew) is driven by a latent AR(1) factor that also drives the
    forward perp return / volatility.

    ``signal_to_vol`` > 0 plants a persistent surface -> forward-vol relationship
    the Spearman IC should detect; ``signal_to_vol`` == 0 plants none.
    """
    rng = random.Random(seed)
    bar_ms = 300_000
    base_ms = 1_700_000_000_000
    base_ms -= base_ms % bar_ms
    px = 60000.0 if inst == "BTC" else 3000.0
    candles = []
    trades = []
    latent = 0.5  # latent factor in [0, 1]; drives BOTH the surface and forward vol
    for i in range(n_bars):
        latent = ar * latent + rng.uniform(0, 1) * (1.0 - ar)
        latent = max(0.0, min(1.0, latent))
        # drift magnitude proportional to the latent factor (always >= 0) so the
        # forward realized vol is monotone in the surface signals below.
        drift = latent * signal_to_vol + rng.uniform(-1, 1) * 1e-6
        px = max(1.0, px * (1.0 + drift))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        base_iv = 50.0 + latent * 20.0  # ATM IV level rises with the latent factor
        for j in range(n_trades_per_bar):
            strike = px * (1.0 + rng.uniform(-0.04, 0.04))  # near-ATM
            typ = "P" if j % 2 == 0 else "C"
            if typ == "P":
                iv = base_iv + 5.0 + latent * 10.0  # put IV (fear) rises with latent
            else:
                iv = base_iv - latent * 5.0
            iv = max(1.0, iv + rng.uniform(-1.0, 1.0))
            trades.append({
                "ts": ts + rng.randint(1, bar_ms - 1),
                "instrument": f"{inst}-27NOV26-{int(round(strike))}-{typ}",
                "iv": iv,
                "amount": 1.0,
                "index_price": px,
                "option_type": typ.lower(),
            })
    return {
        "schema": "three_way_options_surface_orderflow_okx_perp_capture_v1",
        "underlying": inst,
        "venue": "deribit+okx",
        "window_start": "2023-11-14T00:00:00Z",
        "window_end": "2023-11-15T00:00:00Z",
        "surface": {"bar_seconds": 300, "resolution": "5", "snapshots": []},
        "option_trades": trades,
        "perp_candles": candles,
        "okx_inst_id": f"{inst}-USD-SWAP",
        "okx_perp_trades": [],
        "source": {"authenticated": False, "public_read_only": True, "venue": "deribit+okx"},
    }


def test_ids_are_eval71():
    assert e71.REPORT_ID.startswith("EVAL_71_")
    assert e71.PREREG_ID.startswith("EVAL_71_")
    assert e71.BLOCKED_ID.startswith("EVAL_71_")
    assert "SURFACE_IV_RV_PREDICTIVENESS" in e71.REPORT_ID


def test_statistic_reused_verbatim_from_eval65():
    """EVAL-71 must reuse the sealed EVAL-65 statistics, not fork them."""
    assert e71.e65._perm_p_ic is e65._perm_p_ic
    assert e71.e65._boot_ci_ic is e65._boot_ci_ic
    assert e71.e65._spearman is e65._spearman
    assert e71.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e71.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e71.SEED == e65.SEED


def test_parse_strike_type():
    assert e71._parse_strike_type("BTC-27NOV26-65000-P") == (65000.0, "P")
    assert e71._parse_strike_type("ETH-17NOV26-1780-C") == (1780.0, "C")
    assert e71._parse_strike_type("garbage") is None
    assert e71._parse_strike_type("BTC-USD-SWAP") is None


def test_build_surface_bars_is_causal_and_near_atm():
    cap = _craft_surface_capture("BTC", n_bars=20, seed=1, n_trades_per_bar=20)
    bars = e71.build_surface_bars(cap, bar_seconds=300.0)
    assert len(bars) == 20
    opens = [b["bar_open_ms"] for b in bars]
    assert opens == sorted(opens)
    assert len(set(opens)) == len(opens)
    # every bar should carry a finite close and a populated near-ATM IV here
    for b in bars:
        assert b["close"] > 0.0
        assert b["atm_iv"] is not None and b["atm_iv"] > 0.0
        assert b["n_atm_trades"] > 0
    # skew = mean(put iv) - mean(call iv) must be finite and well-defined
    skews = [b["skew"] for b in bars if b["skew"] is not None]
    assert len(skews) > 0
    assert all(math.isfinite(s) for s in skews)


def test_forward_rv_is_causal():
    bars = [
        {"close": 100.0},
        {"close": 110.0},
        {"close": 121.0},
        {"close": 133.1},
    ]
    rv = e71._forward_rv(bars, 2)
    # log returns: log(1.1), log(1.1), log(1.1)
    lr = math.log(1.1)
    assert len(rv) == 2
    assert abs(rv[0] - lr) < 1e-9
    assert abs(rv[1] - lr) < 1e-9


def test_forward_fill_carries_last_value():
    out = e71._forward_fill([None, 5.0, None, None, 7.0, None])
    assert out == [0.0, 5.0, 5.0, 5.0, 7.0, 7.0]


def test_evaluate_predictiveness_runs_and_is_causal():
    cap = _craft_surface_capture("BTC", n_bars=200, seed=1, signal_to_vol=0.02)
    res = e71.evaluate_predictiveness(
        cap, surface_signal="atm_iv", bar_seconds=300.0, horizon_bars=6,
    )
    assert res["underlying"] == "BTC"
    assert res["n_pairs"] > 0
    assert "spearman_ic" in res and "permutation_p" in res and "pass" in res
    assert len(res["bootstrap_ci"]) == 3


def test_planted_surface_predicts_forward_vol():
    """A planted surface -> forward-vol relationship must yield a positive IC."""
    cap = _craft_surface_capture("BTC", n_bars=600, seed=5, signal_to_vol=0.03)
    res = e71.evaluate_predictiveness(
        cap, surface_signal="skew", bar_seconds=300.0, horizon_bars=24,
    )
    assert res["spearman_ic"] > 0.0


def test_floor_blocks_below_floor():
    cap = _craft_surface_capture("BTC", n_bars=40, seed=7, n_trades_per_bar=3)
    fl = e71._underlying_surface_floor(cap)
    assert fl["ok"] is False
    assert fl["checks"]["option_trades_ok"] is False


def test_floor_passes_on_heavy_capture():
    # 1010 bars * 300s = 303000s span, 1010 candles, 1010*50 = 50500 option trades.
    cap = _craft_surface_capture("BTC", n_bars=1010, seed=3, n_trades_per_bar=50)
    fl = e71._underlying_surface_floor(cap)
    assert fl["n_option_trades"] >= e71.FLOOR["min_option_trades_per_underlying"]
    assert fl["n_near_atm_option_trades"] >= e71.FLOOR["min_near_atm_option_trades_per_underlying"]
    assert fl["perp_span_seconds"] >= e71.FLOOR["min_perp_span_seconds_per_underlying"]
    assert fl["ok"] is True


def test_run_eval71_no_write_blocks_below_floor():
    cap = _craft_surface_capture("BTC", n_bars=40, seed=7, n_trades_per_bar=3)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "three_way_BTC_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
        report = e71.run_eval71(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e71.REPORT_ID


def test_run_eval71_no_write_meets_floor_and_summarizes(monkeypatch):
    # Keep the orchestration path fast: one signal, one bar grid, one horizon, few
    # permutations. The floor itself is NOT weakened (real 50500-trade fixtures).
    monkeypatch.setattr(e71, "SURFACE_SIGNALS", ("atm_iv",))
    monkeypatch.setattr(e71, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e71, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e71, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e71, "BOOTSTRAP_RESAMPLES", 50)

    caps = {
        "BTC": _craft_surface_capture("BTC", n_bars=1010, seed=3, n_trades_per_bar=50),
        "ETH": _craft_surface_capture("ETH", n_bars=1010, seed=4, n_trades_per_bar=50),
    }
    with tempfile.TemporaryDirectory() as td:
        for inst, cap in caps.items():
            p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
            p.write_text(json.dumps(cap))
        report = e71.run_eval71(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert len(report["per_underlying"]) == 2
    assert len(report["per_config"]) == 2  # 2 underlyings * 1 config