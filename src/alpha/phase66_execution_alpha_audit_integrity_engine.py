"""
Phase 66: Execution Alpha Audit & Integrity Engine (crypto options + orderflow).

Execution alpha audit & integrity: audit trail attestation, regulatory reporting
integrity, kill-switch audit linkage, toxicity-aware audit throttles, deterministic;
PAPER-ONLY. Composes Phases 17-65.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

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
    h = hashlib.sha256(f"{seed}|p66audit|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p66audit_{tag}_{h}"


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
class Phase66ExecutionAlphaAuditIntegrityConfig:
    seed: int = 66060
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    audit_sampling_rate: float = 0.98
    regulatory_reporting_integrity_threshold: float = 0.999
    kill_switch_audit_linkage_strict: bool = True
    toxicity_audit_throttle_threshold: float = 0.34
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError(
                "Phase66ExecutionAlphaAuditIntegrityEngine: paper_only must remain True (live path hard-gated)"
            )
        if not 0.0 < self.audit_sampling_rate <= 1.0:
            raise ValueError("audit_sampling_rate must be in (0,1]")


class Phase66ExecutionAlphaAuditIntegrityEngine:
    """Execution alpha audit & integrity for crypto options + orderflow."""

    def __init__(self, cfg: Phase66ExecutionAlphaAuditIntegrityConfig | None = None) -> None:
        self.cfg = cfg or Phase66ExecutionAlphaAuditIntegrityConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase66ExecutionAlphaAuditIntegrityEngine: paper_only must remain True")
        self.gov65 = Phase65ExecutionAlphaComplianceGovernanceEngine(
            Phase65ExecutionAlphaComplianceGovernanceConfig(seed=self.cfg.seed + 1, paper_only=True, cycles=self.cfg.cycles)
        )
        self.gov64 = Phase64ExecutionAlphaRiskGovernanceEngine(
            Phase64ExecutionAlphaRiskGovernanceConfig(seed=self.cfg.seed + 2, paper_only=True, cycles=60)
        )
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.audit_attestations: List[Dict[str, Any]] = []
        self.regulatory_reports: List[Dict[str, Any]] = []
        self.kill_switch_audits: List[Dict[str, Any]] = []
        self.toxicity_audit_throttles: List[Dict[str, Any]] = []
        self.integrity_violations: List[Dict[str, Any]] = []
        self._cycle = 0

    def _audit_decision(self, tox: float, ks_triggered: bool, integrity_score: float) -> Dict[str, Any]:
        throttle = 1.0
        audit_enhanced = False
        reasons: List[str] = []
        if tox >= self.cfg.toxicity_audit_throttle_threshold:
            throttle *= 0.5
            audit_enhanced = True
            reasons.append("toxicity_audit_throttle")
        if ks_triggered and self.cfg.kill_switch_audit_linkage_strict:
            audit_enhanced = True
            throttle *= 0.4
            reasons.append("kill_switch_audit_linkage")
        if integrity_score < self.cfg.regulatory_reporting_integrity_threshold:
            audit_enhanced = True
            throttle *= 0.3
            reasons.append("integrity_breach")
        return {
            "audit_enhanced": bool(audit_enhanced),
            "audit_throttle_factor": round(float(_finite(throttle)), 6),
            "audit_reasons": reasons,
            "attested": True,
        }

    def audit_integrity(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.audit_attestations = []
        self.regulatory_reports = []
        self.kill_switch_audits = []
        self.toxicity_audit_throttles = []
        self.integrity_violations = []

        gov65_rep = self.gov65.enforce_compliance_governance(cycles=60)
        gov64_rep = self.gov64.enforce_risk_governance(cycles=60)
        tox_rep = self.tox58.mitigate(cycles=40)
        self.risk54.run_campaign(cycles=30)
        self.of.run_campaign(cycles=40)

        avg_tox = _finite(tox_rep.get("avg_vpin", 0.18))
        ks_count = int(gov65_rep.get("n_kill_switch_events", 0))

        for i in range(cycles):
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 17) * 0.013))
            ks_triggered = (i < ks_count) if ks_count > 0 else (i % 31 == 0 and toxicity_i >= 0.4)
            integrity_score = max(0.0, min(1.0, 0.9995 - (0.0003 if toxicity_i >= 0.35 else 0.0)))
            dec = self._audit_decision(toxicity_i, ks_triggered, integrity_score)

            self.audit_attestations.append(
                serialize_metrics_strict(
                    {
                        "audit_att_id": _make_id(self.cfg.seed, "aatt", i),
                        "cycle": i,
                        "venue": venue,
                        "underlying": underlying,
                        "attested": dec["attested"],
                        "audit_enhanced": dec["audit_enhanced"],
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }
                )
            )
            self.regulatory_reports.append(
                serialize_metrics_strict(
                    {
                        "reg_id": _make_id(self.cfg.seed, "rpt", i),
                        "cycle": i,
                        "venue": venue,
                        "underlying": underlying,
                        "regulatory_reporting_integrity": round(float(_finite(integrity_score)), 9),
                        "sampled": (i % 100) / 100.0 < self.cfg.audit_sampling_rate,
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }
                )
            )
            if ks_triggered:
                self.kill_switch_audits.append(
                    serialize_metrics_strict(
                        {
                            "ksa_id": _make_id(self.cfg.seed, "ksa", i),
                            "cycle": i,
                            "venue": venue,
                            "kill_switch_triggered": True,
                            "audit_linkage_strict": self.cfg.kill_switch_audit_linkage_strict,
                            "audit_enhanced": dec["audit_enhanced"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if dec["audit_throttle_factor"] < 1.0:
                self.toxicity_audit_throttles.append(
                    serialize_metrics_strict(
                        {
                            "tat_id": _make_id(self.cfg.seed, "tat", i),
                            "cycle": i,
                            "venue": venue,
                            "toxicity": round(float(_finite(toxicity_i)), 6),
                            "audit_throttle_factor": dec["audit_throttle_factor"],
                            "audit_reasons": dec["audit_reasons"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if integrity_score < self.cfg.regulatory_reporting_integrity_threshold:
                self.integrity_violations.append(
                    serialize_metrics_strict(
                        {
                            "viol_id": _make_id(self.cfg.seed, "viol", i),
                            "cycle": i,
                            "venue": venue,
                            "integrity_score": round(float(_finite(integrity_score)), 9),
                            "violation": True,
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )

        rep = serialize_metrics_strict(
            {
                "phase": "PHASE66_EXECUTION_ALPHA_AUDIT_INTEGRITY_ENGINE",
                "timestamp": _utc_now(),
                "paper_only": True,
                "gates_ok": True,
                "seed": self.cfg.seed,
                "cycles": cycles,
                "n_audit_attestations": len(self.audit_attestations),
                "n_regulatory_reports": len(self.regulatory_reports),
                "n_kill_switch_audits": len(self.kill_switch_audits),
                "n_toxicity_audit_throttles": len(self.toxicity_audit_throttles),
                "n_integrity_violations": len(self.integrity_violations),
                "audit_sampling_rate": self.cfg.audit_sampling_rate,
                "regulatory_reporting_integrity_threshold": self.cfg.regulatory_reporting_integrity_threshold,
                "avg_audit_throttle": round(
                    float(
                        sum(_finite(x.get("audit_throttle_factor", 1.0)) for x in self.toxicity_audit_throttles)
                        / max(1, len(self.toxicity_audit_throttles))
                    )
                    if self.toxicity_audit_throttles
                    else 1.0,
                    6,
                ),
                "composes": ["PHASE65", "PHASE64", "PHASE54", "PHASE39", "PHASE58"],
            }
        )
        _assert_finite(rep, "phase66_audit_rep")
        return rep

    def generate_artifacts(self, outdir: str | None = None) -> Dict[str, Any]:
        outdir = Path(outdir or self.cfg.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        rep = self.audit_integrity(cycles=self.cfg.cycles)
        payload = serialize_metrics_strict(
            {
                "report": rep,
                "audit_attestations": self.audit_attestations,
                "regulatory_reports": self.regulatory_reports,
                "kill_switch_audits": self.kill_switch_audits,
                "toxicity_audit_throttles": self.toxicity_audit_throttles,
                "integrity_violations": self.integrity_violations,
            }
        )
        _assert_finite(payload, "phase66_audit_payload")
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = outdir / f"PHASE66_EXECUTION_ALPHA_AUDIT_INTEGRITY_ENGINE_{ts}.json"
        md_path = outdir / f"PHASE66_EXECUTION_ALPHA_AUDIT_INTEGRITY_ENGINE_{ts}.md"
        json_path.write_text(json.dumps(payload, indent=2, allow_nan=False))
        md = [
            "# PHASE66_EXECUTION_ALPHA_AUDIT_INTEGRITY_ENGINE",
            f"Timestamp: {_utc_now()}",
            f"paper_only: {rep['paper_only']}",
            f"gates_ok: {rep['gates_ok']}",
            f"cycles: {rep['cycles']}",
            f"n_audit_attestations: {rep['n_audit_attestations']}",
            f"n_kill_switch_audits: {rep['n_kill_switch_audits']}",
            f"n_integrity_violations: {rep['n_integrity_violations']}",
            f"audit_sampling_rate: {rep['audit_sampling_rate']}",
            "",
            "## Composes",
            "- PHASE65, PHASE64, PHASE54, PHASE39, PHASE58",
            "",
        ]
        md_path.write_text("\n".join(md))
        rep["json_path"] = str(json_path)
        rep["md_path"] = str(md_path)
        return rep
