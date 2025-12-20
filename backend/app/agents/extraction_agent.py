"""
Extraction Agent

Pulls full content from competitor URLs using Tavily Extract API
Handles JavaScript-rendered pages and returns clean text
"""

from tavily import TavilyClient
from typing import Dict, List
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

class ExtractionAgent:
    # Extracts clean content from URLs found during research
    def __init__(self, tavily_api_key: str):
        self.client = TavilyClient(api_key=tavily_api_key)
        self.name = "extraction"
    
    async def execute(self, state: Dict) -> Dict:
        # Extract content from all research URLs in parallel
        research_results = state.get("research_results", [])
        
        if not research_results:
            logger.warning("No research results to extract from")
            return {
                **state,
                "extracted_data": [],
                "errors": state.get("errors", []) + ["No research results available"]
            }
        
        logger.info("Starting extraction...")
        
        # Pull out URLs we want to extract
        urls_to_extract = self._collect_urls(research_results)
        
        logger.info(f"Found {len(urls_to_extract)} URLs to extract")
        
        if not urls_to_extract:
            logger.warning("No valid URLs in research results")
            return {
                **state,
                "extracted_data": [],
                "current_step": "extraction_complete",
                "completed_agents": state.get("completed_agents", []) + [self.name],
                "updated_at": datetime.now()
            }
        
        # Extract everything in parallel
        tasks = [
            self._extract_url(item) 
            for item in urls_to_extract
        ]
        
        logger.info(f"Extracting {len(tasks)} URLs in parallel...")
        extracted_data = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for failures
        processed_data = []
        for i, result in enumerate(extracted_data):
            if isinstance(result, Exception):
                logger.error(f"Failed to extract {urls_to_extract[i]['url']}: {str(result)}")
                processed_data.append({
                    "competitor": urls_to_extract[i]["competitor"],
                    "url": urls_to_extract[i]["url"],
                    "status": "error",
                    "error": str(result),
                    "extracted_at": datetime.now().isoformat()
                })
            else:
                processed_data.append(result)
        
        success_count = sum(1 for d in processed_data if d.get("status") == "success")
        logger.info(f"Extraction done: {success_count}/{len(processed_data)} successful")
        
        return {
            **state,
            "extracted_data": processed_data,
            "current_step": "extraction_complete",
            "completed_agents": state.get("completed_agents", []) + [self.name],
            "updated_at": datetime.now()
        }
    
    async def _extract_url(self, item: Dict) -> Dict:
        # Extract content from a single URL
        url = item["url"]
        competitor = item["competitor"]
        
        logger.info(f"Extracting: {url[:60]}...")
        
        try:
            # Tavily client is sync, wrap it to make it async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.extract(urls=[url])
            )
            
            # Check if we got content back
            if response and "results" in response and len(response["results"]) > 0:
                result = response["results"][0]
                raw_content = result.get("raw_content", "")
                
                logger.info(f"Got {len(raw_content)} characters from {competitor}")
                
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
                logger.warning(f"No content from {url}")
                return {
                    "competitor": competitor,
                    "url": url,
                    "status": "error",
                    "error": "No content in response",
                    "extracted_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Extraction error for {url}: {str(e)}")
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
        Grab the top URLs from research results
        Takes top 2 per competitor by default - usually enough for good coverage
        """
        urls_to_extract = []
        
        for result in research_results:
            # Skip if research failed for this competitor
            if result.get("status") != "success":
                logger.debug(f"Skipping {result.get('competitor')} - research failed")
                continue
            
            competitor = result.get("competitor")
            results_list = result.get("results", [])
            
            # Grab top N (Here 2) URLs for this competitor
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