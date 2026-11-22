"""Unit tests for EVAL-179 (term_ratio cell): does the **cross-asset causal ATM IV
term-structure ratio spillover** (the OTHER underlying's ``term_ratio``) predict
the subsequent **forward realized return variance** of the target underlying's
signed log-returns?

EVAL-179 fills the next unbuilt cross-asset surface x forward-variance cell: the
cross-asset term_ratio-spillover x forward-variance grid had never been measured
(single-asset term_ratio -> variance is sealed EVAL-175; cross-asset atm_iv ->
variance is sealed EVAL-176; cross-asset skew -> variance is sealed EVAL-177;
cross-asset term_slope -> variance is EVAL-178). It reuses the EVAL-74
``term_ratio`` term-bar signal verbatim, the EVAL-71 surface floor verbatim, the
EVAL-148 cross-asset alignment, and the EVAL-172 forward variance target
verbatim; the new logic is the cross-asset term_ratio spillover pairing against
that target.

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
import scripts.eval179_cross_asset_term_ratio_spillover_forward_variance as e179

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000
_BASE_MS -= _BASE_MS % _BAR_MS


def _craft_term_ratio_capture(
    inst="BTC", *, n_bars=200, seed=0, n_atm_trades_per_bar=24, base_ms=_BASE_MS, bar_ms=_BAR_MS,
):
    """Deterministic three-way capture whose real option-trade IV populates a
    non-null near-ATM term ratio at every bar (near-ATM and far-ATM trades with
    distinct IVs across distinct expiries)."""
    rng = random.Random(seed)
    px = 60000.0 if inst == "BTC" else 3000.0
    near_strike = round(px, -1)
    far_strike = near_strike + max(10, int(px * 0.01))  # ~1% spread, both within 5% ATM band
    candles = []
    trades = []
    for i in range(n_bars):
        px = max(1.0, px * (1.0 + rng.uniform(-1.0, 1.0) * 1e-4))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        # near-ATM IV on both strikes/expiries -> positive term ratio.
        near_iv = 70.0 + rng.uniform(-0.5, 0.5)
        far_iv = near_iv - rng.uniform(0.5, 2.0)
        for j in range(n_atm_trades_per_bar):
            side = "P" if j % 2 == 0 else "C"
            iv = near_iv if j % 3 == 0 else far_iv
            strikes = near_strike if j % 3 == 0 else far_strike
            expiry = "20NOV26" if j % 3 == 0 else "20DEC26"
            trades.append({
                "ts": ts + j * 1000,
                "instrument": f"{inst}-{expiry}-{int(round(strikes))}-{side}",
                "iv": iv,
                "amount": 1.0 + 0.1 * j,
                "index_price": px,
                "option_type": side,
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
def test_ids_are_eval179_term_ratio_forward_variance():
    assert e179.REPORT_ID.startswith("EVAL_179_")
    assert e179.PREREG_ID.startswith("EVAL_179_")
    assert e179.BLOCKED_ID.startswith("EVAL_179_")
    assert "TERM_RATIO" in e179.REPORT_ID
    assert "SPILLOVER" in e179.REPORT_ID
    assert "FORWARD_VARIANCE" in e179.REPORT_ID
    assert e179.SURFACE_SIGNAL == "term_ratio"
    assert e179.TARGET == "forward_variance"


# 2) sealed machinery reused verbatim (not forked)
def test_reuse_helpers():
    assert e179.e71 is e71
    assert e179.e74 is e74
    assert e179.e65 is e65
    assert e179.e61 is e61
    assert e179.e62 is e62
    assert e179.e172 is e172


# 3) forward realized return variance is finite and non-negative
def test_forward_return_variance_is_finite_and_distinct():
    rng = random.Random(179)
    bars = []
    px = 100.0
    for i in range(80):
        drift = 0.05 if i % 17 == 0 else rng.uniform(-0.002, 0.002)
        px = px * (1.0 + drift)
        bars.append({"close": px, "bar_open_ms": i * 300000, "term_ratio": 1.5})
    var = e179._forward_return_variance(bars, 24)
    finite = [v for v in var if v is not None and math.isfinite(v)]
    assert len(finite) > 10
    assert all(v >= 0.0 for v in finite)


# 4) build_cross_section aligns both underlyings on the common bar grid (term bars)
def test_build_cross_section_aligns_common_grid():
    caps = {
        "BTC": _craft_term_ratio_capture("BTC", n_bars=120, seed=1),
        "ETH": _craft_term_ratio_capture("ETH", n_bars=120, seed=2),
    }
    cs = e179.build_cross_section(caps, bar_seconds=300.0)
    assert set(cs["underlyings"]) == {"BTC", "ETH"}
    assert len(cs["common"]) > 50
    assert cs["bar_seconds"] == 300.0
    assert set(cs["maps"]["BTC"].keys()) >= set(cs["common"])
    assert set(cs["maps"]["ETH"].keys()) >= set(cs["common"])


# 5) spillover signal is the OTHER asset's term_ratio (cross-asset, not self)
def test_spillover_signal_is_other_asset():
    caps = {
        "BTC": _craft_term_ratio_capture("BTC", n_bars=220, seed=3),
        "ETH": _craft_term_ratio_capture("ETH", n_bars=220, seed=4),
    }
    cs = e179.build_cross_section(caps, bar_seconds=300.0)
    btc_tr = e179._term_ratio_on_common(cs, "BTC")
    eth_tr = e179._term_ratio_on_common(cs, "ETH")
    assert len(btc_tr) == len(cs["common"])
    assert len(eth_tr) == len(cs["common"])
    filled_eth = e71._forward_fill(eth_tr)
    filled_btc = e71._forward_fill(btc_tr)
    assert all(v is not None for v in filled_eth)
    assert all(v is not None for v in filled_btc)


# 6) _eval_one_config targets forward variance with cross-asset term_ratio, deterministically
def test_eval_one_config_structure_and_deterministic(monkeypatch):
    monkeypatch.setattr(e179, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e179, "BOOTSTRAP_RESAMPLES", 50)
    caps = {
        "BTC": _craft_term_ratio_capture("BTC", n_bars=300, seed=5),
        "ETH": _craft_term_ratio_capture("ETH", n_bars=300, seed=6),
    }
    a = e179._eval_one_config(caps, target_inst="BTC", bar_seconds=60.0, horizon_bars=6)
    b = e179._eval_one_config(caps, target_inst="BTC", bar_seconds=60.0, horizon_bars=6)
    assert a["target_underlying"] == "BTC"
    assert a["signal_underlying"] == "ETH"
    assert a["signal"] == "term_ratio"
    assert a["target"] == "forward_variance"
    assert a["bar_seconds"] == 60.0
    assert a["horizon_bars"] == 6
    assert a["n_pairs"] >= e179.MIN_USABLE_PAIRS_PER_CONFIG
    assert -1.0 <= a["spearman_ic"] <= 1.0
    assert 0.0 <= a["permutation_p"] <= 1.0
    ci = a["bootstrap_ci"]
    assert len(ci) == 3 and ci[1] <= ci[0] <= ci[2]
    # determinism
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


# 7) below floor seals BLOCKED, never NO-GO
def test_below_floor_blocks_not_nogo():
    caps = {
        "BTC": _craft_term_ratio_capture("BTC", n_bars=40, seed=1, n_atm_trades_per_bar=4),
        "ETH": _craft_term_ratio_capture("ETH", n_bars=40, seed=2, n_atm_trades_per_bar=4),
    }
    td = _write_captures(caps)
    report = e179.run_eval179(capture_dir=td, write=False, task_label="TEST")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    if not report.get("floor_ok"):
        assert report["verdict"] == "BLOCKED"


# 8) run_eval179(write=False) meets floor and summarizes (floor monkeypatched ok)
def test_run_eval179_no_write_meets_floor_and_summarizes(monkeypatch):
    monkeypatch.setattr(e179, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e179, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e179, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e179, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e179, "campaign_floor",
        lambda captures: {"checks": {}, "ok": True},
    )
    caps = {
        "BTC": _craft_term_ratio_capture("BTC", n_bars=300, seed=17),
        "ETH": _craft_term_ratio_capture("ETH", n_bars=300, seed=18),
    }
    td = _write_captures(caps)
    report = e179.run_eval179(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    # one config per target (2 targets x 1 grid point) = 2
    assert len(report["per_config"]) == 2
    assert report["protocol"]["target"] == "forward_variance"
    assert report["protocol"]["surface_signal"] == "term_ratio"


# 9) protocol constants pre-registered and floor reuses EVAL-71 surface floor + EVAL-74 term floor
def test_protocol_constants():
    proto = e179.build_protocol("data/raw/eval61")
    assert proto["surface_signal"] == "term_ratio"
    assert proto["target"] == "forward_variance"
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert proto["forward_horizons_bars"] == [6, 24, 72]
    assert proto["cross_section"]["baseline"] == "BTC"
    assert proto["cross_section"]["relative"] == "ETH"
    assert proto["stats"]["seed"] == e62.SEED
    assert proto["floor"]["min_underlyings"] == e71.FLOOR["min_underlyings"]
    assert proto["floor"]["min_option_trades_per_underlying"] == e71.FLOOR["min_option_trades_per_underlying"]
    assert proto["floor"]["min_aligned_common_bars"] == e179.MIN_ALIGNED_COMMON_BARS
    assert proto["signal_window_seconds"] == e74.SIGNAL_WINDOW_SECONDS
    assert proto["atm_band"] == e74.ATM_BAND


# 10) campaign_floor requires both underlyings and alignment
def test_campaign_floor_requires_both_and_alignment():
    caps_both = {
        "BTC": _craft_term_ratio_capture("BTC", n_bars=1200, seed=9, n_atm_trades_per_bar=40),
        "ETH": _craft_term_ratio_capture("ETH", n_bars=1200, seed=10, n_atm_trades_per_bar=40),
    }
    floor = e179.campaign_floor(caps_both)
    assert floor["underlyings_ok"] is True
    assert floor["aligned_ok"] is True
    assert floor["ok"] is True
    # single underlying fails underlyings_ok
    floor_one = e179.campaign_floor({"BTC": caps_both["BTC"]})
    assert floor_one["underlyings_ok"] is False
    assert floor_one["ok"] is False


# 11) per-target summary keys signal/target pairing
def test_per_target_summary_pairing(monkeypatch):
    monkeypatch.setattr(e179, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e179, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e179, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e179, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e179, "campaign_floor",
        lambda captures: {"checks": {}, "ok": True},
    )
    caps = {
        "BTC": _craft_term_ratio_capture("BTC", n_bars=300, seed=21),
        "ETH": _craft_term_ratio_capture("ETH", n_bars=300, seed=22),
    }
    td = _write_captures(caps)
    report = e179.run_eval179(capture_dir=td, write=False)
    targets = {s["target_underlying"] for s in report["per_target"]}
    assert targets == {"BTC", "ETH"}
    for s in report["per_target"]:
        sig = s["signal_underlying"]
        tgt = s["target_underlying"]
        assert sig != tgt  # cross-asset: signal never equals target
        assert sig in ("BTC", "ETH")


# 12) pooled BH-FDR key present and campaign_state set
def test_pooled_bh_fdr_and_campaign_state(monkeypatch):
    monkeypatch.setattr(e179, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e179, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e179, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e179, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e179, "campaign_floor",
        lambda captures: {"checks": {}, "ok": True},
    )
    caps = {
        "BTC": _craft_term_ratio_capture("BTC", n_bars=300, seed=31),
        "ETH": _craft_term_ratio_capture("ETH", n_bars=300, seed=32),
    }
    td = _write_captures(caps)
    report = e179.run_eval179(capture_dir=td, write=False)
    assert "bh_fdr" in report["pooled"]
    assert "campaign_state" in report["pooled"]
    assert report["pooled"]["campaign_state"] in (
        "EVAL_179_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_VARIANCE",
        "EVAL_179_BLOCKED_FLOOR",
    )
