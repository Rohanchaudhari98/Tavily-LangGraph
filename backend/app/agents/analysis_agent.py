"""
Analysis Agent - Uses GPT-4 to synthesize competitive intelligence.

This agent:
1. Takes research results and extracted content
2. Analyzes pricing, features, positioning
3. Generates strategic insights and recommendations
"""

from openai import OpenAI
from typing import Dict, List
from datetime import datetime
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

class AnalysisAgent:
    """
    Synthesizes competitive intelligence using GPT-4.
    
    Takes raw data from Research and Extraction agents and produces:
    - Pricing comparison
    - Feature analysis
    - Market positioning insights
    - Strategic recommendations
    
    Supports two analysis modes:
    - Standard (gpt-4o-mini): Fast, cost-effective, good quality
    - Premium (gpt-4o): Slower, more expensive, highest quality
    """
    
    def __init__(self, openai_api_key: str, use_premium: bool = False):
        """
        Initialize with OpenAI API key.
        
        Args:
            openai_api_key: Your OpenAI API key
            use_premium: If True, use GPT-4o for highest quality analysis.
                        If False (default), use GPT-4o-mini for fast, cost-effective analysis.
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.name = "analysis"
        self.use_premium = use_premium
        
        # Model selection
        if use_premium:
            self.model = "gpt-4o"  # Premium: Better quality, slower, ~60x more expensive
            logger.info("🌟 Analysis Agent initialized with PREMIUM mode (gpt-4o)")
        else:
            self.model = "gpt-4o-mini"  # Standard: Fast, cheap, good quality
            logger.info("⚡ Analysis Agent initialized with STANDARD mode (gpt-4o-mini)")
    
    async def execute(self, state: Dict) -> Dict:
        """
        Analyze competitive intelligence and generate insights.
        
        Args:
            state: Current workflow state with research_results and extracted_data
            
        Returns:
            Updated state with analysis populated
        """
        research_results = state.get("research_results", [])
        extracted_data = state.get("extracted_data", [])
        crawl_results = state.get("crawl_results", [])
        query = state.get("query", "")
        competitors = state.get("competitors", [])
        
        logger.info(f"🧠 Analysis Agent starting...")
        logger.info(f"   Mode: {'PREMIUM (gpt-4o)' if self.use_premium else 'STANDARD (gpt-4o-mini)'}")
        logger.info(f"   Query: {query}")
        logger.info(f"   Competitors: {len(competitors)}")
        logger.info(f"   Research results: {len(research_results)}")
        logger.info(f"   Extracted pages: {len(extracted_data)}")
        
        # Validate we have data to analyze
        if not research_results and not extracted_data:
            logger.warning("⚠️  No data to analyze")
            return {
                **state,
                "analysis": None,
                "errors": state.get("errors", []) + ["No data available for analysis"],
                "current_step": "analysis_failed",
                "completed_agents": state.get("completed_agents", []) + [self.name],
                "updated_at": datetime.now()
            }
        
        # Prepare data for analysis
        analysis_context = self._prepare_context(
            query, 
            competitors,
            research_results, 
            extracted_data,
            crawl_results
        )
        
        logger.info(f"📊 Context prepared: {len(analysis_context)} characters")
        
        try:
            # Generate analysis using GPT-4
            analysis_result = await self._generate_analysis(
                query,
                competitors,
                analysis_context
            )
            
            logger.info(f"✅ Analysis complete: {len(analysis_result)} characters")
            
            return {
                **state,
                "analysis": analysis_result,
                "analysis_mode": "premium" if self.use_premium else "standard",
                "current_step": "analysis_complete",
                "completed_agents": state.get("completed_agents", []) + [self.name],
                "updated_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {str(e)}")
            return {
                **state,
                "analysis": None,
                "errors": state.get("errors", []) + [f"Analysis error: {str(e)}"],
                "current_step": "analysis_failed",
                "completed_agents": state.get("completed_agents", []) + [self.name],
                "updated_at": datetime.now()
            }
    
    def _prepare_context(
        self,
        query: str,
        competitors: List[str],
        research_results: List[Dict],
        extracted_data: List[Dict],
        crawl_results: List[Dict] = None
    ) -> str:
        """
        Prepare context from all gathered data.
        """
        context_parts = []
        
        # Add research summaries
        context_parts.append("=== RESEARCH SUMMARIES ===\n")
        for result in research_results:
            if result.get("status") == "success":
                competitor = result.get("competitor")
                answer = result.get("answer", "")
                context_parts.append(f"\n{competitor}:")
                context_parts.append(f"{answer}\n")
        
        # Add extracted content
        context_parts.append("\n=== EXTRACTED CONTENT ===\n")
        for data in extracted_data:
            if data.get("status") == "success":
                competitor = data.get("competitor")
                url = data.get("url")
                content = data.get("raw_content", "")
                
                truncated_content = content[:2000]
                if len(content) > 2000:
                    truncated_content += "... [truncated]"
                
                context_parts.append(f"\n{competitor} - {url}:")
                context_parts.append(f"{truncated_content}\n")
        
        # Add crawl results
        if crawl_results:
            context_parts.append("\n=== DEEP CRAWL FINDINGS ===\n")
            for crawl in crawl_results:
                if crawl.get("status") == "success":
                    competitor = crawl.get("competitor")
                    pages_crawled = crawl.get("pages_crawled", 0)
                    content = crawl.get("combined_content", "")
                    
                    # Truncate combined content
                    truncated_content = content[:2000]
                    if len(content) > 2000:
                        truncated_content += "... [truncated]"
                    
                    context_parts.append(f"\n{competitor} - Deep Crawl ({pages_crawled} pages):")
                    context_parts.append(f"{truncated_content}\n")
        
        return "\n".join(context_parts)

    async def _generate_analysis(
        self,
        query: str,
        competitors: List[str],
        context: str
    ) -> str:
        """
        Generate analysis using GPT-4.
        
        Args:
            query: User's query
            competitors: List of competitors
            context: Prepared context with all data
            
        Returns:
            Analysis text
        """
        system_prompt = """You are a competitive intelligence analyst. 
        
    Your job is to analyze competitor data and provide actionable insights.

    Format your analysis in clear sections:

    1. EXECUTIVE SUMMARY
    - Key takeaways in 2-3 sentences

    2. PRICING COMPARISON
    - Compare pricing models
    - Identify pricing strategies
    - Note any special offers or tiers

    3. FEATURE ANALYSIS
    - Compare key features
    - Identify unique capabilities
    - Note feature gaps

    4. MARKET POSITIONING
    - How each competitor positions themselves
    - Target customer segments
    - Value propositions

    5. STRATEGIC RECOMMENDATIONS
    - Opportunities identified
    - Competitive advantages to leverage
    - Areas for differentiation

    Be specific, data-driven, and actionable. Use bullet points for clarity."""

        user_prompt = f"""Analyze the following competitive intelligence data:

    QUERY: {query}
    COMPETITORS: {', '.join(competitors)}

    DATA:
    {context}

    Provide a comprehensive competitive analysis following the format in your system prompt."""

        logger.info(f"🤖 Calling {self.model}...")
        
        # OpenAI client is synchronous, wrap in executor for async
        loop = asyncio.get_event_loop()
        
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more focused analysis
                max_tokens=2000
            )
        )
        
        analysis = response.choices[0].message.content
        
        # Log token usage for monitoring
        usage = response.usage
        logger.info(f"📊 Token usage: {usage.total_tokens} total "
                f"({usage.prompt_tokens} prompt + {usage.completion_tokens} completion)")
        
        # Calculate approximate cost
        if self.use_premium:
            # GPT-4o pricing (approximate)
            cost = (usage.prompt_tokens * 0.000005) + (usage.completion_tokens * 0.000015)
        else:
            # GPT-4o-mini pricing (approximate)
            cost = (usage.prompt_tokens * 0.00000015) + (usage.completion_tokens * 0.0000006)
        
        logger.info(f"💰 Estimated cost: ${cost:.4f}")
        
        return analysis
    
    def __repr__(self):
        mode = "premium" if self.use_premium else "standard"
        return f"AnalysisAgent(name={self.name}, model={self.model}, mode={mode})"