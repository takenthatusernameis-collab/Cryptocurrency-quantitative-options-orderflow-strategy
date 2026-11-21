"""Unit tests for EVAL-161 TRACK B: does the single-asset causal near-to-far ATM
implied-vol **term slope** (term_slope = IV(near expiry) - IV(far expiry))
predict the subsequent **forward expected shortfall / CVaR** of the signed return
of the SAME underlying?

EVAL-161 reuses EVAL-74 _term_bars (term_slope signal), EVAL-71 _forward_fill,
EVAL-61 expanding_zscore, EVAL-65 _perm_p_ic/_boot_ci_ic inference verbatim;
the new logic is the forward CVaR target (mean of worst alpha-tail of forward
log returns).

Unit tests with deterministic in-memory fixtures only — e74._term_bars is
monkeypatched where needed. No real data, no research_state writes, no network.
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
import scripts.eval161_single_asset_term_slope_forward_cvar as e161

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000


def _bars(n=260, seed=0, close0=60000.0, bar_ms=_BAR_MS):
    """Deterministic per-bar perp bars (close random walk)."""
    rng = random.Random(seed)
    px = close0
    out = []
    for i in range(n):
        px = max(1.0, px * (1 + rng.uniform(-1, 1) * 1e-4))
        out.append({"bar_open_ms": _BASE_MS + i * bar_ms, "close": px})
    return out


def _captures():
    """Minimal capture dicts (one per underlying)."""
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
def test_ids_are_eval161():
    assert e161.REPORT_ID.startswith("EVAL_161_")
    assert e161.PREREG_ID.startswith("EVAL_161_")
    assert e161.BLOCKED_ID.startswith("EVAL_161_")
    assert "TERM_SLOPE" in e161.REPORT_ID
    assert "FORWARD_CVAR" in e161.REPORT_ID
    assert e161.TERM_SIGNAL == "term_slope"
    assert e161.TARGET == "forward_cvar"
    assert abs(e161.CVAR_ALPHA - 0.05) < 1e-12


# 2) sealed machinery reused verbatim (not forked)
def test_reuse_helpers():
    assert e161.e74 is e74
    assert e161.e71 is e71
    assert e161.e65 is e65
    assert e161.e62 is e62
    assert e161.e61 is e61
    assert e161.e74._term_bars is e74._term_bars
    assert e161.e71._forward_fill is e71._forward_fill
    assert e161.e61.expanding_zscore is e61.expanding_zscore
    assert e161.e65._perm_p_ic is e65._perm_p_ic
    assert e161.e65._boot_ci_ic is e65._boot_ci_ic
    assert e161.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e161.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e161.SEED == e62.SEED
    assert e161.ZWINDOW == e62.ZWINDOW
    assert e161.FDR_ALPHA == e62.FDR_ALPHA


# 3) forward CVaR is finite (dispersed fixture, not degenerate)
def test_forward_cvar_is_finite():
    rng = random.Random(153)
    bars = []
    px = 100.0
    for i in range(140):
        drift = 0.05 if i % 19 == 0 else rng.uniform(-0.003, 0.003)
        px = px * (1.0 + drift)
        bars.append({"close": px})
    cv = e161._forward_cvar(bars, 24)
    finite = [v for v in cv if v is not None and math.isfinite(v)]
    assert len(finite) > 10


# 3b) forward CVaR equals manual worst-alpha-tail mean
def test_forward_cvar_matches_manual_tail_mean():
    closes = [100.0, 101.0, 99.0, 102.0, 98.0, 103.0, 97.0, 104.0]
    bars = [{"close": c} for c in closes]
    got = e161._forward_cvar(bars, 3, cvar_alpha=0.5)
    lr = [math.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)]
    assert len(got) == len(lr) - 3 + 1
    alpha = 0.5
    for k, g in enumerate(got):
        seg = sorted(lr[k:k + 3])
        n_tail = max(1, int(math.ceil(len(seg) * alpha)))
        expected = sum(seg[:n_tail]) / len(seg[:n_tail])
        assert g is not None and abs(g - expected) < 1e-15


# 4) _eval_one_config targets forward CVaR with term_slope, deterministically
def test_eval_one_config_structure_and_deterministic(monkeypatch):
    monkeypatch.setattr(e161, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e161, "BOOTSTRAP_RESAMPLES", 50)
    term_bars = [
        {"bar_open_ms": _BASE_MS + i * _BAR_MS, "close": 100.0 + i * 0.01,
         "term_slope": 0.001 * i} for i in range(300)
    ]
    monkeypatch.setattr(e74, "_term_bars", lambda cap, bar_seconds=300.0: term_bars)
    caps = _captures()
    a = e161._eval_one_config(caps["BTC"], bar_seconds=60.0, horizon_bars=6)
    b = e161._eval_one_config(caps["BTC"], bar_seconds=60.0, horizon_bars=6)
    assert a["underlying"] == "BTC"
    assert a["signal"] == "term_slope"
    assert a["target"] == "forward_cvar"
    assert a["bar_seconds"] == 60.0
    assert a["horizon_bars"] == 6
    assert a["n_pairs"] >= e161.MIN_USABLE_PAIRS_PER_CONFIG
    assert -1.0 <= a["spearman_ic"] <= 1.0
    assert 0.0 <= a["permutation_p"] <= 1.0
    ci = a["bootstrap_ci"]
    assert len(ci) == 3 and ci[1] <= ci[0] <= ci[2]
    # determinism
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


# 5) below floor seals BLOCKED, never NO-GO
def test_below_floor_blocks_not_nogo(monkeypatch):
    monkeypatch.setattr(e74, "_term_bars", lambda cap, bar_seconds=300.0: [])
    caps = _captures()
    td = _write_captures(caps)
    report = e161.run_eval161(capture_dir=td, write=False, task_label="TEST")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    if not report.get("floor_ok"):
        assert report["verdict"] == "BLOCKED"


# 6) run_eval161(write=False) meets floor and summarizes (floor monkeypatched ok)
def test_run_eval161_no_write_meets_floor_and_summarizes(monkeypatch):
    monkeypatch.setattr(e161, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e161, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e161, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e161, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e161, "_campaign_floor",
        lambda per_underlying: {"checks": {"underlyings_ok": True,
                                           "all_underlyings_ok": True}, "ok": True},
    )
    term_bars = [
        {"bar_open_ms": _BASE_MS + i * _BAR_MS, "close": 100.0 + i * 0.01,
         "term_slope": 0.001 * i} for i in range(300)
    ]
    monkeypatch.setattr(e74, "_term_bars", lambda cap, bar_seconds=300.0: term_bars)
    td = _write_captures(_captures())
    report = e161.run_eval161(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    # one config per underlying (1 grid point x 1 horizon x 2 underlyings) = 2
    assert len(report["per_config"]) == 2
    assert report["protocol"]["target"] == "forward_cvar"
    assert report["protocol"]["term_signal"] == "term_slope"


# 7) protocol constants pre-registered
def test_protocol_constants():
    proto = e161.build_protocol("data/raw/eval61")
    assert proto["term_signal"] == "term_slope"
    assert proto["target"] == "forward_cvar"
    assert abs(proto["cvar_alpha"] - 0.05) < 1e-12
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert proto["forward_horizons_bars"] == [6, 24, 72]
    assert proto["stats"]["seed"] == e62.SEED
    assert proto["stats"]["zwindow"] == e62.ZWINDOW
    assert proto["stats"]["fdr_alpha"] == e62.FDR_ALPHA
    assert proto["floor"]["min_underlyings"] == 2


# 8) per-underlying summary keys
def test_per_underlying_summary_keys(monkeypatch):
    monkeypatch.setattr(e161, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e161, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e161, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e161, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e161, "_campaign_floor",
        lambda per_underlying: {"checks": {"underlyings_ok": True,
                                           "all_underlyings_ok": True}, "ok": True},
    )
    term_bars = [
        {"bar_open_ms": _BASE_MS + i * _BAR_MS, "close": 100.0 + i * 0.01,
         "term_slope": 0.001 * i} for i in range(300)
    ]
    monkeypatch.setattr(e74, "_term_bars", lambda cap, bar_seconds=300.0: term_bars)
    td = _write_captures(_captures())
    report = e161.run_eval161(capture_dir=td, write=False)
    underlyings = {s["underlying"] for s in report["per_underlying"]}
    assert underlyings == {"BTC", "ETH"}
    for s in report["per_underlying"]:
        assert s["signal"] == "term_slope" if "signal" in s else True
        assert s["underlying"] in ("BTC", "ETH")
        assert isinstance(s["n_configs"], int)
        assert isinstance(s["best_ic"], float)
        assert isinstance(s["any_pass"], bool)


# 9) pooled BH-FDR key present and campaign_state set
def test_pooled_bh_fdr_and_campaign_state(monkeypatch):
    monkeypatch.setattr(e161, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e161, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e161, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e161, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e161, "_campaign_floor",
        lambda per_underlying: {"checks": {"underlyings_ok": True,
                                           "all_underlyings_ok": True}, "ok": True},
    )
    term_bars = [
        {"bar_open_ms": _BASE_MS + i * _BAR_MS, "close": 100.0 + i * 0.01,
         "term_slope": 0.001 * i} for i in range(300)
    ]
    monkeypatch.setattr(e74, "_term_bars", lambda cap, bar_seconds=300.0: term_bars)
    td = _write_captures(_captures())
    report = e161.run_eval161(capture_dir=td, write=False)
    assert "bh_fdr" in report["pooled"]
    assert "campaign_state" in report["pooled"]
    assert report["pooled"]["campaign_state"] in (
        "EVAL_161_SINGLE_ASSET_TERM_SLOPE_FORWARD_CVAR",
        "EVAL_161_BLOCKED_FLOOR",
    )
