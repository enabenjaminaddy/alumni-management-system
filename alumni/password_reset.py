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
        
        # Create the reset URL
        reset_url = f"{domain}/reset/{uid}/{token}/"
        
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
            # Create SendGrid message
            message = Mail(
                from_email=from_email,
                to_emails=to_email[0]
            )
            
            # Add template
            message.template_id = template_id
            
            # Add dynamic data
            message.dynamic_template_data = dynamic_data
            
            # Get API client and send
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            sg.send(message)
            
        except Exception as e:
            # On failure, fall back to the default method
            print(f"SendGrid failed, falling back to default: {str(e)}")
            
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
                
            # Send the email
            email_message.send()