from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.product import Product

class PriceHistoryBase(BaseModel):
    price: float = Field(..., gt=0, example=99.99)
    currency: str = Field("USD", max_length=3, example="USD")
    availability: bool = True
    in_stock: bool = True
    source: Optional[str] = Field(None, example="amazon")

class PriceHistoryCreate(PriceHistoryBase):
    product_id: int

class PriceHistoryUpdate(PriceHistoryBase):
    pass

class PriceHistoryInDBBase(PriceHistoryBase):
    id: int
    date: datetime
    product_id: int

    class Config:
        orm_mode = True

class PriceHistory(PriceHistoryInDBBase):
    product: Product

class PriceHistoryInDB(PriceHistoryInDBBase):
    pass

class PriceTrendAnalysis(BaseModel):
    product_id: int
    current_price: float
    average_price: float
    min_price: float
    max_price: float
    price_change_7d: Optional[float] = None
    price_change_30d: Optional[float] = None
    last_updated: datetime
    