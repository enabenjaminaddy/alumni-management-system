from django.db import models

# Create your models here.

EMPLOYMENT_STATUS_CHOICES = [
    ('employed', 'Employed'),
    ('self_employed', 'Self-Employed'),
    ('seeking', 'Seeking Employment'),
]

class AlumniProfile(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    current_address = models.CharField(max_length=500, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    social_media_accounts = models.TextField(blank=True, null=True, help_text="List of social media links/accounts")
    
    graduation_year = models.PositiveIntegerField(blank=True, null=True)
    course_studied = models.CharField(max_length=255, blank=True, null=True)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_location = models.CharField(max_length=255, blank=True, null=True)
    
    skills_acquired = models.TextField(blank=True, null=True)
    work_experience = models.TextField(blank=True, null=True)
    monthly_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    monthly_investment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    testimonial = models.TextField(blank=True, null=True, help_text="Quote or story about their experience with the training program")
    mentorship_interest = models.BooleanField(default=False, help_text="Interest in mentoring current students")
    networking_interest = models.BooleanField(default=False, help_text="Interest in attending alumni events")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name
