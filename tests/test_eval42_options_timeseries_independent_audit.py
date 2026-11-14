"""Focused unit tests for the EVAL-42 independent-audit helpers.

These cover only the pure, deterministic helpers: component exposure, causal
quintile/z-score positions, sign flip, the four-part pass predicate, quantile
interpolation, slice index selection and tape resolution. They do NOT run the
walk-forward audit, which is exercised by the script itself.
"""

from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
_MODULE_PATH = ROOT / "scripts" / "eval42_options_timeseries_independent_audit.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "eval42_options_timeseries_independent_audit", _MODULE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mod = _load_module()


def _sig(ts: str, **components: float) -> SimpleNamespace:
    base = {
        "forward_curve_slope": -1.0,
        "atm_iv_term_slope": -1.0,
        "iv_skew": 1.0,
        "put_call_ratio": -0.15625,
    }
    base.update(components)
    return SimpleNamespace(
        snapshot_timestamp=datetime.fromisoformat(ts.replace("Z", "+00:00")),
        options_signal_raw=components.get("_composite", 0.0),
        components=base,
    )


def test_component_signals_exposes_single_component() -> None:
    signals = [
        _sig("2026-11-14T11:35:00Z", put_call_ratio=0.25),
        _sig("2026-11-14T11:40:00Z", put_call_ratio=-0.5),
    ]
    exposed = mod.component_signals(signals, "put_call_ratio")
    assert [s.options_signal_raw for s in exposed] == [0.25, -0.5]
    assert exposed[0].snapshot_timestamp == signals[0].snapshot_timestamp
    # Originals are never mutated.
    assert signals[0].options_signal_raw == 0.0


def test_quantile_interpolation_is_causal_safe_and_bounded() -> None:
    assert mod._quantile([], 0.5) == 0.0
    assert mod._quantile([3.0], 0.9) == 3.0
    assert mod._quantile([0.0, 10.0], 0.5) == 5.0
    assert mod._quantile([0.0, 10.0], 0.0) == 0.0
    assert mod._quantile([0.0, 10.0], 1.0) == 10.0


def test_causal_quintile_positions_min_samples_and_toxicity_gate() -> None:
    sigs = [float(i) for i in range(40)]
    tox = [0.0] * 40
    pos = mod.causal_quintile_positions(sigs, tox, n_quantiles=5, min_samples=20)
    assert pos[:19] == [0] * 19
    # The live value is the maximum seen so far -> top quintile.
    assert pos[19] == 1
    assert pos[-1] == 1
    # A descending series puts the live value in the bottom quintile.
    desc = [float(-i) for i in range(40)]
    dpos = mod.causal_quintile_positions(desc, tox, n_quantiles=5, min_samples=20)
    assert dpos[19] == -1
    assert dpos[-1] == -1

    tox_gated = list(tox)
    tox_gated[-1] = 0.99
    assert mod.causal_quintile_positions(sigs, tox_gated, n_quantiles=5, min_samples=20)[-1] == 0


def test_causal_zscore_positions_sign_only_after_min_samples() -> None:
    sigs = [0.0] * 20 + [1.0, -1.0]
    tox = [0.0] * 22
    pos = mod.causal_zscore_positions(sigs, tox, window=10, min_samples=5)
    assert pos[:19] == [0] * 19
    assert pos[19] == 0  # zero deviation -> flat
    assert pos[20] == 1
    assert pos[21] == -1


def test_sign_flip_is_exact_negation_of_long_threshold() -> None:
    sigs = [0.5, -0.5, 0.0, 0.15]
    tox = [0.0, 0.0, 0.0, 0.0]
    base = mod.threshold_positions(sigs, tox, direction="long", threshold=0.2)
    # The long construction is flat on the short side by design.
    assert base == [1, 0, 0, 0]
    assert mod.sign_flip_positions(sigs, tox, threshold=0.2) == [-1, 0, 0, 0]
    assert mod.sign_flip_positions(sigs, tox, threshold=0.2) == [-p for p in base]


def test_threshold_positions_requires_strict_direction_and_gate() -> None:
    sigs = [0.5, -0.5, 0.0, 0.5]
    tox = [0.0, 0.0, 0.0, 0.9]
    assert mod.threshold_positions(sigs, tox, direction="long", threshold=0.2) == [1, 0, 0, 0]
    assert mod.threshold_positions(sigs, tox, direction="short", threshold=0.2) == [0, -1, 0, 0]


def test_pass_four_requires_every_part() -> None:
    base = dict(
        oos_sharpe=2.0, num_trades=10, control_sharpe=1.0, permutation_p=0.01,
        ci_lo=0.5, ci_hi=3.0, distinct_levels=5, abs_ic=0.1,
    )
    assert mod.pass_four(**base)["pass_four"] is True
    for field, bad in (
        ("oos_sharpe", 0.5),
        ("num_trades", 0),
        ("permutation_p", 0.05),
        ("ci_lo", -1.0),
        ("distinct_levels", 1),
        ("abs_ic", 0.0),
    ):
        broken = dict(base)
        broken[field] = bad
        assert mod.pass_four(**broken)["pass_four"] is False


def test_pass_four_negative_ci_lower_bound_still_excludes_zero() -> None:
    block = mod.pass_four(
        oos_sharpe=-2.0, num_trades=5, control_sharpe=0.0, permutation_p=0.01,
        ci_lo=-5.0, ci_hi=-1.0, distinct_levels=3, abs_ic=0.2,
    )
    assert block["ci_excludes_zero"] is True
    # A negative Sharpe is still not superior to a zero control.
    assert block["pass_four"] is False


def test_slice_indices_are_inclusive_and_ordered() -> None:
    bars = [
        datetime(2026, 11, 14, 12, minute, 0, tzinfo=timezone.utc)
        for minute in range(5)
    ]
    idxs = mod._slice_indices(bars, "2026-11-14T12:01:00Z", "2026-11-14T12:03:00Z")
    assert idxs == [1, 2, 3]
    assert mod._slice_indices(bars, None, None) == [0, 1, 2, 3, 4]
    assert mod._slice_indices(bars, "2026-11-14T13:00:00Z", None) == []


def test_resolve_inputs_reports_missing_without_substituting(tmp_path) -> None:
    fresh = tmp_path / "fresh.json"
    fresh.write_text("{}", encoding="utf-8")
    out = mod.resolve_inputs({"fresh": str(fresh), "midday": str(tmp_path / "absent.json")})
    assert out["present"] == {"fresh": str(fresh)}
    assert out["missing"] == [{"tape": "midday", "path": str(tmp_path / "absent.json")}]
    assert out["full_bar_met"] is False


def test_resolve_inputs_full_bar_when_both_present(tmp_path) -> None:
    fresh = tmp_path / "fresh.json"
    midday = tmp_path / "midday.json"
    fresh.write_text("{}", encoding="utf-8")
    midday.write_text("{}", encoding="utf-8")
    out = mod.resolve_inputs({"fresh": str(fresh), "midday": str(midday)})
    assert out["full_bar_met"] is True
    assert out["missing"] == []


def test_declared_slices_are_disjoint_pairs() -> None:
    names = [s["name"] for s in mod.SLICES]
    for required in (
        "fresh_full", "midday_full", "midday_only", "fresh_only",
        "fresh_early_half", "fresh_late_half",
    ):
        assert required in names
    early = next(s for s in mod.SLICES if s["name"] == "fresh_early_half")
    late = next(s for s in mod.SLICES if s["name"] == "fresh_late_half")
    assert early["end"] < late["start"]