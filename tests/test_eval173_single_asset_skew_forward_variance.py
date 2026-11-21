"""Unit tests for EVAL-173: single-asset skew -> forward realized return variance."""

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
import scripts.eval172_single_asset_atm_iv_forward_variance as e172
import scripts.eval173_single_asset_skew_forward_variance as e173

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000
_BASE_MS -= _BASE_MS % _BAR_MS


def _surface_bars(n: int = 300, seed: int = 0) -> list[dict]:
    rng = random.Random(seed)
    px = 60000.0
    bars = []
    for i in range(n):
        px *= 1.0 + rng.uniform(-0.002, 0.002)
        bars.append({
            "bar_open_ms": _BASE_MS + i * _BAR_MS,
            "close": px,
            "skew": 0.001 * i + rng.uniform(-0.01, 0.01),
        })
    return bars


def _captures() -> dict[str, dict]:
    return {
        "BTC": {
            "underlying": "BTC",
            "surface": {"snapshots": []},
            "option_trades": [],
            "perp_candles": [],
        },
        "ETH": {
            "underlying": "ETH",
            "surface": {"snapshots": []},
            "option_trades": [],
            "perp_candles": [],
        },
    }


def _write_captures(captures: dict[str, dict]) -> str:
    td = tempfile.mkdtemp()
    for inst, capture in captures.items():
        path = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
        path.write_text(json.dumps(capture))
    return td


def _patch_fast_inference(monkeypatch) -> None:
    monkeypatch.setattr(e172, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e172, "BOOTSTRAP_RESAMPLES", 50)


def _patch_bars(monkeypatch, bars: list[dict]) -> None:
    monkeypatch.setattr(
        e71,
        "build_surface_bars",
        lambda cap, bar_seconds=300.0, signal_window_seconds=900.0, atm_band=0.05: bars,
    )


def _patch_floor_ok(monkeypatch) -> None:
    monkeypatch.setattr(
        e173,
        "_campaign_floor",
        lambda per_underlying: {"checks": {}, "ok": True},
    )


def test_ids_are_eval173_skew_forward_variance():
    assert e173.REPORT_ID == "EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE_COMBINED"
    assert e173.PREREG_ID == "EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE_PREREGISTRATION"
    assert e173.BLOCKED_ID == "EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE_BLOCKED"
    assert e173.SURFACE_SIGNAL == "skew"
    assert e173.TARGET == "forward_variance"


def test_reuse_helpers():
    assert e173.e71 is e71
    assert e173.e65 is e65
    assert e173.e62 is e62
    assert e173.e61 is e61
    assert e173.e172 is e172
    assert e173._forward_return_variance is e172._forward_return_variance
    assert e173._eval_one_config is not e172._eval_one_config


def test_forward_return_variance_is_finite_and_nonnegative():
    rng = random.Random(173)
    bars = []
    px = 100.0
    for i in range(100):
        shock = 0.05 if i % 19 == 0 else rng.uniform(-0.003, 0.003)
        px *= 1.0 + shock
        bars.append({"close": px})
    values = e173._forward_return_variance(bars, 24)
    finite = [v for v in values if v is not None and math.isfinite(v)]
    assert len(finite) > 10
    assert all(v >= 0.0 for v in finite)


def test_eval_one_config_targets_skew_forward_variance(monkeypatch):
    _patch_fast_inference(monkeypatch)
    _patch_bars(monkeypatch, _surface_bars())
    a = e173._eval_one_config(_captures()["BTC"], bar_seconds=60.0, horizon_bars=6)
    b = e173._eval_one_config(_captures()["BTC"], bar_seconds=60.0, horizon_bars=6)
    assert a["underlying"] == "BTC"
    assert a["signal"] == "skew"
    assert a["target"] == "forward_variance"
    assert a["bar_seconds"] == 60.0
    assert a["horizon_bars"] == 6
    assert a["n_pairs"] >= e173.MIN_USABLE_PAIRS_PER_CONFIG
    assert -1.0 <= a["spearman_ic"] <= 1.0
    assert 0.0 <= a["permutation_p"] <= 1.0
    assert len(a["bootstrap_ci"]) == 3
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


def test_below_floor_blocks_not_nogo(monkeypatch):
    _patch_bars(monkeypatch, [])
    td = _write_captures(_captures())
    report = e173.run_eval173(capture_dir=td, write=False, task_label="TEST")
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"


def test_run_eval173_no_write_meets_floor_and_summarizes(monkeypatch):
    monkeypatch.setattr(e173, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e173, "FORWARD_HORIZONS_BARS", (6,))
    _patch_fast_inference(monkeypatch)
    _patch_floor_ok(monkeypatch)
    _patch_bars(monkeypatch, _surface_bars())
    td = _write_captures(_captures())
    report = e173.run_eval173(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert len(report["per_config"]) == 2
    assert report["protocol"]["target"] == "forward_variance"
    assert report["protocol"]["surface_signal"] == "skew"


def test_protocol_constants_reuse_eval71_and_eval172():
    protocol = e173.build_protocol("data/raw/eval61")
    assert protocol["surface_signal"] == "skew"
    assert protocol["target"] == "forward_variance"
    assert protocol["bar_seconds_grid"] == [60.0, 300.0]
    assert protocol["forward_horizons_bars"] == [6, 24, 72]
    assert protocol["signal_window_seconds"] == e71.SIGNAL_WINDOW_SECONDS
    assert protocol["atm_band"] == e71.ATM_BAND
    assert protocol["stats"]["seed"] == e62.SEED
    assert protocol["floor"]["min_underlyings"] == e71.FLOOR["min_underlyings"]


def test_campaign_floor_requires_both_underlyings():
    captures = _captures()
    floor = e173._campaign_floor({k: e71._underlying_surface_floor(v) for k, v in captures.items()})
    assert floor["ok"] is False
    one = e173._campaign_floor({"BTC": e71._underlying_surface_floor(captures["BTC"])})
    assert one["checks"]["underlyings_ok"] is False
    assert one["ok"] is False


def test_per_underlying_summary_pairing(monkeypatch):
    monkeypatch.setattr(e173, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e173, "FORWARD_HORIZONS_BARS", (6,))
    _patch_fast_inference(monkeypatch)
    _patch_floor_ok(monkeypatch)
    _patch_bars(monkeypatch, _surface_bars())
    td = _write_captures(_captures())
    report = e173.run_eval173(capture_dir=td, write=False)
    assert len(report["per_underlying"]) == 2
    assert {row["underlying"] for row in report["per_underlying"]} == {"BTC", "ETH"}
    for row in report["per_underlying"]:
        assert isinstance(row["n_configs"], int)
        assert isinstance(row["best_ic"], float)
        assert isinstance(row["any_pass"], bool)


def test_pooled_bh_fdr_and_campaign_state(monkeypatch):
    monkeypatch.setattr(e173, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e173, "FORWARD_HORIZONS_BARS", (6,))
    _patch_fast_inference(monkeypatch)
    _patch_floor_ok(monkeypatch)
    _patch_bars(monkeypatch, _surface_bars())
    td = _write_captures(_captures())
    report = e173.run_eval173(capture_dir=td, write=False)
    assert "bh_fdr" in report["pooled"]
    assert "campaign_state" in report["pooled"]
    assert report["pooled"]["campaign_state"] in (
        "EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE",
        "EVAL_173_BLOCKED_FLOOR",
    )