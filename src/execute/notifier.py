from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Optional

try: # pragma: no cover - requires network
from telegram import Bot
except Exception: # pragma: no cover
Bot = None

from ..config import get_settings

logger = logging.getLogger(__name__)

class Notifier:
def __init__(self, settings=None) -> None:
self.settings = settings or get_settings()
self._bot = None
self._last_sent = defaultdict(float)
if Bot and self.settings.telegram_bot_token:
self._bot = Bot(token=self.settings.telegram_bot_token)

def send(self, message: str) -> None:
    if not self.settings.telegram_chat_id:
        logger.debug("Telegram chat id missing, skipping message")
        return
    if not self._bot:
        logger.info("No Telegram bot configured, message would be: %s", message)
        return
    try:  # pragma: no cover
        self._bot.send_message(chat_id=self.settings.telegram_chat_id, text=message)
    except Exception as exc:
        logger.error("Failed to send Telegram message: %s", exc)

def notify(self, key: str, message: str, min_interval: int = 30) -> None:
    now = time.time()
    if now - self._last_sent[key] < min_interval:
        logger.debug("Skipping notification %s due to rate limit", key)
        return
    self.send(message)
    self._last_sent[key] = now
all = ["Notifier"]
