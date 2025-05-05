from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.crud.base import CRUDBase
from app.db.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def get_by_url(self, db: Session, url: str) -> Optional[Product]:
        """Get product by URL"""
        return db.query(Product).filter(Product.url == url).first()

    def get_multi_by_owner(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """Get multiple products owned by a user"""
        return (
            db.query(Product)
            .filter(Product.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_products(self, db: Session) -> List[Product]:
        """Get all active products"""
        return db.query(Product).filter(Product.is_active == True).all()

    def search(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """Search products by name or description"""
        search = f"%{query}%"
        return (
            db.query(Product)
            .filter(
                or_(
                    Product.name.ilike(search),
                    Product.description.ilike(search)
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_price_drops(
        self, db: Session, *, threshold: float = 0.1, days: int = 7
    ) -> List[Product]:
        """Get products with significant price drops"""
        # This would be more complex in a real implementation
        # Joining with price_history table and comparing recent prices
        return db.query(Product).limit(10).all()

product_crud = CRUDProduct(Product)
