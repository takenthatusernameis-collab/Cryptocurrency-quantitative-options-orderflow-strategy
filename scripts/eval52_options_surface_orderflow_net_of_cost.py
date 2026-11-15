#!/usr/bin/env python3
"""EVAL-52: real Deribit **options SURFACE x options-venue ORDER FLOW** net-of-cost
falsification -- the pure options-side combined strategy.

The repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is a **combined options + orderflow** strategy. Every prior rung falsified one leg
(option surface EVAL-46..49, spot order flow EVAL-43/45/50, options-venue order
flow standalone EVAL-51) or a cross-venue pairing (EVAL-48/49). The **one
combination never measured** is the options market's **own surface fused with its
own order flow**. This script is the pre-registered net-of-cost falsification of
that fused signal on real, synchronized Deribit captures produced by
``scripts/eval52_acquire_synchronized_options.py``.

Strictly additive: it consumes only the measured capture JSON files under
``--capture-dir`` and reuses the sealed statistics helpers (``_sharpe_of_returns``,
``_dsr_of_returns``, ``_cscv_pbo``, ``_benjamini_hochberg``, ``block_bootstrap_ci``,
``permutation_test``) plus the sealed surface-signal primitive
``_options_signal_components``. It never re-runs a prior EVAL and never edits ``src/``.

Pre-declared protocol (identical for every underlying; no curve fitting):
  * resample the underlying perpetual 1m candles to a ``bar_seconds`` grid (60s or
    300s) and take the last close per bar; per-bar causal return into the next bar;
  * **options-surface alpha** (causal, newest snapshot whose 5m candle has *closed*
    by ``bar_end``): ``_options_signal_components(chain, spot, now)`` ->
    ``options_signal_raw`` = mean of ``gex_flip_signal`` / ``skew_slope_signal`` /
    ``calib_residual_signal`` clipped to [-1, 1];
  * **options-venue order flow** (per bar, real option trades in
    ``(bar_end - bar_seconds, bar_end]``):
      - ``imbalance``         = (buy_amt - sell_amt) / (buy_amt + sell_amt)
      - ``notional_imbalance``= (notional_buy - notional_sell) / (notional_buy + notional_sell)
      - ``call_minus_put``    = ((call_buy-call_sell) - (put_buy-put_sell)) / total_amt
    where amounts are measured Deribit ``amount`` and notional weights by ``index_price``;
  * **fusion rules** (pre-registered, fixed, no fitting):
      (a) ``sign_agreement``   -- both options-side legs agree in sign -> take that sign, else flat;
      (b) ``regime_filter``    -- surface sign as causal regime gate x order-flow direction;
      (c) ``continuous_zscore``-- causal expanding z-score of each leg, summed, ``clip(z_sum/2,-1,1)``;
  * position -> per-bar net-of-cost return
    ``pos_t * perp_return_{t->t+1} - cost_bps * |pos_t - pos_{t-1}| / 1e4`` with a
    pre-registered conservative 5 bps on turnover (net-of-cost by construction);
  * full-series (causal -> out-of-sample) plus rolling walk-forward Sharpe/max-DD;
  * stats: 1000-perm paired permutation (strategy vs flat), 1000-resample block
    bootstrap CI on Sharpe (block 2), CSCV PBO across the pre-registered grid
    (k=4), BH-FDR (alpha 0.1), DSR; seed 42.

Pre-declared GO bar (conservative; the ladder EVAL-46..51 is CLOSED so NO-GO is the
default and GO needs strong evidence): GO only if, on **both** BTC and ETH and
**at least one** grid config, net-of-cost Sharpe > 0, no kill-switch breach
(max-DD <= 0.20), permutation p < 0.05, bootstrap 95% CI lower bound > 0, and pooled
PBO < 0.5. Otherwise ``NO-GO CONFIRMED (PASS)``.

Heavy-work floor (sealed): refuses to seal a verdict unless **every** underlying
independently clears the per-underlying floor -- surface >=100 snapshots / >=50
instruments / >=240 5m bars; options order flow >=2000 trades / >=50 instruments /
>=240 bars / >=79200 s span; the two legs overlap on >=240 common 5m bars -- and the
roster has >=2 underlyings. Below floor seals a measured ``EVAL_52_BLOCKED_<UTC>``
(never a NO-GO).

Seal ``EVAL_52_PREREGISTRATION_<UTC>.{json,md}`` (before measurement) then
``EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_<UTC>.{json,md}`` (or
``EVAL_52_BLOCKED_<UTC>``).
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analytics.integrated_options_orderflow_evaluation import (  # noqa: E402
    _dsr_of_returns,
    _options_signal_components,
    _sharpe_of_returns,
)
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
    _cscv_pbo,
)
from src.analytics.strategy_evaluation import (  # noqa: E402
    block_bootstrap_ci,
    permutation_test,
)
from src.data.loader import _parse_dt  # noqa: E402
from src.data.normalization import normalize_options_chain  # noqa: E402
from src.data.schemas import OptionContract, OptionQuote, OptionsChain  # noqa: E402
from src.data.validators import validate_options_chain  # noqa: E402

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED"
PREREG_ID = "EVAL_52_PREREGISTRATION"
BLOCKED_ID = "EVAL_52_BLOCKED"

BAR_SECONDS = 300.0
ZWINDOW = 20
Z_CLAMP = 2.0
COST_BPS = 5.0
PERMUTATION_PERMS = 1000
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_BLOCK = 2
PBO_K_FOLDS = 4
PBO_N_COMBINATIONS = 16
FDR_ALPHA = 0.1
SEED = 42
KILL_SWITCH_MAX_DD = 0.20

# Heavy-work floor (per underlying).
MIN_SNAPSHOTS = 100
MIN_BARS = 240
MIN_INSTRUMENTS = 50
MIN_TRADES = 2000
MIN_SPAN_SECONDS = 79200.0
MIN_COMMON_BARS = 240
MIN_UNDERLYINGS = 2

OF_SIGNALS: Tuple[str, ...] = ("imbalance", "notional_imbalance", "call_minus_put")
FUSION_RULES: Tuple[str, ...] = ("sign_agreement", "regime_filter", "continuous_zscore")
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
SURFACE_BAR_SECONDS = 300.0
SIGNAL_EPS = 1e-9

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/integrated_options_orderflow_evaluation.py",
    "src/analytics/real_walkforward_certification.py",
    "src/analytics/strategy_evaluation.py",
    "src/data/loader.py",
    "scripts/eval48_acquire_deribit_options.py",
    "scripts/eval51_acquire_options_orderflow.py",
    "scripts/eval52_acquire_synchronized_options.py",
    "scripts/eval52_options_surface_orderflow_net_of_cost.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval52_acquire_synchronized_options.py "
    "scripts/eval52_options_surface_orderflow_net_of_cost.py "
    "tests/test_eval52_options_surface_orderflow_net_of_cost.py",
    "python3 -m pytest -q tests/test_eval52_options_surface_orderflow_net_of_cost.py",
    "python3 scripts/eval52_acquire_synchronized_options.py "
    "--underlying BTC --underlying ETH --days 1 --out-dir data/raw/eval52 --seal",
    "python3 scripts/eval52_options_surface_orderflow_net_of_cost.py --no-write",
    "python3 scripts/eval52_options_surface_orderflow_net_of_cost.py",
)


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp_for_filename(iso_ts: str) -> str:
    return iso_ts.replace("-", "").replace(":", "").replace(".", "")


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
        return v if math.isfinite(v) else float(default)
    except (TypeError, ValueError):
        return float(default)


def _mean(vals: Sequence[float]) -> float:
    vals = [float(v) for v in vals]
    return sum(vals) / len(vals) if vals else 0.0


def _std(vals: Sequence[float]) -> float:
    vals = [float(v) for v in vals]
    n = len(vals)
    if n < 2:
        return 0.0
    m = sum(vals) / n
    return math.sqrt(sum((v - m) ** 2 for v in vals) / n)


def _max_drawdown(rets: Sequence[float]) -> float:
    eq = 1.0
    peak = 1.0
    mdd = 0.0
    for r in rets:
        eq *= 1.0 + float(r)
        if eq <= 0:
            return 1.0
        peak = max(peak, eq)
        dd = (peak - eq) / peak if peak > 0 else 0.0
        mdd = max(mdd, dd)
    return mdd


def kill_switch_breach(max_drawdown: float) -> bool:
    return float(max_drawdown) > KILL_SWITCH_MAX_DD


def _bar_end(ts_ms: int, bar_ms: int) -> int:
    return ((int(ts_ms) // bar_ms) + 1) * bar_ms


def expanding_zscore(xs: Sequence[float], window: int, min_periods: int = 5) -> List[float]:
    out: List[float] = []
    for i in range(len(xs)):
        lo = max(0, i - int(window) + 1)
        w = [float(v) for v in xs[lo : i + 1]]
        if len(w) < max(2, int(min_periods)):
            out.append(0.0)
            continue
        m = sum(w) / len(w)
        sd = math.sqrt(sum((v - m) ** 2 for v in w) / len(w))
        out.append((float(xs[i]) - m) / sd if sd > 0 else 0.0)
    return out


def _sign(x: float, eps: float = SIGNAL_EPS) -> float:
    if x > eps:
        return 1.0
    if x < -eps:
        return -1.0
    return 0.0


# ---------------------------------------------------------------------------
# Fusion rules (pre-registered)
# ---------------------------------------------------------------------------
def fuse_sign_agreement(surface: Sequence[float], orderflow: Sequence[float]) -> List[float]:
    """(a) trade only when both options-side legs agree in sign, else flat."""
    out: List[float] = []
    for s, f in zip(surface, orderflow):
        ds = _sign(_finite(s))
        df = _sign(_finite(f))
        out.append(ds if (ds != 0.0 and ds == df) else 0.0)
    return out


def fuse_regime_filter(surface: Sequence[float], orderflow: Sequence[float]) -> List[float]:
    """(b) surface sign as causal regime gate x order-flow direction."""
    out: List[float] = []
    for s, f in zip(surface, orderflow):
        regime = _sign(_finite(s))
        direction = _sign(_finite(f))
        out.append(regime * direction)
    return out


def fuse_continuous_zscore(
    surface: Sequence[float], orderflow: Sequence[float],
    *, zwindow: int = ZWINDOW, z_clamp: float = Z_CLAMP,
) -> List[float]:
    """(c) causal expanding z-score of each leg, summed, ``clip(z_sum/2, -1, 1)``."""
    zs = expanding_zscore(surface, zwindow)
    zf = expanding_zscore(orderflow, zwindow)
    out: List[float] = []
    for a, b in zip(zs, zf):
        # clip(z_sum / 2, -1, 1); ``z_clamp`` kept for signature symmetry.
        out.append(max(-1.0, min(1.0, (a + b) / 2.0)))
    return out


FUSION_FUNCS = {
    "sign_agreement": fuse_sign_agreement,
    "regime_filter": fuse_regime_filter,
    "continuous_zscore": fuse_continuous_zscore,
}


# ---------------------------------------------------------------------------
# Surface signal (per snapshot) + chain reconstruction
# ---------------------------------------------------------------------------
def chain_from_quotes(underlying: str, venue: str, quotes: Sequence[Dict[str, Any]],
                      ts: datetime) -> OptionsChain:
    """Rebuild an ``OptionsChain`` from captured quote dicts (mirrors the loader)."""
    cs: List[OptionQuote] = []
    for item in quotes:
        contract = OptionContract(
            symbol=str(item.get("symbol") or ""),
            underlying=str(item.get("underlying") or underlying or ""),
            strike=float(item.get("strike") or 0.0),
            expiry=_parse_dt(item.get("expiry")),
            option_type=str(item.get("option_type") or "call").lower(),
            venue=venue,
            contract_size=float(item.get("contract_size") or 1.0),
        )
        q = OptionQuote(
            contract=contract,
            bid=float(item.get("bid") or 0.0),
            ask=float(item.get("ask") or 0.0),
            last=item.get("last"),
            mark=item.get("mark"),
            bid_iv=item.get("bid_iv"),
            ask_iv=item.get("ask_iv"),
            mark_iv=item.get("mark_iv"),
            delta=item.get("delta"),
            gamma=item.get("gamma"),
            theta=item.get("theta"),
            vega=item.get("vega"),
            open_interest=float(item.get("open_interest") or 0.0),
            volume=float(item.get("volume") or 0.0),
            timestamp=_parse_dt(item.get("timestamp") or item.get("time") or ts),
        )
        cs.append(q)
    chain = OptionsChain(underlying=underlying, venue=venue, quotes=cs, timestamp=ts)
    chain = normalize_options_chain(chain)
    validate_options_chain(chain)
    return chain


def surface_signal_series(
    capture: Dict[str, Any], perp_candles: Sequence[Dict[str, Any]]
) -> List[Tuple[int, float]]:
    """Per-snapshot causal surface signal as ``[(available_time_ms, value)]`` ascending.

    ``available_time_ms = bar_ms + SURFACE_BAR_SECONDS*1000`` -- the 5m option candle
    has fully closed only at that time, so a trading bar may use the snapshot only
    when ``bar_end >= available_time_ms`` (no lookahead).
    """
    underlying = capture.get("underlying", "UNKNOWN")
    venue = capture.get("venue", "deribit")
    out: List[Tuple[int, float]] = []
    last_spot: Optional[float] = None
    for c in sorted(perp_candles, key=lambda x: int(x["ts"])):
        px = _finite(c.get("close"), 0.0)
        if px > 0:
            last_spot = px
        # not used directly; kept for clarity
    for snap in capture.get("surface", {}).get("snapshots", []):
        bar_ms = int(snap.get("bar_ms") or 0)
        if bar_ms <= 0:
            continue
        quotes = snap.get("quotes") or []
        if not quotes:
            continue
        spot = _finite(snap.get("spot"), 0.0)
        if spot <= 0:
            spot = last_spot or 0.0
        if spot <= 0:
            continue
        ts = datetime.fromtimestamp(bar_ms / 1000.0, tz=timezone.utc)
        try:
            chain = chain_from_quotes(underlying, venue, quotes, ts)
            comp = _options_signal_components(chain, float(spot), ts, seed=SEED)
            val = _finite(comp.get("options_signal_raw"), 0.0)
        except Exception:  # noqa: BLE001 - a snapshot that cannot be priced is skipped
            continue
        out.append((bar_ms + int(SURFACE_BAR_SECONDS) * 1000, float(val)))
    out.sort(key=lambda x: x[0])
    return out


def align_surface(available: Sequence[Tuple[int, float]], bar_ends: Sequence[int]) -> List[float]:
    """Newest snapshot value whose ``available_time <= bar_end`` (else 0.0 flat)."""
    times = [t for t, _ in available]
    vals = [v for _, v in available]
    out: List[float] = []
    j = -1
    for be in bar_ends:
        while j + 1 < len(times) and times[j + 1] <= be:
            j += 1
        out.append(vals[j] if j >= 0 else 0.0)
    return out


# ---------------------------------------------------------------------------
# Bar building (underlying grid + order-flow aggregation)
# ---------------------------------------------------------------------------
def build_bars(
    capture: Dict[str, Any],
    surface_available: Sequence[Tuple[int, float]],
    bar_seconds: float,
) -> List[Dict[str, Any]]:
    """Resample 1m perp candles to ``bar_seconds``; attach surface + order-flow signals."""
    bar_ms = int(float(bar_seconds) * 1000)
    candles = sorted(capture.get("perp_candles", []), key=lambda c: int(c["ts"]))
    if len(candles) < 2:
        return []

    closes: Dict[int, float] = {}
    for c in candles:
        be = _bar_end(int(c["ts"]), bar_ms)
        try:
            px = float(c["close"])
        except (TypeError, ValueError):
            continue
        if px > 0:
            closes[be] = px

    agg: Dict[int, Dict[str, float]] = {}

    def _bucket(be: int) -> Dict[str, float]:
        b = agg.get(be)
        if b is None:
            b = {
                "buy_amt": 0.0, "sell_amt": 0.0,
                "notional_buy": 0.0, "notional_sell": 0.0,
                "call_buy": 0.0, "call_sell": 0.0,
                "put_buy": 0.0, "put_sell": 0.0,
                "n_trades": 0,
            }
            agg[be] = b
        return b

    for t in capture.get("option_trades", []):
        try:
            ts = int(t["ts"])
            amt = abs(float(t.get("amount") or 0.0))
        except (TypeError, ValueError):
            continue
        if amt <= 0 or ts <= 0:
            continue
        idx = float(t.get("index_price") or 0.0)
        direction = str(t.get("direction") or "").lower()
        opt = str(t.get("option_type") or "").lower()
        be = _bar_end(ts, bar_ms)
        b = _bucket(be)
        b["n_trades"] += 1
        notional = amt * idx
        if direction == "buy":
            b["buy_amt"] += amt
            b["notional_buy"] += notional
            if opt == "call":
                b["call_buy"] += amt
            elif opt == "put":
                b["put_buy"] += amt
        elif direction == "sell":
            b["sell_amt"] += amt
            b["notional_sell"] += notional
            if opt == "call":
                b["call_sell"] += amt
            elif opt == "put":
                b["put_sell"] += amt

    bar_ends = sorted(closes)
    surf = align_surface(surface_available, bar_ends)

    bars: List[Dict[str, Any]] = []
    for i, be in enumerate(bar_ends):
        b = agg.get(be, {
            "buy_amt": 0.0, "sell_amt": 0.0,
            "notional_buy": 0.0, "notional_sell": 0.0,
            "call_buy": 0.0, "call_sell": 0.0,
            "put_buy": 0.0, "put_sell": 0.0,
            "n_trades": 0,
        })
        total_amt = b["buy_amt"] + b["sell_amt"]
        total_notional = b["notional_buy"] + b["notional_sell"]
        imbalance = (b["buy_amt"] - b["sell_amt"]) / total_amt if total_amt > 0 else 0.0
        notional_imbalance = (
            (b["notional_buy"] - b["notional_sell"]) / total_notional
            if total_notional > 0 else 0.0
        )
        cp = (b["call_buy"] - b["call_sell"]) - (b["put_buy"] - b["put_sell"])
        call_minus_put = cp / total_amt if total_amt > 0 else 0.0
        ret = 0.0
        if i + 1 < len(bar_ends):
            nxt = closes[bar_ends[i + 1]]
            cur = closes[be]
            if cur > 0 and nxt > 0:
                ret = nxt / cur - 1.0
        bars.append({
            "bar_end": int(be),
            "close": float(closes[be]),
            "ret": float(ret),
            "surface": float(surf[i]),
            "imbalance": float(imbalance),
            "notional_imbalance": float(notional_imbalance),
            "call_minus_put": float(call_minus_put),
            "n_trades": int(b["n_trades"]),
        })
    return bars


def strategy_returns(
    bars: Sequence[Dict[str, Any]], positions: Sequence[float], *, cost_bps: float = COST_BPS
) -> Dict[str, Any]:
    """Net-of-cost returns: ``pos_t*ret_t - cost_bps*|pos_t-pos_{t-1}|/1e4``."""
    if len(bars) < 2:
        return {"returns": [], "nonzero": 0, "signal_std": 0.0}
    returns: List[float] = []
    prev_pos = 0.0
    for i in range(len(bars) - 1):
        pos = float(positions[i]) if i < len(positions) else 0.0
        gross = pos * float(bars[i].get("ret", 0.0))
        turnover = abs(pos - prev_pos)
        cost = float(cost_bps) * turnover / 1e4
        returns.append(gross - cost)
        prev_pos = pos
    nonzero = sum(1 for p in positions if abs(float(p)) > 1e-9)
    return {"returns": returns, "nonzero": int(nonzero)}


def walkforward_folds(returns: Sequence[float], train: int, test: int, step: int) -> List[Dict[str, Any]]:
    folds: List[Dict[str, Any]] = []
    n = len(returns)
    start = int(train)
    while start + int(test) <= n:
        seg = [float(r) for r in returns[start : start + int(test)]]
        folds.append({
            "test_start": start,
            "test_end": start + int(test),
            "oos_sharpe": _sharpe_of_returns(seg),
            "oos_max_drawdown": _max_drawdown(seg),
            "n": len(seg),
        })
        start += int(step)
    return folds


def evaluate_config(
    capture: Dict[str, Any],
    surface_available: Sequence[Tuple[int, float]],
    *,
    fusion: str,
    of_signal: str,
    bar_seconds: float,
) -> Dict[str, Any]:
    inst = capture.get("underlying", "UNKNOWN")
    bars = build_bars(capture, surface_available, bar_seconds)
    if len(bars) < 4:
        return {
            "underlying": inst, "fusion": fusion, "signal": of_signal,
            "bar_seconds": float(bar_seconds), "error": "insufficient bars", "n_returns": 0,
            "pass": False,
        }
    surface = [b["surface"] for b in bars]
    orderflow = [b[of_signal] for b in bars]
    positions = FUSION_FUNCS[fusion](surface, orderflow)
    sr = strategy_returns(bars, positions)
    rets = sr["returns"]
    if len(rets) < 3:
        return {
            "underlying": inst, "fusion": fusion, "signal": of_signal,
            "bar_seconds": float(bar_seconds), "error": "insufficient returns",
            "n_returns": 0, "pass": False,
        }
    sharpe = _sharpe_of_returns(rets)
    mdd = _max_drawdown(rets)
    flat = [0.0] * len(rets)
    perm = permutation_test(rets, flat, statistic=_mean,
                            n_permutations=PERMUTATION_PERMS, paired=True, seed=SEED)
    boot = block_bootstrap_ci(rets, statistic=_sharpe_of_returns,
                              n_bootstrap=BOOTSTRAP_RESAMPLES, block_size=BOOTSTRAP_BLOCK,
                              seed=SEED)
    wf = walkforward_folds(rets, train=max(10, len(rets) // 3),
                           test=max(10, len(rets) // 5), step=max(10, len(rets) // 5))
    breach = kill_switch_breach(mdd)
    perm_p = _finite(perm.get("p_value"), 1.0)
    ci_low = _finite(boot[1], 0.0)
    ci_high = _finite(boot[2], 0.0)
    passed = bool(
        sharpe > 0.0
        and not breach
        and perm_p < 0.05
        and ci_low > 0.0
        and sr["nonzero"] > 0
    )
    return {
        "underlying": inst,
        "fusion": fusion,
        "signal": of_signal,
        "bar_seconds": float(bar_seconds),
        "n_bars": len(bars),
        "n_returns": len(rets),
        "nonzero_positions": sr["nonzero"],
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "kill_switch_breach": breach,
        "permutation_p": perm_p,
        "bootstrap_ci": [boot[0], ci_low, ci_high],
        "dsr": _dsr_of_returns(rets),
        "walkforward": wf,
        "mean_return": _mean(rets),
        "pass": passed,
    }


# ---------------------------------------------------------------------------
# Inventory + floor
# ---------------------------------------------------------------------------
def _capture_inventory(capture_dir: str) -> List[Dict[str, Any]]:
    """Load the newest synchronized capture per underlying."""
    best: Dict[str, Tuple[int, Dict[str, Any]]] = {}
    for path in sorted(glob.glob(os.path.join(capture_dir, "options_surface_orderflow_*.json"))):
        try:
            c = json.loads(Path(path).read_text())
        except (OSError, ValueError):
            continue
        inst = c.get("underlying", "?")
        stamp = 0
        try:
            tail = Path(path).stem.split("_")[-1]
            stamp = int("".join(ch for ch in tail if ch.isdigit()))
        except ValueError:
            stamp = 0
        if inst not in best or stamp > best[inst][0]:
            best[inst] = (stamp, c)
    return [c for _, c in best.values()]


def _bar_ends(perp_candles: Sequence[Dict[str, Any]], bar_seconds: float) -> List[int]:
    bar_ms = int(float(bar_seconds) * 1000)
    ends: set[int] = set()
    for c in perp_candles:
        px = _finite(c.get("close"), 0.0)
        if px > 0:
            ends.add(_bar_end(int(c["ts"]), bar_ms))
    return sorted(ends)


def _underlying_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    inst = capture.get("underlying", "?")
    surface = capture.get("surface", {})
    snaps = surface.get("snapshots", []) or []
    trades = capture.get("option_trades", []) or []
    perp = capture.get("perp_candles", []) or []

    n_snapshots = len(snaps)
    surface_instruments = len({
        q.get("symbol") for s in snaps for q in (s.get("quotes") or [])
    })
    surface_bars_5m = len(_bar_ends(perp, 300.0))

    trade_ts = [int(t["ts"]) for t in trades if int(t.get("ts") or 0) > 0]
    n_trades = len(trades)
    of_instruments = len({t.get("instrument") for t in trades if t.get("instrument")})
    span = ((max(trade_ts) - min(trade_ts)) / 1000.0) if len(trade_ts) >= 2 else 0.0
    of_bars_5m = int(span // 300.0) if span > 0 else 0

    # Common-grid overlap: 5m bars with a closed surface snapshot available and
    # falling inside the order-flow trade time range.
    surf_avail = surface_signal_series(capture, perp)
    avail_times = [t for t, _ in surf_avail]
    common = 0
    if trade_ts and avail_times:
        lo, hi = min(trade_ts), max(trade_ts)
        for be in _bar_ends(perp, 300.0):
            if be < lo or be > hi:
                continue
            # newest available snapshot <= be
            if any(at <= be for at in avail_times):
                common += 1

    checks = {
        "snapshots_ok": bool(n_snapshots >= MIN_SNAPSHOTS),
        "surface_instruments_ok": bool(surface_instruments >= MIN_INSTRUMENTS),
        "surface_bars_ok": bool(surface_bars_5m >= MIN_BARS),
        "trades_ok": bool(n_trades >= MIN_TRADES),
        "of_instruments_ok": bool(of_instruments >= MIN_INSTRUMENTS),
        "of_span_ok": bool(span >= MIN_SPAN_SECONDS),
        "of_bars_ok": bool(of_bars_5m >= MIN_BARS),
        "common_overlap_ok": bool(common >= MIN_COMMON_BARS),
    }
    return {
        "underlying": inst,
        "n_surface_snapshots": n_snapshots,
        "n_surface_instruments": surface_instruments,
        "n_surface_bars_5m": surface_bars_5m,
        "n_option_trades": n_trades,
        "n_of_instruments": of_instruments,
        "of_span_seconds": round(span, 3),
        "n_of_bars_5m": of_bars_5m,
        "n_common_bars_5m": common,
        "checks": checks,
        "ok": bool(all(checks.values())),
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-52",
        "title": "Real Deribit options surface x options-venue order flow net-of-cost falsification",
        "capture_dir": str(capture_dir),
        "surface_components": ["gex_flip_signal", "skew_slope_signal", "calib_residual_signal"],
        "surface_signal": "mean(components) clipped to [-1,1] (_options_signal_components)",
        "orderflow_signals": list(OF_SIGNALS),
        "fusion_rules": list(FUSION_RULES),
        "fusion_detail": {
            "sign_agreement": "both options-side legs agree in sign -> take that sign, else flat",
            "regime_filter": "surface sign as causal regime gate x order-flow direction",
            "continuous_zscore": "causal expanding z-score of each leg, summed, clip(z_sum/2,-1,1)",
        },
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "zwindow": int(ZWINDOW),
        "z_clamp": float(Z_CLAMP),
        "cost_bps": float(COST_BPS),
        "cost_model": "net-of-cost: pre-registered 5 bps on turnover (taker + impact)",
        "walkforward": {"train_frac": "1/3", "test_frac": "1/5", "step_frac": "1/5"},
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation_paired": True,
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "pbo_k_folds": PBO_K_FOLDS,
            "pbo_n_combinations": PBO_N_COMBINATIONS,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
        },
        "kill_switch_max_dd": KILL_SWITCH_MAX_DD,
        "go_bar": (
            "GO only if, on both BTC and ETH and at least one grid config, net-of-cost "
            "Sharpe > 0, no kill-switch breach (max-DD <= 0.20), permutation p < 0.05, "
            "bootstrap 95% CI lower > 0, and pooled PBO < 0.5; else NO-GO."
        ),
        "floor": {
            "min_surface_snapshots_per_underlying": MIN_SNAPSHOTS,
            "min_bars_per_underlying": MIN_BARS,
            "min_instruments_per_underlying": MIN_INSTRUMENTS,
            "min_option_trades_per_underlying": MIN_TRADES,
            "min_span_seconds_per_underlying": MIN_SPAN_SECONDS,
            "min_common_bars_per_underlying": MIN_COMMON_BARS,
            "min_underlyings": MIN_UNDERLYINGS,
        },
    }


def run_eval52(
    *,
    capture_dir: str = "data/raw/eval52",
    write: bool = True,
    task_label: str = "EVAL-52-SYNCHRONIZED-OPTIONS-SURFACE-X-OPTIONS-ORDERFLOW-FUSION",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _capture_inventory(str(capture_dir_abs))

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    surface_by_inst: Dict[str, List[Tuple[int, float]]] = {}
    for c in captures:
        inst = c.get("underlying", "?")
        fl = _underlying_floor(c)
        per_underlying_floor[inst] = fl
        try:
            surface_by_inst[inst] = surface_signal_series(
                c, c.get("perp_candles", []) or []
            )
        except Exception:  # noqa: BLE001
            surface_by_inst[inst] = []

    floor_ok = bool(
        len(captures) >= MIN_UNDERLYINGS
        and per_underlying_floor
        and all(v["ok"] for v in per_underlying_floor.values())
    )

    per_config: List[Dict[str, Any]] = []
    returns_by_config: Dict[str, List[float]] = {}
    errors: List[str] = []
    for cap in captures:
        inst = cap.get("underlying", "?")
        surf = surface_by_inst.get(inst, [])
        for fusion in FUSION_RULES:
            for sig in OF_SIGNALS:
                for bar_s in GRID_BAR_SECONDS:
                    try:
                        res = evaluate_config(
                            cap, surf, fusion=fusion, of_signal=sig, bar_seconds=bar_s
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(f"{inst}::{fusion}::{sig}::bar{bar_s}: {exc!r}")
                        continue
                    per_config.append(res)
                    if res.get("n_returns", 0) > 0:
                        bars = build_bars(cap, surf, bar_s)
                        pos = FUSION_FUNCS[fusion](
                            [b["surface"] for b in bars], [b[sig] for b in bars]
                        )
                        returns_by_config[
                            f"{inst}::{fusion}::{sig}::bar{bar_s}"
                        ] = strategy_returns(bars, pos)["returns"]

    pbo = _cscv_pbo(returns_by_config, n_combinations=PBO_N_COMBINATIONS,
                    k_folds=PBO_K_FOLDS, seed=SEED) if len(returns_by_config) >= 2 else {
                    "overall_pbo": 0.0, "note": "insufficient configs"}
    p_values = {
        f"{r['underlying']}::{r['fusion']}::{r['signal']}::bar{r['bar_seconds']}": _finite(
            r.get("permutation_p"), 1.0
        )
        for r in per_config if r.get("n_returns", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}

    by_inst: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_inst.setdefault(r["underlying"], []).append(r)
    inst_summary: List[Dict[str, Any]] = []
    for inst, rows in by_inst.items():
        best = max(rows, key=lambda r: _finite(r.get("sharpe"), -1e9))
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_sharpe": _finite(best.get("sharpe"), 0.0),
            "best_config": f"{best['fusion']}::{best['signal']}::bar{best['bar_seconds']}",
            "any_pass": bool(any(r.get("pass") for r in rows)),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    pooled_pbo = _finite(pbo.get("overall_pbo"), 0.0)
    go = bool(floor_ok and all_pass and pooled_pbo < 0.5)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = "EVAL_52_OPTIONS_SURFACE_ORDERFLOW" if floor_ok else "EVAL_52_BLOCKED_FLOOR"

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "real Deribit options surface x options-venue order flow net-of-cost falsification"
            if floor_ok else "capture below heavy-work floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(per_underlying_floor),
        "floor": build_protocol(capture_dir)["floor"],
        "per_underlying_floor": per_underlying_floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_underlying": inst_summary,
        "pooled": {
            "overall_pbo": pooled_pbo,
            "bh_fdr": bh,
            "all_underlyings_pass": all_pass,
            "campaign_state": campaign_state,
        },
        "errors": errors,
    }

    if not write:
        return report

    prereg = build_prereg(report)
    _seal(PREREG_ID, prereg, build_prereg_md)

    if not floor_ok:
        _seal(BLOCKED_ID, _build_blocked_report(report), build_blocked_md)
        return report

    _seal(REPORT_ID, report, build_md)
    return report


def build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    p = report["protocol"]
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report["generated_at"],
        "task": report["task"],
        "hypothesis": (
            "The fused options-surface x options-venue-order-flow strategy is net-of-cost "
            "tradable for the underlying BTC/ETH perpetual on real, synchronized Deribit data."
        ),
        "protocol": p,
        "capture_dir": report["capture_dir"],
    }


def build_prereg_md(p: Dict[str, Any]) -> str:
    proto = p["protocol"]
    lines = [
        f"# {p['prereg_id']} — EVAL-52 options surface x options order-flow net-of-cost falsification",
        "",
        f"- Generated: `{p['generated_at']}`",
        f"- Task: `{p['task']}`",
        f"- Hypothesis: {p['hypothesis']}",
        f"- Capture dir: `{p['capture_dir']}`",
        "",
        "## Pre-declared protocol",
        "",
        f"- Surface components: {proto['surface_components']}",
        f"- Surface signal: {proto['surface_signal']}",
        f"- Order-flow signals: {proto['orderflow_signals']}",
        f"- Fusion rules: {proto['fusion_rules']}",
        f"- Bar grid (s): {proto['bar_seconds_grid']}",
        f"- z-window: {proto['zwindow']}; z-clamp: {proto['z_clamp']}",
        f"- Cost: {proto['cost_model']} ({proto['cost_bps']} bps)",
        f"- Stats: perm {proto['stats']['permutation_perms']} paired / "
        f"bootstrap {proto['stats']['bootstrap_resamples']} block {proto['stats']['bootstrap_block']} / "
        f"PBO k={proto['stats']['pbo_k_folds']} / BH-FDR alpha {proto['stats']['fdr_alpha']} / "
        f"seed {proto['stats']['seed']}",
        f"- Kill-switch max-DD: {proto['kill_switch_max_dd']}",
        "",
        "## Pre-declared GO bar",
        "",
        proto["go_bar"],
        "",
        "## Heavy-work floor (must be met to seal a verdict)",
        "",
        f"- min surface snapshots/underlying: {proto['floor']['min_surface_snapshots_per_underlying']}",
        f"- min bars/underlying: {proto['floor']['min_bars_per_underlying']}",
        f"- min instruments/underlying: {proto['floor']['min_instruments_per_underlying']}",
        f"- min option trades/underlying: {proto['floor']['min_option_trades_per_underlying']}",
        f"- min span seconds/underlying: {proto['floor']['min_span_seconds_per_underlying']}",
        f"- min common 5m bars/underlying: {proto['floor']['min_common_bars_per_underlying']}",
        f"- min underlyings: {proto['floor']['min_underlyings']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — Real Deribit options surface x options order flow net-of-cost falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying floor",
        "",
        "| underlying | snaps | surf inst | 5m bars | trades | of inst | span s | common 5m | ok |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(
            f"| {inst} | {fl['n_surface_snapshots']} | {fl['n_surface_instruments']} | "
            f"{fl['n_surface_bars_5m']} | {fl['n_option_trades']} | {fl['n_of_instruments']} | "
            f"{fl['of_span_seconds']:.0f} | {fl['n_common_bars_5m']} | {fl['ok']} |"
        )
    lines += ["", "## Per-underlying (best config)", "",
              "| underlying | configs | best Sharpe | best config | any pass |",
              "|---|---|---|---|---|"]
    for s in r["per_underlying"]:
        lines.append(
            f"| {s['underlying']} | {s['n_configs']} | {s['best_sharpe']:.4f} | "
            f"{s['best_config']} | {s['any_pass']} |"
        )
    lines += ["", "## Pooled", "",
              f"- Overall PBO: {r['pooled']['overall_pbo']:.4f}",
              f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}",
              f"- All underlyings pass: {r['pooled']['all_underlyings_pass']}"]
    if r["errors"]:
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {BLOCKED_ID} — options surface x options order flow net-of-cost (below heavy-work floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Floor met: {r['floor_ok']}",
        "",
        "The capture does not meet the pre-registered heavy-work floor, so no",
        "GO/NO-GO verdict is emitted. A wider/longer synchronized real Deribit",
        "capture is required.",
        "",
        "## Per-underlying floor",
        "",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(f"- {inst}: {json.dumps(fl['checks'])}")
    lines.append("")
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r["generated_at"],
        "task": r["task"],
        "verdict": "BLOCKED",
        "capture_dir": r["capture_dir"],
        "underlyings": r["underlyings"],
        "per_underlying_floor": r["per_underlying_floor"],
        "floor": r["floor"],
        "floor_ok": r["floor_ok"],
    }


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, default=str))


def _seal(report_id: str, report: Dict[str, Any], md_builder=None) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp_for_filename(report.get("generated_at") or _utc_now_iso())
    written: Dict[str, str] = {}
    j = OUT_DIR / f"{report_id}_{stamp}.json"
    _write_json(j, report)
    written["json"] = str(j)
    if md_builder is not None:
        m = OUT_DIR / f"{report_id}_{stamp}.md"
        m.write_text(md_builder(report), encoding="utf-8")
        written["md"] = str(m)
    return written


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-52 real Deribit options surface x options order flow net-of-cost falsification"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval52")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--task-label",
                    default="EVAL-52-SYNCHRONIZED-OPTIONS-SURFACE-X-OPTIONS-ORDERFLOW-FUSION")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval52(
            capture_dir=args.capture_dir, write=write, task_label=args.task_label
        )
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": _utc_now_iso(),
                "task": args.task_label,
                "verdict": "BLOCKED",
                "capture_dir": args.capture_dir,
                "underlyings": [],
                "per_underlying_floor": {},
                "floor": build_protocol(args.capture_dir)["floor"],
                "floor_ok": False,
                "error": repr(exc),
            })
            _seal(BLOCKED_ID, blocked, build_blocked_md)
        return 1

    print(json.dumps({
        "verdict": report.get("verdict"),
        "floor_ok": report.get("floor_ok"),
        "underlyings": report.get("underlyings"),
        "per_underlying_floor": report.get("per_underlying_floor"),
        "per_underlying": report.get("per_underlying"),
        "overall_pbo": report.get("pooled", {}).get("overall_pbo"),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())