"""
Test LangGraph Workflow End-to-End.

This tests the complete workflow orchestration:
1. Creates workflow
2. Prepares initial state
3. Executes workflow
4. Validates results
"""

import pytest
import asyncio
import time
from app.graph.workflow import (
    create_competitive_intelligence_workflow,
    create_initial_state
)
from app.config import settings


@pytest.mark.asyncio
async def test_langgraph_workflow():
    """
    Test the complete LangGraph workflow with 3 competitors.
    """
    
    print("\n" + "="*70)
    print("LANGGRAPH WORKFLOW TEST")
    print("="*70)
    
    # ===== STEP 1: CREATE WORKFLOW =====
    print("\nSTEP 1: Creating LangGraph Workflow...")
    
    workflow = create_competitive_intelligence_workflow(
        tavily_api_key=settings.tavily_api_key,
        openai_api_key=settings.openai_api_key,
        use_premium_analysis=False  # Standard mode for testing
    )
    
    print("Workflow created successfully!")
    
    # ===== STEP 2: PREPARE INITIAL STATE =====
    print("\nSTEP 2: Preparing Initial State...")
    
    initial_state = create_initial_state(
        query="AI search API pricing and features",
        company_name="Tavily",
        competitors=[
            "Perplexity AI",
            "You.com",
            "Exa"
        ]
    )
    
    print(f"   Initial state prepared:")
    print(f"   - Query: {initial_state['query']}")
    print(f"   - Company: {initial_state['company_name']}")
    print(f"   - Competitors: {len(initial_state['competitors'])}")
    
    # ===== STEP 3: EXECUTE WORKFLOW =====
    print("\n STEP 3: Executing Workflow...")
    print("   This will run all 4 agents in sequence:")
    print("   Research → Extraction → Crawl → Analysis")
    print()
    
    start_time = time.time()
    
    # Run the workflow (LangGraph orchestrates everything!)
    final_state = await workflow.ainvoke(initial_state)
    
    execution_time = time.time() - start_time
    
    print(f"\nWorkflow completed in {execution_time:.2f}s")
    
    # ===== STEP 4: VALIDATE RESULTS =====
    print("\nSTEP 4: Validating Results...")
    
    # Check research results
    research_success = sum(
        1 for r in final_state['research_results'] 
        if r.get('status') == 'success'
    )
    print(f"Research: {research_success}/{len(final_state['competitors'])} competitors")
    
    # Check extraction results
    extraction_success = sum(
        1 for e in final_state['extracted_data']
        if e.get('status') == 'success'
    )
    print(f"Extraction: {extraction_success} pages extracted")
    
    # Check crawl results
    crawl_success = sum(
        1 for c in final_state['crawl_results']
        if c.get('status') == 'success'
    )
    total_pages_crawled = sum(
        c.get('pages_crawled', 0) 
        for c in final_state['crawl_results']
        if c.get('status') == 'success'
    )
    print(f"Crawl: {crawl_success} sites crawled, {total_pages_crawled} pages discovered")
    
    # Check analysis
    if final_state.get('analysis'):
        analysis_length = len(final_state['analysis'])
        print(f"Analysis: Generated ({analysis_length:,} characters)")
    else:
        print(f"Analysis: Failed")
    
    # Check completed agents
    completed = final_state.get('completed_agents', [])
    print(f"\nCompleted agents: {', '.join(completed)}")
    
    # Check errors
    errors = final_state.get('errors', [])
    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors:
            print(f"   - {error}")
    else:
        print(f"\nNo errors!")
    
    # ===== STEP 5: DISPLAY SAMPLE OUTPUT =====
    print("\n" + "="*70)
    print("SAMPLE OUTPUT")
    print("="*70)
    
    if final_state.get('analysis'):
        # Show first 500 characters of analysis
        analysis_preview = final_state['analysis'][:500]
        print(f"\n{analysis_preview}...")
        print(f"\n... [truncated, full analysis is {len(final_state['analysis']):,} characters]")
    
    print("\n" + "="*70)
    print("LANGGRAPH TEST COMPLETE!")
    print("="*70)
    print(f"\n Summary:")
    print(f"   - Workflow execution time: {execution_time:.2f}s")
    print(f"   - Competitors analyzed: {len(final_state['competitors'])}")
    print(f"   - Research results: {len(final_state['research_results'])}")
    print(f"   - Extracted pages: {len(final_state['extracted_data'])}")
    print(f"   - Crawled sites: {len(final_state['crawl_results'])}")
    print(f"   - Analysis generated: {'Yes' if final_state.get('analysis') else 'No'}")
    print(f"   - Errors: {len(final_state.get('errors', []))}")
    print()
    
    return final_state


@pytest.mark.asyncio
async def test_workflow_state_flow():
    """
    Test that state flows correctly between agents.
    """
    
    print("\n" + "="*70)
    print(" STATE FLOW TEST")
    print("="*70)
    
    print("\nThis test verifies that state is properly passed between agents.")
    
    workflow = create_competitive_intelligence_workflow(
        tavily_api_key=settings.tavily_api_key,
        openai_api_key=settings.openai_api_key,
        use_premium_analysis=False
    )
    
    initial_state = create_initial_state(
        query="pricing",
        company_name="TestCorp",
        competitors=["Competitor A"]
    )
    
    print("\n Initial State:")
    print(f"   - research_results: {len(initial_state['research_results'])} (should be 0)")
    print(f"   - extracted_data: {len(initial_state['extracted_data'])} (should be 0)")
    print(f"   - crawl_results: {len(initial_state['crawl_results'])} (should be 0)")
    print(f"   - analysis: {initial_state['analysis']} (should be None)")
    print(f"   - completed_agents: {initial_state['completed_agents']} (should be [])")
    
    print("\n Running workflow...")
    final_state = await workflow.ainvoke(initial_state)
    
    print("\n Final State:")
    print(f"   - research_results: {len(final_state['research_results'])} (should be > 0)")
    print(f"   - extracted_data: {len(final_state['extracted_data'])} (should be > 0)")
    print(f"   - crawl_results: {len(final_state['crawl_results'])} (should be > 0)")
    print(f"   - analysis: {'Present' if final_state['analysis'] else 'None'} (should be Present)")
    print(f"   - completed_agents: {final_state['completed_agents']}")
    
    # Validate state flow
    expected_agents = ['research', 'extraction', 'crawl', 'analysis']
    completed = final_state.get('completed_agents', [])
    
    print("\n Validation:")
    for agent in expected_agents:
        if agent in completed:
            print(f"     {agent} completed")
        else:
            print(f"     {agent} NOT completed")
    
    if set(expected_agents) == set(completed):
        print("\n STATE FLOW TEST PASSED!")
    else:
        print("\n STATE FLOW TEST FAILED!")
    
    print("="*70 + "\n")


async def main():
    """Run all LangGraph tests"""
    
    print("\n" + "RUNNING LANGGRAPH TESTS")
    
    # Test 1: Full workflow
    await test_langgraph_workflow()
    
    # Test 2: State flow
    await test_workflow_state_flow()
    
    print("ALL TESTS COMPLETE!\n")


if __name__ == "__main__":
    asyncio.run(main())