import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
engine = create_engine(
    settings.DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_migrations():
    """
    Non-destructive SQLite migration ensuring existing databases
    automatically acquire enhanced columns without data loss.
    """
    if "sqlite" not in settings.DATABASE_URL:
        return

    db_path = settings.DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check datasets table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='datasets'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(datasets)")
            existing_cols = [row[1] for row in cursor.fetchall()]
            new_dataset_cols = [
                ("cleaned_file_path", "TEXT"),
                ("cleaned_row_count", "INTEGER"),
                ("cleaning_config_json", "TEXT DEFAULT '{}'"),
                ("cleaning_report_json", "TEXT DEFAULT '{}'")
            ]
            for col_name, col_type in new_dataset_cols:
                if col_name not in existing_cols:
                    cursor.execute(f"ALTER TABLE datasets ADD COLUMN {col_name} {col_type}")

        # Check forecast_runs table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='forecast_runs'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(forecast_runs)")
            existing_cols = [row[1] for row in cursor.fetchall()]
            new_run_cols = [
                ("validation_metrics_json", "TEXT DEFAULT '{}'"),
                ("hourly_metrics_json", "TEXT DEFAULT '{}'"),
                ("dow_metrics_json", "TEXT DEFAULT '{}'"),
                ("model_artifact_path", "TEXT")
            ]
            for col_name, col_type in new_run_cols:
                if col_name not in existing_cols:
                    cursor.execute(f"ALTER TABLE forecast_runs ADD COLUMN {col_name} {col_type}")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Migration notice: {e}")
