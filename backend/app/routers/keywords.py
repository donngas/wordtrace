"""
Keywords API Router.

Endpoints for keyword extraction and testing.
"""

import os
from fastapi import APIRouter, HTTPException
from common.schema import ExtractRequest, ExtractResponse

from modules.llm.llm_client import OpenRouterClient
from modules.llm.extractor import KeywordExtractor, ExtractionResult


router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.post("/extract", response_model=ExtractResponse)
async def extract_keywords(request: ExtractRequest) -> ExtractResponse:
    """
    Extract keywords and category from article text.
    
    This endpoint is for testing the extraction functionality.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENROUTER_API_KEY not configured",
        )
    
    client = OpenRouterClient(api_key=api_key)
    
    try:
        extractor = KeywordExtractor(client)
        result = await extractor.extract(
            title=request.title,
            content=request.content,
        )
        
        return ExtractResponse(
            article_category=result.article_category.value,
            keywords=[
                {
                    "name": kw.name,
                    "canonical_name": kw.canonical_name,
                    "keyword_type": kw.keyword_type,
                    "category": kw.category,
                }
                for kw in result.keywords
            ],
        )
    finally:
        await client.close()
