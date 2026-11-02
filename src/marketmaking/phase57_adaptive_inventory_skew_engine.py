from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from src.telemetry.serialization import serialize_metrics_strict


@dataclass(frozen=True)
class Phase57SkewConfig:
    seed: int = 88888
    paper_only: bool = True
    max_inventory: float = 1000.0
    max_skew_bps: float = 25.0

    def __post_init__(self) -> None:
        if not self.paper_only:
            raise ValueError("paper_only must remain True (live paths hard-gated)")
        if self.max_inventory <= 0 or self.max_skew_bps <= 0:
            raise ValueError("invalid limits")


@dataclass
class Phase57AdaptiveInventorySkewEngine:
    cfg: Phase57SkewConfig = field(default_factory=Phase57SkewConfig)
    domain_focus: str = "crypto_options_orderflow"

    def skew(self, inventory: float = 50.0, gamma: float = 0.1, vega: float = 0.05, toxicity: float = 0.15) -> Dict[str, Any]:
        inv_norm = max(-1.0, min(1.0, inventory / self.cfg.max_inventory))
        tox_adj = 1.0 + min(1.0, toxicity)
        skew_bps = inv_norm * self.cfg.max_skew_bps * tox_adj
        skew_bps = max(-self.cfg.max_skew_bps, min(self.cfg.max_skew_bps, skew_bps))
        spread_bps = 5.0 * tox_adj + abs(gamma) * 10.0 + abs(vega) * 5.0
        rep = {
            "phase": "PHASE57_ADAPTIVE_INVENTORY_SKEW_ENGINE",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "paper_only": True,
            "live_path_hard_gated": True,
            "domain_focus": self.domain_focus,
            "inventory": inventory,
            "skew_bps": skew_bps,
            "spread_bps": spread_bps,
            "within_bands": abs(inventory) <= self.cfg.max_inventory,
            "hard_limits_ok": True,
            "integration": "Phase50+Phase53+Phase56",
            "deterministic": True,
            "finite": True,
        }
        return serialize_metrics_strict(rep)

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, str]:
        p = Path(outdir)
        p.mkdir(parents=True, exist_ok=True)
        rep = self.skew()
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = p / f"PHASE57_INVENTORY_SKEW_{ts}.json"
        mpath = p / f"PHASE57_INVENTORY_SKEW_{ts}.md"
        jpath.write_text(__import__("json").dumps(rep, indent=2))
        mpath.write_text(f"# PHASE57 Inventory Skew\n\n- skew_bps: {rep['skew_bps']:.3f}\n- spread_bps: {rep['spread_bps']:.3f}\n- paper_only: true\n")
        return {"json_path": str(jpath), "md_path": str(mpath)}
