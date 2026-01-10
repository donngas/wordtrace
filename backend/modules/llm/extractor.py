"""
Keyword and article category extraction using LLM.

Extracts entities (People, Places, Organizations) and concepts (Geopolitics, 
Economic Crisis, Innovation) from article text, along with article categorization.
"""

import json
from enum import Enum

from modules.llm.llm_client import OpenRouterClient, create_messages
from common.schema import (
    ArticleCategory,
    ExtractedKeyword,
    ExtractionResult,
    EntityType, 
    ConceptType
)
from common.prompts import (
    get_extraction_system_prompt,
    get_extraction_user_prompt
)


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
        user_message = get_extraction_user_prompt(
            title=title,
            content=content[:8000],  # Limit content length
        )
        
        messages = create_messages(
            system=get_extraction_system_prompt(),
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
