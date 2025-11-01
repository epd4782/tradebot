from future import annotations

from dataclasses import dataclass
from typing import List

try:
import numpy as np
except ImportError: # pragma: no cover - optional dependency
np = None # type: ignore
try:
import pandas as pd
except ImportError: # pragma: no cover - optional dependency
pd = None # type: ignore
try:
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
except ImportError: # pragma: no cover - optional dependency
SGDClassifier = None # type: ignore
StandardScaler = None # type: ignore

@dataclass
class OnlineModel:
feature_cols: List[str]
probability_threshold: float = 0.55

def __post_init__(self) -> None:
    if StandardScaler is None or SGDClassifier is None:
        raise ImportError("scikit-learn is required for OnlineModel")
    self.scaler = StandardScaler()
    self.model = SGDClassifier(loss="log_loss", max_iter=1, warm_start=True)
    self.is_init = False        self._model_initialized = False

def _prepare(self, X: pd.DataFrame) -> np.ndarray:
    if pd is None or np is None:
        raise ImportError("pandas and numpy are required for online model")
    data = X[self.feature_cols].values
    if not self.is_init:
        self.scaler.fit(data)
        self.is_init = True
    else:
        self.scaler.partial_fit(data)
    return self.scaler.transform(data)

def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
    if pd is None or np is None:
        raise ImportError("pandas and numpy are required for online model")
    if not self._model_initialized:
        return np.full((len(X), 2), 0.5)
    data = self.scaler.transform(X[self.feature_cols].values)
    return self.model.predict_proba(data)

def partial_fit_on_barclose(self, X: pd.DataFrame, y: np.ndarray) -> None:
    if pd is None or np is None:
        raise ImportError("pandas and numpy are required for online model")
    if len(X) == 0:
        return
    mask = ~np.isnan(y)
    if not mask.any():
        return
    X_fit = X.loc[mask]
    y_fit = y[mask]
    if X_fit.empty:
        return
    data = self._prepare(X_fit)
    classes = np.array([0, 1])
    if not self._model_initialized:
        self.model.partial_fit(data, y_fit, classes=classes)
        self._model_initialized = True
    else:
        self.model.partial_fit(data, y_fit)

def should_enter(self, probability: float) -> bool:
    return probability >= self.probability_threshold
all = ["OnlineModel"]