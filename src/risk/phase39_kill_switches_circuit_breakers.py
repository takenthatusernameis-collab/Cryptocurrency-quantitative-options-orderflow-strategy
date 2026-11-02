"""
Phase 39: Kill-Switches, Circuit Breakers & Live-Readiness Guards for Crypto Options + Orderflow.

Multi-layer kill-switches, circuit breakers, position limits by venue/regime,
pre/post-trade validation hooks. Deterministic, finite numerics, PAPER-ONLY default
with hard-gated live paths. Extends Phases 17-38.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p39ks|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p39ks_{tag}_{h}"


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


class KillSwitchLevel(str, Enum):
    SOFT = "soft"
    HARD = "hard"
    GLOBAL = "global"


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass(frozen=True)
class KillSwitchConfig39:
    seed: int = 39039
    paper_only: bool = True
    underlyings: Tuple[str, ...] = ("BTC", "ETH", "SOL", "XRP")
    venues: Tuple[str, ...] = ("deribit", "okx", "bybit", "binance")
    max_drawdown_pct: float = 0.08
    kill_dd_pct: float = 0.12
    max_daily_loss_usd: float = 50000.0
    max_position_notional_usd: float = 2000000.0
    per_venue_limit_usd: float = 600000.0
    max_order_rate_per_sec: float = 50.0
    max_consecutive_errors: int = 10
    require_manual_reset: bool = True


@dataclass(frozen=True)
class KillEvent:
    event_id: str
    cycle: int
    level: str
    trigger: str
    venue: str
    regime: str
    action: str
    timestamp: str


@dataclass(frozen=True)
class CircuitSnapshot:
    venue: str
    state: str
    failures: int
    successes: int
    last_trip: Optional[str]
    time_to_half_open_sec: float


@dataclass(frozen=True)
class KillSwitchCycle:
    cycle: int
    timestamp: str
    paper_only: bool
    regime: str
    circuits: Tuple[CircuitSnapshot, ...]
    kill_events: Tuple[KillEvent, ...]
    global_halt: bool
    trading_enabled: bool
    action_taken: str


class Phase39KillSwitchesCircuitBreakers:
    def __init__(self, config: Optional[KillSwitchConfig39] = None, seed: int = 39039):
        self.config = config or KillSwitchConfig39(seed=seed)
        if not isinstance(self.config.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.config.paper_only:
            raise ValueError("Phase39KillSwitchesCircuitBreakers: paper_only must remain True (live path hard-gated)")
        self.seed = int(self.config.seed)
        self._ctr = 0
        self.kill_events_all: List[KillEvent] = []
        self.cycles: List[KillSwitchCycle] = []
        self._venue_states = {v: CircuitState.CLOSED for v in self.config.venues}
        self._venue_failures = {v: 0 for v in self.config.venues}
        self._venue_successes = {v: 0 for v in self.config.venues}
        self._global_halt = False

    def _id(self, tag: str) -> str:
        self._ctr += 1
        return _make_id(self.seed, tag, self._ctr)

    def _regime(self, c: int) -> str:
        r = c % 4
        return ("normal", "stressed", "volatile", "crisis")[r]

    def evaluate_cycle(self, cycle: int, state: Optional[Dict[str, Any]] = None) -> KillSwitchCycle:
        state = state or {}
        regime = self._regime(cycle)
        kill_events: List[KillEvent] = []
        circuits: List[CircuitSnapshot] = []

        dd = _finite(state.get("drawdown_pct", 0.02 + 0.01 * (cycle % 5)))
        daily_loss = _finite(state.get("daily_loss_usd", 0.0))
        total_notional = _finite(state.get("total_notional_usd", 800000.0 + 100000.0 * (cycle % 4)))
        order_rate = _finite(state.get("order_rate_per_sec", 10.0 + 5.0 * (cycle % 6)))
        consecutive_err = int(state.get("consecutive_errors", 0))

        if dd > self.config.kill_dd_pct or regime == "crisis":
            ev = KillEvent(
                event_id=self._id("global"),
                cycle=cycle,
                level=KillSwitchLevel.GLOBAL.value,
                trigger="drawdown_kill" if dd > self.config.kill_dd_pct else "crisis_regime",
                venue="*",
                regime=regime,
                action="global_halt_trading",
                timestamp=_utc_now(),
            )
            kill_events.append(ev)
            self.kill_events_all.append(ev)
            self._global_halt = True

        if daily_loss < -self.config.max_daily_loss_usd:
            ev = KillEvent(
                event_id=self._id("daily"),
                cycle=cycle,
                level=KillSwitchLevel.HARD.value,
                trigger="max_daily_loss",
                venue="*",
                regime=regime,
                action="halt_new_positions",
                timestamp=_utc_now(),
            )
            kill_events.append(ev)
            self.kill_events_all.append(ev)

        if total_notional > self.config.max_position_notional_usd:
            ev = KillEvent(
                event_id=self._id("pos"),
                cycle=cycle,
                level=KillSwitchLevel.HARD.value,
                trigger="max_position_notional",
                venue="*",
                regime=regime,
                action="force_reduce_exposure",
                timestamp=_utc_now(),
            )
            kill_events.append(ev)
            self.kill_events_all.append(ev)

        for venue in self.config.venues:
            vnotional = _finite(state.get(f"notional_{venue}", total_notional / len(self.config.venues)))
            if vnotional > self.config.per_venue_limit_usd:
                ev = KillEvent(
                    event_id=self._id(f"v_{venue}"),
                    cycle=cycle,
                    level=KillSwitchLevel.SOFT.value,
                    trigger="per_venue_limit",
                    venue=venue,
                    regime=regime,
                    action="throttle_venue",
                    timestamp=_utc_now(),
                )
                kill_events.append(ev)
                self.kill_events_all.append(ev)
                self._venue_failures[venue] += 1
                if self._venue_failures[venue] >= self.config.max_consecutive_errors:
                    self._venue_states[venue] = CircuitState.OPEN
            else:
                self._venue_successes[venue] += 1
                if self._venue_states[venue] == CircuitState.OPEN and self._venue_successes[venue] >= 3:
                    self._venue_states[venue] = CircuitState.HALF_OPEN
                elif self._venue_states[venue] == CircuitState.HALF_OPEN and self._venue_successes[venue] >= 5:
                    self._venue_states[venue] = CircuitState.CLOSED
                    self._venue_failures[venue] = 0

            circuits.append(
                CircuitSnapshot(
                    venue=venue,
                    state=self._venue_states[venue].value,
                    failures=self._venue_failures[venue],
                    successes=self._venue_successes[venue],
                    last_trip=_utc_now() if self._venue_states[venue] == CircuitState.OPEN else None,
                    time_to_half_open_sec=300.0 if self._venue_states[venue] == CircuitState.OPEN else 0.0,
                )
            )

        if order_rate > self.config.max_order_rate_per_sec:
            ev = KillEvent(
                event_id=self._id("rate"),
                cycle=cycle,
                level=KillSwitchLevel.SOFT.value,
                trigger="order_rate_limit",
                venue="*",
                regime=regime,
                action="rate_limit_orders",
                timestamp=_utc_now(),
            )
            kill_events.append(ev)
            self.kill_events_all.append(ev)

        if consecutive_err >= self.config.max_consecutive_errors:
            ev = KillEvent(
                event_id=self._id("err"),
                cycle=cycle,
                level=KillSwitchLevel.HARD.value,
                trigger="consecutive_errors",
                venue="*",
                regime=regime,
                action="halt_on_errors",
                timestamp=_utc_now(),
            )
            kill_events.append(ev)
            self.kill_events_all.append(ev)

        global_halt = self._global_halt or any(k.level == KillSwitchLevel.GLOBAL.value for k in kill_events)
        trading_enabled = not global_halt and not any(k.level == KillSwitchLevel.HARD.value and k.trigger in ("max_daily_loss", "halt_on_errors") for k in kill_events)
        action_taken = "halt_all" if global_halt else ("restrict" if kill_events else "none")

        res = KillSwitchCycle(
            cycle=cycle,
            timestamp=_utc_now(),
            paper_only=True,
            regime=regime,
            circuits=tuple(circuits),
            kill_events=tuple(kill_events),
            global_halt=global_halt,
            trading_enabled=trading_enabled,
            action_taken=action_taken,
        )
        _assert_finite_dict(asdict(res), "kill_switch_cycle")
        self.cycles.append(res)
        return res

    def run_campaign(self) -> Dict[str, Any]:
        self.cycles = []
        self.kill_events_all = []
        self._ctr = 0
        self._venue_states = {v: CircuitState.CLOSED for v in self.config.venues}
        self._venue_failures = {v: 0 for v in self.config.venues}
        self._venue_successes = {v: 0 for v in self.config.venues}
        self._global_halt = False

        for c in range(12):
            res = self.evaluate_cycle(c)
        out = {
            "phase": "PHASE39_KILL_SWITCHES",
            "timestamp_utc": _utc_now(),
            "paper_only": True,
            "n_cycles": len(self.cycles),
            "n_kill_events": len(self.kill_events_all),
            "global_halts": sum(1 for x in self.cycles if x.global_halt),
            "trading_enabled_cycles": sum(1 for x in self.cycles if x.trading_enabled),
            "cycles": [asdict(x) for x in self.cycles],
            "kill_events": [asdict(x) for x in self.kill_events_all],
        }
        _assert_finite_dict(out, "kill_switch_campaign")
        return out
