"""
Test password reset email functionality directly.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings

from alumni.password_reset import SendGridPasswordResetView

class Command(BaseCommand):
    help = 'Test password reset email functionality directly'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            required=True,
            help='Email address to send the test password reset to',
        )

    def handle(self, *args, **options):
        email = options['email']
        self.stdout.write(f"Testing password reset email to: {email}")
        
        # Find user by email
        user = User.objects.filter(email=email).first()
        if not user:
            self.stdout.write(self.style.ERROR(f"No user found with email: {email}"))
            return
        
        # Generate password reset token manually
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Prepare context similar to what the password reset view would use
        context = {
            'user': user,
            'token': token,
            'uid': uid,
            'domain': 'localhost:8000',  # Use your actual domain here
            'protocol': 'http',
            'site_name': 'HDMF Alumni Portal',
        }
        
        # Email settings
        from_email = settings.DEFAULT_FROM_EMAIL
        subject_template_name = 'alumni/password_reset_subject.txt'
        email_template_name = 'alumni/password_reset_email.html'
        
        self.stdout.write("Creating password reset view instance...")
        reset_view = SendGridPasswordResetView()
        
        self.stdout.write("Calling send_mail method directly...")
        try:
            # Call the send_mail method directly with our context
            reset_view.send_mail(
                subject_template_name=subject_template_name,
                email_template_name=email_template_name,
                context=context,
                from_email=from_email,
                to_email=[email],
            )
            self.stdout.write(self.style.SUCCESS("Password reset email sent successfully!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error sending password reset email: {e}"))