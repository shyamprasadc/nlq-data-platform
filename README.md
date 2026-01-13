# FastAPI Backend - Production-Ready Template

A production-ready FastAPI backend with clean layered architecture, following service-based design patterns.

## 🏗️ Architecture

This project implements a **layered architecture** with clear separation of concerns:

```
API Layer (Routes) → Service Layer → Repository Layer → Database Layer
```

- **API Layer**: Thin controllers handling HTTP requests/responses
- **Service Layer**: Business logic and coordination
- **Repository Layer**: Data access and database queries
- **Database Layer**: SQLAlchemy models and schema

## 🚀 Quick Start

### Prerequisites
- Python 3.14+
- `uv` package manager (or `pip`)

### Installation

1. **Clone and navigate to the project:**
```bash
cd /Users/shyam/Desktop/Projects/Python/fastapi-backend
```

2. **Install dependencies:**
```bash
uv sync
```

3. **Configure environment:**
The `.env` file is already set up with development defaults. Update `SECRET_KEY` for production.

4. **Run the application:**
```bash
uvicorn app.main:app --reload
```

Or use the provided script:
```bash
python main.py
```

The API will be available at: http://localhost:8000

### Using Docker

**Build and run with Docker Compose (recommended):**
```bash
docker-compose up -d
```

This will start:
- FastAPI application on port 8000
- PostgreSQL database on port 5432
- Redis (optional) on port 6379

**Or build and run with Docker only:**
```bash
# Build the image
docker build -t fastapi-backend .

# Run the container
docker run -d -p 8000:8000 --name fastapi-app fastapi-backend
```

**View logs:**
```bash
docker-compose logs -f app
```

**Stop services:**
```bash
docker-compose down
```

**Stop and remove volumes:**
```bash
docker-compose down -v
```


## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 Key Features

### ✅ Clean Architecture
- Layered design with dependency injection
- Repository pattern for data access
- Service layer for business logic
- Thin controllers

### ✅ Authentication
- JWT token-based authentication
- Password hashing with bcrypt
- User management endpoints

### ✅ AI/LLM Ready
- Mock LLM service for development
- Placeholder methods for OpenAI, HuggingFace, LangChain
- Document storage for AI interactions

### ✅ Database
- SQLAlchemy ORM with SQLite (development)
- Easy migration to PostgreSQL/MySQL
- Automatic table creation
- Timestamp tracking

### ✅ Developer Experience
- Pydantic for validation and documentation
- Structured logging
- Comprehensive error handling
- Type hints throughout

## 📁 Project Structure

```
app/
├── main.py                    # Application entry point
├── core/                      # Core configuration
│   ├── config.py             # Settings management
│   ├── security.py           # Auth & security
│   └── logging.py            # Logging setup
├── api/v1/                    # API endpoints (versioned)
│   ├── endpoints/
│   │   ├── auth.py           # Authentication
│   │   ├── users.py          # User management
│   │   └── ai.py             # AI/LLM endpoints
│   └── api_router.py         # Router aggregation
├── schemas/                   # Pydantic schemas
├── models/                    # SQLAlchemy models
├── services/                  # Business logic
├── repositories/              # Data access
├── db/                        # Database setup
├── utils/                     # Utilities
└── tests/                     # Test suite
```

## 🧪 Testing

Run the test suite:
```bash
pytest app/tests/
```

Run with coverage:
```bash
pytest app/tests/ --cov=app
```

## 🔌 API Endpoints

### Health Check
- `GET /health` - Application health status

### Authentication
- `POST /api/v1/auth/login` - User login (returns JWT)
- `POST /api/v1/auth/logout` - User logout

### Users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### AI/LLM
- `POST /api/v1/ai/generate` - Generate AI response
- `GET /api/v1/ai/documents` - List documents
- `POST /api/v1/ai/documents` - Create document
- `GET /api/v1/ai/documents/{id}` - Get document
- `PUT /api/v1/ai/documents/{id}` - Update document
- `DELETE /api/v1/ai/documents/{id}` - Delete document

## 🔧 Configuration

Key environment variables in `.env`:

```bash
# Database
DATABASE_URL=sqlite:///./app.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Environment
ENVIRONMENT=development
```

## 🚢 Production Deployment

### 1. Database Migration
Switch to PostgreSQL:
```bash
# Update .env
DATABASE_URL=postgresql://user:password@localhost/dbname

# Set up Alembic
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 2. LLM Integration
Update `app/services/llm_service.py` with your preferred provider:

**OpenAI:**
```python
from openai import OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)
```

**HuggingFace:**
```python
from transformers import pipeline
generator = pipeline('text-generation', model='gpt2')
```

### 3. Security
- Generate a strong `SECRET_KEY`: `openssl rand -hex 32`
- Enable HTTPS
- Configure CORS for your production domain
- Add rate limiting
- Set up monitoring (Sentry, Datadog, etc.)

### 4. Deployment Options
- **Docker**: Create Dockerfile and docker-compose.yml
- **Cloud**: Deploy to AWS, GCP, or Azure
- **Platform**: Use Heroku, Railway, or Render

## 📖 Example Usage

### Create a user:
```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
  }'
```

### Login:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

### Generate AI response:
```bash
curl -X POST http://localhost:8000/api/v1/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain FastAPI in simple terms",
    "max_tokens": 500,
    "temperature": 0.7
  }'
```

## 🛠️ Development

### Adding a new endpoint:
1. Create Pydantic schema in `app/schemas/`
2. Create SQLAlchemy model in `app/models/` (if needed)
3. Create repository in `app/repositories/`
4. Create service in `app/services/`
5. Create endpoint in `app/api/v1/endpoints/`
6. Add router to `app/api/v1/api_router.py`

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Keep routes thin (delegate to services)

## 📝 License

MIT License - feel free to use this template for your projects!

## 🤝 Contributing

Contributions are welcome! Please follow the existing code structure and patterns.

## 📞 Support

For issues or questions, please open an issue on the repository.

---

**Built with ❤️ using FastAPI, SQLAlchemy, and Pydantic**
