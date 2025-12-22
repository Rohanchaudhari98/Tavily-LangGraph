"""
Analysis Agent

Generates competitive intelligence reports using GPT-4.
Analyzes gathered data and provides structured insights.
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
    Builds competitive intelligence reports with GPT-4.
    
    Two modes:
    - Standard (gpt-4o-mini): Faster and cheaper
    - Premium (gpt-4o): Higher quality, more expensive
    """
    
    def __init__(self, openai_api_key: str, use_premium: bool = False, query_id: str = None, db = None):
        self.client = OpenAI(
            api_key=openai_api_key,
            timeout=180.0,  # Timeout for analysis and streaming
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
        # Extract data from state
        research_results = state.get("research_results", [])
        extracted_data = state.get("extracted_data", [])
        crawl_results = state.get("crawl_results", [])
        query = state.get("query", "")
        company_name = state.get("company_name", "Your Company")
        competitors = state.get("competitors", [])
        
        logger.info(f"Starting analysis for {company_name}, query: {query}")
        logger.info(f"Mode: {'PREMIUM' if self.use_premium else 'STANDARD'}")
        logger.info(f"Analyzing {len(competitors)} competitors")
        
        # Return early if no data is available
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
        
        # Combine data into one context string
        analysis_context = self._prepare_context(
            query, 
            competitors,
            research_results, 
            extracted_data,
            crawl_results
        )
        
        logger.info(f"Context prepared: {len(analysis_context)} characters")
        
        try:
            # Callback for streaming updates to database
            async def update_mongodb(partial_analysis: str):
                if self.query_id and self.db and partial_analysis:
                    try:
                        await self.db.update_query(self.query_id, {
                            "analysis": partial_analysis,
                            "updated_at": datetime.now()
                        })
                    except Exception as e:
                        logger.warning(f"Failed to update MongoDB during streaming: {e}")
            
            # Generate the analysis
            analysis_result = await self._generate_analysis(
                query,
                company_name,
                competitors,
                analysis_context,
                update_callback=update_mongodb if self.query_id and self.db else None
            )
            
            logger.info(f"Analysis complete: {len(analysis_result)} characters")
            
            # Extract chart data from the analysis
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
        # Merge all collected data into a single string
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
                    
                    # Truncate if too long
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
        # Generate a report using GPT with streaming
        system_prompt = f"""You are a competitive intelligence analyst working for {company_name}.
...
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
        
        # Stream the model's output
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
                    max_tokens=4000,
                    stream=True
                )
            )
            
            analysis = ""
            chunk_count = 0
            
            try:
                for chunk in stream:
                    if not chunk.choices:
                        logger.warning("Empty chunk received")
                        break
                    if chunk.choices[0].finish_reason:
                        logger.info(f"Stream finished: {chunk.choices[0].finish_reason}")
                        if chunk.choices[0].finish_reason == "length":
                            logger.warning("Analysis truncated due to max_tokens limit")
                        break
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        analysis += content
                        chunk_count += 1
                        
                        # Update DB periodically
                        if update_callback and chunk_count % 20 == 0:
                            try:
                                await update_callback(analysis)
                            except Exception as e:
                                logger.warning(f"Failed to update DB during streaming: {e}")
                
            except Exception as stream_error:
                logger.error(f"Error in stream: {str(stream_error)}")
                if analysis:
                    logger.warning(f"Returning partial analysis ({len(analysis)} chars)")
                else:
                    raise
            
            # Final DB update
            if update_callback and analysis:
                try:
                    await update_callback(analysis)
                except Exception as e:
                    logger.warning(f"Failed final DB update: {e}")
            
            logger.info(f"Analysis streamed: {len(analysis)} characters in {chunk_count} chunks")
            
            if not analysis:
                raise ValueError("Stream completed but no content received")
            
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
        Pull structured chart data from analysis.
        Returns pricing, features, and risks in JSON.
        """
        
        if not competitors:
            logger.warning("No competitors for chart extraction")
            return None
        
        comp_json_examples = []
        for i, comp in enumerate(competitors[:3]):
            comp_json_examples.append(f'"{comp}": {7 + i}')
        
        competitors_json = ',\n            '.join(comp_json_examples)
        
        extraction_prompt = f"""Extract structured data from this analysis for charts...
[Prompt truncated for brevity]"""

        try:
            logger.info("Extracting chart data...")
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Extract structured data and return ONLY valid JSON."},
                        {"role": "user", "content": extraction_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=1500
                )
            )
            
            chart_data_str = response.choices[0].message.content.strip()
            if chart_data_str.startswith("```"):
                lines = chart_data_str.split("\n")
                chart_data_str = "\n".join(lines[1:-1]) if len(lines) > 2 else chart_data_str
                if chart_data_str.startswith("json"):
                    chart_data_str = chart_data_str[4:]
            chart_data_str = chart_data_str.strip()
            
            chart_data = json.loads(chart_data_str)
            
            if not isinstance(chart_data.get('pricing'), list):
                raise ValueError("Invalid pricing data")
            if not isinstance(chart_data.get('features'), list):
                raise ValueError("Invalid features data")
            if not isinstance(chart_data.get('risks'), list):
                raise ValueError("Invalid risks data")
            
            logger.info(f"Chart data extracted: {len(chart_data.get('pricing', []))} pricing, "
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
