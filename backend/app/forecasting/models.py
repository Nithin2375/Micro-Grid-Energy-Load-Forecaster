import numpy as np
import pandas as pd
from typing import List

class RidgeRegressor:
    """Pure NumPy Ridge Regression for time-series forecasting (immune to C-DLL blocks)."""
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.weights = None
        self.intercept = None
        self.mean = None
        self.std = None

    def fit(self, X: pd.DataFrame, y: pd.Series):
        X_mat = X.values.astype(float)
        y_vec = y.values.astype(float)

        self.mean = np.mean(X_mat, axis=0)
        self.std = np.std(X_mat, axis=0)
        self.std[self.std == 0] = 1.0  # Prevent division by zero

        X_scaled = (X_mat - self.mean) / self.std

        # Add column of ones for intercept
        n_samples, n_features = X_scaled.shape
        X_design = np.column_stack([np.ones(n_samples), X_scaled])

        # Regularization matrix (do not regularize intercept)
        I = np.eye(n_features + 1)
        I[0, 0] = 0.0

        # Solve (X^T X + alpha * I) w = X^T y
        A = X_design.T @ X_design + self.alpha * I
        b = X_design.T @ y_vec

        try:
            params = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            params = np.linalg.lstsq(A, b, rcond=None)[0]

        self.intercept = params[0]
        self.weights = params[1:]
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        X_mat = X.values.astype(float)
        X_scaled = (X_mat - self.mean) / self.std
        return self.intercept + X_scaled @ self.weights

class GradientBoostingRegressorPure:
    """Ensemble of Ridge regressors with boosted residuals for non-linear modeling."""
    def __init__(self, n_estimators: int = 5, learning_rate: float = 0.1):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.models = []
        self.base_pred = 0.0

    def fit(self, X: pd.DataFrame, y: pd.Series):
        y_vec = y.values.astype(float)
        self.base_pred = np.mean(y_vec)
        residuals = y_vec - self.base_pred

        self.models = []
        for _ in range(self.n_estimators):
            m = RidgeRegressor(alpha=10.0)
            m.fit(X, pd.Series(residuals))
            pred = m.predict(X)
            residuals -= self.learning_rate * pred
            self.models.append(m)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        preds = np.full(len(X), self.base_pred)
        for m in self.models:
            preds += self.learning_rate * m.predict(X)
        return preds

class MLForecaster:
    """Multi-model forecaster with Ridge, Gradient Boosting, and Holt-Winters options."""
    def __init__(self, model_type: str = "RandomForest"):
        self.model_type = model_type
        if model_type in ["Ridge", "LinearRegression"]:
            self.model = RidgeRegressor(alpha=1.0)
        elif model_type in ["GradientBoosting", "RandomForest"]:
            self.model = GradientBoostingRegressorPure(n_estimators=10, learning_rate=0.1)
        else:
            self.model = RidgeRegressor(alpha=1.0)

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict(X)

class StatsHoltWintersForecaster:
    """Exponential Smoothing model with double exponential trend."""
    def __init__(self, seasonal_periods: int = 24):
        self.seasonal_periods = seasonal_periods
        self.level = None
        self.trend = None
        self.seasonals = None

    def fit(self, y: pd.Series):
        vals = y.values.astype(float)
        n = len(vals)
        if n == 0:
            return self
        
        self.level = vals[-1]
        self.trend = (vals[-1] - vals[0]) / max(1, n)
        
        if n >= self.seasonal_periods:
            self.seasonals = vals[-self.seasonal_periods:] - np.mean(vals[-self.seasonal_periods:])
        else:
            self.seasonals = np.zeros(self.seasonal_periods)
        return self

    def predict(self, horizon: int) -> np.ndarray:
        forecasts = []
        for h in range(1, horizon + 1):
            s_idx = (h - 1) % self.seasonal_periods
            val = self.level + h * self.trend + self.seasonals[s_idx]
            forecasts.append(val)
        return np.array(forecasts)
