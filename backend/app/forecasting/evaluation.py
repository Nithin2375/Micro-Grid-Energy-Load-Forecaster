import numpy as np
import pandas as pd
from typing import Dict, Any

def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # Clean any NaNs
    mask = ~np.isnan(y_true) & ~np.isnan(y_pred)
    y_true = y_true[mask]
    y_pred = y_pred[mask]
    
    if len(y_true) == 0:
        return {"mae": 0.0, "rmse": 0.0, "mape": None, "smape": 0.0, "wape": 0.0, "r2": 0.0}

    errors = y_true - y_pred
    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(errors ** 2)))

    # MAPE (only computed when non-zero)
    non_zero_mask = y_true != 0
    if np.any(non_zero_mask):
        mape = float(np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100.0)
    else:
        mape = None

    # sMAPE (Symmetric MAPE)
    denom = (np.abs(y_true) + np.abs(y_pred)) / 2.0
    valid_denom = denom > 1e-5
    if np.any(valid_denom):
        smape = float(np.mean(np.abs(y_true[valid_denom] - y_pred[valid_denom]) / denom[valid_denom]) * 100.0)
    else:
        smape = 0.0

    # WAPE (Weighted Absolute Percentage Error)
    sum_actual = float(np.sum(np.abs(y_true)))
    if sum_actual > 1e-5:
        wape = float((np.sum(np.abs(errors)) / sum_actual) * 100.0)
    else:
        wape = 0.0

    # R2 Score
    ss_res = np.sum(errors ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 1e-5 else 0.0

    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "mape": round(mape, 2) if mape is not None else None,
        "smape": round(smape, 2),
        "wape": round(wape, 2),
        "r2": round(r2, 3)
    }
