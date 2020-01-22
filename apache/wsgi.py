"""
WSGI config for DiamondBase project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0,BASE_DIR)
sys.path.append('/var/www/DiamondBase/sample_database')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiamondBase.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
