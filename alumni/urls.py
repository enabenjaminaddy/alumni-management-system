from django.contrib import admin
from django.urls import path
from  alumni import views
from alumni.views import AlumniLoginView, AlumniLogoutView
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns = [
    path('', AlumniLoginView.as_view(), name='login'),  # Root URL redirects to login
    path('home/', views.home, name='home'),
    path('edit/', views.edit_form, name='edit_form'),
    path('delete-picture/', views.delete_profile_picture, name='delete_profile_picture'),
    path('adminpanel/', views.adminpanel, name='adminpanel'),  # Legacy admin panel
    path('org-admin/', views.org_admin_dashboard, name='org_admin_dashboard'),  # New org admin dashboard
    
    # Organization Admin specific URLs
    path('org-admin/alumni/', views.alumni_list, name='alumni_list'),
    path('profile/edit/', views.alumni_profile_edit, name='alumni_profile_edit'),
    path('org-admin/alumni/<int:alumni_id>/send-invite/', views.send_invite, name='send_invite'),
    path('alumni/set-password/<uidb64>/<token>/', views.set_alumni_password, name='set_alumni_password'),
    path('org-admin/alumni/add/', views.add_alumni, name='add_alumni'),
    path('org-admin/alumni/<int:alumni_id>/edit/', views.edit_alumni, name='edit_alumni'),
    path('org-admin/alumni/<int:alumni_id>/delete/', views.delete_alumni, name='delete_alumni'),
    path('org-admin/bulk-operations/', views.bulk_operations, name='bulk_operations'),
    # path('alumni/bulk-operations/', views.bulk_operations, name='bulk_operations'),
    
    path('login/', AlumniLoginView.as_view(), name='login'),
    path('logout/', AlumniLogoutView.as_view(), name='logout'),
    
    # Password Reset URLs
    path('password-reset/', 
         PasswordResetView.as_view(
             template_name='alumni/password_reset.html',
             email_template_name='alumni/password_reset_email.html',
             subject_template_name='alumni/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         PasswordResetDoneView.as_view(template_name='alumni/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         PasswordResetConfirmView.as_view(template_name='alumni/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('reset/done/', 
         PasswordResetCompleteView.as_view(template_name='alumni/password_reset_complete.html'), 
         name='password_reset_complete'),
]