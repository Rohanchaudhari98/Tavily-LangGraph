"""
Extraction Agent - Uses Tavily Extract API to get structured data from URLs.

This agent:
1. Takes URLs from Research Agent results
2. Extracts full content from those pages
3. Returns clean, structured data
"""

from tavily import TavilyClient
from typing import Dict, List
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

class ExtractionAgent:
    """
    Extracts structured data from competitor URLs using Tavily Extract API.
    
    Tavily Extract is powerful because:
    - Handles JavaScript-rendered content
    - Bypasses paywalls (where legally possible)
    - Returns clean text (no HTML parsing needed)
    - Fast and reliable
    """
    
    def __init__(self, tavily_api_key: str):
        """
        Initialize with Tavily API key.
        
        Args:
            tavily_api_key: Your Tavily API key
        """
        self.client = TavilyClient(api_key=tavily_api_key)
        self.name = "extraction"
    
    async def execute(self, state: Dict) -> Dict:
        """
        Extract content from research URLs IN PARALLEL.
        
        Args:
            state: Current workflow state with research_results
            
        Returns:
            Updated state with extracted_data populated
        """
        research_results = state.get("research_results", [])
        
        if not research_results:
            logger.warning("⚠️  No research results to extract from")
            return {
                **state,
                "extracted_data": [],
                "errors": state.get("errors", []) + ["No research results available"]
            }
        
        logger.info(f"🔬 Extraction Agent starting...")
        
        # Collect URLs to extract from
        urls_to_extract = self._collect_urls(research_results)
        
        logger.info(f"Found {len(urls_to_extract)} URLs to extract")
        
        if not urls_to_extract:
            logger.warning("⚠️  No valid URLs found in research results")
            return {
                **state,
                "extracted_data": [],
                "current_step": "extraction_complete",
                "completed_agents": state.get("completed_agents", []) + [self.name],
                "updated_at": datetime.now()
            }
        
        # Extract from all URLs in parallel
        tasks = [
            self._extract_url(item) 
            for item in urls_to_extract
        ]
        
        logger.info(f"🚀 Extracting from {len(tasks)} URLs in parallel...")
        extracted_data = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_data = []
        for i, result in enumerate(extracted_data):
            if isinstance(result, Exception):
                logger.error(f"❌ Extraction failed for {urls_to_extract[i]['url']}: {str(result)}")
                processed_data.append({
                    "competitor": urls_to_extract[i]["competitor"],
                    "url": urls_to_extract[i]["url"],
                    "status": "error",
                    "error": str(result),
                    "extracted_at": datetime.now().isoformat()
                })
            else:
                processed_data.append(result)
        
        # Count successes
        success_count = sum(1 for d in processed_data if d.get("status") == "success")
        logger.info(f"✅ Extraction complete. {success_count}/{len(processed_data)} successful")
        
        # Update state
        return {
            **state,
            "extracted_data": processed_data,
            "current_step": "extraction_complete",
            "completed_agents": state.get("completed_agents", []) + [self.name],
            "updated_at": datetime.now()
        }
    
    async def _extract_url(self, item: Dict) -> Dict:
        """
        Extract content from a single URL (async method).
        
        Args:
            item: Dictionary with url, competitor, title, score
            
        Returns:
            Extracted data for this URL
        """
        url = item["url"]
        competitor = item["competitor"]
        
        logger.info(f"Extracting: {url[:60]}...")
        
        try:
            # Tavily client is sync, so wrap in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.extract(urls=[url])
            )
            
            # Parse response
            if response and "results" in response and len(response["results"]) > 0:
                result = response["results"][0]
                raw_content = result.get("raw_content", "")
                
                logger.info(f"✅ Extracted {len(raw_content)} characters from {competitor}")
                
                return {
                    "competitor": competitor,
                    "url": url,
                    "title": item.get("title", ""),
                    "raw_content": raw_content,
                    "content_length": len(raw_content),
                    "extracted_at": datetime.now().isoformat(),
                    "status": "success"
                }
            else:
                logger.warning(f"⚠️  No content extracted from {url}")
                return {
                    "competitor": competitor,
                    "url": url,
                    "status": "error",
                    "error": "No content in response",
                    "extracted_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Extraction error for {url}: {str(e)}")
            return {
                "competitor": competitor,
                "url": url,
                "status": "error",
                "error": str(e),
                "extracted_at": datetime.now().isoformat()
            }
    
    def _collect_urls(
        self, 
        research_results: List[Dict], 
        max_per_competitor: int = 2
    ) -> List[Dict]:
        """
        Collect top URLs from research results.
        
        Args:
            research_results: Results from Research Agent
            max_per_competitor: Maximum URLs to extract per competitor (default: 2)
            
        Returns:
            List of URLs with metadata
        """
        urls_to_extract = []
        
        for result in research_results:
            # Skip failed research results
            if result.get("status") != "success":
                logger.debug(f"Skipping {result.get('competitor')} - research failed")
                continue
            
            competitor = result.get("competitor")
            results_list = result.get("results", [])
            
            # Take top N results per competitor
            for item in results_list[:max_per_competitor]:
                url = item.get("url")
                if url:
                    urls_to_extract.append({
                        "competitor": competitor,
                        "url": url,
                        "title": item.get("title", ""),
                        "score": item.get("score", 0)
                    })
        
        return urls_to_extract
    
    def __repr__(self):
        return f"ExtractionAgent(name={self.name})"