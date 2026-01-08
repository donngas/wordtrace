"""
SQLite database for keyword storage and deduplication.

Stores canonical keywords with their embeddings for similarity-based matching.
"""

import sqlite3
import json
import uuid
from pathlib import Path
from contextlib import contextmanager
from pydantic import BaseModel


class StoredKeyword(BaseModel):
    """A keyword stored in the database."""
    id: str
    canonical_name: str
    keyword_type: str  # "entity" or "concept"
    category: str
    embedding: list[float]
    aliases: list[str]


class KeywordsDatabase:
    """SQLite-based keyword storage with embedding support."""
    
    def __init__(self, db_path: str | Path = "keywords.db"):
        """
        Initialize the keywords database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize the database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS keywords (
                    id TEXT PRIMARY KEY,
                    canonical_name TEXT NOT NULL UNIQUE,
                    keyword_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    aliases TEXT NOT NULL DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index for faster lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_keywords_type_category 
                ON keywords(keyword_type, category)
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection with context management."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def add_keyword(
        self,
        canonical_name: str,
        keyword_type: str,
        category: str,
        embedding: list[float],
        aliases: list[str] | None = None,
    ) -> StoredKeyword:
        """
        Add a new keyword to the database.
        
        Args:
            canonical_name: Standardized keyword name
            keyword_type: "entity" or "concept"
            category: Specific category (person, place, etc.)
            embedding: Embedding vector
            aliases: Alternative names for this keyword
            
        Returns:
            The created StoredKeyword
        """
        keyword_id = str(uuid.uuid4())
        aliases = aliases or []
        
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO keywords (id, canonical_name, keyword_type, category, embedding, aliases)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    keyword_id,
                    canonical_name,
                    keyword_type,
                    category,
                    json.dumps(embedding),
                    json.dumps(aliases),
                ),
            )
            conn.commit()
        
        return StoredKeyword(
            id=keyword_id,
            canonical_name=canonical_name,
            keyword_type=keyword_type,
            category=category,
            embedding=embedding,
            aliases=aliases,
        )
    
    def get_keyword_by_id(self, keyword_id: str) -> StoredKeyword | None:
        """Get a keyword by its ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM keywords WHERE id = ?",
                (keyword_id,),
            ).fetchone()
            
            if row is None:
                return None
            
            return self._row_to_keyword(row)
    
    def get_keyword_by_name(self, canonical_name: str) -> StoredKeyword | None:
        """Get a keyword by its canonical name."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM keywords WHERE canonical_name = ?",
                (canonical_name,),
            ).fetchone()
            
            if row is None:
                return None
            
            return self._row_to_keyword(row)
    
    def get_all_keywords(self) -> list[StoredKeyword]:
        """Get all keywords from the database."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM keywords").fetchall()
            return [self._row_to_keyword(row) for row in rows]
    
    def get_all_embeddings(self) -> list[tuple[str, list[float]]]:
        """
        Get all keyword IDs and embeddings for similarity matching.
        
        Returns:
            List of (id, embedding) tuples
        """
        with self._get_connection() as conn:
            rows = conn.execute("SELECT id, embedding FROM keywords").fetchall()
            return [(row["id"], json.loads(row["embedding"])) for row in rows]
    
    def add_alias(self, keyword_id: str, alias: str) -> None:
        """
        Add an alias to an existing keyword.
        
        Args:
            keyword_id: ID of the keyword
            alias: New alias to add
        """
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT aliases FROM keywords WHERE id = ?",
                (keyword_id,),
            ).fetchone()
            
            if row is None:
                raise ValueError(f"Keyword not found: {keyword_id}")
            
            aliases = json.loads(row["aliases"])
            if alias not in aliases:
                aliases.append(alias)
                conn.execute(
                    "UPDATE keywords SET aliases = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (json.dumps(aliases), keyword_id),
                )
                conn.commit()
    
    def _row_to_keyword(self, row: sqlite3.Row) -> StoredKeyword:
        """Convert a database row to a StoredKeyword."""
        return StoredKeyword(
            id=row["id"],
            canonical_name=row["canonical_name"],
            keyword_type=row["keyword_type"],
            category=row["category"],
            embedding=json.loads(row["embedding"]),
            aliases=json.loads(row["aliases"]),
        )
    
    def count(self) -> int:
        """Get the total number of keywords."""
        with self._get_connection() as conn:
            result = conn.execute("SELECT COUNT(*) FROM keywords").fetchone()
            return result[0]
