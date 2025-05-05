import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configuration
    DB_URI = os.getenv('DATABASE_URL', 'sqlite:///price_tracker.db')
    
    # Scraper configuration
    REQUEST_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    REQUEST_TIMEOUT = 10
    
    # Notification configuration
    EMAIL_SENDER = os.getenv('EMAIL_SENDER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    SMS_API_KEY = os.getenv('SMS_API_KEY')
    
    # Scheduling
    CHECK_INTERVAL_HOURS = 6