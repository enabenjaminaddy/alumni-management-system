"""
Test script for diagnosing email subject issues with SendGrid templates
"""
import os
import json
import django
import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_management_system.settings')
django.setup()

from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from alumni.sendgrid_templates import TEMPLATE_IDS

def test_sendgrid_subjects():
    """Test how subjects are handled with SendGrid templates"""
    print(f"DEBUG: Using SendGrid API Key: {settings.SENDGRID_API_KEY[:5]}...{settings.SENDGRID_API_KEY[-4:] if settings.SENDGRID_API_KEY else None}")
    print(f"DEBUG: EMAIL_SUBJECT_PREFIX = '{settings.EMAIL_SUBJECT_PREFIX}'")
    print(f"DEBUG: DEFAULT_FROM_EMAIL = '{settings.DEFAULT_FROM_EMAIL}'")
    
    # Test recipient email
    test_email = "your-test-email@example.com"  # Replace with your test email
    
    # Test with subject directly in Mail constructor
    try:
        print("\n1. Testing with subject in Mail constructor...")
        message1 = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=test_email,
            subject=f"{settings.EMAIL_SUBJECT_PREFIX} Direct Subject Test"
        )
        message1.template_id = TEMPLATE_IDS['alumni_invitation']
        message1.dynamic_template_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'activation_link': 'https://example.com',
            'organization_name': 'Test Org'
        }
        
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message1)
        print(f"Response status code: {response.status_code}")
        print(f"Headers: {response.headers}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    time.sleep(2)  # Wait between tests
    
    # Test with subject in template data
    try:
        print("\n2. Testing with subject in template data...")
        message2 = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=test_email
        )
        message2.template_id = TEMPLATE_IDS['alumni_invitation']
        message2.dynamic_template_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'activation_link': 'https://example.com',
            'organization_name': 'Test Org',
            'subject': f"{settings.EMAIL_SUBJECT_PREFIX} Subject in Template Data"
        }
        
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message2)
        print(f"Response status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    time.sleep(2)  # Wait between tests
    
    # Test with both
    try:
        print("\n3. Testing with subject in both places...")
        message3 = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=test_email,
            subject=f"{settings.EMAIL_SUBJECT_PREFIX} Direct Subject (Should Override)"
        )
        message3.template_id = TEMPLATE_IDS['alumni_invitation']
        message3.dynamic_template_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'activation_link': 'https://example.com',
            'organization_name': 'Test Org',
            'subject': f"{settings.EMAIL_SUBJECT_PREFIX} Subject in Template Data (Should Not Be Used)"
        }
        
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message3)
        print(f"Response status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {str(e)}")
        
    print("\nTests completed. Check your email inbox and spam folder.")

if __name__ == "__main__":
    test_sendgrid_subjects()