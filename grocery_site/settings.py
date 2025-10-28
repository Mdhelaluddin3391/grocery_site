from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-%4rg3g-0b4a%h3)g7g)p2+!lg3j1b8=6tu9y9#s4y#4-obk(um'
DEBUG = True
ALLOWED_HOSTS = []

# -------------------------------------------------------------------
# Application definition
# -------------------------------------------------------------------
INSTALLED_APPS = [
    # Django default apps...
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Authentication & social login
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Your custom apps
    'users',
    'store',
    'cart',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # required for django-allauth
]

ROOT_URLCONF = 'grocery_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # <-- for Google login HTML templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.footer_categories',
                'store.context_processors.main_categories_processor',
                'cart.context_processors.cart_item_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'grocery_site.wsgi.application'

# -------------------------------------------------------------------
# Database
# -------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# -------------------------------------------------------------------
# Password validators
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------------------------------------------
# Internationalization
# -------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # <-- Better for India
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# Static files
# -------------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------------------------------------------
# Custom user model
# -------------------------------------------------------------------
AUTH_USER_MODEL = 'users.CustomUser'

# -------------------------------------------------------------------
# Email backend (for console output)
# -------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# -------------------------------------------------------------------
# Store settings
# -------------------------------------------------------------------
STORE_LOCATION_NAME = "Dharmanagar"
STORE_COORDINATES = {"lat": 24.3725, "lng": 92.1661}

# -------------------------------------------------------------------
# Django Allauth (Google Login) configuration
# -------------------------------------------------------------------
SITE_ID = 1

# This tells Django which authentication methods to use
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',        # Needed for Django admin login
    'allauth.account.auth_backends.AuthenticationBackend', # Needed for Google login
]

# --- CORE ALLAUTH SETTINGS FOR MODERN VERSIONS ---

# 1. Connects your custom security logic
SOCIALACCOUNT_ADAPTER = 'dashboard.staff_social_adapter.StaffSocialAccountAdapter'

# 2. Skips the intermediate "Continue" confirmation page
SOCIALACCOUNT_LOGIN_ON_GET = True

# 3. New-style settings that replace the deprecated and conflicting ones
ACCOUNT_LOGIN_METHODS = ['email']      # Users are identified by their email
ACCOUNT_SIGNUP_FIELDS = ['email']      # Sign-up only requires an email (no password form)
ACCOUNT_USER_MODEL_USERNAME_FIELD = None # We are not using usernames
ACCOUNT_USERNAME_REQUIRED = False      # Explicitly disable usernames
ACCOUNT_EMAIL_REQUIRED = True          # Email is mandatory
ACCOUNT_EMAIL_VERIFICATION = 'none'    # Do not ask for email verification
ACCOUNT_USER_MODEL_EMAIL_FIELD = None  #<-- ADD THIS LINE

# --- URLs to redirect to after login/logout ---
LOGIN_REDIRECT_URL = '/dashboard/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/dashboard/login/'

# --- Google Provider Specific Settings ---
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}