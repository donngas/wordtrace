import asyncio
import uuid
from datetime import datetime
from loguru import logger

from modules.graph.neo4j_client import Neo4jClient
from modules.graph.schema_manager import initialize_schema
from modules.graph.graph_operations import GraphOperations

async def test_graph_module():
    logger.info("Testing Graph Module...")
    
    # 1. Connect
    client = Neo4jClient()
    try:
        await client.connect()
        logger.info("Connection successful")
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return

    # 2. Schema
    try:
        await initialize_schema(client)
        logger.info("Schema initialized (Constraints/Indexes)")
    except Exception as e:
        logger.error(f"Schema initialization failed: {e}")

    # 3. Operations
    ops = GraphOperations(client)
    
    # Create Dummy Data
    article_id = str(uuid.uuid4())
    keyword_id = str(uuid.uuid4())
    
    article_data = {
        "id": article_id,
        "title": "Test Article",
        "url": "http://example.com/test",
        "category": "Technology",
        "published_at": datetime.now(),
        "source": "TechCrunch"
    }
    
    keyword_data = {
        "id": keyword_id,
        "canonical_name": "Artificial Intelligence",
        "keyword_type": "concept",
        "category": "Innovation"
    }
    
    try:
        logger.info(f"Creating Article: {article_id}")
        await ops.create_article(article_data)
        
        logger.info(f"Creating Keyword: {keyword_id}")
        await ops.create_keyword(keyword_data)
        
        logger.info("Linking Article -> Keyword")
        await ops.link_article_to_keywords(article_id, [keyword_id], [0.95])
        
        # Verify Verification
        query = """
        MATCH (a:Article {id: $aid})-[r:HAS_KEYWORD]->(k:Keyword {id: $kid})
        RETURN a.title, k.canonical_name, r.relevance_score
        """
        result = await client.execute_query(query, {"aid": article_id, "kid": keyword_id})
        
        if result and result[0]['a.title'] == "Test Article":
            logger.info("Verification Query Passed: Data persisted correctly")
        else:
            logger.error(f"Verification Query Failed: {result}")
            
    except Exception as e:
        logger.exception(f"Operations failed: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_graph_module())
