from django.db import models
from django.contrib.auth.models import User
import os
import time
import glob

# Create your models here.

def user_profile_image_path(instance, filename):
    """Generate file path for user profile images"""
    # Get file extension
    ext = filename.split('.')[-1]
    # Create filename using user ID, timestamp, and original extension
    timestamp = int(time.time())
    filename = f"profile_{instance.id}_{timestamp}.{ext}"
    return os.path.join('profile_images', filename)

EMPLOYMENT_STATUS_CHOICES = [
    ('employed', 'Employed'),
    ('self_employed', 'Self-Employed'),
    ('seeking', 'Seeking Employment'),
]

class AlumniProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alumni_profile', null=True, blank=True)
    profile_picture = models.ImageField(upload_to=user_profile_image_path, blank=True, null=True, help_text="Upload a passport-style photograph")
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
        return f"{self.first_name} {self.last_name}"
    
    def get_initials(self):
        """Get user initials for display when no profile picture"""
        first_initial = self.first_name[0].upper() if self.first_name else ''
        last_initial = self.last_name[0].upper() if self.last_name else ''
        return f"{first_initial}{last_initial}"
    
    def delete_profile_picture(self):
        """Delete the profile picture file from storage"""
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
            self.profile_picture = None
            self.save()
    
    def cleanup_old_profile_pictures(self):
        """Delete old profile picture files for this user"""
        from django.conf import settings
        if self.id:
            # Find all old profile pictures for this user
            profile_images_dir = os.path.join(settings.MEDIA_ROOT, 'profile_images')
            if os.path.exists(profile_images_dir):
                pattern = os.path.join(profile_images_dir, f"profile_{self.id}_*.*")
                old_files = glob.glob(pattern)
                
                # Keep the current file, delete the rest
                current_file = None
                if self.profile_picture:
                    current_file = self.profile_picture.path
                
                for file_path in old_files:
                    if current_file and os.path.abspath(file_path) != os.path.abspath(current_file):
                        try:
                            os.remove(file_path)
                        except (OSError, FileNotFoundError):
                            pass  # File already deleted or doesn't exist
    
    def save(self, *args, **kwargs):
        # Check if this is an update and profile picture changed
        if self.pk:
            try:
                old_instance = AlumniProfile.objects.get(pk=self.pk)
                if old_instance.profile_picture != self.profile_picture and old_instance.profile_picture:
                    # Profile picture changed, delete old file first
                    try:
                        if os.path.isfile(old_instance.profile_picture.path):
                            os.remove(old_instance.profile_picture.path)
                    except (OSError, FileNotFoundError):
                        pass
            except AlumniProfile.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Clean up any remaining old files after saving
        if self.pk:
            self.cleanup_old_profile_pictures()
