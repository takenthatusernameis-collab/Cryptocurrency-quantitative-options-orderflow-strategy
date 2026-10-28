"""Deribit options and orderflow ingestion."""
from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, cast

import requests

from ..data.schemas import (
    Liquidation,
    OptionContract,
    OptionQuote,
    OptionsChain,
    OrderflowSnapshot,
    Trade,
)
from .base import BaseOptionsIngestion, BaseOrderflowIngestion


INSTRUMENT_RE = re.compile(r"^([A-Z]+)-(\d{1,2}[A-Z]{3}\d{2}|\d{8})-(\d+(?:\.\d+)?)-([CP])$")


def _parse_deribit_instrument(instrument_name: str) -> Optional[Dict[str, Any]]:
    m = INSTRUMENT_RE.match(instrument_name)
    if not m:
        return None
    underlying = m.group(1)
    expiry_str = m.group(2)
    strike_str = m.group(3)
    opt_type_char = m.group(4)
    strike = float(strike_str)
    option_type = "call" if opt_type_char == "C" else "put"

    expiry_dt = None
    try:
        if re.match(r"^\d{8}$", expiry_str):
            # YYYYMMDD
            expiry_dt = datetime.strptime(expiry_str, "%Y%m%d").replace(tzinfo=timezone.utc)
        else:
            # e.g. 30DEC22
            expiry_dt = datetime.strptime(expiry_str, "%d%b%y").replace(tzinfo=timezone.utc)
    except Exception:
        return None
    return {
        "underlying": underlying,
        "expiry": expiry_dt,
        "strike": strike,
        "option_type": option_type,
        "instrument_name": instrument_name,
    }


class DeribitClient:
    BASE_URL = "https://www.deribit.com/api/v2"

    def __init__(self, session: Optional[requests.Session] = None, timeout: float = 10.0, max_retries: int = 3) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout
        self.max_retries = max_retries

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        last_exc = None
        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, dict) and data.get("error"):
                    raise RuntimeError(f"Deribit API error: {data['error']}")
                return cast(Dict[str, Any], data)
            except Exception as exc:
                last_exc = exc
                time.sleep(0.2 * (attempt + 1))
        if last_exc:
            raise last_exc
        raise RuntimeError("Unknown Deribit API error")

    def get_instruments(self, currency: str, kind: str = "option", expired: bool = False) -> List[Dict[str, Any]]:
        data = self._get("/public/get_instruments", {"currency": currency, "kind": kind, "expired": str(expired).lower()})
        result = data.get("result") if isinstance(data, dict) else None
        if isinstance(result, list):
            return result
        return []

    def get_order_book(self, instrument_name: str, depth: int = 1) -> Dict[str, Any]:
        data = self._get("/public/get_order_book", {"instrument_name": instrument_name, "depth": depth})
        result = data.get("result") if isinstance(data, dict) else None
        if isinstance(result, dict):
            return result
        return {}

    def get_ticker(self, instrument_name: str) -> Dict[str, Any]:
        data = self._get("/public/ticker", {"instrument_name": instrument_name})
        result = data.get("result") if isinstance(data, dict) else None
        if isinstance(result, dict):
            return result
        return {}

    def get_last_trades_by_instrument(self, instrument_name: str, count: int = 100) -> List[Dict[str, Any]]:
        data = self._get("/public/get_last_trades_by_instrument", {"instrument_name": instrument_name, "count": count})
        result = data.get("result") if isinstance(data, dict) else None
        if isinstance(result, dict):
            trades = result.get("trades")
            if isinstance(trades, list):
                return trades
            return []
        if isinstance(result, list):
            return result
        return []


