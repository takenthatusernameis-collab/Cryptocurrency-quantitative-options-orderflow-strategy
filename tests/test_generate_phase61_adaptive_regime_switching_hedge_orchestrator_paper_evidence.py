import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.generate_phase61_adaptive_regime_switching_hedge_orchestrator_paper_evidence import (  # noqa: E402
    ARTIFACT_TYPE,
    SYMBOLS,
    UNDERLYINGS,
    VENUES,
    _strip_timestamps,
    generate,
    validate_artifact,
)

SEED = 61061
CYCLES = 80


class Phase61EvidenceGuardsSchema(unittest.TestCase):
    def test_generate_artifact_guards_and_schema(self):
        d = generate(cycles=CYCLES, seed=SEED)
        self.assertEqual(d["artifact_type"], ARTIFACT_TYPE)
        self.assertTrue(d["paper_only"])
        self.assertFalse(d["live_trading_enabled"])
        self.assertFalse(d["next9_unblocked"])
        self.assertTrue(d["advisory"])
        self.assertTrue(d["no_external_venue_mutation"])
        self.assertTrue(d["validation"]["valid"])
        self.assertEqual(d["validation"]["issues"], [])
        self.assertEqual(d["venues"], list(VENUES))
        self.assertEqual(d["symbols"], list(SYMBOLS))
        self.assertEqual(d["underlyings"], list(UNDERLYINGS))
        self.assertGreater(int(d["cycles"]), 0)
        self.assertTrue(d["campaign"]["paper_only"])
        self.assertTrue(d["campaign"]["gates_ok"])
        self.assertTrue(d["campaign"]["hedge60_integration_ok"])
        self.assertTrue(d["campaign"]["hedge59_integration_ok"])
        self.assertTrue(d["campaign"]["risk54_integration_ok"])
        self.assertTrue(d["campaign"]["tox58_integration_ok"])
        self.assertTrue(d["regime_switching_surface"]["paper_only"])
        self.assertTrue(d["regime_switching_surface"]["deterministic_replay_equal"])
        self.assertTrue(d["regime_switching_surface"]["bounds_ok"])
        self.assertGreater(int(d["regime_switching_surface"]["n_hedges"]), 0)
        self.assertTrue(d["risk_posture"]["paper_only"])
        self.assertFalse(d["risk_posture"]["next9_unblocked"])
        self.assertFalse(d["risk_posture"]["live_trading_enabled"])
        self.assertIn(d["risk_posture"]["kill_switch_slo_posture"], ("armed_paper", "observed_paper", "paper_guarded"))
        json.dumps(d, allow_nan=False)

    def test_rejects_live_and_next9_unblock_and_paper_only_false(self):
        for key, value in (
            ("live_trading_enabled", True),
            ("next9_unblocked", True),
            ("paper_only", False),
            ("advisory", False),
            ("no_external_venue_mutation", False),
        ):
            d = generate(cycles=CYCLES, seed=SEED)
            d[key] = value
            ok, issues = validate_artifact(d)
            self.assertFalse(ok, f"expected invalid for {key}={value}: {issues}")
            self.assertGreater(len(issues), 0)

    def test_deterministic_seed_reproduces_surface(self):
        a = generate(cycles=CYCLES, seed=SEED)
        b = generate(cycles=CYCLES, seed=SEED)
        self.assertTrue(a["determinism"]["deterministic_seeded"])
        self.assertTrue(a["determinism"]["same_seed_cycles_reproduce_surface"])
        self.assertTrue(a["determinism"]["bounds_ok"])
        self.assertEqual(
            json.dumps(_strip_timestamps(a), sort_keys=True),
            json.dumps(_strip_timestamps(b), sort_keys=True),
        )
        c = generate(cycles=CYCLES, seed=999)
        self.assertNotEqual(
            json.dumps(_strip_timestamps(c), sort_keys=True),
            json.dumps(_strip_timestamps(a), sort_keys=True),
        )

    def test_venue_symbol_coverage_and_finite_probes(self):
        d = generate(cycles=CYCLES, seed=SEED)
        pairs = {(x["venue"], x["symbol"]) for x in d["venue_symbol_coverage"]}
        expected = {(v, s) for v in VENUES for s in SYMBOLS}
        self.assertEqual(pairs, expected)
        self.assertTrue(all(x["paper_only"] is True for x in d["venue_symbol_coverage"]))
        self.assertTrue(all(x.get("deterministic_probe_hedge_id") for x in d["venue_symbol_coverage"]))
        self.assertTrue(all(bool(x.get("probe_finite")) for x in d["venue_symbol_coverage"]))
        self.assertTrue(all(bool(x.get("probe_bounds_within_limits")) for x in d["venue_symbol_coverage"]))
        self.assertTrue(all(bool(x.get("probe_delta_neutral_guarded")) for x in d["venue_symbol_coverage"]))
        self.assertTrue(all(bool(x.get("probe_hedge_ratio_bounded")) for x in d["venue_symbol_coverage"]))
        self.assertTrue(all(bool(x.get("probe_regime_conditional_posture")) for x in d["venue_symbol_coverage"]))
        self.assertEqual(set(d["regime_switching_surface"]["venues"]), set(VENUES))
        self.assertEqual(set(d["regime_switching_surface"]["symbols"]), set(SYMBOLS))

    def test_regime_switching_surface_bounds_and_risk_posture(self):
        d = generate(cycles=CYCLES, seed=SEED)
        surf = d["regime_switching_surface"]
        self.assertGreaterEqual(float(surf["avg_delta_notional_usd"]), 0.0)
        self.assertGreaterEqual(float(surf["avg_vega_notional_usd"]), 0.0)
        self.assertGreaterEqual(float(surf["avg_gamma_notional_usd"]), 0.0)
        self.assertGreater(float(surf["avg_hedge_ratio"]), 0.0)
        self.assertLessEqual(float(surf["max_bound_ratio"]), 1.0)
        self.assertGreaterEqual(float(surf["max_bound_ratio"]), 0.0)
        self.assertGreaterEqual(float(surf["avg_toxicity"]), 0.0)
        self.assertLessEqual(float(surf["avg_toxicity"]), 1.0)
        self.assertGreaterEqual(float(surf["avg_vol_shock"]), 0.0)
        self.assertGreater(float(surf["n_hedges"]), 0)
        self.assertTrue(all(bool(v) for v in d["determinism"]["bounds"].values()))
        rp = d["risk_posture"]
        self.assertIn(rp["kill_switch_slo_posture"], ("armed_paper", "observed_paper", "paper_guarded"))
        self.assertTrue(rp["all_coverage_gates_ok"])

    def test_cli_no_write_mode(self):
        res = subprocess.run(
            [
                sys.executable,
                "scripts/generate_phase61_adaptive_regime_switching_hedge_orchestrator_paper_evidence.py",
                "--cycles",
                str(CYCLES),
                "--seed",
                str(SEED),
                "--no-write",
            ],
            cwd=str(REPO),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        payload = json.loads(res.stdout)
        self.assertTrue(payload["valid"])
        self.assertTrue(payload["paper_only"])
        self.assertFalse(payload["live_trading_enabled"])
        self.assertFalse(payload["next9_unblocked"])
        self.assertTrue(payload["deterministic"])

    def test_cross_refs_reference_phase61_and_composed_phases(self):
        d = generate(cycles=CYCLES, seed=SEED)
        joined = " ".join(d["evidence_refs"] + d["cross_refs"])
        self.assertIn("phase61_adaptive_regime_switching_hedge_orchestrator.py", joined)
        self.assertIn("Phase61AdaptiveRegimeSwitchingHedgeOrchestrator", joined)
        self.assertIn("PHASE60_ADAPTIVE_EXECUTION_INTELLIGENCE_ENGINE_PAPER_EVIDENCE_20261107T192105Z.json", joined)
        self.assertIn("PHASE60_TOXICITY_RESILIENT_HEDGE_FUSION_PAPER_EVIDENCE_20261107T185604Z.json", joined)
        self.assertIn("PHASE59_ADAPTIVE_CROSS_ASSET_HEDGE_FUSION_PAPER_EVIDENCE_20261107T172922Z.json", joined)
        self.assertIn("PHASE58_FLOW_TOXICITY_MITIGATOR_PAPER_EVIDENCE_20261107T165643Z.json", joined)
        self.assertIn("PAPER_OPS_SESSION_GATE", joined)
        self.assertIn("CONTINUOUS_VALIDATION_20261107T195952Z.json", joined)


if __name__ == "__main__":
    unittest.main()
