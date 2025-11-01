from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd

class Strategy(Protocol):
def generate_signals(self, df: pd.DataFrame) -> pd.Series: ...
def name(self) -> str: ...

@dataclass
class SignalResult:
entries: pd.Series
exits: pd.Series

all = ["Strategy", "SignalResult"]
