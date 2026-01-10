"""
Gemini API embeddings client.

Uses Gemini's gemini-embedding-001 model for keyword similarity matching.
"""

from google import genai
from google.genai import types
import numpy as np


class EmbeddingsClient:
    """Client for Gemini embedding generation."""
    
    DEFAULT_MODEL = "gemini-embedding-001"
    
    def __init__(self, api_key: str, model: str | None = None):
        """
        Initialize the embeddings client.
        
        Args:
            api_key: Gemini API key
            model: Embedding model to use (defaults to gemini-embedding-001)
        """
        self.model = model or self.DEFAULT_MODEL
        self._client = genai.Client(api_key=api_key)
    
    async def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        result = self._client.models.embed_content(
            model=self.model,
            contents=text,
        )
        return list(result.embeddings[0].values)
    
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts (batch).
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        result = self._client.models.embed_content(
            model=self.model,
            contents=texts,
        )
        return [list(emb.values) for emb in result.embeddings]


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity score (0-1)
    """
    a = np.array(vec1)
    b = np.array(vec2)
    
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return float(dot_product / (norm_a * norm_b))


def find_most_similar(
    target_embedding: list[float],
    embeddings: list[tuple[str, list[float]]],
    threshold: float = 0.85,
) -> tuple[str, float] | None:
    """
    Find the most similar embedding above a threshold.
    
    Args:
        target_embedding: The embedding to compare against
        embeddings: List of (id, embedding) tuples to search
        threshold: Minimum similarity threshold
        
    Returns:
        Tuple of (id, similarity) if found, None otherwise
    """
    best_match: tuple[str, float] | None = None
    
    for id_, embedding in embeddings:
        similarity = cosine_similarity(target_embedding, embedding)
        if similarity >= threshold:
            if best_match is None or similarity > best_match[1]:
                best_match = (id_, similarity)
    
    return best_match
