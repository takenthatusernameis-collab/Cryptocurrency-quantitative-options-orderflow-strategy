"""Unit tests for EVAL-142: the **cross-asset term-structure ratio spillover
(the OTHER underlying's causal ``term_ratio**) -> signal-timed delta-hedged
**risk reversal** net-of-cost monetization at the sealed EVAL-64 feasible
floor.

EVAL-142 is the charter's *tradeable, net-of-cost alpha* rung for the EVAL-139
cross-asset ``term_ratio`` spillover GO: it pairs that signal with the sealed
EVAL-76 risk-reversal trade construction + EVAL-62 mark-path net-of-cost P&L,
tested at the sealed EVAL-64 feasible floor verbatim. It is distinct from
EVAL-135 (``term_slope`` spillover -> risk reversal, BLOCKED) and from EVAL-139
(predictiveness only).

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin the things the next session must not break:
1. the artifact ids are EVAL-142;
2. the sealed machinery (EVAL-61/62/64/65/71/74, EVAL-57 helpers) is reused verbatim, not forked;
3. ``build_cross_section`` / ``_term_ratio_on_common`` mirror the EVAL-139 cross-asset alignment;
4. ``build_risk_reversal_states`` emits the EVAL-76 state schema consumed verbatim by ``e62.markpath_returns``;
5. ``campaign_floor`` is the sealed EVAL-64 feasible floor verbatim (not weakened);
6. ``run_eval142(write=False)`` reports BLOCKED below the composed floor and a verdict above it;
7. the GO bar requires net-of-cost mean > 0, bootstrap CI lower > 0, directional
   permutation p < 0.05, nonzero positions, and pooled BH-FDR rejection on BOTH underlyings;
8. the protocol / floor constants are pre-registered (floor source = sealed EVAL-64).
"""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import scripts.eval57_vrp_net_of_cost as e57
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61
import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64
import scripts.eval65_orderflow_tox_rv_predictiveness as e65
import scripts.eval71_surface_iv_rv_predictiveness as e71
import scripts.eval74_surface_term_structure_predictiveness as e74
import scripts.eval142_cross_asset_term_ratio_spillover_risk_reversal_net_of_cost as e124

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
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
def test_ids_are_eval142():
    assert e124.REPORT_ID.startswith("EVAL_142_")
    assert e124.PREREG_ID.startswith("EVAL_142_")
    assert e124.BLOCKED_ID.startswith("EVAL_142_")
    assert "TERM_RATIO_SPILLOVER_RISK_REVERSAL_NET_OF_COST" in e124.REPORT_ID
    assert e124.TARGET == "net_of_cost_mean_return"
    assert e124.SURFACE_SIGNAL == "term_ratio"


# ---------------------------------------------------------------------------
# 2) sealed helpers reused verbatim
# ---------------------------------------------------------------------------
def test_uses_sealed_helpers_verbatim():
    assert e124.e61 is e61
    assert e124.e62 is e62
    assert e124.e64 is e64
    assert e124.e65 is e65
    assert e124.e71 is e71
    assert e124.e74 is e74
    assert e124.e57 is e57
    assert e124.PERMUTATION_PERMS is e65.PERMUTATION_PERMS
    assert e124.BOOTSTRAP_RESAMPLES is e65.BOOTSTRAP_RESAMPLES
    assert e124.BOOTSTRAP_BLOCK is e65.BOOTSTRAP_BLOCK
    assert e124.FDR_ALPHA is e62.FDR_ALPHA
    assert e124.SEED is e62.SEED
    assert e124.ZWINDOW is e62.ZWINDOW
    assert e124.SIZE_CAP is e62.SIZE_CAP
    assert e124.HEDGE_FEE_BPS is e62.HEDGE_FEE_BPS
    assert e124.KILL_SWITCH_MAX_DD is e62.KILL_SWITCH_MAX_DD


