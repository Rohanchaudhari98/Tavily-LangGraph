"""
Analysis Agent

Synthesizes all gathered data into a comprehensive competitive intelligence report.
Uses GPT-4 for deep analysis and strategic insights.
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
    Creates competitive intelligence reports using GPT-4.
    
    Supports two modes:
    - Standard (gpt-4o-mini): Fast and cost-effective
    - Premium (gpt-4o): Highest quality, more expensive
    """
    
    def __init__(self, openai_api_key: str, use_premium: bool = False, query_id: str = None, db = None):
        self.client = OpenAI(
            api_key=openai_api_key,
            timeout=180.0,  # 3 minute timeout for streaming (longer for analysis)
            max_retries=3
        )
        self.name = "analysis"
        self.use_premium = use_premium
        self.query_id = query_id 
        self.db = db
        
        if use_premium:
            self.model = "gpt-4o"
            logger.info("Using PREMIUM mode (gpt-4o)")
        else:
            self.model = "gpt-4o-mini"
            logger.info("Using STANDARD mode (gpt-4o-mini)")
    
    async def execute(self, state: Dict) -> Dict:
        # Generate competitive intelligence report from all gathered data
        research_results = state.get("research_results", [])
        extracted_data = state.get("extracted_data", [])
        crawl_results = state.get("crawl_results", [])
        query = state.get("query", "")
        company_name = state.get("company_name", "Your Company")
        competitors = state.get("competitors", [])
        
        logger.info(f"Starting analysis...")
        logger.info(f"Mode: {'PREMIUM (gpt-4o)' if self.use_premium else 'STANDARD (gpt-4o-mini)'}")
        logger.info(f"Company: {company_name}")
        logger.info(f"Query: {query}")
        logger.info(f"Analyzing {len(competitors)} competitors")
        
        # Make sure we have something to analyze
        if not research_results and not extracted_data and not crawl_results:
            logger.warning("No data to analyze")
            return {
                **state,
                "analysis": None,
                "chart_data": None,
                "errors": state.get("errors", []) + ["No data available for analysis"],
                "current_step": "analysis_failed",
                "completed_agents": state.get("completed_agents", []) + [self.name],
                "updated_at": datetime.now()
            }
        
        # Combine all data into context
        analysis_context = self._prepare_context(
            query, 
            competitors,
            research_results, 
            extracted_data,
            crawl_results
        )
        
        logger.info(f"Context prepared: {len(analysis_context)} characters")
        
        try:
            # Generate the analysis with streaming
            # Pass callback to update MongoDB during streaming
            async def update_mongodb(partial_analysis: str):
                if self.query_id and self.db and partial_analysis:
                    try:
                        await self.db.update_query(self.query_id, {
                            "analysis": partial_analysis,
                            "updated_at": datetime.now()
                        })
                    except Exception as e:
                        logger.warning(f"Failed to update MongoDB during streaming: {e}")
            
            analysis_result = await self._generate_analysis(
                query,
                company_name,
                competitors,
                analysis_context,
                update_callback=update_mongodb if self.query_id and self.db else None
            )
            
            logger.info(f"Analysis complete: {len(analysis_result)} characters")
            
            # Pull out structured data for charts
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
            logger.error(f"Analysis failed: {str(e)}")
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
        # Bundle all collected data into a single context string
        context_parts = []
        
        # Add search summaries
        if research_results:
            context_parts.append("=== RESEARCH SUMMARIES ===\n")
            for result in research_results:
                if result.get("status") == "success":
                    competitor = result.get("competitor")
                    answer = result.get("answer", "")
                    context_parts.append(f"\n{competitor}:")
                    context_parts.append(f"{answer}\n")
        
        # Add extracted page content
        if extracted_data:
            context_parts.append("\n=== EXTRACTED CONTENT ===\n")
            for data in extracted_data:
                if data.get("status") == "success":
                    competitor = data.get("competitor")
                    url = data.get("url")
                    content = data.get("raw_content", "")
                    
                    # Keep it reasonable, truncate if needed
                    truncated_content = content[:2000]
                    if len(content) > 2000:
                        truncated_content += "... [truncated]"
                    
                    context_parts.append(f"\n{competitor} - {url}:")
                    context_parts.append(f"{truncated_content}\n")
        
        # Add crawl findings
        if crawl_results:
            context_parts.append("\n=== DEEP CRAWL FINDINGS ===\n")
            for crawl in crawl_results:
                if crawl.get("status") == "success":
                    competitor = crawl.get("competitor")
                    pages_crawled = crawl.get("pages_crawled", 0)
                    content = crawl.get("combined_content", "")
                    
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
        context: str,
        update_callback=None
    ) -> str:
        # Generate the competitive intelligence report using GPT with streaming
        system_prompt = f"""You are a competitive intelligence analyst working for {company_name}.

                            USER'S QUERY: "{query}"

                            CRITICAL: All analysis must be from {company_name}'s perspective. Frame everything as advice TO {company_name} ABOUT their competitors.

                            Create a comprehensive competitive intelligence report with these sections:

                            1. EXECUTIVE SUMMARY
                            - Overview addressing the query directly
                            - Key insights about competitor positioning
                            - Main opportunities and threats for {company_name}

                            2. PRICING COMPARISON
                            - How competitors price their offerings
                            - What pricing strategies they use
                            - What this means for {company_name}'s pricing
                            - How {company_name} can price competitively

                            3. FEATURE ANALYSIS
                            - What features competitors offer
                            - Unique capabilities that stand out
                            - Feature gaps {company_name} could exploit
                            - Where {company_name} might have advantages

                            4. MARKET POSITIONING
                            - How competitors position themselves
                            - Customer segments they target
                            - Value propositions they use
                            - How {company_name} should position to stand out

                            5. RISK ANALYSIS
                            Strategic risk assessment from {company_name}'s perspective:
                            
                            CRITICAL RISKS (immediate attention):
                            - Competitive threats with high impact AND high likelihood
                            - What threatens {company_name}'s market position
                            - Pricing pressures that could hurt revenue
                            - Feature gaps risking customer churn
                            
                            For each risk provide:
                            - Clear threat description
                            - Impact level: High/Medium/Low (with justification)
                            - Likelihood: High/Medium/Low (based on observations)
                            - Mitigation action for {company_name}
                            - Timeline (e.g., "Q1 2024", "Within 6 months")
                            
                            EMERGING RISKS (monitor and prepare):
                            - Market trends becoming threats
                            - Technology shifts competitors adopt
                            - New entrants disrupting the market
                            
                            Format each critical risk as:
                            **Risk Name** (Impact: X | Likelihood: Y)
                            - **Threat**: [Specific competitive threat]
                            - **Impact on {company_name}**: [Business impact]
                            - **Mitigation**: [Specific action]
                            - **Timeline**: [When to act]

                            6. ADDITIONAL INSIGHTS (only if query requires it)
                            - Topics like: customer support, partnerships, brand reputation, 
                                company culture, tech stack, marketing, geographic presence
                            - Address unique aspects from the query
                            - Skip entirely if not needed for the query

                            7. STRATEGIC RECOMMENDATIONS FOR {company_name}
                            - Opportunities {company_name} should pursue
                            - Competitive advantages to leverage
                            - Differentiation areas
                            - Short-term moves (3-6 months)
                            - Long-term initiatives (6-12+ months)

                            FORMATTING:
                            - Use markdown (## for sections, ### for subsections)
                            - Professional, analytical tone
                            - Specific and data-driven
                            - Actionable for {company_name}
                            - Focused on the query
                            - Bullet points for clarity

                            REMEMBER: Write as if presenting TO {company_name}, not about them. 
                            Say "{company_name} should..." not "the competitor should..."
                            """

        user_prompt = f"""Analyze this competitive intelligence data for {company_name}:

                        QUERY: {query}

                        YOUR COMPANY: {company_name}

                        COMPETITORS: {', '.join(competitors)}

                        COMPETITIVE DATA:
                        {context}

                        Provide comprehensive competitive analysis following the structure in your system prompt.
                        Skip section 6 (Additional Insights) if the query only asks about pricing, features, positioning, or risks."""

        logger.info(f"Calling {self.model} for analysis (streaming)...")
        
        # Use streaming for real-time updates
        loop = asyncio.get_event_loop()
        
        try:
            stream = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=4000,  # Increased to prevent truncation
                    stream=True
                )
            )
            
            # Collect streamed chunks
            analysis = ""
            chunk_count = 0
            
            try:
                for chunk in stream:
                    # Check if stream was interrupted
                    if not chunk.choices:
                        logger.warning("Received empty chunk, stream may have ended")
                        break
                    
                    # Check for finish reason (stream completion) - check before processing content
                    if chunk.choices[0].finish_reason:
                        logger.info(f"Stream finished with reason: {chunk.choices[0].finish_reason}")
                        if chunk.choices[0].finish_reason == "length":
                            logger.warning("Analysis was truncated due to max_tokens limit")
                        break
                    
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        analysis += content
                        chunk_count += 1
                        
                        # Update MongoDB every 20 chunks on AWS (less frequent to reduce overhead)
                        # More frequent updates on localhost for better UX
                        update_frequency = 20  # Reduced from 10 to reduce AWS DB overhead
                        if update_callback and chunk_count % update_frequency == 0:
                            try:
                                await update_callback(analysis)
                            except Exception as e:
                                logger.warning(f"Failed to update MongoDB during streaming: {e}")
                                # Continue streaming even if update fails
                
            except Exception as stream_error:
                logger.error(f"Error during stream processing: {str(stream_error)}")
                # Return partial analysis if we have any
                if analysis:
                    logger.warning(f"Returning partial analysis ({len(analysis)} chars) due to stream error")
                else:
                    raise  # Re-raise if we have no analysis at all
            
            # Final update
            if update_callback and analysis:
                try:
                    await update_callback(analysis)
                except Exception as e:
                    logger.warning(f"Failed final MongoDB update: {e}")
            
            logger.info(f"Analysis streamed: {len(analysis)} characters in {chunk_count} chunks")
            
            if not analysis:
                raise ValueError("Analysis stream completed but no content was received")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to generate analysis stream: {str(e)}")
            raise
    
    async def _extract_chart_data(
        self,
        analysis: str,
        company_name: str,
        competitors: List[str]
    ) -> Dict:
        """
        Parse the analysis text to extract structured data for charts.
        Uses GPT to pull out pricing, features, and risks.
        """
        
        if not competitors:
            logger.warning("No competitors for charts")
            return None
        
        # Build example JSON structure for the prompt
        comp_json_examples = []
        for i, comp in enumerate(competitors[:3]):
            comp_json_examples.append(f'"{comp}": {7 + i}')
        
        competitors_json = ',\n            '.join(comp_json_examples)
        
        extraction_prompt = f"""Extract structured data from this competitive analysis for charts.

                                ANALYSIS TEXT:
                                {analysis[:4000]}

                                Extract pricing, feature scores, and risk data. Return ONLY valid JSON with no markdown.

                                REQUIRED JSON STRUCTURE:
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
                                        }}
                                    ],
                                    "risks": [
                                        {{"risk": "Price Sensitivity", "impact": 8, "likelihood": 9}},
                                        {{"risk": "Content Competition", "impact": 9, "likelihood": 8}}
                                    ]
                                }}

                                EXTRACTION RULES:
                                1. Pricing: Extract from "PRICING COMPARISON" section
                                - Use base monthly price in USD
                                - If range given, use lowest tier
                                
                                2. Features: Score 0-10 (10=excellent)
                                - Extract 5 key features from "FEATURE ANALYSIS"
                                - Score {company_name} and all competitors
                                
                                3. Risks: Extract from "RISK ANALYSIS" section
                                - Top 3-5 critical risks
                                - Convert High=9, Medium=6, Low=3

                                Return ONLY the JSON object:"""

        try:
            logger.info("Extracting chart data from analysis...")
            
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "Extract structured data and return ONLY valid JSON."
                        },
                        {
                            "role": "user",
                            "content": extraction_prompt
                        }
                    ],
                    temperature=0.1,
                    max_tokens=1500
                )
            )
            
            chart_data_str = response.choices[0].message.content.strip()
            
            # Strip markdown code blocks if present
            if chart_data_str.startswith("```"):
                lines = chart_data_str.split("\n")
                chart_data_str = "\n".join(lines[1:-1]) if len(lines) > 2 else chart_data_str
                if chart_data_str.startswith("json"):
                    chart_data_str = chart_data_str[4:]
            
            chart_data_str = chart_data_str.strip()
            
            # Parse and validate
            chart_data = json.loads(chart_data_str)
            
            if not isinstance(chart_data.get('pricing'), list):
                raise ValueError("Invalid pricing data structure")
            if not isinstance(chart_data.get('features'), list):
                raise ValueError("Invalid features data structure")
            if not isinstance(chart_data.get('risks'), list):
                raise ValueError("Invalid risks data structure")
            
            logger.info(f"Chart data extracted: {len(chart_data.get('pricing', []))} pricing points, "
                       f"{len(chart_data.get('features', []))} features, "
                       f"{len(chart_data.get('risks', []))} risks")
            
            return chart_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse chart JSON: {str(e)}")
            logger.error(f"Raw response: {chart_data_str[:200]}...")
            return None
            
        except Exception as e:
            logger.error(f"Chart extraction failed: {str(e)}")
            return None
    
    def __repr__(self):
        mode = "premium" if self.use_premium else "standard"
        return f"AnalysisAgent(name={self.name}, model={self.model}, mode={mode})"