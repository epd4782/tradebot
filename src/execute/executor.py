from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

from ..broker.binance_adapter import BinanceAdapter
from ..broker.paper_wallet import PaperWallet
from ..config import get_settings

logger = logging.getLogger(__name__)

@dataclass
class ExecutionContext:
equity: float = 10_000.0
equity_curve: list = field(default_factory=list)
order_callback: Optional[Callable[[Dict], None]] = None
wallet: PaperWallet = field(default_factory=lambda: PaperWallet(balance={"USDT": 10_000.0}))
mode: str = "paper"

class Executor:
def __init__(self, settings=None) -> None:
self.settings = settings or get_settings()
self.context = ExecutionContext()
self.adapter: Optional[BinanceAdapter] = None

def execute_order(self, symbol: str, side: str, quantity: float, price: float) -> Dict:
    if self.context.mode == "paper":
        fill = self.context.wallet.execute(symbol, side, quantity, price)
        payload = {
            "symbol": symbol,
            "side": side,
            "amount": quantity,
            "price": fill.price,
            "fee": fill.fee,
            "equity": self.context.wallet.equity_history[-1][1] if self.context.wallet.equity_history else self.context.wallet.total_value(),
            "mode": "paper",
        }
        logger.info("Paper order executed: %s", payload)
        if self.context.order_callback:
            self.context.order_callback(payload)
        return payload
    adapter = self.adapter or BinanceAdapter(settings=self.settings)
    response = adapter.create_order(symbol, side, quantity, price)
    if self.context.order_callback:
        self.context.order_callback(response)
    return response
all = ["Executor", "ExecutionContext"]
