
"""
Centralized data models and schemas for WordTrace.
"""

from enum import Enum
from typing import Any
from pydantic import BaseModel


# --- From modules/llm/llm_client.py ---

class Message(BaseModel):
    """Chat message model."""
    role: str
    content: str


# --- From modules/llm/extractor.py ---

class EntityType(str, Enum):
    """Types of entity keywords."""
    PERSON = "person"
    PLACE = "place"
    ORGANIZATION = "organization"


class ConceptType(str, Enum):
    """Types of concept keywords."""
    GEOPOLITICS = "geopolitics"
    ECONOMIC_CRISIS = "economic_crisis"
    INNOVATION = "innovation"


class ArticleCategory(str, Enum):
    """Article categories."""
    POLITICS = "politics"
    BUSINESS = "business"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    TECHNOLOGY = "technology"
    HEALTH_SCIENCE = "health_science"
    WORLD = "world"


class ExtractedKeyword(BaseModel):
    """A keyword extracted from article text."""
    name: str
    canonical_name: str
    keyword_type: str  # "entity" or "concept"
    category: str  # EntityType or ConceptType value


class ExtractionResult(BaseModel):
    """Result of keyword extraction and categorization."""
    article_category: ArticleCategory
    keywords: list[ExtractedKeyword]


# --- From modules/keywords/keywords_db.py ---

class StoredKeyword(BaseModel):
    """A keyword stored in the database."""
    id: str
    canonical_name: str
    keyword_type: str  # "entity" or "concept"
    category: str
    embedding: list[float]
    aliases: list[str]


# --- From modules/keywords/deduplicator.py ---

class DeduplicationResult(BaseModel):
    """Result of keyword deduplication."""
    keyword: StoredKeyword
    is_new: bool
    matched_similarity: float | None = None


# --- From app/routers/keywords.py ---

class ExtractRequest(BaseModel):
    """Request body for keyword extraction."""
    title: str
    content: str


class ExtractResponse(BaseModel):
    """Response for keyword extraction."""
    article_category: str
    keywords: list[dict]
