from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.crud.user import user_crud
from app.db.session import get_db
from app.schemas.token import Token
from app.schemas.user import User

router = APIRouter()

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """OAuth2 compatible token login"""
    user = user_crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "expires_at": (
            datetime.utcnow() + access_token_expires
        ).isoformat()
    }

@router.post("/test-token", response_model=User)
def test_token(
    current_user: User = Depends(security.get_current_active_user)
):
    """Test access token validity"""
    return current_user

@router.post("/refresh-token", response_model=Token)
def refresh_token(
    current_user: User = Depends(security.get_current_active_user)
):
    """Refresh access token"""
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return {
        "access_token": security.create_access_token(
            current_user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "expires_at": (
            datetime.utcnow() + access_token_expires
        ).isoformat()
    }
