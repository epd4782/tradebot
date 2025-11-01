from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

class ModelStore:
def __init__(self, base_path: Path) -> None:
self.base_path = base_path
self.base_path.mkdir(parents=True, exist_ok=True)

def save(self, model: Any, name: str) -> Path:
    path = self.base_path / f"{name}.joblib"
    joblib.dump(model, path)
    return path

def load(self, name: str) -> Any:
    path = self.base_path / f"{name}.joblib"
    if not path.exists():
        raise FileNotFoundError(path)
    return joblib.load(path)
all = ["ModelStore"]
