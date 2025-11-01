import sys
from pathlib import Path

import pytest
pytest.importorskip("pandas")
import pandas as pd

sys.path.insert(0, str(Path(file).resolve().parents[1]))
from src.strategy.momentum_rsi import MomentumRSIStrategy
from src.strategy.mean_reversion import MeanReversionStrategy
from src.strategy.breakout_atr import BreakoutATRStrategy

def sample_df():
idx = pd.date_range("2023-01-01", periods=100, freq="H")
close = pd.Series(range(100), index=idx) + 100
df = pd.DataFrame({
"open": close - 1,
"high": close + 1,
"low": close - 2,
"close": close,
"volume": 100,
})
return df

def test_momentum_signals():
df = sample_df()
strategy = MomentumRSIStrategy()
signals = strategy.generate_signals(df)
assert len(signals.entries) == len(df)
assert signals.entries.iloc[0] == 0

def test_mean_reversion_signals():
df = sample_df()
strategy = MeanReversionStrategy()
signals = strategy.generate_signals(df)
assert len(signals.entries) == len(df)

def test_breakout_signals():
df = sample_df()
strategy = BreakoutATRStrategy()
signals = strategy.generate_signals(df)
assert len(signals.entries) == len(df)