import sys
from pathlib import Path

import pytest
pytest.importorskip("pandas")
pytest.importorskip("sklearn")
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(file).resolve().parents[1]))
from src.ml.online_model import OnlineModel

def test_partial_fit_ignores_nan_labels():
model = OnlineModel(feature_cols=["feat"], probability_threshold=0.55)
df = pd.DataFrame({"feat": [1.0, 2.0, 3.0]})
labels = np.array([0, 1, np.nan])

model.partial_fit_on_barclose(df, labels)

assert model._model_initialized is True
probs = model.predict_proba(df)
assert probs.shape == (3, 2)
assert model.should_enter(0.60) is True
assert model.should_enter(0.50) is False