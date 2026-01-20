"""
Pydantic schemas for JWT tokens.
Used for authentication token validation and responses.
"""
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class TokenData(BaseModel):
    """Schema for token payload data."""
    email: Optional[str] = None
    type: Optional[str] = None
