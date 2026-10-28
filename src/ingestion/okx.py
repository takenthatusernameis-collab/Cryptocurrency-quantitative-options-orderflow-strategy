"""OKX ingestion (public REST)."""
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


INSTRUMENT_RE = re.compile(r"^([A-Z0-9]+)-([A-Z0-9]+)-(\d{6}|\d{8})-(\d+(?:\.\d+)?)-([CP])$")


def _parse_okx_instrument(inst_id: str) -> Optional[Dict[str, Any]]:
    m = INSTRUMENT_RE.match(inst_id)
    if not m:
        # Try alternative format
        return None
    underlying = m.group(1)
    # settle/quote currency often group2, ignore for underlying
    expiry_str = m.group(3)
    strike_str = m.group(4)
    opt_type_char = m.group(5)
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
        "instrument_name": inst_id,
    }


class OKXClient:
    """Thin REST client for the OKX public API (v5).

    Wraps a :class:`requests.Session` with retry/backoff on transient errors.
    Validates the top-level ``code`` field (``"0"`` or ``"00000"`` indicates
    success) and raises a :class:`RuntimeError` carrying the API message on
    failure, or the last observed exception after ``max_retries`` attempts.
    All methods are public (no authentication).
    """

    BASE_URL = "https://www.okx.com"

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
                if isinstance(data, dict) and str(data.get("code")) not in ("0", "00000"):
                    raise RuntimeError(f"OKX API error: {data.get('code')} {data.get('msg')}")
                return cast(Dict[str, Any], data)
            except Exception as exc:
                last_exc = exc
                time.sleep(0.2 * (attempt + 1))
        if last_exc:
            raise last_exc
        raise RuntimeError("Unknown OKX API error")

    def get_instruments(self, uly: str, inst_type: str = "OPTION") -> List[Dict[str, Any]]:
        data = self._get("/api/v5/public/instruments", {"instType": inst_type, "uly": uly})
        result = data.get("data") if isinstance(data, dict) else None
        if isinstance(result, list):
            return result
        return []

    def get_tickers(self, uly: str, inst_type: str = "OPTION") -> List[Dict[str, Any]]:
        data = self._get("/api/v5/market/tickers", {"instType": inst_type, "uly": uly})
        result = data.get("data") if isinstance(data, dict) else None
        if isinstance(result, list):
            return result
        return []

    def get_trades(self, inst_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        data = self._get("/api/v5/market/trades", {"instId": inst_id, "limit": str(limit)})
        result = data.get("data") if isinstance(data, dict) else None
        if isinstance(result, list):
            return result
        return []


class OKXOptionsIngestion(BaseOptionsIngestion):
    """OKX options-chain ingestion via the public ``instruments``/``tickers`` endpoints.

    Builds :class:`OptionQuote` objects from instrument metadata and per-instrument
    tickers. Instrument IDs are parsed via :func:`_parse_okx_instrument`,
    supporting the ``BTC-USD-241227-50000-C`` style format. On any top-level
    API failure, returns an empty chain with the current timestamp.
    """

    def __init__(self, client: Optional[OKXClient] = None) -> None:
        super().__init__("okx")
        self.client = client or OKXClient()

    def fetch_available_expiries(self, underlying: str) -> List[datetime]:
        uly = f"{underlying}-USD"
        try:
            instruments = self.client.get_instruments(uly, inst_type="OPTION")
        except Exception:
            return []
        expiries = set()
        for inst in instruments:
            inst_id = inst.get("instId") or ""
            parsed = _parse_okx_instrument(inst_id)
            if parsed and parsed["underlying"].upper() == underlying.upper():
                expiries.add(parsed["expiry"])
        return sorted(list(expiries))

    def fetch_options_chain(self, underlying: str) -> OptionsChain:
        quotes: List[OptionQuote] = []
        uly = f"{underlying}-USD"
        try:
            instruments = self.client.get_instruments(uly, inst_type="OPTION")
        except Exception:
            return OptionsChain(underlying=underlying, venue=self.venue, quotes=[], timestamp=datetime.now(timezone.utc))

        try:
            tickers = self.client.get_tickers(uly, inst_type="OPTION")
            ticker_map = {t.get("instId"): t for t in tickers if isinstance(t, dict)}
        except Exception:
            ticker_map = {}

        for inst in instruments:
            inst_id = inst.get("instId") or ""
            parsed = _parse_okx_instrument(inst_id)
            if not parsed:
                continue
            parsed_under = parsed["underlying"].upper()
            if parsed_under != underlying.upper() and parsed_under not in (underlying.upper(), f"{underlying.upper()}"):
                # try to be flexible
                pass
            contract = OptionContract(
                symbol=inst_id,
                underlying=underlying.upper(),
                strike=float(parsed["strike"]),
                expiry=parsed["expiry"],
                option_type=parsed["option_type"],
                venue=self.venue,
                contract_size=float(inst.get("ctVal", 1.0) or inst.get("contractVal", 1.0) or 1.0),
            )
            ticker = ticker_map.get(inst_id, {}) or {}
            bid = ticker.get("bidPx") or ticker.get("bid")
            ask = ticker.get("askPx") or ticker.get("ask")
            last = ticker.get("last") or ticker.get("lastPx")
            mark = ticker.get("markPx") or ticker.get("idxPx")
            bid_iv = ticker.get("bidVol") or ticker.get("bidIv")
            ask_iv = ticker.get("askVol") or ticker.get("askIv")
            mark_iv = ticker.get("markVol") or ticker.get("markIv")
            delta = ticker.get("delta")
            gamma = ticker.get("gamma")
            theta = ticker.get("theta")
            vega = ticker.get("vega")
            open_interest = ticker.get("oi") or ticker.get("openInterest")
            volume = ticker.get("vol24h") or ticker.get("volCcy24h") or ticker.get("volume")

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


class OKXOrderflowIngestion(BaseOrderflowIngestion):
    """OKX orderflow ingestion via the public ``trades`` endpoint.

    Fetches recent trades and normalizes them into an
    :class:`OrderflowSnapshot`. Side classification maps the OKX ``side``
    field (``'buy'``/``'sell'``) directly. Liquidations are not exposed by
    this public client and return an empty list. On API failure, returns an
    empty snapshot with the current timestamp.
    """

    def __init__(self, client: Optional[OKXClient] = None) -> None:
        super().__init__("okx")
        self.client = client or OKXClient()

    def fetch_trades(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        trades: List[Trade] = []
        inst_id = symbol if "-" in symbol and len(symbol) > 10 else f"{symbol}-USDT-SWAP" if "SWAP" not in symbol else symbol
        # For options, inst_id is full contract; try as-is
        try:
            raw_trades = self.client.get_trades(inst_id, limit=min(limit, 100))
        except Exception:
            return OrderflowSnapshot(symbol=symbol, venue=self.venue, trades=[], timestamp=datetime.now(timezone.utc))
        for idx, t in enumerate(raw_trades):
            try:
                px = t.get("px")
                sz = t.get("sz")
                side = t.get("side")  # buy/sell
                trade_id = t.get("tradeId") or f"{inst_id}-{idx}"
                ts = t.get("ts")
                if ts:
                    try:
                        ts_dt = datetime.fromtimestamp(int(ts) / 1000.0, tz=timezone.utc)
                    except Exception:
                        ts_dt = datetime.now(timezone.utc)
                else:
                    ts_dt = datetime.now(timezone.utc)
                trades.append(
                    Trade(
                        trade_id=str(trade_id),
                        symbol=inst_id,
                        venue=self.venue,
                        price=float(px) if px is not None else 0.0,
                        size=float(sz) if sz is not None else 0.0,
                        side="buy" if str(side).lower() == "buy" else "sell",
                        timestamp=ts_dt,
                    )
                )
            except Exception:
                continue
        return OrderflowSnapshot(symbol=symbol, venue=self.venue, trades=trades, timestamp=datetime.now(timezone.utc))

    def fetch_liquidations(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        # OKX liquidations may require different endpoints; return empty normalized snapshot if unavailable
        return OrderflowSnapshot(symbol=symbol, venue=self.venue, liquidations=[], timestamp=datetime.now(timezone.utc))
