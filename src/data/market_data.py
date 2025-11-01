from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import pandas as pd
from sqlalchemy import Column, DateTime, Float, Integer, MetaData, String, Table, create_engine, select
from sqlalchemy.dialects.sqlite import insert

from ..config import get_settings

logger = logging.getLogger(__name__)

metadata = MetaData()

candles = Table(
"candles",
metadata,
Column("id", Integer, primary_key=True),
Column("symbol", String, nullable=False),
Column("timeframe", String, nullable=False),
Column("timestamp", DateTime, nullable=False),
Column("open", Float, nullable=False),
Column("high", Float, nullable=False),
Column("low", Float, nullable=False),
Column("close", Float, nullable=False),
Column("volume", Float, nullable=False),
)

@dataclass
class MarketDataService:
engine_url: str

def __post_init__(self):
    self.engine = create_engine(self.engine_url, future=True)
    metadata.create_all(self.engine)

def fetch(self, symbol: str, timeframe: str, since: Optional[int] = None, limit: int = 500) -> pd.DataFrame:
    with self.engine.begin() as conn:
        stmt = (
            select(candles)
            .where(candles.c.symbol == symbol)
            .where(candles.c.timeframe == timeframe)
            .order_by(candles.c.timestamp.desc())
            .limit(limit)
        )
        rows = conn.execute(stmt).fetchall()
    if not rows:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    df = pd.DataFrame(rows, columns=rows[0].keys())
    df.sort_values("timestamp", inplace=True)
    df.set_index("timestamp", inplace=True)
    return df

def store(self, symbol: str, timeframe: str, data) -> None:
    if not data:
        return
    records = []
    for entry in data:
        ts, open_, high, low, close, volume = entry
        records.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "timestamp": pd.to_datetime(ts, unit="ms"),
                "open": float(open_),
                "high": float(high),
                "low": float(low),
                "close": float(close),
                "volume": float(volume),
            }
        )
    if not records:
        return
    with self.engine.begin() as conn:
        for record in records:
            stmt = (
                insert(candles)
                .values(**record)
                .on_conflict_do_nothing(index_elements=["symbol", "timeframe", "timestamp"])
            )
            conn.execute(stmt)
def default_market_data_service() -> MarketDataService:
settings = get_settings()
return MarketDataService(engine_url=settings.db_url)
