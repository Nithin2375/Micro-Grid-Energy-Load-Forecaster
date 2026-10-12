# 🚀 Deployment Guide: Vercel (Frontend) & Render (Backend)

This repository is pre-configured for seamless cloud deployment:
- **Backend API**: Hosted on **Render** (FastAPI, SQLite/PostgreSQL, ML engine)
- **Frontend UI**: Hosted on **Vercel** (React, Vite, Recharts Dashboard)

---

## Part 1: Deploy Backend on Render

### Option A: Using Render Blueprints (Recommended - 1 Click)
1. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Blueprint**.
2. Connect your GitHub repository: `https://github.com/Nithin2375/Micro-Grid-Energy-Load-Forecaster`.
3. Render will automatically detect [`render.yaml`](file:///c:/Users/nithi/.gemini/antigravity-ide/scratch/microgrid_load_forecaster/render.yaml) and configure the service.
4. Click **Apply**.
5. Once deployed, copy your backend URL (e.g., `https://microgrid-forecaster-api.onrender.com`).

---

### Option B: Manual Web Service Setup
If creating as a standard Web Service:
1. In Render Dashboard, click **New +** -> **Web Service**.
2. Connect `https://github.com/Nithin2375/Micro-Grid-Energy-Load-Forecaster`.
3. Configure the following fields:
   - **Name**: `microgrid-load-forecaster-api`
   - **Region**: Choose closest to you (e.g., Singapore, Frankfurt, Oregon)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `PYTHON_VERSION`: `3.11.9`
   - `DATABASE_URL`: `sqlite:///./microgrid.db`
   - `CORS_ORIGINS`: `*` (or your Vercel app domain once deployed)
5. Click **Create Web Service**.
6. When deployment finishes, test by opening: `https://<your-render-app>.onrender.com/health`.
   It should return: `{"status": "healthy", ...}`.

---

## Part 2: Deploy Frontend on Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New...** -> **Project**.
2. Import `https://github.com/Nithin2375/Micro-Grid-Energy-Load-Forecaster`.
3. In the project configuration:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click *Edit* and select **`frontend`**
   - **Build Command**: `npm run build` (detected automatically)
   - **Output Directory**: `dist` (detected automatically)
4. Expand **Environment Variables** and add:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://<your-render-backend-name>.onrender.com`
     *(Replace with your actual Render backend URL from Part 1)*
5. Click **Deploy**.

---

## Part 3: Verify the Deployed Application

1. Open your Vercel deployment URL (e.g., `https://micro-grid-energy-load-forecaster.vercel.app`).
2. Verify that the System Status badge in the top right shows **"System Online"** (green).
3. Click **"Load Sample Dataset"** on the Data Management page to populate the synthetic microgrid hourly data.
4. Go to **Model Training**, choose **Ridge Regression** or **Gradient Boosting**, and click **Train & Run Forecast**.
5. View forecast curves, renewable vs demand metrics, and export predictions on the **Export** page.

---

## Configuration Reference

| Environment Variable | Service | Default | Description |
|----------------------|---------|---------|-------------|
| `VITE_API_BASE_URL` | Frontend | `http://localhost:8000` | Points frontend Axios requests to the deployed backend |
| `DATABASE_URL` | Backend | `sqlite:///./microgrid.db` | Database connection string (SQLite file or PostgreSQL URL) |
| `CORS_ORIGINS` | Backend | `*` | Allowed CORS origins (comma-separated or `*`) |
| `PORT` | Backend | Dynamic (Render) | Port assigned by Render runtime |
