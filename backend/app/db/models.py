import datetime
import json
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

class DatasetModel(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    cleaned_file_path = Column(String, nullable=True)
    cleaned_row_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    row_count = Column(Integer, default=0)
    timestamp_column = Column(String, nullable=False)
    start_time = Column(String, nullable=True)
    end_time = Column(String, nullable=True)
    time_interval = Column(String, nullable=True)
    columns_json = Column(Text, default="[]")
    quality_json = Column(Text, default="{}")
    cleaning_config_json = Column(Text, default="{}")
    cleaning_report_json = Column(Text, default="{}")

    runs = relationship("ForecastRunModel", back_populates="dataset", cascade="all, delete-orphan")

    @property
    def columns(self):
        return json.loads(self.columns_json or "[]")

    @property
    def quality(self):
        return json.loads(self.quality_json or "{}")

    @property
    def cleaning_config(self):
        return json.loads(self.cleaning_config_json or "{}")

    @property
    def cleaning_report(self):
        return json.loads(self.cleaning_report_json or "{}")

class ForecastRunModel(Base):
    __tablename__ = "forecast_runs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    target_column = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    horizon = Column(Integer, default=24)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    parameters_json = Column(Text, default="{}")
    metrics_json = Column(Text, default="{}")
    validation_metrics_json = Column(Text, default="{}")
    hourly_metrics_json = Column(Text, default="{}")
    dow_metrics_json = Column(Text, default="{}")
    model_artifact_path = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)

    dataset = relationship("DatasetModel", back_populates="runs")
    predictions = relationship("PredictionModel", back_populates="run", cascade="all, delete-orphan")

    @property
    def parameters(self):
        return json.loads(self.parameters_json or "{}")

    @property
    def metrics(self):
        return json.loads(self.metrics_json or "{}")

    @property
    def validation_metrics(self):
        return json.loads(self.validation_metrics_json or "{}")

    @property
    def hourly_metrics(self):
        return json.loads(self.hourly_metrics_json or "{}")

    @property
    def dow_metrics(self):
        return json.loads(self.dow_metrics_json or "{}")

class PredictionModel(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("forecast_runs.id"), nullable=False)
    timestamp = Column(String, nullable=False)
    actual_value = Column(Float, nullable=True)
    predicted_value = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)
    is_future = Column(Boolean, default=False)

    run = relationship("ForecastRunModel", back_populates="predictions")
