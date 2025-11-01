from __future__ import annotations

try:
import pandas as pd
except ImportError: # pragma: no cover - optional dependency
pd = None # type: ignore

from .base import SignalResult
from ..data.features import compute_features

class MomentumRSIStrategy:
def __init__(
self,
rsi_entry: float = 55.0,
rsi_exit: float = 50.0,
vol_threshold: float = 0.02,
) -> None:
self.rsi_entry = rsi_entry
self.rsi_exit = rsi_exit
self.vol_threshold = vol_threshold

def name(self) -> str:
    return "momentum_rsi"

def generate_signals(self, df: pd.DataFrame) -> SignalResult:
    if pd is None:
        raise ImportError("pandas is required for strategy signals")
    features = compute_features(df)
    atr_ratio = (features["atr"] / df["close"]).replace([float("inf"), float("-inf")], 0.0).fillna(0.0)
    volatility_ok = atr_ratio < self.vol_threshold
    long_condition = (features["sma_50"] > features["sma_200"]) & (features["rsi"] > self.rsi_entry) & volatility_ok
    exit_condition = (features["rsi"] < self.rsi_exit) | (features["sma_50"] < features["sma_200"])

    entries = long_condition.astype(int).shift(1).fillna(0).astype(int)
    exits = exit_condition.astype(int).shift(1).fillna(0).astype(int)
    return SignalResult(entries=entries, exits=exits)
all = ["MomentumRSIStrategy"]
