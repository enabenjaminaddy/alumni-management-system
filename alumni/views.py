from django.shortcuts import render, redirect, get_object_or_404
from alumni.forms import AlumniProfileForm
from alumni.models import AlumniProfile
from alumni.utils import get_user_role, is_organization_admin, is_alumni, get_dashboard_url_for_role
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
import csv
from django.utils import timezone
from django.contrib.auth.models import Group, User
from django.db.models import Q, Exists, OuterRef
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import login
from django.utils.crypto import get_random_string



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
    context = {
        'user_role': user_role,
        'user': request.user,
    }
    return render(request, 'alumni/home.html', context)

@login_required
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
    """Organization Admin dashboard - only for organization admins"""
    context = {
        'user_role': get_user_role(request.user),
        'user': request.user,
    }
    return render(request, 'alumni/admin.html', context)


@login_required
@user_passes_test(is_organization_admin, login_url='login') 
def org_admin_dashboard(request):
    """Main Organization Admin dashboard"""
    # Get statistics
    total_alumni = AlumniProfile.objects.count()
    employed_alumni = AlumniProfile.objects.filter(employment_status='employed').count()
    self_employed_alumni = AlumniProfile.objects.filter(employment_status='self_employed').count()
    recent_updates = AlumniProfile.objects.filter(
        updated_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).count()
    
    context = {
        'user_role': get_user_role(request.user),
        'user': request.user,
        'total_alumni': total_alumni,
        'employed_alumni': employed_alumni,
        'self_employed_alumni': self_employed_alumni,
        'recent_updates': recent_updates,
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

def send_invite(request, alumni_id):
    if request.method == 'POST':
        try:
            alumni = get_object_or_404(AlumniProfile, id=alumni_id)

            # 1. Check if a user account already exists
            if User.objects.filter(email=alumni.email).exists():
                messages.error(request, f"An account for {alumni.email} already exists.")
                return redirect('alumni_list')

            # 2. Create a temporary, inactive user account
            # We use a long, random password that no one will ever use.
            temp_password = get_random_string(length=12)
            user = User.objects.create_user(
                username=alumni.email, # Use email as username for simplicity
                email=alumni.email,
                password=temp_password,
                first_name=alumni.first_name,
                last_name=alumni.last_name,
                is_active=False # The account is inactive until they set a password
            )
            alumni.user = user
            alumni.save()

            # 3. Generate a unique, one-time-use token and activation link
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = request.build_absolute_uri(
                f'/alumni/set-password/{uid}/{token}/' # This URL needs to exist
            )

            # 4. Send the email
            email_subject = 'You are invited to the Alumni Portal!'
            email_body = render_to_string('alumni/invite_email.html', {
                'alumni': alumni,
                'activation_link': activation_link,
            })
            send_mail(email_subject, email_body, 'no-reply@yourfoundation.org', [alumni.email])

            messages.success(request, f"Successfully sent an invitation to {alumni.first_name}.")

            print(f"Sending invite to {alumni.email}...")
            # --------------------------------------------------
            # messages.success(request, f"Successfully sent an invitation to {alumni.first_name} {alumni.last_name}.")
        except AlumniProfile.DoesNotExist:
            messages.error(request, "Alumni profile not found.")
    
    return redirect('alumni_list')


@login_required
@user_passes_test(is_organization_admin, login_url='login')
def add_alumni(request):
    """Add new alumni profile"""
    if request.method == 'POST':
        form = AlumniProfileForm(request.POST)
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
        form = AlumniProfileForm(request.POST, instance=alumni)
        if form.is_valid():
            form.save()
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
def alumni_profile_edit(request):
    """
    Allows a logged-in alumnus to edit their own profile.
    """
    try:
        # This is the key: it gets the profile linked to the current user.
        # This requires the OneToOneField link from the previous explanation.
        profile = request.user.alumni_profile 
    except AlumniProfile.DoesNotExist:
        messages.error(request, "Your alumni profile could not be found. Please contact an administrator.")
        return redirect('home') # Or some other appropriate page

    if request.method == 'POST':
        # We pass 'instance=profile' to tell the form to UPDATE this specific profile, not create a new one.
        form = AlumniProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('home') # Redirect to their dashboard after saving
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # When the page is first loaded, pre-populate the form with the user's existing data.
        form = AlumniProfileForm(instance=profile)

    context = {
        'form': form,
        'title': 'Edit Your Profile',
        'submit_text': 'Save Changes',
        'user': request.user,
    }
    # This can reuse your existing admin form template
    return render(request, 'alumni/admin_form.html', context)

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
    This version is more robust and handles unlinked, existing user accounts.
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
        try:
            user = User.objects.get(email=alumni.email)
            
            # If a user was found, check if they are already linked to a *different* profile.
            if hasattr(user, 'alumni_profile') and user.alumni_profile != alumni:
                return (False, f"Error: The user {alumni.email} is already linked to another alumni profile.")
            
            # If the user is unlinked, we can claim them for this profile.
            alumni.user = user
            alumni.save()
            action_message = "resent invitation to existing user"

        except User.DoesNotExist:
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
    send_mail(email_subject, email_body, 'no-reply@yourfoundation.org', [alumni.email])
    
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
    response['Content-Disposition'] = f'attachment; filename="alumni_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
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


class AlumniLoginView(LoginView):
    """
    Handles the user login process with role-based redirection.
    """
    template_name = 'alumni/login.html'

    def get_success_url(self):
        """Redirect user based on their role after successful login"""
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
        """Handle GET requests for logout"""
        return self.post(request, *args, **kwargs)


class AlumniLoggedOutView(TemplateView):
    template_name = 'alumni/logged_out.html'