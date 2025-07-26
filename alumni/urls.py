from django.contrib import admin
from django.urls import path
from  alumni import views
from alumni.views import AlumniLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('home/', views.home, name='home'),
    path('edit/', views.edit_form, name='edit_form'),
    path('adminpanel/', views.adminpanel, name='adminpanel'),
    path('login/', AlumniLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='your_login_url_name'), name='logout'),
]