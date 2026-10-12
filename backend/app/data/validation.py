import pandas as pd
from typing import Dict, Any, Tuple
from app.data.profiling import profile_dataframe
from app.data.cleaning import clean_dataframe

def validate_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Validates, profiles, and generates an initial baseline cleaned DataFrame.
    Preserves backwards compatibility with existing pipelines while providing
    full data profiling metrics.
    """
    profile = profile_dataframe(df)
    ts_col = profile["timestamp_column"]

    # Generate baseline cleaned DataFrame without mutating original
    clean_df, cleaning_report = clean_dataframe(
        df=df,
        timestamp_col=ts_col,
        duplicate_policy="keep_first",
        imputation_method="time_interpolation",
        enforce_physical_bounds=True
    )

    # Post-cleaning profile for before-and-after comparison
    post_profile = profile_dataframe(clean_df, timestamp_col_override=ts_col)

    combined_summary = {
        **profile,
        "cleaning_report": cleaning_report,
        "cleaned_row_count": len(clean_df),
        "post_cleaning_quality_score": post_profile["quality_score"],
        "post_cleaning_missing_count": post_profile["missing_values_count"]
    }

    return clean_df, combined_summary
