# Student Project Setup & Execution Guide

This guide provides step-by-step instructions for installing prerequisites, configuring environment settings, starting the FastAPI backend server, running the React Vite frontend dashboard, executing automated unit tests, and troubleshooting common issues.

---

## 1. System Prerequisites

Ensure the following software packages are installed on your computer:
- **Python**: Version 3.10 or higher (Verified on Python 3.14.3)
- **Node.js**: Version 18 or higher (Verified on Node v24.14.0)
- **npm**: Version 9 or higher (Verified on npm 11.9.0)
- **Git** (optional, for version control)

---

## 2. Step-by-Step Installation

### Step A: Clone / Open Repository Directory
Open your terminal (PowerShell, Command Prompt, or Terminal) and navigate to the project directory:
```bash
cd microgrid_load_forecaster
```

### Step B: Backend Environment & Dependency Setup
1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```

2. (Optional but recommended) Create a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

4. Verify backend installation by running pytest:
   ```bash
   python -m pytest tests
   ```
   *Expected Output*: `8 passed in 1.86s`

### Step C: Frontend Dependency Setup
1. Open a new terminal window or navigate back to the root directory and enter `frontend`:
   ```bash
   cd ../frontend
   ```

2. Install Node packages:
   ```bash
   npm install
   ```

3. Verify frontend production build:
   ```bash
   npm run build
   ```
   *Expected Output*: `✓ built in 3.20s`

---

## 3. Running the Application

### Running Backend Server
From the `backend/` directory:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger API Documentation: `http://localhost:8000/docs`
- ReDoc API Documentation: `http://localhost:8000/redoc`
- Health Check Endpoint: `http://localhost:8000/health`

### Running Frontend Development Server
From the `frontend/` directory:
```bash
npm run dev
```
- Open your web browser and navigate to: `http://localhost:5173`

---

## 4. How to Use the Application (Student Workflow)

1. **Ingest Data**:
   - Open `http://localhost:5173`.
   - Click the **Data & Quality** tab.
   - Click **Load Sample Micro-Grid Dataset** to automatically seed the sample dataset, or upload your own CSV file containing a `timestamp` column and numeric power signals (e.g. `load_kW`).
   - Review the automated **Data Quality Audit Report** (Quality Score, missing values %, sampling frequency, column statistics, validation warnings).

2. **Train Models & Generate Forecasts**:
   - Click the **Model Training** tab.
   - Select your target signal (e.g., `load_kW`), forecasting model (e.g., `Random Forest`), and forecast horizon (e.g., `24 Hours`).
   - Click **Execute Forecast Pipeline**.
   - Review the **Model Performance Comparison Matrix** showing MAE, RMSE, sMAPE, WAPE, R², and % improvement over baseline.

3. **Explore Dashboard & Export Results**:
   - Click **Overview & Forecasts** to view the interactive time-series chart showing historical actuals, holdout test predictions, and future forecasts with 95% confidence bands.
   - Click **Export Results** to inspect prediction records and download the CSV report.

---

## 5. Troubleshooting & Common Errors

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'app'` | Running pytest from outside backend directory without PYTHONPATH | Run `python -m pytest tests` from inside the `backend` folder, or set `$env:PYTHONPATH="."` |
| `CORS Error in Browser` | Frontend connecting to different backend port | Ensure FastAPI backend is running on `http://localhost:8000` |
| `Port 8000 already in use` | Another process is using port 8000 | Kill existing process or run `uvicorn app.main:app --port 8001` and update `API_BASE_URL` in `frontend/src/services/api.js` |
| `CSV missing timestamp column` | Uploaded CSV doesn't have datetime column | Ensure your CSV includes a column named `timestamp`, `date`, or `datetime` |
