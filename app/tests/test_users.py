"""
Example tests for user endpoints.
Demonstrates testing patterns for FastAPI applications.
"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


def setup_module():
    """Setup test database before running tests."""
    Base.metadata.create_all(bind=engine)


def teardown_module():
    """Cleanup test database after running tests."""
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_user():
    """Test user creation."""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
    }

    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "hashed_password" not in data  # Should not expose password


def test_create_duplicate_user():
    """Test that creating a duplicate user fails."""
    user_data = {
        "email": "duplicate@example.com",
        "password": "testpassword123",
        "full_name": "Duplicate User",
    }

    # First creation should succeed
    response1 = client.post("/api/v1/users/", json=user_data)
    assert response1.status_code == 201

    # Second creation should fail
    response2 = client.post("/api/v1/users/", json=user_data)
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"].lower()


def test_get_user():
    """Test retrieving a user."""
    # Create a user first
    user_data = {
        "email": "gettest@example.com",
        "password": "testpassword123",
        "full_name": "Get Test User",
    }

    create_response = client.post("/api/v1/users/", json=user_data)
    user_id = create_response.json()["id"]

    # Get the user
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == user_data["email"]


def test_get_nonexistent_user():
    """Test retrieving a non-existent user."""
    response = client.get("/api/v1/users/99999")
    assert response.status_code == 404


def test_login():
    """Test user login."""
    # Create a user first
    user_data = {
        "email": "logintest@example.com",
        "password": "testpassword123",
        "full_name": "Login Test User",
    }

    client.post("/api/v1/users/", json=user_data)

    # Login
    login_data = {"email": user_data["email"], "password": user_data["password"]}

    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    login_data = {"email": "nonexistent@example.com", "password": "wrongpassword"}

    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


def test_ai_generate():
    """Test AI generation endpoint."""
    prompt_data = {
        "prompt": "Hello, AI!",
        "max_tokens": 100,
        "temperature": 0.7,
        "model": "gpt-3.5-turbo",
    }

    response = client.post("/api/v1/ai/generate", json=prompt_data)
    assert response.status_code == 200

    data = response.json()
    assert "response" in data
    assert "model" in data
    assert data["model"] == prompt_data["model"]
