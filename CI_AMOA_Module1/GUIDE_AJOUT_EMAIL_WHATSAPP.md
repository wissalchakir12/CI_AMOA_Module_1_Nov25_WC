# 🚀 Guide d'Implémentation : Notifications Email + WhatsApp

Guide complet pour ajouter les fonctionnalités de notifications email et intégration WhatsApp au module CIMR Claims Automation.

---

## 📧 PARTIE 1 : NOTIFICATIONS EMAIL

### 📋 Étape 1 : Installer les dépendances

Ajoutez dans le fichier `requirements.txt` :

```txt
jinja2>=3.1.2
```

Puis installez :

```bash
pip install jinja2
```

### 📋 Étape 2 : Mettre à jour le fichier `.env`

Ajoutez ces variables dans `env.template` :

```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre_email@gmail.com
SMTP_PASSWORD=votre_app_password
SENDER_EMAIL=noreply@cimr.ma
SENDER_NAME=CIMR - Service Réclamations

# Email Templates
EMAIL_ENABLED=True
```

**Note pour Gmail :**
- Activez l'authentification à 2 facteurs
- Générez un "App Password" depuis : https://myaccount.google.com/apppasswords
- Utilisez ce mot de passe dans `SMTP_PASSWORD`

**Autres fournisseurs SMTP :**

| Fournisseur | SMTP_HOST | SMTP_PORT |
|-------------|-----------|-----------|
| Gmail | smtp.gmail.com | 587 |
| Outlook | smtp-mail.outlook.com | 587 |
| Yahoo | smtp.mail.yahoo.com | 587 |
| SendGrid | smtp.sendgrid.net | 587 |
| AWS SES | email-smtp.eu-west-1.amazonaws.com | 587 |

### 📋 Étape 3 : Mettre à jour `settings.py`

Dans le fichier `src/config/settings.py`, ajoutez ces champs à la classe `Settings` :

```python
class Settings(BaseSettings):
    # ... existing fields ...

    # Email Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SENDER_EMAIL: str = "noreply@cimr.ma"
    SENDER_NAME: str = "CIMR Service Réclamations"
    EMAIL_ENABLED: bool = False
```

### 📋 Étape 4 : Créer le service Email

Créez le fichier `src/utils/email_service.py` :

```python
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
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.sender_email = settings.SENDER_EMAIL
        self.sender_name = settings.SENDER_NAME
        self.enabled = settings.EMAIL_ENABLED

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
                    .header { background-color: #0066cc; color: white; padding: 20px; text-align: center; }
                    .content { background-color: #f9f9f9; padding: 20px; margin: 20px 0; }
                    .info-box { background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #0066cc; }
                    .footer { text-align: center; color: #666; font-size: 12px; margin-top: 20px; }
                    .button { background-color: #0066cc; color: white; padding: 10px 20px; text-decoration: none; display: inline-block; margin: 10px 0; }
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
                    .header { background-color: #0066cc; color: white; padding: 20px; text-align: center; }
                    .content { background-color: #f9f9f9; padding: 20px; margin: 20px 0; }
                    .status-box { background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #28a745; }
                    .resolution { background-color: #e8f5e9; padding: 15px; margin: 15px 0; border-radius: 5px; }
                    .footer { text-align: center; color: #666; font-size: 12px; margin-top: 20px; }
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

            message_body = f"""
            Bonjour {member_name},

            Nous travaillons toujours sur votre réclamation #{ticket_id}.

            Votre réclamation est en cours de traitement depuis {days_pending} jour(s).
            Notre équipe fait le maximum pour la résoudre rapidement.

            Merci de votre patience.

            Cordialement,
            CIMR - Service Réclamations
            """

            message = MIMEText(message_body)
            message['Subject'] = subject
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = member_email

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
```

### 📋 Étape 5 : Intégrer dans le workflow

Modifiez `src/agents/claims_workflow.py` :

**Ajoutez en haut du fichier :**

