import json
import hashlib
import os
import feedparser
from datetime import datetime
from loguru import logger
from typing import List, Dict

from backend.common.schema import Article, ArticleStatus
from backend.modules.articles import articles_db

FEEDS_FILE = os.path.join(os.path.dirname(__file__), "feeds.json")

def load_feeds() -> List[Dict[str, str]]:
    """Loads RSS feed configurations from JSON file."""
    if not os.path.exists(FEEDS_FILE):
        logger.warning(f"Feeds file not found at {FEEDS_FILE}")
        return []
    try:
        with open(FEEDS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load feeds: {e}")
        return []

def generate_article_id(url: str) -> str:
    """Generates a deterministic ID based on the URL hash."""
    # Simple normalization: strip whitespace and trailing slash
    normalized_url = url.strip().rstrip("/")
    return hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()

def parse_date(entry) -> str:
    """Attempts to parse publication date from feed entry."""
    # feedparser standardizes dates to struct_time in 'published_parsed'
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        dt = datetime(*entry.published_parsed[:6])
        return dt.isoformat()
    return datetime.now().isoformat()

def process_feed(source_id: str, feed_url: str):
    """Fetches and processes a single RSS feed."""
    logger.info(f"Fetching feed: {source_id} ({feed_url})")
    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo:
             logger.warning(f"Feed {source_id} has parsing errors: {feed.bozo_exception}")

        new_count = 0
        for entry in feed.entries:
            url = entry.get("link")
            if not url:
                continue

            article_id = generate_article_id(url)
            
            # Create Article object
            article = Article(
                id=article_id,
                url=url,
                source_id=source_id,
                title=entry.get("title"),
                published_at=parse_date(entry),
                status=ArticleStatus.IDENTIFIED,
                identified_at=datetime.now().isoformat()
            )

            # Upsert to DB
            if articles_db.upsert_article(article):
                new_count += 1
                logger.debug(f" identified: {article.title}")
            
        logger.info(f"Feed {source_id}: {new_count} new articles identified.")

    except Exception as e:
        logger.error(f"Error processing feed {source_id}: {e}")

def run():
    """Main execution entry point."""
    feeds = load_feeds()
    if not feeds:
        logger.warning("No feeds configured.")
        return

    logger.info("Starting RSS fetcher run...")
    for feed in feeds:
        process_feed(feed["id"], feed["url"])
    logger.info("RSS fetcher run complete.")

if __name__ == "__main__":
    run()
