"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz/', views.healthz, name='healthz'),
    path('api/', include('catalog.urls')),
]
