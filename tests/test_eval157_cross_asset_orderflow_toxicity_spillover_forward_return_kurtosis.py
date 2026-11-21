"""Unit tests for EVAL-157: does the **cross-asset causal options order-flow
toxicity spillover** (the OTHER underlying's z-scored options order-flow
toxicity) predict the subsequent **forward realized return kurtosis** (fourth
standardized moment) of the target underlying?

EVAL-157 reuses the EVAL-62 ``build_states(tox_signal="tox")`` toxicity signal
verbatim, the EVAL-77 cross-asset alignment on toxicity states, the EVAL-138
forward realized-return-kurtosis target verbatim, and the EVAL-65 inference
verbatim; the new logic is the cross-asset toxicity spillover pairing against
that distributional target.

Constructibility is verified on real data but these are **unit tests with
deterministic in-memory fixtures only** — ``e62.build_states`` is monkeypatched
to return synthetic states. No real data, no research_state writes, no network.
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
import scripts.eval138_cross_asset_term_ratio_spillover_forward_return_kurtosis as e138
import scripts.eval157_cross_asset_orderflow_toxicity_spillover_forward_return_kurtosis as e157

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000


def _states(n=260, seed=0, spot0=60000.0, bar_ms=_BAR_MS):
    """Deterministic per-bar order-flow toxicity states (spot random walk +
    signed z). bar_ms is the bar-open alignment key."""
    rng = random.Random(seed)
    px = spot0
    out = []
    for i in range(n):
        px = max(1.0, px * (1 + rng.uniform(-1, 1) * 1e-4))
        out.append({"bar_ms": _BASE_MS + i * bar_ms, "spot": px, "signal_z": rng.uniform(-2.0, 2.0)})
    return out


def _captures():
    """Minimal capture dicts (one per underlying); ``build_states`` is
    monkeypatched in the tests that need priceable states."""
    return {
        "BTC": {"underlying": "BTC", "surface": {"snapshots": []},
                "option_trades": [], "perp_candles": []},
        "ETH": {"underlying": "ETH", "surface": {"snapshots": []},
                "option_trades": [], "perp_candles": []},
    }


def _write_captures(caps):
    td = tempfile.mkdtemp()
    for inst, cap in caps.items():
        p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
    return td


# 1) artifact ids
def test_ids_are_eval157():
    assert e157.REPORT_ID.startswith("EVAL_157_")
    assert e157.PREREG_ID.startswith("EVAL_157_")
    assert e157.BLOCKED_ID.startswith("EVAL_157_")
    assert "ORDERFLOW_TOXICITY" in e157.REPORT_ID
    assert "SPILLOVER" in e157.REPORT_ID
    assert "FORWARD_RETURN_KURTOSIS" in e157.REPORT_ID
    assert e157.SURFACE_SIGNAL == "toxicity"
    assert e157.TARGET == "realized_return_kurtosis"


# 2) sealed machinery reused verbatim (not forked)
def test_reuse_helpers():
    assert e157.e71 is e71
    assert e157.e62 is e62
    assert e157.e65 is e65
    assert e157.e61 is e61
    assert e157.e138 is e138
    assert e157.e62.build_states is e62.build_states
    assert e157.e65._perm_p_ic is e65._perm_p_ic
    assert e157.e65._boot_ci_ic is e65._boot_ci_ic
    assert e157.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e157.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e157.SEED == e62.SEED
    assert e157.ZWINDOW == e62.ZWINDOW
    assert e157.FDR_ALPHA == e62.FDR_ALPHA


# 3) forward return kurtosis is finite (fat-tailed fixture, not degenerate)
def test_forward_return_kurtosis_is_finite():
    rng = random.Random(153)
    bars = []
    px = 100.0
    for i in range(140):
        drift = 0.05 if i % 19 == 0 else rng.uniform(-0.003, 0.003)
        px = px * (1.0 + drift)
        bars.append({"close": px})
    sk = e157._forward_return_kurtosis(bars, 24)
    finite = [v for v in sk if v is not None and math.isfinite(v)]
    assert len(finite) > 10


# 3b) forward kurtosis is byte-identical to the sealed EVAL-138 target
def test_forward_return_kurtosis_matches_eval138():
    rng = random.Random(7)
    bars = []
    px = 100.0
    for i in range(120):
        drift = 0.04 if i % 23 == 0 else rng.uniform(-0.002, 0.002)
        px = px * (1.0 + drift)
        bars.append({"close": px})
    a = e157._forward_return_kurtosis(bars, 12)
    b = e138._forward_return_kurtosis(bars, 12)
    assert a == b


# 4) build_cross_section aligns both underlyings on the common bar_ms grid
def test_build_cross_section_aligns_common_grid(monkeypatch):
    states_btc = _states(n=120, seed=1)
    states_eth = _states(n=120, seed=2)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: (
                            states_btc if cap.get("underlying") == "BTC" else states_eth))
    cs = e157.build_cross_section(_captures(), bar_seconds=300.0)
    assert set(cs["underlyings"]) == {"BTC", "ETH"}
    assert len(cs["common"]) == 120
    assert cs["bar_seconds"] == 300.0
    assert set(cs["maps"]["BTC"].keys()) >= set(cs["common"])
    assert set(cs["maps"]["ETH"].keys()) >= set(cs["common"])


# 5) spillover signal is the OTHER asset's toxicity (cross-asset, not self)
def test_spillover_signal_is_other_asset(monkeypatch):
    states_btc = _states(n=220, seed=3)
    states_eth = _states(n=220, seed=4)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: (
                            states_btc if cap.get("underlying") == "BTC" else states_eth))
    cs = e157.build_cross_section(_captures(), bar_seconds=300.0)
    btc_tox = e157._tox_on_common(cs, "BTC")
    eth_tox = e157._tox_on_common(cs, "ETH")
    assert len(btc_tox) == len(cs["common"])
    assert len(eth_tox) == len(cs["common"])
    filled_eth = e71._forward_fill(eth_tox)
    filled_btc = e71._forward_fill(btc_tox)
    assert all(v is not None for v in filled_eth)
    assert all(v is not None for v in filled_btc)


# 6) _eval_one_config targets forward kurtosis with cross-asset toxicity, deterministically
def test_eval_one_config_structure_and_deterministic(monkeypatch):
    monkeypatch.setattr(e157, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e157, "BOOTSTRAP_RESAMPLES", 50)
    states_btc = _states(n=300, seed=5)
    states_eth = _states(n=300, seed=6)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: (
                            states_btc if cap.get("underlying") == "BTC" else states_eth))
    caps = _captures()
    a = e157._eval_one_config(caps, target_inst="BTC", bar_seconds=60.0, horizon_bars=6)
    b = e157._eval_one_config(caps, target_inst="BTC", bar_seconds=60.0, horizon_bars=6)
    assert a["target_underlying"] == "BTC"
    assert a["signal_underlying"] == "ETH"
    assert a["signal"] == "toxicity"
    assert a["target"] == "realized_return_kurtosis"
    assert a["bar_seconds"] == 60.0
    assert a["horizon_bars"] == 6
    assert a["n_pairs"] >= e157.MIN_USABLE_PAIRS_PER_CONFIG
    assert -1.0 <= a["spearman_ic"] <= 1.0
    assert 0.0 <= a["permutation_p"] <= 1.0
    ci = a["bootstrap_ci"]
    assert len(ci) == 3 and ci[1] <= ci[0] <= ci[2]
    # determinism
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


# 7) below floor seals BLOCKED, never NO-GO
def test_below_floor_blocks_not_nogo(monkeypatch):
    monkeypatch.setattr(e62, "build_states", lambda cap, tox_signal, bar_seconds: [])
    caps = _captures()
    td = _write_captures(caps)
    report = e157.run_eval157(capture_dir=td, write=False, task_label="TEST")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    if not report.get("floor_ok"):
        assert report["verdict"] == "BLOCKED"


# 8) run_eval157(write=False) meets floor and summarizes (floor monkeypatched ok)
def test_run_eval157_no_write_meets_floor_and_summarizes(monkeypatch):
    monkeypatch.setattr(e157, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e157, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e157, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e157, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e157, "campaign_floor",
        lambda captures, bar_seconds=None: {"underlyings": sorted(captures), "ok": True,
                                            "per_underlying": {i: {"ok": True} for i in captures},
                                            "checks": {"underlyings_ok": True, "aligned_ok": True}},
    )
    states = _states(n=300, seed=5)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: states)
    td = _write_captures(_captures())
    report = e157.run_eval157(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    # one config per target (2 targets x 1 grid point) = 2
    assert len(report["per_config"]) == 2
    assert report["protocol"]["target"] == "realized_return_kurtosis"
    assert report["protocol"]["surface_signal"] == "toxicity"


# 9) protocol constants pre-registered
def test_protocol_constants():
    proto = e157.build_protocol("data/raw/eval61")
    assert proto["surface_signal"] == "toxicity"
    assert proto["target"] == "realized_return_kurtosis"
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert proto["forward_horizons_bars"] == [6, 24, 72]
    assert proto["cross_section"]["baseline"] == "BTC"
    assert proto["cross_section"]["relative"] == "ETH"
    assert proto["stats"]["seed"] == e62.SEED
    assert proto["stats"]["zwindow"] == e62.ZWINDOW
    assert proto["stats"]["fdr_alpha"] == e62.FDR_ALPHA
    assert proto["floor"]["min_underlyings"] == 2
    assert proto["floor"]["min_aligned_common_bars"] == e157.MIN_ALIGNED_COMMON_BARS


# 10) campaign_floor requires both underlyings and alignment
def test_campaign_floor_requires_both_and_alignment(monkeypatch):
    states_rich = _states(n=300, seed=9)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: states_rich)
    caps_both = _captures()
    floor = e157.campaign_floor(caps_both, bar_seconds=300.0)
    assert floor["underlyings_ok"] is True
    assert floor["aligned_ok"] is True
    assert floor["ok"] is True
    # single underlying fails underlyings_ok
    floor_one = e157.campaign_floor({"BTC": caps_both["BTC"]}, bar_seconds=300.0)
    assert floor_one["underlyings_ok"] is False
    assert floor_one["ok"] is False


# 11) per-target summary keys signal/target pairing (cross-asset: signal != target)
def test_per_target_summary_pairing(monkeypatch):
    monkeypatch.setattr(e157, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e157, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e157, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e157, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e157, "campaign_floor",
        lambda captures, bar_seconds=None: {"underlyings": sorted(captures), "ok": True,
                                            "per_underlying": {i: {"ok": True} for i in captures},
                                            "checks": {"underlyings_ok": True, "aligned_ok": True}},
    )
    states_btc = _states(n=300, seed=21)
    states_eth = _states(n=300, seed=22)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: (
                            states_btc if cap.get("underlying") == "BTC" else states_eth))
    td = _write_captures(_captures())
    report = e157.run_eval157(capture_dir=td, write=False)
    targets = {s["target_underlying"] for s in report["per_target"]}
    assert targets == {"BTC", "ETH"}
    for s in report["per_target"]:
        sig = s["signal_underlying"]
        tgt = s["target_underlying"]
        assert sig != tgt  # cross-asset: signal never equals target
        assert sig in ("BTC", "ETH")


# 12) pooled BH-FDR key present and campaign_state set
def test_pooled_bh_fdr_and_campaign_state(monkeypatch):
    monkeypatch.setattr(e157, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e157, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e157, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e157, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e157, "campaign_floor",
        lambda captures, bar_seconds=None: {"underlyings": sorted(captures), "ok": True,
                                            "per_underlying": {i: {"ok": True} for i in captures},
                                            "checks": {"underlyings_ok": True, "aligned_ok": True}},
    )
    states_btc = _states(n=300, seed=31)
    states_eth = _states(n=300, seed=32)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: (
                            states_btc if cap.get("underlying") == "BTC" else states_eth))
    td = _write_captures(_captures())
    report = e157.run_eval157(capture_dir=td, write=False)
    assert "bh_fdr" in report["pooled"]
    assert "campaign_state" in report["pooled"]
    assert report["pooled"]["campaign_state"] in (
        "EVAL_157_CROSS_ASSET_ORDERFLOW_TOXICITY_SPILLOVER_FORWARD_RETURN_KURTOSIS",
        "EVAL_157_BLOCKED_FLOOR",
    )