```python
from src.utils.email_service import email_service
```

**Dans la fonction `create_claim_step`, après avoir créé le ticket, ajoutez :**

```python
# Send confirmation email if member_email is provided
if claim_data.get('member_email'):
    try:
        email_service.send_claim_confirmation(
            member_email=claim_data['member_email'],
            member_name=claim_data['member_name'],
            ticket_id=ticket_id,
            claim_category="En cours de classification"
        )
        logger.info(f"✅ Confirmation email sent for ticket {ticket_id}")
    except Exception as e:
        logger.warning(f"⚠️ Could not send confirmation email: {e}")
```

### 📋 Étape 6 : Ajouter le champ email au formulaire

Modifiez `pages/1_Member_Portal.py` pour ajouter un champ email :

```python
# Ajoutez après le champ member_id :
member_email = st.text_input(
    "📧 Adresse Email (optionnel)",
    placeholder="exemple@email.com",
    help="Pour recevoir des notifications par email"
)
```

Et dans la soumission du formulaire, incluez l'email :

```python
claim_data = {
    "member_name": member_name,
    "member_id": member_id,
    "member_email": member_email,  # Ajoutez cette ligne
    "channel": "Web",
    "message": claim_message,
    "attachment_url": attachment_url if uploaded_file else None
}
```

### 📋 Étape 7 : Tester l'envoi d'emails

Créez un fichier de test `test_email.py` à la racine :

```python
"""
Test Email Service
"""
from src.utils.email_service import email_service

# Test confirmation email
def test_confirmation_email():
    result = email_service.send_claim_confirmation(
        member_email="votre_email@test.com",
        member_name="Test User",
        ticket_id="TEST123",
        claim_category="Paiement"
    )
    print(f"✅ Confirmation email sent: {result}")

# Test status update email
def test_status_update_email():
    result = email_service.send_status_update(
        member_email="votre_email@test.com",
        member_name="Test User",
        ticket_id="TEST123",
        old_status="Nouveau",
        new_status="Résolu",
        resolution_message="Votre problème a été résolu avec succès."
    )
    print(f"✅ Status update email sent: {result}")

if __name__ == "__main__":
    print("Testing email service...")
    test_confirmation_email()
    test_status_update_email()
```

Exécutez :

```bash
python test_email.py
```

---

## 📱 PARTIE 2 : INTÉGRATION WHATSAPP

### 📋 Étape 1 : Créer un compte Twilio

