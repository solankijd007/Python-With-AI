"""
CRUD operations for Item model.
Provides database operations for item management with ownership verification.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


def get_item(db: Session, item_id: int) -> Optional[Item]:
    """
    Get item by ID.
    
    Args:
        db: Database session
        item_id: Item ID
        
    Returns:
        Item object or None if not found
    """
    return db.query(Item).filter(Item.id == item_id).first()


def get_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    owner_id: Optional[int] = None
) -> List[Item]:
    """
    Get list of items with pagination and optional filtering by owner.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        owner_id: Optional filter by owner ID
        
    Returns:
        List of items
    """
    query = db.query(Item)
    if owner_id is not None:
        query = query.filter(Item.owner_id == owner_id)
    return query.offset(skip).limit(limit).all()


def get_items_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Item]:
    """
    Get all items owned by a specific user.
    
    Args:
        db: Database session
        owner_id: Owner user ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of items owned by the user
    """
    return db.query(Item).filter(Item.owner_id == owner_id).offset(skip).limit(limit).all()


def create_item(db: Session, item: ItemCreate, owner_id: int) -> Item:
    """
    Create a new item.
    
    Args:
        db: Database session
        item: Item creation schema
        owner_id: ID of the user who owns this item
        
    Returns:
        Created item object
    """
    db_item = Item(
        title=item.title,
        description=item.description,
        owner_id=owner_id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(
    db: Session,
    item_id: int,
    item_update: ItemUpdate,
    owner_id: Optional[int] = None
) -> Optional[Item]:
    """
    Update item information.
    Optionally verify ownership before updating.
    
    Args:
        db: Database session
        item_id: Item ID to update
        item_update: Item update schema
        owner_id: Optional owner ID for ownership verification
        
    Returns:
        Updated item object or None if not found or not authorized
    """
    db_item = get_item(db, item_id)
    if not db_item:
        return None
    
    # Verify ownership if owner_id is provided
    if owner_id is not None and db_item.owner_id != owner_id:
        return None
    
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int, owner_id: Optional[int] = None) -> bool:
    """
    Delete an item.
    Optionally verify ownership before deleting.
    
    Args:
        db: Database session
        item_id: Item ID to delete
        owner_id: Optional owner ID for ownership verification
        
    Returns:
        True if deleted, False if not found or not authorized
    """
    db_item = get_item(db, item_id)
    if not db_item:
        return False
    
    # Verify ownership if owner_id is provided
    if owner_id is not None and db_item.owner_id != owner_id:
        return False
    
    db.delete(db_item)
    db.commit()
    return True


def count_items(db: Session, owner_id: Optional[int] = None) -> int:
    """
    Count total number of items, optionally filtered by owner.
    
    Args:
        db: Database session
        owner_id: Optional filter by owner ID
        
    Returns:
        Total count of items
    """
    query = db.query(Item)
    if owner_id is not None:
        query = query.filter(Item.owner_id == owner_id)
    return query.count()
