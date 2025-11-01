from future import annotations

from dataclasses import dataclass
from datetime import datetime

import yfinance as yf

@dataclass
class MarketSnapshot:
dax_level: float
dax_change_pct: float
btc_price: float
btc_change_pct: float
eth_price: float
eth_change_pct: float

def fetch_market_snapshot() -> MarketSnapshot:
tickers = ["^GDAXI", "BTC-USD", "ETH-USD"]
data = yf.download(tickers, period="2d", interval="1d", progress=False, auto_adjust=True)
latest = data["Close"].iloc[-1]
prev = data["Close"].iloc[-2]
change = (latest - prev) / prev * 100.0
return MarketSnapshot(
dax_level=float(latest["^GDAXI"]),
dax_change_pct=float(change["^GDAXI"]),
btc_price=float(latest["BTC-USD"]),
btc_change_pct=float(change["BTC-USD"]),
eth_price=float(latest["ETH-USD"]),
eth_change_pct=float(change["ETH-USD"]),
)

def build_daily_report(equity: float, wtd: float) -> str:
snap = fetch_market_snapshot()
now = datetime.now().strftime("%Y-%m-%d")
return (
f"[Daily Report {now}] DAX {snap.dax_level:.2f} ({snap.dax_change_pct:+.2f}%), "
f"BTC {snap.btc_price:.2f} ({snap.btc_change_pct:+.2f}%), "
f"ETH {snap.eth_price:.2f} ({snap.eth_change_pct:+.2f}%), "
f"Equity {equity:.2f}, WTD {wtd:+.2f}%"
)

def build_weekly_report(pnl_pct: float, max_dd: float, top_strategy: str) -> str:
now = datetime.now().strftime("%Y-%m-%d")
return f"[Weekly Report {now}] Woche: PnL {pnl_pct:+.2f}% | MaxDD {max_dd:.2f}% | TopStrat {top_strategy}"