"""
Settings package for core project.
"""

import os

# Determine which settings to use based on environment
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'core.settings.prod':
    from .prod import *
else:
    from .dev import *