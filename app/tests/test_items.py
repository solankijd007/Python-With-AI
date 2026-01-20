"""
Tests for item endpoints.
"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app import crud, schemas


def test_create_item(client: TestClient, auth_headers: dict):
    """Test creating an item."""
    response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=auth_headers,
        json={
            "title": "Test Item",
            "description": "Test Description"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["description"] == "Test Description"
    assert "id" in data
    assert "owner_id" in data


def test_create_item_without_auth(client: TestClient):
    """Test that creating item without auth fails."""
    response = client.post(
        f"{settings.API_V1_STR}/items/",
        json={
            "title": "Test Item",
            "description": "Test Description"
        }
    )
    assert response.status_code == 401


def test_read_items(client: TestClient, db: Session, auth_headers: dict):
    """Test reading all items (public endpoint)."""
    # Create some items
    for i in range(3):
        client.post(
            f"{settings.API_V1_STR}/items/",
            headers=auth_headers,
            json={
                "title": f"Item {i}",
                "description": f"Description {i}"
            }
        )
    
    # Read items without auth (public endpoint)
    response = client.get(f"{settings.API_V1_STR}/items/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_read_my_items(client: TestClient, auth_headers: dict):
    """Test reading current user's items."""
    # Create items
    for i in range(2):
        client.post(
            f"{settings.API_V1_STR}/items/",
            headers=auth_headers,
            json={
                "title": f"My Item {i}",
                "description": f"My Description {i}"
            }
        )
    
    response = client.get(
        f"{settings.API_V1_STR}/items/my-items",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_read_item(client: TestClient, auth_headers: dict):
    """Test reading a specific item."""
    # Create item
    create_response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=auth_headers,
        json={
            "title": "Test Item",
            "description": "Test Description"
        }
    )
    item_id = create_response.json()["id"]
    
    # Read item (public endpoint)
    response = client.get(f"{settings.API_V1_STR}/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Item"


def test_update_item(client: TestClient, auth_headers: dict):
    """Test updating an item."""
    # Create item
    create_response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=auth_headers,
        json={
            "title": "Original Title",
            "description": "Original Description"
        }
    )
    item_id = create_response.json()["id"]
    
    # Update item
    response = client.put(
        f"{settings.API_V1_STR}/items/{item_id}",
        headers=auth_headers,
        json={"title": "Updated Title"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Original Description"


def test_update_other_user_item_fails(client: TestClient, db: Session):
    """Test that updating another user's item fails."""
    # Create first user and item
    user1_data = {
        "email": "user1@example.com",
        "password": "password123",
        "full_name": "User One"
    }
    client.post(f"{settings.API_V1_STR}/auth/register", json=user1_data)
    login1 = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": user1_data["email"], "password": user1_data["password"]}
    )
    headers1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}
    
    create_response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=headers1,
        json={"title": "User1 Item"}
    )
    item_id = create_response.json()["id"]
    
    # Create second user
    user2_data = {
        "email": "user2@example.com",
        "password": "password123",
        "full_name": "User Two"
    }
    client.post(f"{settings.API_V1_STR}/auth/register", json=user2_data)
    login2 = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": user2_data["email"], "password": user2_data["password"]}
    )
    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}
    
    # Try to update user1's item as user2
    response = client.put(
        f"{settings.API_V1_STR}/items/{item_id}",
        headers=headers2,
        json={"title": "Hacked Title"}
    )
    assert response.status_code == 403


def test_delete_item(client: TestClient, auth_headers: dict):
    """Test deleting an item."""
    # Create item
    create_response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=auth_headers,
        json={"title": "To Delete"}
    )
    item_id = create_response.json()["id"]
    
    # Delete item
    response = client.delete(
        f"{settings.API_V1_STR}/items/{item_id}",
        headers=auth_headers
    )
    assert response.status_code == 204
    
    # Verify item is deleted
    get_response = client.get(f"{settings.API_V1_STR}/items/{item_id}")
    assert get_response.status_code == 404


def test_delete_other_user_item_fails(client: TestClient, db: Session):
    """Test that deleting another user's item fails."""
    # Create first user and item
    user1_data = {
        "email": "user1@example.com",
        "password": "password123",
        "full_name": "User One"
    }
    client.post(f"{settings.API_V1_STR}/auth/register", json=user1_data)
    login1 = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": user1_data["email"], "password": user1_data["password"]}
    )
    headers1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}
    
    create_response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=headers1,
        json={"title": "User1 Item"}
    )
    item_id = create_response.json()["id"]
    
    # Create second user
    user2_data = {
        "email": "user2@example.com",
        "password": "password123",
        "full_name": "User Two"
    }
    client.post(f"{settings.API_V1_STR}/auth/register", json=user2_data)
    login2 = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": user2_data["email"], "password": user2_data["password"]}
    )
    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}
    
    # Try to delete user1's item as user2
    response = client.delete(
        f"{settings.API_V1_STR}/items/{item_id}",
        headers=headers2
    )
    assert response.status_code == 403
