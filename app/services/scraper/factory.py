from typing import Optional, Type
from urllib.parse import urlparse

from app.services.scraper.base_scraper import BaseScraper
from app.services.scraper.amazon_scraper import AmazonScraper
from app.services.scraper.ebay_scraper import EbayScraper
from app.services.scraper.walmart_scraper import WalmartScraper
from app.config import settings
from app.core.logging import logger

class ScraperFactory:
    _scrapers = {
        'amazon': AmazonScraper,
        'ebay': EbayScraper,
        'walmart': WalmartScraper
    }

    @classmethod
    def get_scraper(cls, url: str) -> Optional[Type[BaseScraper]]:
        """Get appropriate scraper based on URL"""
        try:
            domain = urlparse(url).netloc.lower()
            
            if 'amazon.' in domain:
                return cls._scrapers['amazon'](
                    headless=settings.SCRAPER_HEADLESS,
                    proxy=settings.SCRAPER_PROXY
                )
            elif 'ebay.' in domain:
                return cls._scrapers['ebay'](
                    headless=settings.SCRAPER_HEADLESS,
                    proxy=settings.SCRAPER_PROXY
                )
            elif 'walmart.' in domain:
                return cls._scrapers['walmart'](
                    headless=settings.SCRAPER_HEADLESS,
                    proxy=settings.SCRAPER_PROXY
                )
            
            logger.warning(f"No scraper available for URL: {url}")
            return None
            
        except Exception as e:
            logger.error(f"Scraper factory error: {str(e)}")
            return None

    @classmethod
    def register_scraper(cls, domain: str, scraper_class: Type[BaseScraper]):
        """Register a new scraper for a domain"""
        cls._scrapers[domain] = scraper_class