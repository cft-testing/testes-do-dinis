"""
Email Sender Module
Sends newsletter via email
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime


class EmailSender:
    """Sends newsletter emails"""

    def __init__(self):
        """Initialize email sender with environment configuration"""
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("EMAIL_FROM", self.username)
        self.to_email = os.getenv("EMAIL_TO")

        if not all([self.username, self.password, self.to_email]):
            raise ValueError("Email configuration incomplete. Check .env file.")

    def send_newsletter(
        self,
        html_content: str,
        text_content: str,
        subject: Optional[str] = None,
        recipients: Optional[List[str]] = None
    ) -> bool:
        """
        Send newsletter email

        Args:
            html_content: HTML version of newsletter
            text_content: Plain text version of newsletter
            subject: Email subject (auto-generated if not provided)
            recipients: List of recipient emails (uses default if not provided)

        Returns:
            True if sent successfully, False otherwise
        """
        if recipients is None:
            recipients = [r.strip() for r in self.to_email.split(",")]

        if subject is None:
            subject = self._generate_subject()

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = ", ".join(recipients)

            # Add text and HTML parts
            part1 = MIMEText(text_content, "plain", "utf-8")
            part2 = MIMEText(html_content, "html", "utf-8")

            msg.attach(part1)
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            print(f"Newsletter sent successfully to {len(recipients)} recipient(s)")
            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def _generate_subject(self) -> str:
        """Generate email subject with current date"""
        date_str = datetime.now().strftime("%d/%m/%Y")
        newsletter_name = os.getenv("NEWSLETTER_NAME", "CFT Trend Radar")
        return f"{newsletter_name} - {date_str}"

    def send_test_email(self, test_recipient: str) -> bool:
        """
        Send a test email to verify configuration

        Args:
            test_recipient: Email address to send test to

        Returns:
            True if sent successfully
        """
        html = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #667eea;">CFT Trend Radar - Test Email</h2>
            <p>This is a test email to verify the email configuration.</p>
            <p>If you received this, the email system is working correctly!</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                Sent at: {datetime}
            </p>
        </body>
        </html>
        """.format(datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        text = """
        CFT Trend Radar - Test Email

        This is a test email to verify the email configuration.
        If you received this, the email system is working correctly!

        Sent at: {datetime}
        """.format(datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        return self.send_newsletter(
            html_content=html,
            text_content=text,
            subject="CFT Trend Radar - Test Email",
            recipients=[test_recipient]
        )

    def validate_configuration(self) -> bool:
        """
        Validate email configuration without sending

        Returns:
            True if configuration appears valid
        """
        required_vars = [
            "SMTP_SERVER",
            "SMTP_PORT",
            "SMTP_USERNAME",
            "SMTP_PASSWORD",
            "EMAIL_TO"
        ]

        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)

        if missing:
            print(f"Missing email configuration: {', '.join(missing)}")
            return False

        print("Email configuration validated successfully")
        return True
