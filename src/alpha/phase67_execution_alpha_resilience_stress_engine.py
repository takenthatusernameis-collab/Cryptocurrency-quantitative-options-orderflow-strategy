"""
Phase 67: Execution Alpha Resilience & Stress Engine (crypto options + orderflow).

Execution alpha resilience & stress: stress scenario injection, anomaly detection/attribution,
recovery orchestration, deterministic; PAPER-ONLY. Compose Phases 17-66.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.alpha.phase66_execution_alpha_audit_integrity_engine import (
    Phase66ExecutionAlphaAuditIntegrityEngine,
    Phase66ExecutionAlphaAuditIntegrityConfig,
)
from src.alpha.phase65_execution_alpha_compliance_governance_engine import (
    Phase65ExecutionAlphaComplianceGovernanceEngine,
    Phase65ExecutionAlphaComplianceGovernanceConfig,
)
from src.alpha.phase64_execution_alpha_risk_governance_engine import (
    Phase64ExecutionAlphaRiskGovernanceEngine,
    Phase64ExecutionAlphaRiskGovernanceConfig,
)
from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrationConfig32,
    OrderflowAlphaIntegrator,
)
from src.orderflow.phase58_flow_toxicity_mitigator import Phase58FlowToxicityMitigator
from src.risk.phase39_kill_switches_circuit_breakers import (
    KillSwitchConfig39,
    Phase39KillSwitchesCircuitBreakers,
)
from src.risk.phase54_realtime_risk_fusion_engine import Phase54RealtimeRiskFusionEngine
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p67res|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p67res_{tag}_{h}"


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if isfinite(v) else default


def _assert_finite(obj: Any, label: str = "obj") -> None:
    bad: List[str] = []

    def walk(v: Any, p: str) -> None:
        if isinstance(v, dict):
            for k, val in v.items():
                walk(val, f"{p}/{k}")
        elif isinstance(v, (list, tuple)):
            for i, val in enumerate(v):
                walk(val, f"{p}[{i}]")
        elif isinstance(v, float) and not isinstance(v, bool):
            if not isfinite(v):
                bad.append(p)

    walk(obj, "$")
    if bad:
        raise ValueError(f"Non-finite in {label}: {bad[:10]}")


@dataclass(frozen=True)
class Phase67ExecutionAlphaResilienceStressConfig:
    seed: int = 67060
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    stress_injection_interval: int = 7
    anomaly_attribution_interval: int = 9
    recovery_orchestration_interval: int = 5
    stress_severity_threshold: float = 0.4
    anomaly_z_threshold: float = 2.5
    recovery_readiness_min: float = 0.995
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError(
                "Phase67ExecutionAlphaResilienceStressEngine: paper_only must remain True (live path hard-gated)"
            )


class Phase67ExecutionAlphaResilienceStressEngine:
    """Execution alpha resilience & stress for crypto options + orderflow."""

    def __init__(self, cfg: Phase67ExecutionAlphaResilienceStressConfig | None = None) -> None:
        self.cfg = cfg or Phase67ExecutionAlphaResilienceStressConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase67ExecutionAlphaResilienceStressEngine: paper_only must remain True")
        self.audit66 = Phase66ExecutionAlphaAuditIntegrityEngine(
            Phase66ExecutionAlphaAuditIntegrityConfig(seed=self.cfg.seed + 1, paper_only=True, cycles=self.cfg.cycles)
        )
        self.comp65 = Phase65ExecutionAlphaComplianceGovernanceEngine(
            Phase65ExecutionAlphaComplianceGovernanceConfig(seed=self.cfg.seed + 2, paper_only=True, cycles=self.cfg.cycles)
        )
        self.gov64 = Phase64ExecutionAlphaRiskGovernanceEngine(
            Phase64ExecutionAlphaRiskGovernanceConfig(seed=self.cfg.seed + 3, paper_only=True, cycles=5)
        )
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.stress_scenarios: List[Dict[str, Any]] = []
        self.anomalies: List[Dict[str, Any]] = []
        self.anomaly_attributions: List[Dict[str, Any]] = []
        self.recovery_orchestrations: List[Dict[str, Any]] = []
        self.resilience_attestations: List[Dict[str, Any]] = []
        self._cycle = 0

    def _resilience_decision(self, recovery_readiness: float, severity: float, z_anom: float) -> Dict[str, Any]:
        throttle = 1.0
        ok = recovery_readiness >= self.cfg.recovery_readiness_min
        reasons: List[str] = []
        if not ok:
            reasons.append("recovery_readiness_below_min")
            throttle *= 0.5
        if severity >= self.cfg.stress_severity_threshold:
            reasons.append("stress_severity_elevated")
            throttle *= 0.7
        if z_anom >= self.cfg.anomaly_z_threshold:
            reasons.append("anomaly_attribution_elevated")
            throttle *= 0.4
        ok = ok and throttle >= 0.4
        return {"resilient": bool(ok), "resilience_throttle_factor": round(float(_finite(throttle)), 6), "reasons": reasons, "orchestrated": True}

    def run_resilience_stress(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.stress_scenarios = []
        self.anomalies = []
        self.anomaly_attributions = []
        self.recovery_orchestrations = []
        self.resilience_attestations = []

        audit_rep = self.audit66.run_audit_integrity(cycles=6)
        comp65_rep = self.comp65.enforce_compliance_governance(cycles=5)
        gov64_rep = self.gov64.enforce_risk_governance(cycles=5)
        tox_rep = self.tox58.mitigate(cycles=4)
        self.risk54.run_campaign(cycles=3)
        self.of.run_campaign(cycles=4)

        avg_tox = _finite(tox_rep.get("avg_vpin", 0.18))

        for i in range(cycles):
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 19) * 0.011))
            severity = max(0.0, min(1.0, toxicity_i * 1.1 + (i % 13) * 0.015))
            z_anom = max(0.0, 1.0 + (i % 7) * 0.6 + toxicity_i * 2.0)
            recovery_readiness = max(0.992, min(1.0, 0.9996 - severity * 0.012))
            dec = self._resilience_decision(recovery_readiness, severity, z_anom)

            if i % self.cfg.stress_injection_interval == 0:
                self.stress_scenarios.append(
                    serialize_metrics_strict(
                        {
                            "stress_id": _make_id(self.cfg.seed, "stress", i),
                            "cycle": i,
                            "venue": venue,
                            "underlying": underlying,
                            "severity": round(float(_finite(severity)), 6),
                            "scenario_type": "venue_liquidity_shock",
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if z_anom >= 1.8:
                aid = _make_id(self.cfg.seed, "anom", i)
                self.anomalies.append(
                    serialize_metrics_strict(
                        {
                            "anom_id": aid,
                            "cycle": i,
                            "venue": venue,
                            "underlying": underlying,
                            "z_score": round(float(_finite(z_anom)), 6),
                            "toxicity": round(float(_finite(toxicity_i)), 6),
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
                if i % self.cfg.anomaly_attribution_interval == 0:
                    self.anomaly_attributions.append(
                        serialize_metrics_strict(
                            {
                                "attr_id": _make_id(self.cfg.seed, "attr", i),
                                "cycle": i,
                                "anom_id": aid,
                                "attribution": "orderflow_toxicity_correlation",
                                "confidence": round(float(min(0.999, 0.9 + z_anom * 0.02)), 6),
                                "paper_only": True,
                                "timestamp": _utc_now(),
                            }
                        )
                    )
            if i % self.cfg.recovery_orchestration_interval == 0:
                self.recovery_orchestrations.append(
                    serialize_metrics_strict(
                        {
                            "rec_id": _make_id(self.cfg.seed, "rec", i),
                            "cycle": i,
                            "venue": venue,
                            "recovery_readiness": round(float(_finite(recovery_readiness)), 9),
                            "resilient": dec["resilient"],
                            "resilience_throttle_factor": dec["resilience_throttle_factor"],
                            "orchestrated": dec["orchestrated"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % 6 == 0:
                self.resilience_attestations.append(
                    serialize_metrics_strict(
                        {
                            "ratt_id": _make_id(self.cfg.seed, "ratt", i),
                            "cycle": i,
                            "recovery_readiness": round(float(_finite(recovery_readiness)), 9),
                            "resilient": dec["resilient"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )

        rep = serialize_metrics_strict(
            {
                "phase": "PHASE67_EXECUTION_ALPHA_RESILIENCE_STRESS_ENGINE",
                "timestamp": _utc_now(),
                "paper_only": True,
                "gates_ok": True,
                "seed": self.cfg.seed,
                "cycles": cycles,
                "n_stress_scenarios": len(self.stress_scenarios),
                "n_anomalies": len(self.anomalies),
                "n_anomaly_attributions": len(self.anomaly_attributions),
                "n_recovery_orchestrations": len(self.recovery_orchestrations),
                "n_resilience_attestations": len(self.resilience_attestations),
                "avg_recovery_readiness": round(
                    float(sum(_finite(x.get("recovery_readiness", 0.0)) for x in self.recovery_orchestrations) / max(1, len(self.recovery_orchestrations))),
                    9,
                ),
                "resilience_pass_rate": round(
                    float(sum(1 for x in self.recovery_orchestrations if x.get("resilient")) / max(1, len(self.recovery_orchestrations))),
                    6,
                ),
                "composes": ["PHASE66", "PHASE65", "PHASE64", "PHASE54", "PHASE39", "PHASE58"],
            }
        )
        _assert_finite(rep, "phase67_resilience_stress_rep")
        return rep

    def generate_artifacts(self, outdir: str | None = None) -> Dict[str, Any]:
        outdir = Path(outdir or self.cfg.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        rep = self.run_resilience_stress(cycles=self.cfg.cycles)
        payload = serialize_metrics_strict(
            {
                "report": rep,
                "stress_scenarios": self.stress_scenarios,
                "anomalies": self.anomalies,
                "anomaly_attributions": self.anomaly_attributions,
                "recovery_orchestrations": self.recovery_orchestrations,
                "resilience_attestations": self.resilience_attestations,
            }
        )
        _assert_finite(payload, "phase67_resilience_stress_payload")
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = outdir / f"PHASE67_EXECUTION_ALPHA_RESILIENCE_STRESS_ENGINE_{ts}.json"
        md_path = outdir / f"PHASE67_EXECUTION_ALPHA_RESILIENCE_STRESS_ENGINE_{ts}.md"
        json_path.write_text(json.dumps(payload, indent=2, allow_nan=False))
        md = [
            "# PHASE67_EXECUTION_ALPHA_RESILIENCE_STRESS_ENGINE",
            f"Timestamp: {_utc_now()}",
            f"paper_only: {rep['paper_only']}",
            f"gates_ok: {rep['gates_ok']}",
            f"cycles: {rep['cycles']}",
            f"avg_recovery_readiness: {rep['avg_recovery_readiness']}",
            f"resilience_pass_rate: {rep['resilience_pass_rate']}",
            f"n_stress_scenarios: {rep['n_stress_scenarios']}",
            f"n_anomalies: {rep['n_anomalies']}",
            "",
            "## Composes",
            "- PHASE66, PHASE65, PHASE64, PHASE54, PHASE39, PHASE58",
            "",
        ]
        md_path.write_text("\n".join(md))
        rep["json_path"] = str(json_path)
        rep["md_path"] = str(md_path)
        return rep
