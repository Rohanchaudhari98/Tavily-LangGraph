"""
Crawl Agent

Deep crawls competitor websites to find information across multiple pages
Focuses on pricing, features, and documentation sections
"""

from tavily import TavilyClient
from typing import Dict, List
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

class CrawlAgent:
    # Crawls competitor sites to gather comprehensive information from multiple pages
    def __init__(self, tavily_api_key: str):
        self.client = TavilyClient(api_key=tavily_api_key)
        self.name = "crawl"
    
    async def execute(self, state: Dict) -> Dict:
        # Deep crawl competitor websites for thorough analysis
        research_results = state.get("research_results", [])
        
        if not research_results:
            logger.warning("No research results to crawl")
            return {
                **state,
                "crawl_results": [],
                "errors": state.get("errors", []) + ["No research results for crawling"]
            }
        
        logger.info("Starting deep crawl...")
        
        # Pick starting URLs for each competitor
        urls_to_crawl = self._collect_crawl_urls(research_results)
        
        logger.info(f"Found {len(urls_to_crawl)} sites to crawl")
        
        if not urls_to_crawl:
            logger.warning("No valid URLs for crawling")
            return {
                **state,
                "crawl_results": [],
                "current_step": "crawl_complete",
                "completed_agents": state.get("completed_agents", []) + [self.name],
                "updated_at": datetime.now()
            }
        
        # Crawl everything in parallel
        tasks = [
            self._crawl_competitor_site(item)
            for item in urls_to_crawl
        ]
        
        logger.info(f"Crawling {len(tasks)} sites in parallel...")
        crawl_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for failures
        processed_results = []
        for i, result in enumerate(crawl_results):
            if isinstance(result, Exception):
                logger.error(f"Crawl failed for {urls_to_crawl[i]['competitor']}: {str(result)}")
                processed_results.append({
                    "competitor": urls_to_crawl[i]["competitor"],
                    "url": urls_to_crawl[i]["url"],
                    "status": "error",
                    "error": str(result),
                    "crawled_at": datetime.now().isoformat()
                })
            else:
                processed_results.append(result)
        
        success_count = sum(1 for r in processed_results if r.get("status") == "success")
        logger.info(f"Crawl done: {success_count}/{len(processed_results)} successful")
        
        return {
            **state,
            "crawl_results": processed_results,
            "current_step": "crawl_complete",
            "completed_agents": state.get("completed_agents", []) + [self.name],
            "updated_at": datetime.now()
        }
    
    async def _crawl_competitor_site(self, item: Dict) -> Dict:
        # Crawl one competitor's site to find related pages
        competitor = item["competitor"]
        start_url = item["url"]
        focus = item.get("focus", "pricing")
        
        logger.info(f"Crawling {competitor} - {focus} section from {start_url[:60]}...")
        
        try:
            # Use site-specific search to find related pages
            loop = asyncio.get_event_loop()
            
            site_domain = self._extract_domain(start_url)
            crawl_query = f"site:{site_domain} {focus} features pricing plans"
            
            response = await loop.run_in_executor(
                None,
                lambda: self.client.search(
                    query=crawl_query,
                    search_depth="advanced",
                    max_results=5,  # Grab up to 5 related pages
                    include_domains=[site_domain]
                )
            )
            
            # Pull content from all pages we found
            all_content = []
            urls_found = []
            
            for result in response.get("results", []):
                content = result.get("content", "")
                url = result.get("url", "")
                
                if content:
                    all_content.append(content)
                    urls_found.append(url)
            
            # Combine everything with page breaks
            combined_content = "\n\n---PAGE BREAK---\n\n".join(all_content)
            
            logger.info(f"Crawled {len(urls_found)} pages from {competitor} ({len(combined_content)} chars)")
            
            return {
                "competitor": competitor,
                "start_url": start_url,
                "focus": focus,
                "pages_crawled": len(urls_found),
                "urls_found": urls_found,
                "combined_content": combined_content,
                "content_length": len(combined_content),
                "crawled_at": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Crawl error for {competitor}: {str(e)}")
            return {
                "competitor": competitor,
                "start_url": start_url,
                "status": "error",
                "error": str(e),
                "crawled_at": datetime.now().isoformat()
            }
    
    def _collect_crawl_urls(
        self, 
        research_results: List[Dict],
        max_per_competitor: int = 1
    ) -> List[Dict]:
        """
        Pick the best starting URL for each competitor.
        We prefer pricing/features pages since they have the most useful info.
        """
        urls_to_crawl = []
        
        for result in research_results:
            if result.get("status") != "success":
                logger.debug(f"Skipping {result.get('competitor')} - research failed")
                continue
            
            competitor = result.get("competitor")
            results_list = result.get("results", [])
            
            # Find the best page to start from
            crawl_url = self._find_best_crawl_url(results_list)
            
            if crawl_url:
                urls_to_crawl.append({
                    "competitor": competitor,
                    "url": crawl_url["url"],
                    "focus": crawl_url["focus"]
                })
        
        return urls_to_crawl
    
    def _find_best_crawl_url(self, results: List[Dict]) -> Dict:
        """
        Pick the best starting point for crawling.
        Priority used here is pricing > features > docs > homepage
        """
        priorities = [
            ("pricing", ["pricing", "plans", "cost"]),
            ("features", ["features", "capabilities", "product"]),
            ("documentation", ["docs", "documentation", "api"]),
            ("homepage", [""])
        ]
        
        for focus, keywords in priorities:
            for result in results:
                url = result.get("url", "").lower()
                title = result.get("title", "").lower()
                
                # Check if this page matches our keywords
                if any(keyword in url or keyword in title for keyword in keywords if keyword):
                    return {
                        "url": result["url"],
                        "focus": focus
                    }
        
        # Just use the first result if nothing matches
        if results:
            return {
                "url": results[0]["url"],
                "focus": "general"
            }
        
        return None
    
    def _extract_domain(self, url: str) -> str:
        # Pull the domain from a full URL
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Strip www if present
        if domain.startswith("www."):
            domain = domain[4:]
        
        return domain
    
    def __repr__(self):
        return f"CrawlAgent(name={self.name})"