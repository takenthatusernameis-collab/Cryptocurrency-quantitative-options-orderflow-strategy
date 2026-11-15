"""Unit tests for EVAL-47 ETH combined options+orderflow audit wrapper.

These tests verify the thin wrapper correctly parametrizes the sealed EVAL-46
pipeline for ETH (constant overrides, BTC->ETH relabeling, blocked-report
structure) without editing the sealed eval46 script or any src/ module.
"""

from __future__ import annotations

import json
from pathlib import Path

import scripts.eval46_integrated_options_orderflow_audit as e46
import scripts.eval47_eth_combined_audit as e47


# ---------------------------------------------------------------------------
# Constant overrides
# ---------------------------------------------------------------------------
def test_options_dir_overridden_to_eval45():
    assert e46.OPTIONS_DIR == "data/raw/eval45"
    assert e47.ETH_OPTIONS_DIR == "data/raw/eval45"


def test_tapes_overridden_to_eth_five():
    assert len(e46.TAPES) == 5
    assert set(e46.TAPES.keys()) == {"eth_w05", "eth_w04", "eth_w03", "eth_w02", "eth_w01"}
    for key, path in e46.TAPES.items():
        assert path.startswith("data/raw/eval45/orderflow_okx_ETH_")
        # key 'eth_w05' maps to path '...ETH_w05_...'
        assert key.split("_", 1)[1] in path  # 'w05' in path


def test_report_and_prereg_ids():
    assert e46.REPORT_ID == "EVAL_47_ETH_COMBINED"
    assert e46.PREREG_ID == "EVAL_47_PREREGISTRATION"
    assert e46.BLOCKED_ID == "EVAL_47_BLOCKED"


def test_code_paths_include_wrapper():
    assert "scripts/eval47_eth_combined_audit.py" in e46.CODE_PATHS
    assert "tests/test_eval47_eth_combined_audit.py" in e46.CODE_PATHS
    assert "scripts/eval46_integrated_options_orderflow_audit.py" in e46.CODE_PATHS


def test_commands_reference_eval47():
    joined = " ".join(e46.COMMANDS)
    assert "eval47_eth_combined_audit.py" in joined
    assert "EVAL_47" in joined or "eval47" in joined


# ---------------------------------------------------------------------------
# Patched _build_report / build_prereg (BTC -> ETH relabeling)
# ---------------------------------------------------------------------------
def test_patched_build_report_eth_scope():
    rep = e46._build_report(
        generated_at="2026-11-15T06:30:00.000Z",
        tape_results=[],
        options_meta={"n_snapshots": 0},
        tape_meta={},
        protocol={},
        task_label=e47.TASK_LABEL,
    )
    assert rep["verdict_scope"] == "FULL_DENSE_ETH"
    assert "EVAL-47" in rep["campaign_state"]
    assert rep["report_id"] == "EVAL_47_ETH_COMBINED"
    assert "EVAL-47" in rep["task_id"]


def test_patched_build_prereg_eth_hypothesis():
    p = e46.build_prereg(
        generated_at="2026-11-15T06:30:00.000Z",
        options_meta={"n_snapshots": 0},
        tape_meta={},
        protocol={},
        task_id="INIT-2026-11-15T06:30:00.000Z-EVAL-47-TEST",
    )
    assert p["report_id"] == "EVAL_47_PREREGISTRATION"
    assert "ETH" in p["hypothesis"]
    assert "BTC" not in p["hypothesis"]


def test_patched_report_and_prereg_have_no_btc_prose():
    """The relabelable verdict prose (verdict_reason / go_bar / hypothesis) is ETH-scoped.

    Only these fields are relabeled; legitimate historical references such as
    ``campaign_state`` citing the sealed EVAL-46 BTC combined NO-GO are intentionally
    left intact.
    """
    rep = e46._build_report(
        generated_at="2026-11-15T06:30:00.000Z",
        tape_results=[],
        options_meta={"n_snapshots": 0},
        tape_meta={},
        protocol={},
        task_label=e47.TASK_LABEL,
    )
    p = e46.build_prereg(
        generated_at="2026-11-15T06:30:00.000Z",
        options_meta={"n_snapshots": 0},
        tape_meta={},
        protocol={},
        task_id="INIT-2026-11-15T06:30:00.000Z-EVAL-47-TEST",
    )

    def check(obj):
        for key in ("verdict_reason", "go_bar", "hypothesis"):
            val = obj.get(key)
            if isinstance(val, str):
                assert "BTC" not in val, f"BTC prose in {key}: {val!r}"
                assert "ETH" in val, f"ETH not present in {key}: {val!r}"

    check(rep)
    check(p.get("protocol", {}))
    assert "all 5 real ETH tapes" in rep["verdict_reason"]
    assert "the available real ETH data" in rep["verdict_reason"]


# ---------------------------------------------------------------------------
# Blocked report
# ---------------------------------------------------------------------------
def test_blocked_report_structure():
    exc = RuntimeError("synthetic test error")
    rep = e47._build_blocked_report("2026-11-15T06:30:00.000Z", exc, e47.TASK_LABEL)
    assert rep["report_id"] == "EVAL_47_BLOCKED"
    assert rep["verdict"] == "BLOCKED"
    assert rep["status"] == "BLOCKED"
    assert rep["error_type"] == "RuntimeError"
    assert "synthetic test error" in rep["error"]
    assert "INIT-" in rep["task_id"]
    assert e47.TASK_LABEL in rep["task_id"]


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
# Integration smoke (skipped if ETH data absent)
# ---------------------------------------------------------------------------
def _eth_data_present() -> bool:
    opt = Path("data/raw/eval45")
    if not opt.is_dir():
        return False
    tapes = list(opt.glob("orderflow_okx_ETH_*.json"))
    opts = list(opt.glob("options_okx_ETH_*.json"))
    return len(tapes) >= 1 and len(opts) >= 1


def test_main_no_write_smoke():
    """Full ETH chain runs end-to-end (truncated, no seal)."""
    if not _eth_data_present():
        import pytest
        pytest.skip("ETH data not on disk")
    rc = e47.main(["--no-write", "--max-trades", "1000"])
    assert rc == 0