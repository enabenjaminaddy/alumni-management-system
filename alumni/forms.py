from django.forms import ModelForm
from alumni.models import AlumniProfile
from django import forms


class AlumniProfileForm(ModelForm):
    class Meta:
        model = AlumniProfile
        fields = [
            'profile_picture', 'first_name', 'last_name', 'current_address', 'phone_number',
            'email', 'social_media_accounts', 'graduation_year', 
            'course_studied', 'employment_status', 'company_name',
            'company_location', 'skills_acquired', 'work_experience',
            'monthly_savings', 'monthly_investment', 'testimonial',
            'mentorship_interest', 'networking_interest'
        ]
        widgets = {
            'social_media_accounts': forms.Textarea(attrs={'rows': 3}),
            'testimonial': forms.Textarea(attrs={'rows': 4}),
            'skills_acquired': forms.Textarea(attrs={'rows': 3}),
            'work_experience': forms.Textarea(attrs={'rows': 3}),
        }