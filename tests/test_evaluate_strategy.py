"""Tests for scripts/evaluate_strategy.py: artifact emission, strict finite JSON,
>=3 baselines, bootstrap CI bracketing, and fixed-seed byte-identical determinism.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from scripts.evaluate_strategy import (
    DETERMINISTIC_TS,
    _bootstrap_ci_on_returns,
    _markdown,
    _run_all,
    attribute_pnl,
    block_bootstrap_ci,
    compute_metrics,
    main,
)

RESEARCH_STATE = Path("research_state")


def _json_finite(obj) -> bool:
    try:
        json.dumps(obj, allow_nan=False)
    except (ValueError, TypeError):
        return False
    return True


def _recursive_finite(value) -> bool:
    if isinstance(value, dict):
        return all(_recursive_finite(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return all(_recursive_finite(v) for v in value)
    if isinstance(value, float):
        return math.isfinite(value)
    return True


def test_cli_writes_artifacts_and_exits_zero(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    rc = main(["--seeds", "1", "2", "3", "--write"])
    assert rc == 0
    stem = f"STRATEGY_EVALUATION_{DETERMINISTIC_TS.replace(':', '')}"
    json_path = RESEARCH_STATE / f"{stem}.json"
    md_path = RESEARCH_STATE / f"{stem}.md"
    assert json_path.exists(), json_path
    assert md_path.exists(), md_path
    report = json.loads(json_path.read_text())
    assert _json_finite(report)
    assert _recursive_finite(report)
    assert report["verdict"] in ("GO", "NO-GO")
    assert "headline" in report and "gates" in report
    assert set(report["baselines"].keys()) >= {
        "delta_hedged_buy_and_hold_long_gamma",
        "naive_orderflow_threshold_no_hedge",
        "zero_signal_random_seed_fixed",
    }, report["baselines"].keys()
    assert report["data_provenance"] == "synthetic"


def test_cli_deterministic_byte_identical_rerun(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    stem = f"STRATEGY_EVALUATION_{DETERMINISTIC_TS.replace(':', '')}"
    json_path = RESEARCH_STATE / f"{stem}.json"
    md_path = RESEARCH_STATE / f"{stem}.md"
    main(["--seeds", "1", "2", "3", "--write"])
    first_json = json_path.read_bytes()
    first_md = md_path.read_bytes()
    main(["--seeds", "1", "2", "3", "--write"])
    assert json_path.read_bytes() == first_json, "JSON rerun not byte-identical"
    assert md_path.read_bytes() == first_md, "Markdown rerun not byte-identical"


def test_run_all_deterministic_dict() -> None:
    r1 = _run_all([1, 2, 3], ["equal_weight", "risk_parity", "vol_target"])
    r2 = _run_all([1, 2, 3], ["equal_weight", "risk_parity", "vol_target"])
    assert json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)
    assert r1["verdict"] in ("GO", "NO-GO")


def test_bootstrap_ci_brackets_and_deterministic() -> None:
    import numpy as np

    vals = [0.01, -0.02, 0.03, -0.01, 0.02] * 40
    for seed in (0, 1, 7):
        point, lo, hi = block_bootstrap_ci(vals, np.mean, seed=seed)
        assert lo <= point <= hi, (seed, lo, point, hi)
    ci_a = block_bootstrap_ci(vals, np.mean, seed=5)
    ci_b = block_bootstrap_ci(vals, np.mean, seed=5)
    assert ci_a == ci_b


def test_attribute_pnl_reconciles_and_finite() -> None:
    rep = attribute_pnl({"a": [1.0, 2.0], "b": [-1.0]})
    assert rep["reconciliation_ok"] is True
    assert abs(rep["reconciled_total"] - rep["grand_total"]) <= 1e-9
    assert _json_finite(rep)


def test_compute_metrics_finite_and_sign() -> None:
    up = [100000.0 * (1.0005 ** i) for i in range(200)]
    down = [100000.0 * (0.9995 ** i) for i in range(200)]
    m_up = compute_metrics(up)
    m_down = compute_metrics(down)
    assert all(math.isfinite(v) for v in m_up.values())
    assert m_up["sharpe"] > m_down["sharpe"]
    assert m_up["ann_return"] > m_down["ann_return"]
