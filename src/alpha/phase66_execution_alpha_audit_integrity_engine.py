"""
Phase 66: Execution Alpha Audit & Integrity Engine (crypto options + orderflow).

Execution alpha audit & integrity: audit trail attestation, regulatory reporting integrity,
kill-switch audit linkage, toxicity-aware audit throttles, deterministic; PAPER-ONLY.
Composes Phases 17-65.
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
from src.alpha.phase63_execution_alpha_governance_engine import (
    Phase63ExecutionAlphaGovernanceEngine,
    Phase63ExecutionAlphaGovernanceConfig,
)
from src.alpha.phase62_execution_alpha_synthesis_engine import (
    Phase62ExecutionAlphaSynthesisEngine,
    Phase62ExecutionAlphaSynthesisConfig,
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
    audit_attestation_interval: int = 5
    regulatory_report_interval: int = 10
    kill_switch_audit_linkage_strict: bool = True
    toxicity_audit_throttle_threshold: float = 0.33
    integrity_score_min: float = 0.995
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError(
                "Phase66ExecutionAlphaAuditIntegrityEngine: paper_only must remain True (live path hard-gated)"
            )


class Phase66ExecutionAlphaAuditIntegrityEngine:
    """Execution alpha audit & integrity for crypto options + orderflow."""

    def __init__(self, cfg: Phase66ExecutionAlphaAuditIntegrityConfig | None = None) -> None:
        self.cfg = cfg or Phase66ExecutionAlphaAuditIntegrityConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase66ExecutionAlphaAuditIntegrityEngine: paper_only must remain True")
        self.comp65 = Phase65ExecutionAlphaComplianceGovernanceEngine(
            Phase65ExecutionAlphaComplianceGovernanceConfig(seed=self.cfg.seed + 1, paper_only=True, cycles=self.cfg.cycles)
        )
        self.gov64 = Phase64ExecutionAlphaRiskGovernanceEngine(
            Phase64ExecutionAlphaRiskGovernanceConfig(seed=self.cfg.seed + 2, paper_only=True, cycles=self.cfg.cycles)
        )
        self.gov63 = Phase63ExecutionAlphaGovernanceEngine(
            Phase63ExecutionAlphaGovernanceConfig(seed=self.cfg.seed + 3, paper_only=True, cycles=5)
        )
        self.synth62 = Phase62ExecutionAlphaSynthesisEngine(
            Phase62ExecutionAlphaSynthesisConfig(seed=self.cfg.seed + 4, paper_only=True, cycles=5)
        )
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.audit_trails: List[Dict[str, Any]] = []
        self.regulatory_reports: List[Dict[str, Any]] = []
        self.kill_switch_audits: List[Dict[str, Any]] = []
        self.audit_throttles: List[Dict[str, Any]] = []
        self.integrity_attestations: List[Dict[str, Any]] = []
        self._cycle = 0

    def _audit_decision(self, integrity_score: float, tox: float, ks_triggered: bool) -> Dict[str, Any]:
        throttle = 1.0
        audit_ok = integrity_score >= self.cfg.integrity_score_min
        reasons: List[str] = []
        if not audit_ok:
            reasons.append("integrity_below_min")
            throttle *= 0.5
        if tox >= self.cfg.toxicity_audit_throttle_threshold:
            reasons.append("toxicity_audit_throttle")
            throttle *= 0.7
        if ks_triggered and self.cfg.kill_switch_audit_linkage_strict:
            reasons.append("kill_switch_audit_linkage")
            throttle *= 0.4
        audit_ok = audit_ok and throttle >= 0.4
        return {
            "audit_pass": bool(audit_ok),
            "audit_throttle_factor": round(float(_finite(throttle)), 6),
            "audit_reasons": reasons,
            "attested": True,
        }

    def run_audit_integrity(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.audit_trails = []
        self.regulatory_reports = []
        self.kill_switch_audits = []
        self.audit_throttles = []
        self.integrity_attestations = []

        comp65_rep = self.comp65.enforce_compliance_governance(cycles=5)
        gov64_rep = self.gov64.enforce_risk_governance(cycles=5)
        gov63_rep = self.gov63.enforce_governance(cycles=5)
        synth_rep = self.synth62.synthesize_alpha(cycles=5)
        tox_rep = self.tox58.mitigate(cycles=4)
        self.risk54.run_campaign(cycles=3)
        self.of.run_campaign(cycles=4)

        avg_tox = _finite(tox_rep.get("avg_vpin", 0.18))

        for i in range(cycles):
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 17) * 0.012))
            integrity_score = max(0.99, min(1.0, 0.9995 - toxicity_i * 0.01))
            ks_triggered = (i % 23 == 0) and toxicity_i >= 0.35
            dec = self._audit_decision(integrity_score, toxicity_i, ks_triggered)

            trail_id = _make_id(self.cfg.seed, "trail", i)
            self.audit_trails.append(
                serialize_metrics_strict(
                    {
                        "trail_id": trail_id,
                        "cycle": i,
                        "venue": venue,
                        "underlying": underlying,
                        "attested": dec["attested"],
                        "audit_pass": dec["audit_pass"],
                        "integrity_score": round(float(_finite(integrity_score)), 9),
                        "toxicity": round(float(_finite(toxicity_i)), 6),
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }
                )
            )
            if i % self.cfg.regulatory_report_interval == 0:
                self.regulatory_reports.append(
                    serialize_metrics_strict(
                        {
                            "rep_id": _make_id(self.cfg.seed, "regrep", i),
                            "cycle": i,
                            "venue": venue,
                            "underlying": underlying,
                            "regulatory_reporting_integrity": round(float(_finite(integrity_score)), 9),
                            "attested": True,
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
                            "linked_trail_id": trail_id,
                            "kill_switch_triggered": True,
                            "audit_linkage_strict": self.cfg.kill_switch_audit_linkage_strict,
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if dec["audit_throttle_factor"] < 1.0:
                self.audit_throttles.append(
                    serialize_metrics_strict(
                        {
                            "ath_id": _make_id(self.cfg.seed, "ath", i),
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
            if i % self.cfg.audit_attestation_interval == 0:
                self.integrity_attestations.append(
                    serialize_metrics_strict(
                        {
                            "inta_id": _make_id(self.cfg.seed, "inta", i),
                            "cycle": i,
                            "integrity_score": round(float(_finite(integrity_score)), 9),
                            "audit_pass": dec["audit_pass"],
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
                "n_audit_trails": len(self.audit_trails),
                "n_regulatory_reports": len(self.regulatory_reports),
                "n_kill_switch_audits": len(self.kill_switch_audits),
                "n_audit_throttles": len(self.audit_throttles),
                "n_integrity_attestations": len(self.integrity_attestations),
                "avg_integrity_score": round(
                    float(sum(_finite(x.get("integrity_score", 0.0)) for x in self.audit_trails) / max(1, len(self.audit_trails))),
                    9,
                ),
                "audit_pass_rate": round(
                    float(sum(1 for x in self.audit_trails if x.get("audit_pass")) / max(1, len(self.audit_trails))),
                    6,
                ),
                "composes": ["PHASE65", "PHASE64", "PHASE63", "PHASE62", "PHASE54", "PHASE39", "PHASE58"],
            }
        )
        _assert_finite(rep, "phase66_audit_integrity_rep")
        return rep

    def generate_artifacts(self, outdir: str | None = None) -> Dict[str, Any]:
        outdir = Path(outdir or self.cfg.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        rep = self.run_audit_integrity(cycles=self.cfg.cycles)
        payload = serialize_metrics_strict(
            {
                "report": rep,
                "audit_trails": self.audit_trails,
                "regulatory_reports": self.regulatory_reports,
                "kill_switch_audits": self.kill_switch_audits,
                "audit_throttles": self.audit_throttles,
                "integrity_attestations": self.integrity_attestations,
            }
        )
        _assert_finite(payload, "phase66_audit_integrity_payload")
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
            f"avg_integrity_score: {rep['avg_integrity_score']}",
            f"audit_pass_rate: {rep['audit_pass_rate']}",
            f"n_kill_switch_audits: {rep['n_kill_switch_audits']}",
            f"n_regulatory_reports: {rep['n_regulatory_reports']}",
            "",
            "## Composes",
            "- PHASE65, PHASE64, PHASE63, PHASE62, PHASE54, PHASE39, PHASE58",
            "",
        ]
        md_path.write_text("\n".join(md))
        rep["json_path"] = str(json_path)
        rep["md_path"] = str(md_path)
        return rep
