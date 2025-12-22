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
    # Run the workflow in the background
    
    from app.graph.workflow import create_competitive_intelligence_workflow, create_initial_state
    
    logger.info(f"Starting workflow for query {query_id}")
    
    try:
        # Set up workflow with API keys and streaming support
        workflow = create_competitive_intelligence_workflow(
            tavily_api_key=tavily_api_key,
            openai_api_key=openai_api_key,
            use_premium_analysis=use_premium_analysis,
            query_id=query_id,  # Pass query_id for streaming updates
            db=db  # Pass db for streaming updates
        )
        
        # Build initial state
        initial_state = create_initial_state(
            query=query,
            company_name=company_name,
            competitors=competitors,
            use_auto_discovery=use_auto_discovery,
            max_competitors=max_competitors,
            freshness=freshness
        )
        
        # Verify state before streaming
        logger.info(f"State before astream - use_auto_discovery: {initial_state.get('use_auto_discovery')}, type: {type(initial_state.get('use_auto_discovery'))}")
        
        # Use streaming to get real-time updates after each agent
        final_state = None
        last_analysis_update = None
        
        async for state in workflow.astream(initial_state):
            # state is a dict with node names as keys
            # Get the latest state from the last node that executed
            for node_name, node_state in state.items():
                final_state = node_state
            
            # Update MongoDB after each agent completes
            completed_agents = node_state.get("completed_agents", [])
            
            # Check if analysis is being generated (partial update)
            current_analysis = node_state.get("analysis")
            is_analysis_agent = node_name == "analyze" or "analysis" in completed_agents
            
            # Update MongoDB with current progress
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
            
            # If analysis exists (even partial), include it
            if current_analysis:
                update_data["analysis"] = current_analysis
                # Only update chart_data if analysis is complete (has all sections)
                if node_state.get("chart_data"):
                    update_data["chart_data"] = node_state.get("chart_data")
                
                    # Update less frequently during analysis generation on AWS (reduce DB overhead)
                    # Only update if analysis has grown significantly or every 5 seconds
                    if is_analysis_agent and current_analysis != last_analysis_update:
                        # Update if analysis grew by >500 chars or if it's been a while
                        should_update = (
                            len(current_analysis) - len(last_analysis_update or "") > 500
                        ) if last_analysis_update else True
                        
                        if should_update:
                            await db.update_query(query_id, update_data)
                            last_analysis_update = current_analysis
                            logger.info(f"Updated query {query_id}: Analysis streaming ({len(current_analysis)} chars)")
            elif completed_agents:
                # Regular agent completion update
                await db.update_query(query_id, update_data)
                logger.info(f"Updated query {query_id}: {len(completed_agents)} agents completed")
        
        # Final update with completed status
        if final_state:
            # Check if analysis agent completed successfully
            completed_agents = final_state.get("completed_agents", [])
            has_analysis = final_state.get("analysis") is not None
            
            # Determine status based on completion
            if "analysis" in completed_agents and has_analysis:
                status = "completed"
            elif "analysis" in completed_agents and not has_analysis:
                # Analysis agent ran but produced no output
                status = "completed"  # Still mark as completed, but with error
                errors = final_state.get("errors", [])
                if not any("analysis" in str(e).lower() for e in errors):
                    errors.append("Analysis completed but no content was generated")
                final_state["errors"] = errors
            else:
                # Analysis agent didn't complete
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
            # No final state - workflow stream may have ended unexpectedly
            logger.warning(f"Workflow stream ended without final state for query {query_id}")
            # Try to get the last known state from MongoDB
            try:
                last_query = await db.get_query(query_id)
                if last_query:
                    completed_agents = last_query.get("completed_agents", [])
                    if "analysis" in completed_agents:
                        # Analysis completed but stream ended before final update
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