import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.generate_phase64_adaptive_toxicity_resilient_capital_deployment_orchestrator_paper_evidence import (  # noqa: E402
    ARTIFACT_TYPE,
    SYMBOLS,
    UNDERLYINGS,
    VENUES,
    _strip_timestamps,
    generate,
    validate_artifact,
)

SEED = 64061
CYCLES = 80


class Phase64EvidenceGuardsSchema(unittest.TestCase):
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
        self.assertGreater(int(d["campaign"]["n_rollout_gates"]), 0)
        self.assertGreater(int(d["campaign"]["n_capital_deployments"]), 0)
        self.assertGreater(int(d["campaign"]["n_hedge_guardrails"]), 0)
        surf = d["capital_deployment_resilience_surface"]
        self.assertTrue(surf["paper_only"])
        self.assertTrue(surf["deterministic_replay_equal"])
        self.assertTrue(surf["bounds_ok"])
        self.assertGreater(int(surf["n_rollout_gates"]), 0)
        self.assertEqual(set(surf["venues"]), set(VENUES))
        self.assertEqual(set(surf["symbols"]), set(SYMBOLS))
        self.assertEqual(set(surf["regimes"]), {"normal", "elevated", "high_toxicity"})
        self.assertEqual(
            set(surf["deployment_postures"]),
            {"rollout_proceed", "rollout_tighten", "failover_hedge_hard"},
        )
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
        self.assertTrue(all(x.get("deterministic_probe_gate_id") for x in d["venue_symbol_coverage"]))
        self.assertTrue(all(bool(x.get("probe_finite")) for x in d["venue_symbol_coverage"]))
        self.assertTrue(all(bool(x.get("probe_bounds_within_limits")) for x in d["venue_symbol_coverage"]))
        self.assertTrue(all(bool(x.get("probe_regime_conditional_posture")) for x in d["venue_symbol_coverage"]))
        self.assertTrue(all(bool(x.get("probe_gates_ok")) for x in d["venue_symbol_coverage"]))

    def test_capital_deployment_surface_bounds_and_risk_posture(self):
        d = generate(cycles=CYCLES, seed=SEED)
        surf = d["capital_deployment_resilience_surface"]
        self.assertGreaterEqual(float(surf["avg_toxicity"]), 0.0)
        self.assertLessEqual(float(surf["avg_toxicity"]), 1.0)
        self.assertGreaterEqual(float(surf["avg_readiness"]), 0.0)
        self.assertLessEqual(float(surf["avg_readiness"]), 1.0)
        self.assertGreaterEqual(float(surf["avg_deploy_allowed_rate"]), 0.0)
        self.assertLessEqual(float(surf["avg_deploy_allowed_rate"]), 1.0)
        self.assertGreaterEqual(float(surf["avg_failover_rate"]), 0.0)
        self.assertLessEqual(float(surf["avg_failover_rate"]), 1.0)
        self.assertGreaterEqual(float(surf["avg_pause_rate"]), 0.0)
        self.assertLessEqual(float(surf["avg_pause_rate"]), 1.0)
        self.assertGreaterEqual(float(surf["max_bound_ratio"]), 0.0)
        self.assertLessEqual(float(surf["max_bound_ratio"]), 1.0)
        self.assertGreaterEqual(float(surf["toxicity_max"]), 0.0)
        self.assertLessEqual(float(surf["toxicity_max"]), 1.0)
        self.assertTrue(all(bool(v) for v in d["determinism"]["bounds"].values()))
        rp = d["risk_posture"]
        self.assertIn(rp["kill_switch_slo_posture"], ("armed_paper", "observed_paper", "paper_guarded"))
        self.assertTrue(rp["all_coverage_gates_ok"])

    def test_cli_no_write_mode(self):
        res = subprocess.run(
            [
                sys.executable,
                "scripts/generate_phase64_adaptive_toxicity_resilient_capital_deployment_orchestrator_paper_evidence.py",
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

    def test_cross_refs_reference_phase64_phase63_and_composed_phases(self):
        d = generate(cycles=CYCLES, seed=SEED)
        joined = " ".join(d["evidence_refs"] + d["cross_refs"])
        self.assertIn("phase64_adaptive_toxicity_resilient_capital_deployment_orchestrator.py", joined)
        self.assertIn("Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestrator", joined)
        self.assertIn("PHASE63_ADAPTIVE_TOXICITY_RESILIENT_DEPLOYMENT_ORCHESTRATOR_PAPER_EVIDENCE_20261107T210310Z.json", joined)
        self.assertIn("PHASE62_ADAPTIVE_REGIME_CONDITIONAL_EXECUTION_RESILIENCE_PAPER_EVIDENCE_20261107T201758Z.json", joined)
        self.assertIn("PHASE61_ADAPTIVE_REGIME_SWITCHING_HEDGE_ORCHESTRATOR_PAPER_EVIDENCE_20261107T200213Z.json", joined)
        self.assertIn("PHASE60_ADAPTIVE_EXECUTION_INTELLIGENCE_ENGINE_PAPER_EVIDENCE_20261107T192105Z.json", joined)
        self.assertIn("PHASE60_TOXICITY_RESILIENT_HEDGE_FUSION_PAPER_EVIDENCE_20261107T185604Z.json", joined)
        self.assertIn("PHASE59_ADAPTIVE_CROSS_ASSET_HEDGE_FUSION_PAPER_EVIDENCE_20261107T172922Z.json", joined)
        self.assertIn("PHASE58_FLOW_TOXICITY_MITIGATOR_PAPER_EVIDENCE_20261107T165643Z.json", joined)
        self.assertIn("PAPER_OPS_SESSION_GATE", joined)
        self.assertIn("CONTINUOUS_VALIDATION_20261107T212338Z.json", joined)


if __name__ == "__main__":
    unittest.main()
