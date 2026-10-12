import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.database import engine, Base, run_migrations
from app.api import health, datasets, forecast_runs

# Create database tables and apply non-destructive SQLite migrations
Base.metadata.create_all(bind=engine)
run_migrations()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="REST API for AI-Driven Micro-Grid Renewable Energy Load Forecaster",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS explicitly
cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(health.router)  # Direct /health endpoint
app.include_router(datasets.router, prefix=settings.API_V1_STR)
app.include_router(forecast_runs.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "Welcome to AI-Driven Micro-Grid Renewable Energy Load Forecaster API",
        "docs": "/docs",
        "health": "/health"
    }
