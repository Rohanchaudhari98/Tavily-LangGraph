"""
API routes for the competitive intelligence system.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import List
from datetime import datetime
import logging

from .models import QueryRequest, QueryResponse, QueryResult, QueryListItem
from app.services.mongodb_service import MongoDBService
from app.core.background import run_workflow_background
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["competitive-intelligence"])

# Initialize MongoDB
db = MongoDBService(
    connection_string=settings.mongodb_uri,
    database_name=settings.mongodb_db_name
)


@router.post("/queries", response_model=QueryResponse)
async def create_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit a new competitive intelligence query.
    
    The workflow runs in the background, so this returns immediately.
    """
    
    logger.info(f"Received query: {request.query} for {request.company_name}")
    
    # Generate unique ID
    query_id = db.generate_id()
    
    # Save query to MongoDB
    query_doc = {
        "_id": query_id,
        "query": request.query,
        "company_name": request.company_name,
        "competitors": request.competitors,
        "use_premium_analysis": request.use_premium_analysis,
        "status": "processing",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "completed_at": None,
        "analysis": None,
        "research_results": [],
        "extracted_data": [],
        "crawl_results": [],
        "completed_agents": [],
        "errors": []
    }
    
    await db.insert_query(query_doc)
    logger.info(f"Query saved with ID: {query_id}")
    
    # Start workflow in background
    background_tasks.add_task(
        run_workflow_background,
        query_id=query_id,
        query=request.query,
        company_name=request.company_name,
        competitors=request.competitors,
        use_premium_analysis=request.use_premium_analysis,
        tavily_api_key=settings.tavily_api_key,
        openai_api_key=settings.openai_api_key,
        db=db
    )
    
    logger.info(f"Background task started for query {query_id}")
    
    return QueryResponse(
        query_id=query_id,
        status="processing",
        message=f"Query submitted successfully. Analyzing {len(request.competitors)} competitors.",
        created_at=datetime.now()
    )


@router.get("/queries/{query_id}", response_model=QueryResult)
async def get_query(query_id: str):
    """
    Get the results for a specific query.
    """
    
    logger.info(f"Fetching query: {query_id}")
    
    query = await db.get_query(query_id)
    
    if not query:
        logger.warning(f"Query not found: {query_id}")
        raise HTTPException(status_code=404, detail="Query not found")
    
    return QueryResult(
        query_id=query["_id"],
        status=query["status"],
        query=query["query"],
        company_name=query["company_name"],
        competitors=query["competitors"],
        analysis=query.get("analysis"),
        research_results=query.get("research_results"),
        extracted_data=query.get("extracted_data"),
        crawl_results=query.get("crawl_results"),
        completed_agents=query.get("completed_agents", []),
        errors=query.get("errors", []),
        analysis_mode=query.get("analysis_mode"),
        created_at=query["created_at"],
        updated_at=query["updated_at"],
        completed_at=query.get("completed_at")
    )


@router.get("/queries", response_model=List[QueryListItem])
async def list_queries(
    skip: int = 0,
    limit: int = 20
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
async def delete_query(query_id: str):
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