"""
Command to verify SendGrid is working correctly.
This checks installation, API key and performs basic tests.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import sys
import importlib
import time

class Command(BaseCommand):
    help = 'Verify SendGrid is configured correctly and working'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=== SendGrid Verification Tool ==="))
        
        # Check 1: Check if sendgrid module is installed
        self.stdout.write("\n1. Checking if sendgrid package is installed...")
        try:
            import sendgrid
            self.stdout.write(self.style.SUCCESS(f"✓ SendGrid installed (version: {sendgrid.__version__})"))
        except ImportError:
            self.stdout.write(self.style.ERROR("✗ SendGrid not installed!"))
            self.stdout.write("   Run: pip install sendgrid==6.11.0")
            return
        
        # Check 2: Check if django-sendgrid-v5 is installed
        self.stdout.write("\n2. Checking if django-sendgrid-v5 package is installed...")
        try:
            import sendgrid_backend
            self.stdout.write(self.style.SUCCESS("✓ django-sendgrid-v5 installed"))
        except ImportError:
            self.stdout.write(self.style.ERROR("✗ django-sendgrid-v5 not installed!"))
            self.stdout.write("   Run: pip install django-sendgrid-v5==1.2.3")
            return
        
        # Check 3: Check settings
        self.stdout.write("\n3. Checking Django settings...")
        
        if 'sendgrid_backend' in settings.INSTALLED_APPS:
            self.stdout.write(self.style.SUCCESS("✓ sendgrid_backend in INSTALLED_APPS"))
        else:
            self.stdout.write(self.style.ERROR("✗ sendgrid_backend missing from INSTALLED_APPS!"))
            self.stdout.write("   Add 'sendgrid_backend' to INSTALLED_APPS in settings.py")
        
        if settings.EMAIL_BACKEND == 'sendgrid_backend.SendgridBackend':
            self.stdout.write(self.style.SUCCESS("✓ EMAIL_BACKEND set to SendgridBackend"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠ EMAIL_BACKEND not set to SendgridBackend!"))
            self.stdout.write(f"   Current value: {settings.EMAIL_BACKEND}")
            self.stdout.write("   Should be: 'sendgrid_backend.SendgridBackend'")
        
        # Check 4: Check API key
        self.stdout.write("\n4. Checking SendGrid API key...")
        
        api_key = settings.SENDGRID_API_KEY
        if api_key:
            masked_key = f"{api_key[:5]}...{api_key[-4:]}" if len(api_key) > 10 else "[too short]"
            self.stdout.write(self.style.SUCCESS(f"✓ SENDGRID_API_KEY found in settings: {masked_key}"))
            
            # Check environment variable
            env_key = os.environ.get('SENDGRID_API_KEY')
            if env_key:
                self.stdout.write(self.style.SUCCESS("✓ SENDGRID_API_KEY also found in environment variables"))
            else:
                self.stdout.write(self.style.WARNING("⚠ SENDGRID_API_KEY not found in environment variables"))
        else:
            self.stdout.write(self.style.ERROR("✗ SENDGRID_API_KEY not set in settings!"))
            self.stdout.write("   Check your .env file or environment variables")
            return
        
        # Check 5: Check SendGrid sandbox mode
        self.stdout.write("\n5. Checking SendGrid sandbox mode...")
        
        if hasattr(settings, 'SENDGRID_SANDBOX_MODE_IN_DEBUG'):
            if settings.SENDGRID_SANDBOX_MODE_IN_DEBUG:
                self.stdout.write(self.style.WARNING("⚠ SENDGRID_SANDBOX_MODE_IN_DEBUG is enabled! Emails will not be sent in DEBUG mode."))
            else:
                self.stdout.write(self.style.SUCCESS("✓ SENDGRID_SANDBOX_MODE_IN_DEBUG is disabled. Emails will be sent."))
        else:
            self.stdout.write(self.style.WARNING("⚠ SENDGRID_SANDBOX_MODE_IN_DEBUG not configured."))
        
        # Check 6: Verify templates
        self.stdout.write("\n6. Checking SendGrid templates...")
        
        try:
            from alumni.sendgrid_templates import TEMPLATE_IDS
            self.stdout.write(self.style.SUCCESS("✓ SendGrid template configuration found"))
            
            for name, template_id in TEMPLATE_IDS.items():
                if template_id and template_id.startswith('d-'):
                    self.stdout.write(self.style.SUCCESS(f"✓ Template ID for {name}: {template_id}"))
                else:
                    self.stdout.write(self.style.ERROR(f"✗ Invalid template ID for {name}: {template_id}"))
        except ImportError:
            self.stdout.write(self.style.ERROR("✗ SendGrid template configuration not found"))
        
        # Check 7: Try to validate API key
        self.stdout.write("\n7. Validating SendGrid API key...")
        
        try:
            from sendgrid import SendGridAPIClient
            sg = SendGridAPIClient(api_key)
            
            # Just check if we can get account info (doesn't send any emails)
            response = sg.client.user.credits.get()
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("✓ SendGrid API key is valid! API connection successful."))
            else:
                self.stdout.write(self.style.ERROR(f"✗ API returned status code: {response.status_code}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error validating API key: {str(e)}"))
        
        # Final verdict
        self.stdout.write("\n=== Summary ===")
        self.stdout.write("SendGrid should be working if all checks have passed.")
        self.stdout.write("If you're still having issues, check the email logs for error messages.")
        self.stdout.write("Remember that password resets use both regular Django views and the SendGrid backend.")
        self.stdout.write("Try using the test commands to send test emails directly.")