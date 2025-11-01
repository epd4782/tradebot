import sys
from pathlib import Path

import pytest
pytest.importorskip("pandas")
import pandas as pd

sys.path.insert(0, str(Path(file).resolve().parents[1]))
from src.data.features import compute_features, make_feature_label

def sample_df():
idx = pd.date_range("2023-01-01", periods=300, freq="H")
data = {
"open": range(300),
"high": [v + 1 for v in range(300)],
"low": [v - 1 for v in range(300)],
"close": [v + 0.5 for v in range(300)],
"volume": [100] * 300,
}
return pd.DataFrame(data, index=idx)

def test_compute_features_shapes():
df = sample_df()
feats = compute_features(df)
assert {"sma_10", "rsi", "atr"}.issubset(feats.columns)
assert len(feats) == len(df)

def test_make_feature_label_alignment():
df = sample_df()
feats, label = make_feature_label(df)
assert len(feats) == len(label)
assert set(label.unique()).issubset({0, 1})
