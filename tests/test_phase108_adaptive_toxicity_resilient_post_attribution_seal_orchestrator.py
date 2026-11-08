import os
import unittest

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from src.hedging.phase108_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase108AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase108AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


class TestPhase108Module(unittest.TestCase):
    def test_paper_only_hard_gate(self):
        with self.assertRaises(ValueError):
            Phase108AdaptiveToxicityResilientPostAttributionSealConfig(paper_only=False)

    def test_smoke(self):
        cfg = Phase108AdaptiveToxicityResilientPostAttributionSealConfig(seed=108108, cycles=4, paper_only=True)
        orch = Phase108AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
        rep = orch.run_post_attribution_seal_orchestration(cycles=4)
        self.assertTrue(rep["paper_only"])
        self.assertTrue(rep["gates_ok"])
        self.assertEqual(rep["phase"], "PHASE108_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR")
        self.assertEqual(rep["composes"], ["PHASE107", "PHASE32"])


if __name__ == "__main__":
    unittest.main()
