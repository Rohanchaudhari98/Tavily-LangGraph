"""
Test MongoDB service connection and basic operations.
"""

import asyncio
from app.services.mongodb_service import MongoDBService
from app.config import settings
from datetime import datetime


async def test_mongodb():
    """Test basic MongoDB operations"""
    
    print("\nTesting MongoDB Service...")
    print("="*70)
    
    # Show connection details (masked password)
    masked_uri = settings.mongodb_uri.replace(settings.mongodb_uri.split('@')[0].split('://')[1], "***:***")
    print(f"\nConnection String: {masked_uri}")
    print(f"Database Name: {settings.mongodb_db_name}")
    
    # Initialize service
    print("\nInitializing MongoDB service...")
    try:
        db = MongoDBService(
            connection_string=settings.mongodb_uri,
            database_name=settings.mongodb_db_name
        )
        print("Service initialized")
    except Exception as e:
        print(f"Failed to initialize service: {e}")
        return
    
    # Test 1: Ping
    print("\n1. Testing connection...")
    try:
        is_connected = await db.ping()
        print(f"   Connected: {is_connected}")
        
        if not is_connected:
            print("\n   Connection failed!")
            print("   Troubleshooting steps:")
            print("   1. Check MongoDB Atlas Network Access (whitelist your IP)")
            print("   2. Verify database user credentials")
            print("   3. Ensure connection string format is correct")
            return
    except Exception as e:
        print(f"   Connection error: {e}")
        print("\n   Troubleshooting steps:")
        print("   1. Check if MongoDB Atlas cluster is running")
        print("   2. Verify network access settings")
        print("   3. Check if password contains special characters (may need URL encoding)")
        return
    
    # Test 2: Create indexes
    print("\n2. Creating indexes...")
    try:
        await db.create_indexes()
        print("   Indexes created")
    except Exception as e:
        print(f"   Error creating indexes: {e}")
    
    # Test 3: Insert a test query
    print("\n3. Inserting test query...")
    query_id = db.generate_id()
    test_query = {
        "_id": query_id,
        "query": "test pricing",
        "company_name": "TestCorp",
        "competitors": ["Competitor A", "Competitor B"],
        "status": "processing",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    try:
        await db.insert_query(test_query)
        print(f"   Inserted query with ID: {query_id}")
    except Exception as e:
        print(f"   Error inserting query: {e}")
        return
    
    # Test 4: Retrieve the query
    print("\n4. Retrieving query...")
    try:
        retrieved = await db.get_query(query_id)
        print(f"   Retrieved: {retrieved['query']} for {retrieved['company_name']}")
    except Exception as e:
        print(f"   Error retrieving query: {e}")
    
    # Test 5: Update the query
    print("\n5. Updating query status...")
    try:
        await db.update_query(
            query_id,
            {"status": "completed", "updated_at": datetime.now()}
        )
        print("   Status updated to 'completed'")
    except Exception as e:
        print(f"   Error updating query: {e}")
    
    # Test 6: List queries
    print("\n6. Listing all queries...")
    try:
        queries = await db.list_queries(limit=10)
        print(f"   Found {len(queries)} queries")
        for q in queries:
            print(f"     - {q['_id']}: {q['query']} ({q['status']})")
    except Exception as e:
        print(f"   Error listing queries: {e}")
    
    # Test 7: Count queries
    print("\n7. Counting queries...")
    try:
        total = await db.count_queries()
        completed = await db.count_queries(status="completed")
        print(f"   Total: {total}, Completed: {completed}")
    except Exception as e:
        print(f"   Error counting queries: {e}")
    
    # Test 8: Delete test query
    print("\n8. Deleting test query...")
    try:
        deleted = await db.delete_query(query_id)
        print(f"   Deleted: {deleted}")
    except Exception as e:
        print(f"   Error deleting query: {e}")
    
    # Close connection
    await db.close()
    
    print("\n" + "="*70)
    print("All tests passed!")
    print()


if __name__ == "__main__":
    asyncio.run(test_mongodb())