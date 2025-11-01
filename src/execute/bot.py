from future import annotations

import json
import logging
import time
from dataclasses import dataclass
from datetime datetime
from typing import Dict, Optional

try: # pragma: no cover - optional heavy deps
import pandas as pd
except ImportError: # pragma: no cover
pd = None # type: ignore

from ..config import Settings, get_settings
from ..data.features import compute_features, make_feature_label
from ..data.market_data import MarketDataService, default_market_data_service
from ..execute.executor import Executor
from ..execute.notifier import Notifier
from ..ml.online_model import OnlineModel
from ..state.store import equity_file, state_dir, status_file, trades_file
from ..strategy.momentum_rsi import MomentumRSIStrategy
from ..strategy.position_sizing import position_size
from ..strategy.risk import RiskManager

logger = logging.getLogger(name)

@dataclass
class PositionState:
symbol: str
quantity: float
entry_price: float

class PaperBot:
"""Simple bar-close driven paper trading loop for Docker deployments."""

def __init__(
    self,
    settings: Optional[Settings] = None,
    market_data: Optional[MarketDataService] = None,
    executor: Optional[Executor] = None,
    notifier: Optional[Notifier] = None,
) -> None:
    if pd is None:
        raise ImportError("pandas is required for paper trading mode")
    self.settings = settings or get_settings()
    self.market_data = market_data or default_market_data_service()
    self.notifier = notifier or Notifier(settings=self.settings)
    self.executor = executor or Executor(settings=self.settings)
    self.executor.context.order_callback = self._handle_fill
    self.strategy = MomentumRSIStrategy()
    self.risk_manager = RiskManager(settings=self.settings)
    self.state_path = state_dir()
    self.positions: Dict[str, PositionState] = {}
    self.last_processed: Dict[str, pd.Timestamp] = {}
    self.last_trained: Dict[str, pd.Timestamp] = {}
    self.last_prices: Dict[str, float] = {}
    self.equity_curve: list[tuple[datetime, float]] = []
    self.paused = False
    self.poll_interval = max(int(self.settings.poll_interval_seconds), 10)
    self.model_features = [
        "sma_10",
        "sma_50",
        "sma_200",
        "rsi",
        "atr",
        "roc",
        "volatility",
    ]
    self.wallet = self.executor.context.wallet
    self.model = self._initialise_model()

def _initialise_model(self) -> Optional[OnlineModel]:
    try:
        return OnlineModel(
            feature_cols=self.model_features,
            probability_threshold=self.settings.ml_probability_threshold,
        )
    except Exception as exc:  # pragma: no cover - optional dependency path
        logger.warning("Online model unavailable: %s", exc)
        return None

def run_forever(self) -> None:
    logger.info("Starting paper trading loop for symbols: %s", self.settings.symbols_list())
    while True:
        try:
            self.run_once()
        except Exception as exc:  # pragma: no cover - resilience
            logger.exception("Paper trading iteration failed: %s", exc)
            time.sleep(self.poll_interval)
        else:
            time.sleep(self.poll_interval)

def run_once(self) -> None:
    # refresh equity snapshot before processing new bars
    self._record_equity_snapshot()
    self._update_risk_pause()

    for symbol in self.settings.symbols_list():
        df = self._fetch_frame(symbol)
        if df is None or df.empty:
            continue
        last_ts = df.index[-1]
        if self.last_processed.get(symbol) == last_ts:
            # nothing new; update price cache and continue
            self.last_prices[symbol] = float(df["close"].iloc[-1])
            continue

        self.last_processed[symbol] = last_ts
        self.last_prices[symbol] = float(df["close"].iloc[-1])

        try:
            features = compute_features(df)
        except Exception as exc:
            logger.error("Feature computation failed for %s: %s", symbol, exc)
            continue
        atr_series = features["atr"].fillna(0.0)
        atr = float(atr_series.iloc[-1]) if not atr_series.empty else 0.0
        try:
            signals = self.strategy.generate_signals(df)
        except Exception as exc:
            logger.error("Signal generation failed for %s: %s", symbol, exc)
            continue
        entry_signal = bool(signals.entries.iloc[-1])
        exit_signal = bool(signals.exits.iloc[-1])

        price = float(df["close"].iloc[-1])

        self._update_model(symbol, df)

        if self.paused:
            continue

        if entry_signal and symbol not in self.positions:
            self._enter_position(symbol, price, atr)
        elif exit_signal and symbol in self.positions:
            self._exit_position(symbol, price)

    self._persist_state()