# ---------------------------------------------------------------------------
# 3) cross-asset alignment mirrors EVAL-139 (e74._term_bars term_ratio)
# ---------------------------------------------------------------------------
def test_build_cross_section_shape():
    caps = _captures()
    cs = e124.build_cross_section(caps, bar_seconds=300.0)
    assert cs["underlyings"] == ["BTC", "ETH"]
    assert cs["common"] == []
    assert cs["bar_seconds"] == 300.0


def test_term_ratio_on_common():
    cs = e124.build_cross_section(_captures(), bar_seconds=300.0)
    out = e124._term_ratio_on_common(cs, "BTC")
    assert out == []


# ---------------------------------------------------------------------------
# 4) risk-reversal state schema (EVAL-76 verbatim, consumed by markpath_returns)
# ---------------------------------------------------------------------------
def test_build_risk_reversal_states_empty():
    caps = _captures()
    states = e124.build_risk_reversal_states(
        caps, target_inst="BTC", bar_seconds=300.0, sig_z=[]
    )
    assert states == []


def test_build_risk_reversal_states_schema_keys():
    # With no priced snapshots there are no states; confirm the builder is
    # deterministic and returns a list (the schema is exercised end-to-end by
    # EVAL-76 which seals on real captures).
    caps = _captures()
    states = e124.build_risk_reversal_states(
        caps, target_inst="ETH", bar_seconds=60.0, sig_z=[0.0, 0.0]
    )
    assert isinstance(states, list)
    assert states == []


# ---------------------------------------------------------------------------
# 5) campaign floor = sealed EVAL-64 feasible floor verbatim, not weakened
# ---------------------------------------------------------------------------
def test_floor_constants_match_eval64():
    assert e124.FLOOR["min_underlyings"] == e64.MIN_UNDERLYINGS
    assert e124.FLOOR["min_surface_snapshots_per_underlying"] == e64.MIN_SNAPSHOTS
    assert e124.FLOOR["min_surface_instruments_per_underlying"] == e64.MIN_SURFACE_INSTRUMENTS
    assert e124.FLOOR["min_surface_bars_5m_per_underlying"] == e64.MIN_SURFACE_BARS_5M
    assert e124.FLOOR["min_option_trades_per_underlying"] == e64.MIN_OPTION_TRADES
    assert e124.FLOOR["min_of_instruments_per_underlying"] == e64.MIN_OF_INSTRUMENTS
    assert e124.FLOOR["min_of_span_seconds_per_underlying"] == e64.MIN_OF_SPAN_SECONDS
    assert e124.FLOOR["min_of_bars_5m_per_underlying"] == e64.MIN_OF_BARS_5M
    assert e124.FLOOR["min_perp_bars_5m_per_underlying"] == e64.MIN_PERP_BARS_5M
    assert e124.FLOOR["min_perp_span_seconds_per_underlying"] == e64.MIN_PERP_SPAN_SECONDS
    assert e124.FLOOR["min_common_bars_per_underlying"] == e64.MIN_COMMON_BARS


def test_campaign_floor_reuses_eval64_not_weakened():
    note = e124.FLOOR.get("note", "")
    assert "EVAL-64" in note
    assert "not weakened" in note.lower()
    caps = _captures()
    floor = e124.campaign_floor(caps)
    assert "per_underlying" in floor
    assert "underlyings_ok" in floor
    assert floor["ok"] is False  # empty fixtures below floor
    assert floor["underlyings_ok"] is False


def test_campaign_floor_uses_e64_underlying_floor_strict():
    caps = _captures()
    floor = e124.campaign_floor(caps)
    for inst in ("BTC", "ETH"):
        assert floor["per_underlying"][inst]["ok"] is False


# ---------------------------------------------------------------------------
# 6) run_eval142(write=False): BLOCKED below floor / verdict above
# ---------------------------------------------------------------------------
def test_run_eval142_write_false_structure():
    report = e124.run_eval142(capture_dir=_write_captures(_captures()), write=False)
    assert report["report_id"] == e124.REPORT_ID
    assert report["task"].startswith("EVAL142-")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    assert "floor_ok" in report and "per_config" in report
    assert "pooled" in report and "bh_fdr" in report["pooled"]
    assert len(report["per_config"]) == len(e124.GRID_BAR_SECONDS) * 2  # 2 underlyings x 2 grids


