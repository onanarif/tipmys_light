
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import RegisterView, EmailLoginView, logout_view 
urlpatterns = [
    path('login/', EmailLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('register/', RegisterView.as_view(), name='register'),    
]
