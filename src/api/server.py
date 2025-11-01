from __future__ import annotations

from dataclasses import asdict
from typing import Dict

from fastapi import FastAPI

from ..config import get_settings
from ..state.store import compute_equity_metrics, load_status

app = FastAPI(title="TradeIt Bot API")

@app.get("/health")
def health() -> Dict[str, str]:
return {"status": "ok"}

@app.get("/config")
def config_view() -> Dict[str, object]:
settings = get_settings()
return asdict(settings)

@app.get("/status")
def status() -> Dict[str, object]:
settings = get_settings()
default_mode = "paper" if (settings.binance_testnet or not settings.binance_api_key) else "live"
payload = load_status(default_mode=default_mode)
payload.setdefault("mode", default_mode)
payload.setdefault("paused", False)
return payload

@app.get("/metrics")
def metrics() -> Dict[str, float]:
equity = compute_equity_metrics()
return {"sharpe": equity.sharpe, "max_drawdown": equity.max_drawdown}

all = ["app"]
