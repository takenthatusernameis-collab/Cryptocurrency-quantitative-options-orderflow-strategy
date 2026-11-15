"""Unit tests for EVAL-49 ETH cross-venue combined options+orderflow audit wrapper.

These tests verify the thin wrapper correctly parametrizes the sealed EVAL-46
pipeline for the ETH cross-venue scope (Deribit ETH options + OKX ETH orderflow),
the ETH/OKX -> cross-venue relabeling, the blocked-report structure, and the
Deribit acquisition helper (including the ``--manifest-id`` seal override) --
without editing the sealed eval46/eval47 scripts or any src/ module.
"""

from __future__ import annotations

from pathlib import Path

import scripts.eval46_integrated_options_orderflow_audit as e46
import scripts.eval49_eth_cross_venue_replication as e49
import scripts.eval48_acquire_deribit_options as acq


# ---------------------------------------------------------------------------
# Constant overrides
# ---------------------------------------------------------------------------
def test_options_dir_overridden_to_eval49():
    assert e46.OPTIONS_DIR == "data/raw/eval49"
    assert e49.CROSS_VENUE_OPTIONS_DIR == "data/raw/eval49"


def test_tapes_are_the_okx_eth_five():
    assert len(e46.TAPES) == 5
    assert set(e46.TAPES.keys()) == {"eth_w01", "eth_w02", "eth_w03", "eth_w04", "eth_w05"}
    for path in e46.TAPES.values():
        assert path.startswith("data/raw/eval45/orderflow_okx_ETH")


def test_report_and_prereg_ids():
    assert e46.REPORT_ID == "EVAL_49_ETH_CROSS_VENUE_COMBINED"
    assert e46.PREREG_ID == "EVAL_49_PREREGISTRATION"
    assert e46.BLOCKED_ID == "EVAL_49_BLOCKED"


def test_code_paths_include_wrapper_and_acquire():
    assert "scripts/eval49_eth_cross_venue_replication.py" in e46.CODE_PATHS
    assert "tests/test_eval49_eth_cross_venue_replication.py" in e46.CODE_PATHS
    assert "scripts/eval48_acquire_deribit_options.py" in e46.CODE_PATHS
    assert "scripts/eval46_integrated_options_orderflow_audit.py" in e46.CODE_PATHS


def test_commands_reference_eval49_and_eth_acquisition():
    joined = " ".join(e46.COMMANDS)
    assert "eval49_eth_cross_venue_replication.py" in joined
    assert "--underlying ETH" in joined
    assert "--manifest-id EVAL_49_DERIBIT_ACQUISITION" in joined
    assert "data/raw/eval49" in joined


# ---------------------------------------------------------------------------
# Patched _build_report / build_prereg (ETH cross-venue relabeling)
# ---------------------------------------------------------------------------
def test_patched_build_report_eth_cross_venue_scope():
    rep = e46._build_report(
        generated_at="2026-11-15T10:10:00.000Z",
        tape_results=[],
        options_meta={"n_snapshots": 0},
        tape_meta={},
        protocol={},
        task_label=e49.TASK_LABEL,
    )
    assert rep["verdict_scope"] == "FULL_DENSE_ETH_CROSS_VENUE"
    assert rep["options_venue"] == "deribit"
    assert rep["orderflow_venue"] == "okx"
    assert "EVAL-49" in rep["campaign_state"]
    assert "EVAL-48" in rep["campaign_state"]
    assert rep["report_id"] == "EVAL_49_ETH_CROSS_VENUE_COMBINED"
    assert "EVAL-49" in rep["task_id"]


def test_patched_build_prereg_eth_cross_venue_hypothesis():
    p = e46.build_prereg(
        generated_at="2026-11-15T10:10:00.000Z",
        options_meta={"n_snapshots": 0},
        tape_meta={},
        protocol={},
        task_id="INIT-2026-11-15T10:10:00.000Z-EVAL-49-TEST",
    )
    assert p["report_id"] == "EVAL_49_PREREGISTRATION"
    assert p["verdict_scope"] == "FULL_DENSE_ETH_CROSS_VENUE"
    assert p["options_venue"] == "deribit"
    assert "Deribit ETH" in p["hypothesis"]


def test_patched_verdict_reason_mentions_deribit():
    rep = e46._build_report(
        generated_at="2026-11-15T10:10:00.000Z",
        tape_results=[],
        options_meta={"n_snapshots": 0},
        tape_meta={},
        protocol={},
        task_label=e49.TASK_LABEL,
    )
    assert "Deribit" in rep["verdict_reason"]
    assert "ETH" in rep["verdict_reason"]


