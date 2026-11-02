from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from src.telemetry.serialization import serialize_metrics_strict


@dataclass(frozen=True)
class Phase56FlowSynthConfig:
    seed: int = 12345
    paper_only: bool = True
    venues: tuple[str, ...] = ("deribit", "okx", "bybit")
    max_venues: int = 3

    def __post_init__(self) -> None:
        if not self.paper_only:
            raise ValueError("paper_only must remain True (live paths hard-gated)")
        if self.max_venues < 1:
            raise ValueError("max_venues must be >=1")


@dataclass
class Phase56CrossVenueOptionsFlowSynthesizer:
    cfg: Phase56FlowSynthConfig = field(default_factory=Phase56FlowSynthConfig)
    domain_focus: str = "crypto_options_orderflow"

    def synthesize(self, venue_flows: Dict[str, Dict[str, float]] | None = None) -> Dict[str, Any]:
        venue_flows = venue_flows or {}
        fragments = []
        for v in self.cfg.venues:
            vf = venue_flows.get(v) or {}
            bid_vol = float(vf.get("bid_vol", 100.0))
            ask_vol = float(vf.get("ask_vol", 100.0))
            tox = float(vf.get("toxicity", 0.1))
            frag = abs(bid_vol - ask_vol) / max(1.0, bid_vol + ask_vol)
            fragments.append({"venue": v, "fragmentation": frag, "toxicity": tox})
        avg_frag = sum(x["fragmentation"] for x in fragments) / max(1, len(fragments))
        avg_tox = sum(x["toxicity"] for x in fragments) / max(1, len(fragments))
        regime = "normal" if avg_frag < 0.15 and avg_tox < 0.25 else "stressed"
        route = "consolidated" if regime == "normal" else "split_venues"
        rep = {
            "phase": "PHASE56_CROSS_VENUE_OPTIONS_FLOW_SYNTHESIZER",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "paper_only": True,
            "live_path_hard_gated": True,
            "domain_focus": self.domain_focus,
            "venues": list(self.cfg.venues),
            "fragments": fragments,
            "avg_fragmentation": avg_frag,
            "avg_toxicity": avg_tox,
            "regime": regime,
            "routing_recommendation": route,
            "integration": "Phase50+Phase51+Phase52+Phase53+Phase54",
            "deterministic": True,
            "finite": True,
        }
        return serialize_metrics_strict(rep)

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, str]:
        p = Path(outdir)
        p.mkdir(parents=True, exist_ok=True)
        rep = self.synthesize()
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = p / f"PHASE56_FLOW_SYNTH_{ts}.json"
        mpath = p / f"PHASE56_FLOW_SYNTH_{ts}.md"
        jpath.write_text(__import__("json").dumps(rep, indent=2))
        mpath.write_text(f"# PHASE56 Cross-Venue Options Flow Synthesis\n\n- timestamp: {rep['timestamp']}\n- regime: {rep['regime']}\n- routing: {rep['routing_recommendation']}\n- avg_fragmentation: {rep['avg_fragmentation']:.6f}\n- avg_toxicity: {rep['avg_toxicity']:.6f}\n- paper_only: true\n")
        return {"json_path": str(jpath), "md_path": str(mpath)}
