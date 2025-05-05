import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
from datetime import datetime
from app.db.session import SessionLocal

class PricePredictorTrainer:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.db = SessionLocal()

    def load_data(self, product_id: int) -> pd.DataFrame:
        """Load price history data from database"""
        query = f"""
            SELECT date, price 
            FROM price_history 
            WHERE product_id = {product_id}
            ORDER BY date
        """
        df = pd.read_sql(query, self.db.connection())
        df['date'] = pd.to_datetime(df['date'])
        return df

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Feature engineering for time series data"""
        df = df.set_index('date').resample('D').mean().ffill()
        df['day_of_week'] = df.index.dayofweek
        df['day_of_month'] = df.index.day
        df['month'] = df.index.month
        df['price_lag1'] = df['price'].shift(1)
        df['price_lag7'] = df['price'].shift(7)
        df['rolling_avg'] = df['price'].rolling(7).mean()
        return df.dropna()

    def train(self, product_id: int) -> dict:
        """Train model for a specific product"""
        df = self.load_data(product_id)
        if len(df) < 30:
            return {"status": "error", "message": "Insufficient data"}

        processed = self.preprocess_data(df)
        X = processed.drop('price', axis=1)
        y = processed['price']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        self.model.fit(X_train, y_train)
        score = self.model.score(X_test, y_test)
        
        # Save model
        model_path = f"models/product_{product_id}.joblib"
        joblib.dump(self.model, model_path)
        
        return {
            "status": "success",
            "product_id": product_id,
            "r2_score": score,
            "model_path": model_path,
            "last_trained": datetime.now().isoformat()
        }

if __name__ == "__main__":
    trainer = PricePredictorTrainer()
    result = trainer.train(123)  # Example product ID
    print(result)