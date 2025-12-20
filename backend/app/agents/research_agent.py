"""
Research Agent

Searches the web for competitor information using Tavily Search API
Runs searches in parallel for speed and supports time-based filtering
"""

from tavily import TavilyClient
from typing import Dict, List, Optional
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

class ResearchAgent:
    # Handles web search for all competitors using Tavily
    def __init__(self, tavily_api_key: str):
        self.client = TavilyClient(api_key=tavily_api_key)
        self.name = "research"
    
    async def execute(self, state: Dict) -> Dict:
        # Run searches for all competitors in parallel
        query = state["query"]
        competitors = state["competitors"]
        freshness = state.get("freshness", "anytime")
        
        logger.info(f"Starting research for query: '{query}'")
        logger.info(f"Searching {len(competitors)} competitors: {competitors}")
        logger.info(f"Time filter: {freshness}")
        
        # Convert freshness setting to days for the API
        days = self._convert_freshness_to_days(freshness)
        if days:
            logger.info(f"Limiting to last {days} days")
        
        # Set up parallel searches
        tasks = [
            self._search_competitor(competitor, query, days) 
            for competitor in competitors
        ]
        
        logger.info(f"Running {len(tasks)} searches in parallel...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for any failures
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
        
        logger.info(f"Research complete: {len(competitors)} competitors searched")
        
        return {
            **state,
            "research_results": processed_results,
            "current_step": "research_complete",
            "completed_agents": state.get("completed_agents", []) + [self.name],
            "updated_at": datetime.now()
        }
    
    def _convert_freshness_to_days(self, freshness: str) -> Optional[int]:
        # Map freshness setting to days for Tavily API
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
        # Search for one competitor - called in parallel with others
        search_query = f"{competitor} {query}"
        
        logger.info(f"Searching: {search_query}" + (f" (last {days} days)" if days else ""))
        
        try:
            # Build search parameters
            search_params = {
                "query": search_query,
                "search_depth": "advanced",
                "max_results": 5,
                "include_answer": True,
                "include_raw_content": False,
                "include_domains": [],
                "exclude_domains": ["wikipedia.org"]  # Skip wiki, we want company sites
            }
            
            if days is not None:
                search_params["days"] = days
            
            # Tavily client is sync, wrap it to make it async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.search(**search_params)
            )
            
            results_count = len(response.get('results', []))
            logger.info(f"Got {results_count} results for {competitor}")
            
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
            logger.error(f"Search failed for {competitor}: {str(e)}")
            return {
                "competitor": competitor,
                "query": search_query,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def __repr__(self):
        return f"ResearchAgent(name={self.name})"