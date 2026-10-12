import json
import io
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import DatasetModel, ForecastRunModel, PredictionModel
from app.db.schemas import ForecastRunCreate, ForecastRunSchema, PredictionListResponse
from app.forecasting.pipeline import run_forecasting_pipeline

router = APIRouter(prefix="/forecast-runs", tags=["forecast-runs"])

@router.post("", response_model=ForecastRunSchema)
def create_forecast_run(payload: ForecastRunCreate, db: Session = Depends(get_db)):
    dataset = db.query(DatasetModel).filter(DatasetModel.id == payload.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    params = {
        "feature_columns": payload.feature_columns,
        "impute_missing": payload.impute_missing
    }

    run = ForecastRunModel(
        dataset_id=payload.dataset_id,
        target_column=payload.target_column,
        model_name=payload.model_name,
        horizon=payload.horizon,
        status="PENDING",
        parameters_json=json.dumps(params),
        metrics_json=json.dumps({})
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    # Run forecasting pipeline synchronously (or background execution)
    run_forecasting_pipeline(db, run.id)
    db.refresh(run)

    return run

@router.get("", response_model=List[ForecastRunSchema])
def list_forecast_runs(db: Session = Depends(get_db)):
    return db.query(ForecastRunModel).order_by(ForecastRunModel.created_at.desc()).all()

@router.get("/{run_id}", response_model=ForecastRunSchema)
def get_forecast_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(ForecastRunModel).filter(ForecastRunModel.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Forecast run not found")
    return run

@router.get("/{run_id}/predictions", response_model=PredictionListResponse)
def get_forecast_predictions(run_id: int, db: Session = Depends(get_db)):
    run = db.query(ForecastRunModel).filter(ForecastRunModel.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Forecast run not found")

    preds = db.query(PredictionModel).filter(PredictionModel.run_id == run_id).order_by(PredictionModel.id.asc()).all()

    return {
        "run_id": run.id,
        "target_column": run.target_column,
        "model_name": run.model_name,
        "predictions": [
            {
                "timestamp": p.timestamp,
                "actual_value": p.actual_value,
                "predicted_value": p.predicted_value,
                "lower_bound": p.lower_bound,
                "upper_bound": p.upper_bound,
                "is_future": p.is_future
            }
            for p in preds
        ]
    }

@router.get("/{run_id}/export")
def export_forecast_csv(run_id: int, db: Session = Depends(get_db)):
    run = db.query(ForecastRunModel).filter(ForecastRunModel.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Forecast run not found")

    preds = db.query(PredictionModel).filter(PredictionModel.run_id == run_id).order_by(PredictionModel.id.asc()).all()

    output = io.StringIO()
    output.write("timestamp,actual_value,predicted_value,lower_bound_95,upper_bound_95,is_future\n")
    for p in preds:
        act = p.actual_value if p.actual_value is not None else ""
        output.write(f"{p.timestamp},{act},{p.predicted_value},{p.lower_bound or ''},{p.upper_bound or ''},{p.is_future}\n")

    output.seek(0)
    filename = f"forecast_run_{run_id}_{run.model_name}.csv"
    headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    return Response(content=output.getvalue(), media_type="text/csv", headers=headers)
