"""Unit tests for the EVAL-69 Phase-B gate (scripts/eval69_phaseb_gate.py).

The gate is the deterministic, idempotent arbiter of the EVAL-69 completion
contract (pooled BTC+ETH traded-form). These tests pin its four outcomes
(SEALED / WAIT_EVAL68 / DUE / FAILED), its EVAL-68 ordering prerequisite (EVAL-69
reads EVAL-68's disjoint forward capture; no acquisition), its seal detection
(stamps >= the pre-registered task floor, stale artifacts excluded), its
disjointness math, and its refusal to run before the prerequisite/threshold.
Deterministic in-memory fixtures only: no real data, no network, no
research_state writes (all filesystem access is redirected to tmp_path).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

import scripts.eval68_phaseb_gate as g68
import scripts.eval69_phaseb_gate as gate


# ---------------------------------------------------------------------------
# Constants / identifiers
# ---------------------------------------------------------------------------
def test_task_id_is_parseable_and_stable():
    floor = gate.task_floor_stamp(gate.TASK_ID)
    assert floor == "20261116T224500Z"
    assert gate.TASK_LABEL == "EVAL69-POOLED-BTC-ETH-OFLOW-TOX-RV-TRADED-OOS"
    assert gate.THRESHOLD_ISO == "2026-11-20T00:00:00Z"
    assert gate.UNDERLYINGS == ("BTC", "ETH")


def test_exit_codes_are_distinct():
    codes = {gate.EXIT_SEALED, gate.EXIT_FAILED, gate.EXIT_WAIT_EVAL68, gate.EXIT_DUE}
    assert codes == {0, 1, 10, 20}


def test_threshold_is_after_earliest_disjoint_end():
    assert gate.parse_iso(gate.THRESHOLD_ISO) >= gate.parse_iso(
        gate.EARLIEST_DISJOINT_CAPTURE_END
    )


def test_reuses_eval68_capture_no_acquisition():
    # EVAL-69 reads EVAL-68's capture dir; it must not have its own eval69 dir.
    assert gate.CAPTURE_DIR.name == "eval68"
    assert "eval69" not in str(gate.CAPTURE_DIR)


# ---------------------------------------------------------------------------
# decide_phase (EVAL-68 ordering + threshold)
# ---------------------------------------------------------------------------
def test_decide_phase_sealed_wins():
    now = datetime(2026, 11, 20, 0, 0, 1, tzinfo=timezone.utc)
    thr = gate.parse_iso(gate.THRESHOLD_ISO)
    assert gate.decide_phase(now, thr, True, False) == "SEALED"
    assert gate.decide_phase(now, thr, True, True) == "SEALED"


def test_decide_phase_waits_for_eval68_first():
    now = datetime(2026, 11, 16, 15, 0, 0, tzinfo=timezone.utc)
    thr = gate.parse_iso(gate.THRESHOLD_ISO)
    # EVAL-68 not sealed yet -> WAIT even if the clock is past threshold.
    assert gate.decide_phase(now, thr, False, False) == "WAIT_EVAL68"
    late = datetime(2026, 11, 21, 0, 0, 0, tzinfo=timezone.utc)
    assert gate.decide_phase(late, thr, False, False) == "WAIT_EVAL68"


def test_decide_phase_due_when_eval68_sealed_and_past_threshold():
    thr = gate.parse_iso(gate.THRESHOLD_ISO)
    assert gate.decide_phase(thr, thr, False, True) == "DUE"
    after = datetime(2026, 11, 21, 0, 0, 0, tzinfo=timezone.utc)
    assert gate.decide_phase(after, thr, False, True) == "DUE"


# ---------------------------------------------------------------------------
# detect_seal (mirrors check_session_sealed.py stamp semantics)
# ---------------------------------------------------------------------------
def test_detect_seal_true_when_combined_after_floor(tmp_path):
    (tmp_path / "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_COMBINED_20261120T000000Z.json").write_text("{}")
    d = gate.detect_seal(tmp_path)
    assert d["sealed"] is True
    assert any(a["kind"] == "COMBINED" for a in d["artifacts"])


def test_detect_seal_true_when_blocked_after_floor(tmp_path):
    (tmp_path / "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_BLOCKED_20261120T000000Z.md").write_text("x")
    d = gate.detect_seal(tmp_path)
    assert d["sealed"] is True
    assert any(a["kind"] == "BLOCKED" for a in d["artifacts"])


def test_detect_seal_false_when_only_prereg(tmp_path):
    (tmp_path / "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_PREREGISTRATION_20261120T000000Z.json").write_text("{}")
    d = gate.detect_seal(tmp_path)
    assert d["sealed"] is False
    assert d["artifacts"] == []


def test_detect_seal_excludes_stale_artifact_below_floor(tmp_path):
    (tmp_path / "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_COMBINED_20260101T000000Z.json").write_text("{}")
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
    assert dm["underlyings"] == ["BTC", "ETH"]


def test_disjointness_clean_at_threshold():
    now = gate.parse_iso("2026-11-20T00:00:00Z")
    dm = gate.disjointness_math(now)
    assert dm["disjoint"] is True
    assert dm["overlap_seconds"] == 0.0
    assert dm["meets_min_span"] is True


# ---------------------------------------------------------------------------
# execute_phaseb refuses before the EVAL-68 prerequisite / threshold
# ---------------------------------------------------------------------------
def test_execute_refuses_before_eval68_sealed(monkeypatch, tmp_path):
    # EVAL-68 not sealed -> refuse, and never shell out.
    monkeypatch.setattr(gate, "eval68_sealed", lambda *a, **k: False)

    def _boom(*a, **k):  # pragma: no cover - must not be called
        raise AssertionError("execute_phaseb must not shell out before EVAL-68 seals")

    monkeypatch.setattr(gate.subprocess, "run", _boom)
    res = gate.execute_phaseb(capture_dir=tmp_path / "cap", research_state_dir=tmp_path)
    assert res["ok"] is False
    assert res["step"] == "eval68_prereq"
    assert res["reason"] == "eval68_not_sealed"


def test_execute_refuses_before_threshold(monkeypatch, tmp_path):
    # EVAL-68 sealed but clock before threshold -> refuse, never shell out.
    monkeypatch.setattr(gate, "eval68_sealed", lambda *a, **k: True)

    def _boom(*a, **k):  # pragma: no cover - must not be called
        raise AssertionError("execute_phaseb must not shell out before threshold")

    monkeypatch.setattr(gate.subprocess, "run", _boom)
    real_dt = gate.datetime

    class _FrozenDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(2026, 11, 16, 15, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(gate, "datetime", _FrozenDT)
    res = gate.execute_phaseb(capture_dir=tmp_path / "cap", research_state_dir=tmp_path)
    assert res["ok"] is False
    assert res["step"] == "threshold"
    assert res["reason"] == "before_threshold"


def test_execute_refuses_when_eval68_capture_missing(monkeypatch, tmp_path):
    real_dt = gate.datetime

    class _FrozenDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(2026, 11, 20, 1, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(gate, "datetime", _FrozenDT)
    monkeypatch.setattr(gate, "eval68_sealed", lambda *a, **k: True)

    def _boom(*a, **k):  # pragma: no cover - must not be called
        raise AssertionError("execute_phaseb must not shell out when capture missing")

    monkeypatch.setattr(gate.subprocess, "run", _boom)
    res = gate.execute_phaseb(capture_dir=tmp_path / "no_cap", research_state_dir=tmp_path)
    assert res["ok"] is False
    assert res["step"] == "capture"
    assert res["reason"] == "missing_eval68_capture"


# ---------------------------------------------------------------------------
# execute_phaseb happy path: capture exists -> dry-run -> seal -> seal-gate OK
# ---------------------------------------------------------------------------
def test_execute_runs_pipeline_and_requires_seal_gate(monkeypatch, tmp_path):
    real_dt = gate.datetime

    class _FrozenDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(2026, 11, 20, 1, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(gate, "datetime", _FrozenDT)
    monkeypatch.setattr(gate, "eval68_sealed", lambda *a, **k: True)

    cap = tmp_path / "data/raw/eval68"
    cap.mkdir(parents=True)
    (cap / "three_way_BTC_20261120T005959Z.json").write_text("{}")
    (cap / "three_way_ETH_20261120T005959Z.json").write_text("{}")

    def _fake_run(cmd, cwd=None):
        return 0, "ok: " + " ".join(str(c) for c in cmd)

    monkeypatch.setattr(gate, "_run", _fake_run)
    monkeypatch.setattr(gate, "run_seal_gate_check", lambda **k: (0, "OK: sealed"))

    res = gate.execute_phaseb(capture_dir=cap, research_state_dir=tmp_path)
    assert res["ok"] is True
    assert res["step"] == "seal_gate"
    steps = {s["step"]: s for s in res["steps"]}
    assert steps["capture"]["status"] == "ok"
    assert steps["dry_run"]["status"] == "ok"
    assert steps["seal"]["status"] == "ok"
    assert steps["seal_gate"]["status"] == "ok"
    # EVAL-69 must NOT acquire (no eval60_acquire call).
    assert "acquire" not in steps


def test_execute_fails_when_seal_gate_fails(monkeypatch, tmp_path):
    real_dt = gate.datetime

    class _FrozenDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(2026, 11, 20, 1, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(gate, "datetime", _FrozenDT)
    monkeypatch.setattr(gate, "eval68_sealed", lambda *a, **k: True)

    cap = tmp_path / "data/raw/eval68"
    cap.mkdir(parents=True)
    (cap / "three_way_BTC_20261120T005959Z.json").write_text("{}")
    (cap / "three_way_ETH_20261120T005959Z.json").write_text("{}")

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
    monkeypatch.setattr(gate, "eval68_sealed", lambda *a, **k: True)

    cap = tmp_path / "data/raw/eval68"
    cap.mkdir(parents=True)
    (cap / "three_way_BTC_20261120T005959Z.json").write_text("{}")
    (cap / "three_way_ETH_20261120T005959Z.json").write_text("{}")

    monkeypatch.setattr(gate, "_run", lambda cmd, cwd=None: (1, "boom"))
    monkeypatch.setattr(gate, "run_seal_gate_check", lambda **k: (0, "OK"))

    res = gate.execute_phaseb(capture_dir=cap, research_state_dir=tmp_path)
    assert res["ok"] is False
    assert res["step"] == "dry_run"


# ---------------------------------------------------------------------------
# main() maps phases to exit codes (status-only paths; no subprocess)
# ---------------------------------------------------------------------------
def test_main_wait_eval68_exit_code(monkeypatch, tmp_path, capsys):
    real_dt = gate.datetime

    class _FrozenDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(2026, 11, 16, 15, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(gate, "datetime", _FrozenDT)
    monkeypatch.setattr(gate, "RS_DIR", tmp_path)
    monkeypatch.setattr(gate, "eval68_sealed", lambda *a, **k: False)

    rc = gate.main(["--research-state-dir", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert rc == gate.EXIT_WAIT_EVAL68
    assert out["phase"] == "WAIT_EVAL68"
    assert out["eval68_sealed"] is False


def test_main_due_without_execute_exit_code(monkeypatch, tmp_path, capsys):
    real_dt = gate.datetime

    class _FrozenDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(2026, 11, 20, 1, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(gate, "datetime", _FrozenDT)
    monkeypatch.setattr(gate, "RS_DIR", tmp_path)
    monkeypatch.setattr(gate, "eval68_sealed", lambda *a, **k: True)

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
    monkeypatch.setattr(gate, "eval68_sealed", lambda *a, **k: True)
    (tmp_path / "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_COMBINED_20261120T000000Z.json").write_text("{}")
    monkeypatch.setattr(gate, "run_seal_gate_check", lambda **k: (0, "OK: sealed"))

    rc = gate.main(["--research-state-dir", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert rc == gate.EXIT_SEALED
    assert out["phase"] == "SEALED"
    assert out["seal_gate_rc"] == 0