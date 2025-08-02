"""
Debug script to test password reset functionality directly.

This script traces through all the imports and view initialization
to identify any issues with the password reset functionality.
"""
import os
import django
import sys
import traceback

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_management_system.settings')
os.environ['DEBUG'] = 'True'  # Force debug mode

print("\n--- INITIALIZING DJANGO ---")
try:
    django.setup()
    print("Django setup completed successfully")
except Exception as e:
    print(f"Django setup error: {e}")
    traceback.print_exc()
    sys.exit(1)

# Import Django settings
try:
    print("\n--- IMPORTING SETTINGS ---")
    from django.conf import settings
    print(f"DEBUG: {settings.DEBUG}")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"SENDGRID_API_KEY exists: {'Yes' if settings.SENDGRID_API_KEY else 'No'}")
    print(f"SENDGRID_SANDBOX_MODE_IN_DEBUG: {settings.SENDGRID_SANDBOX_MODE_IN_DEBUG}")
except Exception as e:
    print(f"Settings import error: {e}")
    traceback.print_exc()

# Import URLs to force URL patterns to be loaded
try:
    print("\n--- IMPORTING URLS ---")
    from alumni import urls
    print(f"URL patterns loaded: {len(urls.urlpatterns)} patterns")
    
    # Find password reset URL
    password_reset_urls = [url for url in urls.urlpatterns if getattr(url, 'name', '') == 'password_reset']
    if password_reset_urls:
        print(f"Password reset URL found: {password_reset_urls[0].pattern}")
    else:
        print("Password reset URL not found in urlpatterns")
except Exception as e:
    print(f"URL import error: {e}")
    traceback.print_exc()

# Import custom password reset view
try:
    print("\n--- IMPORTING PASSWORD RESET VIEW ---")
    from alumni.password_reset import SendGridPasswordResetView
    print("SendGridPasswordResetView imported successfully")
except Exception as e:
    print(f"View import error: {e}")
    traceback.print_exc()

# Test instantiating the view
try:
    print("\n--- INSTANTIATING PASSWORD RESET VIEW ---")
    view_instance = SendGridPasswordResetView()
    print("SendGridPasswordResetView instantiated successfully")
    print(f"View attributes: {dir(view_instance)}")
except Exception as e:
    print(f"View instantiation error: {e}")
    traceback.print_exc()

# Test the form
try:
    print("\n--- TESTING PASSWORD RESET FORM ---")
    from django.contrib.auth.forms import PasswordResetForm
    form = PasswordResetForm()
    print("Form fields:", form.fields.keys())
except Exception as e:
    print(f"Form error: {e}")
    traceback.print_exc()

print("\n--- DEBUG COMPLETE ---")