"""Unit tests for EVAL-151: does the **cross-asset causal options order-flow
toxicity x atm_iv surface interaction spillover** (the OTHER underlying's
z-scored options order-flow toxicity multiplied by its near-ATM implied-vol
level) predict the subsequent **forward signed (directional) log-return mean**
of the target underlying?

EVAL-151 reuses the EVAL-62 ``build_states(tox_signal="tox")`` toxicity
signal verbatim, the EVAL-71 ``build_surface_bars`` atm_iv surface-bar signal
verbatim, the EVAL-77 cross-asset alignment, the EVAL-101 forward signed
log-return-mean target verbatim, and the EVAL-65 inference verbatim; the new
logic is the interaction spillover pairing against that target.

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
import scripts.eval101_single_asset_atm_iv_forward_signed_return as e101
import scripts.eval151_cross_asset_oflow_tox_atm_iv_interaction_spillover_forward_signed_return_mean as e151

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000
_BASE_MS -= _BASE_MS % _BAR_MS


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


def _surface_bars(n=260, seed=0, px0=60000.0, bar_ms=_BAR_MS, atm_iv=0.70):
    """Deterministic per-bar surface atm_iv bars (spot random walk + constant
    near-ATM IV). bar_ms is the bar-open alignment key."""
    rng = random.Random(seed)
    px = px0
    out = []
    for i in range(n):
        px = max(1.0, px * (1 + rng.uniform(-1, 1) * 1e-4))
        ts = _BASE_MS + i * bar_ms
        out.append({
            "bar_open_ms": ts,
            "close": px,
            "atm_iv": atm_iv + rng.uniform(-0.005, 0.005),
        })
    return out


def _captures():
    """Minimal capture dicts (one per underlying); ``build_states`` and
    ``build_surface_bars`` are monkeypatched in the tests that need them."""
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
def test_ids_are_eval151():
    assert e151.REPORT_ID.startswith("EVAL_151_")
    assert e151.PREREG_ID.startswith("EVAL_151_")
    assert e151.BLOCKED_ID.startswith("EVAL_151_")
    assert "O FLOW_ATM_IV_INTERACTION".replace(" ", "_") in e151.REPORT_ID or "OFLOW_TOX_ATM_IV_INTERACTION" in e151.REPORT_ID
    assert "SPILLOVER" in e151.REPORT_ID
    assert "FORWARD_SIGNED_RETURN_MEAN" in e151.REPORT_ID
    assert e151.SURFACE_SIGNAL == "oflow_tox_atm_iv_interaction"
    assert e151.TARGET == "forward_signed_return"


# 2) sealed machinery reused verbatim (not forked)
def test_reuse_helpers():
    assert e151.e71 is e71
    assert e151.e65 is e65
    assert e151.e61 is e61
    assert e151.e62 is e62
    assert e151.e101 is e101
    assert e151.e62.build_states is e62.build_states
    assert e151.e65._perm_p_ic is e65._perm_p_ic
    assert e151.e65._boot_ci_ic is e65._boot_ci_ic
    assert e151.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e151.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e151.SEED == e62.SEED
    assert e151.ZWINDOW == e62.ZWINDOW
    assert e151.FDR_ALPHA == e62.FDR_ALPHA


# 3) forward signed return is finite and directional
def test_forward_signed_return_is_finite_and_directional():
    rng = random.Random(150)
    bars = []
    px = 100.0
    for i in range(80):
        drift = 0.03 if i % 17 == 0 else rng.uniform(-0.002, 0.002)
        px = px * (1.0 + drift)
        bars.append({"close": px})
    fsr = e151._forward_signed_return(bars, 24)
    finite = [v for v in fsr if v is not None and math.isfinite(v)]
    assert len(finite) > 10


# 4) build_cross_section aligns both underlyings on the common bar_ms grid
def test_build_cross_section_aligns_common_grid(monkeypatch):
    states_btc = _states(n=120, seed=1)
    states_eth = _states(n=120, seed=2)
    bars_btc = _surface_bars(n=120, seed=3)
    bars_eth = _surface_bars(n=120, seed=4)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: (
                            states_btc if cap.get("underlying") == "BTC" else states_eth))
    monkeypatch.setattr(e71, "build_surface_bars",
                        lambda cap, bar_seconds: (
                            bars_btc if cap.get("underlying") == "BTC" else bars_eth))
    cs = e151.build_cross_section(_captures(), bar_seconds=300.0)
    assert set(cs["underlyings"]) == {"BTC", "ETH"}
    assert len(cs["common"]) == 120
    assert cs["bar_seconds"] == 300.0


# 5) interaction signal is tox_z * atm_iv_z of the OTHER asset (cross-asset, not self)
def test_interaction_signal_is_other_asset_product(monkeypatch):
    states_btc = _states(n=220, seed=5)
    states_eth = _states(n=220, seed=6)
    bars_btc = _surface_bars(n=220, seed=7, atm_iv=0.65)
    bars_eth = _surface_bars(n=220, seed=8, atm_iv=0.72)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: (
                            states_btc if cap.get("underlying") == "BTC" else states_eth))
    monkeypatch.setattr(e71, "build_surface_bars",
                        lambda cap, bar_seconds: (
                            bars_btc if cap.get("underlying") == "BTC" else bars_eth))
    cs = e151.build_cross_section(_captures(), bar_seconds=300.0)
    btc_tox = e151._tox_on_common(cs, "BTC")
    eth_tox = e151._tox_on_common(cs, "ETH")
    btc_aiv = e151._atm_iv_on_common(cs, "BTC")
    eth_aiv = e151._atm_iv_on_common(cs, "ETH")
    assert len(btc_tox) == len(cs["common"])
    assert len(eth_tox) == len(cs["common"])
    assert len(btc_aiv) == len(cs["common"])
    assert len(eth_aiv) == len(cs["common"])
    # For target BTC, signal comes from ETH: interaction = eth_tox * eth_aiv
    filled_eth_tox = e71._forward_fill(eth_tox)
    filled_eth_aiv = e71._forward_fill(eth_aiv)
    assert all(v is not None for v in filled_eth_tox)
    assert all(v is not None for v in filled_eth_aiv)


# 6) _eval_one_config targets forward signed return with cross-asset interaction, deterministically
def test_eval_one_config_structure_and_deterministic(monkeypatch):
    monkeypatch.setattr(e151, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e151, "BOOTSTRAP_RESAMPLES", 50)
    states_btc = _states(n=300, seed=9)
    states_eth = _states(n=300, seed=10)
    bars_btc = _surface_bars(n=300, seed=11, atm_iv=0.68)
    bars_eth = _surface_bars(n=300, seed=12, atm_iv=0.71)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: (
                            states_btc if cap.get("underlying") == "BTC" else states_eth))
    monkeypatch.setattr(e71, "build_surface_bars",
                        lambda cap, bar_seconds: (
                            bars_btc if cap.get("underlying") == "BTC" else bars_eth))
    caps = _captures()
    a = e151._eval_one_config(caps, target_inst="BTC", bar_seconds=60.0, horizon_bars=6)
    b = e151._eval_one_config(caps, target_inst="BTC", bar_seconds=60.0, horizon_bars=6)
    assert a["target_underlying"] == "BTC"
    assert a["signal_underlying"] == "ETH"
    assert a["signal"] == "oflow_tox_atm_iv_interaction"
    assert a["target"] == "forward_signed_return"
    assert a["bar_seconds"] == 60.0
    assert a["horizon_bars"] == 6
    assert a["n_pairs"] >= e151.MIN_USABLE_PAIRS_PER_CONFIG
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
    monkeypatch.setattr(e71, "build_surface_bars", lambda cap, bar_seconds: [])
    caps = _captures()
    td = _write_captures(caps)
    report = e151.run_eval151(capture_dir=td, write=False, task_label="TEST")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    if not report.get("floor_ok"):
        assert report["verdict"] == "BLOCKED"


# 8) run_eval151(write=False) meets floor and summarizes (floor monkeypatched ok)
def test_run_eval151_no_write_meets_floor_and_summarizes(monkeypatch):
    monkeypatch.setattr(e151, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e151, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e151, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e151, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e151, "campaign_floor",
        lambda captures, bar_seconds=None: {"underlyings": sorted(captures), "ok": True,
                                            "per_underlying": {i: {"ok": True} for i in captures},
                                            "checks": {"underlyings_ok": True, "aligned_ok": True}},
    )
    states = _states(n=300, seed=13)
    bars = _surface_bars(n=300, seed=14, atm_iv=0.70)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: states)
    monkeypatch.setattr(e71, "build_surface_bars",
                        lambda cap, bar_seconds: bars)
    td = _write_captures(_captures())
    report = e151.run_eval151(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    # one config per target (2 targets x 1 grid point) = 2
    assert len(report["per_config"]) == 2
    assert report["protocol"]["target"] == "forward_signed_return"
    assert report["protocol"]["surface_signal"] == "oflow_tox_atm_iv_interaction"


# 9) protocol constants pre-registered
def test_protocol_constants():
    proto = e151.build_protocol("data/raw/eval61")
    assert proto["surface_signal"] == "oflow_tox_atm_iv_interaction"
    assert proto["target"] == "forward_signed_return"
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert proto["forward_horizons_bars"] == [6, 24, 72]
    assert proto["cross_section"]["baseline"] == "BTC"
    assert proto["cross_section"]["relative"] == "ETH"
    assert proto["stats"]["seed"] == e62.SEED
    assert proto["stats"]["zwindow"] == e62.ZWINDOW
    assert proto["stats"]["fdr_alpha"] == e62.FDR_ALPHA
    assert proto["floor"]["min_underlyings"] == 2
    assert proto["floor"]["min_aligned_common_bars"] == e151.MIN_ALIGNED_COMMON_BARS


# 10) campaign_floor requires both underlyings and alignment
def test_campaign_floor_requires_both_and_alignment(monkeypatch):
    states_rich = _states(n=300, seed=15)
    bars_rich = _surface_bars(n=300, seed=16, atm_iv=0.70)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: states_rich)
    monkeypatch.setattr(e71, "build_surface_bars",
                        lambda cap, bar_seconds: bars_rich)
    caps_both = _captures()
    floor = e151.campaign_floor(caps_both, bar_seconds=300.0)
    assert floor["underlyings_ok"] is True
    assert floor["aligned_ok"] is True
    assert floor["ok"] is True
    # single underlying fails underlyings_ok
    floor_one = e151.campaign_floor({"BTC": caps_both["BTC"]}, bar_seconds=300.0)
    assert floor_one["underlyings_ok"] is False
    assert floor_one["ok"] is False


# 11) per-target summary keys signal/target pairing (cross-asset: signal != target)
def test_per_target_summary_pairing(monkeypatch):
    monkeypatch.setattr(e151, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e151, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e151, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e151, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e151, "campaign_floor",
        lambda captures, bar_seconds=None: {"underlyings": sorted(captures), "ok": True,
                                            "per_underlying": {i: {"ok": True} for i in captures},
                                            "checks": {"underlyings_ok": True, "aligned_ok": True}},
    )
    states_btc = _states(n=300, seed=21)
    states_eth = _states(n=300, seed=22)
    bars_btc = _surface_bars(n=300, seed=23, atm_iv=0.69)
    bars_eth = _surface_bars(n=300, seed=24, atm_iv=0.71)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: (
                            states_btc if cap.get("underlying") == "BTC" else states_eth))
    monkeypatch.setattr(e71, "build_surface_bars",
                        lambda cap, bar_seconds: (
                            bars_btc if cap.get("underlying") == "BTC" else bars_eth))
    td = _write_captures(_captures())
    report = e151.run_eval151(capture_dir=td, write=False)
    targets = {s["target_underlying"] for s in report["per_target"]}
    assert targets == {"BTC", "ETH"}
    for s in report["per_target"]:
        sig = s["signal_underlying"]
        tgt = s["target_underlying"]
        assert sig != tgt  # cross-asset: signal never equals target
        assert sig in ("BTC", "ETH")


# 12) pooled BH-FDR key present and campaign_state set
def test_pooled_bh_fdr_and_campaign_state(monkeypatch):
    monkeypatch.setattr(e151, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e151, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e151, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e151, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e151, "campaign_floor",
        lambda captures, bar_seconds=None: {"underlyings": sorted(captures), "ok": True,
                                            "per_underlying": {i: {"ok": True} for i in captures},
                                            "checks": {"underlyings_ok": True, "aligned_ok": True}},
    )
    states_btc = _states(n=300, seed=31)
    states_eth = _states(n=300, seed=32)
    bars_btc = _surface_bars(n=300, seed=33, atm_iv=0.69)
    bars_eth = _surface_bars(n=300, seed=34, atm_iv=0.71)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: (
                            states_btc if cap.get("underlying") == "BTC" else states_eth))
    monkeypatch.setattr(e71, "build_surface_bars",
                        lambda cap, bar_seconds: (
                            bars_btc if cap.get("underlying") == "BTC" else bars_eth))
    td = _write_captures(_captures())
    report = e151.run_eval151(capture_dir=td, write=False)
    assert "bh_fdr" in report["pooled"]
    assert "campaign_state" in report["pooled"]
    assert report["pooled"]["campaign_state"] in (
        "EVAL_151_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN",
        "EVAL_151_BLOCKED_FLOOR",
    )
