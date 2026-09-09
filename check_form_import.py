"""
Simple script to check if our custom form can be imported
"""
import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_management_system.settings')
django.setup()

print("Testing form import...")

try:
    # Test basic imports first
    from django.contrib.auth.forms import PasswordResetForm
    print("✓ Base PasswordResetForm imported successfully")
    
    from alumni.sendgrid_templates import TEMPLATE_IDS
    print("✓ SendGrid templates imported successfully")
    
    from alumni.forms import SendGridPasswordResetForm
    print("✓ Custom SendGridPasswordResetForm imported successfully")
    
    # Test form instantiation
    form = SendGridPasswordResetForm()
    print("✓ Custom form instantiated successfully")
    
    print("\n=== SUCCESS ===")
    print("All imports working correctly!")
    print("The custom form should be used for password resets.")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Other error: {e}")