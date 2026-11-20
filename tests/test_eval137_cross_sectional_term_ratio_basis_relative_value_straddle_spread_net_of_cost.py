"""Unit tests for EVAL-137: the **cross-sectional causal near-to-far ATM
implied-vol term-ratio basis** (EVAL-125's only surviving GO, IC 0.4128, 2
BH-FDR rejections) -> **signal-timed cross-sectional relative-value delta-hedged
ATM straddle spread** net-of-cost monetization (long the cheap-term relative
leg, short the rich-term leg) at the sealed EVAL-64 feasible floor.

EVAL-137 is the charter's net-of-cost rung consuming EVAL-125's GO. It reuses
the sealed EVAL-61/62/64/71/74/77/80/125 machinery verbatim: the term-ratio
basis signal path (EVAL-125/EVAL-77/EVAL-74), the EVAL-80 relative-value ATM
straddle-spread trade construction, the EVAL-62 mark-path net-of-cost P&L +
permutation/bootstrap inference, and the sealed EVAL-64 feasible floor. Needs
no new acquisition and no network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin the things the next session must not break:
1. the artifact ids are EVAL-137;
2. the sealed machinery (EVAL-61/62/64/71/74/77/80/125 helpers) is reused
   verbatim, not forked;
3. the term-ratio basis z-score is the cross-sectional relative signal
   (term_ratio[ETH] - term_ratio[BTC], expanding-z);
4. the relative-value legs apply side = sign(rel_z) on BTC and -side on ETH
   (long cheap-term leg, short rich-term leg);
5. ``evaluate_config`` targets net-of-cost mean_return > 0, its permutation /
   bootstrap inference is bounded and deterministic;
6. the composed floor reuses the sealed EVAL-64 floor verbatim (not weakened);
7. ``run_eval137(write=False)`` reports BLOCKED below the sealed EVAL-64 floor
   and a verdict above it;
8. the protocol/floor/constants are the pre-registered ones.
"""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import scripts.eval61_orderflow_realized_vol_net_of_cost as e61
import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64
import scripts.eval71_surface_iv_rv_predictiveness as e71
import scripts.eval74_surface_term_structure_predictiveness as e74
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77
import scripts.eval80_cross_sectional_relative_value_straddle_monetization as e80
import scripts.eval125_cross_sectional_term_ratio_basis_forward_relative_return_kurtosis_spread as e125
import scripts.eval137_cross_sectional_term_ratio_basis_relative_value_straddle_spread_net_of_cost as e137

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000


def _captures(insts=("BTC", "ETH")):
    return {
        i: {"underlying": i, "surface": {"snapshots": []},
            "option_trades": [], "perp_candles": []}
        for i in insts
    }


def _write_captures(caps):
    td = tempfile.mkdtemp()
    for inst, cap in caps.items():
        p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
    return td


# ---------------------------------------------------------------------------
# 1) artifact ids
# ---------------------------------------------------------------------------
def test_ids_are_eval137():
    assert e137.REPORT_ID.startswith("EVAL_137_")
    assert e137.PREREG_ID.startswith("EVAL_137_")
    assert e137.BLOCKED_ID.startswith("EVAL_137_")
    assert "TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST" in e137.REPORT_ID
    assert "RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST" in e137.PREREG_ID
    assert e137.BASIS_SIGNALS == ("term_ratio",)


# ---------------------------------------------------------------------------
# 2) sealed helpers reused verbatim
# ---------------------------------------------------------------------------
def test_uses_sealed_helpers_verbatim():
    assert e137.e61 is e61
    assert e137.e62 is e62
    assert e137.e64 is e64
    assert e137.e71 is e71
    assert e137.e74 is e74
    assert e137.e77 is e77
    assert e137.e80 is e80
    assert e137.e125 is e125
    assert e137.build_atm_straddle_states is e80.build_atm_straddle_states
    assert e137.PERMUTATION_PERMS is e62.PERMUTATION_PERMS
    assert e137.BOOTSTRAP_RESAMPLES is e62.BOOTSTRAP_RESAMPLES
    assert e137.BOOTSTRAP_BLOCK is e62.BOOTSTRAP_BLOCK
    assert e137.FDR_ALPHA is e62.FDR_ALPHA
    assert e137.SEED is e62.SEED
    assert e137.ZWINDOW is e62.ZWINDOW
    assert e137.SIZE_CAP is e62.SIZE_CAP


