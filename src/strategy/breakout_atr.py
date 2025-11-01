from future import annotations

try:
import pandas as pd
except ImportError: # pragma: no cover - optional dependency
pd = None # type: ignore

from .base import SignalResult
from ..data.features import compute_features

class BreakoutATRStrategy:
def init(self, lookback: int = 20, atr_mult: float = 1.5) -> None:
self.lookback = lookback
self.atr_mult = atr_mult

def name(self) -> str:
    return "breakout_atr"

def generate_signals(self, df: pd.DataFrame) -> SignalResult:
    if pd is None:
        raise ImportError("pandas is required for strategy signals")
    features = compute_features(df)
    rolling_high = df["close"].rolling(window=self.lookback, min_periods=1).max()
    trigger = rolling_high + features["atr"] * self.atr_mult
    entries = (df["close"] > trigger.shift(1)).astype(int)
    trailing_stop = (df["close"] - features["atr"] * self.atr_mult)
    exits = (df["close"] < trailing_stop.shift(1)).astype(int)
    return SignalResult(entries=entries, exits=exits.fillna(0))
all = ["BreakoutATRStrategy"]