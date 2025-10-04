# Reference:
# - https://docs.djangoproject.com/en/5.2/topics/settings/
# - https://docs.djangoproject.com/en/5.2/ref/settings/
# - https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Load environment variables from .env file
env_file = BASE_DIR / '.env'
if env_file.exists():
    import dotenv
    dotenv.load_dotenv(env_file)


# Generate secret key if not exists
# ref: https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-SECRET_KEY
secret_key_file = BASE_DIR / 'secret_key.txt'
if not secret_key_file.exists():
    import secrets
    SECRET_KEY = secrets.token_urlsafe(50)
    with open(secret_key_file, 'w') as f:
        f.write(SECRET_KEY)
else:
    with open(secret_key_file, 'r') as f:
        SECRET_KEY = f.read()


# Debug mode
# ref: https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-DEBUG
DEBUG = os.getenv('DEBUG', 'False') == 'True'


# Allowed hosts
# ref: https://docs.djangoproject.com/en/5.2/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "[::1]",
    "paper-hub.cn"
]


# Application definition
# ref: https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-INSTALLED_APPS
INSTALLED_APPS = [
    'api.apps.ApiConfig',
    'core.apps.CoreConfig',
    'view.apps.ViewConfig',
    'library.apps.LibraryConfig',
    'group.apps.GroupConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]


# Middleware
# ref: https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# CSRF trusted origins
# ref: https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    'https://servicewechat.com',
]


# Root URL configuration
# ref: https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-ROOT_URLCONF
ROOT_URLCONF = 'config.urls'


# Templates
# ref: https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-TEMPLATES
TEMPLATES_DIR = BASE_DIR / 'templates'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.my_configures',
            ],
        },
    },
]


# WSGI application
# ref: https://docs.djangoproject.com/en/5.2/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'


# Database
# ref: https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'DATE_FORMAT': 'Y-m-d',
        'DATETIME_FORMAT': 'Y-m-d H:i:s',
        'DATE_INPUT_FORMATS': '%Y-%m-%d',
        'DATETIME_INPUT_FORMATS': '%Y-%m-%d %H:%M:%S',
    }
}


# Password validation
# ref: https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# ref: https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-LANGUAGE_CODE

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# ref: https://docs.djangoproject.com/en/5.2/ref/settings/#static-files
STATIC_ROOT = BASE_DIR / 'static_root'
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]


# Default primary key field type
# ref: https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Custom settings

# Session expire hours
SESSION_EXPIRE_HOURS = 6
