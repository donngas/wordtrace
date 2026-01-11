import sqlite3
import json
import os
from datetime import datetime
from typing import List, Optional
from loguru import logger

from common.schema import Article, ArticleStatus

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sqlite", "articles.db")

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the articles database table."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                url TEXT UNIQUE NOT NULL,
                source_id TEXT NOT NULL,
                title TEXT,
                published_at TEXT,
                full_text TEXT,
                keywords JSON,
                status TEXT NOT NULL,
                identified_at TEXT NOT NULL,
                retrieved_at TEXT
            )
        """)
        conn.commit()
        logger.info(f"Articles database initialized at {DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    finally:
        conn.close()

def upsert_article(article: Article) -> bool:
    """
    Insert or ignore an article.
    Since ID is a hash of URL, this makes it idempotent.
    Returns True if inserted, False if it already existed.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Check if exists first to return proper status
        cursor.execute("SELECT id FROM articles WHERE id = ?", (article.id,))
        if cursor.fetchone():
            return False

        keywords_json = json.dumps(article.keywords) if article.keywords else None

        cursor.execute("""
            INSERT INTO articles (
                id, url, source_id, title, published_at, full_text, 
                keywords, status, identified_at, retrieved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article.id,
            article.url,
            article.source_id,
            article.title,
            article.published_at,
            article.full_text,
            keywords_json,
            article.status.value,
            article.identified_at,
            article.retrieved_at
        ))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error upserting article {article.id}: {e}")
        raise
    finally:
        conn.close()

def get_article(article_id: str) -> Optional[Article]:
    """Retrieves an article by ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        if row:
            return _row_to_article(row)
        return None
    finally:
        conn.close()

def list_articles(status: Optional[ArticleStatus] = None, limit: int = 100) -> List[Article]:
    """Lists articles, optionally filtered by status."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if status:
            cursor.execute("SELECT * FROM articles WHERE status = ? LIMIT ?", (status.value, limit))
        else:
            cursor.execute("SELECT * FROM articles LIMIT ?", (limit,))
        
        rows = cursor.fetchall()
        return [_row_to_article(row) for row in rows]
    finally:
        conn.close()

def update_article_status(article_id: str, status: ArticleStatus, retrieved_at: Optional[str] = None):
    """Updates the status of an article."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if retrieved_at:
            cursor.execute("UPDATE articles SET status = ?, retrieved_at = ? WHERE id = ?", 
                           (status.value, retrieved_at, article_id))
        else:
            cursor.execute("UPDATE articles SET status = ? WHERE id = ?", (status.value, article_id))
        conn.commit()
    finally:
        conn.close()

def update_article_text(article_id: str, full_text: str):
    """Updates the full text of an article (after retrieval)."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE articles SET full_text = ? WHERE id = ?", (full_text, article_id))
        conn.commit()
    finally:
        conn.close()

def _row_to_article(row) -> Article:
    """Helper to convert DB row to Article object."""
    keywords = json.loads(row["keywords"]) if row["keywords"] else None
    return Article(
        id=row["id"],
        url=row["url"],
        source_id=row["source_id"],
        title=row["title"],
        published_at=row["published_at"],
        full_text=row["full_text"],
        keywords=keywords,
        status=ArticleStatus(row["status"]),
        identified_at=row["identified_at"],
        retrieved_at=row["retrieved_at"]
    )

if __name__ == "__main__":
    init_db()
