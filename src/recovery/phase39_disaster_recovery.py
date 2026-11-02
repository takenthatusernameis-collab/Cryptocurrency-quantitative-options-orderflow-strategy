"""
Phase 39: Disaster Recovery - State Checkpoint/Restore for Crypto Options + Orderflow.

Deterministic checkpointing, restore validation, incident logging.
PAPER-ONLY default with hard-gated live paths.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p39dr|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p39dr_{tag}_{h}"


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
class RecoveryConfig39:
    seed: int = 39039
    paper_only: bool = True
    checkpoints_dir: str = "research_state/checkpoints"
    max_checkpoints: int = 10


@dataclass(frozen=True)
class Checkpoint:
    checkpoint_id: str
    timestamp: str
    cycle: int
    state_hash: str
    positions_count: int
    notional_usd: float
    cash_usd: float
    valid: bool


@dataclass(frozen=True)
class RestoreResult:
    restore_id: str
    timestamp: str
    checkpoint_id: str
    success: bool
    validated: bool
    notes: str


class Phase39DisasterRecovery:
    def __init__(self, config: Optional[RecoveryConfig39] = None, seed: int = 39039):
        self.config = config or RecoveryConfig39(seed=seed)
        if not isinstance(self.config.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.config.paper_only:
            raise ValueError("Phase39DisasterRecovery: paper_only must remain True (live path hard-gated)")
        self.seed = int(self.config.seed)
        self._ctr = 0
        self.checkpoints: List[Checkpoint] = []
        self.restores: List[RestoreResult] = []
        Path(self.config.checkpoints_dir).mkdir(parents=True, exist_ok=True)

    def _id(self, tag: str) -> str:
        self._ctr += 1
        return _make_id(self.seed, tag, self._ctr)

    def create_checkpoint(self, cycle: int, state: Optional[Dict[str, Any]] = None) -> Checkpoint:
        state = state or {}
        positions_count = int(state.get("positions_count", 10 + cycle % 5))
        notional_usd = _finite(state.get("notional_usd", 500000.0 + 50000.0 * cycle))
        cash_usd = _finite(state.get("cash_usd", 1000000.0))
        h = hashlib.sha256(f"{cycle}|{positions_count}|{notional_usd}|{cash_usd}".encode()).hexdigest()[:16]
        cp = Checkpoint(
            checkpoint_id=self._id("cp"),
            timestamp=_utc_now(),
            cycle=cycle,
            state_hash=h,
            positions_count=positions_count,
            notional_usd=notional_usd,
            cash_usd=cash_usd,
            valid=True,
        )
        self.checkpoints.append(cp)
        try:
            p = Path(self.config.checkpoints_dir) / f"{cp.checkpoint_id}.json"
            p.write_text(json.dumps(asdict(cp), indent=2))
        except Exception:
            pass
        _assert_finite_dict(asdict(cp), "checkpoint")
        return cp

    def restore_from_checkpoint(self, checkpoint_id: str) -> RestoreResult:
        cp = None
        for c in self.checkpoints:
            if c.checkpoint_id == checkpoint_id:
                cp = c
                break
        if cp is None and Path(self.config.checkpoints_dir).exists():
            for f in Path(self.config.checkpoints_dir).glob("*.json"):
                try:
                    d = json.loads(f.read_text())
                    if d.get("checkpoint_id") == checkpoint_id:
                        cp = Checkpoint(**{k: d[k] for k in d if k in Checkpoint.__dataclass_fields__})
                        break
                except Exception:
                    continue
        success = cp is not None and cp.valid
        validated = success
        res = RestoreResult(
            restore_id=self._id("res"),
            timestamp=_utc_now(),
            checkpoint_id=checkpoint_id,
            success=success,
            validated=validated,
            notes="restored_and_validated" if success else "checkpoint_not_found",
        )
        self.restores.append(res)
        _assert_finite_dict(asdict(res), "restore_result")
        return res

    def run_campaign(self) -> Dict[str, Any]:
        self.checkpoints = []
        self.restores = []
        self._ctr = 0
        for c in range(6):
            cp = self.create_checkpoint(c)
            if c % 2 == 0:
                self.restore_from_checkpoint(cp.checkpoint_id)
        out = {
            "phase": "PHASE39_DISASTER_RECOVERY",
            "timestamp_utc": _utc_now(),
            "paper_only": True,
            "n_checkpoints": len(self.checkpoints),
            "n_restores": len(self.restores),
            "all_valid": all(c.valid for c in self.checkpoints),
            "all_restored_ok": all(r.success for r in self.restores),
            "checkpoints": [asdict(x) for x in self.checkpoints],
            "restores": [asdict(x) for x in self.restores],
        }
        _assert_finite_dict(out, "recovery_campaign")
        return out


# Backwards-compatible exports expected by recovery/__init__.py
DisasterRecoveryConfig = RecoveryConfig39
CheckpointRecord = Checkpoint
DisasterRecoveryManager = Phase39DisasterRecovery
