# Setting Up SendGrid Email for Alumni Management System

## 1. Install Required Packages

Make sure the following packages are installed:

```bash
pip install -r requirements.txt
```

## 2. Create a SendGrid Account

1. Go to [SendGrid's website](https://sendgrid.com/) and create an account
2. Verify your account and complete the onboarding process
3. Create a SendGrid API Key:
   - Navigate to Settings > API Keys
   - Click "Create API Key"
   - Name it something like "Alumni Portal Email"
   - Select "Full Access" or "Restricted Access" with at least "Mail Send" permissions
   - Copy your API key (you won't be able to see it again!)

## 3. Update Django Settings

Update your `settings.py` file with the following configurations:

```python
# Email settings with SendGrid
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = 'YOUR_API_KEY_HERE'  # Replace with your actual API key

# Set to False in production
SENDGRID_SANDBOX_MODE_IN_DEBUG = True  # Set to False to actually send emails in debug mode

# For tracking email engagement (optional)
SENDGRID_TRACK_EMAIL_OPENS = True
SENDGRID_TRACK_CLICKS_HTML = True

# Use the same from email you've already configured
DEFAULT_FROM_EMAIL = 'Henry Djaba Memorial Foundation <noreply@henrydjaba.org>'
EMAIL_SUBJECT_PREFIX = '[HDMF Alumni Portal] '
```

## 4. Verify Your Domain/Sender Identity

1. In SendGrid dashboard, go to Settings > Sender Authentication
2. Set up either:
   - Domain Authentication (recommended): Authenticate your domain by adding DNS records
   - Single Sender Verification: Verify individual email addresses

## 5. Create Email Templates (Optional)

1. In SendGrid dashboard, go to Email API > Dynamic Templates
2. Create templates for different email types:
   - Alumni Invitation Email
   - Password Reset Email
   - Welcome Email

## 6. Test Configuration

Create a test script to verify your SendGrid integration:

```python
# test_sendgrid.py
from django.core.mail import send_mail

send_mail(
    subject='SendGrid Test Email',
    message='This is a test email from your Alumni Management System.',
    from_email='noreply@henrydjaba.org',
    recipient_list=['your-test-email@example.com'],
    fail_silently=False,
)
```

Run it with:

```bash
python manage.py shell < test_sendgrid.py
```

## 7. Environment Variables (Recommended for Production)

For security, store your API key in environment variables:

1. Install `python-dotenv` if you haven't already
2. Create a `.env` file in your project root:
   ```
   SENDGRID_API_KEY=your_api_key_here
   ```
3. Update your settings.py:

   ```python
   import os
   from dotenv import load_dotenv

   load_dotenv()

   SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
   ```

## Next Steps for Integration

1. Replace the current email functionality in `views.py` with SendGrid templates
2. Add email tracking analytics
3. Set up event webhooks for email tracking
