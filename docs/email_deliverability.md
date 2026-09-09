# Email Deliverability Best Practices

This document provides guidelines to help ensure your emails are delivered to the inbox rather than spam folders.

## Why Emails Go to Spam

Common reasons emails end up in spam folders:

1. **Missing or poor subject lines**
2. **Sender reputation issues**
3. **Email content triggers spam filters**
4. **Authentication issues (SPF, DKIM, DMARC)**
5. **Low engagement rates**
6. **High bounce rates**

## SendGrid Configuration Best Practices

### 1. Complete Sender Authentication

- **Domain Authentication**: Verify your sending domain in SendGrid
- **Link Branding**: Customize the links in your emails
- **Set up SPF, DKIM, and DMARC records** for your domain

### 2. Email Content Guidelines

- **Always include a meaningful subject line**
- Maintain a good text-to-image ratio (60:40)
- Avoid spam trigger words (free, guarantee, urgent, etc.)
- Include an unsubscribe link
- Use a recognizable sender name

### 3. Sending Practices

- **Warm up your IP address** gradually when starting out
- Send from a consistent IP address
- Maintain a consistent sending schedule
- Keep your bounce rate under 2%
- Keep your spam complaint rate under 0.1%

### 4. Testing and Monitoring

- Test emails with spam checking tools
- Monitor your sending reputation
- Review SendGrid stats regularly
- Use SendGrid's Event Webhook for tracking

## Specific Fixes for Our System

### Subject Line Fix

We've updated our email sending functions to:

1. **Always include a subject line**:

   ```python
   # Set a meaningful subject
   message.subject = "[HDMF Alumni Portal] Password Reset"
   ```

2. **Add subject to template data**:

   ```python
   # Make subject available in template
   dynamic_data['subject'] = subject_text
   ```

3. **Fall back to a default subject** if none is provided:
   ```python
   if not subject:
       default_subject = f"{settings.EMAIL_SUBJECT_PREFIX} Notification"
       message.subject = default_subject
   ```

### Debugging Enhancements

We've also added detailed logging in DEBUG mode:

- Email recipients
- Subject lines
- Template IDs
- Template variables
- API response codes

## Template Design Tips

1. **Use the subject variable in your template**:

   ```html
   <!-- In your SendGrid template -->
   <h1>{{subject}}</h1>
   ```

2. **Include your organization name** in the template:

   ```html
   <p>This email was sent by {{organization_name}}</p>
   ```

3. **Include a clear call to action**:
   ```html
   <a
     href="{{activation_link}}"
     style="background-color: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;"
     >Click to Activate</a
   >
   ```

## SendGrid Account Settings to Check

1. **Verify Sender Authentication**:

   - Go to Settings → Sender Authentication
   - Make sure both domain authentication and link branding are verified

2. **Check IP Reputation**:

   - Go to Settings → IP Addresses
   - Check your IP reputation score (should be above 90%)

3. **Review Mail Settings**:
   - Go to Settings → Mail Settings
   - Enable event notification if you want detailed tracking
4. **Check Suppression Lists**:
   - Go to Suppressions
   - Make sure recipient emails aren't on the bounce or block lists
