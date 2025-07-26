from django.shortcuts import render
from alumni.forms import AlumniProfileForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home(request):
    return render(request,'alumni/home.html')

@login_required
def edit_form(request): 
    if request.method == 'POST':
        form = AlumniProfileForm(request.POST)
        if form.is_valid():
            form.save()
        return render(request, "alumni/successful_form.html")
    else:
        form = AlumniProfileForm()
    alum = AlumniProfileForm
    context = {
        'form': alum
    }
    return render(request, 'alumni/form.html', context)

def adminpanel(request):
    return render(request, 'alumni/admin.html')



class AlumniLoginView(LoginView):
    """
    Handles the user login process using Django's built-in view.
    """
    # This tells the view which HTML file to render.
    # Make sure this path matches where you saved the login page template.
    template_name = 'alumni/login.html'

    # This is where the user will be sent after a successful login.
    # 'alumni_home' should be the name of the URL for your alumni homepage.
    success_url = reverse_lazy('alumni_home')

    def get_context_data(self, **kwargs):
        # You can add extra context to pass to your template if needed.
        context = super().get_context_data(**kwargs)
        context['title'] = 'Alumni Login'
        return context
    

class AlumniLoggedOutView(TemplateView):
    template_name = 'alumni/logged_out.html'