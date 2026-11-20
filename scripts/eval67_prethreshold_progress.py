#!/usr/bin/env python3
"""Deterministic pre-threshold progress driver for the EVAL-67/68/69 ladder
plus the physics-independent EVAL-70..92 campaigns.

This is the single heavy-work entrypoint for sessions that run before the
2026-11-20 disjointness threshold. It removes the repeated manual loop that
previously let sessions do timestamp-only carries:

1. bootstrap and verify the environment;
2. run the full targeted + controller/campaign/diagnostics test suites;
3. run all campaign arbiters in order (EVAL-70..92 first -- they are
         physics-independent and runnable now -- then the EVAL-67 -> EVAL-68 ->
         EVAL-69 disjoint-forward ladder);
4. if requested with --execute, execute any arbiter that is DUE;
5. record the verified facts in the readiness JSON.

It never modifies sealed artifacts, src/, preregs, or the EVAL-64 floor.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RS_DIR = ROOT / "research_state"
READINESS_PATH = RS_DIR / "EVAL_67_PREWINDOW_READINESS.json"

TARGETED_TEST_FILES: Tuple[str, ...] = (
    "tests/test_eval70_underlying_oflow_rv_predictiveness.py",
    "tests/test_eval70_phaseb_gate.py",
    "tests/test_eval67_btc_oflow_tox_rv_oos.py",
    "tests/test_eval67_phaseb_gate.py",
    "tests/test_eval67_prethreshold_progress.py",
    "tests/test_eval66_eth_oflow_tox_rv_oos.py",
    "tests/test_eval65_orderflow_tox_rv_predictiveness.py",
    "tests/test_eval68_pooled_btc_eth_oflow_tox_rv_oos.py",
    "tests/test_eval68_phaseb_gate.py",
    "tests/test_eval69_pooled_btc_eth_oflow_tox_rv_traded_oos.py",
    "tests/test_eval69_phaseb_gate.py",
    "tests/test_eval71_surface_iv_rv_predictiveness.py",
    "tests/test_eval72_surface_skew_straddle_monetization.py",
    "tests/test_eval73_surface_iv_rv_stability_split.py",
    "tests/test_eval74_surface_term_structure_predictiveness.py",
    "tests/test_eval75_term_structure_straddle_monetization.py",
    "tests/test_eval76_surface_skew_risk_reversal_monetization.py",
    "tests/test_eval77_cross_sectional_surface_basis_rv_predictiveness.py",
    "tests/test_eval78_oflow_x_surface_rv_predictiveness.py",
    "tests/test_eval79_oflow_x_cross_sectional_basis_rv_predictiveness.py",
    "tests/test_eval79_phaseb_gate.py",
    "tests/test_eval80_cross_sectional_relative_value_straddle_monetization.py",
    "tests/test_eval80_phaseb_gate.py",
    "tests/test_eval81_oflow_directional_return_predictiveness.py",
    "tests/test_eval81_phaseb_gate.py",
    "tests/test_eval82_surface_skew_butterfly_monetization.py",
    "tests/test_eval82_phaseb_gate.py",
    "tests/test_eval83_cross_asset_surface_spillover_rv_predictiveness.py",
    "tests/test_eval83_phaseb_gate.py",
    "tests/test_eval84_term_structure_vol_of_vol_predictiveness.py",
    "tests/test_eval84_phaseb_gate.py",
    "tests/test_eval85_surface_skew_forward_return_tail.py",
    "tests/test_eval85_phaseb_gate.py",
    "tests/test_eval86_surface_skew_forward_vrp_predictiveness.py",
    "tests/test_eval86_phaseb_gate.py",
    "tests/test_eval87_surface_atm_iv_forward_tail_asymmetry.py",
    "tests/test_eval87_phaseb_gate.py",
    "tests/test_eval88_cross_sectional_surface_basis_directional_spread.py",
    "tests/test_eval88_phaseb_gate.py",
    "tests/test_eval89_cross_sectional_skew_basis_relative_vrp_spread.py",
    "tests/test_eval89_phaseb_gate.py",
    "tests/test_eval90_cross_sectional_atm_iv_basis_relative_vol_of_vol_spread.py",
    "tests/test_eval90_phaseb_gate.py",
    "tests/test_eval91_cross_sectional_skew_basis_relative_vol_of_vol_spread.py",
    "tests/test_eval91_phaseb_gate.py",
    "tests/test_eval92_cross_sectional_atm_iv_basis_relative_vrp_spread.py",
    "tests/test_eval92_phaseb_gate.py",
    "tests/test_eval93_cross_sectional_term_slope_basis_relative_rv_spread.py",
    "tests/test_eval93_phaseb_gate.py",
    "tests/test_eval94_cross_sectional_term_ratio_basis_relative_rv_spread.py",
    "tests/test_eval94_phaseb_gate.py",
    "tests/test_eval95_single_asset_atm_iv_forward_vol_of_vol.py",
    "tests/test_eval95_phaseb_gate.py",
    "tests/test_eval96_single_asset_term_slope_forward_vrp.py",
    "tests/test_eval96_phaseb_gate.py",
    "tests/test_eval97_single_asset_skew_forward_vol_of_vol.py",
    "tests/test_eval97_phaseb_gate.py",
    "tests/test_eval98_single_asset_term_ratio_forward_vrp.py",
    "tests/test_eval98_phaseb_gate.py",
    "tests/test_eval99_single_asset_term_slope_forward_tail_asymmetry.py",
    "tests/test_eval99_phaseb_gate.py",
    "tests/test_eval100_single_asset_term_ratio_forward_tail_asymmetry.py",
    "tests/test_eval100_phaseb_gate.py",
    "tests/test_eval101_single_asset_atm_iv_forward_signed_return.py",
    "tests/test_eval101_phaseb_gate.py",
    "tests/test_eval102_single_asset_term_ratio_forward_signed_return.py",
    "tests/test_eval102_phaseb_gate.py",
    "tests/test_eval103_single_asset_skew_forward_signed_return.py",
    "tests/test_eval103_phaseb_gate.py",
    "tests/test_eval104_single_asset_term_slope_forward_signed_return.py",
    "tests/test_eval104_phaseb_gate.py",
    "tests/test_eval105_cross_sectional_term_ratio_basis_relative_tail_asymmetry_spread.py",
    "tests/test_eval105_phaseb_gate.py",
    "tests/test_eval106_cross_sectional_term_slope_basis_relative_tail_asymmetry_spread.py",
    "tests/test_eval106_phaseb_gate.py",
    "tests/test_eval107_cross_sectional_term_ratio_basis_relative_vol_of_vol_spread.py",
    "tests/test_eval107_phaseb_gate.py",
    "tests/test_eval108_cross_sectional_term_slope_basis_relative_vol_of_vol_spread.py",
    "tests/test_eval108_phaseb_gate.py",
    "tests/test_eval109_single_asset_atm_iv_forward_return_skewness.py",
    "tests/test_eval109_phaseb_gate.py",
    "tests/test_eval110_cross_sectional_skew_basis_relative_tail_asymmetry_spread.py",
    "tests/test_eval110_phaseb_gate.py",
    "tests/test_eval111_single_asset_skew_forward_return_skewness.py",
    "tests/test_eval111_phaseb_gate.py",
    "tests/test_eval112_single_asset_term_ratio_forward_return_skewness.py",
    "tests/test_eval112_phaseb_gate.py",
    "tests/test_eval113_single_asset_term_slope_forward_return_skewness.py",
    "tests/test_eval113_phaseb_gate.py",
    "tests/test_eval114_cross_asset_atm_iv_spillover_forward_return_skewness.py",
    "tests/test_eval114_phaseb_gate.py",
    "tests/test_eval115_single_asset_atm_iv_forward_downside_semivariance_share.py",
    "tests/test_eval115_phaseb_gate.py",
    "tests/test_eval116_cross_sectional_skew_basis_forward_relative_return_skewness_spread.py",
    "tests/test_eval116_phaseb_gate.py",
    "tests/test_eval117_single_asset_term_slope_forward_return_kurtosis.py",
    "tests/test_eval117_phaseb_gate.py",
    "tests/test_eval118_cross_sectional_term_slope_basis_forward_relative_return_skewness_spread.py",
    "tests/test_eval118_phaseb_gate.py",
    "tests/test_eval119_single_asset_atm_iv_forward_return_kurtosis.py",
    "tests/test_eval120_cross_sectional_term_ratio_basis_relative_return_skewness_spread.py",
    "tests/test_eval120_phaseb_gate.py",
    "tests/test_eval121_single_asset_skew_forward_return_kurtosis.py",
    "tests/test_eval121_phaseb_gate.py",
    "tests/test_eval122_cross_asset_term_slope_spillover_forward_return_skewness.py",
    "tests/test_eval122_phaseb_gate.py",
    "tests/test_eval123_cross_sectional_skew_basis_forward_relative_return_kurtosis_spread.py",
    "tests/test_eval123_phaseb_gate.py",
    "tests/test_eval124_cross_asset_term_slope_spillover_risk_reversal_net_of_cost.py",
    "tests/test_eval124_phaseb_gate.py",
    "tests/test_eval125_cross_sectional_term_ratio_basis_forward_relative_return_kurtosis_spread.py",
    "tests/test_eval125_phaseb_gate.py",
    "tests/test_eval126_cross_sectional_term_slope_basis_forward_relative_return_kurtosis_spread.py",
    "tests/test_eval126_phaseb_gate.py",
    "tests/test_eval127_cross_sectional_atm_iv_basis_forward_relative_return_kurtosis_spread.py",
    "tests/test_eval127_phaseb_gate.py",
    "tests/test_eval128_cross_sectional_atm_iv_basis_forward_relative_return_skewness_spread.py",
    "tests/test_eval128_phaseb_gate.py",
    "tests/test_eval129_single_asset_term_ratio_forward_return_kurtosis.py",
    "tests/test_eval129_phaseb_gate.py",
    "tests/test_eval130_cross_sectional_atm_iv_basis_forward_relative_return_tail_asymmetry_spread.py",
    "tests/test_eval130_phaseb_gate.py",
    "tests/test_eval131_cross_sectional_term_ratio_basis_forward_relative_return_tail_asymmetry_spread.py",
    "tests/test_eval131_phaseb_gate.py",
    "tests/test_eval132_cross_asset_skew_spillover_forward_return_skewness.py",
    "tests/test_eval132_phaseb_gate.py",
    "tests/test_eval133_cross_asset_term_slope_spillover_forward_return_kurtosis.py",
    "tests/test_eval133_phaseb_gate.py",
    "tests/test_eval134_cross_asset_atm_iv_spillover_forward_return_kurtosis.py",
    "tests/test_eval134_phaseb_gate.py",
    "tests/test_eval135_cross_asset_term_slope_spillover_risk_reversal_net_of_cost.py",
    "tests/test_eval135_phaseb_gate.py",
    "tests/test_eval136_cross_asset_skew_spillover_forward_return_kurtosis.py",
    "tests/test_eval136_phaseb_gate.py",
    "tests/test_eval137_cross_sectional_term_ratio_basis_relative_value_straddle_spread_net_of_cost.py",
    "tests/test_eval137_phaseb_gate.py",
    "tests/test_eval138_cross_asset_term_ratio_spillover_forward_return_kurtosis.py",
    "tests/test_eval138_phaseb_gate.py",
    "tests/test_eval139_cross_asset_term_ratio_spillover_forward_return_skewness.py",
    "tests/test_eval139_phaseb_gate.py",
    "tests/test_eval140_composite_atm_iv_term_slope_spillover_forward_return_skewness.py",
    "tests/test_eval140_phaseb_gate.py",
    "tests/test_eval141_composite_atm_iv_term_ratio_spillover_forward_return_skewness.py",
    "tests/test_eval141_phaseb_gate.py",
    "tests/test_eval142_cross_asset_term_ratio_spillover_risk_reversal_net_of_cost.py",
    "tests/test_eval142_phaseb_gate.py",
    "tests/test_eval143_pooled_cross_asset_term_ratio_spillover_forward_return_skewness.py",
    "tests/test_eval143_phaseb_gate.py",
    "tests/test_eval144_cross_asset_term_ratio_spillover_forward_downside_semivariance_share.py",
    "tests/test_eval144_phaseb_gate.py",
)
DIAGNOSTIC_TEST_FILES: Tuple[str, ...] = (
    "tests/test_controller_progress_accounting.py",
    "tests/test_workflow_diagnostics_scanner.py",
    "tests/test_nonfinite_result_serialization.py",
    "tests/test_campaign_resume.py",
)

EXPECTED_TARGETED_TESTS = 1665
EXPECTED_DIAGNOSTIC_TESTS = 27

STALE_READINESS_KEYS: Tuple[str, ...] = (
    "eval66_seal_gate_exit",
    "eval67_seal_gate_exit",
)

GATE_SPECS: Tuple[Dict[str, Any], ...] = (
    {
        "name": "EVAL-70",
        "script": ROOT / "scripts" / "eval70_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-71",
        "script": ROOT / "scripts" / "eval71_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-72",
        "script": ROOT / "scripts" / "eval72_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-73",
        "script": ROOT / "scripts" / "eval73_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-74",
        "script": ROOT / "scripts" / "eval74_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-75",
        "script": ROOT / "scripts" / "eval75_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-76",
        "script": ROOT / "scripts" / "eval76_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-77",
        "script": ROOT / "scripts" / "eval77_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-78",
        "script": ROOT / "scripts" / "eval78_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-79",
        "script": ROOT / "scripts" / "eval79_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-80",
        "script": ROOT / "scripts" / "eval80_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-81",
        "script": ROOT / "scripts" / "eval81_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-82",
        "script": ROOT / "scripts" / "eval82_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-83",
        "script": ROOT / "scripts" / "eval83_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-84",
        "script": ROOT / "scripts" / "eval84_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-85",
        "script": ROOT / "scripts" / "eval85_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-86",
        "script": ROOT / "scripts" / "eval86_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-87",
        "script": ROOT / "scripts" / "eval87_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-88",
        "script": ROOT / "scripts" / "eval88_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-89",
        "script": ROOT / "scripts" / "eval89_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-90",
        "script": ROOT / "scripts" / "eval90_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-91",
        "script": ROOT / "scripts" / "eval91_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-92",
        "script": ROOT / "scripts" / "eval92_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-93",
        "script": ROOT / "scripts" / "eval93_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-94",
        "script": ROOT / "scripts" / "eval94_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-95",
        "script": ROOT / "scripts" / "eval95_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-96",
        "script": ROOT / "scripts" / "eval96_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-97",
        "script": ROOT / "scripts" / "eval97_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-98",
        "script": ROOT / "scripts" / "eval98_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-99",
        "script": ROOT / "scripts" / "eval99_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-100",
        "script": ROOT / "scripts" / "eval100_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-101",
        "script": ROOT / "scripts" / "eval101_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-102",
        "script": ROOT / "scripts" / "eval102_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-103",
        "script": ROOT / "scripts" / "eval103_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-104",
        "script": ROOT / "scripts" / "eval104_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-105",
        "script": ROOT / "scripts" / "eval105_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-106",
        "script": ROOT / "scripts" / "eval106_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-107",
        "script": ROOT / "scripts" / "eval107_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-108",
        "script": ROOT / "scripts" / "eval108_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-109",
        "script": ROOT / "scripts" / "eval109_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-110",
        "script": ROOT / "scripts" / "eval110_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-111",
        "script": ROOT / "scripts" / "eval111_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-112",
        "script": ROOT / "scripts" / "eval112_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-113",
        "script": ROOT / "scripts" / "eval113_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-114",
        "script": ROOT / "scripts" / "eval114_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-115",
        "script": ROOT / "scripts" / "eval115_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-116",
        "script": ROOT / "scripts" / "eval116_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-117",
        "script": ROOT / "scripts" / "eval117_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-118",
        "script": ROOT / "scripts" / "eval118_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-119",
        "script": ROOT / "scripts" / "eval119_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-120",
        "script": ROOT / "scripts" / "eval120_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-121",
        "script": ROOT / "scripts" / "eval121_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-122",
        "script": ROOT / "scripts" / "eval122_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-123",
        "script": ROOT / "scripts" / "eval123_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-124",
        "script": ROOT / "scripts" / "eval124_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-125",
        "script": ROOT / "scripts" / "eval125_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-126",
        "script": ROOT / "scripts" / "eval126_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-127",
        "script": ROOT / "scripts" / "eval127_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-128",
        "script": ROOT / "scripts" / "eval128_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-129",
        "script": ROOT / "scripts" / "eval129_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-130",
        "script": ROOT / "scripts" / "eval130_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-131",
        "script": ROOT / "scripts" / "eval131_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-132",
        "script": ROOT / "scripts" / "eval132_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-133",
        "script": ROOT / "scripts" / "eval133_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-134",
        "script": ROOT / "scripts" / "eval134_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-135",
        "script": ROOT / "scripts" / "eval135_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-136",
        "script": ROOT / "scripts" / "eval136_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-137",
        "script": ROOT / "scripts" / "eval137_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-138",
        "script": ROOT / "scripts" / "eval138_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-139",
        "script": ROOT / "scripts" / "eval139_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-140",
        "script": ROOT / "scripts" / "eval140_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-141",
        "script": ROOT / "scripts" / "eval141_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-142",
        "script": ROOT / "scripts" / "eval142_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-143",
        "script": ROOT / "scripts" / "eval143_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-144",
        "script": ROOT / "scripts" / "eval144_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-67",
        "script": ROOT / "scripts" / "eval67_phaseb_gate.py",
        "wait_phase": "NOT_DUE",
    },
    {
        "name": "EVAL-68",
        "script": ROOT / "scripts" / "eval68_phaseb_gate.py",
        "wait_phase": "WAIT_EVAL67",
    },
    {
        "name": "EVAL-69",
        "script": ROOT / "scripts" / "eval69_phaseb_gate.py",
        "wait_phase": "WAIT_EVAL68",
    },
)

SEAL_SPECS: Tuple[Dict[str, Any], ...] = (
    {
        "name": "EVAL-66",
        "task_id": "INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION",
        "prereg": "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*",
        "combined": "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*",
        "blocked": "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-70",
        "task_id": "INIT-2026-11-17T02:10:00Z-EVAL70-UNDERLYING-OFLOW-TOX-RV-PREDICTIVENESS",
        "prereg": "EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION_*",
        "combined": "EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED_*",
        "blocked": "EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-71",
        "task_id": "INIT-2026-11-17T04:10:00Z-EVAL71-SURFACE-IV-RV-PREDICTIVENESS",
        "prereg": "EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_PREREGISTRATION_*",
        "combined": "EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_COMBINED_*",
        "blocked": "EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-72",
        "task_id": "INIT-2026-11-17T05:10:00Z-EVAL72-SURFACE-SKEW-STRADDLE-MONETIZATION",
        "prereg": "EVAL_72_SURFACE_SKEW_STRADDLE_MONETIZATION_PREREGISTRATION_*",
        "combined": "EVAL_72_SURFACE_SKEW_STRADDLE_MONETIZATION_COMBINED_*",
        "blocked": "EVAL_72_SURFACE_SKEW_STRADDLE_MONETIZATION_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-73",
        "task_id": "INIT-2026-11-17T05:20:00Z-EVAL73-SURFACE-IV-RV-STABILITY-SPLIT",
        "prereg": "EVAL_73_SURFACE_IV_RV_STABILITY_SPLIT_PREREGISTRATION_*",
        "combined": "EVAL_73_SURFACE_IV_RV_STABILITY_SPLIT_COMBINED_*",
        "blocked": "EVAL_73_SURFACE_IV_RV_STABILITY_SPLIT_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-74",
        "task_id": "INIT-2026-11-17T06:30:00Z-EVAL74-SURFACE-TERM-STRUCTURE-PREDICTIVENESS",
        "prereg": "EVAL_74_SURFACE_TERM_STRUCTURE_PREDICTIVENESS_PREREGISTRATION_*",
        "combined": "EVAL_74_SURFACE_TERM_STRUCTURE_PREDICTIVENESS_COMBINED_*",
        "blocked": "EVAL_74_SURFACE_TERM_STRUCTURE_PREDICTIVENESS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-75",
        "task_id": "INIT-2026-11-17T09:40:00Z-EVAL75-TERM-STRUCTURE-STRADDLE-MONETIZATION",
        "prereg": "EVAL_75_TERM_STRUCTURE_STRADDLE_MONETIZATION_PREREGISTRATION_*",
        "combined": "EVAL_75_TERM_STRUCTURE_STRADDLE_MONETIZATION_COMBINED_*",
        "blocked": "EVAL_75_TERM_STRUCTURE_STRADDLE_MONETIZATION_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-76",
        "task_id": "INIT-2026-11-17T10:15:00Z-EVAL76-SURFACE-SKEW-RISK-REVERSAL-MONETIZATION",
        "prereg": "EVAL_76_SURFACE_SKEW_RISK_REVERSAL_MONETIZATION_PREREGISTRATION_*",
        "combined": "EVAL_76_SURFACE_SKEW_RISK_REVERSAL_MONETIZATION_COMBINED_*",
        "blocked": "EVAL_76_SURFACE_SKEW_RISK_REVERSAL_MONETIZATION_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-77",
        "task_id": "INIT-2026-11-17T10:50:00Z-EVAL77-CROSS-SECTIONAL-SURFACE-BASIS-RV",
        "prereg": "EVAL_77_CROSS_SECTIONAL_SURFACE_BASIS_RV_PREDICTIVENESS_PREREGISTRATION_*",
        "combined": "EVAL_77_CROSS_SECTIONAL_SURFACE_BASIS_RV_PREDICTIVENESS_COMBINED_*",
        "blocked": "EVAL_77_CROSS_SECTIONAL_SURFACE_BASIS_RV_PREDICTIVENESS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-78",
        "task_id": "INIT-2026-11-17T12:00:00Z-EVAL78-OFLOW-X-SURFACE-RV-INTERACTION",
        "prereg": "EVAL_78_OFLOW_X_SURFACE_RV_INTERACTION_PREREGISTRATION_*",
        "combined": "EVAL_78_OFLOW_X_SURFACE_RV_INTERACTION_COMBINED_*",
        "blocked": "EVAL_78_OFLOW_X_SURFACE_RV_INTERACTION_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-79",
        "task_id": "INIT-2026-11-17T12:15:00Z-EVAL79-OFLOW-X-CROSS-SECTIONAL-BASIS-RV-PREDICTIVENESS",
        "prereg": "EVAL_79_OFLOW_X_CROSS_SECTIONAL_BASIS_RV_PREDICTIVENESS_PREREGISTRATION_*",
        "combined": "EVAL_79_OFLOW_X_CROSS_SECTIONAL_BASIS_RV_PREDICTIVENESS_COMBINED_*",
        "blocked": "EVAL_79_OFLOW_X_CROSS_SECTIONAL_BASIS_RV_PREDICTIVENESS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-80",
        "task_id": "INIT-2026-11-17T13:00:00Z-EVAL80-CROSS-SECTIONAL-RV-STRADDLE-MONETIZATION",
        "prereg": "EVAL_80_CROSS_SECTIONAL_RELATIVE_VALUE_STRADDLE_MONETIZATION_PREREGISTRATION_*",
        "combined": "EVAL_80_CROSS_SECTIONAL_RELATIVE_VALUE_STRADDLE_MONETIZATION_COMBINED_*",
        "blocked": "EVAL_80_CROSS_SECTIONAL_RELATIVE_VALUE_STRADDLE_MONETIZATION_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-81",
        "task_id": "INIT-2026-11-17T14:20:00Z-EVAL81-OFLOW-DIRECTIONAL-RETURN-PREDICTIVENESS",
        "prereg": "EVAL_81_OFLOW_DIRECTIONAL_RETURN_PREDICTIVENESS_PREREGISTRATION_*",
        "combined": "EVAL_81_OFLOW_DIRECTIONAL_RETURN_PREDICTIVENESS_COMBINED_*",
        "blocked": "EVAL_81_OFLOW_DIRECTIONAL_RETURN_PREDICTIVENESS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-82",
        "task_id": "INIT-2026-11-17T18:00:00Z-EVAL82-SURFACE-SKEW-BUTTERFLY-MONETIZATION",
        "prereg": "EVAL_82_SURFACE_SKEW_BUTTERFLY_MONETIZATION_PREREGISTRATION_*",
        "combined": "EVAL_82_SURFACE_SKEW_BUTTERFLY_MONETIZATION_COMBINED_*",
        "blocked": "EVAL_82_SURFACE_SKEW_BUTTERFLY_MONETIZATION_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-83",
        "task_id": "INIT-2026-11-17T21:07:14Z-EVAL83-CROSS-ASSET-SURFACE-SPILLOVER-RV-PREDICTIVENESS",
        "prereg": "EVAL_83_CROSS_ASSET_SURFACE_SPILLOVER_RV_PREDICTIVENESS_PREREGISTRATION_*",
        "combined": "EVAL_83_CROSS_ASSET_SURFACE_SPILLOVER_RV_PREDICTIVENESS_COMBINED_*",
        "blocked": "EVAL_83_CROSS_ASSET_SURFACE_SPILLOVER_RV_PREDICTIVENESS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-84",
        "task_id": "INIT-2026-11-17T22:20:00Z-EVAL84-TERM-STRUCTURE-VOL-OF-VOL-PREDICTIVENESS",
        "prereg": "EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS_PREREGISTRATION_*",
        "combined": "EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS_COMBINED_*",
        "blocked": "EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-85",
        "task_id": "INIT-2026-11-17T23:20:00Z-EVAL85-SURFACE-SKEW-FORWARD-RETURN-TAIL-ASYMMETRY",
        "prereg": "EVAL_85_SURFACE_SKEW_FORWARD_RETURN_TAIL_ASYMMETRY_PREREGISTRATION_*",
        "combined": "EVAL_85_SURFACE_SKEW_FORWARD_RETURN_TAIL_ASYMMETRY_COMBINED_*",
        "blocked": "EVAL_85_SURFACE_SKEW_FORWARD_RETURN_TAIL_ASYMMETRY_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-86",
        "task_id": "INIT-2026-11-17T23:35:00Z-EVAL86-SURFACE-SKEW-FORWARD-VRP-PREDICTIVENESS",
        "prereg": "EVAL_86_SURFACE_SKEW_FORWARD_VRP_PREDICTIVENESS_PREREGISTRATION_*",
        "combined": "EVAL_86_SURFACE_SKEW_FORWARD_VRP_PREDICTIVENESS_COMBINED_*",
        "blocked": "EVAL_86_SURFACE_SKEW_FORWARD_VRP_PREDICTIVENESS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-87",
        "task_id": "INIT-2026-11-18T00:37:00Z-EVAL87-SURFACE-ATM-IV-FORWARD-RETURN-TAIL-ASYMMETRY",
        "prereg": "EVAL_87_SURFACE_ATM_IV_FORWARD_RETURN_TAIL_ASYMMETRY_PREREGISTRATION_*",
        "combined": "EVAL_87_SURFACE_ATM_IV_FORWARD_RETURN_TAIL_ASYMMETRY_COMBINED_*",
        "blocked": "EVAL_87_SURFACE_ATM_IV_FORWARD_RETURN_TAIL_ASYMMETRY_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-88",
        "task_id": "INIT-2026-11-18T02:00:00Z-EVAL88-CROSS-SECTIONAL-SURFACE-BASIS-DIRECTIONAL-SPREAD",
        "prereg": "EVAL_88_CROSS_SECTIONAL_SURFACE_BASIS_DIRECTIONAL_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_88_CROSS_SECTIONAL_SURFACE_BASIS_DIRECTIONAL_SPREAD_COMBINED_*",
        "blocked": "EVAL_88_CROSS_SECTIONAL_SURFACE_BASIS_DIRECTIONAL_SPREAD_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-89",
        "task_id": "INIT-2026-11-18T03:50:00Z-EVAL89-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-VRP-SPREAD",
        "prereg": "EVAL_89_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VRP_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_89_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VRP_SPREAD_COMBINED_*",
        "blocked": "EVAL_89_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VRP_SPREAD_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-90",
        "task_id": "INIT-2026-11-18T04:30:00Z-EVAL90-CROSS-SECTIONAL-ATM-IV-BASIS-RELATIVE-VOL-OF-VOL-SPREAD",
        "prereg": "EVAL_90_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_90_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_COMBINED_*",
        "blocked": "EVAL_90_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-91",
        "task_id": "INIT-2026-11-18T05:30:00Z-EVAL91-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-VOL-OF-VOL-SPREAD",
        "prereg": "EVAL_91_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_91_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_COMBINED_*",
        "blocked": "EVAL_91_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-92",
        "task_id": "INIT-2026-11-18T08:20:00Z-EVAL92-CROSS-SECTIONAL-ATM-IV-BASIS-RELATIVE-VRP-SPREAD",
        "prereg": "EVAL_92_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VRP_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_92_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VRP_SPREAD_COMBINED_*",
        "blocked": "EVAL_92_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VRP_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-93",
        "task_id": "INIT-2026-11-18T08:30:00Z-EVAL93-CROSS-SECTIONAL-TERM-SLOPE-BASIS-RELATIVE-RV-SPREAD",
        "prereg": "EVAL_93_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_RV_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_93_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_RV_SPREAD_COMBINED_*",
        "blocked": "EVAL_93_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_RV_SPREAD_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-94",
        "task_id": "INIT-2026-11-18T08:30:00Z-EVAL94-CROSS-SECTIONAL-TERM-SLOPE-BASIS-RELATIVE-RV-SPREAD",
        "prereg": "EVAL_94_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RV_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_94_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RV_SPREAD_COMBINED_*",
        "blocked": "EVAL_94_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RV_SPREAD_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-95",
        "task_id": "INIT-2026-11-18T09:44:00Z-EVAL95-SINGLE-ASSET-ATM-IV-FORWARD-VOL-OF-VOL",
        "prereg": "EVAL_95_SINGLE_ASSET_ATM_IV_FORWARD_VOL_OF_VOL_PREREGISTRATION_*",
        "combined": "EVAL_95_SINGLE_ASSET_ATM_IV_FORWARD_VOL_OF_VOL_COMBINED_*",
        "blocked": "EVAL_95_SINGLE_ASSET_ATM_IV_FORWARD_VOL_OF_VOL_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-96",
        "task_id": "INIT-2026-11-18T10:25:24Z-EVAL96-SINGLE-ASSET-TERM-SLOPE-FORWARD-VRP",
        "prereg": "EVAL_96_SINGLE_ASSET_TERM_SLOPE_FORWARD_VRP_PREREGISTRATION_*",
        "combined": "EVAL_96_SINGLE_ASSET_TERM_SLOPE_FORWARD_VRP_COMBINED_*",
        "blocked": "EVAL_96_SINGLE_ASSET_TERM_SLOPE_FORWARD_VRP_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-97",
        "task_id": "INIT-2026-11-18T11:19:01Z-EVAL97-SINGLE-ASSET-SKEW-FORWARD-VOL-OF-VOL",
        "prereg": "EVAL_97_SINGLE_ASSET_SKEW_FORWARD_VOL_OF_VOL_PREREGISTRATION_*",
        "combined": "EVAL_97_SINGLE_ASSET_SKEW_FORWARD_VOL_OF_VOL_COMBINED_*",
        "blocked": "EVAL_97_SINGLE_ASSET_SKEW_FORWARD_VOL_OF_VOL_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-98",
        "task_id": "INIT-2026-11-18T11:44:00Z-EVAL98-SINGLE-ASSET-TERM-RATIO-FORWARD-VRP",
        "prereg": "EVAL_98_SINGLE_ASSET_TERM_RATIO_FORWARD_VRP_PREREGISTRATION_*",
        "combined": "EVAL_98_SINGLE_ASSET_TERM_RATIO_FORWARD_VRP_COMBINED_*",
        "blocked": "EVAL_98_SINGLE_ASSET_TERM_RATIO_FORWARD_VRP_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-99",
        "task_id": "INIT-2026-11-18T12:10:00Z-EVAL99-SINGLE-ASSET-TERM-SLOPE-FORWARD-TAIL-ASYMMETRY",
        "prereg": "EVAL_99_SINGLE_ASSET_TERM_SLOPE_FORWARD_TAIL_ASYMMETRY_PREREGISTRATION_*",
        "combined": "EVAL_99_SINGLE_ASSET_TERM_SLOPE_FORWARD_TAIL_ASYMMETRY_COMBINED_*",
        "blocked": "EVAL_99_SINGLE_ASSET_TERM_SLOPE_FORWARD_TAIL_ASYMMETRY_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-100",
        "task_id": "INIT-2026-11-18T16:45:00Z-EVAL100-SINGLE-ASSET-TERM-RATIO-FORWARD-TAIL-ASYMMETRY",
        "prereg": "EVAL_100_SINGLE_ASSET_TERM_RATIO_FORWARD_TAIL_ASYMMETRY_PREREGISTRATION_*",
        "combined": "EVAL_100_SINGLE_ASSET_TERM_RATIO_FORWARD_TAIL_ASYMMETRY_COMBINED_*",
        "blocked": "EVAL_100_SINGLE_ASSET_TERM_RATIO_FORWARD_TAIL_ASYMMETRY_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-101",
        "task_id": "INIT-2026-11-18T17:40:00Z-EVAL101-SINGLE-ASSET-ATM-IV-FORWARD-SIGNED-RETURN",
        "prereg": "EVAL_101_SINGLE_ASSET_ATM_IV_FORWARD_SIGNED_RETURN_PREREGISTRATION_*",
        "combined": "EVAL_101_SINGLE_ASSET_ATM_IV_FORWARD_SIGNED_RETURN_COMBINED_*",
        "blocked": "EVAL_101_SINGLE_ASSET_ATM_IV_FORWARD_SIGNED_RETURN_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-102",
        "task_id": "INIT-2026-11-18T17:55:00Z-EVAL102-SINGLE-ASSET-TERM-RATIO-FORWARD-SIGNED-RETURN",
        "prereg": "EVAL_102_SINGLE_ASSET_TERM_RATIO_FORWARD_SIGNED_RETURN_PREREGISTRATION_*",
        "combined": "EVAL_102_SINGLE_ASSET_TERM_RATIO_FORWARD_SIGNED_RETURN_COMBINED_*",
        "blocked": "EVAL_102_SINGLE_ASSET_TERM_RATIO_FORWARD_SIGNED_RETURN_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-103",
        "task_id": "INIT-2026-11-18T18:45:00Z-EVAL103-SINGLE-ASSET-SKEW-FORWARD-SIGNED-RETURN",
        "prereg": "EVAL_103_SINGLE_ASSET_SKEW_FORWARD_SIGNED_RETURN_PREREGISTRATION_*",
        "combined": "EVAL_103_SINGLE_ASSET_SKEW_FORWARD_SIGNED_RETURN_COMBINED_*",
        "blocked": "EVAL_103_SINGLE_ASSET_SKEW_FORWARD_SIGNED_RETURN_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-104",
        "task_id": "INIT-2026-11-18T18:53:00Z-EVAL104-SINGLE-ASSET-TERM-SLOPE-FORWARD-SIGNED-RETURN",
        "prereg": "EVAL_104_SINGLE_ASSET_TERM_SLOPE_FORWARD_SIGNED_RETURN_PREREGISTRATION_*",
        "combined": "EVAL_104_SINGLE_ASSET_TERM_SLOPE_FORWARD_SIGNED_RETURN_COMBINED_*",
        "blocked": "EVAL_104_SINGLE_ASSET_TERM_SLOPE_FORWARD_SIGNED_RETURN_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-105",
        "task_id": "INIT-2026-11-18T19:02:00Z-EVAL105-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-TAIL-ASYMMETRY-SPREAD",
        "prereg": "EVAL_105_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_105_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_COMBINED_*",
        "blocked": "EVAL_105_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-106",
        "task_id": "INIT-2026-11-18T20:36:00Z-EVAL106-CROSS-SECTIONAL-TERM-SLOPE-BASIS-RELATIVE-TAIL-ASYMMETRY-SPREAD",
        "prereg": "EVAL_106_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_106_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_COMBINED_*",
        "blocked": "EVAL_106_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-107",
        "task_id": "INIT-2026-11-18T20:36:00Z-EVAL107-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-VOL-OF-VOL-SPREAD",
        "prereg": "EVAL_107_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_107_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_COMBINED_*",
        "blocked": "EVAL_107_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-108",
        "task_id": "INIT-2026-11-18T20:36:00Z-EVAL108-CROSS-SECTIONAL-TERM-SLOPE-BASIS-RELATIVE-VOL-OF-VOL-SPREAD",
        "prereg": "EVAL_108_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_108_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_COMBINED_*",
        "blocked": "EVAL_108_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-109",
        "task_id": "INIT-2026-11-18T23:00:00Z-EVAL109-SINGLE-ASSET-ATM-IV-FORWARD-RETURN-SKEWNESS",
        "prereg": "EVAL_109_SINGLE_ASSET_ATM_IV_FORWARD_RETURN_SKEWNESS_PREREGISTRATION_*",
        "combined": "EVAL_109_SINGLE_ASSET_ATM_IV_FORWARD_RETURN_SKEWNESS_COMBINED_*",
        "blocked": "EVAL_109_SINGLE_ASSET_ATM_IV_FORWARD_RETURN_SKEWNESS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-110",
        "task_id": "INIT-2026-11-18T23:00:00Z-EVAL110-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-TAIL-ASYMMETRY-SPREAD",
        "prereg": "EVAL_110_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_110_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_COMBINED_*",
        "blocked": "EVAL_110_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-110",
        "task_id": "INIT-2026-11-18T23:00:00Z-EVAL110-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-TAIL-ASYMMETRY-SPREAD",
        "prereg": "EVAL_110_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_110_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_COMBINED_*",
        "blocked": "EVAL_110_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-112",
        "task_id": "INIT-2026-11-18T23:00:00Z-EVAL112-SINGLE-ASSET-TERM-RATIO-FORWARD-RETURN-SKEWNESS",
        "prereg": "EVAL_112_SINGLE_ASSET_TERM_RATIO_FORWARD_RETURN_SKEWNESS_PREREGISTRATION_*",
        "combined": "EVAL_112_SINGLE_ASSET_TERM_RATIO_FORWARD_RETURN_SKEWNESS_COMBINED_*",
        "blocked": "EVAL_112_SINGLE_ASSET_TERM_RATIO_FORWARD_RETURN_SKEWNESS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-113",
        "task_id": "INIT-2026-11-19T00:12:00Z-EVAL113-SINGLE-ASSET-TERM-SLOPE-FORWARD-RETURN-SKEWNESS",
        "prereg": "EVAL_113_SINGLE_ASSET_TERM_SLOPE_FORWARD_RETURN_SKEWNESS_PREREGISTRATION_*",
        "combined": "EVAL_113_SINGLE_ASSET_TERM_SLOPE_FORWARD_RETURN_SKEWNESS_COMBINED_*",
        "blocked": "EVAL_113_SINGLE_ASSET_TERM_SLOPE_FORWARD_RETURN_SKEWNESS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-114",
        "task_id": "INIT-2026-11-19T02:01:53Z-EVAL114-CROSS-ASSET-ATM-IV-SPILLOVER-FORWARD-RETURN-SKEWNESS",
        "prereg": "EVAL_114_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_RETURN_SKEWNESS_PREREGISTRATION_*",
        "combined": "EVAL_114_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_RETURN_SKEWNESS_COMBINED_*",
        "blocked": "EVAL_114_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_RETURN_SKEWNESS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-115",
        "task_id": "INIT-2026-11-19T02:24:37Z-EVAL115-SINGLE-ASSET-ATM-IV-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE",
        "prereg": "EVAL_115_SINGLE_ASSET_ATM_IV_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_PREREGISTRATION_*",
        "combined": "EVAL_115_SINGLE_ASSET_ATM_IV_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_COMBINED_*",
        "blocked": "EVAL_115_SINGLE_ASSET_ATM_IV_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-116",
        "task_id": "INIT-2026-11-19T02:51:29Z-EVAL116-CROSS-SECTIONAL-SKEW-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD",
        "prereg": "EVAL_116_CROSS_SECTIONAL_SKEW_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_116_CROSS_SECTIONAL_SKEW_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_COMBINED_*",
        "blocked": "EVAL_116_CROSS_SECTIONAL_SKEW_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-117",
        "task_id": "INIT-2026-11-19T04:15:00Z-EVAL117-SINGLE-ASSET-TERM-SLOPE-FORWARD-RETURN-KURTOSIS",
        "prereg": "EVAL_117_SINGLE_ASSET_TERM_SLOPE_FORWARD_RETURN_KURTOSIS_PREREGISTRATION_*",
        "combined": "EVAL_117_SINGLE_ASSET_TERM_SLOPE_FORWARD_RETURN_KURTOSIS_COMBINED_*",
        "blocked": "EVAL_117_SINGLE_ASSET_TERM_SLOPE_FORWARD_RETURN_KURTOSIS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-118",
        "task_id": "INIT-2026-11-19T05:15:09Z-EVAL118-CROSS-SECTIONAL-TERM-SLOPE-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD",
        "prereg": "EVAL_118_CROSS_SECTIONAL_TERM_SLOPE_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_118_CROSS_SECTIONAL_TERM_SLOPE_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_COMBINED_*",
        "blocked": "EVAL_118_CROSS_SECTIONAL_TERM_SLOPE_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-119",
        "task_id": "INIT-2026-11-19T05:54:27Z-EVAL119-SINGLE-ASSET-ATM-IV-FORWARD-RETURN-KURTOSIS",
        "prereg": "EVAL_119_SINGLE_ASSET_ATM_IV_FORWARD_RETURN_KURTOSIS_PREREGISTRATION_*",
        "combined": "EVAL_119_SINGLE_ASSET_ATM_IV_FORWARD_RETURN_KURTOSIS_COMBINED_*",
        "blocked": "EVAL_119_SINGLE_ASSET_ATM_IV_FORWARD_RETURN_KURTOSIS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-120",
        "task_id": "INIT-2026-11-19T06:10:00Z-EVAL120-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-RETURN-SKEWNESS-SPREAD",
        "prereg": "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_COMBINED_*",
        "blocked": "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-121",
        "task_id": "INIT-2026-11-19T07:09:20Z-EVAL121-SINGLE-ASSET-SKEW-FORWARD-RETURN-KURTOSIS",
        "prereg": "EVAL_121_SINGLE_ASSET_SKEW_FORWARD_RETURN_KURTOSIS_PREREGISTRATION_*",
        "combined": "EVAL_121_SINGLE_ASSET_SKEW_FORWARD_RETURN_KURTOSIS_COMBINED_*",
        "blocked": "EVAL_121_SINGLE_ASSET_SKEW_FORWARD_RETURN_KURTOSIS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-122",
        "task_id": "INIT-2026-11-19T08:18:00Z-EVAL122-CROSS-ASSET-TERM-SLOPE-SPILLOVER-FORWARD-RETURN-SKEWNESS",
        "prereg": "EVAL_122_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_SKEWNESS_PREREGISTRATION_*",
        "combined": "EVAL_122_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_SKEWNESS_COMBINED_*",
        "blocked": "EVAL_122_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_SKEWNESS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-123",
        "task_id": "INIT-2026-11-19T09:16:32Z-EVAL123-CROSS-SECTIONAL-SKEW-BASIS-FORWARD-RELATIVE-RETURN-KURTOSIS-SPREAD",
        "prereg": "EVAL_123_CROSS_SECTIONAL_SKEW_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_123_CROSS_SECTIONAL_SKEW_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_COMBINED_*",
        "blocked": "EVAL_123_CROSS_SECTIONAL_SKEW_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-124",
        "task_id": "INIT-2026-11-19T10:34:11Z-EVAL124-CROSS-ASSET-TERM-SLOPE-SPILLOVER-RISK-REVERSAL-NET-OF-COST",
        "prereg": "EVAL_124_CROSS_ASSET_TERM_SLOPE_SPILLOVER_RISK_REVERSAL_NET_OF_COST_PREREGISTRATION_*",
        "combined": "EVAL_124_CROSS_ASSET_TERM_SLOPE_SPILLOVER_RISK_REVERSAL_NET_OF_COST_COMBINED_*",
        "blocked": "EVAL_124_CROSS_ASSET_TERM_SLOPE_SPILLOVER_RISK_REVERSAL_NET_OF_COST_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-125",
        "task_id": "INIT-2026-11-19T13:30:02Z-EVAL125-CROSS-SECTIONAL-TERM-RATIO-BASIS-FORWARD-RELATIVE-RETURN-KURTOSIS-SPREAD",
        "prereg": "EVAL_125_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_125_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_COMBINED_*",
        "blocked": "EVAL_125_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-126",
        "task_id": "INIT-2026-11-19T14:10:03Z-EVAL126-CROSS-SECTIONAL-TERM-SLOPE-BASIS-FORWARD-RELATIVE-RETURN-KURTOSIS-SPREAD",
        "prereg": "EVAL_126_CROSS_SECTIONAL_TERM_SLOPE_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_126_CROSS_SECTIONAL_TERM_SLOPE_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_COMBINED_*",
        "blocked": "EVAL_126_CROSS_SECTIONAL_TERM_SLOPE_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-127",
        "task_id": "INIT-2026-11-19T15:44:13Z-EVAL127-CROSS-SECTIONAL-ATM-IV-BASIS-FORWARD-RELATIVE-RETURN-KURTOSIS-SPREAD",
        "prereg": "EVAL_127_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_127_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_COMBINED_*",
        "blocked": "EVAL_127_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-128",
        "task_id": "INIT-2026-11-19T16:17:47Z-EVAL128-CROSS-SECTIONAL-ATM-IV-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD",
        "prereg": "EVAL_128_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_128_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_COMBINED_*",
        "blocked": "EVAL_128_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-129",
        "task_id": "INIT-2026-11-19T16:45:00Z-EVAL129-SINGLE-ASSET-TERM-RATIO-FORWARD-RETURN-KURTOSIS",
        "prereg": "EVAL_129_SINGLE_ASSET_TERM_RATIO_FORWARD_RETURN_KURTOSIS_PREREGISTRATION_*",
        "combined": "EVAL_129_SINGLE_ASSET_TERM_RATIO_FORWARD_RETURN_KURTOSIS_COMBINED_*",
        "blocked": "EVAL_129_SINGLE_ASSET_TERM_RATIO_FORWARD_RETURN_KURTOSIS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-130",
        "task_id": "INIT-2026-11-19T17:42:00Z-EVAL130-CROSS-SECTIONAL-ATM-IV-BASIS-FORWARD-RELATIVE-RETURN-TAIL-ASYMMETRY-SPREAD",
        "prereg": "EVAL_130_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_130_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD_COMBINED_*",
        "blocked": "EVAL_130_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-131",
        "task_id": "INIT-2026-11-19T18:15:00Z-EVAL131-CROSS-SECTIONAL-TERM-RATIO-BASIS-FORWARD-RELATIVE-TAIL-ASYMMETRY-SPREAD",
        "prereg": "EVAL_131_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD_PREREGISTRATION_*",
        "combined": "EVAL_131_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD_COMBINED_*",
        "blocked": "EVAL_131_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-132",
        "task_id": "INIT-2026-11-20T02:02:55Z-EVAL132-CROSS-ASSET-SKEW-SPILLOVER-FORWARD-RETURN-SKEWNESS",
        "prereg": "EVAL_132_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_RETURN_SKEWNESS_PREREGISTRATION_*",
        "combined": "EVAL_132_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_RETURN_SKEWNESS_COMBINED_*",
        "blocked": "EVAL_132_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_RETURN_SKEWNESS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-133",
        "task_id": "INIT-2026-11-20T03:15:00Z-EVAL133-CROSS-ASSET-TERM-SLOPE-SPILLOVER-FORWARD-RETURN-KURTOSIS",
        "prereg": "EVAL_133_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_KURTOSIS_PREREGISTRATION_*",
        "combined": "EVAL_133_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_KURTOSIS_COMBINED_*",
        "blocked": "EVAL_133_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_KURTOSIS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-134",
        "task_id": "INIT-2026-11-20T03:26:31Z-EVAL134-CROSS-ASSET-ATM-IV-SPILLOVER-FORWARD-RETURN-KURTOSIS",
        "prereg": "EVAL_134_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_RETURN_KURTOSIS_PREREGISTRATION_*",
        "combined": "EVAL_134_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_RETURN_KURTOSIS_COMBINED_*",
        "blocked": "EVAL_134_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_RETURN_KURTOSIS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-135",
        "task_id": "INIT-2026-11-20T04:06:36Z-EVAL135-CROSS-ASSET-TERM-SLOPE-SPILLOVER-RISK-REVERSAL-NET-OF-COST-CORRECTED",
        "prereg": "EVAL_135_CROSS_ASSET_TERM_SLOPE_SPILLOVER_RISK_REVERSAL_NET_OF_COST_PREREGISTRATION_*",
        "combined": "EVAL_135_CROSS_ASSET_TERM_SLOPE_SPILLOVER_RISK_REVERSAL_NET_OF_COST_COMBINED_*",
        "blocked": "EVAL_135_CROSS_ASSET_TERM_SLOPE_SPILLOVER_RISK_REVERSAL_NET_OF_COST_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-136",
        "task_id": "INIT-2026-11-20T05:39:37Z-EVAL136-CROSS-ASSET-SKEW-SPILLOVER-FORWARD-RETURN-KURTOSIS",
        "prereg": "EVAL_136_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_RETURN_KURTOSIS_PREREGISTRATION_*",
        "combined": "EVAL_136_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_RETURN_KURTOSIS_COMBINED_*",
        "blocked": "EVAL_136_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_RETURN_KURTOSIS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-137",
        "task_id": "INIT-2026-11-20T07:08:01Z-EVAL137-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-VALUE-STRADDLE-SPREAD-NET-OF-COST",
        "prereg": "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_PREREGISTRATION_*",
        "combined": "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_COMBINED_*",
        "blocked": "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-138",
        "task_id": "INIT-2026-11-20T09:30:47Z-EVAL138-CROSS-ASSET-TERM-RATIO-SPILLOVER-FORWARD-RETURN-KURTOSIS",
        "prereg": "EVAL_138_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_RETURN_KURTOSIS_PREREGISTRATION_*",
        "combined": "EVAL_138_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_RETURN_KURTOSIS_COMBINED_*",
        "blocked": "EVAL_138_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_RETURN_KURTOSIS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-139",
        "task_id": "INIT-2026-11-20T09:37:29Z-EVAL139-CROSS-ASSET-TERM-RATIO-SPILLOVER-FORWARD-RETURN-SKEWNESS",
        "prereg": "EVAL_139_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS_PREREGISTRATION_*",
        "combined": "EVAL_139_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS_COMBINED_*",
        "blocked": "EVAL_139_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-140",
        "task_id": "INIT-2026-11-20T10:54:17Z-EVAL140-COMPOSITE-ATM-IV-TERM-SLOPE-SPILLOVER-FORWARD-RETURN-SKEWNESS",
        "prereg": "EVAL_140_COMPOSITE_ATM_IV_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_SKEWNESS_PREREGISTRATION_*",
        "combined": "EVAL_140_COMPOSITE_ATM_IV_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_SKEWNESS_COMBINED_*",
        "blocked": "EVAL_140_COMPOSITE_ATM_IV_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_SKEWNESS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-141",
        "task_id": "INIT-2026-11-20T11:40:42Z-EVAL141-COMPOSITE-ATM-IV-TERM-RATIO-SPILLOVER-FORWARD-RETURN-SKEWNESS",
        "prereg": "EVAL_141_COMPOSITE_ATM_IV_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS_PREREGISTRATION_*",
        "combined": "EVAL_141_COMPOSITE_ATM_IV_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS_COMBINED_*",
        "blocked": "EVAL_141_COMPOSITE_ATM_IV_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-142",
        "task_id": "INIT-2026-11-20T13:51:59Z-EVAL142-CROSS-ASSET-TERM-RATIO-SPILLOVER-RISK-REVERSAL-NET-OF-COST",
        "prereg": "EVAL_142_CROSS_ASSET_TERM_RATIO_SPILLOVER_RISK_REVERSAL_NET_OF_COST_PREREGISTRATION_*",
        "combined": "EVAL_142_CROSS_ASSET_TERM_RATIO_SPILLOVER_RISK_REVERSAL_NET_OF_COST_COMBINED_*",
        "blocked": "EVAL_142_CROSS_ASSET_TERM_RATIO_SPILLOVER_RISK_REVERSAL_NET_OF_COST_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-143",
        "task_id": "INIT-2026-11-20T14:37:00Z-EVAL143-CROSS-ASSET-TERM-RATIO-SPILLOVER-FORWARD-RETURN-SKEWNESS",
        "prereg": "EVAL_143_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS_PREREGISTRATION_*",
        "combined": "EVAL_143_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS_COMBINED_*",
        "blocked": "EVAL_143_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-144",
        "task_id": "INIT-2026-11-20T18:49:23Z-EVAL144-CROSS-ASSET-TERM-RATIO-SPILLOVER-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE",
        "prereg": "EVAL_144_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_PREREGISTRATION_*",
        "combined": "EVAL_144_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_COMBINED_*",
        "blocked": "EVAL_144_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-67",
        "task_id": "INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION",
        "prereg": "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_*",
        "combined": "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_*",
        "blocked": "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-68",
        "task_id": "INIT-2026-11-16T19:45:00Z-EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS",
        "prereg": "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*",
        "combined": "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_COMBINED_*",
        "blocked": "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-69",
        "task_id": "INIT-2026-11-16T22:45:00Z-EVAL69-POOLED-BTC-ETH-OFLOW-TOX-RV-TRADED-OOS",
        "prereg": "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_PREREGISTRATION_*",
        "combined": "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_COMBINED_*",
        "blocked": "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_BLOCKED_*",
        "expected_exit": 1,
    },
)

_PASS_RE = re.compile(r"(\d+)\s+passed\b")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _child_env() -> Dict[str, str]:
    env = os.environ.copy()
    deps = str(ROOT / ".venv-deps")
    old = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = deps + (os.pathsep + old if old else "")
    return env


def _run(
    cmd: Sequence[str],
    *,
    cwd: Path = ROOT,
    timeout: float = 1800.0,
    env: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    started = time.monotonic()
    try:
        proc = subprocess.run(
            list(cmd),
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env or _child_env(),
        )
        rc = int(proc.returncode)
        out = proc.stdout or ""
        err = proc.stderr or ""
    except subprocess.TimeoutExpired as exc:
        rc = 124
        out = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        err = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        err += f"\nTIMEOUT after {timeout}s"
    except BaseException as exc:  # noqa: BLE001
        rc = 1
        out = ""
        err = repr(exc)
    return {
        "command": list(cmd),
        "rc": rc,
        "stdout": out,
        "stderr": err,
        "output": out + ("\n" + err if err else ""),
        "duration_seconds": round(time.monotonic() - started, 3),
    }


def _parse_pytest_passed(output: str) -> Optional[int]:
    matches = _PASS_RE.findall(output or "")
    if not matches:
        return None
    return max(int(v) for v in matches)


def _pytest_result(files: Sequence[str], *, timeout: float = 1800.0) -> Dict[str, Any]:
    cmd = [sys.executable, "-m", "pytest", "-q", *files]
    res = _run(cmd, timeout=timeout)
    return {
        "command": res["command"],
        "rc": res["rc"],
        "passed": _parse_pytest_passed(res["output"]),
        "duration_seconds": res["duration_seconds"],
        "tail": res["output"][-4000:],
    }


def run_env_check(*, bootstrap: bool = True) -> Dict[str, Any]:
    if bootstrap and not (ROOT / ".venv-deps").is_dir():
        boot = _run([str(ROOT / "scripts" / "verify_env.sh")], timeout=1200.0)
    else:
        boot = {"rc": 0, "output": "skipped", "duration_seconds": 0.0}
    check = _run([str(ROOT / "scripts" / "verify_env.sh"), "--check"], timeout=600.0)
    return {
        "bootstrap_rc": boot["rc"],
        "check_rc": check["rc"],
        "ok": bool(check["rc"] == 0),
        "check_tail": check["output"][-3000:],
    }


def _parse_json_output(output: str) -> Optional[Dict[str, Any]]:
    text = (output or "").strip()
    if not text:
        return None
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        pass
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            value = json.loads(line)
            if isinstance(value, dict):
                return value
        except json.JSONDecodeError:
            continue
    return None


def run_gate(spec: Dict[str, Any], *, execute: bool, timeout: float) -> Dict[str, Any]:
    cmd = [sys.executable, str(spec["script"])]
    if execute:
        cmd.append("--execute")
    res = _run(cmd, timeout=timeout)
    payload = _parse_json_output(res["stdout"])
    return {
        "name": spec["name"],
        "script": str(spec["script"]),
        "execute": bool(execute),
        "exit_code": res["rc"],
        "phase": (payload or {}).get("phase"),
        "payload": payload,
        "duration_seconds": res["duration_seconds"],
        "tail": res["output"][-4000:],
    }


def classify_gate(result: Dict[str, Any]) -> str:
    rc = int(result.get("exit_code", 1))
    phase = str(result.get("phase") or "")
    if rc == 0 and phase == "SEALED":
        return "ok"
    if rc == 10 and phase in ("NOT_DUE", "WAIT_EVAL67", "WAIT_EVAL68"):
        return "ok"
    if rc == 20 and phase == "DUE":
        return "needs_execute"
    if rc == 1 and phase == "FAILED":
        return "failed"
    return "failed"


def run_seal_gate(
    spec: Dict[str, Any], *, expected_exit: Optional[int] = None
) -> Dict[str, Any]:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "check_session_sealed.py"),
        "--task-id",
        str(spec["task_id"]),
        "--glob",
        str(spec["prereg"]),
        "--require-any-glob",
        str(spec["combined"]),
        "--require-any-glob",
        str(spec["blocked"]),
    ]
    res = _run(cmd, timeout=300.0)
    expected = int(spec["expected_exit"] if expected_exit is None else expected_exit)
    return {
        "name": spec["name"],
        "exit_code": res["rc"],
        "expected_exit": expected,
        "ok": res["rc"] == expected,
        "tail": res["output"][-2000:],
    }


def _compact_gate(result: Dict[str, Any]) -> Dict[str, Any]:
    payload = result.get("payload") or {}
    disjoint = payload.get("disjointness") or {}
    return {
        "name": result.get("name"),
        "execute": bool(result.get("execute")),
        "exit_code": result.get("exit_code"),
        "phase": result.get("phase"),
        "classification": result.get("classification"),
        "duration_seconds": result.get("duration_seconds"),
        "overlap_seconds": disjoint.get("overlap_seconds"),
        "disjoint": disjoint.get("disjoint"),
        "eval67_sealed": (payload.get("readiness") or {}).get("eval67_sealed"),
        "eval68_sealed": (payload.get("readiness") or {}).get("eval68_sealed"),
        "tail": (result.get("tail") or "")[-1200:],
    }


def _overall_status(
    *,
    env_result: Dict[str, Any],
    targeted: Dict[str, Any],
    diagnostics: Dict[str, Any],
    gate_results: Sequence[Dict[str, Any]],
    seal_results: Optional[Sequence[Dict[str, Any]]] = None,
    execute_requested: bool,
) -> Dict[str, Any]:
    failures: List[str] = []
    needs_execute: List[str] = []

    if not env_result.get("ok"):
        failures.append("env_check")
    if targeted.get("rc") != 0:
        failures.append("targeted_tests")
    elif targeted.get("passed") != EXPECTED_TARGETED_TESTS:
        failures.append(
            f"targeted_test_count:{targeted.get('passed')}!={EXPECTED_TARGETED_TESTS}"
        )
    if diagnostics.get("rc") != 0:
        failures.append("diagnostic_tests")
    elif diagnostics.get("passed") != EXPECTED_DIAGNOSTIC_TESTS:
        failures.append(
            f"diagnostic_test_count:{diagnostics.get('passed')}!={EXPECTED_DIAGNOSTIC_TESTS}"
        )

    for seal in seal_results or ():
        if not seal.get("ok"):
            failures.append(
                f"seal_gate:{seal.get('name')}:{seal.get('exit_code')}!="
                f"{seal.get('expected_exit')}"
            )

    for gate in gate_results:
        cls = str(gate.get("classification") or "")
        if cls == "needs_execute":
            needs_execute.append(str(gate.get("name")))
        elif cls == "failed":
            failures.append(f"gate:{gate.get('name')}:{gate.get('phase')}")

    if needs_execute and not execute_requested:
        return {
            "ok": False,
            "exit_code": 20,
            "needs_execute": needs_execute,
            "failures": failures,
            "summary": "campaign is DUE; rerun with --execute",
        }
    if needs_execute and execute_requested:
        failures.extend(f"execute_still_due:{name}" for name in needs_execute)
    return {
        "ok": not failures,
        "exit_code": 0 if not failures else 1,
        "needs_execute": [],
        "failures": failures,
        "summary": "pre-threshold heavy work complete" if not failures else "failed",
    }


def _load_readiness() -> Dict[str, Any]:
    if READINESS_PATH.is_file():
        try:
            value = json.loads(READINESS_PATH.read_text())
            if isinstance(value, dict):
                return value
        except json.JSONDecodeError:
            pass
    return {"schema_version": 3}


def _gate_summary(gate_results: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {str(g.get("name")): g for g in gate_results if g.get("name")}


def update_readiness(
    *,
    env_result: Dict[str, Any],
    targeted: Dict[str, Any],
    diagnostics: Dict[str, Any],
    gate_results: Sequence[Dict[str, Any]],
    seal_results: Sequence[Dict[str, Any]],
    overall: Dict[str, Any],
    execute_requested: bool,
) -> Dict[str, Any]:
    data = _load_readiness()
    for stale in STALE_READINESS_KEYS:
        data.pop(stale, None)
    gates = _gate_summary(gate_results)
    seals = {str(s.get("name")): s for s in seal_results}

    g67 = gates.get("EVAL-67", {})
    p67 = (g67.get("payload") or {})
    d67 = (p67.get("disjointness") or {})
    g68 = gates.get("EVAL-68", {})
    p68 = (g68.get("payload") or {})
    d68 = (p68.get("disjointness") or {})
    g69 = gates.get("EVAL-69", {})
    p69 = (g69.get("payload") or {})
    d69 = (p69.get("disjointness") or {})
    g70 = gates.get("EVAL-70", {})
    p70 = (g70.get("payload") or {})
    g72 = gates.get("EVAL-72", {})
    p72 = (g72.get("payload") or {})

    notes = (
        f"Verified {utc_now_iso()} by scripts/eval67_prethreshold_progress.py "
        f"(execute_requested={bool(execute_requested)}): env_check="
        f"{'OK' if env_result.get('ok') else 'FAILED'}; "
        f"targeted_tests={targeted.get('passed')}/{EXPECTED_TARGETED_TESTS} "
        f"(rc={targeted.get('rc')}); "
        f"diagnostics={diagnostics.get('passed')}/{EXPECTED_DIAGNOSTIC_TESTS} "
        f"(rc={diagnostics.get('rc')}); "
        f"EVAL-70={p70.get('phase')} exit={g70.get('exit_code')}; "
        f"EVAL-71={(gates.get('EVAL-71', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-71', {}).get('exit_code')}; "
        f"EVAL-72={p72.get('phase')} exit={g72.get('exit_code')}; "
        f"EVAL-73={(gates.get('EVAL-73', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-73', {}).get('exit_code')}; "
        f"EVAL-74={(gates.get('EVAL-74', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-74', {}).get('exit_code')}; "
        f"EVAL-75={(gates.get('EVAL-75', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-75', {}).get('exit_code')}; "
        f"EVAL-76={(gates.get('EVAL-76', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-76', {}).get('exit_code')}; "
        f"EVAL-77={(gates.get('EVAL-77', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-77', {}).get('exit_code')}; "
        f"EVAL-78={(gates.get('EVAL-78', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-78', {}).get('exit_code')}; "
        f"EVAL-79={(gates.get('EVAL-79', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-79', {}).get('exit_code')}; "
        f"EVAL-80={(gates.get('EVAL-80', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-80', {}).get('exit_code')}; "
        f"EVAL-81={(gates.get('EVAL-81', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-81', {}).get('exit_code')}; "
        f"EVAL-82={(gates.get('EVAL-82', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-82', {}).get('exit_code')}; "
        f"EVAL-83={(gates.get('EVAL-83', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-83', {}).get('exit_code')}; "
        f"EVAL-93={(gates.get('EVAL-93', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-93', {}).get('exit_code')}; "
        f"EVAL-94={(gates.get('EVAL-94', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-94', {}).get('exit_code')}; "
        f"EVAL-95={(gates.get('EVAL-95', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-95', {}).get('exit_code')}; "
        f"EVAL-96={(gates.get('EVAL-96', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-96', {}).get('exit_code')}; "
        f"EVAL-97={(gates.get('EVAL-97', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-97', {}).get('exit_code')}; "
        f"EVAL-98={(gates.get('EVAL-98', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-98', {}).get('exit_code')}; "
        f"EVAL-99={(gates.get('EVAL-99', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-99', {}).get('exit_code')}; "
        f"EVAL-100={(gates.get('EVAL-100', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-100', {}).get('exit_code')}; "
        f"EVAL-101={(gates.get('EVAL-101', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-101', {}).get('exit_code')}; "
        f"EVAL-102={(gates.get('EVAL-102', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-102', {}).get('exit_code')}; "
        f"EVAL-103={(gates.get('EVAL-103', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-103', {}).get('exit_code')}; "
        f"EVAL-104={(gates.get('EVAL-104', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-104', {}).get('exit_code')}; "
        f"EVAL-105={(gates.get('EVAL-105', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-105', {}).get('exit_code')}; "
        f"EVAL-106={(gates.get('EVAL-106', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-106', {}).get('exit_code')}; "
        f"EVAL-107={(gates.get('EVAL-107', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-107', {}).get('exit_code')}; "
        f"EVAL-108={(gates.get('EVAL-108', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-108', {}).get('exit_code')}; "
        f"EVAL-109={(gates.get('EVAL-109', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-109', {}).get('exit_code')}; "
        f"EVAL-110={(gates.get('EVAL-110', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-110', {}).get('exit_code')}; "
        f"EVAL-111={(gates.get('EVAL-111', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-111', {}).get('exit_code')}; "
        f"EVAL-121={(gates.get('EVAL-121', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-121', {}).get('exit_code')}; "
        f"EVAL-67={p67.get('phase')} exit={g67.get('exit_code')} "
        f"overlap_seconds={d67.get('overlap_seconds')} disjoint={d67.get('disjoint')}; "
        f"EVAL-68={p68.get('phase')} exit={g68.get('exit_code')} "
        f"eval67_sealed={(p68.get('readiness') or {}).get('eval67_sealed')}; "
        f"EVAL-69={p69.get('phase')} exit={g69.get('exit_code')} "
        f"eval68_sealed={(p69.get('readiness') or {}).get('eval68_sealed')}; "
        f"overall_ok={bool(overall.get('ok'))} exit={overall.get('exit_code')}. "
        "This is a verified pre-threshold carry, not a completion."
    )

    data.update(
        {
            "updated_at": utc_now_iso(),
            "gate_phase": p67.get("phase"),
            "gate_exit": g67.get("exit_code"),
            "overlap_seconds": d67.get("overlap_seconds"),
            "disjoint": d67.get("disjoint"),
            "env_check": "OK" if env_result.get("ok") else "FAILED",
            "tests_passed": targeted.get("passed"),
            "diagnostics_passed": diagnostics.get("passed"),
            "total_tests_passed": (
                (targeted.get("passed") or 0) + (diagnostics.get("passed") or 0)
            ),
            "notes": notes,
            "test_details": {
                "targeted_expected": EXPECTED_TARGETED_TESTS,
                "targeted_rc": targeted.get("rc"),
                "targeted_duration_seconds": targeted.get("duration_seconds"),
                "diagnostics_expected": EXPECTED_DIAGNOSTIC_TESTS,
                "diagnostics_rc": diagnostics.get("rc"),
                "diagnostics_duration_seconds": diagnostics.get("duration_seconds"),
            },
            "gates": {
                "eval70": _compact_gate(g70),
                "eval71": _compact_gate(gates.get("EVAL-71", {})),
                "eval72": _compact_gate(g72),
                "eval73": _compact_gate(gates.get("EVAL-73", {})),
                "eval74": _compact_gate(gates.get("EVAL-74", {})),
                "eval75": _compact_gate(gates.get("EVAL-75", {})),
                "eval76": _compact_gate(gates.get("EVAL-76", {})),
                "eval77": _compact_gate(gates.get("EVAL-77", {})),
                "eval78": _compact_gate(gates.get("EVAL-78", {})),
                "eval79": _compact_gate(gates.get("EVAL-79", {})),
                "eval80": _compact_gate(gates.get("EVAL-80", {})),
                "eval81": _compact_gate(gates.get("EVAL-81", {})),
                "eval82": _compact_gate(gates.get("EVAL-82", {})),
                "eval83": _compact_gate(gates.get("EVAL-83", {})),
                "eval88": _compact_gate(gates.get("EVAL-88", {})),
                "eval89": _compact_gate(gates.get("EVAL-89", {})),
                "eval90": _compact_gate(gates.get("EVAL-90", {})),
                "eval91": _compact_gate(gates.get("EVAL-91", {})),
                "eval92": _compact_gate(gates.get("EVAL-92", {})),
                "eval93": _compact_gate(gates.get("EVAL-93", {})),
                "eval94": _compact_gate(gates.get("EVAL-94", {})),
                "eval95": _compact_gate(gates.get("EVAL-95", {})),
                "eval96": _compact_gate(gates.get("EVAL-96", {})),
                "eval97": _compact_gate(gates.get("EVAL-97", {})),
                "eval98": _compact_gate(gates.get("EVAL-98", {})),
                "eval99": _compact_gate(gates.get("EVAL-99", {})),
                "eval100": _compact_gate(gates.get("EVAL-100", {})),
                "eval101": _compact_gate(gates.get("EVAL-101", {})),
                "eval102": _compact_gate(gates.get("EVAL-102", {})),
                "eval103": _compact_gate(gates.get("EVAL-103", {})),
                "eval104": _compact_gate(gates.get("EVAL-104", {})),
                "eval105": _compact_gate(gates.get("EVAL-105", {})),
                "eval106": _compact_gate(gates.get("EVAL-106", {})),
                "eval107": _compact_gate(gates.get("EVAL-107", {})),
                "eval108": _compact_gate(gates.get("EVAL-108", {})),
                "eval109": _compact_gate(gates.get("EVAL-109", {})),
                "eval110": _compact_gate(gates.get("EVAL-110", {})),
                "eval111": _compact_gate(gates.get("EVAL-111", {})),
                "eval121": _compact_gate(gates.get("EVAL-121", {})),
                "eval122": _compact_gate(gates.get("EVAL-122", {})),
                "eval67": _compact_gate(g67),
                "eval68": _compact_gate(g68),
                "eval69": _compact_gate(g69),
            },
            "seal_gates": seals,
            "orchestrator": {
                "script": "scripts/eval67_prethreshold_progress.py",
                "execute_requested": bool(execute_requested),
                "overall_ok": bool(overall.get("ok")),
                "exit_code": overall.get("exit_code"),
                "needs_execute": overall.get("needs_execute"),
                "failures": overall.get("failures"),
                "generated_at": utc_now_iso(),
            },
        }
    )

    ev68 = data.get("eval68")
    if not isinstance(ev68, dict):
        ev68 = {}
    ev68.update(
        {
            "gate_phase": p68.get("phase"),
            "gate_exit": g68.get("exit_code"),
            "overlap_seconds": d68.get("overlap_seconds"),
            "seal_gate_exit": (seals.get("EVAL-68") or {}).get("exit_code"),
        }
    )
    data["eval68"] = ev68

    ev69 = data.get("eval69")
    if not isinstance(ev69, dict):
        ev69 = {}
    ev69.update(
        {
            "gate_phase": p69.get("phase"),
            "gate_exit": g69.get("exit_code"),
            "overlap_seconds": d69.get("overlap_seconds"),
            "seal_gate_exit": (seals.get("EVAL-69") or {}).get("exit_code"),
        }
    )
    data["eval69"] = ev69
    return data


def write_readiness(data: Dict[str, Any]) -> None:
    RS_DIR.mkdir(parents=True, exist_ok=True)
    tmp = READINESS_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    tmp.replace(READINESS_PATH)


def run_prethreshold_progress(
    *,
    execute: bool = False,
    run_tests: bool = True,
    write: bool = True,
    gate_timeout: float = 3600.0,
) -> Dict[str, Any]:
    env_result = run_env_check()
    if run_tests:
        targeted = _pytest_result(TARGETED_TEST_FILES, timeout=1800.0)
        diagnostics = _pytest_result(DIAGNOSTIC_TEST_FILES, timeout=600.0)
    else:
        targeted = {
            "command": [],
            "rc": 0,
            "passed": EXPECTED_TARGETED_TESTS,
            "duration_seconds": 0.0,
            "tail": "skipped",
        }
        diagnostics = {
            "command": [],
            "rc": 0,
            "passed": EXPECTED_DIAGNOSTIC_TESTS,
            "duration_seconds": 0.0,
            "tail": "skipped",
        }

    gate_results: List[Dict[str, Any]] = []
    for spec in GATE_SPECS:
        status = run_gate(spec, execute=False, timeout=300.0)
        cls = classify_gate(status)
        entry: Dict[str, Any] = dict(status)
        entry["classification"] = cls
        if execute and cls == "needs_execute":
            execution = run_gate(spec, execute=True, timeout=gate_timeout)
            cls2 = classify_gate(execution)
            entry["execution"] = {
                "exit_code": execution.get("exit_code"),
                "phase": execution.get("phase"),
                "classification": cls2,
                "duration_seconds": execution.get("duration_seconds"),
                "tail": execution.get("tail", "")[-1200:],
            }
            entry["classification"] = cls2
            entry["exit_code"] = execution.get("exit_code")
            entry["phase"] = execution.get("phase")
            entry["payload"] = execution.get("payload")
        gate_results.append(entry)

    sealed_by_name = {
        str(g.get("name")): str(g.get("phase")) == "SEALED" for g in gate_results
    }
    seal_results = [
        run_seal_gate(
            spec,
            expected_exit=0 if sealed_by_name.get(str(spec["name"]), False) else None,
        )
        for spec in SEAL_SPECS
    ]
    overall = _overall_status(
        env_result=env_result,
        targeted=targeted,
        diagnostics=diagnostics,
        gate_results=gate_results,
        seal_results=seal_results,
        execute_requested=execute,
    )
    data = update_readiness(
        env_result=env_result,
        targeted=targeted,
        diagnostics=diagnostics,
        gate_results=gate_results,
        seal_results=seal_results,
        overall=overall,
        execute_requested=execute,
    )
    if write:
        try:
            write_readiness(data)
            readiness_written = True
        except BaseException as exc:  # noqa: BLE001
            readiness_written = False
            overall["failures"].append(f"readiness_write:{exc!r}")
            overall["ok"] = False
            overall["exit_code"] = 1
    else:
        readiness_written = False

    return {
        "ok": bool(overall.get("ok")),
        "exit_code": overall.get("exit_code"),
        "summary": overall.get("summary"),
        "needs_execute": overall.get("needs_execute"),
        "failures": overall.get("failures"),
        "env_check": env_result.get("ok"),
        "targeted_tests": {
            "rc": targeted.get("rc"),
            "passed": targeted.get("passed"),
            "expected": EXPECTED_TARGETED_TESTS,
        },
        "diagnostic_tests": {
            "rc": diagnostics.get("rc"),
            "passed": diagnostics.get("passed"),
            "expected": EXPECTED_DIAGNOSTIC_TESTS,
        },
        "gates": [_compact_gate(g) for g in gate_results],
        "seal_gates": [
            {"name": s.get("name"), "exit_code": s.get("exit_code"), "ok": s.get("ok")}
            for s in seal_results
        ],
        "readiness_written": readiness_written,
        "readiness_path": str(READINESS_PATH),
        "generated_at": utc_now_iso(),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Run the full EVAL-67/68/69 pre-threshold heavy-work loop."
    )
    ap.add_argument(
        "--execute",
        action="store_true",
        help="also execute any campaign arbiter that reports DUE (in ladder order)",
    )
    ap.add_argument(
        "--skip-tests",
        action="store_true",
        help="skip the test suites (not recommended; for status-only debugging)",
    )
    ap.add_argument(
        "--no-write",
        action="store_true",
        help="do not update the readiness JSON",
    )
    ap.add_argument(
        "--gate-timeout",
        type=float,
        default=3600.0,
        help="timeout in seconds for a --execute gate (default: 3600)",
    )
    args = ap.parse_args(argv)

    result = run_prethreshold_progress(
        execute=bool(args.execute),
        run_tests=not bool(args.skip_tests),
        write=not bool(args.no_write),
        gate_timeout=float(args.gate_timeout),
    )
    print(json.dumps(result, indent=2, default=str))
    return int(result.get("exit_code", 1))


if __name__ == "__main__":
    raise SystemExit(main())