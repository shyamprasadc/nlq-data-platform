# NLQ Data Platform

A production-grade Natural Language Query platform combining a FastAPI backend for RAG-powered queries and a PySpark ETL pipeline for data ingestion.

## Project Structure

```
nlq-data-platform/
├── backend/          # FastAPI server (NLQ + RAG pipeline)
├── etl/              # PySpark ETL pipeline (MySQL → S3)
├── docker-compose.yml
└── pyproject.toml    # Unified dependencies
```

## Quick Start

### Prerequisites
- Python 3.14+
- [uv](https://github.com/astral-sh/uv) for dependency management

### Installation
```bash
uv sync
```

### Running Services

**Backend API Server:**
```bash
python backend/run.py
# API docs: http://localhost:8000/docs
```

**ETL Pipeline:**
```bash
python -m etl.main
```

**Docker (all services):**
```bash
docker-compose up -d
```

## Services

| Service | Description | Docs |
|---------|-------------|------|
| **Backend** | FastAPI server with LangChain RAG pipeline for natural language queries | [backend/README.md](backend/README.md) |
| **ETL** | PySpark pipeline for incremental data ingestion from MySQL to S3 | [etl/README.md](etl/README.md) |

## Environment Variables

Each service has its own `.env` file:
- `backend/.env` — API keys, database URLs, secrets
- `etl/.env` — MySQL credentials, S3 bucket config
