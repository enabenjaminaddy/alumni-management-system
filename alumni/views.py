from django.shortcuts import render, redirect, get_object_or_404
from alumni.forms import (
    AlumniProfileForm,
    AnnouncementForm,
    MentorshipRequestForm,
    CSVImportForm,
)
from alumni.models import AlumniProfile, Announcement, MentorshipRequest
from alumni.utils import get_user_role, is_organization_admin, is_alumni, get_dashboard_url_for_role
from alumni.import_utils import parse_alumni_csv, commit_alumni_rows
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Exists, OuterRef, Count, Avg
from django.conf import settings
import csv
import json
import os
from django.utils import timezone
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import login
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_POST

# Create your views here.
@login_required
def home(request):
    """Alumni dashboard - only for alumni users"""
    user_role = get_user_role(request.user)
    
    # Redirect non-alumni users to their appropriate dashboards
    if user_role == 'system_admin':
        return redirect('/admin/')
    elif user_role == 'organization_admin':
        return redirect('org_admin_dashboard')
    elif user_role == 'no_role':
        messages.error(request, 'You do not have the required permissions to access this area.')
        return redirect('login')
    
    # For alumni users, show their dashboard
    latest_announcements = Announcement.objects.filter(is_published=True)[:3]
    mentorship_incoming = []
    mentorship_outgoing = []
    try:
        profile = request.user.alumni_profile
        mentorship_incoming = MentorshipRequest.objects.filter(
            mentor=profile, status='pending'
        ).select_related('mentee')
        mentorship_outgoing = MentorshipRequest.objects.filter(
            mentee=profile
        ).select_related('mentor')[:5]
    except AlumniProfile.DoesNotExist:
        profile = None

    context = {
        'user_role': user_role,
        'user': request.user,
        'latest_announcements': latest_announcements,
        'profile': profile,
        'mentorship_incoming': mentorship_incoming,
        'mentorship_outgoing': mentorship_outgoing,
    }
    return render(request, 'alumni/home.html', context)

