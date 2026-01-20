"""
Import all models here for Alembic migrations.
This ensures Alembic can detect all models when generating migrations.
"""
from app.db.session import Base
from app.models.user import User
from app.models.item import Item

__all__ = ["Base", "User", "Item"]
