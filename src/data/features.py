from future import annotations

try:
import pandas as pd
except ImportError: # pragma: no cover
pd = None # type: ignore
try:
import pandas_ta as ta
except ImportError: # pragma: no cover
ta = None # type: ignore

def compute_features(df: pd.DataFrame) -> pd.DataFrame:
if pd is None or ta is None:
raise ImportError("pandas and pandas_ta are required for feature computation")
feats = pd.DataFrame(index=df.index)
feats["sma_10"] = df["close"].rolling(window=10, min_periods=10).mean()
feats["sma_50"] = df["close"].rolling(window=50, min_periods=50).mean()
feats["sma_200"] = df["close"].rolling(window=200, min_periods=200).mean()
feats["rsi"] = ta.rsi(df["close"], length=14)
feats["atr"] = ta.atr(df["high"], df["low"], df["close"], length=14)
bands = ta.bbands(df["close"], length=20)
feats["bollinger_low"] = bands["BBL_20_2.0"]
feats["bollinger_mid"] = bands["BBM_20_2.0"]
feats["bollinger_high"] = bands["BBU_20_2.0"]
feats["roc"] = ta.roc(df["close"], length=12)
feats["volatility"] = df["close"].rolling(window=20, min_periods=20).std()
return feats

def make_feature_label(df: pd.DataFrame):
feats = compute_features(df)
forward_return = df["close"].shift(-1) / df["close"] - 1.0
label = (forward_return > 0).astype(int)
aligned = feats.iloc[:-1]
label = label.iloc[:-1]
return aligned, label

all = ["compute_features", "make_feature_label"]