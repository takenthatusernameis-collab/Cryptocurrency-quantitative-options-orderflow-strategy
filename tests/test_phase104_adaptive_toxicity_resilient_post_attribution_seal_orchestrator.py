import os
import unittest

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from src.hedging.phase104_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase104AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase104AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


class TestPhase104Module(unittest.TestCase):
    def test_paper_only_hard_gate(self):
        with self.assertRaises(ValueError):
            Phase104AdaptiveToxicityResilientPostAttributionSealConfig(paper_only=False)

    def test_smoke(self):
        cfg = Phase104AdaptiveToxicityResilientPostAttributionSealConfig(seed=104104, cycles=4, paper_only=True)
        orch = Phase104AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
        rep = orch.run_post_attribution_seal_orchestration(cycles=4)
        self.assertTrue(rep["paper_only"])
        self.assertTrue(rep["gates_ok"])
        self.assertEqual(rep["phase"], "PHASE104_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR")
        self.assertEqual(rep["composes"], ["PHASE103", "PHASE32"])


if __name__ == "__main__":
    unittest.main()
