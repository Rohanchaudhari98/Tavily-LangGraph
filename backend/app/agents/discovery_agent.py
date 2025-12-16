"""
Competitor Discovery Agent - Automatically identifies competitors.

This agent:
1. Takes a company name
2. Uses GPT-4 to understand the company's domain
3. Uses Tavily Search to find competitors
4. Returns top 5 most relevant competitors
"""

from openai import OpenAI
from tavily import TavilyClient
from typing import List, Dict
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class CompetitorDiscoveryAgent:
    """
    Automatically discovers competitors for a given company.
    
    Uses a two-step approach:
    1. GPT-4 to understand the company and generate search queries
    2. Tavily Search to find actual competitors from the web
    """
    
    def __init__(self, tavily_api_key: str, openai_api_key: str):
        """
        Initialize with API keys.
        
        Args:
            tavily_api_key: Tavily API key for search
            openai_api_key: OpenAI API key for intelligence
        """
        self.tavily_client = TavilyClient(api_key=tavily_api_key)
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.name = "competitor_discovery"
    
    async def execute(self, state: Dict) -> Dict:
        """
        Discover competitors for the given company.
        
        Args:
            state: Workflow state with company_name
            
        Returns:
            Updated state with competitors list populated
        """
        company_name = state.get("company_name")
        
        if not company_name:
            logger.error("❌ No company name provided")
            return {
                **state,
                "competitors": [],
                "errors": state.get("errors", []) + ["No company name provided"],
                "completed_agents": state.get("completed_agents", []) + [self.name]
            }
        
        logger.info(f"🔍 Competitor Discovery Agent starting for: {company_name}")
        
        try:
            # Step 1: Understand the company using GPT-4
            company_info = await self._understand_company(company_name)
            
            logger.info(f"📊 Company identified as: {company_info['industry']}")
            logger.info(f"💡 Description: {company_info['description'][:100]}...")
            
            # Step 2: Find competitors using Tavily Search
            competitors = await self._find_competitors(
                company_name, 
                company_info
            )
            
            logger.info(f"✅ Found {len(competitors)} competitors: {', '.join(competitors)}")
            
            return {
                **state,
                "competitors": competitors,
                "company_info": company_info,
                "current_step": "competitor_discovery_complete",
                "completed_agents": state.get("completed_agents", []) + [self.name],
                "updated_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"❌ Competitor discovery failed: {str(e)}")
            return {
                **state,
                "competitors": [],
                "errors": state.get("errors", []) + [f"Discovery error: {str(e)}"],
                "completed_agents": state.get("completed_agents", []) + [self.name],
                "updated_at": datetime.now()
            }
    
    async def _understand_company(self, company_name: str) -> Dict:
        """
        Use GPT-4 to understand what the company does.
        
        Args:
            company_name: Name of the company
            
        Returns:
            Dictionary with industry, description, and keywords
        """
        logger.info(f"🤖 Asking GPT-4 about {company_name}...")
        
        prompt = f"""Analyze the company "{company_name}" and provide:
1. Industry/sector
2. Brief description (1-2 sentences)
3. Key search terms to find competitors

Respond in JSON format:
{{
    "industry": "specific industry",
    "description": "what the company does",
    "search_terms": ["term1", "term2", "term3"]
}}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a business analyst expert at identifying companies and their markets. Always respond with valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        logger.info(f"📊 Token usage: {response.usage.total_tokens} tokens")
        
        return result
    
    async def _find_competitors(
        self, 
        company_name: str, 
        company_info: Dict,
        max_competitors: int = 5
    ) -> List[str]:
        """
        Find competitors using Tavily Search.
        
        Args:
            company_name: Name of the company
            company_info: Information about the company from GPT-4
            max_competitors: Maximum number of competitors to return
            
        Returns:
            List of competitor names
        """
        competitors = set()
        
        # Generate search queries
        search_queries = [
            f"{company_name} competitors",
            f"{company_name} alternatives",
            f"best {company_info['industry']} companies",
            f"{company_info['industry']} market leaders",
            f"companies like {company_name}"
        ]
        
        # Search for competitors
        for query in search_queries[:3]:  # Use top 3 queries to save API calls
            logger.info(f"🔎 Searching: {query}")
            
            try:
                # Use Tavily Search
                import asyncio
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.tavily_client.search(
                        query=query,
                        search_depth="basic",
                        max_results=5,
                        include_answer=True
                    )
                )
                
                # Extract competitor names from results
                found = self._extract_competitors_from_results(
                    response,
                    company_name,
                    company_info
                )
                
                competitors.update(found)
                
                # Stop if we have enough
                if len(competitors) >= max_competitors * 2:
                    break
                    
            except Exception as e:
                logger.warning(f"⚠️  Search failed for '{query}': {str(e)}")
        
        # If search didn't find enough, use GPT-4 as fallback
        if len(competitors) < max_competitors:
            logger.info("🤖 Using GPT-4 fallback to find more competitors...")
            gpt_competitors = await self._get_competitors_from_gpt(
                company_name,
                company_info
            )
            competitors.update(gpt_competitors)
        
        # Convert to list and take top N
        competitor_list = list(competitors)
        
        # Remove the company itself if it appears
        competitor_list = [c for c in competitor_list if c.lower() != company_name.lower()]
        
        # Return top N
        return competitor_list[:max_competitors]
    
    def _extract_competitors_from_results(
        self,
        search_response: Dict,
        company_name: str,
        company_info: Dict
    ) -> List[str]:
        """
        Extract competitor names from Tavily search results.
        
        Uses GPT-4 to intelligently parse the search results and
        identify actual company names.
        """
        # Get the AI answer and top results
        answer = search_response.get("answer", "")
        results = search_response.get("results", [])
        
        # Combine answer and result snippets
        context = f"Answer: {answer}\n\n"
        for result in results[:3]:
            context += f"- {result.get('content', '')}\n"
        
        # Ask GPT-4 to extract company names
        prompt = f"""From this text about {company_name} competitors in the {company_info['industry']} industry, extract ONLY the competitor company names.

Text:
{context}

Return a JSON array of company names (max 5):
{{"competitors": ["Company1", "Company2", ...]}}

Rules:
- Only include actual company names, not products or services
- Exclude {company_name} itself
- Use official company names (e.g., "Stripe" not "Stripe Inc.")"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You extract company names from text. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("competitors", [])
            
        except Exception as e:
            logger.warning(f"⚠️  GPT-4 extraction failed: {str(e)}")
            return []
    
    async def _get_competitors_from_gpt(
        self,
        company_name: str,
        company_info: Dict,
        count: int = 5
    ) -> List[str]:
        """
        Use GPT-4 knowledge as fallback to suggest competitors.
        
        This is used when web search doesn't find enough competitors.
        """
        prompt = f"""List the top {count} competitors of {company_name} in the {company_info['industry']} industry.

Company description: {company_info['description']}

Return a JSON array of company names:
{{"competitors": ["Company1", "Company2", ...]}}

Only include real, well-known competitors."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a business analyst with deep knowledge of competitive landscapes. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("competitors", [])
            
        except Exception as e:
            logger.error(f"❌ GPT-4 fallback failed: {str(e)}")
            return []
    
    def __repr__(self):
        return f"CompetitorDiscoveryAgent(name={self.name})"