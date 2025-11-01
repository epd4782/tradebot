from future import annotations

def position_size(
equity: float,
entry_price: float,
atr: float,
risk_per_trade: float,
stop_atr_mult: float,
) -> float:
"""Berechnet StÃ¼ckzahl so, dass ATR*mult Verlust ~ risk_per_trade * equity entspricht."""
if equity <= 0 or entry_price <= 0 or atr <= 0:
return 0.0
risk_amount = equity * risk_per_trade
stop_distance = atr * stop_atr_mult
if stop_distance <= 0:
return 0.0
quantity = risk_amount / stop_distance
return max(float(quantity), 0.0)

all = ["position_size"]