from django.contrib import admin
from django.urls import path
from  alumni import views
from alumni.views import AlumniLoginView, AlumniLogoutView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', AlumniLoginView.as_view(), name='login'),  # Root URL redirects to login
    path('home/', views.home, name='home'),
    path('edit/', views.edit_form, name='edit_form'),
    path('adminpanel/', views.adminpanel, name='adminpanel'),  # Legacy admin panel
    path('org-admin/', views.org_admin_dashboard, name='org_admin_dashboard'),  # New org admin dashboard
    path('login/', AlumniLoginView.as_view(), name='login'),
    path('logout/', AlumniLogoutView.as_view(), name='logout'),
]