from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List

logger = logging.getLogger(__name__)

@dataclass
class Fill:
price: float
fee: float

class PaperWallet:
def __init__(self, balance: Dict[str, float]):
self.balance = balance.copy()
self.equity_history: List[tuple[str, float]] = []

def execute(self, symbol: str, side: str, quantity: float, price: float) -> Fill:
    base = symbol.split("/")[0]
    quote = symbol.split("/")[1]
    notional = quantity * price
    fee = notional * 0.001
    if side.lower() == "buy":
        if self.balance.get(quote, 0.0) < notional + fee:
            raise ValueError("Insufficient balance")
        self.balance[quote] = self.balance.get(quote, 0.0) - notional - fee
        self.balance[base] = self.balance.get(base, 0.0) + quantity
    else:
        if self.balance.get(base, 0.0) < quantity:
            raise ValueError("Insufficient balance")
        self.balance[base] = self.balance.get(base, 0.0) - quantity
        self.balance[quote] = self.balance.get(quote, 0.0) + notional - fee
    total = sum(self.balance.values())
    self.equity_history.append(("UTC", total))
    return Fill(price=price, fee=fee)

def total_value(self, prices: Dict[str, float] | None = None) -> float:
    if not prices:
        return sum(self.balance.values())
    total = 0.0
    for asset, qty in self.balance.items():
        total += qty * prices.get(asset, 1.0)
    return total
all = ["PaperWallet", "Fill"]
