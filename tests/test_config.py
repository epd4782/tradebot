import sys
from pathlib import Path

import os

sys.path.insert(0, str(Path(file).resolve().parents[1]))
from src.config import Settings, get_settings

def test_settings_defaults(tmp_path, monkeypatch):
monkeypatch.delenv("BINANCE_API_KEY", raising=False)
settings = Settings()
assert settings.timeframe == "1h"
assert settings.max_concurrent_positions == 3
assert settings.symbols_list() == ["BTC/USDT", "ETH/USDT"]
assert settings.db_url.endswith("data/bot.db")
assert settings.state_path.endswith("data/state")
assert settings.poll_interval_seconds == 60

def test_get_settings_cached(monkeypatch):
monkeypatch.setenv("BASE_SYMBOLS", "BTC/USDT")
settings = get_settings()
assert "BTC/USDT" in settings.symbols_list()
