"""
FastAPI application for competitive intelligence system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.routes import router
from app.config import settings
import uvicorn

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Competitive Intelligence API",
    description="Multi-agent system for competitive intelligence using LangGraph and Tavily",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

origins = [
    "https://d13qhhlvt9ye93.cloudfront.net",  # CloudFront frontend
    "https://www.tavilyapp.com",   
    "https://tavilyapp.com",
    "http://localhost:5173"
]

# CORS middleware - Allow all origins for AWS deployment
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
async def root(db: MongoDBService = Depends(get_db)):
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