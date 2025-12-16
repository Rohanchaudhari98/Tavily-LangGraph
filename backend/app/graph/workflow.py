"""
LangGraph Workflow for Competitive Intelligence.

Orchestrates all the agents in sequence to produce competitive intelligence.
"""

from langgraph.graph import StateGraph, END
from typing import Dict, List
from datetime import datetime
import logging

from .state import CompetitiveIntelligenceState
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
    
    Wires up 4 agents in sequence:
    1. Research Agent - Finds competitor info via Tavily Search
    2. Extraction Agent - Gets detailed content via Tavily Extract
    3. Crawl Agent - Deep dives into sites via Tavily Crawl
    4. Analysis Agent - Synthesizes everything via GPT-4
    
    Args:
        tavily_api_key: API key for Tavily
        openai_api_key: API key for OpenAI
        use_premium_analysis: True for GPT-4o, False for GPT-4o-mini
        
    Returns:
        Compiled workflow ready to run
    """
    
    logger.info("Building competitive intelligence workflow...")
    
    # Set up all the agents
    research_agent = ResearchAgent(tavily_api_key=tavily_api_key)
    extraction_agent = ExtractionAgent(tavily_api_key=tavily_api_key)
    crawl_agent = CrawlAgent(tavily_api_key=tavily_api_key)
    analysis_agent = AnalysisAgent(
        openai_api_key=openai_api_key,
        use_premium=use_premium_analysis
    )
    
    logger.info(f"Agents initialized:")
    logger.info(f"   - Research Agent (Tavily Search)")
    logger.info(f"   - Extraction Agent (Tavily Extract)")
    logger.info(f"   - Crawl Agent (Tavily Crawl)")
    logger.info(f"   - Analysis Agent ({'GPT-4o' if use_premium_analysis else 'GPT-4o-mini'})")
    
    # Create the graph
    workflow = StateGraph(CompetitiveIntelligenceState)
    
    # Add each agent as a node
    # Note: Can't use 'analysis' as node name since it's a state field
    workflow.add_node("research", research_agent.execute)
    workflow.add_node("extraction", extraction_agent.execute)
    workflow.add_node("crawl", crawl_agent.execute)
    workflow.add_node("analyze", analysis_agent.execute)  # Changed from "analysis" to "analyze"
    
    logger.info("Nodes added to graph")
    
    # Define the flow between agents
    workflow.add_edge("research", "extraction")
    workflow.add_edge("extraction", "crawl")
    workflow.add_edge("crawl", "analyze")  # Changed from "analysis" to "analyze"
    workflow.add_edge("analyze", END)  # Changed from "analysis" to "analyze"
    
    logger.info("Edges defined:")
    logger.info("   research → extraction → crawl → analyze → END")
    
    # Start with research
    workflow.set_entry_point("research")
    
    logger.info("Entry point set to 'research'")
    
    # Compile into a runnable workflow
    compiled_workflow = workflow.compile()
    
    logger.info("Workflow compiled successfully!")
    logger.info("   Ready to process competitive intelligence queries")
    
    return compiled_workflow


def create_initial_state(
    query: str,
    company_name: str,
    competitors: List[str]
) -> CompetitiveIntelligenceState:
    """
    Set up the initial state for the workflow.
    
    Creates the state dict with input parameters and empty result lists
    that will be filled in by each agent.
    
    Args:
        query: What to research (e.g., "pricing strategy")
        company_name: Your company (e.g., "Tavily")
        competitors: List of competitors to analyze
        
    Returns:
        Initial state ready for the workflow
    """
    
    logger.info(f"Creating initial state:")
    logger.info(f"   Query: {query}")
    logger.info(f"   Company: {company_name}")
    logger.info(f"   Competitors: {', '.join(competitors)}")
    
    return CompetitiveIntelligenceState(
        # Input parameters
        query=query,
        company_name=company_name,
        competitors=competitors,
        
        # Empty results (agents will fill these in)
        research_results=[],
        extracted_data=[],
        crawl_results=[],
        analysis=None,
        
        # Workflow tracking
        current_step="initialized",
        completed_agents=[],
        errors=[],
        
        # Timestamps
        started_at=datetime.now(),
        updated_at=datetime.now()
    )