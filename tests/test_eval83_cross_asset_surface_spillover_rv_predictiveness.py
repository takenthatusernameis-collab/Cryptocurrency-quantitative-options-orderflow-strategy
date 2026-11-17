"""Unit tests for EVAL-83: the **cross-asset options-surface lead-lag spillover ->
subsequent forward realized volatility** predictiveness.

EVAL-83 is the on-charter, runnable-now cell that EVAL-71/73 (own-asset surface ->
own RV) and EVAL-77 (contemporaneous basis -> RV spread) leave open: one crypto's
causal options surface vs the *other* crypto's *subsequent* forward RV. It reuses
the sealed EVAL-61/62/65/71 signal reconstructions and the EVAL-65 inference
verbatim, needs no new acquisition and no network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin the things the next session must not break:
1. the artifact ids are EVAL-83;
2. the sealed machinery (EVAL-61/62/65/71 helpers) is reused verbatim, not forked;
3. ``_asset_surface_series`` builds a causal per-bar surface z-series + forward RV
   keyed by bar-open timestamp, with ``fwd_rv is None`` on the incomplete tail;
4. ``_partial_spearman`` is the correct partial (0 when the control equals x;
   ~Spearman when the control is independent);
5. ``evaluate_spillover`` targets the *target* forward RV (not signed return), is
   causal/cross-asset, and its Spearman / partial IC inference is bounded and
   deterministic;
6. the composed floor ANDs the EVAL-71 surface floor and the cross-asset common-bar
   floor (neither weakened);
7. ``run_eval83(write=False)`` reports BLOCKED below the composed floor and a
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
import scripts.eval83_cross_asset_surface_spillover_rv_predictiveness as e83

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def _series(n, *, xs, ys):
    """Build a ``{bar_open_ms: {atm_iv_z, skew_z, fwd_rv}}`` series of length n.

    Both causal surface signals (``atm_iv_z`` and ``skew_z``) carry ``xs`` so a
    test on either signal exercises the same control; ``fwd_rv`` carries ``ys``
    (or ``None`` on the incomplete tail).
    """
    out = {}
    for i in range(n):
        out[_BASE_MS + i * _BAR_MS] = {
            "atm_iv_z": float(xs[i]),
            "skew_z": float(xs[i]),
            "fwd_rv": None if ys[i] is None else float(ys[i]),
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
def test_ids_are_eval83():
    assert e83.REPORT_ID.startswith("EVAL_83_")
    assert e83.PREREG_ID.startswith("EVAL_83_")
    assert e83.BLOCKED_ID.startswith("EVAL_83_")
    assert "SPILLOVER" in e83.REPORT_ID
    assert "CROSS_ASSET" in e83.REPORT_ID


# ---------------------------------------------------------------------------
# 2) sealed machinery reused verbatim
# ---------------------------------------------------------------------------
def test_reuses_sealed_machinery_verbatim():
    assert e83.e61 is e61
    assert e83.e62 is e62
    assert e83.e65 is e65
    assert e83.e71 is e71
    # EVAL-71 surface bars / forward RV / forward fill / floor — verbatim
    assert e83.e71.build_surface_bars is e71.build_surface_bars
    assert e83.e71._forward_rv is e71._forward_rv
    assert e83.e71._forward_fill is e71._forward_fill
    assert e83.e71._underlying_surface_floor is e71._underlying_surface_floor
    # EVAL-65 IC stats + EVAL-61 expanding z-score — verbatim
    assert e83.e65._perm_p_ic is e65._perm_p_ic
    assert e83.e65._boot_ci_ic is e65._boot_ci_ic
    assert e83.e61.expanding_zscore is e61.expanding_zscore
    # stats / grid constants match the sealed sources exactly
    assert e83.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e83.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e83.BOOTSTRAP_BLOCK == e65.BOOTSTRAP_BLOCK
    assert e83.SEED == e62.SEED
    assert e83.ZWINDOW == e62.ZWINDOW
    assert e83.FDR_ALPHA == e62.FDR_ALPHA
    assert e83.SIGNAL_WINDOW_SECONDS == e71.SIGNAL_WINDOW_SECONDS
    assert e83.ATM_BAND == e71.ATM_BAND


# ---------------------------------------------------------------------------
# 3) _asset_surface_series structure
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
                             "atm_iv": 0.5 + 0.001 * i, "skew": 0.01}
                            for i in range(n)
                        ])
    monkeypatch.setattr(e71, "_forward_rv",
                        lambda bars, h: [0.1] * (len(bars) - h))
    cap = {"underlying": "BTC", "perp_candles": candles, "option_trades": trades}
    out = e83._asset_surface_series(cap, bar_seconds=300.0, horizon_bars=6)
    assert len(out) == n
    assert min(out) == _BASE_MS
    tail_key = _BASE_MS + (n - 1) * _BAR_MS
    assert out[tail_key]["fwd_rv"] is None
    for v in out.values():
        assert set(v) == {"atm_iv_z", "skew_z", "fwd_rv"}


# ---------------------------------------------------------------------------
# 4) _partial_spearman correctness
# ---------------------------------------------------------------------------
def test_partial_spearman_zero_when_control_is_x():
    n = 60
    xs = [math.sin(i * 0.3) for i in range(n)]
    ys = [math.cos(i * 0.2) + 0.01 * i for i in range(n)]
    p = e83._partial_spearman(xs, ys, xs)  # control == x -> no residual x variance
    assert abs(p) < 1e-9


def test_partial_spearman_equals_spearman_with_independent_control():
    n = 200
    rng = random.Random(11)
    xs = [rng.gauss(0, 1) for _ in range(n)]
    ys = [x + rng.gauss(0, 0.5) for x in xs]  # strongly monotone in x
    cs = [rng.gauss(0, 1) for _ in range(n)]  # independent control
    p = e83._partial_spearman(xs, ys, cs)
    s = e65._spearman(xs, ys)
    assert abs(p - s) < 0.05
    assert p > 0.5


def test_partial_spearman_deterministic():
    n = 80
    xs = [math.sin(i * 0.1) for i in range(n)]
    ys = [x * 2 + 0.1 for x in xs]
    cs = [math.cos(i * 0.1) for i in range(n)]
    a = e83._partial_spearman(xs, ys, cs)
    b = e83._partial_spearman(xs, ys, cs)
    assert a == b


# ---------------------------------------------------------------------------
# 5) evaluate_spillover targets the TARGET forward RV, causal + cross-asset
# ---------------------------------------------------------------------------
def _patch_series(monkeypatch, series_map):
    monkeypatch.setattr(
        e83, "_asset_surface_series",
        lambda cap, **kw: series_map[cap["underlying"]],
    )


def test_evaluate_spillover_targets_forward_rv(monkeypatch):
    monkeypatch.setattr(e83, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e83, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(e83, "MIN_USABLE_PAIRS_PER_CONFIG", 8)
    n = 220
    xs = [float(i) for i in range(n)]
    ys = [float(i) for i in range(n)]  # target fwd_rv monotone in leader signal
    cs = [float((i * 7) % 13) for i in range(n)]  # non-degenerate own control
    series_map = {
        "BTC": _series(n, xs=xs, ys=[0.0] * n),
        "ETH": _series(n, xs=cs, ys=ys),
    }
    _patch_series(monkeypatch, series_map)
    res = e83.evaluate_spillover(
        {"underlying": "BTC"}, {"underlying": "ETH"},
        surface_signal="atm_iv", bar_seconds=300.0, horizon_bars=6,
    )
    assert res["leader"] == "BTC" and res["target"] == "ETH"
    assert res["target_type"] == "forward_rv"
    assert res["n_pairs"] == n
    assert res["spillover_ic"] > 0.99
    assert 0.0 <= res["permutation_p"] <= 1.0
    ci = res["bootstrap_ci"]
    assert len(ci) == 3 and ci[1] <= ci[0] <= ci[2]
    assert res["partial_spillover_ic"] > 0.0
    assert res["pass"] is True


def test_evaluate_spillover_works_for_skew_signal(monkeypatch):
    monkeypatch.setattr(e83, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e83, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(e83, "MIN_USABLE_PAIRS_PER_CONFIG", 8)
    n = 220
    xs = [float(i) for i in range(n)]
    ys = [float(i) for i in range(n)]
    cs = [float((i * 5) % 11) for i in range(n)]
    series_map = {
        # leader = ETH carries the signal; target = BTC carries forward RV + control
        "ETH": _series(n, xs=xs, ys=[0.0] * n),
        "BTC": _series(n, xs=cs, ys=ys),
    }
    _patch_series(monkeypatch, series_map)
    res = e83.evaluate_spillover(
        {"underlying": "ETH"}, {"underlying": "BTC"},
        surface_signal="skew", bar_seconds=60.0, horizon_bars=24,
    )
    assert res["leader"] == "ETH" and res["target"] == "BTC"
    assert res["spillover_ic"] > 0.99
    assert res["bar_seconds"] == 60.0
    assert res["horizon_bars"] == 24


def test_evaluate_spillover_deterministic(monkeypatch):
    monkeypatch.setattr(e83, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e83, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(e83, "MIN_USABLE_PAIRS_PER_CONFIG", 8)
    n = 120
    rng = random.Random(3)
    xs = [rng.gauss(0, 1) for _ in range(n)]
    ys = [x + rng.gauss(0, 0.3) for x in xs]
    cs = [rng.gauss(0, 1) for _ in range(n)]
    series_map = {
        "BTC": _series(n, xs=xs, ys=[0.0] * n),
        "ETH": _series(n, xs=cs, ys=ys),
    }
    _patch_series(monkeypatch, series_map)
    a = e83.evaluate_spillover(
        {"underlying": "BTC"}, {"underlying": "ETH"},
        surface_signal="atm_iv", bar_seconds=300.0, horizon_bars=6,
    )
    b = e83.evaluate_spillover(
        {"underlying": "BTC"}, {"underlying": "ETH"},
        surface_signal="atm_iv", bar_seconds=300.0, horizon_bars=6,
    )
    assert a["spillover_ic"] == b["spillover_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


def test_evaluate_spillover_insufficient_pairs(monkeypatch):
    series_map = {
        "BTC": _series(5, xs=[0.0] * 5, ys=[0.0] * 5),
        "ETH": _series(5, xs=[0.0] * 5, ys=[0.0] * 5),
    }
    _patch_series(monkeypatch, series_map)
    res = e83.evaluate_spillover(
        {"underlying": "BTC"}, {"underlying": "ETH"},
        surface_signal="atm_iv", bar_seconds=300.0, horizon_bars=6,
    )
    assert res["n_pairs"] < 8
    assert res["pass"] is False
    assert "error" in res


# ---------------------------------------------------------------------------
# 6) composed floor (surface AND cross-asset common-bar)
# ---------------------------------------------------------------------------
def test_campaign_floor_composes_both_floors(monkeypatch):
    monkeypatch.setattr(e71, "_underlying_surface_floor",
                        lambda cap: {"ok": True, "n_option_trades": 100})
    monkeypatch.setattr(
        e83, "_asset_surface_series",
        lambda cap, **kw: {i: {"atm_iv_z": 0.0, "skew_z": 0.0, "fwd_rv": None}
                           for i in range(300)},
    )
    fl = e83.campaign_floor(_captures())
    assert fl["ok"] is True
    assert fl["checks"]["all_underlyings_ok"] is True
    assert fl["checks"]["all_pairs_overlap_ok"] is True
    for u in fl["per_pair"].values():
        assert u["ok"] is True
        assert u["n_common_bars"] == 300


def test_campaign_floor_blocks_below_overlap(monkeypatch):
    monkeypatch.setattr(e71, "_underlying_surface_floor",
                        lambda cap: {"ok": True, "n_option_trades": 100})
    monkeypatch.setattr(
        e83, "_asset_surface_series",
        lambda cap, **kw: {i: {"atm_iv_z": 0.0, "skew_z": 0.0, "fwd_rv": None}
                           for i in range(300 if cap["underlying"] == "BTC" else 10)},
    )
    fl = e83.campaign_floor(_captures())
    assert fl["ok"] is False
    assert fl["checks"]["all_pairs_overlap_ok"] is False


def test_campaign_floor_blocks_when_surface_fails(monkeypatch):
    monkeypatch.setattr(
        e71, "_underlying_surface_floor",
        lambda cap: {"ok": cap.get("underlying") == "BTC", "n_option_trades": 100},
    )
    monkeypatch.setattr(
        e83, "_asset_surface_series",
        lambda cap, **kw: {i: {"atm_iv_z": 0.0, "skew_z": 0.0, "fwd_rv": None}
                           for i in range(300)},
    )
    assert e83.campaign_floor(_captures())["ok"] is False


def test_campaign_floor_blocks_short_capture():
    caps = {"BTC": {"underlying": "BTC", "surface": {"snapshots": []},
                    "option_trades": [], "perp_candles": []}}
    fl = e83.campaign_floor(caps)
    assert fl["ok"] is False


# ---------------------------------------------------------------------------
# 7) orchestration (write=False; no research_state writes)
# ---------------------------------------------------------------------------
def test_run_eval83_no_write_blocks_below_floor():
    td = _write_captures(_captures())
    report = e83.run_eval83(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e83.REPORT_ID


def test_run_eval83_no_write_go_when_all_targets_pass(monkeypatch):
    monkeypatch.setattr(e83, "SURFACE_SIGNALS", ("atm_iv",))
    monkeypatch.setattr(e83, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e83, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e83, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e83, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e83, "campaign_floor",
        lambda captures: {"underlyings": sorted(captures), "ok": True,
                          "per_underlying": {i: {"ok": True} for i in captures},
                          "per_pair": {f"{a}->{b}": {"ok": True}
                                       for a in captures for b in captures if a != b},
                          "checks": {"all_underlyings_ok": True,
                                     "all_pairs_overlap_ok": True}},
    )

    def fake_eval(leader_cap, target_cap, *, surface_signal, bar_seconds, horizon_bars):
        return {
            "leader": leader_cap["underlying"], "target": target_cap["underlying"],
            "signal": surface_signal, "target_type": "forward_rv",
            "bar_seconds": bar_seconds, "horizon_bars": horizon_bars,
            "n_pairs": 200, "n_common_bars": 250,
            "spillover_ic": 0.3, "partial_spillover_ic": 0.25, "own_ic": 0.2,
            "permutation_p": 0.001, "bootstrap_ci": [0.3, 0.1, 0.5], "pass": True,
        }

    monkeypatch.setattr(e83, "evaluate_spillover", fake_eval)
    td = _write_captures(_captures())
    report = e83.run_eval83(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] == "GO CONFIRMED"
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    # 2 ordered pairs x 1 signal x 1 grid x 1 horizon = 2 configs
    assert len(report["per_config"]) == 2
    assert all(t["any_incoming_pass"] for t in report["per_target"])


def test_run_eval83_no_write_nogo_when_not_all_targets_pass(monkeypatch):
    monkeypatch.setattr(e83, "SURFACE_SIGNALS", ("atm_iv",))
    monkeypatch.setattr(e83, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e83, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e83, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e83, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e83, "campaign_floor",
        lambda captures: {"underlyings": sorted(captures), "ok": True,
                          "per_underlying": {i: {"ok": True} for i in captures},
                          "per_pair": {f"{a}->{b}": {"ok": True}
                                       for a in captures for b in captures if a != b},
                          "checks": {"all_underlyings_ok": True,
                                     "all_pairs_overlap_ok": True}},
    )

    def fake_eval(leader_cap, target_cap, *, surface_signal, bar_seconds, horizon_bars):
        passing = leader_cap["underlying"] == "BTC"
        return {
            "leader": leader_cap["underlying"], "target": target_cap["underlying"],
            "signal": surface_signal, "target_type": "forward_rv",
            "bar_seconds": bar_seconds, "horizon_bars": horizon_bars,
            "n_pairs": 200, "n_common_bars": 250,
            "spillover_ic": 0.3 if passing else -0.05,
            "partial_spillover_ic": 0.25 if passing else -0.02,
            "own_ic": 0.2,
            "permutation_p": 0.001 if passing else 0.6,
            "bootstrap_ci": [0.3, 0.1, 0.5] if passing else [-0.1, -0.2, 0.0],
            "pass": passing,
        }

    monkeypatch.setattr(e83, "evaluate_spillover", fake_eval)
    td = _write_captures(_captures())
    report = e83.run_eval83(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] == "NO-GO CONFIRMED (PASS)"
    assert report["pooled"]["any_pair_pass"] is True
    assert report["pooled"]["all_targets_pass"] is False


# ---------------------------------------------------------------------------
# 8) protocol / floor constants
# ---------------------------------------------------------------------------
def test_protocol_and_floor_constants():
    p = e83.build_protocol("data/raw/eval61")
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_common_bars_per_pair"] == 150
    assert p["floor"]["min_usable_pairs_per_config"] == e83.MIN_USABLE_PAIRS_PER_CONFIG
    assert p["surface_signals"] == ["atm_iv", "skew"]
    assert p["target"] == "forward_rv"
    assert p["bar_seconds_grid"] == [60.0, 300.0]
    assert p["forward_horizons_bars"] == [6, 24, 72]
    assert "EVAL-71" in p["extends"]
    assert "EVAL-77" in p["extends"]
    assert "EVAL-71" in p["floor"]["note"]
    assert "cross-asset" in p["title"].lower()
    assert "spillover" in p["title"].lower()
    assert "target" in p["target_detail"].lower()