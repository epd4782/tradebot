import sys
from types import SimpleNamespace
from pathlib import Path

sys.path.insert(0, str(Path(file).resolve().parents[1]))
from src.broker import binance_adapter

class DummyClient:
def init(self):
self.amount_precision = []
self.price_precision = []
self.last_order = None

def amount_to_precision(self, symbol, amount):
    self.amount_precision.append((symbol, amount))
    return "0.0100"

def price_to_precision(self, symbol, price):
    self.price_precision.append((symbol, price))
    return "30000.10"

def create_order(self, symbol, order_type, side, amount, price, params):
    self.last_order = {
        "symbol": symbol,
        "type": order_type,
        "side": side,
        "amount": amount,
        "price": price,
        "params": params,
    }
    return self.last_order

def fetch_time(self):
    return 0

def load_markets(self):
    return {}

def check_required_credentials(self):
    return True
def test_create_order_rounding(monkeypatch):
dummy = DummyClient()
monkeypatch.setattr(binance_adapter, "mk_exchange", lambda *, **__: dummy)
settings = SimpleNamespace(
binance_api_key="key",
binance_api_secret="secret",
binance_testnet=True,
taker_fee_bps=10.0,
)
adapter = binance_adapter.BinanceAdapter(settings=settings)
response = adapter.create_order("BTC/USDT", "buy", 0.012345, 30000.1234, order_type="limit")

assert response["amount"] == 0.0100
assert response["price"] == 30000.10
assert "newClientOrderId" in response["params"]
assert response["params"]["newClientOrderId"].startswith("bot-")