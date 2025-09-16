"""
Core views for the ecommerce project.
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone


@require_http_methods(["GET"])
def healthz(request):
    """
    Health check endpoint.
    Returns 200 with timestamp and version info.
    """
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0',
    })