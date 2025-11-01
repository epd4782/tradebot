from future import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import pandas as pd

@dataclass
class Position:
symbol: str
quantity: float
entry_price: float

def market_value(self, price: float) -> float:
    return self.quantity * price
@dataclass
class Portfolio:
cash: float
positions: Dict[str, Position] = field(default_factory=dict)

def equity(self, prices: Dict[str, float]) -> float:
    total = self.cash
    for pos in self.positions.values():
        total += pos.market_value(prices.get(pos.symbol, pos.entry_price))
    return total

def update_position(self, symbol: str, quantity: float, price: float) -> None:
    if quantity == 0:
        self.positions.pop(symbol, None)
        return
    self.positions[symbol] = Position(symbol=symbol, quantity=quantity, entry_price=price)

def open_positions(self) -> List[Position]:
    return list(self.positions.values())
all = ["Portfolio", "Position"]