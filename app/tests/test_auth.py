"""
Tests for authentication endpoints.
"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app import crud


def test_register_user(client: TestClient, db: Session):
    """Test user registration."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client: TestClient, test_user: dict):
    """Test registration with duplicate email fails."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": test_user["email"],
            "password": "password123",
            "full_name": "Duplicate User"
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_success(client: TestClient, test_user: dict):
    """Test successful login."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient, test_user: dict):
    """Test login with invalid credentials."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": test_user["email"],
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_refresh_token(client: TestClient, test_user: dict):
    """Test refresh token endpoint."""
    # First login to get tokens
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    tokens = login_response.json()
    
    # Use refresh token to get new tokens
    response = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_with_access_token_fails(client: TestClient, test_user: dict):
    """Test that using access token for refresh fails."""
    # Login to get tokens
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    tokens = login_response.json()
    
    # Try to use access token for refresh (should fail)
    response = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": tokens["access_token"]}
    )
    assert response.status_code == 401
    assert "Invalid token type" in response.json()["detail"]


def test_test_token(client: TestClient, auth_headers: dict):
    """Test token validation endpoint."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/test-token",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "id" in data
