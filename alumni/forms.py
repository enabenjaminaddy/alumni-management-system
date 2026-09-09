from django.forms import ModelForm
from django import forms

from alumni.models import AlumniProfile, Announcement, MentorshipRequest

INPUT = 'form-input'
TEXTAREA = 'form-input'
CHECKBOX = 'rounded border-gray-300 text-org-secondary focus:ring-org-secondary'
SELECT = 'form-input'


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
