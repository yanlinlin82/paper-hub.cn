"""
WSGI config for paperhub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
import dotenv
from django.core.wsgi import get_wsgi_application

env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_file):
    dotenv.load_dotenv(env_file)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')

application = get_wsgi_application()
