import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from app.config import settings
from app.core.logging import logger
from app.services.notifications.base import BaseNotifier
from app.templates.email import render_template

class EmailNotifier(BaseNotifier):
    def __init__(self):
        self.sender = settings.EMAIL_SENDER
        self.password = settings.EMAIL_PASSWORD
        self.smtp_server = settings.EMAIL_SMTP_SERVER
        self.smtp_port = settings.EMAIL_SMTP_PORT

    async def send(
        self,
        recipient: str,
        subject: str,
        template: str,
        context: Optional[dict] = None
    ) -> bool:
        """Send email notification"""
        if not self.sender or not self.password:
            logger.error("Email credentials not configured")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = recipient
            msg['Subject'] = subject

            # Render HTML email from template
            html_content = render_template(template, context or {})
            msg.attach(MIMEText(html_content, 'html'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.send_message(msg)

            logger.info(f"Email sent to {recipient}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    async def send_price_alert(
        self,
        recipient: str,
        product_name: str,
        current_price: float,
        target_price: float,
        product_url: str
    ) -> bool:
        """Send price alert email"""
        return await self.send(
            recipient=recipient,
            subject=f"Price Alert: {product_name}",
            template="price_alert.html",
            context={
                'product_name': product_name,
                'current_price': current_price,
                'target_price': target_price,
                'product_url': product_url
            }
        )