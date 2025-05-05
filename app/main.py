from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.background import BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.api.v1.routers import api_router
from config import Config, settings
from api.core.logging import get_logger
from app.db.session import SessionLocal

# Initialize logger
logger = get_logger(__name__)
from app.db.models import Product
from app.schemas.product import ProductCreate, ProductOut
from api.crud.products import product_crud
from app.services.scraper.factory import ScraperFactory
from tasks.price_checks import check_product_price
from app.dependencies import get_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Next-Gen Price Tracker with AI and Blockchain",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS settings
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize application services on startup"""
    logger.info("Starting up Price Tracker...")
    # Initialize blockchain connection
    # Initialize AI models
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup application services on shutdown"""
    logger.info("Shutting down Price Tracker...")

@app.get("/health", tags=["health"])
def health_check():
    """Endpoint for health checks"""
    return {"status": "healthy"}

@app.post("/products/", response_model=ProductOut, tags=["products"])
def create_product(
    product: ProductCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new product to track"""
    try:
        # First check if product already exists
        db_product = product_crud.get_by_url(db, url=product.url)
        if db_product:
            raise HTTPException(status_code=400, detail="Product already being tracked")
        
        # Create the product
        db_product = product_crud.create(db, obj_in=product)
        
        # Immediately trigger a price check
        background_tasks.add_task(check_product_price.delay, db_product.id)
        
        return db_product
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}/check", tags=["products"])
def trigger_price_check(
    product_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Manually trigger a price check for a product"""
    product = product_crud.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    background_tasks.add_task(check_product_price.delay, product_id)
    return {"message": "Price check initiated"}

@app.get("/products/{product_id}/predict", tags=["products"])
def predict_price(
    product_id: int,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get price prediction for a product"""
    product = product_crud.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # In a real implementation, this would call the PricePredictor service
    return {
        "product_id": product_id,
        "predictions": [
            {"date": "2023-01-01", "predicted_price": 49.99, "confidence": 0.85},
            {"date": "2023-01-02", "predicted_price": 48.50, "confidence": 0.82}
        ]
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )