import sys
from pathlib import Path

sys.path.insert(0, str(Path(file).resolve().parents[1]))
from src.strategy.position_sizing import position_size

def test_position_size_basic():
qty = position_size(equity=10_000, entry_price=20_000, atr=200, risk_per_trade=0.01, stop_atr_mult=2)
expected = (10_000 * 0.01) / (200 * 2)
assert qty == expected
qty2 = position_size(equity=0, entry_price=20_000, atr=200, risk_per_trade=0.01, stop_atr_mult=2)
assert qty2 == 0.0
