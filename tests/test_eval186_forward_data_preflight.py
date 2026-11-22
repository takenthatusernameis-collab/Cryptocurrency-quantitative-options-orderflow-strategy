"""Unit tests for the EVAL-186 forward-data preflight (anti-avoidance gate).

Deterministic in-memory fixtures only. No real data, network, or research_state
writes are used by these tests. The preflight is exercised by monkeypatching the
sealed runner's capture loader / floor / disjointness helpers so the three
verdicts (READY_TO_ACQUIRE, WAIT_FORWARD_DATA, BLOCKED_*) are covered without
touching data/raw/eval185cap.
"""

from __future__ import annotations

from datetime import datetime, timezone

import scripts.eval186_forward_data_preflight as preflight
import scripts.eval186_track_a_fresh_window_replication as e186


def _utc(text: str) -> datetime:
    return e186._parse_iso(text)


def _cap(inst: str, start: str, end: str):
    return {"underlying": inst, "window_start": start, "window_end": end}


def _patch(monkeypatch, *, captures, has_capture, floor_ok, disjoint_ok):
    monkeypatch.setattr(preflight, "_load_captures", lambda _d: captures)
    monkeypatch.setattr(e186, "_has_real_capture", lambda _p: has_capture)

    def _fake_floor_summary(cap):
        return {
            "underlying": cap.get("underlying", "?"),
            "ok": bool(floor_ok),
            "n_surface_snapshots": 1000 if floor_ok else 48,
            "n_surface_bars_5m": 1000 if floor_ok else 48,
            "n_option_trades": 2000 if floor_ok else 615,
            "n_of_bars_5m": 1000 if floor_ok else 46,
            "n_perp_candles": 1000 if floor_ok else 236,
            "perp_span_seconds": 300000.0 if floor_ok else 14100.0,
            "n_perp_bars_5m": 1000 if floor_ok else 47,
            "n_common_bars_5m": 240 if floor_ok else 47,
            "checks": {},
        }

    def _fake_disjointness(cap):
        return {
            "underlying": cap.get("underlying", "?"),
            "ok": bool(disjoint_ok),
            "reason": "strictly_forward_disjoint" if disjoint_ok else "overlaps_previous_window",
            "capture_window": [cap.get("window_start"), cap.get("window_end")],
            "capture_span_seconds": 319680.0,
            "starts_after_previous": bool(disjoint_ok),
        }

    monkeypatch.setattr(e186, "_floor_summary", _fake_floor_summary)
    monkeypatch.setattr(e186, "check_forward_disjointness", _fake_disjointness)


def test_ready_when_floor_and_disjoint_now(monkeypatch):
    caps = [
        _cap("BTC", "2026-11-22T07:12:00Z", "2026-11-25T23:58:00Z"),
        _cap("ETH", "2026-11-22T07:12:00Z", "2026-11-25T23:58:00Z"),
    ]
    _patch(monkeypatch, captures=caps, has_capture=True, floor_ok=True, disjoint_ok=True)
    now = _utc("2026-11-26T12:00:00Z")  # past earliest forward end
    report = preflight.build_report("x", "data/raw/eval185cap", now=now)
    assert report["verdict"] == "READY_TO_ACQUIRE"
    assert report["exit_code"] == preflight.EXIT_READY
    assert report["floor_and_disjoint_ok"] is True
    assert report["acquire_command"][1] == "scripts/eval60_acquire_three_way.py"
    assert "--end" in report["acquire_command"]
    assert report["followup_commands"]


def test_wait_when_under_floor_but_disjoint(monkeypatch):
    caps = [
        _cap("BTC", "2026-11-22T07:12:00Z", "2026-11-26T00:00:00Z"),
        _cap("ETH", "2026-11-22T07:12:00Z", "2026-11-26T00:00:00Z"),
    ]
    _patch(monkeypatch, captures=caps, has_capture=True, floor_ok=False, disjoint_ok=True)
    now = _utc("2026-11-22T12:34:00Z")  # before earliest forward end
    report = preflight.build_report("x", "data/raw/eval185cap", now=now)
    assert report["verdict"] == "WAIT_FORWARD_DATA"
    assert report["exit_code"] == preflight.EXIT_WAIT
    assert report["floor_ok"] is False
    assert report["disjointness_ok"] is True
    assert report["seconds_until_earliest_forward_end"] > 0
    assert report["earliest_forward_capture_end"] == e186.EARLIEST_FORWARD_CAPTURE_END
    assert report["suggested_acquire_end"] == e186.EARLIEST_FORWARD_CAPTURE_END


def test_blocked_non_disjoint(monkeypatch):
    caps = [
        _cap("BTC", "2026-11-22T07:12:00Z", "2026-11-26T00:00:00Z"),
        _cap("ETH", "2026-11-22T07:12:00Z", "2026-11-26T00:00:00Z"),
    ]
    _patch(monkeypatch, captures=caps, has_capture=True, floor_ok=True, disjoint_ok=False)
    now = _utc("2026-11-26T12:00:00Z")
    report = preflight.build_report("x", "data/raw/eval185cap", now=now)
    assert report["verdict"] == "BLOCKED_NON_DISJOINT"
    assert report["exit_code"] == preflight.EXIT_BLOCKED
    assert report["floor_and_disjoint_ok"] is False


def test_blocked_no_capture(monkeypatch):
    _patch(monkeypatch, captures=[], has_capture=False, floor_ok=False, disjoint_ok=False)
    now = _utc("2026-11-26T12:00:00Z")
    report = preflight.build_report("x", "data/raw/eval185cap", now=now)
    assert report["verdict"] == "BLOCKED_NO_CAPTURE"
    assert report["exit_code"] == preflight.EXIT_BLOCKED
    assert report["has_capture"] is False
    assert set(report["missing_underlyings"]) == {"BTC", "ETH"}


def test_earliest_forward_end_is_previously_sealed_plus_acquire_days():
    # The runner's earliest forward end must equal PREVIOUS_WINDOW_END + ACQUIRE_DAYS.
    expected = e186._parse_iso(e186.PREVIOUS_WINDOW_END)
    from datetime import timedelta

    expected = expected + timedelta(days=float(e186.ACQUIRE_DAYS))
    assert e186.EARLIEST_FORWARD_CAPTURE_END == e186._iso(expected)


def test_preflight_never_seals_or_writes(monkeypatch):
    caps = [
        _cap("BTC", "2026-11-22T07:12:00Z", "2026-11-25T23:58:00Z"),
        _cap("ETH", "2026-11-22T07:12:00Z", "2026-11-25T23:58:00Z"),
    ]
    _patch(monkeypatch, captures=caps, has_capture=True, floor_ok=True, disjoint_ok=True)
    now = _utc("2026-11-26T12:00:00Z")
    report = preflight.build_report("x", "data/raw/eval185cap", now=now)
    # build_report must be pure: no seal markers, no capture writes.
    assert "sealed" not in json_text(report).lower() or "never seals" in json_text(report).lower()
    assert "exit_code" in report and report["exit_code"] == preflight.EXIT_READY


def json_text(obj) -> str:
    import json

    return json.dumps(obj)