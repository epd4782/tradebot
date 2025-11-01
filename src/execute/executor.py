from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Dict, Optional

from ..broker.paper_wallet import PaperWallet
from ..config import get_settings

logger = logging.getLogger(__name__)

@dataclass
class ExecutionContext:
mode: str # "paper" or "live"
wallet: PaperWallet
order_callback: Optional[Callable] = None

class Executor:
def __init__(self, settings=None, wallet: Optional[PaperWallet] = None) -> None:
self.settings = settings or get_settings()
default_wallet = PaperWallet(
balance={"USDT": 10_000.0},
fee_bps=self.settings.taker_fee_bps,
slippage_bps=self.settings.slippage_bps,
)
self.context = ExecutionContext(
mode=(
"live"
if self.settings.binance_api_key
and not self.settings.binance_testnet
else "paper"
),
wallet=wallet or default_wallet,
)

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
    from ..broker.binance_adapter import BinanceAdapter

    adapter = BinanceAdapter(settings=self.settings)
    response = adapter.create_order(symbol, side, quantity, price)
    if self.context.order_callback:
        self.context.order_callback(response)
    return response
all = ["Executor", "ExecutionContext"]
