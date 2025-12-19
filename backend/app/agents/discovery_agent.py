"""
Competitor Discovery Agent - Automatically identifies competitors.

This agent:
1. Takes a company name
2. Uses GPT-4o-mini to understand the company's domain with precision
3. Uses Tavily Search to find DIRECT competitors
4. Filters out adjacent market players and non-competitors
5. Returns top N most relevant competitors
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
    
    Uses a two-step approach with improved precision:
    1. GPT-4o-mini to understand the company's CORE BUSINESS and MARKET SEGMENT
    2. Tavily Search to find actual DIRECT competitors from the web
    3. GPT-4o-mini to filter and validate competitor relevance
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
            state: Workflow state with company_name and max_competitors
            
        Returns:
            Updated state with competitors list populated
        """
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
        
        logger.info(f"Competitor Discovery Agent starting for: {company_name}")
        logger.info(f"Target: Find up to {max_competitors} direct competitors")
        
        try:
            # Step 1: Understand the company using GPT-4o-mini with precision
            company_info = await self._understand_company(company_name)
            
            logger.info(f"Company analysis complete:")
            logger.info(f"  Market Segment: {company_info['market_segment']}")
            logger.info(f"  Primary Business: {company_info['primary_business']}")
            logger.info(f"  Target Customer: {company_info['target_customer']}")
            
            # Step 2: Find competitors using Tavily Search
            competitors = await self._find_competitors(
                company_name, 
                company_info,
                max_competitors=max_competitors
            )
            
            logger.info(f"Discovery complete: Found {len(competitors)} competitors")
            logger.info(f"Competitors: {', '.join(competitors)}")
            
            return {
                **state,
                "competitors": competitors,
                "company_info": company_info,
                "current_step": "competitor_discovery_complete",
                "completed_agents": state.get("completed_agents", []) + [self.name],
                "updated_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Competitor discovery failed: {str(e)}")
            return {
                **state,
                "competitors": [],
                "errors": state.get("errors", []) + [f"Discovery error: {str(e)}"],
                "completed_agents": state.get("completed_agents", []) + [self.name],
                "updated_at": datetime.now()
            }
    
    async def _understand_company(self, company_name: str) -> Dict:
        """
        Use GPT-4o-mini to understand what the company does with precision.
        
        Args:
            company_name: Name of the company
            
        Returns:
            Dictionary with detailed company profile
        """
        logger.info(f"Analyzing {company_name} with GPT-4o-mini...")
        
        prompt = f"""You are a business analyst expert. Analyze "{company_name}" precisely.

Your goal: Identify the CORE BUSINESS and PRIMARY MARKET SEGMENT, not just the broad industry.

Examples of precision:
- Bad: "Stripe is in fintech" (too broad)
- Good: "Stripe is a payment processing API for online merchants"

- Bad: "Slack is in SaaS"
- Good: "Slack is a team messaging and collaboration platform"

For {company_name}, provide:

1. **Primary Business Model**: What do they actually sell? (e.g., "API-based payment processing", "cloud storage", "CRM software")

2. **Target Customer**: Who buys from them? (e.g., "e-commerce businesses", "enterprise teams", "developers")

3. **Core Value Proposition**: What problem do they solve? (one sentence)

4. **Market Segment**: Specific niche, not broad industry (e.g., "payment gateways for online merchants" not "fintech")

5. **Competitor Search Terms**: 3-5 highly specific search terms that would find DIRECT competitors (companies selling the same thing to the same customers)

Respond in JSON:
{{
    "primary_business": "what they sell",
    "target_customer": "who buys it",
    "value_proposition": "problem they solve",
    "market_segment": "specific niche",
    "search_terms": ["specific term 1", "specific term 2", "specific term 3"]
}}

Be extremely specific. Avoid generic industry terms."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a business analyst who identifies companies with surgical precision. You focus on CORE BUSINESS and PRIMARY MARKET, not tangential services or broad industries. Always respond with valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        logger.info(f"Token usage: {response.usage.total_tokens} tokens")
        
        return result
    
    async def _find_competitors(
        self, 
        company_name: str, 
        company_info: Dict,
        max_competitors: int = 5
    ) -> List[str]:
        """
        Find competitors using Tavily Search with improved targeting.
        
        Args:
            company_name: Name of the company
            company_info: Information about the company from GPT-4o-mini
            max_competitors: Maximum number of competitors to return
            
        Returns:
            List of competitor names
        """
        competitors = set()
        
        # Generate more targeted search queries
        search_queries = [
            # Direct competitor searches
            f"{company_name} vs competitors",
            f"{company_name} alternatives comparison",
            f"best {company_info['market_segment']} companies",
            
            # Market segment searches
            f"top {company_info['primary_business']} providers",
            f"{company_info['market_segment']} market leaders",
            
            # Customer perspective
            f"alternatives to {company_name} for {company_info['target_customer']}"
        ]
        
        # Use the most relevant queries
        for query in search_queries[:4]:  # Use top 4 queries
            logger.info(f"Searching: {query}")
            
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
                
                # Stop if we have enough high-quality competitors
                if len(competitors) >= max_competitors * 1.5:
                    break
                    
            except Exception as e:
                logger.warning(f"Search failed for '{query}': {str(e)}")
        
        # If not enough found, use GPT-4o-mini fallback
        if len(competitors) < max_competitors:
            logger.info(f"Only found {len(competitors)}, using GPT-4o-mini to supplement...")
            gpt_competitors = await self._get_competitors_from_gpt(
                company_name,
                company_info,
                count=max_competitors - len(competitors) + 2
            )
            competitors.update(gpt_competitors)
        
        # Convert to list and remove the company itself
        competitor_list = [c for c in list(competitors) if c.lower() != company_name.lower()]
        
        # Return top N
        return competitor_list[:max_competitors]
    
    def _extract_competitors_from_results(
        self,
        search_response: Dict,
        company_name: str,
        company_info: Dict
    ) -> List[str]:
        """
        Extract competitor names from Tavily search results with strict filtering.
        
        Uses GPT-4o-mini to intelligently parse the search results and
        identify DIRECT competitors only.
        """
        # Get the AI answer and top results
        answer = search_response.get("answer", "")
        results = search_response.get("results", [])
        
        # Combine answer and result snippets
        context = f"Search Answer: {answer}\n\n"
        for result in results[:5]:  # Increased from 3 to 5 for more context
            context += f"Source: {result.get('title', '')}\n"
            context += f"Content: {result.get('content', '')}\n\n"
        
        # Improved extraction prompt
        prompt = f"""You are analyzing search results to find DIRECT competitors of {company_name}.

