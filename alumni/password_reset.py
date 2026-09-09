"""
Custom password reset views that use SendGrid templates.
"""
from django.contrib.auth.views import PasswordResetView
from alumni.forms import SendGridPasswordResetForm
from django.conf import settings

print("\n***** LOADING SENDGRID PASSWORD RESET VIEW *****\n")

class SendGridPasswordResetView(PasswordResetView):
    """
    Custom password reset view that uses SendGrid templates by using our custom form.
    """
    # Use our custom form that properly sends with SendGrid
    form_class = SendGridPasswordResetForm
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("\n***** SENDGRID PASSWORD RESET VIEW INITIALIZED *****\n")
    
    def form_valid(self, form):
        print("\n***** PASSWORD RESET FORM SUBMITTED *****\n")
        print(f"Email requested: {form.cleaned_data.get('email')}")
        return super().form_valid(form)