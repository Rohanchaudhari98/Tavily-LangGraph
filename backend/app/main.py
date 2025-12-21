"""
FastAPI application for competitive intelligence system.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.routes import router
from app.config import settings
from app.services.mongodb_service import MongoDBService
from app.services.mongodb_dependency import get_db
from app.utils.logging_config import setup_logging
import uvicorn

# Set up logging with file output
setup_logging(log_level=settings.log_level, log_dir="logs")

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Competitive Intelligence API",
    description="Multi-agent system for competitive intelligence using LangGraph and Tavily",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Allowed origins for CORS
origins = [
    "https://d13qhhlvt9ye93.cloudfront.net",
    "https://www.tavilyapp.com",   
    "https://tavilyapp.com",
    "http://localhost:5173"
]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root(db: MongoDBService = Depends(get_db)):
    """Root endpoint with health check."""
    try:
        await db.ping()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    all_healthy = db_status == "ok"

    return {
        "message": "Competitive Intelligence API",
        "status": "healthy" if all_healthy else "unhealthy",
        "db_status": db_status,
        "environment": settings.environment,
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check(db: MongoDBService = Depends(get_db)):
    """Health check endpoint for monitoring."""
    try:
        await db.ping()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    all_healthy = db_status == "ok"

    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "db_status": db_status,
        "environment": settings.environment,
        "debug": settings.debug
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )