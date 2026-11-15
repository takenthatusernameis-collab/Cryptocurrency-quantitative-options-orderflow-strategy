"""Unit tests for EVAL-48 cross-venue combined options+orderflow audit wrapper.

These tests verify the thin wrapper correctly parametrizes the sealed EVAL-46
pipeline for the cross-venue scope (Deribit options + OKX orderflow), the
BTC/OKX -> cross-venue relabeling, the blocked-report structure, and the
Deribit acquisition helper — without editing the sealed eval46 script or any
src/ module.
"""

from __future__ import annotations

import json
from pathlib import Path

import scripts.eval46_integrated_options_orderflow_audit as e46
import scripts.eval48_cross_venue_replication as e48
import scripts.eval48_acquire_deribit_options as acq


# ---------------------------------------------------------------------------
# Constant overrides
# ---------------------------------------------------------------------------
def test_options_dir_overridden_to_eval48():
    assert e46.OPTIONS_DIR == "data/raw/eval48"
    assert e48.CROSS_VENUE_OPTIONS_DIR == "data/raw/eval48"


def test_tapes_are_the_okx_btc_two():
    assert len(e46.TAPES) == 2
    assert set(e46.TAPES.keys()) == {"41d_fresh", "midday"}
    for path in e46.TAPES.values():
        assert path.startswith("data/raw/eval41/orderflow_okx_BTC")


def test_report_and_prereg_ids():
    assert e46.REPORT_ID == "EVAL_48_CROSS_VENUE_COMBINED"
    assert e46.PREREG_ID == "EVAL_48_PREREGISTRATION"
    assert e46.BLOCKED_ID == "EVAL_48_BLOCKED"


def test_code_paths_include_wrapper_and_acquire():
    assert "scripts/eval48_cross_venue_replication.py" in e46.CODE_PATHS
    assert "tests/test_eval48_cross_venue_replication.py" in e46.CODE_PATHS
    assert "scripts/eval48_acquire_deribit_options.py" in e46.CODE_PATHS
    assert "scripts/eval46_integrated_options_orderflow_audit.py" in e46.CODE_PATHS


def test_commands_reference_eval48():
    joined = " ".join(e46.COMMANDS)
    assert "eval48_cross_venue_replication.py" in joined
    assert "eval48_acquire_deribit_options.py" in joined


# ---------------------------------------------------------------------------
# Patched _build_report / build_prereg (cross-venue relabeling)
# ---------------------------------------------------------------------------
def test_patched_build_report_cross_venue_scope():
    rep = e46._build_report(
        generated_at="2026-11-15T08:20:00.000Z",
        tape_results=[],
        options_meta={"n_snapshots": 0},
        tape_meta={},
        protocol={},
        task_label=e48.TASK_LABEL,
    )
    assert rep["verdict_scope"] == "FULL_DENSE_CROSS_VENUE"
    assert rep["options_venue"] == "deribit"
    assert rep["orderflow_venue"] == "okx"
    assert "EVAL-48" in rep["campaign_state"]
    assert rep["report_id"] == "EVAL_48_CROSS_VENUE_COMBINED"
    assert "EVAL-48" in rep["task_id"]


def test_patched_build_prereg_cross_venue_hypothesis():
    p = e46.build_prereg(
        generated_at="2026-11-15T08:20:00.000Z",
        options_meta={"n_snapshots": 0},
        tape_meta={},
        protocol={},
        task_id="INIT-2026-11-15T08:20:00.000Z-EVAL-48-TEST",
    )
    assert p["report_id"] == "EVAL_48_PREREGISTRATION"
    assert p["verdict_scope"] == "FULL_DENSE_CROSS_VENUE"
    assert p["options_venue"] == "deribit"
    assert "Deribit" in p["hypothesis"]


def test_patched_verdict_reason_mentions_deribit():
    rep = e46._build_report(
        generated_at="2026-11-15T08:20:00.000Z",
        tape_results=[],
        options_meta={"n_snapshots": 0},
        tape_meta={},
        protocol={},
        task_label=e48.TASK_LABEL,
    )
    # verdict_reason is relabeled to the cross-venue data provenance.
    assert "Deribit" in rep["verdict_reason"]
    assert "orderflow" in rep["verdict_reason"]


