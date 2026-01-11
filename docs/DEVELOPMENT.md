# Development Guide

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) - Python package manager

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
uv sync
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

**Required environment variables:**

| Variable               | Description                                       |
| ---------------------- | ------------------------------------------------- |
| `OPENROUTER_API_KEY`   | API key from [OpenRouter](https://openrouter.ai/) |
| `GEMINI_API_KEY`       | Google Gemini API key for embeddings              |
| `SIMILARITY_THRESHOLD` | Keyword matching threshold (default: `0.85`)      |
| `NEO4J_URI`           | Neo4j URI (e.g., bolt://localhost:7687) (WIP)     |
| `NEO4J_USER`          | Neo4j Username (default: neo4j) (WIP)             |
| `NEO4J_PASSWORD`      | Neo4j Password (WIP)                              |

### 3. Run Development Server

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app
│   └── routers/                # Route handlers
├── modules/
│   ├── articles/               # News acquisition
│   │   ├── rss_fetcher.py      # RSS polling
│   │   ├── paperboy.py         # Full text retrieval
│   │   └── articles_db.py      # SQLite storage
│   ├── pipeline/               # Orchestration
│   │   └── orchestrator.py     # Main pipeline runner
│   ├── llm/                    # LLM integration
│   │   ├── llm_client.py       # OpenAI/OpenRouter client
│   │   ├── embeddings.py       # Gemini Embeddings client
│   │   └── extractor.py        # Logic
│   ├── keywords/               # Keyword management
│   │   ├── keywords_db.py
│   │   └── deduplicator.py
│   └── graph/                  # Graph DB (WIP)
│       └── neo4j_client.py
├── tests/                      # Test suite
├── pyproject.toml
└── .env.example
```

## Testing

- All test code shall be placed in the `backend/tests` directory
- All test code shall be named `test_*.py`

## Code Style

- **Python**: Follow PEP 8, use type hints
- **Imports**: Use absolute imports from project root
- **Async**: Use async/await for I/O operations

## Adding Dependencies

```bash
cd backend
uv add package-name
```
