import os
import unittest

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from src.hedging.phase106_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase106AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase106AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


class TestPhase106Module(unittest.TestCase):
    def test_paper_only_hard_gate(self):
        with self.assertRaises(ValueError):
            Phase106AdaptiveToxicityResilientPostAttributionSealConfig(paper_only=False)

    def test_smoke(self):
        cfg = Phase106AdaptiveToxicityResilientPostAttributionSealConfig(seed=105105, cycles=4, paper_only=True)
        orch = Phase106AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
        rep = orch.run_post_attribution_seal_orchestration(cycles=4)
        self.assertTrue(rep["paper_only"])
        self.assertTrue(rep["gates_ok"])
        self.assertEqual(rep["phase"], "PHASE106_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR")
        self.assertEqual(rep["composes"], ["PHASE105", "PHASE32"])


if __name__ == "__main__":
    unittest.main()
