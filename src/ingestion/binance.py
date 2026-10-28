"""Binance ingestion (public REST)."""
from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

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


INSTRUMENT_RE = re.compile(r"^([A-Z]+)-(\d{6}|\d{8})-(\d+(?:\.\d+)?)-([CP])$")


def _parse_binance_symbol(symbol: str) -> Optional[Dict[str, Any]]:
    # Binance option symbols vary; try to parse common forms
    m = INSTRUMENT_RE.match(symbol)
    if not m:
        # Try BTCUSDT-YYMMDD-...
        m2 = re.match(r"^([A-Z]+)USDT?-([0-9]{6,8})-(\d+(?:\.\d+)?)-([CP])", symbol)
        if m2:
            underlying = m2.group(1)
            expiry_str = m2.group(2)
            strike_str = m2.group(3)
            opt_type_char = m2.group(4)
        else:
            return None
    else:
        underlying = m.group(1)
        expiry_str = m.group(2)
        strike_str = m.group(3)
        opt_type_char = m.group(4)

    strike = float(strike_str)
    option_type = "call" if opt_type_char == "C" else "put"
    expiry_dt = None
    try:
        if len(expiry_str) == 8:
            expiry_dt = datetime.strptime(expiry_str, "%Y%m%d").replace(tzinfo=timezone.utc)
        elif len(expiry_str) == 6:
            expiry_dt = datetime.strptime(expiry_str, "%y%m%d").replace(tzinfo=timezone.utc)
        else:
            return None
    except Exception:
        return None
    return {
        "underlying": underlying,
        "expiry": expiry_dt,
        "strike": strike,
        "option_type": option_type,
        "symbol": symbol,
    }


class BinanceClient:
    BASE_URL = "https://eapi.binance.com"

    def __init__(self, session: Optional[requests.Session] = None, timeout: float = 10.0, max_retries: int = 3):
        self.session = session or requests.Session()
        self.timeout = timeout
        self.max_retries = max_retries

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.BASE_URL}{endpoint}"
        last_exc = None
        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                resp.raise_for_status()
                data = resp.json()
                return data
            except Exception as exc:
                last_exc = exc
                time.sleep(0.2 * (attempt + 1))
        if last_exc:
            raise last_exc
        raise RuntimeError("Unknown Binance API error")

    def exchange_info(self) -> Dict[str, Any]:
        data = self._get("/eapi/v1/exchangeInfo")
        if isinstance(data, dict):
            return data
        return {}

    def ticker(self, symbol: Optional[str] = None) -> Any:
        params = {"symbol": symbol} if symbol else {}
        data = self._get("/eapi/v1/ticker", params=params)
        return data

    def trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        data = self._get("/eapi/v1/trades", {"symbol": symbol, "limit": limit})
        if isinstance(data, list):
            return data
        return []


