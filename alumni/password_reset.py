"""
Custom password reset views that use SendGrid templates.
"""
from django.contrib.auth.views import PasswordResetView
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from alumni.sendgrid_templates import TEMPLATE_IDS

class SendGridPasswordResetView(PasswordResetView):
    """Custom password reset view that uses SendGrid templates."""
    
    def send_mail(
        self, subject_template_name, email_template_name, 
        context, from_email, to_email, html_email_template_name=None
    ):
        """Override send_mail to use SendGrid templates."""
        
        # Get the user and token from the context
        user = context['user']
        token = context['token']
        uid = context['uid']
        
        # Get the domain and site_name from the context
        domain = context['domain']
        site_name = context['site_name']
        
        # Create the reset URL with protocol (this was missing!)
        protocol = context['protocol']
        reset_url = f"{protocol}://{domain}/reset/{uid}/{token}/"
        
        # Print debug info regardless of DEBUG setting
        print(f"Password reset requested for: {to_email[0]}")
        print(f"Reset URL generated: {reset_url}")
        
        # Get the SendGrid template ID
        template_id = TEMPLATE_IDS['password_reset']
        
        # Create dynamic data for the template
        dynamic_data = {
            'username': user.get_username(),
            'email': to_email[0],
            'reset_url': reset_url,
            'domain': domain,
            'site_name': site_name,
            'uid': uid,
            'token': token,
            'protocol': context['protocol'],
        }
        
        # First try SendGrid template
        try:
            print(f"\n--- SENDING PASSWORD RESET EMAIL ---")
            print(f"From: {from_email}")
            print(f"To: {to_email[0]}")
            print(f"Template ID: {template_id}")
            
            # Create SendGrid message
            message = Mail(
                from_email=from_email,
                to_emails=to_email[0]
            )
            
            # Add template
            message.template_id = template_id
            
            # Set subject explicitly to prevent spam filtering
            subject_text = "Password Reset"
            if hasattr(settings, 'EMAIL_SUBJECT_PREFIX') and settings.EMAIL_SUBJECT_PREFIX:
                subject_text = f"{settings.EMAIL_SUBJECT_PREFIX} {subject_text}"
            
            # Ensure the subject is set directly on the message
            message.subject = subject_text
            
            # Add subject to dynamic data so it can be used in template
            dynamic_data['subject'] = subject_text
            
            # Double check subject is set (Debug output)
            if settings.DEBUG:
                print(f"Debug: Setting password reset email subject to: '{subject_text}'")
                
            # Force message headers to include subject if needed
            if hasattr(settings, 'SENDGRID_TEMPLATE_SUBJECT_OVERRIDE') and settings.SENDGRID_TEMPLATE_SUBJECT_OVERRIDE:
                print(f"Debug: Using subject override for password reset: '{subject_text}'")
            
            # Add dynamic data
            message.dynamic_template_data = dynamic_data
            
            # Print debug info if in DEBUG mode
            if settings.DEBUG:
                print(f"Sending password reset email to: {to_email[0]}")
                print(f"Subject: {subject_text}")
                print(f"Template ID: {template_id}")
                import json
                print(f"Template data: {json.dumps(dynamic_data, indent=2)}")
            
            # Get API client and send
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            
            # Print response info if in debug mode
            if settings.DEBUG:
                print(f"SendGrid API response: {response.status_code}")
                if not (200 <= response.status_code < 300):
                    print(f"SendGrid response body: {response.body}")
            
        except Exception as e:
            # On failure, fall back to the default method
            print(f"\n!!! PASSWORD RESET EMAIL ERROR !!!")
            print(f"SendGrid failed with error: {str(e)}")
            print(f"API Key exists: {'Yes' if settings.SENDGRID_API_KEY else 'No'}")
            print(f"API Key starts with: {settings.SENDGRID_API_KEY[:5] + '...' if settings.SENDGRID_API_KEY else 'N/A'}")
            print(f"Template ID used: {template_id}")
            print(f"Falling back to default email method...")
            
            # Get the subject and body
            subject = loader.render_to_string(subject_template_name, context)
            subject = ''.join(subject.splitlines())
            body = loader.render_to_string(email_template_name, context)
            
            # Create the email message
            email_message = EmailMultiAlternatives(subject, body, from_email, to_email)
            
            # Add HTML content if available
            if html_email_template_name is not None:
                html_email = loader.render_to_string(html_email_template_name, context)
                email_message.attach_alternative(html_email, 'text/html')
                
            # Print debug info for the fallback email
            print(f"Sending fallback email with subject: {subject}")
            print(f"To: {to_email[0]}")
            
            # Send the email
            try:
                email_message.send()
                print(f"Fallback email sent successfully")
            except Exception as fallback_error:
                print(f"ERROR: Fallback email also failed: {str(fallback_error)}")