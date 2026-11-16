"""Unit tests for EVAL-67: BTC-only OOS replication of the suggestive EVAL-65
options order-flow toxicity -> realized-vol predictiveness slice
(tox/imbalance, bar60, horizon 72).

Copy-and-retarget of sealed EVAL-66: reuses EVAL-62 build_states and EVAL-64
feasible floor; BTC-only, 2 pre-registered configs, plus the EVAL-67 disjointness
gate against the sealed EVAL-64/65 BTC window
(2026-11-09T06:48:16Z..2026-11-16T06:48:16Z). Deterministic in-memory fixtures
only (no real data, no research_state writes, no network).
"""

from __future__ import annotations

import json
import math
import random
import tempfile
from pathlib import Path

import pytest

import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64
import scripts.eval65_orderflow_tox_rv_predictiveness as e65
import scripts.eval67_btc_oflow_tox_rv_oos as e67


def _craft_capture(n_bars=120, seed=0, inst="BTC", n_trades_per_bar=3,
                   n_of_instruments=150, signal_to_vol=0.0):
    rng = random.Random(seed)
    base_ms = 1_700_000_000_000
    bar_ms = 300_000
    px = 60000.0 if inst == "BTC" else 3000.0
    candles = []
    trades = []
    for i in range(n_bars):
        tox = rng.uniform(-1, 1)
        drift = tox * signal_to_vol + rng.uniform(-1, 1) * 1e-4
        px = max(1.0, px * (1 + drift))
        candles.append({"ts": base_ms + i * bar_ms, "open": px, "high": px,
                        "low": px, "close": px})
        sign = 1.0 if tox >= 0 else -1.0
        for _ in range(n_trades_per_bar):
            direction = "buy" if sign > 0 else "sell"
            opt = "call" if rng.random() < 0.5 else "put"
            strike = round(px + rng.randint(-2, 2) * 50, 2)
            amt = rng.uniform(0.1, 2.0)
            inst_name = f"{inst}-OPT-{i % max(1, n_of_instruments)}"
            trades.append({
                "ts": base_ms + i * bar_ms + rng.randint(1, bar_ms - 1),
                "instrument": inst_name,
                "direction": direction,
                "amount": amt,
                "price": 0.01,
                "index_price": px,
                "iv": 0.8,
                "option_type": opt,
                "strike": strike,
                "expiry": "2026-12-30T08:00:00Z",
            })

    snaps = []
    for i in range(n_bars):
        bar_ms_i = base_ms + i * bar_ms
        spot = candles[i]["close"]
        strike = round(spot, 2)
        mark = 0.1
        quotes = []
        for opt in ("call", "put"):
            quotes.append({
                "symbol": f"{inst}-OPT-{int(strike)}-{opt[0].upper()}-{i}",
                "underlying": inst,
                "strike": strike,
                "expiry": "2026-12-30T08:00:00Z",
                "option_type": opt,
                "bid": mark * 0.98,
                "ask": mark * 1.02,
                "mark": mark,
                "open_interest": 100.0,
                "volume": 10.0,
                "timestamp": "2023-11-14T00:00:00Z",
            })
        snaps.append({"bar_ms": bar_ms_i, "spot": spot, "quotes": quotes})

    return {
        "schema": "three_way_options_surface_orderflow_okx_perp_capture_v1",
        "underlying": inst,
        "venue": "deribit+okx",
        "window_start": "2023-11-14T00:00:00Z",
        "window_end": "2023-11-15T00:00:00Z",
        "surface": {"bar_seconds": 300, "resolution": "5", "snapshots": snaps},
        "option_trades": trades,
        "perp_candles": candles,
        "okx_inst_id": f"{inst}-USD-SWAP",
        "okx_perp_trades": [],
        "source": {"authenticated": False, "public_read_only": True, "venue": "deribit+okx"},
    }


def test_ids_are_eval67():
    assert e67.REPORT_ID == "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED"
    assert e67.PREREG_ID == "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION"
    assert e67.BLOCKED_ID == "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED"


def test_configs_restricted_to_suggestive_slice():
    assert e67.TOX_SIGNALS == ("tox", "imbalance")
    assert e67.GRID_BAR_SECONDS == (60.0,)
    assert e67.FORWARD_HORIZONS_BARS == (72,)
    assert e67.MIN_UNDERLYINGS == 1


def test_reuses_sealed_builders_and_floor():
    assert e67.e62.build_states is e62.build_states
    assert e67._underlying_floor_strict is e64._underlying_floor_strict
    assert e67.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e67.FDR_ALPHA == e65.FDR_ALPHA


def test_evaluate_predictiveness_runs_btc():
    cap = _craft_capture(n_bars=220, seed=1, inst="BTC", signal_to_vol=0.02)
    res = e67.evaluate_predictiveness(
        cap, tox_signal="tox", bar_seconds=60.0, horizon_bars=72
    )
    assert res["underlying"] == "BTC"
    assert res["n_pairs"] > 0
    assert "spearman_ic" in res and "permutation_p" in res and "pass" in res
    assert len(res["bootstrap_ci"]) == 3


