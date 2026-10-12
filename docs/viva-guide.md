# Student Project Viva Preparation & Question Bank

This document serves as a comprehensive viva study guide for the project titled **"Predictive Modeling and Time-Series: AI-Driven Micro-Grid Renewable Energy Load Forecaster"**.

---

## 1. Project Abstract
Micro-grids integrate localized renewable power generators (Solar PV, Wind Turbines) alongside battery storage systems and variable consumer loads. Due to the intermittent nature of solar irradiance and wind speeds, accurate short-term load forecasting is essential to maintain grid stability, optimize energy storage dispatch, and minimize grid reliance. This project implements a web-based decision support system using FastAPI, React (Vite), Scikit-Learn, and Recharts. The system automates CSV data quality auditing, engineers temporal and autoregressive features, executes chronological holdout validation to prevent data leakage, trains machine learning forecasters (Random Forest, Ridge Regression, Gradient Boosting, Holt-Winters), and displays forecasts with 95% confidence intervals on an interactive dashboard.

---

## 2. Problem Statement
Existing traditional power grids rely on centralized baseline generation, which cannot accommodate localized microgrid intermittency efficiently. In microgrid operations:
- Random weather variations cause solar and wind power fluctuations.
- Over-estimating demand leads to wasted battery capacity or costly grid imports.
- Under-estimating demand causes blackouts or battery over-discharge.
- Standard random train/test data splitting in ML introduces severe future data leakage, making offline accuracy metrics falsely optimistic.

---

## 3. Existing System vs. Proposed System

| Parameter | Existing System / Baseline | Proposed AI-Driven Forecaster |
| :--- | :--- | :--- |
| **Data Validation** | Manual inspection or raw ingestion without audit | Automated Quality Audit (Quality Score %, interval detection, bounds check) |
| **Validation Method** | Random K-Fold Split (Suffers from future data leakage) | Strict Chronological Holdout Split (80% Train, 20% Test) |
| **Forecasting Algorithm** | Static rules or simple persistence naive | Multi-model ML (Random Forest, Ridge, Gradient Boosting, Holt-Winters) |
| **Metrics Evaluated** | Single metric (MAE or RMSE only) | Multi-Metric (MAE, RMSE, sMAPE, WAPE, R², % vs Baseline) |
| **Visualization & UX** | Static CSV files or basic spreadsheets | Interactive React Dashboard with historical, holdout, and 95% confidence bands |

---

## 4. Key Modules & Algorithms

1. **Ingestion & Quality Audit Module**: Validates uploaded files, cleans missing values using linear interpolation, detects duplicate timestamps, checks signal min/max bounds, and generates a Quality Audit Report.
2. **Feature Engineering Module**: Converts timestamps into temporal signals (`hour`, `dayofweek`, `month`, `hour_sin`, `hour_cos`) and autoregressive lag features (`lag_1`, `lag_2`, `lag_24`, `rolling_mean_6`, `rolling_mean_24`).
3. **Forecasting Engine**:
   - **Persistence Naive Baseline**: Predicts $\hat{y}_{t+h} = y_t$.
   - **Seasonal Naive Baseline**: Predicts 24-hour seasonal lag $\hat{y}_{t+h} = y_{t+h-24}$.
   - **Supervised ML Regressors**: Trains Random Forest, Ridge, and Gradient Boosting on training features.
   - **Holt-Winters Exponential Smoothing**: Captures trend and 24-hour additive seasonality.
4. **Evaluation & Visualization Module**: Computes holdout test set MAE, RMSE, sMAPE, WAPE, and R², generates future forecasts with 95% prediction intervals, and enables 1-click CSV export.

---

## 5. Top 25 Viva Questions and Detailed Answers

### Q1: What is the main objective of this project?
**Answer**: To develop a full-stack time-series forecasting web application that predicts short-term micro-grid load and renewable generation, compares candidate machine learning models against seasonal baselines using chronological holdout validation, and presents interactive forecasts and exportable CSV reports to assist grid operators.

