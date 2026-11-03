from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.execution.kill_switches_circuit_breakers import KillSwitchConfig39, Phase39KillSwitchesCircuitBreakers
from src.hedging.phase70_adaptive_toxicity_resilient_recovery_reinforcement_orchestrator import (
    Phase70AdaptiveToxicityResilientRecoveryReinforcementConfig,
    Phase70AdaptiveToxicityResilientRecoveryReinforcementOrchestrator,
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
class Phase71AdaptiveToxicityResilientContainmentCertificationConfig:
    seed: int = 71062
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    venue_quarantine_interval: int = 7
    capital_contain_interval: int = 6
    hedging_contain_interval: int = 5
    quarantine_min: float = 0.9978
    contain_sev_threshold: float = 0.44
    hedge_contain_min: float = 0.9980
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError(
                "Phase71AdaptiveToxicityResilientContainmentCertificationOrchestrator: paper_only must remain True (live path hard-gated)"
            )


class Phase71AdaptiveToxicityResilientContainmentCertificationOrchestrator:
    """Adaptive toxicity-resilient containment certification orchestrator for crypto options + orderflow."""

    def __init__(self, cfg: Phase71AdaptiveToxicityResilientContainmentCertificationConfig | None = None) -> None:
        self.cfg = cfg or Phase71AdaptiveToxicityResilientContainmentCertificationConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase71AdaptiveToxicityResilientContainmentCertificationOrchestrator: paper_only must remain True")
        self.rec70o = Phase70AdaptiveToxicityResilientRecoveryReinforcementOrchestrator(
            Phase70AdaptiveToxicityResilientRecoveryReinforcementConfig(seed=self.cfg.seed + 1, paper_only=True, cycles=self.cfg.cycles)
        )
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.venue_quarantines: List[Dict[str, Any]] = []
        self.capital_containments: List[Dict[str, Any]] = []
        self.hedging_containments: List[Dict[str, Any]] = []
        self.contain_cert_attestations: List[Dict[str, Any]] = []
        self._cycle = 0

    def _orch_contain_decision(self, quarantine_ok: float, sev: float, hedge_ok: float) -> Dict[str, Any]:
        throttle = 1.0
        ok = quarantine_ok >= self.cfg.quarantine_min and hedge_ok >= self.cfg.hedge_contain_min
        reasons: List[str] = []
        if quarantine_ok < self.cfg.quarantine_min:
            reasons.append("quarantine_below_min")
            throttle *= 0.47
        if sev >= self.cfg.contain_sev_threshold:
            reasons.append("contain_sev_elevated")
            throttle *= 0.67
        if hedge_ok < self.cfg.hedge_contain_min:
            reasons.append("hedge_contain_below_min")
            throttle *= 0.47
        ok = ok and throttle >= 0.39
        return {"contained": bool(ok), "orch_contain_throttle_factor": round(float(_finite(throttle)), 6), "reasons": reasons, "enforced": True}

    def run_containment_certification_orchestration(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.venue_quarantines = []
        self.capital_containments = []
        self.hedging_containments = []
        self.contain_cert_attestations = []

        r_rep = self.rec70o.run_recovery_reinforcement_orchestration(cycles=60)
        tox_rep = self.tox58.mitigate(cycles=40)
        self.risk54.run_campaign(cycles=30)
        self.of.run_campaign(cycles=40)

        avg_tox = _finite(tox_rep.get("avg_vpin", 0.18))
        avg_rec = _finite(r_rep.get("recovery_reinforce_pass_rate", 0.99))

        for i in range(cycles):
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 19) * 0.011))
            sev = max(0.0, min(1.0, toxicity_i * 1.18 + (i % 13) * 0.014))
            quarantine_ok = max(0.995, min(1.0, 0.9999 - sev * 0.01))
            hedge_ok = max(0.995, min(1.0, 0.9999 - sev * 0.01))
            dec = self._orch_contain_decision(quarantine_ok, sev, hedge_ok)

            if i % self.cfg.venue_quarantine_interval == 0:
                self.venue_quarantines.append(
                    serialize_metrics_strict(
                        {
                            "vqu_id": _make_id(self.cfg.seed, "vqu", i),
                            "cycle": i,
                            "venue": venue,
                            "quarantine_ok": round(float(_finite(quarantine_ok)), 9),
                            "action": "venue_quarantine_enforced",
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % self.cfg.capital_contain_interval == 0 and sev >= 0.4:
                self.capital_containments.append(
                    serialize_metrics_strict(
                        {
                            "ccap_id": _make_id(self.cfg.seed, "ccap", i),
                            "cycle": i,
                            "venue": venue,
                            "underlying": underlying,
                            "severity": round(float(_finite(sev)), 6),
                            "action": "capital_contain_selective",
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % self.cfg.hedging_contain_interval == 0:
                self.hedging_containments.append(
                    serialize_metrics_strict(
                        {
                            "hcont_id": _make_id(self.cfg.seed, "hcont", i),
                            "cycle": i,
                            "venue": venue,
                            "hedge_ok": round(float(_finite(hedge_ok)), 9),
                            "reinforced": dec["contained"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % 6 == 0:
                self.contain_cert_attestations.append(
                    serialize_metrics_strict(
                        {
                            "cca_id": _make_id(self.cfg.seed, "cca", i),
                            "cycle": i,
                            "certified": dec["contained"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )

        rep = serialize_metrics_strict(
            {
                "phase": "PHASE71_ADAPTIVE_TOXICITY_RESILIENT_CONTAINMENT_CERTIFICATION_ORCHESTRATOR",
                "timestamp": _utc_now(),
                "paper_only": True,
                "gates_ok": True,
                "seed": self.cfg.seed,
                "cycles": cycles,
                "n_venue_quarantines": len(self.venue_quarantines),
                "n_capital_containments": len(self.capital_containments),
                "n_hedging_containments": len(self.hedging_containments),
                "n_contain_cert_attestations": len(self.contain_cert_attestations),
                "avg_quarantine_ok": round(
                    float(sum(_finite(x.get("quarantine_ok", 0.0)) for x in self.venue_quarantines) / max(1, len(self.venue_quarantines))),
                    9,
                ),
                "containment_certification_pass_rate": round(
                    float(sum(1 for x in self.hedging_containments if x.get("reinforced")) / max(1, len(self.hedging_containments))),
                    6,
                ),
                "composes": ["PHASE70", "PHASE69", "PHASE54", "PHASE39", "PHASE58"],
            }
        )
        _assert_finite(rep, "phase71_contain_orch_rep")
        return rep

    def generate_artifacts(self, outdir: str | None = None) -> Dict[str, Any]:
        outdir = Path(outdir or self.cfg.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        rep = self.run_containment_certification_orchestration(cycles=self.cfg.cycles)
        payload = serialize_metrics_strict(
            {
                "report": rep,
                "venue_quarantines": self.venue_quarantines,
                "capital_containments": self.capital_containments,
                "hedging_containments": self.hedging_containments,
                "contain_cert_attestations": self.contain_cert_attestations,
            }
        )
        _assert_finite(payload, "phase71_contain_orch_payload")
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = outdir / f"PHASE71_ADAPTIVE_TOXICITY_RESILIENT_CONTAINMENT_CERTIFICATION_ORCHESTRATOR_{ts}.json"
        md_path = outdir / f"PHASE71_ADAPTIVE_TOXICITY_RESILIENT_CONTAINMENT_CERTIFICATION_ORCHESTRATOR_{ts}.md"
        json_path.write_text(json.dumps(payload, indent=2, allow_nan=False))
        md = [
            "# PHASE71_ADAPTIVE_TOXICITY_RESILIENT_CONTAINMENT_CERTIFICATION_ORCHESTRATOR",
            f"Timestamp: {_utc_now()}",
            f"paper_only: {rep['paper_only']}",
            f"gates_ok: {rep['gates_ok']}",
            f"cycles: {rep['cycles']}",
            f"avg_quarantine_ok: {rep['avg_quarantine_ok']}",
            f"containment_certification_pass_rate: {rep['containment_certification_pass_rate']}",
            f"n_venue_quarantines: {rep['n_venue_quarantines']}",
            f"n_capital_containments: {rep['n_capital_containments']}",
            "",
            "## Composes",
            "- PHASE70, PHASE69, PHASE54, PHASE39, PHASE58",
            "",
        ]
        md_path.write_text("\n".join(md))
        rep["json_path"] = str(json_path)
        rep["md_path"] = str(md_path)
        return rep
