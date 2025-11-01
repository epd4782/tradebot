from __future__ import annotations

import argparse
import logging
from typing import List, Optional

import pandas as pd
import uvicorn

from .api.server import app
from .backtest.engine import BacktestEngine
from .config import get_settings
from .data.market_data import MarketDataService, default_market_data_service
from .data.news_report import build_daily_report, build_weekly_report
from .execute.bot import PaperBot
from .execute.notifier import Notifier
from .logging_conf import configure_logging
from .state.store import compute_equity_metrics
from .strategy.breakout_atr import BreakoutATRStrategy
from .strategy.mean_reversion import MeanReversionStrategy
from .strategy.momentum_rsi import MomentumRSIStrategy
from .ui.dashboard import run_dashboard

try: # pragma: no cover - optional dependency
from apscheduler.schedulers.background import BackgroundScheduler
except Exception: # pragma: no cover
BackgroundScheduler = None

logger = logging.getLogger(__name__)

def _load_prices(service: MarketDataService, symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
df = service.fetch(symbol, timeframe)
df = df.loc[start:end] if start or end else df
return df

def run_backtest(args: argparse.Namespace) -> None:
settings = get_settings()
service = default_market_data_service()
engine = BacktestEngine(settings=settings)
strategy_map = {
"momentum": MomentumRSIStrategy(),
"mean": MeanReversionStrategy(),
"breakout": BreakoutATRStrategy(),
}
strategy = strategy_map.get(args.strategy, MomentumRSIStrategy())
logger.info("Running backtest for %s", args.symbols)
frames = []
for symbol in args.symbols.split(","):
df = _load_prices(service, symbol.strip(), args.timeframe, args.start, args.end)
frames.append(df)
df = pd.concat(frames)
signals = strategy.generate_signals(df)
result = engine.run(df, signals, symbol=args.symbols)
logger.info("Backtest stats: %s", result.stats)

def run_paper(_: argparse.Namespace) -> None:
settings = get_settings()
notifier = Notifier(settings=settings)
schedule_reports(notifier)
try:
bot = PaperBot(settings=settings, notifier=notifier)
except ImportError as exc:
logger.error("Unable to start paper trading: %s", exc)
raise SystemExit(1) from exc
try:
bot.run_forever()
except KeyboardInterrupt:
logger.info("Paper trading stopped by user")

def run_live(_: argparse.Namespace) -> None:
settings = get_settings()
if not settings.binance_api_key:
raise SystemExit("Binance keys missing")
if settings.binance_testnet:
raise SystemExit("Disable testnet before starting live trading")
notifier = Notifier(settings=settings)
schedule_reports(notifier)
logger.info("Live trading mode initialised")

def run_report(args: argparse.Namespace) -> None:
if args.weekly:
report = build_weekly_report(2.0, -5.0, "momentum_rsi")
else:
report = build_daily_report(10_000.0, 1.5)
logger.info("Report: %s", report)

def run_api(_: argparse.Namespace) -> None:
uvicorn.run(app, host="0.0.0.0", port=8000)

def run_ui(_: argparse.Namespace) -> None:
run_dashboard()

def _parse_time_window(spec: str) -> tuple[int, int]:
hour, minute = spec.split(":")
return int(hour), int(minute)

def schedule_reports(notifier: Notifier) -> Optional[object]:
settings = get_settings()
if BackgroundScheduler is None:
logger.warning("APScheduler not available, skipping scheduled reports")
return None
scheduler = BackgroundScheduler(timezone="Europe/Berlin")
daily_hour, daily_minute = _parse_time_window(settings.telegram_daily_report_time)
weekly_hour, weekly_minute = _parse_time_window(settings.telegram_weekly_report_time)

def _daily_job() -> None:
    metrics = compute_equity_metrics()
    notifier.notify(
        "daily_report",
        build_daily_report(metrics.equity, metrics.wtd),
        min_interval=60,
    )

def _weekly_job() -> None:
    metrics = compute_equity_metrics()
    notifier.notify(
        "weekly_report",
        build_weekly_report(metrics.wtd, metrics.max_drawdown, "momentum_rsi"),
        min_interval=60,
    )

scheduler.add_job(_daily_job, "cron", hour=daily_hour, minute=daily_minute)
scheduler.add_job(
    _weekly_job,
    "cron",
    day_of_week="sun",
    hour=weekly_hour,
    minute=weekly_minute,
)
scheduler.start()
logger.info("Scheduled daily and weekly Telegram reports")
return scheduler
def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
parser = argparse.ArgumentParser(description="TradeIt bot controller")
sub = parser.add_subparsers(dest="command", required=True)

bt = sub.add_parser("backtest")
bt.add_argument("--symbols", default="BTC/USDT")
bt.add_argument("--timeframe", default="1h")
bt.add_argument("--start", default="")
bt.add_argument("--end", default="")
bt.add_argument("--strategy", default="momentum")
bt.set_defaults(func=run_backtest)

sub.add_parser("paper").set_defaults(func=run_paper)
sub.add_parser("live").set_defaults(func=run_live)

report = sub.add_parser("report")
group = report.add_mutually_exclusive_group()
group.add_argument("--daily", action="store_true")
group.add_argument("--weekly", action="store_true")
report.set_defaults(func=run_report)

sub.add_parser("api").set_defaults(func=run_api)
sub.add_parser("ui").set_defaults(func=run_ui)

return parser.parse_args(argv)
def main(argv: List[str] | None = None) -> None:
configure_logging()
args = parse_args(argv)
args.func(args)

if __name__ == "__main__":
main()
