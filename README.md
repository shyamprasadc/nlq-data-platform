# NLQ Data Platform

> Production-grade NLQ platform with FastAPI-powered RAG pipeline and AWS data engineering infrastructure for natural language querying across multiple data sources

[![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.124+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

The **NLQ Data Platform** is a production-ready system that enables natural language querying across multiple data sources. It combines:

- **FastAPI Backend**: RESTful API with RAG (Retrieval-Augmented Generation) pipeline
- **Vector Database**: Semantic search and document retrieval
- **LLM Integration**: Natural language understanding and SQL generation
- **AWS Data Infrastructure**: Scalable ETL pipelines with Glue, Athena, and PySpark
- **Clean Architecture**: Layered design with service-based patterns

### 🏗️ Platform Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NLQ Data Platform                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │   Frontend   │──────│  FastAPI     │                   │
│  │   (Future)   │      │   Backend    │                   │
│  └──────────────┘      └──────┬───────┘                   │
│                               │                            │
│                    ┌──────────┴──────────┐                │
│                    │                     │                 │
│              ┌─────▼─────┐        ┌─────▼─────┐          │
│              │    RAG    │        │  Vector   │          │
│              │  Pipeline │        │ Database  │          │
│              └─────┬─────┘        └───────────┘          │
│                    │                                       │
│              ┌─────▼─────┐                                │
│              │    LLM    │                                │
│              │  Service  │                                │
│              └─────┬─────┘                                │
│                    │                                       │
│         ┌──────────┴──────────┐                          │
│         │                     │                           │
│    ┌────▼────┐          ┌────▼────┐                     │
│    │  NLQ to │          │  Data   │                     │
│    │   SQL   │          │ Sources │                     │
│    └─────────┘          └─────────┘                     │
│                                                           │
├───────────────────────────────────────────────────────────┤
│                  AWS Data Infrastructure                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │   S3     │  │  Glue    │  │  Athena  │  │ PySpark │ │
│  │  (Data   │─▶│  (ETL)   │─▶│ (Query)  │  │ (Proc.) │ │
│  │  Lake)   │  │          │  │          │  │         │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└───────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
nlq-data-platform/
├── backend/                    # FastAPI Backend Service (Current)
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── core/              # Configuration & security
│   │   ├── api/v1/            # API endpoints
│   │   ├── schemas/           # Pydantic models
│   │   ├── models/            # Database models
│   │   ├── services/          # Business logic
│   │   │   ├── llm_service.py      # LLM integration
│   │   │   ├── ai_service.py       # RAG pipeline
│   │   │   └── user_service.py     # User management
│   │   ├── repositories/      # Data access layer
│   │   ├── db/                # Database setup
│   │   └── tests/             # Test suite
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
│
├── etl/                       # AWS ETL Pipelines (Coming Soon)
│   ├── glue_jobs/            # AWS Glue ETL scripts
│   ├── pyspark/              # PySpark transformations
│   ├── athena_queries/       # Athena SQL queries
│   └── infrastructure/       # Terraform/CloudFormation
│
├── vector-db/                 # Vector Database Setup (Coming Soon)
│   ├── embeddings/           # Document embeddings
│   ├── indexing/             # Vector indexing
│   └── retrieval/            # Semantic search
│
└── docs/                      # Documentation
    ├── architecture.md
    ├── api-reference.md
    └── deployment.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.14+
- Docker & Docker Compose
- AWS Account (for ETL pipelines)
- OpenAI/HuggingFace API key (for LLM integration)

### Backend Service Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Install dependencies:**
```bash
uv sync
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run with Docker Compose (Recommended):**
```bash
docker-compose up -d
```

Or run locally:
```bash
uvicorn app.main:app --reload
```

5. **Access the API:**
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔑 Key Features

### ✅ Backend Service (Current)

#### Clean Architecture
- **Layered design**: Routes → Services → Repositories → Database
- **Dependency injection** for testability
- **Repository pattern** for data access
- **Service layer** for business logic

#### Authentication & Security
- JWT token-based authentication
- Password hashing with bcrypt
- Role-based access control (ready)
- CORS configuration

#### AI/LLM Integration
- **RAG Pipeline**: Document retrieval and generation
- **Vector Search**: Semantic document matching
- **LLM Service**: OpenAI, HuggingFace, LangChain support
- **NLQ to SQL**: Natural language to SQL conversion (ready)

#### Database
- SQLAlchemy ORM with PostgreSQL
- Automatic migrations with Alembic
- Document storage for AI interactions
- User management

#### API Endpoints

**Authentication:**
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/logout` - User logout

**Users:**
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

**AI/NLQ:**
- `POST /api/v1/ai/generate` - Generate AI response from NLQ
- `GET /api/v1/ai/documents` - List indexed documents
- `POST /api/v1/ai/documents` - Index new document
- `GET /api/v1/ai/documents/{id}` - Get document
- `PUT /api/v1/ai/documents/{id}` - Update document
- `DELETE /api/v1/ai/documents/{id}` - Delete document

### 🔄 ETL Pipeline (Coming Soon)

- **AWS Glue**: Serverless ETL jobs
- **PySpark**: Distributed data processing
- **AWS Athena**: SQL queries on S3 data lake
- **Data Catalog**: Metadata management
- **Incremental Loading**: Efficient data updates

### 🔍 Vector Database (Coming Soon)

- **Embeddings**: Document and query vectorization
- **Semantic Search**: Context-aware retrieval
- **Indexing**: Efficient vector storage
- **Similarity Matching**: Relevant document retrieval

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.124+
- **ORM**: SQLAlchemy 2.0+
- **Validation**: Pydantic 2.0+
- **Authentication**: python-jose, passlib
- **Database**: PostgreSQL (production), SQLite (development)

### AI/ML
- **LLM**: OpenAI GPT-4, HuggingFace Transformers
- **Framework**: LangChain
- **Vector DB**: Pinecone, Weaviate, or ChromaDB (planned)
- **Embeddings**: OpenAI, HuggingFace

### AWS Infrastructure
- **Storage**: S3 (Data Lake)
- **ETL**: AWS Glue, PySpark
- **Query**: AWS Athena
- **Orchestration**: AWS Step Functions
- **Monitoring**: CloudWatch

### DevOps
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions (planned)
- **IaC**: Terraform (planned)
- **Monitoring**: Prometheus, Grafana (planned)

---

## 📖 Use Cases

### 1. Natural Language Querying
```
User: "Show me all sales from last quarter where revenue exceeded $100k"
       ↓
NLQ Platform processes the query
       ↓
Generates SQL: SELECT * FROM sales WHERE date >= '2024-01-01' AND revenue > 100000
       ↓
Executes on AWS Athena
       ↓
Returns formatted results
```

### 2. Document-Based Q&A
```
User: "What were the key findings in the Q4 report?"
       ↓
RAG Pipeline retrieves relevant document sections
       ↓
LLM generates contextual answer
       ↓
Returns answer with source citations
```

### 3. Data Exploration
```
User: "What data sources are available?"
       ↓
Platform queries data catalog
       ↓
Returns available tables, schemas, and metadata
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/nlq_platform

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Configuration
OPENAI_API_KEY=your-openai-key
HUGGINGFACE_API_KEY=your-hf-key

# Vector Database
VECTOR_DB_URL=your-vector-db-url
VECTOR_DB_API_KEY=your-vector-db-key

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET=your-data-lake-bucket

# CORS
CORS_ORIGINS=http://localhost:3000,https://your-frontend.com

# Environment
ENVIRONMENT=production
```

---

## 🚢 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f app

# Scale services
docker-compose up -d --scale app=3
```

### AWS Deployment (Planned)

- **ECS/Fargate**: Container orchestration
- **RDS**: Managed PostgreSQL
- **ElastiCache**: Redis for caching
- **ALB**: Load balancing
- **CloudFront**: CDN for static assets

---

## 🧪 Testing

```bash
# Run all tests
pytest backend/app/tests/

# Run with coverage
pytest backend/app/tests/ --cov=app

# Run specific test file
pytest backend/app/tests/test_users.py
```

---

## 📊 Roadmap

### Phase 1: Backend Service ✅ (Current)
- [x] FastAPI application with clean architecture
- [x] User authentication and management
- [x] LLM service integration (mock)
- [x] Document storage
- [x] Docker containerization
- [x] API documentation

### Phase 2: LLM & RAG Pipeline 🔄 (In Progress)
- [ ] OpenAI/HuggingFace integration
- [ ] Vector database setup
- [ ] Document embedding pipeline
- [ ] Semantic search implementation
- [ ] RAG pipeline optimization

### Phase 3: NLQ to SQL 📋 (Planned)
- [ ] SQL generation from natural language
- [ ] Query validation and optimization
- [ ] Multi-database support
- [ ] Query result formatting
- [ ] Query history and caching

### Phase 4: AWS ETL Pipeline 📋 (Planned)
- [ ] AWS Glue job development
- [ ] PySpark transformations
- [ ] Athena query optimization
- [ ] Data catalog setup
- [ ] Incremental data loading

### Phase 5: Production Features 📋 (Planned)
- [ ] Advanced monitoring and logging
- [ ] Rate limiting and throttling
- [ ] Advanced caching strategies
- [ ] Multi-tenancy support
- [ ] Admin dashboard

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add type hints to all functions
- Write comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For issues, questions, or contributions:
- **Issues**: [GitHub Issues](https://github.com/yourusername/nlq-data-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/nlq-data-platform/discussions)

---

## 🙏 Acknowledgments

- **FastAPI**: For the excellent web framework
- **LangChain**: For LLM orchestration tools
- **AWS**: For scalable cloud infrastructure
- **OpenAI**: For powerful language models

---

**Built with ❤️ for democratizing data access through natural language**

---

## 📚 Additional Documentation

- [Backend Service Documentation](backend/README.md)
- [Docker Deployment Guide](backend/DOCKER.md)
- [API Reference](docs/api-reference.md) (Coming Soon)
- [Architecture Overview](docs/architecture.md) (Coming Soon)
- [ETL Pipeline Guide](docs/etl-pipeline.md) (Coming Soon)
