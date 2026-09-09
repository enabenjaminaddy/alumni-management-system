# SendGrid Template Integration

This document explains how the Alumni Management System integrates with SendGrid templates for email delivery.

## Overview

The system now uses SendGrid templates for two main email operations:
1. Alumni invitation emails
2. Password reset emails

Each operation uses a designated template in your SendGrid account.

## Configuration

### 1. Set Up Your Template IDs

Edit the `alumni/sendgrid_templates.py` file to add your actual template IDs:

```python
# Replace with your actual template IDs from SendGrid
ALUMNI_INVITATION_TEMPLATE_ID = 'd-your-template-id-for-alumni-invitation'
PASSWORD_RESET_TEMPLATE_ID = 'd-your-template-id-for-password-reset'
```

### 2. Template Variables

#### Alumni Invitation Template

The Alumni Invitation template should include these variables:
- `{{first_name}}` - Alumni's first name
- `{{last_name}}` - Alumni's last name
- `{{email}}` - Alumni's email address
- `{{activation_link}}` - Full URL to set the password
- `{{organization_name}}` - Organization name
- `{{uid}}` - User ID (encoded)
- `{{token}}` - Security token

Example template content:
```html
<h1>Welcome to the Alumni Portal, {{first_name}}!</h1>
<p>You have been invited to join the {{organization_name}} Alumni Portal.</p>
<p>Please click the link below to set your password and activate your account:</p>
<p><a href="{{activation_link}}">Activate Your Account</a></p>
```

#### Password Reset Template

The Password Reset template should include these variables:
- `{{username}}` - User's username
- `{{email}}` - User's email address
- `{{reset_url}}` - Full URL to reset password
- `{{domain}}` - Website domain
- `{{site_name}}` - Website name
- `{{protocol}}` - HTTP or HTTPS

Example template content:
```html
<h1>Password Reset Request</h1>
<p>You're receiving this email because you requested a password reset for your user account at {{site_name}}.</p>
<p>Please go to the following page and choose a new password:</p>
<p><a href="{{reset_url}}">Reset Your Password</a></p>
<p>Your username, in case you've forgotten: {{username}}</p>
```

## How It Works

### Invitation Emails

The system uses the `_send_alumni_invitation()` function in `alumni/views.py` to:
1. Create or identify a user account
2. Generate a password set link
3. Send an email using the SendGrid template

### Password Reset Emails

The system uses a custom `SendGridPasswordResetView` class in `alumni/password_reset.py` to:
1. Override the default Django password reset email functionality
2. Use SendGrid templates instead
3. Fall back to the standard email if SendGrid fails

## Fallback Mechanism

For both operations, if SendGrid template sending fails (e.g., API issues), the system will fall back to Django's standard email sending mechanism using the local templates.

## Testing

To test the SendGrid templates:
1. Use the "Send Invite" button in the Alumni List for invitation emails
2. Use the "Forgot Password" link on the login page for password reset emails