Company Profile:
- Business: {company_info['primary_business']}
- Market: {company_info['market_segment']}
- Customers: {company_info['target_customer']}

Search Results:
{context}

Task: Extract company names that are DIRECT competitors (selling similar products/services to similar customers).

STRICT RULES:
1. Only include companies that compete in the SAME market segment
2. Exclude companies that:
   - Operate in adjacent/different markets
   - Are partners/vendors rather than competitors
   - Are customers of {company_name}
   - Offer complementary (not competing) services
3. Exclude {company_name} itself
4. Use official company names (e.g., "Stripe" not "Stripe Inc.")
5. Maximum 5 companies

Examples:
- If analyzing Stripe (payment processing), include: Square, Adyen, Checkout.com
- If analyzing Stripe, exclude: Brex (corporate cards), Plaid (bank connectivity), QuickBooks (accounting)

Return ONLY direct competitors as JSON:
{{"competitors": ["Company1", "Company2", ...]}}"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a competitive intelligence analyst who identifies DIRECT competitors with precision. You understand the difference between direct competitors, adjacent market players, partners, and complementary services. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Very low for consistent, focused results
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            competitors = result.get("competitors", [])
            
            logger.info(f"Extracted {len(competitors)} direct competitors from search")
            return competitors
            
        except Exception as e:
            logger.warning(f"GPT-4o-mini extraction failed: {str(e)}")
            return []
    
    async def _get_competitors_from_gpt(
        self,
        company_name: str,
        company_info: Dict,
        count: int = 5
    ) -> List[str]:
        """
        Use GPT-4o-mini knowledge as fallback to suggest competitors.
        
        This is used when web search doesn't find enough competitors.
        """
        prompt = f"""You are a competitive intelligence expert with deep market knowledge.

List the top {count} DIRECT competitors of {company_name}.

Company Profile:
- Business: {company_info['primary_business']}
- Market: {company_info['market_segment']}
- Customers: {company_info['target_customer']}
- Value Prop: {company_info['value_proposition']}

Requirements:
1. ONLY include companies that:
   - Sell similar products/services
   - Target the same customer segment
   - Compete directly for the same deals
   
2. EXCLUDE companies that:
   - Operate in adjacent markets
   - Are partners/ecosystem players
   - Serve different customer segments
   - Offer complementary (not competing) products

3. Prioritize:
   - Well-known, established competitors
   - Companies with similar business models
   - Direct market overlap

Return JSON with ONLY direct competitors:
{{"competitors": ["Company1", "Company2", ...]}}

Be selective. Quality over quantity."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a competitive analyst who understands market segmentation and competitive dynamics. You distinguish between direct competitors, indirect competitors, partners, and complementary services. Focus on DIRECT competition only. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            competitors = result.get("competitors", [])
            
            logger.info(f"GPT-4o-mini suggested {len(competitors)} competitors")
            return competitors
            
        except Exception as e:
            logger.error(f"GPT-4o-mini fallback failed: {str(e)}")
            return []
    
    def __repr__(self):
        return f"CompetitorDiscoveryAgent(name={self.name})"