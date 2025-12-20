"""
State definition for the competitive intelligence workflow.

Defines the shared state object that flows between agents.
Each agent reads from and writes to this state.
"""

from typing import TypedDict, List, Dict, Optional, Literal
from datetime import datetime


class CompetitiveIntelligenceState(TypedDict):
    # Shared state passed between all agents in the workflow
    
    # Input parameters
    query: str
    company_name: str
    competitors: List[str]
    use_auto_discovery: bool
    max_competitors: int
    company_info: Optional[Dict]
    freshness: str
    
    # Agent outputs
    research_results: List[Dict]
    extracted_data: List[Dict]
    crawl_results: List[Dict]
    analysis: Optional[str]
    chart_data: Optional[Dict]
    
    # Workflow metadata
    current_step: str
    completed_agents: List[str]
    errors: List[str]
    
    # Timestamps
    started_at: datetime
    updated_at: datetime