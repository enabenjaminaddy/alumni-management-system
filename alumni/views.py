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
import os

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


@login_required
@user_passes_test(is_organization_admin, login_url='login')
def alumni_list(request):
    """Alumni list with search and filtering"""
    search_query = request.GET.get('search', '')
    employment_filter = request.GET.get('employment', '')
    course_filter = request.GET.get('course', '')
    year_filter = request.GET.get('year', '')
    
    # Start with all alumni
    alumni = AlumniProfile.objects.all().order_by('-created_at')
    
    # Apply search filter
    if search_query:
        alumni = alumni.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(company_name__icontains=search_query)
        )
    
    # Apply employment filter
    if employment_filter:
        alumni = alumni.filter(employment_status=employment_filter)
    
    # Apply course filter
    if course_filter:
        alumni = alumni.filter(course_studied__icontains=course_filter)
    
    # Apply year filter
    if year_filter:
        alumni = alumni.filter(graduation_year=year_filter)
    
    # Pagination
    paginator = Paginator(alumni, 20)  # Show 20 alumni per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique values for filters
    employment_choices = AlumniProfile.objects.values_list('employment_status', flat=True).distinct()
    course_choices = AlumniProfile.objects.values_list('course_studied', flat=True).distinct().exclude(course_studied__isnull=True)
    year_choices = AlumniProfile.objects.values_list('graduation_year', flat=True).distinct().exclude(graduation_year__isnull=True)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'employment_filter': employment_filter,
        'course_filter': course_filter,
        'year_filter': year_filter,
        'employment_choices': employment_choices,
        'course_choices': course_choices,
        'year_choices': sorted(year_choices, reverse=True) if year_choices else [],
        'user_role': get_user_role(request.user),
        'user': request.user,
    }
    return render(request, 'alumni/alumni_list.html', context)


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


@login_required
@user_passes_test(is_organization_admin, login_url='login')
def bulk_operations(request):
    """Handle bulk operations on alumni profiles"""
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_ids = request.POST.getlist('selected_alumni')
        
        if not selected_ids:
            messages.error(request, 'No alumni selected.')
            return redirect('alumni_list')
        
        selected_alumni = AlumniProfile.objects.filter(id__in=selected_ids)
        
        if action == 'delete':
            count = selected_alumni.count()
            selected_alumni.delete()
            messages.success(request, f'{count} alumni profiles deleted successfully.')
        
        elif action == 'export':
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