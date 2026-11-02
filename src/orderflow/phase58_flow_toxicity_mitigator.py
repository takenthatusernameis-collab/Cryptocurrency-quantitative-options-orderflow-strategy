"""
Phase 58: Flow Toxicity Mitigator (crypto options + orderflow).

Flow toxicity mitigation: VPIN/toxicity scoring, adverse selection detection,
size caps, quarantine logic, deterministic. PAPER-ONLY, finite numerics.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrationConfig32,
    OrderflowAlphaIntegrator,
)
from src.orderflow.phase52_toxicity_resilient_flow_optimizer import Phase52ToxicityResilientFlowOptimizer
from src.risk.phase39_kill_switches_circuit_breakers import (
    KillSwitchConfig39,
    Phase39KillSwitchesCircuitBreakers,
)
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p58tox|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p58tox_{tag}_{h}"


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
class Phase58FlowToxicityMitigatorConfig:
    seed: int = 58058
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    vpin_threshold_warn: float = 0.25
    vpin_threshold_quarantine: float = 0.38
    adverse_sel_threshold: float = 0.32
    size_cap_warn_mult: float = 0.7
    size_cap_quarantine_mult: float = 0.4
    quarantine_cooldown_cycles: int = 5
    max_consecutive_quarantine: int = 3
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase58FlowToxicityMitigator: paper_only must remain True (live path hard-gated)")
        if not (0.0 <= self.vpin_threshold_warn <= 1.0):
            raise ValueError("vpin_threshold_warn must be in [0,1]")
        if not (0.0 <= self.vpin_threshold_quarantine <= 1.0):
            raise ValueError("vpin_threshold_quarantine must be in [0,1]")
        if self.vpin_threshold_quarantine < self.vpin_threshold_warn:
            raise ValueError("vpin_threshold_quarantine must be >= vpin_threshold_warn")


class Phase58FlowToxicityMitigator:
    """Flow toxicity mitigation for crypto options + orderflow."""

    def __init__(self, cfg: Phase58FlowToxicityMitigatorConfig | None = None) -> None:
        self.cfg = cfg or Phase58FlowToxicityMitigatorConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase58FlowToxicityMitigator: paper_only must remain True")
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.flow52 = Phase52ToxicityResilientFlowOptimizer()
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.toxicity_scores: List[Dict[str, Any]] = []
        self.adverse_sel: List[Dict[str, Any]] = []
        self.size_caps: List[Dict[str, Any]] = []
        self.quarantine_log: List[Dict[str, Any]] = []
        self._cycle = 0

    def _compute_vpin(self) -> float:
        rep = self.of.run_campaign(cycles=20)
        tox = _finite(rep.get("avg_toxicity", 0.19))
        imb = abs(_finite(rep.get("avg_imbalance", 0.11)))
        vpin = tox * (1.0 + imb * 0.35)
        return max(0.0, min(1.0, vpin))

    def mitigate(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.toxicity_scores = []
        self.adverse_sel = []
        self.size_caps = []
        self.quarantine_log = []
        vpin = self._compute_vpin()
        flow_rep = self.flow52.optimize_flow(cycles=20)
        ksum = self.ks.run_campaign()
        halted = bool(ksum.get("halted", False))
        consecutive_quarantine = 0

        for i in range(cycles):
            vpin_i = max(0.0, min(1.0, vpin + ((i * 131542391) % 1000) * 1e-5))
            as_est = vpin_i * (1.12 + 0.08 * (vpin_i > self.cfg.vpin_threshold_warn))
            as_est = max(0.0, min(1.0, _finite(as_est)))
            self.toxicity_scores.append(serialize_metrics_strict({
                "score_id": _make_id(self.cfg.seed, "vpin", i),
                "cycle": i,
                "vpin": float(vpin_i),
                "venue": self.cfg.venues[i % len(self.cfg.venues)],
                "underlying": self.cfg.underlyings[i % len(self.cfg.underlyings)],
                "paper_only": True,
                "timestamp": _utc_now(),
            }))
            self.adverse_sel.append(serialize_metrics_strict({
                "as_id": _make_id(self.cfg.seed, "as", i),
                "cycle": i,
                "adverse_selection": float(as_est),
                "breach_as": bool(as_est >= self.cfg.adverse_sel_threshold),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))
            if vpin_i >= self.cfg.vpin_threshold_quarantine or halted or consecutive_quarantine >= self.cfg.max_consecutive_quarantine:
                size_mult = self.cfg.size_cap_quarantine_mult
                action = "quarantine"
                consecutive_quarantine += 1
            elif vpin_i >= self.cfg.vpin_threshold_warn or as_est >= self.cfg.adverse_sel_threshold:
                size_mult = self.cfg.size_cap_warn_mult
                action = "tighten"
                consecutive_quarantine = max(0, consecutive_quarantine - 1)
            else:
                size_mult = 1.0
                action = "allow"
                consecutive_quarantine = max(0, consecutive_quarantine - 1)
            size_mult = max(0.1, min(1.0, _finite(size_mult)))
            self.size_caps.append(serialize_metrics_strict({
                "cap_id": _make_id(self.cfg.seed, "cap", i),
                "cycle": i,
                "action": action,
                "size_cap_mult": float(size_mult),
                "consecutive_quarantine": int(consecutive_quarantine),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))
            if action == "quarantine":
                self.quarantine_log.append(serialize_metrics_strict({
                    "q_id": _make_id(self.cfg.seed, "q", i),
                    "cycle": i,
                    "venue": self.cfg.venues[i % len(self.cfg.venues)],
                    "reason": "vpin_quarantine_or_halt_or_consec",
                    "cooldown_cycles": int(self.cfg.quarantine_cooldown_cycles),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))

        gates_ok = bool(not halted) and all(c["size_cap_mult"] >= 0.1 for c in self.size_caps)
        rep = serialize_metrics_strict({
            "phase": "PHASE58_FLOW_TOXICITY_MITIGATOR",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "avg_vpin": float(sum(s["vpin"] for s in self.toxicity_scores) / max(1, len(self.toxicity_scores))),
            "avg_adverse_selection": float(sum(a["adverse_selection"] for a in self.adverse_sel) / max(1, len(self.adverse_sel))),
            "n_quarantined": len(self.quarantine_log),
            "flow52_integration_ok": bool(flow_rep.get("gates_ok", False)),
            "kill_switch_halted": bool(halted),
        })
        _assert_finite(rep, "phase58_tox_mitigator_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.mitigate(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE58_FLOW_TOXICITY_MITIGATOR_{ts}.json"
        mpath = out / f"PHASE58_FLOW_TOXICITY_MITIGATOR_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(f"# PHASE58 Flow Toxicity Mitigator\n\n- Timestamp: {rep['timestamp']}\n- Gates OK: {rep['gates_ok']}\n- Avg VPIN: {rep['avg_vpin']}\n- Avg Adverse Selection: {rep['avg_adverse_selection']}\n- Quarantined: {rep['n_quarantined']}\n")
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
