"""
API routes for the competitive intelligence system.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from typing import List
from datetime import datetime
import logging

from .models import QueryRequest, QueryResponse, QueryResult, QueryListItem
from app.services.mongodb_service import MongoDBService
from app.services.mongodb_dependency import get_db
from app.core.background import run_workflow_background
from app.config import settings
from app.utils.env import require_env

logger = logging.getLogger(__name__)

# Create router FIRST before using it
router = APIRouter(prefix="/api", tags=["competitive-intelligence"])

# Helper function for background task DB access
def get_db_for_background() -> MongoDBService:
    """Get MongoDB client safely for background tasks."""
    return get_db()


# Routes
@router.post("/queries", response_model=QueryResponse)
async def create_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    db: MongoDBService = Depends(get_db)
):
    """
    Submit a new competitive intelligence query.
    
    The workflow runs in the background, so this returns immediately.
    """
    
    # Validation: Must have either competitors OR auto-discovery enabled
    if not request.use_auto_discovery and len(request.competitors) == 0:
        raise HTTPException(
            status_code=400,
            detail="Must provide competitors OR enable auto-discovery"
        )
    
    if request.use_auto_discovery:
        logger.info(f"Auto-discovery query for {request.company_name} (max: {request.max_competitors})")
    else:
        logger.info(f"Manual query: {request.query} for {request.company_name}")
    
    logger.info(f"Freshness filter: {request.freshness}")
    
    # Generate unique ID
    query_id = db.generate_id()
    
    # Save query to MongoDB
    query_doc = {
        "_id": query_id,
        "query": request.query,
        "company_name": request.company_name,
        "competitors": request.competitors,
        "use_premium_analysis": request.use_premium_analysis,
        "use_auto_discovery": request.use_auto_discovery,
        "max_competitors": request.max_competitors,
        "freshness": request.freshness,
        "status": "processing",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "completed_at": None,
        "analysis": None,
        "company_info": None,
        "research_results": [],
        "extracted_data": [],
        "crawl_results": [],
        "completed_agents": [],
        "errors": []
    }
    
    await db.insert_query(query_doc)
    logger.info(f"Query saved with ID: {query_id}")
    
    # Enforce env vars for background workflow
    require_env("TAVILY_API_KEY", settings.tavily_api_key)
    require_env("OPENAI_API_KEY", settings.openai_api_key)
    
    # Start workflow in background
    background_tasks.add_task(
        run_workflow_background,
        query_id=query_id,
        query=request.query,
        company_name=request.company_name,
        competitors=request.competitors,
        use_premium_analysis=request.use_premium_analysis,
        use_auto_discovery=request.use_auto_discovery,
        max_competitors=request.max_competitors,
        freshness=request.freshness,
        tavily_api_key=settings.tavily_api_key,
        openai_api_key=settings.openai_api_key,
        db=get_db_for_background()
    )
    
    logger.info(f"Background task started for query {query_id}")
    
    # Different message based on mode
    if request.use_auto_discovery:
        message = f"Query submitted. AI will discover up to {request.max_competitors} competitors."
    else:
        message = f"Query submitted successfully. Analyzing {len(request.competitors)} competitors."
    
    return QueryResponse(
        query_id=query_id,
        status="processing",
        message=message,
        created_at=datetime.now()
    )


@router.get("/queries/{query_id}", response_model=QueryResult)
async def get_query(
    query_id: str,
    db: MongoDBService = Depends(get_db)
):
    """
    Get the results for a specific query.
    """
    
    logger.info(f"Fetching query: {query_id}")
    
    query = await db.get_query(query_id)
    
    if not query:
        logger.warning(f"Query not found: {query_id}")
        raise HTTPException(status_code=404, detail="Query not found")
    
    # Calculate total agents based on whether discovery was used
    use_auto_discovery = query.get("use_auto_discovery", False)
    total_agents = 5 if use_auto_discovery else 4
    
    return QueryResult(
        query_id=query["_id"],
        status=query["status"],
        query=query["query"],
        company_name=query["company_name"],
        competitors=query["competitors"],
        freshness=query.get("freshness", "anytime"),
        analysis=query.get("analysis"),
        chart_data=query.get("chart_data"),
        research_results=query.get("research_results"),
        extracted_data=query.get("extracted_data"),
        crawl_results=query.get("crawl_results"),
        completed_agents=query.get("completed_agents", []),
        errors=query.get("errors", []),
        analysis_mode=query.get("analysis_mode"),
        company_info=query.get("company_info"),
        total_agents=total_agents,
        use_auto_discovery=use_auto_discovery,
        created_at=query["created_at"],
        updated_at=query["updated_at"],
        completed_at=query.get("completed_at")
    )


@router.get("/queries", response_model=List[QueryListItem])
async def list_queries(
    skip: int = 0,
    limit: int = 20,
    db: MongoDBService = Depends(get_db)
):
    """
    List all queries (most recent first).
    """
    
    logger.info(f"Listing queries (skip={skip}, limit={limit})")
    
    queries = await db.list_queries(skip=skip, limit=limit)
    
    return [
        QueryListItem(
            query_id=q["_id"],
            query=q["query"],
            company_name=q["company_name"],
            competitor_count=len(q["competitors"]),
            status=q["status"],
            created_at=q["created_at"]
        )
        for q in queries
    ]


@router.delete("/queries/{query_id}")
async def delete_query(
    query_id: str,
    db: MongoDBService = Depends(get_db)
):
    """
    Delete a query and its results.
    """
    
    logger.info(f"Deleting query: {query_id}")
    
    success = await db.delete_query(query_id)
    
    if not success:
        logger.warning(f"Query not found for deletion: {query_id}")
        raise HTTPException(status_code=404, detail="Query not found")
    
    logger.info(f"Query deleted: {query_id}")
    
    return {"message": "Query deleted successfully"}