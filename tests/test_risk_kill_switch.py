import sys
from pathlib import Path

import pytest
pytest.importorskip("pandas")
import pandas as pd

sys.path.insert(0, str(Path(file).resolve().parents[1]))
from src.config import Settings
from src.strategy.risk import RiskManager

def test_daily_loss_triggers_pause():
settings = Settings()
settings.max_daily_loss = 0.03
risk = RiskManager(settings=settings)
idx = pd.date_range("2024-01-01", periods=2, freq="H")
equity = pd.Series([1000.0, 960.0], index=idx)

assert risk.should_pause_trading(equity) is True
assert risk.check_daily_loss(equity) is False