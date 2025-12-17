"""
Research Agent - Uses Tavily Search API to find competitor information.

This agent:
1. Takes query and competitors from state
2. Searches web for each competitor with optional time filtering
3. Returns search results to state

Tavily Search provides:
- Web search results with URLs
- AI-generated answer
- Relevant snippets
- Time-filtered results
"""

from tavily import TavilyClient
from typing import Dict, List, Optional
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    Searches the web for competitive intelligence using Tavily Search API.
    Now with parallel processing and freshness filtering!
    """
    
    def __init__(self, tavily_api_key: str):
        self.client = TavilyClient(api_key=tavily_api_key)
        self.name = "research"
    
    async def execute(self, state: Dict) -> Dict:
        """
        Execute research for all competitors IN PARALLEL.
        
        Args:
            state: Current workflow state with query, competitors, and freshness
            
        Returns:
            Updated state with research_results populated
        """
        query = state["query"]
        competitors = state["competitors"]
        freshness = state.get("freshness", "anytime")
        
        logger.info(f"Research Agent starting for query: '{query}'")
        logger.info(f"Competitors to research: {competitors}")
        logger.info(f"Freshness filter: {freshness}")
        
        # Convert freshness to days parameter
        days = self._convert_freshness_to_days(freshness)
        if days:
            logger.info(f"Filtering results to last {days} days")
        
        # Create tasks for all competitors
        tasks = [
            self._search_competitor(competitor, query, days) 
            for competitor in competitors
        ]
        
        # Run all searches in parallel
        logger.info(f"Running {len(tasks)} searches in parallel...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Search failed for {competitors[i]}: {str(result)}")
                processed_results.append({
                    "competitor": competitors[i],
                    "status": "error",
                    "error": str(result),
                    "timestamp": datetime.now().isoformat()
                })
            else:
                processed_results.append(result)
        
        logger.info(f"Research complete for {len(competitors)} competitors")
        
        return {
            **state,
            "research_results": processed_results,
            "current_step": "research_complete",
            "completed_agents": state.get("completed_agents", []) + [self.name],
            "updated_at": datetime.now()
        }
    
    def _convert_freshness_to_days(self, freshness: str) -> Optional[int]:
        """
        Convert freshness string to number of days for Tavily API.
        
        Args:
            freshness: One of "anytime", "1month", "3months", "6months", "1year"
            
        Returns:
            Number of days, or None for "anytime"
        """
        freshness_map = {
            "anytime": None,
            "1month": 30,
            "3months": 90,
            "6months": 180,
            "1year": 365
        }
        
        return freshness_map.get(freshness, None)
    
    async def _search_competitor(
        self, 
        competitor: str, 
        query: str,
        days: Optional[int] = None
    ) -> Dict:
        """
        Search for a single competitor with optional time filtering.
        
        This is now async so multiple calls can run concurrently.
        
        Args:
            competitor: Competitor name
            query: Search query
            days: Optional number of days to filter results (None = anytime)
            
        Returns:
            Search results for this competitor
        """
        search_query = f"{competitor} {query}"
        
        logger.info(f"Searching: {search_query}" + (f" (last {days} days)" if days else ""))
        
        try:
            # Prepare search parameters
            search_params = {
                "query": search_query,
                "search_depth": "advanced",
                "max_results": 5,
                "include_answer": True,
                "include_raw_content": False,
                "include_domains": [],
                "exclude_domains": ["wikipedia.org"]
            }
            
            # Add days parameter if freshness filter is set
            if days is not None:
                search_params["days"] = days
            
            # Tavily client is sync, so wrap in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,  # Use default executor
                lambda: self.client.search(**search_params)
            )
            
            results_count = len(response.get('results', []))
            logger.info(f"Found {results_count} results for {competitor}")
            
            return {
                "competitor": competitor,
                "query": search_query,
                "answer": response.get("answer", ""),
                "results": response.get("results", []),
                "freshness": days if days else "anytime",
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Search error for {competitor}: {str(e)}")
            return {
                "competitor": competitor,
                "query": search_query,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def __repr__(self):
        return f"ResearchAgent(name={self.name})"