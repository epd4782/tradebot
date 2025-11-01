from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(file).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
sys.path.insert(0, str(SRC))

@pytest.fixture(autouse=True)
def reset_settings_cache():
from src.config import get_settings

get_settings.cache_clear()
yield
get_settings.cache_clear()
