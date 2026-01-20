"""
Tests for user endpoints.
"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings


def test_read_user_me(client: TestClient, auth_headers: dict, test_user: dict):
    """Test getting current user."""
    response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["full_name"] == test_user["full_name"]


def test_update_user_me(client: TestClient, auth_headers: dict):
    """Test updating current user."""
    response = client.put(
        f"{settings.API_V1_STR}/users/me",
        headers=auth_headers,
        json={"full_name": "Updated Name"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"


def test_update_user_email(client: TestClient, auth_headers: dict):
    """Test updating user email."""
    response = client.put(
        f"{settings.API_V1_STR}/users/me",
        headers=auth_headers,
        json={"email": "newemail@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newemail@example.com"


def test_read_user_without_auth(client: TestClient):
    """Test that accessing user endpoint without auth fails."""
    response = client.get(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 401


def test_update_password(client: TestClient, auth_headers: dict, test_user: dict):
    """Test updating user password."""
    new_password = "newpassword123"
    response = client.put(
        f"{settings.API_V1_STR}/users/me",
        headers=auth_headers,
        json={"password": new_password}
    )
    assert response.status_code == 200
    
    # Test login with new password
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": test_user["email"],
            "password": new_password
        }
    )
    assert login_response.status_code == 200
