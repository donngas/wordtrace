from modules.graph.neo4j_client import Neo4jClient

async def initialize_schema(client: Neo4jClient):
    """
    Initialize the graph database schema.
    Creates necessary constraints and indexes for performance and data integrity.
    """
    
    # 1. Enforce Uniqueness
    # We use the external UUIDs (from SQLite/Articles DB) as the source of truth.
    await client.execute_query(
        "CREATE CONSTRAINT article_id_unique IF NOT EXISTS FOR (a:Article) REQUIRE a.id IS UNIQUE"
    )
    await client.execute_query(
        "CREATE CONSTRAINT keyword_id_unique IF NOT EXISTS FOR (k:Keyword) REQUIRE k.id IS UNIQUE"
    )

    # 2. Performance Indexes
    # Single property indexes
    await client.execute_query(
        "CREATE INDEX article_published_at IF NOT EXISTS FOR (a:Article) ON (a.published_at)"
    )
    await client.execute_query(
        "CREATE INDEX article_category IF NOT EXISTS FOR (a:Article) ON (a.category)"
    )
    
    # Compound index for filtered queries (Project optimization)
    # Finds articles by date AND category instantly
    await client.execute_query(
        "CREATE INDEX article_filter_compound IF NOT EXISTS FOR (a:Article) ON (a.published_at, a.category)"
    )

    # Keyword lookup index
    await client.execute_query(
        "CREATE INDEX keyword_canonical_name IF NOT EXISTS FOR (k:Keyword) ON (k.canonical_name)"
    )