def test_run_eval67_no_write_blocks_below_floor():
    cap = _craft_capture(n_bars=40, seed=7, inst="BTC")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "three_way_BTC_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
        report = e67.run_eval67(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e67.REPORT_ID


def test_run_eval67_refuses_to_seal_empty_capture_dir():
    with tempfile.TemporaryDirectory() as td:
        with pytest.raises(e67.NoRealCaptureError):
            e67.run_eval67(capture_dir=td, write=True)


def test_run_eval67_refuses_to_seal_dir_with_only_eth_capture():
    eth = _craft_capture(n_bars=1010, seed=8, inst="ETH")
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "three_way_ETH_20230101T000000Z.json").write_text(json.dumps(eth))
        with pytest.raises(e67.NoRealCaptureError):
            e67.run_eval67(capture_dir=td, write=True)


def test_run_eval67_filters_to_btc_only_and_counts_configs():
    btc = _craft_capture(n_bars=1010, seed=3, inst="BTC", n_trades_per_bar=2,
                         n_of_instruments=150, signal_to_vol=0.0)
    eth = _craft_capture(n_bars=1010, seed=4, inst="ETH", n_trades_per_bar=2,
                         n_of_instruments=150, signal_to_vol=0.0)
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "three_way_BTC_20230101T000000Z.json").write_text(json.dumps(btc))
        (Path(td) / "three_way_ETH_20230101T000000Z.json").write_text(json.dumps(eth))
        report = e67.run_eval67(capture_dir=td, write=False)
    assert report["underlyings"] == ["BTC"]
    # 2 signals * 1 bar grid * 1 horizon = 2 configs, BTC only
    assert len(report["per_config"]) == 2
    assert all(r["underlying"] == "BTC" for r in report["per_config"])


