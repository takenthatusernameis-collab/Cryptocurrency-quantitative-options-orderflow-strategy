"""Robust data loader with normalization, validation, caching."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..errors import DataError
from ..telemetry.error_logging import log_error_with_context
from .normalization import normalize_orderflow, normalize_options_chain, normalize_symbol, normalize_timestamp
from .schemas import Liquidation, FundingRate, OptionsChain, OptionContract, OptionQuote, OrderflowSnapshot, Trade
from .validators import validate_options_chain, validate_orderflow_snapshot


_CACHE: Dict[str, Any] = {}


def _load_json(path: Union[str, Path]) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _parse_dt(ts: Any) -> datetime:
    if isinstance(ts, datetime):
        return normalize_timestamp(ts)
    if isinstance(ts, (int, float)):
        # assume seconds or ms
        val = float(ts)
        if val > 1e12:  # ms
            val = val / 1000.0
        elif val > 1e9:  # seconds
            pass
        else:
            val = float(ts)
        return datetime.fromtimestamp(val, tz=timezone.utc)
    if isinstance(ts, str):
        # try common formats
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return normalize_timestamp(dt)
        except Exception:
            pass
        try:
            # try numeric string
            v = float(ts)
            if v > 1e12:
                v = v / 1000.0
            return datetime.fromtimestamp(v, tz=timezone.utc)
        except Exception:
            pass
    return normalize_timestamp(None)


class DataLoader:
    def __init__(self, cache: bool = True):
        self.cache = cache

    def load_trades(self, path: Union[str, Path], venue: str = "unknown") -> List[Trade]:
        key = f"trades:{os.path.abspath(path)}"
        if self.cache and key in _CACHE:
            return _CACHE[key]
        data = _load_json(path)
        trades: List[Trade] = []
        for item in data:
            try:
                trade = Trade(
                    trade_id=str(item.get("trade_id") or item.get("id") or item.get("tid") or ""),
                    symbol=normalize_symbol(item.get("symbol") or item.get("instId") or item.get("instrument") or "", venue),
                    venue=venue,
                    price=float(item.get("price") or 0.0),
                    size=float(item.get("size") or item.get("qty") or item.get("amount") or 0.0),
                    side=str(item.get("side") or item.get("takerSide") or item.get("direction") or "buy").lower(),
                    timestamp=_parse_dt(item.get("timestamp") or item.get("time") or item.get("ts")),
                )
                trades.append(trade)
            except Exception as e:
                log_error_with_context(
                    "Failed to parse trade",
                    operation="load_trades",
                    module="src.data.loader",
                    extra={"path": str(path)},
                    exc=e,
                )
        if self.cache:
            _CACHE[key] = trades
        return trades

    def load_orderflow(self, path: Union[str, Path], venue: str = "unknown", symbol: str = "") -> OrderflowSnapshot:
        key = f"orderflow:{os.path.abspath(path)}"
        if self.cache and key in _CACHE:
            return _CACHE[key]
        data = _load_json(path)
        trades = []
        liquidations = []
        funding_rates = []
        # support both flat list and dict
        items = data.get("trades", []) if isinstance(data, dict) else data
        if isinstance(items, dict) and "trades" in items:
            items = items["trades"]
        for item in items if isinstance(items, list) else []:
            try:
                trades.append(
                    Trade(
                        trade_id=str(item.get("trade_id") or item.get("id") or ""),
                        symbol=normalize_symbol(item.get("symbol") or symbol or "", venue),
                        venue=venue,
                        price=float(item.get("price") or 0.0),
                        size=float(item.get("size") or item.get("qty") or 0.0),
                        side=str(item.get("side") or "buy").lower(),
                        timestamp=_parse_dt(item.get("timestamp") or item.get("time") or item.get("ts")),
                    )
                )
            except Exception as e:
                log_error_with_context(
                    "Failed to parse trade in orderflow",
                    operation="load_orderflow",
                    module="src.data.loader",
                    exc=e,
                )
        # liquidations
        liqs = data.get("liquidations", []) if isinstance(data, dict) else []
        for item in liqs:
            try:
                liquidations.append(
                    Liquidation(
                        liquidation_id=str(item.get("liquidation_id") or item.get("id") or ""),
                        symbol=normalize_symbol(item.get("symbol") or symbol or "", venue),
                        venue=venue,
                        price=float(item.get("price") or 0.0),
                        size=float(item.get("size") or 0.0),
                        side=str(item.get("side") or "long").lower(),
                        timestamp=_parse_dt(item.get("timestamp") or item.get("time") or item.get("ts")),
                    )
                )
            except Exception as e:
                log_error_with_context(
                    "Failed to parse liquidation",
                    operation="load_orderflow",
                    module="src.data.loader",
                    exc=e,
                )
        # funding
        frs = data.get("funding_rates", []) if isinstance(data, dict) else []
        for item in frs:
            try:
                funding_rates.append(
                    FundingRate(
                        symbol=normalize_symbol(item.get("symbol") or symbol or "", venue),
                        venue=venue,
                        funding_rate=float(item.get("funding_rate") or item.get("rate") or 0.0),
                        funding_time=_parse_dt(item.get("funding_time") or item.get("fundingTimestamp") or item.get("time")),
                        timestamp=_parse_dt(item.get("timestamp") or item.get("time") or item.get("ts")),
                    )
                )
            except Exception as e:
                log_error_with_context(
                    "Failed to parse funding rate",
                    operation="load_orderflow",
                    module="src.data.loader",
                    exc=e,
                )
        snap = OrderflowSnapshot(
            symbol=normalize_symbol(symbol or (trades[0].symbol if trades else ""), venue),
            venue=venue,
            trades=trades,
            liquidations=liquidations,
            funding_rates=funding_rates,
            timestamp=normalize_timestamp(datetime.now(timezone.utc)),
        )
        snap = normalize_orderflow(snap)
        validate_orderflow_snapshot(snap)
        if self.cache:
            _CACHE[key] = snap
        return snap

    def load_options_chain(self, path: Union[str, Path], venue: str = "unknown", underlying: str = "") -> OptionsChain:
        key = f"options:{os.path.abspath(path)}"
        if self.cache and key in _CACHE:
            return _CACHE[key]
        data = _load_json(path)
        quotes = []
        items = data.get("quotes", []) if isinstance(data, dict) else data
        for item in items:
            try:
                contract = OptionContract(
                    symbol=str(item.get("symbol") or item.get("instrument") or ""),
                    underlying=str(item.get("underlying") or underlying or ""),
                    strike=float(item.get("strike") or 0.0),
                    expiry=_parse_dt(item.get("expiry") or item.get("expiration")),
                    option_type=str(item.get("option_type") or item.get("type") or "call").lower(),
                    venue=venue,
                    contract_size=float(item.get("contract_size") or item.get("contractSize") or 1.0),
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
                    open_interest=float(item.get("open_interest") or item.get("oi") or 0.0),
                    volume=float(item.get("volume") or 0.0),
                    timestamp=_parse_dt(item.get("timestamp") or item.get("time") or item.get("ts")),
                )
                quotes.append(q)
            except Exception as e:
                log_error_with_context(
                    "Failed to parse option quote",
                    operation="load_options_chain",
                    module="src.data.loader",
                    exc=e,
                )
        chain = OptionsChain(
            underlying=underlying or (quotes[0].contract.underlying if quotes else ""),
            venue=venue,
            quotes=quotes,
            timestamp=normalize_timestamp(datetime.now(timezone.utc)),
        )
        chain = normalize_options_chain(chain)
        validate_options_chain(chain)
        if self.cache:
            _CACHE[key] = chain
        return chain

    def clear_cache(self):
        global _CACHE
        _CACHE = {}


def load_trades(*args, **kwargs):
    return DataLoader().load_trades(*args, **kwargs)


def load_orderflow(*args, **kwargs):
    return DataLoader().load_orderflow(*args, **kwargs)


def load_options_chain(*args, **kwargs):
    return DataLoader().load_options_chain(*args, **kwargs)