### Q2: Why is load forecasting important for micro-grids?
**Answer**: Micro-grids combine localized renewable generation with energy storage systems (batteries). Accurate load forecasts enable grid management systems to schedule battery charging/discharging, prevent supply shortages, minimize expensive peak grid energy imports, and ensure grid stability.

### Q3: What is data leakage in time-series forecasting, and how does your project prevent it?
**Answer**: Data leakage occurs when information from future observations leaks into past training features (e.g. using random train/test splits or calculating global feature scalers/rolling averages across the entire dataset before splitting). We prevent it by enforcing a strict **chronological split** (80% historical train, 20% holdout test) and computing all scalers and lag features using training data only.

### Q4: Why do you evaluate models against a Seasonal Naive baseline?
**Answer**: Electrical load exhibits strong 24-hour daily periodicity (e.g., peak demand at 8 AM and 7 PM). A candidate machine learning model must outperform a simple 24-hour seasonal persistence model (which assumes today's 8 AM load equals yesterday's 8 AM load) to prove that its learned features add genuine predictive value.

### Q5: What features did you engineer from the timestamp column?
**Answer**: We engineered temporal features including `hour` (0–23), `dayofweek` (0–6), `month` (1–12), `is_weekend` (0 or 1), cyclical trigonometric features (`hour_sin` and `hour_cos`), and target autoregressive features (`target_lag_1`, `target_lag_2`, `target_lag_24`, `target_rolling_mean_6`, `target_rolling_mean_24`).

### Q6: Why do you encode hour as sine and cosine (`hour_sin`, `hour_cos`)?
**Answer**: Hours are cyclical: hour 23 (11 PM) and hour 0 (12 AM) are adjacent in time. Numerical integer encoding treats 23 and 0 as distant numbers. Trigonometric transformation $\sin(2\pi \cdot \text{hour} / 24)$ and $\cos(2\pi \cdot \text{hour} / 24)$ maps hour 23 and hour 0 to neighboring points in continuous 2D space.

### Q7: What is the difference between MAE and RMSE?
**Answer**: MAE (Mean Absolute Error) measures the average magnitude of prediction errors in absolute terms. RMSE (Root Mean Squared Error) squares the errors before taking the average and square root, giving higher penalty to large outlier prediction errors.

### Q8: What is sMAPE, and why is it preferred over standard MAPE?
**Answer**: Standard MAPE divides error by actual value $y_i$, which causes division-by-zero or extreme percentages when actual load values are close to zero. sMAPE (Symmetric MAPE) normalizes the absolute error by the average of actual and predicted values $(|y_i| + |\hat{y}_i|)/2$, bounding the percentage between 0% and 200%.

### Q9: What is WAPE?
**Answer**: WAPE (Weighted Absolute Percentage Error) divides the sum of absolute prediction errors by the total sum of actual values: $\text{WAPE} = \frac{\sum |y_i - \hat{y}_i|}{\sum y_i} \times 100\%$. It provides a scale-adjusted error percentage that is unaffected by near-zero individual timestamps.

### Q10: How does your application handle missing values in uploaded CSV datasets?
**Answer**: Our validation engine identifies missing cells, calculates the missing percentage, and applies linear interpolation across continuous time-series power signals. Silent row dropping is avoided so that fixed hourly sampling intervals remain intact for lag calculations.

### Q11: How do you calculate the 95% confidence bounds for future forecasts?
**Answer**: We calculate the standard deviation of residuals ($\sigma_e$) on the holdout test set: $\text{Residual} = y_{\text{test}} - \hat{y}_{\text{test}}$. Assuming normally distributed residuals, the 95% prediction interval for future step $h$ is computed as $\hat{y}_{t+h} \pm 1.96 \cdot \sigma_e$.

### Q12: Explain how recursive multi-step forecasting works for future horizons.
**Answer**: For step $t+1$, the model uses known historical lags to predict $\hat{y}_{t+1}$. For step $t+2$, the predicted value $\hat{y}_{t+1}$ is fed back as the lag-1 feature (`target_lag_1`) alongside updated cyclical hour features to recursively generate predictions step-by-step up to horizon $H$.

