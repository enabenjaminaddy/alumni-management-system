"""
Test script for SendGrid integration with the Alumni Management System.

How to use:
1. First ensure you've set up SendGrid in your settings.py
2. Run this script with: python manage.py shell < test_sendgrid.py 
3. Check the recipient email inbox to verify delivery
"""

from django.core.mail import send_mail
from django.conf import settings
import sys

# Print configuration information
print(f"Using email backend: {settings.EMAIL_BACKEND}")
print(f"SendGrid sandbox mode: {getattr(settings, 'SENDGRID_SANDBOX_MODE_IN_DEBUG', 'Not configured')}")
print(f"From email: {settings.DEFAULT_FROM_EMAIL}")

# Test recipient - change this to your email address
TEST_EMAIL = "your-email@example.com"

try:
    # Basic email test
    print(f"\nSending test email to {TEST_EMAIL}...")
    send_mail(
        subject=f'{settings.EMAIL_SUBJECT_PREFIX} Test Email',
        message='This is a test email from your Alumni Management System.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[TEST_EMAIL],
        fail_silently=False,
    )
    print("Test email sent successfully!")
    
    # Test email with HTML content
    print("\nSending HTML test email...")
    send_mail(
        subject=f'{settings.EMAIL_SUBJECT_PREFIX} HTML Test Email',
        message='This is a test email with HTML content.',
        html_message="""
        <html>
            <body>
                <h1 style="color: purple;">Alumni Management System</h1>
                <p>This is a test email with <strong>HTML formatting</strong>.</p>
                <p>If you can see this formatted text, HTML emails are working correctly.</p>
                <a href="https://example.com/test-link">Test Link</a>
            </body>
        </html>
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[TEST_EMAIL],
        fail_silently=False,
    )
    print("HTML test email sent successfully!")
    
except Exception as e:
    print(f"Error sending email: {e}")
    sys.exit(1)