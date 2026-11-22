"""Unit tests for EVAL-186 TRACK A fresh-window replication and its gate.

Deterministic in-memory fixtures only. No real data, network, or research_state
writes are used by these tests.
"""

from __future__ import annotations

import json
from pathlib import Path

import scripts.eval61_orderflow_realized_vol_net_of_cost as e61
import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64
import scripts.eval67_btc_oflow_tox_rv_oos as e67
import scripts.eval69_pooled_btc_eth_oflow_tox_rv_traded_oos as e69
import scripts.eval184_surface_traded_netofcost_oos as e184
import scripts.eval186_phaseb_gate as gate
import scripts.eval186_track_a_fresh_window_replication as e186

FORWARD_START = "2026-11-22T07:12:00Z"
FORWARD_END = "2026-11-25T23:58:00Z"


def _cap(inst: str = "BTC", start: str = FORWARD_START, end: str = FORWARD_END):
    return {
        "underlying": inst,
        "window_start": start,
        "window_end": end,
        "surface": {"snapshots": []},
        "option_trades": [],
        "perp_candles": [],
    }


def _floor_ok(cap):
    return {
        "underlying": cap.get("underlying", "?"),
        "ok": True,
        "checks": {k: True for k in e186.build_protocol("x")["floor"]["checks"]},
        "n_surface_snapshots": 1000,
        "n_surface_instruments": 100,
        "n_surface_bars_5m": 1000,
        "n_option_trades": 2000,
        "n_of_instruments": 150,
        "of_span_seconds": 82000.0,
        "n_of_bars_5m": 240,
        "n_perp_candles": 1000,
        "perp_span_seconds": 300000.0,
        "n_perp_bars_5m": 1000,
        "n_common_bars_5m": 240,
    }


def _family_report(
    *,
    report_id: str,
    verdict: str,
    power: bool = True,
    floor: bool = True,
    max_returns: int = 2000,
):
    return {
        "report_id": report_id,
        "verdict": verdict,
        "floor_ok": floor,
        "disjointness_ok": floor,
        "floor_and_disjoint_ok": floor,
        "missing_underlyings": [],
        "pooled": {
            "max_pooled_returns": max_returns,
            "power_adequate": power,
            "min_pooled_returns": e186.MIN_POOLED_RETURNS,
            "pass_configs": ["fake::config"] if verdict == "GO CONFIRMED" else [],
            "bh_fdr": {"rejected": ["fake::config"] if verdict == "GO CONFIRMED" else []},
        },
        "per_config": [],
        "errors": [],
    }


def _patch_common(monkeypatch, *, floor_ok=True, forward_ok=True):
    caps = [_cap("BTC"), _cap("ETH", start=FORWARD_START, end=FORWARD_END)]
    monkeypatch.setattr(e186, "_select_captures", lambda _dir: caps)
    monkeypatch.setattr(e186, "_floor_summary", _floor_ok)
    if not forward_ok:
        monkeypatch.setattr(
            e186,
            "check_forward_disjointness",
            lambda cap: {"underlying": cap["underlying"], "ok": False, "reason": "test"},
        )
    return caps


def test_ids_match_gate_and_runner():
    assert e186.REPORT_ID == "EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_COMBINED"
    assert e186.PREREG_ID == "EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_PREREGISTRATION"
    assert e186.BLOCKED_ID == "EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_BLOCKED"
    assert e186.PREREG_GLOB == gate.PREREG_GLOB
    assert e186.COMBINED_GLOB == gate.COMBINED_GLOB
    assert e186.BLOCKED_GLOB == gate.BLOCKED_GLOB
    assert e186.DEFAULT_TASK_LABEL == gate.TASK_LABEL
    assert gate.TASK_ID == "INIT-2026-11-22T09:51:17Z-EVAL186-TRACK-A-FRESH-WINDOW-REPLICATION"


def test_reuses_sealed_family_runners_and_floor():
    assert e186.e69 is e69
    assert e186.e184 is e184
    assert e186.e64 is e64
    assert e186.e67 is e67
    assert e186.e61 is e61
    assert e186.e62 is e62
    assert e186._underlying_floor_strict is e64._underlying_floor_strict


