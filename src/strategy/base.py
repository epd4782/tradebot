from future import annotations

from dataclasses import dataclass
from typing import Protocol

try:
import pandas as pd
except ImportError: # pragma: no cover - optional dependency
pd = None # type: ignore

class Strategy(Protocol):
def name(self) -> str:
...

def generate_signals(self, df: pd.DataFrame):
    ...
@dataclass
class SignalResult:
entries: pd.Series
exits: pd.Series

all = ["Strategy", "SignalResult"]