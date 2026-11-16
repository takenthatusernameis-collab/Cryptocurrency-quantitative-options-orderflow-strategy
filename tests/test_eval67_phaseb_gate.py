"""Unit tests for the EVAL-67 Phase-B gate (scripts/eval67_phaseb_gate.py).

The gate is the deterministic, idempotent arbiter of the EVAL-67 completion
contract. These tests pin its four outcomes (SEALED / NOT_DUE / DUE / FAILED),
its seal detection (stamps >= the pre-registered task floor, stale artifacts
excluded), its disjointness math, and its refusal to acquire before the
threshold. Deterministic in-memory fixtures only: no real data, no network, no
research_state writes (all filesystem access is redirected to tmp_path).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

import scripts.eval67_phaseb_gate as gate


# ---------------------------------------------------------------------------
# Constants / identifiers
# ---------------------------------------------------------------------------
def test_task_id_is_parseable_and_stable():
    floor = gate.task_floor_stamp(gate.TASK_ID)
    assert floor == "20261116T132540Z"
    assert gate.TASK_LABEL == "EVAL67-BTC-OFLOW-TOX-RV-OOS"
    assert gate.THRESHOLD_ISO == "2026-11-20T00:00:00Z"


def test_exit_codes_are_distinct():
    codes = {gate.EXIT_SEALED, gate.EXIT_FAILED, gate.EXIT_NOT_DUE, gate.EXIT_DUE}
    assert codes == {0, 1, 10, 20}


def test_threshold_is_after_earliest_disjoint_end():
    assert gate.parse_iso(gate.THRESHOLD_ISO) >= gate.parse_iso(
        gate.EARLIEST_DISJOINT_CAPTURE_END
    )


# ---------------------------------------------------------------------------
# decide_phase
# ---------------------------------------------------------------------------
def test_decide_phase_sealed_wins():
    now = datetime(2026, 11, 20, 0, 0, 1, tzinfo=timezone.utc)
    thr = gate.parse_iso(gate.THRESHOLD_ISO)
    assert gate.decide_phase(now, thr, True) == "SEALED"


def test_decide_phase_not_due_before_threshold():
    now = datetime(2026, 11, 16, 15, 0, 0, tzinfo=timezone.utc)
    thr = gate.parse_iso(gate.THRESHOLD_ISO)
    assert gate.decide_phase(now, thr, False) == "NOT_DUE"


def test_decide_phase_due_at_threshold():
    thr = gate.parse_iso(gate.THRESHOLD_ISO)
    assert gate.decide_phase(thr, thr, False) == "DUE"
    after = datetime(2026, 11, 21, 0, 0, 0, tzinfo=timezone.utc)
    assert gate.decide_phase(after, thr, False) == "DUE"


# ---------------------------------------------------------------------------
# detect_seal (mirrors check_session_sealed.py stamp semantics)
# ---------------------------------------------------------------------------
def test_detect_seal_true_when_combined_after_floor(tmp_path):
    (tmp_path / "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_20261120T000000Z.json").write_text("{}")
    d = gate.detect_seal(tmp_path)
    assert d["sealed"] is True
    assert any(a["kind"] == "COMBINED" for a in d["artifacts"])


def test_detect_seal_true_when_blocked_after_floor(tmp_path):
    (tmp_path / "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_20261120T000000Z.md").write_text("x")
    d = gate.detect_seal(tmp_path)
    assert d["sealed"] is True
    assert any(a["kind"] == "BLOCKED" for a in d["artifacts"])


def test_detect_seal_false_when_only_prereg(tmp_path):
    (tmp_path / "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261120T000000Z.json").write_text("{}")
    d = gate.detect_seal(tmp_path)
    assert d["sealed"] is False
    assert d["artifacts"] == []


def test_detect_seal_excludes_stale_artifact_below_floor(tmp_path):
    # stamp 2026-01-01 is before the task floor 2026-11-16T13:25:40Z
    (tmp_path / "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_20260101T000000Z.json").write_text("{}")
    d = gate.detect_seal(tmp_path)
    assert d["sealed"] is False


def test_detect_seal_false_on_missing_dir(tmp_path):
    d = gate.detect_seal(tmp_path / "does_not_exist")
    assert d["sealed"] is False
    assert d["artifacts"] == []


# ---------------------------------------------------------------------------
# disjointness_math
# ---------------------------------------------------------------------------
def test_disjointness_overlaps_now():
    now = datetime(2026, 11, 16, 15, 0, 0, tzinfo=timezone.utc)
    dm = gate.disjointness_math(now)
    assert dm["disjoint"] is False
    assert dm["overlap_seconds"] > 0.0
    assert dm["span_seconds"] == pytest.approx(3.7 * 86400.0)


def test_disjointness_clean_at_threshold():
    now = gate.parse_iso("2026-11-20T00:00:00Z")
    dm = gate.disjointness_math(now)
    assert dm["disjoint"] is True
    assert dm["overlap_seconds"] == 0.0
    assert dm["meets_min_span"] is True


def test_disjointness_span_meets_floor_at_threshold():
    now = gate.parse_iso(gate.THRESHOLD_ISO)
    dm = gate.disjointness_math(now)
    assert dm["span_seconds"] >= 300000.0
    assert dm["meets_min_span"] is True


# ---------------------------------------------------------------------------
# execute_phaseb refuses before threshold (no subprocess calls)
# ---------------------------------------------------------------------------
def test_execute_refuses_before_threshold(monkeypatch):
    # Freeze "now" before the threshold and fail loudly if any subprocess runs.
    monkeypatch.setattr(gate, "now_iso", lambda: "2026-11-16T15:00:00Z")

    def _boom(*a, **k):  # pragma: no cover - must not be called
        raise AssertionError("execute_phaseb must not shell out before threshold")

    monkeypatch.setattr(gate.subprocess, "run", _boom)
    # Patch datetime inside execute_phaseb via threshold comparison path.
    real_dt = gate.datetime

    class _FrozenDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(2026, 11, 16, 15, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(gate, "datetime", _FrozenDT)
    res = gate.execute_phaseb()
    assert res["ok"] is False
    assert res["step"] == "threshold"
    assert res["reason"] == "before_threshold"
    assert res["disjointness"]["disjoint"] is False


# ---------------------------------------------------------------------------
# execute_phaseb happy path: acquire skipped -> dry-run -> seal -> seal-gate OK
# ---------------------------------------------------------------------------
def test_execute_runs_pipeline_and_requires_seal_gate(monkeypatch, tmp_path):
    real_dt = gate.datetime

    class _FrozenDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(2026, 11, 20, 1, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(gate, "datetime", _FrozenDT)

    cap = tmp_path / "data/raw/eval67"
    cap.mkdir(parents=True)
    (cap / "three_way_BTC_20261120T005959Z.json").write_text("{}")

    calls = []

    def _fake_run(cmd, cwd=None):
        calls.append(list(cmd))
        joined = " ".join(str(c) for c in cmd)

        class _P:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return 0, "ok: " + joined

    monkeypatch.setattr(gate, "_run", _fake_run)
    monkeypatch.setattr(gate, "run_seal_gate_check", lambda **k: (0, "OK: sealed"))

    res = gate.execute_phaseb(capture_dir=cap, research_state_dir=tmp_path)
    assert res["ok"] is True
    assert res["step"] == "seal_gate"
    steps = {s["step"]: s for s in res["steps"]}
    # capture already exists -> acquire skipped
    assert steps["acquire"]["status"] == "skipped"
    assert steps["dry_run"]["status"] == "ok"
    assert steps["seal"]["status"] == "ok"
    assert steps["seal_gate"]["status"] == "ok"


def test_execute_fails_when_seal_gate_fails(monkeypatch, tmp_path):
    real_dt = gate.datetime

    class _FrozenDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(2026, 11, 20, 1, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(gate, "datetime", _FrozenDT)

    cap = tmp_path / "data/raw/eval67"
    cap.mkdir(parents=True)
    (cap / "three_way_BTC_20261120T005959Z.json").write_text("{}")

    monkeypatch.setattr(gate, "_run", lambda cmd, cwd=None: (0, "ok"))
    monkeypatch.setattr(gate, "run_seal_gate_check", lambda **k: (1, "FAIL: not sealed"))

    res = gate.execute_phaseb(capture_dir=cap, research_state_dir=tmp_path)
    assert res["ok"] is False
    assert res["step"] == "seal_gate"
    assert res["seal_gate_rc"] == 1


def test_execute_fails_when_dry_run_fails(monkeypatch, tmp_path):
    real_dt = gate.datetime

    class _FrozenDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(2026, 11, 20, 1, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(gate, "datetime", _FrozenDT)

    cap = tmp_path / "data/raw/eval67"
    cap.mkdir(parents=True)
    (cap / "three_way_BTC_20261120T005959Z.json").write_text("{}")

    # acquire skipped (capture exists); dry-run fails
    monkeypatch.setattr(gate, "_run", lambda cmd, cwd=None: (1, "boom"))
    monkeypatch.setattr(gate, "run_seal_gate_check", lambda **k: (0, "OK"))

    res = gate.execute_phaseb(capture_dir=cap, research_state_dir=tmp_path)
    assert res["ok"] is False
    assert res["step"] == "dry_run"


def test_execute_acquires_when_no_capture(monkeypatch, tmp_path):
    real_dt = gate.datetime

    class _FrozenDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(2026, 11, 20, 1, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(gate, "datetime", _FrozenDT)

    cap = tmp_path / "data/raw/eval67"  # does not exist yet
    monkeypatch.setattr(gate, "_run", lambda cmd, cwd=None: (0, "ok"))
    monkeypatch.setattr(gate, "run_seal_gate_check", lambda **k: (0, "OK"))

    res = gate.execute_phaseb(capture_dir=cap, research_state_dir=tmp_path)
    assert res["ok"] is True
    steps = {s["step"]: s for s in res["steps"]}
    assert steps["acquire"]["status"] == "ok"
    assert cap.is_dir()  # gate created the capture dir before acquiring


# ---------------------------------------------------------------------------
# main() maps phases to exit codes (status-only paths; no subprocess)
# ---------------------------------------------------------------------------
def test_main_not_due_exit_code(monkeypatch, tmp_path, capsys):
    real_dt = gate.datetime

    class _FrozenDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(2026, 11, 16, 15, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(gate, "datetime", _FrozenDT)
    monkeypatch.setattr(gate, "RS_DIR", tmp_path)

    rc = gate.main(["--research-state-dir", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert rc == gate.EXIT_NOT_DUE
    assert out["phase"] == "NOT_DUE"
    assert "CORRECT CARRY" in out["contract"]


def test_main_due_without_execute_exit_code(monkeypatch, tmp_path, capsys):
    real_dt = gate.datetime

    class _FrozenDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(2026, 11, 20, 1, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(gate, "datetime", _FrozenDT)
    monkeypatch.setattr(gate, "RS_DIR", tmp_path)

    rc = gate.main(["--research-state-dir", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert rc == gate.EXIT_DUE
    assert out["phase"] == "DUE"
    assert "HEAVY WORK REQUIRED" in out["contract"]


def test_main_sealed_exit_code(monkeypatch, tmp_path, capsys):
    real_dt = gate.datetime

    class _FrozenDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(2026, 11, 20, 1, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(gate, "datetime", _FrozenDT)
    (tmp_path / "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_20261120T000000Z.json").write_text("{}")
    monkeypatch.setattr(gate, "run_seal_gate_check", lambda **k: (0, "OK: sealed"))

    rc = gate.main(["--research-state-dir", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert rc == gate.EXIT_SEALED
    assert out["phase"] == "SEALED"
    assert out["seal_gate_rc"] == 0