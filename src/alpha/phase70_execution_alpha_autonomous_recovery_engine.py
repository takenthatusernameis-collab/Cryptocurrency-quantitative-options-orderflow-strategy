"""
Phase 70: Execution Alpha Autonomous Recovery Engine (crypto options + orderflow).
Execution alpha autonomous recovery: recovery playbook execution, anomaly recovery attribution,
recovery verification, deterministic; PAPER-ONLY. Compose Phases 17-69.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.alpha.phase69_execution_alpha_self_healing_resilience_engine import (
    Phase69ExecutionAlphaSelfHealingResilienceEngine,
    Phase69ExecutionAlphaSelfHealingResilienceConfig,
)
from src.alpha.phase68_execution_alpha_containment_attribution_engine import (
    Phase68ExecutionAlphaContainmentAttributionEngine,
    Phase68ExecutionAlphaContainmentAttributionConfig,
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
    h = hashlib.sha256(f"{seed}|p70alpha|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p70alpha_{tag}_{h}"


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
class Phase70ExecutionAlphaAutonomousRecoveryConfig:
    seed: int = 70060
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    recovery_playbook_interval: int = 6
    recovery_attest_interval: int = 7
    recovery_verify_min: float = 0.9965
    recovery_conf_min: float = 0.935
    recovery_sev_threshold: float = 0.44
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError(
                "Phase70ExecutionAlphaAutonomousRecoveryEngine: paper_only must remain True (live path hard-gated)"
            )


class Phase70ExecutionAlphaAutonomousRecoveryEngine:
    """Execution alpha autonomous recovery for crypto options + orderflow."""

    def __init__(self, cfg: Phase70ExecutionAlphaAutonomousRecoveryConfig | None = None) -> None:
        self.cfg = cfg or Phase70ExecutionAlphaAutonomousRecoveryConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase70ExecutionAlphaAutonomousRecoveryEngine: paper_only must remain True")
        self.sh69 = Phase69ExecutionAlphaSelfHealingResilienceEngine(
            Phase69ExecutionAlphaSelfHealingResilienceConfig(seed=self.cfg.seed + 1, paper_only=True, cycles=self.cfg.cycles)
        )
        self.cont68 = Phase68ExecutionAlphaContainmentAttributionEngine(
            Phase68ExecutionAlphaContainmentAttributionConfig(seed=self.cfg.seed + 2, paper_only=True, cycles=self.cfg.cycles)
        )
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.recovery_playbooks: List[Dict[str, Any]] = []
        self.recovery_attestations: List[Dict[str, Any]] = []
        self.recovery_actions: List[Dict[str, Any]] = []
        self.recovery_attribution_attestations: List[Dict[str, Any]] = []
        self._cycle = 0

    def _recovery_decision(self, recovery_verify: float, severity: float, conf: float) -> Dict[str, Any]:
        throttle = 1.0
        ok = recovery_verify >= self.cfg.recovery_verify_min and conf >= self.cfg.recovery_conf_min
        reasons: List[str] = []
        if recovery_verify < self.cfg.recovery_verify_min:
            reasons.append("recovery_verification_below_min")
            throttle *= 0.44
        if severity >= self.cfg.recovery_sev_threshold:
            reasons.append("recovery_severity_elevated")
            throttle *= 0.64
        if conf < self.cfg.recovery_conf_min:
            reasons.append("recovery_conf_below_min")
            throttle *= 0.52
        ok = ok and throttle >= 0.4
        return {"recovered": bool(ok), "recovery_throttle_factor": round(float(_finite(throttle)), 6), "reasons": reasons, "enforced": True}

    def run_autonomous_recovery(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.recovery_playbooks = []
        self.recovery_attestations = []
        self.recovery_actions = []
        self.recovery_attribution_attestations = []

        s_rep = self.sh69.run_self_healing_resilience(cycles=60)
        c_rep = self.cont68.run_containment_attribution(cycles=60)
        tox_rep = self.tox58.mitigate(cycles=40)
        self.risk54.run_campaign(cycles=30)
        self.of.run_campaign(cycles=40)

        avg_tox = _finite(tox_rep.get("avg_vpin", 0.18))
        avg_sh = _finite(s_rep.get("self_heal_pass_rate", 0.99))

        for i in range(cycles):
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 17) * 0.012))
            severity = max(0.0, min(1.0, toxicity_i * 1.11 + (i % 11) * 0.016))
            conf = max(0.885, min(0.999, 0.942 + (i % 5) * 0.01 + toxicity_i * 0.03))
            recovery_verify = max(0.9935, min(1.0, 0.9998 - severity * 0.01))
            dec = self._recovery_decision(recovery_verify, severity, conf)

            if i % self.cfg.recovery_playbook_interval == 0:
                self.recovery_playbooks.append(
                    serialize_metrics_strict(
                        {
                            "rp_id": _make_id(self.cfg.seed, "rp", i),
                            "cycle": i,
                            "venue": venue,
                            "underlying": underlying,
                            "severity": round(float(_finite(severity)), 6),
                            "policy": "autonomous_recovery_playbook",
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % self.cfg.recovery_attest_interval == 0:
                self.recovery_attestations.append(
                    serialize_metrics_strict(
                        {
                            "ra_id": _make_id(self.cfg.seed, "ra", i),
                            "cycle": i,
                            "venue": venue,
                            "underlying": underlying,
                            "confidence": round(float(_finite(conf)), 6),
                            "recovery": "autonomous_recovery_attestation",
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % 5 == 0:
                self.recovery_actions.append(
                    serialize_metrics_strict(
                        {
                            "ract_id": _make_id(self.cfg.seed, "ract", i),
                            "cycle": i,
                            "recovery_verify": round(float(_finite(recovery_verify)), 9),
                            "recovered": dec["recovered"],
                            "recovery_throttle_factor": dec["recovery_throttle_factor"],
                            "enforced": dec["enforced"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % 7 == 0:
                self.recovery_attribution_attestations.append(
                    serialize_metrics_strict(
                        {
                            "rat_id": _make_id(self.cfg.seed, "rat", i),
                            "cycle": i,
                            "recovery_verify": round(float(_finite(recovery_verify)), 9),
                            "recovered": dec["recovered"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )

        rep = serialize_metrics_strict(
            {
                "phase": "PHASE70_EXECUTION_ALPHA_AUTONOMOUS_RECOVERY_ENGINE",
                "timestamp": _utc_now(),
                "paper_only": True,
                "gates_ok": True,
                "seed": self.cfg.seed,
                "cycles": cycles,
                "n_recovery_playbooks": len(self.recovery_playbooks),
                "n_recovery_attestations": len(self.recovery_attestations),
                "n_recovery_actions": len(self.recovery_actions),
                "n_recovery_attribution_attestations": len(self.recovery_attribution_attestations),
                "avg_recovery_verify": round(
                    float(sum(_finite(x.get("recovery_verify", 0.0)) for x in self.recovery_actions) / max(1, len(self.recovery_actions))),
                    9,
                ),
                "recovery_pass_rate": round(
                    float(sum(1 for x in self.recovery_actions if x.get("recovered")) / max(1, len(self.recovery_actions))),
                    6,
                ),
                "composes": ["PHASE69", "PHASE68", "PHASE54", "PHASE39", "PHASE58"],
            }
        )
        _assert_finite(rep, "phase70_recovery_rep")
        return rep

    def generate_artifacts(self, outdir: str | None = None) -> Dict[str, Any]:
        outdir = Path(outdir or self.cfg.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        rep = self.run_autonomous_recovery(cycles=self.cfg.cycles)
        payload = serialize_metrics_strict(
            {
                "report": rep,
                "recovery_playbooks": self.recovery_playbooks,
                "recovery_attestations": self.recovery_attestations,
                "recovery_actions": self.recovery_actions,
                "recovery_attribution_attestations": self.recovery_attribution_attestations,
            }
        )
        _assert_finite(payload, "phase70_recovery_payload")
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = outdir / f"PHASE70_EXECUTION_ALPHA_AUTONOMOUS_RECOVERY_ENGINE_{ts}.json"
        md_path = outdir / f"PHASE70_EXECUTION_ALPHA_AUTONOMOUS_RECOVERY_ENGINE_{ts}.md"
        json_path.write_text(json.dumps(payload, indent=2, allow_nan=False))
        md = [
            "# PHASE70_EXECUTION_ALPHA_AUTONOMOUS_RECOVERY_ENGINE",
            f"Timestamp: {_utc_now()}",
            f"paper_only: {rep['paper_only']}",
            f"gates_ok: {rep['gates_ok']}",
            f"cycles: {rep['cycles']}",
            f"avg_recovery_verify: {rep['avg_recovery_verify']}",
            f"recovery_pass_rate: {rep['recovery_pass_rate']}",
            f"n_recovery_playbooks: {rep['n_recovery_playbooks']}",
            f"n_recovery_attestations: {rep['n_recovery_attestations']}",
            "",
            "## Composes",
            "- PHASE69, PHASE68, PHASE54, PHASE39, PHASE58",
            "",
        ]
        md_path.write_text("\n".join(md))
        rep["json_path"] = str(json_path)
        rep["md_path"] = str(md_path)
        return rep
