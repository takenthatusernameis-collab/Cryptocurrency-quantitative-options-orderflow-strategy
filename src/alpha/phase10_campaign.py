"""Phase 10 Campaign Orchestrator."""
from __future__ import annotations

import json
import math
import os
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.alpha.vol_surface_rv import VolSurfaceRVEngine, VolSurfaceRVConfig
from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.alpha.signal_fusion import SignalFusion
from src.alpha.position_sizing import PositionSizer
from src.alpha.walkforward_oos import WalkForwardOOS, OOSConfig
from src.data.schemas import OptionContract, OptionQuote, OptionsChain, OrderflowSnapshot, Trade
from src.telemetry.serialization import serialize_metrics_strict, assert_json_valid


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _git_sha() -> Optional[str]:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd="/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy",
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        if r.returncode == 0:
            return r.stdout.decode().strip()
    except Exception:
        pass
    return None


class Phase10Campaign:
    def __init__(self, symbols: Tuple[str, ...] = ("BTC", "ETH"), seed: int = 42,
                 spot: Optional[Dict[str, float]] = None):
        self.symbols = tuple(symbols)
        self.seed = int(seed)
        self.spot = spot or {"BTC": 65000.0, "ETH": 3400.0}
        self.outdir = Path("research_state")
        self.outdir.mkdir(parents=True, exist_ok=True)

    def _gen_chain(self, symbol: str) -> OptionsChain:
        rng = np.random.default_rng(hash((symbol, self.seed)) % (2**32))
        now = datetime(2026, 10, 31, 0, 0, 0, tzinfo=timezone.utc)
        strikes = [self.spot[symbol] * (1 + d) for d in np.linspace(-0.2, 0.2, 9)]
        expiries_list = []
        for d in [7, 14, 30, 60]:
            expiries_list.append(now + timedelta(days=d))
        quotes: List[OptionQuote] = []
        for exp in expiries_list:
            T = max(1e-12, (exp - now).total_seconds() / (365.25 * 86400))
            for k in strikes:
                for ot in ["call", "put"]:
                    m = k / self.spot[symbol]
                    iv = 0.8 + 0.3 * abs(m - 1.0) + 0.1 * math.sqrt(T)
                    iv = float(np.clip(iv, 0.3, 2.0))
                    bid = max(0.01, iv * self.spot[symbol] * math.sqrt(T) * 0.01)
                    ask = bid * 1.02
                    contract = OptionContract(
                        symbol=f"{symbol}-USD-{exp.strftime('%y%m%d')}-{int(k)}-{ot[0].upper()}",
                        underlying=symbol,
                        strike=float(k),
                        expiry=exp,
                        option_type=ot,
                        venue="synthetic",
                        contract_size=1.0,
                    )
                    quotes.append(OptionQuote(
                        contract=contract,
                        bid=float(bid),
                        ask=float(ask),
                        mark=float(0.5*(bid+ask)),
                        mark_iv=float(iv),
                        bid_iv=float(iv*0.98),
                        ask_iv=float(iv*1.02),
                        volume=float(rng.uniform(10, 1000)),
                        open_interest=float(rng.uniform(100, 10000)),
                        timestamp=now,
                    ))
        chain = OptionsChain(
            underlying=symbol,
            venue="synthetic",
            quotes=quotes,
            timestamp=now,
        )
        return chain

    def _gen_orderflow(self, symbol: str) -> OrderflowSnapshot:
        rng = np.random.default_rng(hash((symbol, self.seed, "of")) % (2**32))
        now = datetime(2026, 10, 31, 0, 0, 0, tzinfo=timezone.utc)
        trades: List[Trade] = []
        for i in range(200):
            side = "buy" if rng.random() < 0.53 else "sell"
            sz = float(rng.exponential(0.5))
            px = self.spot[symbol] * (1 + rng.normal(0, 0.001))
            trades.append(Trade(
                trade_id=f"p10_{symbol}_{i}",
                symbol=f"{symbol}USDT",
                venue="synthetic",
                price=float(px),
                size=float(sz),
                side=side,
                timestamp=now,
            ))
        return OrderflowSnapshot(
            symbol=f"{symbol}USDT",
            venue="synthetic",
            timestamp=now,
            trades=trades,
        )

    def run(self) -> Dict[str, Any]:
        sha = _git_sha()
        rv_eng = VolSurfaceRVEngine(VolSurfaceRVConfig(seed=self.seed))
        of_eng = OrderflowAlphaEngine(seed=self.seed)
        fusion = SignalFusion(seed=self.seed)
        sizer = PositionSizer(capital=100000.0, seed=self.seed)
        oos = WalkForwardOOS(OOSConfig(seed=self.seed))

        all_rv = []
        all_of = []
        for sym in self.symbols:
            chain = self._gen_chain(sym)
            opps = rv_eng.detect_dislocations(chain, spot=self.spot[sym])
            all_rv.extend(opps)
            snap = self._gen_orderflow(sym)
            feat = of_eng.extract_features(snap)
            all_of.append(feat)

        pf = {"BTC": 0.01, "ETH": 0.015}
        intents = fusion.fuse(all_rv, all_of, pf)
        sized = sizer.size(intents)

        rng = np.random.default_rng(self.seed)
        rets = rng.normal(0.0002, 0.01, 500)
        oos_rep = oos.run(rets)

        rv_rep = rv_eng.generate_report(all_rv, self.seed)
        of_rep = of_eng.generate_report(all_of)
        fus_rep = fusion.generate_report(intents)
        sz_rep = sizer.generate_report(sized)

        for rep in [rv_rep, of_rep, fus_rep, sz_rep, oos_rep]:
            rep["git_sha"] = sha
            rep["symbols"] = list(self.symbols)
            rep["seed"] = int(self.seed)

        paths = []
        for name, rep in [
            ("VOL_SURFACE_RV_REPORT", rv_rep),
            ("ORDERFLOW_ALPHA_REPORT", of_rep),
            ("SIGNAL_FUSION_REPORT", fus_rep),
            ("SIZING_REPORT", sz_rep),
            ("WALKFORWARD_OOS_REPORT", oos_rep),
        ]:
            p_json = self.outdir / f"{name}.json"
            p_md = self.outdir / f"{name}.md"
            assert_json_valid(rep)
            p_json.write_text(json.dumps(rep, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
            md = f"# {name}\n\n- Timestamp: {rep.get('timestamp')}\n- Seed: {rep.get('seed')}\n- Git SHA: {rep.get('git_sha')}\n- Symbols: {rep.get('symbols')}\n- Count: {rep.get('count', rep.get('n_folds'))}\n"
            p_md.write_text(md, encoding="utf-8")
            paths.extend([str(p_json), str(p_md)])

        master = {
            "timestamp": _utc_now(),
            "git_sha": sha,
            "seed": int(self.seed),
            "symbols": list(self.symbols),
            "counts": {
                "rv_opps": len(all_rv),
                "of_features": len(all_of),
                "intents": len(intents),
                "sized": len(sized),
            },
            "artifacts": paths,
        }
        master = serialize_metrics_strict(master)
        assert_json_valid(master)
        (self.outdir / "PHASE10_ALPHA_REPORT.json").write_text(json.dumps(master, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        (self.outdir / "PHASE10_ALPHA_REPORT.md").write_text(f"# PHASE10_ALPHA_REPORT\n\n{json.dumps(master, indent=2)}\n", encoding="utf-8")
        paths.extend([str(self.outdir / "PHASE10_ALPHA_REPORT.json"), str(self.outdir / "PHASE10_ALPHA_REPORT.md")])
        return {"artifacts": paths, "master": master}
