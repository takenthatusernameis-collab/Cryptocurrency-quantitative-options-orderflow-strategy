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
    h = hashlib.sha256(f"{seed}|p22slice|{idx}".encode()).hexdigest()[:12]
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
class SlicerConfig:
    seed: int = 42
    paper_only: bool = True
    max_slice_notional_usd: float = 200000.0
    min_slices: int = 1
    max_slices: int = 20
    default_schedule: str = "twap"
    participation_rate: float = 0.1
    enforce_hard_limits: bool = True


@dataclass(frozen=True)
class Slice:
    slice_id: str
    slice_index: int
    notional_usd: float
    qty: float
    scheduled_offset_ms: float
    venue: str
    symbol: str
    side: str
    paper_only: bool
    timestamp: str


@dataclass(frozen=True)
class SlicingPlan:
    plan_id: str
    symbol: str
    side: str
    total_notional_usd: float
    total_qty: float
    schedule: str
    slice_count: int
    slices: List[Slice]
    venue: str
    paper_only: bool
    timestamp: str


class OrderSlicer:
    def __init__(self, config: Optional[SlicerConfig] = None, seed: int = 42):
        self.config = config or SlicerConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("OrderSlicer: paper_only must remain True")
        self.config = SlicerConfig(
            seed=int(self.config.seed),
            paper_only=True,
            max_slice_notional_usd=float(self.config.max_slice_notional_usd),
            min_slices=int(self.config.min_slices),
            max_slices=int(self.config.max_slices),
            default_schedule=str(self.config.default_schedule),
            participation_rate=float(self.config.participation_rate),
            enforce_hard_limits=bool(self.config.enforce_hard_limits),
        )
        self.seed = int(self.config.seed)
        self.audit: List[Dict[str, Any]] = []

    def _pid(self, idx: int) -> str:
        return _make_id(self.seed, "plan", idx)

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def slice_order(
        self,
        symbol: str,
        side: str,
        total_notional_usd: float,
        total_qty: float,
        venue: str,
        schedule: Optional[str] = None,
        n_slices: Optional[int] = None,
        idx: int = 0,
    ) -> SlicingPlan:
        self._log("slice_order", {"symbol": symbol, "side": side, "total_notional_usd": total_notional_usd})
        symbol = str(symbol).upper()
        side = str(side).lower()
        venue = str(venue).lower()
        schedule = schedule or self.config.default_schedule
        if schedule not in ("twap", "vwap", "adaptive"):
            schedule = "twap"
        if n_slices is None:
            n_slices = int(math.ceil(total_notional_usd / self.config.max_slice_notional_usd))
        n_slices = int(max(self.config.min_slices, min(self.config.max_slices, n_slices)))
        plan_id = self._pid(idx)
        per = total_notional_usd / n_slices
        per_qty = total_qty / n_slices
        slices: List[Slice] = []
        for i in range(n_slices):
            offset_ms = i * (60000.0 / max(n_slices, 1)) if schedule == "twap" else i * (30000.0 / max(n_slices, 1))
            slices.append(
                Slice(
                    slice_id=f"{plan_id}_s{i:03d}",
                    slice_index=i,
                    notional_usd=float(per),
                    qty=float(per_qty),
                    scheduled_offset_ms=float(offset_ms),
                    venue=venue,
                    symbol=symbol,
                    side=side,
                    paper_only=True,
                    timestamp=_det_ts(self.seed, idx + i),
                )
            )
        plan = {
            "plan_id": plan_id,
            "symbol": symbol,
            "side": side,
            "total_notional_usd": float(total_notional_usd),
            "total_qty": float(total_qty),
            "schedule": schedule,
            "slice_count": int(n_slices),
            "slices": [asdict(s) for s in slices],
            "venue": venue,
            "paper_only": True,
            "timestamp": _det_ts(self.seed, idx),
        }
        _assert_no_nan_inf(plan, "p22_slicing_plan")
        return SlicingPlan(
            plan_id=plan["plan_id"],
            symbol=plan["symbol"],
            side=plan["side"],
            total_notional_usd=plan["total_notional_usd"],
            total_qty=plan["total_qty"],
            schedule=plan["schedule"],
            slice_count=plan["slice_count"],
            slices=slices,
            venue=plan["venue"],
            paper_only=True,
            timestamp=plan["timestamp"],
        )

    def generate_report(self, plans: List[SlicingPlan]) -> Dict[str, Any]:
        total_slices = sum(p.slice_count for p in plans)
        avg_slice_notional = float(sum(p.total_notional_usd for p in plans) / max(total_slices, 1))
        rep = {
            "report": "PHASE22_ORDER_SLICING_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "plan_count": len(plans),
            "total_slice_count": int(total_slices),
            "plans": [asdict(p) for p in plans],
            "summary": {
                "avg_slice_notional_usd": float(avg_slice_notional),
                "schedules_used": list(dict.fromkeys(p.schedule for p in plans)),
                "paper_only": True,
            },
            "audit": self.audit,
            "git_sha": _git_sha(),
            "paper_only": True,
        }
        _assert_no_nan_inf(rep, "p22_slicing_report")
        return rep
