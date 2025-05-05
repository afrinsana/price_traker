import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

from celery import shared_task
from sqlalchemy.orm import Session
import pandas as pd

from app.db.session import SessionLocal
from app.db.models import Product, PriceHistory, Alert
from app.services.scraper.factory import ScraperFactory
from app.services.notifications.email import EmailNotifier
from app.services.notifications.sms import SMSNotifier
from app.services.analytics.price_predictor import PricePredictor
from app.core.logging import logger

@shared_task(bind=True, max_retries=3)
def check_product_price(self, product_id: int) -> Optional[Dict]:
    """
    Enhanced price check task with BI/ML features:
    - Tracks price volatility metrics
    - Logs statistical features for BI analysis
    - Triggers ML model retraining if significant drift detected
    """
    db = SessionLocal()
    try:
        # 1. Get product and scrape current price
        product = db.query(Product).get(product_id)
        if not product:
            logger.error(f"Product {product_id} not found")
            return None

        scraper = ScraperFactory.get_scraper(product.url)
        if not scraper:
            logger.error(f"No scraper for product {product_id}")
            return None

        product_data = scraper.scrape(product.url)
        if not product_data or 'price' not in product_data:
            logger.error(f"Failed to scrape product {product_id}")
            return None

        current_price = product_data['price']
        
        # 2. Save price history with BI metadata
        price_history = PriceHistory(
            product_id=product.id,
            price=current_price,
            date=datetime.now(),
            availability=product_data.get('availability', True),
            source=product_data.get('source', 'web')
        )
        db.add(price_history)
        
        # 3. Calculate BI metrics
        history_df = pd.read_sql(
            f"SELECT date, price FROM price_history WHERE product_id = {product_id}",
            db.connection()
        )
        stats = {
            'current_price': current_price,
            '7d_avg': history_df['price'].rolling(7).mean().iloc[-1],
            'volatility': history_df['price'].std(),
            'min_7d': history_df['price'].rolling(7).min().iloc[-1],
            'max_7d': history_df['price'].rolling(7).max().iloc[-1]
        }
        
        # 4. Check for significant price drift (BI Alert)
        price_drift = abs(current_price - stats['7d_avg']) / stats['7d_avg']
        if price_drift > 0.15:  # 15% change
            logger.warning(f"Significant price drift detected: {price_drift:.2%}")
            trigger_ml_retrain.delay(product_id)
        
        # 5. Update product and check alerts
        product.current_price = current_price
        product.last_checked = datetime.now()
        db.commit()
        
        check_price_alerts(product_id, current_price, db)
        
        return {
            'product_id': product_id,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Price check failed for product {product_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()

@shared_task
def trigger_ml_retrain(product_id: int):
    """Trigger ML model retraining if price patterns change significantly"""
    from ml.price_prediction.train_model import PricePredictorTrainer
    trainer = PricePredictorTrainer()
    trainer.train(product_id)

def check_price_alerts(product_id: int, current_price: float, db: Session):
    """Check if price meets any alert conditions"""
    alerts = db.query(Alert).filter(
        Alert.product_id == product_id,
        Alert.active == True
    ).all()
    
    for alert in alerts:
        if current_price <= alert.target_price:
            send_alert_notification(alert, current_price)

def send_alert_notification(alert: Alert, current_price: float):
    """Send alert via user's preferred channel"""
    notifier = EmailNotifier() if alert.notification_type == 'email' else SMSNotifier()
    notifier.send_price_alert(
        recipient=alert.user.email,
        product_name=alert.product.name,
        current_price=current_price,
        target_price=alert.target_price,
        product_url=alert.product.url
    )
    