import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from scripts.generate_phase108_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence import (  # noqa: E402
    ARTIFACT_TYPE,
    VENUES,
    SYMBOLS,
    generate,
    validate_artifact,
)

PYTHON = sys.executable
SCRIPT = "scripts/generate_phase108_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py"


class TestPhase108Generator(unittest.TestCase):
    def _d(self):
        return generate(cycles=4, seed=108108, write=False)

    def test_valid_advisory_shape(self):
        d = self._d()
        ok, issues = validate_artifact(d)
        self.assertTrue(ok, issues)
        self.assertEqual(d["artifact_type"], ARTIFACT_TYPE)
        self.assertTrue(d["paper_only"])
        self.assertTrue(d["advisory"])
        self.assertTrue(d["no_external_venue_mutation"])
        self.assertFalse(d["live_trading_enabled"])
        self.assertFalse(d["next9_unblocked"])

    def test_rejects_live_next9_paper_false_advisory_false_external(self):
        for mutate in (
            lambda d: d.__setitem__("live_trading_enabled", True),
            lambda d: d.__setitem__("next9_unblocked", True),
            lambda d: d.__setitem__("paper_only", False),
            lambda d: d.__setitem__("advisory", False),
            lambda d: d.__setitem__("no_external_venue_mutation", False),
        ):
            d = self._d()
            mutate(d)
            ok, _ = validate_artifact(d)
            self.assertFalse(ok)

    def test_deterministic_seed_reproducibility(self):
        a = _strip(generate(cycles=4, seed=108108, write=False))
        b = _strip(generate(cycles=4, seed=108108, write=False))
        self.assertEqual(a, b)
        self.assertTrue(a["determinism"]["same_seed_cycles_reproduce_surface"])

    def test_coverage_finite_probes_bounds(self):
        d = self._d()
        cov = d["venue_symbol_coverage"]
        self.assertEqual(len(cov), len(VENUES) * len(SYMBOLS))
        for r in cov:
            self.assertTrue(r["paper_only"])
            self.assertTrue(r["probe_finite"])
            self.assertTrue(r["probe_bounds_within_limits"])
            self.assertTrue(r["probe_gates_ok"])
        self.assertTrue(d["seal_surface"]["bounds_ok"])
        self.assertTrue(d["campaign"]["gates_ok"])

    def test_bounds_risk_posture(self):
        d = self._d()
        rp = d["risk_posture"]
        self.assertTrue(rp["paper_only"])
        self.assertFalse(rp["next9_unblocked"])
        self.assertFalse(rp["live_trading_enabled"])
        self.assertTrue(rp["all_coverage_gates_ok"])
        bounds = d["determinism"]["bounds"]
        self.assertTrue(all(bounds.values()))

    def test_cli_no_write(self):
        env = os.environ.copy()
        env["PHASE_QUICK_VERIFY"] = "1"
        env["PYTHONPATH"] = str(REPO)
        p = subprocess.run(
            [PYTHON, SCRIPT, "--no-write", "--cycles", "4", "--seed", "108108"],
            cwd=REPO, env=env, capture_output=True, text=True, timeout=600,
        )
        self.assertEqual(p.returncode, 0, p.stderr + "\n" + p.stdout)
        out = json.loads(p.stdout)
        self.assertTrue(out["valid"])
        self.assertTrue(out["paper_only"])
        self.assertFalse(out["live_trading_enabled"])
        self.assertFalse(out["next9_unblocked"])
        self.assertTrue(out["deterministic"])
        self.assertIsNone(out.get("artifact_path"))

    def test_cross_refs_phase108_phase107_composes_paper_ops(self):
        d = self._d()
        refs = " ".join(d["cross_refs"] + d["evidence_refs"])
        for needle in ("Phase108AdaptiveToxicityResilientPostAttributionSealOrchestrator",
                       "Phase107AdaptiveToxicityResilientPostAttributionSealOrchestrator",
                       "composes=PHASE107,PHASE32", "PAPER_OPS_SESSION_GATE", "CONTINUOUS_VALIDATION"):
            self.assertIn(needle, refs)


def _strip(d):
    x = json.loads(json.dumps(d))
    x.pop("timestamp_utc", None)
    x.pop("validation", None)
    return x


if __name__ == "__main__":
    unittest.main()
