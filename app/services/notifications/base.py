from abc import ABC, abstractmethod
from typing import Optional, Dict

class BaseNotifier(ABC):
    @abstractmethod
    async def send(
        self,
        recipient: str,
        subject: str,
        template: str,
        context: Optional[Dict] = None
    ) -> bool:
        """Send notification"""
        pass

    @abstractmethod
    async def send_price_alert(
        self,
        recipient: str,
        product_name: str,
        current_price: float,
        target_price: float,
        product_url: str
    ) -> bool:
        """Send price alert notification"""
        pass
    