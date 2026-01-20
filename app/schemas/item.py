"""
Pydantic schemas for Item model.
Used for request/response validation and serialization.
"""
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.user import User


class ItemBase(BaseModel):
    """Base item schema with common attributes."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ItemCreate(ItemBase):
    """Schema for creating a new item."""
    pass


class ItemUpdate(BaseModel):
    """Schema for updating item information."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ItemInDBBase(ItemBase):
    """Base schema for item in database."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Item(ItemInDBBase):
    """Schema for item response with owner information."""
    pass

