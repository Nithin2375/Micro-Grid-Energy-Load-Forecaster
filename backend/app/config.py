import os

class Settings:
    PROJECT_NAME: str = "AI-Driven Micro-Grid Renewable Energy Load Forecaster"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./microgrid.db"
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    MAX_UPLOAD_SIZE_MB: int = 50

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
