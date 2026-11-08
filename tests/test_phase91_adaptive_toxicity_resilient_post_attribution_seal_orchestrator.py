"""Smoke test: Phase91 hedging module (paper-only, stub/harness safe)."""
from __future__ import annotations

import os
import sys
import threading
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
os.environ.setdefault("PHASE_QUICK_VERIFY", "1")


def _apply_stubs():
    try:
        import src.orderflow.phase32_orderflow_alpha_integration as p32
        p32.OrderflowAlphaIntegrator.run_campaign = lambda self, cycles=80: {"phase": "PHASE32", "paper_only": True, "gates_ok": True, "cycles": cycles, "n_trades": 0}
    except Exception:
        pass
    try:
        import src.orderflow.phase58_flow_toxicity_mitigator as p58
        if hasattr(p58, "Phase58FlowToxicityMitigator"):
            p58.Phase58FlowToxicityMitigator.run_campaign = lambda self, *a, **k: {"phase": "PHASE58", "paper_only": True, "gates_ok": True}
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
            m = __import__(modname, fromlist=[clsname])
            c = getattr(m, clsname, None)
            if c:
                if hasattr(c, "evaluate_all"):
                    c.evaluate_all = lambda self, *a, **k: {"status": "ok", "paper_only": True}
                if hasattr(c, "evaluate_slo"):
                    c.evaluate_slo = lambda self, *a, **k: {"status": "ok", "paper_only": True}
        except Exception:
            pass
    _orig = threading.Thread.start
    threading.Thread.start = lambda self, *a, **k: (_orig(self.__class__(target=self._target, daemon=True, args=getattr(self,'_args',()), kwargs=getattr(self,'_kwargs',{}))) if False else (setattr(self, "daemon", True) or _orig(self, *a, **k)))


_apply_stubs()

from src.hedging.phase91_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (  # noqa: E402
    Phase91AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase91AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase91_smoke():
    orch = Phase91AdaptiveToxicityResilientPostAttributionSealOrchestrator(
        Phase91AdaptiveToxicityResilientPostAttributionSealConfig(seed=91091, paper_only=True, cycles=8)
    )
    rep = orch.run_post_attribution_seal_orchestration(cycles=8)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert "PHASE90" in rep["composes"]
    assert "PHASE32" in rep["composes"]
    print("MODULE_SMOKE_OK", rep["phase"], rep["paper_only"], rep["gates_ok"], bool("PHASE90" in rep["composes"]))


if __name__ == "__main__":
    test_phase91_smoke()
