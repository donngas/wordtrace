# Development Guide

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) - Python package manager
- Neo4j 5.x (local or Docker)
- Node.js 20+ (for frontend)

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

| Variable               | Description                                             |
| ---------------------- | ------------------------------------------------------- |
| `OPENROUTER_API_KEY`   | API key from [OpenRouter](https://openrouter.ai/)       |
| `NEO4J_URI`            | Neo4j connection URI (default: `bolt://localhost:7687`) |
| `NEO4J_USER`           | Neo4j username (default: `neo4j`)                       |
| `NEO4J_PASSWORD`       | Neo4j password                                          |
| `SIMILARITY_THRESHOLD` | Keyword matching threshold (default: `0.85`)            |

### 3. Start Neo4j

**Option A: Docker**

```bash
docker run -d \
  --name wordtrace-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5
```

**Option B: Neo4j Desktop**
Download from [neo4j.com](https://neo4j.com/download/)

### 4. Run Development Server

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

## Frontend Setup

> Frontend development comes later. Minimal setup instructions:

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app
│   └── routers/               # Route handlers
│       ├── keywords.py
│       ├── articles.py
│       └── graph.py
├── modules/
│   ├── llm/                   # LLM integration
│   │   ├── llm_client.py
│   │   └── extractor.py
│   ├── keywords/              # Keyword management
│   │   ├── keywords_db.py
│   │   └── deduplicator.py
│   ├── news/                  # News acquisition
│   │   ├── rss_parser.py
│   │   └── article_fetcher.py
│   └── graph/                 # Neo4j operations
│       ├── neo4j_client.py
│       └── graph_operations.py
├── tests/                     # Test suite
├── pyproject.toml
└── .env.example
```

## Testing

```bash
cd backend
uv run pytest
```

## Code Style

- **Python**: Follow PEP 8, use type hints
- **Imports**: Use absolute imports from project root
- **Async**: Use async/await for I/O operations

## Adding Dependencies

```bash
cd backend
uv add package-name
```
