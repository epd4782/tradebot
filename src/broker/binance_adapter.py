from future import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import Dict, Optional

import ccxt
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import get_settings

logger = logging.getLogger(name)

@dataclass
class OrderResponse:
id: str
status: str
symbol: str
side: str
price: float
amount: float

def _client() -> ccxt.binance:
settings = get_settings()
exchange = ccxt.binance(
{
"apiKey": settings.binance_api_key,
"secret": settings.binance_api_secret,
"enableRateLimit": True,
"options": {"defaultType": "spot"},
"timeout": 20000,
}
)
if settings.binance_testnet:
exchange.set_sandbox_mode(True)
exchange.load_markets()
return exchange

def _round(exchange: ccxt.binance, symbol: str, amount: float, price: Optional[float]):
rounded_amount = float(exchange.amount_to_precision(symbol, amount))
rounded_price = float(exchange.price_to_precision(symbol, price)) if price is not None else None
return rounded_amount, rounded_price

def _order_id() -> str:
return f"bot-{uuid.uuid4().hex[:16]}"

class BinanceAdapter:
def init(self, settings=None):
self.settings = settings or get_settings()
self.exchange = _client()

@retry(reraise=True, stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
def get_balance(self) -> Dict[str, float]:
    balance = self.exchange.fetch_balance()
    return {k: float(v["free"]) for k, v in balance.get("free", {}).items()}

@retry(reraise=True, stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
def fetch_ohlcv(self, symbol: str, timeframe: str, since: Optional[int] = None, limit: int = 500):
    return self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)

@retry(reraise=True, stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
def create_order(
    self,
    symbol: str,
    side: str,
    amount: float,
    price: Optional[float] = None,
    order_type: str = "limit",
) -> Dict:
    rounded_amount, rounded_price = _round(self.exchange, symbol, amount, price)
    logger.info(
        "Creating order %s %s amount=%sâ†’%s price=%sâ†’%s",
        side,
        symbol,
        amount,
        rounded_amount,
        price,
        rounded_price,
    )
    order = self.exchange.create_order(
        symbol,
        order_type,
        side,
        rounded_amount,
        rounded_price,
        params={"newClientOrderId": _order_id()},
    )
    return order
all = ["BinanceAdapter", "OrderResponse"]