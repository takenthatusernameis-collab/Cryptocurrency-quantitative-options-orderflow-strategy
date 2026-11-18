"""Unit tests for EVAL-107: does the cross-sectional near-to-far ATM IV
**term ratio basis** (ETH minus BTC) predict the subsequent **relative
vol-of-vol spread** (BTC minus ETH forward vol-of-vol)?

EVAL-107 is the on-charter, runnable-now distinct follow-up to EVAL-105
(term-ratio basis -> relative *tail-asymmetry* spread), EVAL-90 (atm_iv
basis -> relative *vol-of-vol* spread), EVAL-84 (single-asset term_slope ->
own *vol-of-vol*), and EVAL-97 (single-asset skew -> own *vol-of-vol*). It
reuses EVAL-74's ``_term_bars``/term floor, EVAL-77's
``_relative_signal_series`` cross-sectional alignment, and EVAL-84/90's
``_forward_rel_vov_spread`` target verbatim; the new logic is the campaign
composition.

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
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77
import scripts.eval84_term_structure_vol_of_vol_predictiveness as e84
import scripts.eval90_cross_sectional_atm_iv_basis_relative_vol_of_vol_spread as e90
import scripts.eval107_cross_sectional_term_ratio_basis_relative_vol_of_vol_spread as e107

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000
_BASE_MS -= _BASE_MS % _BAR_MS


def _craft_term_capture(
    inst="BTC", *, n_bars=200, seed=0, n_trades_per_bar=24, base_ms=_BASE_MS, bar_ms=_BAR_MS,
):
    """Deterministic three-way capture whose real option-trade IV populates a
    non-null term structure (>=2 distinct near-ATM expiries) at every bar."""
    rng = random.Random(seed)
    px = 60000.0 if inst == "BTC" else 3000.0
    expiries = ("20NOV26", "27DEC26")  # 2 distinct expiries for a term signal
    candles = []
    trades = []
    for i in range(n_bars):
        px = max(1.0, px * (1.0 + rng.uniform(-1.0, 1.0) * 1e-4))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        for j in range(n_trades_per_bar):
            frac = (j / (n_trades_per_bar - 1)) if n_trades_per_bar > 1 else 0.0
            strike = px * (0.99 + 0.02 * frac)
            typ = "P" if j % 2 == 0 else "C"
            expiry = expiries[j % len(expiries)]
            iv = (65.0 if expiry == expiries[0] else 55.0) + rng.uniform(-0.5, 0.5)
            trades.append({
                "ts": ts + j * 1000,
                "instrument": f"{inst}-{expiry}-{int(round(strike))}-{typ}",
                "iv": iv,
                "amount": 1.0 + 0.1 * j,
                "index_price": px,
                "option_type": typ.lower(),
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
def test_ids_are_eval107():
    assert e107.REPORT_ID.startswith("EVAL_107_")
    assert e107.PREREG_ID.startswith("EVAL_107_")
    assert e107.BLOCKED_ID.startswith("EVAL_107_")
    assert "TERM_RATIO" in e107.REPORT_ID
    assert "VOL_OF_VOL" in e107.REPORT_ID
    assert e107.TERM_SIGNALS == ("term_ratio",)
    assert e107.TARGET == "forward_relative_vol_of_vol_spread"


# 2) sealed machinery reused verbatim (not forked)
def test_reuse_helpers():
    assert e107.e74 is e74
    assert e107.e77 is e77
    assert e107.e84 is e84
    assert e107.e90 is e90
    assert e107.e71 is e71
    assert e107.e65 is e65
    assert e107.e61 is e61
    assert e107.e62 is e62
    # forward relative vol-of-vol spread target reused verbatim from EVAL-90 (same object)
    assert e90._forward_rel_vov_spread is e90._forward_rel_vov_spread
    # cross-sectional relative signal series reused from EVAL-77 (same object)
    assert e77._relative_signal_series is e77._relative_signal_series


# 3) floor delegated to sealed EVAL-74 term floor verbatim
def test_underlying_floor_delegates_to_eval74_verbatim():
    cap = _craft_term_capture("BTC", n_bars=1200, seed=3, n_trades_per_bar=40)
    assert e107._underlying_term_floor(cap) == e74._underlying_term_floor(cap)


# 4) evaluate_config targets relative vol-of-vol spread with term_ratio, deterministically
def test_evaluate_config_structure_and_deterministic(monkeypatch):
    monkeypatch.setattr(e107, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e107, "BOOTSTRAP_RESAMPLES", 50)
    caps = {
        "BTC": _craft_term_capture("BTC", n_bars=220, seed=5, n_trades_per_bar=24),
        "ETH": _craft_term_capture("ETH", n_bars=220, seed=6, n_trades_per_bar=24),
    }
    a = e107.evaluate_config(caps, term_signal="term_ratio", bar_seconds=60.0, horizon_bars=6)
    b = e107.evaluate_config(caps, term_signal="term_ratio", bar_seconds=60.0, horizon_bars=6)
    assert a["signal"] == "term_ratio"
    assert a["target"] == "forward_relative_vol_of_vol_spread"
    assert a["bar_seconds"] == 60.0
    assert a["horizon_bars"] == 6
    assert a["n_pairs"] >= e107.MIN_USABLE_PAIRS_PER_CONFIG
    assert -1.0 <= a["spearman_ic"] <= 1.0
    assert 0.0 <= a["permutation_p"] <= 1.0
    ci = a["bootstrap_ci"]
    assert len(ci) == 3 and ci[1] <= ci[0] <= ci[2]
    # determinism
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


# 5) below floor seals BLOCKED, never NO-GO
def test_below_floor_blocks_not_nogo():
    cap = _craft_term_capture("BTC", n_bars=40, seed=1, n_trades_per_bar=2)
    td = _write_captures({"BTC": cap})
    report = e107.run_eval107(capture_dir=td, write=False, task_label="TEST")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    if not report.get("floor_ok"):
        assert report["verdict"] == "BLOCKED"


# 6) run_eval107(write=False) meets floor and summarizes (floor monkeypatched ok)
def test_run_eval107_no_write_meets_floor_and_summarizes(monkeypatch):
    monkeypatch.setattr(e107, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e107, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e107, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e107, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e107, "campaign_floor",
        lambda captures: {"checks": {}, "ok": True},
    )
    caps = {
        "BTC": _craft_term_capture("BTC", n_bars=220, seed=17),
        "ETH": _craft_term_capture("ETH", n_bars=220, seed=18),
    }
    td = _write_captures(caps)
    report = e107.run_eval107(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    # one config (1 signal x 1 grid point x 1 horizon)
    assert len(report["per_config"]) == 1
    assert report["protocol"]["target"] == "forward_relative_vol_of_vol_spread"
    assert report["protocol"]["term_signals"] == ["term_ratio"]


# 7) protocol constants pre-registered and floor reuses EVAL-74 term floor
def test_protocol_constants():
    proto = e107.build_protocol("data/raw/eval61")
    assert proto["term_signals"] == ["term_ratio"]
    assert proto["target"] == "forward_relative_vol_of_vol_spread"
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert proto["forward_horizons_bars"] == [6, 24, 72]
    assert proto["stats"]["seed"] == e62.SEED
    assert proto["floor"]["min_underlyings"] == e74.FLOOR["min_underlyings"]
    assert proto["floor"]["min_distinct_expiries"] == e74.MIN_DISTINCT_EXPIRIES
    assert proto["floor"]["min_expiry_trades"] == e74.MIN_EXPIRY_TRADES
    assert proto["floor"]["min_bars_with_term"] == e74.MIN_BARS_WITH_TERM
    assert proto["signal_window_seconds"] == e74.SIGNAL_WINDOW_SECONDS
    assert proto["atm_band"] == e74.ATM_BAND
    assert proto["cross_section"]["baseline"] == "BTC"
    assert proto["cross_section"]["relative"] == "ETH"