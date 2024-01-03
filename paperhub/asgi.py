"""
ASGI config for paperhub project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
import dotenv
from django.core.asgi import get_asgi_application

env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_file):
    dotenv.load_dotenv(env_file)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')

application = get_asgi_application()
