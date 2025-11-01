from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd

@dataclass
class PerformanceMetrics:
cagr: float
sharpe: float
sortino: float
max_drawdown: float
win_rate: float
profit_factor: float

def compute_metrics(equity_curve: pd.Series, trades: pd.DataFrame) -> PerformanceMetrics:
returns = equity_curve.pct_change().dropna()
cagr = (equity_curve.iloc[-1] / equity_curve.iloc[0]) ** (365 / len(equity_curve)) - 1
sharpe = returns.mean() / (returns.std() + 1e-9) * (len(returns) ** 0.5)
downside = returns[returns < 0]
sortino = returns.mean() / (downside.std() + 1e-9) * (len(returns) ** 0.5)
running_max = equity_curve.cummax()
max_drawdown = ((equity_curve / running_max) - 1).min()
wins = trades[trades["PnL"] > 0]
win_rate = len(wins) / max(len(trades), 1)
gross_profit = trades[trades["PnL"] > 0]["PnL"].sum()
gross_loss = trades[trades["PnL"] < 0]["PnL"].abs().sum()
profit_factor = gross_profit / max(gross_loss, 1e-9)
return PerformanceMetrics(
cagr=float(cagr),
sharpe=float(sharpe),
sortino=float(sortino),
max_drawdown=float(max_drawdown),
win_rate=float(win_rate),
profit_factor=float(profit_factor),
)

def format_metrics(metrics: PerformanceMetrics) -> Dict[str, float]:
return {
"CAGR": metrics.cagr,
"Sharpe": metrics.sharpe,
"Sortino": metrics.sortino,
"Max Drawdown": metrics.max_drawdown,
"Win Rate": metrics.win_rate,
"Profit Factor": metrics.profit_factor,
}
