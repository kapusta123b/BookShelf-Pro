from dotenv import load_dotenv
from pathlib import Path
from os import environ

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')



SECRET_KEY = environ.get('SECRET_KEY')

DEBUG = environ.get('DEBUG', 'False') == 'True'

CSRF_TRUSTED_ORIGINS = environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost').split(',')

ALLOWED_HOSTS = environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

USE_X_FORWARDED_HOST = True


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #SCSS
    'sass_processor',
    'compressor',

    #ReCaptcha
    'django_recaptcha',

    #allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',

    'main',
    'books',
    'library',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # allauth
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": environ.get("DB_NAME"),
        "USER": environ.get("DB_USER"),
        "PASSWORD": environ.get("DB_PASS"),
        "HOST": environ.get("DB_HOST"),
        "PORT": environ.get("DB_PORT"),
    }
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

SITE_ID = 1

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static', BASE_DIR / 'sass-cache']

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
    'compressor.finders.CompressorFinder',
]

AUTH_USER_MODEL = "users.User"

# redirects
LOGIN_URL = "user:login"
LOGIN_REDIRECT_URL = "main:index"
LOGOUT_REDIRECT_URL = "main:index"

#SCSS
SASS_PROCESSOR_ROOT = BASE_DIR / 'sass-cache'
SASS_PROCESSOR_INCLUDE_DIRS = [
    BASE_DIR / 'static' / 'deps' / 'css',
]

COMPRESS_ROOT = BASE_DIR / 'static'

# mail configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = environ.get('EMAIL_NAME')
EMAIL_HOST_PASSWORD = environ.get('EMAIL_APP_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# django-recaptcha
RECAPTCHA_PUBLIC_KEY = environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = environ.get('RECAPTCHA_PRIVATE_KEY')

# django-allauth configuration
ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

ACCOUNT_FORMS ={
    'login': 'users.forms.UserLoginForm',
    'signup': 'users.forms.UserSignUpForm'
}