"""
LangGraph Workflow for Competitive Intelligence.

Orchestrates all the agents in sequence to produce competitive intelligence.
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
    use_premium_analysis: bool = False
) -> StateGraph:
    """
    Create the competitive intelligence workflow using LangGraph.
    
    Wires up 5 agents with conditional routing:
    1. Discovery Agent (optional) - Auto-discovers competitors
    2. Research Agent - Finds competitor info via Tavily Search
    3. Extraction Agent - Gets detailed content via Tavily Extract
    4. Crawl Agent - Deep dives into sites via Tavily Crawl
    5. Analysis Agent - Synthesizes everything via GPT-4
    
    Args:
        tavily_api_key: API key for Tavily
        openai_api_key: API key for OpenAI
        use_premium_analysis: True for GPT-4o, False for GPT-4o-mini
        
    Returns:
        Compiled workflow ready to run
    """
    
    logger.info("🏗️  Building competitive intelligence workflow...")
    
    # Set up all the agents
    discovery_agent = CompetitorDiscoveryAgent(
        tavily_api_key=tavily_api_key,
        openai_api_key=openai_api_key
    )
    research_agent = ResearchAgent(tavily_api_key=tavily_api_key)
    extraction_agent = ExtractionAgent(tavily_api_key=tavily_api_key)
    crawl_agent = CrawlAgent(tavily_api_key=tavily_api_key)
    analysis_agent = AnalysisAgent(
        openai_api_key=openai_api_key,
        use_premium=use_premium_analysis
    )
    
    logger.info(f" Agents initialized:")
    logger.info(f"   - Discovery Agent (GPT-4 + Tavily)")
    logger.info(f"   - Research Agent (Tavily Search)")
    logger.info(f"   - Extraction Agent (Tavily Extract)")
    logger.info(f"   - Crawl Agent (Tavily Crawl)")
    logger.info(f"   - Analysis Agent ({'GPT-4o' if use_premium_analysis else 'GPT-4o-mini'})")
    
    # Create the graph
    workflow = StateGraph(CompetitiveIntelligenceState)
    
    # Add each agent as a node
    workflow.add_node("discovery", discovery_agent.execute)
    workflow.add_node("research", research_agent.execute)
    workflow.add_node("extraction", extraction_agent.execute)
    workflow.add_node("crawl", crawl_agent.execute)
    workflow.add_node("analyze", analysis_agent.execute)
    
    logger.info("Nodes added to graph")
    
    # Define conditional routing function
    def route_start(state: CompetitiveIntelligenceState) -> str:
        """
        Decide whether to start with discovery or skip to research.
        
        Returns 'discovery' if auto-discovery is enabled, otherwise 'research'
        """
        if state.get("use_auto_discovery", False):
            logger.info("🔍 Auto-discovery enabled - starting with discovery agent")
            return "discovery"
        else:
            logger.info("📋 Manual competitors provided - skipping to research")
            return "research"
    
    # Set conditional entry point
    workflow.set_conditional_entry_point(
        route_start,
        {
            "discovery": "discovery",
            "research": "research"
        }
    )
    
    # Define the flow between agents
    workflow.add_edge("discovery", "research")  # Discovery → Research
    workflow.add_edge("research", "extraction")
    workflow.add_edge("extraction", "crawl")
    workflow.add_edge("crawl", "analyze")
    workflow.add_edge("analyze", END)
    
    logger.info("Edges defined:")
    logger.info("   START → [discovery OR research] → extraction → crawl → analyze → END")
    
    # Compile into a runnable workflow
    compiled_workflow = workflow.compile()
    
    logger.info("Workflow compiled successfully!")
    logger.info("   Ready to process competitive intelligence queries")
    
    return compiled_workflow


def create_initial_state(
    query: str,
    company_name: str,
    competitors: List[str],
    use_auto_discovery: bool = False,
    max_competitors: int = 5,
    freshness: str = "anytime"  # NEW
) -> CompetitiveIntelligenceState:
    """
    Set up the initial state for the workflow.
    
    Creates the state dict with input parameters and empty result lists
    that will be filled in by each agent.
    
    Args:
        query: What to research (e.g., "pricing strategy")
        company_name: Your company (e.g., "Tavily")
        competitors: List of competitors (empty if using auto-discovery)
        use_auto_discovery: Whether to auto-discover competitors
        max_competitors: Max competitors to discover (if auto-discovery enabled)
        freshness: Time range filter for search results
        
    Returns:
        Initial state ready for the workflow
    """
    
    logger.info(f"Creating initial state:")
    logger.info(f"   Query: {query}")
    logger.info(f"   Company: {company_name}")
    logger.info(f"   Freshness: {freshness}")
    
    if use_auto_discovery:
        logger.info(f"   Auto-Discovery: Enabled (max: {max_competitors})")
    else:
        logger.info(f"   Competitors: {', '.join(competitors)}")
    
    return CompetitiveIntelligenceState(
        # Input parameters
        query=query,
        company_name=company_name,
        competitors=competitors,
        use_auto_discovery=use_auto_discovery,
        max_competitors=max_competitors,
        freshness=freshness,  # NEW
        
        # Empty results (agents will fill these in)
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