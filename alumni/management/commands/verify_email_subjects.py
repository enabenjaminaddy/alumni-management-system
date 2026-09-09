"""
Command to verify email subjects with SendGrid templates.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from alumni.sendgrid_templates import TEMPLATE_IDS
import json
import time

class Command(BaseCommand):
    help = 'Tests SendGrid email subjects and verifies they work correctly'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            help='Email address to send the test to',
            required=True
        )
    
    def handle(self, *args, **options):
        test_email = options['email']
        self.stdout.write(f"Running email subject tests to {test_email}")
        
        # Try all different ways to set a subject
        self.test_standard_subject(test_email)
        time.sleep(2)
        self.test_dynamic_subject(test_email)
        time.sleep(2)
        self.test_both_methods(test_email)
        
        # Try different SendGrid templates
        self.test_both_templates(test_email)
        
        self.stdout.write(self.style.SUCCESS("All tests completed. Check your inbox and spam folder."))
    
    def test_standard_subject(self, email):
        self.stdout.write("\nTest 1: Using subject in Mail constructor...")
        try:
            message = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=email,
                subject=f"{settings.EMAIL_SUBJECT_PREFIX} Method 1: Direct Subject"
            )
            message.template_id = TEMPLATE_IDS['alumni_invitation']
            message.dynamic_template_data = {
                'first_name': 'Test',
                'last_name': 'User',
                'activation_link': 'https://example.com',
                'organization_name': 'Testing Organization',
            }
            
            # Print message details
            self.stdout.write(f"Subject: {message.subject}")
            self.stdout.write(f"Template ID: {message.template_id}")
            
            # Send email
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            self.stdout.write(self.style.SUCCESS(f"Response: {response.status_code}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
    
    def test_dynamic_subject(self, email):
        self.stdout.write("\nTest 2: Using subject in dynamic_template_data only...")
        try:
            message = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=email
            )
            message.template_id = TEMPLATE_IDS['alumni_invitation']
            message.dynamic_template_data = {
                'first_name': 'Test',
                'last_name': 'User',
                'activation_link': 'https://example.com',
                'organization_name': 'Testing Organization',
                'subject': f"{settings.EMAIL_SUBJECT_PREFIX} Method 2: Dynamic Data Subject",
            }
            
            # Print message details
            self.stdout.write(f"Subject: {message.subject if hasattr(message, 'subject') else 'Not directly set'}")
            self.stdout.write(f"Template ID: {message.template_id}")
            self.stdout.write(f"Subject in dynamic data: {message.dynamic_template_data.get('subject')}")
            
            # Send email
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            self.stdout.write(self.style.SUCCESS(f"Response: {response.status_code}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
    
    def test_both_methods(self, email):
        self.stdout.write("\nTest 3: Using subject in both places...")
        try:
            message = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=email,
                subject=f"{settings.EMAIL_SUBJECT_PREFIX} Method 3: DIRECT SUBJECT (should override)"
            )
            message.template_id = TEMPLATE_IDS['alumni_invitation']
            message.dynamic_template_data = {
                'first_name': 'Test',
                'last_name': 'User',
                'activation_link': 'https://example.com',
                'organization_name': 'Testing Organization',
                'subject': f"{settings.EMAIL_SUBJECT_PREFIX} Method 3: dynamic data subject (should not be used)",
            }
            
            # Print message details
            self.stdout.write(f"Subject: {message.subject}")
            self.stdout.write(f"Template ID: {message.template_id}")
            self.stdout.write(f"Subject in dynamic data: {message.dynamic_template_data.get('subject')}")
            
            # Send email
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            self.stdout.write(self.style.SUCCESS(f"Response: {response.status_code}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
    
    def test_both_templates(self, email):
        self.stdout.write("\nTest 4: Testing both templates with explicit subjects...")
        try:
            # Invitation template
            message = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=email,
                subject=f"{settings.EMAIL_SUBJECT_PREFIX} Invitation Template Test"
            )
            message.template_id = TEMPLATE_IDS['alumni_invitation']
            message.dynamic_template_data = {
                'first_name': 'Test',
                'last_name': 'User',
                'activation_link': 'https://example.com',
                'organization_name': 'Testing Organization',
                'subject': message.subject,
            }
            
            # Send email
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            self.stdout.write(self.style.SUCCESS(f"Invitation template response: {response.status_code}"))
            
            time.sleep(2)
            
            # Password reset template
            message = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=email,
                subject=f"{settings.EMAIL_SUBJECT_PREFIX} Password Reset Template Test"
            )
            message.template_id = TEMPLATE_IDS['password_reset']
            message.dynamic_template_data = {
                'username': 'testuser',
                'reset_url': 'https://example.com/reset',
                'domain': 'example.com',
                'site_name': 'Testing Site',
                'protocol': 'https',
                'subject': message.subject,
            }
            
            # Send email
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            self.stdout.write(self.style.SUCCESS(f"Password reset template response: {response.status_code}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))