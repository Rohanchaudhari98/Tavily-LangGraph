"""
LangGraph workflow for competitive intelligence.

Orchestrates all agents in sequence to produce competitive intelligence reports.
"""

from langgraph.graph import StateGraph, END
from typing import Dict, List
from datetime import datetime
import logging

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
    Build the competitive intelligence workflow.

    Connects 5 agents with conditional routing and parallel execution:
    - Discovery Agent (optional)
    - Research Agent
    - Extraction Agent (parallel with Crawl)
    - Crawl Agent (parallel with Extraction)
    - Analysis Agent
    """

    logger.info("Building workflow...")

    # Initialize agents
    discovery_agent = CompetitorDiscoveryAgent(tavily_api_key, openai_api_key)
    research_agent = ResearchAgent(tavily_api_key)
    extraction_agent = ExtractionAgent(tavily_api_key)
    crawl_agent = CrawlAgent(tavily_api_key)
    analysis_agent = AnalysisAgent(openai_api_key, use_premium_analysis, query_id, db)

    logger.info(f"Agents initialized: Discovery, Research, Extraction, Crawl, Analysis")

    # Create workflow graph
    workflow = StateGraph(CompetitiveIntelligenceState)

    # Add agent nodes
    workflow.add_node("discovery", discovery_agent.execute)
    workflow.add_node("research", research_agent.execute)
    workflow.add_node("extraction", extraction_agent.execute)
    workflow.add_node("crawl", crawl_agent.execute)
    workflow.add_node("analyze", analysis_agent.execute)

    # Conditional entry: start with discovery if auto-discovery enabled
    def route_start(state: CompetitiveIntelligenceState) -> str:
        use_auto_discovery = False
        if isinstance(state, dict):
            use_auto_discovery = state.get("use_auto_discovery", False)
        elif hasattr(state, "use_auto_discovery"):
            use_auto_discovery = getattr(state, "use_auto_discovery", False)
        if isinstance(use_auto_discovery, str):
            use_auto_discovery = use_auto_discovery.lower() in ("true", "1", "yes")
        else:
            use_auto_discovery = bool(use_auto_discovery)
        return "discovery" if use_auto_discovery else "research"

    workflow.set_conditional_entry_point(
        route_start,
        {"discovery": "discovery", "research": "research"}
    )

    # Join node: waits for extraction and crawl to complete
    def join_data_collection(state: CompetitiveIntelligenceState) -> CompetitiveIntelligenceState:
        return {**state, "current_step": "data_collection_complete"}

    workflow.add_node("join_data", join_data_collection)

    # Connect edges
    workflow.add_edge("discovery", "research")
    workflow.add_edge("research", "extraction")
    workflow.add_edge("research", "crawl")
    workflow.add_edge("extraction", "join_data")
    workflow.add_edge("crawl", "join_data")
    workflow.add_edge("join_data", "analyze")
    workflow.add_edge("analyze", END)

    logger.info("Workflow compiled: START → [discovery OR research] → [extraction + crawl] → join_data → analyze → END")

    return workflow.compile()


def create_initial_state(
    query: str,
    company_name: str,
    competitors: List[str],
    use_auto_discovery: bool = False,
    max_competitors: int = 5,
    freshness: str = "anytime"
) -> CompetitiveIntelligenceState:
    """
    Create initial workflow state with input parameters and empty results.
    """

    initial_state = CompetitiveIntelligenceState(
        # Input
        query=query,
        company_name=company_name,
        competitors=competitors,
        use_auto_discovery=use_auto_discovery,
        max_competitors=max_competitors,
        freshness=freshness,

        # Empty results
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

    return initial_state
