# WordTrace

A news article keyword analysis and co-occurrence network visualization tool.

## Overview

WordTrace acquires news articles, extracts keywords using LLM, and presents analysis with graph visualization.

### Key Features

- **News Acquisition**: RSS/API-based article discovery
- **Keyword Extraction**: LLM-powered entity and concept identification (via OpenRouter/Gemini 2.5 Flash)
- **Article Categorization**: Automatic classification into Politics, Business, Sports, etc.
- **Smart Deduplication**: Gemini API embedding-based similarity matching

### Keyword Categories

| Type | Categories |
| --- | --- |
| **Entities** | People, Places, Organizations |
| **Concepts** | Geopolitics, Economic Crisis, Innovation |

### Article Categories

Politics, Business, Sports, Entertainment, Technology, Health & Science, World

## Architecture

```
wordtrace/
├── backend/
│   ├── app/                    # FastAPI application
│   │   ├── main.py             # App entry point
│   │   └── routers/            # API route handlers
│   └── modules/                # Core business logic
│       ├── llm/                # Keyword extraction
│       └── keywords/           # Deduplication + SQLite
└── frontend/                   # React visualization (TBD)
```

### Data Flow

```mermaid
graph LR
    A[Article Text] --> B[LLM Extraction]
    B --> C[Keyword Dedup]
    C --> D[(SQLite)]
```

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Python 3.12+, FastAPI, uv |
| LLM | OpenRouter API (Gemini 2.5 Flash) |
| Embeddings | Gemini API (text-embedding-004) |
| Keywords DB | SQLite3 |
| Frontend | React, react-force-graph (TBD) |

## Quick Start

```bash
# Backend
cd backend
uv sync
cp .env.example .env  # Configure API keys
uv run uvicorn app.main:app --reload
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design details
- [Development](docs/DEVELOPMENT.md) - Setup and contribution guide

## License

MIT

## To Do

- Plan and implement graph storage architecture + integration with articles
- Set up docker environment for the repository, especially for Neo4j
- Implement News Acquisition module (rss, newspaper4k)
- Work on proper backend (routers, etc.)
- Create Frontend
