import os
import pytest
import pandas as pd
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_microgrid.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_dataset_upload_and_forecast_flow():
    # 1. Upload sample CSV with valid dates
    dates = pd.date_range("2026-01-01", periods=48, freq="h")
    lines = ["timestamp,load_kW,solar_generation_kW"]
    for i, dt in enumerate(dates):
        lines.append(f"{dt.strftime('%Y-%m-%d %H:%M:%S')},{150 + i*2},{i*5}")
    csv_content = "\n".join(lines)
    
    response = client.post(
        "/api/v1/datasets/upload",
        files={"file": ("test_data.csv", csv_content, "text/csv")}
    )
    assert response.status_code == 200
    dataset = response.json()
    dataset_id = dataset["id"]
    assert dataset["row_count"] == 48

    # 2. Preview & Quality summary
    preview_res = client.get(f"/api/v1/datasets/{dataset_id}/preview")
    assert preview_res.status_code == 200
    assert len(preview_res.json()["preview"]) <= 48

    quality_res = client.get(f"/api/v1/datasets/{dataset_id}/quality")
    assert quality_res.status_code == 200
    assert quality_res.json()["quality_score"] > 80

    # 3. Create Forecast Run
    run_payload = {
        "dataset_id": dataset_id,
        "target_column": "load_kW",
        "model_name": "RandomForest",
        "horizon": 12
    }
    run_res = client.post("/api/v1/forecast-runs", json=run_payload)
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert run_data["status"] == "COMPLETED"
    assert "mae" in run_data["metrics"]

    # 4. Fetch predictions
    preds_res = client.get(f"/api/v1/forecast-runs/{run_data['id']}/predictions")
    assert preds_res.status_code == 200
    preds_data = preds_res.json()["predictions"]
    assert len(preds_data) > 0
    assert any(p["is_future"] for p in preds_data)

    # 5. Export CSV
    export_res = client.get(f"/api/v1/forecast-runs/{run_data['id']}/export")
    assert export_res.status_code == 200
    assert "text/csv" in export_res.headers["content-type"]
