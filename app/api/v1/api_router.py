"""
API v1 router aggregation.
Combines all v1 endpoint routers into a single router.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, ai

# Create the main v1 API router
api_router = APIRouter()

# Include all endpoint routers
# Each router is prefixed and tagged appropriately in its own file
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(ai.router)