def test_run_eval67_meets_floor_for_single_btc():
    btc = _craft_capture(n_bars=1010, seed=5, inst="BTC", n_trades_per_bar=2,
                         n_of_instruments=150, signal_to_vol=0.0)
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "three_way_BTC_20230101T000000Z.json").write_text(json.dumps(btc))
        report = e67.run_eval67(capture_dir=td, write=False)
    assert report["per_underlying_floor"]["BTC"]["ok"] is True
    assert report["floor_ok"] is True
    assert report["verdict"] in ("NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    assert len(report["per_config"]) == 2


def test_check_disjointness_rejects_overlap():
    cap = _craft_capture(n_bars=1010, seed=6, inst="BTC")
    cap["window_start"] = "2026-11-10T00:00:00Z"
    cap["window_end"] = "2026-11-13T00:00:00Z"
    dj = e67.check_disjointness(cap)
    assert dj["ok"] is False
    assert dj["reason"] == "overlaps_sealed_btc_window"
    assert dj["overlap_seconds"] > 0


def test_check_disjointness_accepts_disjoint():
    cap = _craft_capture(n_bars=1010, seed=6, inst="BTC")
    cap["window_start"] = "2026-11-17T00:00:00Z"
    cap["window_end"] = "2026-11-20T12:00:00Z"
    dj = e67.check_disjointness(cap)
    assert dj["ok"] is True
    assert dj["overlap_seconds"] == 0.0
    assert dj["meets_min_span"] is True


def test_run_eval67_no_write_blocks_non_disjoint_even_if_floor_ok():
    btc = _craft_capture(n_bars=1010, seed=9, inst="BTC", n_trades_per_bar=2,
                         n_of_instruments=150, signal_to_vol=0.0)
    btc["window_start"] = "2026-11-10T00:00:00Z"
    btc["window_end"] = "2026-11-13T00:00:00Z"
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "three_way_BTC_20230101T000000Z.json").write_text(json.dumps(btc))
        report = e67.run_eval67(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["disjointness_ok"] is False
    assert report["floor_and_disjoint_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["pooled"]["campaign_state"] == "EVAL_67_BLOCKED_FLOOR_OR_DISJOINTNESS"

# ---------------------------------------------------------------------------
# EVAL-67 self-completing capture bridge (persistent, no-network unit tests)
# ---------------------------------------------------------------------------
import scripts.eval67_capture_bridge as bridge  # noqa: E402


def test_bridge_constants_and_task_id_parseable():
    assert bridge.THRESHOLD == "2026-11-20T00:00:00Z"
    assert bridge.CAPTURE_DIR == "data/raw/eval67"
    assert bridge.TASK_ID == (
        "INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION"
    )
    # The task id must carry a parseable ISO stamp for check_session_sealed.py.
    import re
    assert re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", bridge.TASK_ID)


def test_bridge_threshold_epoch_in_future_relative_to_sealed_window():
    # Threshold must be strictly after the sealed BTC window end.
    sealed_end = e67._parse_iso(e67.SEALED_BTC_WINDOW_END)
    assert bridge._threshold_epoch() > sealed_end.timestamp()


def test_bridge_refuses_before_threshold(monkeypatch):
    # Simulate now < threshold: main() must NOT run any acquisition step.
    monkeypatch.setattr(bridge, "_threshold_epoch", lambda: 1_000_000_000_000.0)
    monkeypatch.setattr(bridge.time, "time", lambda: 1_000_000_000_000.0 - 1.0)
    # If it ever reached the pipeline it would call _run_streaming; forbid that.
    def _boom(*a, **k):
        raise AssertionError("pipeline ran before threshold")
    monkeypatch.setattr(bridge, "_run_streaming", _boom)
    # Avoid an infinite wait loop: force the sleep to raise after first iteration.
    def _sleep(_s):
        raise SystemExit(0)
    monkeypatch.setattr(bridge.time, "sleep", _sleep)
    with pytest.raises(SystemExit):
        bridge.main()


def test_bridge_pipeline_order_and_completion_manifest(monkeypatch, tmp_path):
    # Force threshold already reached, capture dir under tmp.
    monkeypatch.setattr(bridge, "_threshold_epoch", lambda: 0.0)
    monkeypatch.setattr(bridge.time, "time", lambda: 10.0)
    monkeypatch.setattr(bridge, "LIVENESS_DIR", tmp_path)
    monkeypatch.setattr(bridge, "CAPTURE_DIR", str(tmp_path / "data/raw/eval67"))
    monkeypatch.setattr(bridge, "ROOT", tmp_path)

    calls = []

    def _fake_stream(pid, phase, cmd):
        calls.append((phase, cmd))
        # Every step succeeds.
        return 0, f"{phase}-ok"

    monkeypatch.setattr(bridge, "_run_streaming", _fake_stream)
    rc = bridge.main()
    assert rc == 0
    phases = [p for p, _ in calls]
    # Exact heavy-work order: acquire -> evaluate -> seal -> gate.
    assert phases == ["acquiring", "evaluating", "sealing", "gating"]

    # Completion manifest must exist and record COMPLETE + gate rc 0.
    manifests = list(tmp_path.glob("EVAL_67_BRIDGE_COMPLETE_*.json"))
    assert len(manifests) == 1
    data = json.loads(manifests[0].read_text())
    assert data["result"] == "COMPLETE"
    assert data["gate_rc"] == 0
    assert set(data["steps"]) == {"acquire", "dry_run", "seal", "gate"}
    assert all(v["rc"] == 0 for v in data["steps"].values())
    assert data["task_id"] == bridge.TASK_ID


def test_bridge_acquire_failure_short_circuits(monkeypatch, tmp_path):
    monkeypatch.setattr(bridge, "_threshold_epoch", lambda: 0.0)
    monkeypatch.setattr(bridge.time, "time", lambda: 10.0)
    monkeypatch.setattr(bridge, "LIVENESS_DIR", tmp_path)
    monkeypatch.setattr(bridge, "CAPTURE_DIR", str(tmp_path / "data/raw/eval67"))
    monkeypatch.setattr(bridge, "ROOT", tmp_path)

    calls = []

    def _fake_stream(pid, phase, cmd):
        calls.append(phase)
        if phase == "acquiring":
            return 7, "acquire-boom"
        return 0, "ok"

    monkeypatch.setattr(bridge, "_run_streaming", _fake_stream)
    rc = bridge.main()
    assert rc == 7
    # Must NOT proceed to evaluate/seal/gate after a failed acquisition.
    assert calls == ["acquiring"]
    data = json.loads(next(tmp_path.glob("EVAL_67_BRIDGE_COMPLETE_*.json")).read_text())
    assert data["result"] == "ACQUIRE_FAILED"
    assert data["steps"]["acquire"]["rc"] == 7


def test_bridge_gate_failure_marks_gate_failed(monkeypatch, tmp_path):
    monkeypatch.setattr(bridge, "_threshold_epoch", lambda: 0.0)
    monkeypatch.setattr(bridge.time, "time", lambda: 10.0)
    monkeypatch.setattr(bridge, "LIVENESS_DIR", tmp_path)
    monkeypatch.setattr(bridge, "CAPTURE_DIR", str(tmp_path / "data/raw/eval67"))
    monkeypatch.setattr(bridge, "ROOT", tmp_path)

    def _fake_stream(pid, phase, cmd):
        if phase == "gating":
            return 1, "gate-fail"
        return 0, "ok"

    monkeypatch.setattr(bridge, "_run_streaming", _fake_stream)
    rc = bridge.main()
    assert rc == 1
    data = json.loads(next(tmp_path.glob("EVAL_67_BRIDGE_COMPLETE_*.json")).read_text())
    assert data["result"] == "GATE_FAILED"
    assert data["gate_rc"] == 1
    assert data["seal_rc"] == 0
