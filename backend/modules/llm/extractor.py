"""
Keyword and article category extraction using LLM.

Extracts entities (People, Places, Organizations) and concepts (Geopolitics, 
Economic Crisis, Innovation) from article text, along with article categorization.
"""

import json
from pydantic import BaseModel
from enum import Enum

from modules.llm.llm_client import OpenRouterClient, create_messages


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


EXTRACTION_SYSTEM_PROMPT = """You are a news article analyzer. Your task is to:

1. Categorize the article into ONE of these categories:
   - politics
   - business
   - sports
   - entertainment
   - technology
   - health_science
   - world

2. Extract keywords from the article. Keywords should be:
   
   ENTITIES (specific named things):
   - person: Named individuals (e.g., "Donald Trump", "Elon Musk")
   - place: Geographic locations (e.g., "Washington D.C.", "European Union")
   - organization: Companies, governments, institutions (e.g., "Tesla", "United Nations")
   
   CONCEPTS (abstract themes):
   - geopolitics: International relations, diplomacy, conflicts
   - economic_crisis: Financial downturns, recessions, market crashes
   - innovation: New technologies, breakthroughs, inventions

For each keyword, provide:
- name: The exact name as it appears in the article
- canonical_name: The standardized/most common form (e.g., "President Trump" → "Donald Trump")
- keyword_type: Either "entity" or "concept"
- category: The specific category from above

Extract 5-15 keywords per article. Focus on the most significant and relevant ones.

Respond with valid JSON only."""

EXTRACTION_USER_TEMPLATE = """Analyze this article:

Title: {title}

Content:
{content}

Respond with JSON in this exact format:
{{
  "article_category": "<category>",
  "keywords": [
    {{
      "name": "<exact name from article>",
      "canonical_name": "<standardized name>",
      "keyword_type": "<entity or concept>",
      "category": "<specific category>"
    }}
  ]
}}"""


class KeywordExtractor:
    """Extracts keywords and categories from articles using LLM."""
    
    def __init__(self, client: OpenRouterClient):
        """
        Initialize the extractor.
        
        Args:
            client: OpenRouter client for LLM calls
        """
        self.client = client
    
    async def extract(self, title: str, content: str) -> ExtractionResult:
        """
        Extract keywords and category from an article.
        
        Args:
            title: Article title
            content: Article content/body
            
        Returns:
            ExtractionResult with category and keywords
        """
        user_message = EXTRACTION_USER_TEMPLATE.format(
            title=title,
            content=content[:8000],  # Limit content length
        )
        
        messages = create_messages(
            system=EXTRACTION_SYSTEM_PROMPT,
            user=user_message,
        )
        
        # Request JSON response format
        response_format = {
            "type": "json_object",
        }
        
        response_text = await self.client.get_completion_text(
            messages=messages,
            response_format=response_format,
            temperature=0.3,  # Lower temperature for consistency
        )
        
        # Parse the JSON response
        data = json.loads(response_text)
        
        # Validate and create result
        keywords = [
            ExtractedKeyword(
                name=kw["name"],
                canonical_name=kw["canonical_name"],
                keyword_type=kw["keyword_type"],
                category=kw["category"],
            )
            for kw in data["keywords"]
        ]
        
        return ExtractionResult(
            article_category=ArticleCategory(data["article_category"]),
            keywords=keywords,
        )


async def extract_from_article(
    client: OpenRouterClient,
    title: str,
    content: str,
) -> ExtractionResult:
    """
    Convenience function to extract keywords from an article.
    
    Args:
        client: OpenRouter client
        title: Article title
        content: Article content
        
    Returns:
        ExtractionResult with category and keywords
    """
    extractor = KeywordExtractor(client)
    return await extractor.extract(title, content)
