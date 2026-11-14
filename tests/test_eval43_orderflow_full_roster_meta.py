"""Focused unit tests for the EVAL-43 full-roster meta-analysis helpers.

These cover only the pure, deterministic helpers: orderflow-only threshold
positions with the toxicity gate, the kill-switch predicate, causal IC, tape
resolution and the pooled GO-bar predicate. They do NOT run the walk-forward
meta-analysis, which is exercised by the script itself.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_MODULE_PATH = ROOT / "scripts" / "eval43_orderflow_full_roster_meta.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "eval43_orderflow_full_roster_meta", _MODULE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mod = _load_module()


def test_threshold_positions_long_short_flat_and_gate() -> None:
    sigs = [0.5, -0.5, 0.0, 0.5, -0.5]
    tox = [0.0, 0.0, 0.0, 0.9, 0.0]
    pos = mod.threshold_positions(sigs, tox, threshold=0.2, toxicity_threshold=0.7)
    assert pos == [1, -1, 0, 0, -1]


def test_threshold_positions_strict_inequality() -> None:
    # Exactly at the threshold is flat (strict >).
    assert mod.threshold_positions([0.2, -0.2], [0.0, 0.0], threshold=0.2) == [0, 0]


def test_kill_switch_breach_boundary() -> None:
    assert mod.kill_switch_breach(0.2) is False
    assert mod.kill_switch_breach(0.2000001) is True
    assert mod.kill_switch_breach(0.0) is False


def test_ic_stats_perfect_positive_and_flat() -> None:
    # prices rise linearly, so the 1-bar forward return decreases with i; a
    # decreasing signal is therefore perfectly positively correlated.
    prices = [100.0 + i for i in range(30)]
    down = [float(-i) for i in range(30)]
    ic = mod._ic_stats(down, prices, horizons=(1,))
    assert ic["ic_by_horizon"]["1"] > 0.9
    assert ic["ic_mean"] > 0.9

    flat = mod._ic_stats([0.0] * 30, prices, horizons=(1, 5))
    assert flat["ic_mean"] == 0.0
    assert flat["ic_by_horizon"]["5"] == 0.0


def test_resolve_inputs_reports_missing_without_substituting(tmp_path) -> None:
    present = tmp_path / "a.json"
    present.write_text("{}", encoding="utf-8")
    out = mod.resolve_inputs(
        {"a": str(present), "b": str(tmp_path / "absent.json")},
        default_tapes={"a": str(present), "b": str(tmp_path / "absent.json")},
    )
    assert out["present"] == {"a": str(present)}
    assert out["missing"] == [{"tape": "b", "path": str(tmp_path / "absent.json")}]
    assert out["full_roster_met"] is False


def test_resolve_inputs_full_roster(tmp_path) -> None:
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text("{}", encoding="utf-8")
    b.write_text("{}", encoding="utf-8")
    out = mod.resolve_inputs(
        {"a": str(a), "b": str(b)},
        default_tapes={"a": str(a), "b": str(b)},
    )
    assert out["full_roster_met"] is True
    assert out["missing"] == []


def _tape(name: str, sharpe: float, dd: float = 0.0) -> dict:
    return {"name": name, "oos_sharpe": sharpe, "oos_max_drawdown": dd, "kill_switch_breach": dd > 0.2}


def test_pooled_verdict_falsified_when_bar_met() -> None:
    tapes = [_tape(f"t{i}", 1.0) for i in range(3)]
    out = mod.pooled_verdict(tapes)
    assert out["passed"] is True
    assert out["verdict"] == "FALSIFIED"
    assert out["n_positive_sharpe"] == 3


def test_pooled_verdict_kill_switch_blocks_even_with_positive_sharpe() -> None:
    tapes = [_tape("a", 2.0), _tape("b", 2.0), _tape("c", 2.0, dd=0.5)]
    out = mod.pooled_verdict(tapes)
    assert out["passed"] is False
    assert out["verdict"] == "NO-GO CONFIRMED (PASS)"
    assert out["kill_switch_tapes"] == ["c"]


def test_pooled_verdict_requires_three_positive_tapes() -> None:
    tapes = [_tape("a", 1.0), _tape("b", 1.0), _tape("c", -0.5)]
    out = mod.pooled_verdict(tapes)
    assert out["passed"] is False
    assert out["n_positive_sharpe"] == 2


def test_declared_roster_has_all_five_tapes() -> None:
    assert set(mod.TAPES) == {"41a", "41b", "41c", "41d_fresh", "midday"}
    for path in mod.TAPES.values():
        assert path.endswith(".json")
        assert "synthetic" not in path.lower()