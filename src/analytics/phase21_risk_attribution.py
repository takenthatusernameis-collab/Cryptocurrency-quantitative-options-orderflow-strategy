#!/usr/bin/env python3
import hashlib
import math
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _git_sha() -> str | None:
    sha = os.environ.get("GIT_SHA")
    if sha:
        return str(sha)
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd="/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.decode().strip()
    except Exception:
        pass
    return None


def _det_ts(seed: int, idx: int = 0) -> str:
    h = hashlib.sha256(f"{seed}|p21attr|{idx}".encode()).hexdigest()[:12]
    return f"2026-11-01T14:{h[:2]}:{h[2:4]}Z"


def _assert_no_nan_inf(obj: Any, label: str) -> None:
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
        raise ValueError(f"Non-finite values detected in {label}: {bad[:10]}")


@dataclass(frozen=True)
class AttributionConfig:
    seed: int = 42
    paper_only: bool = True


@dataclass(frozen=True)
class AttributionLine:
    line_id: str
    strategy: str
    venue: str
    symbol: str
    delta_contribution: float
    gamma_contribution: float
    vega_contribution: float
    theta_contribution: float
    notional_usd: float
    pnl_attrib_usd: float
    paper_only: bool
    timestamp: str


class Phase21RiskAttribution:
    def __init__(self, config: Optional[AttributionConfig] = None, seed: int = 42):
        self.config = config or AttributionConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("Phase21RiskAttribution: paper_only must remain True")
        self.config = AttributionConfig(seed=int(self.config.seed), paper_only=True)
        self.seed = int(self.config.seed)
        self._counter = 0
        self.audit: List[Dict[str, Any]] = []

    def _lid(self) -> str:
        self._counter += 1
        h = hashlib.sha256(f"{self.seed}|p21attrline|{self._counter}".encode()).hexdigest()[:12]
        return f"p21_attr_{h}"

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def attribute(self, snapshots: List[Any]) -> List[AttributionLine]:
        self._log("attribute", {"count": len(snapshots)})
        lines: List[AttributionLine] = []
        for i, s in enumerate(snapshots):
            # snapshots may be dict or object
            if hasattr(s, "__dict__"):
                d = asdict(s) if hasattr(s, "__dataclass_fields__") else vars(s)
            elif isinstance(s, dict):
                d = s
            else:
                continue
            strat = d.get("strategy", "unknown")
            venue = d.get("venue", "unknown")
            sym = d.get("symbol", "BTC")
            notional = float(d.get("notional_usd", 0.0))
            delta = float(d.get("delta", 0.0))
            gamma = float(d.get("gamma", 0.0))
            vega = float(d.get("vega", 0.0))
            theta = float(d.get("theta", 0.0))
            delta_c = delta * notional * 1e-5
            gamma_c = gamma * (notional ** 2) * 1e-12
            vega_c = vega * 0.01
            theta_c = theta * 0.1
            pnl_attrib = delta_c + gamma_c + vega_c + theta_c
            if not all(math.isfinite(x) for x in [delta_c, gamma_c, vega_c, theta_c, pnl_attrib]):
                delta_c = gamma_c = vega_c = theta_c = pnl_attrib = 0.0
            lines.append(
                AttributionLine(
                    line_id=self._lid(),
                    strategy=str(strat),
                    venue=str(venue),
                    symbol=str(sym),
                    delta_contribution=float(delta_c),
                    gamma_contribution=float(gamma_c),
                    vega_contribution=float(vega_c),
                    theta_contribution=float(theta_c),
                    notional_usd=float(notional),
                    pnl_attrib_usd=float(pnl_attrib),
                    paper_only=True,
                    timestamp=_det_ts(self.seed, i),
                )
            )
        _assert_no_nan_inf([asdict(l) for l in lines], "p21_attr_lines")
        return lines

    def generate_report(self, snapshots: List[Any], lines: Optional[List[AttributionLine]] = None) -> Dict[str, Any]:
        if lines is None:
            lines = self.attribute(snapshots)
        by_strategy: Dict[str, float] = {}
        by_venue: Dict[str, float] = {}
        by_symbol: Dict[str, float] = {}
        for l in lines:
            by_strategy[l.strategy] = by_strategy.get(l.strategy, 0.0) + l.pnl_attrib_usd
            by_venue[l.venue] = by_venue.get(l.venue, 0.0) + l.pnl_attrib_usd
            by_symbol[l.symbol] = by_symbol.get(l.symbol, 0.0) + l.pnl_attrib_usd
        rep = {
            "report": "PHASE21_RISK_ATTRIBUTION_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "line_count": len(lines),
            "lines": [asdict(l) for l in lines],
            "by_strategy": {k: float(v) for k, v in by_strategy.items()},
            "by_venue": {k: float(v) for k, v in by_venue.items()},
            "by_symbol": {k: float(v) for k, v in by_symbol.items()},
            "total_pnl_attrib_usd": float(sum(l.pnl_attrib_usd for l in lines)),
            "audit": self.audit,
            "git_sha": _git_sha(),
            "paper_only": True,
        }
        _assert_no_nan_inf(rep, "p21_attr_report")
        return rep
