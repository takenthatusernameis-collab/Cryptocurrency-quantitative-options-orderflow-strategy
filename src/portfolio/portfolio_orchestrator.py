"""Multi-strategy coordination, position aggregation, netting, exposure limits.

Phase 14.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _det_ts(seed: int) -> str:
    base = datetime(2026, 11, 1, tzinfo=timezone.utc)
    from datetime import timedelta
    return (base + timedelta(seconds=int(seed))).isoformat().replace("+00:00", "Z")


@dataclass
class OrchestrationConfig:
    max_gross_exposure: float = 2_000_000.0
    max_net_exposure: float = 1_000_000.0
    max_position_size: float = 100_000.0
    netting_enabled: bool = True
    diversification_min_strategies: int = 2
    paper_only: bool = True


def default_orchestration_config() -> OrchestrationConfig:
    return OrchestrationConfig()


@dataclass
class PortfolioPosition:
    position_id: str
    strategy: str
    venue: str
    symbol: str
    side: str  # long/short/flat
    quantity: float
    notional: float
    netted: bool
    timestamp: str


class PortfolioOrchestrator:
    def __init__(self, config: Optional[OrchestrationConfig] = None, seed: int = 42):
        self.config = config or default_orchestration_config()
        self.seed = int(seed)
        self.config.paper_only = True  # enforce
        self._counter = 0

    def _pid(self) -> str:
        self._counter += 1
        h = hashlib.sha256(f"{self.seed}|pos|{self._counter}".encode()).hexdigest()[:12]
        return f"pos_{h}"

    def aggregate_positions(
        self,
        strategy_positions: Dict[str, List[Dict[str, Any]]],
        spot: Dict[str, float],
    ) -> List[PortfolioPosition]:
        positions: List[PortfolioPosition] = []
        idx = 0
        for strat, plist in strategy_positions.items():
            for p in plist:
                sym = str(p.get("symbol", "BTC")).upper()
                side = str(p.get("side", "long")).lower()
                qty = float(p.get("quantity", 0.0))
                if not math.isfinite(qty) or qty < 0:
                    qty = 0.0
                s = float(spot.get(sym, 65000.0))
                notional = qty * s * (1.0 if side != "short" else -1.0)
                idx += 1
                positions.append(
                    PortfolioPosition(
                        position_id=self._pid(),
                        strategy=str(strat),
                        venue=str(p.get("venue", "deribit")).lower(),
                        symbol=sym,
                        side=side,
                        quantity=float(qty),
                        notional=float(notional),
                        netted=bool(self.config.netting_enabled),
                        timestamp=_det_ts(self.seed + idx),
                    )
                )
        return positions

    def net_positions(self, positions: List[PortfolioPosition]) -> Dict[str, Any]:
        net_by_sym: Dict[str, float] = {}
        for pos in positions:
            net_by_sym[pos.symbol] = net_by_sym.get(pos.symbol, 0.0) + float(pos.notional)
        net_rep = {
            "timestamp": _det_ts(self.seed),
            "netting_enabled": bool(self.config.netting_enabled),
            "net_by_symbol": {k: float(v) for k, v in net_by_sym.items()},
            "gross_exposure": float(sum(abs(v) for v in net_by_sym.values())),
            "net_exposure": float(sum(net_by_sym.values())),
        }
        return serialize_metrics_strict(net_rep)

    def check_exposure_limits(self, positions: List[PortfolioPosition], spot: Dict[str, float]) -> Dict[str, Any]:
        gross = 0.0
        net = 0.0
        violations: List[str] = []
        for pos in positions:
            s = float(spot.get(pos.symbol, 65000.0))
            npos = abs(pos.quantity * s)
            gross += npos
            if pos.side == "short":
                net -= pos.quantity * s
            elif pos.side == "long":
                net += pos.quantity * s
            if npos > self.config.max_position_size + 1e-12:
                violations.append(f"max_position_exceeded:{pos.position_id}")
        if gross > self.config.max_gross_exposure + 1e-12:
            violations.append("max_gross_exposure_exceeded")
        if abs(net) > self.config.max_net_exposure + 1e-12:
            violations.append("max_net_exposure_exceeded")
        rep = {
            "timestamp": _det_ts(self.seed),
            "gross_exposure": float(gross),
            "net_exposure": float(net),
            "violations": violations,
            "within_limits": len(violations) == 0,
            "paper_only": True,
        }
        return serialize_metrics_strict(rep)

    def generate_report(self, positions: List[PortfolioPosition], spot: Dict[str, float]) -> Dict[str, Any]:
        net_rep = self.net_positions(positions)
        lim_rep = self.check_exposure_limits(positions, spot)
        rep = {
            "report": "PORTFOLIO_ORCHESTRATION_REPORT",
            "timestamp": _det_ts(self.seed),
            "seed": self.seed,
            "config": asdict(self.config),
            "positions": [asdict(p) for p in positions],
            "netting": net_rep,
            "limits": lim_rep,
            "counts": {"positions": len(positions)},
            "paper_only": True,
        }
        return serialize_metrics_strict(rep)
