from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
binance_api_key: str = ""
binance_api_secret: str = ""
binance_testnet: bool = True
base_symbols: List[str] = ["BTC/USDT", "ETH/USDT"]
timeframe: str = "1h"
risk_per_trade: float = 0.01
max_concurrent_positions: int = 3
max_total_exposure: float = 0.8
max_daily_loss: float = 0.03
db_url: str = "sqlite:///./data/bot.db"
telegram_bot_token: str = ""
telegram_chat_id: str = ""
allow_toggle: bool = False
state_path: str = "./data/state"
poll_interval_seconds: int = 60
slippage_bps: int = 5
taker_fee_bps: int = 10
ml_probability_threshold: float = 0.55
telegram_daily_report_time: str = "08:00"
telegram_weekly_report_time: str = "18:00"

model_config = SettingsConfigDict(env_file=".env", extra="ignore")

def symbols_list(self) -> List[str]:
    return [s.strip() for s in self.base_symbols]
@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
return Settings()