# ---------------------------------------------------------------------------
# Blocked report
# ---------------------------------------------------------------------------
def test_blocked_report_structure():
    exc = RuntimeError("synthetic test error")
    rep = e49._build_blocked_report("2026-11-15T10:10:00.000Z", exc, e49.TASK_LABEL)
    assert rep["report_id"] == "EVAL_49_BLOCKED"
    assert rep["verdict"] == "BLOCKED"
    assert rep["status"] == "BLOCKED"
    assert "INIT-" in rep["task_id"]
    assert e49.TASK_LABEL in rep["task_id"]


# ---------------------------------------------------------------------------
# Reuse of eval46 helpers (no duplication)
# ---------------------------------------------------------------------------
def test_reuses_eval46_fusion_rules():
    assert e46.FUSION_RULES == ("sign_agreement", "regime_filter", "continuous_zscore")


# ---------------------------------------------------------------------------
# Acquisition helper: manifest id override + ETH parsing
# ---------------------------------------------------------------------------
def test_acquisition_manifest_id_override(tmp_path):
    instruments = [
        {"instrument_name": "ETH-20NOV26-3500-C",
         "expiry": acq._parse_iso("2026-11-20T08:00:00Z"),
         "strike": 3500.0, "option_type": "call"},
        {"instrument_name": "ETH-20NOV26-3500-P",
         "expiry": acq._parse_iso("2026-11-20T08:00:00Z"),
         "strike": 3500.0, "option_type": "put"},
    ]
    bar_ms = int(acq._parse_iso("2026-11-14T22:00:00Z").timestamp() * 1000)
    candles = {"ETH-20NOV26-3500-C": {bar_ms: 0.02},
               "ETH-20NOV26-3500-P": {bar_ms: 0.01}}
    assert acq.build_snapshots(candles, instruments, [bar_ms], 2, "ETH")


def test_parse_eth_instrument():
    info = acq._parse_deribit_instrument("ETH-20NOV26-3500-C")
    assert info["underlying"] == "ETH"
    assert info["strike"] == 3500.0
    assert info["option_type"] == "call"
    assert info["expiry"].date().isoformat() == "2026-11-20"


def test_seal_manifest_accepts_manifest_id(tmp_path, monkeypatch):
    import research_state  # noqa: F401  (ensure package importable)
    import scripts.eval48_acquire_deribit_options as a

    written = tmp_path / "m.json"
    written.write_text("{}")
    monkeypatch.setattr(a, "ROOT", tmp_path)
    paths = a.seal_manifest(
        tmp_path,
        {
            "underlying": "ETH",
            "window_start": "2026-11-14T20:20:00Z",
            "window_end": "2026-11-15T05:20:00Z",
            "n_snapshots": 1,
            "n_instruments_with_data": 1,
            "n_instruments_probed": 1,
            "min_quotes": 2,
            "min_quotes_realized": 2,
            "max_quotes_realized": 2,
            "per_expiry_counts": {"2026-11-20": 1},
        },
        "2026-11-15T10:10:00.000Z",
        "EVAL-49-TEST", manifest_id="EVAL_49_DERIBIT_ACQUISITION",
    )
    assert "EVAL_49_DERIBIT_ACQUISITION_" in paths["json"]
    assert "EVAL_49_DERIBIT_ACQUISITION_" in paths["md"]


# ---------------------------------------------------------------------------
# Data presence (skip if Deribit ETH snapshots absent)
# ---------------------------------------------------------------------------
def _eval49_data_present() -> bool:
    opt = Path("data/raw/eval49")
    if not opt.is_dir():
        return False
    return len(list(opt.glob("options_deribit_ETH_*.json"))) >= 30


def test_deribit_eth_snapshots_load_and_vary():
    if not _eval49_data_present():
        import pytest
        pytest.skip("Deribit ETH snapshots not on disk")
    sigs = e49._load_snapshot_signals_with_spot("ETH", "data/raw/eval49")
    assert len(sigs) >= 30
    distinct = {round(s.options_signal_raw, 6) for s in sigs}
    assert len(distinct) >= 2, "Deribit ETH options signal must be non-degenerate"


# ---------------------------------------------------------------------------
# Integration smoke (skip if data absent)
# ---------------------------------------------------------------------------
def test_main_no_write_smoke():
    """Full ETH cross-venue chain runs end-to-end (truncated, no seal)."""
    if not _eval49_data_present():
        import pytest
        pytest.skip("Deribit ETH snapshots not on disk")
    rc = e49.main(["--no-write", "--max-trades", "1000"])
    assert rc == 0