"""
Main FastAPI application.
Initializes the app with middleware, routes, and lifecycle events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.core.config import settings
from backend.core.logging import setup_logging, get_logger
from backend.api.v1.api_router import api_router
from backend.db.init_db import init_db

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.

    Handles startup and shutdown logic:
    - Startup: Initialize database, load models, etc.
    - Shutdown: Cleanup resources, close connections, etc.
    """
    # Startup
    logger.info("Starting up application...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Initialize FastAPI application
app = FastAPI(
    title="NLQ Data Platform API",
    description="Production-grade NLQ platform with FastAPI-powered RAG pipeline for natural language querying across multiple data sources",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Configure CORS middleware
# In production, restrict origins to your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint.

    Used by load balancers, monitoring systems, and container orchestration
    to verify the application is running correctly.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint with API information.

    Returns:
        Welcome message and API documentation links
    """
    return {
        "message": "Welcome to the NLQ Data Platform API",
        "description": "Natural Language Query platform for querying data sources using natural language",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "api_version": "v1",
        "api_prefix": "/api/v1",
    }


# Include API v1 router
# All v1 endpoints are prefixed with /api/v1
app.include_router(api_router, prefix="/api/v1")
