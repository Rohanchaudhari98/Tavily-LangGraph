"""
LangGraph workflow for competitive intelligence.

Orchestrates all agents in sequence to produce competitive intelligence reports.
"""

from langgraph.graph import StateGraph, END
from typing import Dict, List
from datetime import datetime
import logging
import os

from .state import CompetitiveIntelligenceState
from app.agents.discovery_agent import CompetitorDiscoveryAgent
from app.agents.research_agent import ResearchAgent
from app.agents.extraction_agent import ExtractionAgent
from app.agents.crawl_agent import CrawlAgent
from app.agents.analysis_agent import AnalysisAgent

logger = logging.getLogger(__name__)


def create_competitive_intelligence_workflow(
    tavily_api_key: str,
    openai_api_key: str,
    use_premium_analysis: bool = False,
    query_id: str = None,
    db = None
) -> StateGraph:
    """
    Build the competitive intelligence workflow using LangGraph.
    
    Connects 5 agents with conditional routing and parallel execution:
    1. Discovery Agent (optional) - Finds competitors
    2. Research Agent - Searches via Tavily
    3. Extraction Agent - Gets page content via Tavily (runs in parallel with Crawl)
    4. Crawl Agent - Deep dives into sites via Tavily (runs in parallel with Extraction)
    5. Analysis Agent - Synthesizes everything with GPT-4
    
    Note: Extraction and Crawl run in parallel after Research completes,
    then both must finish before Analysis starts.
    """
    
    logger.info("Building workflow...")
    
    # Initialize all agents
    discovery_agent = CompetitorDiscoveryAgent(
        tavily_api_key=tavily_api_key,
        openai_api_key=openai_api_key
    )
    research_agent = ResearchAgent(tavily_api_key=tavily_api_key)
    extraction_agent = ExtractionAgent(tavily_api_key=tavily_api_key)
    crawl_agent = CrawlAgent(tavily_api_key=tavily_api_key)
    analysis_agent = AnalysisAgent(
        openai_api_key=openai_api_key,
        use_premium=use_premium_analysis,
        query_id=query_id,
        db=db
    )
    
    logger.info(f"Agents initialized:")
    logger.info(f"  - Discovery (GPT-4 + Tavily)")
    logger.info(f"  - Research (Tavily Search)")
    logger.info(f"  - Extraction (Tavily Extract)")
    logger.info(f"  - Crawl (Tavily Crawl)")
    logger.info(f"  - Analysis ({'GPT-4o' if use_premium_analysis else 'GPT-4o-mini'})")
    
    # Build the graph
    workflow = StateGraph(CompetitiveIntelligenceState)
    
    # Add nodes for each agent
    workflow.add_node("discovery", discovery_agent.execute)
    workflow.add_node("research", research_agent.execute)
    workflow.add_node("extraction", extraction_agent.execute)
    workflow.add_node("crawl", crawl_agent.execute)
    workflow.add_node("analyze", analysis_agent.execute)
    
    logger.info("Nodes added to graph")
    
    def route_start(state: CompetitiveIntelligenceState) -> str:
        """
        Decide whether to start with discovery or jump to research.
        Returns 'discovery' if auto-discovery enabled, otherwise 'research'.
        """
        # Access state - handle both dict and object access
        use_auto_discovery = False
        
        if isinstance(state, dict):
            use_auto_discovery = state.get("use_auto_discovery", False)
        elif hasattr(state, "use_auto_discovery"):
            use_auto_discovery = getattr(state, "use_auto_discovery", False)
        elif hasattr(state, "get"):
            use_auto_discovery = state.get("use_auto_discovery", False)
        
        # Ensure it's a boolean
        if isinstance(use_auto_discovery, str):
            use_auto_discovery = use_auto_discovery.lower() in ("true", "1", "yes")
        else:
            use_auto_discovery = bool(use_auto_discovery) if use_auto_discovery is not None else False
        
        # Log full state for debugging
        logger.info(f"Routing function called - state type: {type(state)}")
        if isinstance(state, dict):
            logger.info(f"State keys: {list(state.keys())}")
            logger.info(f"use_auto_discovery in state: {'use_auto_discovery' in state}")
            logger.info(f"use_auto_discovery value: {state.get('use_auto_discovery')}")
        logger.info(f"Routing decision - use_auto_discovery: {use_auto_discovery}")
        
        if use_auto_discovery:
            logger.info("Auto-discovery enabled - starting with discovery agent")
            return "discovery"
        else:
            logger.info("Manual competitors provided - starting with research")
            return "research"
    
    # Set up conditional entry point
    workflow.set_conditional_entry_point(
        route_start,
        {
            "discovery": "discovery",
            "research": "research"
        }
    )
    
    # Join node to ensure both extraction and crawl complete before analysis
    def join_data_collection(state: CompetitiveIntelligenceState) -> CompetitiveIntelligenceState:
        """
        Join node that waits for both extraction and crawl to complete.
        This ensures analysis only runs after both agents finish.
        """
        logger.info("Data collection complete - both extraction and crawl finished")
        return {
            **state,
            "current_step": "data_collection_complete"
        }
    
    # Add join node
    workflow.add_node("join_data", join_data_collection)
    
    # Connect the agents
    workflow.add_edge("discovery", "research")
    
    # Fan out from research to both extraction and crawl (parallel execution)
    workflow.add_edge("research", "extraction")
    workflow.add_edge("research", "crawl")
    
    # Both extraction and crawl must complete before join
    workflow.add_edge("extraction", "join_data")
    workflow.add_edge("crawl", "join_data")
    
    # Join to analysis
    workflow.add_edge("join_data", "analyze")
    workflow.add_edge("analyze", END)
    
    logger.info("Flow: START → [discovery OR research] → [extraction + crawl (parallel)] → join_data → analyze → END")
    
    # Compile and return
    compiled_workflow = workflow.compile()
    
    logger.info("Workflow compiled and ready")
    
    return compiled_workflow


def create_initial_state(
    query: str,
    company_name: str,
    competitors: List[str],
    use_auto_discovery: bool = False,
    max_competitors: int = 5,
    freshness: str = "anytime"
) -> CompetitiveIntelligenceState:
    """
    Create the initial state for the workflow.
    Sets up input parameters and empty result lists.
    """
    
    logger.info(f"Creating initial state:")
    logger.info(f"  Query: {query}")
    logger.info(f"  Company: {company_name}")
    logger.info(f"  Freshness: {freshness}")
    
    if use_auto_discovery:
        logger.info(f"  Auto-Discovery: Enabled (max: {max_competitors})")
    else:
        logger.info(f"  Competitors: {', '.join(competitors)}")
    
    initial_state = CompetitiveIntelligenceState(
        # Input
        query=query,
        company_name=company_name,
        competitors=competitors,
        use_auto_discovery=use_auto_discovery,
        max_competitors=max_competitors,
        freshness=freshness,
        
        # Empty results - agents will populate these
        company_info=None,
        research_results=[],
        extracted_data=[],
        crawl_results=[],
        analysis=None,
        chart_data=None,
        
        # Workflow tracking
        current_step="initialized",
        completed_agents=[],
        errors=[],
        
        # Timestamps
        started_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Verify the state was created correctly
    logger.info(f"Initial state created - use_auto_discovery type: {type(initial_state.get('use_auto_discovery'))}, value: {initial_state.get('use_auto_discovery')}")
    
    return initial_state