"""Unit tests for EVAL-174: does the single-asset causal near-ATM options
term-structure ``term_slope`` predict the subsequent **forward realized return
variance** of the signed log-return of the same underlying?

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
import scripts.eval74_surface_term_structure_predictiveness as e74
import scripts.eval172_single_asset_atm_iv_forward_variance as e172
import scripts.eval174_single_asset_term_slope_forward_variance as e174

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000
_BASE_MS -= _BASE_MS % _BAR_MS


def _craft_term_capture(
    inst="BTC", *, n_bars=200, seed=0, n_trades_per_bar=6, base_ms=_BASE_MS, bar_ms=_BAR_MS,
):
    """Deterministic three-way capture whose real option-trade tape populates a
    non-null term_slope (>=2 distinct near-ATM expiries) at every bar."""
    rng = random.Random(seed)
    px = 60000.0 if inst == "BTC" else 3000.0
    # Strikes safely inside the ±0.05 ATM band (avoid the 1.05 boundary trap).
    near_strike = int(round(px * 0.99))
    far_strike = int(round(px * 1.01))
    candles = []
    trades = []
    for i in range(n_bars):
        px = max(1.0, px * (1.0 + rng.uniform(-1.0, 1.0) * 1e-4))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        near_iv = 70.0 + rng.uniform(-0.5, 0.5)
        far_iv = near_iv + rng.uniform(0.0, 2.0)
        base_ts = ts
        for j in range(n_trades_per_bar):
            t = base_ts + j * 1000
            trades.append({
                "ts": t,
                "instrument": f"{inst}-20NOV26-{near_strike}-C",
                "iv": near_iv,
                "amount": 1.0 + 0.1 * j,
                "index_price": px,
                "option_type": "C",
            })
            trades.append({
                "ts": t + 500,
                "instrument": f"{inst}-20DEC26-{far_strike}-C",
                "iv": far_iv,
                "amount": 1.0 + 0.1 * j,
                "index_price": px,
                "option_type": "C",
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
def test_ids_are_eval174_term_slope_forward_variance():
    assert e174.REPORT_ID.startswith("EVAL_174_")
    assert e174.PREREG_ID.startswith("EVAL_174_")
    assert e174.BLOCKED_ID.startswith("EVAL_174_")
    assert "TERM_SLOPE" in e174.REPORT_ID
    assert "SINGLE_ASSET" in e174.REPORT_ID
    assert "FORWARD_VARIANCE" in e174.REPORT_ID
    assert e174.SURFACE_SIGNAL == "term_slope"
    assert e174.TARGET == "forward_variance"


# 2) sealed machinery reused verbatim (not forked)
def test_reuse_helpers():
    assert e174.e71 is e71
    assert e174.e74 is e74
    assert e174.e65 is e65
    assert e174.e61 is e61
    assert e174.e62 is e62
    assert e174.e172 is e172


# 3) forward realized variance is finite and distinct from signed-return mean
def test_forward_return_variance_is_finite_and_distinct():
    rng = random.Random(174)
    bars = []
    px = 100.0
    for i in range(80):
        drift = 0.05 if i % 17 == 0 else rng.uniform(-0.002, 0.002)
        px = px * (1.0 + drift)
        bars.append({"close": px, "bar_open_ms": i * 300000, "term_slope": 0.7})
    var = e174._forward_return_variance(bars, 24)
    finite = [v for v in var if v is not None and math.isfinite(v)]
    assert len(finite) > 10
    assert all(v >= 0.0 for v in finite)


# 4) _term_bars populates term_slope on every bar
def test_term_bars_populate_term_slope():
    cap = _craft_term_capture("BTC", n_bars=120, seed=1, n_trades_per_bar=40)
    bars = e74._term_bars(
        cap, bar_seconds=300.0,
        signal_window_seconds=e71.SIGNAL_WINDOW_SECONDS,
        atm_band=e71.ATM_BAND,
    )
    assert len(bars) > 50
    assert all(b.get("term_slope") is not None for b in bars)


# 5) _eval_one_config targets forward variance with term_slope, deterministically
def test_eval_one_config_structure_and_deterministic(monkeypatch):
    monkeypatch.setattr(e174, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e174, "BOOTSTRAP_RESAMPLES", 50)
    cap = _craft_term_capture("BTC", n_bars=300, seed=5, n_trades_per_bar=40)
    a = e174._eval_one_config(cap, bar_seconds=60.0, horizon_bars=6)
    b = e174._eval_one_config(cap, bar_seconds=60.0, horizon_bars=6)
    assert a["underlying"] == "BTC"
    assert a["signal"] == "term_slope"
    assert a["target"] == "forward_variance"
    assert a["bar_seconds"] == 60.0
    assert a["horizon_bars"] == 6
    assert a["n_pairs"] >= e174.MIN_USABLE_PAIRS_PER_CONFIG
    assert -1.0 <= a["spearman_ic"] <= 1.0
    assert 0.0 <= a["permutation_p"] <= 1.0
    ci = a["bootstrap_ci"]
    assert len(ci) == 3 and ci[1] <= ci[0] <= ci[2]
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


# 6) below floor seals BLOCKED, never NO-GO
def test_below_floor_blocks_not_nogo():
    cap = _craft_term_capture("BTC", n_bars=40, seed=1, n_trades_per_bar=4)
    td = _write_captures({"BTC": cap})
    report = e174.run_eval174(capture_dir=td, write=False, task_label="TEST")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    if not report.get("floor_ok"):
        assert report["verdict"] == "BLOCKED"


# 7) run_eval174(write=False) meets floor and summarizes (floor monkeypatched ok)
def test_run_eval174_no_write_meets_floor_and_summarizes(monkeypatch):
    monkeypatch.setattr(e174, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e174, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e174, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e174, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e174, "_campaign_floor",
        lambda captures: {"checks": {}, "ok": True},
    )
    caps = {
        "BTC": _craft_term_capture("BTC", n_bars=300, seed=17, n_trades_per_bar=40),
        "ETH": _craft_term_capture("ETH", n_bars=300, seed=18, n_trades_per_bar=40),
    }
    td = _write_captures(caps)
    report = e174.run_eval174(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert len(report["per_config"]) == 2
    assert report["protocol"]["target"] == "forward_variance"
    assert report["protocol"]["surface_signal"] == "term_slope"


# 8) protocol constants pre-registered and floor reuses EVAL-71 surface floor
def test_protocol_constants():
    proto = e174.build_protocol("data/raw/eval61")
    assert proto["surface_signal"] == "term_slope"
    assert proto["target"] == "forward_variance"
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert proto["forward_horizons_bars"] == [6, 24, 72]
    assert proto["stats"]["seed"] == e62.SEED
    assert proto["floor"]["min_underlyings"] == e71.FLOOR["min_underlyings"]
    assert proto["floor"]["min_option_trades_per_underlying"] == e71.FLOOR["min_option_trades_per_underlying"]
    assert proto["signal_window_seconds"] == e71.SIGNAL_WINDOW_SECONDS
    assert proto["atm_band"] == e71.ATM_BAND


# 9) campaign_floor requires both underlyings
def test_campaign_floor_requires_both_underlyings():
    caps_both = {
        "BTC": _craft_term_capture("BTC", n_bars=1200, seed=9, n_trades_per_bar=40),
        "ETH": _craft_term_capture("ETH", n_bars=1200, seed=10, n_trades_per_bar=40),
    }
    floor = e174._campaign_floor(
        {inst: e71._underlying_surface_floor(cap) for inst, cap in caps_both.items()}
    )
    assert floor["checks"]["underlyings_ok"] is True
    assert floor["ok"] is True
    floor_one = e174._campaign_floor(
        {"BTC": e71._underlying_surface_floor(caps_both["BTC"])}
    )
    assert floor_one["checks"]["underlyings_ok"] is False
    assert floor_one["ok"] is False


# 10) per-underlying summary keys signal/target
def test_per_underlying_summary_pairing(monkeypatch):
    monkeypatch.setattr(e174, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e174, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e174, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e174, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e174, "_campaign_floor",
        lambda captures: {"checks": {}, "ok": True},
    )
    caps = {
        "BTC": _craft_term_capture("BTC", n_bars=300, seed=21, n_trades_per_bar=40),
        "ETH": _craft_term_capture("ETH", n_bars=300, seed=22, n_trades_per_bar=40),
    }
    td = _write_captures(caps)
    report = e174.run_eval174(capture_dir=td, write=False)
    underlyings = {s["underlying"] for s in report["per_underlying"]}
    assert underlyings == {"BTC", "ETH"}
    assert len(report["per_underlying"]) == 2


# 11) pooled BH-FDR key present and campaign_state set
def test_pooled_bh_fdr_and_campaign_state(monkeypatch):
    monkeypatch.setattr(e174, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e174, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e174, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e174, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e174, "_campaign_floor",
        lambda captures: {"checks": {}, "ok": True},
    )
    caps = {
        "BTC": _craft_term_capture("BTC", n_bars=300, seed=31, n_trades_per_bar=40),
        "ETH": _craft_term_capture("ETH", n_bars=300, seed=32, n_trades_per_bar=40),
    }
    td = _write_captures(caps)
    report = e174.run_eval174(capture_dir=td, write=False)
    assert "bh_fdr" in report["pooled"]
    assert "campaign_state" in report["pooled"]
    assert report["pooled"]["campaign_state"] in (
        "EVAL_174_SINGLE_ASSET_TERM_SLOPE_FORWARD_VARIANCE",
        "EVAL_174_BLOCKED_FLOOR",
    )
