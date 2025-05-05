from datetime import datetime
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Float, 
    DateTime, 
    ForeignKey,
    Boolean,
    Text
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(512), unique=True, nullable=False)
    image_url = Column(String(512), nullable=True)
    current_price = Column(Float, nullable=True)
    original_price = Column(Float, nullable=True)
    target_price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    is_active = Column(Boolean(), default=True)
    last_checked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="products")
    price_history = relationship("PriceHistory", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name[:20]}...)>"