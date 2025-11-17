"""
Test Email Service for CIMR Claims Automation
Tests email notifications functionality
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.email_service import email_service
from loguru import logger


def test_confirmation_email():
    """Test sending a confirmation email"""
    print("\n" + "="*60)
    print("TEST 1: Sending Confirmation Email")
    print("="*60)

    try:
        result = email_service.send_claim_confirmation(
            member_email="votre_email@test.com",  # CHANGEZ CECI PAR VOTRE EMAIL
            member_name="Ahmed Benali",
            ticket_id="TEST-12345",
            claim_category="Paiement"
        )

        if result:
            print("✅ SUCCESS: Confirmation email sent successfully!")
            print("📧 Check your inbox at: votre_email@test.com")
        else:
            print("⚠️ WARNING: Email not sent (service might be disabled)")
            print("💡 Make sure EMAIL_ENABLED=True in your .env file")

        return result

    except Exception as e:
        print(f"❌ ERROR: Failed to send confirmation email")
        print(f"   Error: {str(e)}")
        return False


def test_status_update_email():
    """Test sending a status update email"""
    print("\n" + "="*60)
    print("TEST 2: Sending Status Update Email")
    print("="*60)

    try:
        result = email_service.send_status_update(
            member_email="votre_email@test.com",  # CHANGEZ CECI PAR VOTRE EMAIL
            member_name="Ahmed Benali",
            ticket_id="TEST-12345",
            old_status="Nouveau",
            new_status="Résolu",
            resolution_message="Votre problème de paiement a été résolu. Le montant sera crédité dans les 48 heures."
        )

        if result:
            print("✅ SUCCESS: Status update email sent successfully!")
            print("📧 Check your inbox at: votre_email@test.com")
        else:
            print("⚠️ WARNING: Email not sent (service might be disabled)")

        return result

    except Exception as e:
        print(f"❌ ERROR: Failed to send status update email")
        print(f"   Error: {str(e)}")
        return False


def test_reminder_email():
    """Test sending a reminder email"""
    print("\n" + "="*60)
    print("TEST 3: Sending Reminder Email")
    print("="*60)

    try:
        result = email_service.send_reminder_email(
            member_email="votre_email@test.com",  # CHANGEZ CECI PAR VOTRE EMAIL
            member_name="Ahmed Benali",
            ticket_id="TEST-12345",
            days_pending=5
        )

        if result:
            print("✅ SUCCESS: Reminder email sent successfully!")
            print("📧 Check your inbox at: votre_email@test.com")
        else:
            print("⚠️ WARNING: Email not sent (service might be disabled)")

        return result

    except Exception as e:
        print(f"❌ ERROR: Failed to send reminder email")
        print(f"   Error: {str(e)}")
        return False


def check_email_config():
    """Check email configuration"""
    print("\n" + "="*60)
    print("EMAIL CONFIGURATION CHECK")
    print("="*60)

    print(f"\n📊 Current Configuration:")
    print(f"   SMTP Host: {email_service.smtp_host}")
    print(f"   SMTP Port: {email_service.smtp_port}")
    print(f"   SMTP User: {email_service.smtp_user}")
    print(f"   Sender Email: {email_service.sender_email}")
    print(f"   Sender Name: {email_service.sender_name}")
    print(f"   Email Enabled: {email_service.enabled}")

    if not email_service.enabled:
        print("\n⚠️ WARNING: Email service is DISABLED")
        print("💡 To enable it:")
        print("   1. Copy env.template to .env")
        print("   2. Set EMAIL_ENABLED=True")
        print("   3. Configure SMTP credentials")
        print("\n📝 For Gmail:")
        print("   - Use SMTP_HOST=smtp.gmail.com")
        print("   - Use SMTP_PORT=587")
        print("   - Generate App Password: https://myaccount.google.com/apppasswords")
        return False

    if not email_service.smtp_user or email_service.smtp_user == "votre_email@gmail.com":
        print("\n⚠️ WARNING: SMTP credentials not configured")
        print("💡 Please update your .env file with real credentials")
        return False

    print("\n✅ Email configuration looks good!")
    return True


def main():
    """Run all email tests"""
    print("\n" + "="*60)
    print("🧪 CIMR EMAIL SERVICE TEST SUITE")
    print("="*60)

    # Check configuration first
    config_ok = check_email_config()

    if not config_ok:
        print("\n❌ Configuration issues detected. Please fix them before running tests.")
        print("\n📖 See GUIDE_AJOUT_EMAIL_WHATSAPP.md for detailed instructions.")
        return

    # Run tests
    print("\n🚀 Running email tests...")
    print("⏳ Please wait...\n")

    results = []
    results.append(("Confirmation Email", test_confirmation_email()))
    results.append(("Status Update Email", test_status_update_email()))
    results.append(("Reminder Email", test_reminder_email()))

    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Email service is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check your configuration.")

    print("\n💡 Tips:")
    print("   - Check your spam/junk folder if you don't see the emails")
    print("   - Make sure your SMTP credentials are correct")
    print("   - For Gmail, use an App Password, not your regular password")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        logger.exception("Test suite failed")
