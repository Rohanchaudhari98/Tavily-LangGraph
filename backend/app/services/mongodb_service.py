"""
MongoDB Service - Handles all database operations.

Uses async PyMongo driver to store and retrieve:
- User queries
- Agent outputs
- Analysis results
- Workflow metadata
"""

from pymongo import AsyncMongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MongoDBService:
    """
    Async MongoDB service for storing competitive intelligence data.
    
    Collections:
    - queries: Stores all user queries and their results
    """
    
    def __init__(self, connection_string: str, database_name: str = "competitive_intelligence"):
        """
        Initialize MongoDB connection.
        
        Args:
            connection_string: MongoDB connection URI (from MongoDB Atlas)
            database_name: Name of the database to use
        """
        self.connection_string = connection_string
        self.database_name = database_name
        
        # Create async MongoDB client
        self.client = AsyncMongoClient(connection_string)
        self.db = self.client[database_name]
        
        # Collections
        self.queries = self.db["queries"]
        
        logger.info(f"MongoDB service initialized for database: {database_name}")
    
    async def ping(self) -> bool:
        """
        Check if MongoDB connection is alive.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            await self.client.admin.command('ping')
            return True
        except ConnectionFailure:
            return False
    
    def generate_id(self) -> str:
        """
        Generate a unique ID for a query.
        
        Returns:
            String representation of MongoDB ObjectId
        """
        return str(ObjectId())
    
    async def insert_query(self, query_doc: Dict) -> str:
        """
        Insert a new query document.
        
        Args:
            query_doc: Dictionary with query data
            
        Returns:
            The inserted document's ID
        """
        result = await self.queries.insert_one(query_doc)
        logger.info(f"Inserted query with ID: {result.inserted_id}")
        return str(result.inserted_id)
    
    async def get_query(self, query_id: str) -> Optional[Dict]:
        """
        Get a query by ID.
        
        Args:
            query_id: The query's unique ID
            
        Returns:
            Query document or None if not found
        """
        query = await self.queries.find_one({"_id": query_id})
        
        if query:
            logger.info(f"Found query: {query_id}")
        else:
            logger.warning(f"Query not found: {query_id}")
        
        return query
    
    async def update_query(self, query_id: str, update_data: Dict) -> bool:
        """
        Update a query with new data.
        
        Args:
            query_id: The query's unique ID
            update_data: Dictionary of fields to update
            
        Returns:
            True if updated, False if not found
        """
        result = await self.queries.update_one(
            {"_id": query_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated query: {query_id}")
            return True
        else:
            logger.warning(f"Query not modified: {query_id}")
            return False
    
    async def list_queries(
        self, 
        skip: int = 0, 
        limit: int = 20,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        List queries with pagination and optional filtering.
        
        Args:
            skip: Number of documents to skip (for pagination)
            limit: Maximum number of documents to return
            status: Optional status filter ("processing", "completed", "failed")
            
        Returns:
            List of query documents
        """
        # Build filter
        filter_dict = {}
        if status:
            filter_dict["status"] = status
        
        # Query with pagination
        cursor = self.queries.find(filter_dict).sort("created_at", -1).skip(skip).limit(limit)
        queries = await cursor.to_list(length=limit)
        
        logger.info(f"Listed {len(queries)} queries (skip={skip}, limit={limit})")
        
        return queries
    
    async def delete_query(self, query_id: str) -> bool:
        """
        Delete a query and its results.
        
        Args:
            query_id: The query's unique ID
            
        Returns:
            True if deleted, False if not found
        """
        result = await self.queries.delete_one({"_id": query_id})
        
        if result.deleted_count > 0:
            logger.info(f"Deleted query: {query_id}")
            return True
        else:
            logger.warning(f"Query not found for deletion: {query_id}")
            return False
    
    async def count_queries(self, status: Optional[str] = None) -> int:
        """
        Count total number of queries.
        
        Args:
            status: Optional status filter
            
        Returns:
            Number of queries
        """
        filter_dict = {}
        if status:
            filter_dict["status"] = status
        
        count = await self.queries.count_documents(filter_dict)
        return count
    
    async def get_recent_queries(self, limit: int = 5) -> List[Dict]:
        """
        Get the most recent queries.
        
        Args:
            limit: Number of queries to return
            
        Returns:
            List of recent query documents
        """
        cursor = self.queries.find().sort("created_at", -1).limit(limit)
        queries = await cursor.to_list(length=limit)
        
        logger.info(f"Retrieved {len(queries)} recent queries")
        
        return queries
    
    async def create_indexes(self):
        """
        Create database indexes for better query performance.
        
        Call this once when setting up the database.
        """
        # Index on created_at for sorting
        await self.queries.create_index([("created_at", -1)])
        
        # Index on status for filtering
        await self.queries.create_index("status")
        
        # Index on company_name for searching
        await self.queries.create_index("company_name")
        
        logger.info("Database indexes created")
    
    async def close(self):
        """
        Close the MongoDB connection.
        
        Call this when shutting down the application.
        """
        await self.client.close()
        logger.info("MongoDB connection closed")
    
    def __repr__(self):
        return f"MongoDBService(database={self.database_name})"