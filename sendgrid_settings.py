"""
Django settings for alumni_management_system project with SendGrid email configuration.

This is a template file that shows how to integrate SendGrid into your settings.py.
Copy these changes to your main settings.py file when you're ready to implement SendGrid.
"""

# Import required libraries
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email settings with SendGrid
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

# Set to False in production to actually send emails
SENDGRID_SANDBOX_MODE_IN_DEBUG = True

# Email tracking features (optional)
SENDGRID_TRACK_EMAIL_OPENS = True
SENDGRID_TRACK_CLICKS_HTML = True

# Keep your existing email address configuration
DEFAULT_FROM_EMAIL = 'Alumni Management System <noreply@example.com>'
EMAIL_SUBJECT_PREFIX = '[Alumni Portal] '

# Add sendgrid_backend to your INSTALLED_APPS
# INSTALLED_APPS = [
#     ...existing apps...,
#     'sendgrid_backend',
# ]