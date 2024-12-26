"""Email tool implementation"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
import logging
from .base import BaseTool
from ..types import ToolResponse

logger = logging.getLogger(__name__)

class EmailTool(BaseTool):
    """Tool for sending emails

    This tool provides email sending capabilities to agents. It validates
    email addresses and handles common email sending errors gracefully.
    """

    @property
    def description(self) -> str:
        """Get the tool description"""
        return "Send emails with specified subject and content"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate email parameters

        Checks for required fields and basic email format validation.

        Args:
            params: Dictionary containing email parameters

        Returns:
            True if parameters are valid, False otherwise
        """
        required_fields = {'to', 'subject', 'content'}
        if not all(field in params for field in required_fields):
            logger.error(f"Missing required email fields: {required_fields - set(params.keys())}")
            return False

        # Basic email validation
        email = params['to']
        if '@' not in email or '.' not in email:
            logger.error(f"Invalid email format: {email}")
            return False

        return True

    async def execute(self, **kwargs) -> ToolResponse:
        """Send an email

        Args:
            **kwargs: Must include 'to', 'subject', and 'content' parameters

        Returns:
            ToolResponse indicating success/failure of email sending
        """
        try:
            # Extract required parameters
            to = kwargs.get('to')
            subject = kwargs.get('subject')
            content = kwargs.get('content')

            # Validate parameters
            if not self.validate_params({'to': to, 'subject': subject, 'content': content}):
                return ToolResponse(
                    success=False,
                    result=None,
                    error="Invalid email parameters"
                )

            msg = MIMEMultipart()
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(content, 'plain'))

            # Implementation of email sending logic
            # For now, we're using the mock implementation
            logger.info(f"Sending email to {to}")

            return ToolResponse(
                success=True,
                result=f"Email sent to {to}"
            )

        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return ToolResponse(
                success=False,
                result=None,
                error=f"Failed to send email: {str(e)}"
            )