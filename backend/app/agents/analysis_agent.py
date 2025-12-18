"""
Analysis Agent - Uses GPT-4 to synthesize competitive intelligence.

This agent:
1. Takes research results and extracted content
2. Analyzes pricing, features, positioning
3. Conducts strategic risk assessment
4. Generates strategic insights and recommendations
5. Extracts structured data for charts
6. Handles flexible queries with "Additional Insights" section
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
    - Risk analysis and threat assessment
    - Additional insights (for non-standard queries)
    - Strategic recommendations
    - Structured chart data for visualization
    
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
            Updated state with analysis and chart_data populated
        """
        research_results = state.get("research_results", [])
        extracted_data = state.get("extracted_data", [])
        crawl_results = state.get("crawl_results", [])
        query = state.get("query", "")
        company_name = state.get("company_name", "Your Company")
        competitors = state.get("competitors", [])
        
        logger.info(f"🧠 Analysis Agent starting...")
        logger.info(f"   Mode: {'PREMIUM (gpt-4o)' if self.use_premium else 'STANDARD (gpt-4o-mini)'}")
        logger.info(f"   Company: {company_name}")
        logger.info(f"   Query: {query}")
        logger.info(f"   Competitors: {len(competitors)}")
        logger.info(f"   Research results: {len(research_results)}")
        logger.info(f"   Extracted pages: {len(extracted_data)}")
        
        # Validate we have data to analyze
        if not research_results and not extracted_data and not crawl_results:
            logger.warning("⚠️  No data to analyze")
            return {
                **state,
                "analysis": None,
                "chart_data": None,
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
                company_name,
                competitors,
                analysis_context
            )
            
            logger.info(f"✅ Analysis complete: {len(analysis_result)} characters")
            
            # Extract chart data from analysis
            chart_data = await self._extract_chart_data(
                analysis_result,
                company_name,
                competitors
            )
            
            return {
                **state,
                "analysis": analysis_result,
                "chart_data": chart_data,
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
                "chart_data": None,
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
        
        Args:
            query: User's query
            competitors: List of competitors
            research_results: Results from research agent
            extracted_data: Results from extraction agent
            crawl_results: Results from crawl agent
            
        Returns:
            Formatted context string for analysis
        """
        context_parts = []
        
        # Add research summaries
        if research_results:
            context_parts.append("=== RESEARCH SUMMARIES ===\n")
            for result in research_results:
                if result.get("status") == "success":
                    competitor = result.get("competitor")
                    answer = result.get("answer", "")
                    context_parts.append(f"\n{competitor}:")
                    context_parts.append(f"{answer}\n")
        
        # Add extracted content
        if extracted_data:
            context_parts.append("\n=== EXTRACTED CONTENT ===\n")
            for data in extracted_data:
                if data.get("status") == "success":
                    competitor = data.get("competitor")
                    url = data.get("url")
                    content = data.get("raw_content", "")
                    
                    # Truncate long content
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
        
        return "\n".join(context_parts) if context_parts else "No data available"

    async def _generate_analysis(
        self,
        query: str,
        company_name: str,
        competitors: List[str],
        context: str
    ) -> str:
        """
        Generate analysis using GPT-4.
        
        Args:
            query: User's query
            company_name: Your company name
            competitors: List of competitors
            context: Prepared context with all data
            
        Returns:
            Analysis text in markdown format
        """
        system_prompt = f"""You are a competitive intelligence analyst working for {company_name}.

**USER'S SPECIFIC QUERY:** "{query}"

**CRITICAL INSTRUCTIONS:** 
- All analysis MUST be from {company_name}'s perspective
- All strategic recommendations MUST be for {company_name}, NOT for the competitors
- Your goal is to help {company_name} compete better against: {', '.join(competitors)}
- Frame everything as advice TO {company_name} ABOUT their competitors
- Address ALL aspects of the user's query, even if they don't fit standard categories

Create a comprehensive competitive intelligence report for {company_name} with these sections:

**1. EXECUTIVE SUMMARY**
   - Direct overview addressing the query: "{query}"
   - Key insights about how competitors position themselves
   - Main opportunities and threats for {company_name}
   - High-level takeaways from the analysis

**2. PRICING COMPARISON**
   - How do competitors' pricing models compare?
   - What pricing strategies are competitors using?
   - What special offers or tiers do they have?
   - What does this mean for {company_name}'s pricing strategy?
   - How can {company_name} price competitively?

**3. FEATURE ANALYSIS**
   - What features and capabilities do competitors offer?
   - What unique capabilities do they have that stand out?
   - What feature gaps exist that {company_name} could exploit?
   - Where might {company_name} have potential advantages?
   - How do competitor features align with customer needs?

**4. MARKET POSITIONING**
   - How do competitors position themselves in the market?
   - What customer segments are they targeting?
   - What value propositions are they using?
   - How should {company_name} position itself to stand out?
   - What differentiators should {company_name} emphasize?

**5. RISK ANALYSIS**
   Conduct a strategic risk assessment from {company_name}'s perspective:

   **Critical Risks** (Immediate attention required):
   - Identify specific competitive threats with high impact AND high likelihood
   - What competitor capabilities directly threaten {company_name}'s market position?
   - What pricing pressures could erode {company_name}'s revenue?
   - What feature gaps put {company_name} at risk of customer churn?
   - For each risk provide:
     * Clear description of the threat
     * Impact level: High/Medium/Low (with brief justification)
     * Likelihood: High/Medium/Low (based on competitive moves observed)
     * Recommended mitigation action for {company_name}
     * Suggested timeline (e.g., "Q1 2024", "Within 6 months")

   **Emerging Risks** (Monitor and prepare):
   - Market trends that could become significant threats
   - Technology shifts competitors are adopting
   - New entrants or business models disrupting the market
   - Regulatory or industry changes that could impact {company_name}

   **Strategic Opportunities at Risk**:
   - Market segments {company_name} is losing or could lose to competitors
   - Revenue streams under competitive pressure
   - Growth opportunities competitors might capture first
   - Partnerships or channels at risk

   **Risk Mitigation Priorities**:
   - Rank top 3-5 risks by urgency
   - Provide specific action items with timelines
   - Estimate required investment level (High/Medium/Low) where relevant
   
   **Format each critical risk as:**
   **Risk Name** (Impact: X | Likelihood: Y)
   - **Threat**: [Specific competitive threat]
   - **Impact on {company_name}**: [Business impact]
   - **Mitigation**: [Specific action for {company_name}]
   - **Timeline**: [When to act]

**6. ADDITIONAL INSIGHTS** (ONLY include if query asks about topics not covered above)
   - Topics that might require this section:
     * Customer support quality and response times
     * Partnerships, acquisitions, or strategic alliances
     * Brand reputation and customer sentiment
     * Company culture and hiring trends
     * Technology stack or infrastructure
     * Marketing strategies or campaigns
     * Geographic presence or expansion plans
     * Sustainability or social responsibility initiatives
   - Address any unique aspects from the query: "{query}"
   - Provide insights that don't fit neatly into pricing, features, positioning, or risks
   - **IMPORTANT:** Skip this section entirely if not needed for the query

**7. STRATEGIC RECOMMENDATIONS FOR {company_name}**
   - Opportunities {company_name} should pursue based on competitor weaknesses
   - Competitive advantages {company_name} should leverage
   - Areas where {company_name} should differentiate itself from competitors
   - Specific, actionable steps {company_name} should take to improve market position
   - **Short-term moves** (next 3-6 months) prioritized by impact
   - **Long-term strategic initiatives** (6-12+ months)
   - Quick wins that can be implemented immediately

**FORMATTING RULES:**
- Use clear markdown formatting with headers (## for sections, ### for subsections)
- Write in a professional, analytical tone
- Be specific and data-driven when possible
- Avoid generic advice - make it actionable for {company_name}
- Keep the analysis focused on the query: "{query}"
- Use bullet points for clarity and scannability
- Highlight critical risks and urgent actions clearly

**REMEMBER:** 
- Write as if you're presenting TO {company_name}, not about them
- Say "{company_name} should..." not "the competitor should..."
- All recommendations are for {company_name}'s benefit
- Every insight should help {company_name} compete better
- Risk analysis must be specific, quantified where possible, and actionable
"""

        user_prompt = f"""Analyze the following competitive intelligence data for {company_name}:

**QUERY:** {query}

**YOUR COMPANY:** {company_name}

**COMPETITORS ANALYZED:** {', '.join(competitors)}

**COMPETITIVE DATA:**
{context}

Provide a comprehensive competitive analysis following the structure in your system prompt. 
Focus on answering the specific query "{query}" while providing strategic context that helps 
{company_name} understand the competitive landscape and identify opportunities.

Remember to skip section 6 (Additional Insights) if the query only asks about standard topics 
like pricing, features, positioning, or risks."""

        logger.info(f"🤖 Calling {self.model} for {company_name}...")
        
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
                max_tokens=3000  # Increased to accommodate risk analysis section
            )
        )
        
        analysis = response.choices[0].message.content
        
        # Log token usage for monitoring
        usage = response.usage
        logger.info(f"📊 Token usage: {usage.total_tokens} total "
                f"({usage.prompt_tokens} prompt + {usage.completion_tokens} completion)")
        
        # Calculate approximate cost
        if self.use_premium:
            # GPT-4o pricing (approximate as of 2024)
            prompt_cost = usage.prompt_tokens * 0.000005  # $5 per 1M tokens
            completion_cost = usage.completion_tokens * 0.000015  # $15 per 1M tokens
            cost = prompt_cost + completion_cost
        else:
            # GPT-4o-mini pricing (approximate as of 2024)
            prompt_cost = usage.prompt_tokens * 0.00000015  # $0.15 per 1M tokens
            completion_cost = usage.completion_tokens * 0.0000006  # $0.60 per 1M tokens
            cost = prompt_cost + completion_cost
        
        logger.info(f"💰 Estimated cost: ${cost:.4f}")
        
        return analysis
    
    async def _extract_chart_data(
        self,
        analysis: str,
        company_name: str,
        competitors: List[str]
    ) -> Dict:
        """
        Extract structured chart data from the analysis text.
        
        Uses GPT to parse the analysis and extract:
        - Pricing data for bar chart
        - Feature scores for radar chart
        - Risk data for risk matrix
        
        Args:
            analysis: The markdown analysis text
            company_name: Your company name
            competitors: List of competitor names
            
        Returns:
            Dictionary with chart data, or None if extraction fails
        """
        
        if not competitors:
            logger.warning("⚠️  No competitors to create charts for")
            return None
        
        # Build competitors list for JSON template
        comp_json_examples = []
        for i, comp in enumerate(competitors[:3]):  # Limit to 3 for template
            comp_json_examples.append(f'"{comp}": {7 + i}')
        
        competitors_json = ',\n            '.join(comp_json_examples)
        
        extraction_prompt = f"""Extract structured data from this competitive analysis for visualization charts.

**ANALYSIS TEXT:**
{analysis[:4000]}

**YOUR TASK:**
Parse the analysis and extract pricing, feature scores, and risk data. 
Return ONLY valid JSON with no markdown formatting or explanation.

**REQUIRED JSON STRUCTURE:**
{{
    "pricing": [
        {{"company": "{company_name}", "price": 9.99}},
        {{"company": "{competitors[0] if competitors else 'Competitor1'}", "price": 10.99}}
    ],
    "features": [
        {{
            "feature": "Content Quality",
            "{company_name}": 8,
            {competitors_json}
        }},
        {{
            "feature": "Pricing",
            "{company_name}": 7,
            {competitors_json}
        }},
        {{
            "feature": "User Experience",
            "{company_name}": 9,
            {competitors_json}
        }},
        {{
            "feature": "Innovation",
            "{company_name}": 8,
            {competitors_json}
        }},
        {{
            "feature": "Market Reach",
            "{company_name}": 9,
            {competitors_json}
        }}
    ],
    "risks": [
        {{"risk": "Price Sensitivity", "impact": 8, "likelihood": 9}},
        {{"risk": "Content Competition", "impact": 9, "likelihood": 8}}
    ]
}}

**EXTRACTION RULES:**
1. **Pricing**: Extract from "PRICING COMPARISON" section
   - Use base/standard tier monthly price in USD
   - If price ranges given (e.g., "$9.99-$22.99"), use the lowest tier
   - If no exact price, estimate based on tier descriptions
   
2. **Features**: Score 0-10 based on analysis (10=excellent, 0=poor)
   - Extract 5 key features mentioned in "FEATURE ANALYSIS" section
   - Score {company_name} and all competitors on each feature
   - Features might include: Content Quality, Pricing, User Experience, Innovation, Market Reach, etc.
   
3. **Risks**: Extract from "RISK ANALYSIS" section
   - Get top 3-5 critical risks mentioned
   - Impact & Likelihood: Convert High=9, Medium=6, Low=3
   - If exact scores not stated, estimate based on risk description

**IMPORTANT:**
- Return ONLY the JSON object
- No markdown code blocks
- No explanations before or after
- Ensure all JSON is valid (proper quotes, commas, brackets)

Return the JSON now:"""

        try:
            logger.info("📊 Extracting chart data from analysis...")
            
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="gpt-4o-mini",  # Use mini for cost efficiency
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a data extraction expert. Extract structured data and return ONLY valid JSON."
                        },
                        {
                            "role": "user",
                            "content": extraction_prompt
                        }
                    ],
                    temperature=0.1,  # Very low for consistent extraction
                    max_tokens=1500
                )
            )
            
            chart_data_str = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if chart_data_str.startswith("```"):
                lines = chart_data_str.split("\n")
                chart_data_str = "\n".join(lines[1:-1]) if len(lines) > 2 else chart_data_str
                if chart_data_str.startswith("json"):
                    chart_data_str = chart_data_str[4:]
            
            chart_data_str = chart_data_str.strip()
            
            # Parse JSON
            chart_data = json.loads(chart_data_str)
            
            # Validate structure
            if not isinstance(chart_data.get('pricing'), list):
                raise ValueError("Invalid pricing data structure")
            if not isinstance(chart_data.get('features'), list):
                raise ValueError("Invalid features data structure")
            if not isinstance(chart_data.get('risks'), list):
                raise ValueError("Invalid risks data structure")
            
            logger.info(f"✅ Chart data extracted: {len(chart_data.get('pricing', []))} pricing points, "
                       f"{len(chart_data.get('features', []))} features, "
                       f"{len(chart_data.get('risks', []))} risks")
            
            return chart_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse chart data JSON: {str(e)}")
            logger.error(f"Raw response: {chart_data_str[:200]}...")
            return None
            
        except Exception as e:
            logger.error(f"❌ Chart data extraction failed: {str(e)}")
            return None
    
    def __repr__(self):
        mode = "premium" if self.use_premium else "standard"
        return f"AnalysisAgent(name={self.name}, model={self.model}, mode={mode})"