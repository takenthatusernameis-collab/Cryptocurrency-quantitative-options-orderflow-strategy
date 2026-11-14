"""Focused unit tests for the EVAL-41 Track B decisive-grid helpers.

These cover only the pure, deterministic helpers (position builders and the
per-window GO/pass predicate). They do NOT run the full walk-forward grid, which
is exercised by ``scripts/eval41_options_timeseries_net_of_cost.py`` itself.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_MODULE_PATH = ROOT / "scripts" / "eval41_options_timeseries_net_of_cost.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("eval41_options_timeseries_net_of_cost", _MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mod = _load_module()


def test_positions_for_long_and_short() -> None:
    sigs = [0.5, -0.5, 0.05, -0.05, 0.0]
    tox = [0.0, 0.0, 0.0, 0.0, 0.0]
    long_pos = mod.positions_for(sigs, tox, direction="long", threshold=0.1)
    short_pos = mod.positions_for(sigs, tox, direction="short", threshold=0.1)
    assert long_pos == [1, 0, 0, 0, 0]
    assert short_pos == [0, -1, 0, 0, 0]


def test_positions_for_toxicity_gate_zeroes_signal() -> None:
    sigs = [0.9, 0.9]
    tox = [0.9, 0.1]
    pos = mod.positions_for(sigs, tox, direction="long", threshold=0.1)
    assert pos == [0, 1]


def test_positions_for_threshold_monotonic() -> None:
    sigs = [0.15, 0.15, 0.15]
    tox = [0.0, 0.0, 0.0]
    assert mod.positions_for(sigs, tox, direction="long", threshold=0.1) == [1, 1, 1]
    assert mod.positions_for(sigs, tox, direction="long", threshold=0.2) == [0, 0, 0]


def test_orderflow_positions_gate() -> None:
    sigs = [0.5, -0.5, 0.0]
    tox = [0.0, 0.95, 0.0]
    assert mod.orderflow_positions(sigs, tox) == [1, 0, 0]


def test_variant_window_pass_requires_all_four() -> None:
    base = dict(
        oos_sharpe=2.0, num_trades=10, control_sharpe=1.0, permutation_p=0.01,
        ci_lo=0.5, ci_hi=3.0, distinct_levels=5, abs_ic=0.1,
    )
    assert mod._variant_window_pass(**base)["window_pass"] is True
    # Each single failure must flip the window.
    assert mod._variant_window_pass(**{**base, "oos_sharpe": 0.5})["window_pass"] is False
    assert mod._variant_window_pass(**{**base, "num_trades": 0})["window_pass"] is False
    assert mod._variant_window_pass(**{**base, "permutation_p": 0.5})["window_pass"] is False
    assert mod._variant_window_pass(**{**base, "ci_lo": -1.0, "ci_hi": 0.5})["window_pass"] is False
    assert mod._variant_window_pass(**{**base, "distinct_levels": 1})["window_pass"] is False
    assert mod._variant_window_pass(**{**base, "abs_ic": 0.0})["window_pass"] is False


def test_evaluate_variant_requires_both_windows() -> None:
    passing = dict(
        oos_sharpe=2.0, num_trades=10, control_sharpe=1.0, permutation_p=0.01,
        ci_lo=0.5, ci_hi=3.0, distinct_levels=5, abs_ic=0.1, window_pass=True,
    )
    failing = {**passing, "window_pass": False}
    both = mod._evaluate_variant(
        name="v", direction="long", threshold=0.1,
        per_window=[{"window": "a", **passing}, {"window": "b", **passing}],
    )
    assert both["passed_all_windows"] is True
    one = mod._evaluate_variant(
        name="v", direction="long", threshold=0.1,
        per_window=[{"window": "a", **passing}, {"window": "b", **failing}],
    )
    assert one["passed_all_windows"] is False