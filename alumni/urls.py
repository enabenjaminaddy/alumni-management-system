from django.urls import path
from alumni import views
from alumni.views import AlumniLoginView, AlumniLogoutView
from django.contrib.auth.views import LogoutView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from alumni.password_reset import SendGridPasswordResetView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),
    path('login/', AlumniLoginView.as_view(), name='login'),
    path('logout/', AlumniLogoutView.as_view(), name='logout'),
    path('home/', views.home, name='home'),
    path('edit/', views.edit_form, name='edit_form'),
    path('delete-picture/', views.delete_profile_picture, name='delete_profile_picture'),
    path('adminpanel/', views.adminpanel, name='adminpanel'),
    path('org-admin/', views.org_admin_dashboard, name='org_admin_dashboard'),

    path('org-admin/alumni/', views.alumni_list, name='alumni_list'),
    path('org-admin/alumni/import/', views.import_alumni_csv, name='import_alumni_csv'),
    path('profile/edit/', views.alumni_profile_edit, name='alumni_profile_edit'),
    path('org-admin/alumni/<int:alumni_id>/send-invite/', views.send_invite, name='send_invite'),
    path('alumni/set-password/<uidb64>/<token>/', views.set_alumni_password, name='set_alumni_password'),
    path('org-admin/alumni/add/', views.add_alumni, name='add_alumni'),
    path('org-admin/alumni/<int:alumni_id>/edit/', views.edit_alumni, name='edit_alumni'),
    path('org-admin/alumni/<int:alumni_id>/delete/', views.delete_alumni, name='delete_alumni'),
    path('org-admin/bulk-operations/', views.bulk_operations, name='bulk_operations'),
<<<<<<< HEAD

    path('announcements/', views.announcements_list, name='announcements_list'),
    path('announcements/new/', views.announcement_create, name='announcement_create'),
    path('announcements/<int:pk>/', views.announcement_detail, name='announcement_detail'),
    path('announcements/<int:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),

    path('mentorship/', views.mentorship_hub, name='mentorship_hub'),
    path('mentorship/<int:pk>/respond/', views.mentorship_respond, name='mentorship_respond'),
    path('org-admin/mentorship/', views.mentorship_admin, name='mentorship_admin'),

    path(
        'password-reset/',
        PasswordResetView.as_view(
            template_name='alumni/password_reset.html',
            email_template_name='alumni/password_reset_email.html',
            subject_template_name='alumni/password_reset_subject.txt',
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        PasswordResetDoneView.as_view(template_name='alumni/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(template_name='alumni/password_reset_confirm.html'),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(template_name='alumni/password_reset_complete.html'),
        name='password_reset_complete',
    ),
]
=======
    # path('alumni/bulk-operations/', views.bulk_operations, name='bulk_operations'),
    
    path('login/', AlumniLoginView.as_view(), name='login'),
    path('logout/', AlumniLogoutView.as_view(), name='logout'),
    
    # Password Reset URLs - Using SendGrid Template
    path('password-reset/', 
         SendGridPasswordResetView.as_view(
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
<<<<<<< HEAD
>>>>>>> 823cd9a1f049d4ba3da43adb895bd692246c80fb
=======
>>>>>>> origin/main
>>>>>>> new-features
