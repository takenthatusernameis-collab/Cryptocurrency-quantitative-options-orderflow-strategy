"""Unit tests for EVAL-74: does the options implied-volatility **term structure**
(near-dated minus far-dated near-ATM IV slope) predict forward realized vol?

EVAL-74 is the on-charter, runnable-now *distinct-surface-signal* check that
follows EVAL-71 (GO: surface level/skew predicts forward RV), EVAL-72 (NO-GO:
that signal does not monetize net-of-cost) and EVAL-73 (GO: EVAL-71 is temporally
stable). It reuses EVAL-71's bar grid / spot / forward-rv machinery and EVAL-65's
Spearman rank-IC statistics verbatim; the only new logic is the cross-expiry
term-structure aggregation. It needs no new acquisition and no network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin seven things the next session must not break:
1. the artifact ids are EVAL-74;
2. the statistic (Spearman rank IC) and the EVAL-71 surface machinery are reused
   verbatim, not forked;
3. the term-structure bar grid / spot series are exactly EVAL-71's;
4. ``term_slope = IV(near) - IV(far)`` and ``term_ratio = IV(near)/IV(far) - 1``
   are computed over near-ATM trades grouped by expiry, with sparse expiries
   (< MIN_EXPIRY_TRADES) excluded;
5. a planted, persistent positive term-slope -> forward-vol relationship yields a
   positive passing Spearman IC;
6. the composed floor blocks (never NO-GO) below floor;
7. ``run_eval74(write=False)`` reports BLOCKED below floor and summarizes above it.
"""

from __future__ import annotations

import json
import random
import tempfile
from pathlib import Path

import scripts.eval61_orderflow_realized_vol_net_of_cost as e61
import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval65_orderflow_tox_rv_predictiveness as e65
import scripts.eval71_surface_iv_rv_predictiveness as e71
import scripts.eval74_surface_term_structure_predictiveness as e74

DEFAULT_EXPIRIES = ("18NOV26", "20NOV26", "27NOV26", "4DEC26")


