import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional

def profile_dataframe(df: pd.DataFrame, timestamp_col_override: Optional[str] = None) -> Dict[str, Any]:
    """
    Comprehensive, domain-aware profiling of a microgrid time-series dataset.
    Detects column types, temporal regularities, missingness, physical anomalies, and computes
    a transparent, auditable Data Quality Score.
    """
    warnings: List[str] = []
    
    # 1. Identify timestamp column
    if timestamp_col_override and timestamp_col_override in df.columns:
        ts_col = timestamp_col_override
    else:
        candidates = [c for c in df.columns if any(k in c.lower() for k in ['time', 'date', 'datetime', 'timestamp'])]
        ts_col = candidates[0] if candidates else df.columns[0]
        if not candidates:
            warnings.append(f"No explicit datetime column detected. Defaulting to first column '{ts_col}'.")

    # Timestamp conversion & check
    ts_series = pd.to_datetime(df[ts_col], errors='coerce')
    invalid_ts_count = int(ts_series.isna().sum())
    if invalid_ts_count > 0:
        warnings.append(f"Detected {invalid_ts_count} rows with unparseable or null timestamps.")

    valid_mask = ts_series.notna()
    valid_ts = ts_series[valid_mask]
    
    # Chronological ordering check
    is_sorted = bool(valid_ts.is_monotonic_increasing)
    if not is_sorted and len(valid_ts) > 1:
        warnings.append("Timestamps are not strictly sorted in chronological order.")

    # Duplicate rows and duplicate timestamps
    exact_duplicate_rows = int(df.duplicated().sum())
    duplicate_timestamps = int(valid_ts.duplicated().sum())
    if exact_duplicate_rows > 0:
        warnings.append(f"Found {exact_duplicate_rows} exact duplicate rows.")
    if duplicate_timestamps > 0:
        warnings.append(f"Found {duplicate_timestamps} duplicate timestamp entries.")

    # Sampling frequency & intervals analysis
    freq_str = "Unknown"
    median_interval_sec = 0.0
    missing_timestamp_gaps = []
    irregular_intervals_count = 0

    if len(valid_ts) > 1:
        sorted_ts = valid_ts.sort_values().drop_duplicates()
        diffs = sorted_ts.diff().dropna()
        sec_diffs = diffs.dt.total_seconds()
        
        if len(sec_diffs) > 0:
            median_interval_sec = float(sec_diffs.median())
            mode_val = float(sec_diffs.mode().iloc[0]) if not sec_diffs.mode().empty else median_interval_sec

            if mode_val == 3600:
                freq_str = "1 Hour (1H)"
            elif mode_val == 900:
                freq_str = "15 Minutes (15T)"
            elif mode_val == 1800:
                freq_str = "30 Minutes (30T)"
            elif mode_val == 300:
                freq_str = "5 Minutes (5T)"
            elif mode_val == 60:
                freq_str = "1 Minute (1T)"
            elif mode_val == 86400:
                freq_str = "1 Day (1D)"
            else:
                freq_str = f"{int(mode_val)} Seconds"

            # Check gaps larger than 1.5x expected interval
            gap_mask = sec_diffs > (mode_val * 1.5)
            irregular_intervals_count = int(gap_mask.sum())
            if irregular_intervals_count > 0:
                warnings.append(f"Detected {irregular_intervals_count} missing temporal gaps / irregular sampling jumps.")
                # Record top 5 gaps
                gap_indices = np.where(gap_mask)[0]
                for idx in gap_indices[:5]:
                    start_gap = sorted_ts.iloc[idx]
                    end_gap = sorted_ts.iloc[idx + 1]
                    missing_steps = int(round(sec_diffs.iloc[idx] / max(1.0, mode_val))) - 1
                    missing_timestamp_gaps.append({
                        "from": str(start_gap),
                        "to": str(end_gap),
                        "duration_sec": float(sec_diffs.iloc[idx]),
                        "missing_steps": missing_steps
                    })

    # Numeric signals profiling
    numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != ts_col]
    total_cells = len(df) * len(numeric_cols) if numeric_cols else 1
    total_missing_cells = int(df[numeric_cols].isna().sum().sum()) if numeric_cols else 0
    missing_pct = round((total_missing_cells / total_cells) * 100.0, 2)

    column_stats: Dict[str, Dict[str, Any]] = {}
    total_outliers = 0
    total_physical_anomalies = 0

    for col in numeric_cols:
        col_series = pd.to_numeric(df[col], errors='coerce')
        missing_count = int(col_series.isna().sum())
        inf_count = int(np.isinf(col_series.fillna(0)).sum())
        clean_s = col_series.dropna()

        if len(clean_s) > 0:
            c_min = float(clean_s.min())
            c_max = float(clean_s.max())
            c_mean = float(clean_s.mean())
            c_std = float(clean_s.std()) if len(clean_s) > 1 else 0.0
            q25 = float(clean_s.quantile(0.25))
            q75 = float(clean_s.quantile(0.75))
            iqr = q75 - q25
            lower_iqr = q25 - 1.5 * iqr
            upper_iqr = q75 + 1.5 * iqr
            outlier_count = int(((clean_s < lower_iqr) | (clean_s > upper_iqr)).sum())
        else:
            c_min = c_max = c_mean = c_std = q25 = q75 = lower_iqr = upper_iqr = 0.0
            outlier_count = 0

        total_outliers += outlier_count

        # Microgrid physical domain checks
        col_lower = col.lower()
        physical_flags: List[str] = []

        # Battery State of Charge [0, 100]%
        if any(b in col_lower for b in ['soc', 'battery_soc', 'state_of_charge']):
            out_of_bounds = int(((clean_s < 0) | (clean_s > 100)).sum())
            if out_of_bounds > 0:
                physical_flags.append(f"{out_of_bounds} readings outside realistic battery SOC bounds [0-100%]")
                total_physical_anomalies += out_of_bounds

        # Solar Generation (strictly non-negative, zero at night)
        if any(s in col_lower for s in ['solar', 'pv', 'photovoltaic']):
            if c_min < -0.1:
                neg_count = int((clean_s < -0.1).sum())
                physical_flags.append(f"{neg_count} negative generation readings (< 0 kW)")
                total_physical_anomalies += neg_count

        # Wind Generation (strictly non-negative)
        if any(w in col_lower for w in ['wind', 'turbine']):
            if c_min < -0.1:
                neg_count = int((clean_s < -0.1).sum())
                physical_flags.append(f"{neg_count} negative generation readings (< 0 kW)")
                total_physical_anomalies += neg_count

        # Demand / Load (typically non-negative unless net-metered)
        if any(l in col_lower for l in ['load', 'demand', 'consumption']) and 'net' not in col_lower:
            if c_min < -0.1:
                neg_count = int((clean_s < -0.1).sum())
                warnings.append(f"Load signal '{col}' contains {neg_count} negative readings. Verify if net-metering is active.")

        column_stats[col] = {
            "missing_count": missing_count,
            "missing_pct": round((missing_count / len(df)) * 100.0, 2) if len(df) > 0 else 0.0,
            "inf_count": inf_count,
            "min": round(c_min, 2),
            "max": round(c_max, 2),
            "mean": round(c_mean, 2),
            "std": round(c_std, 2),
            "q25": round(q25, 2),
            "q75": round(q75, 2),
            "iqr_lower": round(lower_iqr, 2),
            "iqr_upper": round(upper_iqr, 2),
            "outlier_count": outlier_count,
            "physical_flags": physical_flags
        }

    # Transparent Quality Score Calculation
    # Base: 100.0 points
    # Deductions:
    # - Missing values: max -30
    # - Duplicate timestamps: max -20
    # - Invalid timestamps: max -20
    # - Physical violations: max -15
    # - Irregular temporal jumps: max -15
    n_rows = max(1, len(df))
    deduct_missing = min(30.0, missing_pct * 1.5)
    deduct_dups = min(20.0, (duplicate_timestamps / n_rows) * 100.0 * 2.0)
    deduct_invalid_ts = min(20.0, (invalid_ts_count / n_rows) * 100.0 * 5.0)
    deduct_physical = min(15.0, (total_physical_anomalies / max(1, total_cells)) * 100.0 * 2.0)
    deduct_irregular = min(15.0, irregular_intervals_count * 1.5)

    quality_score = max(0.0, round(100.0 - (deduct_missing + deduct_dups + deduct_invalid_ts + deduct_physical + deduct_irregular), 1))

    score_breakdown = {
        "base_score": 100.0,
        "deduction_missing_values": round(deduct_missing, 1),
        "deduction_duplicate_timestamps": round(deduct_dups, 1),
        "deduction_invalid_timestamps": round(deduct_invalid_ts, 1),
        "deduction_physical_anomalies": round(deduct_physical, 1),
        "deduction_sampling_irregularity": round(deduct_irregular, 1),
        "final_quality_score": quality_score
    }

    start_str = str(valid_ts.min()) if len(valid_ts) > 0 else None
    end_str = str(valid_ts.max()) if len(valid_ts) > 0 else None

    return {
        "total_rows": int(len(df)),
        "timestamp_column": ts_col,
        "start_time": start_str,
        "end_time": end_str,
        "detected_frequency": freq_str,
        "median_interval_seconds": median_interval_sec,
        "is_chronologically_sorted": is_sorted,
        "exact_duplicate_rows": exact_duplicate_rows,
        "duplicate_timestamps": duplicate_timestamps,
        "invalid_timestamps": invalid_ts_count,
        "irregular_intervals_count": irregular_intervals_count,
        "missing_timestamp_gaps": missing_timestamp_gaps,
        "numeric_columns": numeric_cols,
        "missing_values_count": total_missing_cells,
        "missing_values_pct": missing_pct,
        "total_outliers_detected": total_outliers,
        "total_physical_anomalies": total_physical_anomalies,
        "quality_score": quality_score,
        "score_breakdown": score_breakdown,
        "warnings": warnings,
        "column_stats": column_stats
    }
