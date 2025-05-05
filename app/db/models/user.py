from datetime import datetime
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Boolean, 
    DateTime,
    LargeBinary
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    email_verified = Column(Boolean(), default=False)
    notification_pref = Column(String(10), default="email")  # email, sms, push
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    profile_image = Column(LargeBinary, nullable=True)

    # Relationships
    products = relationship("Product", back_populates="user")
    alerts = relationship("Alert", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"