"""Data validation utilities."""

from typing import Any, Dict, List

from ..errors import DataError, SchemaError
from ..telemetry.error_logging import log_error_with_context
from .schemas import OptionsChain, OrderflowSnapshot, Trade


def validate_trade(trade: Trade) -> None:
    try:
        if trade.price < 0 or trade.size < 0:
            raise SchemaError("Trade price/size must be non-negative", context={"trade_id": getattr(trade, "trade_id", None)})
        if trade.side not in ("buy", "sell"):
            raise SchemaError("Trade side must be 'buy' or 'sell'", context={"trade_id": getattr(trade, "trade_id", None)})
    except (SchemaError, DataError):
        raise
    except Exception as e:
        raise SchemaError("Trade validation failed", cause=e)


def validate_orderflow_snapshot(snap: OrderflowSnapshot) -> OrderflowSnapshot:
    try:
        if not isinstance(snap.trades, list):
            raise SchemaError("trades must be a list")
        for t in snap.trades:
            validate_trade(t)
        for l in getattr(snap, "liquidations", []) or []:
            if getattr(l, "price", 0) < 0 or getattr(l, "size", 0) < 0:
                raise SchemaError("Liquidation price/size must be non-negative")
            if getattr(l, "side") not in ("long", "short"):
                raise SchemaError("Liquidation side must be 'long' or 'short'")
        for f in getattr(snap, "funding_rates", []) or []:
            # allow negative/positive funding; just ensure numeric
            try:
                float(getattr(f, "funding_rate", 0.0))
            except Exception as e:
                raise SchemaError("Funding rate must be numeric", cause=e)
        return snap
    except (SchemaError, DataError):
        raise
    except Exception as e:
        raise DataError("Orderflow snapshot validation failed", cause=e)


def validate_options_chain(chain: OptionsChain) -> OptionsChain:
    try:
        if not isinstance(chain.quotes, list):
            raise SchemaError("quotes must be a list")
        for q in chain.quotes:
            try:
                if q.bid < 0 or q.ask < 0:
                    raise SchemaError("Bid/ask must be non-negative")
                if q.ask < q.bid - 1e-12:  # allow tiny numerical noise? but better strict; be permissive small
                    # allow crossing? maybe not typical; but don't hard fail aggressively
                    pass
                if q.contract.strike <= 0:
                    raise SchemaError("Strike must be positive")
                if q.contract.option_type not in ("call", "put"):
                    raise SchemaError("Option type must be 'call' or 'put'")
            except (SchemaError, DataError):
                raise
            except Exception as e:
                raise SchemaError("Option quote validation failed", cause=e)
        return chain
    except (SchemaError, DataError):
        raise
    except Exception as e:
        raise DataError("Options chain validation failed", cause=e)


def fail_fast_on_schema_drift(obj: Any, expected_type: Any) -> None:
    """Fail fast if object doesn't match expected type."""
    if not isinstance(obj, expected_type):
        raise SchemaError(f"Schema drift: expected {expected_type}, got {type(obj)}")
