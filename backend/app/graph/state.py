"""
Shared state definition for the multi-agent system.

This state is passed between all agents and contains:
- Input data (query, competitors)
- Intermediate results from each agent
- Metadata (progress, errors)
"""

from typing import TypedDict, List, Dict, Optional, Annotated
from datetime import datetime
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    State dictionary shared across all agents in the workflow.
    
    TypedDict provides type hints but allows dynamic updates.
    Each agent can read from and write to this state.
    """
    
    # ===== INPUT DATA =====
    # These are set at the start and don't change
    query: str  # e.g., "What is their pricing strategy?"
    company_name: str  # e.g., "Acme Corp"
    competitors: List[str]  # e.g., ["CompanyA", "CompanyB"]
    
    # ===== AGENT OUTPUTS =====
    # Each agent populates its section
    research_results: List[Dict]  # From ResearchAgent (Tavily Search)
    extracted_data: List[Dict]   # From ExtractionAgent (Tavily Extract)
    crawl_results: List[Dict]    # From CrawlAgent (Tavily Crawl)
    analysis: Optional[str]      # From AnalysisAgent (GPT-4 synthesis)
    verification_status: Dict    # From VerificationAgent
    
    # ===== MESSAGES =====
    # LangGraph special: tracks conversation history
    # add_messages is a reducer that appends new messages
    messages: Annotated[List[Dict], add_messages]
    
    # ===== WORKFLOW METADATA =====
    current_step: str  # e.g., "research_complete", "analyzing"
    completed_agents: List[str]  # e.g., ["research", "extract"]
    errors: List[str]  # Any errors encountered
    next_agent: Optional[str]  # Which agent to run next
    
    # ===== TIMESTAMPS =====
    started_at: datetime
    updated_at: datetime


def create_initial_state(
    query: str,
    company_name: str,
    competitors: List[str]
) -> AgentState:
    """
    Factory function to create initial state.
    
    This ensures we always start with a valid state structure.
    """
    return {
        # Input
        "query": query,
        "company_name": company_name,
        "competitors": competitors,
        
        # Empty outputs
        "research_results": [],
        "extracted_data": [],
        "crawl_results": [],
        "analysis": None,
        "verification_status": {},
        
        # Empty messages
        "messages": [],
        
        # Workflow tracking
        "current_step": "initialized",
        "completed_agents": [],
        "errors": [],
        "next_agent": "research",  # Start with research
        
        # Timestamps
        "started_at": datetime.now(),
        "updated_at": datetime.now()
    }