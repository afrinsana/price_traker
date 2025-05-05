from fastapi import APIRouter, Depends
from app.services.analytics.price_predictor import PricePredictor
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/predict/{product_id}")
def predict_future_prices(
    product_id: int,
    days: int = 7,
    db: Session = Depends(get_db)
):
    predictor = PricePredictor(db)
    predictor = PricePredictor()
    return predictor.predict(product_id, days)