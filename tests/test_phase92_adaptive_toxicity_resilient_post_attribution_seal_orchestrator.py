from __future__ import annotations

import os

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

import threading  # noqa: E402

try:
    import src.orderflow.phase32_orderflow_alpha_integration as _p32  # noqa: F401
    _p32.OrderflowAlphaIntegrator.run_campaign = lambda self, cycles=80: {"phase": "PHASE32", "paper_only": True, "gates_ok": True, "cycles": cycles, "n_trades": 0}
except Exception:
    pass
try:
    import src.orderflow.phase58_flow_toxicity_mitigator as _p58  # noqa: F401
    if hasattr(_p58, "Phase58FlowToxicityMitigator"):
        _p58.Phase58FlowToxicityMitigator.run_campaign = lambda self, *a, **k: {"phase": "PHASE58", "paper_only": True, "gates_ok": True}
        _p58.Phase58FlowToxicityMitigator.mitigate = lambda self, *a, **k: {"mitigated": True, "paper_only": True, "avg_vpin": 0.18}
except Exception:
    pass
try:
    import src.risk.phase54_realtime_risk_fusion_engine as _p54  # noqa: F401
    if hasattr(_p54, "Phase54RealtimeRiskFusionEngine"):
        _p54.Phase54RealtimeRiskFusionEngine.run_campaign = lambda self, *a, **k: {"phase": "PHASE54", "paper_only": True, "gates_ok": True}
except Exception:
    pass
_orig = threading.Thread.start

def _safe(self, *a, **k):
    if not getattr(self, "daemon", False):
        self.daemon = True
    return _orig(self, *a, **k)
threading.Thread.start = _safe

from src.hedging.phase92_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (  # noqa: E402
    Phase92AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase92AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase92_post_attribution_seal_orchestrator_smoke() -> None:
    cfg = Phase92AdaptiveToxicityResilientPostAttributionSealConfig(seed=92092, paper_only=True, cycles=4)
    orch = Phase92AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
    rep = orch.run_post_attribution_seal_orchestration(cycles=4)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["phase"] == "PHASE92_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"
    assert rep["cycles"] == 4
    assert rep["n_seal_attestations"] > 0
    assert rep["n_hedging_seal_attestations"] > 0
    assert "composes" in rep
    assert rep["composes"][0] == "PHASE91"
    assert "PHASE90" in rep["composes"]
    assert "PHASE32" in rep["composes"]
