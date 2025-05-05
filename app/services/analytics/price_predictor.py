import numpy as np
import pandas as pd
from typing import Dict, Optional, List
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBRegressor
from prophet import Prophet
import joblib
import os

from app.db.session import SessionLocal
from app.core.logging import logger

class PricePredictor:
    def __init__(self):
        self.models_dir = "data/models"
        os.makedirs(self.models_dir, exist_ok=True)

    async def train_model(self, product_id: int, price_history: List[Dict]) -> bool:
        """Train price prediction model for a product"""
        try:
            if len(price_history) < 30:
                logger.warning(f"Insufficient data for product {product_id}")
                return False

            df = pd.DataFrame(price_history)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            # Feature engineering
            df['day_of_week'] = df['date'].dt.dayofweek
            df['day_of_month'] = df['date'].dt.day
            df['month'] = df['date'].dt.month
            df['price_change'] = df['price'].pct_change()
            df['rolling_avg'] = df['price'].rolling(7).mean()

            # Train multiple models
            models = {
                'xgboost': XGBRegressor(),
                'prophet': Prophet(),
                'gradient_boosting': GradientBoostingRegressor()
            }

            best_score = -1
            best_model = None

            for name, model in models.items():
                if name == 'prophet':
                    prophet_df = df.rename(columns={'date': 'ds', 'price': 'y'})
                    model.fit(prophet_df[['ds', 'y']])
                else:
                    X = df.drop(['price', 'date'], axis=1)
                    y = df['price']
                    model.fit(X, y)

                # Evaluate model (simplified)
                score = self._evaluate_model(model, df)
                if score > best_score:
                    best_score = score
                    best_model = model

            # Save the best model
            model_path = os.path.join(self.models_dir, f"{product_id}.joblib")
            joblib.dump(best_model, model_path)
            return True

        except Exception as e:
            logger.error(f"Training failed for product {product_id}: {str(e)}")
            return False

    async def predict(self, product_id: int, days: int = 7) -> Optional[Dict]:
        """Predict future prices for a product"""
        try:
            model_path = os.path.join(self.models_dir, f"{product_id}.joblib")
            if not os.path.exists(model_path):
                return None

            model = joblib.load(model_path)
            predictions = []

            if isinstance(model, Prophet):
                future = model.make_future_dataframe(periods=days)
                forecast = model.predict(future)
                predictions = forecast[['ds', 'yhat']].tail(days).to_dict('records')
            else:
                # Create future features
                last_date = pd.Timestamp.now()
                future_dates = pd.date_range(start=last_date, periods=days)
                future_features = pd.DataFrame({
                    'date': future_dates,
                    'day_of_week': future_dates.dayofweek,
                    'day_of_month': future_dates.day,
                    'month': future_dates.month
                })
                # Add simulated features
                future_features['price_change'] = np.random.uniform(-0.05, 0.05, days)
                future_features['rolling_avg'] = np.linspace(0.9, 1.1, days)
                
                predictions = model.predict(future_features.drop('date', axis=1))
                predictions = [
                    {'date': d.date(), 'predicted_price': float(p)}
                    for d, p in zip(future_dates, predictions)
                ]

            return {
                'product_id': product_id,
                'predictions': predictions,
                'confidence': self._calculate_confidence(predictions)
            }

        except Exception as e:
            logger.error(f"Prediction failed for product {product_id}: {str(e)}")
            return None

    # ... (helper methods for evaluation and confidence calculation)