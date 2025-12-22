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
    freshness: str,
    tavily_api_key: str,
    openai_api_key: str,
    db: MongoDBService
):
    # Start the workflow in the background
    from app.graph.workflow import create_competitive_intelligence_workflow, create_initial_state
    
    logger.info(f"Starting workflow for query {query_id}")
    
    try:
        # Initialize the workflow with API keys and streaming
        workflow = create_competitive_intelligence_workflow(
            tavily_api_key=tavily_api_key,
            openai_api_key=openai_api_key,
            use_premium_analysis=use_premium_analysis,
            query_id=query_id,
            db=db
        )
        
        # Build initial workflow state
        initial_state = create_initial_state(
            query=query,
            company_name=company_name,
            competitors=competitors,
            use_auto_discovery=use_auto_discovery,
            max_competitors=max_competitors,
            freshness=freshness
        )
        
        logger.info(f"Initial state prepared - use_auto_discovery: {initial_state.get('use_auto_discovery')}, type: {type(initial_state.get('use_auto_discovery'))}")
        
        final_state = None
        last_analysis_update = None
        
        # Stream workflow state updates
        async for state in workflow.astream(initial_state):
            for node_name, node_state in state.items():
                final_state = node_state
            
            completed_agents = node_state.get("completed_agents", [])
            current_analysis = node_state.get("analysis")
            is_analysis_agent = node_name == "analyze" or "analysis" in completed_agents
            
            # Prepare MongoDB update
            update_data = {
                "status": "processing",
                "competitors": node_state.get("competitors", []),
                "company_info": node_state.get("company_info"),
                "research_results": node_state.get("research_results", []),
                "extracted_data": node_state.get("extracted_data", []),
                "crawl_results": node_state.get("crawl_results", []),
                "completed_agents": completed_agents,
                "current_step": node_state.get("current_step", "processing"),
                "errors": node_state.get("errors", []),
                "updated_at": datetime.now()
            }
            
            # Include analysis if available
            if current_analysis:
                update_data["analysis"] = current_analysis
                if node_state.get("chart_data"):
                    update_data["chart_data"] = node_state.get("chart_data")
                
                # Only update DB when analysis grows significantly
                if is_analysis_agent and current_analysis != last_analysis_update:
                    should_update = (
                        len(current_analysis) - len(last_analysis_update or "") > 500
                    ) if last_analysis_update else True
                    
                    if should_update:
                        await db.update_query(query_id, update_data)
                        last_analysis_update = current_analysis
                        logger.info(f"Updated query {query_id}: Analysis streaming ({len(current_analysis)} chars)")
            elif completed_agents:
                # Update DB for other agents
                await db.update_query(query_id, update_data)
                logger.info(f"Updated query {query_id}: {len(completed_agents)} agents completed")
        
        # Final state update
        if final_state:
            completed_agents = final_state.get("completed_agents", [])
            has_analysis = final_state.get("analysis") is not None
            
            if "analysis" in completed_agents and has_analysis:
                status = "completed"
            elif "analysis" in completed_agents and not has_analysis:
                status = "completed"
                errors = final_state.get("errors", [])
                if not any("analysis" in str(e).lower() for e in errors):
                    errors.append("Analysis completed but no content was generated")
                final_state["errors"] = errors
            else:
                status = "failed"
            
            await db.update_query(query_id, {
                "status": status,
                "analysis": final_state.get("analysis"),
                "chart_data": final_state.get("chart_data"),
                "competitors": final_state.get("competitors"),
                "company_info": final_state.get("company_info"),
                "research_results": final_state.get("research_results"),
                "extracted_data": final_state.get("extracted_data"),
                "crawl_results": final_state.get("crawl_results"),
                "completed_agents": completed_agents,
                "errors": final_state.get("errors"),
                "completed_at": datetime.now() if status == "completed" else None,
                "updated_at": datetime.now()
            })
            
            logger.info(f"Workflow {'completed' if status == 'completed' else 'ended'} for query {query_id}")
        else:
            # Handle unexpected workflow end
            logger.warning(f"Workflow stream ended without final state for query {query_id}")
            try:
                last_query = await db.get_query(query_id)
                if last_query:
                    completed_agents = last_query.get("completed_agents", [])
                    if "analysis" in completed_agents:
                        await db.update_query(query_id, {
                            "status": "completed",
                            "completed_at": datetime.now(),
                            "updated_at": datetime.now()
                        })
                        logger.info(f"Marked query {query_id} as completed based on last known state")
                    else:
                        await db.update_query(query_id, {
                            "status": "failed",
                            "errors": ["Workflow stream ended unexpectedly"],
                            "updated_at": datetime.now()
                        })
            except Exception as e:
                logger.error(f"Failed to update query status from last known state: {e}")
        
    except Exception as e:
        logger.error(f"Workflow failed for query {query_id}: {str(e)}", exc_info=True)
        try:
            await db.update_query(query_id, {
                "status": "failed",
                "errors": [str(e)],
                "updated_at": datetime.now()
            })
        except Exception as db_error:
            logger.error(f"Failed to update query status to failed: {db_error}")