def test_capture_schedule_is_strictly_forward_not_overlapping():
    assert e186.PREVIOUS_WINDOW_END == "2026-11-22T06:46:43Z"
    assert e186.earliest_forward_capture_end() == "2026-11-25T23:34:43Z"
    assert e186.RECOMMENDED_CAPTURE_END == "2026-11-26T00:00:00Z"
    assert gate.RECOMMENDED_CAPTURE_START == "2026-11-22T07:12:00Z"
    assert gate.RECOMMENDED_CAPTURE_START > gate.PREVIOUS_WINDOW_END
    assert gate.RECOMMENDED_CAPTURE_END > gate.EARLIEST_FORWARD_CAPTURE_END


def test_forward_disjointness_accepts_recommended_window():
    row = e186.check_forward_disjointness(_cap())
    assert row["ok"] is True
    assert row["reason"] == "strictly_forward_disjoint"
    assert row["previous_overlap_seconds"] == 0.0
    assert row["sealed_overlap_seconds"] == 0.0
    assert row["starts_after_previous"] is True
    assert row["meets_min_span"] is True


def test_forward_disjointness_rejects_eval84_overlap():
    cap = _cap(start="2026-11-18T13:58:43Z", end="2026-11-22T06:46:43Z")
    row = e186.check_forward_disjointness(cap)
    assert row["ok"] is False
    assert row["reason"] == "overlaps_eval84_eval185_window"
    assert row["previous_overlap_seconds"] > 0.0


def test_forward_disjointness_rejects_reversed_and_sealed_windows():
    reversed_row = e186.check_forward_disjointness(
        _cap(start="2026-11-20T00:00:00Z", end="2026-11-19T00:00:00Z")
    )
    assert reversed_row["ok"] is False
    sealed_row = e186.check_forward_disjointness(
        _cap(start="2026-11-10T00:00:00Z", end="2026-11-13T00:00:00Z")
    )
    assert sealed_row["ok"] is False
    assert sealed_row["reason"] == "overlaps_sealed_eval64_window"


def test_forward_disjointness_rejects_short_and_missing_windows():
    short = e186.check_forward_disjointness(
        _cap(start="2026-11-22T07:12:00Z", end="2026-11-22T08:12:00Z")
    )
    assert short["ok"] is False
    assert short["reason"] == "below_minimum_capture_span"
    missing = e186.check_forward_disjointness({"underlying": "BTC"})
    assert missing["ok"] is False
    assert missing["reason"] == "missing_capture_window"


def test_no_write_empty_capture_is_blocked_without_family_calls(monkeypatch):
    def fail(*_args, **_kwargs):
        raise AssertionError("family runner must not run without a real capture")

    monkeypatch.setattr(e186.e69, "run_eval69", fail)
    monkeypatch.setattr(e186.e184, "run_eval184", fail)
    report = e186.run_eval186(capture_dir="/tmp/does-not-exist", write=False)
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e186.REPORT_ID
    assert report["families"]["order_flow"]["verdict"] == "BLOCKED"


def test_non_forward_capture_blocks_without_family_calls(monkeypatch):
    caps = [
        _cap("BTC", start="2026-11-18T13:58:43Z", end="2026-11-22T06:46:43Z"),
        _cap("ETH", start="2026-11-18T13:58:43Z", end="2026-11-22T06:46:43Z"),
    ]
    monkeypatch.setattr(e186, "_select_captures", lambda _dir: caps)
    monkeypatch.setattr(e186, "_floor_summary", _floor_ok)

    def fail(*_args, **_kwargs):
        raise AssertionError("family runner must not run on an overlapping capture")

    monkeypatch.setattr(e186.e69, "run_eval69", fail)
    monkeypatch.setattr(e186.e184, "run_eval184", fail)
    report = e186.run_eval186(capture_dir="unused", write=False)
    assert report["verdict"] == "BLOCKED"
    assert report["forward_disjointness_ok"] is False


def test_composition_dual_no_go(monkeypatch):
    _patch_common(monkeypatch)
    monkeypatch.setattr(
        e186.e69,
        "run_eval69",
        lambda **_kwargs: _family_report(
            report_id=e69.REPORT_ID, verdict="NO-GO CONFIRMED (PASS)"
        ),
    )
    monkeypatch.setattr(
        e186.e184,
        "run_eval184",
        lambda **_kwargs: _family_report(
            report_id=e184.REPORT_ID, verdict="NO-GO CONFIRMED (PASS)"
        ),
    )
    report = e186.run_eval186(capture_dir="unused", write=False)
    assert report["verdict"] == "NO-GO CONFIRMED (PASS)"
    assert report["pooled"]["go_families"] == []
    assert report["pooled"]["power_adequate"] is True


