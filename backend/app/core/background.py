"""
Background job runner for executing workflows.

Runs LangGraph workflows asynchronously and updates MongoDB with results.
"""

import asyncio
from datetime import datetime
from typing import Dict
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
    competitors: list[str],
    use_premium_analysis: bool,
    tavily_api_key: str,
    openai_api_key: str,
    db: MongoDBService
):
    """
    Run the competitive intelligence workflow in the background.
    
    This function:
    1. Creates the LangGraph workflow
    2. Executes it with the given parameters
    3. Updates MongoDB with progress and results
    4. Handles any errors gracefully
    """
    
    logger.info(f"Starting workflow for query {query_id}")
    
    try:
        # Create the workflow
        workflow = create_competitive_intelligence_workflow(
            tavily_api_key=tavily_api_key,
            openai_api_key=openai_api_key,
            use_premium_analysis=use_premium_analysis
        )
        
        # Create initial state
        initial_state = create_initial_state(
            query=query,
            company_name=company_name,
            competitors=competitors
        )
        
        # Execute the workflow
        logger.info(f"Executing workflow for query {query_id}")
        final_state = await workflow.ainvoke(initial_state)
        
        # Save results to MongoDB
        logger.info(f"Saving results for query {query_id}")
        await db.update_query(
            query_id=query_id,
            update_data={
                "status": "completed",
                "analysis": final_state.get("analysis"),
                "research_results": final_state.get("research_results"),
                "extracted_data": final_state.get("extracted_data"),
                "crawl_results": final_state.get("crawl_results"),
                "completed_agents": final_state.get("completed_agents"),
                "errors": final_state.get("errors", []),
                "analysis_mode": final_state.get("analysis_mode"),
                "completed_at": datetime.now(),
                "updated_at": datetime.now()
            }
        )
        
        logger.info(f"Workflow completed successfully for query {query_id}")
        
    except Exception as e:
        logger.error(f"Workflow failed for query {query_id}: {str(e)}")
        
        # Update MongoDB with error status
        await db.update_query(
            query_id=query_id,
            update_data={
                "status": "failed",
                "errors": [str(e)],
                "updated_at": datetime.now()
            }
        )