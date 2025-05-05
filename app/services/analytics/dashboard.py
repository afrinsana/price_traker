import plotly.express as px
import pandas as pd
from typing import List, Dict

from app.db.session import SessionLocal
from app.core.logging import logger

class DashboardGenerator:
    def __init__(self):
        pass

    async def generate_price_history_chart(self, product_id: int) -> Dict:
        """Generate price history chart for a product"""
        try:
            db = SessionLocal()
            history = db.execute(
                "SELECT date, price FROM price_history WHERE product_id = :product_id ORDER BY date",
                {'product_id': product_id}
            ).fetchall()

            if not history:
                return None

            df = pd.DataFrame(history, columns=['date', 'price'])
            fig = px.line(
                df, 
                x='date', 
                y='price',
                title='Price History',
                labels={'price': 'Price ($)', 'date': 'Date'}
            )

            return fig.to_dict()

        except Exception as e:
            logger.error(f"Failed to generate chart: {str(e)}")
            return None
        finally:
            db.close()

    async def generate_comparison_chart(self, product_ids: List[int]) -> Dict:
        """Generate price comparison chart for multiple products"""
        try:
            db = SessionLocal()
            placeholders = ', '.join([':id_' + str(i) for i in range(len(product_ids))])
            params = {'id_' + str(i): pid for i, pid in enumerate(product_ids)}
            
            query = f"""
                SELECT ph.date, ph.price, p.name 
                FROM price_history ph
                JOIN products p ON ph.product_id = p.id
                WHERE ph.product_id IN ({placeholders})
                ORDER BY ph.date
            """
            
            history = db.execute(query, params).fetchall()
            
            if not history:
                return None

            df = pd.DataFrame(history, columns=['date', 'price', 'name'])
            fig = px.line(
                df,
                x='date',
                y='price',
                color='name',
                title='Price Comparison',
                labels={'price': 'Price ($)', 'date': 'Date', 'name': 'Product'}
            )

            return fig.to_dict()

        except Exception as e:
            logger.error(f"Failed to generate comparison chart: {str(e)}")
            return None
        finally:
            db.close()