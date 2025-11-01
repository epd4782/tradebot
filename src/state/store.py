from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

try:
import pandas as pd
except ImportError: # pragma: no cover
pd = None # type: ignore

from ..config import get_settings

logger = logging.getLogger(__name__)

@dataclass
class EquityMetrics:
equity: float
wtd: float
ytd: float
max_drawdown: float
sharpe: float

def state_dir() -> Path:
settings = get_settings()
path = Path(settings.state_path)
path.mkdir(parents=True, exist_ok=True)
return path

def status_file() -> Path:
return state_dir() / "status.json"

def equity_file() -> Path:
return state_dir() / "equity.csv"

def trades_file() -> Path:
return state_dir() / "trades.jsonl"

def load_status(default_mode: Optional[str] = None) -> Dict[str, object]:
path = status_file()
if path.exists():
try:
return json.loads(path.read_text())
except json.JSONDecodeError as exc: # pragma: no cover - file corruption
logger.error("Failed to parse status.json: %s", exc)
if default_mode is None:
settings = get_settings()
default_mode = "paper" if (settings.binance_testnet or not settings.binance_api_key) else "live"
return {"equity": 0.0, "open_positions": [], "mode": default_mode, "paused": False}

def load_equity_series():
if pd is None:
return None
path = equity_file()
if not path.exists():
return None
try:
df = pd.read_csv(path, parse_dates=["timestamp"])
except Exception as exc: # pragma: no cover - IO issues
logger.error("Failed to load equity.csv: %s", exc)
return None
if df.empty:
return None
df = df.sort_values("timestamp")
df.set_index("timestamp", inplace=True)
return df["equity"]

def _week_start(ts: datetime) -> datetime:
return (ts - pd.Timedelta(days=ts.weekday())).replace(hour=0, minute=0, second=0, microsecond=0) # type: ignore[attr-defined]

def _year_start(ts: datetime) -> datetime:
return ts.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

def compute_equity_metrics() -> EquityMetrics:
series = load_equity_series()
if series is None or series.empty:
return EquityMetrics(0.0, 0.0, 0.0, 0.0, 0.0)

latest = float(series.iloc[-1])
last_ts = series.index[-1].to_pydatetime()

wtd = 0.0
ytd = 0.0
if pd is not None:
    week_start = _week_start(last_ts)
    week_series = series.loc[series.index >= week_start]
    if not week_series.empty:
        wtd = float((week_series.iloc[-1] / week_series.iloc[0] - 1.0) * 100.0)

    year_start = _year_start(last_ts)
    year_series = series.loc[series.index >= year_start]
    if not year_series.empty:
        ytd = float((year_series.iloc[-1] / year_series.iloc[0] - 1.0) * 100.0)

returns = series.pct_change().dropna()
sharpe = 0.0
if not returns.empty:
    sharpe = float(returns.mean() / (returns.std() + 1e-9) * (len(returns) ** 0.5))
running_max = series.cummax()
max_drawdown = float(((series / running_max) - 1.0).min() * 100.0)

return EquityMetrics(
    equity=latest,
    wtd=wtd,
    ytd=ytd,
    max_drawdown=max_drawdown,
    sharpe=sharpe,
)
def load_trades(limit: int = 50):
if pd is None:
return None
path = trades_file()
if not path.exists():
return pd.DataFrame(columns=["timestamp", "symbol", "side", "price", "amount", "fee"])
try:
df = pd.read_json(path, lines=True)
except ValueError as exc: # pragma: no cover - parse errors
logger.error("Failed to parse trades.jsonl: %s", exc)
return pd.DataFrame(columns=["timestamp", "symbol", "side", "price", "amount", "fee"])
if limit:
df = df.tail(limit)
return df

all = [
"EquityMetrics",
"compute_equity_metrics",
"load_equity_series",
"load_status",
"load_trades",
"state_dir",
"status_file",
"equity_file",
"trades_file",
]
