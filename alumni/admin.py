from django.contrib import admin
from alumni.models import AlumniProfile, Announcement, MentorshipRequest


@admin.register(AlumniProfile)
class AlumniProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'employment_status', 'graduation_year')
    search_fields = ('first_name', 'last_name', 'email', 'company_name')
    list_filter = ('employment_status', 'mentorship_interest', 'networking_interest')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'created_at', 'created_by')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'body')


@admin.register(MentorshipRequest)
class MentorshipRequestAdmin(admin.ModelAdmin):
    list_display = ('mentee', 'mentor', 'status', 'created_at')
    list_filter = ('status',)
