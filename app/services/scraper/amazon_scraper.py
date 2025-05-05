import random
import time
from typing import Optional, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from services.scraper.base_scraper import BaseScraper
from app.utils.exceptions import ScrapingError
from app.core.logging import logger
from app.utils.helpers import random_delay, normalize_price

class AmazonScraper(BaseScraper):
    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        super().__init__(headless=headless, proxy=proxy)
        self.anti_bot_techniques = [
            self._random_mouse_movements,
            self._random_scrolls,
            self._random_delays
        ]

    async def scrape(self, url: str) -> Dict:
        """Advanced Amazon scraping with bot detection evasion"""
        try:
            # Initialize browser with anti-detection config
            browser = await self._init_browser()
            page = await browser.new_page()
            
            # Apply stealth and randomize fingerprint
            await self._apply_stealth(page)
            await self._randomize_fingerprint(page)
            
            # Navigate with human-like behavior
            await self._human_like_navigation(page, url)
            
            # Check for bot detection
            if await self._is_blocked(page):
                raise ScrapingError("Bot detected by Amazon")
            
            # Get page content with multiple fallback methods
            content = await self._get_page_content(page)
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract product data with multiple fallback selectors
            product_data = {
                'name': self._extract_name(soup),
                'price': self._extract_price(soup),
                'original_price': self._extract_original_price(soup),
                'availability': self._extract_availability(soup),
                'rating': self._extract_rating(soup),
                'review_count': self._extract_review_count(soup),
                'image_url': self._extract_image(soup),
                'seller': self._extract_seller(soup)
            }
            
            # Validate extracted data
            if not product_data['name'] or product_data['price'] is None:
                raise ScrapingError("Essential data not found")
            
            # Add metadata
            product_data.update({
                'url': url,
                'timestamp': int(time.time()),
                'source': 'amazon',
                'shipping_info': self._extract_shipping(soup)
            })
            
            return product_data
            
        except Exception as e:
            logger.error(f"Amazon scraping failed: {str(e)}")
            raise ScrapingError(f"Amazon scraping error: {str(e)}")
        finally:
            if 'browser' in locals():
                await browser.close()

    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extract product name with multiple fallback selectors"""
        selectors = [
            {'id': 'productTitle'},
            {'id': 'title'},
            {'class': 'a-size-large product-title-word-break'},
            {'class': 'a-size-medium a-color-base a-text-normal'},
            {'class': 'a-size-base-plus a-color-base a-text-normal'}
        ]
        return self._find_with_fallbacks(soup, selectors)

    def _extract_price(self, soup: BeautifulSoup) -> float:
        """Extract current price with multiple fallback selectors"""
        price_selectors = [
            {'class': 'a-price-whole'},
            {'id': 'priceblock_ourprice'},
            {'id': 'priceblock_dealprice'},
            {'class': 'a-color-price'},
            {'class': 'priceToPay'}
        ]
        price_text = self._find_with_fallbacks(soup, price_selectors)
        return normalize_price(price_text) if price_text else None

    # ... (other extraction methods with similar robustness)