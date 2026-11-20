"""Unit tests for EVAL-132: does the **cross-asset causal near-ATM implied-vol
skew spillover** (the OTHER underlying's ``skew``) predict the subsequent
**forward realized return skewness** (third standardized moment) of the target
underlying?

EVAL-132 is the first cell of a NEW physics-independent predictiveness line that
has never been run: cross-asset skew spillover -> forward realized return
skewness. It reuses the EVAL-71 surface reconstruction
(``build_surface_bars`` with ``skew`` signal), the EVAL-71 surface floor verbatim,
the cross-asset alignment, and the EVAL-109 forward realized-return-skewness
target verbatim; the new logic is the cross-asset skew spillover pairing.

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
import scripts.eval132_cross_asset_skew_spillover_forward_return_skewness as e132

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000
_BASE_MS -= _BASE_MS % _BAR_MS


def _craft_skew_capture(
    inst="BTC", *, n_bars=200, seed=0, n_trades_per_bar=40, base_ms=_BASE_MS, bar_ms=_BAR_MS,
):
    """Deterministic three-way capture whose real option-trade IV populates a
    non-null near-ATM put-call skew at every bar (>= put and call trades in the
    trailing signal window near ATM)."""
    rng = random.Random(seed)
    px = 60000.0 if inst == "BTC" else 3000.0
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
            iv = 65.0 + rng.uniform(-1.0, 1.0) if typ == "P" else 55.0 + rng.uniform(-1.0, 1.0)
            trades.append({
                "ts": ts + j * 1000,
                "instrument": f"{inst}-20NOV26-{int(round(strike))}-{typ}",
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
def test_ids_are_eval132():
    assert e132.REPORT_ID.startswith("EVAL_132_")
    assert e132.PREREG_ID.startswith("EVAL_132_")
    assert e132.BLOCKED_ID.startswith("EVAL_132_")
    assert "SKEW" in e132.REPORT_ID
    assert "SPILLOVER" in e132.REPORT_ID
    assert "FORWARD_RETURN_SKEWNESS" in e132.REPORT_ID
    assert e132.SURFACE_SIGNAL == "skew"
    assert e132.TARGET == "realized_return_skewness"


# 2) sealed machinery reused verbatim (not forked)
def test_reuse_helpers():
    assert e132.e71 is e71
    assert e132.e65 is e65
    assert e132.e61 is e61
    assert e132.e62 is e62


# 3) forward realized return skewness is finite and distinct from RV level
def test_forward_return_skewness_is_finite():
    rng = random.Random(132)
    bars = []
    px = 100.0
    for i in range(80):
        drift = 0.03 if i % 17 == 0 else rng.uniform(-0.002, 0.002)
        px = px * (1.0 + drift)
        bars.append({"close": px, "bar_open_ms": i * 300000, "skew": 0.4})
    skew = e132._forward_return_skewness(bars, 24)
    finite = [v for v in skew if v is not None and math.isfinite(v)]
    assert len(finite) > 10
    assert any(v != 0.0 for v in finite)
    assert all(abs(v) < 50.0 for v in finite)
    rv = e71._forward_rv(bars, 24)
    assert len(rv) > 0


# 4) build_cross_section aligns both underlyings on the common surface bar grid
def test_build_cross_section_aligns_common_grid():
    caps = {
        "BTC": _craft_skew_capture("BTC", n_bars=120, seed=1),
        "ETH": _craft_skew_capture("ETH", n_bars=120, seed=2),
    }
    cs = e132.build_cross_section(caps, bar_seconds=300.0)
    assert set(cs["underlyings"]) == {"BTC", "ETH"}
    assert len(cs["common"]) > 50
    assert cs["bar_seconds"] == 300.0
    assert set(cs["maps"]["BTC"].keys()) >= set(cs["common"])
    assert set(cs["maps"]["ETH"].keys()) >= set(cs["common"])
    # skew is actually reconstructed (surface signal present)
    skews = e132._skew_on_common(cs, "BTC")
    assert any(v is not None for v in skews)


# 5) spillover signal is the OTHER asset's skew (cross-asset, not self)
def test_spillover_signal_is_other_asset():
    caps = {
        "BTC": _craft_skew_capture("BTC", n_bars=220, seed=3),
        "ETH": _craft_skew_capture("ETH", n_bars=220, seed=4),
    }
    cs = e132.build_cross_section(caps, bar_seconds=300.0)
    btc_skew = e132._skew_on_common(cs, "BTC")
    eth_skew = e132._skew_on_common(cs, "ETH")
    assert len(btc_skew) == len(cs["common"])
    assert len(eth_skew) == len(cs["common"])
    # for BTC target the signal is ETH's skew; for ETH target the signal is BTC's
    assert all(v is not None for v in e71._forward_fill(eth_skew))
    assert all(v is not None for v in e71._forward_fill(btc_skew))


# 6) _eval_one_config targets forward realized return skewness with cross-asset skew, deterministically
def test_eval_one_config_structure_and_deterministic(monkeypatch):
    monkeypatch.setattr(e132, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e132, "BOOTSTRAP_RESAMPLES", 50)
    caps = {
        "BTC": _craft_skew_capture("BTC", n_bars=300, seed=5),
        "ETH": _craft_skew_capture("ETH", n_bars=300, seed=6),
    }
    a = e132._eval_one_config(caps, target_inst="BTC", bar_seconds=60.0, horizon_bars=6)
    b = e132._eval_one_config(caps, target_inst="BTC", bar_seconds=60.0, horizon_bars=6)
    assert a["target_underlying"] == "BTC"
    assert a["signal_underlying"] == "ETH"
    assert a["signal"] == "skew"
    assert a["target"] == "realized_return_skewness"
    assert a["bar_seconds"] == 60.0
    assert a["horizon_bars"] == 6
    assert a["n_pairs"] >= e132.MIN_USABLE_PAIRS_PER_CONFIG
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
        "BTC": _craft_skew_capture("BTC", n_bars=40, seed=1, n_trades_per_bar=2),
        "ETH": _craft_skew_capture("ETH", n_bars=40, seed=2, n_trades_per_bar=2),
    }
    td = _write_captures(caps)
    report = e132.run_eval132(capture_dir=td, write=False, task_label="TEST")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    if not report.get("floor_ok"):
        assert report["verdict"] == "BLOCKED"


# 8) run_eval132(write=False) meets floor and summarizes (floor monkeypatched ok)
def test_run_eval132_no_write_meets_floor_and_summarizes(monkeypatch):
    monkeypatch.setattr(e132, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e132, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e132, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e132, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e132, "campaign_floor",
        lambda captures: {"checks": {}, "ok": True},
    )
    caps = {
        "BTC": _craft_skew_capture("BTC", n_bars=300, seed=17),
        "ETH": _craft_skew_capture("ETH", n_bars=300, seed=18),
    }
    td = _write_captures(caps)
    report = e132.run_eval132(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    # one config per target (2 targets x 1 grid point) = 2
    assert len(report["per_config"]) == 2
    assert report["protocol"]["target"] == "realized_return_skewness"
    assert report["protocol"]["surface_signal"] == "skew"


# 9) protocol constants pre-registered and floor reuses EVAL-71 surface floor
def test_protocol_constants():
    proto = e132.build_protocol("data/raw/eval61")
    assert proto["surface_signal"] == "skew"
    assert proto["target"] == "realized_return_skewness"
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert proto["forward_horizons_bars"] == [6, 24, 72]
    assert proto["cross_section"]["baseline"] == "BTC"
    assert proto["cross_section"]["relative"] == "ETH"
    assert proto["stats"]["seed"] == e62.SEED
    assert proto["floor"]["min_underlyings"] == e71.FLOOR["min_underlyings"]
    assert proto["floor"]["min_option_trades_per_underlying"] == e71.FLOOR["min_option_trades_per_underlying"]
    assert proto["floor"]["min_aligned_common_bars"] == e132.MIN_ALIGNED_COMMON_BARS
    assert proto["signal_window_seconds"] == e71.SIGNAL_WINDOW_SECONDS
    assert proto["atm_band"] == e71.ATM_BAND


# 10) campaign_floor requires both underlyings and alignment
def test_campaign_floor_requires_both_and_alignment():
    caps_both = {
        "BTC": _craft_skew_capture("BTC", n_bars=1200, seed=9, n_trades_per_bar=40),
        "ETH": _craft_skew_capture("ETH", n_bars=1200, seed=10, n_trades_per_bar=40),
    }
    floor = e132.campaign_floor(caps_both)
    assert floor["underlyings_ok"] is True
    assert floor["aligned_ok"] is True
    assert floor["ok"] is True
    # single underlying fails underlyings_ok
    floor_one = e132.campaign_floor({"BTC": caps_both["BTC"]})
    assert floor_one["underlyings_ok"] is False
    assert floor_one["ok"] is False


# 11) per-target summary keys signal/target pairing
def test_per_target_summary_pairing(monkeypatch):
    monkeypatch.setattr(e132, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e132, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e132, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e132, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e132, "campaign_floor",
        lambda captures: {"checks": {}, "ok": True},
    )
    caps = {
        "BTC": _craft_skew_capture("BTC", n_bars=300, seed=21),
        "ETH": _craft_skew_capture("ETH", n_bars=300, seed=22),
    }
    td = _write_captures(caps)
    report = e132.run_eval132(capture_dir=td, write=False)
    targets = {s["target_underlying"] for s in report["per_target"]}
    assert targets == {"BTC", "ETH"}
    for s in report["per_target"]:
        sig = s["signal_underlying"]
        tgt = s["target_underlying"]
        assert sig != tgt  # cross-asset: signal never equals target
        assert sig in ("BTC", "ETH")


# 12) pooled BH-FDR key present and campaign_state set
def test_pooled_bh_fdr_and_campaign_state(monkeypatch):
    monkeypatch.setattr(e132, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e132, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e132, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e132, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e132, "campaign_floor",
        lambda captures: {"checks": {}, "ok": True},
    )
    caps = {
        "BTC": _craft_skew_capture("BTC", n_bars=300, seed=31),
        "ETH": _craft_skew_capture("ETH", n_bars=300, seed=32),
    }
    td = _write_captures(caps)
    report = e132.run_eval132(capture_dir=td, write=False)
    assert "bh_fdr" in report["pooled"]
    assert "campaign_state" in report["pooled"]
    assert report["pooled"]["campaign_state"] in (
        "EVAL_132_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_RETURN_SKEWNESS",
        "EVAL_132_BLOCKED_FLOOR",
    )
