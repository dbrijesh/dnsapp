"""
Django settings for leadup project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# CSRF Settings for production
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if os.environ.get('CSRF_TRUSTED_ORIGINS') else []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap5',

    # Local apps
    'accounts',
    'programs',
    'learners',
    'admins',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'leadup.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.azure_sso_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'leadup.wsgi.application'

# Database configuration
# SQLite for local development and Azure Container Apps (for now)
# Azure SQL can be enabled by setting USE_AZURE_SQL=True
if os.environ.get('USE_AZURE_SQL', 'False') == 'True':
    DATABASES = {
        'default': {
            'ENGINE': 'mssql',
            'NAME': os.environ.get('AZURE_SQL_DATABASE'),
            'USER': os.environ.get('AZURE_SQL_USER'),
            'PASSWORD': os.environ.get('AZURE_SQL_PASSWORD'),
            'HOST': os.environ.get('AZURE_SQL_SERVER'),
            'PORT': '1433',
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
            },
        }
    }
else:
    # Use SQLite - store in /app/data for persistence in container
    db_path = os.environ.get('SQLITE_DB_PATH', str(BASE_DIR / 'db.sqlite3'))
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': db_path,
        }
    }

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Azure Blob Storage configuration
USE_AZURE_STORAGE = os.environ.get('USE_AZURE_STORAGE', 'False') == 'True'
if USE_AZURE_STORAGE:
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_STORAGE_CONTAINER_NAME = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'course-materials')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Azure AD SSO configuration
USE_AZURE_AD_SSO = os.environ.get('USE_AZURE_AD_SSO', 'False') == 'True'

if USE_AZURE_AD_SSO:
    # When SSO is enabled, ONLY use Azure AD backend (no password fallback)
    AUTHENTICATION_BACKENDS = ['accounts.backends.AzureADBackend']

    # Azure AD OAuth settings
    AZURE_AD_CLIENT_ID = os.environ.get('AZURE_AD_CLIENT_ID')
    AZURE_AD_CLIENT_SECRET = os.environ.get('AZURE_AD_CLIENT_SECRET')
    AZURE_AD_TENANT_ID = os.environ.get('AZURE_AD_TENANT_ID')
    AZURE_AD_REDIRECT_URI = os.environ.get('AZURE_AD_REDIRECT_URI')

    # MSAL configuration
    AZURE_AD_AUTHORITY = f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}"
    AZURE_AD_SCOPES = ["openid", "profile", "email", "User.Read"]

    # Token validation
    AZURE_AD_TOKEN_ISSUER = f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/v2.0"
    AZURE_AD_TOKEN_AUDIENCE = AZURE_AD_CLIENT_ID
else:
    # Local development fallback
    AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

# Login/Logout URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'learners:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Session settings
SESSION_COOKIE_AGE = 3600 if USE_AZURE_AD_SSO else 86400  # 1 hour for SSO, 24 hours otherwise
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