### Q13: What machine learning algorithms are implemented in your system?
**Answer**: 
1. **Random Forest / Boosted Trees**: Non-linear ensemble model.
2. **Ridge Regression**: Linear model with L2 regularization.
3. **Pure Gradient Boosting**: Sequential residual boosting.
4. **Holt-Winters Exponential Smoothing**: Double exponential trend with 24-hour additive seasonality.

### Q14: What technology stack is used for the backend?
**Answer**: Python 3.14, FastAPI for REST API, Pydantic v2 for request/response validation, SQLAlchemy for database ORM, and SQLite for local persistence.

### Q15: What technology stack is used for the frontend?
**Answer**: React 18, Vite, Recharts for time-series charts, Lucide-React for UI icons, Axios for backend HTTP requests, and custom CSS design tokens.

### Q16: How does the backend communicate with the frontend?
**Answer**: Over a versioned REST API (`/api/v1`) using JSON request and response payloads, with explicit CORS middleware enabled.

### Q17: What endpoints are available in your REST API?
**Answer**:
- `GET /health` — Health check
- `POST /datasets/upload` — CSV upload and quality audit
- `GET /datasets` & `GET /datasets/{id}/preview` — List & preview records
- `POST /forecast-runs` — Execute forecasting run
- `GET /forecast-runs/{id}/predictions` — Retrieve predictions
- `GET /forecast-runs/{id}/export` — Download CSV export

### Q18: What is SQLite, and why was it chosen for this project?
**Answer**: SQLite is a lightweight, serverless, file-based relational database. It is ideal for local student projects because it requires zero separate database server configuration while fully supporting SQL queries via SQLAlchemy.

### Q19: What validation checks are performed during dataset upload?
**Answer**:
1. File extension validation (.csv or .xlsx).
2. Timestamp column identification and datetime parsing.
3. Duplicate timestamp detection and deduplication.
4. Sampling frequency inference (e.g. 1 Hour).
5. Missing value detection and percentage calculation.
6. Negative value check for physical power signals.

### Q20: How is the Data Quality Score calculated?
**Answer**: Starting from a base score of 100%, points are deducted proportionally based on missing value percentage ($1.5 \times \text{missing}\%$), duplicate timestamps ($2 \times \text{duplicates}$), and invalid unparseable timestamps ($5 \times \text{invalid}$).

### Q21: What is the difference between active power (kW) and energy (kWh)?
**Answer**: Power (kW) is the instantaneous rate of electricity consumption or generation. Energy (kWh) is the integral of power over time (e.g., running a 1 kW load for 1 hour consumes 1 kWh of energy).

### Q22: Can your system forecast signals other than total load?
**Answer**: Yes. The user can select any numeric power signal in the dataset as the target variable, such as `solar_generation_kW`, `wind_generation_kW`, `grid_import_kW`, or `battery_soc`.

### Q23: What are the main limitations of the current project?
**Answer**:
1. Does not include real-time live IoT telemetry hardware sensors.
2. Weather forecasting data (temperature, cloud cover) relies on historical dataset features rather than live external weather API integrations.
3. Offline local execution model without cloud deployment.

### Q24: What future enhancements can be added to this project?
**Answer**:
1. Integrating Deep Learning models (LSTM / GRU / Temporal Fusion Transformers).
2. Live OpenWeatherMap API integration for real-time irradiance forecasting.
3. Automated battery dispatch optimization algorithm based on load forecasts.
4. Multi-tenant user authentication and cloud deployment on AWS/Docker.

### Q25: Why shouldn't these forecasts be used directly for physical microgrid control?
**Answer**: ML forecasts are statistical estimates subject to model error and unexpected weather fluctuations. Physical microgrid operations require hardware safety interlocks, over-current protection relays, and strict manual or PLC control overrides.
