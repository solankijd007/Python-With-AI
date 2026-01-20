"""
Item management endpoints.
Provides CRUD operations for items with ownership verification.
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.db.session import get_db

router = APIRouter()


@router.post("/", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
def create_item(
    *,
    db: Session = Depends(get_db),
    item_in: schemas.ItemCreate,
    current_user: models.User = Depends(security.get_current_active_user),
) -> Any:
    """
    Create a new item.
    Requires authentication.
    
    - **title**: Item title (required)
    - **description**: Item description (optional)
    """
    item = crud.crud_item.create_item(db, item=item_in, owner_id=current_user.id)
    return item


@router.get("/", response_model=List[schemas.Item])
def read_items(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve list of all items.
    Public endpoint - no authentication required.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    items = crud.crud_item.get_items(db, skip=skip, limit=limit)
    return items


@router.get("/my-items", response_model=List[schemas.Item])
def read_my_items(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(security.get_current_active_user),
) -> Any:
    """
    Retrieve current user's items.
    Requires authentication.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    items = crud.crud_item.get_items_by_owner(
        db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return items


@router.get("/{item_id}", response_model=schemas.Item)
def read_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
) -> Any:
    """
    Get item by ID.
    Public endpoint - no authentication required.
    """
    item = crud.crud_item.get_item(db, item_id=item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    return item


@router.put("/{item_id}", response_model=schemas.Item)
def update_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    item_in: schemas.ItemUpdate,
    current_user: models.User = Depends(security.get_current_active_user),
) -> Any:
    """
    Update an item.
    Only the owner or superuser can update an item.
    
    - **title**: Optional new title
    - **description**: Optional new description
    """
    # Get item
    item = crud.crud_item.get_item(db, item_id=item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    # Check ownership
    if item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. You can only update your own items.",
        )
    
    item = crud.crud_item.update_item(db, item_id=item_id, item_update=item_in)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user: models.User = Depends(security.get_current_active_user),
) -> None:
    """
    Delete an item.
    Only the owner or superuser can delete an item.
    """
    # Get item
    item = crud.crud_item.get_item(db, item_id=item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    # Check ownership
    if item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. You can only delete your own items.",
        )
    
    crud.crud_item.delete_item(db, item_id=item_id)
