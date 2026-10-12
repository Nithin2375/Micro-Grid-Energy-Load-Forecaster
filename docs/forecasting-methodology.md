# Time-Series Forecasting Methodology & Evaluation

This document details the algorithms, feature engineering techniques, chronological holdout split rules, evaluation metrics, and data leakage prevention mechanisms implemented in the **AI-Driven Micro-Grid Load Forecaster**.

---

## 1. Baseline Models vs Candidate Models

To objectively evaluate machine learning performance, every candidate model is compared against simple baseline models on identical held-out test timestamps.

### Baseline Models
1. **Persistence Naive**: Predicts that future load will equal the single last observed value:
   $$\hat{y}_{t+h} = y_t$$
2. **Seasonal Naive (24-Hour Period)**: Predicts that load at hour $t+h$ will equal the load observed at the same hour on the previous day (24 steps prior):
   $$\hat{y}_{t+h} = y_{t+h-24}$$

### Candidate Forecasters
1. **Random Forest / Gradient Boosted Trees Regressor**: Non-linear ensemble model trained on temporal features (`hour`, `dayofweek`, `month`, `is_weekend`, `hour_sin`, `hour_cos`) and autoregressive target lags (`lag_1`, `lag_2`, `lag_24`, `rolling_mean_6`, `rolling_mean_24`).
2. **Ridge Linear Regression**: L2-regularized linear model providing linear baseline interpretable weights for lag windows.
3. **Pure Gradient Boosting**: Sequential residual boosting ensemble for non-linear load profile dynamics.
4. **Holt-Winters Exponential Smoothing**: Classical statistical model capturing double exponential trend and 24-hour additive seasonality.

---

## 2. Feature Engineering & Data Leakage Prevention

### Anti-Leakage Rules
- **Rule 1: Strict Chronological Split**: Data is split into 80% Train and 20% Test sequentially by timestamp. Random cross-validation (K-Fold) is prohibited to avoid future-to-past data leakage.
- **Rule 2: Fit on Train Only**: Feature scalers, mean imputers, and rolling statistics are calculated solely from the Training set.
- **Rule 3: Shifted Rolling Windows**: Rolling statistics use `.shift(1)` so that feature calculation at time $t$ uses only observations up to $t-1$.

```python
# Rolling statistics engineered without future leakage
df['target_rolling_mean_6'] = df[target_col].shift(1).rolling(window=6, min_periods=1).mean()
df['target_rolling_mean_24'] = df[target_col].shift(1).rolling(window=24, min_periods=1).mean()
```

---

## 3. Mathematical Definitions of Evaluation Metrics

Let $y_i$ be the actual load value and $\hat{y}_i$ be the model prediction for test step $i=1, \dots, N$.

### 1. Mean Absolute Error (MAE)
$$\text{MAE} = \frac{1}{N} \sum_{i=1}^{N} |y_i - \hat{y}_i|$$

### 2. Root Mean Squared Error (RMSE)
$$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (y_i - \hat{y}_i)^2}$$

### 3. Symmetric Mean Absolute Percentage Error (sMAPE)
$$\text{sMAPE} = \frac{100\%}{N} \sum_{i=1}^{N} \frac{|y_i - \hat{y}_i|}{(|y_i| + |\hat{y}_i|) / 2}$$

### 4. Weighted Absolute Percentage Error (WAPE)
$$\text{WAPE} = \frac{\sum_{i=1}^{N} |y_i - \hat{y}_i|}{\sum_{i=1}^{N} |y_i|} \times 100\%$$

### 5. Baseline Improvement Percentage
$$\text{Improvement \%} = \left( \frac{\text{MAE}_{\text{baseline}} - \text{MAE}_{\text{candidate}}}{\text{MAE}_{\text{baseline}}} \right) \times 100\%$$
