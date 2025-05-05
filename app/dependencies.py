from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from pydantic import ValidationError

from app.core.config import settings
from app.core.security import oauth2_scheme
from app.core.logging import logger
from app.db.session import SessionLocal
from app.schemas.user import TokenPayload
from app.crud.user import user_crud
from app.services.scraper.factory import ScraperFactory
from app.services.notification.email import EmailNotifier
from app.services.analytics.price_predictor import PricePredictor
from app.services.blockchain.price_oracle import PriceOracle

def get_db() -> Generator:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Dependency for getting current authenticated user"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user = user_crud.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

def get_scraper_factory() -> ScraperFactory:
    """Dependency for getting scraper factory"""
    return ScraperFactory()

def get_email_notifier() -> EmailNotifier:
    """Dependency for getting email notifier"""
    return EmailNotifier()

def get_price_predictor() -> PricePredictor:
    """Dependency for getting price predictor"""
    return PricePredictor()

def get_price_oracle() -> PriceOracle:
    """Dependency for getting blockchain price oracle"""
    return PriceOracle()

def get_admin_user(
    current_user: dict = Depends(get_current_user)
):
    """Dependency for checking admin privileges"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

# Rate limiting dependency (example using Redis)
def rate_limit(
    key: str = "global",
    limit: int = 100,
    window: int = 60  # seconds
):
    """Dependency for rate limiting"""
    # In a real implementation, this would check Redis
    # For simplicity, we're just returning a pass-through dependency
    def inner():
        return True
    return Depends(inner)
