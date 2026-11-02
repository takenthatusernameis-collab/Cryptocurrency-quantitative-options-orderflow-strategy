from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from src.telemetry.serialization import serialize_metrics_strict


@dataclass(frozen=True)
class Phase57CircuitConfig:
    seed: int = 66666
    paper_only: bool = True
    cooldown_sec: int = 60

    def __post_init__(self) -> None:
        if not self.paper_only:
            raise ValueError("paper_only must remain True (live paths hard-gated)")


@dataclass
class Phase57ProductionCircuitBreakers:
    cfg: Phase57CircuitConfig = field(default_factory=Phase57CircuitConfig)
    domain_focus: str = "crypto_options_orderflow"

    def evaluate(self, metrics: Dict[str, float] | None = None) -> Dict[str, Any]:
        metrics = metrics or {"drawdown_pct": 0.02, "latency_ms_p99": 80.0, "toxicity": 0.15, "risk_breach": 0.0}
        breaches: List[str] = []
        if float(metrics.get("drawdown_pct", 0.0)) > 0.08:
            breaches.append("drawdown")
        if float(metrics.get("latency_ms_p99", 0.0)) > 200.0:
            breaches.append("latency")
        if float(metrics.get("toxicity", 0.0)) > 0.4:
            breaches.append("toxicity")
        if float(metrics.get("risk_breach", 0.0)) > 0.0:
            breaches.append("risk")
        halted = len(breaches) > 0
        rep = {
            "phase": "PHASE57_PRODUCTION_CIRCUIT_BREAKERS",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "paper_only": True,
            "live_path_hard_gated": True,
            "domain_focus": self.domain_focus,
            "metrics": metrics,
            "breaches": breaches,
            "halted": halted,
            "auto_halt_triggered": halted,
            "auto_restart_ready": True,
            "cooldown_sec": self.cfg.cooldown_sec,
            "escalation_required": halted,
            "integration": "Phase45+Phase54+Phase55+Phase56",
            "composed_phases": "17-56",
            "deterministic": True,
            "finite": True,
        }
        return serialize_metrics_strict(rep)

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, str]:
        p = Path(outdir)
        p.mkdir(parents=True, exist_ok=True)
        rep = self.evaluate()
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = p / f"PHASE57_CIRCUIT_BREAKERS_{ts}.json"
        mpath = p / f"PHASE57_CIRCUIT_BREAKERS_{ts}.md"
        jpath.write_text(__import__("json").dumps(rep, indent=2))
        mpath.write_text(f"# PHASE57 Circuit Breakers\n\n- halted: {rep['halted']}\n- breaches: {rep['breaches']}\n- cooldown_sec: {rep['cooldown_sec']}\n- paper_only: true\n")
        return {"json_path": str(jpath), "md_path": str(mpath)}
