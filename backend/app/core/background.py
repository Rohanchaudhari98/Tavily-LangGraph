"""
Background job runner for executing workflows.

Runs LangGraph workflows asynchronously and updates MongoDB with results.
"""

import asyncio
from datetime import datetime
from typing import Dict, List
import logging

from app.graph.workflow import (
    create_competitive_intelligence_workflow,
    create_initial_state
)
from app.services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)


async def run_workflow_background(
    query_id: str,
    query: str,
    company_name: str,
    competitors: List[str],
    use_premium_analysis: bool,
    use_auto_discovery: bool,
    max_competitors: int,
    freshness: str,  # NEW
    tavily_api_key: str,
    openai_api_key: str,
    db: MongoDBService
):
    """Run the workflow in the background"""
    
    from app.graph.workflow import create_competitive_intelligence_workflow, create_initial_state
    
    logger.info(f"Starting workflow for query {query_id}")
    
    try:
        # Create workflow
        workflow = create_competitive_intelligence_workflow(
            tavily_api_key=tavily_api_key,
            openai_api_key=openai_api_key,
            use_premium_analysis=use_premium_analysis
        )
        
        # Create initial state with new parameters
        initial_state = create_initial_state(
            query=query,
            company_name=company_name,
            competitors=competitors,
            use_auto_discovery=use_auto_discovery,
            max_competitors=max_competitors,
            freshness=freshness
        )
        
        # Run workflow
        final_state = await workflow.ainvoke(initial_state)
        
        # Update MongoDB with results
        await db.update_query(query_id, {
            "status": "completed",
            "analysis": final_state.get("analysis"),
            "competitors": final_state.get("competitors"),
            "company_info": final_state.get("company_info"),
            "research_results": final_state.get("research_results"),
            "extracted_data": final_state.get("extracted_data"),
            "crawl_results": final_state.get("crawl_results"),
            "completed_agents": final_state.get("completed_agents"),
            "errors": final_state.get("errors"),
            "completed_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        logger.info(f"Workflow completed for query {query_id}")
        
    except Exception as e:
        logger.error(f"Workflow failed for query {query_id}: {str(e)}")
        await db.update_query(query_id, {
            "status": "failed",
            "errors": [str(e)],
            "updated_at": datetime.now()
        })