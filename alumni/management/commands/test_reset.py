"""
Django management command to test password reset functionality directly.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import PasswordResetForm
from django.http import HttpRequest
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.conf import settings

class Command(BaseCommand):
    help = 'Test password reset functionality by directly triggering the form'
    
    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Email to send password reset to')
        
    def handle(self, *args, **options):
        email = options['email']
        self.stdout.write(self.style.SUCCESS(f"Testing password reset for email: {email}"))
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
            self.stdout.write(f"Found user: {user.username} ({user.email})")
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR(f"No user found with email: {email}"))
            self.stdout.write("Creating a test user...")
            username = email.split('@')[0]
            user = User.objects.create_user(
                username=username,
                email=email,
                password='temppassword'
            )
            self.stdout.write(f"Created test user: {username}")
        
        # Create a mock request
        request = HttpRequest()
        request.META['SERVER_NAME'] = 'localhost'
        request.META['SERVER_PORT'] = '8000'
        request.META['HTTP_HOST'] = 'localhost:8000'
        
        # Force print all relevant information
        self.stdout.write("\n=== EMAIL CONFIGURATION ===")
        self.stdout.write(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"SENDGRID_API_KEY exists: {'Yes' if settings.SENDGRID_API_KEY else 'No'}")
        self.stdout.write(f"SENDGRID_SANDBOX_MODE_IN_DEBUG: {settings.SENDGRID_SANDBOX_MODE_IN_DEBUG}")
        
        # Use Django's built-in PasswordResetForm to generate the email
        self.stdout.write("\n=== EXECUTING PASSWORD RESET ===")
        form = PasswordResetForm({'email': email})
        
        if form.is_valid():
            self.stdout.write("Form is valid")
            
            # Get the options that will be passed to send_mail
            opts = {
                'use_https': request.is_secure(),
                'token_generator': default_token_generator,
                'from_email': settings.DEFAULT_FROM_EMAIL,
                'email_template_name': 'alumni/password_reset_email.html',
                'subject_template_name': 'alumni/password_reset_subject.txt',
                'request': request,
                'html_email_template_name': None,
                'extra_email_context': None,
            }
            
            # Debug info
            self.stdout.write(f"Domain: {get_current_site(request).domain}")
            self.stdout.write(f"Protocol: {'https' if opts['use_https'] else 'http'}")
            
            # Generate token and UID for user
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Generate reset URL
            reset_url = f"http://localhost:8000{reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"
            self.stdout.write(f"Reset URL: {reset_url}")
            
            try:
                # Send the actual email
                form.save(**opts)
                self.stdout.write(self.style.SUCCESS("Password reset email sent successfully!"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error sending password reset email: {e}"))
        else:
            self.stdout.write(self.style.ERROR(f"Form is not valid: {form.errors}"))