from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Micro-Grid Renewable Energy Load Forecaster API",
        "version": "1.0.0"
    }