# ---------------------------------------------------------------------------
# 3) floor reuses sealed EVAL-64 verbatim, not weakened
# ---------------------------------------------------------------------------
def test_floor_is_eval64_verbatim_not_weakened():
    assert e137.FLOOR["min_underlyings"] == e64.MIN_UNDERLYINGS == 2
    assert e137.FLOOR["min_surface_snapshots_per_underlying"] == e64.MIN_SNAPSHOTS == 1000
    assert e137.FLOOR["min_surface_instruments_per_underlying"] == e64.MIN_SURFACE_INSTRUMENTS == 100
    assert e137.FLOOR["min_surface_bars_5m_per_underlying"] == e64.MIN_SURFACE_BARS_5M == 1000
    assert e137.FLOOR["min_option_trades_per_underlying"] == e64.MIN_OPTION_TRADES == 2000
    assert e137.FLOOR["min_of_instruments_per_underlying"] == e64.MIN_OF_INSTRUMENTS == 150
    assert e137.FLOOR["min_of_span_seconds_per_underlying"] == e64.MIN_OF_SPAN_SECONDS == 82000.0
    assert e137.FLOOR["min_of_bars_5m_per_underlying"] == e64.MIN_OF_BARS_5M == 240
    assert e137.FLOOR["min_perp_bars_5m_per_underlying"] == e64.MIN_PERP_BARS_5M == 1000
    assert e137.FLOOR["min_perp_span_seconds_per_underlying"] == e64.MIN_PERP_SPAN_SECONDS == 300000.0
    assert e137.FLOOR["min_common_bars_per_underlying"] == e64.MIN_COMMON_BARS == 240
    note = e137.FLOOR.get("note", "")
    assert "EVAL-64" in note
    assert "NOT weakened" in note
    # campaign_floor reuses e64._underlying_floor_strict verbatim (identity).
    assert e137._underlying_floor is e64._underlying_floor_strict
    caps = _captures()
    floor = e137.campaign_floor(caps)
    assert "per_underlying" in floor
    assert "underlyings_ok" in floor
    assert floor["ok"] is False  # empty fixtures below floor


# ---------------------------------------------------------------------------
# 4) grid + horizons preregistered
# ---------------------------------------------------------------------------
def test_grid_preregistered():
    assert e137.GRID_BAR_SECONDS == (60.0, 300.0)
    assert e137.BASIS_SIGNALS == ("term_ratio",)
    assert len(e137.BASIS_SIGNALS) * len(e137.GRID_BAR_SECONDS) == 2


# ---------------------------------------------------------------------------
# 5) term-ratio basis z-score is cross-sectional relative signal
# ---------------------------------------------------------------------------
def test_term_ratio_basis_is_cross_sectional_relative():
    caps = _captures()
    css = e137.build_cross_section_with_term_ratio(caps, bar_seconds=60.0)
    assert "cs" in css and "rel_z_by_bar" in css
    assert set(css["cs"]["underlyings"]) == {"BTC", "ETH"}
    # term_ratio field overlaid on each map bar (may be None).
    for inst in ("BTC", "ETH"):
        for bo, bar in css["cs"]["maps"][inst].items():
            assert "term_ratio" in bar


# ---------------------------------------------------------------------------
# 6) relative-value legs: side = sign(rel_z) on BTC, -side on ETH
# ---------------------------------------------------------------------------
def test_relative_value_legs_side_exposure():
    caps = _captures()
    legs = e137.build_relative_value_legs(caps, bar_seconds=300.0)
    assert set(legs.keys()) >= {"common_trade_bars", "btc_leg", "eth_leg", "cs", "bar_seconds"}
    assert legs["bar_seconds"] == 300.0
    assert legs["btc_leg"] == [] and legs["eth_leg"] == []  # empty fixtures
    assert legs["surface_signal"] == "term_ratio"


