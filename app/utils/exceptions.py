from fastapi import HTTPException, status
from typing import Any, Dict, Optional
from pydantic import BaseModel

class APIError(BaseModel):
    """Base schema for API error responses"""
    detail: str
    code: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class PriceTrackerException(HTTPException):
    """Base exception for Price Tracker application"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers
        )
        self.code = code
        self.meta = meta

    def to_schema(self) -> APIError:
        """Convert exception to APIError schema"""
        return APIError(
            detail=self.detail,
            code=self.code,
            meta=self.meta
        )

# Authentication & Authorization Exceptions
class UnauthorizedError(PriceTrackerException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code="unauthorized"
        )

class ForbiddenError(PriceTrackerException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            code="forbidden"
        )

class InvalidCredentialsError(PriceTrackerException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            code="invalid_credentials"
        )

# Resource Exceptions
class NotFoundError(PriceTrackerException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found",
            code="not_found"
        )

class AlreadyExistsError(PriceTrackerException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource} already exists",
            code="already_exists"
        )

# Validation Exceptions
class ValidationError(PriceTrackerException):
    def __init__(self, errors: Dict[str, Any]):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Validation error",
            code="validation_error",
            meta={"errors": errors}
        )

# Business Logic Exceptions
class ScrapingError(PriceTrackerException):
    def __init__(self, platform: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail or f"Failed to scrape {platform}",
            code="scraping_error",
            meta={"platform": platform}
        )

class NotificationError(PriceTrackerException):
    def __init__(self, channel: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail or f"Failed to send {channel} notification",
            code="notification_error",
            meta={"channel": channel}
        )

class PredictionError(PriceTrackerException):
    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail or "Failed to generate price prediction",
            code="prediction_error"
        )

# Rate Limiting
class RateLimitError(PriceTrackerException):
    def __init__(self, retry_after: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
            code="rate_limit_exceeded",
            headers={"Retry-After": str(retry_after)}
        )

# Database Exceptions
class DatabaseError(PriceTrackerException):
    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail or "Database operation failed",
            code="database_error"
        )

# External Service Exceptions
class ExternalServiceError(PriceTrackerException):
    def __init__(self, service: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail or f"External service error: {service}",
            code="external_service_error",
            meta={"service": service}
        )

# Custom Exception Handler
def handle_price_tracker_exception(exc: PriceTrackerException):
    """Convert PriceTrackerException to FastAPI response"""
    from fastapi.responses import JSONResponse
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_schema().dict(),
        headers=exc.headers
    )