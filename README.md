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

| Type         | Categories                               |
| ------------ | ---------------------------------------- |
| **Entities** | People, Places, Organizations            |
| **Concepts** | Geopolitics, Economic Crisis, Innovation |

### Article Categories

Politics, Business, Sports, Entertainment, Technology, Health & Science, World

## Architecture

```
wordtrace/
├── backend/
│   ├── app/                    # FastAPI application
│   └── modules/                # Core business logic
│       ├── articles/           # RSS & Retrieval
│       ├── pipeline/           # Orchestration
│       ├── llm/                # Extraction
│       ├── keywords/           # Deduplication
│       └── graph/              # Neo4j Client (WIP)
└── frontend/                   # React visualization (TBD)
```

## Tech Stack

| Layer       | Technology                        |
| ----------- | --------------------------------- |
| Backend     | Python 3.12+, FastAPI, uv         |
| LLM         | OpenRouter API (Gemini 2.5 Flash) |
| Embeddings  | Gemini API (text-embedding-004)   |
| Keywords DB | SQLite3                           |
| Frontend    | React, react-force-graph (TBD)    |

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

## To Do

### On existing code

- Fix: URL normalization is weak (stripping query params)
- Fix: Date handling should be UTC-aware and ISO 8601 enforced
- Refactor: Orchestrator leaks SQL (move update logic to articles_db)
- Config: Externalize hardcoded values (User Agent, Model Name)

### Roadmap

- Integration pipeline with Neo4j
- Reassess OpenRouter usage for convenience (consider going all Gemini)
  - Keep LangGraph integration in mind: for more structured and streamlined LLM usage across the application
- Configure news acquisition in detail, including selecting sources
- Work on proper backend API (routers, etc.)
- Create Frontend

### Abstract ideas

- Keyword elaboration
  - Keyword window upon click
    - AI-generated descriptions
    - keyword-centric analysis report
    - Hyperlink to Google search or Wikipedia page
  - Keyword tierization: Assign tiers to keywords based on their importance
    - Higher tier keywords get generated descriptions with LLM etc.
    - Tier gets updated based on updated usage of the keyword in articles
    - Keywords can be demoted to hiatus state if not appearing in articles for a while
  - Updating canonical names
    - For higher tier keywords, canonical names get reconsidered (keep previous vs update) by LLM
    - Possibly based on Google search metrics or Wikipedia page title
  - Keep our own metrics for keyword trends
