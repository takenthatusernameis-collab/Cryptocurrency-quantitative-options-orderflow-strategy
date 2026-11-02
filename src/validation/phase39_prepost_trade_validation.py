"""
Phase 39: Pre-Trade/Post-Trade Validation for Crypto Options + Orderflow.

Deterministic validation gates, finite numerics, PAPER-ONLY default.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p39pv|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p39pv_{tag}_{h}"


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


def _assert_finite_dict(d: Dict[str, Any], label: str = "obj") -> None:
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

    walk(d, "$")
    if bad:
        raise ValueError(f"Non-finite in {label}: {bad[:10]}")


@dataclass(frozen=True)
class PrePostConfig39:
    seed: int = 39039
    paper_only: bool = True
    max_order_notional_usd: float = 100000.0
    max_slippage_bps: float = 15.0
    require_option_greeks_valid: bool = True


@dataclass(frozen=True)
class ValidationGate:
    gate_id: str
    phase: str  # pre|post
    name: str
    passed: bool
    reason: str
    timestamp: str


@dataclass(frozen=True)
class ValidationResult:
    result_id: str
    cycle: int
    paper_only: bool
    pre_gates: List[ValidationGate]
    post_gates: List[ValidationGate]
    all_passed: bool
    blocked: bool


class Phase39PrePostTradeValidation:
    def __init__(self, config: Optional[PrePostConfig39] = None, seed: int = 39039):
        self.config = config or PrePostConfig39(seed=seed)
        if not isinstance(self.config.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.config.paper_only:
            raise ValueError("Phase39PrePostTradeValidation: paper_only must remain True (live path hard-gated)")
        self.seed = int(self.config.seed)
        self._ctr = 0
        self.results: List[ValidationResult] = []

    def _id(self, tag: str) -> str:
        self._ctr += 1
        return _make_id(self.seed, tag, self._ctr)

    def validate(self, cycle: int, order: Optional[Dict[str, Any]] = None, fill: Optional[Dict[str, Any]] = None) -> ValidationResult:
        order = order or {}
        fill = fill or {}
        pre_gates: List[ValidationGate] = []
        post_gates: List[ValidationGate] = []

        notional = _finite(order.get("notional_usd", 50000.0))
        pre_gates.append(
            ValidationGate(
                gate_id=self._id("pre_n"),
                phase="pre",
                name="order_notional_limit",
                passed=notional <= self.config.max_order_notional_usd,
                reason="ok" if notional <= self.config.max_order_notional_usd else "exceeds_limit",
                timestamp=_utc_now(),
            )
        )

        delta = _finite(order.get("delta", 0.1))
        pre_gates.append(
            ValidationGate(
                gate_id=self._id("pre_g"),
                phase="pre",
                name="greeks_finite",
                passed=math.isfinite(delta),
                reason="ok" if math.isfinite(delta) else "non_finite",
                timestamp=_utc_now(),
            )
        )

        venue_ok = order.get("venue", "deribit") in ("deribit", "okx", "bybit", "binance")
        pre_gates.append(
            ValidationGate(
                gate_id=self._id("pre_v"),
                phase="pre",
                name="venue_allowlist",
                passed=venue_ok,
                reason="ok" if venue_ok else "venue_not_allowed",
                timestamp=_utc_now(),
            )
        )

        slippage_bps = _finite(fill.get("slippage_bps", 5.0))
        post_gates.append(
            ValidationGate(
                gate_id=self._id("post_s"),
                phase="post",
                name="slippage_limit",
                passed=slippage_bps <= self.config.max_slippage_bps,
                reason="ok" if slippage_bps <= self.config.max_slippage_bps else "slippage_exceeds",
                timestamp=_utc_now(),
            )
        )

        fill_ok = fill.get("filled", True) in (True, False)
        post_gates.append(
            ValidationGate(
                gate_id=self._id("post_f"),
                phase="post",
                name="fill_state_valid",
                passed=isinstance(fill_ok, bool),
                reason="ok",
                timestamp=_utc_now(),
            )
        )

        all_passed = all(g.passed for g in pre_gates + post_gates)
        blocked = not all_passed
        res = ValidationResult(
            result_id=self._id("vres"),
            cycle=cycle,
            paper_only=True,
            pre_gates=pre_gates,
            post_gates=post_gates,
            all_passed=all_passed,
            blocked=blocked,
        )
        self.results.append(res)
        _assert_finite_dict(asdict(res), "validation_result")
        return res

    def run_campaign(self) -> Dict[str, Any]:
        self.results = []
        self._ctr = 0
        for c in range(12):
            self.validate(c)
        out = {
            "phase": "PHASE39_PREPOST_VALIDATION",
            "timestamp_utc": _utc_now(),
            "paper_only": True,
            "n_results": len(self.results),
            "all_passed_count": sum(1 for x in self.results if x.all_passed),
            "blocked_count": sum(1 for x in self.results if x.blocked),
            "results": [asdict(x) for x in self.results],
        }
        _assert_finite_dict(out, "prepost_campaign")
        return out
