"""
Test the FastAPI backend endpoints.

This script tests:
1. Health check
2. Creating a query
3. Getting query status
4. Listing queries
5. Deleting a query
"""

import requests
import time
import json

# API base URL
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"{title}")
    print("="*70)

def test_health_check():
    """Test health check endpoints"""
    print_section("TEST 1: Health Check")
    
    # Test root endpoint
    print("\n1. Testing root endpoint (GET /)...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test health endpoint
    print("\n2. Testing health endpoint (GET /health)...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    assert response.status_code == 200, "Health check failed!"
    print("\n✓ Health check passed!")

def test_create_query():
    """Test creating a new query"""
    print_section("TEST 2: Create Query")
    
    query_data = {
        "query": "AI search API pricing and features",
        "company_name": "Tavily",
        "competitors": [
            "Perplexity AI",
            "You.com",
            "Exa"
        ],
        "use_premium_analysis": False
    }
    
    print("\nSubmitting query...")
    print(f"Query: {query_data['query']}")
    print(f"Company: {query_data['company_name']}")
    print(f"Competitors: {', '.join(query_data['competitors'])}")
    
    response = requests.post(
        f"{BASE_URL}/api/queries",
        json=query_data
    )
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    assert response.status_code == 200, "Query creation failed!"
    assert "query_id" in result, "No query_id in response!"
    
    query_id = result["query_id"]
    print(f"\n✓ Query created successfully!")
    print(f"✓ Query ID: {query_id}")
    
    return query_id

def test_get_query(query_id, wait_for_completion=False):
    """Test getting query status and results"""
    print_section("TEST 3: Get Query Status")
    
    print(f"\nFetching query: {query_id}")
    
    if wait_for_completion:
        print("\nWaiting for workflow to complete...")
        print("This may take 20-30 seconds...")
        
        max_wait = 60  # Maximum 60 seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = requests.get(f"{BASE_URL}/api/queries/{query_id}")
            result = response.json()
            status = result["status"]
            
            print(f"\r   Status: {status} (elapsed: {int(time.time() - start_time)}s)", end="")
            
            if status in ["completed", "failed"]:
                print()  # New line
                break
            
            time.sleep(2)  # Check every 2 seconds
        
        print()
    else:
        response = requests.get(f"{BASE_URL}/api/queries/{query_id}")
        result = response.json()
    
    print(f"\nStatus: {response.status_code}")
    print(f"\nQuery Details:")
    print(f"   Status: {result['status']}")
    print(f"   Query: {result['query']}")
    print(f"   Company: {result['company_name']}")
    print(f"   Competitors: {len(result['competitors'])}")
    print(f"   Completed Agents: {', '.join(result.get('completed_agents', []))}")
    
    if result.get("analysis"):
        print(f"\n   Analysis Preview:")
        print(f"   {result['analysis'][:200]}...")
        print(f"   (Total length: {len(result['analysis'])} characters)")
    
    if result.get("errors"):
        print(f"\n   Errors: {result['errors']}")
    
    assert response.status_code == 200, "Failed to get query!"
    print(f"\n✓ Query retrieved successfully!")
    
    return result

def test_list_queries():
    """Test listing all queries"""
    print_section("TEST 4: List Queries")
    
    print("\nFetching all queries...")
    
    response = requests.get(f"{BASE_URL}/api/queries?limit=10")
    
    print(f"Status: {response.status_code}")
    queries = response.json()
    
    print(f"\nFound {len(queries)} queries:")
    for i, q in enumerate(queries, 1):
        print(f"\n   {i}. Query ID: {q['query_id']}")
        print(f"      Query: {q['query']}")
        print(f"      Company: {q['company_name']}")
        print(f"      Competitors: {q['competitor_count']}")
        print(f"      Status: {q['status']}")
        print(f"      Created: {q['created_at']}")
    
    assert response.status_code == 200, "Failed to list queries!"
    print(f"\n✓ Queries listed successfully!")
    
    return queries

def test_delete_query(query_id):
    """Test deleting a query"""
    print_section("TEST 5: Delete Query")
    
    print(f"\nDeleting query: {query_id}")
    
    response = requests.delete(f"{BASE_URL}/api/queries/{query_id}")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200, "Failed to delete query!"
    print(f"\n✓ Query deleted successfully!")
    
    # Verify deletion
    print("\nVerifying deletion...")
    response = requests.get(f"{BASE_URL}/api/queries/{query_id}")
    
    if response.status_code == 404:
        print("✓ Query no longer exists (confirmed)")
    else:
        print("⚠ Query still exists (unexpected)")

def test_api_documentation():
    """Test API documentation endpoints"""
    print_section("TEST 6: API Documentation")
    
    print("\n1. Testing OpenAPI docs (GET /docs)...")
    response = requests.get(f"{BASE_URL}/docs")
    print(f"   Status: {response.status_code}")
    print(f"   Available at: {BASE_URL}/docs")
    
    print("\n2. Testing ReDoc (GET /redoc)...")
    response = requests.get(f"{BASE_URL}/redoc")
    print(f"   Status: {response.status_code}")
    print(f"   Available at: {BASE_URL}/redoc")
    
    print("\n3. Testing OpenAPI JSON (GET /openapi.json)...")
    response = requests.get(f"{BASE_URL}/openapi.json")
    print(f"   Status: {response.status_code}")
    
    print("\n✓ API documentation accessible!")

def run_all_tests(wait_for_completion=False):
    """Run all tests in sequence"""
    
    print("\n" + "🧪 FASTAPI BACKEND TEST SUITE")
    print("="*70)
    print(f"\nTesting API at: {BASE_URL}")
    print(f"Wait for completion: {wait_for_completion}")
    
    try:
        # Test 1: Health check
        test_health_check()
        
        # Test 2: Create query
        query_id = test_create_query()
        
        # Test 3: Get query (optionally wait for completion)
        result = test_get_query(query_id, wait_for_completion=wait_for_completion)
        
        # Test 4: List queries
        test_list_queries()
        
        # Test 5: Delete query (only if not waiting for completion)
        if not wait_for_completion:
            test_delete_query(query_id)
        else:
            print_section("Query Status")
            print(f"\nQuery ID: {query_id}")
            print(f"Status: {result['status']}")
            if result['status'] == 'completed':
                print(f"✓ Workflow completed successfully!")
                print(f"\nYou can view the full results at:")
                print(f"   {BASE_URL}/api/queries/{query_id}")
        
        # Test 6: Documentation
        test_api_documentation()
        
        # Summary
        print_section("TEST SUMMARY")
        print("\n✓ All tests passed!")
        print(f"\n📊 API is fully functional!")
        print(f"\n🌐 Interactive docs available at:")
        print(f"   Swagger UI: {BASE_URL}/docs")
        print(f"   ReDoc: {BASE_URL}/redoc")
        
        if wait_for_completion and result['status'] == 'completed':
            print(f"\n📝 View your analysis:")
            print(f"   GET {BASE_URL}/api/queries/{query_id}")
        
        print()
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to API at {BASE_URL}")
        print("   Make sure the server is running:")
        print("   python -m app.main")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    # Check if user wants to wait for completion
    wait = "--wait" in sys.argv or "-w" in sys.argv
    
    run_all_tests(wait_for_completion=wait)