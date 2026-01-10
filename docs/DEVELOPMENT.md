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
| `SIMILARITY_THRESHOLD` | Keyword matching threshold (default: `0.85`)      |

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
│       └── keywords.py
├── modules/
│   ├── llm/                    # LLM integration
│   │   ├── llm_client.py
│   │   └── extractor.py
│   └── keywords/               # Keyword management
│       ├── keywords_db.py
│       └── deduplicator.py
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
