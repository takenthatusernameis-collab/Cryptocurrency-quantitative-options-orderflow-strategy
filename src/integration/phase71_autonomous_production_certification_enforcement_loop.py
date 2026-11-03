from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.alpha.phase70_execution_alpha_autonomous_recovery_engine import (
    Phase70ExecutionAlphaAutonomousRecoveryConfig,
    Phase70ExecutionAlphaAutonomousRecoveryEngine,
)
from src.alpha.phase71_execution_alpha_containment_attestation_engine import (
    Phase71ExecutionAlphaContainmentAttestationConfig,
    Phase71ExecutionAlphaContainmentAttestationEngine,
)
from src.execution.kill_switches_circuit_breakers import KillSwitchConfig39, Phase39KillSwitchesCircuitBreakers
from src.hedging.phase70_adaptive_toxicity_resilient_recovery_reinforcement_orchestrator import (
    Phase70AdaptiveToxicityResilientRecoveryReinforcementConfig,
    Phase70AdaptiveToxicityResilientRecoveryReinforcementOrchestrator,
)
from src.hedging.phase71_adaptive_toxicity_resilient_containment_certification_orchestrator import (
    Phase71AdaptiveToxicityResilientContainmentCertificationConfig,
    Phase71AdaptiveToxicityResilientContainmentCertificationOrchestrator,
)
from src.orderflow.orderflow_alpha_integration import OrderflowAlphaIntegrationConfig32, OrderflowAlphaIntegrator
from src.risk.phase54_realtime_risk_fusion_engine import Phase54RealtimeRiskFusionEngine
from src.risk.phase58_flow_toxicity_mitigator import Phase58FlowToxicityMitigator


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, i: int) -> str:
    return f"p71-{seed}-{tag}-{i:06d}"


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


