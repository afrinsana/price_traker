import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine

# Connect to DB
engine = create_engine("sqlite:///price_tracker.db")
df = pd.read_sql("SELECT * FROM price_history", engine)

# Initialize Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Price Analytics Dashboard"),
    dcc.Graph(
        figure=px.line(df, x='date', y='price', color='product_id', 
                      title="Price Trends Over Time")
    ),
    dcc.Graph(
        figure=px.box(df, x='product_id', y='price', 
                     title="Price Distribution by Product")
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)
    