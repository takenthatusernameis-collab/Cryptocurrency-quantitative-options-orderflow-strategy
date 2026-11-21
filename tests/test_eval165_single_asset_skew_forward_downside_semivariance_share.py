"""Unit tests for EVAL-165: the **causal near-ATM implied-vol skew -> subsequent
forward downside-semivariance share** predictiveness.

EVAL-165 is the on-charter, runnable-now campaign that fills the ``skew`` cell
of the single-asset surface downside-semivariance-share grid (only ``atm_iv``
EVAL-115 was sealed). It reuses the sealed EVAL-61/62/65/71 signal
reconstructions and the EVAL-65 inference verbatim, needs no new acquisition and
no network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin the things the next session must not break:
1. the artifact ids are EVAL-165;
2. the sealed machinery (EVAL-61/62/65/71 helpers) is reused verbatim, not forked;
3. ``_forward_downside_semivariance_share`` is causal (target strictly after
   bar k) and is None on degenerate / zero-variance windows;
4. ``_asset_surface_series`` builds a causal per-bar skew z-series + forward
   downside-semivariance share keyed by bar-open timestamp;
5. ``evaluate_config`` targets the *same underlying's* forward downside-semivariance
   share, is causal/own-asset, and its Spearman / permutation / bootstrap
   inference is bounded and deterministic;
6. the composed floor ANDs the EVAL-71 surface floor (not weakened);
7. ``run_eval165(write=False)`` reports BLOCKED below the composed floor and a
   verdict above it;
8. the protocol/floor constants are the pre-registered ones.
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
import scripts.eval165_single_asset_skew_forward_downside_semivariance_share as e165

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def _series(n, *, signal_zs, fwd):
    """Build a ``{bar_open_ms: {skew_z, fwd_downside_share}}`` series of length n."""
    out = {}
    for i in range(n):
        out[_BASE_MS + i * _BAR_MS] = {
            "skew_z": float(signal_zs[i]),
            "fwd_downside_share": None if fwd[i] is None else float(fwd[i]),
        }
    return out


def _captures(insts=("BTC", "ETH")):
    return {
        i: {"underlying": i, "surface": {"snapshots": []},
            "option_trades": [], "perp_candles": []}
        for i in insts
    }


def _write_captures(caps):
    td = tempfile.mkdtemp()
    for inst, cap in caps.items():
        p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
    return td


# ---------------------------------------------------------------------------
# 1) artifact ids
# ---------------------------------------------------------------------------
def test_ids_are_eval165():
    assert e165.REPORT_ID.startswith("EVAL_165_")
    assert e165.PREREG_ID.startswith("EVAL_165_")
    assert e165.BLOCKED_ID.startswith("EVAL_165_")
    assert "DOWNSIDE_SEMIVARIANCE_SHARE" in e165.REPORT_ID
    assert "SINGLE_ASSET_SKEW" in e165.REPORT_ID
    assert e165.SURFACE_SIGNAL == "skew"
    assert e165.TARGET == "forward_downside_semivariance_share"


# ---------------------------------------------------------------------------
# 2) sealed machinery reused verbatim
# ---------------------------------------------------------------------------
def test_reuses_sealed_machinery_verbatim():
    assert e165.e61 is e61
    assert e165.e62 is e62
    assert e165.e65 is e65
    assert e165.e71 is e71
    # EVAL-71 surface bars / forward fill / floor — verbatim
    assert e165.e71.build_surface_bars is e71.build_surface_bars
    assert e165.e71._forward_fill is e71._forward_fill
    assert e165.e71._underlying_surface_floor is e71._underlying_surface_floor
    # EVAL-65 IC stats + EVAL-61 expanding z-score — verbatim
    assert e165.e65._perm_p_ic is e65._perm_p_ic
    assert e165.e65._boot_ci_ic is e65._boot_ci_ic
    assert e165.e61.expanding_zscore is e61.expanding_zscore
    # stats / grid constants match the sealed sources exactly
    assert e165.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e165.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e165.BOOTSTRAP_BLOCK == e65.BOOTSTRAP_BLOCK
    assert e165.SEED == e62.SEED
    assert e165.ZWINDOW == e62.ZWINDOW
    assert e165.FDR_ALPHA == e62.FDR_ALPHA
    assert e165.SIGNAL_WINDOW_SECONDS == e71.SIGNAL_WINDOW_SECONDS
    assert e165.ATM_BAND == e71.ATM_BAND


# ---------------------------------------------------------------------------
# 3) _forward_downside_semivariance_share structure (causal, None on degenerate)
# ---------------------------------------------------------------------------
def test_downside_share_structure():
    n = 40
    closes = [100.0 + 0.1 * i + (0.05 * (i % 5)) for i in range(n)]
    bars = [{"bar_open_ms": _BASE_MS + i * _BAR_MS, "close": closes[i]} for i in range(n)]
    out = e165._forward_downside_semivariance_share(bars, horizon_bars=6)
    # length is max(0, len(lr) - horizon_bars + 1) where lr has n-1 returns
    assert len(out) == max(0, (n - 1) - 6 + 1)
    assert all(v is None or isinstance(v, float) for v in out)


def test_downside_share_causal_target_strictly_after_k():
    # downside share for decision k uses returns[k..k+H-1], never close[k] itself
    closes = [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0]
    bars = [{"bar_open_ms": _BASE_MS + i * _BAR_MS, "close": c} for i, c in enumerate(closes)]
    out = e165._forward_downside_semivariance_share(bars, horizon_bars=3)
    assert len(out) == len(closes) - 3
    assert out[0] is not None


def test_downside_share_zero_variance_yields_none():
    # all returns equal -> total variance = 0 -> None
    closes = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0]
    bars = [{"bar_open_ms": _BASE_MS + i * _BAR_MS, "close": c} for i, c in enumerate(closes)]
    out = e165._forward_downside_semivariance_share(bars, horizon_bars=3)
    assert len(out) == len(closes) - 3
    assert all(v is None for v in out)


def test_downside_share_in_range():
    # share should be in [0, 1] when defined
    rng = random.Random(7)
    closes = [100.0]
    for i in range(60):
        closes.append(closes[-1] * (1.0 + rng.gauss(0, 0.01)))
    bars = [{"bar_open_ms": _BASE_MS + i * _BAR_MS, "close": c} for i, c in enumerate(closes)]
    out = e165._forward_downside_semivariance_share(bars, horizon_bars=10)
    defined = [v for v in out if v is not None]
    assert len(defined) > 0
    assert all(0.0 <= v <= 1.0 for v in defined)


# ---------------------------------------------------------------------------
# 4) _asset_surface_series structure
# ---------------------------------------------------------------------------
def test_asset_surface_series_structure(monkeypatch):
    n = 30
    closes = [100.0 + i for i in range(n)]
    candles = [{"ts": _BASE_MS + i * _BAR_MS, "close": closes[i]} for i in range(n)]
    trades = [
        {"ts": _BASE_MS + i * _BAR_MS, "instrument": "BTC-27NOV26-100-C",
         "iv": 0.5 + 0.001 * i, "amount": 1.0, "index_price": 100.0}
        for i in range(n)
    ]
    monkeypatch.setattr(e71, "build_surface_bars",
                        lambda cap, **kw: [
                            {"bar_open_ms": _BASE_MS + i * _BAR_MS, "close": closes[i],
                             "atm_iv": 0.5 + 0.001 * i, "skew": 0.01 * i}
                            for i in range(n)
                        ])
    monkeypatch.setattr(e165, "_forward_downside_semivariance_share",
                        lambda bars, h: [0.2] * max(0, (len(bars) - 1) - h + 1))
    cap = {"underlying": "BTC", "perp_candles": candles, "option_trades": trades}
    out = e165._asset_surface_series(cap, bar_seconds=300.0, horizon_bars=6)
    assert len(out) == n
    assert min(out) == _BASE_MS
    tail_key = _BASE_MS + (n - 1) * _BAR_MS
    assert out[tail_key]["fwd_downside_share"] is None
    for v in out.values():
        assert set(v) == {"skew_z", "skew", "fwd_downside_share"}


# ---------------------------------------------------------------------------
# 5) evaluate_config targets the same underlying's forward downside-semivariance share
# ---------------------------------------------------------------------------
def _patch_series(monkeypatch, series_map):
    monkeypatch.setattr(
        e165, "_asset_surface_series",
        lambda cap, **kw: series_map[cap["underlying"]],
    )


def test_evaluate_config_targets_downside_share(monkeypatch):
    monkeypatch.setattr(e165, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e165, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(e165, "MIN_USABLE_PAIRS_PER_CONFIG", 8)
    n = 220
    xs = [float(i) for i in range(n)]
    ys = [float(i) / float(n) for i in range(n)]  # downside share monotone in skew
    series_map = {
        "BTC": _series(n, signal_zs=xs, fwd=ys),
        "ETH": _series(n, signal_zs=[0.0] * n, fwd=[0.0] * n),
    }
    _patch_series(monkeypatch, series_map)
    res = e165.evaluate_config(
        {"underlying": "BTC"},
        surface_signal="skew", bar_seconds=300.0, horizon_bars=6,
    )
    assert res["underlying"] == "BTC"
    assert res["target"] == "forward_downside_semivariance_share"
    assert res["signal"] == "skew"
    assert res["n_pairs"] == n
    assert res["spearman_ic"] > 0.99
    assert 0.0 <= res["permutation_p"] <= 1.0
    ci = res["bootstrap_ci"]
    assert len(ci) == 3 and ci[1] <= ci[0] <= ci[2]
    assert res["pass"] is True


def test_evaluate_config_works_for_60s_grid(monkeypatch):
    monkeypatch.setattr(e165, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e165, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(e165, "MIN_USABLE_PAIRS_PER_CONFIG", 8)
    n = 150
    xs = [float(i) for i in range(n)]
    ys = [float(i) / float(n) for i in range(n)]
    series_map = {
        "ETH": _series(n, signal_zs=xs, fwd=ys),
    }
    _patch_series(monkeypatch, series_map)
    res = e165.evaluate_config(
        {"underlying": "ETH"},
        surface_signal="skew", bar_seconds=60.0, horizon_bars=24,
    )
    assert res["underlying"] == "ETH"
    assert res["bar_seconds"] == 60.0
    assert res["horizon_bars"] == 24
    assert res["spearman_ic"] > 0.99


def test_evaluate_config_deterministic(monkeypatch):
    monkeypatch.setattr(e165, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e165, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(e165, "MIN_USABLE_PAIRS_PER_CONFIG", 8)
    n = 120
    rng = random.Random(3)
    xs = [rng.gauss(0, 1) for _ in range(n)]
    ys = [max(0.0, x + rng.gauss(0, 0.3)) / 2.0 for x in xs]
    series_map = {
        "BTC": _series(n, signal_zs=xs, fwd=ys),
    }
    _patch_series(monkeypatch, series_map)
    a = e165.evaluate_config(
        {"underlying": "BTC"}, surface_signal="skew", bar_seconds=300.0, horizon_bars=6,
    )
    b = e165.evaluate_config(
        {"underlying": "BTC"}, surface_signal="skew", bar_seconds=300.0, horizon_bars=6,
    )
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


def test_evaluate_config_insufficient_pairs(monkeypatch):
    series_map = {
        "BTC": _series(5, signal_zs=[0.0] * 5, fwd=[0.0] * 5),
    }
    _patch_series(monkeypatch, series_map)
    res = e165.evaluate_config(
        {"underlying": "BTC"}, surface_signal="skew", bar_seconds=300.0, horizon_bars=6,
    )
    assert res["n_pairs"] < 8
    assert res["pass"] is False
    assert "error" not in res
    assert res["reason"] == "insufficient_pairs"


# ---------------------------------------------------------------------------
# 6) composed floor (EVAL-71 surface floor)
# ---------------------------------------------------------------------------
def test_campaign_floor_composes_surface_floor(monkeypatch):
    fl = e165._campaign_floor({"BTC": {"ok": True}, "ETH": {"ok": True}})
    assert fl["ok"] is True
    assert fl["checks"]["all_underlyings_ok"] is True


def test_campaign_floor_blocks_below_surface_floor():
    fl = e165._campaign_floor({"BTC": {"ok": True}})
    assert fl["ok"] is False


def test_campaign_floor_blocks_empty():
    assert e165._campaign_floor({})["ok"] is False


# ---------------------------------------------------------------------------
# 7) orchestration (write=False; no research_state writes)
# ---------------------------------------------------------------------------
def test_run_eval165_no_write_blocks_below_floor():
    td = _write_captures(_captures())
    report = e165.run_eval165(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e165.REPORT_ID


def test_run_eval165_no_write_go_when_all_underlyings_pass(monkeypatch):
    monkeypatch.setattr(e165, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e165, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e165, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e165, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e165, "_campaign_floor",
        lambda per_underlying: {"checks": {"underlyings_ok": True,
                                           "all_underlyings_ok": True}, "ok": True},
    )

    def fake_eval(cap, *, surface_signal, bar_seconds, horizon_bars):
        return {
            "underlying": cap["underlying"], "signal": surface_signal,
            "target": "forward_downside_semivariance_share", "bar_seconds": bar_seconds,
            "horizon_bars": horizon_bars, "n_pairs": 200,
            "spearman_ic": 0.3, "permutation_p": 0.001,
            "bootstrap_ci": [0.3, 0.1, 0.5], "pass": True, "reason": "ok",
        }

    monkeypatch.setattr(e165, "evaluate_config", fake_eval)
    td = _write_captures(_captures())
    report = e165.run_eval165(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] == "GO CONFIRMED"
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    # 2 underlyings x 1 signal x 1 grid x 1 horizon = 2 configs
    assert len(report["per_config"]) == 2
    assert all(s["any_pass"] for s in report["per_underlying"])


def test_run_eval165_no_write_nogo_when_not_all_underlyings_pass(monkeypatch):
    monkeypatch.setattr(e165, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e165, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e165, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e165, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e165, "_campaign_floor",
        lambda per_underlying: {"checks": {"underlyings_ok": True,
                                           "all_underlyings_ok": True}, "ok": True},
    )

    def fake_eval(cap, *, surface_signal, bar_seconds, horizon_bars):
        passing = cap["underlying"] == "BTC"
        return {
            "underlying": cap["underlying"], "signal": surface_signal,
            "target": "forward_downside_semivariance_share", "bar_seconds": bar_seconds,
            "horizon_bars": horizon_bars, "n_pairs": 200,
            "spearman_ic": 0.3 if passing else -0.05,
            "permutation_p": 0.001 if passing else 0.6,
            "bootstrap_ci": [0.3, 0.1, 0.5] if passing else [-0.1, -0.2, 0.0],
            "pass": passing, "reason": "ok" if passing else "gate_fail",
        }

    monkeypatch.setattr(e165, "evaluate_config", fake_eval)
    td = _write_captures(_captures())
    report = e165.run_eval165(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] == "NO-GO CONFIRMED (PASS)"
    assert report["pooled"]["all_underlyings_pass"] is False


# ---------------------------------------------------------------------------
# 8) protocol / floor constants
# ---------------------------------------------------------------------------
def test_protocol_and_floor_constants():
    p = e165.build_protocol("data/raw/eval61")
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_usable_pairs_per_config"] == e165.MIN_USABLE_PAIRS_PER_CONFIG
    assert p["surface_signals"] == ["skew"]
    assert p["target"] == "forward_downside_semivariance_share"
    assert p["bar_seconds_grid"] == [60.0, 300.0]
    assert p["forward_horizons_bars"] == [6, 24, 72]
    assert "EVAL-71" in p["extends"]
    assert "EVAL-115" in p["extends"]
    assert "downside" in p["target_detail"].lower()
    assert "downside" in p["title"].lower()


# ---------------------------------------------------------------------------
# 9) _forward_downside_semivariance_share is finite on dispersed increments
# ---------------------------------------------------------------------------
def test_forward_downside_share_matches_manual(monkeypatch):
    closes = [100.0, 101.0, 99.0, 102.0, 98.0, 103.0, 97.0, 104.0]
    bars = [{"close": c} for c in closes]
    got = e165._forward_downside_semivariance_share(bars, 3)
    lr = [math.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)]
    assert len(got) == len(lr) - 3 + 1
    for k, g in enumerate(got):
        seg = lr[k:k + 3]
        mu = sum(seg) / len(seg)
        m2 = sum((v - mu) ** 2 for v in seg) / len(seg)
        expected = (sum(min(v - mu, 0.0) ** 2 for v in seg) / len(seg)) / m2
        assert g is not None and abs(g - expected) < 1e-15