"""
Phase 52: Real-Time Liquidity Allocator (crypto options + orderflow).

Real-time liquidity allocation across venues/tenors/strikes for options+perps:
fragmentation-aware allocation, queue/latency/liquidity scoring, hedgable
inventory caps, toxicity-adjusted capacity, order slicing/allocation, TCA.
PAPER-ONLY, deterministic.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.execution.phase32_execution_quality import ExecutionQualityEngine, ExecutionQualityConfig32
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
    h = hashlib.sha256(f"{seed}|p52alloc|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p52alloc_{tag}_{h}"


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
class Phase52AllocatorConfig:
    seed: int = 52053
    paper_only: bool = True
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    underlyings: tuple = ("BTC", "ETH", "SOL")
    tenors: tuple = ("1D", "7D", "30D", "90D")
    strikes: tuple = ("ATM", "25D", "10D")
    cycles: int = 60
    frag_penalty_max: float = 0.25
    latency_penalty_bps: float = 1.5
    queue_penalty_bps: float = 1.0
    tox_adj_cap_factor: float = 0.7
    max_alloc_usd: float = 500000.0
    hedgable_inv_cap_usd: float = 1500000.0
    slice_count_min: int = 2
    slice_count_max: int = 6
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase52RealtimeLiquidityAllocator: paper_only must remain True (live path hard-gated)")
        if self.max_alloc_usd < 0:
            raise ValueError("max_alloc_usd must be >= 0")
        if self.slice_count_min < 1 or self.slice_count_max < self.slice_count_min:
            raise ValueError("invalid slice counts")


class Phase52RealtimeLiquidityAllocator:
    """Fragmentation-aware liquidity allocator for crypto options + orderflow."""

    def __init__(self, cfg: Phase52AllocatorConfig | None = None) -> None:
        self.cfg = cfg or Phase52AllocatorConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase52RealtimeLiquidityAllocator: paper_only must remain True")
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.eq = ExecutionQualityEngine(ExecutionQualityConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles))
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.allocations: List[Dict[str, Any]] = []
        self.slices: List[Dict[str, Any]] = []
        self.tca: List[Dict[str, Any]] = []
        self._cycle = 0

    def allocate(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.allocations = []
        self.slices = []
        self.tca = []
        of_rep = self.of.run_campaign(cycles=15)
        tox = max(0.0, min(1.0, _finite(of_rep.get("avg_toxicity", 0.19))))
        imb = _finite(of_rep.get("avg_imbalance", 0.11))
        ksum = self.ks.run_campaign()
        halted = bool(ksum.get("halted", False))

        for i in range(cycles):
            # fragmentation scoring per venue
            frag_scores = []
            for j, v in enumerate(self.cfg.venues):
                lat_pen = self.cfg.latency_penalty_bps * ((j + 1) / len(self.cfg.venues))
                q_pen = self.cfg.queue_penalty_bps * ((i % 4 + 1) / 4.0)
                frag = (lat_pen + q_pen) / 10000.0
                frag = max(0.0, min(self.cfg.frag_penalty_max, _finite(frag)))
                frag_scores.append((v, frag))
            # normalize weights (higher frag -> lower weight)
            weights = []
            for v, f in frag_scores:
                w = max(1e-6, 1.0 - f)
                # toxicity adjustment
                w = w * (1.0 - tox * (1.0 - self.cfg.tox_adj_cap_factor))
                weights.append(w)
            s = sum(weights) or 1.0
            norm = [w / s for w in weights]
            alloc_usd = self.cfg.max_alloc_usd * (1.0 - 0.2 * tox)
            alloc_usd = min(self.cfg.max_alloc_usd, max(0.0, _finite(alloc_usd)))
            for j, (v, _) in enumerate(frag_scores):
                a_usd = alloc_usd * norm[j]
                if a_usd > self.cfg.hedgable_inv_cap_usd * 0.001:  # hedgable cap context
                    a_usd = min(a_usd, self.cfg.hedgable_inv_cap_usd * 0.0008)
                self.allocations.append(serialize_metrics_strict({
                    "alloc_id": _make_id(self.cfg.seed, "alloc", i * 10 + j),
                    "cycle": i,
                    "venue": v,
                    "underlying": self.cfg.underlyings[j % len(self.cfg.underlyings)],
                    "tenor": self.cfg.tenors[j % len(self.cfg.tenors)],
                    "strike": self.cfg.strikes[j % len(self.cfg.strikes)],
                    "alloc_usd": float(_finite(a_usd)),
                    "frag_penalty": float(_finite(frag_scores[j][1])),
                    "tox_adj_factor": float(_finite(1.0 - tox * (1.0 - self.cfg.tox_adj_cap_factor))),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
                # slicing
                nsl = self.cfg.slice_count_min + (i % (self.cfg.slice_count_max - self.cfg.slice_count_min + 1))
                per_slice = a_usd / max(1, nsl)
                for si in range(nsl):
                    self.slices.append(serialize_metrics_strict({
                        "slice_id": _make_id(self.cfg.seed, "slice", i * 100 + j * 10 + si),
                        "alloc_id": _make_id(self.cfg.seed, "alloc", i * 10 + j),
                        "cycle": i,
                        "venue": v,
                        "slice_usd": float(_finite(per_slice)),
                        "slice_idx": si,
                        "n_slices": nsl,
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }))
            # TCA
            est_slip_bps = (tox * 8.0 + abs(imb) * 3.0) * (1.0 if not halted else 1.4)
            self.tca.append(serialize_metrics_strict({
                "tca_id": _make_id(self.cfg.seed, "tca", i),
                "cycle": i,
                "est_slippage_bps": float(_finite(est_slip_bps)),
                "toxicity": float(_finite(tox)),
                "imbalance": float(_finite(imb)),
                "n_allocs": len(self.cfg.venues),
                "n_slices": len(self.cfg.venues) * (self.cfg.slice_count_min + (i % 4)),
                "halted": bool(halted),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))

        gates_ok = bool(not halted) and all(a["alloc_usd"] >= 0 and a["alloc_usd"] <= self.cfg.max_alloc_usd for a in self.allocations)
        rep = serialize_metrics_strict({
            "phase": "PHASE52_REALTIME_LIQUIDITY_ALLOCATOR",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "avg_toxicity": float(_finite(tox)),
            "n_allocations": len(self.allocations),
            "n_slices": len(self.slices),
            "n_tca": len(self.tca),
            "total_alloc_usd": float(_finite(sum(a["alloc_usd"] for a in self.allocations))),
            "halted_by_kill_switch": bool(halted),
        })
        _assert_finite(rep, "phase52_alloc_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.allocate(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE52_LIQUIDITY_ALLOCATOR_{ts}.json"
        mpath = out / f"PHASE52_LIQUIDITY_ALLOCATOR_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(f"# PHASE52 Liquidity Allocator\n\n- Timestamp: {rep['timestamp']}\n- Gates OK: {rep['gates_ok']}\n- Avg Toxicity: {rep['avg_toxicity']}\n- Allocations: {rep['n_allocations']}\n- Slices: {rep['n_slices']}\n- Total Alloc USD: {rep['total_alloc_usd']}\n")
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