@login_required
@user_passes_test(is_alumni, login_url='login')
def edit_form(request):
    # Get or create profile for the current user
    try:
        profile = request.user.alumni_profile
        has_existing_profile = True
    except AlumniProfile.DoesNotExist:
        profile = None
        has_existing_profile = False
    
    if request.method == 'POST':
        if profile:
            form = AlumniProfileForm(request.POST, request.FILES, instance=profile)
        else:
            form = AlumniProfileForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                alumni_profile = form.save(commit=False)
                alumni_profile.user = request.user
                alumni_profile.save()
                if 'profile_picture' in request.FILES:
                    messages.success(request, 'Profile picture uploaded and profile updated successfully!')
                else:
                    messages.success(request, 'Profile updated successfully!')
                return render(request, "alumni/successful_form.html", {
                    'user': request.user,
                    'profile': alumni_profile
                })
            except Exception as e:
                messages.error(request, f'Error saving profile: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
            # Add specific field errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        if profile:
            form = AlumniProfileForm(instance=profile)
            messages.info(request, 'Edit your profile details below. Your current information is displayed.')
        else:
            form = AlumniProfileForm()
            messages.info(request, 'Create your alumni profile by filling out the form below.')
    
    context = {
        'form': form,
        'has_existing_profile': has_existing_profile,
        'user': request.user,
        'user_role': get_user_role(request.user),
        'profile': profile
    }
    return render(request, 'alumni/form.html', context)

@login_required
@user_passes_test(is_organization_admin, login_url='login')
def adminpanel(request):
    """Legacy Budibase panel — redirect to the native dashboard."""
    return redirect('org_admin_dashboard')


@login_required
@user_passes_test(is_organization_admin, login_url='login') 
def org_admin_dashboard(request):
    """Main Organization Admin dashboard"""
    total_alumni = AlumniProfile.objects.count()
    employed_alumni = AlumniProfile.objects.filter(employment_status='employed').count()
    self_employed_alumni = AlumniProfile.objects.filter(employment_status='self_employed').count()
    seeking_alumni = AlumniProfile.objects.filter(employment_status='seeking').count()
    recent_updates = AlumniProfile.objects.filter(
        updated_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).count()
    mentor_pool = AlumniProfile.objects.filter(mentorship_interest=True).count()
    networking_pool = AlumniProfile.objects.filter(networking_interest=True).count()
    pending_matches = MentorshipRequest.objects.filter(status='pending').count()
    accepted_matches = MentorshipRequest.objects.filter(status='accepted').count()

    placed = employed_alumni + self_employed_alumni
    employment_rate = round((placed / total_alumni) * 100, 1) if total_alumni else 0

    by_course = list(
        AlumniProfile.objects.exclude(course_studied__isnull=True)
        .exclude(course_studied='')
        .values('course_studied')
        .annotate(
            total=Count('id'),
            employed=Count('id', filter=Q(employment_status='employed')),
            self_employed=Count('id', filter=Q(employment_status='self_employed')),
            seeking=Count('id', filter=Q(employment_status='seeking')),
        )
        .order_by('-total')[:8]
    )
    by_year = list(
        AlumniProfile.objects.exclude(graduation_year__isnull=True)
        .values('graduation_year')
        .annotate(
            total=Count('id'),
            employed=Count('id', filter=Q(employment_status='employed')),
            self_employed=Count('id', filter=Q(employment_status='self_employed')),
            seeking=Count('id', filter=Q(employment_status='seeking')),
        )
        .order_by('-graduation_year')[:10]
    )
    savings_avg = AlumniProfile.objects.aggregate(avg=Avg('monthly_savings'))['avg'] or 0
    investment_avg = AlumniProfile.objects.aggregate(avg=Avg('monthly_investment'))['avg'] or 0

    context = {
        'user_role': get_user_role(request.user),
        'user': request.user,
        'total_alumni': total_alumni,
        'employed_alumni': employed_alumni,
        'self_employed_alumni': self_employed_alumni,
        'seeking_alumni': seeking_alumni,
        'recent_updates': recent_updates,
        'mentor_pool': mentor_pool,
        'networking_pool': networking_pool,
        'pending_matches': pending_matches,
        'accepted_matches': accepted_matches,
        'employment_rate': employment_rate,
        'by_course_json': json.dumps(by_course),
        'by_year_json': json.dumps(by_year),
        'savings_avg': savings_avg,
        'investment_avg': investment_avg,
        'published_announcements': Announcement.objects.filter(is_published=True).count(),
    }
    return render(request, 'alumni/org_admin_dashboard.html', context)

def set_alumni_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                user.is_active = True # Activate the account!
                user.save()
                try:
                    # Assumes your group is named 'Alumni'. Change if needed.
                    alumni_group = Group.objects.get(name='Alumni') 
                    user.groups.add(alumni_group)
                except Group.DoesNotExist:
                    # Handle case where the group doesn't exist
                    # You might want to log this error
                    messages.error(request, 'Configuration error: Alumni group not found.')
                login(request, user) # Log the user in
                messages.success(request, 'Your password has been set and you are now logged in!')
                return redirect('home') # Redirect to their dashboard
        else:
            form = SetPasswordForm(user)
        
        return render(request, 'alumni/set_password_form.html', {'form': form})
    else:
        messages.error(request, 'The activation link is invalid or has expired.')
        return redirect('login')


@login_required
@user_passes_test(is_organization_admin, login_url='login')
def alumni_list(request):
    """Alumni list with search, filtering, and user account status."""
    search_query = request.GET.get('search', '')
    employment_filter = request.GET.get('employment', '')
    course_filter = request.GET.get('course', '')
    year_filter = request.GET.get('year', '')
    
    # --- KEY CHANGE: Annotate with user existence ---
    # We create a subquery that checks if a User exists with the same email.
    user_exists_subquery = User.objects.filter(email=OuterRef('email'))
    
    alumni = AlumniProfile.objects.annotate(
        has_user_account=Exists(user_exists_subquery.values('pk')),
        is_user_active=Exists(user_exists_subquery.filter(is_active=True).values('pk'))
    ).order_by('-created_at')
    
    # Apply search filter
    if search_query:
        alumni = alumni.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(company_name__icontains=search_query)
        )
    
    # Apply other filters...
    if employment_filter:
        alumni = alumni.filter(employment_status=employment_filter)
    if course_filter:
        alumni = alumni.filter(course_studied__icontains=course_filter)
    if year_filter:
        alumni = alumni.filter(graduation_year=year_filter)
    
    # Pagination
    paginator = Paginator(alumni, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique values for filters
    course_choices = AlumniProfile.objects.values_list('course_studied', flat=True).distinct().exclude(course_studied__isnull=True)
    year_choices = AlumniProfile.objects.values_list('graduation_year', flat=True).distinct().exclude(graduation_year__isnull=True)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'employment_filter': employment_filter,
        'course_filter': course_filter,
        'year_filter': year_filter,
        'course_choices': course_choices,
        'year_choices': sorted(year_choices, reverse=True) if year_choices else [],
        'user': request.user,
    }
    return render(request, 'alumni/alumni_list.html', context)

