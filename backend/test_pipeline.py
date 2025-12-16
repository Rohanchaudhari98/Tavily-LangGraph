"""
Complete Pipeline Test - Research → Extraction → Crawl → Analysis
"""

import asyncio
import time
from app.agents.research_agent import ResearchAgent
from app.agents.extraction_agent import ExtractionAgent
from app.agents.crawl_agent import CrawlAgent
from app.agents.analysis_agent import AnalysisAgent
from app.config import settings

async def test_complete_pipeline(
    competitors: list[str],
    query: str = "AI search API pricing, features, and developer experience",
    use_premium_analysis: bool = False
):
    """
    Complete test of the entire competitive intelligence pipeline.
    
    Args:
        competitors: List of competitor names (can be any number)
        query: Research query
        use_premium_analysis: If True, use GPT-4o; if False, use GPT-4o-mini
    """
    
    # Initialize all agents
    research_agent = ResearchAgent(tavily_api_key=settings.tavily_api_key)
    extraction_agent = ExtractionAgent(tavily_api_key=settings.tavily_api_key)
    crawl_agent = CrawlAgent(tavily_api_key=settings.tavily_api_key)
    analysis_agent = AnalysisAgent(
        openai_api_key=settings.openai_api_key,
        use_premium=use_premium_analysis
    )
    
    initial_state = {
        "query": query,
        "company_name": "Tavily",
        "competitors": competitors,
        "research_results": [],
        "extracted_data": [],
        "crawl_results": [],
        "analysis": None,
        "completed_agents": [],
        "errors": [],
        "updated_at": None
    }
    
    print("\n" + "="*70)
    print("🎯 COMPETITIVE INTELLIGENCE PIPELINE")
    print("="*70)
    print(f"\n📋 Query: {initial_state['query']}")
    print(f"🏢 Company: {initial_state['company_name']}")
    print(f"🔍 Analyzing: {', '.join(competitors)}")
    print(f"🔢 Total competitors: {len(competitors)}")
    print(f"⚙️  Analysis mode: {'🌟 PREMIUM (GPT-4o)' if use_premium_analysis else '⚡ STANDARD (GPT-4o-mini)'}")
    print()
    
    # Track total time
    pipeline_start = time.time()
    
    # ========================================================================
    # STEP 1: RESEARCH
    # ========================================================================
    print("="*70)
    print("STEP 1/4: 🔍 RESEARCH AGENT (Parallel Processing)")
    print("="*70 + "\n")
    
    research_start = time.time()
    state = await research_agent.execute(initial_state)
    research_time = time.time() - research_start
    
    print(f"\n✅ Research Complete in {research_time:.2f}s")
    
    # Show detailed research results
    print("\n📊 RESEARCH RESULTS:")
    print("-" * 70)
    
    for result in state['research_results']:
        print(f"\n🏢 {result['competitor'].upper()}")
        print(f"   Status: {'✅ Success' if result['status'] == 'success' else '❌ Failed'}")
        
        if result['status'] == 'success':
            print(f"   URLs Found: {len(result['results'])}")
            
            # Show AI-generated answer
            answer = result.get('answer', '')
            if answer:
                print(f"\n   🤖 AI Summary:")
                print(f"   {answer[:200]}...")
            
            # Show top 3 URLs
            print(f"\n   🔗 Top Sources:")
            for i, item in enumerate(result['results'][:3], 1):
                print(f"      {i}. {item.get('title', 'No title')[:50]}")
                print(f"         {item.get('url')}")
        else:
            print(f"   Error: {result.get('error', 'Unknown')}")
    
    # ========================================================================
    # STEP 2: EXTRACTION
    # ========================================================================
    print("\n" + "="*70)
    print("STEP 2/4: 📄 EXTRACTION AGENT (Parallel Processing)")
    print("="*70 + "\n")
    
    extraction_start = time.time()
    state = await extraction_agent.execute(state)
    extraction_time = time.time() - extraction_start
    
    print(f"\n✅ Extraction Complete in {extraction_time:.2f}s")
    
    # Show extraction summary by competitor
    print("\n📄 EXTRACTED CONTENT SUMMARY:")
    print("-" * 70)
    
    # Group by competitor
    by_competitor = {}
    for data in state['extracted_data']:
        comp = data['competitor']
        if comp not in by_competitor:
            by_competitor[comp] = []
        by_competitor[comp].append(data)
    
    for competitor, extractions in by_competitor.items():
        print(f"\n🏢 {competitor.upper()}")
        print(f"   Pages Extracted: {len(extractions)}")
        
        successful = sum(1 for e in extractions if e['status'] == 'success')
        total_chars = sum(e.get('content_length', 0) for e in extractions if e['status'] == 'success')
        
        print(f"   Successful: {successful}/{len(extractions)}")
        print(f"   Total content: {total_chars:,} characters")
        
        # Show first URL
        if extractions and extractions[0]['status'] == 'success':
            print(f"   Sample URL: {extractions[0]['url'][:60]}...")
    
    # ========================================================================
    # STEP 3: CRAWL
    # ========================================================================
    print("\n" + "="*70)
    print("STEP 3/4: 🕷️ CRAWL AGENT (Deep Website Analysis)")
    print("="*70 + "\n")
    
    crawl_start = time.time()
    state = await crawl_agent.execute(state)
    crawl_time = time.time() - crawl_start
    
    print(f"\n✅ Crawl Complete in {crawl_time:.2f}s")
    
    # Show crawl summary
    print("\n🕷️ CRAWL RESULTS SUMMARY:")
    print("-" * 70)
    
    for crawl in state['crawl_results']:
        print(f"\n🏢 {crawl['competitor'].upper()}")
        print(f"   Status: {'✅ Success' if crawl['status'] == 'success' else '❌ Failed'}")
        
        if crawl['status'] == 'success':
            print(f"   Pages Crawled: {crawl.get('pages_crawled', 0)}")
            print(f"   Total Content: {crawl.get('content_length', 0):,} characters")
            print(f"   Focus Area: {crawl.get('focus', 'N/A')}")
            
            urls = crawl.get('urls_found', [])
            if urls:
                print(f"   Pages Found:")
                for i, url in enumerate(urls[:3], 1):
                    print(f"      {i}. {url[:60]}...")
        else:
            print(f"   Error: {crawl.get('error', 'Unknown')}")
    
    # ========================================================================
    # STEP 4: ANALYSIS
    # ========================================================================
    print("\n" + "="*70)
    print(f"STEP 4/4: 🧠 ANALYSIS AGENT ({'Premium GPT-4o' if use_premium_analysis else 'Standard GPT-4o-mini'})")
    print("="*70 + "\n")
    
    analysis_start = time.time()
    state = await analysis_agent.execute(state)
    analysis_time = time.time() - analysis_start
    
    print(f"\n✅ Analysis Complete in {analysis_time:.2f}s")
    
    # ========================================================================
    # COMPETITIVE INTELLIGENCE REPORT
    # ========================================================================
    if state.get('analysis'):
        print("\n" + "="*70)
        print("📊 COMPETITIVE INTELLIGENCE REPORT")
        print("="*70 + "\n")
        
        # Display the full analysis
        print(state['analysis'])
        
    else:
        print("\n❌ Analysis Failed")
        if state.get('errors'):
            print(f"Errors: {state['errors']}")
    
    # ========================================================================
    # PERFORMANCE METRICS & SUMMARY
    # ========================================================================
    total_time = time.time() - pipeline_start
    
    print("\n" + "="*70)
    print("⚡ PERFORMANCE METRICS")
    print("="*70 + "\n")
    
    print("⏱️  TIMING BREAKDOWN:")
    print(f"   Research:   {research_time:>6.2f}s  ({research_time/total_time*100:>5.1f}%)")
    print(f"   Extraction: {extraction_time:>6.2f}s  ({extraction_time/total_time*100:>5.1f}%)")
    print(f"   Crawl:      {crawl_time:>6.2f}s  ({crawl_time/total_time*100:>5.1f}%)")
    print(f"   Analysis:   {analysis_time:>6.2f}s  ({analysis_time/total_time*100:>5.1f}%)")
    print(f"   {'-'*40}")
    print(f"   TOTAL:      {total_time:>6.2f}s")
    
    print(f"\n📊 DATA PROCESSED:")
    
    # Research metrics
    success_research = sum(1 for r in state['research_results'] if r['status'] == 'success')
    total_urls_found = sum(len(r.get('results', [])) for r in state['research_results'] if r['status'] == 'success')
    
    print(f"   Competitors researched: {success_research}/{len(competitors)}")
    print(f"   Total URLs found: {total_urls_found}")
    
    # Extraction metrics
    success_extract = sum(1 for e in state['extracted_data'] if e['status'] == 'success')
    total_chars = sum(e.get('content_length', 0) for e in state['extracted_data'] if e['status'] == 'success')
    
    print(f"   Pages extracted: {success_extract}/{len(state['extracted_data'])}")
    print(f"   Extraction content: {total_chars:,} characters")
    
    # Crawl metrics
    crawl_count = sum(1 for c in state['crawl_results'] if c['status'] == 'success')
    total_crawl_pages = sum(c.get('pages_crawled', 0) for c in state['crawl_results'] if c['status'] == 'success')
    total_crawl_chars = sum(c.get('content_length', 0) for c in state['crawl_results'] if c['status'] == 'success')
    
    print(f"   Sites crawled: {crawl_count}/{len(state['crawl_results'])}")
    print(f"   Pages discovered: {total_crawl_pages}")
    print(f"   Crawl content: {total_crawl_chars:,} characters")
    
    # Total content
    total_all_content = total_chars + total_crawl_chars
    print(f"   TOTAL CONTENT ANALYZED: {total_all_content:,} characters")
    
    # Analysis metrics
    if state.get('analysis'):
        analysis_length = len(state['analysis'])
        print(f"   Analysis length: {analysis_length:,} characters")
        print(f"   Analysis mode: {state.get('analysis_mode', 'unknown')}")
    
    print(f"\n🚀 EFFICIENCY:")
    sequential_estimate = len(competitors) * 6  # ~6s per competitor with crawl
    speedup = sequential_estimate / total_time if total_time > 0 else 0
    print(f"   Sequential estimate: ~{sequential_estimate}s")
    print(f"   Actual parallel time: {total_time:.2f}s")
    print(f"   Speedup factor: {speedup:.1f}x faster")
    
    print(f"\n✅ PIPELINE STATUS:")
    print(f"   Completed agents: {', '.join(state['completed_agents'])}")
    print(f"   Current step: {state['current_step']}")
    print(f"   Errors: {len(state.get('errors', []))}")
    
    if state.get('errors'):
        print(f"\n⚠️  ERRORS:")
        for error in state['errors']:
            print(f"   - {error}")
    
    print("\n" + "="*70)
    print("✨ PIPELINE TEST COMPLETE!")
    print("="*70 + "\n")
    
    return state


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def main():
    """Run tests with different configurations"""
    
    # Default test: 7 competitors, standard analysis
    print("\n" + "🔵 TEST: 7 COMPETITORS - STANDARD ANALYSIS (GPT-4o-mini)")
    print("="*70)
    
    await test_complete_pipeline(
        competitors=[
            "Perplexity AI",
            "You.com",
            "Exa",
            "SerpAPI",
            "Serper",
            "Bing Search API",
            "Google CSE"
        ],
        query="AI search API pricing, features, and developer experience",
        use_premium_analysis=False  # Standard mode
    )
    
    # Uncomment to test premium analysis
    # print("\n\n" + "🌟 TEST: 3 COMPETITORS - PREMIUM ANALYSIS (GPT-4o)")
    # print("="*70)
    # 
    # await test_complete_pipeline(
    #     competitors=["Perplexity AI", "You.com", "Exa"],
    #     query="AI search API pricing and features",
    #     use_premium_analysis=True  # Premium mode
    # )
    
    # Uncomment to test with more competitors
    # print("\n\n" + "🔴 TEST: 7 COMPETITORS - STANDARD ANALYSIS")
    # print("="*70)
    # 
    # await test_complete_pipeline(
    #     competitors=[
    #         "Perplexity AI", "You.com", "Exa", "SerpAPI", 
    #         "Serper", "Brave Search API", "Bing Search API"
    #     ],
    #     query="search API pricing and features",
    #     use_premium_analysis=False
    # )


if __name__ == "__main__":
    asyncio.run(main())