def _fetch_frame(self, symbol: str):
    try:
        since = None
        last_ts = self.last_processed.get(symbol)
        if last_ts is not None:
            since = int(last_ts.value // 1_000_000)
        return self.market_data.fetch(
            symbol,
            self.settings.timeframe,
            limit=500,
            since=since,
        )
    except Exception as exc:  # pragma: no cover - network path
        logger.error("Failed to fetch market data for %s: %s", symbol, exc)
        return None

def _update_model(self, symbol: str, df: pd.DataFrame) -> None:
    if self.model is None:
        return
    try:
        features, labels = make_feature_label(df)
    except Exception as exc:
        logger.debug("Unable to prepare features for ML model: %s", exc)
        return
    if symbol in self.last_trained and self.last_trained[symbol] == features.index[-1]:
        return
    self.model.partial_fit_on_barclose(features[self.model_features], labels.values)
    self.last_trained[symbol] = features.index[-1]

def _enter_position(self, symbol: str, price: float, atr: float) -> None:
    equity = self._current_equity()
    quantity = position_size(
        equity=equity,
        entry_px=price,
        atr=atr,
        risk_per_trade=self.settings.risk_per_trade,
    )
    if quantity <= 0:
        logger.debug("Position size zero for %s; skipping", symbol)
        return
    if not self._risk_allows_entry(quantity, price):
        logger.info("Risk limits prevented entry for %s", symbol)
        return
    fill = self.executor.execute_order(symbol, "buy", quantity, price)
    self.positions[symbol] = PositionState(
        symbol=symbol,
        quantity=float(fill.get("amount", quantity)),
        entry_price=float(fill.get("price", price)),
    )
    self.notifier.notify(
        "trade_open",
        f"[{symbol}] momentum_rsi BUY qty={self.positions[symbol].quantity:.6f} @ {self.positions[symbol].entry_price:.2f}",
        min_interval=10,
    )

def _exit_position(self, symbol: str, price: float) -> None:
    position = self.positions.get(symbol)
    if not position:
        return
    self.executor.execute_order(symbol, "sell", position.quantity, price)
    pnl = (price - position.entry_price) * position.quantity
    self.notifier.notify(
        "trade_close",
        f"[{symbol}] EXIT qty={position.quantity:.6f} @ {price:.2f} PnL={pnl:.2f}",
        min_interval=10,
    )
    self.positions.pop(symbol, None)

def _risk_allows_entry(self, quantity: float, price: float) -> bool:
    if not self.risk_manager.check_position_limit(len(self.positions)):
        return False
    projected = self._projected_exposure(quantity * price)
    return self.risk_manager.check_exposure(projected)

def _projected_exposure(self, additional_value: float = 0.0) -> float:
    equity = self._current_equity()
    if equity <= 0:
        return 0.0
    open_value = 0.0
    for pos in self.positions.values():
        open_value += pos.quantity * self.last_prices.get(pos.symbol, pos.entry_price)
    return (open_value + additional_value) / equity

def _current_equity(self) -> float:
    price_map = {symbol: price for symbol, price in self.last_prices.items()}
    return float(self.wallet.total_value(price_map))

def _record_equity_snapshot(self) -> None:
    equity = self._current_equity()
    if not self.equity_curve or self.equity_curve[-1][1] != equity:
        self.equity_curve.append((datetime.utcnow(), equity))
        if len(self.equity_curve) > 10_000:
            self.equity_curve = self.equity_curve[-10_000:]

def _equity_series(self) -> pd.Series:
    if not self.equity_curve:
        return pd.Series(dtype=float)
    timestamps, values = zip(*self.equity_curve)
    return pd.Series(values, index=pd.to_datetime(list(timestamps)))

def _update_risk_pause(self) -> None:
    series = self._equity_series()
    if series.empty:
        return
    should_pause = self.risk_manager.should_pause_trading(series)
    if should_pause and not self.paused:
        loss_pct = self.risk_manager.daily_loss_pct(series)
        self.notifier.notify(
            "risk_pause",
            f"Daily loss limit hit ({loss_pct:.2f}%) â€” pausing entries",
            min_interval=300,
        )
    elif not should_pause and self.paused:
        self.notifier.notify("risk_resume", "Trading resumed", min_interval=300)
    self.paused = should_pause

def _persist_state(self) -> None:
    equity = self._current_equity()
    status = {
        "timestamp": datetime.utcnow().isoformat(),
        "mode": "paper",
        "equity": equity,
        "paused": self.paused,
        "open_positions": [
            {
                "symbol": pos.symbol,
                "quantity": pos.quantity,
                "entry_price": pos.entry_price,
            }
            for pos in self.positions.values()
        ],
    }
    status_path = status_file()
    status_path.write_text(json.dumps(status, indent=2))

    if self.equity_curve and pd is not None:
        equity_path = equity_file()
        df = pd.DataFrame(self.equity_curve, columns=["timestamp", "equity"])
        df.to_csv(equity_path, index=False)

def _handle_fill(self, payload: Dict) -> None:
    record = dict(payload)
    record["timestamp"] = datetime.utcnow().isoformat()
    trades_path = trades_file()
    with trades_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")

def _fetch_prices(self) -> Dict[str, float]:  # pragma: no cover - helper for future use
    return dict(self.last_prices)
all = ["PaperBot", "PositionState"]