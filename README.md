
TradeIt Binance Trading Bot
Ein leichtgewichtiges, produktionsnahes Projekt fÃ¼r einen modularen Spot-Krypto-Trading-Bot auf Binance.

Features
Broker-Adapter fÃ¼r Binance (ccxt) mit Paper-Wallet-Fallback

Datenmodul mit SQLite-Caching, Feature Engineering und Markt-/News-Reports

Mehrere Strategien (Momentum RSI, Mean Reversion, Breakout ATR) sowie Ensemble-Auswahl

Risk- und Positions-Management mit ATR-basierten Stops und Exposure-Limits

Backtesting-Engine mit Kennzahlen, Walk-Forward-Updates und CLI-Steuerung

Online lernendes ML-Modul mit SGDClassifier

Telegram-Alerts, FastAPI Status-API und Streamlit Dashboard

Docker Compose Setup fÃ¼r Bot, API und UI

Setup
Python 3.11 installieren

Repository klonen und in das Projekt wechseln:

git clone <repo-url>
cd trading-bot
Virtuelle Umgebung erstellen und AbhÃ¤ngigkeiten installieren:

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
.env anhand von .env.example anpassen oder die bereitgestellte .env fÃ¼r Testnet/Paper verwenden. Die wichtigsten Variablen:

DB_URL=sqlite:///./data/bot.db â€“ persistente SQLite-Datenbank im gemounteten data/-Verzeichnis

STATE_PATH=./data/state â€“ Status- und Equity-Dateien fÃ¼r API/UI

POLL_INTERVAL_SECONDS=60 â€“ Abfrageintervall des Paper-Bots

Offline Wheelhouse & CI
Lege vor dem ersten CI-Lauf alle benÃ¶tigten Wheels in wheelhouse/ ab (pip download -r requirements.txt -d wheelhouse).

Die GitHub Actions Workflow-Datei offline-ci.yml installiert ausschlieÃŸlich aus diesem Verzeichnis. Ist es leer, fÃ¼hrt sie das Offline-Test-Harness scripts/offline_tests.py ohne zusÃ¤tzliche Pakete aus, sodass der Build nicht am Proxy scheitert.

Optional kÃ¶nnen weitere Wheels (z.â€¯B. interne Builds) ergÃ¤nzt werden, ohne Anpassungen am Workflow vornehmen zu mÃ¼ssen.

CLI Beispiele
python -m src.main backtest --symbols BTC/USDT,ETH/USDT --timeframe 1h --start 2023-01-01 --end 2024-01-01 --strategy ensemble
python -m src.main paper
python -m src.main live
python -m src.main report --daily
python -m src.main ui
Docker
docker compose up -d --build
Dies startet Bot (Paper-Modus), FastAPI und das Streamlit Dashboard. FÃ¼r vollstÃ¤ndig offline Builds setze beim Image-Build das Argument --build-arg USE_OFFLINE_WHEELS=true, nachdem die benÃ¶tigten Wheels in wheelhouse/ abgelegt wurden.

Alle Services teilen sich das lokale ./data-Verzeichnis (gemountet nach /app/data). Darin befinden sich u.â€¯a.:

data/bot.db â€“ SQLite Cache/Trades

data/state/status.json â€“ aktueller Bot-Status

data/state/equity.csv â€“ Equity-Verlauf fÃ¼r API/UI

data/state/trades.jsonl â€“ Trade-Log (JSON Lines)

Paper-Mode Deployment (Docker Compose)
.env mit Paper/Testnet-Keys ausstatten (Standardwerte vorhanden).

Wheels in wheelhouse/ kopieren, falls kein Internetzugang verfÃ¼gbar ist.

Container-Stack starten:

docker compose up -d --build
Streamlit UI unter http://localhost:8501, FastAPI unter http://localhost:8000 aufrufen.

Sicherheit
Bewahre API-Keys sicher in der .env auf.

Handle Limits konservativ und Ã¼berwache die PositionsgrÃ¶ÃŸe.

Backtests sind keine Garantie fÃ¼r zukÃ¼nftige ErtrÃ¤ge.