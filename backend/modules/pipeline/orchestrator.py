import asyncio
import os
import json
from loguru import logger
from datetime import datetime
from dotenv import load_dotenv

# Pipeline components
from modules.articles import rss_fetcher, paperboy, articles_db
from modules.llm.llm_client import OpenRouterClient
from modules.llm.embeddings import EmbeddingsClient
from modules.llm.extractor import extract_from_article
from modules.keywords.deduplicator import process_article_keywords
from modules.keywords.keywords_db import KeywordsDatabase
from common.schema import ArticleStatus, Article

# Load env for API keys
load_dotenv()

async def process_retrieved_articles(limit: int = 10):
    """
    Process RETRIEVED articles:
    1. Extract keywords/categories using LLM
    2. Deduplicate and store keywords
    3. Update Article status to ANALYSED
    """
    # Initialize clients
    try:
        llm_client = OpenRouterClient()
        embeddings_client = EmbeddingsClient()
        keywords_db = KeywordsDatabase()
    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}")
        return

    articles = articles_db.list_articles(status=ArticleStatus.RETRIEVED, limit=limit)
    if not articles:
        logger.info("No retrieved articles to process.")
        return

    logger.info(f"Processing {len(articles)} retrieved articles...")

    for article in articles:
        logger.info(f"Analyzing: {article.title}")
        try:
            # 1. Extraction
            extraction_result = await extract_from_article(
                client=llm_client,
                title=article.title or "",
                content=article.full_text or ""
            )
            
            # 2. Deduplication & Storage
            if extraction_result.keywords:
                dedup_results = await process_article_keywords(
                    embeddings_client=embeddings_client,
                    keywords_db=keywords_db,
                    keywords=extraction_result.keywords
                )
                logger.debug(f"  - Extracted {len(extraction_result.keywords)} keywords, {len([r for r in dedup_results if r.is_new])} new.")
            
            # 3. Update Status & Backup Keywords
            article_keywords_json = [k.model_dump() for k in extraction_result.keywords]
            article.keywords = article_keywords_json
            article.status = ArticleStatus.ANALYSED
            
            # TODO: Add dedicated metadata update method to articles_db 
            conn = articles_db.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE articles 
                SET status = ?, keywords = ? 
                WHERE id = ?
            """, (
                ArticleStatus.ANALYSED.value, 
                json.dumps(article_keywords_json),
                article.id
            ))
            conn.commit()
            conn.close()
            
            logger.info(f"  - Marked as ANALYSED")

        except Exception as e:
            logger.error(f"Error processing article {article.id}: {e}")
            # TODO: Implement error status or retry logic
            continue

async def run_pipeline():
    """
    Main orchestrator function.
    Runs the full pipeline: Acquisition -> Retrieval -> Analysis.
    """
    logger.info("=== Starting Pipeline Run ===")
    
    # 1. Acquisition (RSS)
    logger.info("--- Stage 1: RSS Acquisition ---")
    rss_fetcher.run()
    
    # 2. Retrieval (Paperboy)
    logger.info("--- Stage 2: Content Retrieval ---")
    paperboy.run()
    
    # 3. Analysis (Extraction + Deduplication)
    logger.info("--- Stage 3: Content Analysis ---")
    await process_retrieved_articles()
    
    logger.info("=== Pipeline Run Complete ===")

if __name__ == "__main__":
    # Async entry point
    asyncio.run(run_pipeline())