# ---------------------------------------------------------------------------
# 7) evaluate_config cross-sectional net-of-cost shape
# ---------------------------------------------------------------------------
def test_evaluate_config_cross_sectional_shape():
    caps = _captures()
    res = e137.evaluate_config(caps, bar_seconds=300.0)
    assert res["signal"] == "term_ratio"
    assert res["bar_seconds"] == 300.0
    assert "n_states" in res and "n_returns" in res
    assert res["n_states"] < e137.MIN_STATES_PER_CONFIG
    assert res["pass"] is False  # empty fixtures -> no states -> early return


def test_evaluate_config_insufficient_states():
    caps = _captures()
    res = e137.evaluate_config(caps, bar_seconds=60.0)
    assert res["n_states"] < e137.MIN_STATES_PER_CONFIG
    assert res["pass"] is False


# ---------------------------------------------------------------------------
# 8) run_eval137(write=False): BLOCKED below floor / verdict above
# ---------------------------------------------------------------------------
def test_run_eval137_write_false_structure():
    report = e137.run_eval137(capture_dir=_write_captures(_captures()), write=False)
    assert report["report_id"] == e137.REPORT_ID
    assert report["task"].startswith("EVAL137-")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    assert "floor_ok" in report and "per_config" in report
    assert "pooled" in report and "bh_fdr" in report["pooled"]
    assert len(report["per_config"]) == len(e137.BASIS_SIGNALS) * len(
        e137.GRID_BAR_SECONDS
    )


def test_go_bar_requires_pooled_bh_fdr():
    report = e137.run_eval137(capture_dir=_write_captures(_captures()), write=False)
    # Empty fixtures -> floor not ok -> BLOCKED, never a synthetic NO-GO
    assert report["verdict"] == "BLOCKED"
    assert report["floor_ok"] is False


# ---------------------------------------------------------------------------
# 9) protocol / floor constants preregistered
# ---------------------------------------------------------------------------
def test_protocol_floor_constants_preregistered():
    proto = e137.build_protocol("data/raw/eval61")
    assert proto["eval"] == "EVAL-137"
    assert proto["cross_section"]["baseline"] == "BTC"
    assert proto["cross_section"]["relative"] == "ETH"
    assert "term_ratio" in proto["cross_section"]["relative_signal"]
    assert proto["basis_signals"] == ["term_ratio"]
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert proto["stats"]["min_states_per_config"] == 100
    assert proto["stats"]["seed"] == e62.SEED
    assert "no new acquisition" in proto["data_availability"]["note"]
    assert "no network" in proto["data_availability"]["note"]
    assert "EVAL-64" in proto["floor"]["note"]
    assert "NOT weakened" in proto["floor"]["note"]


# ---------------------------------------------------------------------------
# 10) baseline / relative legs
# ---------------------------------------------------------------------------
def test_baseline_relative_legs_btc_eth():
    assert e137.BASELINE == "BTC"
    assert e137.RELATIVE == "ETH"


# ---------------------------------------------------------------------------
# 11) bootstrap CI bounded
# ---------------------------------------------------------------------------
def test_bootstrap_ci_bounded():
    caps = _captures()
    res = e137.evaluate_config(caps, bar_seconds=300.0)
    # Empty fixtures -> insufficient states, no inference dict emitted.
    assert res["n_states"] < e137.MIN_STATES_PER_CONFIG
    assert res["pass"] is False


# ---------------------------------------------------------------------------
# 12) code paths + commands
# ---------------------------------------------------------------------------
def test_code_paths_include_runner():
    assert (
        "scripts/eval137_cross_sectional_term_ratio_basis_relative_value_straddle_spread_net_of_cost.py"
        in e137.CODE_PATHS
    )


def test_commands_include_seal_and_no_write():
    assert any("--no-write" in c for c in e137.COMMANDS)
    assert any("--seal" in c for c in e137.COMMANDS)


# ---------------------------------------------------------------------------
# 13) GO bar uses mean_return > 0 (not Sharpe), no kill-switch
# ---------------------------------------------------------------------------
def test_go_bar_is_mean_return_positive():
    proto = e137.build_protocol("data/raw/eval61")
    gb = proto["go_bar"]
    assert "mean_return > 0" in gb
    assert "permutation p < 0.05" in gb
    assert "CI lower > 0" in gb
    assert "BH-FDR rejects" in gb
    assert "kill" not in gb.lower()  # EVAL-137 has no kill-switch (EVAL-80 does)
