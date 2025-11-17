"""
Email Service for CIMR Claims Automation
Sends notifications to members about claim status
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from loguru import logger
from jinja2 import Template

from src.config.settings import settings


class EmailService:
    """Service for sending email notifications"""

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.sender_email = settings.sender_email
        self.sender_name = settings.sender_name
        self.enabled = settings.email_enabled

    def _get_smtp_connection(self):
        """Establish SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            return server
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {e}")
            raise

    def send_claim_confirmation(
        self,
        member_email: str,
        member_name: str,
        ticket_id: str,
        claim_category: str
    ) -> bool:
        """
        Send confirmation email when claim is received

        Args:
            member_email: Member's email address
            member_name: Member's full name
            ticket_id: Claim ticket ID
            claim_category: Category of the claim

        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            logger.info("Email notifications disabled")
            return False

        try:
            subject = f"Confirmation de réception - Réclamation #{ticket_id}"

            # HTML Email Template
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background-color: #0066cc; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background-color: #f9f9f9; padding: 20px; margin: 20px 0; }
                    .info-box { background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #0066cc; border-radius: 5px; }
                    .footer { text-align: center; color: #666; font-size: 12px; margin-top: 20px; padding: 20px; background-color: #f0f0f0; border-radius: 0 0 10px 10px; }
                    .button { background-color: #0066cc; color: white; padding: 12px 25px; text-decoration: none; display: inline-block; margin: 15px 0; border-radius: 5px; }
                    .button:hover { background-color: #0052a3; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>CIMR - Confirmation de Réclamation</h1>
                    </div>
                    <div class="content">
                        <h2>Bonjour {{ member_name }},</h2>
                        <p>Nous avons bien reçu votre réclamation. Notre équipe va la traiter dans les meilleurs délais.</p>

                        <div class="info-box">
                            <strong>Numéro de ticket :</strong> {{ ticket_id }}<br>
                            <strong>Catégorie :</strong> {{ claim_category }}<br>
                            <strong>Date de réception :</strong> {{ current_date }}
                        </div>

                        <p>Vous recevrez une notification par email dès que votre réclamation sera traitée.</p>
                        <p>Vous pouvez suivre l'état de votre réclamation à tout moment sur notre portail.</p>

                        <a href="http://localhost:8501" class="button">Suivre ma réclamation</a>
                    </div>
                    <div class="footer">
                        <p>Ceci est un email automatique, merci de ne pas y répondre.</p>
                        <p>&copy; 2025 CIMR - Tous droits réservés</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Render template
            template = Template(html_template)
            html_body = template.render(
                member_name=member_name,
                ticket_id=ticket_id,
                claim_category=claim_category,
                current_date=self._get_current_date()
            )

            # Create email
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = member_email

            # Add HTML content
            html_part = MIMEText(html_body, 'html')
            message.attach(html_part)

            # Send email
            with self._get_smtp_connection() as server:
                server.send_message(message)

            logger.info(f"✅ Confirmation email sent to {member_email} for ticket {ticket_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send confirmation email: {e}")
            return False

    def send_status_update(
        self,
        member_email: str,
        member_name: str,
        ticket_id: str,
        old_status: str,
        new_status: str,
        resolution_message: Optional[str] = None
    ) -> bool:
        """
        Send email when claim status changes

        Args:
            member_email: Member's email
            member_name: Member's name
            ticket_id: Claim ticket ID
            old_status: Previous status
            new_status: New status
            resolution_message: Resolution message if resolved

        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            return False

        try:
            subject = f"Mise à jour - Réclamation #{ticket_id}"

            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background-color: #0066cc; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background-color: #f9f9f9; padding: 20px; margin: 20px 0; }
                    .status-box { background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #28a745; border-radius: 5px; }
                    .resolution { background-color: #e8f5e9; padding: 15px; margin: 15px 0; border-radius: 5px; border: 1px solid #4caf50; }
                    .footer { text-align: center; color: #666; font-size: 12px; margin-top: 20px; padding: 20px; background-color: #f0f0f0; border-radius: 0 0 10px 10px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Mise à Jour de Votre Réclamation</h1>
                    </div>
                    <div class="content">
                        <h2>Bonjour {{ member_name }},</h2>
                        <p>Le statut de votre réclamation a été mis à jour.</p>

                        <div class="status-box">
                            <strong>Numéro de ticket :</strong> {{ ticket_id }}<br>
                            <strong>Ancien statut :</strong> {{ old_status }}<br>
                            <strong>Nouveau statut :</strong> <span style="color: #28a745; font-weight: bold;">{{ new_status }}</span>
                        </div>

                        {% if resolution_message %}
                        <div class="resolution">
                            <h3>Message de résolution :</h3>
                            <p>{{ resolution_message }}</p>
                        </div>
                        {% endif %}

                        <p>Merci de votre patience.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2025 CIMR - Service Réclamations</p>
                    </div>
                </div>
            </body>
            </html>
            """

            template = Template(html_template)
            html_body = template.render(
                member_name=member_name,
                ticket_id=ticket_id,
                old_status=old_status,
                new_status=new_status,
                resolution_message=resolution_message
            )

            # Create and send email
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = member_email

            html_part = MIMEText(html_body, 'html')
            message.attach(html_part)

            with self._get_smtp_connection() as server:
                server.send_message(message)

            logger.info(f"✅ Status update email sent to {member_email}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send status update email: {e}")
            return False

    def send_reminder_email(
        self,
        member_email: str,
        member_name: str,
        ticket_id: str,
        days_pending: int
    ) -> bool:
        """
        Send reminder email for pending claims

        Args:
            member_email: Member's email
            member_name: Member's name
            ticket_id: Claim ticket ID
            days_pending: Number of days the claim has been pending

        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            return False

        try:
            subject = f"Rappel - Réclamation #{ticket_id} en cours"

            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background-color: #ff9800; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background-color: #f9f9f9; padding: 20px; margin: 20px 0; }
                    .footer { text-align: center; color: #666; font-size: 12px; margin-top: 20px; padding: 20px; background-color: #f0f0f0; border-radius: 0 0 10px 10px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Rappel - Réclamation en Cours</h1>
                    </div>
                    <div class="content">
                        <h2>Bonjour {{ member_name }},</h2>
                        <p>Nous travaillons toujours sur votre réclamation <strong>#{{ ticket_id }}</strong>.</p>
                        <p>Votre réclamation est en cours de traitement depuis <strong>{{ days_pending }} jour(s)</strong>.</p>
                        <p>Notre équipe fait le maximum pour la résoudre rapidement.</p>
                        <p>Merci de votre patience.</p>
                    </div>
                    <div class="footer">
                        <p>Cordialement,<br>CIMR - Service Réclamations</p>
                    </div>
                </div>
            </body>
            </html>
            """

            template = Template(html_template)
            html_body = template.render(
                member_name=member_name,
                ticket_id=ticket_id,
                days_pending=days_pending
            )

            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = member_email

            html_part = MIMEText(html_body, 'html')
            message.attach(html_part)

            with self._get_smtp_connection() as server:
                server.send_message(message)

            logger.info(f"✅ Reminder email sent to {member_email}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send reminder email: {e}")
            return False

    def _get_current_date(self) -> str:
        """Get current date formatted"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y à %H:%M")


# Singleton instance
email_service = EmailService()
