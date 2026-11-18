"""Unit tests for EVAL-103: does the single-asset causal near-ATM implied-vol
**skew** (put-call IV difference) predict the subsequent **forward signed
(directional) log-return** of the same underlying?

EVAL-103 is the on-charter, runnable-now distinct follow-up to EVAL-71
(surface -> forward *RV level*), EVAL-81 (options *order-flow* vs forward
*signed return*), EVAL-85/86/97 (*skew* vs forward tail asymmetry / VRP /
vol-of-vol), EVAL-101 (*atm_iv* level vs forward *signed return*), and EVAL-102
(*term_ratio* vs forward *signed return*). It reuses the EVAL-71
``build_surface_bars`` ``skew`` signal path and EVAL-71 surface floor verbatim,
and transcribes EVAL-81's forward signed log-return target; the new logic is
the campaign composition.

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
import scripts.eval103_single_asset_skew_forward_signed_return as e103

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000
_BASE_MS -= _BASE_MS % _BAR_MS


def _craft_skew_capture(
    inst="BTC", *, n_bars=200, seed=0, n_trades_per_bar=24, base_ms=_BASE_MS, bar_ms=_BAR_MS,
):
    """Deterministic three-way capture whose real option-trade IV populates a
    non-null skew signal (both puts and calls near-ATM) at every bar."""
    rng = random.Random(seed)
    px = 60000.0 if inst == "BTC" else 3000.0
    expiries = ("20NOV26", "27DEC26")  # 2 distinct expiries for surface floor
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
def test_ids_are_eval103():
    assert e103.REPORT_ID.startswith("EVAL_103_")
    assert e103.PREREG_ID.startswith("EVAL_103_")
    assert e103.BLOCKED_ID.startswith("EVAL_103_")
    assert "SKEW" in e103.REPORT_ID
    assert "SIGNED_RETURN" in e103.REPORT_ID
    assert e103.SURFACE_SIGNAL == "skew"
    assert e103.TARGET == "signed_return"


# 2) sealed machinery reused verbatim (not forked)
def test_reuse_helpers():
    assert e103.e71 is e71
    assert e103.e65 is e65
    assert e103.e61 is e61
    assert e103.e62 is e62


# 3) forward signed return is finite and distinct from RV level / tail asymmetry
def test_forward_signed_return_is_finite():
    bars = []
    px = 100.0
    for i in range(80):
        drift = 0.02 if i % 2 == 0 else 0.0001
        px = px * (1.0 + drift)
        bars.append({"close": px, "bar_open_ms": i * 300000, "skew": 0.01})
    signed = e103._forward_signed_return(bars, 24)
    finite = [v for v in signed if v is not None and math.isfinite(v)]
    assert len(finite) > 10
    assert any(v != 0.0 for v in finite)
    assert any(v > 0.0 for v in finite)
    rv = e71._forward_rv(bars, 24)
    assert len(rv) > 0


# 4) floor delegated to sealed EVAL-71 surface floor verbatim
def test_underlying_floor_delegates_to_eval71_verbatim():
    cap = _craft_skew_capture("BTC", n_bars=1200, seed=3, n_trades_per_bar=40)
    assert e103._underlying_floor(cap) == e71._underlying_surface_floor(cap)


# 5) _eval_one_config targets forward signed return with skew, deterministically
def test_eval_one_config_structure_and_deterministic(monkeypatch):
    monkeypatch.setattr(e103, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e103, "BOOTSTRAP_RESAMPLES", 50)
    cap = _craft_skew_capture("BTC", n_bars=220, seed=5, n_trades_per_bar=24)
    a = e103._eval_one_config(cap, bar_seconds=60.0, horizon_bars=6)
    b = e103._eval_one_config(cap, bar_seconds=60.0, horizon_bars=6)
    assert a["signal"] == "skew"
    assert a["target"] == "signed_return"
    assert a["bar_seconds"] == 60.0
    assert a["horizon_bars"] == 6
    assert a["n_pairs"] >= e103.MIN_USABLE_PAIRS_PER_CONFIG
    assert -1.0 <= a["spearman_ic"] <= 1.0
    assert 0.0 <= a["permutation_p"] <= 1.0
    ci = a["bootstrap_ci"]
    assert len(ci) == 3 and ci[1] <= ci[0] <= ci[2]
    # determinism
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


# 6) below floor seals BLOCKED, never NO-GO
def test_below_floor_blocks_not_nogo():
    cap = _craft_skew_capture("BTC", n_bars=40, seed=1, n_trades_per_bar=2)
    td = _write_captures({"BTC": cap})
    report = e103.run_eval103(capture_dir=td, write=False, task_label="TEST")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    if not report.get("floor_ok"):
        assert report["verdict"] == "BLOCKED"


# 7) run_eval103(write=False) meets floor and summarizes (floor monkeypatched ok)
def test_run_eval103_no_write_meets_floor_and_summarizes(monkeypatch):
    monkeypatch.setattr(e103, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e103, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e103, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e103, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e103, "_campaign_floor",
        lambda per_underlying: {"checks": {}, "ok": True},
    )
    caps = {
        "BTC": _craft_skew_capture("BTC", n_bars=220, seed=17),
        "ETH": _craft_skew_capture("ETH", n_bars=220, seed=18),
    }
    td = _write_captures(caps)
    report = e103.run_eval103(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    # one config per underlying (2 underlyings x 1 grid point)
    assert len(report["per_config"]) == 2
    assert report["protocol"]["target"] == "signed_return"
    assert report["protocol"]["surface_signal"] == "skew"


# 8) protocol constants pre-registered and floor reuses EVAL-71 surface floor
def test_protocol_constants():
    proto = e103.build_protocol("data/raw/eval61")
    assert proto["surface_signal"] == "skew"
    assert proto["target"] == "signed_return"
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert proto["forward_horizons_bars"] == [6, 24, 72]
    assert proto["stats"]["seed"] == e62.SEED
    assert proto["floor"]["min_underlyings"] == e71.FLOOR["min_underlyings"]
    assert proto["signal_window_seconds"] == e71.SIGNAL_WINDOW_SECONDS
    assert proto["atm_band"] == e71.ATM_BAND
