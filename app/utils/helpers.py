import re
import random
import time
from typing import Optional
from urllib.parse import urlparse
from datetime import datetime, timedelta

def normalize_price(price_str: Optional[str]) -> Optional[float]:
    """Convert price string to float"""
    if not price_str:
        return None
    
    try:
        # Remove all non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', price_str)
        return float(cleaned)
    except (ValueError, TypeError):
        return None

def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    """Random delay between requests to avoid detection"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def generate_unique_id() -> str:
    """Generate unique ID for tasks"""
    return f"{int(time.time())}-{random.randint(1000, 9999)}"

def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse datetime from string"""
    try:
        return datetime.fromisoformat(dt_str)
    except (ValueError, TypeError):
        return None

def format_timedelta(td: timedelta) -> str:
    """Format timedelta as human-readable string"""
    seconds = int(td.total_seconds())
    periods = [
        ('year', 60*60*24*365),
        ('month', 60*60*24*30),
        ('day', 60*60*24),
        ('hour', 60*60),
        ('minute', 60),
        ('second', 1)
    ]
    
    parts = []
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            part = f"{period_value} {period_name}"
            if period_value > 1:
                part += "s"
            parts.append(part)
    
    return ", ".join(parts) if parts else "just now"
