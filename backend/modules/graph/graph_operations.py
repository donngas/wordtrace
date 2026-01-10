from datetime import datetime
from modules.graph.neo4j_client import Neo4jClient

class GraphOperations:
    """
    Handles high-level graph operations (CRUD).
    Ensures data consistency between SQL DBs and Graph DB via shared IDs.
    """
    
    def __init__(self, client: Neo4jClient):
        self.client = client

    async def create_article(self, article_data: dict):
        """
        Create or update an Article node.
        
        Args:
            article_data: Dict containing:
                - id: UUID (from Article DB)
                - title: str
                - url: str
                - category: str
                - published_at: datetime
                - source: str
        """
        query = """
        MERGE (a:Article {id: $id})
        SET a.title = $title,
            a.url = $url,
            a.category = $category,
            a.published_at = $published_at,
            a.source = $source,
            a.updated_at = datetime()
        """
        await self.client.execute_query(query, article_data)

    async def create_keyword(self, keyword_data: dict):
        """
        Create or update a Keyword node.
        
        Args:
            keyword_data: Dict containing:
                - id: UUID (from Keyword DB)
                - canonical_name: str
                - keyword_type: str
                - category: str
        """
        query = """
        MERGE (k:Keyword {id: $id})
        SET k.canonical_name = $canonical_name,
            k.keyword_type = $keyword_type,
            k.category = $category
        """
        await self.client.execute_query(query, keyword_data)

    async def link_article_to_keywords(self, article_id: str, keyword_ids: list[str], scores: list[float] = None):
        """
        Create relationships between an Article and multiple Keywords.
        
        Args:
            article_id: UUID of the article
            keyword_ids: List of Keyword UUIDs
            scores: Optional list of relevance scores (0.0-1.0)
        """
        if not keyword_ids:
            return

        if scores is None:
            scores = [1.0] * len(keyword_ids)
            
        params = {
            "article_id": article_id,
            "relationships": [
                {"kid": kid, "score": score} 
                for kid, score in zip(keyword_ids, scores)
            ]
        }

        query = """
        MATCH (a:Article {id: $article_id})
        UNWIND $relationships as rel
        MATCH (k:Keyword {id: rel.kid})
        MERGE (a)-[r:HAS_KEYWORD]->(k)
        SET r.relevance_score = rel.score,
            r.created_at = datetime()
        """
        await self.client.execute_query(query, params)
