from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, 
    users, 
    products, 
    alerts,
    price_history
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(
    price_history.router, 
    prefix="/price-history", 
    tags=["price-history"]
)
from .endpoints import predict  # Add this line

api_router.include_router(predict.router, prefix="/predict", tags=["predictions"])