from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, HttpUrl, validator

from app.schemas.price_history import PriceHistory
from app.schemas.user import User

class ProductBase(BaseModel):
    name: str = Field(..., max_length=256, example="Wireless Headphones")
    description: Optional[str] = Field(None, example="Noise cancelling wireless headphones")
    url: HttpUrl = Field(..., example="https://example.com/product/123")
    image_url: Optional[HttpUrl] = Field(None, example="https://example.com/images/123.jpg")
    target_price: float = Field(..., gt=0, example=99.99)
    currency: str = Field("USD", max_length=3, example="USD")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = Field(None, max_length=256)
    description: Optional[str] = None
    url: Optional[HttpUrl] = None
    image_url: Optional[HttpUrl] = None
    target_price: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=3)

class ProductInDBBase(ProductBase):
    id: int
    current_price: Optional[float] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    last_checked: Optional[datetime] = None
    user_id: int

    class Config:
        orm_mode = True

class Product(ProductInDBBase):
    price_history: List[PriceHistory] = []
    user: User

class ProductInDB(ProductInDBBase):
    pass

class ProductPriceUpdate(BaseModel):
    current_price: float = Field(..., gt=0)
    original_price: Optional[float] = Field(None, gt=0)
    currency: str = Field("USD", max_length=3)
    availability: bool = True
    in_stock: bool = True

    @validator('original_price')
    def validate_prices(cls, v, values):
        if v is not None and 'current_price' in values and v < values['current_price']:
            raise ValueError("Original price must be greater than or equal to current price")
        return v