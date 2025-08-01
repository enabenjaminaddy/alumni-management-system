"""
Test script for SendGrid integration with the Alumni Management System.

How to use:
1. First ensure you've set up SendGrid in your settings.py
2. Run this script with: python manage.py shell < test_sendgrid.py 
3. Check the recipient email inbox to verify delivery
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
import sys
import os
import time

# Print configuration information
print(f"Using email backend: {settings.EMAIL_BACKEND}")
print(f"SendGrid sandbox mode: {getattr(settings, 'SENDGRID_SANDBOX_MODE_IN_DEBUG', 'Not configured')}")
print(f"From email: {settings.DEFAULT_FROM_EMAIL}")

# Test recipient - change this to your email address
TEST_EMAIL = "info@henrydjabamemorialfdn.org.gh"

# Check environment and configuration
print(f"\nPython version: {sys.version}")
print(f"Django version: {settings.DJANGO_VERSION if hasattr(settings, 'DJANGO_VERSION') else 'Not defined'}")

# Check if API key is configured
if not hasattr(settings, 'SENDGRID_API_KEY') or not settings.SENDGRID_API_KEY:
    print("\nERROR: SENDGRID_API_KEY is not configured in settings.py")
    print("Current value:", settings.SENDGRID_API_KEY if hasattr(settings, 'SENDGRID_API_KEY') else None)
    print("Environment variable exists:", 'SENDGRID_API_KEY' in os.environ)
    print("Make sure you've added the SendGrid API key to your settings file or environment.")
    sys.exit(1)

try:
    # Method 1: Direct email message sending (no waiting for response)
    print(f"\nSending test email to {TEST_EMAIL} (direct method)...")
    
    # Create the email message
    email = EmailMultiAlternatives(
        subject=f'{settings.EMAIL_SUBJECT_PREFIX} Direct Test Email',
        body='This is a test email from your Alumni Management System.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[TEST_EMAIL]
    )
    
    # Send without waiting for response
    print("Sending email...")
    email.send(fail_silently=True)
    print("Email dispatched to SendGrid. Check your inbox and SendGrid dashboard.")
    
    # Add a small delay for any background processing
    print("Pausing briefly...")
    time.sleep(1)
    
    print("\nTest completed! If you don't see any error messages, the email was accepted by SendGrid.")
    print("Note: Even if the test completes successfully, delivery may still fail if there are SendGrid configuration issues.")
    print("Check your SendGrid dashboard for delivery status and any bounces or errors.")
    
except Exception as e:
    print(f"\nERROR sending email: {e}")
    print("\nDEBUG INFORMATION:")
    print(f"- Email backend: {settings.EMAIL_BACKEND}")
    print(f"- From email: {settings.DEFAULT_FROM_EMAIL}")
    print(f"- SENDGRID_API_KEY exists: {'Yes' if hasattr(settings, 'SENDGRID_API_KEY') and settings.SENDGRID_API_KEY else 'No'}")
    print(f"- API key value (first 4 chars): {settings.SENDGRID_API_KEY[:4] + '...' if hasattr(settings, 'SENDGRID_API_KEY') and settings.SENDGRID_API_KEY else 'None'}")
    print(f"- SENDGRID_SANDBOX_MODE_IN_DEBUG: {getattr(settings, 'SENDGRID_SANDBOX_MODE_IN_DEBUG', 'Not set')}")
    print(f"- INSTALLED_APPS contains sendgrid_backend: {'Yes' if 'sendgrid_backend' in settings.INSTALLED_APPS else 'No'}")
    
    # Add instructions for common issues
    print("\nPOSSIBLE SOLUTIONS:")
    print("1. Make sure SENDGRID_API_KEY is set in your settings.py or environment")
    print("2. Check that django-sendgrid-v5 is installed: pip install django-sendgrid-v5")
    print("3. Verify your SendGrid API key is valid in your SendGrid account")
    print("4. Try setting SENDGRID_SANDBOX_MODE_IN_DEBUG = False temporarily to send real emails")
    print("5. Add 'sendgrid_backend' to your INSTALLED_APPS in settings.py")
    print("6. Check if your email domain matches your SendGrid verified sender")
    
    sys.exit(1)