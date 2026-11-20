"""Unit tests for EVAL-140: does an **equal-weight z-score composite** of the two
strongest surviving cross-asset options spillover GOs — the OTHER underlying's
near-ATM ``atm_iv`` level (EVAL-114 leg) and its near-minus-far ATM IV
``term_slope`` (EVAL-122 leg) — predict the target underlying's subsequent
**forward realized return skewness** better than either leg alone?

EVAL-140 is the pre-registered successor to EVAL-139. It reuses the EVAL-71
``atm_iv`` surface bar, the EVAL-74 ``term_slope`` reconstruction, the EVAL-71
surface floor verbatim, the cross-asset alignment, and the
EVAL-109/112/113/116 forward realized-return-skewness target verbatim; the new
logic is the equal-weight composite of the two surviving spillover signals and
the "beats each leg's best IC" GO bar.

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
import scripts.eval140_composite_atm_iv_term_slope_spillover_forward_return_skewness as e140

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000
_BASE_MS -= _BASE_MS % _BAR_MS


def _craft_surface_capture(
    inst="BTC", *, n_bars=200, seed=0, n_trades_per_bar=24, base_ms=_BASE_MS, bar_ms=_BAR_MS,
):
    """Deterministic three-way capture whose real option-trade IV populates a
    non-null near-ATM ``atm_iv`` AND a non-null near-minus-far ``term_slope``
    (>=2 near-ATM expiries, >=5 near-ATM trades each) at every bar."""
    rng = random.Random(seed)
    px = 60000.0 if inst == "BTC" else 3000.0
    near_exp = "20NOV26"
    far_exp = "20DEC26"
    candles = []
    trades = []
    for i in range(n_bars):
        px = max(1.0, px * (1.0 + rng.uniform(-1.0, 1.0) * 1e-4))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        # near expiry IV consistently above far expiry IV -> positive term_slope.
        near_iv = 70.0 + rng.uniform(-0.5, 0.5)
        far_iv = 60.0 + rng.uniform(-0.5, 0.5)
        for j in range(n_trades_per_bar // 2):
            frac = (j / (n_trades_per_bar // 2 - 1)) if n_trades_per_bar // 2 > 1 else 0.0
            strike = px * (0.99 + 0.02 * frac)
            trades.append({
                "ts": ts + j * 1000,
                "instrument": f"{inst}-{near_exp}-{int(round(strike))}-P",
                "iv": near_iv,
                "amount": 1.0 + 0.1 * j,
                "index_price": px,
                "option_type": "put",
            })
            trades.append({
                "ts": ts + j * 1000,
                "instrument": f"{inst}-{far_exp}-{int(round(strike))}-C",
                "iv": far_iv,
                "amount": 1.0 + 0.1 * j,
                "index_price": px,
                "option_type": "call",
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


# 1) artifact ids + composite identity
def test_ids_are_eval140():
    assert e140.REPORT_ID.startswith("EVAL_140_")
    assert e140.PREREG_ID.startswith("EVAL_140_")
    assert e140.BLOCKED_ID.startswith("EVAL_140_")
    assert "COMPOSITE" in e140.REPORT_ID
    assert "ATM_IV" in e140.REPORT_ID
    assert "TERM_SLOPE" in e140.REPORT_ID
    assert "SPILLOVER" in e140.REPORT_ID
    assert "FORWARD_RETURN_SKEWNESS" in e140.REPORT_ID
    assert e140.SURFACE_SIGNALS == ("atm_iv", "term_slope")
    assert e140.COMPOSITE_SIGNAL == "composite_atm_iv_term_slope"
    assert e140.TARGET == "realized_return_skewness"


# 2) sealed machinery reused verbatim (not forked)
def test_reuse_helpers():
    assert e140.e71 is e71
    assert e140.e74 is e74
    assert e140.e65 is e65
    assert e140.e61 is e61
    assert e140.e62 is e62


# 3) forward realized return skewness is finite and distinct from RV level
def test_forward_return_skewness_is_finite():
    rng = random.Random(140)
    bars = []
    px = 100.0
    for i in range(80):
        drift = 0.03 if i % 17 == 0 else rng.uniform(-0.002, 0.002)
        px = px * (1.0 + drift)
        bars.append({"close": px})
    skew = e140._forward_return_skewness(bars, 24)
    finite = [v for v in skew if v is not None and math.isfinite(v)]
    assert len(finite) > 10
    assert any(v != 0.0 for v in finite)
    assert all(abs(v) < 100.0 for v in finite)
    assert len(e71._forward_rv(bars, 24)) > 0


# 4) build_cross_section aligns both underlyings on the common bar grid, carrying both legs
def test_build_cross_section_aligns_common_grid_and_both_legs():
    caps = {
        "BTC": _craft_surface_capture("BTC", n_bars=120, seed=1),
        "ETH": _craft_surface_capture("ETH", n_bars=120, seed=2),
    }
    cs = e140.build_cross_section(caps, bar_seconds=300.0)
    assert set(cs["underlyings"]) == {"BTC", "ETH"}
    assert len(cs["common"]) > 50
    assert cs["bar_seconds"] == 300.0
    for inst in ("BTC", "ETH"):
        assert set(cs["maps"][inst].keys()) >= set(cs["common"])
        assert set(cs["term_maps"][inst].keys()) >= set(cs["common"])
        assert len(e140._signal_on_common(cs, inst, "atm_iv")) == len(cs["common"])
        assert len(e140._signal_on_common(cs, inst, "term_slope")) == len(cs["common"])


# 5) both legs are populated causally after forward-fill
def test_both_legs_populated_after_forward_fill():
    caps = {
        "BTC": _craft_surface_capture("BTC", n_bars=220, seed=3),
        "ETH": _craft_surface_capture("ETH", n_bars=220, seed=4),
    }
    cs = e140.build_cross_section(caps, bar_seconds=300.0)
    for inst in ("BTC", "ETH"):
        for leg in e140.SURFACE_SIGNALS:
            filled = e71._forward_fill(e140._signal_on_common(cs, inst, leg))
            assert all(v is not None for v in filled)
            assert any(v != 0.0 for v in filled)


# 6) _zscore_pair equals the sealed forward-fill -> expanding-zscore chain per leg
def test_zscore_pair_matches_sealed_chain():
    caps = {
        "BTC": _craft_surface_capture("BTC", n_bars=220, seed=5),
        "ETH": _craft_surface_capture("ETH", n_bars=220, seed=6),
    }
    cs = e140.build_cross_section(caps, bar_seconds=300.0)
    z_atm, z_term = e140._zscore_pair(cs, "ETH")
    exp_atm = e61.expanding_zscore(
        e71._forward_fill(e140._signal_on_common(cs, "ETH", "atm_iv")), e62.ZWINDOW
    )
    exp_term = e61.expanding_zscore(
        e71._forward_fill(e140._signal_on_common(cs, "ETH", "term_slope")), e62.ZWINDOW
    )
    assert z_atm == exp_atm
    assert z_term == exp_term
    assert len(z_atm) == len(cs["common"]) == len(z_term)


# 7) composite is the equal-weight z-score combo of the OTHER asset's two legs
def test_composite_is_equal_weight_other_asset_zscore(monkeypatch):
    monkeypatch.setattr(e140, "PERMUTATION_PERMS", 40)
    monkeypatch.setattr(e140, "BOOTSTRAP_RESAMPLES", 40)
    caps = {
        "BTC": _craft_surface_capture("BTC", n_bars=300, seed=7),
        "ETH": _craft_surface_capture("ETH", n_bars=300, seed=8),
    }
    cfg = e140._eval_one_config(caps, target_inst="BTC", bar_seconds=300.0, horizon_bars=6)
    assert cfg["signal_underlying"] == "ETH"  # cross-asset, not self
    assert cfg["signal"] == e140.COMPOSITE_SIGNAL
    cs = e140.build_cross_section(caps, bar_seconds=300.0)
    z_atm, z_term = e140._zscore_pair(cs, "ETH")
    closes = e140._closes_on_common(cs, "BTC")
    fwd = e140._forward_return_skewness([{"close": c} for c in closes], 6)
    xs, ys = [], []
    for k in range(len(cs["common"])):
        if k >= len(fwd) or fwd[k] is None:
            continue
        xs.append(0.5 * z_atm[k] + 0.5 * z_term[k])
        ys.append(fwd[k])
    assert len(xs) == cfg["n_pairs"]
    ic, _ = e65._perm_p_ic(xs, ys, e140.PERMUTATION_PERMS, e140.SEED)
    assert math.isclose(cfg["spearman_ic"], ic, rel_tol=1e-12, abs_tol=1e-12)


# 8) _eval_one_config structure, leg comparators and determinism
def test_eval_one_config_structure_and_deterministic(monkeypatch):
    monkeypatch.setattr(e140, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e140, "BOOTSTRAP_RESAMPLES", 50)
    caps = {
        "BTC": _craft_surface_capture("BTC", n_bars=300, seed=9),
        "ETH": _craft_surface_capture("ETH", n_bars=300, seed=10),
    }
    a = e140._eval_one_config(caps, target_inst="BTC", bar_seconds=60.0, horizon_bars=6)
    b = e140._eval_one_config(caps, target_inst="BTC", bar_seconds=60.0, horizon_bars=6)
    assert a["target_underlying"] == "BTC"
    assert a["signal_underlying"] == "ETH"
    assert a["signal"] == e140.COMPOSITE_SIGNAL
    assert a["legs"] == ["atm_iv", "term_slope"]
    assert a["target"] == "realized_return_skewness"
    assert a["bar_seconds"] == 60.0
    assert a["horizon_bars"] == 6
    assert a["n_pairs"] >= e140.MIN_USABLE_PAIRS_PER_CONFIG
    assert -1.0 <= a["spearman_ic"] <= 1.0
    assert 0.0 <= a["permutation_p"] <= 1.0
    ci = a["bootstrap_ci"]
    assert len(ci) == 3 and ci[1] <= ci[0] <= ci[2]
    assert set(a["leg_ic"]) == {"atm_iv", "term_slope"}
    for v in a["leg_ic"].values():
        assert -1.0 <= v <= 1.0
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]
    assert a["leg_ic"] == b["leg_ic"]


# 9) below floor seals BLOCKED, never NO-GO
def test_below_floor_blocks_not_nogo():
    caps = {
        "BTC": _craft_surface_capture("BTC", n_bars=40, seed=1, n_trades_per_bar=4),
        "ETH": _craft_surface_capture("ETH", n_bars=40, seed=2, n_trades_per_bar=4),
    }
    td = _write_captures(caps)
    report = e140.run_eval140(capture_dir=td, write=False, task_label="TEST")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    if not report.get("floor_ok"):
        assert report["verdict"] == "BLOCKED"


# 10) run_eval140(write=False) meets floor and summarizes (floor monkeypatched ok)
def test_run_eval140_no_write_meets_floor_and_summarizes(monkeypatch):
    monkeypatch.setattr(e140, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e140, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e140, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e140, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(e140, "campaign_floor", lambda captures: {"checks": {}, "ok": True})
    caps = {
        "BTC": _craft_surface_capture("BTC", n_bars=300, seed=17),
        "ETH": _craft_surface_capture("ETH", n_bars=300, seed=18),
    }
    td = _write_captures(caps)
    report = e140.run_eval140(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert len(report["per_config"]) == 2  # 2 targets x 1 grid x 1 horizon
    assert report["protocol"]["target"] == "realized_return_skewness"
    assert report["protocol"]["composite_signal"] == e140.COMPOSITE_SIGNAL
    for s in report["per_target"]:
        assert "leg_best_ic" in s
        assert set(s["leg_best_ic"]) == {"atm_iv", "term_slope"}
        assert isinstance(s["beats_both_legs"], bool)


# 11) protocol constants pre-registered and floor reuses EVAL-71 surface floor
def test_protocol_constants():
    proto = e140.build_protocol("data/raw/eval61")
    assert proto["surface_signals"] == ["atm_iv", "term_slope"]
    assert proto["composite_signal"] == "composite_atm_iv_term_slope"
    assert proto["composite_weights"] == {"atm_iv": 0.5, "term_slope": 0.5}
    assert proto["target"] == "realized_return_skewness"
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert proto["forward_horizons_bars"] == [6, 24, 72]
    assert proto["cross_section"]["baseline"] == "BTC"
    assert proto["cross_section"]["relative"] == "ETH"
    assert proto["stats"]["seed"] == e62.SEED
    assert proto["floor"]["min_underlyings"] == e71.FLOOR["min_underlyings"]
    assert proto["floor"]["min_option_trades_per_underlying"] == e71.FLOOR["min_option_trades_per_underlying"]
    assert proto["floor"]["min_aligned_common_bars"] == e140.MIN_ALIGNED_COMMON_BARS
    assert proto["signal_window_seconds"] == e74.SIGNAL_WINDOW_SECONDS
    assert proto["atm_band"] == e74.ATM_BAND


# 12) campaign_floor requires both underlyings and alignment
def test_campaign_floor_requires_both_and_alignment():
    caps_both = {
        "BTC": _craft_surface_capture("BTC", n_bars=1200, seed=19, n_trades_per_bar=40),
        "ETH": _craft_surface_capture("ETH", n_bars=1200, seed=20, n_trades_per_bar=40),
    }
    floor = e140.campaign_floor(caps_both)
    assert floor["underlyings_ok"] is True
    assert floor["aligned_ok"] is True
    assert floor["ok"] is True
    floor_one = e140.campaign_floor({"BTC": caps_both["BTC"]})
    assert floor_one["underlyings_ok"] is False
    assert floor_one["ok"] is False


# 13) per-target summary keys the cross-asset pairing and pooled state
def test_per_target_pairing_and_pooled(monkeypatch):
    monkeypatch.setattr(e140, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e140, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e140, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e140, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(e140, "campaign_floor", lambda captures: {"checks": {}, "ok": True})
    caps = {
        "BTC": _craft_surface_capture("BTC", n_bars=300, seed=21),
        "ETH": _craft_surface_capture("ETH", n_bars=300, seed=22),
    }
    td = _write_captures(caps)
    report = e140.run_eval140(capture_dir=td, write=False)
    targets = {s["target_underlying"] for s in report["per_target"]}
    assert targets == {"BTC", "ETH"}
    for s in report["per_target"]:
        assert s["signal_underlying"] != s["target_underlying"]
        assert s["signal_underlying"] in ("BTC", "ETH")
    assert "bh_fdr" in report["pooled"]
    assert "all_targets_beat_both_legs" in report["pooled"]
    assert report["pooled"]["campaign_state"] in (
        "EVAL_140_COMPOSITE_ATM_IV_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_SKEWNESS",
        "EVAL_140_BLOCKED_FLOOR",
    )
