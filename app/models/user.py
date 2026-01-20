"""
User database model.
Represents users in the system with authentication and profile information.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class User(Base):
    """
    User model for authentication and user management.
    
    Attributes:
        id: Primary key
        email: Unique email address for authentication
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        is_active: Whether the user account is active
        is_superuser: Whether the user has admin privileges
        created_at: Timestamp of user creation
        updated_at: Timestamp of last update
        items: Relationship to user's items
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship to items
    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
