"""
User management endpoints.
Provides CRUD operations for user accounts with authentication.
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.db.session import get_db

router = APIRouter()


@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(security.get_current_active_user),
) -> Any:
    """
    Get current authenticated user.
    """
    return current_user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(security.get_current_active_user),
) -> Any:
    """
    Update current user information.
    
    - **email**: Optional new email address
    - **full_name**: Optional new full name
    - **password**: Optional new password
    """
    # Check if email is being changed and if it's already taken
    if user_in.email and user_in.email != current_user.email:
        existing_user = crud.crud_user.get_user_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists",
            )
    
    user = crud.crud_user.update_user(db, user_id=current_user.id, user_update=user_in)
    return user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific user by ID.
    Requires authentication.
    """
    user = crud.crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Regular users can only view their own profile
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return user


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(security.get_current_active_user),
) -> Any:
    """
    Retrieve list of users.
    Only accessible by superusers.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Superuser access required.",
        )
    
    users = crud.crud_user.get_users(db, skip=skip, limit=limit)
    return users


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: models.User = Depends(security.get_current_active_user),
) -> None:
    """
    Delete a user.
    Users can delete their own account, superusers can delete any account.
    """
    # Check if user exists
    user = crud.crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check permissions
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    crud.crud_user.delete_user(db, user_id=user_id)
