import re
from typing import Optional, Dict, Any, Annotated
from urllib.parse import urlparse
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, validator, constr, confloat, HttpUrl
from datetime import datetime, timedelta

class Validator:
    """Core validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address using RFC standards"""
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False

    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password meets security requirements"""
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'[0-9]', password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        return True

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format and accessibility"""
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate international phone number format"""
        pattern = r'^\+?[1-9]\d{1,14}$'  # E.164 standard
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_price(price: float) -> bool:
        """Validate price is positive and reasonable"""
        return 0 < price < 1_000_000  # $1M upper limit

    @staticmethod
    def validate_date_range(start: datetime, end: datetime) -> bool:
        """Validate date range is logical"""
        return start < end

class ProductSchema(BaseModel):
    """Pydantic schema for product validation"""
    name: Annotated[str, constr(min_length=2, max_length=256)]
    url: HttpUrl
    target_price: Annotated[float, confloat(gt=0, lt=1_000_000)]
    description: Optional[Annotated[str, constr(max_length=2000)]] = None
    currency: Annotated[str, constr(min_length=3, max_length=3)] = "USD"

    @validator('url')
    def validate_product_url(cls, v):
        if not any(domain in str(v) for domain in ['amazon', 'walmart', 'ebay']):
            raise ValueError("Only Amazon, Walmart and eBay products are supported")
        return v

    @validator('currency')
    def validate_currency(cls, v):
        if v.upper() != v:
            return v.upper()
        return v

class UserSchema(BaseModel):
    """Pydantic schema for user validation"""
    email: str
    password: Annotated[str, constr(min_length=8)]
    full_name: Optional[Annotated[str, constr(max_length=100)]] = None
    phone: Optional[str] = None
    notification_pref: Annotated[str, constr(regex='^(email|sms|push)$')] = "email"

    @validator('email')
    def validate_email(cls, v):
        if not Validator.validate_email(v):
            raise ValueError("Invalid email format")
        return v.lower()

    @validator('password')
    def validate_password_strength(cls, v):
        if not Validator.validate_password(v):
            raise ValueError(
                "Password must contain at least 8 characters with "
                "uppercase, lowercase, numbers and special characters"
            )
        return v

    @validator('phone', pre=True, always=True)
    def validate_phone_number(cls, v, values):
        if v is None and values.get('notification_pref') == 'sms':
            raise ValueError("Phone number required for SMS notifications")
        if v and not Validator.validate_phone(v):
            raise ValueError("Invalid phone number format")
        return v

class PriceHistorySchema(BaseModel):
    """Pydantic schema for price history validation"""
    price: Annotated[float, confloat(gt=0)]
    currency: Annotated[str, constr(min_length=3, max_length=3)] = "USD"
    availability: bool = True
    in_stock: bool = True
    source: Annotated[str, constr(max_length=50)]

class AlertSchema(BaseModel):
    """Pydantic schema for price alert validation"""
    product_id: int
    target_price: Annotated[float, confloat(gt=0)]
    notification_type: Annotated[str, constr(regex='^(email|sms|push)$')] = "email"
    active: bool = True

def validate_input(data: Dict[str, Any], schema: BaseModel) -> Dict[str, Any]:
    """Generic input validation using Pydantic schemas"""
    try:
        validated = schema(**data)
        return validated.dict(exclude_unset=True)
    except Exception as e:
        from app.utils.exceptions import ValidationError
        raise ValidationError({"detail": str(e), "errors": e.errors() if hasattr(e, 'errors') else None})

def validate_ecommerce_url(url: str) -> str:
    """Specialized URL validation for supported e-commerce sites"""
    if not Validator.validate_url(url):
        raise ValueError("Invalid URL format")
    
    domain = urlparse(url).netloc.lower()
    supported = ['amazon.', 'walmart.', 'ebay.', 'bestbuy.', 'target.']
    
    if not any(s in domain for s in supported):
        raise ValueError(f"Unsupported e-commerce site. Supported: {', '.join(s.replace('.', '') for s in supported)}")
    
    return url

def sanitize_input(input_str: str) -> str:
    """Basic input sanitization to prevent XSS"""
    if not input_str:
        return input_str
        
    return re.sub(r'<[^>]*>', '', input_str).strip()

def validate_date_format(date_str: str, fmt: str = "%Y-%m-%d") -> bool:
    """Validate date string format"""
    try:
        datetime.strptime(date_str, fmt)
        return True
    except ValueError:
        return False