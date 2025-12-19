"""
State Definition for Competitive Intelligence Workflow.

This defines the shared state that flows between agents.
Each agent reads from and writes to this state.
"""

from typing import TypedDict, List, Dict, Optional, Literal
from datetime import datetime


class CompetitiveIntelligenceState(TypedDict):
    """
    Shared state for the competitive intelligence workflow.
    
    This state object is passed between all agents and contains:
    - Input parameters (query, company, competitors)
    - Outputs from each agent
    - Workflow metadata
    """
    
    # ===== INPUT PARAMETERS =====
    query: str
    """The research query (e.g., 'pricing strategy and features')"""
    
    company_name: str
    """The company conducting the analysis (e.g., 'Tavily')"""
    
    competitors: List[str]
    """List of competitor names to analyze (populated by discovery or manual entry)"""
    
    use_auto_discovery: bool
    """Whether to use AI to automatically discover competitors"""
    
    max_competitors: int
    """Maximum number of competitors to discover (used by discovery agent)"""
    
    company_info: Optional[Dict]
    """
    Information about the company from discovery agent.
    Contains: industry, description, search_terms
    """
    
    # Freshness filter
    freshness: str
    """Time range for search results: anytime, 1month, 3months, 6months, 1year"""
    
    # ===== AGENT OUTPUTS =====
    research_results: List[Dict]
    """
    Output from Research Agent.
    Each dict contains:
    - competitor: str
    - status: str ('success' or 'error')
    - results: List[Dict] (search results)
    - answer: str (AI-generated summary)
    """
    
    extracted_data: List[Dict]
    """
    Output from Extraction Agent.
    Each dict contains:
    - competitor: str
    - url: str
    - status: str
    - raw_content: str (extracted text)
    - content_length: int
    """
    
    crawl_results: List[Dict]
    """
    Output from Crawl Agent.
    Each dict contains:
    - competitor: str
    - pages_crawled: int
    - urls_found: List[str]
    - combined_content: str
    - status: str
    """
    
    analysis: Optional[str]
    """
    Output from Analysis Agent.
    Comprehensive competitive intelligence report (markdown format).
    """

    chart_data: Optional[Dict]
    """Structured data for charts (pricing, features, risks)"""
    
    # ===== WORKFLOW METADATA =====
    current_step: str
    """Current step in the workflow (e.g., 'discovery', 'research', 'extraction')"""
    
    completed_agents: List[str]
    """List of agents that have completed execution"""
    
    errors: List[str]
    """List of error messages encountered during execution"""
    
    # ===== TIMESTAMPS =====
    started_at: datetime
    """When the workflow started"""
    
    updated_at: datetime
    """Last update timestamp"""