"""Focused tests for the EVAL-45 Leg B ETH options readiness/BLOCKED helpers.

Pure/deterministic only: readiness arithmetic, on-disk ETH snapshot counting and
the "never relabel BTC as ETH" invariant. No network.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_MODULE_PATH = ROOT / "scripts" / "eval45_options_eth_blocked.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("eval45_options_eth_blocked", _MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mod = _load_module()


def test_assess_readiness_blocks_below_minimum() -> None:
    out = mod.assess_readiness(snapshot_count=0, required_min=30)
    assert out["blocked"] is True
    assert out["dense_series_available"] is False
    assert out["required_min"] == 30
    assert out["btc_snapshot_reference"] == 101


def test_assess_readiness_passes_at_minimum() -> None:
    out = mod.assess_readiness(snapshot_count=30, required_min=30)
    assert out["blocked"] is False
    assert out["dense_series_available"] is True


def test_count_eth_option_snapshots_counts_only_eth(tmp_path) -> None:
    eth = {"instruments": [{"instId": "ETH-USD-261225-4000-C"}]}
    btc = {"instruments": [{"instId": "BTC-USD-261225-60000-C"}]}
    (tmp_path / "eth_snap.json").write_text(json.dumps(eth), encoding="utf-8")
    (tmp_path / "btc_snap.json").write_text(json.dumps(btc), encoding="utf-8")
    out = mod.count_eth_option_snapshots(tmp_path)
    assert out["snapshot_count"] == 1
    assert out["scan_error"] is None
    assert any("eth_snap.json" in p for p in out["sample_paths"])


def test_count_eth_option_snapshots_missing_dir() -> None:
    out = mod.count_eth_option_snapshots(Path("/nonexistent/dir/xyz"))
    assert out["snapshot_count"] == 0
    assert "missing dir" in out["scan_error"]


def test_blocked_report_is_blocked_not_nogo() -> None:
    readiness = mod.assess_readiness(snapshot_count=0, required_min=30)
    report = mod.build_blocked_report(
        generated_at="2026-11-15T01:30:00.000000Z",
        readiness=readiness,
        disk={"snapshot_count": 0, "sample_paths": [], "scan_error": None},
        venue={"reachable": True, "n_quotes": 717, "n_distinct_expiries": 13},
        command="python3 scripts/eval45_options_eth_blocked.py",
        probe=True,
    )
    assert report["status"] == "BLOCKED"
    assert report["verdict"] == "BLOCKED"
    assert report["never_valid_true"] is True
    assert report["live_trading_enabled"] is False
    md = mod.build_blocked_md(report)
    assert "BLOCKED" in md and "NO-GO" in md