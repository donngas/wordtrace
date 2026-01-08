"""
Keyword deduplication pipeline.

Matches extracted keywords against existing ones using embedding similarity,
and handles canonicalization of new keywords.
"""

from pydantic import BaseModel

from modules.llm.embeddings import EmbeddingsClient, find_most_similar
from modules.llm.extractor import ExtractedKeyword
from modules.keywords.keywords_db import KeywordsDatabase, StoredKeyword


class DeduplicationResult(BaseModel):
    """Result of keyword deduplication."""
    keyword: StoredKeyword
    is_new: bool
    matched_similarity: float | None = None


class KeywordDeduplicator:
    """
    Deduplicates keywords using embedding similarity.
    
    When a new keyword is extracted:
    1. Generate embedding using Gemini API
    2. Compare against all existing keyword embeddings
    3. If similarity > threshold: link to existing keyword as alias
    4. If no match: create new keyword
    """
    
    def __init__(
        self,
        embeddings_client: EmbeddingsClient,
        keywords_db: KeywordsDatabase,
        similarity_threshold: float = 0.85,
    ):
        """
        Initialize the deduplicator.
        
        Args:
            embeddings_client: Gemini embeddings client
            keywords_db: Keywords database
            similarity_threshold: Minimum similarity to consider a match (0-1)
        """
        self.embeddings = embeddings_client
        self.db = keywords_db
        self.threshold = similarity_threshold
        
        # Cache embeddings in memory for faster matching
        self._embeddings_cache: list[tuple[str, list[float]]] | None = None
    
    def _refresh_cache(self) -> None:
        """Refresh the embeddings cache from database."""
        self._embeddings_cache = self.db.get_all_embeddings()
    
    async def deduplicate(self, keyword: ExtractedKeyword) -> DeduplicationResult:
        """
        Deduplicate a single keyword.
        
        Args:
            keyword: The extracted keyword to process
            
        Returns:
            DeduplicationResult with the (existing or new) keyword
        """
        # Ensure cache is loaded
        if self._embeddings_cache is None:
            self._refresh_cache()
        
        # Generate embedding for the extracted keyword
        embedding = await self.embeddings.embed_text(keyword.canonical_name)
        
        # Find best match in existing keywords
        match = find_most_similar(
            target_embedding=embedding,
            embeddings=self._embeddings_cache or [],
            threshold=self.threshold,
        )
        
        if match is not None:
            # Found a similar keyword - link as alias
            matched_id, similarity = match
            existing_keyword = self.db.get_keyword_by_id(matched_id)
            
            if existing_keyword is None:
                raise ValueError(f"Keyword not found in database: {matched_id}")
            
            # Add the original name as an alias if different
            if keyword.name != existing_keyword.canonical_name:
                self.db.add_alias(matched_id, keyword.name)
            
            if keyword.canonical_name != existing_keyword.canonical_name:
                self.db.add_alias(matched_id, keyword.canonical_name)
            
            return DeduplicationResult(
                keyword=existing_keyword,
                is_new=False,
                matched_similarity=similarity,
            )
        
        # No match found - create new keyword
        new_keyword = self.db.add_keyword(
            canonical_name=keyword.canonical_name,
            keyword_type=keyword.keyword_type,
            category=keyword.category,
            embedding=embedding,
            aliases=[keyword.name] if keyword.name != keyword.canonical_name else [],
        )
        
        # Update cache with new keyword
        if self._embeddings_cache is not None:
            self._embeddings_cache.append((new_keyword.id, embedding))
        
        return DeduplicationResult(
            keyword=new_keyword,
            is_new=True,
        )
    
    async def deduplicate_batch(
        self,
        keywords: list[ExtractedKeyword],
    ) -> list[DeduplicationResult]:
        """
        Deduplicate multiple keywords.
        
        Args:
            keywords: List of extracted keywords
            
        Returns:
            List of DeduplicationResult
        """
        results = []
        for keyword in keywords:
            result = await self.deduplicate(keyword)
            results.append(result)
        return results


async def process_article_keywords(
    embeddings_client: EmbeddingsClient,
    keywords_db: KeywordsDatabase,
    keywords: list[ExtractedKeyword],
    similarity_threshold: float = 0.85,
) -> list[DeduplicationResult]:
    """
    Convenience function to process all keywords from an article.
    
    Args:
        embeddings_client: Gemini embeddings client
        keywords_db: Keywords database
        keywords: Extracted keywords from an article
        similarity_threshold: Matching threshold
        
    Returns:
        List of DeduplicationResult
    """
    deduplicator = KeywordDeduplicator(
        embeddings_client=embeddings_client,
        keywords_db=keywords_db,
        similarity_threshold=similarity_threshold,
    )
    return await deduplicator.deduplicate_batch(keywords)
