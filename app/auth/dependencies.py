from datetime import datetime
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse
from app.models.user import User
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> UserResponse:
    """
    Dependency to get the current user from the JWT token without a database lookup.
    This function supports two types of payloads:
      - A full payload as a dict containing user info.
      - A minimal payload, either as a dict with only a 'sub' key or directly as a UUID.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = User.verify_token(token)
    if token_data is None:
        raise credentials_exception

    try:
        # If the token data is a dictionary:
        if isinstance(token_data, dict):
            # If the payload contains a full set of user fields, use them directly.
            if "username" in token_data:
                return UserResponse(**token_data)
            # Otherwise, assume it is a minimal payload with only the 'sub' key.
            elif "sub" in token_data:
                return UserResponse(
                    id=token_data["sub"],
                    username="unknown",
                    email="unknown@example.com",
                    first_name="Unknown",
                    last_name="User",
                    is_active=True,
                    is_verified=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            else:
                raise credentials_exception

        # If the token data is directly a UUID (minimal payload):
        elif isinstance(token_data, UUID):
            return UserResponse(
                id=token_data,
                username="unknown",
                email="unknown@example.com",
                first_name="Unknown",
                last_name="User",
                is_active=True,
                is_verified=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        else:
            raise credentials_exception

    except Exception:
        raise credentials_exception

def get_current_user_from_db(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current user from the database using JWT token.
    Returns the actual User model instance, not just a UserResponse.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = User.verify_token(token)
    if token_data is None:
        raise credentials_exception

    try:
        # Extract user ID from token
        user_id = None
        if isinstance(token_data, dict):
            if "sub" in token_data:
                user_id = UUID(token_data["sub"]) if isinstance(token_data["sub"], str) else token_data["sub"]
            elif "id" in token_data:
                user_id = UUID(token_data["id"]) if isinstance(token_data["id"], str) else token_data["id"]
        elif isinstance(token_data, UUID):
            user_id = token_data
        
        if user_id is None:
            raise credentials_exception
        
        # Load user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
        
        return user

    except Exception:
        raise credentials_exception

def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Dependency to ensure that the current user is active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def get_current_active_user_from_db(
    current_user: User = Depends(get_current_user_from_db)
) -> User:
    """
    Dependency to ensure that the current user from database is active.
    Returns the actual User model instance.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
