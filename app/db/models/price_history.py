from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    price = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    currency = Column(String(3), default="USD")
    availability = Column(Boolean, default=True)
    in_stock = Column(Boolean, default=True)
    source = Column(String(50), nullable=True)  # website, api, etc.

    # Relationships
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="price_history")

    def __repr__(self):
        return f"<PriceHistory(id={self.id}, price={self.price}, date={self.date})>"