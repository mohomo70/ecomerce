"""
URLs for users app.
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('me/', views.me, name='me'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('csrf/', views.csrf_token, name='csrf_token'),
]