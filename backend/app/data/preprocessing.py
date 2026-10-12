import pandas as pd
import numpy as np
from typing import List, Tuple

def preprocess_and_feature_engineer(
    df: pd.DataFrame,
    timestamp_col: str,
    target_col: str,
    feature_cols: List[str] = None,
    impute_missing: bool = True
) -> pd.DataFrame:
    df = df.copy()
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    df = df.sort_values(by=timestamp_col).reset_index(drop=True)

    if feature_cols is None:
        feature_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != target_col]

    # Impute missing values if required
    if impute_missing:
        # Linear interpolation for continuous energy series
        df[target_col] = df[target_col].interpolate(method='linear', limit_direction='both')
        for col in feature_cols:
            if col in df.columns and df[col].isna().any():
                df[col] = df[col].interpolate(method='linear', limit_direction='both')

    # Time-derived features
    df['hour'] = df[timestamp_col].dt.hour
    df['dayofweek'] = df[timestamp_col].dt.dayofweek
    df['month'] = df[timestamp_col].dt.month
    df['is_weekend'] = (df['dayofweek'] >= 5).astype(int)
    
    # Cyclical hour encoding (sin/cos)
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24.0)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24.0)

    # Lag features for target variable (e.g. 1 hour ago, 24 hours ago, 168 hours ago)
    df['target_lag_1'] = df[target_col].shift(1)
    df['target_lag_2'] = df[target_col].shift(2)
    df['target_lag_24'] = df[target_col].shift(24)

    # Rolling statistics (using shifted values to prevent data leakage)
    df['target_rolling_mean_6'] = df[target_col].shift(1).rolling(window=6, min_periods=1).mean()
    df['target_rolling_mean_24'] = df[target_col].shift(1).rolling(window=24, min_periods=1).mean()
    df['target_rolling_std_24'] = df[target_col].shift(1).rolling(window=24, min_periods=1).std().fillna(0)

    # Fill initial NaNs created by lag features safely using bfill/ffill
    df = df.bfill().ffill()

    return df