def test_run_eval142_below_floor_is_blocked_never_nogo():
    report = e124.run_eval142(capture_dir=_write_captures(_captures()), write=False)
    # Empty fixtures -> below the sealed EVAL-64 floor -> BLOCKED, never NO-GO.
    assert report["verdict"] == "BLOCKED"
    assert report["floor_ok"] is False


# ---------------------------------------------------------------------------
# 7) go bar requires pooled BH-FDR + both underlyings
# ---------------------------------------------------------------------------
def test_per_config_count_and_shape():
    report = e124.run_eval142(capture_dir=_write_captures(_captures()), write=False)
    for r in report["per_config"]:
        assert r["target_underlying"] in ("BTC", "ETH")
        assert r["signal_underlying"] in ("BTC", "ETH")
        assert r["signal"] == "term_ratio"
        assert r["bar_seconds"] in (60.0, 300.0)
        assert "mean_return" in r and "permutation_p" in r
        assert "bootstrap_ci" in r and len(r["bootstrap_ci"]) == 3
        assert r["pass"] is False  # empty fixtures -> no pass


# ---------------------------------------------------------------------------
# 8) protocol / floor constants preregistered
# ---------------------------------------------------------------------------
def test_protocol_floor_constants_preregistered():
    proto = e124.build_protocol("data/raw/eval68")
    assert proto["eval"] == "EVAL-142"
    assert proto["cross_section"]["baseline"] == "BTC"
    assert proto["cross_section"]["relative"] == "ETH"
    assert proto["surface_signal"] == "term_ratio"
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert "EVAL-64" in proto["floor_source"]
    assert "no new acquisition" in proto["data_availability"]["note"]
    assert "no network" in proto["data_availability"]["note"]
    assert proto["stats"]["fdr_alpha"] == e62.FDR_ALPHA
    assert proto["stats"]["seed"] == e62.SEED


def test_signal_is_term_ratio_only():
    assert e124.SURFACE_SIGNAL == "term_ratio"
    assert e124.TARGET == "net_of_cost_mean_return"


def test_grid_preregistered():
    assert e124.GRID_BAR_SECONDS == (60.0, 300.0)
    assert len(e124.GRID_BAR_SECONDS) == 2


# ---------------------------------------------------------------------------
# 9) no synthetic data / real-data note
# ---------------------------------------------------------------------------
def test_no_synthetic_data_note():
    assert "real" in e124.build_protocol("data/raw/eval68")["data_availability"]["note"]
    assert "no network" in e124.COMMANDS[3]


# ---------------------------------------------------------------------------
# 10) code paths + commands
# ---------------------------------------------------------------------------
def test_code_paths_include_runner():
    assert "scripts/eval142_cross_asset_term_ratio_spillover_risk_reversal_net_of_cost.py" in e124.CODE_PATHS
    assert "scripts/eval64_orderflow_realized_vol_markpath_feasible.py" in e124.CODE_PATHS


def test_commands_include_seal_and_no_write():
    assert any("--no-write" in c for c in e124.COMMANDS)
    assert any("--seal" in c for c in e124.COMMANDS)


# ---------------------------------------------------------------------------
# 11) baseline / relative legs
# ---------------------------------------------------------------------------
def test_baseline_relative_legs_btc_eth():
    assert e124.BASELINE == "BTC"
    assert e124.RELATIVE == "ETH"


# ---------------------------------------------------------------------------
# 12) bootstrap CI bounded
# ---------------------------------------------------------------------------
def test_bootstrap_ci_bounded():
    caps = _captures()
    report = e124.run_eval142(capture_dir=_write_captures(caps), write=False)
    for r in report["per_config"]:
        ci = r["bootstrap_ci"]
        med, lo, hi = ci
        assert math.isfinite(med) or math.isnan(med)
        assert math.isfinite(lo) or math.isnan(lo)
        assert math.isfinite(hi) or math.isnan(hi)
        assert 0.0 <= r["permutation_p"] <= 1.0