class DeribitOptionsIngestion(BaseOptionsIngestion):
    def __init__(self, client: Optional[DeribitClient] = None) -> None:
        super().__init__("deribit")
        self.client = client or DeribitClient()

    def fetch_available_expiries(self, underlying: str) -> List[datetime]:
        try:
            instruments = self.client.get_instruments(underlying, kind="option", expired=False)
        except Exception:
            return []
        expiries = set()
        for inst in instruments:
            name = inst.get("instrument_name") or inst.get("instrument") or ""
            parsed = _parse_deribit_instrument(name)
            if parsed and parsed["underlying"] == underlying:
                expiries.add(parsed["expiry"])
        return sorted(list(expiries))

    def fetch_options_chain(self, underlying: str) -> OptionsChain:
        quotes: List[OptionQuote] = []
        try:
            instruments = self.client.get_instruments(underlying, kind="option", expired=False)
        except Exception:
            return OptionsChain(underlying=underlying, venue=self.venue, quotes=[], timestamp=datetime.now(timezone.utc))

        for inst in instruments:
            name = inst.get("instrument_name") or inst.get("instrument") or ""
            parsed = _parse_deribit_instrument(name)
            if not parsed or parsed["underlying"] != underlying:
                continue
            contract = OptionContract(
                symbol=name,
                underlying=underlying,
                strike=float(parsed["strike"]),
                expiry=parsed["expiry"],
                option_type=parsed["option_type"],
                venue=self.venue,
                contract_size=float(inst.get("contract_size", 1.0) or 1.0),
            )
            ticker = {}
            try:
                ticker = self.client.get_ticker(name)
            except Exception:
                ticker = {}
            bid = ticker.get("best_bid_price") if isinstance(ticker, dict) else None
            ask = ticker.get("best_ask_price") if isinstance(ticker, dict) else None
            last = ticker.get("last_price") if isinstance(ticker, dict) else None
            mark = ticker.get("mark_price") if isinstance(ticker, dict) else None
            bid_iv = ticker.get("bid_iv") if isinstance(ticker, dict) else None
            ask_iv = ticker.get("ask_iv") if isinstance(ticker, dict) else None
            mark_iv = ticker.get("mark_iv") if isinstance(ticker, dict) else None
            greeks = ticker.get("greeks") if isinstance(ticker, dict) else {}
            delta = greeks.get("delta") if isinstance(greeks, dict) else ticker.get("delta")
            gamma = greeks.get("gamma") if isinstance(greeks, dict) else ticker.get("gamma")
            theta = greeks.get("theta") if isinstance(greeks, dict) else ticker.get("theta")
            vega = greeks.get("vega") if isinstance(greeks, dict) else ticker.get("vega")
            open_interest = ticker.get("open_interest") if isinstance(ticker, dict) else None
            volume = ticker.get("stats", {}).get("volume") if isinstance(ticker.get("stats"), dict) else ticker.get("volume")

            try:
                quote = OptionQuote(
                    contract=contract,
                    bid=float(bid) if bid is not None else 0.0,
                    ask=float(ask) if ask is not None else 0.0,
                    last=float(last) if last is not None else None,
                    mark=float(mark) if mark is not None else None,
                    bid_iv=float(bid_iv) if bid_iv is not None else None,
                    ask_iv=float(ask_iv) if ask_iv is not None else None,
                    mark_iv=float(mark_iv) if mark_iv is not None else None,
                    delta=float(delta) if delta is not None else None,
                    gamma=float(gamma) if gamma is not None else None,
                    theta=float(theta) if theta is not None else None,
                    vega=float(vega) if vega is not None else None,
                    open_interest=float(open_interest) if open_interest is not None else 0.0,
                    volume=float(volume) if volume is not None else 0.0,
                    timestamp=datetime.now(timezone.utc),
                )
                quotes.append(quote)
            except Exception:
                continue

        return OptionsChain(underlying=underlying, venue=self.venue, quotes=quotes, timestamp=datetime.now(timezone.utc))


class DeribitOrderflowIngestion(BaseOrderflowIngestion):
    def __init__(self, client: Optional[DeribitClient] = None) -> None:
        super().__init__("deribit")
        self.client = client or DeribitClient()

    def fetch_trades(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        trades: List[Trade] = []
        try:
            raw_trades = self.client.get_last_trades_by_instrument(symbol, count=min(limit, 1000))
        except Exception:
            raw_trades = []
        for t in raw_trades:
            try:
                trade_id = str(t.get("trade_id") or t.get("id") or "")
                price = float(t.get("price") or 0.0)
                size = float(t.get("amount") or t.get("quantity") or t.get("size") or 0.0)
                direction = t.get("direction") or t.get("side") or ""
                side = "buy" if str(direction).lower() in ("buy", "long") else "sell"
                ts = t.get("timestamp")
                if isinstance(ts, (int, float)):
                    # ms
                    if ts > 1e12:
                        dt = datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc)
                    else:
                        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                elif isinstance(ts, str):
                    try:
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    except Exception:
                        dt = datetime.now(timezone.utc)
                else:
                    dt = datetime.now(timezone.utc)
                trades.append(
                    Trade(
                        trade_id=trade_id or f"deribit-{int(time.time()*1000)}",
                        symbol=symbol,
                        venue=self.venue,
                        price=price,
                        size=size,
                        side=side,
                        timestamp=dt,
                    )
                )
            except Exception:
                continue
        return OrderflowSnapshot(symbol=symbol, venue=self.venue, trades=trades, timestamp=datetime.now(timezone.utc))

    def fetch_liquidations(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        # Deribit public liquidation data is available via some streams; as fallback, return empty normalized snapshot
        # but structure is correct for integration
        return OrderflowSnapshot(
            symbol=symbol,
            venue=self.venue,
            trades=[],
            liquidations=[],
            funding_rates=[],
            timestamp=datetime.now(timezone.utc),
        )
