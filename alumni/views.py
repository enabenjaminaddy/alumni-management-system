from django.shortcuts import render, redirect
from alumni.forms import AlumniProfileForm
from alumni.models import AlumniProfile
from alumni.utils import get_user_role, is_organization_admin, is_alumni, get_dashboard_url_for_role
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

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
    except AlumniProfile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        if profile:
            form = AlumniProfileForm(request.POST, instance=profile)
        else:
            form = AlumniProfileForm(request.POST)
        
        if form.is_valid():
            alumni_profile = form.save(commit=False)
            alumni_profile.user = request.user
            alumni_profile.save()
            return render(request, "alumni/successful_form.html")
    else:
        if profile:
            form = AlumniProfileForm(instance=profile)
        else:
            form = AlumniProfileForm()
    
    context = {
        'form': form
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
    context = {
        'user_role': get_user_role(request.user),
        'user': request.user,
        'total_alumni': AlumniProfile.objects.count(),
    }
    return render(request, 'alumni/org_admin_dashboard.html', context)



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