import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional

def clean_dataframe(
    df: pd.DataFrame,
    timestamp_col: str,
    duplicate_policy: str = "keep_first",
    imputation_method: str = "time_interpolation",
    max_interpolation_gap: int = 6,
    allow_large_gap_interpolation: bool = False,
    outlier_policy: str = "flag_only",
    enforce_physical_bounds: bool = True,
    allow_negative_power: bool = False,
    resample_regular_grid: bool = False
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Configurable, non-destructive cleaning pipeline for micro-grid time-series data.
    Preserves original structure while generating an auditable cleaned DataFrame.
    """
    cleaned = df.copy()
    actions_taken: List[str] = []
    initial_rows = len(cleaned)
    initial_missing = int(cleaned.isna().sum().sum())

    # 1. Parse and sanitize timestamps
    cleaned[timestamp_col] = pd.to_datetime(cleaned[timestamp_col], errors='coerce')
    invalid_ts = int(cleaned[timestamp_col].isna().sum())
    if invalid_ts > 0:
        cleaned = cleaned.dropna(subset=[timestamp_col]).copy()
        actions_taken.append(f"Removed {invalid_ts} rows with invalid / unparseable timestamps.")

    # 2. Chronological sort
    cleaned = cleaned.sort_values(by=timestamp_col).reset_index(drop=True)

    # 3. Exact duplicate row removal
    exact_dups = int(cleaned.duplicated().sum())
    if exact_dups > 0:
        cleaned = cleaned.drop_duplicates().reset_index(drop=True)
        actions_taken.append(f"Removed {exact_dups} exact duplicate rows.")

    # 4. Duplicate timestamp resolution
    dup_ts_count = int(cleaned.duplicated(subset=[timestamp_col]).sum())
    if dup_ts_count > 0:
        numeric_cols = cleaned.select_dtypes(include=[np.number]).columns.tolist()
        
        if duplicate_policy == "mean" and numeric_cols:
            cleaned = cleaned.groupby(timestamp_col, as_index=False).mean()
            actions_taken.append(f"Aggregated {dup_ts_count} duplicate timestamp records using mean aggregation.")
        elif duplicate_policy == "median" and numeric_cols:
            cleaned = cleaned.groupby(timestamp_col, as_index=False).median()
            actions_taken.append(f"Aggregated {dup_ts_count} duplicate timestamp records using median aggregation.")
        elif duplicate_policy == "sum" and numeric_cols:
            cleaned = cleaned.groupby(timestamp_col, as_index=False).sum()
            actions_taken.append(f"Aggregated {dup_ts_count} duplicate timestamp records using sum aggregation.")
        elif duplicate_policy == "keep_last":
            cleaned = cleaned.drop_duplicates(subset=[timestamp_col], keep='last').reset_index(drop=True)
            actions_taken.append(f"Resolved {dup_ts_count} duplicate timestamps by keeping last occurrence.")
        else:  # default "keep_first"
            cleaned = cleaned.drop_duplicates(subset=[timestamp_col], keep='first').reset_index(drop=True)
            actions_taken.append(f"Resolved {dup_ts_count} duplicate timestamps by keeping first occurrence.")

    # 5. Detect and handle regular sampling intervals
    inferred_freq = None
    if len(cleaned) > 2:
        diffs = cleaned[timestamp_col].diff().dropna().dt.total_seconds()
        median_sec = diffs.median()
        mode_sec = diffs.mode().iloc[0] if not diffs.mode().empty else median_sec

        if mode_sec == 3600:
            inferred_freq = "1h"
        elif mode_sec == 900:
            inferred_freq = "15min"
        elif mode_sec == 1800:
            inferred_freq = "30min"
        elif mode_sec == 86400:
            inferred_freq = "1D"

    # Optional regular grid resampling
    if resample_regular_grid and inferred_freq and len(cleaned) > 2:
        start_t = cleaned[timestamp_col].min()
        end_t = cleaned[timestamp_col].max()
        full_grid = pd.date_range(start=start_t, end=end_t, freq=inferred_freq)
        cleaned = cleaned.set_index(timestamp_col).reindex(full_grid).reset_index()
        cleaned.rename(columns={'index': timestamp_col}, inplace=True)
        actions_taken.append(f"Reindexed timestamps to complete regular grid ({inferred_freq}). Added missing timestamps.")

    # 6. Physical bounds validation & clamping
    numeric_cols = [c for c in cleaned.select_dtypes(include=[np.number]).columns if c != timestamp_col]

    if enforce_physical_bounds:
        for col in numeric_cols:
            col_lower = col.lower()
            # Battery SOC clamp to [0, 100]
            if any(b in col_lower for b in ['soc', 'battery_soc']):
                out_bounds = int(((cleaned[col] < 0) | (cleaned[col] > 100)).sum())
                if out_bounds > 0:
                    cleaned[col] = cleaned[col].clip(lower=0.0, upper=100.0)
                    actions_taken.append(f"Clamped {out_bounds} battery state of charge values in '{col}' to [0.0, 100.0]%.")

            # Renewable generation clamp to >= 0
            if any(g in col_lower for g in ['solar', 'wind', 'pv']) and not allow_negative_power:
                neg_vals = int((cleaned[col] < 0).sum())
                if neg_vals > 0:
                    cleaned[col] = cleaned[col].clip(lower=0.0)
                    actions_taken.append(f"Clamped {neg_vals} negative generation values in '{col}' to 0.0 kW.")

            # Load clamp to >= 0 unless user specifies bidirectional power
            if any(l in col_lower for l in ['load', 'demand', 'consumption']) and 'net' not in col_lower and not allow_negative_power:
                neg_vals = int((cleaned[col] < 0).sum())
                if neg_vals > 0:
                    cleaned[col] = cleaned[col].clip(lower=0.0)
                    actions_taken.append(f"Clamped {neg_vals} negative consumption values in '{col}' to 0.0 kW.")

    # 7. Outlier handling
    outliers_modified = 0
    if outlier_policy in ["clip_iqr", "impute_nan"]:
        for col in numeric_cols:
            clean_s = cleaned[col].dropna()
            if len(clean_s) > 10:
                q25 = clean_s.quantile(0.25)
                q75 = clean_s.quantile(0.75)
                iqr = q75 - q25
                lower_b = q25 - 1.5 * iqr
                upper_b = q75 + 1.5 * iqr

                mask = (cleaned[col] < lower_b) | (cleaned[col] > upper_b)
                c_outliers = int(mask.sum())
                if c_outliers > 0:
                    outliers_modified += c_outliers
                    if outlier_policy == "clip_iqr":
                        cleaned[col] = cleaned[col].clip(lower=lower_b, upper=upper_b)
                        actions_taken.append(f"Clipped {c_outliers} IQR outliers in '{col}' to bounds [{lower_b:.2f}, {upper_b:.2f}].")
                    elif outlier_policy == "impute_nan":
                        cleaned.loc[mask, col] = np.nan
                        actions_taken.append(f"Set {c_outliers} statistical outliers in '{col}' to NaN for subsequent imputation.")
    else:
        actions_taken.append("Outliers retained (flag-only policy) to preserve valid peak load dynamics.")

    # 8. Missing value imputation with gap-size control
    imputed_count = 0
    limit_gap = None if allow_large_gap_interpolation else max_interpolation_gap

    for col in numeric_cols:
        col_missing = int(cleaned[col].isna().sum())
        if col_missing > 0:
            if imputation_method in ["time_interpolation", "linear"]:
                # Use interpolation with maximum consecutive limit
                cleaned[col] = cleaned[col].interpolate(
                    method='linear',
                    limit=limit_gap,
                    limit_direction='both'
                )
                # Fallback remainder if any
                cleaned[col] = cleaned[col].bfill().ffill()
            elif imputation_method == "forward_fill":
                cleaned[col] = cleaned[col].ffill(limit=limit_gap).bfill()
            elif imputation_method == "mean":
                col_mean = float(cleaned[col].mean())
                cleaned[col] = cleaned[col].fillna(col_mean)
            elif imputation_method == "median":
                col_med = float(cleaned[col].median())
                cleaned[col] = cleaned[col].fillna(col_med)

            post_missing = int(cleaned[col].isna().sum())
            cur_imputed = col_missing - post_missing
            imputed_count += cur_imputed
            actions_taken.append(f"Imputed {cur_imputed} missing cells in '{col}' using {imputation_method}.")

    final_rows = len(cleaned)
    final_missing = int(cleaned.isna().sum().sum())

    report = {
        "initial_rows": initial_rows,
        "final_rows": final_rows,
        "rows_removed": initial_rows - final_rows,
        "initial_missing_cells": initial_missing,
        "final_missing_cells": final_missing,
        "imputed_cells": imputed_count,
        "duplicate_timestamps_resolved": dup_ts_count,
        "outliers_modified": outliers_modified,
        "actions_taken": actions_taken,
        "configuration": {
            "duplicate_policy": duplicate_policy,
            "imputation_method": imputation_method,
            "max_interpolation_gap": max_interpolation_gap,
            "allow_large_gap_interpolation": allow_large_gap_interpolation,
            "outlier_policy": outlier_policy,
            "enforce_physical_bounds": enforce_physical_bounds,
            "allow_negative_power": allow_negative_power,
            "resample_regular_grid": resample_regular_grid
        }
    }

    return cleaned, report
