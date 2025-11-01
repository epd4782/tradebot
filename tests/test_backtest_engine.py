import sys
from pathlib import Path

import pytest
pytest.importorskip("pandas")
import pandas as pd

sys.path.insert(0, str(Path(file).resolve().parents[1]))
from src.backtest.engine import BacktestEngine
from src.strategy.momentum_rsi import MomentumRSIStrategy
from src.strategy.base import SignalResult

def sample_df():
idx = pd.date_range("2023-01-01", periods=200, freq="H")
close = pd.Series(range(200), index=idx) + 100
df = pd.DataFrame({
"open": close - 1,
"high": close + 1,
"low": close - 2,
"close": close,
"volume": 100,
})
return df

def test_backtest_engine_runs():
df = sample_df()
strategy = MomentumRSIStrategy()
signals = strategy.generate_signals(df)
engine = BacktestEngine()
result = engine.run(df, signals, symbol="BTC/USDT")
assert not result.equity_curve.empty
assert isinstance(result.stats, dict)