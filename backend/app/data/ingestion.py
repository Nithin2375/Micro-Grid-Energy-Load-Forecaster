import os
import uuid
import pandas as pd
from fastapi import UploadFile, HTTPException
from app.config import settings
from app.data.validation import validate_dataframe

def save_and_validate_upload(file: UploadFile) -> tuple:
    """
    Saves the original uploaded dataset without modification, profiles it,
    and creates a separately stored cleaned version.
    Returns: (raw_filename, raw_path, cleaned_filename, cleaned_path, raw_df, clean_df, quality_summary)
    """
    if not (file.filename.endswith(".csv") or file.filename.endswith(".xlsx")):
        raise HTTPException(status_code=400, detail="Only CSV or Excel files (.csv, .xlsx) are supported.")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())[:8]
    ext = os.path.splitext(file.filename)[1]
    
    # 1. Preserve original uploaded file exactly
    raw_filename = f"raw_dataset_{file_id}{ext}"
    raw_path = os.path.join(settings.UPLOAD_DIR, raw_filename)

    try:
        with open(raw_path, "wb") as f:
            content = file.file.read()
            if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
                raise HTTPException(status_code=400, detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB.")
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    # 2. Parse file
    try:
        if ext == ".csv":
            raw_df = pd.read_csv(raw_path)
        else:
            raw_df = pd.read_excel(raw_path)
    except Exception as e:
        if os.path.exists(raw_path):
            os.remove(raw_path)
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV/Excel content: {str(e)}")

    if len(raw_df) == 0:
        if os.path.exists(raw_path):
            os.remove(raw_path)
        raise HTTPException(status_code=400, detail="Uploaded file contains no rows.")

    # 3. Validate & generate separate cleaned dataset
    try:
        clean_df, quality_summary = validate_dataframe(raw_df)
        cleaned_filename = f"cleaned_dataset_{file_id}.csv"
        cleaned_path = os.path.join(settings.UPLOAD_DIR, cleaned_filename)
        clean_df.to_csv(cleaned_path, index=False)
    except Exception as e:
        if os.path.exists(raw_path):
            os.remove(raw_path)
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")

    return raw_filename, raw_path, cleaned_filename, cleaned_path, raw_df, clean_df, quality_summary