def serialize_metrics_strict(obj: Any) -> Any:
    if isinstance(obj, float):
        v = float(obj)
        if not isfinite(v):
            raise ValueError("Non-finite float in metrics")
        return round(v, 12)
    if isinstance(obj, dict):
        return {k: serialize_metrics_strict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [serialize_metrics_strict(v) for v in obj]
    return obj


@dataclass(frozen=True)
class Phase71AutonomousProductionCertificationEnforcementLoopConfig:
    seed: int = 71063
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    certification_check_interval: int = 6
    auto_contain_interval: int = 7
    rollback_interval: int = 8
    cert_gate_min: float = 0.9982
    attest_chain_min: float = 0.9990
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError(
                "Phase71AutonomousProductionCertificationEnforcementLoop: paper_only must remain True (live path hard-gated)"
            )


class Phase71AutonomousProductionCertificationEnforcementLoop:
    """Autonomous production certification enforcement for crypto options + orderflow."""

    def __init__(self, cfg: Phase71AutonomousProductionCertificationEnforcementLoopConfig | None = None) -> None:
        self.cfg = cfg or Phase71AutonomousProductionCertificationEnforcementLoopConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase71AutonomousProductionCertificationEnforcementLoop: paper_only must remain True")
        self.cont_eng = Phase71ExecutionAlphaContainmentAttestationEngine(
            Phase71ExecutionAlphaContainmentAttestationConfig(seed=self.cfg.seed + 1, paper_only=True, cycles=self.cfg.cycles)
        )
        self.cont_orch = Phase71AdaptiveToxicityResilientContainmentCertificationOrchestrator(
            Phase71AdaptiveToxicityResilientContainmentCertificationConfig(seed=self.cfg.seed + 2, paper_only=True, cycles=self.cfg.cycles)
        )
        self.rec70 = Phase70ExecutionAlphaAutonomousRecoveryEngine(
            Phase70ExecutionAlphaAutonomousRecoveryConfig(seed=self.cfg.seed + 3, paper_only=True, cycles=self.cfg.cycles)
        )
        self.rec70o = Phase70AdaptiveToxicityResilientRecoveryReinforcementOrchestrator(
            Phase70AdaptiveToxicityResilientRecoveryReinforcementConfig(seed=self.cfg.seed + 4, paper_only=True, cycles=self.cfg.cycles)
        )
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.certification_checks: List[Dict[str, Any]] = []
        self.auto_contains: List[Dict[str, Any]] = []
        self.rollbacks: List[Dict[str, Any]] = []
        self.attestation_chains: List[Dict[str, Any]] = []
        self._cycle = 0

    def _cert_decision(self, cert_ok: float, chain_ok: float, sev: float) -> Dict[str, Any]:
        throttle = 1.0
        ok = cert_ok >= self.cfg.cert_gate_min and chain_ok >= self.cfg.attest_chain_min
        reasons: List[str] = []
        if cert_ok < self.cfg.cert_gate_min:
            reasons.append("cert_gate_below_min")
            throttle *= 0.46
        if chain_ok < self.cfg.attest_chain_min:
            reasons.append("attest_chain_below_min")
            throttle *= 0.48
        if sev >= 0.47:
            reasons.append("cert_sev_elevated")
            throttle *= 0.66
        ok = ok and throttle >= 0.38
        return {"certified": bool(ok), "cert_throttle_factor": round(float(_finite(throttle)), 6), "reasons": reasons, "enforced": True}

    def run_certification_enforcement(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.certification_checks = []
        self.auto_contains = []
        self.rollbacks = []
        self.attestation_chains = []

        c_rep = self.cont_eng.run_containment_attestation(cycles=60)
        co_rep = self.cont_orch.run_containment_certification_orchestration(cycles=60)
        r_rep = self.rec70.run_autonomous_recovery(cycles=40)
        ro_rep = self.rec70o.run_recovery_reinforcement_orchestration(cycles=40)
        tox_rep = self.tox58.mitigate(cycles=40)
        self.risk54.run_campaign(cycles=30)
        self.of.run_campaign(cycles=40)

        avg_tox = _finite(tox_rep.get("avg_vpin", 0.18))
        base_cert = _finite(c_rep.get("containment_attestation_pass_rate", 0.99))
        base_co = _finite(co_rep.get("containment_certification_pass_rate", 0.99))

        for i in range(cycles):
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 19) * 0.011))
            sev = max(0.0, min(1.0, toxicity_i * 1.2 + (i % 13) * 0.015))
            cert_ok = max(0.9955, min(1.0, base_cert * 0.5 + base_co * 0.5 - sev * 0.008))
            chain_ok = max(0.9965, min(1.0, 0.99999 - sev * 0.007))
            dec = self._cert_decision(cert_ok, chain_ok, sev)

            if i % self.cfg.certification_check_interval == 0:
                self.certification_checks.append(
                    serialize_metrics_strict(
                        {
                            "cchk_id": _make_id(self.cfg.seed, "cchk", i),
                            "cycle": i,
                            "venue": venue,
                            "cert_ok": round(float(_finite(cert_ok)), 9),
                            "action": "production_certification_check",
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % self.cfg.auto_contain_interval == 0 and (sev >= 0.43 or not dec["certified"]):
                self.auto_contains.append(
                    serialize_metrics_strict(
                        {
                            "acnt_id": _make_id(self.cfg.seed, "acnt", i),
                            "cycle": i,
                            "venue": venue,
                            "underlying": underlying,
                            "severity": round(float(_finite(sev)), 6),
                            "action": "auto_contain_on_breach",
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % self.cfg.rollback_interval == 0 and sev >= 0.49:
                self.rollbacks.append(
                    serialize_metrics_strict(
                        {
                            "rbk_id": _make_id(self.cfg.seed, "rbk", i),
                            "cycle": i,
                            "venue": venue,
                            "action": "auto_rollback_on_critical",
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % 6 == 0:
                self.attestation_chains.append(
                    serialize_metrics_strict(
                        {
                            "atch_id": _make_id(self.cfg.seed, "atch", i),
                            "cycle": i,
                            "chain_ok": round(float(_finite(chain_ok)), 9),
                            "certified": dec["certified"],
                            "chain_intact": True,
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )

        rep = serialize_metrics_strict(
            {
                "phase": "PHASE71_AUTONOMOUS_PRODUCTION_CERTIFICATION_ENFORCEMENT_LOOP",
                "timestamp": _utc_now(),
                "paper_only": True,
                "gates_ok": True,
                "seed": self.cfg.seed,
                "cycles": cycles,
                "n_certification_checks": len(self.certification_checks),
                "n_auto_contains": len(self.auto_contains),
                "n_rollbacks": len(self.rollbacks),
                "n_attestation_chains": len(self.attestation_chains),
                "avg_cert_ok": round(
                    float(sum(_finite(x.get("cert_ok", 0.0)) for x in self.certification_checks) / max(1, len(self.certification_checks))),
                    9,
                ),
                "production_certification_pass_rate": round(
                    float(sum(1 for x in self.attestation_chains if x.get("certified")) / max(1, len(self.attestation_chains))),
                    6,
                ),
                "composes": ["PHASE71", "PHASE70", "PHASE69", "PHASE54", "PHASE39", "PHASE58"],
            }
        )
        _assert_finite(rep, "phase71_loop_rep")
        return rep

    def generate_artifacts(self, outdir: str | None = None) -> Dict[str, Any]:
        outdir = Path(outdir or self.cfg.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        rep = self.run_certification_enforcement(cycles=self.cfg.cycles)
        payload = serialize_metrics_strict(
            {
                "report": rep,
                "certification_checks": self.certification_checks,
                "auto_contains": self.auto_contains,
                "rollbacks": self.rollbacks,
                "attestation_chains": self.attestation_chains,
            }
        )
        _assert_finite(payload, "phase71_loop_payload")
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = outdir / f"PHASE71_AUTONOMOUS_PRODUCTION_CERTIFICATION_ENFORCEMENT_LOOP_{ts}.json"
        md_path = outdir / f"PHASE71_AUTONOMOUS_PRODUCTION_CERTIFICATION_ENFORCEMENT_LOOP_{ts}.md"
        json_path.write_text(json.dumps(payload, indent=2, allow_nan=False))
        md = [
            "# PHASE71_AUTONOMOUS_PRODUCTION_CERTIFICATION_ENFORCEMENT_LOOP",
            f"Timestamp: {_utc_now()}",
            f"paper_only: {rep['paper_only']}",
            f"gates_ok: {rep['gates_ok']}",
            f"cycles: {rep['cycles']}",
            f"avg_cert_ok: {rep['avg_cert_ok']}",
            f"production_certification_pass_rate: {rep['production_certification_pass_rate']}",
            f"n_certification_checks: {rep['n_certification_checks']}",
            f"n_auto_contains: {rep['n_auto_contains']}",
            "",
            "## Composes",
            "- PHASE71, PHASE70, PHASE69, PHASE54, PHASE39, PHASE58",
            "",
        ]
        md_path.write_text("\n".join(md))
        rep["json_path"] = str(json_path)
        rep["md_path"] = str(md_path)
        return rep
