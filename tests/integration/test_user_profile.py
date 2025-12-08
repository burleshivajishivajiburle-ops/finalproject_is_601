import pytest
from app.models.user import User

def test_update_profile_username(db_session, test_user):
    """Test updating user profile username"""
    new_username = "updated_username"
    
    test_user.update_profile(db_session, {"username": new_username})
    db_session.commit()
    db_session.refresh(test_user)
    
    assert test_user.username == new_username
    assert test_user.updated_at is not None

def test_update_profile_email(db_session, test_user):
    """Test updating user profile email"""
    from faker import Faker
    fake = Faker()
    new_email = fake.unique.email()
    
    test_user.update_profile(db_session, {"email": new_email})
    db_session.commit()
    db_session.refresh(test_user)
    
    assert test_user.email == new_email

def test_update_profile_names(db_session, test_user):
    """Test updating user first and last names"""
    test_user.update_profile(db_session, {
        "first_name": "UpdatedFirst",
        "last_name": "UpdatedLast"
    })
    db_session.commit()
    db_session.refresh(test_user)
    
    assert test_user.first_name == "UpdatedFirst"
    assert test_user.last_name == "UpdatedLast"

def test_update_profile_duplicate_username(db_session):
    """Test that updating to existing username raises error"""
    # Import faker to generate unique values
    from faker import Faker
    fake = Faker()
    
    # Create first user
    user1_data = {
        "first_name": "User",
        "last_name": "One",
        "email": fake.unique.email(),
        "username": fake.unique.user_name(),
        "password": "Password123!"
    }
    user1 = User.register(db_session, user1_data)
    db_session.commit()
    
    # Create second user
    user2_data = {
        "first_name": "User",
        "last_name": "Two",
        "email": fake.unique.email(),
        "username": fake.unique.user_name(),
        "password": "Password123!"
    }
    user2 = User.register(db_session, user2_data)
    db_session.commit()
    
    # Try to update user2's username to user1's username
    with pytest.raises(ValueError, match="Username already exists"):
        user2.update_profile(db_session, {"username": user1.username})

def test_update_profile_duplicate_email(db_session):
    """Test that updating to existing email raises error"""
    # Import faker to generate unique values
    from faker import Faker
    fake = Faker()
    
    # Create first user
    user1_data = {
        "first_name": "User",
        "last_name": "One",
        "email": fake.unique.email(),
        "username": fake.unique.user_name(),
        "password": "Password123!"
    }
    user1 = User.register(db_session, user1_data)
    db_session.commit()
    
    # Create second user
    user2_data = {
        "first_name": "User",
        "last_name": "Two",
        "email": fake.unique.email(),
        "username": fake.unique.user_name(),
        "password": "Password123!"
    }
    user2 = User.register(db_session, user2_data)
    db_session.commit()
    
    # Try to update user2's email to user1's email
    with pytest.raises(ValueError, match="Email already exists"):
        user2.update_profile(db_session, {"email": user1.email})

def test_update_profile_same_username(db_session, test_user):
    """Test that updating to same username works"""
    original_username = test_user.username
    
    test_user.update_profile(db_session, {"username": original_username})
    db_session.commit()
    db_session.refresh(test_user)
    
    assert test_user.username == original_username

def test_update_profile_multiple_fields(db_session, test_user):
    """Test updating multiple profile fields at once"""
    from faker import Faker
    fake = Faker()
    
    unique_username = fake.unique.user_name()
    unique_email = fake.unique.email()
    
    update_data = {
        "first_name": "NewFirst",
        "last_name": "NewLast",
        "username": unique_username,
        "email": unique_email
    }
    
    test_user.update_profile(db_session, update_data)
    db_session.commit()
    db_session.refresh(test_user)
    
    assert test_user.first_name == "NewFirst"
    assert test_user.last_name == "NewLast"
    assert test_user.username == unique_username
    assert test_user.email == unique_email

def test_change_password_success(db_session, test_user):
    """Test successful password change"""
    old_password = "TestPass123"
    new_password = "NewPass456"
    
    # Store old hashed password for comparison
    old_hashed = test_user.password
    
    test_user.change_password(db_session, old_password, new_password)
    db_session.commit()
    db_session.refresh(test_user)
    
    # Verify old password no longer works
    assert not test_user.verify_password(old_password)
    
    # Verify new password works
    assert test_user.verify_password(new_password)
    
    # Verify password hash changed
    assert test_user.password != old_hashed

def test_change_password_wrong_old_password(db_session, test_user):
    """Test password change fails with wrong old password"""
    with pytest.raises(ValueError, match="Current password is incorrect"):
        test_user.change_password(db_session, "WrongPassword", "NewPass123")

def test_change_password_too_short(db_session, test_user):
    """Test password change fails with short new password"""
    with pytest.raises(ValueError, match="New password must be at least 6 characters long"):
        test_user.change_password(db_session, "TestPass123", "short")

def test_change_password_same_as_old(db_session, test_user):
    """Test password change fails when new password is same as old"""
    old_password = "TestPass123"
    
    with pytest.raises(ValueError, match="New password must be different from current password"):
        test_user.change_password(db_session, old_password, old_password)

def test_change_password_updates_timestamp(db_session, test_user):
    """Test that password change updates the updated_at timestamp"""
    original_updated_at = test_user.updated_at
    
    # Small delay to ensure timestamp changes
    import time
    time.sleep(0.1)
    
    test_user.change_password(db_session, "TestPass123", "NewPass456")
    db_session.commit()
    db_session.refresh(test_user)
    
    assert test_user.updated_at > original_updated_at

def test_change_password_empty_new_password(db_session, test_user):
    """Test password change fails with empty new password"""
    with pytest.raises(ValueError, match="New password must be at least 6 characters long"):
        test_user.change_password(db_session, "TestPass123", "")

def test_update_profile_empty_fields(db_session, test_user):
    """Test updating profile with empty dict does nothing"""
    original_first_name = test_user.first_name
    original_last_name = test_user.last_name
    
    test_user.update_profile(db_session, {})
    db_session.commit()
    db_session.refresh(test_user)
    
    assert test_user.first_name == original_first_name
    assert test_user.last_name == original_last_name

def test_update_profile_partial_update(db_session, test_user):
    """Test updating only some profile fields"""
    original_username = test_user.username
    original_email = test_user.email
    
    test_user.update_profile(db_session, {"first_name": "PartialUpdate"})
    db_session.commit()
    db_session.refresh(test_user)
    
    assert test_user.first_name == "PartialUpdate"
    assert test_user.username == original_username
    assert test_user.email == original_email