class BinanceOptionsIngestion(BaseOptionsIngestion):
    def __init__(self, client: Optional[BinanceClient] = None):
        super().__init__("binance")
        self.client = client or BinanceClient()

    def fetch_available_expiries(self, underlying: str) -> List[datetime]:
        try:
            info = self.client.exchange_info()
        except Exception:
            return []
        expiries = set()
        option_symbols = info.get("optionSymbols") if isinstance(info, dict) else None
        if isinstance(option_symbols, list):
            for s in option_symbols:
                sym = s.get("symbol") if isinstance(s, dict) else str(s)
                parsed = _parse_binance_symbol(sym)
                if parsed and parsed["underlying"] == underlying.upper():
                    expiries.add(parsed["expiry"])
        return sorted(list(expiries))

    def fetch_options_chain(self, underlying: str) -> OptionsChain:
        quotes: List[OptionQuote] = []
        try:
            info = self.client.exchange_info()
        except Exception:
            return OptionsChain(underlying=underlying, venue=self.venue, quotes=[], timestamp=datetime.now(timezone.utc))

        try:
            tickers = self.client.ticker()
            if isinstance(tickers, dict):
                ticker_list = [tickers]
            elif isinstance(tickers, list):
                ticker_list = tickers
            else:
                ticker_list = []
            ticker_map = {}
            for t in ticker_list:
                if isinstance(t, dict):
                    sym = t.get("symbol")
                    if sym:
                        ticker_map[sym] = t
        except Exception:
            ticker_map = {}

        option_symbols = info.get("optionSymbols") if isinstance(info, dict) else []
        if not isinstance(option_symbols, list):
            return OptionsChain(underlying=underlying, venue=self.venue, quotes=[], timestamp=datetime.now(timezone.utc))

        for s in option_symbols:
            if not isinstance(s, dict):
                continue
            sym = s.get("symbol") or ""
            parsed = _parse_binance_symbol(sym)
            if not parsed or parsed["underlying"] != underlying.upper():
                continue
            contract = OptionContract(
                symbol=sym,
                underlying=underlying.upper(),
                strike=float(parsed["strike"]),
                expiry=parsed["expiry"],
                option_type=parsed["option_type"],
                venue=self.venue,
                contract_size=float(s.get("contractSize", 1.0) or 1.0),
            )
            ticker = ticker_map.get(sym, {}) or {}
            bid = ticker.get("bidPrice") or ticker.get("bid")
            ask = ticker.get("askPrice") or ticker.get("ask")
            last = ticker.get("lastPrice") or ticker.get("last")
            mark = ticker.get("markPrice")
            bid_iv = ticker.get("bidIV")
            ask_iv = ticker.get("askIV")
            mark_iv = ticker.get("markIV")
            delta = ticker.get("delta")
            gamma = ticker.get("gamma")
            theta = ticker.get("theta")
            vega = ticker.get("vega")
            open_interest = ticker.get("openInterest") or ticker.get("oi")
            volume = ticker.get("volume") or ticker.get("sumVolume")

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

        return OptionsChain(underlying=underlying.upper(), venue=self.venue, quotes=quotes, timestamp=datetime.now(timezone.utc))


class BinanceOrderflowIngestion(BaseOrderflowIngestion):
    def __init__(self, client: Optional[BinanceClient] = None):
        super().__init__("binance")
        self.client = client or BinanceClient()

    def fetch_trades(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        trades: List[Trade] = []
        try:
            raw_trades = self.client.trades(symbol, limit=min(limit, 1000))
        except Exception:
            return OrderflowSnapshot(symbol=symbol, venue=self.venue, trades=[], timestamp=datetime.now(timezone.utc))
        for idx, t in enumerate(raw_trades):
            try:
                px = t.get("price") or t.get("p")
                sz = t.get("qty") or t.get("amount") or t.get("q")
                side = t.get("side")
                if side is None and "buyerMaker" in t:
                    side = "sell" if t.get("buyerMaker") else "buy"
                trade_id = t.get("id") or t.get("tradeId") or f"{symbol}-{idx}"
                ts = t.get("time") or t.get("T")
                if ts:
                    try:
                        # ms
                        ts_val = int(ts)
                        if ts_val > 10**12:
                            ts_dt = datetime.fromtimestamp(ts_val / 1000.0, tz=timezone.utc)
                        else:
                            ts_dt = datetime.fromtimestamp(ts_val, tz=timezone.utc)
                    except Exception:
                        ts_dt = datetime.now(timezone.utc)
                else:
                    ts_dt = datetime.now(timezone.utc)
                trades.append(
                    Trade(
                        trade_id=str(trade_id),
                        symbol=symbol,
                        venue=self.venue,
                        price=float(px) if px is not None else 0.0,
                        size=float(sz) if sz is not None else 0.0,
                        side="buy" if str(side).lower() in ("buy", "b") else "sell",
                        timestamp=ts_dt,
                    )
                )
            except Exception:
                continue
        return OrderflowSnapshot(symbol=symbol, venue=self.venue, trades=trades, timestamp=datetime.now(timezone.utc))

    def fetch_liquidations(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        return OrderflowSnapshot(symbol=symbol, venue=self.venue, liquidations=[], timestamp=datetime.now(timezone.utc))