@login_required
@user_passes_test(is_organization_admin, login_url='login')
@require_POST
def send_invite(request, alumni_id):
    try:
        alumni = get_object_or_404(AlumniProfile, id=alumni_id)
        success, message = _send_alumni_invitation(request, alumni)
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
    except AlumniProfile.DoesNotExist:
        messages.error(request, "Alumni profile not found.")
    return redirect('alumni_list')



@login_required
@user_passes_test(is_organization_admin, login_url='login')
def add_alumni(request):
    """Add new alumni profile"""
    if request.method == 'POST':
        form = AlumniProfileForm(request.POST, request.FILES)
        if form.is_valid():
            alumni_profile = form.save()
            messages.success(request, f'Alumni profile for {alumni_profile.first_name} {alumni_profile.last_name} created successfully!')
            return redirect('alumni_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AlumniProfileForm()
    
    context = {
        'form': form,
        'title': 'Add New Alumni',
        'submit_text': 'Create Alumni Profile',
        'user_role': get_user_role(request.user),
        'user': request.user,
    }
    return render(request, 'alumni/admin_form.html', context)


@login_required
@user_passes_test(is_organization_admin, login_url='login')
def edit_alumni(request, alumni_id):
    """Edit existing alumni profile"""
    alumni = get_object_or_404(AlumniProfile, id=alumni_id)
    
    if request.method == 'POST':
        form = AlumniProfileForm(request.POST, request.FILES, instance=alumni)
        
        # Check if user wants to remove profile picture
        remove_picture = request.POST.get('remove_picture') == 'true'
        
        if form.is_valid():
            # Get the old profile picture before saving
            old_picture = alumni.profile_picture
            
            # Handle profile picture removal
            if remove_picture and old_picture:
                if os.path.isfile(old_picture.path):
                    try:
                        os.remove(old_picture.path)
                    except (OSError, FileNotFoundError):
                        pass
                # Clear the profile picture field
                form.instance.profile_picture = None
            
            # Save the form
            updated_alumni = form.save()
            
            # If profile picture changed (new upload), clean up old file
            if 'profile_picture' in form.changed_data and updated_alumni.profile_picture and not remove_picture:
                if old_picture and old_picture != updated_alumni.profile_picture:
                    # Delete old file if it exists
                    if os.path.isfile(old_picture.path):
                        try:
                            os.remove(old_picture.path)
                        except (OSError, FileNotFoundError):
                            pass
            
            messages.success(request, f'Alumni profile for {alumni.first_name} {alumni.last_name} updated successfully!')
            return redirect('alumni_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AlumniProfileForm(instance=alumni)
    
    context = {
        'form': form,
        'alumni': alumni,
        'title': f'Edit {alumni.first_name} {alumni.last_name}',
        'submit_text': 'Update Alumni Profile',
        'user_role': get_user_role(request.user),
        'user': request.user,
    }
    return render(request, 'alumni/admin_form.html', context)

@login_required
@user_passes_test(is_alumni, login_url='login')
def alumni_profile_edit(request):
    """Redirect to the main alumni edit form."""
    return redirect('edit_form')

@login_required
@user_passes_test(is_organization_admin, login_url='login')
def delete_alumni(request, alumni_id):
    """Delete alumni profile"""
    alumni = get_object_or_404(AlumniProfile, id=alumni_id)
    
    if request.method == 'POST':
        name = f"{alumni.first_name} {alumni.last_name}"
        alumni.delete()
        messages.success(request, f'Alumni profile for {name} deleted successfully!')
        return redirect('alumni_list')
    
    context = {
        'alumni': alumni,
        'user_role': get_user_role(request.user),
        'user': request.user,
    }
    return render(request, 'alumni/confirm_delete.html', context)

def _send_alumni_invitation(request, alumni):
    """
    Helper function to create or reuse a user account and send an invitation email.
    This version handles both initial invites and resending to existing inactive users.
    Returns a tuple: (success_boolean, message_string)
    """
    # 1. Check if the profile is linked to an ACTIVE user. If so, we can't do anything.
    if alumni.user and alumni.user.is_active:
        return (False, f"An active account for {alumni.email} already exists.")

    user = None
    action_message = "sent invitation"

    # 2. Determine if we can reuse an existing user or need to create one.
    if alumni.user:
        # The profile is already linked to an INACTIVE user. We will resend the invite.
        user = alumni.user
        action_message = "resent invitation"
    else:
        # The profile is not linked. Check if an unlinked user with this email exists.
        existing_user = User.objects.filter(email=alumni.email).first()
        
        if existing_user:
            # An unlinked user was found. Let's use it.
            user = existing_user
            # Check if this user is already linked to a different profile.
            if hasattr(user, 'alumni_profile') and user.alumni_profile != alumni:
                return (False, f"Error: The user {alumni.email} is already linked to another alumni profile.")
            
            # Link the found user to this profile.
            alumni.user = user
            alumni.save()
            action_message = "resent invitation to existing user"
        else:
            # No user found with this email, so we create a new one.
            temp_password = get_random_string(length=12)
            user = User.objects.create_user(
                username=alumni.email,
                email=alumni.email,
                password=temp_password,
                first_name=alumni.first_name,
                last_name=alumni.last_name,
                is_active=False
            )
            alumni.user = user
            alumni.save()
            action_message = "sent invitation"

    # 3. Generate a new token and activation link for the user we found or created.
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_link = request.build_absolute_uri(
        f'/alumni/set-password/{uid}/{token}/'
    )

    # 4. Send the email
    email_subject = 'You are invited to the Alumni Portal!'
    email_body = render_to_string('alumni/invite_email.html', {
        'alumni': alumni,
        'activation_link': activation_link,
    })
    send_mail(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [alumni.email],
    )
    
    # 5. Return a success status and message
    return (True, f"Successfully {action_message} to {alumni.first_name} {alumni.last_name}.")


@login_required
@user_passes_test(is_organization_admin, login_url='login')
def bulk_operations(request):
    """Handle all bulk operations on alumni profiles (invite, export, delete)"""
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_ids = request.POST.getlist('selected_alumni')
        
        if not selected_ids:
            messages.error(request, 'No alumni selected.')
            return redirect('alumni_list')
        
        selected_alumni = AlumniProfile.objects.filter(id__in=selected_ids)
        
        # --- MERGED LOGIC ---
        if action == 'invite':
            invited_count = 0
            already_exists_count = 0
            for alumni in selected_alumni:
                success, message = _send_alumni_invitation(request, alumni)
                if success:
                    invited_count += 1
                else:
                    already_exists_count += 1
            
            if invited_count > 0:
                messages.success(request, f'Successfully sent {invited_count} invitations.')
            if already_exists_count > 0:
                messages.warning(request, f'{already_exists_count} alumni already had an account and were not invited again.')

        elif action == 'delete':
            count = selected_alumni.count()
            selected_alumni.delete()
            messages.success(request, f'{count} alumni profiles deleted successfully.')
        
        elif action == 'export':
            # This calls your existing export function
            return export_alumni_csv(selected_alumni)
        
        else:
            messages.error(request, 'Invalid action selected.')
    
    return redirect('alumni_list')




@login_required
@user_passes_test(is_alumni, login_url='login')
def delete_profile_picture(request):
    """Delete user's profile picture"""
    try:
        profile = request.user.alumni_profile
        if profile.profile_picture:
            profile.delete_profile_picture()
            messages.success(request, 'Profile picture deleted successfully!')
        else:
            messages.info(request, 'No profile picture to delete.')
    except AlumniProfile.DoesNotExist:
        messages.error(request, 'Profile not found.')

    return redirect('edit_form')


def export_alumni_csv(alumni_queryset):
    """Export alumni data as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="alumni_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow([
        'First Name', 'Last Name', 'Email', 'Phone', 'Address',
        'Graduation Year', 'Course', 'Employment Status', 'Company',
        'Company Location', 'Skills', 'Monthly Savings', 'Monthly Investment',
        'Mentorship Interest', 'Networking Interest', 'Created Date'
    ])

    for alumni in alumni_queryset:
        writer.writerow([
            alumni.first_name,
            alumni.last_name,
            alumni.email,
            alumni.phone_number,
            alumni.current_address,
            alumni.graduation_year,
            alumni.course_studied,
            alumni.get_employment_status_display(),
            alumni.company_name,
            alumni.company_location,
            alumni.skills_acquired,
            alumni.monthly_savings,
            alumni.monthly_investment,
            'Yes' if alumni.mentorship_interest else 'No',
            'Yes' if alumni.networking_interest else 'No',
            alumni.created_at.strftime('%Y-%m-%d')
        ])

    return response


@login_required
@user_passes_test(is_organization_admin, login_url='login')
def import_alumni_csv(request):
    """CSV upload for alumni profiles"""
    preview_rows = None
    preview_errors = None

    if request.method == 'POST':
        action = request.POST.get('action', 'preview')
        form = CSVImportForm(request.POST, request.FILES)

        if action == 'commit' and request.session.get('csv_import_rows'):
            rows = request.session.pop('csv_import_rows', [])
            request.session.pop('csv_import_errors', None)
            created, updated = commit_alumni_rows(rows)
            messages.success(request, f'Imported {created} new, updated {updated}.')
            return redirect('alumni_list')

        if form.is_valid():
            rows, errors = parse_alumni_csv(form.cleaned_data['csv_file'])
            # decimals aren't session-friendly as Decimal objects
            request.session['csv_import_rows'] = [
                {
                    **r,
                    'monthly_savings': str(r['monthly_savings']),
                    'monthly_investment': str(r['monthly_investment']),
                }
                for r in rows
            ]
            request.session['csv_import_errors'] = errors
            preview_rows = rows
            preview_errors = errors
            if errors and not rows:
                messages.error(request, 'Could not import — fix the errors below and try again.')
            elif errors:
                messages.warning(
                    request,
                    f'{len(errors)} rows have problems and will be skipped. '
                    f'{len(rows)} look good.',
                )
            else:
                messages.success(request, f'{len(rows)} rows look good. Confirm to save.')
        else:
            messages.error(request, 'Please choose a CSV file.')
    else:
        form = CSVImportForm()
        request.session.pop('csv_import_rows', None)
        request.session.pop('csv_import_errors', None)

    return render(request, 'alumni/import_alumni.html', {
        'form': form,
        'preview_rows': preview_rows,
        'preview_errors': preview_errors,
        'user': request.user,
    })


@login_required
def announcements_list(request):
    """List announcements (drafts only visible to admins)"""
    role = get_user_role(request.user)
    if role in ('organization_admin', 'system_admin'):
        qs = Announcement.objects.all()
    else:
        qs = Announcement.objects.filter(is_published=True)

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'alumni/announcements_list.html', {
        'page_obj': page_obj,
        'user_role': role,
        'user': request.user,
        'is_admin': role in ('organization_admin', 'system_admin'),
    })


@login_required
def announcement_detail(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    role = get_user_role(request.user)
    if not announcement.is_published and role not in ('organization_admin', 'system_admin'):
        messages.error(request, 'Announcement not found.')
        return redirect('announcements_list')
    return render(request, 'alumni/announcement_detail.html', {
        'announcement': announcement,
        'user_role': role,
        'user': request.user,
        'is_admin': role in ('organization_admin', 'system_admin'),
    })


@login_required
@user_passes_test(is_organization_admin, login_url='login')
def announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announce = form.save(commit=False)
            announce.created_by = request.user
            announce.save()
            if form.cleaned_data.get('notify_alumni') and announce.is_published:
                _notify_alumni_announcement(announce)
                messages.success(request, 'Saved and emailed alumni.')
            else:
                messages.success(request, 'Announcement saved.')
            return redirect('announcements_list')
    else:
        form = AnnouncementForm()
    return render(request, 'alumni/announcement_form.html', {
        'form': form,
        'title': 'New Announcement',
        'user': request.user,
    })


@login_required
@user_passes_test(is_organization_admin, login_url='login')
def announcement_edit(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            announce = form.save()
            if form.cleaned_data.get('notify_alumni') and announce.is_published:
                _notify_alumni_announcement(announce)
                messages.success(request, 'Updated and emailed alumni.')
            else:
                messages.success(request, 'Announcement updated.')
            return redirect('announcement_detail', pk=announce.pk)
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'alumni/announcement_form.html', {
        'form': form,
        'title': 'Edit Announcement',
        'announcement': announcement,
        'user': request.user,
    })


@login_required
@user_passes_test(is_organization_admin, login_url='login')
@require_POST
def announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    announcement.delete()
    messages.success(request, 'Announcement deleted.')
    return redirect('announcements_list')


def _notify_alumni_announcement(announcement):
    emails = list(
        AlumniProfile.objects.exclude(email='')
        .values_list('email', flat=True)
        .distinct()
    )
    if not emails:
        return
    subject = f"{settings.EMAIL_SUBJECT_PREFIX}{announcement.title}"
    body = (
        f"{announcement.title}\n\n"
        f"{announcement.body}\n\n"
        f"— Alumni Management System"
    )
    for email in emails[:200]:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=True)


@login_required
@user_passes_test(is_alumni, login_url='login')
def mentorship_hub(request):
    try:
        profile = request.user.alumni_profile
    except AlumniProfile.DoesNotExist:
        messages.error(request, 'Set up your profile first before requesting a mentor.')
        return redirect('edit_form')

    if request.method == 'POST':
        form = MentorshipRequestForm(request.POST, mentee=profile)
        if form.is_valid():
            req = form.save(commit=False)
            req.mentee = profile
            req.status = 'pending'
            req.save()
            _notify_mentorship_request(req)
            messages.success(request, 'Mentorship request sent.')
            return redirect('mentorship_hub')
    else:
        form = MentorshipRequestForm(mentee=profile)

    incoming = MentorshipRequest.objects.filter(mentor=profile).select_related('mentee')
    outgoing = MentorshipRequest.objects.filter(mentee=profile).select_related('mentor')
    return render(request, 'alumni/mentorship_hub.html', {
        'form': form,
        'incoming': incoming,
        'outgoing': outgoing,
        'profile': profile,
        'user': request.user,
    })


@login_required
@user_passes_test(is_alumni, login_url='login')
@require_POST
def mentorship_respond(request, pk):
    try:
        profile = request.user.alumni_profile
    except AlumniProfile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('home')

    req = get_object_or_404(MentorshipRequest, pk=pk, mentor=profile, status='pending')
    action = request.POST.get('action')
    if action == 'accept':
        req.status = 'accepted'
        req.save()
        _notify_mentorship_status(req)
        messages.success(request, f'You accepted a mentorship request from {req.mentee}.')
    elif action == 'decline':
        req.status = 'declined'
        req.save()
        _notify_mentorship_status(req)
        messages.info(request, 'Mentorship request declined.')
    return redirect('mentorship_hub')


@login_required
@user_passes_test(is_organization_admin, login_url='login')
def mentorship_admin(request):
    status_filter = request.GET.get('status', '')
    qs = MentorshipRequest.objects.select_related('mentee', 'mentor').all()
    if status_filter:
        qs = qs.filter(status=status_filter)
    return render(request, 'alumni/mentorship_admin.html', {
        'requests': qs[:100],
        'status_filter': status_filter,
        'user': request.user,
        'mentor_pool': AlumniProfile.objects.filter(mentorship_interest=True).count(),
    })


def _notify_mentorship_request(req):
    if not req.mentor.email:
        return
    subject = f'{settings.EMAIL_SUBJECT_PREFIX}New mentorship request'
    body = (
        f"Hi {req.mentor.first_name},\n\n"
        f"{req.mentee.first_name} {req.mentee.last_name} requested you as a mentor.\n"
        f"Message: {req.message or '(none)'}\n\n"
        f"Log in to Alumni Management System to accept or decline."
    )
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [req.mentor.email], fail_silently=True)


def _notify_mentorship_status(req):
    if not req.mentee.email:
        return
    subject = f'{settings.EMAIL_SUBJECT_PREFIX}Mentorship request {req.status}'
    body = (
        f"Hi {req.mentee.first_name},\n\n"
        f"{req.mentor.first_name} {req.mentor.last_name} has {req.status} your mentorship request.\n"
    )
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [req.mentee.email], fail_silently=True)


class AlumniLoginView(LoginView):
    """
    Handles the user login process with role-based redirection.
    """
    template_name = 'alumni/login.html'

    def get_success_url(self):
        user = self.request.user
        role = get_user_role(user)
        return get_dashboard_url_for_role(role)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Alumni Login'
        return context


class AlumniLogoutView(LogoutView):
    """Custom logout view that accepts both GET and POST requests"""
    http_method_names = ['get', 'post']
    next_page = 'login'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class AlumniLoggedOutView(TemplateView):
    template_name = 'alumni/logout.html'