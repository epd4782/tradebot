from future import annotations

try:
import pandas as pd
except ImportError: # pragma: no cover - optional dependency
pd = None # type: ignore
try:
import streamlit as st
except ImportError: # pragma: no cover - optional dependency
st = None # type: ignore

from ..config import get_settings
from ..state.store import compute_equity_metrics, load_equity_series, load_status, load_trades

def run_dashboard() -> None:
if st is None or pd is None:
raise ImportError("streamlit and pandas are required for the dashboard")
st.set_page_config(page_title="TradeIt Bot", layout="wide")
settings = get_settings()
st.title("TradeIt Bot Overview")
status = load_status()
mode = status.get("mode") or ("Paper" if not settings.binance_api_key else "Live")
st.sidebar.write("Mode", mode.capitalize())
if status.get("paused"):
st.sidebar.warning("Trading pausiert (Daily loss limit)")

st.subheader("Equity Curve")
equity_series = load_equity_series()
if equity_series is not None and not equity_series.empty:
    equity_df = equity_series.to_frame(name="equity")
    st.line_chart(equity_df)
else:
    st.info("Noch keine Equity-Daten verfÃ¼gbar")

st.subheader("Open Positions")
open_positions = status.get("open_positions", [])
if open_positions:
    st.table(pd.DataFrame(open_positions))
else:
    st.write("Keine offenen Positionen")

trades = load_trades()
st.subheader("Recent Trades")
if trades is not None and not trades.empty:
    st.dataframe(trades.sort_values("timestamp", ascending=False))
else:
    st.write("Noch keine Trades")

st.subheader("Equity & Risk Metrics")
metrics = compute_equity_metrics()
metrics_col1, metrics_col2 = st.columns(2)
metrics_col1.metric("Equity", f"{metrics.equity:,.2f} USDT")
metrics_col1.metric("Sharpe", f"{metrics.sharpe:.2f}")
metrics_col2.metric("Max Drawdown", f"{metrics.max_drawdown:.2f}%")
metrics_col2.metric("WTD", f"{metrics.wtd:.2f}%")

if settings.allow_toggle:
    col1, col2 = st.columns(2)
    if col1.button("Start"):
        st.toast("Start command sent")
    if col2.button("Stop"):
        st.toast("Stop command sent")
if name == "main":
run_dashboard()

all = ["run_dashboard"]