# ---------------------------------------------------------------------------
# Blocked report
# ---------------------------------------------------------------------------
def test_blocked_report_structure():
    exc = RuntimeError("synthetic test error")
    rep = e48._build_blocked_report("2026-11-15T08:20:00.000Z", exc, e48.TASK_LABEL)
    assert rep["report_id"] == "EVAL_48_BLOCKED"
    assert rep["verdict"] == "BLOCKED"
    assert rep["status"] == "BLOCKED"
    assert rep["error_type"] == "RuntimeError"
    assert "synthetic test error" in rep["error"]
    assert "INIT-" in rep["task_id"]
    assert e48.TASK_LABEL in rep["task_id"]


# ---------------------------------------------------------------------------
# Reuse of eval46 helpers (no duplication)
# ---------------------------------------------------------------------------
def test_reuses_eval46_fusion_rules():
    assert e46.FUSION_RULES == ("sign_agreement", "regime_filter", "continuous_zscore")


def test_reuses_eval46_seal_and_utcnow():
    assert callable(e46._seal)
    assert callable(e46._utc_now_iso)
    ts = e46._utc_now_iso()
    assert ts.endswith("Z")
    assert "T" in ts


# ---------------------------------------------------------------------------
# Deribit acquisition helper
# ---------------------------------------------------------------------------
def test_acquisition_defaults_and_parse():
    assert acq.SCHEMA == "deribit_public_tradingview_chart_reconstruction_v1"
    assert acq.DEFAULT_EXPIRIES == ("2026-11-15", "2026-11-20", "2026-11-27")
    info = acq._parse_deribit_instrument("BTC-20NOV26-66000-C")
    assert info["underlying"] == "BTC"
    assert info["strike"] == 66000.0
    assert info["option_type"] == "call"
    assert info["expiry"].date().isoformat() == "2026-11-20"


def test_build_snapshots_gates_on_min_quotes():
    instruments = [
        {"instrument_name": "BTC-20NOV26-66000-C", "expiry": acq._parse_iso("2026-11-20T08:00:00Z"),
         "strike": 66000.0, "option_type": "call"},
        {"instrument_name": "BTC-20NOV26-66000-P", "expiry": acq._parse_iso("2026-11-20T08:00:00Z"),
         "strike": 66000.0, "option_type": "put"},
    ]
    bar_ms = int(acq._parse_iso("2026-11-14T13:20:00Z").timestamp() * 1000)
    candles = {
        "BTC-20NOV26-66000-C": {bar_ms: 0.02},
        "BTC-20NOV26-66000-P": {bar_ms: 0.01},
    }
    # min_quotes=3 -> both bars dropped (only 2 quotes)
    assert acq.build_snapshots(candles, instruments, [bar_ms], 3, "BTC") == []
    # min_quotes=2 -> one snapshot with 2 quotes, bid/ask bracket the mark
    snaps = acq.build_snapshots(candles, instruments, [bar_ms], 2, "BTC")
    assert len(snaps) == 1
    quotes = snaps[0][1]
    assert len(quotes) == 2
    call = next(q for q in quotes if q["option_type"] == "call")
    assert call["mark"] == 0.02
    assert call["bid"] < call["mark"] < call["ask"]


# ---------------------------------------------------------------------------
# Data presence (skip if Deribit snapshots absent)
# ---------------------------------------------------------------------------
def _eval48_data_present() -> bool:
    opt = Path("data/raw/eval48")
    if not opt.is_dir():
        return False
    return len(list(opt.glob("options_deribit_BTC_*.json"))) >= 30


def test_deribit_snapshots_load_and_vary():
    if not _eval48_data_present():
        import pytest
        pytest.skip("Deribit BTC snapshots not on disk")
    from src.analytics.options_time_varying_signal import load_snapshot_signals

    sigs = load_snapshot_signals("BTC", "data/raw/eval48")
    assert len(sigs) >= 30
    distinct = {round(s.options_signal_raw, 6) for s in sigs}
    assert len(distinct) >= 2, "Deribit options signal must be non-degenerate"


# ---------------------------------------------------------------------------
# Integration smoke (skip if data absent)
# ---------------------------------------------------------------------------
def test_main_no_write_smoke():
    """Full cross-venue chain runs end-to-end (truncated, no seal)."""
    if not _eval48_data_present():
        import pytest
        pytest.skip("Deribit BTC snapshots not on disk")
    rc = e48.main(["--no-write", "--max-trades", "1000"])
    assert rc == 0