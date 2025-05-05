import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from app.utils.helpers import logger
from app.config import Config

class BaseScraper:
    def __init__(self):
        self.headers = Config.REQUEST_HEADERS
        self.timeout = Config.REQUEST_TIMEOUT
        
    def _get_page(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching page: {e}")
            return None
            
    def _extract_price(self, price_str):
        """Convert price string to float"""
        try:
            return float(''.join(c for c in price_str if c.isdigit() or c == '.'))
        except (ValueError, TypeError, AttributeError):
            logger.error(f"Could not extract price from: {price_str}")
            return None
            
    def scrape(self, url):
        """To be implemented by child classes"""
        raise NotImplementedError("Subclasses must implement this method")
    