from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ScoreBreakdown(BaseModel):
    base_score: float = 100.0
    deduction_missing_values: float = 0.0
    deduction_duplicate_timestamps: float = 0.0
    deduction_invalid_timestamps: float = 0.0
    deduction_physical_anomalies: float = 0.0
    deduction_sampling_irregularity: float = 0.0
    final_quality_score: float = 100.0

class QualitySummary(BaseModel):
    total_rows: int
    missing_values_count: int
    missing_values_pct: float
    duplicate_timestamps: int
    exact_duplicate_rows: Optional[int] = 0
    detected_frequency: str
    median_interval_seconds: Optional[float] = 0.0
    is_chronologically_sorted: Optional[bool] = True
    numeric_columns: List[str]
    timestamp_column: str
    quality_score: float
    score_breakdown: Optional[Dict[str, Any]] = None
    warnings: List[str]
    column_stats: Dict[str, Dict[str, Any]]
    missing_timestamp_gaps: Optional[List[Dict[str, Any]]] = None
    cleaning_report: Optional[Dict[str, Any]] = None
    cleaned_row_count: Optional[int] = None
    post_cleaning_quality_score: Optional[float] = None
    post_cleaning_missing_count: Optional[int] = None

class DatasetCleanRequest(BaseModel):
    duplicate_policy: str = Field("keep_first", description="keep_first, keep_last, mean, median, sum")
    imputation_method: str = Field("time_interpolation", description="time_interpolation, forward_fill, mean, median")
    max_interpolation_gap: int = Field(6, ge=1, le=168, description="Max consecutive steps allowed for interpolation")
    allow_large_gap_interpolation: bool = Field(False, description="Explicit approval to interpolate across large missing intervals")
    outlier_policy: str = Field("flag_only", description="flag_only, clip_iqr, impute_nan")
    enforce_physical_bounds: bool = Field(True, description="Clamp battery SOC [0-100] and non-negative generation")
    allow_negative_power: bool = Field(False, description="Allow legitimate negative power for bidirectional microgrids")
    resample_regular_grid: bool = Field(False, description="Resample onto regular time grid")

class DatasetSchema(BaseModel):
    id: int
    filename: str
    original_filename: str
    created_at: Any
    row_count: int
    cleaned_row_count: Optional[int] = None
    timestamp_column: str
    start_time: Optional[str]
    end_time: Optional[str]
    time_interval: Optional[str]
    columns: List[str]
    quality: QualitySummary
    cleaning_config: Optional[Dict[str, Any]] = None
    cleaning_report: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ForecastRunCreate(BaseModel):
    dataset_id: int
    target_column: str
    model_name: str = Field("RandomForest", description="Model algorithm name (Naive, SeasonalNaive, LinearRegression, RandomForest, GradientBoosting, LSTM)")
    horizon: int = Field(24, ge=1, le=168, description="Forecast horizon in steps (e.g. 1, 6, 12, 24, 48, 168)")
    feature_columns: Optional[List[str]] = None
    impute_missing: bool = True
    exogenous_mode: str = Field("exclude_exogenous", description="exclude_exogenous, autoregressive_only, persistence_exogenous")
    tune_hyperparameters: bool = Field(False, description="Perform cross-validated hyperparameter tuning")

class MetricSummary(BaseModel):
    mae: Optional[float] = None
    rmse: Optional[float] = None
    mape: Optional[float] = None
    smape: Optional[float] = None
    wape: Optional[float] = None
    r2: Optional[float] = None
    baseline_mae: Optional[float] = None
    baseline_rmse: Optional[float] = None
    improvement_over_baseline_pct: Optional[float] = None
    val_mae: Optional[float] = None
    val_rmse: Optional[float] = None
    val_smape: Optional[float] = None
    val_r2: Optional[float] = None

class PredictionItem(BaseModel):
    timestamp: str
    actual_value: Optional[float] = None
    predicted_value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    is_future: bool = False

class ForecastRunSchema(BaseModel):
    id: int
    dataset_id: int
    target_column: str
    model_name: str
    horizon: int
    status: str
    created_at: Any
    parameters: Dict[str, Any]
    metrics: Optional[MetricSummary] = Field(default_factory=MetricSummary)
    validation_metrics: Optional[Dict[str, Any]] = None
    hourly_metrics: Optional[Dict[str, Any]] = None
    dow_metrics: Optional[Dict[str, Any]] = None
    model_artifact_path: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class PredictionListResponse(BaseModel):
    run_id: int
    target_column: str
    model_name: str
    predictions: List[PredictionItem]
