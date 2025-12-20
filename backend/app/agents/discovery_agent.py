"""
Competitor Discovery Agent

Identifies direct competitors for a given company using a two-step approach:
1. Analyze the company's core business with GPT-4o-mini
2. Search for competitors using Tavily and validate with GPT
"""

from openai import OpenAI
from tavily import TavilyClient
from typing import List, Dict
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class CompetitorDiscoveryAgent:
    # Discovers competitors by analyzing company profile and searching the web
    
    def __init__(self, tavily_api_key: str, openai_api_key: str):
        self.tavily_client = TavilyClient(api_key=tavily_api_key)
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.name = "competitor_discovery"
    
    async def execute(self, state: Dict) -> Dict:
        # Main execution method - finds competitors and updates workflow state
        company_name = state.get("company_name")
        max_competitors = state.get("max_competitors", 5)
        
        if not company_name:
            logger.error("No company name provided")
            return {
                **state,
                "competitors": [],
                "errors": state.get("errors", []) + ["No company name provided"],
                "completed_agents": state.get("completed_agents", []) + [self.name]
            }
        
        logger.info(f"Starting competitor discovery for: {company_name}")
        logger.info(f"Looking for up to {max_competitors} direct competitors")
        
        try:
            # First, understand what the company actually does
            company_info = await self._understand_company(company_name)
            
            logger.info(f"Company analysis complete:")
            logger.info(f"  Market: {company_info['market_segment']}")
            logger.info(f"  Business: {company_info['primary_business']}")
            logger.info(f"  Customers: {company_info['target_customer']}")
            
            # Then search for companies in the same space
            competitors = await self._find_competitors(
                company_name,
                company_info,
                max_competitors=max_competitors
            )
            
            logger.info(f"Found {len(competitors)} competitors: {', '.join(competitors)}")
            
            return {
                **state,
                "competitors": competitors,
                "company_info": company_info,
                "current_step": "competitor_discovery_complete",
                "completed_agents": state.get("completed_agents", []) + [self.name],
                "updated_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Discovery failed: {str(e)}")
            return {
                **state,
                "competitors": [],
                "errors": state.get("errors", []) + [f"Discovery error: {str(e)}"],
                "completed_agents": state.get("completed_agents", []) + [self.name],
                "updated_at": datetime.now()
            }
    
    async def _understand_company(self, company_name: str) -> Dict:
        """
        Analyze what the company does and who they serve.
        We need this to avoid finding companies in adjacent markets.
        """
        logger.info(f"Analyzing {company_name}...")
        
        prompt = f"""Analyze "{company_name}" and identify their core business precisely.

                    Don't just say "fintech" or "SaaS" - be specific about what they actually sell.

                    Examples of good analysis:
                    - Stripe: "Payment processing API for online merchants"
                    - Slack: "Team messaging platform for workplace collaboration"
                    - Snowflake: "Cloud data warehouse for analytics"

                    For {company_name}, tell me:

                    1. Primary Business: What do they sell?
                    2. Target Customer: Who buys it?
                    3. Core Value Prop: What problem do they solve?
                    4. Market Segment: Their specific niche
                    5. Search Terms: 3-5 terms to find direct competitors

                    Respond in JSON:
                    {{
                        "primary_business": "...",
                        "target_customer": "...",
                        "value_proposition": "...",
                        "market_segment": "...",
                        "search_terms": ["...", "...", "..."]
                    }}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You analyze companies with precision. Focus on their core business, not tangential services. Always respond with valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        logger.info(f"Used {response.usage.total_tokens} tokens")
        
        return result
    
    async def _find_competitors(
        self, 
        company_name: str, 
        company_info: Dict,
        max_competitors: int = 5
    ) -> List[str]:
        # Search the web for competitors and validate them
        competitors = set()
        
        # Build targeted search queries
        search_queries = [
            f"{company_name} vs competitors",
            f"{company_name} alternatives comparison",
            f"best {company_info['market_segment']} companies",
            f"top {company_info['primary_business']} providers",
            f"{company_info['market_segment']} market leaders",
            f"alternatives to {company_name} for {company_info['target_customer']}"
        ]
        
        # Search with top 4 queries - usually enough to find good results
        for query in search_queries[:4]:
            logger.info(f"Searching: {query}")
            
            try:
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
                
                # Parse search results and extract competitor names
                found = self._extract_competitors_from_results(
                    response,
                    company_name,
                    company_info
                )
                
                competitors.update(found)
                
                # Once we have 1.5x our target, we can stop searching
                if len(competitors) >= max_competitors * 1.5:
                    break
                    
            except Exception as e:
                logger.warning(f"Search failed for '{query}': {str(e)}")
        
        # If web search didn't find enough, use GPT knowledge as backup
        if len(competitors) < max_competitors:
            logger.info(f"Only found {len(competitors)}, using GPT fallback...")
            gpt_competitors = await self._get_competitors_from_gpt(
                company_name,
                company_info,
                count=max_competitors - len(competitors) + 2
            )
            competitors.update(gpt_competitors)
        
        # Clean up and return
        competitor_list = [c for c in list(competitors) if c.lower() != company_name.lower()]
        return competitor_list[:max_competitors]
    
    def _extract_competitors_from_results(
        self,
        search_response: Dict,
        company_name: str,
        company_info: Dict
    ) -> List[str]:
        """
        Parse search results and pull out competitor names
        Uses GPT to be smart about what's actually a competitor vs adjacent market
        """
        answer = search_response.get("answer", "")
        results = search_response.get("results", [])
        
        # Build context from search results
        context = f"Search Answer: {answer}\n\n"
        for result in results[:5]:
            context += f"Source: {result.get('title', '')}\n"
            context += f"Content: {result.get('content', '')}\n\n"
        
        prompt = f"""Extract direct competitors of {company_name} from these search results.

                    Company: {company_name}
                    - Business: {company_info['primary_business']}
                    - Market: {company_info['market_segment']}
                    - Customers: {company_info['target_customer']}

                    Search Results:
                    {context}

                    Rules:
                    1. Only include companies competing in the same market
                    2. Exclude partners, vendors, or customers
                    3. Exclude companies in adjacent/different markets
                    4. Don't include {company_name} itself
                    5. Use official names (e.g., "Stripe" not "Stripe Inc.")
                    6. Max 5 companies

                    Example: For Stripe (payment processing), include Square and Adyen, but exclude Brex (corporate cards) or Plaid (bank connectivity).

                    Return JSON:
                    {{"competitors": ["Company1", "Company2", ...]}}"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You're a competitive analyst who knows the difference between direct competitors and adjacent market players. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            competitors = result.get("competitors", [])
            
            logger.info(f"Extracted {len(competitors)} competitors from search")
            return competitors
            
        except Exception as e:
            logger.warning(f"Extraction failed: {str(e)}")
            return []
    
    async def _get_competitors_from_gpt(
        self,
        company_name: str,
        company_info: Dict,
        count: int = 5
    ) -> List[str]:
        # Fallback to GPT's knowledge when search doesn't find enough results
        prompt = f"""List the top {count} direct competitors of {company_name}.

                    Company Profile:
                    - Business: {company_info['primary_business']}
                    - Market: {company_info['market_segment']}
                    - Customers: {company_info['target_customer']}

                    Only include companies that sell similar products to the same customers.
                    Exclude partners, adjacent markets, or complementary services.
                    Prioritize well-known competitors with direct market overlap.

                    Return JSON:
                    {{"competitors": ["Company1", "Company2", ...]}}"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You understand market segmentation and competitive dynamics. Focus on direct competitors only. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            competitors = result.get("competitors", [])
            
            logger.info(f"GPT suggested {len(competitors)} competitors")
            return competitors
            
        except Exception as e:
            logger.error(f"GPT fallback failed: {str(e)}")
            return []
    
    def __repr__(self):
        return f"CompetitorDiscoveryAgent(name={self.name})"