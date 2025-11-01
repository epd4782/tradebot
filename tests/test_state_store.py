from __future__ import annotations

from datetime import datetime

import pytest

pandas = pytest.importorskip("pandas")

from src.state.store import compute_equity_metrics, load_status, state_dir

def test_load_status_default(monkeypatch, tmp_path):
monkeypatch.setenv("STATE_PATH", str(tmp_path))
from src.config import get_settings

get_settings.cache_clear()
state_dir()
status = load_status()
assert status["equity"] == 0.0
assert status["open_positions"] == []
def test_compute_equity_metrics(monkeypatch, tmp_path):
monkeypatch.setenv("STATE_PATH", str(tmp_path))
from src.config import get_settings

get_settings.cache_clear()
path = state_dir()
df = pandas.DataFrame(
    [
        {"timestamp": datetime(2024, 1, 1, 0, 0), "equity": 10_000.0},
        {"timestamp": datetime(2024, 1, 8, 0, 0), "equity": 10_200.0},
        {"timestamp": datetime(2024, 1, 9, 0, 0), "equity": 10_300.0},
    ]
)
df.to_csv(path / "equity.csv", index=False)

metrics = compute_equity_metrics()
assert metrics.equity == 10_300.0
assert metrics.wtd == pytest.approx(0.980392, rel=1e-3)
assert metrics.ytd == pytest.approx(3.0, rel=1e-3)
assert metrics.max_drawdown == pytest.approx(0.0, abs=1e-6)
assert metrics.sharpe >= 0.0
