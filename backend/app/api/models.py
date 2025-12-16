"""
Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for creating a competitive intelligence query"""
    
    query: str = Field(
        ...,
        description="What to research about competitors",
        min_length=3,
        max_length=500,
        examples=["AI search API pricing and features"]
    )
    
    company_name: str = Field(
        ...,
        description="Your company name",
        min_length=1,
        max_length=100,
        examples=["Tavily"]
    )
    
    competitors: List[str] = Field(
        ...,
        description="List of competitor names to analyze",
        min_length=1,
        max_length=10,
        examples=[["Perplexity AI", "You.com", "Exa"]]
    )
    
    use_premium_analysis: bool = Field(
        default=False,
        description="Use GPT-4o instead of GPT-4o-mini (slower, better quality)"
    )


class QueryResponse(BaseModel):
    """Response after submitting a query"""
    
    query_id: str = Field(
        ...,
        description="Unique ID for this query"
    )
    
    status: str = Field(
        ...,
        description="Current status",
        examples=["processing"]
    )
    
    message: str = Field(
        ...,
        description="Human-readable message"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When the query was created"
    )


class QueryResult(BaseModel):
    """Full results for a completed query"""
    
    query_id: str
    status: str  # "processing", "completed", "failed"
    
    # Input
    query: str
    company_name: str
    competitors: List[str]
    
    # Results (only present when completed)
    analysis: Optional[str] = None
    research_results: Optional[List[dict]] = None
    extracted_data: Optional[List[dict]] = None
    crawl_results: Optional[List[dict]] = None
    
    # Metadata
    completed_agents: List[str] = []
    errors: List[str] = []
    analysis_mode: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class QueryListItem(BaseModel):
    """Summary item for listing queries"""
    
    query_id: str
    query: str
    company_name: str
    competitor_count: int
    status: str
    created_at: datetime