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
    h = hashlib.sha256(f"{seed}|p22slip|{idx}".encode()).hexdigest()[:12]
    return f"2026-11-01T14:{h[:2]}:{h[2:4]}Z"


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p22_{tag}_{h}"


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
class SlippageConfig:
    seed: int = 42
    paper_only: bool = True
    temporary_impact_coeff: float = 0.1
    permanent_impact_coeff: float = 0.02
    spread_half_bps: float = 1.0
    depth_scale_usd: float = 1000000.0
    vol_adjustment: float = 0.5
    max_slippage_bps: float = 50.0
    enforce_hard_limits: bool = True


@dataclass(frozen=True)
class SlippageInput:
    input_id: str
    symbol: str
    venue: str
    side: str
    notional_usd: float
    qty: float
    mid_price: float
    spread_bps: float
    depth_usd: float
    volatility: float
    paper_only: bool
    timestamp: str


@dataclass(frozen=True)
class SlippageResult:
    result_id: str
    input_id: str
    symbol: str
    venue: str
    temporary_impact_bps: float
    permanent_impact_bps: float
    spread_cost_bps: float
    total_slippage_bps: float
    slippage_cost_usd: float
    expected_fill_price: float
    within_limit: bool
    paper_only: bool
    timestamp: str


class SlippageModel:
    def __init__(self, config: Optional[SlippageConfig] = None, seed: int = 42):
        self.config = config or SlippageConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("SlippageModel: paper_only must remain True")
        self.config = SlippageConfig(
            seed=int(self.config.seed),
            paper_only=True,
            temporary_impact_coeff=float(self.config.temporary_impact_coeff),
            permanent_impact_coeff=float(self.config.permanent_impact_coeff),
            spread_half_bps=float(self.config.spread_half_bps),
            depth_scale_usd=float(self.config.depth_scale_usd),
            vol_adjustment=float(self.config.vol_adjustment),
            max_slippage_bps=float(self.config.max_slippage_bps),
            enforce_hard_limits=bool(self.config.enforce_hard_limits),
        )
        self.seed = int(self.config.seed)
        self.audit: List[Dict[str, Any]] = []

    def _iid(self, idx: int) -> str:
        return _make_id(self.seed, "in", idx)

    def _rid(self, idx: int) -> str:
        return _make_id(self.seed, "slip", idx)

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def make_input(self, symbol: str, venue: str, side: str, notional_usd: float, qty: float, mid_price: float, spread_bps: float, depth_usd: float, volatility: float, idx: int = 0) -> SlippageInput:
        import random

        rng = random.Random(self.seed + 9000 + idx)
        symbol = str(symbol).upper()
        venue = str(venue).lower()
        side = str(side).lower()
        if mid_price <= 0:
            mid_price = rng.uniform(80000.0, 120000.0) if symbol == "BTC" else rng.uniform(2000.0, 4000.0)
        return SlippageInput(
            input_id=self._iid(idx),
            symbol=symbol,
            venue=venue,
            side=side,
            notional_usd=float(notional_usd),
            qty=float(qty),
            mid_price=float(mid_price),
            spread_bps=float(spread_bps),
            depth_usd=float(depth_usd),
            volatility=float(volatility),
            paper_only=True,
            timestamp=_det_ts(self.seed, idx),
        )

    def estimate(self, inp: SlippageInput, idx: int = 0) -> SlippageResult:
        self._log("estimate", {"input_id": inp.input_id, "symbol": inp.symbol})
        part = inp.notional_usd / max(inp.depth_usd, 1.0)
        temp_impact = self.config.temporary_impact_coeff * math.sqrt(max(part, 0.0)) * 100.0
        perm_impact = self.config.permanent_impact_coeff * part * 100.0
        spread_cost = self.config.spread_half_bps + inp.spread_bps / 2.0
        vol_adj = 1.0 + self.config.vol_adjustment * inp.volatility
        total = (temp_impact + perm_impact + spread_cost) * vol_adj
        total = float(max(0.0, min(self.config.max_slippage_bps, total)))
        cost_usd = inp.notional_usd * total / 10000.0
        side_mult = 1.0 + total / 20000.0 if inp.side == "buy" else 1.0 - total / 20000.0
        fill_price = inp.mid_price * side_mult
        within = total <= self.config.max_slippage_bps
        if self.config.enforce_hard_limits and total > self.config.max_slippage_bps:
            within = False
        rep = {
            "result_id": self._rid(idx),
            "input_id": inp.input_id,
            "symbol": inp.symbol,
            "venue": inp.venue,
            "temporary_impact_bps": float(temp_impact),
            "permanent_impact_bps": float(perm_impact),
            "spread_cost_bps": float(spread_cost),
            "total_slippage_bps": float(total),
            "slippage_cost_usd": float(cost_usd),
            "expected_fill_price": float(fill_price),
            "within_limit": bool(within),
            "paper_only": True,
            "timestamp": _det_ts(self.seed, idx),
        }
        _assert_no_nan_inf(rep, "p22_slippage_result")
        return SlippageResult(
            result_id=rep["result_id"],
            input_id=rep["input_id"],
            symbol=rep["symbol"],
            venue=rep["venue"],
            temporary_impact_bps=rep["temporary_impact_bps"],
            permanent_impact_bps=rep["permanent_impact_bps"],
            spread_cost_bps=rep["spread_cost_bps"],
            total_slippage_bps=rep["total_slippage_bps"],
            slippage_cost_usd=rep["slippage_cost_usd"],
            expected_fill_price=rep["expected_fill_price"],
            within_limit=rep["within_limit"],
            paper_only=True,
            timestamp=rep["timestamp"],
        )

    def generate_report(self, inputs: List[SlippageInput], results: List[SlippageResult]) -> Dict[str, Any]:
        avg_slip = float(sum(r.total_slippage_bps for r in results) / len(results)) if results else 0.0
        avg_cost = float(sum(r.slippage_cost_usd for r in results) / len(results)) if results else 0.0
        within = sum(1 for r in results if r.within_limit)
        rep = {
            "report": "PHASE22_SLIPPAGE_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "input_count": len(inputs),
            "result_count": len(results),
            "inputs": [asdict(i) for i in inputs],
            "results": [asdict(r) for r in results],
            "summary": {
                "avg_total_slippage_bps": float(avg_slip),
                "avg_slippage_cost_usd": float(avg_cost),
                "within_limit_count": int(within),
                "within_limit_rate": float(within / len(results)) if results else 0.0,
                "paper_only": True,
            },
            "audit": self.audit,
            "git_sha": _git_sha(),
            "paper_only": True,
        }
        _assert_no_nan_inf(rep, "p22_slippage_report")
        return rep
