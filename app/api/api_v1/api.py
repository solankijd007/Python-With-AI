"""
API v1 router aggregation.
Combines all endpoint routers for version 1 of the API.
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, items

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
