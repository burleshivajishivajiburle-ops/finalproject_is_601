import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User

client = TestClient(app)

def test_get_current_user_profile(db_session, test_user):
    """Test getting current user profile"""
    # Create access token
    token = User.create_access_token({"sub": str(test_user.id)})
    
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["first_name"] == test_user.first_name
    assert data["last_name"] == test_user.last_name

def test_get_current_user_profile_unauthorized():
    """Test getting profile without authentication"""
    response = client.get("/users/me")
    
    assert response.status_code == 401

def test_update_user_profile_success(db_session, test_user):
    """Test successful profile update"""
    token = User.create_access_token({"sub": str(test_user.id)})
    
    update_data = {
        "first_name": "UpdatedFirst",
        "last_name": "UpdatedLast"
    }
    
    response = client.put(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "UpdatedFirst"
    assert data["last_name"] == "UpdatedLast"

def test_update_user_profile_username(db_session, test_user):
    """Test updating username"""
    token = User.create_access_token({"sub": str(test_user.id)})
    
    update_data = {"username": "newusername123"}
    
    response = client.put(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newusername123"

def test_update_user_profile_email(db_session, test_user):
    """Test updating email"""
    token = User.create_access_token({"sub": str(test_user.id)})
    
    update_data = {"email": "newemail@example.com"}
    
    response = client.put(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newemail@example.com"

def test_update_user_profile_duplicate_username(db_session):
    """Test updating to existing username fails"""
    # Create first user
    user1_data = {
        "first_name": "User",
        "last_name": "One",
        "email": "user1@example.com",
        "username": "user1",
        "password": "Password123!"
    }
    user1 = User.register(db_session, user1_data)
    db_session.commit()
    
    # Create second user
    user2_data = {
        "first_name": "User",
        "last_name": "Two",
        "email": "user2@example.com",
        "username": "user2",
        "password": "Password123!"
    }
    user2 = User.register(db_session, user2_data)
    db_session.commit()
    
    token = User.create_access_token({"sub": str(user2.id)})
    
    response = client.put(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "user1"}
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_update_user_profile_no_fields(db_session, test_user):
    """Test updating with no fields returns error"""
    token = User.create_access_token({"sub": str(test_user.id)})
    
    response = client.put(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={}
    )
    
    assert response.status_code == 400
    assert "No fields provided" in response.json()["detail"]

def test_change_password_success(db_session, test_user):
    """Test successful password change"""
    token = User.create_access_token({"sub": str(test_user.id)})
    
    password_data = {
        "current_password": "TestPass123",
        "new_password": "NewPass456",
        "confirm_new_password": "NewPass456"
    }
    
    response = client.post(
        "/users/me/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json=password_data
    )
    
    assert response.status_code == 200
    assert "success" in response.json()["message"].lower()

def test_change_password_wrong_current(db_session, test_user):
    """Test password change with wrong current password"""
    token = User.create_access_token({"sub": str(test_user.id)})
    
    password_data = {
        "current_password": "WrongPassword",
        "new_password": "NewPass456",
        "confirm_new_password": "NewPass456"
    }
    
    response = client.post(
        "/users/me/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json=password_data
    )
    
    assert response.status_code == 400
    assert "incorrect" in response.json()["detail"].lower()

def test_change_password_mismatch(db_session, test_user):
    """Test password change with mismatched new passwords"""
    token = User.create_access_token({"sub": str(test_user.id)})
    
    password_data = {
        "current_password": "TestPass123",
        "new_password": "NewPass456",
        "confirm_new_password": "DifferentPass789"
    }
    
    response = client.post(
        "/users/me/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json=password_data
    )
    
    assert response.status_code == 422  # Validation error from Pydantic

def test_change_password_same_as_old(db_session, test_user):
    """Test password change with same password"""
    token = User.create_access_token({"sub": str(test_user.id)})
    
    password_data = {
        "current_password": "TestPass123",
        "new_password": "TestPass123",
        "confirm_new_password": "TestPass123"
    }
    
    response = client.post(
        "/users/me/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json=password_data
    )
    
    assert response.status_code == 422  # Validation error from Pydantic

def test_change_password_too_short(db_session, test_user):
    """Test password change with short password"""
    token = User.create_access_token({"sub": str(test_user.id)})
    
    password_data = {
        "current_password": "TestPass123",
        "new_password": "short",
        "confirm_new_password": "short"
    }
    
    response = client.post(
        "/users/me/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json=password_data
    )
    
    assert response.status_code == 400 or response.status_code == 422

def test_create_calculation_exponentiation(db_session, test_user):
    """Test creating exponentiation calculation"""
    token = User.create_access_token({"sub": str(test_user.id)})
    
    calc_data = {
        "type": "exponentiation",
        "inputs": [2, 3]
    }
    
    response = client.post(
        "/calculations",
        headers={"Authorization": f"Bearer {token}"},
        json=calc_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "exponentiation"
    assert data["result"] == 8

def test_create_calculation_modulus(db_session, test_user):
    """Test creating modulus calculation"""
    token = User.create_access_token({"sub": str(test_user.id)})
    
    calc_data = {
        "type": "modulus",
        "inputs": [10, 3]
    }
    
    response = client.post(
        "/calculations",
        headers={"Authorization": f"Bearer {token}"},
        json=calc_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "modulus"
    assert data["result"] == 1

def test_create_calculation_modulus_by_zero(db_session, test_user):
    """Test creating modulus calculation with zero fails"""
    token = User.create_access_token({"sub": str(test_user.id)})
    
    calc_data = {
        "type": "modulus",
        "inputs": [10, 0]
    }
    
    response = client.post(
        "/calculations",
        headers={"Authorization": f"Bearer {token}"},
        json=calc_data
    )
    
    assert response.status_code == 400
    assert "zero" in response.json()["detail"].lower()

def test_create_calculation_exponentiation_multiple(db_session, test_user):
    """Test creating exponentiation with multiple inputs"""
    token = User.create_access_token({"sub": str(test_user.id)})
    
    calc_data = {
        "type": "exponentiation",
        "inputs": [2, 3, 2]
    }
    
    response = client.post(
        "/calculations",
        headers={"Authorization": f"Bearer {token}"},
        json=calc_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["result"] == 64  # (2^3)^2 = 64
