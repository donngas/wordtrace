import time
from datetime import datetime
from loguru import logger
from newspaper import Article as NewspaperArticle
from newspaper import Config
from common.schema import ArticleStatus
from modules.articles import articles_db

# User agent to avoid 403s on some sites
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def fetch_pending_articles(limit: int = 20):
    """
    Fetches articles with IDENTIFIED status and retrieves their content.
    """
    articles = articles_db.list_articles(status=ArticleStatus.IDENTIFIED, limit=limit)
    if not articles:
        logger.info("No pending articles to retrieve.")
        return

    logger.info(f"Found {len(articles)} pending articles. Starting retrieval...")

    config = Config()
    config.browser_user_agent = USER_AGENT
    config.request_timeout = 10

    success_count = 0
    
    for article in articles:
        try:
            logger.debug(f"Retrieving: {article.url}")
            
            # download() and parse()
            # We use the explicitly created Article object from newspaper4k
            paper = NewspaperArticle(article.url, config=config)
            paper.download()
            paper.parse()
            
            full_text = paper.text
            
            if not full_text:
                logger.warning(f"No text extracted for {article.url}")
                # Optional: Mark as failed or try again later? 
                # For now, we'll keep it as IDENTIFIED but maybe we need a FAILED status later.
                # Or just update it with empty text and let the next stage handle it.
                continue

            # Update DB
            articles_db.update_article_text(article.id, full_text)
            articles_db.update_article_status(
                article.id, 
                ArticleStatus.RETRIEVED, 
                retrieved_at=datetime.now().isoformat()
            )
            success_count += 1
            
            # Be polite to servers
            time.sleep(1) 

        except Exception as e:
            logger.error(f"Failed to retrieve {article.url}: {e}")
            # Identify if it's a 404 or permanent error to mark as DELETED?
            # For now, just skip.

    logger.info(f"Retrieval run complete. Successfully retrieved {success_count}/{len(articles)} articles.")

def run():
    """Main execution entry point."""
    fetch_pending_articles()

if __name__ == "__main__":
    run()
