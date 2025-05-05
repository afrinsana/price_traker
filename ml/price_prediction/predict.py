import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta

class PricePredictor:
    def __init__(self, model_path: str):
        self.model = joblib.load(model_path)
        
    def create_future_features(self, last_date: datetime, days: int = 7) -> pd.DataFrame:
        """Generate feature dataframe for future dates"""
        future_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=days
        )
        
        features = pd.DataFrame({
            'date': future_dates,
            'day_of_week': future_dates.dayofweek,
            'day_of_month': future_dates.day,
            'month': future_dates.month
        }).set_index('date')
        
        # Add simulated lag features (would be improved with real data)
        features['price_lag1'] = np.random.normal(100, 10, days)
        features['price_lag7'] = np.random.normal(100, 15, days)
        features['rolling_avg'] = np.linspace(95, 105, days)
        
        return features

    def predict(self, last_known_data: dict, days: int = 7) -> list:
        """Generate price predictions"""
        last_date = pd.to_datetime(last_known_data['date'])
        future_features = self.create_future_features(last_date, days)
        
        predictions = self.model.predict(future_features)
        
        return [{
            "date": date.isoformat(),
            "predicted_price": float(price),
            "confidence": 0.85  # Placeholder for actual confidence
        } for date, price in zip(future_features.index, predictions)]
    