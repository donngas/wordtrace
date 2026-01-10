import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from neo4j import AsyncGraphDatabase, AsyncDriver

class Neo4jClient:
    """
    Async client for Neo4j database interactions.
    Handles connection lifecycle and query execution.
    """
    
    def __init__(self):
        self._driver: AsyncDriver | None = None
        self._uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self._user = os.getenv("NEO4J_USER", "neo4j")
        self._password = os.getenv("NEO4J_PASSWORD", "password")

    async def connect(self):
        """Establish connection to Neo4j."""
        if not self._driver:
            self._driver = AsyncGraphDatabase.driver(
                self._uri, 
                auth=(self._user, self._password)
            )

    async def close(self):
        """Close the connection."""
        if self._driver:
            await self._driver.close()
            self._driver = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[Any, None]:
        """
        Provide a transactional session context.
        
        Usage:
            async with client.session() as session:
                result = await session.run(...)
        """
        if not self._driver:
            await self.connect()
            
        async with self._driver.session() as session:
            yield session

    async def execute_query(self, query: str, parameters: dict = None) -> Any:
        """
        Execute a single query in a dedicated session.
        Useful for one-off operations.
        """
        if parameters is None:
            parameters = {}
            
        async with self.session() as session:
            result = await session.run(query, parameters)
            return await result.data()
