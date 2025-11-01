from future import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy

from ..strategy.base import SignalResult
from ..strategy.ensemble import EnsembleSelector
from ..strategy.momentum_rsi import MomentumRSIStrategy
from ..strategy.mean_reversion import MeanReversionStrategy
from ..strategy.breakout_atr import BreakoutATRStrategy
from ..strategy.position_sizing import position_size

@dataclass
class BacktestResult:
equity_curve: pd.Series
trades: pd.DataFrame
stats: Dict[str, float]

class BacktestEngine:
def init(self, cash: float = 10_000.0, commission: float = 0.001):
self.cash = cash
self.commission = commission

def run(self, df: pd.DataFrame, signals: SignalResult, symbol: str) -> BacktestResult:
    class WrappedStrategy(Strategy):
        def init(inner_self):
            inner_self.signal_entries = signals.entries.astype(bool)
            inner_self.signal_exits = signals.exits.astype(bool)

        def next(inner_self):
            if inner_self.signal_entries.iloc[-1] and not inner_self.position:
                size = position_size(
                    inner_self.equity,
                    inner_self.data.Close[-1],
                    max(inner_self.data.Close[-1] * 0.01, 1e-6),
                    risk_per_trade=0.01,
                    stop_atr_mult=2.0,
                )
                if size > 0:
                    inner_self.buy(size=size)
            elif inner_self.signal_exits.iloc[-1] and inner_self.position:
                inner_self.position.close()

    bt = Backtest(
        df,
        WrappedStrategy,
        cash=self.cash,
        commission=self.commission,
        trade_on_close=True,
    )
    stats = bt.run()
    equity_curve = stats["_equity_curve"]["Equity"]
    trades = stats["_trades"].copy()
    return BacktestResult(
        equity_curve=equity_curve,
        trades=trades,
        stats={
            "Equity Final": float(stats["Equity Final [$]"]),
            "CAGR": float(stats.get("Return (Ann.)", 0.0)),
            "Sharpe": float(stats.get("Sharpe Ratio", 0.0)),
            "Win Rate": float(stats.get("Win Rate [%]", 0.0)),
        },
    )
def prepare_strategies() -> Dict[str, object]:
return {
"momentum_rsi": MomentumRSIStrategy(),
"mean_reversion": MeanReversionStrategy(),
"breakout_atr": BreakoutATRStrategy(),
}

def ensemble_select(signals: Dict[str, SignalResult]) -> SignalResult:
selector = EnsembleSelector()
return selector.blend_signals(signals)