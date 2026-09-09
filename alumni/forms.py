from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import PasswordResetForm as BasePasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.template import loader

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from alumni.sendgrid_templates import TEMPLATE_IDS

from alumni.models import AlumniProfile, Announcement, MentorshipRequest

INPUT = 'form-input'
TEXTAREA = 'form-input'
CHECKBOX = 'rounded border-gray-300 text-org-secondary focus:ring-org-secondary'
SELECT = 'form-input'


from alumni.models import AlumniProfile

class AlumniProfileForm(forms.ModelForm):
    """Form for alumni profile data"""
    class Meta:
        model = AlumniProfile
<<<<<<< HEAD
        fields = [
            'profile_picture', 'first_name', 'last_name', 'current_address', 'phone_number',
            'email', 'social_media_accounts', 'graduation_year',
            'course_studied', 'employment_status', 'company_name',
            'company_location', 'skills_acquired', 'work_experience',
            'monthly_savings', 'monthly_investment', 'testimonial',
            'mentorship_interest', 'networking_interest'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': INPUT}),
            'last_name': forms.TextInput(attrs={'class': INPUT}),
            'current_address': forms.TextInput(attrs={'class': INPUT}),
            'phone_number': forms.TextInput(attrs={'class': INPUT}),
            'email': forms.EmailInput(attrs={'class': INPUT}),
            'graduation_year': forms.NumberInput(attrs={'class': INPUT}),
            'course_studied': forms.TextInput(attrs={'class': INPUT}),
            'employment_status': forms.Select(attrs={'class': SELECT}),
            'company_name': forms.TextInput(attrs={'class': INPUT}),
            'company_location': forms.TextInput(attrs={'class': INPUT}),
            'monthly_savings': forms.NumberInput(attrs={'class': INPUT, 'step': '0.01'}),
            'monthly_investment': forms.NumberInput(attrs={'class': INPUT, 'step': '0.01'}),
            'social_media_accounts': forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA}),
            'testimonial': forms.Textarea(attrs={'rows': 4, 'class': TEXTAREA}),
            'skills_acquired': forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA}),
            'work_experience': forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA}),
            'mentorship_interest': forms.CheckboxInput(attrs={'class': CHECKBOX}),
            'networking_interest': forms.CheckboxInput(attrs={'class': CHECKBOX}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'text-sm'}),
        }


class AnnouncementForm(ModelForm):
    notify_alumni = forms.BooleanField(
        required=False,
        initial=False,
        label='Email alumni about this',
        help_text='Sends to everyone with an email on file.',
        widget=forms.CheckboxInput(attrs={'class': CHECKBOX}),
    )

    class Meta:
        model = Announcement
        fields = ['title', 'body', 'category', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT}),
            'body': forms.Textarea(attrs={'rows': 6, 'class': TEXTAREA}),
            'category': forms.Select(attrs={'class': SELECT}),
            'is_published': forms.CheckboxInput(attrs={'class': CHECKBOX}),
        }


class MentorshipRequestForm(forms.ModelForm):
    class Meta:
        model = MentorshipRequest
        fields = ['mentor', 'message']
        widgets = {
            'mentor': forms.Select(attrs={'class': SELECT}),
            'message': forms.Textarea(attrs={
                'rows': 3,
                'class': TEXTAREA,
                'placeholder': 'Optional note to your mentor...',
            }),
        }

    def __init__(self, *args, mentee=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.mentee = mentee
        mentors = AlumniProfile.objects.filter(mentorship_interest=True).order_by(
            'first_name', 'last_name'
        )
        if mentee:
            mentors = mentors.exclude(pk=mentee.pk)
            already = MentorshipRequest.objects.filter(mentee=mentee).values_list(
                'mentor_id', flat=True
            )
            mentors = mentors.exclude(pk__in=already)
        self.fields['mentor'].queryset = mentors
        self.fields['mentor'].label_from_instance = (
            lambda obj: f"{obj.first_name} {obj.last_name}"
            + (f" — {obj.company_name}" if obj.company_name else "")
        )


class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV file',
        help_text='Needs at least: email, first_name, last_name',
        widget=forms.ClearableFileInput(attrs={'class': 'text-sm', 'accept': '.csv'}),
    )
=======
        fields = '__all__'  # You can customize this later


print("\n***** LOADING SENDGRID PASSWORD RESET FORM *****\n")

class SendGridPasswordResetForm(BasePasswordResetForm):
    """
    Custom password reset form that uses SendGrid templates for emails.
    """
    
    def __init__(self, *args, **kwargs):
        print("\n***** SENDGRID PASSWORD RESET FORM INITIALIZED *****\n")
        super().__init__(*args, **kwargs)

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a SendGrid template email to the user for password reset.
        Fixed version that properly handles from_email and uses proven SendGrid integration.
        """
        print("\n***** CUSTOM SENDGRID SEND_MAIL METHOD CALLED *****\n")
        print(f"Email being sent to: {to_email}")
        
        # CRITICAL FIX: Ensure from_email is set (this was the root cause)
        if not from_email:
            from django.conf import settings
            from_email = settings.DEFAULT_FROM_EMAIL
            print(f"Fixed from_email to: {from_email}")
        
        # Get the user from context
        user = context['user']
        
        # Create reset URL with proper protocol
        protocol = context.get('protocol', 'http')
        domain = context['domain']
        uid = context['uid']
        token = context['token']
        reset_url = f"{protocol}://{domain}/reset/{uid}/{token}/"
        
        print(f"Password reset requested for: {to_email[0] if isinstance(to_email, list) else to_email}")
        print(f"Reset URL generated: {reset_url}")
        
        # Import the helper function to maintain consistency with invitation emails
        from alumni.views import send_sendgrid_template_email
        from django.utils import timezone
        
        # Create dynamic data for SendGrid template (matching template variables)
        dynamic_data = {
            'user': {
                'first_name': user.first_name or user.get_username(),
                'last_name': user.last_name or '',
                'username': user.get_username(),
            },
            'username': user.get_username(),
            'email': to_email[0] if isinstance(to_email, list) else to_email,
            'reset_password_url': reset_url,  # This matches the template variable name
            'reset_url': reset_url,  # Keep this for backward compatibility
            'domain': domain,
            'site_name': context.get('site_name', 'Alumni Portal'),
            'uid': uid,
            'token': token,
            'protocol': protocol,
            'current_year': timezone.now().year,
        }
        
        # Get subject for email
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())  # Remove newlines
        
        # Get template ID
        template_id = TEMPLATE_IDS['password_reset']
        print(f"Using SendGrid template ID: {template_id}")
        
        # Use the shared helper function like the invitation system does
        try:
            email_sent = send_sendgrid_template_email(
                to_email=to_email[0] if isinstance(to_email, list) else to_email,
                template_id=template_id,
                dynamic_data=dynamic_data,
                subject=subject
            )
            
            if email_sent:
                print("Password reset email sent successfully via SendGrid")
                return
            else:
                print("SendGrid failed, falling back to Django email method")
                
        except Exception as e:
            print(f"SendGrid error: {str(e)}")
        
        # Fallback to default email method if SendGrid fails
        print("Using Django default email method as fallback")
        super().send_mail(
            subject_template_name, email_template_name, context, 
            from_email, to_email, html_email_template_name
        )
>>>>>>> 823cd9a1f049d4ba3da43adb895bd692246c80fb
