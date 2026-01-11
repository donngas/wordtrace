"""
Centralized data models and schemas for WordTrace.

Groups:
1. Enums & Constants
2. LLM Utilities
3. Core Domain Models (Database)
4. Pipeline & Analysis Models (Transient)
5. API Schemas
"""

from enum import Enum
from typing import Any
from pydantic import BaseModel


# ==========================================
# 1. Enums & Constants
# ==========================================

class ArticleStatus(str, Enum):
    """
    Lifecycle states for an article in the acquisition pipeline.
    
    Used primarily in `modules/articles/articles_db.py` to track progress.
    Flow: IDENTIFIED -> RETRIEVED -> ANALYSED -> COMPLETE (or DELETED).
    """
    IDENTIFIED = "IDENTIFIED"   # Found in RSS, metadata only
    RETRIEVED = "RETRIEVED"     # Full text fetched by paperboy
    ANALYSED = "ANALYSED"       # Keywords extracted by orchestrator/LLM
    COMPLETE = "COMPLETE"       # Ready for usage/graph
    DELETED = "DELETED"         # Discarded or irrelevant


class ArticleCategory(str, Enum):
    """
    High-level topic categories for articles.
    
    Used in `modules/llm/extractor.py` as part of the `ExtractionResult` from the LLM.
    """
    POLITICS = "politics"
    BUSINESS = "business"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    TECHNOLOGY = "technology"
    HEALTH_SCIENCE = "health_science"
    WORLD = "world"


class EntityType(str, Enum):
    """
    Classifications for specific named entities.
    
    Used in `modules/llm/extractor.py` to classify extracted entities and
    in `modules/keywords/keywords_db.py` for stored entity types.
    """
    PERSON = "person"
    PLACE = "place"
    ORGANIZATION = "organization"


class ConceptType(str, Enum):
    """
    Classifications for abstract concepts or themes.
    
    Used in `modules/llm/extractor.py` to classify extracted concepts and
    in `modules/keywords/keywords_db.py` for stored concept types.
    """
    GEOPOLITICS = "geopolitics"
    ECONOMIC_CRISIS = "economic_crisis"
    INNOVATION = "innovation"


# ==========================================
# 2. LLM Utilities
# ==========================================

class Message(BaseModel):
    """
    Represents a single message in an LLM chat conversation.
    
    Used in `modules/llm/llm_client.py` to construct prompts and history for OpenRouter.
    """
    role: str
    content: str


# ==========================================
# 3. Core Domain Models (Database)
# ==========================================

class Article(BaseModel):
    """
    Primary data model for an article in the SQLite database.
    
    Used in `modules/articles/articles_db.py` as the DTO for inserting and retrieving articles.
    Stores metadata, content, and current pipeline status.
    """
    id: str                    # Unique Hash of the URL
    url: str
    source_id: str             # ID of the RSS source/feed
    title: str | None = None
    published_at: str | None = None  # ISO 8601 datetime string
    full_text: str | None = None
    keywords: list[dict] | None = None  # JSON serialization of associated keywords
    status: ArticleStatus
    identified_at: str         # ISO 8601 datetime
    retrieved_at: str | None = None


class StoredKeyword(BaseModel):
    """
    A canonical keyword entity persisted in the Keyword Database.
    
    Used in `modules/keywords/keywords_db.py` as the DTO for stored keywords.
    Includes embedding vector for similarity search and deduplication.
    """
    id: str
    canonical_name: str
    keyword_type: str          # "entity" or "concept"
    category: str              # EntityType or ConceptType value
    embedding: list[float]
    aliases: list[str]         # List of varied surface forms extracted from text


# ==========================================
# 4. Pipeline & Analysis Models (Transient)
# ==========================================

class ExtractedKeyword(BaseModel):
    """
    A raw keyword candidate extracted from text by the LLM.
    
    Used in `modules/llm/extractor.py` to represent individual items found in text.
    These are transient objects processed by the Deduplicator to become StoredKeywords.
    """
    name: str                  # The exact text as it appeared
    canonical_name: str        # Normalized form suggested by LLM
    keyword_type: str          # "entity" or "concept"
    category: str              # EntityType or ConceptType value


class ExtractionResult(BaseModel):
    """
    Structured output from the LLM analysis of an article.
    
    Returned by `modules/llm/extractor.py`.
    Contains the high-level category and list of extracted keyword candidates.
    """
    article_category: ArticleCategory
    keywords: list[ExtractedKeyword]


class DeduplicationResult(BaseModel):
    """
    Outcome of matching an ExtractedKeyword against StoredKeywords.
    
    Used by `modules/keywords/deduplicator.py` (and orchestrator) to decide
    whether to create new StoredKeywords or alias existing ones.
    """
    keyword: StoredKeyword
    is_new: bool
    matched_similarity: float | None = None


# ==========================================
# 5. API Schemas
# ==========================================

class ExtractRequest(BaseModel):
    """
    Input schema for the manual keyword extraction API endpoint.
    
    Used in `app/routers/keywords.py` (implied).
    """
    title: str
    content: str


class ExtractResponse(BaseModel):
    """
    Output schema for the manual keyword extraction API endpoint.
    
    Used in `app/routers/keywords.py` (implied).
    """
    article_category: str
    keywords: list[dict]
