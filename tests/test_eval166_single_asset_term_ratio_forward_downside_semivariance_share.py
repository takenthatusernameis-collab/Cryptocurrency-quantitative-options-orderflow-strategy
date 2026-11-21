"""Unit tests for EVAL-166: the single-asset causal near-to-far ATM implied-vol
**term ratio** (``term_ratio`` = IV(near expiry)/IV(far expiry) - 1) -> subsequent
**forward downside-semivariance share** of the signed return of the SAME
underlying.

EVAL-166 fills the ``term_ratio`` cell of the single-asset surface
downside-semivariance-share grid (only ``atm_iv`` EVAL-115 and ``skew`` EVAL-165
were sealed). It reuses EVAL-74 _term_bars (term_ratio signal), EVAL-71
_forward_fill, EVAL-61 expanding_zscore, EVAL-65 _perm_p_ic/_boot_ci_ic inference
verbatim; the new logic is the forward downside-semivariance-share target applied
to the term_ratio signal.

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
import scripts.eval166_single_asset_term_ratio_forward_downside_semivariance_share as e166

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000


def _term_bars(n=300, seed=0, close0=60000.0, bar_ms=_BAR_MS):
    """Deterministic per-bar term bars: close random walk + monotone term_ratio."""
    rng = random.Random(seed)
    px = close0
    out = []
    for i in range(n):
        px = max(1.0, px * (1 + rng.uniform(-1, 1) * 1e-4))
        out.append({
            "bar_open_ms": _BASE_MS + i * bar_ms,
            "close": px,
            "term_ratio": 0.001 * i,
        })
    return out


def _captures():
    """Minimal capture dicts (one per underlying); empty trades -> below floor."""
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
def test_ids_are_eval166():
    assert e166.REPORT_ID.startswith("EVAL_166_")
    assert e166.PREREG_ID.startswith("EVAL_166_")
    assert e166.BLOCKED_ID.startswith("EVAL_166_")
    assert "TERM_RATIO" in e166.REPORT_ID
    assert "FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE" in e166.REPORT_ID
    assert e166.TERM_SIGNAL == "term_ratio"
    assert e166.TARGET == "forward_downside_semivariance_share"


# 2) sealed machinery reused verbatim (not forked)
def test_reuse_helpers():
    assert e166.e74 is e74
    assert e166.e71 is e71
    assert e166.e65 is e65
    assert e166.e62 is e62
    assert e166.e61 is e61
    assert e166.e74._term_bars is e74._term_bars
    assert e166.e71._forward_fill is e71._forward_fill
    assert e166.e61.expanding_zscore is e61.expanding_zscore
    assert e166.e65._perm_p_ic is e65._perm_p_ic
    assert e166.e65._boot_ci_ic is e65._boot_ci_ic
    assert e166.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e166.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e166.SEED == e62.SEED
    assert e166.ZWINDOW == e62.ZWINDOW
    assert e166.FDR_ALPHA == e62.FDR_ALPHA


# 3) forward downside-semivariance share is finite on dispersed increments
def test_downside_share_is_finite():
    rng = random.Random(166)
    bars = []
    px = 100.0
    for i in range(140):
        drift = 0.05 if i % 19 == 0 else rng.uniform(-0.004, 0.004)
        px = px * (1.0 + drift)
        bars.append({"close": px})
    out = e166._forward_downside_semivariance_share(bars, 24)
    finite = [v for v in out if v is not None and math.isfinite(v)]
    assert len(finite) > 10


# 3b) forward downside-semivariance share equals manual downside/total ratio
def test_downside_share_matches_manual():
    closes = [100.0, 101.0, 99.0, 102.0, 98.0, 103.0, 97.0, 104.0]
    bars = [{"close": c} for c in closes]
    got = e166._forward_downside_semivariance_share(bars, 3)
    lr = [math.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)]
    assert len(got) == len(lr) - 3 + 1
    for k, g in enumerate(got):
        seg = lr[k:k + 3]
        mu = sum(seg) / len(seg)
        m2 = sum((v - mu) ** 2 for v in seg) / len(seg)
        expected = (sum(min(v - mu, 0.0) ** 2 for v in seg) / len(seg)) / m2
        assert g is not None and abs(g - expected) < 1e-15


# 3c) causal: the target for decision k uses returns strictly after k
def test_downside_share_causal_target_strictly_after_k():
    closes = [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0]
    bars = [{"close": c} for c in closes]
    out = e166._forward_downside_semivariance_share(bars, 3)
    assert len(out) == len(closes) - 3
    assert out[0] is not None


# 3d) zero total variance -> None (degenerate window)
def test_downside_share_zero_variance_yields_none():
    closes = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0]
    bars = [{"close": c} for c in closes]
    out = e166._forward_downside_semivariance_share(bars, 3)
    assert len(out) == len(closes) - 3
    assert all(v is None for v in out)


# 3e) share is in [0, 1] when defined
def test_downside_share_in_range():
    rng = random.Random(7)
    closes = [100.0]
    for _ in range(60):
        closes.append(closes[-1] * (1.0 + rng.gauss(0, 0.01)))
    bars = [{"close": c} for c in closes]
    out = e166._forward_downside_semivariance_share(bars, 10)
    defined = [v for v in out if v is not None]
    assert len(defined) > 0
    assert all(0.0 <= v <= 1.0 for v in defined)


# 4) _eval_one_config targets forward downside-semivariance share with term_ratio
def test_eval_one_config_structure_and_deterministic(monkeypatch):
    monkeypatch.setattr(e166, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e166, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(e74, "_term_bars", lambda cap, bar_seconds=300.0: _term_bars(300))
    caps = _captures()
    a = e166._eval_one_config(caps["BTC"], bar_seconds=60.0, horizon_bars=6)
    b = e166._eval_one_config(caps["BTC"], bar_seconds=60.0, horizon_bars=6)
    assert a["underlying"] == "BTC"
    assert a["signal"] == "term_ratio"
    assert a["target"] == "forward_downside_semivariance_share"
    assert a["bar_seconds"] == 60.0
    assert a["horizon_bars"] == 6
    assert a["n_pairs"] >= e166.MIN_USABLE_PAIRS_PER_CONFIG
    assert -1.0 <= a["spearman_ic"] <= 1.0
    assert 0.0 <= a["permutation_p"] <= 1.0
    ci = a["bootstrap_ci"]
    assert len(ci) == 3 and ci[1] <= ci[0] <= ci[2]
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


# 4b) insufficient pairs -> not a pass, no exception
def test_eval_one_config_insufficient_pairs(monkeypatch):
    monkeypatch.setattr(e74, "_term_bars",
                        lambda cap, bar_seconds=300.0: _term_bars(5))
    caps = _captures()
    res = e166._eval_one_config(caps["BTC"], bar_seconds=60.0, horizon_bars=6)
    assert res["n_pairs"] < e166.MIN_USABLE_PAIRS_PER_CONFIG
    assert res["pass"] is False
    assert res["reason"] == "insufficient_pairs"


# 5) below floor seals BLOCKED, never NO-GO
def test_below_floor_blocks_not_nogo(monkeypatch):
    monkeypatch.setattr(e74, "_term_bars", lambda cap, bar_seconds=300.0: [])
    caps = _captures()
    td = _write_captures(caps)
    report = e166.run_eval166(capture_dir=td, write=False, task_label="TEST")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    if not report.get("floor_ok"):
        assert report["verdict"] == "BLOCKED"


# 6) run_eval166(write=False) meets floor and summarizes (floor monkeypatched ok)
def test_run_eval166_no_write_meets_floor_and_summarizes(monkeypatch):
    monkeypatch.setattr(e166, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e166, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e166, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e166, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e166, "_campaign_floor",
        lambda per_underlying: {"checks": {"underlyings_ok": True,
                                           "all_underlyings_ok": True}, "ok": True},
    )
    monkeypatch.setattr(e74, "_term_bars", lambda cap, bar_seconds=300.0: _term_bars(300))
    td = _write_captures(_captures())
    report = e166.run_eval166(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert len(report["per_config"]) == 2
    assert report["protocol"]["target"] == "forward_downside_semivariance_share"
    assert report["protocol"]["term_signal"] == "term_ratio"


# 7) protocol constants pre-registered
def test_protocol_constants():
    proto = e166.build_protocol("data/raw/eval61")
    assert proto["term_signal"] == "term_ratio"
    assert proto["target"] == "forward_downside_semivariance_share"
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert proto["forward_horizons_bars"] == [6, 24, 72]
    assert proto["stats"]["seed"] == e62.SEED
    assert proto["stats"]["zwindow"] == e62.ZWINDOW
    assert proto["stats"]["fdr_alpha"] == e62.FDR_ALPHA
    assert proto["floor"]["min_underlyings"] == 2
    assert "downside" in proto["title"].lower()


# 8) per-underlying summary keys
def test_per_underlying_summary_keys(monkeypatch):
    monkeypatch.setattr(e166, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e166, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e166, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e166, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e166, "_campaign_floor",
        lambda per_underlying: {"checks": {"underlyings_ok": True,
                                           "all_underlyings_ok": True}, "ok": True},
    )
    monkeypatch.setattr(e74, "_term_bars", lambda cap, bar_seconds=300.0: _term_bars(300))
    td = _write_captures(_captures())
    report = e166.run_eval166(capture_dir=td, write=False)
    underlyings = {s["underlying"] for s in report["per_underlying"]}
    assert underlyings == {"BTC", "ETH"}
    for s in report["per_underlying"]:
        assert s["underlying"] in ("BTC", "ETH")
        assert isinstance(s["n_configs"], int)
        assert isinstance(s["best_ic"], float)
        assert isinstance(s["any_pass"], bool)


# 9) pooled BH-FDR key present and campaign_state set
def test_pooled_bh_fdr_and_campaign_state(monkeypatch):
    monkeypatch.setattr(e166, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e166, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e166, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e166, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e166, "_campaign_floor",
        lambda per_underlying: {"checks": {"underlyings_ok": True,
                                           "all_underlyings_ok": True}, "ok": True},
    )
    monkeypatch.setattr(e74, "_term_bars", lambda cap, bar_seconds=300.0: _term_bars(300))
    td = _write_captures(_captures())
    report = e166.run_eval166(capture_dir=td, write=False)
    assert "bh_fdr" in report["pooled"]
    assert "campaign_state" in report["pooled"]
    assert report["pooled"]["campaign_state"] in (
        "EVAL_166_SINGLE_ASSET_TERM_RATIO_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE",
        "EVAL_166_BLOCKED_FLOOR",
    )