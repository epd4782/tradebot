import sys
from types import SimpleNamespace
from pathlib import Path

sys.path.insert(0, str(Path(file).resolve().parents[1]))
from src.execute.notifier import Notifier

def test_notifier_respects_rate_limit():
settings = SimpleNamespace(telegram_bot_token="", telegram_chat_id="chat")
notifier = Notifier(settings=settings)
sent = []

def fake_send(self, message: str) -> None:
    sent.append(message)

notifier.send = fake_send.__get__(notifier, Notifier)
notifier.notify("trade", "hello", min_interval=60)
notifier.notify("trade", "hello", min_interval=60)

assert sent == ["hello"]