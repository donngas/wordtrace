
"""
Centralized prompt templates for WordTrace.
"""

def get_extraction_system_prompt() -> str:
    """
    Get the system prompt for keyword extraction.
    """
    return """You are a news article analyzer. Your task is to:

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


def get_extraction_user_prompt(title: str, content: str) -> str:
    """
    Get the user prompt for keyword extraction.
    
    Args:
        title: Article title
        content: Article content
        
    Returns:
        Formatted user prompt string
    """
    return f"""Analyze this article:

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
