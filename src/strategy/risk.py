from dataclasses import dataclass
from datetime import datetime
import pandas as pd

from ..config import get_settings

@dataclass
class RiskLimits:
max_concurrent: int
max_exposure: float
max_daily_loss: float

class RiskManager:
def __init__(self, settings=None) -> None:
self.settings = settings or get_settings()
self.limits = RiskLimits(
max_concurrent=self.settings.max_concurrent_positions,
max_exposure=self.settings.max_total_exposure,
max_daily_loss=self.settings.max_daily_loss,
)

def check_position_limit(self, open_positions: int) -> bool:
    return open_positions < self.limits.max_concurrent

def check_exposure(self, exposure: float) -> bool:
    return exposure <= self.limits.max_exposure

def daily_loss_pct(self, equity_curve: pd.Series) -> float:
    today = equity_curve[pd.to_datetime(equity_curve.index).date == datetime.utcnow().date()]
    if today.empty:
        return 0.0
    drawdown = today.iloc[-1] / today.iloc[0] - 1.0
    return float(drawdown * 100.0)

def check_daily_loss(self, equity_curve: pd.Series) -> bool:
    loss_pct = self.daily_loss_pct(equity_curve)
    return loss_pct >= -self.limits.max_daily_loss * 100.0

def should_pause_trading(self, equity_curve: pd.Series) -> bool:
    loss_pct = self.daily_loss_pct(equity_curve)
    if loss_pct <= -self.limits.max_daily_loss * 100.0:
        return True
    return False
all = ["RiskManager", "RiskLimits"]
