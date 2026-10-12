# REST API Documentation (/api/v1)

This document provides endpoint specifications, HTTP methods, request payloads, and response structures for the **Micro-Grid Load Forecaster REST API**.

---

## 1. Health Endpoints

### `GET /health` or `GET /api/v1/health`
Checks application health status.

#### Response `200 OK`
```json
{
  "status": "healthy",
  "service": "Micro-Grid Renewable Energy Load Forecaster API",
  "version": "1.0.0"
}
```

---

## 2. Dataset Management Endpoints

### `POST /api/v1/datasets/upload`
Uploads and validates a CSV or Excel time-series file.

- **Content-Type**: `multipart/form-data`
- **Body**: `file` (Binary file, max 50MB)

#### Response `200 OK`
```json
{
  "id": 1,
  "filename": "dataset_a1b2c3d4.csv",
  "original_filename": "microgrid_sample_hourly.csv",
  "created_at": "2026-10-10T12:00:00",
  "row_count": 1440,
  "timestamp_column": "timestamp",
  "start_time": "2026-01-01 00:00:00",
  "end_time": "2026-03-01 23:00:00",
  "time_interval": "1 Hour (1H)",
  "columns": ["timestamp", "load_kW", "solar_generation_kW", "wind_generation_kW", "battery_soc", "grid_import_kW"],
  "quality": {
    "total_rows": 1440,
    "missing_values_count": 0,
    "missing_values_pct": 0.0,
    "duplicate_timestamps": 0,
    "detected_frequency": "1 Hour (1H)",
    "numeric_columns": ["load_kW", "solar_generation_kW", "wind_generation_kW", "battery_soc", "grid_import_kW"],
    "timestamp_column": "timestamp",
    "quality_score": 100.0,
    "warnings": [],
    "column_stats": {
      "load_kW": { "missing_count": 0, "min": 51.2, "mean": 245.8, "max": 482.1 }
    }
  }
}
```

### `GET /api/v1/datasets`
Lists all uploaded datasets sorted by creation date descending.

### `GET /api/v1/datasets/{id}/preview?limit=50`
Previews head rows of a dataset.

### `GET /api/v1/datasets/{id}/quality`
Retrieves data quality audit summary.

---

## 3. Forecast Run Endpoints

### `POST /api/v1/forecast-runs`
Configures and executes a new time-series forecast run.

#### Request Body (`application/json`)
```json
{
  "dataset_id": 1,
  "target_column": "load_kW",
  "model_name": "RandomForest",
  "horizon": 24,
  "impute_missing": true
}
```

#### Response `200 OK`
```json
{
  "id": 1,
  "dataset_id": 1,
  "target_column": "load_kW",
  "model_name": "RandomForest",
  "horizon": 24,
  "status": "COMPLETED",
  "created_at": "2026-10-10T12:05:00",
  "parameters": { "impute_missing": true },
  "metrics": {
    "mae": 14.85,
    "rmse": 18.22,
    "mape": 5.42,
    "smape": 5.28,
    "wape": 5.35,
    "r2": 0.945,
    "baseline_mae": 28.50,
    "baseline_rmse": 35.10,
    "improvement_over_baseline_pct": 47.89
  },
  "error_message": null
}
```

### `GET /api/v1/forecast-runs/{run_id}/predictions`
Retrieves test holdout predictions and future horizon forecast records.

### `GET /api/v1/forecast-runs/{run_id}/export`
Downloads forecast predictions as a CSV file.
