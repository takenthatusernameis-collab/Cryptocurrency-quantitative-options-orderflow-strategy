"""
Phase 30: Dynamic Capital Allocator for vol surface arbitrage.
Regime-aware allocation across strategies/venues/underlyings, Kelly/fractional sizing caps,
drawdown-based scaling. Production-grade, deterministic, paper-only.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib
import json
import math
from pathlib import Path

from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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
            if not math.isfinite(v):
                bad.append(p)

    walk(obj, "$")
    if bad:
        raise ValueError(f"Non-finite in {label}: {bad[:10]}")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p30cap|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p30cap_{tag}_{h}"


@dataclass(frozen=True)
class DynamicCapitalAllocatorConfig:
    seed: int = 42
    paper_only: bool = True
    total_capital_usd: float = 1000000.0
    max_allocation_pct: float = 0.25
    kelly_fraction: float = 0.25
    drawdown_scale_floor: float = 0.3
    regime_multipliers: tuple = (1.0, 0.8, 0.6)  # normal/stress/crisis
    enforce_gates: bool = True


@dataclass(frozen=True)
class CapitalAllocation:
    alloc_id: str
    underlying: str
    strategy: str
    venue: str
    weight: float
    allocated_usd: float
    kelly_sized_usd: float
    regime: str
    drawdown_scale: float
    paper_only: bool
    timestamp: str


class DynamicCapitalAllocator:
    def __init__(self, config: Optional[DynamicCapitalAllocatorConfig] = None, seed: int = 42):
        self.config = config or DynamicCapitalAllocatorConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("DynamicCapitalAllocator: paper_only must remain True (live path hard-gated)")
        self.config = DynamicCapitalAllocatorConfig(
            seed=int(self.config.seed),
            paper_only=True,
            total_capital_usd=float(self.config.total_capital_usd),
            max_allocation_pct=float(self.config.max_allocation_pct),
            kelly_fraction=float(self.config.kelly_fraction),
            drawdown_scale_floor=float(self.config.drawdown_scale_floor),
            regime_multipliers=tuple(self.config.regime_multipliers),
            enforce_gates=bool(self.config.enforce_gates),
        )
        self.seed = int(self.config.seed)
        self._counter = 0
        self.allocations: List[CapitalAllocation] = []

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def allocate(self, opportunities: List[Dict[str, Any]], regime: str = "normal", drawdown_pct: float = 0.0) -> List[CapitalAllocation]:
        self.allocations = []
        # regime scale
        if regime == "crisis":
            rscale = self.config.regime_multipliers[2]
        elif regime == "stress":
            rscale = self.config.regime_multipliers[1]
        else:
            rscale = self.config.regime_multipliers[0]
        # drawdown scaling
        dscale = max(self.config.drawdown_scale_floor, 1.0 - 2.0 * drawdown_pct)
        total_scale = rscale * dscale
        max_alloc_usd = self.config.total_capital_usd * self.config.max_allocation_pct
        for i, opp in enumerate(opportunities):
            und = str(opp.get("underlying", "BTC")).upper()
            strat = str(opp.get("strategy", "vol_arb"))
            venue = str(opp.get("venue", "deribit"))
            edge = float(opp.get("edge_bps", 10.0))
            win_rate = float(opp.get("win_rate", 0.55))
            # Kelly-ish
            kelly = max(0.0, (win_rate * (edge / 10000.0) - (1 - win_rate)) / max(1e-12, edge / 10000.0))
            kelly_sized = self.config.total_capital_usd * kelly * self.config.kelly_fraction * total_scale
            kelly_sized = min(kelly_sized, max_alloc_usd)
            weight = kelly_sized / max(1e-12, self.config.total_capital_usd)
            alloc = CapitalAllocation(
                alloc_id=self._next_id("alloc"),
                underlying=und,
                strategy=strat,
                venue=venue,
                weight=float(weight),
                allocated_usd=float(kelly_sized),
                kelly_sized_usd=float(kelly_sized),
                regime=regime,
                drawdown_scale=float(dscale),
                paper_only=True,
                timestamp=_utc_now(),
            )
            _assert_finite(asdict(alloc), "capital_allocation")
            self.allocations.append(alloc)
        return self.allocations

    def generate_report(self, outdir: str = "research_state") -> Dict[str, Any]:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        total_alloc = sum(a.allocated_usd for a in self.allocations)
        report = {
            "status": "ok",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "total_capital_usd": self.config.total_capital_usd,
            "total_allocated_usd": float(total_alloc),
            "utilization_pct": float(total_alloc / max(1e-12, self.config.total_capital_usd) * 100.0),
            "allocations": [asdict(a) for a in self.allocations],
        }
        _assert_finite(report, "phase30_dynamic_capital_allocator_report")
        rep_json = Path(outdir) / "PHASE30_DYNAMIC_CAPITAL_ALLOCATOR_REPORT.json"
        rep_md = Path(outdir) / "PHASE30_DYNAMIC_CAPITAL_ALLOCATOR_REPORT.md"
        rep_json.write_text(json.dumps(serialize_metrics_strict(report), indent=2))
        rep_md.write_text(
            f"# PHASE30_DYNAMIC_CAPITAL_ALLOCATOR_REPORT\n\n"
            f"Timestamp: {report['timestamp']}\nStatus: ok\nPaper-only: true\n"
            f"Total Capital: ${self.config.total_capital_usd:,.0f}\nAllocated: ${total_alloc:,.0f} ({report['utilization_pct']:.2f}%)\n"
        )
        return {"status": "ok", "json": str(rep_json), "md": str(rep_md), "paper_only": True}
