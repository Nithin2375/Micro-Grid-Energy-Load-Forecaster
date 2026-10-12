import pytest
import pandas as pd
import numpy as np
from app.forecasting.baselines import NaiveForecaster, SeasonalNaiveForecaster
from app.forecasting.models import MLForecaster
from app.forecasting.evaluation import calculate_metrics

def test_naive_forecasters():
    y = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
    naive = NaiveForecaster()
    naive.fit(y)
    preds = naive.predict(3)
    assert len(preds) == 3
    assert np.all(preds == 50.0)

    # Seasonal Naive 24-step
    y_seasonal = pd.Series(np.tile(np.arange(24), 3))  # 72 points
    s_naive = SeasonalNaiveForecaster(season_length=24)
    s_naive.fit(y_seasonal)
    s_preds = s_naive.predict(24)
    assert len(s_preds) == 24
    assert np.array_equal(s_preds, np.arange(24))

def test_ml_forecaster():
    X = pd.DataFrame({
        "feature1": np.random.randn(100),
        "feature2": np.random.randn(100)
    })
    y = pd.Series(np.random.randn(100) * 10 + 50)
    
    model = MLForecaster(model_type="RandomForest")
    model.fit(X, y)
    preds = model.predict(X[:10])
    assert len(preds) == 10

def test_calculate_metrics():
    y_true = np.array([100.0, 200.0, 300.0])
    y_pred = np.array([110.0, 190.0, 310.0])
    metrics = calculate_metrics(y_true, y_pred)
    assert metrics["mae"] == 10.0
    assert metrics["rmse"] == 10.0
    assert metrics["smape"] > 0
    assert metrics["wape"] > 0
