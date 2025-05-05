from typing import Optional, Dict
import httpx

from app.config import settings
from app.core.logging import logger
from app.services.notifications.base import BaseNotifier

class PushNotifier(BaseNotifier):
    def __init__(self):
        self.api_key = settings.PUSH_API_KEY
        self.api_url = settings.PUSH_API_URL

    async def send(
        self,
        recipient: str,
        subject: str,
        template: str,
        context: Optional[Dict] = None
    ) -> bool:
        """Send push notification"""
        if not self.api_key or not self.api_url:
            logger.error("Push notification credentials not configured")
            return False

        try:
            message = self._render_message(template, context or {})
            payload = {
                'to': recipient,
                'title': subject,
                'body': message,
                'data': context or {}
            }

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()

            logger.info(f"Push notification sent to {recipient}")
            return True

        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            return False