import json
import os
import pandas as pd
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import DatasetModel
from app.db.schemas import DatasetSchema, QualitySummary
from app.data.ingestion import save_and_validate_upload

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.post("/upload", response_model=DatasetSchema)
def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw_filename, raw_path, cleaned_filename, cleaned_path, df, clean_df, quality_summary = save_and_validate_upload(file)

    ts_col = quality_summary["timestamp_column"]
    start_time = str(df[ts_col].iloc[0]) if len(df) > 0 else None
    end_time = str(df[ts_col].iloc[-1]) if len(df) > 0 else None

    dataset_record = DatasetModel(
        filename=raw_filename,
        original_filename=file.filename,
        file_path=raw_path,
        cleaned_file_path=cleaned_path,
        cleaned_row_count=len(clean_df),
        row_count=len(df),
        timestamp_column=ts_col,
        start_time=start_time,
        end_time=end_time,
        time_interval=quality_summary["detected_frequency"],
        columns_json=json.dumps(list(df.columns)),
        quality_json=json.dumps(quality_summary)
    )

    db.add(dataset_record)
    db.commit()
    db.refresh(dataset_record)

    return dataset_record

@router.post("/sample", response_model=DatasetSchema)
def load_sample_dataset(db: Session = Depends(get_db)):
    import uuid
    from app.config import settings
    from app.data.validation import validate_dataframe

    # Find sample dataset
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    project_root = os.path.dirname(backend_dir)
    sample_path = os.path.join(project_root, "data", "sample", "microgrid_sample_hourly.csv")
    
    if not os.path.exists(sample_path):
        # Secondary fallback inside backend uploads
        sample_path = os.path.join(backend_dir, "data", "sample", "microgrid_sample_hourly.csv")
    
    if not os.path.exists(sample_path):
        raise HTTPException(status_code=404, detail=f"Sample dataset file not found at {sample_path}")

    try:
        df = pd.read_csv(sample_path)
        clean_df, quality_summary = validate_dataframe(df)

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_id = str(uuid.uuid4())[:8]
        safe_filename = f"dataset_sample_{file_id}.csv"
        saved_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
        clean_df.to_csv(saved_path, index=False)

        ts_col = quality_summary["timestamp_column"]
        start_time = str(clean_df[ts_col].iloc[0]) if len(clean_df) > 0 else None
        end_time = str(clean_df[ts_col].iloc[-1]) if len(clean_df) > 0 else None

        dataset_record = DatasetModel(
            filename=safe_filename,
            original_filename="microgrid_sample_hourly.csv",
            file_path=saved_path,
            row_count=len(clean_df),
            timestamp_column=ts_col,
            start_time=start_time,
            end_time=end_time,
            time_interval=quality_summary["detected_frequency"],
            columns_json=json.dumps(list(clean_df.columns)),
            quality_json=json.dumps(quality_summary)
        )

        db.add(dataset_record)
        db.commit()
        db.refresh(dataset_record)

        return dataset_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load sample dataset: {str(e)}")

@router.get("", response_model=List[DatasetSchema])
def list_datasets(db: Session = Depends(get_db)):
    return db.query(DatasetModel).order_by(DatasetModel.created_at.desc()).all()

@router.get("/{dataset_id}", response_model=DatasetSchema)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.get("/{dataset_id}/preview")
def preview_dataset(dataset_id: int, limit: int = 50, db: Session = Depends(get_db)):
    dataset = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
    if not dataset or not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset or data file not found")

    df = pd.read_csv(dataset.file_path)
    preview_rows = df.head(limit).fillna("").to_dict(orient="records")
    return {
        "dataset_id": dataset.id,
        "filename": dataset.original_filename,
        "total_rows": dataset.row_count,
        "columns": dataset.columns,
        "preview": preview_rows
    }

@router.get("/{dataset_id}/quality", response_model=QualitySummary)
def get_dataset_quality(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset.quality
