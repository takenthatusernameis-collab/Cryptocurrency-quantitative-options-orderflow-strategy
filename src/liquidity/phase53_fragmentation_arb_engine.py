"""
Phase 53: Multi-venue options fragmentation arbitrage (crypto options + orderflow).

Fragmentation arbitrage with basis detection, fragmentation scoring,
toxicity gating. PAPER-ONLY, deterministic, finite numerics.
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
from src.risk.phase39_kill_switches_circuit_breakers import (
    KillSwitchConfig39,
    Phase39KillSwitchesCircuitBreakers,
)
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p53frag|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p53frag_{tag}_{h}"


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
class Phase53FragmentationConfig:
    seed: int = 53053
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 60
    basis_threshold_bps: float = 4.5
    frag_threshold: float = 0.32
    tox_gate: float = 0.38
    min_liq_score: float = 0.45
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase53FragmentationArbEngine: paper_only must remain True (live path hard-gated)")
        if not (0.0 <= self.basis_threshold_bps <= 100.0):
            raise ValueError("basis_threshold_bps must be in [0,100]")
        if not (0.0 <= self.frag_threshold <= 1.0):
            raise ValueError("frag_threshold must be in [0,1]")
        if not (0.0 <= self.tox_gate <= 1.0):
            raise ValueError("tox_gate must be in [0,1]")


class Phase53FragmentationArbEngine:
    """Multi-venue options fragmentation arbitrage engine."""

    def __init__(self, cfg: Phase53FragmentationConfig | None = None) -> None:
        self.cfg = cfg or Phase53FragmentationConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase53FragmentationArbEngine: paper_only must remain True")
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.bases: List[Dict[str, Any]] = []
        self.opps: List[Dict[str, Any]] = []
        self._cycle = 0

    def _frag_score(self, idx: int) -> float:
        rep = self.of.run_campaign(cycles=10)
        tox = _finite(rep.get("avg_toxicity", 0.21))
        imb = abs(_finite(rep.get("avg_imbalance", 0.12)))
        score = max(0.0, min(1.0, tox * 0.7 + imb * 0.5 + (idx % 7) * 1e-3))
        return score

    def run_campaign(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.bases = []
        self.opps = []
        ksum = self.ks.run_campaign()
        halted = bool(ksum.get("halted", False))

        for i in range(cycles):
            frag = self._frag_score(i)
            base_bps = _finite((frag * 6.5 + (i % 5) * 0.4))
            self.bases.append(serialize_metrics_strict({
                "basis_id": _make_id(self.cfg.seed, "basis", i),
                "cycle": i,
                "underlying": self.cfg.underlyings[i % len(self.cfg.underlyings)],
                "venues": list(self.cfg.venues[:3]),
                "basis_bps": float(base_bps),
                "fragmentation_score": float(frag),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))
            eligible = (base_bps >= self.cfg.basis_threshold_bps) and (frag >= self.cfg.frag_threshold) and (frag <= self.cfg.tox_gate)
            if eligible and not halted:
                opp = serialize_metrics_strict({
                    "opp_id": _make_id(self.cfg.seed, "opp", i),
                    "cycle": i,
                    "type": "cross_venue_options_fragmentation_arb",
                    "basis_bps": float(base_bps),
                    "fragmentation_score": float(frag),
                    "liquidity_score": float(max(self.cfg.min_liq_score, 0.7 - frag * 0.2)),
                    "toxicity_gated": True,
                    "route_venues": list(self.cfg.venues[:2]),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                })
                self.opps.append(opp)

        gates_ok = bool((not halted) and (all(b["basis_bps"] >= 0 for b in self.bases)))
        rep = serialize_metrics_strict({
            "phase": "PHASE53_FRAGMENTATION_ARB_ENGINE",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": gates_ok,
            "n_bases": len(self.bases),
            "n_opps": len(self.opps),
            "avg_basis_bps": float(sum(b["basis_bps"] for b in self.bases) / max(1, len(self.bases))),
            "avg_fragmentation_score": float(sum(b["fragmentation_score"] for b in self.bases) / max(1, len(self.bases))),
            "halted_by_kill_switch": bool(halted),
        })
        _assert_finite(rep, "phase53_frag_report")
        return rep

    def generate_artifacts(self, outdir: str) -> Dict[str, Any]:
        rep = self.run_campaign(self.cfg.cycles)
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE53_FRAGMENTATION_ARB_ENGINE_{ts}.json"
        mpath = out / f"PHASE53_FRAGMENTATION_ARB_ENGINE_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump({"report": rep, "opportunities": self.opps[:50]}, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(f"# PHASE53 Fragmentation Arb Engine\n\n- Timestamp: {rep['timestamp']}\n- Gates OK: {rep['gates_ok']}\n- Opportunities: {rep['n_opps']}\n- Avg Basis (bps): {rep['avg_basis_bps']:.4f}\n")
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
