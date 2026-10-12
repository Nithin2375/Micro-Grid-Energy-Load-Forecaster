import pytest
import pandas as pd
import numpy as np
from app.data.validation import validate_dataframe
from app.data.preprocessing import preprocess_and_feature_engineer

def test_validate_dataframe_valid():
    dates = pd.date_range("2026-01-01", periods=48, freq="h")
    df = pd.DataFrame({
        "timestamp": dates,
        "load_kW": np.random.uniform(100, 300, size=48),
        "solar_generation_kW": np.random.uniform(0, 150, size=48)
    })
    clean_df, summary = validate_dataframe(df)
    assert len(clean_df) == 48
    assert summary["quality_score"] > 90
    assert summary["timestamp_column"] == "timestamp"
    assert "load_kW" in summary["numeric_columns"]

def test_validate_dataframe_missing_and_duplicates():
    dates = pd.date_range("2026-01-01", periods=10, freq="h")
    df = pd.DataFrame({
        "timestamp": list(dates) + [dates[0]],  # 1 duplicate
        "load_kW": [100.0, np.nan, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0, 100.0]
    })
    clean_df, summary = validate_dataframe(df)
    assert len(clean_df) == 10
    assert summary["duplicate_timestamps"] == 1
    assert summary["missing_values_count"] == 1

def test_preprocess_and_feature_engineer():
    dates = pd.date_range("2026-01-01", periods=72, freq="h")
    df = pd.DataFrame({
        "timestamp": dates,
        "load_kW": np.random.uniform(100, 300, size=72)
    })
    processed = preprocess_and_feature_engineer(df, "timestamp", "load_kW")
    assert "hour" in processed.columns
    assert "target_lag_1" in processed.columns
    assert "target_rolling_mean_24" in processed.columns
    assert not processed.isna().any().any()
