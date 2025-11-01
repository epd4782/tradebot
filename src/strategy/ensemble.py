import logging
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

try:
import pandas as pd
except ImportError: # pragma: no cover - optional dependency
pd = None # type: ignore

from .base import SignalResult

logger = logging.getLogger(__name__)

@dataclass
class StrategyPerformance:
name: str
equity_curve: pd.Series

def recent_return(self, periods: int = 24) -> float:
    if len(self.equity_curve) < 2:
        return 0.0
    tail = self.equity_curve.tail(periods)
    return tail.iloc[-1] / tail.iloc[0] - 1
@dataclass
class EnsembleSelector:
lookback: int = 24
default_strategy: str = "momentum_rsi"
performances: Dict[str, StrategyPerformance] = field(default_factory=dict)

def update_performance(self, name: str, equity_curve: pd.Series) -> None:
    if pd is None:
        raise ImportError("pandas is required for ensemble management")
    self.performances[name] = StrategyPerformance(name=name, equity_curve=equity_curve)

def select(self) -> str:
    if not self.performances:
        return self.default_strategy
    best = max(self.performances.values(), key=lambda perf: perf.recent_return(self.lookback))
    logger.debug("Selected strategy %s based on recent performance", best.name)
    if best.recent_return(self.lookback) <= 0:
        return self.default_strategy
    return best.name

def blend_signals(self, signals: Dict[str, SignalResult]) -> SignalResult:
    chosen = self.select()
    selected = signals.get(chosen)
    if selected is None:
        logger.warning("Strategy %s not present, falling back to default", chosen)
        selected = signals[self.default_strategy]
    return selected
all = ["EnsembleSelector"]