1. Allez sur [https://www.twilio.com](https://www.twilio.com)
2. Créez un compte gratuit (crédit de $15 offert)
3. Vérifiez votre email et numéro de téléphone
4. Récupérez vos identifiants dans le **Dashboard** :
   - **Account SID** (ex: ACxxxxxxxxxxxxxxxxxxxx)
   - **Auth Token** (cliquez sur "Show" pour voir)
5. Activez **WhatsApp Sandbox** :
   - Allez dans **Messaging** > **Try it out** > **Send a WhatsApp message**
   - Suivez les instructions pour rejoindre le sandbox
   - Récupérez votre **WhatsApp Number** (ex: +14155238886)

### 📋 Étape 2 : Installer les dépendances

Ajoutez dans `requirements.txt` :

```txt
twilio>=8.0.0
```

Puis installez :

```bash
pip install twilio
```

### 📋 Étape 3 : Mettre à jour le fichier `.env`

Ajoutez ces variables dans `env.template` :

```env
# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
WHATSAPP_ENABLED=True
```

**Remplacez :**
- `your_account_sid_here` par votre Account SID
- `your_auth_token_here` par votre Auth Token
- `+14155238886` par votre numéro WhatsApp Twilio

### 📋 Étape 4 : Mettre à jour `settings.py`

Dans `src/config/settings.py`, ajoutez :

```python
class Settings(BaseSettings):
    # ... existing fields ...

    # Twilio WhatsApp Settings
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_NUMBER: str = "whatsapp:+14155238886"
    WHATSAPP_ENABLED: bool = False
```

### 📋 Étape 5 : Créer le service WhatsApp

Créez le fichier `src/utils/whatsapp_service.py` :

```python
"""
WhatsApp Service for CIMR Claims Automation
Handles WhatsApp message sending and webhook receiving
"""
from typing import Optional
from twilio.rest import Client
from loguru import logger

from src.config.settings import settings


class WhatsAppService:
    """Service for sending WhatsApp messages via Twilio"""

    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER
        self.enabled = settings.WHATSAPP_ENABLED

        if self.enabled:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("✅ WhatsApp service initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize WhatsApp client: {e}")
                self.client = None
                self.enabled = False
        else:
            self.client = None

    def send_claim_confirmation(
        self,
        member_phone: str,
        member_name: str,
        ticket_id: str,
        claim_category: str
    ) -> bool:
        """
        Send WhatsApp confirmation when claim is received

        Args:
            member_phone: Member's phone number (format: +212612345678)
            member_name: Member's full name
            ticket_id: Claim ticket ID
            claim_category: Category of the claim

        Returns:
            bool: True if sent successfully
        """
        if not self.enabled or not self.client:
            logger.info("WhatsApp notifications disabled")
            return False

        try:
            # Format phone number for WhatsApp
            to_number = f"whatsapp:{member_phone}"

            # Message content with emojis and formatting
            message_body = f"""
🎫 *CIMR - Confirmation de Réclamation*

Bonjour {member_name},

Nous avons bien reçu votre réclamation.

📋 *Détails :*
• Ticket : *#{ticket_id}*
• Catégorie : {claim_category}
• Date : {self._get_current_date()}

✅ Notre équipe va traiter votre demande dans les meilleurs délais.

Vous recevrez une notification dès que votre réclamation sera traitée.

_Message automatique - CIMR Service Réclamations_
            """.strip()

            # Send message
            message = self.client.messages.create(
                from_=self.whatsapp_number,
                body=message_body,
                to=to_number
            )

            logger.info(f"✅ WhatsApp confirmation sent to {member_phone}. SID: {message.sid}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send WhatsApp message: {e}")
            return False

    def send_status_update(
        self,
        member_phone: str,
        member_name: str,
        ticket_id: str,
        new_status: str,
        resolution_message: Optional[str] = None
    ) -> bool:
        """
        Send WhatsApp message when claim status changes

        Args:
            member_phone: Member's phone number
            member_name: Member's name
            ticket_id: Claim ticket ID
            new_status: New status
            resolution_message: Resolution message if resolved

        Returns:
            bool: True if sent successfully
        """
        if not self.enabled or not self.client:
            return False

        try:
            to_number = f"whatsapp:{member_phone}"

            # Status emoji mapping
            status_emoji = {
                "Nouveau": "🆕",
                "New": "🆕",
                "En cours": "⏳",
                "In progress": "⏳",
                "Résolu": "✅",
                "Resolved": "✅",
                "Escalade": "⚠️",
                "Escalated": "⚠️"
            }

            emoji = status_emoji.get(new_status, "📝")

            message_body = f"""
{emoji} *Mise à Jour - Réclamation #{ticket_id}*

Bonjour {member_name},

Le statut de votre réclamation a changé :
*{new_status}*
            """.strip()

            if resolution_message:
                message_body += f"\n\n💬 *Message :*\n{resolution_message}"

            message_body += "\n\n_CIMR Service Réclamations_"

            # Send message
            message = self.client.messages.create(
                from_=self.whatsapp_number,
                body=message_body,
                to=to_number
            )

            logger.info(f"✅ WhatsApp status update sent to {member_phone}. SID: {message.sid}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send WhatsApp status update: {e}")
            return False

    def send_simple_message(self, to_phone: str, message: str) -> bool:
        """
        Send a simple WhatsApp message

        Args:
            to_phone: Phone number (format: +212612345678)
            message: Message text

        Returns:
            bool: True if sent successfully
        """
        if not self.enabled or not self.client:
            return False

        try:
            to_number = f"whatsapp:{to_phone}"

            msg = self.client.messages.create(
                from_=self.whatsapp_number,
                body=message,
                to=to_number
            )

            logger.info(f"✅ WhatsApp message sent to {to_phone}. SID: {msg.sid}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send WhatsApp message: {e}")
            return False

    def _get_current_date(self) -> str:
        """Get current date formatted"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y à %H:%M")


# Singleton instance
whatsapp_service = WhatsAppService()
```

### 📋 Étape 6 : Créer le webhook WhatsApp

Créez le fichier `src/api/routes/whatsapp.py` :

```python
"""
WhatsApp Webhook Routes
Receives incoming WhatsApp messages from Twilio
"""
from fastapi import APIRouter, Form, Request, HTTPException
from loguru import logger
from typing import Optional

from src.agents.claims_workflow import process_claim_async

router = APIRouter(prefix="/webhooks/whatsapp", tags=["WhatsApp"])


@router.post("/")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    ProfileName: Optional[str] = Form(None),
    MessageSid: Optional[str] = Form(None),
):
    """
    Webhook endpoint to receive WhatsApp messages from Twilio

    Args:
        From: Phone number with whatsapp: prefix (ex: whatsapp:+212612345678)
        Body: Message text from user
        ProfileName: User's WhatsApp profile name
        MessageSid: Unique message identifier from Twilio

    Returns:
        TwiML response (empty to not reply immediately)
    """
    try:
        # Extract phone number (remove 'whatsapp:' prefix)
        phone_number = From.replace("whatsapp:", "")
        message_body = Body
        sender_name = ProfileName or "Utilisateur"

        logger.info(f"📱 Received WhatsApp message from {phone_number} ({sender_name})")
        logger.info(f"Message: {message_body[:100]}...")

        # Check if it's a status check request
        if message_body.strip().lower() in ["statut", "status", "suivi", "ticket"]:
            # TODO: Implement status check functionality
            from src.utils.whatsapp_service import whatsapp_service
            whatsapp_service.send_simple_message(
                to_phone=phone_number,
                message="Pour vérifier le statut de votre réclamation, veuillez fournir votre numéro de ticket.\n\nExemple: Ticket #123"
            )
            return """<?xml version="1.0" encoding="UTF-8"?><Response></Response>"""

        # Process the claim through the workflow
        # Format the input for the workflow
        formatted_input = f"""
Nom: {sender_name}
Téléphone: {phone_number}
Canal: WhatsApp
Message: {message_body}
"""

        logger.info("🔄 Processing WhatsApp claim through workflow...")

        # Process claim asynchronously
        result = await process_claim_async(
            member_input=formatted_input,
            channel="WhatsApp"
        )

        if result.get("success"):
            ticket_id = result.get("ticket_id", "N/A")
            logger.info(f"✅ WhatsApp claim processed successfully. Ticket: {ticket_id}")

            # Send confirmation via WhatsApp
            from src.utils.whatsapp_service import whatsapp_service
            whatsapp_service.send_claim_confirmation(
                member_phone=phone_number,
                member_name=sender_name,
                ticket_id=ticket_id,
                claim_category="En cours de classification"
            )
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"❌ Failed to process WhatsApp claim: {error_msg}")

            # Send error message to user
            from src.utils.whatsapp_service import whatsapp_service
            whatsapp_service.send_simple_message(
                to_phone=phone_number,
                message="❌ Désolé, une erreur s'est produite lors du traitement de votre réclamation. Veuillez réessayer plus tard."
            )

        # Return empty TwiML response (Twilio expects XML)
        return """<?xml version="1.0" encoding="UTF-8"?>
<Response></Response>"""

    except Exception as e:
        logger.error(f"❌ WhatsApp webhook error: {e}")
        return """<?xml version="1.0" encoding="UTF-8"?>
<Response></Response>"""


@router.get("/status")
async def whatsapp_status():
    """
    Check WhatsApp service status

    Returns:
        Service status information
    """
    from src.utils.whatsapp_service import whatsapp_service

    return {
        "service": "WhatsApp",
        "enabled": whatsapp_service.enabled,
        "status": "operational" if whatsapp_service.enabled else "disabled",
        "provider": "Twilio"
    }


@router.post("/test")
async def test_whatsapp(phone: str, message: str = "Test message from CIMR"):
    """
    Test endpoint to send a WhatsApp message

    Args:
        phone: Phone number (format: +212612345678)
        message: Test message to send

    Returns:
        Success status
    """
    from src.utils.whatsapp_service import whatsapp_service

    if not whatsapp_service.enabled:
        raise HTTPException(status_code=503, detail="WhatsApp service is disabled")

    success = whatsapp_service.send_simple_message(phone, message)

    if success:
        return {"success": True, "message": f"Test message sent to {phone}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send message")
```

### 📋 Étape 7 : Enregistrer les routes WhatsApp

Dans `src/api/main.py`, ajoutez :

```python
# Ajoutez en haut avec les autres imports
from src.api.routes import whatsapp

# Ajoutez après les autres routers (après app.include_router(status.router))
app.include_router(whatsapp.router)
```

### 📋 Étape 8 : Configurer le webhook Twilio avec ngrok

**1. Installer ngrok :**

Téléchargez depuis [https://ngrok.com/download](https://ngrok.com/download)

**2. Lancer votre API :**

```bash
python run.py
```

**3. Exposer votre localhost avec ngrok :**

Ouvrez un nouveau terminal :

```bash
ngrok http 8000
```

Vous verrez quelque chose comme :

```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

**4. Configurer Twilio :**

1. Allez dans le **Twilio Console**
2. **Messaging** > **Settings** > **WhatsApp sandbox settings**
3. Dans **"When a message comes in"** :
   - Collez : `https://abc123.ngrok.io/webhooks/whatsapp`
   - Méthode : `HTTP POST`
4. Cliquez **Save**

### 📋 Étape 9 : Tester WhatsApp

**1. Rejoindre le Sandbox (si pas déjà fait) :**

Envoyez un message WhatsApp au numéro Twilio avec le code fourni :
```
join <votre-code-sandbox>
```

**2. Tester l'envoi de message :**

Créez `test_whatsapp.py` :

```python
"""
Test WhatsApp Service
"""
from src.utils.whatsapp_service import whatsapp_service

def test_whatsapp_message():
    # Remplacez par votre numéro (format international)
    result = whatsapp_service.send_simple_message(
        to_phone="+212612345678",  # Votre numéro
        message="🧪 Test message from CIMR Claims Automation!"
    )
    print(f"✅ Message sent: {result}")

def test_claim_confirmation():
    result = whatsapp_service.send_claim_confirmation(
        member_phone="+212612345678",
        member_name="Test User",
        ticket_id="TEST123",
        claim_category="Paiement"
    )
    print(f"✅ Confirmation sent: {result}")

if __name__ == "__main__":
    print("Testing WhatsApp service...")
    test_whatsapp_message()
    test_claim_confirmation()
```

Exécutez :

```bash
python test_whatsapp.py
```

**3. Tester le workflow complet :**

Envoyez un message WhatsApp au numéro Twilio :

```
Bonjour, je n'ai pas reçu ma pension du mois de janvier. Mon CIN est AB123456. Merci.
```

Vous devriez recevoir une confirmation automatique !

---

## 🧪 TESTS COMPLETS

### Test 1 : Email uniquement

```bash
python test_email.py
```

Vérifiez votre boîte email.

### Test 2 : WhatsApp uniquement

```bash
python test_whatsapp.py
```

Vérifiez votre WhatsApp.

### Test 3 : Workflow complet via API

```bash
curl -X POST "http://localhost:8000/api/claims/" \
  -H "Content-Type: application/json" \
  -d '{
    "member_name": "Mohammed Alami",
    "member_id": "AB123456",
    "member_email": "test@example.com",
    "channel": "Web",
    "message": "Je n ai pas reçu ma pension"
  }'
```

### Test 4 : Workflow complet via Streamlit

1. Lancez l'interface : `streamlit run app.py`
2. Allez sur le portail membre
3. Remplissez le formulaire avec votre email
4. Soumettez
5. Vérifiez votre email pour la confirmation

---

## 📊 RÉCAPITULATIF DES FICHIERS

### Fichiers à CRÉER :

| Fichier | Description |
|---------|-------------|
| `src/utils/email_service.py` | Service d'envoi d'emails |
| `src/utils/whatsapp_service.py` | Service WhatsApp Twilio |
| `src/api/routes/whatsapp.py` | Routes webhook WhatsApp |
| `test_email.py` | Tests pour emails |
| `test_whatsapp.py` | Tests pour WhatsApp |

### Fichiers à MODIFIER :

| Fichier | Modifications |
|---------|---------------|
| `requirements.txt` | Ajouter `jinja2>=3.1.2` et `twilio>=8.0.0` |
| `env.template` | Ajouter config email et WhatsApp |
| `.env` | Ajouter vos vraies credentials |
| `src/config/settings.py` | Ajouter champs email et WhatsApp |
| `src/api/main.py` | Inclure router WhatsApp |
| `src/agents/claims_workflow.py` | Intégrer email dans create_claim_step |
| `pages/1_Member_Portal.py` | Ajouter champ email au formulaire |

---

## 🔐 SÉCURITÉ

### Pour Gmail :
1. Activez l'authentification à 2 facteurs
2. Générez un "App Password" : https://myaccount.google.com/apppasswords
3. N'utilisez JAMAIS votre mot de passe Gmail principal

### Pour Twilio :
1. Ne commitez JAMAIS vos credentials dans Git
2. Ajoutez `.env` à `.gitignore`
3. Utilisez des variables d'environnement en production

### Fichier `.gitignore` :
```
.env
*.pyc
__pycache__/
venv/
```

---

## 🚀 DÉPLOIEMENT EN PRODUCTION

### Pour ngrok (production temporaire) :
```bash
# Lancez avec un domaine fixe (compte payant)
ngrok http 8000 --domain=your-domain.ngrok.io
```

### Pour un serveur réel (Heroku, AWS, etc.) :
1. Déployez votre API sur un serveur avec HTTPS
2. Mettez à jour le webhook Twilio avec votre vraie URL :
   ```
   https://votre-domaine.com/webhooks/whatsapp
   ```

---

## 📞 SUPPORT

### Problèmes Email :
- **Erreur SMTP** : Vérifiez host, port, credentials
- **Email non reçu** : Vérifiez spam, vérifiez logs

### Problèmes WhatsApp :
- **Message non envoyé** : Vérifiez Account SID et Auth Token
- **Webhook ne fonctionne pas** : Vérifiez que ngrok tourne et URL est correcte
- **"Join sandbox"** : Rejoignez d'abord le sandbox Twilio

### Logs :
Tous les logs sont dans la console. Regardez pour :
- ✅ = Succès
- ❌ = Erreur
- ⚠️ = Warning

---

## ✅ CHECKLIST FINALE

- [ ] Dépendances installées (`jinja2`, `twilio`)
- [ ] Variables d'environnement configurées dans `.env`
- [ ] Service email créé et testé
- [ ] Service WhatsApp créé et testé
- [ ] Routes webhook créées
- [ ] Webhook Twilio configuré avec ngrok
- [ ] Tests unitaires passent
- [ ] Workflow complet testé
- [ ] Documentation à jour

---

**🎉 Félicitations ! Votre module CIMR supporte maintenant les notifications Email et WhatsApp !**

**Date de création :** 14 Janvier 2025
**Version :** 1.0.0
**Auteur :** Guide d'Implémentation CIMR
