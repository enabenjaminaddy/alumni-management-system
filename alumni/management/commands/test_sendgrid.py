"""
Test SendGrid integration with the Alumni Management System.

How to use:
1. First ensure you've set up SendGrid in your settings.py
2. Run this command with: python manage.py test_sendgrid
3. Check the recipient email inbox to verify delivery
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.conf import settings
import django
import sys
import os
import time

class Command(BaseCommand):
    help = 'Tests SendGrid email configuration by sending a test email'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            default="info@henrydjabamemorialfdn.org.gh",
            help='Email address to send the test to',
        )
        parser.add_argument(
            '--delay',
            type=int,
            default=1,
            help='Delay in seconds after sending email',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f"Using email backend: {settings.EMAIL_BACKEND}"))
        self.stdout.write(f"SendGrid sandbox mode: {getattr(settings, 'SENDGRID_SANDBOX_MODE_IN_DEBUG', 'Not configured')}")
        self.stdout.write(f"From email: {settings.DEFAULT_FROM_EMAIL}")
        
        # Test recipient 
        TEST_EMAIL = options['email']
        
        # Check environment and configuration
        self.stdout.write(f"\nPython version: {sys.version}")
        self.stdout.write(f"Django version: {django.get_version()}")
        
        # Check if API key is configured
        if not hasattr(settings, 'SENDGRID_API_KEY') or not settings.SENDGRID_API_KEY:
            self.stdout.write(self.style.ERROR("\nERROR: SENDGRID_API_KEY is not configured in settings.py"))
            self.stdout.write(f"Current value: {settings.SENDGRID_API_KEY if hasattr(settings, 'SENDGRID_API_KEY') else None}")
            self.stdout.write(f"Environment variable exists: {'SENDGRID_API_KEY' in os.environ}")
            self.stdout.write("Make sure you've added the SendGrid API key to your settings file or environment.")
            return

        try:
            # Method 1: Direct email message sending (no waiting for response)
            self.stdout.write(f"\nSending test email to {TEST_EMAIL} (direct method)...")
            
            # Create the email message
            email = EmailMultiAlternatives(
                subject=f'{settings.EMAIL_SUBJECT_PREFIX} Direct Test Email',
                body='This is a test email from your Alumni Management System.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[TEST_EMAIL]
            )
            
            # Add HTML alternative content
            html_content = """
            <html>
                <body>
                    <h1 style="color: purple;">Alumni Management System</h1>
                    <p>This is a test email with <strong>HTML formatting</strong>.</p>
                    <p>If you can see this formatted text, HTML emails are working correctly.</p>
                    <a href="https://example.com/test-link">Test Link</a>
                </body>
            </html>
            """
            email.attach_alternative(html_content, "text/html")
            
            # Send without waiting for response
            self.stdout.write("Sending email...")
            email.send(fail_silently=False)
            self.stdout.write(self.style.SUCCESS("Email dispatched to SendGrid. Check your inbox and SendGrid dashboard."))
            
            # Add a small delay for any background processing
            self.stdout.write(f"Pausing for {options['delay']} second(s)...")
            time.sleep(options['delay'])
            
            self.stdout.write(self.style.SUCCESS("\nTest completed! If you don't see any error messages, the email was accepted by SendGrid."))
            self.stdout.write("Note: Even if the test completes successfully, delivery may still fail if there are SendGrid configuration issues.")
            self.stdout.write("Check your SendGrid dashboard for delivery status and any bounces or errors.")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nERROR sending email: {e}"))
            self.stdout.write(self.style.WARNING("\nDEBUG INFORMATION:"))
            self.stdout.write(f"- Email backend: {settings.EMAIL_BACKEND}")
            self.stdout.write(f"- From email: {settings.DEFAULT_FROM_EMAIL}")
            self.stdout.write(f"- SENDGRID_API_KEY exists: {'Yes' if hasattr(settings, 'SENDGRID_API_KEY') and settings.SENDGRID_API_KEY else 'No'}")
            
            # Safely check API key prefix
            if hasattr(settings, 'SENDGRID_API_KEY') and settings.SENDGRID_API_KEY:
                api_key_prefix = settings.SENDGRID_API_KEY[:4] + '...' if len(settings.SENDGRID_API_KEY) > 4 else '[Empty]'
                self.stdout.write(f"- API key value (first 4 chars): {api_key_prefix}")
            
            self.stdout.write(f"- SENDGRID_SANDBOX_MODE_IN_DEBUG: {getattr(settings, 'SENDGRID_SANDBOX_MODE_IN_DEBUG', 'Not set')}")
            self.stdout.write(f"- INSTALLED_APPS contains sendgrid_backend: {'Yes' if 'sendgrid_backend' in settings.INSTALLED_APPS else 'No'}")
            
            # Add instructions for common issues
            self.stdout.write(self.style.WARNING("\nPOSSIBLE SOLUTIONS:"))
            self.stdout.write("1. Make sure SENDGRID_API_KEY is set in your settings.py or environment")
            self.stdout.write("2. Check that django-sendgrid-v5 is installed: pip install django-sendgrid-v5")
            self.stdout.write("3. Verify your SendGrid API key is valid in your SendGrid account")
            self.stdout.write("4. Try setting SENDGRID_SANDBOX_MODE_IN_DEBUG = False temporarily to send real emails")
            self.stdout.write("5. Add 'sendgrid_backend' to your INSTALLED_APPS in settings.py")
            self.stdout.write("6. Check if your email domain matches your SendGrid verified sender")
            return