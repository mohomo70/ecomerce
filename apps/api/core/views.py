"""
Core views for the API.
"""
from django.http import JsonResponse
from django.conf import settings
import time


def health_check(request):
    """Health check endpoint."""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': int(time.time()),
        'version': '1.0.0',
        'debug': settings.DEBUG,
    })