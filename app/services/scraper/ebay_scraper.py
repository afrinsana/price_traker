import logging
from typing import Optional, Dict
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from app.services.scraper.base_scraper import BaseScraper
from app.utils.helpers import normalize_price, random_delay
from app.core.logging import logger

class EbayScraper(BaseScraper):
    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        super().__init__(headless=headless, proxy=proxy)
        self.platform = "ebay"

    async def scrape(self, url: str) -> Optional[Dict]:
        """Scrape product data from eBay"""
        try:
            await self._human_like_navigation(url)
            
            # Check for captcha
            if await self._is_blocked():
                logger.warning("Ebay blocked the scraper")
                return None

            # Get page content
            content = await self._get_page_content()
            soup = BeautifulSoup(content, 'html.parser')

            product_data = {
                'name': self._extract_name(soup),
                'price': self._extract_price(soup),
                'original_price': self._extract_original_price(soup),
                'availability': self._extract_availability(soup),
                'image_url': self._extract_image(soup),
                'seller': self._extract_seller(soup),
                'url': url,
                'platform': self.platform
            }

            return product_data

        except Exception as e:
            logger.error(f"Ebay scraping error: {str(e)}")
            return None

    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extract product name from eBay page"""
        selectors = [
            {'class': 'x-item-title__mainTitle'},
            {'id': 'itemTitle'},
            {'class': 'product-title'}
        ]
        return self._find_with_fallbacks(soup, selectors) or "Unknown Product"

    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract current price from eBay page"""
        price_selectors = [
            {'class': 'x-price-primary'},
            {'itemprop': 'price'},
            {'class': 'display-price'}
        ]
        price_text = self._find_with_fallbacks(soup, price_selectors)
        return normalize_price(price_text) if price_text else None

    def _extract_original_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract original price if on sale"""
        original_price_selectors = [
            {'class': 'x-original-price'},
            {'class': 'strikethrough'}
        ]
        price_text = self._find_with_fallbacks(soup, original_price_selectors)
        return normalize_price(price_text) if price_text else None

    # ... (other extraction methods for eBay-specific elements)