def test_either_family_go_refutes_dual_no_go(monkeypatch):
    _patch_common(monkeypatch)
    monkeypatch.setattr(
        e186.e69,
        "run_eval69",
        lambda **_kwargs: _family_report(
            report_id=e69.REPORT_ID, verdict="NO-GO CONFIRMED (PASS)"
        ),
    )
    monkeypatch.setattr(
        e186.e184,
        "run_eval184",
        lambda **_kwargs: _family_report(
            report_id=e184.REPORT_ID, verdict="GO CONFIRMED"
        ),
    )
    report = e186.run_eval186(capture_dir="unused", write=False)
    assert report["verdict"] == "GO CONFIRMED"
    assert report["pooled"]["go_families"] == ["surface"]


def test_no_go_requires_both_families_power_adequate(monkeypatch):
    _patch_common(monkeypatch)
    monkeypatch.setattr(
        e186.e69,
        "run_eval69",
        lambda **_kwargs: _family_report(
            report_id=e69.REPORT_ID, verdict="NO-GO CONFIRMED (PASS)"
        ),
    )
    monkeypatch.setattr(
        e186.e184,
        "run_eval184",
        lambda **_kwargs: _family_report(
            report_id=e184.REPORT_ID, verdict="NO-GO CONFIRMED (PASS)", power=False
        ),
    )
    report = e186.run_eval186(capture_dir="unused", write=False)
    assert report["verdict"] == "INCONCLUSIVE (UNDERPOWERED)"


def test_family_blocked_produces_combined_blocked(monkeypatch):
    _patch_common(monkeypatch)
    monkeypatch.setattr(
        e186.e69,
        "run_eval69",
        lambda **_kwargs: _family_report(
            report_id=e69.REPORT_ID, verdict="BLOCKED", floor=False
        ),
    )
    monkeypatch.setattr(
        e186.e184,
        "run_eval184",
        lambda **_kwargs: _family_report(
            report_id=e184.REPORT_ID, verdict="NO-GO CONFIRMED (PASS)"
        ),
    )
    report = e186.run_eval186(capture_dir="unused", write=False)
    assert report["verdict"] == "BLOCKED"


def test_seal_selects_blocked_artifact_for_non_forward_capture(monkeypatch, tmp_path):
    caps = [_cap("BTC"), _cap("ETH")]
    monkeypatch.setattr(e186, "_select_captures", lambda _dir: caps)
    monkeypatch.setattr(e186, "_floor_summary", _floor_ok)
    monkeypatch.setattr(e186, "check_forward_disjointness", lambda cap: {
        "underlying": cap["underlying"],
        "ok": False,
        "reason": "test",
        "checks": {},
        "capture_window": [None, None],
        "previous_overlap_seconds": 1.0,
        "sealed_overlap_seconds": 0.0,
    })
    monkeypatch.setattr(e186, "_has_real_capture", lambda _dir: True)
    monkeypatch.setattr(e186, "OUT_DIR", tmp_path)
    sealed = []
    monkeypatch.setattr(
        e186.e62,
        "_seal",
        lambda report_id, payload, _builder: sealed.append((report_id, payload)),
    )
    report = e186.run_eval186(capture_dir="unused", write=True)
    assert report["verdict"] == "BLOCKED"
    assert [name for name, _payload in sealed] == [e186.PREREG_ID, e186.BLOCKED_ID]


def test_seal_selects_combined_artifact_for_no_go(monkeypatch, tmp_path):
    _patch_common(monkeypatch)
    monkeypatch.setattr(
        e186.e69,
        "run_eval69",
        lambda **_kwargs: _family_report(
            report_id=e69.REPORT_ID, verdict="NO-GO CONFIRMED (PASS)"
        ),
    )
    monkeypatch.setattr(
        e186.e184,
        "run_eval184",
        lambda **_kwargs: _family_report(
            report_id=e184.REPORT_ID, verdict="NO-GO CONFIRMED (PASS)"
        ),
    )
    monkeypatch.setattr(e186, "_has_real_capture", lambda _dir: True)
    monkeypatch.setattr(e186, "OUT_DIR", tmp_path)
    sealed = []
    monkeypatch.setattr(
        e186.e62,
        "_seal",
        lambda report_id, payload, _builder: sealed.append((report_id, payload)),
    )
    e186.run_eval186(capture_dir="unused", write=True)
    assert [name for name, _payload in sealed] == [e186.PREREG_ID, e186.REPORT_ID]


