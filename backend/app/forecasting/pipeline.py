import json
import pandas as pd
import numpy as np
from datetime import timedelta
from sqlalchemy.orm import Session
from app.db.models import DatasetModel, ForecastRunModel, PredictionModel
from app.data.preprocessing import preprocess_and_feature_engineer
from app.forecasting.baselines import NaiveForecaster, SeasonalNaiveForecaster
from app.forecasting.models import MLForecaster, StatsHoltWintersForecaster
from app.forecasting.evaluation import calculate_metrics

def run_forecasting_pipeline(db: Session, run_id: int):
    run = db.query(ForecastRunModel).filter(ForecastRunModel.id == run_id).first()
    if not run:
        return

    try:
        run.status = "RUNNING"
        db.commit()

        dataset = db.query(DatasetModel).filter(DatasetModel.id == run.dataset_id).first()
        if not dataset:
            raise ValueError("Dataset not found")

        df = pd.read_csv(dataset.file_path)
        timestamp_col = dataset.timestamp_column
        target_col = run.target_column

        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataset.")

        # Preprocess & engineer features
        processed_df = preprocess_and_feature_engineer(
            df=df,
            timestamp_col=timestamp_col,
            target_col=target_col,
            impute_missing=True
        )

        # Chronological split (80% train, 20% test for holdout evaluation)
        n = len(processed_df)
        train_size = int(n * 0.8)
        if n - train_size < 12:  # Ensure at least 12 test steps
            train_size = max(1, n - 12)

        train_df = processed_df.iloc[:train_size].copy()
        test_df = processed_df.iloc[train_size:].copy()

        # Identify feature columns
        non_feature_cols = [timestamp_col, target_col]
        feature_cols = [c for c in processed_df.columns if c not in non_feature_cols]

        X_train, y_train = train_df[feature_cols], train_df[target_col]
        X_test, y_test = test_df[feature_cols], test_df[target_col]

        # 1. Baseline Model (Seasonal Naive 24h)
        s_naive = SeasonalNaiveForecaster(season_length=24)
        s_naive.fit(y_train)
        baseline_test_preds = s_naive.predict(len(y_test))
        baseline_metrics = calculate_metrics(y_test.values, baseline_test_preds)

        # 2. Candidate Model Training & Test Evaluation
        model_name = run.model_name
        if model_name in ["RandomForest", "LinearRegression", "GradientBoosting"]:
            model = MLForecaster(model_type=model_name)
            model.fit(X_train, y_train)
            test_preds = model.predict(X_test)
        elif model_name == "HoltWinters":
            model = StatsHoltWintersForecaster(seasonal_periods=24)
            model.fit(y_train)
            test_preds = model.predict(len(y_test))
        else: # Default to RandomForest
            model = MLForecaster(model_type="RandomForest")
            model.fit(X_train, y_train)
            test_preds = model.predict(X_test)

        candidate_metrics = calculate_metrics(y_test.values, test_preds)

        # Calculate improvement percentage over baseline MAE
        if baseline_metrics["mae"] > 0:
            imp_pct = round(((baseline_metrics["mae"] - candidate_metrics["mae"]) / baseline_metrics["mae"]) * 100.0, 2)
        else:
            imp_pct = 0.0

        metrics_summary = {
            **candidate_metrics,
            "baseline_mae": baseline_metrics["mae"],
            "baseline_rmse": baseline_metrics["rmse"],
            "improvement_over_baseline_pct": imp_pct
        }

        # 3. Fit on full dataset & generate future forecasts
        horizon = run.horizon
        X_full, y_full = processed_df[feature_cols], processed_df[target_col]

        if model_name in ["RandomForest", "LinearRegression", "GradientBoosting"]:
            full_model = MLForecaster(model_type=model_name)
            full_model.fit(X_full, y_full)

            # Auto-regressive iterative future forecasting
            future_predictions = []
            curr_df = processed_df.copy()
            last_dt = pd.to_datetime(curr_df[timestamp_col].iloc[-1])

            # Determine frequency delta
            if len(curr_df) > 1:
                dt_delta = pd.to_datetime(curr_df[timestamp_col].iloc[-1]) - pd.to_datetime(curr_df[timestamp_col].iloc[-2])
            else:
                dt_delta = timedelta(hours=1)

            for step in range(1, horizon + 1):
                next_dt = last_dt + dt_delta * step
                # Create next row template
                next_row = {timestamp_col: next_dt}
                for c in feature_cols:
                    if c in curr_df.columns:
                        next_row[c] = curr_df[c].iloc[-1]
                
                # Update lag & time features
                next_row['hour'] = next_dt.hour
                next_row['dayofweek'] = next_dt.dayofweek
                next_row['month'] = next_dt.month
                next_row['is_weekend'] = 1 if next_dt.dayofweek >= 5 else 0
                next_row['hour_sin'] = np.sin(2 * np.pi * next_dt.hour / 24.0)
                next_row['hour_cos'] = np.cos(2 * np.pi * next_dt.hour / 24.0)
                next_row['target_lag_1'] = curr_df[target_col].iloc[-1]
                next_row['target_lag_2'] = curr_df[target_col].iloc[-2] if len(curr_df) >= 2 else curr_df[target_col].iloc[-1]
                next_row['target_lag_24'] = curr_df[target_col].iloc[-24] if len(curr_df) >= 24 else curr_df[target_col].iloc[-1]
                next_row['target_rolling_mean_6'] = curr_df[target_col].iloc[-6:].mean()
                next_row['target_rolling_mean_24'] = curr_df[target_col].iloc[-24:].mean()
                next_row['target_rolling_std_24'] = curr_df[target_col].iloc[-24:].std() or 0.0

                X_next = pd.DataFrame([next_row])[feature_cols]
                pred_val = float(full_model.predict(X_next)[0])

                next_row[target_col] = pred_val
                curr_df = pd.concat([curr_df, pd.DataFrame([next_row])], ignore_index=True)
                future_predictions.append((next_dt.strftime("%Y-%m-%d %H:%M:%S"), pred_val))

        else:
            full_model = StatsHoltWintersForecaster(seasonal_periods=24)
            full_model.fit(y_full)
            future_vals = full_model.predict(horizon)
            last_dt = pd.to_datetime(processed_df[timestamp_col].iloc[-1])
            dt_delta = timedelta(hours=1)
            future_predictions = [
                ((last_dt + dt_delta * (i + 1)).strftime("%Y-%m-%d %H:%M:%S"), float(v))
                for i, v in enumerate(future_vals)
            ]

        # Calculate residual std error for prediction bounds
        residuals = y_test.values - test_preds
        std_error = float(np.std(residuals)) if len(residuals) > 0 else 5.0

        # Save test period predictions
        prediction_records = []
        for pred_idx, (_, row) in enumerate(test_df.iterrows()):
            ts_str = pd.to_datetime(row[timestamp_col]).strftime("%Y-%m-%d %H:%M:%S")
            act_val = float(row[target_col])
            p_val = float(test_preds[pred_idx]) if 0 <= pred_idx < len(test_preds) else act_val
            prediction_records.append(
                PredictionModel(
                    run_id=run_id,
                    timestamp=ts_str,
                    actual_value=round(act_val, 2),
                    predicted_value=round(p_val, 2),
                    lower_bound=round(p_val - 1.96 * std_error, 2),
                    upper_bound=round(p_val + 1.96 * std_error, 2),
                    is_future=False
                )
            )

        # Save future predictions
        for ts_str, p_val in future_predictions:
            prediction_records.append(
                PredictionModel(
                    run_id=run_id,
                    timestamp=ts_str,
                    actual_value=None,
                    predicted_value=round(p_val, 2),
                    lower_bound=round(p_val - 1.96 * std_error, 2),
                    upper_bound=round(p_val + 1.96 * std_error, 2),
                    is_future=True
                )
            )

        db.bulk_save_objects(prediction_records)

        run.status = "COMPLETED"
        run.metrics_json = json.dumps(metrics_summary)
        db.commit()

    except Exception as e:
        run.status = "FAILED"
        run.error_message = str(e)
        db.commit()