def _craft_term_capture(
    inst="BTC",
    *,
    n_bars=300,
    seed=0,
    signal_to_vol=0.0,
    n_trades_per_bar=40,
    ar=0.8,
    expiries=DEFAULT_EXPIRIES,
):
    """In-memory three-way capture whose real option-trade IV term structure
    (near-minus-far near-ATM IV slope) is driven by a latent AR(1) factor that also
    drives forward perp volatility. ``signal_to_vol`` > 0 plants a positive
    term-slope -> forward-vol relationship; ``== 0`` plants none."""
    rng = random.Random(seed)
    bar_ms = 300_000
    base_ms = 1_700_000_000_000
    base_ms -= base_ms % bar_ms
    px = 60000.0 if inst == "BTC" else 3000.0
    n_exp = len(expiries)
    candles = []
    trades = []
    latent = 0.5
    for i in range(n_bars):
        latent = ar * latent + rng.uniform(0, 1) * (1.0 - ar)
        latent = max(0.0, min(1.0, latent))
        drift = latent * signal_to_vol + rng.uniform(-1, 1) * 1e-6
        px = max(1.0, px * (1.0 + drift))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        for j in range(n_trades_per_bar):
            e_idx = j % n_exp
            frac = (e_idx / (n_exp - 1)) if n_exp > 1 else 0.0
            # near expiry (frac 0): high base IV + high latent sensitivity;
            # far expiry (frac 1): low base IV, low sensitivity.
            base_iv = 60.0 - frac * 20.0
            sens = 20.0 * (1.0 - frac)
            strike = px * (1.0 + rng.uniform(-0.04, 0.04))
            typ = "P" if j % 2 == 0 else "C"
            iv = base_iv + latent * sens + rng.uniform(-0.5, 0.5)
            iv = max(1.0, iv)
            trades.append({
                "ts": ts + rng.randint(1, bar_ms - 1),
                "instrument": f"{inst}-{expiries[e_idx]}-{int(round(strike))}-{typ}",
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


def test_ids_are_eval74():
    assert e74.REPORT_ID.startswith("EVAL_74_")
    assert e74.PREREG_ID.startswith("EVAL_74_")
    assert e74.BLOCKED_ID.startswith("EVAL_74_")
    assert "TERM_STRUCTURE" in e74.REPORT_ID


def test_surface_machinery_reused_verbatim():
    """EVAL-74 must reuse the sealed EVAL-61/62/65 statistics + EVAL-71 surface
    machinery, not fork them."""
    assert e74.e71 is e71
    assert e74.e65 is e65
    assert e74.e62 is e62
    assert e74.e61 is e61
    # EVAL-71 bar grid / spot series reused verbatim
    assert e74.e71.build_surface_bars is e71.build_surface_bars
    # forward rv wrapper delegates to EVAL-71
    bars = [{"close": 100.0}, {"close": 101.0}, {"close": 102.0}, {"close": 103.0}]
    assert e74._forward_rv(bars, 2) == e71._forward_rv(bars, 2)
    # constants match the sealed modules
    assert e74.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e74.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e74.SEED == e62.SEED
    assert e74.ZWINDOW == e62.ZWINDOW
    assert e74.ATM_BAND == e71.ATM_BAND


def test_term_bars_match_eval71_grid_and_close():
    """The term-structure bars must sit on EVAL-71's exact bar grid and spot
    series (only the term fields are added)."""
    cap = _craft_term_capture("BTC", n_bars=80, seed=1, n_trades_per_bar=30)
    base = e71.build_surface_bars(cap, bar_seconds=300.0)
    term = e74._term_bars(cap, bar_seconds=300.0)
    assert len(base) == len(term)
    for b, t in zip(base, term):
        assert b["bar_open_ms"] == t["bar_open_ms"]
        assert abs(float(b["close"]) - float(t["close"])) < 1e-12


def test_term_slope_definition_on_controlled_capture():
    """With constant spot and fixed per-expiry IV, term_slope = IV(near) - IV(far)
    and term_ratio = IV(near)/IV(far) - 1 exactly."""
    bar_ms = 300_000
    base_ms = 1_700_000_000_000
    base_ms -= base_ms % bar_ms
    px = 60000.0
    expiries = ("18NOV26", "27NOV26", "4DEC26")
    iv_by_exp = {"18NOV26": 60.0, "27NOV26": 50.0, "4DEC26": 40.0}
    candles = []
    trades = []
    for i in range(12):
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        for e in expiries:
            for k in range(10):
                typ = "P" if k % 2 == 0 else "C"
                trades.append({
                    "ts": ts + 1000 + k * 100,
                    "instrument": f"BTC-{e}-{int(px)}-{typ}",
                    "iv": iv_by_exp[e],
                    "amount": 1.0,
                    "index_price": px,
                    "option_type": typ.lower(),
                })
    cap = {
        "schema": "three_way_options_surface_orderflow_okx_perp_capture_v1",
        "underlying": "BTC",
        "option_trades": trades,
        "perp_candles": candles,
    }
    term = e74._term_bars(cap, bar_seconds=300.0)
    assert term
    for b in term:
        assert b["term_slope"] is not None
        assert abs(b["term_slope"] - (60.0 - 40.0)) < 1e-9
        assert abs(b["term_ratio"] - (60.0 / 40.0 - 1.0)) < 1e-9
        # near = earliest, far = latest present
        assert b["n_term_expiries"] == len(expiries)


def test_min_expiry_trades_excludes_sparse_expiry():
    """An expiry bucket with < MIN_EXPIRY_TRADES near-ATM trades in the window is
    excluded; with only one dense expiry, no term slope is produced."""
    bar_ms = 300_000
    base_ms = 1_700_000_000_000
    base_ms -= base_ms % bar_ms
    px = 60000.0
    candles = []
    trades = []
    for i in range(20):
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        # dense near expiry: 10 trades/bar
        for k in range(10):
            typ = "P" if k % 2 == 0 else "C"
            trades.append({
                "ts": ts + 1000 + k * 100,
                "instrument": f"BTC-18NOV26-{int(px)}-{typ}",
                "iv": 60.0, "amount": 1.0, "index_price": px,
                "option_type": typ.lower(),
            })
        # sparse far expiry: 1 trade/bar (< MIN_EXPIRY_TRADES over a 3-bar window)
        trades.append({
            "ts": ts + 500,
            "instrument": f"BTC-4DEC26-{int(px)}-P",
            "iv": 40.0, "amount": 1.0, "index_price": px, "option_type": "p",
        })
    cap = {
        "schema": "three_way_options_surface_orderflow_okx_perp_capture_v1",
        "underlying": "BTC",
        "option_trades": trades,
        "perp_candles": candles,
    }
    term = e74._term_bars(cap, bar_seconds=300.0)
    assert term
    for b in term:
        # only the dense near expiry survives -> fewer than 2 expiries -> no slope
        assert b["n_term_expiries"] < 2
        assert b["term_slope"] is None
        assert b["term_ratio"] is None


def test_term_slope_positive_on_planted_relationship(monkeypatch):
    """A planted, persistent positive term-slope -> forward-vol relationship yields
    a positive, passing Spearman IC."""
    monkeypatch.setattr(e74, "PERMUTATION_PERMS", 100)
    monkeypatch.setattr(e74, "BOOTSTRAP_RESAMPLES", 100)
    cap = _craft_term_capture("BTC", n_bars=1010, seed=5, signal_to_vol=0.02,
                              n_trades_per_bar=50)
    res = e74.evaluate_term_predictiveness(
        cap, term_signal="term_slope", bar_seconds=300.0, horizon_bars=6,
    )
    assert res["n_pairs"] >= 20
    assert res["spearman_ic"] > 0.0
    assert res["pass"] is True


def test_evaluate_term_insufficient_bars():
    cap = _craft_term_capture("BTC", n_bars=8, seed=1, n_trades_per_bar=5)
    res = e74.evaluate_term_predictiveness(
        cap, term_signal="term_slope", bar_seconds=300.0, horizon_bars=6,
    )
    assert res["pass"] is False
    assert res.get("error") == "insufficient surface bars"
    assert res["n_pairs"] == 0


def test_floor_blocks_below_floor():
    cap = _craft_term_capture("BTC", n_bars=40, seed=7, n_trades_per_bar=3,
                              expiries=("18NOV26",))
    fl = e74._underlying_term_floor(cap)
    assert fl["ok"] is False
    assert fl["checks"]["distinct_expiries_ok"] is False


def test_floor_passes_on_heavy_capture():
    cap = _craft_term_capture("BTC", n_bars=1010, seed=3, signal_to_vol=0.02,
                              n_trades_per_bar=50)
    fl = e74._underlying_term_floor(cap)
    assert fl["eval71_floor_ok"] is True
    assert fl["term_adequacy"]["checks"]["distinct_expiries_ok"] is True
    assert fl["term_adequacy"]["checks"]["bars_with_term_ok"] is True
    assert fl["ok"] is True


def test_run_eval74_no_write_blocks_below_floor():
    cap = _craft_term_capture("BTC", n_bars=40, seed=7, n_trades_per_bar=3,
                              expiries=("18NOV26",))
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "three_way_BTC_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
        report = e74.run_eval74(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e74.REPORT_ID


def test_run_eval74_no_write_meets_floor_and_summarizes(monkeypatch):
    """Orchestration above the floor: one signal, one bar grid, one horizon, few
    permutations (the floor is forced green here to keep the test fast; the real
    floor is exercised on the real captures by the driver)."""
    monkeypatch.setattr(e74, "TERM_SIGNALS", ("term_slope",))
    monkeypatch.setattr(e74, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e74, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e74, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e74, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e74, "_underlying_term_floor",
        lambda cap: {"underlying": cap.get("underlying", "?"), "ok": True,
                     "checks": {}},
    )
    caps = {
        "BTC": _craft_term_capture("BTC", n_bars=1010, seed=3, signal_to_vol=0.02,
                                   n_trades_per_bar=50),
        "ETH": _craft_term_capture("ETH", n_bars=1010, seed=4, signal_to_vol=0.02,
                                   n_trades_per_bar=50),
    }
    with tempfile.TemporaryDirectory() as td:
        for inst, cap in caps.items():
            p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
            p.write_text(json.dumps(cap))
        report = e74.run_eval74(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert len(report["per_underlying"]) == 2
    assert len(report["per_config"]) == 2  # 2 underlyings * 1 config


def test_protocol_and_floor_constants():
    p = e74.build_protocol("data/raw/eval61")
    assert p["floor"]["min_underlyings"] == 2
    assert set(p["term_signals"]) == {"term_slope", "term_ratio"}
    assert p["bar_seconds_grid"] == [60.0, 300.0]
    assert p["forward_horizons_bars"] == [6, 24, 72]
    assert "EVAL-71" in p["extends"]
    assert p["floor"]["min_distinct_expiries"] == e74.MIN_DISTINCT_EXPIRIES
    assert p["floor"]["min_expiry_trades"] == e74.MIN_EXPIRY_TRADES
    assert "term structure" in p["title"].lower()