def test_gate_detect_seal_respects_task_floor(tmp_path):
    old = tmp_path / "EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_COMBINED_20261122T095000Z.json"
    old.write_text("{}")
    assert gate.detect_seal(tmp_path)["sealed"] is False
    new = tmp_path / "EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_COMBINED_20261122T100000Z.json"
    new.write_text("{}")
    detected = gate.detect_seal(tmp_path)
    assert detected["sealed"] is True
    assert detected["floor_stamp"] == "20261122T095117Z"


def test_gate_decide_phase_precedence():
    assert gate.decide_phase(sealed=True, capture_present=False, runner_green=False) == "SEALED"
    assert gate.decide_phase(sealed=False, capture_present=False, runner_green=True) == "WAIT_CAPTURE"
    assert gate.decide_phase(sealed=False, capture_present=True, runner_green=False) == "WAIT_RUNNER"
    assert gate.decide_phase(sealed=False, capture_present=True, runner_green=True) == "DUE"


def test_gate_capture_inventory(tmp_path):
    empty = gate.capture_inventory(tmp_path)
    assert empty["present"] is False
    (tmp_path / "three_way_BTC_20261126T000000Z.json").write_text("{}")
    only_btc = gate.capture_inventory(tmp_path)
    assert only_btc["present"] is False
    (tmp_path / "three_way_ETH_20261126T000000Z.json").write_text("{}")
    both = gate.capture_inventory(tmp_path)
    assert both["present"] is True
    assert len(both["btc"]) == 1 and len(both["eth"]) == 1


def test_gate_main_wait_capture(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(gate, "runner_present_and_green", lambda **_kwargs: {
        "runner_present": True,
        "runner_green": False,
        "returncode": 1,
        "tail": "test",
    })
    rc = gate.main(["--capture-dir", str(tmp_path), "--research-state-dir", str(tmp_path)])
    payload = json.loads(capsys.readouterr().out)
    assert rc == gate.EXIT_WAIT_CAPTURE
    assert payload["phase"] == "WAIT_CAPTURE"
    assert payload["readiness"]["acquisition_command"][-1] == "--seal"


def test_gate_main_due_without_execute(monkeypatch, tmp_path, capsys):
    (tmp_path / "three_way_BTC_20261126T000000Z.json").write_text("{}")
    (tmp_path / "three_way_ETH_20261126T000000Z.json").write_text("{}")
    monkeypatch.setattr(gate, "runner_present_and_green", lambda **_kwargs: {
        "runner_present": True,
        "runner_green": True,
        "returncode": 0,
        "tail": "ok",
    })
    rc = gate.main(["--capture-dir", str(tmp_path), "--research-state-dir", str(tmp_path)])
    payload = json.loads(capsys.readouterr().out)
    assert rc == gate.EXIT_DUE
    assert payload["phase"] == "DUE"


def test_gate_main_sealed_is_idempotent(monkeypatch, tmp_path, capsys):
    artifact = tmp_path / "EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_COMBINED_20261122T100000Z.json"
    artifact.write_text("{}")
    monkeypatch.setattr(gate, "run_seal_gate_check", lambda **_kwargs: (0, "ok"))

    def fail(**_kwargs):
        raise AssertionError("sealed gate must skip runner")

    monkeypatch.setattr(gate, "runner_present_and_green", fail)
    rc = gate.main(["--capture-dir", str(tmp_path), "--research-state-dir", str(tmp_path)])
    payload = json.loads(capsys.readouterr().out)
    assert rc == gate.EXIT_SEALED
    assert payload["phase"] == "SEALED"
    assert payload["seal_gate_rc"] == 0


def test_gate_execute_missing_capture_is_not_sealed(tmp_path):
    result = gate.execute_phaseb(capture_dir=tmp_path, research_state_dir=tmp_path)
    assert result["ok"] is False
    assert result["step"] == "capture"
    assert list(tmp_path.glob("EVAL_186_*")) == []


def test_no_stale_eval184_or_eval185_task_labels():
    assert e186.DEFAULT_TASK_LABEL == "EVAL186-TRACK-A-FRESH-WINDOW-REPLICATION"
    assert "EVAL184" not in e186.DEFAULT_TASK_LABEL
    assert "EVAL185" not in e186.DEFAULT_TASK_LABEL