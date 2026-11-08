"""Tests for phase86 adaptive toxicity-resilient post-attestation finality orchestrator paper evidence generator.

Generator/script/env tests only (no network). Controlled env: PHASE_QUICK_VERIFY=1 avoids
hanging composed phase69-85 real sub-orchestrator logic (see handoff bottlenecks).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO))


def _stubs() -> None:
    try:
        import src.orderflow.phase32_orderflow_alpha_integration as p32
        p32.OrderflowAlphaIntegrator.run_campaign = lambda self, cycles=80: {"phase": "PHASE32", "paper_only": True, "gates_ok": True, "cycles": cycles, "n_trades": 0}
    except Exception:
        pass
    try:
        import src.orderflow.phase58_flow_toxicity_mitigator as p58
        if hasattr(p58, "Phase58FlowToxicityMitigator"):
            p58.Phase58FlowToxicityMitigator.run_campaign = lambda self, *a, **k: {"phase": "PHASE58", "paper_only": True, "gates_ok": True}
            p58.Phase58FlowToxicityMitigator.mitigate = lambda self, *a, **k: {"mitigated": True, "paper_only": True, "avg_vpin": 0.18}
    except Exception:
        pass
    try:
        import src.risk.phase54_realtime_risk_fusion_engine as p54
        if hasattr(p54, "Phase54RealtimeRiskFusionEngine"):
            p54.Phase54RealtimeRiskFusionEngine.run_campaign = lambda self, *a, **k: {"phase": "PHASE54", "paper_only": True, "gates_ok": True}
    except Exception:
        pass
    for modname, clsname in [("src.telemetry.slo_monitor", "SLOMonitor"), ("src.telemetry.health_slo_monitor", "HealthSLOMonitor"), ("src.observability.slo_monitor", "SLOMonitor")]:
        try:
            m = __import__(modname, fromlist=[clsname]); c = getattr(m, clsname, None)
            if c:
                if hasattr(c, "evaluate_all"): c.evaluate_all = lambda self, *a, **k: {"status": "ok"}
                if hasattr(c, "evaluate_slo"): c.evaluate_slo = lambda self, *a, **k: {"status": "ok"}
        except Exception:
            pass
    import threading
    _orig = threading.Thread.start

    def _safe(self, *a, **k):
        if not getattr(self, "daemon", False): self.daemon = True
        return _orig(self, *a, **k)
    threading.Thread.start = _safe


_stubs()

from generate_phase86_adaptive_toxicity_resilient_post_attestation_finality_orchestrator_paper_evidence import (  # noqa: E402
    ARTIFACT_TYPE,
    SYMBOLS,
    VENUES,
    _strip_timestamps,
    generate,
    validate_artifact,
)

SEED = 86086
CYCLES = 8


class Phase86AdaptiveToxicityResilientPostAttestationFinalityEvidenceTests(unittest.TestCase):
    def test_generate_valid_advisory_paper_shape(self) -> None:
        d = generate(cycles=CYCLES, seed=SEED)
        ok, issues = validate_artifact(d)
        self.assertTrue(ok, issues)
        self.assertEqual(d["artifact_type"], ARTIFACT_TYPE)
        self.assertTrue(d["paper_only"])
        self.assertTrue(d["advisory"])
        self.assertTrue(d["no_external_venue_mutation"])
        self.assertFalse(d["live_trading_enabled"])
        self.assertFalse(d["next9_unblocked"])
        self.assertTrue(d["validation"]["valid"])
        self.assertEqual(d["validation"]["issues"], [])
        self.assertTrue(d["campaign"]["paper_only"])
        self.assertTrue(d["campaign"]["gates_ok"])
        surf = d["finality_surface"]
        self.assertTrue(surf["paper_only"])
        self.assertTrue(surf["bounds_ok"])
        self.assertTrue(surf["deterministic_replay_equal"])
        self.assertGreater(int(surf["n_finality_attestations"]), 0)
        self.assertGreater(int(surf["n_hedging_finality_attestations"]), 0)
        self.assertEqual(set(surf["venues"]), set(VENUES))
        self.assertEqual(set(surf["symbols"]), set(SYMBOLS))
        self.assertEqual(set(surf["regimes"]), {"normal", "elevated", "high_toxicity"})
        self.assertEqual(set(surf["finality_modes"]), {"finality_monitor", "finality_cross_venue", "finality_depth_reinforce"})
        self.assertTrue(d["risk_posture"]["paper_only"])
        self.assertFalse(d["risk_posture"]["next9_unblocked"])
        self.assertFalse(d["risk_posture"]["live_trading_enabled"])
        self.assertIn(d["risk_posture"]["kill_switch_slo_posture"], ("armed_paper", "observed_paper", "paper_guarded"))
        json.dumps(d, allow_nan=False)

    def test_rejects_live_and_next9_unblock_and_paper_only_false(self) -> None:
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

    def test_deterministic_seed_reproduces_surface(self) -> None:
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

    def test_venue_symbol_coverage_and_finite_probes(self) -> None:
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

    def test_finality_surface_bounds_and_risk_posture(self) -> None:
        d = generate(cycles=CYCLES, seed=SEED)
        surf = d["finality_surface"]
        self.assertGreaterEqual(float(surf["avg_cross_venue_ok"]), 0.0)
        self.assertLessEqual(float(surf["avg_cross_venue_ok"]), 1.0)
        self.assertGreaterEqual(float(surf["ok_max"]), 0.0)
        self.assertLessEqual(float(surf["ok_max"]), 1.0)
        self.assertGreaterEqual(float(surf["avg_finality_pass_rate"]), 0.0)
        self.assertLessEqual(float(surf["avg_finality_pass_rate"]), 1.0)
        self.assertGreaterEqual(float(surf["max_bound_ratio"]), 0.0)
        self.assertLessEqual(float(surf["max_bound_ratio"]), 1.0)
        self.assertTrue(all(bool(v) for v in d["determinism"]["bounds"].values()))
        rp = d["risk_posture"]
        self.assertIn(rp["kill_switch_slo_posture"], ("armed_paper", "observed_paper", "paper_guarded"))
        self.assertTrue(rp["all_coverage_gates_ok"])

    def test_cli_no_write_mode(self) -> None:
        res = subprocess.run(
            [
                sys.executable,
                "scripts/generate_phase86_adaptive_toxicity_resilient_post_attestation_finality_orchestrator_paper_evidence.py",
                "--cycles", str(CYCLES), "--seed", str(SEED), "--no-write",
            ],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=600,
            env={**os.environ, "PHASE_QUICK_VERIFY": "1"},
        )
        self.assertEqual(res.returncode, 0, f"stdout={res.stdout[-500:]}\nstderr={res.stderr[-500:]}")
        payload = json.loads(res.stdout)
        self.assertTrue(payload["valid"])
        self.assertTrue(payload["paper_only"])
        self.assertFalse(payload["live_trading_enabled"])
        self.assertFalse(payload["next9_unblocked"])
        self.assertTrue(payload["deterministic"])

    def test_cross_refs_reference_phase86_phase85_and_composed_phases(self) -> None:
        d = generate(cycles=CYCLES, seed=SEED)
        joined = " ".join(d["evidence_refs"] + d["cross_refs"])
        self.assertIn("phase86_adaptive_toxicity_resilient_post_attestation_finality_orchestrator.py", joined)
        self.assertIn("Phase86AdaptiveToxicityResilientPostAttestationFinalityOrchestrator", joined)
        self.assertIn("PHASE85_ADAPTIVE_TOXICITY_RESILIENT_POST_CLOSEOUT_ATTRIBUTION_ATTESTATION_ORCHESTRATOR_PAPER_EVIDENCE_20261108T074529Z.json", joined)
        self.assertIn("PAPER_OPS_SESSION_GATE", joined)
        self.assertIn("composes=PHASE85,PHASE84,PHASE83,PHASE82,PHASE81,PHASE80,PHASE79,PHASE78,PHASE77,PHASE76,PHASE75,PHASE74,PHASE73,PHASE72,PHASE71,PHASE70,PHASE69,PHASE58,PHASE54,PHASE39,PHASE32", joined)


if __name__ == "__main__":
    unittest.main()
