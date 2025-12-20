"""
Crawl Agent - Deep crawls competitor websites using Tavily API.

This agent:
1. Takes URLs from Research Agent results
2. Deep crawls competitor websites (pricing, features, docs pages)
3. Discovers hidden information not found in basic extraction
4. Returns comprehensive content from multiple related pages
"""

from tavily import TavilyClient
from typing import Dict, List
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

class CrawlAgent:
    """
    Deep crawls competitor websites to find comprehensive information.
    
    Goes beyond single-page extraction to discover:
    - Hidden pricing tiers (enterprise, volume discounts)
    - Complete feature documentation across multiple pages
    - Integration guides and API docs
    - Customer testimonials and case studies
    
    Uses Tavily's ability to follow links and extract from multiple pages.
    """
    
    def __init__(self, tavily_api_key: str):
        """
        Initialize with Tavily API key.
        
        Args:
            tavily_api_key: Your Tavily API key
        """
        self.client = TavilyClient(api_key=tavily_api_key)
        self.name = "crawl"
    
    async def execute(self, state: Dict) -> Dict:
        """
        Deep crawl competitor websites for comprehensive analysis.
        
        Args:
            state: Current workflow state with research_results
            
        Returns:
            Updated state with crawl_results populated
        """
        research_results = state.get("research_results", [])
        
        if not research_results:
            logger.warning("No research results to crawl from")
            return {
                **state,
                "crawl_results": [],
                "errors": state.get("errors", []) + ["No research results for crawling"]
            }
        
        logger.info(f"Crawl Agent starting...")
        
        # Collect URLs to crawl
        urls_to_crawl = self._collect_crawl_urls(research_results)
        
        logger.info(f"Found {len(urls_to_crawl)} URLs to deep crawl")
        
        if not urls_to_crawl:
            logger.warning("No valid URLs found for crawling")
            return {
                **state,
                "crawl_results": [],
                "current_step": "crawl_complete",
                "completed_agents": state.get("completed_agents", []) + [self.name],
                "updated_at": datetime.now()
            }
        
        # Crawl all URLs in parallel
        tasks = [
            self._crawl_competitor_site(item) 
            for item in urls_to_crawl
        ]
        
        logger.info(f"Crawling {len(tasks)} competitor sites in parallel...")
        crawl_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
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
        
        # Count successes
        success_count = sum(1 for r in processed_results if r.get("status") == "success")
        logger.info(f"Crawl complete. {success_count}/{len(processed_results)} successful")
        
        # Update state
        return {
            **state,
            "crawl_results": processed_results,
            "current_step": "crawl_complete",
            "completed_agents": state.get("completed_agents", []) + [self.name],
            "updated_at": datetime.now()
        }
    
    async def _crawl_competitor_site(self, item: Dict) -> Dict:
        """
        Deep crawl a single competitor's website.
        
        Args:
            item: Dictionary with competitor, url, and focus area
            
        Returns:
            Crawled data from the competitor site
        """
        competitor = item["competitor"]
        start_url = item["url"]
        focus = item.get("focus", "pricing")
        
        logger.info(f"Crawling {competitor} - {focus} section from {start_url[:60]}...")
        
        try:
            # Use Tavily's search with site-specific query to simulate crawl
            # This gets multiple pages from the same domain
            loop = asyncio.get_event_loop()
            
            # Construct search query to find related pages
            site_domain = self._extract_domain(start_url)
            crawl_query = f"site:{site_domain} {focus} features pricing plans"
            
            response = await loop.run_in_executor(
                None,
                lambda: self.client.search(
                    query=crawl_query,
                    search_depth="advanced",
                    max_results=5,  # Get 5 related pages from same site
                    include_domains=[site_domain]
                )
            )
            
            # Extract content from all found pages
            all_content = []
            urls_found = []
            
            for result in response.get("results", []):
                content = result.get("content", "")
                url = result.get("url", "")
                
                if content:
                    all_content.append(content)
                    urls_found.append(url)
            
            # Combine all content
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
        Collect URLs to crawl from research results.
        
        Prioritizes pricing and features pages for deep crawling.
        
        Args:
            research_results: Results from Research Agent
            max_per_competitor: URLs to crawl per competitor (default: 1)
            
        Returns:
            List of URLs with metadata for crawling
        """
        urls_to_crawl = []
        
        for result in research_results:
            # Skip failed research results
            if result.get("status") != "success":
                logger.debug(f"Skipping {result.get('competitor')} - research failed")
                continue
            
            competitor = result.get("competitor")
            results_list = result.get("results", [])
            
            # Find best URL to crawl from (prioritize pricing/features)
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
        Find the best URL to start crawling from.
        
        Prioritizes:
        1. Pricing pages
        2. Features pages
        3. Documentation pages
        4. Homepage
        
        Args:
            results: List of search results
            
        Returns:
            Dict with url and focus area
        """
        # Priority keywords for crawling
        priorities = [
            ("pricing", ["pricing", "plans", "cost"]),
            ("features", ["features", "capabilities", "product"]),
            ("documentation", ["docs", "documentation", "api"]),
            ("homepage", [""])  # Fallback
        ]
        
        for focus, keywords in priorities:
            for result in results:
                url = result.get("url", "").lower()
                title = result.get("title", "").lower()
                
                # Check if any keyword matches
                if any(keyword in url or keyword in title for keyword in keywords if keyword):
                    return {
                        "url": result["url"],
                        "focus": focus
                    }
        
        # Fallback to first result
        if results:
            return {
                "url": results[0]["url"],
                "focus": "general"
            }
        
        return None
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL for site-specific search.
        
        Args:
            url: Full URL
            
        Returns:
            Domain name (e.g., "stripe.com")
        """
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]
        
        return domain
    
    def __repr__(self):
        return f"CrawlAgent(name={self.name})"