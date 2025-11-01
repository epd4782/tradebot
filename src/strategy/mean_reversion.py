from future annotations import annotations

try:
import pandas as pd
except ImportError: # pragma: no cover - optional dependency
pd = None # type: ignore

from .base import SignalResult
from ..data.features import compute_features

class MeanReversionStrategy:
def init(self, rsi_entry: float = 30.0, rsi_exit: float = 45.0) -> None:
self.rsi_entry = rsi_entry
self.rsi_exit = rsi_exit

def name(self) -> str:
    return "mean_reversion"

def generate_signals(self, df: pd.DataFrame) -> SignalResult:
    if pd is None:
        raise ImportError("pandas is required for strategy signals")
    features = compute_features(df)
    entries = ((features["rsi"] < self.rsi_entry) & (df["close"] < features["bollinger_low"])).astype(int)
    exits = ((features["rsi"] > self.rsi_exit) | (df["close"] >= features["bollinger_mid"])).astype(int)
    return SignalResult(entries=entries, exits=exits)
all = ["MeanReversionStrategy"]